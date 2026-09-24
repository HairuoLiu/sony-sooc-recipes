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

The repository holds **164 filters** across **15 groups** and **2 engines**:

- **149** are compiled into the app (engine `recipe-lab`): **77** transcribed verbatim from the
  upstream project, plus **72** authored in this repository (the camera-simulation, film, brand-pack
  and app-look batches).
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
build/recipe-lab-sony-pmca/src/com/hairuoliu/sonysoocrecipes/Recipes.java
        │
        │  tools/build_apk.sh  →  upstream build.sh
        │  (JDK 17 + Android SDK build-tools 30.0.3 + platform API 28 + NDK r16b)
        ▼
SonySOOCRecipes-<tag>.apk          ──  signing key stays local, never committed
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

| | upstream project | Film Studio / 胶片工坊 |
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

### Why this repository uses the upstream project as its engine

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
it. There are **eight CI gates** plus the release build.

| # | Gate | Script | What it blocks |
|---|---|---|---|
| 1 | Registry legal | `validate_catalog.py` | Wrong enum, out-of-range value, broken group contiguity, dishonest licence claim, a `film-studio` entry carrying parameters |
| 1b | Authored cases | `tests/test_catalog.py` | A home-grown recipe with no pinned case in `tests/cases.json`, or a value that drifted from its case. `TestAuthoredHaveCases` fails the suite if `source: authored-here` has no case |
| 1c | UI theme (`run UI theme test cases`) | `tests/test_ui_theme.py` | The frosted two-bar main screen: the layout keeps every view id `MainActivity` binds, every referenced drawable and string resolves, and every colour is `#AARRGGBB`. A wrong visibility value stops aapt from inflating — the app dies on launch. Numbered 1c rather than 2 because it is the same kind of check as 1 and 1b: a cheap static check on tracked inputs, in the same job. Gate 2 is already the Recipes.java step |
| 3 | Fidelity | `check_fidelity.py` | **A recipe value silently changed** vs. upstream — the APK would then shoot different colours than the project it builds on. Compares every recipe value-for-value, expanded to full 15-value form so shorthand spelling matches |
| 4 | Browser | `gen_browser.py` + `tests/smoke_browser.js` | A typo in the single-file browser that would ship a blank page; also fails if `catalog/index.html` is stale |
| 5 | README counts | `check_readme_counts.py` | The README's filter counts no longer match the catalog |
| 6 | Assets | `check_assets.py` | A document pointing at an image that does not exist; an image hotlinked from a third-party host (status badges excepted — they are generated per request, so vendoring one would freeze a build status); a sample in `docs/assets/samples/` not named `<recipe-id>--off.jpg` / `--on.jpg` with an id that exists in the catalog |
| 7 | Bilingual docs | `check_docs.py` | An English document with no `.zh-CN.md` twin and no entry in `ENGLISH_ONLY` saying why; a twin whose English original is gone; CJK text inside a shared `docs/assets/*.svg` (the diagrams serve both languages); a count drawn inside a diagram that the catalog has outgrown. It cannot judge whether a translation is *faithful* and does not pretend to |

Steps in order:

1. You edit `catalog/filters.json` (never `Recipes.java`).
2. Gate 1 + 1b run on every push/PR to `catalog/`, `tools/`, `tests/`; the UI theme gate
   (`tests/test_ui_theme.py`, the CI step named "run UI theme test cases") is part of the same
   local-gate family and guards the main-screen layout (see [§10](#10-the-main-screen-is-a-replayed-patch-not-committed-source)).
3. Gate 3 fetches upstream `Recipes.java` and checks value-for-value fidelity.
4. `gen_recipes.py` regenerates `Recipes.java`; the artifact is uploaded for inspection.
5. Gate 4 regenerates and smoke-tests the browser.
6. Gate 5 checks README counts.
7. Gate 6 scans every README and `docs/*.md` for image references and fails on a missing file, a
   third-party hotlink (status badges excepted), or a mis-named sample in `docs/assets/samples/`.
8. Gate 7 checks the bilingual document set: every document is either twinned or declared
   English-only, the shared `docs/assets/*.svg` diagrams carry no translated text, and the counts
   drawn inside those diagrams still match the catalog.
9. On a `v*` tag, `release.yml` re-runs gates 1+1b, then clones upstream at the **pinned
   `UPSTREAM_SHA`**, rebrands the fork, applies the pack transform and the launcher icon, replays
   the frosted main screen (`patch_ui.py`), regenerates, builds with JDK 17 + build-tools 30.0.3 +
   NDK r16b, and attaches `SonySOOCRecipes-<tag>.apk` + a SHA-256 sum to the GitHub Release.

> **Honest note.** The upstream revision is pinned in **two** places — `catalog/filters.json`
> (`sources.recipe-lab.fetched_rev`) and `release.yml` (`UPSTREAM_SHA`) — and `test_catalog.py`
> (`TestPinnedUpstream`) fails if they disagree. A tag must always build the exact upstream it was
> validated against; an unpinned clone could build a different APK next month.
>
> The **build steps themselves** are written out twice for the same reason and carry the same risk:
> once in `tools/build_apk.sh` and once in `release.yml`. `TestBuildPipelinesAgree` (same file) holds
> them together, and that test is not theoretical — it exists because the drift had already happened.
> `release.yml` was missing the `patch_ui.py` step, so the **v0.7.0 APKs shipped upstream's main
> screen** while this file, the CHANGELOG and the README all described the frosted two-bar screen as
> shipped. Every gate was green: the theme's tools were all tested, and nothing tested that the
> release build ran them.

**Brand packs.** The same pipeline also builds one app per camera brand. `catalog/packs.json`
lists the packs, and `release.yml` derives its build matrix from that file at run time — one
job per pack plus the all-in-one, each cloning upstream fresh and running `apply_pack.py`, then
`patch_ui.py`, then `gen_recipes.py --pack <id>`. A pack differs from the all-in-one only in package
name, `app_name`, and launcher icon; the *why* is in [docs/BRAND-PACKS.md](BRAND-PACKS.md). Gate 6
(`check_assets.py`) now also covers `assets/app-icon/` and every
`assets/app-icon-packs/<icon_set>/`, so a missing density or an orphan icon set fails the build.

---

## 8. Repository layout

This section maps the tree so the paths above make sense.

```
sony-sooc-recipes/
├── assets/app-icon/          launcher icon set — transparent RGBA, 4 densities + 512 px master
├── assets/app-icon-packs/     per-brand-pack launcher icon sets, one dir per icon_set
├── catalog/
│   ├── filters.json          ★ single source of truth — all filters live here
│   ├── packs.json             brand-pack definitions (id, app_name, groups, icon_set) + unassigned_groups
│   ├── index.html            browsable filter browser (single file, no deps)
│   └── README.md             field reference
├── docs/
│   ├── INSTALL.md                  dual-channel install
│   ├── INSTALL.zh-CN.md            Chinese install guide
│   ├── ARCHITECTURE.md             this file (English)
│   ├── ARCHITECTURE.zh-CN.md       中文版
│   ├── BRAND-PACKS.md              brand packs — why, how, trademark, icons
│   ├── BRAND-PACKS.zh-CN.md        品牌包中文版
│   ├── ADDING-FILTERS.md           full "add a filter" flow
│   ├── ADDING-FILTERS.zh-CN.md     Chinese version
│   ├── FAQ.md                      frequently asked questions
│   ├── FAQ.zh-CN.md                Chinese FAQ
│   ├── CHANNEL-COMPARISON.md       USB vs Wi-Fi ADB, with a verdict
│   ├── MAPPING-RECIPES.md          maps a desired look to achievable camera settings
│   ├── LUT-TO-SETTINGS.md          how a .cube becomes a recipe, and what is lost doing it
│   └── assets/                     diagrams + README (architecture.svg, engines.svg, parameters.svg, install-flow.svg)
├── tools/
│   ├── validate_catalog.py   registry gate (CI gate 1)
│   ├── cataloglib.py         shared catalog/packs access: one count, one load_pack
│   ├── gen_recipes.py        registry → Recipes.java (CI gate 2 step); --pack narrows to one brand
│   ├── check_fidelity.py     value-for-value vs upstream (CI gate 3)
│   ├── gen_browser.py        browser generator (CI gate 4)
│   ├── check_readme_counts.py README counts (CI gate 5)
│   ├── check_assets.py       image / asset references + icon-set gate (CI gate 6)
│   ├── check_docs.py         twin coverage, shared diagrams, counts drawn in diagrams (CI gate 7)
│   ├── install-wifi.sh       Wi-Fi ADB install helper
│   ├── apply_pack.py         rewrites package name + app name for one brand pack
│   ├── patch_ui.py           replays the frosted two-bar main screen onto the upstream checkout (after apply_pack, before gen_recipes); adds `-A assets` to the upstream aapt call
│   ├── preview_ui.py         renders the patched main screen so you can see it without a camera
│   ├── build_app_icon.py     regenerates the all-in-one launcher icon set from a source photo
│   └── build_apk.sh          calls upstream build.sh; --pack / --all-packs build the packs
├── tests/
│   ├── test_catalog.py       33 cases + invariants (CI gate 1b)
│   ├── test_packs.py         pack transform, matrix and subset cases (CI + release)
│   ├── test_gates.py         the self-test: breaks one thing per gate, asserts failure
│   ├── test_ui_theme.py      the frosted two-bar main screen: view ids, drawables/strings, #AARRGGBB colours (25 cases)
│   ├── cases.json            pinned values for authored-here recipes
│   └── smoke_browser.js      browser smoke test (CI gate 4)
├── .github/workflows/
│   ├── ci.yml                all gates, split across jobs
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

**Provenance is enforced, not documented.** The line between MIT (the upstream project, transcribed verbatim and
locked by fidelity checks) and PolyForm Noncommercial (Film Studio, name-only) is a *test*, not a
paragraph. Blurring it is the one mistake that would make the repository unsafe to host, so
`validate_catalog.py` and `test_catalog.py` fail the build over it.

---

## 10. The main screen is a replayed patch, not committed source

This section explains why the app's frosted two-bar main screen is not in the source tree, and why
each piece of it is the way it is. If you only want to change a colour or a toggle, edit
`catalog/ui-theme.json` and `assets/ui/main.xml`; everything below is the *why*.

### Why it is a replayed patch

The main screen is produced by replaying a patch onto the upstream checkout at build time. It is
**not** source that lives in this repo. Three tracked inputs drive it: `catalog/ui-theme.json` (every
colour, plus the three on-screen toggles), `assets/ui/main.xml` (the layout itself) and
`assets/fonts/` (the bundled faces and the licence text that has to travel with them).
`tools/patch_ui.py` replays them onto a checkout, and `tools/preview_ui.py` renders the result so you
can see it without a camera.

The reason it is a patch and not a hand-edit under `build/`: `build/` is gitignored, and
`tools/build_apk.sh` resets the checkout to the pinned upstream revision before every build —
`prepare_fork` runs `git reset --hard` and `git clean -fdxq`. A hand edit made under `build/`
survives exactly zero builds: the next build throws it away. So the only inputs that matter are the
tracked ones, and the only writer of the layout is `patch_ui.py`. That is the same
single-source-of-truth discipline as `filters.json` → `Recipes.java`, just one level further down.

`patch_ui.py` runs in **both** pipelines — `build_apk.sh` locally, `release.yml` on a tag, which is
what `TestBuildPipelinesAgree` exists to assert — **after** `apply_pack` and **before**
`gen_recipes`. The order
is not arbitrary: the layout references the app's custom views by fully-qualified class name, and
`apply_pack` renames that class name per brand pack and fills the package in from the checkout's own
`AndroidManifest.xml`. A layout that named the class before the rename would not match any class the
pack actually ships.

### The frost is simulated, not blurred

`minSdkVersion 10` (Gingerbread) has no RenderScript (API 11+) and no RenderEffect (API 31+), so
there is no blur primitive to reach for. A "frosted glass" bar here is what frosted glass was before
blur existed: a translucent layer at ~0.90 alpha, a faint gradient sheen, and rounded inner corners
that read as a glass slab. The high alpha is deliberate, not cosmetic — the camera frame behind the
bars can be arbitrarily bright or dark, and at high enough alpha the composite stays light, so the
dark text keeps its contrast over any scene. Lower the alpha and that guarantee stops holding: a
bright frame bleeds through and the text vanishes into it.

### The font is bundled, and aapt fails silently without a flag

The font is **Quicksand** (SIL OFL 1.1), Regular + Bold, about 157 KB the pair, shipped as a raw
asset under `assets/fonts/` and bound to the views in Java with `Typeface.createFromAsset`. API 10
ships no rounded system font, and `android:fontFamily` / `res/font` are API 26, so there is no system
route to a rounded face — the font has to travel with the APK. Consequence: each APK grows by roughly
the size of the two `.ttf` files.

Critically, `patch_ui.py` also adds `-A assets` to the upstream `build.sh` / `build.cmd` aapt call.
Upstream ships no `assets/` directory at all, and aapt **silently omits** a missing assets directory
rather than complaining. If that flag is ever lost, the app does not crash — it quietly renders Droid
Sans. That silent fallback is the one failure mode here with no error message anywhere: the build
still succeeds, the gate still passes, and only a human comparing the screen against the design would
notice. The flag is the only thing standing between the design and a silently wrong font.

The licence travels by the same route and for a harder reason: `patch_ui.py` copies `assets/fonts/`
**whole**, so `OFL-Quicksand.txt` reaches the APK beside the faces it covers. The OFL's one
redistribution condition is that the licence accompanies the font, and a licence obligation left
behind in the repository is not met — see [NOTICE.md](../NOTICE.md). It is also the failure mode
least likely to be noticed, since a missing text file changes nothing about how the app looks.

### The toggles, and why a wrong value kills launch

Three on-screen toggles live in the theme file: `legend_visibility` (currently `"gone"` — the row of
glyphs and labels under the chips; with no touchscreen, navigation is the camera's wheel and dial, so
that row is the only on-screen reminder of what ENTER and AEL/DISP do), `app_title_visibility`, and
`tag_visibility` (the CS / PE chip behind the recipe name: CS = Creative Style, the camera's own look
engine, which survives into RAW; PE = Picture Effect, which only lands on JPEG). A wrong visibility
value is not a soft failure — it makes aapt fail to **inflate** the layout, and the app dies on
launch. That is the failure the gate exists to catch.

### The gate that protects all of it

`tests/test_ui_theme.py` is the only thing standing between a bad colour or a dropped view id in
`catalog/ui-theme.json` / `assets/ui/` and an APK that fails to inflate its layout on the camera.
`build/` is wiped before every build, so nothing else in `run_all.py` would notice a broken theme. The
gate enforces four things: the layout keeps every view id `MainActivity` binds with `findViewById`;
every drawable and string the layout references resolves; every colour is `#AARRGGBB`; and every
`@id/x` a view points at was created earlier in the same file. (25 cases.) It runs locally, like the
catalog and assets gates — CI runs it as a step named "run UI theme test cases".

That fourth rule is a static stand-in for aapt, and it exists because of a real failure: the layout
pointed at `@id/head` on one view while the bar owning `@+id/head` was declared further down, and
aapt resolves ids in a single document-order pass. It failed at the first step of the upstream build
— during `R.java` generation — so the theme could not compile at all, which stayed invisible for as
long as no pipeline that ran `patch_ui.py` was ever exercised. aapt itself cannot run here (3 GB of
NDK r16b), so the rule is checked on the text instead.

> **Honest note.** This is the one gate whose loss would not even turn CI red: the silent `-A
> assets` fallback means a missing font ships as Droid Sans with no error anywhere. The layout and
> colour checks are mechanical; the font flag is the part you have to notice by hand.
