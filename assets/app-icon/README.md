# App icon

The launcher icon the release build drops into the fork's `res/drawable-*/ic_launcher.png`.

| File | Goes to | Size |
|---|---|---|
| `ic_launcher-mdpi.png` | `res/drawable-mdpi/ic_launcher.png` | 48 |
| `ic_launcher-hdpi.png` | `res/drawable-hdpi/ic_launcher.png` | 72 |
| `ic_launcher-xhdpi.png` | `res/drawable-xhdpi/ic_launcher.png` | 96 |
| `ic_launcher-xxhdpi.png` | `res/drawable-xxhdpi/ic_launcher.png` | 144 |
| `icon-512.png` | `dist/icon-512.png` (the fork's README) | 512 |

`master.jpg` is the source artwork, kept so the set is reproducible. Regenerate with:

```bash
python tools/build_app_icon.py     # needs Pillow + numpy
```

## Why the icons are committed rather than generated in CI

`release.yml` clones upstream fresh at a pinned revision, so anything living only in the
fork's working tree is gone by the time the build runs. The icon is a **build input**, the
same way `catalog/filters.json` is: it belongs to this repository, and both the release
workflow and `tools/build_apk.sh` copy it into the checkout.

## Format

Transparent RGBA at all five sizes, matching what upstream ships — the camera's app menu
draws its own tile behind each icon, so a baked-in background would fight it. The set is
**not** adaptive-icon (`<adaptive-icon>` landed in API 26; this app targets API 10).

## The keying, in one paragraph

The master is a dark camera on plain white, so the background is removed by
**connectivity**, not by a brightness threshold — the chrome lens barrel is nearly as white
as the background and a threshold key would punch holes in it. See the header of
`tools/build_app_icon.py` for the details, including why the drop shadow is dropped and why
edge pixels are un-mixed against white before the downscale.
