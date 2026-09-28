# Cinema LUT — SonySOOCRecipes-cinema.apk

<p align="center"><b>English</b> · <a href="cinema.zh-CN.md">简体中文</a></p>

## Summary

| | |
|---|---|
| App name | Cinema LUT |
| Package name | com.hairuoliu.sonysoocrecipes.cinema |
| APK filename | SonySOOCRecipes-cinema.apk |
| Compiled recipes | 9 |
| Source groups | Kino LUT |
| Catalog version | 0.6.0 (updated 2026-09-13) |

**At a glance:** this pack compiles **9** colour recipes that reproduce one purchased
motion-picture look — a **Kino**-family cine LUT — as camera settings, one recipe per
white-balance variant the LUT ships.

## Where these numbers come from

This pack is not a brand simulation and not a film-stock guess. The nine recipes were
**measured** out of the LUT files with a script: each `.cube` is parsed, sampled with
trilinear interpolation, linearised through the sRGB transfer function, and converted to a
correlated colour temperature and a Duv offset using the Planckian locus computed by
numerically integrating Planck's law against the CIE 1931 observer. Every value below is a
measurement, not a reading of a filename.

Three findings decided the design:

1. **The 45 files are one look with the dials moved, not 45 looks.** All 45 share an identical
   black point, the five exposure folders fit a single tone curve with the input shifted
   (−0.38 / −0.19 / 0 / +0.23 / +0.48 stops), and the nine white-balance variants fit **pure
   channel gains with the green gain fixed at 1.000** — an amber↔blue move only, which is
   exactly what the camera's A/B axis is.
2. **The exposure sweep is left to the body's dial.** The LUT's five exposure steps span 0.86
   stops in steps of about 0.2; the camera's exposure compensation moves in 1/3-stop clicks, so
   baking the sweep would produce five recipes where the dial gives a continuous, lossless
   answer.
3. **The white-balance sweep becomes nine recipes.** Measured against the LUT's own STANDARD
   step, the nine variants shift −19.4 … +45.2 mired. Shot under roughly 6500 K daylight, each
   one is a kelvin value the camera already has.

## Recipes

Every recipe shares the same base — Creative **NEUTRAL**, saturation 0, contrast 0, sharpness
0, colour matrix off, Picture Effect off, exposure 0, DRO Lv5 — and differs only in white
balance. The base is the look's own cast (a neutral grey lands at CCT ≈ 9580 K / Duv +0.019,
which is about 49 mired of blue plus a slight green lean); the kelvin value carries the blue
half and `G-M +2` carries the green half.

| Name | 中文 | Type | What it is / key settings |
|------|------|------|---------------------------|
| Kino Cool 4 | Kino 冷调 4 | Colour | Coolest of the nine. Measured −19.4 mired against STANDARD, a pure amber↔blue move. Creative Style **NEUTRAL**; DRO Lv5; WB **4500 K**. |
| Kino Cool 3 | Kino 冷调 3 | Colour | Measured −15.5 mired against STANDARD. Creative Style **NEUTRAL**; DRO Lv5; WB **4600 K**. |
| Kino Cool 2 | Kino 冷调 2 | Colour | Measured −11.8 mired against STANDARD. Creative Style **NEUTRAL**; DRO Lv5; WB **4700 K**. |
| Kino Cool 1 | Kino 冷调 1 | Colour | Measured −7.0 mired against STANDARD. Creative Style **NEUTRAL**; DRO Lv5; WB **4800 K**. |
| Kino Standard | Kino 标准 | Colour | The reference step — STANDARD white balance, and the recipe to calibrate against. Creative Style **NEUTRAL**; DRO Lv5; WB **4900 K**. |
| Kino Warm 1 | Kino 暖调 1 | Colour | Measured +15.9 mired against STANDARD. Creative Style **NEUTRAL**; DRO Lv5; WB **5300 K**. |
| Kino Warm 2 | Kino 暖调 2 | Colour | Measured +27.2 mired against STANDARD. Creative Style **NEUTRAL**; DRO Lv5; WB **5700 K**. |
| Kino Warm 3 | Kino 暖调 3 | Colour | Measured +36.5 mired against STANDARD. Creative Style **NEUTRAL**; DRO Lv5; WB **6000 K**. |
| Kino Warm 4 | Kino 暖调 4 | Colour | Warmest of the nine. Measured +45.2 mired against STANDARD. Creative Style **NEUTRAL**; DRO Lv5; WB **6300 K**. |

## Honest note — what these recipes cannot do

This is the most carefully measured group in the repository, and it still cannot be a faithful
copy. The reason is structural, not a matter of effort:

- **The look's teal lives in the shadows, and the camera has no shadow-only colour control.**
  A neutral input at 0.20 renders near **13000 K** with Duv +0.038, while an input at 0.65
  renders almost neutral. That is split toning: the colour shift depends on how bright the
  pixel is. Every colour control this app can write — Creative Style, white balance, the colour
  matrix, saturation — is **global and multiplicative**, and the only two luminance-aware knobs
  are contrast (a one-dimensional curve) and DRO (which lifts shadows but adds no colour). A
  global tint can match one level of the tone scale exactly and nothing else.
- **These nine recipes match the mid-tone.** The kelvin values make a grey card land where the
  LUT puts it, which is the anchor you can actually check on a body. The consequence is stated
  rather than hidden: shadows will come out **less** teal than the LUT, highlights slightly
  more blue.
- **A 3×3 matrix explains only about 65 % of the colour change** — the residual 35 % is exactly
  that tone-dependent behaviour, so selecting the hidden colour-matrix flag would not close the
  gap either.
- **The recipes are unverified.** They are marked `verified: false` in the catalog like every
  other home-grown entry, because the last step — Sony's own colour pipeline, the actual mired
  size of an A/B step, how much DRO Lv5 really lifts — cannot be observed off-camera.

**How to close it:** shoot a grey card under daylight, apply **Kino Standard**, and check the
rendered grey. If it reads cooler or warmer than the target, walk the kelvin value in the
recipe and re-apply; if it reads green or magenta, adjust `G-M`. Then shift each of the other
eight by the same correction — they differ only in the step.

- The other route would be the **Toy Camera (cool)** picture effect, which *does* put a cast in
  the shadows — but it overrides Creative Style entirely (style, saturation and contrast all
  stop working) and adds vignetting and a quality drop. That trade was declined deliberately.

## Provenance and licence

The nine parameter sets here are **original work by this project** and are recorded in
`catalog/filters.json` as `source: authored-here`. No LUT file, table or coefficient from the
purchased pack is redistributed — what ships is a set of ordinary camera settings derived from
measurements of that pack. The LUT pack itself is a commercial product and is **not** included
in this repository or in any APK; you still need your own copy to use it in a raw workflow.
See [NOTICE.md](../../NOTICE.md).

---

**Catalog menu:** [README.md](README.md) · [README.zh-CN.md](README.zh-CN.md)
**Brand packs index:** [../BRAND-PACKS.md](../BRAND-PACKS.md) · [../BRAND-PACKS.zh-CN.md](../BRAND-PACKS.zh-CN.md)
