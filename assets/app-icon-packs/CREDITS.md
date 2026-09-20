# Brand-pack icon artwork — provenance and licences

Most brand packs carry a launcher icon built from a photograph of a *film product*, not a
camera body. Three packs are the exception — they depict a camera body — and one merges several
film families into a single app:

- `leica` shows the Leica M9, a camera body.
- `fujifilm` shows the Fujifilm X100VI, a camera body.
- `hasselblad` shows the Hasselblad X2D II 100C, a camera body.
- `filmstocks` is named after a film stock, not a camera — its icon shows Fujifilm film canisters.
- `kodak` keeps the Kodak name, but its icon is a Kodak Gold 400 / 400 film canister, not a camera body.
- `nichefilm` is the **Niche Film Style** app (`ilford` + `cine` + `other-stocks`), and its icon is a CineStill film product shot, not a camera.
- `pentax`, `ricoh` and `sony` are each a user-supplied film product image — the user has confirmed the picture, and no model or stock name is claimed for any of them.

So the "famous camera" premise holds for only **three** of the nine packs (`leica`, `fujifilm`,
`hasselblad`); the other **six** (`filmstocks`, `ricoh`, `kodak`, `pentax`, `nichefilm`, `sony`)
depict **film stock**, not a camera body — which is honest, because those packs' recipes are
film simulations. This file records where every one of those photographs came from and under what licence,
because whenever a CC BY or other attribution-bearing image is used, **that attribution is a
licence condition, not a courtesy**. As of now no such image ships — see below — but the
record has to stay accurate either way, since a credit left behind for a photograph that is no
longer distributed is itself a misattribution.

## What the licence rule is, and why it is this strict

The standing rule is: only **public domain, CC0, or CC BY** images are accepted. Two families
are excluded on purpose:

- **CC BY-SA** carries a share-alike term. The icon is an *adapted* work — the photograph is
  reframed, cropped and then resized — so share-alike would propagate to the adaptation, and
  in practice to the application that distributes it. That would force this whole app under
  CC BY-SA, which it is not. This is why the first Fujifilm pick was rejected.
- **CC BY-NC / CC BY-ND** forbid commercial use and derivatives respectively, and an icon is
  both.

CC BY remains acceptable in principle because it permits commercial use, at the cost of a
mandatory attribution obligation. That obligation is discharged in three places, all of which
must stay in sync: this file, `NOTICE.md`, and the release notes for the pack in question (a
user who downloads only `SonySOOCRecipes-kodak.apk` never sees this repository, so the credits
have to travel with the APK). **No CC BY image is currently in use**, so the obligation is
dormant — it resumes the day a licensed photograph is added.

### The rule was deliberately relaxed for all nine user-supplied images

All nine packs now use photographs that the **user supplied specifically for this project** —
commercial product photographs and official manufacturer renders. `ricoh` and `pentax` were
the last two Wikimedia Commons CC BY 2.0 photographs and were replaced with user-supplied
images too, so nothing free-licensed is distributed in any pack. These are **all rights
reserved, unlicensed** material. No licence of any kind (not CC0, not CC BY, not public
domain) was granted:

- the project accepted them on the **copyright holder's / user's own instruction**;
- **no licence was granted** by the rights holder — this is not "used with permission",
  because nothing was licensed;
- the **publishing party carries the risk** of distributing all-rights-reserved photographs
  inside the APK. That risk is the publisher's to accept or decline; it is recorded here
  rather than hidden.

Because nothing licensed ships, the former CC BY credit lines for `ricoh` (Ricoh GR by
Kārlis Dambrāns) and `pentax` (Pentax K1000 by Terry Presley) have been removed from this
file, from `NOTICE.md` and from the release notes. Removing them is the honest move: keeping a
credit for a photograph that no longer ships would attribute material the APK does not contain.

## Attribution table

Nine packs have an icon, and all nine carry **no licence at all** — all-rights-reserved
commercial photographs supplied by the user, recorded below with their source but with **no
attribution obligation**, because no licence was granted. There is therefore no CC BY material
in the table any more.

| Pack | Depicts | Author / source | Licence | Source |
|------|---------|----------------|---------|--------|
| `leica` | Leica M9 (2009) | sketch.vip — Leica M9 product render | **All rights reserved** — user-supplied, no licence granted | sketch.vip M9 render |
| `fujifilm` | Fujifilm X100VI (2023) | fujifilm-x.b-cdn.net — X100VI product thumbnail (480×480) | **All rights reserved** — user-supplied, no licence granted | fujifilm-x.b-cdn.net X100VI product thumbnail |
| `filmstocks` | Fujifilm film canisters (film stock) | user-supplied product photograph | **All rights reserved** — user-supplied, no licence granted | user-supplied (pasted image) |
| `ricoh` | Ricoh film product (user-supplied) | user-supplied product photograph | **All rights reserved** — user-supplied, no licence granted | user-supplied (pasted image) |
| `kodak` | Kodak Gold 400 / 400 film canister | prophotosupply.com — Kodak Gold 400 product photo | **All rights reserved** — user-supplied, no licence granted | prophotosupply.com Kodak Gold 400 |
| `pentax` | Pentax film product (user-supplied; source was already a transparent cut-out) | user-supplied product photograph | **All rights reserved** — user-supplied, no licence granted | user-supplied (pasted image) |
| `nichefilm` | CineStill film product | user-supplied product photograph | **All rights reserved** — user-supplied, no licence granted | user-supplied (pasted image) |
| `hasselblad` | Hasselblad X2D II 100C (2022) | cameraelectronic.com.au — official X2D II 100C render (Shopify CDN) | **All rights reserved** — user-supplied, no licence granted | cameraelectronic.com.au product page (Shopify CDN) |
| `sony` | Sony film product (user-supplied) | user-supplied product photograph | **All rights reserved** — user-supplied, no licence granted | user-supplied (pasted image) |

No pack currently needs a visible credit for its icon, because none ships licensed material;
the whole set is user-supplied and unlicensed, and the distribution risk sits with the
publisher instead. If a CC BY image is ever added again, it must be marked as such here, in
`NOTICE.md` and in that pack's release notes — an APK is distributed on its own, so a credit
that exists only in this repository does not travel with it.

Removing the old CC BY entries was part of this change, not an oversight: a credit describing a
photograph that is no longer in the APK would be inaccurate in exactly the way a missing
credit is.

## Rejected: the first Fujifilm pick

`File:Fujifilm X100-IMG 6097.jpg` by Rama is **CC BY-SA 2.0 (fr)** and was rejected after
it had already been downloaded and rendered. The icon reframes and resizes the photograph,
which makes it an adapted work, and share-alike would propagate from the adaptation to the
application distributing it — forcing this whole app under CC BY-SA, which it is not. It was
replaced by the user-supplied X100VI product thumbnail above. Do not reinstate it, and check
the licence before adding any photograph here.

## Which subject (camera body or film product) each pack uses, and why

The pick is "the brand's most famous camera", which is a judgement call. For the six packs
whose icon is film rather than a camera body, the same judgement applies to the *film stock*
depicted. The reasoning, kept here so it can be argued with rather than rediscovered:

- **Leica M9** — Leica's first full-frame digital M-rangefinder (2009), the digital form of
  the M body the M3 established. The M3's reasoning — the M-mount and the twin-window
  silhouette every later M camera inherited — still describes what "a Leica" looks like; the
  M9 is the current camera that shape now names.
- **Kodak Gold 400 / 400 canister** — Kodak Gold 400 is one of Kodak's best-selling consumer
  colour negatives, and its canister is the most recognisable Kodak object that is not a
  camera. The earlier Instamatic 255-X pick was a camera; the current icon is the film itself.
- **nichefilm — CineStill film product** — this pack gathers the **niche and heritage film
  stocks**: the `ilford` group, the `cine` group and `other-stocks` (Agfa, Polaroid,
  Ferrania…), 26 recipes in total. Its icon is a CineStill film product shot, which is why the
  old "Cinestill + Ilford Looks" name never matched — the pack is now named after the niche
  films it carries rather than after one brand. Note that the `cine` group is a
  **motion-picture look family** (Cinestill 50D, Cinestill 800T, classic cinema, Rec709) and is
  **not** an Ilford product.
- **Pentax — user-supplied film product** — the earlier icon was the K1000 (roughly three
  million units, and for two decades the default "first film camera" in every photography
  course; the 1957 Asahi Pentax created the modern Japanese SLR layout, but the K1000 is the
  model people actually recognise). That CC BY photograph has since been replaced by a
  **user-supplied Pentax film image**. This pack's recipes are film simulations, so film rather
  than a body is the honest subject. The source arrived already keyed out, with its own alpha.
- **Hasselblad X2D II 100C** — Hasselblad's current 100 MP medium-format mirrorless body
  (2022); the modern continuation of the 500C's modular 6×6 shape that means "Hasselblad". The
  500C's electronic sibling, the 500EL, went to the Moon on Apollo.
- **Ricoh — user-supplied film product** — the earlier icon was the GR (2013), which brought
  APS-C quality into a pocketable fixed-lens body and became the street-photography tool of its
  generation; the name descends from the film GR1 that Daido Moriyama used. That CC BY
  photograph has since been replaced by a **user-supplied Ricoh film image** — this pack's
  recipes are film simulations, so film rather than a body is the honest subject.
- **Fujifilm X100VI** — the current X100-series camera (2023); the hybrid optical/electronic
  viewfinder compact the original X100 (2011) started. Now the visual shorthand for "Fujifilm
  camera".
- **Sony — user-supplied film product** — the earlier icon was the α7 (ILCE-7), the first
  full-frame mirrorless camera and the origin of that whole market segment; the α7 III is the
  best-selling descendant. That CC BY photograph has since been replaced by a **user-supplied
  Sony film image** — this pack's recipes are film simulations, so film rather than a body is
  the honest subject.
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

`tools/build_pack_icons.py` keys the camera or film product out of its photograph into a
silhouette and composites it onto a solid near-black rounded tile (RGB(28,28,30) ≈ #1C1C1E),
so a dark subject stays legible on a dark launcher wallpaper; the rounded corners stay and
everything outside the rounded rect is transparent, so the icon reads as a launcher badge rather
than a square photo. Pass `--no-bg` to recover the previous transparent-only silhouette. Its
docstring explains the two rendering paths and the framing/keying. If a master is replaced,
re-run the render — the PNGs are committed, so a stale render would otherwise ship.

**The silhouettes now sit on a dark tile.** A pure cut-out was legible on a light wallpaper but
a dark subject (the Leica M9, the Hasselblad body) disappeared into a dark one, so the render
composites each silhouette onto a solid near-black rounded tile (RGB(28,28,30) ≈ #1C1C1E).
Everything outside the rounded rect stays fully transparent, so it still reads as a launcher
badge rather than a square photo. `--no-bg` restores the transparent-only rendering.

## Trademark

Separately from copyright: the pack names and the cameras depicted are trademarks of their
respective owners, and this project is not affiliated with or endorsed by any of them. See
the naming discussion in `docs/BRAND-PACKS.md` — that section is deliberately not optimistic
about what a `<Brand> Style` app name does and does not achieve.
