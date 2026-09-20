# Adding a Filter (Recipe)

<p align="center"><b>English</b> · <a href="ADDING-FILTERS.zh-CN.md">简体中文</a></p>

This guide tells you how to add one film-style recipe to `catalog/filters.json`, the
single source of truth. The APK is generated from that file; you never hand-edit the
generated `Recipes.java`.

Two things before you start:

- **Only write docs and `catalog/filters.json`.** Do not touch `tools/`, `tests/`,
  `.github/`, `README.md`, or the other docs. The tests, generator, and CI will turn
  your catalog edit into a build — that machinery is off-limits to edit here.
- **A recipe is an approximation, not a copy.** This camera has no Picture Profile menu,
  no tone curve, no LUT channel, no Log. Every "Kodak", "Fuji", or "Leica" look in this
  repo is rebuilt from only the settings the camera can store persistently. Read
  `docs/MAPPING-RECIPES.md` before inventing parameters; it is the authority on what the
  engine can and cannot do.

---

## 1. When you should add one — and when you should not

The catalog already holds **155 recipes across 14 groups / two engines**. Many
style intervals are already saturated. Adding "another faded warm negative" does not
increase coverage — it dilutes it. The catalog is a reference, not a pile.

`docs/MAPPING-RECIPES.md` §1.2 sorts the original recipe-lab entries (a snapshot) into
12 visual bands. The bands that are **already full** (do not add more of these):

- **Band 3 — low-saturation faded / cinematic** (classic-chrome, eterna, gr-negative-film,
  nikon-flat, rec709-video, gr-bleach-bypass). Generic "faded" looks are covered.
- **Band 8 — high-key soft / pastel faded** (soft-high-key, fuji-pro-400h, olympus-pale-light,
  gr-retro, polaroid-instax, nostalgic-neg). Generic "soft glow" looks are covered.
- **Band 2 — warm everyday negative** (kodak-gold-200, kodak-ultramax-400, kodak-colorplus-200,
  kodak-portra-400/800, fuji-superia-400, agfa-vista-200, leica-classic).

By contrast, §1.3 of that document names intervals that are **genuinely empty and worth
filling** — these are the only self-authored entries that passed review in the initial catalog:

| Look to add | `pe` | Why it is not a duplicate |
|---|---|---|
| Toy-camera (vignette + tint) | `1` | Only route to a vignette on this camera; was unused by all 93 upstream recipes |
| Part-color (selective colour) | `6` | The one route to "keep one hue" on this camera; was unused |
| Posterization | `3` | Flat poster-band separation; was unused |
| Teal mood (clean global teal) | `0` + `ab`/`gm` | Only `gr-cross-process` leans teal currently, and it goes green/magenta, not clean teal |
| Watercolor / Illust | `13` / `12` | Niche but genuinely unused |

> **Honest note.** If your idea is "another faded warm film stock", do not open a PR.
> The repository already has those. The valuable additions are the `pe`-driven effects
> in the table above, or a clearly distinct band. When in doubt, ask in an issue first.

---

## 2. De-duplication check

Do this before writing any JSON.

1. Read `docs/MAPPING-RECIPES.md` §1.2 and find the band your idea belongs to.
2. Grep the catalog for the brand and the rough parameter shape:
   ```bash
   grep -n '"name": "Kodak' catalog/filters.json
   ```
3. Confirm no existing entry already matches your target within ±1 on `sat`/`con` and the
   same `style` + `wb` intent. (e.g. `kodak-gold-200` is `STD, sat 2, con 1, ab 3, gm 1,
   ev 1` — anything closer than that is a duplicate, not a variant.)
4. Check the `id` is not taken: every `id` in the catalog must be unique, and the
   generator also requires unique **`name`** (the display string, not the `id`) among
   recipe-lab entries. A `name` clash makes two recipes indistinguishable in the app list.
5. If it survives steps 1–4, proceed. If not, close the idea or reframe it into an empty band.

---

## 3. The complete parameter table

Every recipe-lab entry carries these fields. Values below are the **real domains the
camera stores**; "menu reachable" tells you whether a user can reproduce the value from
the on-camera menus (slider stops at ±3 — anything beyond is APK-only and the user cannot
dial it in by hand).

| Field | Domain | What it means | What you see on the camera |
|---|---|---|---|
| `style` | `STD` `VIVID` `NEUTRAL` `PORTRAIT` `LANDSCAPE` `MONO` `CLEAR` `DEEP` `LIGHT` `SUNSET` `NIGHT` `AUTUMN` `SEPIA` | Creative Style — the tonal base | The Creative Style picker; stored as an enum (1..13) |
| `sat` | −16…+16 (core); menu only ±3 | Saturation vs. the style default | The Saturation sub-slider; **beyond ±3 the slider shows the nearest value and a user touch loses the extra punch** |
| `con` | −16…+16 (core); menu only ±3 | Contrast vs. the style default | The Contrast sub-slider |
| `sharp` | −16…+16 (core); menu only ±3 | Sharpness vs. the style default | The Sharpness sub-slider |
| `matrix` | `0` standard / `1` alternate | Sony's undisclosed alternate colour matrix (~+45% chroma, blue/green cross-talk). Only takes effect on `VIVID CLEAR DEEP LIGHT SUNSET NIGHT AUTUMN` | Invisible in any menu; only the APK writes it |
| `wb.mode` | `AUTO` / `K` | White balance mode | `AUTO` → no kelvin; `K` → colour-temperature mode |
| `wb.kelvin` | 2500…9900 | Colour temperature, only when `wb.mode = K` | The K-mode temperature; `AUTO` requires `kelvin = 0` |
| `wb.ab` | −7…+7 | Amber(+) / Blue(−) fine tune | WB shift A/B |
| `wb.gm` | −7…+7 | Green(+) / Magenta(−) fine tune | WB shift G/M |
| `pe` | 0…13 | Picture Effect index (see table below) | A separate effect family; when non-zero, **Creative Style is ignored by the camera** |
| `sub` | per `pe` | Effect sub-parameter | Only some effects use it (table below) |
| `ev` | −5…+5 (1 unit = ⅓ EV) | Exposure bias | Stored exposure compensation |
| `dro` | `0` off / `1`–`5` level / `6` auto | DRO (dynamic-range optimiser) | DRO menu |

`pe` index table (stored as the runtime effect index — this is exactly what the camera records):

| `pe` | Name | `sub` values | Notes |
|---|---|---|---|
| 0 | off | — | Style/sat/con/sharp/matrix all active |
| 1 | toy-camera | 0 normal · 1 cool · 2 warm · 3 green · 4 magenta | Carries a vignette + tint; **only** vignette route on this camera |
| 2 | pop-color | — | — |
| 3 | posterization | 0 color · 1 b&w | — |
| 4 | retro-photo | — | Built-in faded/yellowed look |
| 5 | soft-high-key | 0 blue · 1 pink · 2 green | High-key lift |
| 6 | part-color | 0 red · 1 green · 2 blue · 3 yellow | Selective colour |
| 7 | rough-mono | — | Coarse grain B&W (the only grain source) |
| 8 | soft-focus | — | — |
| 9 | hdr-art | — | — |
| 10 | richtone-mono | — | — |
| 11 | miniature | — | — |
| 12 | illust | — | — |
| 13 | watercolor | — | — |

Real examples straight from the catalog:

- `kodak-gold-200` (warm everyday neg): `STD, sat 2, con 1, sharp 0, matrix 0,
  wb AUTO kelvin 0 ab 3 gm 1, pe 0, sub 0, ev 1, dro 6`.
- `olympus-pop-art` (extreme saturation, APK-only): `VIVID, sat +8, matrix 1` —
  `sat +8` is past the menu's ±3, so a user cannot reproduce it by hand.
- `eterna-bleach-bypass`: `NEUTRAL, sat -9, con 3` — the most extreme `sat` in the catalog.
- `teal-mood` (authored): `NEUTRAL, sat -3, ab -2, gm 1` — stays inside the menu's ±3,
  unlike most upstream extremes.

> **Honest note.** `sat`/`con`/`sharp` core-accept −16…+16, but the body menu stops at
> ±3. Existing entries go as far as `sat -9` (eterna-bleach-bypass) and `sat +8`
> (olympus-pop-art). Those only survive because the APK writes them; a user who opens the
> menu loses the extra range. Prefer staying inside ±3 for recipes a user should be able
> to reproduce; if you go beyond, say so in `note`.

---

## 4. Two paths to a new recipe

### Path A — transcribe an upstream recipe you already have

Use this when the look already exists upstream (recipe-lab, MIT) and you are faithfully
recording it.

1. Take the exact parameter block from the upstream `Recipes.java` (or the source you
   trust). Do **not** round, "tidy", or re-tune anything — transcription drift is the
   failure mode this whole repo exists to prevent.
2. Set `"source": "recipe-lab"`, `"verified": true`, and keep `engine: "recipe-lab"`.
3. Run the fidelity gate to prove you did not shift a value:
   ```bash
   curl -sSLf -o build/upstream-Recipes.java \
     https://raw.githubusercontent.com/voxivoid/recipe-lab-sony-pmca/6b5c8aa2900019d98496c7047a90ce73d2d6a725/src/com/voxivoid/recipelab/Recipes.java
   python tools/check_fidelity.py --upstream build/upstream-Recipes.java
   ```
   Fetch the pinned SHA (`sources.recipe-lab.fetched_rev` in `catalog/filters.json`), not a
   branch. A branch moves, and comparing against a moving target reports upstream's own
   edits as your drift. `-f` matters too: without it a 404 is written into the file and the
   next command fails on a parse error that names nothing useful.
   It compares **semantically** (constructor defaults expanded). Any real value drift
   prints as `MISSING` and fails. Your new recipe will appear under `ADDED` as expected —
   that is fine. The engine counts 77 upstream recipes as load-bearing; do not change that
   count unless you genuinely added or removed an upstream transcription.
4. No `note` and no `tests/cases.json` entry is required for `source: recipe-lab` — the
   fidelity check *is* its specification.

### Path B — author a recipe yourself

Use this when the look does not exist upstream and you are building it from a target
"taste".

1. Start from the target, not from numbers. Pick the visual band in
   `docs/MAPPING-RECIPES.md` §1.2, then use the §2.1 "visual goal → parameter" table to
   derive the field values. Example: "clean teal, phone-app style" → §2.1 says there is
   no true split-tone on this camera, only global `ab`/`gm`; so `NEUTRAL, sat -3, ab -2,
   gm 1` (this is exactly `teal-mood`).
2. Remember the hard engine rule: **when `pe ≠ 0`, the camera ignores `style` and the
   `sat`/`con`/`sharp`/`matrix` sliders entirely.** So for any `pe` recipe, set those to
   `0` and let `pe` + `sub` do the work. Pinning them to `0` also stops a later contributor
   from "helpfully" re-tuning values the camera cannot even see.
3. You **must** set three fields honestly:
   - `"source": "authored-here"`
   - `"verified": false` (nothing self-authored has been on a camera yet)
   - `"note"`: a plain-language sentence on what it approximates and that it is unverified,
     e.g. *"Authored here. Phone-app teal look; no true split-tone on this camera, so this
     is a clean global teal via ab/gm. Not verified on hardware."*
4. You **must** also write a pinned test case (see §6). `TestAuthoredHaveCases` fails the
   suite otherwise, and CI goes red.

> **Honest note.** Path B recipes ship marked `NOT VERIFIED ON HARDWARE` in the generated
> Java. A green CI means the file is consistent, not that the colour is right. On-camera
> validation (§8 of `INSTALL.md`) is still required before you flip `verified` to `true`.

---

## 5. Registering the recipe, step by step

Edit `catalog/filters.json`. The `"filters"` array is the list; insert your object inside
the block of its `group`.

1. **Order matters — keep each group contiguous.** The generator emits one Java array run
   per group and relies on all of a group's recipe-lab entries sitting together. Insert
   your entry *within* the existing run of its group; never split a group into two runs.
   (film-studio-matrix entries may interleave freely — they are not compiled — but
   recipe-lab must stay contiguous.) If you break contiguity, `gen_recipes.py` aborts with
   a clear error before anything builds.
2. **Naming.**
   - `id`: lowercase kebab-case, self-explanatory, unique across the whole catalog
     (e.g. `teal-mood`, `toy-camera-warm`). Avoid colliding with an existing `id`.
   - `name`: the string shown in the app. Must be **globally unique among recipe-lab
     entries** (the generator writes `name`, not `id`, into Java). If two recipe-lab
     recipes share a `name`, the app list cannot tell them apart and a test fails.
   - Optional `name_zh`: a human-readable Chinese name.
   - `group`: must be one of the declared group ids in `groups[]` (see the current 13:
     sony, fuji-sim, fuji-film, kodak, cine, ricoh-gr, leica, hasselblad, canon-nikon,
     pana-olympus, other-stocks, ilford, app-look).
3. **Full field shape** (recipe-lab):
   ```json
   { "id": "teal-mood", "name": "Teal Mood", "name_zh": "青调", "group": "app-look",
     "engine": "recipe-lab", "source": "authored-here", "tone": "color",
     "verified": false,
     "note": "Authored here. Phone-app teal look; no true split-tone on this camera, so this is a clean global teal via ab/gm. Not verified on hardware.",
     "recipe": { "style": "NEUTRAL", "sat": -3, "con": 0, "sharp": 0, "matrix": 0,
                 "wb": { "mode": "AUTO", "kelvin": 0, "ab": -2, "gm": 1 },
                 "pe": 0, "sub": 0, "ev": 0, "dro": 6 } }
   ```
4. **Adding a brand-new group** takes three synchronized edits — miss one and CI fails:
   - `catalog/filters.json` `groups[]`: add `{ "id": "<kebab>", "label": "<Display>" }`.
   - `tools/gen_recipes.py` `GROUP_JAVA`: add the mapping `"<kebab>": "<JAVACONST>"`
     (the generator aborts if a group has no Java constant).
   - `README.md` **and** `README.zh-CN.md` group tables: add the same row to both —
     the two READMEs carry the same table, and `tools/check_readme_counts.py` reads the
     English one.
   `validate_catalog.py` reads groups from `groups[]`, so you do **not** need to touch the
   validator. (You are asked not to edit `tools/` or `README.md` in this docs task — if
   your addition needs a new group, open an issue and let the maintainers make those two
   edits; you only add the `groups[]` row here.)

> **Honest note.** `film-studio` (PolyForm Noncommercial) entries must **never** carry a
> `recipe` object. Register the name only. If you attach parameters to a `film-studio`
> entry, the validator errors out immediately — that boundary is legal, not stylistic.

---

## 6. Writing the pinned test case

`tests/cases.json` is the specification for recipes this repo authors itself. Upstream
recipes are locked by `check_fidelity.py`; ours have no upstream, so this file *is* the
contract. The rule `TestAuthoredHaveCases` enforces: **an entry with
`"source": "authored-here"` and no matching case fails the suite**, and a case pointing at
anything that is not `authored-here` is dead weight and also fails.

A case is a full, exact copy of the catalog entry's identifying fields and recipe:

```json
{
  "id": "teal-mood",
  "why": "A clean global teal. Deliberately not a split-tone: there is no tone curve on this camera, only global ab/gm, so the note says so. sat -3 stays inside the body's +/-3 slider, unlike several upstream recipes that exceed it and can only be written by the APK.",
  "fields": {
    "name": "Teal Mood",
    "group": "app-look",
    "engine": "recipe-lab",
    "source": "authored-here",
    "tone": "color",
    "verified": false
  },
  "recipe": {
    "style": "NEUTRAL",
    "sat": -3,
    "con": 0,
    "sharp": 0,
    "matrix": 0,
    "wb": { "mode": "AUTO", "kelvin": 0, "ab": -2, "gm": 1 },
    "pe": 0,
    "sub": 0,
    "ev": 0,
    "dro": 6
  }
}
```

Rules for the case:

- `id` must equal the catalog `id`.
- `recipe` must list **all ten** keys (`style sat con sharp matrix wb pe sub ev dro`) and
  their `wb` object — `test_case_recipes_are_complete` rejects a partial recipe, because a
  partial one would let the rest drift silently.
- `fields` should list every non-default identifying field you want nailed (`name group
  engine source tone verified`, plus `cross_ref` if present).
- Change the case and the catalog **together, on purpose.** `test_every_case_matches_the_catalog`
  fails if they disagree.

Copy `gr-moriyama`, `kodak-vision2-500t`, `toy-camera-warm`, `toy-camera-cool`,
`part-color-red`, `posterization-color`, or `teal-mood` from the existing file as templates.

---

## 7. Local validation — the nine gates

Run the pre-push script. It runs all nine gates and reports every failure together —
it does not stop at the first one, so one broken gate never hides another:

```bash
python tests/run_all.py
```

| Gate | Command | What it blocks |
|---|---|---|
| validate | `tools/validate_catalog.py` | Structural errors (bad enum, out-of-range value, broken `cross_ref`, non-contiguous group) and provenance errors (a `film-studio` entry carrying `recipe`, or the matrix engine mislabeled MIT). `sat` past the menu ±3 and "`pe` ignores Creative Style" print as **notes**, not errors — those are by-design. |
| test cases | `tests/test_catalog.py` | Invariants for every filter, plus pinned values. `TestAuthoredHaveCases` fails any `authored-here` entry with no case, and any case not pointing at an `authored-here` entry. |
| UI theme | `tests/test_ui_theme.py` | The frosted two-bar main screen keeps every view id `MainActivity` binds with `findViewById`, every drawable and string the layout references resolves, and every colour is `#AARRGGBB`. A wrong visibility value stops aapt from inflating the layout, so the app dies on launch. Runs anywhere — never skipped. |
| generated Java | `tools/gen_recipes.py --check --fork` | The on-disk `Recipes.java` differs from what the catalog would generate. **Skipped** if `build/recipe-lab-sony-pmca` is not checked out (so is the fidelity check). |
| browser | `tools/gen_browser.py` + `tests/smoke_browser.js` | `catalog/index.html` is stale or fails to render. **Skipped** if `node` is not on PATH. |
| README counts | `tools/check_readme_counts.py` | The numbers in `README.md` no longer match the catalog. |
| assets | `tools/check_assets.py` | A document pointing at an image that does not exist, a third-party hotlink (status badges excepted), a `docs/assets/samples/` file not named `<recipe-id>--off.jpg` / `--on.jpg` with an id that is in the catalog, or an icon set missing a density. |
| bilingual docs | `tools/check_docs.py` | An English document with no `.zh-CN.md` twin and no declaration saying why, a twin whose English original is gone, translated text baked into a shared `docs/assets/*.svg`, or a count drawn inside a diagram that the catalog has outgrown. |
| self-test | `tests/test_gates.py` | A gate that no longer fails on broken input. It feeds each gate something it must reject and asserts a non-zero exit — run last, because it is the only gate that temporarily writes probe files. |

The generated-Java and browser gates skip (loudly) when their prerequisite is missing; a
missing tool is not a broken catalog. All nine passing is the bar before you push.

If the generated-Java gate is skipped for lack of a fork but you still want the fidelity proof
for a Path A recipe, run `check_fidelity.py` manually as shown in §4.

---

## 8. Commit and release

- **One recipe per PR**, or one coherent same-brand set. Do not mix unrelated parameter
  changes into one commit — the fidelity gate names every drifted value, and mixing makes
  them hard to locate.
- **Commit message convention:**
  ```
  feat(recipes): add Teal Mood

  Closes #NN
  ```
  Use `feat(recipes):` for additions. Reference the issue that established the empty band.
- **Tag → CI builds the APK.** Pushing a tag triggers the release workflow, which clones
  upstream at the pinned commit, regenerates `Recipes.java`, builds the APK, and attaches
  it to the GitHub Release. The pinned upstream SHA lives in both
  `catalog/filters.json` (`sources.recipe-lab.fetched_rev`) and
  `.github/workflows/release.yml` (`UPSTREAM_SHA`); `TestPinnedUpstream` fails if they
  drift. You normally do not edit `.github/` — if the pin must move, coordinate with the
  maintainer.
- **On-camera verification is still on you.** CI green proves the file is consistent, not
  that the colour is correct. Install via the USB / Sony-PMCA-RE channel (`INSTALL.md`),
  store the recipe, power-cycle the camera (a recipe that vanishes after reboot was never
  written), shoot JPEGs on disposable subjects, then flip `verified` to `true` and record
  the model + firmware in `note`.

---

## 9. The "cannot do" list — read before claiming a recipe

This camera's settings store has no field for any of the following, and it has no Picture
Profile / LUT channel. `docs/MAPPING-RECIPES.md` §2.2 has the full 13-item list. The ones
people most often try to fake — and must not:

- **Real colour grain** — only `pe=7` rough-mono gives grain, and it is B&W only. Do not
  ship a "grainy colour" recipe; high-ISO noise is not grain texture.
- **Light leak / vignette** — no overlay layer exists. The only approximation is
  `pe=1` toy-camera, which carries a built-in vignette + tint. Label it as an approximation,
  never as "light leak".
- **Tone curve / S-curve / Log** — a6000 stores no curve. No route.
- **True split-toning (teal/orange)** — only global `ab`/`gm` exist; you cannot put teal in
  shadows and orange in highlights. A global teal (like `teal-mood`) is honest; a claimed
  split-tone is not.
- **HSL per-hue, LUT, local/gradient, clarity, double exposure, chromatic aberration** —
  none are representable.

> **Honest note.** If your target look depends on any item above, say so in `note` and
> describe only the approximation the camera can actually store. Shipping a recipe that
> claims effects the hardware cannot produce is the one thing this repository will not do.

See `docs/MAPPING-RECIPES.md` for the authoritative mapping and the full constraint list.
