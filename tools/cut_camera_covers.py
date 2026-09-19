"""Cut the brand-pack cover cameras and film stocks out of their backgrounds and refill ~80%.

This is the visual-unification pass. Every launcher icon is a *cut-out* subject
(transparent background) enlarged to fill ~80% of the square, rather than a framed
photo that keeps its original background.

Why rembg and not the existing luminance keying in build_pack_icons.py: several
of these are black cameras on dark or textured backgrounds, which no luminance
threshold can separate. rembg (U2-Net) does semantic subject segmentation.

This script is deliberately separate from build_pack_icons.py. It produces cut-out
masters under camera-covers/cutout/, named <pack-id>.png; build_pack_icons.py picks
those up automatically (--cutout, default camera-covers/cutout) and renders them as
transparent silhouettes. It never overwrites master.jpg.

The fill target is ~80% of the binding dimension of the subject's bounding box,
which gives a comfortable margin without either a tiny subject or an amputated
one.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from rembg import remove, new_session

ROOT = Path(__file__).resolve().parent.parent
ICON_ROOT = ROOT / "assets" / "app-icon-packs"
OUT = ROOT.parent / "camera-covers" / "cutout"

# rembg model quality vs speed: u2net is the default and good for product shots.
MODEL = "u2net"

# Fill target: the subject's binding bbox side should be ~ this share of canvas.
FILL = 0.80

PACKS = ["leica", "fujifilm", "ricoh", "kodak", "pentax", "ilford",
         "hasselblad", "sony"]


def cut(master: Path) -> Image.Image:
    """Remove background, return an RGBA image at native resolution."""
    raw = master.read_bytes()
    session = new_session(MODEL)
    out = remove(raw, session=session, alpha_matting=True,
                 alpha_matting_foreground_threshold=240,
                 alpha_matting_background_threshold=10,
                 alpha_matting_erode_size=10)
    return Image.open(__import__("io").BytesIO(out)).convert("RGBA")


def clean_mask(a: np.ndarray) -> np.ndarray:
    """Drop isolated specks outside the subject without eating the already-
    matted soft edges. rembg's alpha_matting has already refined the edge, so
    we must NOT re-erode (a second opening destroys a thin camera silhouette).
    Only the largest connected component is kept; everything else is dropped.
    """
    import cv2
    mask = (a > 40).astype(np.uint8)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if n <= 1:
        return mask
    # Keep the largest component (index 0 is the background).
    largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    mask = (labels == largest).astype(np.uint8) * 255
    return mask


def fill80(img: Image.Image) -> tuple[Image.Image, float]:
    """Centre the cutout on a square canvas so it fills ~FILL of the side."""
    a = np.asarray(img)
    mask = clean_mask(a[:, :, 3])
    ys, xs = np.where(mask > 127)
    if len(xs) == 0:
        return img, 0.0
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    w, h = x1 - x0 + 1, y1 - y0 + 1
    subject = img.crop((int(x0), int(y0), int(x1), int(y1)))

    # Canvas sized so the subject's binding side is FILL of it.
    side = max(w, h) / FILL
    side = int(round(side))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    ox = (side - w) // 2
    oy = (side - h) // 2
    canvas.paste(subject, (int(ox), int(oy)), subject)
    fill = max(w, h) / side
    return canvas, fill


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--packs", default=",".join(PACKS),
                    help="comma-separated pack ids (default: all)")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    report = []
    for pid in args.packs.split(","):
        master = ICON_ROOT / pid / "master.jpg"
        if not master.exists():
            print(f"  skip {pid}: no master.jpg")
            continue
        img = cut(master)
        canvas, fill = fill80(img)
        dst = args.out / f"{pid}.png"
        canvas.save(dst)
        report.append((pid, fill, canvas.size))
        print(f"  {pid:11s} fill={fill*100:5.1f}%  -> {dst.name} {canvas.size[0]}x{canvas.size[1]}")

    print("\nsummary:")
    for pid, fill, size in report:
        flag = "OK" if 0.72 <= fill <= 0.88 else "CHECK"
        print(f"  {pid:11s} {fill*100:5.1f}%  {size[0]}px  [{flag}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
