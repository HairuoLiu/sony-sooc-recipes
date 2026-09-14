#!/usr/bin/env python3
"""Turn one fresh upstream checkout into one brand pack, in place.

    python tools/apply_pack.py --pack leica --fork build/recipe-lab-sony-pmca
    python tools/apply_pack.py --pack leica --fork DIR --dry-run
    python tools/apply_pack.py --pack leica --fork DIR --check

A pack is NOT a fork. It is the same codebase, the same catalog and the same native
library, with two things changed and one thing added:

  * the **Android package name** gains the pack id (`...sonysoocrecipes` ->
    `...sonysoocrecipes.leica`). This is not cosmetic. Android identifies an app by its
    package name, so two APKs sharing one package name cannot be installed side by side —
    the second is treated as an update of the first and replaces it. Without this, the
    whole "install only the pack you want" plan collapses to one installed app.
  * the **app name** in res/values/strings.xml.
  * the pack's **icon set**, if assets/app-icon-packs/<icon_set>/ exists.

Why the renaming is written as four explicit separator forms rather than one tidy sed.
The package string appears in the upstream tree as `com.hairuoliu.sonysoocrecipes` (the
manifest, every Java `package` line, the JNI exception lookup, the custom-view class names
in res/layout), as `com/hairuoliu/sonysoocrecipes` (build.sh, check-version.sh, and a
directory path inside jni.cpp), and as `com\\hairuoliu\\sonysoocrecipes` (build.cmd).
Skipping any one of them produces a build that dies in javac or aapt, or an app that
crashes on launch when the native layer cannot find its exception class.

Each form is anchored on the FULL package, never on the trailing token. That is
deliberate: the string `sonysoocrecipes` on its own is also the native library name
(`LOCAL_MODULE` in jni/Android.mk, `System.loadLibrary` in NativeBackup.java, and
`libsonysoocrecipes.so` in both build scripts). Rewriting the bare token would produce
`libsonysoocrecipes.leica.so`, which is not a loadable library name, and the app would die
with UnsatisfiedLinkError. `--check` fails if that has happened.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

import cataloglib

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PACKS = ROOT / "catalog" / "packs.json"
DEFAULT_ICONS = ROOT / "assets" / "app-icon-packs"
BASE_ICONS = ROOT / "assets" / "app-icon"

PACKAGE_BASE = "com.hairuoliu.sonysoocrecipes"
LIB_NAME = "sonysoocrecipes"
DENSITIES = ("mdpi", "hdpi", "xhdpi", "xxhdpi")

# Text files worth rewriting. .git and out/ are skipped — the first is not ours to touch,
# the second does not exist until a build has run.
SKIP_DIRS = {".git", "out", "__pycache__"}
TEXT_SUFFIXES = {".java", ".cpp", ".c", ".h", ".mk", ".xml", ".sh", ".cmd", ".md", ".txt", ""}


def apk_name(pack: dict) -> str:
    """The APK filename a pack's build.sh is rewritten to produce.

    A function rather than an inline f-string because it is the one piece of pack naming
    that two other places have to agree with: tools/build_matrix.py (which hands the name to
    the release workflow, so the collect step knows what to pick up) and tests/test_packs.py.
    Two copies of this rule is exactly how a release ends up asserting on a filename that
    the build never produced.
    """
    return f"SonySOOCRecipes-{pack['id']}.apk"


def separator_forms(package: str, all_pack_ids: list[str]) -> list[tuple[re.Pattern, str]]:
    """The four ways a Java package is spelled in this tree, as idempotent patterns.

    Each pattern is anchored on the FULL package and refuses to fire when another package
    segment already follows. That single lookahead buys three things:

      * running the transform twice cannot produce `...sonysoocrecipes.leica.leica`;
      * re-running after a partial failure resumes instead of corrupting;
      * it still rewrites the *legitimate* dotted class references, e.g. the custom views
        named in res/layout (`com.hairuoliu.sonysoocrecipes.HintBar`), because `HintBar` is
        not a pack id. A blunter `(?!\\.)` would have silently skipped those and produced an
        APK whose layout inflates a class that does not exist.
    """
    ids = "|".join(re.escape(i) for i in sorted(all_pack_ids, key=len, reverse=True))
    # No pack id may be a prefix of another, or `--pack fuji` could fire on a checkout
    # already carrying `fujifilm` and produce `...fuji.fujifilm`. Checked rather than
    # assumed, because packs.json is data and the next person to add a pack will not know.
    ordered = sorted(all_pack_ids, key=len)
    for i, a in enumerate(ordered):
        for b in ordered[i + 1:]:
            if b.startswith(a):
                raise SystemExit(f"pack id {a!r} is a prefix of {b!r} — the rename cannot "
                                 "tell them apart; rename one of them")
    out: list[tuple[str, re.Pattern, str]] = []
    for sep in (".", "/", "\\", "_"):
        base = PACKAGE_BASE.replace(".", sep)
        # The boundary excludes letters and digits but NOT the underscore: a JNI symbol is
        # `Java_com_a_b_leica_NativeBackup_read`, where the pack segment is followed by an
        # underscore. Excluding it made the pattern re-fire on its own output
        # (`..._leica_leica_...`), which is how this was caught.
        pattern = re.compile(
            re.escape(base) + r"(?!" + re.escape(sep) + r"(?:" + ids + r")(?![A-Za-z0-9]))"
        )
        out.append((base, pattern, package.replace(".", sep)))
    return out


def move_tree(src: Path, dst: Path) -> None:
    """Move `src` to `dst` even when `dst` nests inside `src`.

    A pack package is the base package plus one segment, so the destination directory is
    physically inside the source directory (src/com/a/b -> src/com/a/b/leica). A plain
    move refuses to do that, and rightly so. Route through a sibling temp name instead.
    """
    if dst == src:
        return
    if src in dst.parents:
        tmp = src.parent / (src.name + "__pack_tmp")
        if tmp.exists():
            shutil.rmtree(tmp)
        shutil.move(str(src), str(tmp))
        src.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp), str(dst))
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))


def text_files(fork: Path) -> list[Path]:
    out: list[Path] = []
    for p in sorted(fork.rglob("*")):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(fork).parts[:-1]):
            continue
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".so", ".o", ".a", ".bin", ".keystore"}:
            continue
        out.append(p)
    return out


def apply_icons(fork: Path, pack: dict, report, dry: bool) -> None:
    """Copy a pack's icon set over the fork's launcher icon, else keep what is there."""
    src_root = DEFAULT_ICONS / pack.get("icon_set", pack["id"])
    if not src_root.is_dir():
        fallback = BASE_ICONS
        report.append(f"icons: no {src_root.relative_to(ROOT)} yet — keeping the app's "
                      f"default icon set from {fallback.relative_to(ROOT)}")
        src_root = fallback

    missing = [d for d in DENSITIES if not (src_root / f"ic_launcher-{d}.png").is_file()]
    if missing:
        report.append(f"icons: WARNING {src_root.relative_to(ROOT)} is missing "
                      f"{', '.join(missing)} — those densities keep upstream's icon")
    for d in DENSITIES:
        src = src_root / f"ic_launcher-{d}.png"
        dst = fork / "res" / f"drawable-{d}" / "ic_launcher.png"
        if src.is_file() and dst.parent.is_dir():
            if not dry:
                shutil.copyfile(src, dst)
        elif src.is_file():
            report.append(f"icons: no {dst.parent.relative_to(fork)} in the checkout — skipped")

    # The store-listing icon (dist/icon-512.png) is a separate file from the launcher
    # densities and upstream ships its own, so without this a pack's listing icon would
    # stay upstream's. Same graceful-skip behaviour as the densities above.
    src512 = src_root / "icon-512.png"
    dst512 = fork / "dist" / "icon-512.png"
    if src512.is_file() and dst512.parent.is_dir():
        if not dry:
            shutil.copyfile(src512, dst512)
    elif src512.is_file():
        report.append(f"icons: no {dst512.parent.relative_to(fork)} in the checkout — skipped")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack", required=True, help="pack id from catalog/packs.json")
    ap.add_argument("--fork", type=Path, default=ROOT / "build" / "recipe-lab-sony-pmca")
    ap.add_argument("--dry-run", action="store_true", help="report, change nothing")
    ap.add_argument("--check", action="store_true",
                    help="verify the checkout is already this pack and is self-consistent")
    args = ap.parse_args()

    pack, all_ids = cataloglib.load_pack(DEFAULT_PACKS, args.pack)
    fork: Path = args.fork
    package = f"{PACKAGE_BASE}.{pack['id']}"
    report: list[str] = []

    if not (fork / "AndroidManifest.xml").is_file():
        raise SystemExit(f"{fork} does not look like an upstream checkout "
                         "(no AndroidManifest.xml)")

    old_src = fork / "src" / Path(*PACKAGE_BASE.split("."))
    new_src = fork / "src" / Path(*package.split("."))
    manifest = (fork / "AndroidManifest.xml").read_text(encoding="utf-8")
    forms = separator_forms(package, all_ids)

    # ---- check mode -------------------------------------------------------------------
    # The test is "would running the transform change anything?", not "does the base
    # package appear anywhere?". A pack package *starts with* the base package, so a
    # substring test flags every correctly-rewritten file and is worse than useless.
    if args.check:
        problems: list[str] = []
        if f'package="{package}"' not in manifest:
            problems.append(f'AndroidManifest.xml does not declare package="{package}"')

        leftovers: list[str] = []
        for p in text_files(fork):
            try:
                t = p.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            hits = sum(len(pattern.findall(t)) for _, pattern, _ in forms)
            if hits:
                leftovers.append(f"{p.relative_to(fork)} ({hits})")
        if leftovers:
            problems.append("the base package is still unrewritten in: "
                            + ", ".join(leftovers[:6])
                            + (f" (+{len(leftovers) - 6} more)" if len(leftovers) > 6 else ""))

        if not new_src.is_dir():
            problems.append(f"{new_src.relative_to(fork)} does not exist")
        # old_src necessarily still exists — it is now the *parent* of new_src. The real
        # question is whether any Java source is still sitting directly in it.
        if old_src.is_dir():
            strays = [f.name for f in old_src.iterdir() if f.is_file() and f.suffix == ".java"]
            if strays:
                problems.append(f"{old_src.relative_to(fork)} still holds "
                                f"{len(strays)} source file(s) — the tree was not moved")

        # The library name must have survived untouched. A dot is not legal in a loadable
        # library name, so this is a hard failure, not a warning.
        for f in ("jni/Android.mk", "build.sh"):
            p = fork / f
            if p.is_file() and f".{pack['id']}.so" in p.read_text(encoding="utf-8"):
                problems.append(f"{f}: the native library name was rewritten "
                                f"(lib{LIB_NAME}.{pack['id']}.so) — it must stay lib{LIB_NAME}.so")

        if problems:
            for p in problems:
                print("FAIL " + p)
            return 1
        print(f"OK — {fork} is pack {pack['id']!r} ({package}) and self-consistent")
        return 0

    # ---- 1. the package rename --------------------------------------------------------
    # Idempotent by construction (see separator_forms), so a re-run after a partial
    # failure finishes the job instead of refusing or double-appending.
    counts = {label: 0 for label, _, _ in forms}
    touched: list[str] = []
    for p in text_files(fork):
        try:
            before = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        after = before
        for label, pattern, new in forms:
            # A lambda, not a string: the Windows form of the replacement contains
            # backslashes, and re treats a string replacement as a template — it would
            # read `\h` as an escape and raise PatternError.
            after, n = pattern.subn(lambda m: new, after)
            counts[label] += n
        if after != before:
            if not args.dry_run:
                p.write_text(after, encoding="utf-8", newline="")
            touched.append(str(p.relative_to(fork)))
    report.append(f"package {PACKAGE_BASE} -> {package}")
    for label, n in counts.items():
        if n:
            report.append(f"  {n:3d} x {label}")
    report.append(f"  in {len(touched)} file(s)")

    # ---- 2. move the source tree ------------------------------------------------------
    # Guarded, because old_src still exists after the move — it becomes the *parent* of
    # new_src. An unguarded second run moved the whole tree one level deeper
    # (.../sonysoocrecipes/leica/leica/). Move only when Java sources are still sitting
    # directly in the base directory.
    rel_old = "/".join(PACKAGE_BASE.split("."))
    rel_new = "/".join(package.split("."))
    strays = ([f for f in old_src.iterdir() if f.is_file() and f.suffix == ".java"]
              if old_src.is_dir() else [])
    if strays:
        if not args.dry_run:
            move_tree(old_src, new_src)
        report.append(f"moved src/{rel_old} -> src/{rel_new} ({len(strays)} source files)")
    elif new_src.is_dir():
        report.append(f"source tree already at src/{rel_new}")
    else:
        report.append(f"WARNING neither src/{rel_old} nor src/{rel_new} exists")

    # ---- 3. the app name + the APK name -----------------------------------------------
    strings = fork / "res" / "values" / "strings.xml"
    if strings.is_file():
        t = strings.read_text(encoding="utf-8")
        new_t, n = re.subn(r'(<string name="app_name">)[^<]*(</string>)',
                           lambda m: m.group(1) + pack["app_name"] + m.group(2), t)
        if n and not args.dry_run:
            strings.write_text(new_t, encoding="utf-8", newline="")
        report.append(f"app_name -> {pack['app_name']!r}" if n
                      else 'app_name: no <string name="app_name"> found')

    apk = apk_name(pack)
    renamed: list[str] = []
    for f in ("build.sh", "build.cmd"):
        p = fork / f
        if not p.is_file():
            continue
        t = p.read_text(encoding="utf-8")
        if "SonySOOCRecipes.apk" in t:
            t = t.replace("SonySOOCRecipes.apk", apk)
            if not args.dry_run:
                p.write_text(t, encoding="utf-8", newline="")
            renamed.append(f)
    report.append(f"APK output name -> {apk}" + (f" (in {', '.join(renamed)})"
                                                 if renamed else " (nothing to rename)"))

    # ---- 4. icons ---------------------------------------------------------------------
    apply_icons(fork, pack, report, args.dry_run)

    # ---- 5. prove the library name survived -------------------------------------------
    lib_ok = True
    for f in ("jni/Android.mk", "build.sh"):
        p = fork / f
        if p.is_file():
            t = p.read_text(encoding="utf-8")
            if f".{pack['id']}.so" in t:
                lib_ok = False
                report.append(f"HARD FAIL {f}: library name corrupted "
                              f"(lib{LIB_NAME}.{pack['id']}.so)")
            elif LIB_NAME not in t:
                lib_ok = False
                report.append(f"HARD FAIL {f}: library name {LIB_NAME!r} disappeared")

    print(("DRY RUN — nothing written\n" if args.dry_run else "") + "\n".join(report))
    if not lib_ok:
        return 1
    print(f"\nnext: python tools/gen_recipes.py --pack {pack['id']} --fork {args.fork}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
