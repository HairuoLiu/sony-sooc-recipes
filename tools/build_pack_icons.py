#!/usr/bin/env python3
"""Build each brand pack's launcher icon from its camera photograph.

    python tools/build_pack_icons.py                 # every pack that has a master
    python tools/build_pack_icons.py --pack leica
    python tools/build_pack_icons.py --import ../camera-covers/raw

Master artwork lives at assets/app-icon-packs/<icon_set>/master.jpg, one per pack, and is
committed: a photograph of the camera the pack is named after. The generated PNGs next to
it are what tools/apply_pack.py copies into the fork — see assets/app-icon-packs/CREDITS.md
for the provenance and licence of every photograph, which is a compliance obligation, not
decoration.

Why this is not tools/build_app_icon.py. That script keys the background out of a single
studio shot to match upstream's transparent silhouette, and its docstring is explicit that
the keying works only because the master is a dark camera on a plain *white* background.
These are seven different photographs from a public image archive: backgrounds vary from
pure white through studio grey to dark wood, several have no clean background at all, and
a black camera on a black seamless is indistinguishable from its background by any
luminance rule. Keying them would either leave a grey halo or eat the camera. So the pack
icons keep their background and are *framed* instead — a rounded square, which is what a
launcher icon looks like on modern Android anyway and which reads as deliberate rather
than as a failed cut-out.

The three steps, in order, and why each exists:

  1. **Find the camera.** The subject is located by comparing every pixel against the
     photograph's own border colour — the median of its four edge strips — rather than
     against white. That is what makes this work on a white studio shot and a dark wood
     table alike. The detection runs on a 1024 px proxy: on a 6016 px original the extra
     precision buys nothing and costs seconds, and proxy-scale noise reduction is what
     stops a few stray pixels from stretching the bounding box to the whole frame.

  2. **Frame it square without cropping it.** The crop box is sized to the subject plus a
     margin, so the camera is never cut off, and then the image is *padded* — with its own
     border colour — wherever the subject sits too close to an edge for that square to fit.
     Padding rather than cropping is the important choice: cropping a wide subject out of a
     3:2 frame is exactly how you ship an icon of half a camera.

  3. **Round the corners**, per density, on a 4x supersampled mask. Rounding at 48 px
     directly produces visibly stepped corners.

Requires Pillow and numpy.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PACKS = ROOT / "catalog" / "packs.json"
ICON_ROOT = ROOT / "assets" / "app-icon-packs"

# Android launcher densities, in px. Same set the single-icon builder emits, so a pack's
# icon set is interchangeable with assets/app-icon/ from the build's point of view.
DENSITIES = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144}
LARGE = 512

# Masters are committed, so they are held at the size the largest output can actually use.
# 1600 px is 3x the 512 icon and leaves headroom for retuning the framing later.
MASTER_MAX = 1600
MASTER_QUALITY = 88

# Subject detection.
PROXY = 1024
BG_TOL = 26.0        # per-channel deviation from the border colour that counts as subject
BG_STRIP = 0.02      # the border is sampled from this fraction of each edge
MIN_SUBJECT = 0.06   # a detected subject smaller than this share of the frame is distrust
DENOISE = 3          # odd kernel for the opening that removes speckle before the bbox

# Composition.
MARGIN = 0.06        # breathing room around the camera, as a fraction of its long side
RADIUS = 0.20        # corner radius as a fraction of the icon side
SUPERSAMPLE = 4


def base_rgb(img: Image.Image) -> np.ndarray:
    """RGB float array. Alpha is composited onto white first — a transparent PNG master
    would otherwise read as black and swallow the subject detection."""
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        flat = Image.new("RGBA", img.size, (255, 255, 255, 255))
        flat.alpha_composite(img)
        img = flat
    return np.asarray(img.convert("RGB")).astype(np.float64)


def border_colour(rgb: np.ndarray) -> np.ndarray:
    """Median colour of the four edge strips.

    The median rather than the mean: the subject occasionally touches an edge, and a
    handful of camera pixels should not drag the estimated background colour.
    """
    h, w = rgb.shape[:2]
    t = max(2, int(round(min(h, w) * BG_STRIP)))
    strips = np.concatenate([
        rgb[:t, :, :].reshape(-1, 3),
        rgb[-t:, :, :].reshape(-1, 3),
        rgb[:, :t, :].reshape(-1, 3),
        rgb[:, -t:, :].reshape(-1, 3),
    ])
    return np.median(strips, axis=0)


def _open(mask: np.ndarray, k: int) -> np.ndarray:
    """Binary opening (erode then dilate), which is what removes isolated specks.

    PIL's MinFilter/MaxFilter are the cheapest way to do it without pulling in scipy.
    """
    img = Image.fromarray((mask * 255).astype(np.uint8), "L")
    img = img.filter(ImageFilter.MinFilter(k)).filter(ImageFilter.MaxFilter(k))
    return np.asarray(img) > 127


def content_bbox(rgb: np.ndarray) -> tuple[int, int, int, int]:
    """Bounding box of the subject, in full-resolution coordinates.

    Returns the whole frame if the subject cannot be trusted, which is the safe failure:
    a slightly loose icon beats a crop that has decided the camera is background.
    """
    h, w = rgb.shape[:2]
    scale = min(1.0, PROXY / max(h, w))
    if scale < 1.0:
        small = Image.fromarray(rgb.astype(np.uint8)).resize(
            (max(1, round(w * scale)), max(1, round(h * scale))), Image.BOX)
        proxy = np.asarray(small).astype(np.float64)
    else:
        proxy = rgb

    bg = border_colour(proxy)
    mask = np.abs(proxy - bg).max(axis=2) > BG_TOL
    mask = _open(mask, DENOISE)

    if not mask.any():
        return 0, 0, w, h
    ys, xs = np.where(mask)
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    y0, y1 = int(ys.min()), int(ys.max()) + 1

    inv = 1.0 / scale
    x0, y0 = int(x0 * inv), int(y0 * inv)
    x1, y1 = int(np.ceil(x1 * inv)), int(np.ceil(y1 * inv))
    x1, y1 = min(x1, w), min(y1, h)

    if (x1 - x0) * (y1 - y0) < MIN_SUBJECT * w * h:
        return 0, 0, w, h
    return x0, y0, x1, y1


def frame_square(rgb: np.ndarray) -> Image.Image:
    """A square crop centred on the subject, padded with its own background colour.

    Padding is what guarantees the subject survives: the square is sized from the subject
    itself, so a subject that reaches the top and bottom of a 3:2 frame would need a
    square taller than the frame, and cropping to fit would amputate it. Extending the
    border colour keeps the camera whole and is visually indistinguishable from the
    original background.
    """
    h, w = rgb.shape[:2]
    x0, y0, x1, y1 = content_bbox(rgb)
    bw, bh = x1 - x0, y1 - y0
    side = max(1, int(round(max(bw, bh) * (1.0 + 2.0 * MARGIN))))
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0

    pad_l = max(0, int(np.ceil(side / 2.0 - cx)))
    pad_t = max(0, int(np.ceil(side / 2.0 - cy)))
    pad_r = max(0, int(np.ceil(cx + side / 2.0 - w)))
    pad_b = max(0, int(np.ceil(cy + side / 2.0 - h)))

    if pad_l or pad_t or pad_r or pad_b:
        # An explicit canvas rather than np.pad: a per-channel constant is not something
        # np.pad's constant_values accepts for a 3-D array, and edge replication would
        # smear a textured background (wood grain, fabric) into visible streaks.
        bg = np.round(border_colour(rgb)).astype(np.uint8)
        hh, ww = h + pad_t + pad_b, w + pad_l + pad_r
        canvas = np.empty((hh, ww, 3), dtype=np.uint8)
        canvas[:, :] = bg
        canvas[pad_t:pad_t + h, pad_l:pad_l + w] = rgb.astype(np.uint8)
        rgb = canvas.astype(np.float64)
        cx, cy = cx + pad_l, cy + pad_t

    left = int(round(cx - side / 2.0))
    top = int(round(cy - side / 2.0))
    left = max(0, min(left, rgb.shape[1] - side))
    top = max(0, min(top, rgb.shape[0] - side))
    square = rgb[top:top + side, left:left + side]
    return Image.fromarray(square.astype(np.uint8), "RGB")


def rounded_mask(side: int) -> Image.Image:
    ss = side * SUPERSAMPLE
    m = Image.new("L", (ss, ss), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        [0, 0, ss - 1, ss - 1], radius=RADIUS * ss, fill=255)
    return m.resize((side, side), Image.LANCZOS)


def render(square: Image.Image, out: Path) -> list[tuple[Path, int]]:
    written: list[tuple[Path, int]] = []
    for name, side in DENSITIES.items():
        art = square.resize((side, side), Image.LANCZOS).convert("RGBA")
        art.putalpha(rounded_mask(side))
        p = out / f"ic_launcher-{name}.png"
        art.save(p)
        written.append((p, side))
    art = square.resize((LARGE, LARGE), Image.LANCZOS).convert("RGBA")
    art.putalpha(rounded_mask(LARGE))
    p = out / f"icon-{LARGE}.png"
    art.save(p)
    written.append((p, LARGE))
    return written


def write_master(src: Path, dst: Path) -> tuple[int, int]:
    img = Image.open(src)
    rgb = base_rgb(img)
    h, w = rgb.shape[:2]
    if max(h, w) > MASTER_MAX:
        s = MASTER_MAX / max(h, w)
        rgb = np.asarray(Image.fromarray(rgb.astype(np.uint8)).resize(
            (max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)).astype(np.float64)
    dst.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgb.astype(np.uint8), "RGB").save(
        dst, "JPEG", quality=MASTER_QUALITY, optimize=True)
    return dst.stat().st_size, rgb.shape[1]


def load_packs(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {p["id"]: p for p in data["packs"]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack", help="only this pack (default: every pack with a master)")
    ap.add_argument("--icons", type=Path, default=ICON_ROOT,
                    help="root of the per-pack icon sets")
    ap.add_argument("--import", dest="import_dir", type=Path, metavar="DIR",
                    help="copy DIR/<pack-id>.jpg in as the master for each pack, then stop "
                         "(downscaled to %d px; run again without --import to render)" % MASTER_MAX)
    args = ap.parse_args()

    packs = load_packs(DEFAULT_PACKS)
    if args.pack and args.pack not in packs:
        raise SystemExit(f"no pack {args.pack!r} "
                         f"(have: {', '.join(sorted(packs))})")
    wanted = {args.pack: packs[args.pack]} if args.pack else packs

    # ---- import: bring an external photograph in as the committed master -----------------
    if args.import_dir:
        if not args.import_dir.is_dir():
            raise SystemExit(f"{args.import_dir} is not a directory")
        imported, skipped = [], []
        for pid, pack in sorted(wanted.items()):
            src = args.import_dir / f"{pid}.jpg"
            if not src.is_file():
                skipped.append(pid)
                continue
            size, px = write_master(src, args.icons / pack["icon_set"] / "master.jpg")
            imported.append(f"  {pid:11s} -> {pack['icon_set']}/master.jpg  {px} px  {size} B")
        for line in imported:
            print(line)
        if skipped:
            print(f"  no source photo for: {', '.join(skipped)} "
                  "(that pack keeps the app's default icon)")
        return 0

    # ---- render ---------------------------------------------------------------------------
    missing: list[str] = []
    for pid, pack in sorted(wanted.items()):
        set_dir = args.icons / pack["icon_set"]
        master = set_dir / "master.jpg"
        if not master.is_file():
            missing.append(pid)
            continue
        square = frame_square(base_rgb(Image.open(master)))
        written = render(square, set_dir)
        print(f"{pid}  (icon_set {pack['icon_set']}, app_name {pack['app_name']!r})")
        print(f"  master {master.name} -> square {square.size[0]}x{square.size[1]} px")
        for p, side in written:
            print(f"  {p.relative_to(ROOT)}  {side}x{side}  {p.stat().st_size} B")

    if missing:
        print()
        try:
            shown = args.icons.relative_to(ROOT)
        except ValueError:
            shown = args.icons
        for pid in missing:
            print(f"  note: pack {pid!r} has no master at "
                  f"{shown}/{packs[pid]['icon_set']}/master.jpg — "
                  "it will ship the app's default icon")
    if not wanted or len(missing) == len(wanted):
        print("\nnothing rendered", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
