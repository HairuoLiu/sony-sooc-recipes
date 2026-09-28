#!/usr/bin/env python3
"""Build the launcher icons the release workflow drops into the fork's res/drawable-*.

    python tools/build_app_icon.py

Master artwork: assets/app-icon/master.jpg — a dark camera body on a plain white
background. The background is keyed out, so the icon matches what upstream ships
(a transparent RGBA drawable) and reads correctly on both the light and the dark
app-menu tiles these cameras draw.

Why the keying is not a luminance threshold. A plain "bright = transparent" rule
destroys the camera: its chrome lens barrel is nearly as bright as the background.
So the background is found by connectivity instead — flood-fill from the border
through near-white pixels — and a luminance ramp is used only inside a 2px band
around that region, purely to feather the edge. Two consequences worth keeping in
mind if this is ever retuned:

  * specular highlights inside the body stay opaque, because they are not
    reachable from the border;
  * the soft drop shadow under the camera is background-connected, so it is
    dropped. That is deliberate: a semi-transparent grey smudge is worse on a
    dark menu tile than a clean silhouette.

Edge colours are un-mixed against white before any resizing. Without that step a
light fringe survives the downscale and shows up as a pale outline on a dark tile.

Requires Pillow and numpy. The outputs are committed; this script only needs to be
re-run when the master or the crop changes.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "assets" / "app-icon" / "master.jpg"
OUT = ROOT / "assets" / "app-icon"

# Android launcher densities, in px.
DENSITIES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144}
LARGE = 512

# Keying constants. BG_MIN is the near-white cut used for the flood fill; a pixel at or
# above it is background *if* it is connected to the border. EDGE_HI/EDGE_LO bound the
# feather ramp: fully transparent at EDGE_HI and above, fully opaque at EDGE_LO and below.
BG_MIN = 238
EDGE_HI = 250.0
EDGE_LO = 205.0
FEATHER_PX = 2

# The subject is 1.75:1, so width always binds and the camera sits in a horizontal band.
# The margin is deliberately small: upstream's own drawable is full-bleed (its content
# touches all four edges of the 48px square), and at 48px every wasted pixel costs
# legibility. 0.03 leaves a 45px-wide camera in a 48px icon.
MARGIN = 0.03


def luminance(rgb: np.ndarray) -> np.ndarray:
    return 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]


def background_mask(lum: np.ndarray) -> np.ndarray:
    """Near-white pixels reachable from the image border.

    PIL has no region-growing primitive that returns a mask, so the fill is done on a
    binarised copy: background pixels become 128, which leaves the subject at 0 and makes
    the result a plain array comparison.
    """
    h, w = lum.shape
    seed = np.where(lum >= BG_MIN, 255, 0).astype(np.uint8)
    img = Image.fromarray(seed, "L")
    draw = ImageDraw.Draw(img)
    starts = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
              (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]
    for xy in starts:
        if img.getpixel(xy) == 255:
            ImageDraw.floodfill(img, xy, 128, thresh=0)
    return np.asarray(img) == 128


def dilate(mask: np.ndarray, px: int) -> np.ndarray:
    img = Image.fromarray((mask * 255).astype(np.uint8), "L")
    img = img.filter(ImageFilter.MaxFilter(px * 2 + 1))
    return np.asarray(img) > 127


def build_rgba() -> Image.Image:
    rgb = np.asarray(Image.open(MASTER).convert("RGB")).astype(np.float64)
    lum = luminance(rgb)

    bg = background_mask(lum)
    band = dilate(bg, FEATHER_PX)

    alpha = np.where(band, np.clip((EDGE_HI - lum) * 255.0 / (EDGE_HI - EDGE_LO), 0.0, 255.0),
                     255.0)
    alpha[bg] = 0.0

    # Un-mix white out of the semi-transparent ring: the master sits on white, so a pixel
    # at coverage a is really (colour*a + 255*(1-a)). Solve for colour, or the ring keeps
    # a white cast that turns into a pale halo on a dark tile.
    a = alpha / 255.0
    out = rgb.copy()
    soft = (a > 0.15) & (a < 1.0)
    if soft.any():
        asafe = np.where(soft, a, 1.0)[:, :, None]
        mixed = (rgb - 255.0 * (1.0 - asafe)) / asafe
        out = np.where(soft[:, :, None], np.clip(mixed, 0, 255), rgb)

    rgba = np.dstack([out, alpha]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def fit_square(art: Image.Image, side: int, margin: float) -> Image.Image:
    """Centre the art on a transparent square, sized to whichever axis binds first."""
    inner = side * (1.0 - 2.0 * margin)
    aw, ah = art.size
    scale = min(inner / aw, inner / ah)
    nw, nh = max(1, round(aw * scale)), max(1, round(ah * scale))
    resized = art.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(resized, ((side - nw) // 2, (side - nh) // 2), resized)
    return canvas


def main() -> int:
    art = build_rgba()
    bbox = art.getbbox()
    if bbox is None:
        print("keying produced an empty image — is the master on a plain background?",
              file=sys.stderr)
        return 1
    art = art.crop(bbox)

    # Icon requested at 512: hand it the master-resolution art so the downscale starts
    # from everything the source has.
    printed = []
    for name, side in DENSITIES.items():
        path = OUT / f"ic_launcher-{name}.png"
        fit_square(art, side, MARGIN).save(path)
        printed.append((path, side))
    path = OUT / f"icon-{LARGE}.png"
    fit_square(art, LARGE, MARGIN).save(path)
    printed.append((path, LARGE))

    print(f"master {MASTER.name} -> keyed {art.size[0]}x{art.size[1]} px")
    for p, side in printed:
        print(f"  {p.relative_to(ROOT)}  {side}x{side}  {p.stat().st_size} B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
