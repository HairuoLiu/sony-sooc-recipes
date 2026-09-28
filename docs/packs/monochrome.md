# Monochrome Style
<p align="center"><b>English</b> · <a href="monochrome.zh-CN.md">简体中文</a></p>

## Summary

| | |
|---|---|
| App name | Monochrome Style |
| Package name | com.hairuoliu.sonysoocrecipes.monochrome |
| **Ships in** | the full installer only — not in the free Base one |
| Compiled recipes | 32 |
| Source groups | 7 (a whitelist spanning Fuji Sim, Kodak, Ricoh GR, Leica, Pana / Olympus, Other Stocks, Ilford) |
| Catalog version | 0.6.0 (updated 2026-09-13) |

**At a glance:** this pack compiles **32** black-and-white recipes — every `tone: mono`
look in the catalog — gathered from across seven groups into one app. It is a curated
**filter whitelist**, not a single brand: the recipes come from Fuji Sim (Acros), Kodak,
Ricoh GR, Leica, Pana / Olympus (L.Monochrome D), Other Stocks and Ilford, because a
monochrome look is something several brands each contribute rather than one brand's
exclusive territory.

## Where these numbers come from

Unlike every other pack, Monochrome does **not** own a group. It is a hand-picked list of
filter ids — 35 of them — drawn from seven groups:

- **Fuji Sim** — Acros and its yellow / red / green filter variants;
- **Kodak** — Tri-X 400, T-Max, Tri-X 1600 (pushed), Eastman Double-X 5222, Plus-X Pan 125;
- **Ricoh GR** — the high-contrast, hard and soft monotone looks, plus Moriyama;
- **Leica** — Monochrom, B&W HC / Natural, Greg WLM, IA, Blu, Sel and Sepia;
- **Pana / Olympus** — L.Monochrome D;
- **Other Stocks** — Ambrotype, Polaroid Type 100 Sepia, Rollei Ortho 25, Svema Type-42;
- **Ilford** — HP5, FP4, Delta 100, Delta 3200, Pan F 50.

Three of those ids (`fs-acros`, `fs-gr-hcbw`, `fs-gr-moriyama`) are `film-studio-matrix`
entries — reference-only, non-redistributable — and compile into nothing, so the 35 ids in
the whitelist become **32 compiled recipes**.

A whitelist pack deliberately spans groups, which means it **shares recipes with the brand
packs by design**. The brand packs keep their black-and-white recipes (Leica Style still
contains Leica Monochrom; Kodak Style still contains Tri-X), and this pack re-includes the
same recipes side by side. That is not duplication — the all-in-one, every brand pack and
this pack all read from the one catalog — it is a different *view* of it. Two of the groups
it draws from (`pana-olympus`, `other-stocks`) are normally kept out of every brand pack for
trademark reasons; here they are pulled in by id, one or four recipes at a time, which is
exactly why this pack exists as a whitelist rather than as a normal group pack.

## Recipes

Every recipe here is a black-and-white or sepia look. All but a handful sit on the camera's
**MONO** or **SEPIA** Creative Style (the exceptions lean on the **rough-mono** Picture
Effect, `pe=7`, for a grainy B&W). The key settings below are taken straight from the
catalog, so they match what the app actually applies.

| Name | 中文 | Type | What it is / key settings |
|------|------|------|---------------------------|
| Acros | 黑白 ACROS | B&W | Acros — Creative **MONO**, sat 0, con 1, sharp 1, DRO Lv6. |
| Acros +Ye (yellow filter) | ACROS 黄滤镜 | B&W | Acros +Ye (yellow filter) — Creative **MONO**, sat 0, con 1, sharp 1, DRO Lv6. |
| Acros +R (red filter) | ACROS 红滤镜 | B&W | Acros +R (red filter) — Creative **MONO**, sat 0, con 0, sharp 0, PE 7, DRO Lv6. |
| Acros +G (green filter) | ACROS 绿滤镜 | B&W | Acros +G (green filter) — Creative **MONO**, sat 0, con 1, sharp 1, DRO Lv6. |
| Sepia | 棕褐色 | B&W | Sepia — Creative **SEPIA**, sat 0, con 0, sharp 0, DRO Lv6. |
| Kodak Tri-X 400 | 柯达 Tri-X 400 | B&W | Kodak Tri-X 400 — Creative **MONO**, sat 0, con 2, sharp 2, EV 1, DRO Lv6. |
| Kodak T-Max | 柯达 T-Max | B&W | Kodak T-Max — Creative **MONO**, sat 0, con 2, sharp 3, DRO Lv6. |
| Kodak Tri-X 1600 (pushed) | 柯达 Tri-X 1600（迫冲） | B&W | Kodak Tri-X 1600 (pushed) — Creative **MONO**, sat 0, con 0, sharp 0, PE 7, EV 1, DRO Lv6. |
| Kodak Eastman Double-X 5222 | 柯达 Eastman Double-X 5222 | B&W | The cine black-and-white negative behind *Schindler's List* and *Roma*: hard, grainy, high-contrast. The catalog had Tri-X but not this cine B&W. Authored-here, not verified on hardware. — Creative **MONO**, sat 0, con 2, sharp 1, DRO Lv3. |
| Kodak Plus-X Pan 125 | 柯达 Plus-X 125 | B&W | A softer, finer-grained classic B&W negative (a 1979 expiry): flat contrast, pulled sharpness, the complement to Double-X's hardness. Authored-here, not verified on hardware. — Creative **MONO**, sat 0, con 0, sharp -1, DRO Lv4. |
| GR Hi-Contrast B&W | GR 高反差黑白 | B&W | GR Hi-Contrast B&W — Creative **MONO**, sat 0, con 3, sharp 1, PE 7, DRO Lv6. |
| GR Hard Monotone | GR 硬调黑白 | B&W | GR Hard Monotone — Creative **MONO**, sat 0, con 2, sharp 2, DRO Lv6. |
| GR Soft Monotone | GR 柔调黑白 | B&W | GR Soft Monotone — Creative **MONO**, sat 0, con -2, sharp -1, DRO Lv6. |
| GR Moriyama (grainy B&W) | GR 森山风 | B&W | Authored-here to fill the one gap the upstream project left (film-studio has it, recipe-lab does not). Not verified on hardware — try it on discardable footage first. — Creative **MONO**, sat 0, con 3, sharp 1, PE 7, EV -1, DRO Lv6. |
| Leica Monochrom | 徕卡 Monochrom | B&W | Leica Monochrom — Creative **MONO**, sat 0, con 2, sharp 1, DRO Lv6. |
| Leica B&W HC | 徕卡 黑白高反差 | B&W | Leica's high-contrast B&W. Measured: pure B&W, contrast 1.20. Authored-here, not verified on hardware. — Creative **MONO**, sat 0, con 2, sharp 1, DRO Lv1. |
| Leica B&W Natural | 徕卡 黑白自然 | B&W | Leica's natural-contrast B&W. Measured: pure B&W, contrast 1.02. Authored-here, not verified on hardware. — Creative **MONO**, sat 0, con 0, sharp 0, DRO Lv4. |
| Leica Greg WLM (warm mono) | 徕卡 Greg WLM（暖调黑白） | B&W | Warm B&W: a slight amber shift (measured R-G +0.014), moderate contrast. Authored-here, not verified on hardware. — Creative **MONO**, sat 0, con 1, sharp 0, DRO Lv3. |
| Leica IA (hard mono) | 徕卡 IA（硬黑白） | B&W | The hardest B&W in the Leica set (measured 1.25), DRO off. One notch harder than B&W HC. Authored-here, not verified on hardware. — Creative **MONO**, sat 0, con 3, sharp 1. |
| Leica Blu (cool mono) | 徕卡 Blu（冷调黑白） | B&W | Cool B&W: near-monochrome (measured saturation 0.19) with a blue lean. MONO plus a blue white-balance fine-tune. Authored-here, not verified on hardware. — Creative **MONO**, sat 0, con 0, sharp 0, DRO Lv3. |
| Leica Sel (pale silver) | 徕卡 Sel（淡银） | B&W | Pale silver-grey: measured saturation 0.14, lifted blacks, flat contrast. One stop brighter overall. Authored-here, not verified on hardware. — Creative **MONO**, sat 0, con 0, sharp -1, EV 1, DRO Lv5. |
| Leica Sepia | 徕卡 褐调 | B&W | Warm sepia: measured saturation 0.20, warm lean (B-G -0.051). Uses the camera's own SEPIA style. Authored-here, not verified on hardware. — Creative **SEPIA**, sat 0, con 0, sharp 0, DRO Lv4. |
| Pana L.Monochrome D | 松下 L.单色D | B&W | Pana L.Monochrome D — Creative **MONO**, sat 0, con 3, sharp 1, DRO Lv6. |
| Ambrotype (wet plate) | 安布罗式湿版 | B&W | The 1850s wet-collodion process: warm-sepia near-B&W, soft contrast, lifted blacks. MONO plus an amber white-balance fine-tune for the warmth. Authored-here, not verified on hardware. — Creative **MONO**, sat 0, con 0, sharp -1, DRO Lv5. |
| Polaroid Type 100 Sepia | 宝丽来 Type 100 褐调 | B&W | The sepia version of Polaroid packfilm (2009): overall brighter, extremely soft contrast. Measured contrast 0.74, saturation 0.27. Authored-here, not verified on hardware. — Creative **SEPIA**, sat 0, con -2, sharp -1, EV 1, DRO Lv6. |
| Rollei Ortho 25 | Rollei Ortho 25 | B&W | Orthochromatic B&W film: blind to red, bright skies, deep skin tones. The camera cannot do orthochromatic response, so only its hard, high-contrast character is kept; the red-channel behaviour cannot be reproduced. Authored-here, not verified on hardware. — Creative **MONO**, sat 0, con 2, sharp 1, DRO Lv2. |
| Svema Type-42 | Svema Type-42 | B&W | Soviet Svema B&W film (1991 expiry): measured essentially pure B&W (saturation 0.11), high contrast (1.28). Authored-here, not verified on hardware. — Creative **MONO**, sat 0, con 2, sharp 0, DRO Lv3. |
| Ilford HP5 | 伊尔福 HP5 | B&W | Ilford HP5 — Creative **MONO**, sat 0, con 1, sharp 0, EV 1, DRO Lv6. |
| Ilford FP4 | 伊尔福 FP4 | B&W | Ilford FP4 — Creative **MONO**, sat 0, con 1, sharp 1, DRO Lv6. |
| Ilford Delta 100 | 伊尔福 Delta 100 | B&W | Ilford Delta 100 — Creative **MONO**, sat 0, con 1, sharp 1, DRO Lv6. |
| Ilford Delta 3200 | 伊尔福 Delta 3200 | B&W | Ilford Delta 3200 — Creative **MONO**, sat 0, con 3, sharp -2, EV 2, DRO Lv6. |
| Ilford Pan F 50 | 伊尔福 Pan F 50 | B&W | Ilford Pan F 50 — Creative **MONO**, sat 0, con 2, sharp 2, DRO Lv6. |

## Honest note — what these recipes cannot do

These are community-derived *approximations*, not copies of any film's response. The engine
ceiling is the same as everywhere else in this project: a 2014-era body cannot store a tone
curve, so every look is assembled from what the settings store can actually hold. For
black-and-white specifically:

- **There is no true silver-grain texture.** The grainy looks (Acros +R, Tri-X 1600, the GR
  high-contrast and Moriyama looks) lean on the camera's `rough-mono` Picture Effect to get
  *a* grain, but it is the engine's one grain source, not a film's grain. Coloured grain is
  impossible — the camera has no such dial.
- **Orthochromatic and split-toning behaviour cannot be reproduced.** Rollei Ortho 25's
  red-blind response and the warm/cool tints of the Leica family are kept as *character*
  only; the underlying spectral or tonal behaviour is beyond the engine.
- **Most of these are unverified.** The handful that are upstream recipes (Acros, the Ilford
  films, the Kodak Tri-X / T-Max) are matched value-for-value to the upstream project and
  trusted; Leica Monochrom carries `verified: true` in the catalog. Everything authored here
  (`gr-moriyama`, the Kodak Double-X / Plus-X, the Leica B&W family, Ambrotype, Rollei Ortho
  25, Svema, Polaroid Type 100 Sepia) is `verified: false`, because the last step — how the
  numbers actually land on a body — cannot be observed off-camera. Each recipe's status lives
  in the `verified` field of `catalog/filters.json`, not on the screen.

**How to close it:** shoot a grey card under daylight, apply a look, and check the rendered
grey; walk the `con` / `sharp` / white-balance fine-tune in the recipe and re-apply.

## Provenance and licence

This pack introduces **no new recipe values**. It is a different selection over the same
catalog that the all-in-one and every brand pack already ship — the same parameter sets, the
same sources (77 upstream recipes matched value-for-value, 72 authored-here), just gathered
by `tone: mono` instead of by brand. The launcher icon is **user-supplied cover art**: the pack
is a cross-brand selection with no single product to photograph honestly, so it shipped an
in-repo drawing (an aperture, in the same spirit as the `cinema` pack's icon) until 2026-09-27,
and a supplied cover until 2026-09-28 — since then it has been a supplied black-and-white
film-strip drawing, cut out and placed on the same dark rounded tile as every other pack.
Full provenance and the standing licence rules are in **[NOTICE.md](../../NOTICE.md)**.

---

**Catalog menu:** [README.md](README.md) · [README.zh-CN.md](README.zh-CN.md)
**Brand packs index:** [../BRAND-PACKS.md](../BRAND-PACKS.md) · [../BRAND-PACKS.zh-CN.md](../BRAND-PACKS.zh-CN.md)
