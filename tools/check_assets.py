#!/usr/bin/env python3
"""Check that every image a document points at actually exists.

A README whose pictures rot is worse than a README with no pictures, and the usual way
that happens is a rename nobody noticed. Images live in docs/assets/ and nowhere else —
nothing may be hotlinked from a third-party host, so a reference that is not a local path
is a finding too. The single exception is a status badge, which only means anything if it
is generated at request time.

    python tools/check_assets.py

Also enforces the sample naming convention from docs/assets/README.md: a file in
samples/ is `<recipe-id>--off.jpg` / `--on.jpg`, and the id has to exist in the catalog.
A typo there would otherwise leave an orphan picture that no document can find.

Also gates the launcher icon sets, which this script used to walk right past: the
all-in-one set `assets/app-icon/` and the per-pack sets `assets/app-icon-packs/<icon_set>/`.
Every pack in `catalog/packs.json` must carry its five densities at the exact pixel size,
or the gate fails — an icon set missing a density, or one that matches no pack's
`icon_set`, would otherwise ship silently. A pack whose set directory does not exist yet
is a **note, not an error**: `apply_pack.py` deliberately falls back to the default set,
so an icon still being drawn must not block the build.
"""

from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "docs" / "assets"
CATALOG = ROOT / "catalog" / "filters.json"
APP_ICON = ROOT / "assets" / "app-icon"
PACK_ICONS = ROOT / "assets" / "app-icon-packs"

SCAN = sorted(
    [ROOT / "README.md", ROOT / "README.zh-CN.md", ROOT / "CHANGELOG.md"]
) + sorted((ROOT / "docs").glob("*.md")) + sorted(ASSETS.glob("*.md"))

IMG_TAG = re.compile(r"""<img[^>]+src\s*=\s*["']([^"']+)["']""", re.I)
MD_IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
SAMPLE = re.compile(r"^(?P<id>.+)--(?P<state>off|on)\.(jpg|jpeg|png)$", re.I)
FENCES = re.compile(r"^(```|~~~).*?^\1", re.M | re.S)

# Status badges are the one legitimate exception to "no third-party hosts": they are
# generated per request, so vendoring them would freeze a build status that is supposed to
# move. Everything else — diagrams, screenshots, samples — has to live in docs/assets/.
BADGE_HOSTS = {"img.shields.io", "badgen.net", "flat.badgen.net", "badge.fury.io"}


def is_badge(ref: str) -> bool:
    """A CI status badge or a shields.io style badge."""
    try:
        parts = urlsplit(ref)
    except ValueError:
        return False
    host = (parts.hostname or "").lower()
    path = parts.path.lower()
    if host in BADGE_HOSTS:
        return True
    # GitHub renders its own workflow status as <owner>/<repo>/actions/workflows/x/badge.svg
    return host == "github.com" and "/actions/workflows/" in path and path.endswith("badge.svg")


def strip_code(text: str) -> str:
    """Assets/ conventions doc shows example <img> markup in a fenced block. Those are
    instructions, not references — without this they read as broken links."""
    return FENCES.sub("", text)


# The five files every launcher icon set must ship, and the pixel size each must be.
# mdpi/hdpi/xhdpi/xxhdpi map to the four drawable densities; icon-512 is the store listing.
ICON_FILES = (
    ("ic_launcher-mdpi.png", 48),
    ("ic_launcher-hdpi.png", 72),
    ("ic_launcher-xhdpi.png", 96),
    ("ic_launcher-xxhdpi.png", 144),
    ("icon-512.png", 512),
)


def png_size(path: Path) -> tuple[int, int]:
    """Return (width, height) of a PNG, or raise ValueError if it is not a valid PNG.

    Parses the IHDR chunk directly so the gate has no third-party dependency and behaves
    identically in CI (where Pillow may be absent) and locally.
    """
    with path.open("rb") as fh:
        if fh.read(8) != b"\x89PNG\r\n\x1a\n":
            raise ValueError("bad signature")
        fh.read(4)  # IHDR length, always 13
        if fh.read(4) != b"IHDR":
            raise ValueError("first chunk is not IHDR")
        buf = fh.read(8)
        if len(buf) < 8:
            raise ValueError("truncated IHDR")
        return struct.unpack(">II", buf)


def check_icon_set(directory: Path, problems: list[str]) -> None:
    """Check one launcher icon set's five files and sizes; append findings to `problems`.

    A missing file or a file that is not a valid PNG, or is the wrong size, is appended as
    a problem (the caller treats these as errors). Whether a *nonexistent* set directory is
    an error is the caller's choice — a pack whose set is still being drawn is only a note,
    whereas the all-in-one set ships today and is mandatory.
    """
    for fname, size in ICON_FILES:
        p = directory / fname
        if not p.is_file():
            problems.append(f"{directory.relative_to(ROOT)}: missing {fname} "
                            f"({size}x{size} expected)")
            continue
        try:
            w, h = png_size(p)
        except ValueError as exc:
            problems.append(f"{directory.relative_to(ROOT)}: {fname} is not a valid PNG "
                            f"({exc})")
            continue
        if w != size or h != size:
            problems.append(f"{directory.relative_to(ROOT)}: {fname} is {w}x{h}, "
                            f"expected {size}x{size}")


def main() -> int:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    known_ids = {f["id"] for f in catalog["filters"]}

    errors: list[str] = []
    notes: list[str] = []
    checked = 0

    for doc in SCAN:
        if not doc.exists():
            continue
        text = strip_code(doc.read_text(encoding="utf-8"))
        refs = [m for m in IMG_TAG.findall(text)] + [m for m in MD_IMG.findall(text)]
        for ref in refs:
            if ref.startswith(("http://", "https://", "data:", "//")):
                if is_badge(ref):
                    notes.append(f"{doc.relative_to(ROOT)}: status badge {ref} — allowed, "
                                 "it has to be generated per request")
                else:
                    errors.append(f"{doc.relative_to(ROOT)}: external image {ref!r} — "
                                  "images must live in docs/assets/, not a third-party host")
                continue
            checked += 1
            target = (doc.parent / ref.split("#")[0]).resolve()
            if not target.exists():
                errors.append(f"{doc.relative_to(ROOT)}: missing image {ref} "
                              f"(looked for {target.relative_to(ROOT)})")

    # sample naming convention
    samples = ASSETS / "samples"
    if samples.exists():
        for f in sorted(samples.iterdir()):
            if not f.is_file():
                continue
            m = SAMPLE.match(f.name)
            if not m:
                errors.append(f"docs/assets/samples/{f.name}: expected "
                              "<recipe-id>--off.jpg or <recipe-id>--on.jpg")
                continue
            if m.group("id") not in known_ids:
                errors.append(f"docs/assets/samples/{f.name}: '{m.group('id')}' is not "
                              "a recipe id in catalog/filters.json")

    # orphan images: present on disk, referenced nowhere
    on_disk = {p.resolve() for p in ASSETS.rglob("*")
               if p.is_file() and p.suffix.lower() in {".svg", ".png", ".jpg", ".jpeg"}}
    referenced: set[Path] = set()
    for doc in SCAN:
        if not doc.exists():
            continue
        text = strip_code(doc.read_text(encoding="utf-8"))
        for ref in IMG_TAG.findall(text) + MD_IMG.findall(text):
            if not ref.startswith(("http", "data:", "//")):
                referenced.add((doc.parent / ref.split("#")[0]).resolve())
    for orphan in sorted(on_disk - referenced):
        notes.append(f"{orphan.relative_to(ROOT)} is not referenced by any document")

    # --- brand-pack launcher icons ------------------------------------------------
    # The gate used to walk only docs/assets/, so the launcher sets were never checked: a
    # density missing from a set, or an icon set that belongs to no pack, would ship
    # silently. The all-in-one set (assets/app-icon/) exists and is mandatory; a pack set
    # may be absent while it is still being drawn, in which case apply_pack.py falls back
    # to the default set and we only note it. See docs/BRAND-PACKS.md.
    icon_problems: list[str] = []
    packs_file = ROOT / "catalog" / "packs.json"
    if packs_file.is_file():
        try:
            packs_doc = json.loads(packs_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            packs_doc = None
        if packs_doc is not None:
            icon_sets_used: set[str] = set()
            for pack in packs_doc["packs"]:
                icon_set = pack.get("icon_set", pack["id"])
                icon_sets_used.add(icon_set)
                d = PACK_ICONS / icon_set
                if not d.is_dir():
                    # apply_pack.py falls back to assets/app-icon/ on purpose, so an
                    # unfinished set must not fail the build — it is a note.
                    notes.append(
                        f"catalog/packs.json: pack {pack['id']!r} has no "
                        f"assets/app-icon-packs/{icon_set}/ yet — it will ship the "
                        f"default icon from assets/app-icon/"
                    )
                    continue
                check_icon_set(d, problems=icon_problems)

            # An icon-set directory that matches no pack's icon_set is a typo waiting to
            # ship: it would never be selected and would sit in the repo unexplained.
            if PACK_ICONS.is_dir():
                for d in sorted(PACK_ICONS.iterdir()):
                    if d.is_dir() and d.name not in icon_sets_used:
                        icon_problems.append(
                            f"{d.relative_to(ROOT)}: matches no pack's icon_set in "
                            f"catalog/packs.json — orphan icon set"
                        )
    # The all-in-one set ships today, so a missing or wrong-size file there is an error.
    check_icon_set(APP_ICON, problems=icon_problems)
    errors.extend(icon_problems)

    print(f"assets   : {ASSETS.relative_to(ROOT)}")
    print(f"images   : {len(on_disk)} on disk | {checked} reference(s) checked")
    print(f"recipes  : {len(known_ids)} known ids for sample naming")
    print()

    for n in notes:
        print(f"  note   {n}")
    for e in errors:
        print(f"  ERROR  {e}")

    if errors:
        print(f"\nFAILED — {len(errors)} error(s)")
        return 1
    print(f"OK — every referenced image exists, no external hosts ({len(notes)} note(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
