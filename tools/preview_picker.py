#!/usr/bin/env python3
"""Render the FN recipe browser (PickerView) as an HTML mock, from the same inputs the
APK is built from.

    python tools/preview_picker.py                  # writes build/picker-preview.html
    python tools/preview_picker.py --recipe kodak-gold-200
    python tools/preview_picker.py --out preview.html

Why this exists: tools/preview_ui.py renders the two-bar MAIN screen, but the FN browser
is a Canvas-drawn leaf view (assets/ui/PickerView.java) that the layout-aware preview cannot
reach. So until now every font/colour decision in the browser was made blind. This renders
the same single-column white browser PickerView.onDraw() paints - the same geometry, the
same colours from catalog/ui-theme.json - so a browser tweak you approve here is the one
that ships.

It draws two frames on one page: the CURRENT browser and the browser with the font bumped
by --bump sizes, so a "+2" change is visible before any Java is committed. The bump is a
preview-only simulation; the real number lives in assets/ui/PickerView.java.

What it is NOT: a simulation of Android. Text is not measured, so it does not wrap or
ellipsize exactly the way the camera would - treat it as a good answer to "does this read
well" and a bad answer to "is this pixel-exact". The list window is the same slice the
camera shows (the rows around the selected recipe), not all 155 recipes.
"""

from __future__ import annotations

import argparse
import ast
import base64
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import patch_ui  # noqa: E402

CATALOG = ROOT / "catalog" / "filters.json"
FONT_DIR = ROOT / "assets" / "fonts"
DEFAULT_OUT = ROOT / "build" / "picker-preview.html"

# The LCD this app targets. At 1x one dp is one CSS px; PickerView multiplies every size
# by the device density d, so the same geometry holds at any dpi - only the absolute px
# change. The preview picks a density and zooms the whole frame, the same trick preview_ui
# uses for the main screen.
SCREEN_W, SCREEN_H = 640, 480
DENSITY = 1.5   # assumed camera density for the preview (hdpi-ish); the ratio of the bump
ZOOM = 2        # magnify the 640x480 frame so it is readable in a browser


def css_colour(argb: str | None, default: str = "transparent") -> str:
    """'#F2FBFDFF' -> 'rgba(251,253,242,0.949)'. Android packs alpha first; CSS last."""
    if not argb or not argb.startswith("#"):
        return default
    hexes = argb[1:]
    if len(hexes) == 8:
        a, r, g, b = (hexes[i:i + 2] for i in (0, 2, 4, 6))
        return (f"rgba({int(r, 16)},{int(g, 16)},{int(b, 16)},"
                f"{round(int(a, 16) / 255, 3)})")
    if len(hexes) == 6:
        return "#" + hexes
    return default


def compact_summary(recipe: dict) -> str:
    """Approximate upstream Recipe.summary(): the non-default params as a short string.

    The exact upstream text is not needed to judge a font size, only that there is a
    plausible second line under the recipe name.
    """
    bits: list[str] = []
    style = recipe.get("style")
    if style:
        bits.append(str(style))
    for key, sym in (("sat", "SAT"), ("con", "CON"), ("sharp", "SHARP"), ("ev", "EV")):
        v = recipe.get(key)
        if v:
            bits.append(f"{sym}{v:+d}")
    wb = recipe.get("wb") or {}
    if wb.get("kelvin"):
        bits.append(f"{wb['kelvin']}K")
    return "  ·  ".join(bits) if bits else "standard"


def build_model(catalog: dict) -> tuple[list[str], list[int], list[int], list[dict]]:
    """Mirror the flat arrays PickerView reads from upstream Recipes.

    Returns (group_labels, group_counts, group_starts, all_recipes). every recipe carries
    name, summary(), is_effect(), and group index, matching what onDraw() consumes.
    """
    groups = {g["id"]: g for g in catalog["groups"]}
    order = [g["id"] for g in catalog["groups"]]
    by_group: dict[str, list[dict]] = {gid: [] for gid in order}
    for f in catalog["filters"]:
        gid = f.get("group")
        if gid not in by_group:
            by_group[gid] = []
        recipe = f.get("recipe") or {}
        if isinstance(recipe, str):
            try:
                recipe = ast.literal_eval(recipe)  # trusted local catalog, dict literal
            except Exception:
                recipe = {}
        by_group[gid].append({
            "name": f.get("name", f.get("id", "?")),
            "summary": compact_summary(recipe),
            "is_effect": bool(recipe.get("pe")),
            "_raw": recipe,
        })

    labels: list[str] = []
    counts: list[int] = []
    starts: list[int] = []
    all_recipes: list[dict] = []
    for gid in order:
        items = by_group[gid]
        if not items:
            continue
        labels.append(groups.get(gid, {}).get("label", gid).upper())
        counts.append(len(items))
        starts.append(len(all_recipes))
        all_recipes.extend(items)
    return labels, counts, starts, all_recipes


def pick_selected(catalog: dict, wanted: str | None) -> int:
    """Flat index (header + recipes per group) of the recipe to render as selected.

    Mirrors preview_ui: default to a mid-list Kodak recipe so the counter and window look
    like the real thing rather than always the first item. The flat index is the same one
    PickerView.onDraw() computes to centre the scroll window on the selection.
    """
    filters = catalog["filters"]
    order = [g["id"] for g in catalog["groups"]]
    pos: dict[str, tuple[str, int]] = {}
    for gid in order:
        items = [f for f in filters if f.get("group") == gid]
        for j, f in enumerate(items):
            pos[f["id"]] = (gid, j)

    if wanted:
        if wanted not in pos:
            raise SystemExit(f"no recipe {wanted!r} in catalog/filters.json")
        gid, j = pos[wanted]
    else:
        kodak = [f for f in filters if f.get("group") == "kodak"]
        want = kodak[len(kodak) // 2] if kodak else filters[len(filters) // 2]
        gid, j = pos[want["id"]]

    flat = 0
    for g in order:
        if g == gid:
            break
        flat += 1 + sum(1 for f in filters if f.get("group") == g)
    return flat + 1 + j


def font_faces(theme: dict) -> str:
    """@font-face blocks with Quicksand inlined as base64 - the face the browser ships."""
    out = []
    for name in (str(theme.get("font_regular", "")), str(theme.get("font_bold", ""))):
        p = FONT_DIR / name
        if p.is_file():
            b64 = base64.b64encode(p.read_bytes()).decode("ascii")
            fam = p.stem.replace("-Regular", "").replace("-Bold", "")
            weight = 700 if name.endswith("Bold") else 400
            out.append(f'  @font-face {{ font-family:"{html.escape(fam)}"; '
                       f'font-weight:{weight}; font-style:normal; '
                       f'src:url(data:font/ttf;base64,{b64}) format("truetype"); }}')
    return "\n".join(out)


def render_frame(theme: dict, catalog: dict, bump: int, selected_flat: int,
                 font_family: str) -> str:
    """One 640x480 browser screen at the given font bump, as HTML/CSS."""
    d = DENSITY
    labels, counts, starts, all_recipes = build_model(catalog)
    ng = len(labels)
    total = 0
    for g in range(ng):
        total += 1 + counts[g]

    pad = 12 * d
    top = pad + 16 * d
    bottom = SCREEN_H - pad - 24 * d
    list_top = top
    list_h = bottom - list_top
    row_h = 30 * d

    gsel = 0
    for gi, s in enumerate(starts):
        if selected_flat >= s and selected_flat < s + counts[gi] + 1:
            gsel = gi
            break
    flat = 0
    for gg in range(gsel):
        flat += 1 + counts[gg]
    flat += 1 + (selected_flat - starts[gsel])
    visible = max(1, int(list_h / row_h))
    first = max(0, min(flat - visible // 2, total - visible))

    head_sz = (9 + bump) * d
    item_sz = (13 + bump) * d
    small_sz = (10 + bump) * d

    bg = css_colour(theme["frost_top_start"])
    ink = css_colour(theme["ink"])
    dim = css_colour(theme["ink_dim"])
    accent = css_colour(theme["accent"])
    accent_ink = css_colour(theme["accent_ink"])
    rule = css_colour(theme["chip_idle"])
    fam_css = f'"{html.escape(font_family)}", "Droid Sans", Arial, sans-serif'

    rows: list[str] = []
    y = list_top - first * row_h
    draw_flat = 0
    for gg in range(ng):
        if draw_flat >= first and y < bottom:
            rows.append(
                f'<div style="position:absolute;left:{pad}px;top:{y + 2 * d}px;'
                f'font-size:{head_sz}px;font-weight:700;letter-spacing:.05em;'
                f'color:{dim};font-family:{fam_css}">'
                f'{html.escape(labels[gg])}  ·  {counts[gg]}</div>')
        draw_flat += 1
        y += row_h
        for k in range(counts[gg]):
            if draw_flat >= first and y < bottom:
                idx = starts[gg] + k
                rc = all_recipes[idx]
                on = idx == selected_flat
                if on:
                    rows.append(
                        f'<div style="position:absolute;left:{pad - 4 * d}px;'
                        f'top:{y - 3 * d}px;width:{SCREEN_W - 2 * pad + 8 * d}px;'
                        f'height:{row_h - 5 * d}px;background:{accent};'
                        f'border-radius:{4 * d}px"></div>')
                name_col = accent_ink if on else ink
                sum_col = accent_ink if on else dim
                tag = "PE" if rc["is_effect"] else "CS"
                tag_w = max(head_sz + 16 * d, 52 * d)
                # reserve the tag column on the right and clip the name/sub-text to it, so a
                # long name cannot run under the tag (mirrors PickerView's clipRect)
                name_max = SCREEN_W - 2 * pad - tag_w - 8 * d
                rows.append(
                    f'<div style="position:absolute;left:{pad}px;top:{y + 1 * d}px;'
                    f'max-width:{name_max}px;overflow:hidden;text-overflow:ellipsis;'
                    f'white-space:nowrap;font-size:{item_sz}px;font-weight:700;'
                    f'color:{name_col};font-family:{fam_css}">{html.escape(rc["name"])}</div>')
                rows.append(
                    f'<div style="position:absolute;left:{pad}px;top:{y + 13 * d}px;'
                    f'max-width:{name_max}px;overflow:hidden;text-overflow:ellipsis;'
                    f'white-space:nowrap;font-size:{small_sz}px;color:{sum_col};'
                    f'font-family:{fam_css}">{html.escape(rc["summary"])}</div>')
                rows.append(
                    f'<div style="position:absolute;right:{pad}px;top:{y + 12 * d}px;'
                    f'width:{tag_w}px;height:{12 * d}px;line-height:{12 * d}px;text-align:center;'
                    f'font-size:{9 * d}px;font-weight:700;border-radius:{2 * d}px;'
                    f'color:{sum_col};background:{rule if not on else "rgba(26,18,8,.2)"};'
                    f'font-family:{fam_css}">{tag}</div>')
            draw_flat += 1
            y += row_h
            if y > bottom and draw_flat >= first + visible:
                break
        if y > bottom and draw_flat >= first + visible:
            break

    legend = (f'<div style="position:absolute;left:{pad}px;right:{pad}px;'
              f'bottom:{pad}px;display:flex;gap:{18 * d}px;align-items:center;'
              f'font-size:{9 * d}px;color:{dim};font-family:{fam_css}">'
              f'<span><b style="font-size:{10 * d}px">&#8597;</b> move</span>'
              f'<span><b style="font-size:{10 * d}px">&#9166;</b> pick</span>'
              f'<span><b style="font-size:{10 * d}px">Fn</b> close</span></div>')

    header = (f'<div style="position:absolute;left:{pad}px;top:{pad + 1 * d}px;'
              f'font-size:{head_sz}px;font-weight:700;color:{ink};'
              f'font-family:{fam_css}">RECIPES&nbsp;&nbsp;·&nbsp;&nbsp;'
              f'{len(all_recipes)}</div>')

    return f"""<div class="stage" style="background:{bg}">
  <div class="frame" style="font-family:{fam_css}">
    {header}
    <div style="position:absolute;left:{pad}px;right:{pad}px;top:{top - 5 * d}px;
         height:1px;background:{rule}"></div>
    {''.join(rows)}
    {legend}
  </div>
</div>"""


def build_html(theme: dict, catalog: dict, bump: int, selected_flat: int,
               font_family: str, zoom: float = float(ZOOM)) -> str:
    before = render_frame(theme, catalog, 0, selected_flat, font_family)
    after = render_frame(theme, catalog, bump, selected_flat, font_family)
    fam_css = f'"{html.escape(font_family)}", "Droid Sans", Arial, sans-serif'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>FN browser preview — font +{bump}</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ margin:0; padding:28px; background:#eef1f4; color:#16202b;
         font:14px/1.5 -apple-system, "Segoe UI", "Helvetica Neue", Arial,
         "PingFang SC", "Microsoft YaHei", sans-serif; }}
  h1 {{ font-size:17px; margin:0 0 4px; font-weight:700; }}
  p.note {{ margin:0 0 18px; color:#5c6b7a; max-width:820px; font-size:13px; }}
  .pair {{ display:flex; gap:28px; flex-wrap:wrap; align-items:flex-start; }}
  h2 {{ font-size:13px; margin:0 0 6px; font-weight:700; }}
  .stage {{ width:{SCREEN_W * zoom}px; height:{SCREEN_H * zoom}px; position:relative;
            overflow:hidden; border-radius:6px; box-shadow:0 6px 22px rgba(22,32,43,.28); }}
  .frame {{ width:{SCREEN_W}px; height:{SCREEN_H}px; position:absolute; top:0; left:0;
            transform:scale({zoom}); transform-origin:top left; }}
</style>
</head>
<body>
<h1>FN recipe browser — font {"+" + str(bump) if bump else "current"}</h1>
<p class="note">Rendered from <code>assets/ui/PickerView.java</code> +
<code>catalog/ui-theme.json</code> + <code>catalog/filters.json</code> — the same white
single-column browser the APK paints. The right frame simulates the font bumped by {bump}
sizes (name {13 + bump}sp, summary {10 + bump}sp, header {9 + bump}sp); the left is the
current build. Geometry and colour are real; text is not measured, so it does not ellipsize
exactly as the camera would. Density assumed {DENSITY} (the bump is a ratio, so it reads the
same at any density).</p>

<div class="pair">
  <div>
    <h2>Current (9 / 13 / 10 sp)</h2>
    {before}
  </div>
  <div>
    <h2>After (+{bump}: {9 + bump} / {13 + bump} / {10 + bump} sp)</h2>
    {after}
  </div>
</div>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--recipe", help="catalog id to render as selected (default: a mid Kodak)")
    ap.add_argument("--bump", type=int, default=2, help="sizes to add to every font (default 2)")
    ap.add_argument("--theme", type=Path, default=patch_ui.DEFAULT_THEME)
    ap.add_argument("--zoom", type=float, default=float(ZOOM), help=f"frame zoom (default {ZOOM})")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output HTML path")
    args = ap.parse_args()

    theme = patch_ui.load_theme(args.theme)
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    selected = pick_selected(catalog, args.recipe)

    # Font family the browser actually ships (Quicksand), for a faithful face in the page.
    regular = str(theme.get("font_regular", ""))
    font_family = FONT_DIR / regular
    fam = font_family.stem.replace("-Regular", "").replace("-Bold", "") if font_family else "Quicksand"

    page = build_html(theme, catalog, args.bump, selected, fam, args.zoom)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page, encoding="utf-8")
    print(f"wrote {args.out}  ({len(page)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
