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

import cataloglib

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_THEME = ROOT / "catalog" / "ui-theme.json"
DEFAULT_PACKS = ROOT / "catalog" / "packs.json"
UI_LAYOUT = ROOT / "assets" / "ui" / "main.xml"
FONT_DIR = ROOT / "assets" / "fonts"
PICKER_TEMPLATE = ROOT / "assets" / "ui" / "PickerView.java"
EDITOR_TEMPLATE = ROOT / "assets" / "ui" / "EditorView.java"
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
BASE_PACKAGE = cataloglib.package_base(DEFAULT_PACKS)
PKG_TOKEN = "{ui_package}"

HEX8 = re.compile(r"^#[0-9A-Fa-f]{8}$")

# The ids MainActivity binds with findViewById, and the class each one is cast to
# (None = bound to a plain View, so any class will do). If assets/ui/main.xml ever drops
# one of these the app compiles and then dies on launch, so the test asserts all of them.
REQUIRED_IDS = {
    "surface": "SurfaceView",
    "panel": None,
    # v0.88: the editor (MainActivity.openEditor) hides the top bar so only the compact
    # bottom bar is on screen, which means MainActivity has to hold a reference to it.
    "topbar": "RelativeLayout",
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
    "editor": "EditorView",
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
    # v0.93: the parameter summary is off by default — the bar reads name · brand ·
    # position only, and MainActivity still writes the summary (the view stays declared,
    # so flipping the theme brings it back without touching Java).
    "{meta_visibility}": "meta_visibility",
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
# Same idea for assets/ui/EditorView.java (v0.90). It is a new file rather than an upstream
# one, but it is replayed whole for exactly the reason PickerView is: build/ is reset to
# upstream before every build, so a tracked template is the only thing that survives.
EDITOR_TOKENS = {
    "{ui_package}": None,
    "{editor_bg}": "frost_bottom_start",
    "{editor_ink}": "ink",
    "{editor_dim}": "ink_dim",
    "{editor_accent}": "accent",
    "{editor_accent_ink}": "accent_ink",
    "{editor_rule}": "chip_idle",
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


def render_java_template(theme: dict, package: str, template: Path,
                         tokens: dict, name: str) -> str:
    """A tracked .java template with its colour + package tokens filled in.

    PickerView and EditorView are both replayed whole (not patched line-by-line) because
    build/ is reset to upstream before every build and a tracked template is the only thing
    that survives. The two differ only in which template file and which token table they
    use, so the fill loop lives here once. `package` defaults to the all-in-one base at the
    call sites; a real build passes the checkout's own package so a pack's view references
    its renamed class.
    """
    text = template.read_text(encoding="utf-8")
    for token, key in tokens.items():
        text = text.replace(token, package if key is None else java_literal(theme[key]))
    leftover = [t for t in tokens if t in text]
    if leftover:
        raise SystemExit(f"assets/ui/{name}.java still holds unfilled token(s) "
                         f"{leftover} — every token must be listed in {name.upper()}_TOKENS "
                         "(the package token is filled from the checkout's AndroidManifest.xml)")
    return text


def picker_for(theme: dict, package: str = BASE_PACKAGE) -> str:
    """assets/ui/PickerView.java with colours and the package token filled in.

    The picker is upstream code replayed whole (not patched line-by-line), so this is the
    one function that turns the tracked template into the file the fork compiles. `package`
    defaults to the all-in-one base so callers that only render the default app need not pass
    one; a real build passes the checkout's own package so a pack's browser references its
    renamed class.
    """
    return render_java_template(theme, package, PICKER_TEMPLATE, PICKER_TOKENS, "PickerView")


def editor_for(theme: dict, package: str = BASE_PACKAGE) -> str:
    """assets/ui/EditorView.java with colours and the package token filled in.

    Same replay pattern as picker_for: the editor is a tracked template rewritten whole
    over the upstream checkout, because build/ is reset before every build and a tracked
    file is the only thing that survives.
    """
    return render_java_template(theme, package, EDITOR_TEMPLATE, EDITOR_TOKENS, "EditorView")


def drawables_for(theme: dict) -> dict[str, str]:
    """The theme as Android drawables. See ui-theme.json for why the frost is simulated."""

    def shape(body: str) -> str:
        return ('<?xml version="1.0" encoding="utf-8"?>\n'
                '<shape xmlns:android="http://schemas.android.com/apk/res/android" '
                'android:shape="rectangle">\n' + body + '</shape>\n')

    r = theme["bar_radius_dp"]
    # The bars are opaque enough (~0.9) that the composite stays light whatever the camera
    # behind them is doing, which is what keeps dark text legible. See ui-theme.json.
    # v0.88: bar_top rounds ALL FOUR corners. It used to round only the bottom two, which
    # was correct when the bar was a slab glued to y=0 and wrong the moment the layout gave
    # it a top margin — a slab with square top corners floating 14dp down is the "cropped /
    # misaligned" look the user reported against the mock, whose topbar is a fully rounded
    # pill. bar_bottom keeps its top-only rounding on purpose: it is still flush with the
    # bottom edge, exactly like the mock's sheet.
    return {
        "bar_top.xml": shape(
            f'    <gradient android:angle="270" android:startColor="{theme["frost_top_start"]}" '
            f'android:endColor="{theme["frost_top_end"]}" />\n'
            f'    <corners android:radius="{r}dp" />\n'
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
        # v0.89: the selected-but-not-focused chip is the "胶囊状的选中指示栏" — it has to
        # read as a capsule, not as a faint tint. The accent rim is what makes it a shape:
        # at 15% alpha with no stroke the selected row was indistinguishable from an idle one
        # on a bright scene, which is why pressing UP looked like it did nothing.
        "chip_hi.xml": shape(
            f'    <solid android:color="{theme["chip_hi"]}" />\n'
            f'    <corners android:radius="9dp" />\n'
            f'    <stroke android:width="1dp" android:color="{theme["accent"]}" />\n'),
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


# v0.86 — the "strength" (强度) parameter. A 0–100% global multiplier on the recipe's
# look: it scales the four continuous Creative-Style params (saturation / contrast /
# sharpness / exposure) by their deviation from neutral, so 50% applies the recipe's
# character at half strength. It lives in prefs (not the camera) and is never written as
# its own slot — only the scaled sat/con/sharp/ev reach the hardware. The top bar hide is
# left to the existing AEL/DISP overlay cycle (state 2 = pure preview), so no new key is
# bound and chip navigation (K_UP = recipe-line ⇄ chip-line) is untouched.
STRENGTH = [
    # --- the row index + a default; N = ROW_ID.length grows to 16 automatically -------
    ("MainActivity.java",
     "    private static final int R_RECIPE = 0, R_STYLE = 1, R_SAT = 2, R_CON = 3, R_SHARP = 4, R_MTX = 5, R_PE = 6, R_SUB = 7, R_WBMODE = 8, R_KELVIN = 9, R_AB = 10, R_GM = 11, R_EV = 12, R_DRO = 13, R_QUAL = 14;",
     "    private static final int R_RECIPE = 0, R_STYLE = 1, R_SAT = 2, R_CON = 3, R_SHARP = 4, R_MTX = 5, R_PE = 6, R_SUB = 7, R_WBMODE = 8, R_KELVIN = 9, R_AB = 10, R_GM = 11, R_EV = 12, R_DRO = 13, R_QUAL = 14, R_STR = 15;\n    private static final int STR_DEFAULT = 100;",
     "strength row index"),
    # --- append the new row to every parallel array (id -5 = derived, never written) ----
    ("MainActivity.java",
     "    private static final int[] ROW_ID = { 0, ID_STYLE, ID_SAT, ID_CON, ID_SHARP, ID_PP_NO, ID_PE, -1 /* depends on effect */, ID_WB_MODE, ID_WB_TEMP, ID_WB_AB, ID_WB_GM, ID_EV, ID_DRO, -2 /* two slots */ };",
     "    private static final int[] ROW_ID = { 0, ID_STYLE, ID_SAT, ID_CON, ID_SHARP, ID_PP_NO, ID_PE, -1 /* depends on effect */, ID_WB_MODE, ID_WB_TEMP, ID_WB_AB, ID_WB_GM, ID_EV, ID_DRO, -2 /* two slots */, -5 /* strength: derived multiplier, never written */ };",
     "strength row id"),
    ("MainActivity.java",
     "    private static final int[] ROW_MIN = { 0, 1, -16, -8, -8, 0, 0, 0, 0, 25, -7, -7, -15, 0, 0 };",
     "    private static final int[] ROW_MIN = { 0, 1, -16, -8, -8, 0, 0, 0, 0, 25, -7, -7, -15, 0, 0, 0 };",
     "strength row min"),
    ("MainActivity.java",
     "    private static final int[] ROW_MAX = { 0, 13, 16, 8, 8, 1, 13, 4, 20, 99, 7, 7, 15, 6, 3 };",
     "    private static final int[] ROW_MAX = { 0, 13, 16, 8, 8, 1, 13, 4, 20, 99, 7, 7, 15, 6, 3, 100 };",
     "strength row max"),
    ("MainActivity.java",
     "    private static final int[] ORDER = { R_QUAL, R_STYLE, R_SAT, R_CON, R_SHARP, R_MTX, R_PE, R_SUB, R_WBMODE, R_KELVIN, R_AB, R_GM, R_EV, R_DRO };",
     "    private static final int[] ORDER = { R_QUAL, R_STYLE, R_SAT, R_CON, R_SHARP, R_MTX, R_PE, R_SUB, R_WBMODE, R_KELVIN, R_AB, R_GM, R_EV, R_DRO, R_STR };",
     "strength in navigation order"),
    # --- helper methods, injected just ahead of stageRecipe() ---------------------------
    ("MainActivity.java",
     "    private void stageRecipe() {",
     '''    // Strength scales the recipe's look by its deviation from neutral, 0–100%.
    private int strScale(int base) { return (int) Math.round(base * edit[R_STR] / 100.0); }
    private void rescaleStrength() {
        Recipes.Recipe r = Recipes.ALL[recipe];
        edit[R_SAT] = strScale(r.sat); edit[R_CON] = strScale(r.con);
        edit[R_SHARP] = strScale(r.sharp); edit[R_EV] = strScale(r.ev);
    }
    private void stageRecipe() {''',
     "strength helpers"),
    # --- stageRecipe: read persisted strength, scale the four continuous params ---------
    ("MainActivity.java",
     "        edit[R_STYLE] = r.style; edit[R_SAT] = r.sat; edit[R_CON] = r.con; edit[R_SHARP] = r.sharp; edit[R_MTX] = r.matrix;",
     "        edit[R_STR] = prefs.getInt(\"strength\", STR_DEFAULT); edit[R_STYLE] = r.style; edit[R_SAT] = strScale(r.sat); edit[R_CON] = strScale(r.con); edit[R_SHARP] = strScale(r.sharp); edit[R_MTX] = r.matrix;",
     "stage scales sat/con/sharp"),
    ("MainActivity.java",
     "        edit[R_PE] = r.pe; edit[R_EV] = r.ev; edit[R_DRO] = r.dro; edit[R_SUB] = r.sub;",
     "        edit[R_PE] = r.pe; edit[R_EV] = strScale(r.ev); edit[R_DRO] = r.dro; edit[R_SUB] = r.sub;",
     "stage scales ev"),
    # --- load(): the -5 slot is a derived multiplier, never read from the camera --------
    ("MainActivity.java",
     "                if (id == -2) { cur[i] = edit[i] = readQuality(); continue; }",
     "                if (id == -2) { cur[i] = edit[i] = readQuality(); continue; }\n                if (id == -5) { cur[i] = edit[i] = prefs.getInt(\"strength\", STR_DEFAULT); continue; }",
     "load strength"),
    # --- writeAll(): skip the derived slot so only scaled params reach the hardware ------
    ("MainActivity.java",
     "                if (!rowDirty(i)) continue;",
     "                if (!rowDirty(i)) continue;\n                if (i == R_STR) continue;   // strength is a derived multiplier, never written as its own slot",
     "writeAll skips strength"),
    # --- rowDirty(): the derived slot carries no own dirty flag -------------------------
    ("MainActivity.java",
     "    private boolean rowDirty(int i) {\n        if (i == R_QUAL) return edit[i] != cur[i];",
     "    private boolean rowDirty(int i) {\n        if (i == R_STR) return false;   // derived multiplier, no own slot\n        if (i == R_QUAL) return edit[i] != cur[i];",
     "rowDirty skips strength"),
    # --- stepValue(): the strength chip steps by 5 across 0–100 and re-scales -----------
    # v0.91: also refuses rows a Picture Effect overrides (STYLE/SAT/CON/SHARP/MTX/STR) —
    # they are listed in the editor greyed, and changing them would do nothing on the body.
    ("MainActivity.java",
     "    private void stepValue(int dir) {\n        if (row == 0) return;",
     "    private void stepValue(int dir) {\n        if (row == 0 || rowDisabled(row)) return;       // v0.91: PE-overridden rows are listed but not editable\n        if (row == R_STR) { edit[R_STR] = Math.max(0, Math.min(100, edit[R_STR] + dir * 5)); prefs.edit().putInt(\"strength\", edit[R_STR]).apply(); rescaleStrength(); applyPreviewSoon(); render(); return; }",
     "step strength"),
    # --- fmt(): render the strength chip value as a percentage --------------------------
    ("MainActivity.java",
     '''            case R_QUAL: return v >= 0 && v < 4 ? Q_LABEL[v] : "?" + v;
            default: return (v > 0 ? "+" : "") + v;''',
     '''            case R_QUAL: return v >= 0 && v < 4 ? Q_LABEL[v] : "?" + v;
            case R_STR: return v + "%";
            default: return (v > 0 ? "+" : "") + v;''',
     "fmt strength"),
    # --- rowVisible(): under a Picture Effect the Style params (and strength) are hidden -
    ("MainActivity.java",
     "            case R_STYLE: case R_SAT: case R_CON: case R_SHARP: case R_MTX: return !pe;",
     "            case R_STYLE: case R_SAT: case R_CON: case R_SHARP: case R_MTX: return !pe;\n            case R_STR: return !pe;",
     "strength visible with style"),
]


def anchors(theme: dict) -> list[tuple[str, str, str, str]]:
    """(file, old-text, new-text, label) edits, applied to whichever copy of the file the
    checkout holds - apply_pack.py may already have moved it deeper into its package."""
    return [
        ("MainActivity.java", CONSTANTS_ANCHOR, constants_for(theme), "colour constants"),
        ("MainActivity.java",
         "name.setTextColor(row == 0 ? ACCENT : WHITE);",
         "name.setTextColor(row == 0 ? ACCENT_TXT : WHITE);",
         "recipe-name colour"),
        # The position counter. Upstream wrote the brand too ("PENTAX   5 / 164"); the bar
        # is now a single centred cluster with the brand gone, so keep just the position.
        ("MainActivity.java",
         'count.setText(grp + "   " + pos);',
         'count.setText(pos);',
         "position counter (no brand)"),
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
        # Open in the HIDDEN overlay state, so the two frosted bars never cover the frame the
        # moment the app launches. User feedback (real α7S II, v0.86): the default two-bar view
        # looked worse than the full-screen preview, because Android 2.3.7 cannot blur the bars
        # and on the ~3" screen they eat a large share of the frame. The AEL/DISP cycle is
        # unchanged: one press from hidden brings the full panel back (2 -> 0 -> 1 -> 2).
        # v0.89: back to opening on the FULL panel. v0.87 opened hidden so the bars would not
        # cover the frame, but the cost was a screen that looks empty on launch and a UP key
        # that does nothing (the UP/DOWN handler bailed out while overlay != 0). AEL/DISP still
        # cycles to the pill and to the pure viewfinder, so the clean frame is one press away.
        ("MainActivity.java",
         "    private int row = 0, recipe = 0, overlay = 0;     // overlay: 0 full, 1 pill, 2 hidden, 3 browser",
         "    private int row = 0, recipe = 0, overlay = 0, overlayPrev = 0;     // overlay: 0 full, 1 pill, 2 hidden, 3 browser (opens on the full panel)",
         "overlay opens on the full panel"),
        # v0.87: the badge behind the recipe name stops reporting camera status and carries the
        # look's BRAND instead (宾得 / 柯达 / 徕卡 …; EN PENTAX / KODAK / LEICA …). GROUPS is
        # arraycopied from GROUPS_ZH at class load when the body is zh, so `grp` is already
        # localised. Dropping the branch also drops the coloured status fills (badge_err /
        # _warn / _ok), leaving the framed chip declared in assets/ui/main.xml.
        ("MainActivity.java",
         '''            if (protectedStore) { badge.setText("PROTECTED"); badge.setBackgroundResource(R.drawable.badge_err); }
            else if (dirty) { badge.setText("PREVIEW"); badge.setBackgroundResource(R.drawable.badge_warn); }
            else { badge.setText("ACTIVE"); badge.setBackgroundResource(R.drawable.badge_ok); }''',
         '''            badge.setText(grp);   // v0.87: the look's brand, not a camera status''',
         "badge shows the brand"),
        # ---- v0.88: the bottom-bar editor -------------------------------------------------
        # Three reports, one root cause: openBrowser(false) hard-coded overlay = 0, so every
        # ENTER pick (and every FN round-trip) dumped the user onto the full two-bar screen.
        # That is the "bottom panel pops out and will not stay hidden" report, and it also
        # defeated v0.87's open-hidden default. Closing the browser now restores the overlay
        # it was opened from.
        ("MainActivity.java",
         "    private void openBrowser(boolean open) { overlay = open ? 3 : 0; row = 0; focus = false; browserCol = 1; render(); }",
         '''    /** v0.88: ENTER / RIGHT in the browser open the compact bottom-bar editor on the picked
     *  recipe instead of merely closing the list. Only the bottom bar is shown (topBar is
     *  hidden), so the frame stays open while a value is dialled.
     *
     *  v0.91: the editor is now a vertical list (EditorView), not the chip strip. It shows
     *  every parameter — including the ones a Picture Effect overrides, which are listed
     *  greyed instead of hidden. The editor arrives with the first row selected but NOT
     *  focused, so the capsule marks the row and the first UP/DOWN press dials it; LEFT/RIGHT
     *  move between rows. (focus used to win every key and made the strip feel like it only
     *  had one row.) */
    private void openEditor() {
        overlayPrev = overlay;
        overlay = 0; bottomOnly = true; focus = false; browserCol = 1;
        row = ORDER[0];
        render();
    }

    private void openBrowser(boolean open) { if (open) { overlayPrev = overlay; overlay = 3; } else { overlay = overlayPrev; bottomOnly = false; } row = 0; focus = false; browserCol = 1; render(); }''',
         "editor: openEditor + browser restores previous overlay"),
        # v0.91: push the whole editor state into EditorView in one call. The view keeps no
        # camera state of its own; this is the only sync point, called from render() whenever
        # bottomOnly is on. Names come from ROW_NAME (already locale-swapped), values from
        # fmt(i, edit[i]) — the same formatter the chip strip uses — and rowDisabled marks the
        # rows a Picture Effect overrides so the view can grey them.
        ("MainActivity.java",
         "    private void openBrowser(boolean open) { if (open) { overlayPrev = overlay; overlay = 3; } else { overlay = overlayPrev; bottomOnly = false; } row = 0; focus = false; browserCol = 1; render(); }",
         "    private void openBrowser(boolean open) { if (open) { overlayPrev = overlay; overlay = 3; } else { overlay = overlayPrev; bottomOnly = false; } row = 0; focus = false; browserCol = 1; render(); }\n\n"
         "    private void syncEditor() {\n"
         "        int n = ORDER.length;\n"
         "        String[] names = new String[n], values = new String[n];\n"
         "        boolean[] off = new boolean[n];\n"
         "        int sel = 0;\n"
         "        for (int k = 0; k < n; k++) {\n"
         "            int i = ORDER[k];\n"
         "            names[k] = ROW_NAME[i];\n"
         "            values[k] = fmt(i, edit[i]);\n"
         "            off[k] = rowDisabled(i);\n"
         "            if (i == row) sel = k;\n"
         "        }\n"
         "        editor.setRows(Recipes.ALL[recipe].name, names, values, off, sel, focus);\n"
         "    }",
         "editor: syncEditor pushes rows to the view"),
        # The flag itself, and the handle on the top bar the editor has to hide.
        ("MainActivity.java",
         "    private boolean focus = false;",
         "    private boolean focus = false;\n"
         "    private boolean bottomOnly = false;      // v0.88: editor shows the bottom bar only\n"
         "    private EditorView editor;               // v0.91: vertical parameter list",
         "editor: bottomOnly flag"),
        ("MainActivity.java",
         "    private View panel;",
         "    private View panel, topBar;",
         "editor: topBar field"),
        ("MainActivity.java",
         "        panel = findViewById(R.id.panel);",
         "        panel = findViewById(R.id.panel);\n        topBar = findViewById(R.id.topbar);\n"
         "        editor = (EditorView) findViewById(R.id.editor);",
         "editor: bind topBar + editor"),
        ("MainActivity.java",
         "            panel.setVisibility(View.VISIBLE); mini.setVisibility(View.GONE);",
         "            panel.setVisibility(View.VISIBLE); mini.setVisibility(View.GONE);\n"
         "            topBar.setVisibility(bottomOnly ? View.GONE : View.VISIBLE);\n"
         "            chipScroll.setVisibility(bottomOnly ? View.GONE : View.VISIBLE);\n"
         "            editor.setVisibility(bottomOnly ? View.VISIBLE : View.GONE);\n"
         "            if (bottomOnly) syncEditor();",
         "editor: hide the top bar and the chip strip, show the vertical editor"),
        ("MainActivity.java",
         "    /** LEFT/RIGHT inside the chip strip: next / previous visible chip, wrapping */\n"
         "    private void moveChip(int dir) {\n"
         "        int pos = 0;\n"
         "        for (int k = 0; k < ORDER.length; k++) if (ORDER[k] == row) pos = k;\n"
         "        for (int k = 0; k < ORDER.length; k++) {\n"
         "            pos = (pos + ORDER.length + dir) % ORDER.length;\n"
         "            if (rowVisible(ORDER[pos])) break;\n"
         "        }\n"
         "        row = ORDER[pos]; lastChip = row; render();\n"
         "    }",
         "    /** LEFT/RIGHT inside the chip strip: next / previous visible chip, wrapping */\n"
         "    private void moveChip(int dir) {\n"
         "        int pos = 0;\n"
         "        for (int k = 0; k < ORDER.length; k++) if (ORDER[k] == row) pos = k;\n"
         "        for (int k = 0; k < ORDER.length; k++) {\n"
         "            pos = (pos + ORDER.length + dir) % ORDER.length;\n"
         "            if (rowVisible(ORDER[pos]) && !rowDisabled(ORDER[pos])) break;   // v0.91: skip PE-overridden rows\n"
         "        }\n"
         "        row = ORDER[pos]; lastChip = row; render();\n"
         "    }",
         "editor: moveChip skips disabled rows"),
        # greyed and labelled "（不能改动）" (v0.92 wording; EN "(read-only)") — instead of
        # vanishing the way rowVisible() used to hide it. rowVisible keeps its old job (which
        # chips the main screen shows), and this new predicate answers a different question:
        # "can the user change this value right now?". It is what the editor uses to decide
        # which rows are greyed.
        ("MainActivity.java",
         "    private boolean rowVisible(int i) {",
         "    /** v0.91: true when this parameter is overridden by the active Picture Effect\n"
         "     *  and therefore not editable. Listed in the editor greyed, never hidden. */\n"
         "    private boolean rowDisabled(int i) {\n"
         "        boolean pe = edit[R_PE] != 0;\n"
         "        return pe && (i == R_STYLE || i == R_SAT || i == R_CON || i == R_SHARP\n"
         "                      || i == R_MTX || i == R_STR);\n"
         "    }\n\n"
         "    private boolean rowVisible(int i) {",
         "editor: rowDisabled predicate"),
        # v0.91: the HintBar used to be the only place the editor's key legend lived, so it
        # was force-shown in bottomOnly mode. The vertical editor now draws its own legend at
        # the bottom of the list, so the HintBar is left at GONE here — legend_visibility in
        # the theme already hides it on the main screen, and this just keeps it from flashing
        # on top of the editor's legend.
        ("MainActivity.java",
         "            hints.setMode(row == 0 ? HintBar.RECIPE : focus ? HintBar.EDIT : HintBar.CHIPS);",
         "            hints.setMode(row == 0 ? HintBar.RECIPE : focus ? HintBar.EDIT : HintBar.CHIPS);\n"
         "            hints.setVisibility(View.GONE);   // v0.91: EditorView draws its own legend",
         "editor: show the key legend"),
        # v0.90/0.91 history: UP/DOWN dialled the value and LEFT/RIGHT walked the rows, on
        # the theory that the editor should agree with the horizontal chip strip it grew out
        # of. On hardware (α7S II, v0.91 feedback) that reads backwards: the editor is now a
        # VERTICAL list, so the eye expects the up key to move the selection up — and a list
        # is navigated with its own axis, not the strip's.
        # v0.92: UP/DOWN walk the list (UP = the row above), LEFT/RIGHT dial the value, and
        # the wheel/dial dial too (see the two anchors below — the wheel previously fell
        # through to nextRecipe inside the editor and changed the recipe mid-edit).
        ("MainActivity.java",
         "                if (focus) stepValue(e.getScanCode() == K_UP ? +1 : -1); else toggleLine();",
         "                if (bottomOnly) moveEditorRow(e.getScanCode() == K_UP ? -1 : +1);     // v1.0.0: UP/DOWN walk every row, disabled included\n"
         "                else if (focus) stepValue(e.getScanCode() == K_UP ? +1 : -1); else toggleLine();",
         "editor: up/down walks the list"),
        # v0.90/0.91 history: LEFT/RIGHT walked the rows. v0.92 swaps the axes with the
        # anchor above: the vertical list is walked with UP/DOWN, so LEFT/RIGHT dial the
        # selected row's value. The anchor is pinned to the LEFT/RIGHT arm by its own dir
        # line (K_RIGHT) — the dial carries an identical body but a K_DIAL_CW dir line, so
        # a shorter OLD would rewrite the dial's arm too.
        ("MainActivity.java",
         "                int dir = e.getScanCode() == K_RIGHT ? +1 : -1;\n"
         "                if (focus) stepValue(dir); else if (row == 0 || overlay != 0) nextRecipe(dir); else moveChip(dir);",
         "                int dir = e.getScanCode() == K_RIGHT ? +1 : -1;\n"
         "                if (bottomOnly) stepValue(dir);                                     // v0.92: LEFT/RIGHT dial the selected value\n"
         "                else if (focus) stepValue(dir);\n"
         "                else if (row == 0 || overlay != 0) nextRecipe(dir);\n"
         "                else moveChip(dir);",
         "editor: left/right dials the value"),
        # v0.92: the wheel and the dial are dials — in the editor they dial the selected
        # row's value, like they do everywhere else. This also fixes a v0.91 regression
        # nobody had named yet: with the editor open and unfocused, the wheel fell through
        # to nextRecipe() and silently changed the RECIPE while the user was editing one
        # row's value. bottomOnly wins before focus so the dial works on the unfocused
        # editor the moment it opens.
        ("MainActivity.java",
         "                int dir = e.getScanCode() == K_WHEEL_CW ? +1 : -1;\n"
         "                if (focus) stepValue(dir); else nextRecipe(dir);",
         "                int dir = e.getScanCode() == K_WHEEL_CW ? +1 : -1;\n"
         "                if (bottomOnly || focus) stepValue(dir); else nextRecipe(dir);   // v0.92: the wheel dials in the editor",
         "editor: wheel dials the value"),
        ("MainActivity.java",
         "                int dir = e.getScanCode() == K_DIAL_CW ? +1 : -1;\n"
         "                if (focus) stepValue(dir); else if (row == 0 || overlay != 0) nextRecipe(dir); else moveChip(dir);",
         "                int dir = e.getScanCode() == K_DIAL_CW ? +1 : -1;\n"
         "                if (bottomOnly || focus) stepValue(dir); else if (row == 0 || overlay != 0) nextRecipe(dir); else moveChip(dir);   // v0.92: the dial dials in the editor",
         "editor: dial dials the value"),
        # AEL/DISP still cycles the overlay, but it must leave the editor state or the top
        # bar stays hidden with no way back.
        ("MainActivity.java",
         "            case K_AEL: case K_DISP: overlay = (overlay + 1) % 3; render(); return true;",
         "            case K_AEL: case K_DISP: bottomOnly = false; overlay = (overlay + 1) % 3; render(); return true;",
         "editor: AEL/DISP leaves the editor"),
        # FN in the editor discards and goes back to the list (the mock's "FN 放弃").
        # v0.89: applyPreview() is the expensive call here (camera.setParameters), so it only
        # runs when the edit actually changed something. Discarding an untouched recipe was
        # paying for a full camera reconfigure to write back the values it already had.
        ("MainActivity.java",
         "            case K_FN: openBrowser(true); return true;",
         "            case K_FN: if (bottomOnly) { bottomOnly = false; row = 0; focus = false; boolean wasDirty = dirty(); stageRecipe(); if (wasDirty) applyPreview(); overlay = 3; render(); } else openBrowser(true); return true;",
         "editor: FN discards"),
        # v0.89: the key that felt slow. Every dial click while scrolling ran nextRecipe ->
        # applyPreview -> camera.setParameters, i.e. one full camera reconfigure per step of
        # the wheel. Preview changes are cosmetic and can lag a frame; writing to the camera
        # cannot. Coalesce them: each step cancels the pending one and re-posts it, so a fast
        # scroll pays for one apply instead of one per step.
        ("MainActivity.java",
         "    private final Runnable hideToast = new Runnable() { public void run() { toast.setVisibility(View.GONE); } };",
         "    private final Runnable hideToast = new Runnable() { public void run() { toast.setVisibility(View.GONE); } };\n"
         "    private final Runnable applyPreviewRunnable = new Runnable() { public void run() { applyPreview(); } };\n"
         "    private void applyPreviewSoon() { handler.removeCallbacks(applyPreviewRunnable); handler.postDelayed(applyPreviewRunnable, 120); }",
         "perf: coalesced preview apply"),
        ("MainActivity.java",
         "    private void nextRecipe(int dir) { recipe = (recipe + Recipes.ALL.length + dir) % Recipes.ALL.length; stageRecipe(); applyPreview(); render(); }",
         "    private void nextRecipe(int dir) { recipe = (recipe + Recipes.ALL.length + dir) % Recipes.ALL.length; stageRecipe(); applyPreviewSoon(); render(); }",
         "perf: scrolling coalesces the preview"),
        # v0.89: UP/DOWN used to do nothing at all unless the full panel was already on
        # screen, which read as a dead key. They now bring the panel up first.
        ("MainActivity.java",
         "                if (overlay != 0) return true;",
         "                if (overlay != 0) { bottomOnly = false; overlay = 0; render(); return true; }   // v0.89: reveal the panel first",
         "up/down reveals the panel"),
        # ---- v0.89: the bundled face has to reach the canvas-drawn views too --------------
        # applyFont() binds the face to TextViews and to Legend.FONT. The three views that
        # draw their own text with their own Paints (PickerView, PromptView) were never told,
        # so on a Chinese body the main screen rendered while the FN browser and the RAW/JPEG
        # prompt rendered boxes: 安布罗式湿版, 宝丽来 Type 100 褐调. PickerView is a tracked
        # template and carries its own hook; PromptView is upstream and gets one here.
        ("PromptView.java",
         "import android.graphics.Paint;",
         "import android.graphics.Paint;\nimport android.graphics.Typeface;",
         "font: PromptView import"),
        ("PromptView.java",
         "public class PromptView extends View {",
         "public class PromptView extends View {\n"
         "    /** Set by MainActivity.applyFont(); applied to the Paints below on the first draw. */\n"
         "    public static Typeface FONT;\n"
         "    private boolean fontApplied = false;",
         "font: PromptView hook"),
        ("PromptView.java",
         "        float w = getWidth(), h = getHeight(), pad = 16 * d;",
         "        if (FONT != null && !fontApplied) { title.setTypeface(FONT); body.setTypeface(FONT); opt.setTypeface(FONT); note.setTypeface(FONT); fontApplied = true; }\n"
         "        float w = getWidth(), h = getHeight(), pad = 16 * d;",
         "font: PromptView paints"),
        # Storing used to leave the panel on screen. Now every commit returns to the screen
        # the editor opened FROM (overlayPrev, normally the recipe list at overlay 3) rather
        # than a blank view — saving from the editor used to land on overlay 2 (everything
        # hidden) and the user had to press again to get the list. The companion anchor
        # "editor: hide editor outside editor mode" hides the EditorView itself (it is a
        # sibling of panel, so panel.setGone does not touch it) on every render.
        ("MainActivity.java",
         "            case K_ENTER: if (row == 0 || overlay != 0) writeAll(); else setFocus(!focus); return true;",
         "            case K_ENTER: if (bottomOnly || row == 0 || overlay != 0 || focus) { writeAll(); bottomOnly = false; focus = false; row = 0; overlay = overlayPrev; render(); } else setFocus(true); return true;",
         "auto-hide after store"),
        # Companion to "auto-hide after store": the editor (EditorView) is a SIBLING of
        # panel/picker, not a child of panel — so panel.setVisibility(GONE) does NOT hide it.
        # render() only set editor visibility inside the overlay == 0 branch, which the
        # store path skips (it returns to overlay 3 / 1 / 2). So after saving, the editor
        # panel stayed painted on top of the browser. Bind editor visibility to bottomOnly
        # up here, ahead of the overlay branches, so it is always correct no matter which
        # overlay the store returns to.
        ("MainActivity.java",
         "        picker.setVisibility(overlay == 3 ? View.VISIBLE : View.GONE);",
         "        picker.setVisibility(overlay == 3 ? View.VISIBLE : View.GONE);\n        editor.setVisibility(bottomOnly ? View.VISIBLE : View.GONE);",
         "editor: hide editor outside editor mode"),
    ] + STRENGTH + font_java(theme) + label_java() + perf() + editor_ux()


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
    names = [str(theme.get("font_regular", "")), str(theme.get("font_bold", "")),
             str(theme.get("font_regular_zh", "")), str(theme.get("font_bold_zh", ""))]
    for name in names:
        if not name:
            raise SystemExit("catalog/ui-theme.json needs font_regular, font_bold, "
                             "font_regular_zh and font_bold_zh")
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


def label_java() -> list[tuple[str, str, str, str]]:
    """The on-screen words upstream hardcodes into MainActivity / HintBar / PromptView,
    switched by locale so a Chinese body reads Chinese and an English one reads English.

    Everything here is user-visible chrome that is neither a recipe name nor a group label
    (those come from Recipes.java, already bilingual). Each replacement keeps the English
    branch intact: Recipes.ZH is resolved once at class load, so there is no per-draw cost.
    Array-valued words (chip labels, hint-bar legend, prompt legend, quality labels, prompt
    option pills) get a _ZH twin that is arraycopied over the English one when the body is
    zh; one-off toast / status / summary fragments become Recipes.ZH ? zh : en ternaries.
    """
    return [
        # --- already-localised in v0.82: CS/PE chip tag -------------------------------------
        ("MainActivity.java", 'tag.setText(edit[R_PE] != 0 ? "PE" : "CS");',
         'tag.setText(Recipes.ZH ? (edit[R_PE] != 0 ? "效果" : "风格") : (edit[R_PE] != 0 ? "PE" : "CS"));',
         "CS/PE tag"),
        # The three status badges (受保护 / 预览中 / 已启用; EN PROTECTED / PREVIEW / ACTIVE) were
        # REMOVED in v0.87 — the badge slot now carries the look's brand instead, so these have
        # no old-text left to match. Do not re-add them without also restoring the status
        # branch in render() that the "badge shows the brand" anchor replaces.

        # --- chip parameter labels (the small caption above each value) --------------------
        ("MainActivity.java",
         '''    private static final String[] ROW_NAME = { "RECIPE", "STYLE", "SAT", "CON", "SHARP", "MATRIX", "EFFECT", "SUB", "WB", "KELVIN", "A-B", "G-M", "EV", "DRO", "QUALITY" };''',
         '''    private static final String[] ROW_NAME = { "RECIPE", "STYLE", "SAT", "CON", "SHARP", "MATRIX", "EFFECT", "SUB", "WB", "KELVIN", "A-B", "G-M", "EV", "DRO", "QUALITY", "STRENGTH" };
    private static final String[] ROW_NAME_ZH = { "配方", "风格", "饱和", "反差", "锐度", "矩阵", "效果", "子项", "白平衡", "色温", "A-B", "G-M", "曝光", "DRO", "画质", "强度" };
    static { if (Recipes.ZH) System.arraycopy(ROW_NAME_ZH, 0, ROW_NAME, 0, ROW_NAME_ZH.length); }''',
         "chip row labels"),

        # --- quality labels (chip value, prompt title, summary) ----------------------------
        ("MainActivity.java",
         '''    private static final String[] Q_LABEL = { "RAW", "RAW+JPG", "JPG Fine", "JPG Std" };''',
         '''    private static final String[] Q_LABEL = { "RAW", "RAW+JPG", "JPG Fine", "JPG Std" };
    private static final String[] Q_LABEL_ZH = { "RAW", "RAW+JPG", "JPG 精细", "JPG 标准" };
    static { if (Recipes.ZH) System.arraycopy(Q_LABEL_ZH, 0, Q_LABEL, 0, Q_LABEL_ZH.length); }''',
         "quality labels"),

        # --- RAW / JPEG prompt option pills ----------------------------------------------
        ("MainActivity.java",
         '''    private static final String[] PROMPT_OPTS = { "Accept", "Cancel" };''',
         '''    private static final String[] PROMPT_OPTS = { "Accept", "Cancel" };
    private static final String[] PROMPT_OPTS_ZH = { "接受", "取消" };
    static { if (Recipes.ZH) System.arraycopy(PROMPT_OPTS_ZH, 0, PROMPT_OPTS, 0, PROMPT_OPTS_ZH.length); }''',
         "prompt option pills"),

        # --- prompt dialog: title, body, note ---------------------------------------------
        ("MainActivity.java",
         '''        String t = "Quality: " + Q_LABEL[cur[R_QUAL]] + "  →  " + Q_LABEL[edit[R_QUAL]];''',
         '''        String t = Recipes.ZH ? ("画质：" + Q_LABEL[cur[R_QUAL]] + "  →  " + Q_LABEL[edit[R_QUAL]]) : ("Quality: " + Q_LABEL[cur[R_QUAL]] + "  →  " + Q_LABEL[edit[R_QUAL]]);''',
         "prompt title"),
        ("MainActivity.java",
         '''        String b = edit[R_PE] != 0 ? "JPEG is needed to apply this recipe." : "Creative Style recipes use the Factory recipe's quality.";''',
         '''        String b = edit[R_PE] != 0 ? (Recipes.ZH ? "应用此配方需要 JPEG 格式。" : "JPEG is needed to apply this recipe.") : (Recipes.ZH ? "创意风格配方沿用出厂画质。" : "Creative Style recipes use the Factory recipe's quality.");''',
         "prompt body"),
        ("MainActivity.java",
         '''        prompt.set(t, b, PROMPT_OPTS, promptSel, qualityPersistent() ? null : "quality slot not located yet — live view only");''',
         '''        prompt.set(t, b, PROMPT_OPTS, promptSel, qualityPersistent() ? null : (Recipes.ZH ? "尚未定位画质存储位 — 仅实时预览" : "quality slot not located yet — live view only"));''',
         "prompt note"),

        # --- transient toasts -------------------------------------------------------------
        ("MainActivity.java",
         '''} catch (Throwable t) { showToast("Read failed: " + t.getMessage(), 0); }''',
         '''} catch (Throwable t) { showToast(Recipes.ZH ? ("读取失败：" + t.getMessage()) : ("Read failed: " + t.getMessage()), 0); }''',
         "toast: read failed"),
        ("MainActivity.java",
         '''        if (!dirty()) { showToast("Already stored — nothing to write", 2500); return; }''',
         '''        if (!dirty()) { showToast(Recipes.ZH ? "已是最新，无需写入" : "Already stored — nothing to write", 2500); return; }''',
         "toast: nothing to write"),
        ("MainActivity.java",
         '''            msg = "Stored " + n + " value" + (n == 1 ? "" : "s") + " — power-cycle the camera to apply everywhere";''',
         '''            msg = Recipes.ZH ? ("已写入 " + n + " 项参数 — 重启相机以全局生效") : ("Stored " + n + " value" + (n == 1 ? "" : "s") + " — power-cycle the camera to apply everywhere");''',
         "toast: stored"),
        ("MainActivity.java",
         '''        } catch (Throwable t) { msg = "WRITE FAILED: " + t.getMessage(); }''',
         '''        } catch (Throwable t) { msg = Recipes.ZH ? ("写入失败：" + t.getMessage()) : ("WRITE FAILED: " + t.getMessage()); }''',
         "toast: write failed"),
        ("MainActivity.java",
         '''                if (promptSel == 0) writeAll(true); else showToast("Not stored", 2000);   // cancel: recipe stays previewed only''',
         '''                if (promptSel == 0) writeAll(true); else showToast(Recipes.ZH ? "未存储" : "Not stored", 2000);   // cancel: recipe stays previewed only''',
         "toast: not stored"),
        ("MainActivity.java",
         '''        showToast("Quality: " + Q_LABEL[edit[R_QUAL]] + (qualityPersistent() ? "  — ENTER to store" : "  (live view only until the slot is known)"), 2500);''',
         '''        showToast(Recipes.ZH ? ("画质：" + Q_LABEL[edit[R_QUAL]] + (qualityPersistent() ? "  — 按 ENTER 存储" : "  （实时预览，待定位存储位）")) : ("Quality: " + Q_LABEL[edit[R_QUAL]] + (qualityPersistent() ? "  — ENTER to store" : "  (live view only until the slot is known)")), 2500);''',
         "toast: cycle quality"),
        ("MainActivity.java",
         '''                showToast("Snapshot of " + ids.size() + " settings taken. Change a menu setting, reopen, press Fn again.", 6000);''',
         '''                showToast(Recipes.ZH ? ("已快照 " + ids.size() + " 项设置。修改菜单设置后重新打开，再按 Fn。") : ("Snapshot of " + ids.size() + " settings taken. Change a menu setting, reopen, press Fn again."), 6000);''',
         "toast: snapshot"),
        ("MainActivity.java",
         '''        } catch (Throwable t) { showToast("snapshot error: " + t, 0); }''',
         '''        } catch (Throwable t) { showToast(Recipes.ZH ? ("快照出错：" + t) : ("snapshot error: " + t), 0); }''',
         "toast: snapshot error"),
        ("MainActivity.java",
         '''    private void stageFactory() { recipe = 0; stageRecipe(); applyPreview(); showToast("Factory values staged — ENTER to store", 3000); render(); }''',
         '''    private void stageFactory() { recipe = 0; stageRecipe(); applyPreview(); showToast(Recipes.ZH ? "已载入出厂值 — 按 ENTER 存储" : "Factory values staged — ENTER to store", 3000); render(); }''',
         "toast: factory staged"),
        # --- v0.88: ENTER / RIGHT in the browser open the editor ---------------------------
        # ENTER used to close the list and pop a "已预览 — 按 ENTER 存储" toast. That toast
        # is why picking a look felt identical to the previous release: it did not open
        # anything, it just renamed the state. ENTER now opens the settings editor, so the
        # toast anchor that used to localise this line is gone with it (an anchor whose
        # target no longer exists is a hard FAIL, not a no-op).
        ("MainActivity.java",
         '''                openBrowser(false); showToast(Recipes.ALL[recipe].name + " previewed — ENTER to store", 3000); return true;''',
         '''                openEditor(); return true;   // v0.88: ENTER opens the settings editor''',
         "editor: ENTER in the browser"),
        # RIGHT used to only flip browserCol, a leftover from the two-column browser that
        # the picker now ignores — so the "right key" did literally nothing visible. It opens
        # the editor now, and LEFT closes the list (the mock calls LEFT meaningless in here,
        # but leaving a dead key that swallows input is worse than making it a back key).
        ("MainActivity.java",
         "            case K_LEFT: case K_RIGHT: browserCol ^= 1; render(); return true;",
         "            case K_RIGHT: openEditor(); return true;\n"
         "            case K_LEFT: openBrowser(false); return true;",
         "editor: RIGHT opens, LEFT closes"),

        # --- the one-line summary under the recipe name ------------------------------------
        ("MainActivity.java",
         '''            if (edit[R_PE] != 0) { m.append("Picture Effect ").append(Recipes.PE_LABEL[edit[R_PE]]); String sl = Recipes.subLabel(edit[R_PE], edit[R_SUB]); if (sl != null) m.append(' ').append(sl); m.append(" (Creative Style ignored, JPEG only)"); }''',
         '''            if (edit[R_PE] != 0) { m.append(Recipes.ZH ? "图片特效 " : "Picture Effect ").append(Recipes.PE_LABEL[edit[R_PE]]); String sl = Recipes.subLabel(edit[R_PE], edit[R_SUB]); if (sl != null) m.append(' ').append(sl); m.append(Recipes.ZH ? "（创意风格已忽略，仅 JPEG）" : " (Creative Style ignored, JPEG only)"); }''',
         "summary: PE line"),
        ("MainActivity.java",
         '''            if (edit[R_MTX] == 1 && edit[R_PE] == 0) m.append("  ·  PP3 matrix");''',
         '''            if (edit[R_MTX] == 1 && edit[R_PE] == 0) m.append(Recipes.ZH ? "  ·  PP3 矩阵" : "  ·  PP3 matrix");''',
         "summary: PP3 matrix"),
        ("MainActivity.java",
         '''            if (qualityChanges()) m.append("  ·  QUALITY → ").append(Q_LABEL[edit[R_QUAL]]).append(" (now ").append(Q_LABEL[cur[R_QUAL]]).append(")");''',
         '''            if (qualityChanges()) m.append(Recipes.ZH ? "  · 画质 → " : "  ·  QUALITY → ").append(Q_LABEL[edit[R_QUAL]]).append(Recipes.ZH ? "（当前 " : " (now ").append(Q_LABEL[cur[R_QUAL]]).append(")");''',
         "summary: quality"),
        ("MainActivity.java",
         '''            if (edit[R_PE] != 0 && qualityIsRaw()) m.append("  ·  RAW is on: effect ignored");''',
         '''            if (edit[R_PE] != 0 && qualityIsRaw()) m.append(Recipes.ZH ? "  · RAW 开启：特效已忽略" : "  ·  RAW is on: effect ignored");''',
         "summary: RAW on"),
        ("MainActivity.java",
         '''            if (!previewOk) m.append("  ·  no live preview: ").append(previewErr);''',
         '''            if (!previewOk) m.append(Recipes.ZH ? "  · 无实时预览：" : "  ·  no live preview: ").append(previewErr);''',
         "summary: no preview"),

        # --- the minimal pill overlay ----------------------------------------------------
        ("MainActivity.java",
         '''            mini.setText((edit[R_PE] != 0 ? "PE  " : "CS  ") + r.name + "   " + pos + (dirty ? "   · preview" : "   · active") + (qualityChanges() ? "   · quality → " + Q_LABEL[edit[R_QUAL]] : ""));''',
         '''            mini.setText((edit[R_PE] != 0 ? (Recipes.ZH ? "特效  " : "PE  ") : (Recipes.ZH ? "风格  " : "CS  ")) + r.name + "   " + pos + (qualityChanges() ? (Recipes.ZH ? "   · 画质 → " : "   · quality → ") + Q_LABEL[edit[R_QUAL]] : ""));''',
         "pill line"),

        # --- single-value chip captions that are words, not numbers ------------------------
        ("MainActivity.java",
         '''            case R_MTX: return v == 0 ? "off" : "PP3";''',
         '''            case R_MTX: return v == 0 ? (Recipes.ZH ? "关" : "off") : "PP3";''',
         "chip value: matrix off"),
        ("MainActivity.java",
         '''            case R_WBMODE: return v == 1 ? "auto" : v == 14 ? "kelvin" : String.valueOf(v);''',
         '''            case R_WBMODE: return v == 1 ? (Recipes.ZH ? "自动" : "auto") : v == 14 ? (Recipes.ZH ? "色温" : "kelvin") : String.valueOf(v);''',
         "chip value: wb mode"),

        # --- HintBar key legend under the main panel --------------------------------------
        # v0.90: EDIT now carries four entries, not three. It used to show only UP/DOWN
        # ("数值"), which was already wrong — UP/DOWN was walking the strip at the time — and
        # it had no entry at all for the key that did walk it. The legend is the only place
        # that can tell the user which key does what, so it has to name both axes.
        ("HintBar.java",
         "        { Legend.UPDOWN, Legend.ENTER, Legend.MENU } };",
         "        { Legend.LEFTRIGHT, Legend.UPDOWN, Legend.ENTER, Legend.MENU } };",
         "hint-bar edit icons"),
        ("HintBar.java",
         '''    private static final String[][] TEXT = {
        { "recipe", "params", "browse", "store", "factory", "hide", "exit" },
        { "param", "recipe", "edit", "browse", "factory", "hide", "exit" },
        { "value", "done", "done" } };''',
         '''    private static final String[][] TEXT = {
        { "recipe", "params", "browse", "store", "factory", "hide", "exit" },
        { "param", "recipe", "edit", "browse", "factory", "hide", "exit" },
        { "param", "value", "done", "done" } };
    private static final String[][] TEXT_ZH = {
        { "配方", "参数", "浏览", "存入", "出厂", "隐藏", "退出" },
        { "参数", "配方", "编辑", "浏览", "出厂", "隐藏", "退出" },
        { "参数", "数值", "完成", "完成" } };
    static { if (Recipes.ZH) { TEXT[0] = TEXT_ZH[0]; TEXT[1] = TEXT_ZH[1]; TEXT[2] = TEXT_ZH[2]; } }''',
         "hint-bar legend"),

        # --- PromptView legend under the modal prompt -------------------------------------
        ("PromptView.java",
         '''    private static final String[] LEGEND_TEXT = { "choose", "confirm", "cancel" };''',
         '''    private static final String[] LEGEND_TEXT = { "choose", "confirm", "cancel" };
    private static final String[] LEGEND_TEXT_ZH = { "选择", "确认", "取消" };
    static { if (Recipes.ZH) System.arraycopy(LEGEND_TEXT_ZH, 0, LEGEND_TEXT, 0, LEGEND_TEXT_ZH.length); }''',
         "prompt legend"),
    ]


def perf() -> list[tuple[str, str, str, str]]:
    """Three hot-path optimisations for MainActivity, replayed as anchors.

    These match the text AFTER the STRENGTH / font / label anchors have run (they are
    appended last), so their `old` strings are the patched intermediate, not the upstream
    original. The three spots were measured on the α7S II as the only per-input costs that
    scaled with the user's dialling speed:

    1. rowDirty(R_SUB) read the camera's SUB slot through NativeBackup on EVERY render (the
       chip loop calls rowDirty once per row), even when nothing about the effect had
       changed. When edit[R_PE] == cur[R_PE], cur[R_SUB] already holds that slot's stored
       value (load() wrote it), so the native read is replaced with the cached cur[i]. The
       storedSub() path is kept only for the rare moment the staged effect differs from the
       stored one — and there R_PE is already dirty, so the read is not even load-bearing.

    2. stepValue() applied the preview synchronously per dial step (camera.setParameters is
       the expensive call). nextRecipe() already coalesces through applyPreviewSoon(); the
       dial now does the same, so a fast spin pays for one camera reconfigure instead of
       one per step. (The strength row's own preview already coalesces in the STRENGTH
       anchor above.)

    3. Three SharedPreferences writes used .commit() (a synchronous fsync) on every change:
       the last recipe, the base quality, and the strength. .apply() updates memory
       immediately and writes the disk asynchronously — identical read-back behaviour, no
       per-step fsync. The values are low-stakes preferences (a lost write on process death
       costs one reselection), so async is the correct trade-off. (The strength write is
       converted in the STRENGTH anchor above; the recipe and quality writes are here.)
    """
    return [
        # --- rowDirty(R_SUB): reuse cur[R_SUB] instead of a native read per render ------
        ("MainActivity.java",
         "        if (i == R_SUB) return Recipes.subId(edit[R_PE]) != 0 && edit[i] != storedSub();",
         "        if (i == R_SUB) return Recipes.subId(edit[R_PE]) != 0 && edit[i] != (edit[R_PE] == cur[R_PE] ? cur[i] : storedSub());",
         "perf: SUB dirty reuses the cached stored value"),
        # --- three synchronous fsyncs become async --------------------------------------
        ("MainActivity.java",
         "        prefs.edit().putInt(\"recipe\", recipe).commit();          // reopen on the last selected recipe",
         "        prefs.edit().putInt(\"recipe\", recipe).apply();           // reopen on the last selected recipe",
         "perf: last recipe persists async"),
        ("MainActivity.java",
         "        if (!Recipes.ALL[recipe].isEffect() || edit[R_QUAL] >= 2) prefs.edit().putInt(\"baseQuality\", edit[R_QUAL]).commit();",
         "        if (!Recipes.ALL[recipe].isEffect() || edit[R_QUAL] >= 2) prefs.edit().putInt(\"baseQuality\", edit[R_QUAL]).apply();",
         "perf: base quality persists async"),
        # --- stepValue() coalesces the camera reconfigure --------------------------------
        ("MainActivity.java",
         "        applyPreview(); render();\n    }\n\n    /** enumerated rows (names, not numbers) scroll endlessly */",
         "        applyPreviewSoon(); render();\n    }\n\n    /** enumerated rows (names, not numbers) scroll endlessly */",
         "perf: dial coalesces the preview"),
    ]


def editor_ux() -> list[tuple[str, str, str, str]]:
    """Hardware-driven editor fixes (α7S II, v1.0.0 feedback), appended last so they match
    the text the editor/v0.9x anchors above have already produced.

    Three things the hardware asked for, and where each landed:
    1. The read-only note rode a second line UNDER the value ("0" then "（不能改动）"
       below it), which read as noise. The note now rides the value string itself —
       MainActivity appends "（不能改动）" / " (read-only)" to the value, so the editor
       draws "标准（不能改动）" on one line. The EditorView template stops drawing its own
       second-line note (see assets/ui/EditorView.java). → the anchor below.
    2. A row a Picture Effect overrides was un-selectable: the editor's UP/DOWN walked the
       list through moveChip(), which skips rows where rowVisible() is false — and every
       PE-overridden row is invisible on the main screen, so the cursor could never land on
       one to show it. The editor now walks with moveEditorRow(), which steps the ORDER list
       one entry at a time and lands on disabled rows too. You can move onto one, you just
       cannot dial it (stepValue already returns early on rowDisabled). The UP/DOWN call
       itself is rewritten by the v0.92 "up/down walks the list" anchor above (it now calls
       moveEditorRow directly); this function only ADDS the moveEditorRow method the call
       needs. → the anchor below.
    3. Saving from the editor left a blank view (overlay 2) instead of returning to the
       recipe list. That fix lives in the "auto-hide after store" anchor above — its
       store path now returns to overlayPrev, the screen the editor opened from. Nothing
       extra to add here.
    """
    return [
        # --- the read-only note rides the value string --------------------------------
        ("MainActivity.java",
         "            values[k] = fmt(i, edit[i]);",
         "            values[k] = fmt(i, edit[i]) + (rowDisabled(i) ? (Recipes.ZH ? \"（不能改动）\" : \" (read-only)\") : \"\");",
         "editor: read-only note rides the value"),
        # --- the editor walks every row, disabled included -----------------------------
        ("MainActivity.java",
         "        row = ORDER[pos]; lastChip = row; render();\n"
         "    }\n\n"
         "    /** UP/DOWN: switch between the recipe line and the chip strip */",
         "        row = ORDER[pos]; lastChip = row; render();\n"
         "    }\n\n"
         "    /** UP/DOWN in the editor: step the ORDER list one row at a time, landing on\n"
         "     *  disabled rows too — you can select a PE-overridden row, you just cannot dial\n"
         "     *  it. moveChip() is wrong here because it skips rows where rowVisible() is\n"
         "     *  false, and every PE-overridden row is invisible on the main screen. */\n"
         "    private void moveEditorRow(int dir) {\n"
         "        int pos = 0;\n"
         "        for (int k = 0; k < ORDER.length; k++) if (ORDER[k] == row) pos = k;\n"
         "        pos = (pos + ORDER.length + dir) % ORDER.length;\n"
         "        row = ORDER[pos]; lastChip = row; render();\n"
         "    }\n\n"
         "    /** UP/DOWN: switch between the recipe line and the chip strip */",
         "editor: moveEditorRow steps every row"),
    ]


def font_java(theme: dict) -> list[tuple[str, str, str, str]]:
    """MainActivity + Legend edits that bind the bundled face.

    Two things are deliberate. The loads are wrapped in a Throwable catch because a missing
    or corrupt asset throws at runtime, not compile time, and the only acceptable outcome
    is 'fall back to the system font' — a camera app that dies on launch because a .ttf is
    missing is absurd. And the bold face falls back to a synthesised bold rather than to
    regular, so a theme that names only one file still reads as bold where it should.
    """
    regular, bold, regular_zh, bold_zh = fonts_for(theme)
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
         f'            uiFontRegular = Typeface.createFromAsset(getAssets(), Recipes.ZH ? "fonts/{regular_zh}" : "fonts/{regular}");\n'
         f'            uiFontBold = Typeface.createFromAsset(getAssets(), Recipes.ZH ? "fonts/{bold_zh}" : "fonts/{bold}");\n'
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
         "        Legend.FONT = f; PickerView.FONT = f; PromptView.FONT = f; EditorView.FONT = f;\n"
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
        # v0.91: the vertical editor is a NEW file (no upstream PickerView slot to overwrite),
        # so find_source cannot locate it — it has never existed in the checkout. Walk the
        # source tree the same way find_source does and compare against editor_for().
        ev = None
        for hit in (fork / "src").rglob("EditorView.java"):
            ev = hit
            break
        if ev is None or not ev.is_file() or ev.read_text(encoding="utf-8") != editor_for(theme, package):
            problems.append("src/.../EditorView.java is not the vertical editor from "
                            "assets/ui/EditorView.java")
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

    # v0.91: the vertical editor. Brand-new file, so write it next to whichever package the
    # checkout is currently building as — apply_pack has already renamed the tree by now, so
    # the editor lands in the same src/.../<pkg>/ folder as PickerView and Recipes.java.
    ev = None
    for hit in (fork / "src").rglob("EditorView.java"):
        ev = hit
        break
    if ev is None:
        # first build on this checkout: drop it next to PickerView (same package folder)
        try:
            pv = find_source(fork, "PickerView.java")
            ev = pv.parent / "EditorView.java"
        except SystemExit as exc:
            problems.append(str(exc))
    if ev is not None:
        write_file(ev, editor_for(theme, package), args.dry_run, report,
                   "java: EditorView.java")

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
