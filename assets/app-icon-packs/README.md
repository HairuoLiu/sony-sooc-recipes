# Brand-pack icons

One icon set per brand pack, keyed by the pack's `icon_set` in `catalog/packs.json`.
`tools/apply_pack.py` copies the matching set into the fork's `res/drawable-*` — a pack
with no set here silently keeps `../app-icon/`, so a half-finished set cannot break a build.

| Directory | Pack | Camera |
|---|---|---|
| `hasselblad/` | `hasselblad` | Hasselblad 500C |
| `kodak/` | `kodak` | Kodak Brownie 127 |
| `leica/` | `leica` | Leica M3 |
| `ilford/` | `ilford` | Ilford Sporti |
| `pentax/` | `pentax` | Asahi Pentax K1000 |
| `ricoh/` | `ricoh` | Ricoh GR (2013) |
| `fujifilm/` | `fujifilm` | *pending a compliant photograph* |
| `sony/` | `sony` | *pending a photograph* |

Each directory holds the same five files as `../app-icon/`, at the same pixel sizes and in
the same transparent RGBA format, plus `master.jpg` — the source photograph, downscaled to
1600 px and committed so the set is reproducible:

| File | Goes to | Size |
|---|---|---|
| `ic_launcher-mdpi.png` | `res/drawable-mdpi/ic_launcher.png` | 48 |
| `ic_launcher-hdpi.png` | `res/drawable-hdpi/ic_launcher.png` | 72 |
| `ic_launcher-xhdpi.png` | `res/drawable-xhdpi/ic_launcher.png` | 96 |
| `ic_launcher-xxhdpi.png` | `res/drawable-xxhdpi/ic_launcher.png` | 144 |
| `icon-512.png` | `dist/icon-512.png` (the fork's README) | 512 |

Regenerate after replacing a master:

```bash
python tools/build_pack_icons.py            # needs Pillow + numpy
python tools/build_pack_icons.py --pack leica
```

## Read CREDITS.md before touching any of this

`CREDITS.md` records the author and licence of every photograph here. Most are **CC BY**,
which permits commercial use only with attribution — so the attribution is a licence
condition that has to travel with the APK, not just live in this repository. **CC BY-SA is
disqualifying**: the icon is an adapted work, so share-alike would reach the whole app.
Check the licence before adding or replacing a photograph.

## Why these icons are not keyed out like `../app-icon/`

`../app-icon/` is a single studio shot of a dark camera on plain white, and its builder
removes the background by connectivity. These are seven different photographs from a public
image archive, with backgrounds ranging from seamless white to studio grey to a wooden table.
Luminance keying cannot separate a black camera from a black background without also eating
it, so the pack icons keep their background and are framed instead: the camera is located by
comparing each pixel against the photograph's *own* border colour, framed into a square that
is padded rather than cropped so the camera is never cut off, and given rounded corners.

The visible consequence, and the reason this is worth stating plainly: **the all-in-one
app's icon is a transparent silhouette, the pack icons are rounded photographic tiles.**
They do not look like a set, and that is the intent — eight near-identical silhouettes would
be useless in an app menu, and telling the packs apart at a glance is the entire point of
giving each one its own cover.

See the header of `tools/build_pack_icons.py` for the framing algorithm and the reasoning
behind each step.
