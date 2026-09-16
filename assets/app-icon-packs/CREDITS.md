# Brand-pack icon artwork — provenance and licences

Each brand pack carries a launcher icon built from a photograph of the camera that pack is
named after. This file records where every one of those photographs came from and under
what licence, because for most of them **attribution is a licence condition, not a
courtesy**.

## What the licence rule is, and why it is this strict

Only **public domain, CC0, or CC BY** images are accepted. Two families are excluded on
purpose:

- **CC BY-SA** carries a share-alike term. The icon is an *adapted* work — the photograph is
  reframed, cropped and then resized — so share-alike would propagate to the adaptation, and
  in practice to the application that distributes it. That would force this whole app under
  CC BY-SA, which it is not. This is why the first Fujifilm pick was rejected.
- **CC BY-NC / CC BY-ND** forbid commercial use and derivatives respectively, and an icon is
  both.

CC BY is accepted because it permits commercial use, at the cost of a mandatory attribution
obligation. That obligation is discharged in three places, all of which must stay in sync:
this file, `NOTICE.md`, and the release notes for the pack in question (a user who downloads
only `SonySOOCRecipes-kodak.apk` never sees this repository, so the credits have to travel
with the APK).

## Attribution table

All eight packs have an icon. Three carry no attribution obligation at all — two are CC0
(`fujifilm`, `kodak`) and one is public domain (`hasselblad`). The other five are CC BY, so
their author credit is a licence condition.

| Pack | Camera | Author | Licence | Source |
|------|--------|--------|---------|--------|
| `fujifilm` | Fujifilm FinePix X100 (2011) | frank mckenna (frankiefoto), via Unsplash | **CC0** — no attribution required | [File:Fujifilm FinePix X100 with Fujinon Asph Super EBC 23mm F2](https://commons.wikimedia.org/wiki/File:Fujifilm_FinePix_X100_with_Fujinon_Asph_Super_EBC_23mm_F2_(Unsplash_JbTBJYOEc28).jpg) |
| `hasselblad` | Hasselblad 500C (1957) | Holger Ellgaard | Public domain (PD-self) — no attribution required | [File:Hasselblad 500C.jpg](https://commons.wikimedia.org/wiki/File:Hasselblad_500C.jpg) |
| `ilford` | Ilford Sporti (c. 1955) | Matthew Paul Argall | CC BY 4.0 — attribution required | [File:Ilford Sporti camera.jpg](https://commons.wikimedia.org/wiki/File:Ilford_Sporti_camera.jpg) |
| `kodak` | Kodak Instamatic 255-X (1970–1972) | 2538O | **CC0** — no attribution required | [File:Kodak Instamatic 255-X.jpg](https://commons.wikimedia.org/wiki/File:Kodak_Instamatic_255-X.jpg) |
| `leica` | Leica M3 (1954–1966) | Hannes Grobe | CC BY 3.0 — attribution required | [File:Leica-m3 hg.JPG](https://commons.wikimedia.org/wiki/File:Leica-m3_hg.JPG) |
| `pentax` | Asahi Pentax K1000 (1976–1997) | Terry Presley | CC BY 2.0 — attribution required | [File:Pentax K1000 (6301325288).jpg](https://commons.wikimedia.org/wiki/File:Pentax_K1000_(6301325288).jpg) |
| `ricoh` | Ricoh GR (2013) | Kārlis Dambrāns | CC BY 2.0 — attribution required | [File:Ricoh GR (16159018330).jpg](https://commons.wikimedia.org/wiki/File:Ricoh_GR_(16159018330).jpg) |
| `sony` | Sony α7 (ILCE-7, 2013) | Henry Söderlund | CC BY 2.0 — attribution required | [File:Sony A7, A7R, A7S — by Henry Söderlund](https://commons.wikimedia.org/wiki/File:Sony_A7,_A7R,_A7S_-_by_Henry_S%C3%B6derlund_(14700037048).jpg) |

Licence texts: [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) ·
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) ·
[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/) ·
[CC BY 2.0](https://creativecommons.org/licenses/by/2.0/)

Five of the eight therefore need a visible credit wherever the app is distributed. See
`NOTICE.md` for the block that carries it, and remember that an APK is distributed on its
own — a credit that exists only in this repository does not travel with it.

## Rejected: the first Fujifilm pick

`File:Fujifilm X100-IMG 6097.jpg` by Rama is **CC BY-SA 2.0 (fr)** and was rejected after
it had already been downloaded and rendered. The icon reframes and resizes the photograph,
which makes it an adapted work, and share-alike would propagate from the adaptation to the
application distributing it — forcing this whole app under CC BY-SA, which it is not. It was
replaced by the CC0 photograph above. Do not reinstate it, and check the licence before
adding any photograph here.

## Which camera each pack uses, and why

The pick is "the brand's most famous camera", which is a judgement call. The reasoning, kept
here so it can be argued with rather than rediscovered:

- **Leica M3** — the definitive Leica rangefinder. Introduced the M-mount and the
  twin-window silhouette that every later M camera inherited. The Barnack screw-mount Leica I
  is historically more foundational, but the M3 is what "a Leica" looks like.
- **Kodak Instamatic 255-X** — the Instamatic line (126-cartridge, 1963–1970) is the
  best-selling camera range ever, and the name became generic for "point-and-shoot". The
  255-X is a representative 1970 model with a clean, freely-licensed product photograph. The
  original 1900 Brownie is more historically foundational, but its free photographs are
  cluttered; an earlier pick (the Brownie 127) was a minor 127-film variant and was replaced
  for not being the icon.
- **Ilford Sporti** — Ilford is a film manufacturer (HP5, FP4, Delta), not a camera maker; it
  badged cameras built by Dacora of Germany. The Sporti is the best-documented of those under a
  free licence. The Sportsman was considered but has no equally usable photograph.
- **Pentax K1000** — roughly three million units, and for two decades the default "first film
  camera" in every photography course. The 1957 Asahi Pentax created the modern Japanese SLR
  layout, but the K1000 is the model people actually recognise.
- **Hasselblad 500C** — established the modular 6×6 medium-format SLR; its electronic sibling
  the 500EL went to the Moon on Apollo. The 500C is the origin of the shape that means
  "Hasselblad".
- **Ricoh GR (2013)** — brought APS-C quality into a pocketable fixed-lens body and became the
  street-photography tool of its generation; the name descends from the film GR1 that Daido
  Moriyama used. The film GR1 is the alternative pick.
- **Fujifilm FinePix X100** — created the modern retro-styled compact category: hybrid
  optical/electronic viewfinder and physical dials in a fixed-lens APS-C body. Now the
  visual shorthand for "Fujifilm camera". The CC0 photograph is the X100 with its
  Fujinon 23mm f/2, shot against a plain background.
- **Sony α7 (ILCE-7)** — the first full-frame mirrorless camera, and the origin of that
  whole market segment. The α7 III is the best-selling descendant and the RX100 is the
  other defensible pick; the original α7 is the one that changed the industry.

## How the masters were produced

`camera-covers/` in the working tree is where the photographs were collected and the licence
research recorded; it is a scratch directory and is **not** part of this repository. What is
committed is, per pack, `master.jpg` (downscaled to 1600 px on the long edge, JPEG q88) and
the five generated PNGs.

```
python tools/build_pack_icons.py --import <dir-of-<pack-id>.jpg>   # bring a master in
python tools/build_pack_icons.py                                   # render every pack
python tools/build_pack_icons.py --pack leica                      # render one
```

`tools/build_pack_icons.py` frames the camera and rounds the corners; its docstring explains
why these icons keep their photographic background instead of being keyed out the way
`assets/app-icon/` is. If a master is replaced, re-run the render — the PNGs are committed,
so a stale render would otherwise ship.

## Trademark

Separately from copyright: the pack names and the cameras depicted are trademarks of their
respective owners, and this project is not affiliated with or endorsed by any of them. See
the naming discussion in `docs/BRAND-PACKS.md` — that section is deliberately not optimistic
about what a `<Brand> Looks` app name does and does not achieve.
