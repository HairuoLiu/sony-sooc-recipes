# Brand-pack icon artwork — provenance and licences

Most brand packs carry a launcher icon built from a photograph of the camera that pack is
named after. Three packs are the exception, and one is a merged app:

- `filmstocks` is named after a film stock, not a camera — its icon shows Fujifilm film
  canisters.
- `kodak` keeps the Kodak name, but its current icon is a Kodak Gold 400 / 400 film canister,
  not a camera body.
- `ilford` is now the **Cinestill + Ilford** app, and its icon is a CineStill film product
  shot, not a camera.

So the "famous camera" premise holds for six of the nine packs (`leica`, `fujifilm`, `ricoh`,
`pentax`, `hasselblad`, `sony`); the other three (`filmstocks`, `kodak`, `ilford`) depict film
stock. This file records where every one of those photographs came from and under what licence,
because for the CC BY ones **attribution is a licence condition, not a courtesy**.

## What the licence rule is, and why it is this strict

The standing rule is: only **public domain, CC0, or CC BY** images are accepted. Two families
are excluded on purpose:

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

### The rule was deliberately relaxed for seven user-supplied images

Seven of the nine packs (`leica`, `fujifilm`, `filmstocks`, `kodak`, `ilford`, `hasselblad`,
`sony`) now use photographs that the **user supplied specifically for this project** — commercial
product photographs and official manufacturer renders. These are **all rights reserved,
unlicensed** material. No licence of any kind (not CC0, not CC BY, not public domain) was
granted:

- the project accepted them on the **copyright holder's / user's own instruction**;
- **no licence was granted** by the rights holder — this is not "used with permission",
  because nothing was licensed;
- the **publishing party carries the risk** of distributing all-rights-reserved photographs
  inside the APK. That risk is the publisher's to accept or decline; it is recorded here
  rather than hidden.

The two remaining packs (`ricoh`, `pentax`) keep their original CC BY 2.0
photographs from Wikimedia Commons and still require a visible credit wherever the app is
distributed.

## Attribution table

Nine packs have an icon. Seven of them (`leica`, `fujifilm`, `filmstocks`, `kodak`, `ilford`,
`hasselblad`, `sony`) carry **no licence at all** — all-rights-reserved commercial photographs
supplied by the user, recorded below with their source but with **no attribution obligation**,
because no licence was granted. The other two (`ricoh`, `pentax`) are **CC BY 2.0**,
so their author credit is a licence condition and must travel with the APK.

| Pack | Depicts | Author / source | Licence | Source |
|------|---------|----------------|---------|--------|
| `leica` | Leica M9 (2009) | sketch.vip — Leica M9 product render | **All rights reserved** — user-supplied, no licence granted | sketch.vip M9 render |
| `fujifilm` | Fujifilm X100VI (2023) | fujifilm-x.b-cdn.net — X100VI product thumbnail (480×480) | **All rights reserved** — user-supplied, no licence granted | fujifilm-x.b-cdn.net X100VI product thumbnail |
| `filmstocks` | Fujifilm film canisters | user-supplied product photograph | **All rights reserved** — user-supplied, no licence granted | user-supplied (pasted image) |
| `ricoh` | Ricoh GR (2013) | Kārlis Dambrāns | CC BY 2.0 — attribution required | [File:Ricoh GR (16159018330).jpg](https://commons.wikimedia.org/wiki/File:Ricoh_GR_(16159018330).jpg) |
| `kodak` | Kodak Gold 400 / 400 film canister | prophotosupply.com — Kodak Gold 400 product photo | **All rights reserved** — user-supplied, no licence granted | prophotosupply.com Kodak Gold 400 |
| `pentax` | Asahi Pentax K1000 (1976–1997) | Terry Presley | CC BY 2.0 — attribution required | [File:Pentax K1000 (6301325288).jpg](https://commons.wikimedia.org/wiki/File:Pentax_K1000_(6301325288).jpg) |
| `ilford` | CineStill film product | user-supplied product photograph | **All rights reserved** — user-supplied, no licence granted | user-supplied (pasted image) |
| `hasselblad` | Hasselblad X2D II 100C (2022) | cameraelectronic.com.au — official X2D II 100C render (Shopify CDN) | **All rights reserved** — user-supplied, no licence granted | cameraelectronic.com.au product page (Shopify CDN) |
| `sony` | Sony camera | user-supplied product photograph | **All rights reserved** — user-supplied, no licence granted | user-supplied (pasted image) |

Licence texts: [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/)

Two of the nine therefore need a visible credit wherever the app is distributed (the CC BY
2.0 packs: `ricoh`, `pentax`). See `NOTICE.md` for the block that carries it, and
remember that an APK is distributed on its own — a credit that exists only in this repository
does not travel with it.

## Rejected: the first Fujifilm pick

`File:Fujifilm X100-IMG 6097.jpg` by Rama is **CC BY-SA 2.0 (fr)** and was rejected after
it had already been downloaded and rendered. The icon reframes and resizes the photograph,
which makes it an adapted work, and share-alike would propagate from the adaptation to the
application distributing it — forcing this whole app under CC BY-SA, which it is not. It was
replaced by the user-supplied X100VI product thumbnail above. Do not reinstate it, and check
the licence before adding any photograph here.

## Which camera (or film stock) each pack uses, and why

The pick is "the brand's most famous camera", which is a judgement call. For the three packs
whose icon is a film canister rather than a camera, the same judgement applies to the *film
stock* depicted. The reasoning, kept here so it can be argued with rather than rediscovered:

- **Leica M9** — Leica's first full-frame digital M-rangefinder (2009), the digital form of
  the M body the M3 established. The M3's reasoning — the M-mount and the twin-window
  silhouette every later M camera inherited — still describes what "a Leica" looks like; the
  M9 is the current camera that shape now names.
- **Kodak Gold 400 / 400 canister** — Kodak Gold 400 is one of Kodak's best-selling consumer
  colour negatives, and its canister is the most recognisable Kodak object that is not a
  camera. The earlier Instamatic 255-X pick was a camera; the current icon is the film itself.
- **Ilford / Cinestill — CineStill film product** — `ilford` is now the **Cinestill +
  Ilford** app, and its icon is a CineStill film product shot. Note that the `cine` group is a
  **motion-picture look family** (Cinestill 50D, Cinestill 800T, classic cinema, Rec709) and is
  **not** an Ilford product — it is grouped into this pack for distribution convenience, not
  because it is an Ilford film.
- **Pentax K1000** — roughly three million units, and for two decades the default "first film
  camera" in every photography course. The 1957 Asahi Pentax created the modern Japanese SLR
  layout, but the K1000 is the model people actually recognise.
- **Hasselblad X2D II 100C** — Hasselblad's current 100 MP medium-format mirrorless body
  (2022); the modern continuation of the 500C's modular 6×6 shape that means "Hasselblad". The
  500C's electronic sibling, the 500EL, went to the Moon on Apollo.
- **Ricoh GR (2013)** — brought APS-C quality into a pocketable fixed-lens body and became the
  street-photography tool of its generation; the name descends from the film GR1 that Daido
  Moriyama used. The film GR1 is the alternative pick.
- **Fujifilm X100VI** — the current X100-series camera (2023); the hybrid optical/electronic
  viewfinder compact the original X100 (2011) started. Now the visual shorthand for "Fujifilm
  camera".
- **Sony α7 (ILCE-7)** — the first full-frame mirrorless camera, and the origin of that
  whole market segment. The α7 III is the best-selling descendant and the RX100 is the
  other defensible pick; the original α7 is the one that changed the industry.
- **filmstocks — Fujifilm film canisters** — this pack is named after Fujifilm's *film stocks*
  rather than a camera, so its icon is Fujifilm film canisters instead of a body. The recipes in
  the pack (Pro 400H, Superia 400, C200 …) are all Fujifilm colour negatives.

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

`tools/build_pack_icons.py` keys the camera or film stock out of its photograph into a
transparent silhouette (the same treatment as `assets/app-icon/`); its docstring explains the
framing and keying. If a master is replaced, re-run the render — the PNGs are committed,
so a stale render would otherwise ship.

## Trademark

Separately from copyright: the pack names and the cameras depicted are trademarks of their
respective owners, and this project is not affiliated with or endorsed by any of them. See
the naming discussion in `docs/BRAND-PACKS.md` — that section is deliberately not optimistic
about what a `<Brand> Looks` app name does and does not achieve.
