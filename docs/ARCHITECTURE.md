# Architecture: why it is built this way, and what it can and cannot do

<p align="center"><b>English</b> · <a href="ARCHITECTURE.zh-CN.md">简体中文</a></p>

> **Honest note.** This project does not replicate another brand's colour science. It collects
> film-style "recipes" into one data file, compiles them into an APK, and installs them on pre-2017
> Sony bodies (a6000 / a6300 / a6500 / a5100 / NEX / RX100 III–V / a7 II). Every look below is an
> *approximation built only from settings the camera can store persistently* — not a copy of a LUT, a
> Log curve, or a matrix from another vendor. Read [§5](#5-the-engine-ceiling--what-this-camera-cannot-do)
> before you expect anything specific.

This document explains the architecture: the two engines, what a recipe actually writes into the
camera, the hard limits of the hardware, the data model, the CI pipeline, and *why* the project is
shaped the way it is. If you only want to add a filter, read [`docs/ADDING-FILTERS.md`](ADDING-FILTERS.md)
instead.

---

## 1. What this document is for

This section orients you. The rest of the file is reference: by the end you should understand how a
single JSON file becomes colours on a ten-year-old sensor, and where that path stops.

The repository holds **99 filters** across **13 groups** and **2 engines**:

- **84** are compiled into the app (engine `recipe-lab`): **77** transcribed verbatim from the
  upstream Recipe Lab project, plus **7** authored in this repository.
- **15** are reference-only entries (engine `film-studio-matrix`) — catalogued by name, never
  compiled, never parameterised.

---

## 2. The big picture — data flows from a registry to the camera's settings store

This section shows the whole path in one picture. One file, `catalog/filters.json`, is the single
source of truth; everything downstream is generated from it.

<p align="center">
  <img src="assets/architecture.svg" width="760" alt="architecture">
  <br><sub>Figure: the path from the registry to the camera's settings store</sub>
</p>

```
catalog/filters.json
        │
        │  tools/gen_recipes.py
        ▼
build/recipe-lab-sony-pmca/src/com/voxivoid/recipelab/Recipes.java
        │
        │  tools/build_apk.sh  →  upstream build.sh
        │  (JDK 17 + Android SDK build-tools 30.0.3 + platform API 28 + NDK r16b)
        ▼
RecipeLab-<tag>.apk          ──  signing key stays local, never committed
        │
        │  Sony-PMCA-RE (USB)   or   adb install -r (Wi-Fi)
        ▼
camera settings store  ──  persists after power-off
```

**Editing `Recipes.java` by hand is wrong.** It is regenerated on demand and rejected by CI as stale.
To change a filter, change `catalog/filters.json`.

---

## 3. Two engines, two completely different mechanisms

This section is the single most important thing to understand: **the two upstream projects change
different things.** They are not two flavours of the same trick.

<p align="center">
  <img src="assets/engines.svg" width="760" alt="engines">
  <br><sub>Figure: the settings-store engine vs. the hardware-matrix engine</sub>
</p>

| | Recipe Lab | Film Studio / 胶片工坊 |
|---|---|---|
| Author | [voxivoid](https://github.com/voxivoid/recipe-lab-sony-pmca) | [ukiki0718-netizen](https://github.com/ukiki0718-netizen/sony-a5100-film-studio) |
| Changes | The camera's **persistent settings store**: Creative Style + sat/con/sharp, WB + fine tune, EV, DRO, Picture Effect, plus a colour-matrix switch Sony never exposed in the menu | The in-camera image **pipeline**: a 3×3 hardware colour matrix + a shared 1024-point gamma curve |
| Nature | Like setting a stack of menu values very fast | Real per-pixel colour processing |
| Effective scope | Persists after reboot; covers **P/A/S/M and video**; works with the app closed | Photo + experimental video, with **30 / 50 / 70 / 100%** strength |
| Strength steps | None (one fixed set) | ✅ four steps |
| Model coverage | a6000 / a6500 / a5100 / a7 II verified (per `catalog`); targets all PMCA bodies | **a5100 fw 1.10 only** |
| Dependency | None | Needs a **base APK not shipped with this repo** (bonyback1's Ricoh module, built on Sony "Photo Effect+") |
| License | **MIT** | **PolyForm Noncommercial 1.0.0** (non-OSI, no commercial use) + Fuji/Sony rights reserved |
| Redistributable | ✅ yes | ❌ no |

### Why this repository makes Recipe Lab its engine

1. **Clean licence.** MIT — you can fork, redistribute, and ship the APK freely.
2. **Wide coverage.** One APK covers every PMCA body, instead of being pinned to one firmware.
3. **Generatable.** 77 recipes are just 77 lines in a Java array — naturally produced from data.
4. **Reinstallable.** No separately-fetched base APK, so no "go find base.apk yourself" legal grey zone.

Film Studio is the "harder" route — its matrix is genuine processing — but it is tied to one firmware,
needs an undistributed base APK, and is noncommercial. So this repository keeps it as a **reference
catalogue** (see [§6](#6-the-data-model--what-one-filter-looks-like)), never as an engine.

> **Honest note.** The 15 Film Studio looks are recorded by *name and orientation only*. Their fitted
> numbers are never transcribed into this repo — not only because of the licence, but because those
> numbers were fitted to a different pipeline (matrix + gamma) and would be meaningless inside a
> settings-store engine. `validate_catalog.py` fails the build if a `film-studio` entry ever carries a
> `recipe` object.

---

## 4. What a recipe actually changes

This section lists every field a `recipe-lab` recipe writes, with the legal range the camera (or the
upstream engine) actually enforces. These ranges come straight from `tools/validate_catalog.py`.

| Field | Legal range | What it does |
|---|---|---|
| `style` | `STD` `VIVID` `NEUTRAL` `PORTRAIT` `LANDSCAPE` `MONO` `CLEAR` `DEEP` `LIGHT` `SUNSET` `NIGHT` `AUTUMN` `SEPIA` | Creative Style (the stored enum) |
| `sat` `con` `sharp` | −16…+16 | Creative Style sliders. The menu only shows −3…+3; the camera core accepts more, but the on-screen slider snaps to the nearest menu value and touching it loses the extra punch |
| `matrix` | `0` \| `1` | `1` = the alternate (PP3) colour matrix, ~+45% chroma with blue/green cross-talk. Only takes effect on `VIVID` `CLEAR` `DEEP` `LIGHT` `SUNSET` `NIGHT` `AUTUMN` |
| `wb.mode` | `AUTO` \| `K` | `AUTO` must carry `kelvin: 0`; `K` sets a colour temperature |
| `wb.kelvin` | 2500…9900 | Colour temperature in Kelvin (only when `wb.mode = "K"`) |
| `wb.ab` `wb.gm` | −7…+7 | WB fine tune: `ab` amber(+)/blue(−), `gm` green(+)/magenta(−) |
| `pe` | `0`…`13` | Picture Effect index. **When `pe != 0` the camera ignores Creative Style and disables RAW — JPEG only** |
| `sub` | depends on `pe` | Effect sub-parameter. `pe=0` forces `sub=0`. Only `pe` ∈ {1,3,5,6} expose one (counts 5/2/3/4) |
| `ev` | −5…+5 | Exposure bias, in 1/3-EV steps (persistent) |
| `dro` | `0`…`6` | DRO: `0` off, `1`–`5` level, `6` auto (persistent) |

### The one engine behaviour you must remember

> **Honest note.** When `pe != 0`, the camera **ignates Creative Style** — so `sat` / `con` / `sharp`
> and `matrix` are stored but have no visible effect, and RAW is silently dropped. A `pe` recipe can
> only shoot JPEG. This is upstream camera behaviour, not a bug in this repo, and `validate_catalog.py`
> emits a `note` (not an error) when it sees it.

---

## 5. The engine ceiling — what this camera cannot do

This section is written without polish on purpose. You need the boundaries, not praise. The root cause
is hardware: the a6000 has **no Picture Profile menu**, so it cannot store any tone curve. A recipe can
only use what the body can persist.

**Everything is an approximation, never a reproduction.** Specifically, the following are impossible on
these bodies through this project:

- **Log curves** (S-Log, V-Log, Blackmagic Film, Cinelike D) — no tone curve can be stored.
- **Tinted black & white** (selenium, cyanotype) — only global `ab`/`gm`, which cannot target tone.
- **Sony camcorder *Cinematone* gamma** — present in firmware, but the a6000 camera layer neither lists
  nor accepts it.
- **Real (colour) film grain** — the settings store has no overlay layer. `pe=7` (rough mono) fakes a
  grain *feel* in B&W only.
- **Light leak / genuine vignette as an overlay** — a vignette is reachable *only* via `pe=1` toy-camera,
  which also forces its own colour cast; there is no independent leakage layer.
- **LUT files** — the camera has no LUT support at all.
- **HSL per-channel** — only a global saturation slider plus a global `ab`/`gm` shift.
- **True split-toning** (teal/orange) — only a single global `ab`/`gm` lean is possible; you can fake a
  teal mood (see `teal-mood`) but never a real dual-tone curve.
- **Local adjustments** — no region-aware processing exists in this engine.
- **RAW with a Picture Effect or matrix look** — RAW/RAW+JPEG silently discard them; JPEG only.

> **Honest note.** If a look you want needs any of the above, this camera + this engine cannot deliver
> it. That is the ceiling, stated plainly so you do not waste a shoot finding out.

---

## 6. The data model — what one filter looks like

This section shows the shape of `catalog/filters.json` and three real entries (values copied verbatim
from the file, not invented).

### Top-level fields

| Field | Purpose |
|---|---|
| `version` | Registry format version |
| `engines` | Description, limits, and licence of each engine |
| `sources` | Per-upstream author, licence, fetched revision, redistributable flag |
| `style_constants` / `pe_constants` / `dro_constants` | Stored enums (reverse-engineered from upstream) |
| `groups` | Brand groupings — **order here is the order inside the APK** |
| `filters` | Every filter |

### One filter

| Field | Required | Value | Meaning |
|---|---|---|---|
| `id` | ✔ | kebab-case, unique | Reference key for the generator and docs |
| `name` | ✔ | string | Name shown in the camera app |
| `name_zh` | | string | Chinese name, browser only |
| `group` | ✔ | a `groups[].id` | Brand grouping |
| `engine` | ✔ | `recipe-lab` \| `film-studio-matrix` | Which mechanism |
| `source` | ✔ | `recipe-lab` \| `authored-here` \| `film-studio` | Provenance |
| `tone` | ✔ | `color` \| `mono` | Browser filter |
| `verified` | ✔ | `true` \| `false` | **Validated on real hardware?** |
| `cross_ref` | | another `id` | The twin look in the other engine |
| `note` | | string | Shown in the browser |
| `recipe` | recipe-lab only | object | The parameters (see §4) |
| `strengths` | film-studio only | `[30,50,70,100]` | The four steps |

A `film-studio-matrix` entry **must not** carry `recipe` — `validate_catalog.py` errors on it.

### Real example — a minimal recipe-lab filter (the zero baseline)

```json
{
  "id": "factory-st", "name": "FACTORY (ST)", "name_zh": "出厂标准",
  "group": "sony", "engine": "recipe-lab", "source": "recipe-lab",
  "tone": "color", "verified": true,
  "recipe": { "style": "STD", "sat": 0, "con": 0, "sharp": 0, "matrix": 0,
              "wb": { "mode": "AUTO", "kelvin": 0, "ab": 0, "gm": 0 },
              "pe": 0, "sub": 0, "ev": 0, "dro": 6 }
}
```

### Real example — WB fine tune + exposure bias, still Creative Style

```json
{
  "id": "kodak-gold-200", "name": "Kodak Gold 200", "name_zh": "柯达金 200",
  "group": "kodak", "engine": "recipe-lab", "source": "recipe-lab",
  "tone": "color", "verified": true,
  "recipe": { "style": "STD", "sat": 2, "con": 1, "sharp": 0, "matrix": 0,
              "wb": { "mode": "AUTO", "kelvin": 0, "ab": 3, "gm": 1 },
              "pe": 0, "sub": 0, "ev": 1, "dro": 6 }
}
```

### Real example — matrix switch on + cross-engine twin

```json
{
  "id": "velvia", "name": "Velvia", "group": "fuji-sim",
  "engine": "recipe-lab", "source": "recipe-lab", "tone": "color",
  "verified": true, "cross_ref": "fs-velvia",
  "recipe": { "style": "VIVID", "sat": 5, "con": 1, "sharp": 0, "matrix": 1,
              "wb": { "mode": "AUTO", "kelvin": 0, "ab": 0, "gm": 0 },
              "pe": 0, "sub": 0, "ev": 0, "dro": 6 }
}
```

### Real example — a film-studio-matrix entry (name only, no parameters)

```json
{
  "id": "fs-provia", "name": "PROVIA", "group": "fuji-sim",
  "engine": "film-studio-matrix", "source": "film-studio", "tone": "color",
  "verified": true, "cross_ref": "provia",
  "strengths": [30, 50, 70, 100],
  "note": "Fujifilm GFX ETERNA 55 v1.10 LUT fitted to a 3x3 matrix + 1024-pt gamma. 100% upstream params."
}
```

### Group order is constrained

`recipe-lab` entries **must sit contiguously per group, in the `groups` order** — the generator emits a
`GROUP_START` / `GROUP_COUNT` static block that depends on it, and breaks otherwise. `film-studio-matrix`
entries may interleave with their brand's `recipe-lab` twins (they compile nowhere), which keeps each
brand together in the browser.

---

## 7. The pipeline and its gates — from editing one number to a published APK

This section traces one change from `filters.json` to a signed APK, and names every gate that can stop
it. There are **six CI gates** plus the release build.

| # | Gate | Script | What it blocks |
|---|---|---|---|
| 1 | Registry legal | `validate_catalog.py` | Wrong enum, out-of-range value, broken group contiguity, dishonest licence claim, a `film-studio` entry carrying parameters |
| 1b | Authored cases | `tests/test_catalog.py` | A home-grown recipe with no pinned case in `tests/cases.json`, or a value that drifted from its case. `TestAuthoredHaveCases` fails the suite if `source: authored-here` has no case |
| 3 | Fidelity | `check_fidelity.py` | **A recipe value silently changed** vs. upstream — the APK would then shoot different colours than the project it builds on. Compares every recipe value-for-value, expanded to full 15-value form so shorthand spelling matches |
| 4 | Browser | `gen_browser.py` + `tests/smoke_browser.js` | A typo in the single-file browser that would ship a blank page; also fails if `catalog/index.html` is stale |
| 5 | README counts | `check_readme_counts.py` | The README's filter counts no longer match the catalog |
| 6 | Assets | `check_assets.py` | A document pointing at an image that does not exist; an image hotlinked from a third-party host (status badges excepted — they are generated per request, so vendoring one would freeze a build status); a sample in `docs/assets/samples/` not named `<recipe-id>--off.jpg` / `--on.jpg` with an id that exists in the catalog |

Steps in order:

1. You edit `catalog/filters.json` (never `Recipes.java`).
2. Gate 1 + 1b run on every push/PR to `catalog/`, `tools/`, `tests/`.
3. Gate 3 fetches upstream `Recipes.java` and checks value-for-value fidelity.
4. `gen_recipes.py` regenerates `Recipes.java`; the artifact is uploaded for inspection.
5. Gate 4 regenerates and smoke-tests the browser.
6. Gate 5 checks README counts.
7. Gate 6 scans every README and `docs/*.md` for image references and fails on a missing file, a
   third-party hotlink (status badges excepted), or a mis-named sample in `docs/assets/samples/`.
8. On a `v*` tag, `release.yml` re-runs gates 1+1b, then clones upstream at the **pinned
   `UPSTREAM_SHA`**, regenerates, builds with JDK 17 + build-tools 30.0.3 + NDK r16b, and attaches
   `RecipeLab-<tag>.apk` + a SHA-256 sum to the GitHub Release.

> **Honest note.** The upstream revision is pinned in **two** places — `catalog/filters.json`
> (`sources.recipe-lab.fetched_rev`) and `release.yml` (`UPSTREAM_SHA`) — and `test_catalog.py`
> (`TestPinnedUpstream`) fails if they disagree. A tag must always build the exact upstream it was
> validated against; an unpinned clone could build a different APK next month.

---

## 8. Repository layout

This section maps the tree so the paths above make sense.

```
sony-sooc-recipes/
├── catalog/
│   ├── filters.json          ★ single source of truth — all filters live here
│   ├── index.html            browsable filter browser (single file, no deps)
│   └── README.md             field reference
├── docs/
│   ├── INSTALL.md                  dual-channel install
│   ├── INSTALL.zh-CN.md            Chinese install guide
│   ├── ARCHITECTURE.md             this file (English)
│   ├── ARCHITECTURE.zh-CN.md       中文版
│   ├── ADDING-FILTERS.md           full "add a filter" flow
│   ├── ADDING-FILTERS.zh-CN.md     Chinese version
│   ├── FAQ.md                      frequently asked questions
│   ├── FAQ.zh-CN.md                Chinese FAQ
│   ├── CHANNEL-COMPARISON.md       USB vs Wi-Fi ADB, with a verdict
│   ├── MAPPING-RECIPES.md          maps a desired look to achievable camera settings
│   └── assets/                     diagrams + README (architecture.svg, engines.svg, parameters.svg, install-flow.svg)
├── tools/
│   ├── validate_catalog.py   registry gate (CI gate 1)
│   ├── gen_recipes.py        registry → Recipes.java (CI gate 2 step)
│   ├── check_fidelity.py     value-for-value vs upstream (CI gate 3)
│   ├── gen_browser.py        browser generator (CI gate 4)
│   ├── check_readme_counts.py README counts (CI gate 5)
│   ├── check_assets.py       image / asset references (CI gate 6)
│   ├── install-wifi.sh       Wi-Fi ADB install helper
│   └── build_apk.sh          calls upstream build.sh with the generated Recipes.java
├── tests/
│   ├── test_catalog.py       33 cases + invariants (CI gate 1b)
│   ├── cases.json            pinned values for authored-here recipes
│   └── smoke_browser.js      browser smoke test (CI gate 4)
├── .github/workflows/
│   ├── ci.yml                six gates
│   └── release.yml           tag → build APK → attach to Release
├── LICENSE                   MIT (this repo's code)
└── NOTICE.md                 upstream attribution and licence boundaries
```

---

## 9. Why it is designed this way

This section justifies the two non-obvious decisions: a single source of truth, and generated artifacts
that are **not** committed.

**One source of truth.** Recipes used to get lost because people hand-edited `Recipes.java` in the
upstream fork. Making `catalog/filters.json` the only place a filter is defined means there is exactly
one thing to edit, review, and trust. The generator is the *only* writer of `Recipes.java`.

**Generated artifacts stay out of the repo.** `Recipes.java` and the APK are build outputs. Committing
them would let them drift from the catalog — and CI gate 1b / gate 3 exist precisely to catch that drift.
The generated Java is produced in CI (and locally, on demand) and uploaded as an artifact; the APK is
produced only by `release.yml` and attached to a GitHub Release, never checked in. The signing key is
local and never committed.

**Provenance is enforced, not documented.** The line between MIT (Recipe Lab, transcribed verbatim and
locked by fidelity checks) and PolyForm Noncommercial (Film Studio, name-only) is a *test*, not a
paragraph. Blurring it is the one mistake that would make the repository unsafe to host, so
`validate_catalog.py` and `test_catalog.py` fail the build over it.
