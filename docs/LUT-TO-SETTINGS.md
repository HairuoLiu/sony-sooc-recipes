# From .cube to camera settings: how one conversion actually works

<p align="center"><b>English</b> · <a href="LUT-TO-SETTINGS.zh-CN.md">简体中文</a></p>

> This answers two questions: **"how did you turn the .cube files in the LUT folder into a recipe
> inside the camera?"** and **"why does it end up as just a few numbers like +1 / −2?"**
>
> In one line: **this is not transcoding, it is measuring and then rewriting.** A 33³ LUT holds
> 35,937 nodes; it gets reduced to roughly 10 scalars — and **none** of those scalars can express
> "change only this hue" or "change only this tonal range".

---

## 1. The two-step pipeline

### Step 1 — measurement: 35,937 nodes down to ~10 numbers

Scripts: `build/analyze_luts.py` (the 18 camera-simulation entries), `measure_leica_luts.py`
(the three Leica entries). Method: read the `.cube`, sample representative colours, reduce to a
"personality" profile. **Read-only — nothing is modified.**

| Metric | How it is measured | Which camera parameter receives it |
|---|---|---|
| `mid_contrast` | Output luma slope between neutral grey 0.3 and 0.8 (1.0 = unchanged) | `con` |
| `sat_ratio` | Lab chroma ratio `co/ci` over 9–10 patches, averaged | `sat` |
| `cast_a` | Mean a\* over the grey ramp (red +/green −) | `gm` |
| `cast_b` | Mean b\* over the grey ramp (yellow +/blue −) | `ab` |
| `shadow_lift` | Luma(out) − luma(in) at 5% grey | `dro` |
| `highlight_compress` | Luma(in) − luma(out) at 95% grey | **nowhere to go** |
| Per-patch hue shift | Lab hue-angle difference in degrees | **nowhere to go** |
| Per-patch saturation ratio | Single-patch chroma ratio | **averaged away** |

### Step 2 — the inverse model: fold the metrics into integers

`derive_settings()` in `measure_leica_luts.py`. This is the entire logic:

```python
sat = clamp(round((sat_ratio - 1.0) * 20), -3, 3)
con = clamp(round((mid_contrast - 1.0) * 20), -3, 3)
ab  = clamp(round(cast_b / 3.0), -3, 3)
gm  = clamp(round(cast_a / 3.0), -3, 3)
dro = clamp(round(shadow_lift * 40), 0, 6)
style = "NEUTRAL" if (sat_ratio < 0.85 and mid_contrast < 1.0) \
        else ("VIVID" if sat_ratio > 1.1 else "STD")
```

Three division constants (20 / 3 / 40), one rounding, one clamp — **that is all of it**. Three
immediate consequences:

- A contrast difference within **±2.5%** rounds to `con = 0`. The information is simply gone.
- A `sat_ratio` above 1.15 or below 0.85 **hits the ±3 ceiling**; the excess strength is truncated.
- A neutral grey ramp with no cast (a\*≈0, b\*≈0) gives `ab = gm = 0` — **even if the chromatic
  regions are heavily cast**, because the formula only ever looks at neutral grey.

> **The two batches differ here.** The camera-simulation (18) and film (38) batches use the same
> measurements but **not the formula**: their values were written by hand from the measured profile
> (`build/add_camera_sims.py`, `build/add_film_batch.py`). The reason is that the formula produces
> demonstrably wrong conclusions where the target space is too small, while a hand-written entry can
> cite a manufacturer's published description and record its own trade-offs in `note`. The three
> Leica entries (CNT / CLS / ETN) are the only ones that ever ran through the formula, because that
> particular request was for a strict, side-by-side comparison.

---

## 2. Everything the camera side actually has

Slot IDs and write ranges come from the fork's `MainActivity.java` (**each parameter is a single
byte slot**); the reachable ranges come from the Sony menu and upstream reverse engineering.

| Slot | Parameter | App can write | **Reachable in the camera menu** |
|---|---|---|---|
| `0x01070175` | Creative Style `style` | 1–13 | pick 1 of 13 |
| `0x01070187` | Saturation `sat` | −16…+16 | **±3 (7 steps)** |
| `0x01070178` | Contrast `con` | −8…+8 | **±3 (7 steps)** |
| `0x0107018a` | Sharpness `sharp` | −8…+8 | ±3 |
| `0x0107031c` | PP3 colour-matrix switch | 0 / 1 | not exposed in the menu at all |
| `0x01070018` | Colour temperature `kelvin` | 25–99 (i.e. 2500–9900K) | ✅ directly adjustable |
| `0x01070017` / `0x01070016` | WB trim `ab` / `gm` | −7…+7 | ±7 (15 steps) |
| `0x010706f1` | Picture Effect `pe` | 0–13 | pick 1 of 14 |
| `0x010700b8` | Exposure compensation `ev` | −15…+15 (1/3 EV steps) | ✅ directly adjustable |
| `0x01070104` | DRO | 0–6 | 7 states |

Total: **one style enum plus about eight global integers.** All of them are global — not one of them
can take a separate value per hue, per tonal range, or per image region.

> **The app can write harder than the menu allows, and it does not help.** Values like `sat = −9`
> can be injected by the APK and the camera will store them, but the on-body Creative Style slider
> tops out at ±3 — the moment you touch the menu, the extra strength snaps away.
> `docs/MAPPING-RECIPES.md` §2.4 lists the 11 current recipes that sit outside that range.

---

## 3. Item-by-item losses — the actual reason for the discrepancy

| What a real LUT can do | What the camera can do | Consequence |
|---|---|---|
| Set saturation per hue | **One** global `sat` | Per-hue information is **averaged away** |
| Rotate a single hue (keep skin put while pushing sky) | Nothing rotates hue | Hue information is **discarded wholesale**; there is no field for it |
| Any tone curve (S-curve, lifted blacks, highlight roll-off) | **One** `con` scalar (no Picture Profile on a6000) | Curve shape has nowhere to go |
| Teal shadows with warm highlights (split-toning) | **One** global `ab`/`gm` | Split-toning degrades to a single overall cast |
| 35,937 × 3 independent output values | ~8 scalars | See below |

**This is an order-of-magnitude gap, not a precision gap.** The result can only be an approximation,
and the discrepancy usually shows up as "a particular hue or tonal range went the *wrong way*",
rather than "the strength is a bit off".

---

## 4. A complete worked example: `LEICA CLS.cube`

**Measured** (33³; data from `leica_lut_diff.txt`):

```
mid_contrast = 1.177                sat_ratio mean = 0.791
grey cast a* = -1.11  b* = +1.17    shadow_lift = -0.026

per-patch saturation ratio:  R 0.93 · G 0.70 · B 0.80 · C 0.71 · M 0.95 · Y 0.75
                             skin 0.77 · foliage 1.03 · sky 0.49
per-patch hue shift:         skin +21° · sky -11° · C -7° · Y +5°
```

**Folded into settings**:

```
sat = round((0.791 - 1) * 20) = round(-4.18) = -4  → clamp → -3   ← hit the ceiling
con = round((1.177 - 1) * 20) = round(+3.54) = +4  → clamp → +3   ← hit the ceiling
ab  = round( 1.17 / 3) = round( 0.39) = 0
gm  = round(-1.11 / 3) = round(-0.37) = 0
dro = round(-0.026 * 40)           = -1  → clamp → 0
style = STD
```

Final expression: **`STD, sat -3, con +3, ab 0, gm 0, dro 0`**. Four losses worth reading carefully:

1. **Both sliders hit the ceiling.** The LUT needs roughly sat −4 and con +4; the 7-step grid cannot
   produce either.
2. **sky is cut to 0.49 while foliage is *raised* to 1.03 — opposite directions.** A single global
   `sat = −3` desaturates foliage too. That is a directional error, not a strength shortfall.
3. **The skin hue rotation of +21° never lands at all**, because there is no field for it.
4. **`shadow_lift` is negative** (the LUT darkens shadows) while `dro` can only lift them, so the
   formula clamps to 0 — **that entire axis is discarded**.

---

## 5. Why the three Leica entries in the catalog show a different set of numbers

`leica-contemporary` / `leica-classic` / `leica-eternal` have `source: recipe-lab` — they come from
the upstream project, not from `authored-here`. The derivation above was a **control experiment** run
to check them, and all three disagreed — so the differences were reported and **the entries were left
alone**. The disagreement is not only in strength; some of it is in direction:

| | Measured LUT character | Derived settings | Upstream catalog recipe |
|---|---|---|---|
| Contemporary | Saturation pulled down, S-curve (+9.6% mid), no grey cast | STD · sat −2 · con +2 · dro 0 | STD · sat +1 · con +1 · dro 6 |
| Classic | Saturation clearly down, S-curve (+17.7%), slightly warm | STD · sat −3 · con +3 · dro 0 | STD · sat −1 · con +2 · ab +1 · dro 6 |
| Eternal | **High contrast** (+31%), magenta–blue cool cast | STD · sat +2 · con +3 · ab −1 · gm +1 | **NEUTRAL, low contrast** · sat −3 · ab +1 · dro 3 |

Eternal is the clearest case: the LUT is high-contrast and cool, the upstream recipe is low-contrast
and warm — **almost fully reversed**.

---

## 6. Checking it yourself

```bash
python build/analyze_luts.py      # measured profile of the 18 camera-simulation entries
python measure_leica_luts.py      # Leica trio: measured vs derived vs upstream → leica_lut_diff.txt
```

Both scripts only **read** the `.cube` files and print results; neither touches the catalog. To add an
entry, follow [`docs/ADDING-FILTERS.md`](ADDING-FILTERS.md).

---

## 7. Conclusion

- This is not "LUT transcoding". It is **reading the LUT's character and re-dialling it on the few
  knobs the camera actually has.**
- The expressiveness gap is one of magnitude: a LUT is a three-dimensional lookup table (per hue,
  per tone), while the camera offers about eight global scalars.
- So **a discrepancy is guaranteed** — and it usually appears as "one hue or tonal range went the
  wrong way" rather than "the strength is slightly off".
- The only technical path to genuinely reproducing a LUT is the `film-studio-matrix` route:
  a hardware 3×3 matrix plus a 1024-point Gamma. It is locked to a5100 firmware 1.10, needs a base
  APK that cannot be redistributed, and is licensed non-commercially.
  See [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) §3.
