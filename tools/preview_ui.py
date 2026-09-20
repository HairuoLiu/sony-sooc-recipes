#!/usr/bin/env python3
"""Render the main screen as an HTML mock, from the same inputs the APK is built from.

    python tools/preview_ui.py                     # writes build/ui-preview.html
    python tools/preview_ui.py --recipe kodak-gold-200
    python tools/preview_ui.py --recipe ilford-hp5 --out preview.html

Why this exists: the app only runs on a Sony camera body. There is no emulator, no
screenshot, and no way to install a build and look at it without the hardware - so every
layout decision used to be made blind and then discovered on the camera. This renders the
same two files that tools/patch_ui.py feeds the build (assets/ui/main.xml and
catalog/ui-theme.json) as a static page, so what you approve here is what ships.

It is a faithful mock of geometry and colour, not a simulation of Android:

  * the frame is 640x480, the size of the LCD this app targets, and every size in the
    layout is applied as dp/sp at 1:1 - so the proportions on screen are the real ones;
  * bar backgrounds come from the drawables patch_ui generates, parsed back out of the
    XML, so a colour edited in the theme shows up here and nowhere else;
  * text colours, sizes and paddings are read from the layout itself.

What it does NOT do: measure text, wrap, ellipsize, or lay out a RelativeLayout properly.
Where the layout says 'centre this', the preview centres it; Android arrives at the same
place by a longer route. Treat it as a good answer to 'does this read well', and a bad
answer to 'is this pixel-exact'.

The text it fills in is a real recipe from catalog/filters.json, not placeholder Latin,
because a bar that looks fine with 'Lorem ipsum' can still break on 'Eterna Bleach Bypass'.
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import patch_ui  # noqa: E402  (tools/ on sys.path, imported after the path is set)

NS = "{http://schemas.android.com/apk/res/android}"
CATALOG = ROOT / "catalog" / "filters.json"
FONT_DIR = ROOT / "assets" / "fonts"
DEFAULT_OUT = ROOT / "build" / "ui-preview.html"

# The screen this app is written for. Sizes in the layout are dp, and at 1x one dp is one
# CSS pixel here - which is exactly how they relate on an mdpi Android screen.
SCREEN_W, SCREEN_H = 640, 480
ZOOM = 2  # a 640x480 frame is unreadable in a browser; scale the whole frame, not the sizes

# Chip rows, in MainActivity's order (ROW_NAME). Skipped rows are the ones the app itself
# hides on a given recipe - MATRIX and EFFECT/QUALITY only appear when they apply.
CHIP_ROWS = [
    ("STYLE", lambda r: r.get("style")),
    ("SAT", lambda r: r.get("sat")),
    ("CON", lambda r: r.get("con")),
    ("SHARP", lambda r: r.get("sharp")),
    ("WB", lambda r: (r.get("wb") or {}).get("mode")),
    ("KELVIN", lambda r: (r.get("wb") or {}).get("kelvin")),
    ("A-B", lambda r: (r.get("wb") or {}).get("ab")),
    ("G-M", lambda r: (r.get("wb") or {}).get("gm")),
    ("EV", lambda r: r.get("ev")),
    ("DRO", lambda r: r.get("dro")),
]


def dp(text: str | None, default: float = 0.0) -> float:
    """'12dp' -> 12.0, '17sp' -> 17.0. Missing or unparseable -> default."""
    if not text:
        return default
    m = re.match(r"^(-?[\d.]+)(dp|sp|dip|px)$", text.strip())
    return float(m.group(1)) if m else default


def css_colour(argb: str | None, default: str = "transparent") -> str:
    """'#99566473' -> 'rgba(86,100,115,0.6)'. Android packs alpha first; CSS puts it last."""
    if not argb or not argb.startswith("#"):
        return default
    hexes = argb[1:]
    if len(hexes) == 8:
        a, r, g, b = (hexes[i:i + 2] for i in (0, 2, 4, 6))
        return f"rgba({int(r, 16)},{int(g, 16)},{int(b, 16)},{round(int(a, 16) / 255, 3)})"
    if len(hexes) == 6:
        return "#" + hexes
    return default


def bar_css(drawable_xml: str) -> str:
    """Read back a drawable patch_ui generated and turn it into CSS.

    Parsing the generated XML rather than re-reading the theme keeps one rule: the theme
    describes colours once, patch_ui turns them into Android, and this turns the same
    Android into CSS. Nothing here invents a value.
    """
    root = ET.fromstring(drawable_xml)
    parts: list[str] = []
    grad = root.find("gradient")
    if grad is not None:
        start = css_colour(grad.get(NS + "startColor"))
        end = css_colour(grad.get(NS + "endColor"))
        # Android's angle is 0 = left-to-right, measured clockwise; 270 is top-to-bottom.
        # CSS 'to bottom' is the same thing. Anything else is passed through rotated.
        angle = int(grad.get(NS + "angle", "0"))
        parts.append(f"linear-gradient({angle - 270}deg, {start}, {end})")
    solid = root.find("solid")
    if solid is not None:
        parts.append(f"linear-gradient({css_colour(solid.get(NS + 'color'))},"
                     f"{css_colour(solid.get(NS + 'color'))})")
    corners = root.find("corners")
    radius = "0"
    if corners is not None:
        tl = dp(corners.get(NS + "topLeftRadius") or
                corners.get(NS + "radius"), 0)
        tr = dp(corners.get(NS + "topRightRadius") or
                corners.get(NS + "radius"), 0)
        br = dp(corners.get(NS + "bottomRightRadius") or
                corners.get(NS + "radius"), 0)
        bl = dp(corners.get(NS + "bottomLeftRadius") or
                corners.get(NS + "radius"), 0)
        radius = f"{tl}px {tr}px {br}px {bl}px"
    stroke = root.find("stroke")
    border = ""
    if stroke is not None:
        w = dp(stroke.get(NS + "width"), 0)
        border = f"border:{w}px solid {css_colour(stroke.get(NS + 'color'))};"
    return (f"background:{', '.join(parts)};border-radius:{radius};" + border)


def background_for(el: ET.Element, theme: dict, fork: Path) -> str:
    """@drawable/whatever this view points at, as CSS.

    Two sources, in this order: the drawables patch_ui generates from the theme, then the
    upstream ones a checkout happens to carry (the badge_* status fills). Reading the real
    file rather than hard-coding its colour is the point — the ACTIVE badge is drawn with
    WHITE text, and on a light bar that only works because badge_ok is an opaque green
    slab. A preview that left the badge unfilled would show the one thing that is actually
    broken as if it were fine.
    """
    ref = el.get(NS + "background") or ""
    if not ref.startswith("@drawable/"):
        return ""
    name = ref.split("/", 1)[1] + ".xml"
    generated = patch_ui.drawables_for(theme)
    if name in generated:
        return bar_css(generated[name])
    upstream = fork / "res" / "drawable" / name
    if upstream.is_file():
        return bar_css(upstream.read_text(encoding="utf-8"))
    return ""


def style_for(el: ET.Element, theme: dict, fork: Path) -> str:
    """The visual attributes of one view, as CSS."""
    out: list[str] = []
    size = dp(el.get(NS + "textSize"))
    if size:
        out.append(f"font-size:{size}px")
    colour = el.get(NS + "textColor")
    if colour:
        out.append(f"color:{css_colour(colour)}")
    if el.get(NS + "textStyle") == "bold":
        out.append("font-weight:700")
    # bar_css already returns a run of declarations; joining on ';' keeps it intact.
    background = background_for(el, theme, fork)
    if background:
        out.append(background.rstrip(";"))
    return ";".join(out)


def pad_css(el: ET.Element) -> str:
    return ";".join(
        f"padding-{side}:{dp(el.get(NS + 'padding' + side.capitalize()))}px"
        for side in ("left", "right", "top", "bottom")
        if el.get(NS + "padding" + side.capitalize())
    )


def app_name(fork: Path) -> str:
    """@string/app_name, read from the checkout. Falls back to the known value.

    The layout only says @string/app_name, so a preview that hard-codes the title would
    drift the moment the app is renamed — and a renamed app whose preview still says the
    old name is exactly the kind of thing that ships.
    """
    strings = fork / "res" / "values" / "strings.xml"
    if strings.is_file():
        m = re.search(r'<string name="app_name">([^<]*)</string>',
                      strings.read_text(encoding="utf-8"))
        if m:
            return html.unescape(m.group(1))
    return "Sony SOOC Recipes"


def chip_css(theme: dict) -> str:
    drawables = patch_ui.drawables_for(theme)
    return bar_css(drawables["chip.xml"])


def chips_html(recipe: dict, theme: dict) -> str:
    """The parameter chips, from a real recipe. Row 0 (RECIPE) is the name row, shown
    in the top bar instead, so it is not repeated here."""
    out = []
    for label, get in CHIP_ROWS:
        value = get(recipe)
        if value is None or value == 0 and label in ("KELVIN",):
            continue
        out.append(
            f'<div class="chip" style="{chip_css(theme)}">'
            f'<div class="chipLabel" style="font-size:9px;'
            f'color:{css_colour(theme["ink_dim"])}">{html.escape(label)}</div>'
            f'<div class="chipValue" style="font-size:13px;font-weight:700;'
            f'color:{css_colour(theme["ink"])}">{html.escape(str(value))}</div>'
            "</div>")
    return "".join(out)


def pick(catalog: dict, wanted: str | None) -> tuple[dict, str, str, int]:
    """(recipe, group label, 'pos/total', index) for the recipe to render."""
    filters = catalog["filters"]
    labels = {g["id"]: g["label"] for g in catalog["groups"]}
    if wanted:
        for f in filters:
            if f["id"] == wanted:
                idx = f
                break
        else:
            raise SystemExit(f"no recipe {wanted!r} in catalog/filters.json")
    else:
        # Default to something mid-list in a large group, so the counter reads like the
        # real thing ('Kodak 7 / 20') rather than always '1 / 20'.
        kodak = [f for f in filters if f["group"] == "kodak"]
        idx = kodak[len(kodak) // 2] if kodak else filters[0]

    same = [f for f in filters if f["group"] == idx["group"]]
    return idx, labels.get(idx["group"], idx["group"]), f"{len(same)}", same.index(idx) + 1


def meta_line(recipe: dict, engine: str) -> str:
    """An approximation of the summary line MainActivity builds."""
    bits = []
    if engine != "recipe-lab":
        bits.append(engine)
    r = recipe.get("recipe", recipe)
    style = r.get("style")
    if style:
        bits.append(f"Creative Style {style}")
    if r.get("pe"):
        bits.append(f"Picture Effect {r['pe']}")
    wb = r.get("wb") or {}
    if wb.get("mode"):
        bits.append(f"WB {wb['mode']}")
    if r.get("ev"):
        bits.append(f"EV {r['ev']:+.1f}".replace("+0.0", "0"))
    return "  ·  ".join(bits)


SYSTEM_FONT = '"Droid Sans", "Roboto", Arial, sans-serif'


def collect_fonts(dirs: list[Path], theme: dict | None = None
                  ) -> list[tuple[str, dict[int, Path]]]:
    """Group *.ttf in each dir into families: 'Quicksand' -> {400: Regular, 700: Bold}.

    A family that ships only a Regular gets faux-bold from the renderer, which is exactly
    what Android would do with the same file — so the preview is not flattering it.

    With a theme passed, only the two files the theme names are collected. That is the
    default case: the page then shows the face that actually ships, next to the system one,
    rather than every font that happens to sit in assets/fonts/.
    """
    wanted = None
    if theme is not None:
        wanted = {str(theme.get("font_regular", "")), str(theme.get("font_bold", ""))}
    families: dict[str, dict[int, Path]] = {}
    for d in dirs:
        if not d.is_dir():
            raise SystemExit(f"--font-dir {d} is not a directory")
        for p in sorted(d.glob("*.ttf")):
            if wanted is not None and p.name not in wanted:
                continue
            stem = p.stem
            # A variable font ("Nunito[wght]") ships one instance per file and cannot be
            # weight-selected on API 10 - Typeface.create(Typeface, BOLD) would just fake
            # it. Skip it here so the comparison only shows what could actually ship.
            if "[" in stem:
                continue
            weight = 400
            for suffix, w in (("-Regular", 400), ("-Bold", 700), ("-Medium", 500)):
                if stem.endswith(suffix):
                    stem, weight = stem[: -len(suffix)], w
                    break
            families.setdefault(stem, {})[weight] = p
    return sorted(families.items())


def font_faces(families: list[tuple[str, dict[int, Path]]]) -> str:
    """@font-face blocks with the TTFs inlined as base64.

    Inlined on purpose: this page gets opened from a browser preview that may serve it
    from anywhere, and a relative url() to the staging dir would 404 there. Self-contained
    beats small here — it is a throwaway comparison page, not a shipped asset.
    """
    out = []
    for name, weights in families:
        for weight, path in sorted(weights.items()):
            b64 = base64.b64encode(path.read_bytes()).decode("ascii")
            out.append(f'  @font-face {{ font-family:"{html.escape(name)}"; '
                       f'font-weight:{weight}; font-style:normal; '
                       f'src:url(data:font/ttf;base64,{b64}) format("truetype"); }}')
    return "\n".join(out)


def build_html(theme: dict, layout: str, catalog: dict, recipe_id: str | None,
               fork: Path, font_dirs: list[Path] | None = None,
               zoom: float = float(ZOOM)) -> str:
    root = ET.fromstring(layout)
    drawables = patch_ui.drawables_for(theme)

    by_id = {el.get(NS + "id"): el for el in root.iter() if el.get(NS + "id")}
    panel = by_id["@+id/panel"]
    bars = list(panel)
    top, bottom = bars[0], bars[-1]

    recipe, group_label, total, pos = pick(catalog, recipe_id)
    r = recipe.get("recipe", recipe)

    top_css = bar_css(drawables["bar_top.xml"]) + ";" + pad_css(top)
    bottom_css = bar_css(drawables["bar_bottom.xml"]) + ";" + pad_css(bottom)

    title_el, head_el, count_el = by_id["@+id/title"], by_id["@+id/head"], by_id["@+id/count"]
    name_el, badge_el, tag_el = (by_id["@+id/name"], by_id["@+id/badge"],
                                 by_id["@+id/tag"])
    meta_el, hints_el = by_id["@+id/meta"], by_id["@+id/hints"]

    def show(el: ET.Element) -> bool:
        return el.get(NS + "visibility") != "gone"

    families = collect_fonts(font_dirs or [FONT_DIR], theme if not font_dirs else None)
    variants: list[tuple[str, str]] = [("System (Droid Sans — what ships today)",
                                        SYSTEM_FONT)]
    variants += [(name, f'"{html.escape(name)}", {SYSTEM_FONT}') for name, _ in families]

    def frame(family: str) -> str:
        """One 640x480 screen. Everything here is the same for every variant except the
        font-family, which is the whole point of a comparison page."""
        return f"""<div class="stage">
  <div class="frame" style="font-family:{family}">
    <div class="scene"></div>

    <div class="barTop">
      <div class="slot left">
        {f'<span class="ellip" style="{style_for(title_el, theme, fork)}">'
         f'{html.escape(app_name(fork))}</span>' if show(title_el) else ''}
      </div>
      <div class="slot mid" style="gap:{dp(badge_el.get(NS + 'layout_marginLeft'), 8)}px">
        <span class="ellip" style="{style_for(name_el, theme, fork)};max-width:16em">
          {html.escape(recipe['name'])}</span>
        <span class="badge" style="{style_for(badge_el, theme, fork)};{pad_css(badge_el)};"
              >ACTIVE</span>
        {f'<span class="tag" style="{style_for(tag_el, theme, fork)};{pad_css(tag_el)}">'
         f'{"PE" if r.get("pe") else "CS"}</span>' if show(tag_el) else ''}
      </div>
      <div class="slot right">
        <span class="ellip" style="{style_for(count_el, theme, fork)}">
          {html.escape(group_label)}&nbsp;&nbsp;{pos} / {html.escape(total)}</span>
      </div>
    </div>

    <div class="barBottom">
      <div class="ellip" style="{style_for(meta_el, theme, fork)}">
        {html.escape(meta_line(recipe, recipe.get('engine', '')))}
      </div>
      <div class="chipscroll">{chips_html(r, theme)}</div>
      {'<div class="legend"><span><b>&#8592;&#8594;</b> recipe</span>'
       '<span><b>&#8593;&#8595;</b> params</span><span><b>Fn</b> browse</span>'
       '<span><b>ENTER</b> store</span><span><b>AEL</b> hide</span>'
       '<span><b>MENU</b> exit</span></div>' if show(hints_el) else ''}
    </div>
  </div>
</div>"""

    frames = "\n\n".join(
        f'<h2 class="variant">{html.escape(label)}</h2>\n{frame(family)}'
        for label, family in variants)

    page_title = f"{recipe['name']} — main screen preview"
    scene = ("radial-gradient(120% 90% at 30% 20%, #f6f1e6 0%, #d8c7a8 38%, "
             "#8f7f63 70%, #3c352b 100%)")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{html.escape(page_title)}</title>
<style>
  :root {{ color-scheme: light; }}
  body {{
    margin:0; padding:28px; background:#eef1f4; color:#16202b;
    font:14px/1.5 -apple-system, "Segoe UI", "Helvetica Neue", Arial,
         "PingFang SC", "Microsoft YaHei", sans-serif;
  }}
  h1 {{ font-size:17px; margin:0 0 4px; font-weight:700; }}
  p.note {{ margin:0 0 18px; color:#5c6b7a; max-width:760px; font-size:13px; }}
{font_faces(families)}
  .stage {{
    width:{SCREEN_W * zoom}px; height:{SCREEN_H * zoom}px;
    position:relative; overflow:hidden; border-radius:6px;
    box-shadow:0 6px 22px rgba(22,32,43,.28);
  }}
  .frame {{
    width:{SCREEN_W}px; height:{SCREEN_H}px; position:absolute; top:0; left:0;
    transform:scale({zoom}); transform-origin:top left;
    font-family:{SYSTEM_FONT};
  }}
  .scene {{ position:absolute; inset:0; background:{scene}; }}
  h2.variant {{ font-size:13px; margin:22px 0 6px; font-weight:700; color:#16202b; }}
  .barTop {{ position:absolute; top:0; left:0; right:0; {top_css};
             display:flex; align-items:center; }}
  .barTop > .slot {{ display:flex; align-items:center; min-width:0; }}
  .slot.left  {{ flex:1 1 0; justify-content:flex-start; }}
  .slot.mid   {{ flex:0 0 auto; }}
  .slot.right {{ flex:1 1 0; justify-content:flex-end; }}
  .barBottom {{ position:absolute; bottom:0; left:0; right:0; {bottom_css}; }}
  .chipscroll {{ display:flex; gap:6px; overflow-x:auto; margin-top:4px; }}
  .chip {{ padding:3px 8px 4px; }}
  .chipLabel {{ letter-spacing:.06em; }}
  .chipValue {{ line-height:1.15; }}
  .badge {{ border-radius:3px; }}
  .tag {{ border-radius:4px; }}
  .ellip {{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
  .legend {{ margin-top:4px; height:26px; display:flex; gap:12px; align-items:center;
             font-size:9px; color:{css_colour(theme['legend_label'])}; }}
  .legend b {{ font-size:10px; color:{css_colour(theme['legend_key'])}; font-weight:700; }}
  .swatches {{ margin:18px 0 0; display:flex; gap:8px; align-items:center; }}
  .swatches button {{
    font:inherit; font-size:12px; padding:5px 11px; border-radius:6px; cursor:pointer;
    border:1px solid #c3ccd4; background:#fff; color:#16202b;
  }}
  .swatches button.on {{ border-color:#8A5A0B; background:#F2B85C; font-weight:700; }}
  .swatches span {{ color:#5c6b7a; font-size:12px; margin-right:4px; }}
</style>
</head>
<body>
<h1>{html.escape(recipe['name'])}</h1>
<p class="note">Rendered from <code>assets/ui/main.xml</code> +
<code>catalog/ui-theme.json</code> — the same two files <code>tools/patch_ui.py</code>
feeds into every build. Geometry and colour are real; text is not measured, so it does not
wrap or ellipsize the way Android would. Switch the scene behind the bars to check the
frost still holds contrast over a dark frame.</p>

{frames}

<div class="swatches">
  <span>scene behind the bars (applies to every screen above):</span>
  <button class="on" data-scene="{scene}">bright</button>
  <button data-scene="linear-gradient(160deg,#20262c,#0d1014)">dark</button>
  <button data-scene="linear-gradient(160deg,#b9c6d1,#5d6f80)">flat grey</button>
  <button data-scene="linear-gradient(160deg,#f2d9b0,#2b1d10)">high contrast</button>
</div>

<script>
  var buttons = document.querySelectorAll('.swatches button');
  buttons.forEach(function (b) {{
    b.addEventListener('click', function () {{
      document.querySelectorAll('.scene').forEach(function (s) {{
        s.style.background = b.dataset.scene;
      }});
      buttons.forEach(function (o) {{ o.classList.remove('on'); }});
      b.classList.add('on');
    }});
  }});
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--recipe", help="catalog id to render (default: a mid-list Kodak recipe)")
    ap.add_argument("--theme", type=Path, default=patch_ui.DEFAULT_THEME)
    ap.add_argument("--fork", type=Path, default=patch_ui.DEFAULT_FORK,
                    help="checkout to read upstream drawables from (the badge fills)")
    ap.add_argument("--font-dir", type=Path, action="append", default=[],
                    help="dir of *.ttf to compare, inlined as base64 (repeatable)")
    ap.add_argument("--zoom", type=float, default=float(ZOOM),
                    help=f"frame magnification (default {ZOOM})")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help=f"where to write the page (default: {DEFAULT_OUT.name} under build/)")
    args = ap.parse_args()

    theme = patch_ui.load_theme(args.theme)
    # Fill the {ui_package} token from the checkout's manifest (the all-in-one base when
    # the fork has none). Brand packs preview the same way the build would — their custom
    # views reference the renamed package.
    try:
        preview_pkg = patch_ui.package_of(args.fork)
    except SystemExit:
        preview_pkg = patch_ui.BASE_PACKAGE
    layout = patch_ui.layout_for(theme, preview_pkg)
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    page = build_html(theme, layout, catalog, args.recipe, args.fork,
                      args.font_dir, args.zoom)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page, encoding="utf-8")
    print(f"wrote {args.out}  ({len(page)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
