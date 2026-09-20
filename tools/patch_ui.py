#!/usr/bin/env python3
"""Replay the frosted two-bar UI onto one upstream checkout, in place.

    python tools/patch_ui.py --fork build/recipe-lab-sony-pmca
    python tools/patch_ui.py --fork DIR --dry-run
    python tools/patch_ui.py --fork DIR --check

Why this exists instead of the layout simply being committed to the fork: the fork IS a
build artifact. tools/build_apk.sh resets build/recipe-lab-sony-pmca to the pinned
upstream revision before every single build (prepare_fork runs git reset --hard and git
clean -fdxq), so anything edited by hand under build/ survives zero builds. This script
re-applies the same change every time, from tracked inputs only:

  * catalog/ui-theme.json   every colour in one reviewable place
  * assets/ui/main.xml      the two-bar layout
  * assets/fonts/           the bundled faces, and the licence text that has to travel with
                            them: the OFL's one redistribution condition, see NOTICE.md

It rewrites PickerView.java in full from a tracked template (assets/ui/PickerView.java):
the in-camera FN browser. MainActivity's own Java is touched only by colour anchors (see
ANCHORS below) and by the browser-key retarget, because its layout keeps every id MainActivity
binds. PickerView is a leaf view — no other class depends on its internals — so replacing it
whole is safe and reviewable in one file, and the same apply step fills its {ui_package} token
per brand pack.

Every Java edit is anchored on the EXACT upstream string it replaces, and an anchor that
has vanished is a hard failure rather than a silent no-op. Upstream refactors its own
code; if this script quietly stopped matching, we would ship an APK that lost its theme
and looked fine in CI. Failing loudly is the cheaper outcome.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_THEME = ROOT / "catalog" / "ui-theme.json"
UI_LAYOUT = ROOT / "assets" / "ui" / "main.xml"
FONT_DIR = ROOT / "assets" / "fonts"
PICKER_TEMPLATE = ROOT / "assets" / "ui" / "PickerView.java"
DEFAULT_FORK = ROOT / "build" / "recipe-lab-sony-pmca"

# The Android package of the all-in-one app. assets/ui/main.xml references the custom
# views (HintBar / PickerView / PromptView) by their fully-qualified class name, and that
# name CONTAINS the package - which changes per brand pack (...sonysoocrecipes.leica).
# The layout therefore carries a {ui_package} token that this script fills from the
# checkout's own AndroidManifest.xml, so a pack's layout points at the pack's class and not
# the all-in-one's. A hardcoded base package here would ship a brand-pack APK whose layout
# references a class that does not exist on that package - it would inflate and crash on
# launch. tools/apply_pack.py renames everything else; this token is the one piece of the
# layout it cannot, because apply_pack runs and THEN this script overwrites main.xml.
BASE_PACKAGE = "com.hairuoliu.sonysoocrecipes"
PKG_TOKEN = "{ui_package}"

HEX8 = re.compile(r"^#[0-9A-Fa-f]{8}$")

# The ids MainActivity binds with findViewById, and the class each one is cast to
# (None = bound to a plain View, so any class will do). If assets/ui/main.xml ever drops
# one of these the app compiles and then dies on launch, so the test asserts all of them.
REQUIRED_IDS = {
    "surface": "SurfaceView",
    "panel": None,
    "chipscroll": "HorizontalScrollView",
    "name": "TextView",
    "badge": "TextView",
    "tag": "TextView",
    "count": "TextView",
    "meta": "TextView",
    "hints": "HintBar",
    "mini": "TextView",
    "toast": "TextView",
    "prompt": "PromptView",
    "picker": "PickerView",
    "chips": "LinearLayout",
}

# Drawables this script writes from the theme. Anything else main.xml points at must come
# from upstream (the badge_* status fills do), and that split is asserted too.
GENERATED_DRAWABLES = ("chip", "chip_hi", "chip_sel", "pill", "toast_bg", "bar_top", "bar_bottom")

CONSTANTS_ANCHOR = (
    "    private static final int ACCENT = 0xFFF2B85C, INK = 0xFF1A1208, "
    "WHITE = 0xFFFFFFFF, DIM = 0x99FFFFFF;"
)


def java_literal(colour: str) -> str:
    """'#FFF2B85C' -> '0xFFF2B85C'. One string serves XML and Java; this adapts it."""
    text = colour.strip()
    if not HEX8.match(text):
        raise SystemExit(f"{colour!r} is not an #AARRGGBB colour (see catalog/ui-theme.json)")
    return "0x" + text[1:].upper()


def load_theme(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    for key, value in sorted(data.items()):
        if key.startswith("$"):
            continue
        if isinstance(value, str) and value.startswith("#"):
            java_literal(value)      # raises on a malformed colour before anything is written
    return data


def constants_for(theme: dict) -> str:
    """The replacement for MainActivity's one colour-constants line.

    The identifiers keep their upstream names on purpose: every call site refers to WHITE
    and DIM by those names, and renaming them would mean chasing each one. What changes is
    the value - WHITE is now the dark primary text on a light bar, and ACCENT_TXT is new,
    because gold that reads as a chip FILL disappears as TEXT on a frosted background.
    """
    return (
        "    // Patched by tools/patch_ui.py for the frosted theme - see catalog/ui-theme.json.\n"
        "    // WHITE is the primary text colour on the light bar and DIM the secondary one, so\n"
        "    // the upstream identifiers now name dark colours: they were kept so no call site\n"
        "    // has to change. ACCENT stays the gold used as a FILL; ACCENT_TXT is the darker\n"
        "    // bronze used wherever the accent is drawn as TEXT, which needs the contrast.\n"
        f"    private static final int ACCENT = {java_literal(theme['accent'])}, "
        f"INK = {java_literal(theme['accent_ink'])}, "
        f"WHITE = {java_literal(theme['ink'])}, "
        f"DIM = {java_literal(theme['ink_dim'])}, "
        f"ACCENT_TXT = {java_literal(theme['accent_text'])};"
    )


LAYOUT_TOKENS = {
    "{app_title_visibility}": "app_title_visibility",
    "{tag_visibility}": "tag_visibility",
    "{legend_visibility}": "legend_visibility",
}

# Colour tokens for the brand-browser template (assets/ui/PickerView.java). Every key maps
# to a catalog/ui-theme.json entry, so the browser's colours live in exactly one place, the
# same as the main screen. {ui_package} is the one exception: it is filled from the checkout's
# own AndroidManifest.xml, so a pack's browser references the pack's renamed class.
PICKER_TOKENS = {
    "{ui_package}": None,
    "{picker_bg}": "frost_top_start",
    "{picker_ink}": "ink",
    "{picker_dim}": "ink_dim",
    "{picker_accent}": "accent",
    "{picker_accent_ink}": "accent_ink",
    "{picker_rule}": "chip_idle",
}
# A wrong value here is not cosmetic: aapt turns android:visibility into an int flag, and a
# string it does not recognise makes the layout fail to INFLATE - the app then dies on
# launch, at which point the error says nothing about the theme file that caused it. So the
# two on-screen toggles are validated here, where the message can name the bad key.
VISIBILITIES = ("visible", "invisible", "gone")


def package_of(fork: Path) -> str:
    """The Android package this checkout builds as, from its own manifest.

    Used to fill {ui_package} in the layout. A pack checkout has been renamed to
    ...sonysoocrecipes.<id> by tools/apply_pack.py before this runs, so reading it back
    from the manifest (rather than assuming the base package) is what keeps a pack's
    custom-view references pointing at the pack's own classes.
    """
    manifest = fork / "AndroidManifest.xml"
    if not manifest.is_file():
        raise SystemExit(f"{fork} has no AndroidManifest.xml — cannot determine its package")
    m = re.search(r'package="([^"]+)"', manifest.read_text(encoding="utf-8"))
    if not m:
        raise SystemExit(f"{manifest} declares no package attribute")
    return m.group(1)


def layout_for(theme: dict, package: str = BASE_PACKAGE) -> str:
    """assets/ui/main.xml with the toggles and the package token filled in.

    package defaults to the all-in-one base so callers that only render the default app
    (the preview tool, the tests) need not pass one. A real build passes the checkout's
    own package so brand packs reference their renamed classes.
    """
    text = UI_LAYOUT.read_text(encoding="utf-8")
    for token, key in LAYOUT_TOKENS.items():
        value = str(theme.get(key, "")).strip()
        if value not in VISIBILITIES:
            raise SystemExit(f"{key} is {value!r} in catalog/ui-theme.json - expected one "
                             f"of {', '.join(VISIBILITIES)}")
        text = text.replace(token, value)
    text = text.replace(PKG_TOKEN, package)
    if "{" in text:
        raise SystemExit("assets/ui/main.xml still holds an unfilled {...} token - "
                         "every token must be listed in LAYOUT_TOKENS (the package token "
                         "is filled from the checkout's AndroidManifest.xml)")
    return text


def picker_for(theme: dict, package: str = BASE_PACKAGE) -> str:
    """assets/ui/PickerView.java with colours and the package token filled in.

    The picker is upstream code replayed whole (not patched line-by-line), so this is the
    one function that turns the tracked template into the file the fork compiles. `package`
    defaults to the all-in-one base so callers that only render the default app need not pass
    one; a real build passes the checkout's own package so a pack's browser references its
    renamed class.
    """
    text = PICKER_TEMPLATE.read_text(encoding="utf-8")
    for token, key in PICKER_TOKENS.items():
        if key is None:
            text = text.replace(token, package)
        else:
            text = text.replace(token, java_literal(theme[key]))
    leftover = [t for t in PICKER_TOKENS if t in text]
    if leftover:
        raise SystemExit("assets/ui/PickerView.java still holds unfilled token(s) "
                         f"{leftover} — every token must be listed in PICKER_TOKENS "
                         "(the package token is filled from the checkout's AndroidManifest.xml)")
    return text


def drawables_for(theme: dict) -> dict[str, str]:
    """The theme as Android drawables. See ui-theme.json for why the frost is simulated."""

    def shape(body: str) -> str:
        return ('<?xml version="1.0" encoding="utf-8"?>\n'
                '<shape xmlns:android="http://schemas.android.com/apk/res/android" '
                'android:shape="rectangle">\n' + body + '</shape>\n')

    r = theme["bar_radius_dp"]
    # The bars are opaque enough (~0.9) that the composite stays light whatever the camera
    # behind them is doing, which is what keeps dark text legible. See ui-theme.json.
    return {
        "bar_top.xml": shape(
            f'    <gradient android:angle="270" android:startColor="{theme["frost_top_start"]}" '
            f'android:endColor="{theme["frost_top_end"]}" />\n'
            f'    <corners android:topLeftRadius="0dp" android:topRightRadius="0dp" '
            f'android:bottomLeftRadius="{r}dp" android:bottomRightRadius="{r}dp" />\n'
            f'    <stroke android:width="1dp" android:color="{theme["frost_rim"]}" />\n'),
        "bar_bottom.xml": shape(
            f'    <gradient android:angle="270" android:startColor="{theme["frost_bottom_start"]}" '
            f'android:endColor="{theme["frost_bottom_end"]}" />\n'
            f'    <corners android:topLeftRadius="{r}dp" android:topRightRadius="{r}dp" '
            f'android:bottomLeftRadius="0dp" android:bottomRightRadius="0dp" />\n'
            f'    <stroke android:width="1dp" android:color="{theme["frost_rim"]}" />\n'),
        "chip.xml": shape(
            f'    <solid android:color="{theme["chip_idle"]}" />\n'
            f'    <corners android:radius="9dp" />\n'
            f'    <stroke android:width="1dp" android:color="{theme["chip_rim"]}" />\n'),
        "chip_hi.xml": shape(
            f'    <solid android:color="{theme["chip_hi"]}" />\n'
            f'    <corners android:radius="9dp" />\n'),
        "chip_sel.xml": shape(
            f'    <solid android:color="{theme["accent"]}" />\n'
            f'    <corners android:radius="9dp" />\n'),
        "pill.xml": shape(
            f'    <solid android:color="{theme["pill_fill"]}" />\n'
            f'    <corners android:radius="10dp" />\n'
            f'    <stroke android:width="1dp" android:color="{theme["pill_rim"]}" />\n'),
        "toast_bg.xml": shape(
            f'    <solid android:color="{theme["toast_fill"]}" />\n'
            f'    <corners android:radius="10dp" />\n'
            f'    <stroke android:width="1dp" android:color="{theme["toast_rim"]}" />\n'),
    }


def anchors(theme: dict) -> list[tuple[str, str, str, str]]:
    """(file, old-text, new-text, label) edits, applied to whichever copy of the file the
    checkout holds - apply_pack.py may already have moved it deeper into its package."""
    return [
        ("MainActivity.java", CONSTANTS_ANCHOR, constants_for(theme), "colour constants"),
        ("MainActivity.java",
         "name.setTextColor(row == 0 ? ACCENT : WHITE);",
         "name.setTextColor(row == 0 ? ACCENT_TXT : WHITE);",
         "recipe-name colour"),
        ("MainActivity.java",
         "tag.setTextColor(edit[R_PE] != 0 ? ACCENT : 0xDDFFFFFF);",
         f"tag.setTextColor(edit[R_PE] != 0 ? ACCENT_TXT : {java_literal(theme['tag_idle'])});",
         "tag colour"),
        ("MainActivity.java",
         "chipLabel[i].setTextColor(foc ? INK : sel ? ACCENT : DIM);",
         "chipLabel[i].setTextColor(foc ? INK : sel ? ACCENT_TXT : DIM);",
         "chip-label colour"),
        ("MainActivity.java",
         "chipValue[i].setTextColor(foc ? INK : ch ? ACCENT : WHITE);",
         "chipValue[i].setTextColor(foc ? INK : ch ? ACCENT_TXT : WHITE);",
         "chip-value colour"),
        # HintBar owns no colours - it draws everything through Legend, so Legend is where
        # the key-legend glyphs get inverted. Left white they vanish on a frosted bar.
        ("Legend.java",
         "fill.setColor(0xCCFFFFFF)",
         f"fill.setColor({java_literal(theme['legend_glyph'])})",
         "legend glyph fill"),
        ("Legend.java",
         "stroke.setColor(0xCCFFFFFF)",
         f"stroke.setColor({java_literal(theme['legend_stroke'])})",
         "legend glyph stroke"),
        ("Legend.java",
         "text.setColor(0x99FFFFFF)",
         f"text.setColor({java_literal(theme['legend_label'])})",
         "legend label"),
        ("Legend.java",
         "keyText.setColor(0xCCFFFFFF)",
         f"keyText.setColor({java_literal(theme['legend_key'])})",
         "legend key text"),
        # The FN browser is now a single column (see assets/ui/PickerView.java), so there is
        # no brand/groups rail to switch between. UP/DOWN scrolls every recipe (nextRecipe)
        # instead of jumping a group or stepping inside one — otherwise the picker could not
        # reach a recipe in the next category. LEFT/RIGHT still toggles browserCol, but the
        # picker ignores it, so the keys are harmless.
        ("MainActivity.java",
         "case K_UP: case K_WHEEL_CCW: case K_DIAL_CCW: if (browserCol == 0) nextGroup(-1); else nextInGroup(-1); return true;",
         "case K_UP: case K_WHEEL_CCW: case K_DIAL_CCW: nextRecipe(-1); return true;   // single-column picker",
         "picker up/down scrolls all recipes"),
        ("MainActivity.java",
         "case K_DOWN: case K_WHEEL_CW: case K_DIAL_CW: if (browserCol == 0) nextGroup(+1); else nextInGroup(+1); return true;",
         "case K_DOWN: case K_WHEEL_CW: case K_DIAL_CW: nextRecipe(+1); return true;   // single-column picker",
         "picker down/up scrolls all recipes"),
    ] + font_java(theme)


# The two packaging lines that decide whether anything under assets/ reaches the APK.
# Upstream ships no assets/, so its aapt call has no -A flag at all - and aapt silently
# omits the directory rather than complaining, which is why this is worth an anchor: if the
# flag is lost, the font is not "missing", the app just quietly renders Droid Sans.
AAPT_SH = r'"$BT/aapt" package -f -M "$MANIFEST" -S res -I "$AJ" -F out/unaligned.apk'
AAPT_CMD = (r'"%BT%\aapt.exe" package -f -M AndroidManifest.xml -S res -I "%AJ%" '
            r'-F out\unaligned.apk || exit /b 1')

# Anchors for MainActivity's font plumbing. buildChips() is the call site: it has to run
# first, because applyFont() walks the chip views that buildChips() just created.
FONT_CALL_ANCHOR = "        buildChips();"
DP_METHOD_ANCHOR = ("    private int dp(float v) { "
                    "return (int) (v * getResources().getDisplayMetrics().density + 0.5f); }")


def fonts_for(theme: dict) -> list[str]:
    """The .ttf filenames the theme names, checked against assets/fonts/ before use.

    A name the theme invents would otherwise fail much later and much quieter: the asset
    would simply not exist inside the APK, createFromAsset throws, the catch swallows it,
    and the app renders the system font — indistinguishable from success unless you look.
    """
    names = [str(theme.get("font_regular", "")), str(theme.get("font_bold", ""))]
    for name in names:
        if not name:
            raise SystemExit("catalog/ui-theme.json needs both font_regular and font_bold")
        if not (FONT_DIR / name).is_file():
            raise SystemExit(f"catalog/ui-theme.json names {name!r} but there is no "
                             f"assets/fonts/{name} — drop the .ttf in, or pick another face")
    return names


def font_payloads(theme: dict) -> dict[str, bytes]:
    """Every file in assets/fonts/, by name — the faces the theme names, and everything
    else sitting beside them.

    Not just the two .ttf files, and the extras are not decoration. assets/fonts/ also
    holds Quicksand's OFL text, and the OFL's single redistribution condition is that the
    licence travels with the font it covers. Shipping the face inside the APK while the
    licence stayed behind in the repository is precisely the omission NOTICE.md says must
    not happen — and it is invisible from every angle: a missing text file changes nothing
    about how the app looks, so only an assertion like the one in tests/test_ui_theme.py
    can catch it.

    fonts_for() still runs first: a theme naming a face that is not here must fail the
    build with the face's own name, not sail through as a smaller payload.
    """
    fonts_for(theme)
    return {p.name: p.read_bytes()
            for p in sorted(FONT_DIR.iterdir()) if p.is_file()}


def font_java(theme: dict) -> list[tuple[str, str, str, str]]:
    """MainActivity + Legend edits that bind the bundled face.

    Two things are deliberate. The loads are wrapped in a Throwable catch because a missing
    or corrupt asset throws at runtime, not compile time, and the only acceptable outcome
    is 'fall back to the system font' — a camera app that dies on launch because a .ttf is
    missing is absurd. And the bold face falls back to a synthesised bold rather than to
    regular, so a theme that names only one file still reads as bold where it should.
    """
    regular, bold = fonts_for(theme)
    return [
        ("MainActivity.java", FONT_CALL_ANCHOR,
         FONT_CALL_ANCHOR + "\n        applyFont();",
         "applyFont() call site"),
        ("MainActivity.java", DP_METHOD_ANCHOR,
         DP_METHOD_ANCHOR + "\n\n"
         "    // Patched by tools/patch_ui.py for the bundled font - see catalog/ui-theme.json.\n"
         "    // minSdkVersion 10 has no rounded system font and no android:fontFamily, so the\n"
         "    // face is loaded from assets/ and bound to the views here instead.\n"
         "    private static Typeface uiFontRegular, uiFontBold;\n"
         "    private static boolean uiFontTried;\n"
         "\n"
         "    private void uiFontLoad() {\n"
         "        if (uiFontTried) return;\n"
         "        uiFontTried = true;\n"
         "        try {\n"
         f'            uiFontRegular = Typeface.createFromAsset(getAssets(), "fonts/{regular}");\n'
         f'            uiFontBold = Typeface.createFromAsset(getAssets(), "fonts/{bold}");\n'
         "        } catch (Throwable t) { uiFontRegular = null; uiFontBold = null; }\n"
         "    }\n"
         "\n"
         "    private void applyFont() {\n"
         "        uiFontLoad();\n"
         "        if (uiFontRegular == null) return;\n"
         "        Typeface f = uiFontRegular;\n"
         "        Typeface fb = uiFontBold != null ? uiFontBold : Typeface.create(f, Typeface.BOLD);\n"
         "        TextView t = (TextView) findViewById(R.id.title);\n"
         "        if (t != null) t.setTypeface(f);\n"
         "        name.setTypeface(fb); badge.setTypeface(fb); tag.setTypeface(fb);\n"
         "        count.setTypeface(f); meta.setTypeface(f); mini.setTypeface(fb); toast.setTypeface(f);\n"
         "        for (int i = 0; i < N; i++) {\n"
         "            if (chipLabel[i] != null) chipLabel[i].setTypeface(f);\n"
         "            if (chipValue[i] != null) chipValue[i].setTypeface(fb);\n"
         "        }\n"
         "        Legend.FONT = f;\n"
         "    }",
         "font plumbing"),
        # Legend draws with Canvas, so a TextView-level font never reaches it. The typeface
        # is applied in setScale() rather than the constructor because HintBar builds its
        # Legend while the layout inflates - before MainActivity has had a chance to load
        # the asset. setScale() runs on every measure and draw, so it picks it up late.
        ("Legend.java", "import android.graphics.Path;",
         "import android.graphics.Path;\nimport android.graphics.Typeface;",
         "Legend Typeface import"),
        ("Legend.java", "    private final Path path = new Path();",
         "    public static Typeface FONT;   // set by MainActivity.applyFont()\n"
         "    private final Path path = new Path();",
         "Legend FONT field"),
        ("Legend.java", "        text.setTextSize(10 * d * k);",
         "        text.setTextSize(10 * d * k);\n"
         "        if (FONT != null) { text.setTypeface(FONT); keyText.setTypeface(FONT); }",
         "Legend paint typeface"),
    ]


def script_edits() -> list[tuple[str, str, str, str]]:
    """(path in the fork, old, new, label) for files that are not under src/.

    build.sh and build.cmd are upstream's own build scripts and they explicitly say to keep
    each other in step, so both get the same flag. Only the packaging line is touched; the
    earlier `aapt package -m -J out/gen` invocation does not need -A.
    """
    return [
        ("build.sh", AAPT_SH, AAPT_SH.replace("-S res ", "-S res -A assets "),
         "aapt ships assets/"),
        ("build.cmd", AAPT_CMD, AAPT_CMD.replace("-S res ", "-S res -A assets "),
         "aapt ships assets/"),
    ]


def find_source(fork: Path, name: str) -> Path:
    """One copy of name under fork/src - a pack checkout nests it one package deeper."""
    hits = [p for p in (fork / "src").rglob(name) if ".git" not in p.parts]
    if len(hits) != 1:
        raise SystemExit(f"expected exactly one {name} under {fork / 'src'}, found {len(hits)}")
    return hits[0]


def write_file(path: Path, text: str, dry: bool, report: list[str], label: str) -> None:
    """Write only when the content actually differs, so a re-run is a genuine no-op."""
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        report.append(f"{label}: already current")
        return
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="")
    report.append(f"{label}: {'would write' if dry else 'written'}")


def write_binary(path: Path, data: bytes, dry: bool, report: list[str], label: str) -> None:
    """Same idempotency rule as write_file, for the .ttf payloads."""
    if path.is_file() and path.read_bytes() == data:
        report.append(f"{label}: already current")
        return
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    report.append(f"{label}: {'would write' if dry else 'written'}")


def apply_text_edit(path: Path, old: str, new: str, dry: bool,
                   report: list[str], problems: list[str], label: str) -> None:
    """One exact-string replacement, refusing to guess when neither side matches.

    The NEW text is looked for FIRST, and that order is load-bearing: several edits append
    to the line they anchor on (buildChips(); -> buildChips(); + applyFont();), so the old
    string is a substring of the new one. Testing old first would match again on every
    re-run and append the block once per build.
    """
    if not path.is_file():
        problems.append(f"{label}: {path} does not exist")
        return
    text = path.read_text(encoding="utf-8")
    if new in text:
        report.append(f"{label}: already applied")
    elif old in text:
        if not dry:
            path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="")
        report.append(f"{label}: patched")
    else:
        problems.append(f"{label}: neither the upstream line nor the patched one was found "
                        f"in {path.name} - upstream moved it, re-check this anchor")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fork", type=Path, default=DEFAULT_FORK,
                    help="upstream checkout to patch (default: build/recipe-lab-sony-pmca)")
    ap.add_argument("--theme", type=Path, default=DEFAULT_THEME)
    ap.add_argument("--dry-run", action="store_true", help="report, change nothing")
    ap.add_argument("--check", action="store_true",
                    help="verify the checkout already carries this theme")
    args = ap.parse_args()

    fork: Path = args.fork
    report: list[str] = []
    problems: list[str] = []

    # Everything the theme is asked for is read here, before a single file is written, so a
    # theme missing a key fails with the key's own name instead of a bare KeyError from
    # somewhere inside drawables_for. The keys are read by indexing rather than by declaring
    # a required-key list on purpose: a list would be a second copy of the same knowledge,
    # and the copy is what would go stale when a key is added.
    try:
        theme = load_theme(args.theme)
        drawables = drawables_for(theme)
        edits = anchors(theme)
        fonts = font_payloads(theme)
    except KeyError as exc:
        # from None: the KeyError is noise here, the named key is the whole message.
        raise SystemExit(f"catalog/ui-theme.json defines no {exc.args[0]!r} key — every "
                         f"key the patcher reads has to be there") from None
    scripts = script_edits()

    if not (fork / "AndroidManifest.xml").is_file():
        raise SystemExit(f"{fork} does not look like an upstream checkout "
                         "(no AndroidManifest.xml)")
    if not UI_LAYOUT.is_file():
        raise SystemExit(f"missing {UI_LAYOUT.relative_to(ROOT)} - this is the layout input")

    # The package this checkout builds as - fills {ui_package} so a pack's custom views
    # reference the pack's renamed classes rather than the all-in-one's.
    package = package_of(fork)
    layout_text = layout_for(theme, package)

    # ---- check mode ----------------------------------------------------------------
    if args.check:
        target = fork / "res" / "layout" / "main.xml"
        if not target.is_file() or target.read_text(encoding="utf-8") != layout_text:
            problems.append("res/layout/main.xml is not the two-bar layout from assets/ui/")
        for name, text in drawables.items():
            p = fork / "res" / "drawable" / name
            if not p.is_file() or p.read_text(encoding="utf-8") != text:
                problems.append(f"res/drawable/{name} does not match the theme")
        for fname, _old, new, label in edits:
            src = find_source(fork, fname)
            if new not in src.read_text(encoding="utf-8"):
                problems.append(f"{fname}: {label} is not patched")
        try:
            pv = find_source(fork, "PickerView.java")
        except SystemExit as exc:
            problems.append(str(exc))
        else:
            if not (pv.is_file() and pv.read_text(encoding="utf-8") == picker_for(theme, package)):
                problems.append("src/.../PickerView.java is not the single-column white "
                                "browser from assets/ui/PickerView.java")
        for name in fonts:
            if not (fork / "assets" / "fonts" / name).is_file():
                problems.append(f"assets/fonts/{name} is not in the checkout - it would "
                                f"not reach the APK")
        for rel, _old, new, label in scripts:
            p = fork / rel
            if not p.is_file() or new not in p.read_text(encoding="utf-8"):
                problems.append(f"{rel}: {label} is not patched - assets/ would not ship")
        if problems:
            for p in problems:
                print("FAIL " + p)
            return 1
        print(f"OK — {fork} carries the frosted two-bar theme "
              f"({len(drawables)} drawables, {len(edits)} Java edits, "
              f"{len(fonts)} font file(s), {len(scripts)} build-script edits)")
        return 0

    # ---- apply ---------------------------------------------------------------------
    write_file(fork / "res" / "layout" / "main.xml", layout_text, args.dry_run, report,
               "layout/main.xml")
    for name, text in drawables.items():
        write_file(fork / "res" / "drawable" / name, text, args.dry_run, report,
                   f"drawable/{name}")

    for name, data in fonts.items():
        write_binary(fork / "assets" / "fonts" / name, data,
                     args.dry_run, report, f"assets/fonts/{name}")

    # The brand browser: replace the upstream two-column black panel with the single-column
    # white one. Done here, after apply_pack has renamed the package, so the {ui_package}
    # token in assets/ui/PickerView.java fills to this pack's renamed class.
    try:
        picker = find_source(fork, "PickerView.java")
    except SystemExit as exc:
        problems.append(str(exc))
    else:
        write_file(picker, picker_for(theme, package), args.dry_run, report,
                   "java: PickerView.java")

    for fname, old, new, label in edits:
        apply_text_edit(find_source(fork, fname), old, new, args.dry_run, report, problems,
                        f"java: {fname} {label}")

    for rel, old, new, label in scripts:
        apply_text_edit(fork / rel, old, new, args.dry_run, report, problems,
                        f"{rel}: {label}")

    print(("DRY RUN — nothing written\n" if args.dry_run else "") + "\n".join(report))
    if problems:
        print()
        for p in problems:
            print("FAIL " + p)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
