# Brand-pack icons

One icon set per brand pack, keyed by the pack's `icon_set` in `catalog/packs.json`.
`tools/apply_pack.py` copies the matching set into the fork's `res/drawable-*` — a pack
with no set here silently keeps `../app-icon/`, so a half-finished set cannot break a build.

| Directory | Pack | Camera / depicts |
|---|---|---|
| `filmstocks/` | `filmstocks` | Fujifilm film canisters (film stock) |
| `fujifilm/` | `fujifilm` | Fujifilm X100VI |
| `hasselblad/` | `hasselblad` | Hasselblad X2D II 100C |
| `ilford/` | `ilford` | CineStill film product (film stock) |
| `kodak/` | `kodak` | Kodak Gold 400 / 400 canister (film stock) |
| `leica/` | `leica` | Leica M9 |
| `pentax/` | `pentax` | Pentax camera (user-supplied; source already had a transparent background) |
| `ricoh/` | `ricoh` | Ricoh camera (user-supplied) |
| `sony/` | `sony` | Sony camera |

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

`CREDITS.md` records the author, licence and provenance of every photograph here. **All nine
are now user-supplied commercial renders with no licence at all** — the publisher carries the
risk of distributing them, and there is no attribution obligation today. `ricoh` and `pentax`
were the last two **CC BY 2.0** images (commercial use permitted only with attribution, which
had to travel with the APK rather than live in this repository) and have since been replaced,
so no licensed photograph ships in any pack. Treat that as the current state, not as a rule
change: **CC BY-SA is still disqualifying**, because the icon is an adapted work and share-alike
would reach the whole app. Check the licence before adding or replacing a photograph, and when
you introduce anything licensed, add its credit in all three places (`CREDITS.md`, `NOTICE.md`
and that pack's release notes).

## How these icons are keyed out

`../app-icon/` is a single studio shot of a dark camera on plain white, and its builder
removes the background by connectivity. These are nine different photographs, all user-supplied
commercial renders, with backgrounds ranging from seamless white to studio grey to a wooden
table — and one (`pentax`) arrived already keyed, carrying its own alpha channel. A luminance
threshold cannot separate a black camera from a black background without also eating it, so
connectivity keying does not work for the rest.

Instead each source is segmented semantically with `rembg` (U-Net), blobs far smaller than the
main subject are dropped as specks (`--min-blob-frac`; the default keeps only the largest, while
a multi-object cover such as three canisters needs a lower fraction or the extra objects vanish),
and the result is centred and enlarged to fill ~80% of the square — that is
`tools/cut_camera_covers.py`. `tools/build_pack_icons.py` then renders the cut-out at the four
densities, intersecting its alpha with the rounded-rect mask so the corners stay rounded *and*
the background stays transparent.

The visible consequence, and the reason this is worth stating plainly: **both the all-in-one
icon and the pack icons are transparent silhouettes** cut from their source photograph. The
packs are told apart by which camera or film stock each silhouette depicts, not by a
photographic background — giving each pack its own cover is the whole point of making them
recognisable at a glance.

See the header of `tools/build_pack_icons.py` for the two rendering paths and the reasoning
behind each step.
