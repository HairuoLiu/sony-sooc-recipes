# Changelog

**English** · [简体中文](CHANGELOG.zh-CN.md)

Each entry records one version uploaded to GitHub. Version numbers follow semantic
versioning, with one exception: a **change to a recipe's values** also counts as a minor
bump. For someone using this, a look whose parameters moved matters more than a new
function does.

`python tests/run_all.py` must pass all of its gates before a tag is pushed — the seven
catalog gates plus the self-test that proves the gates still fail on broken input.

> `v0.5.0` was this repository's **first published release**. The development batches that
> came before it have no Release and therefore no version number; they are listed below as
> "development batch", with their content and licensing decisions kept verbatim so the
> reasoning stays traceable.

---

## v0.7.0 — 2026-09-19 · brand-pack restructure, and all-new icon artwork

- **A ninth brand pack: `filmstocks` (Fuji Film Style).** The Fujifilm pack split in two.
  `fujifilm` now carries only the camera *simulations* — 16 compiled recipes from the
  `fuji-sim` group — and the Fujifilm film *stocks* (10 compiled recipes from the `fuji-film`
  group) moved to the new `filmstocks` pack. The release now ships **ten** APKs: the
  all-in-one plus nine single-brand packs, up from v0.6.0's nine.
- **`ilford` replaced by `nichefilm` (Niche Film Style).** The old `ilford` pack ("Cinestill +
  Ilford Looks", groups `ilford` + `cine`, 9 recipes) was renamed to `nichefilm` and absorbed
  `other-stocks` (17 compiled heritage recipes — Agfa, Polaroid, Ferrania and others), giving
  **26** recipes across `ilford`, `cine` and `other-stocks`. Reason: the pack's icon is a
  CineStill film product shot, which never matched a "Cinestill + Ilford" name; gathering the
  niche / heritage film stocks into one pack fixes that mismatch and gives `other-stocks` a
  home (it previously shipped only inside the all-in-one). The `cine` group is a
  motion-picture look family, not an Ilford product, and `other-stocks` is a mixed bag of
  heritage brands with no single brand behind it.
- **All pack app names changed from "<X> Looks" to "<X> Style".** All nine packs, uniformly,
  so the names read as stylistic rather than as an endorsement.
- **New launcher icons on a dark rounded tile.** Every pack icon is a silhouette of its
  camera or film stock, keyed from its source and composited onto a solid near-black rounded
  tile (RGB 28,28,30 ≈ #1C1C1E) so dark subjects stay legible on dark wallpapers. The
  previous transparent-only silhouette remains available with `--no-bg`.
- **All nine pack icons use user-supplied commercial material.** `leica`, `fujifilm`,
  `filmstocks`, `kodak`, `nichefilm`, `hasselblad`, `sony`, `ricoh` and `pentax` now use
  all-rights-reserved commercial photographs / official manufacturer renders supplied by the
  user, with no licence granted. The publishing party carries the risk; see
  `assets/app-icon-packs/CREDITS.md` for the honest provenance and the relaxed licence rule.
  `ricoh` and `pentax` were the last two Wikimedia Commons **CC BY 2.0** photographs, so no
  free-licensed image ships in any APK and there is no attribution obligation left — their
  former credit lines were removed rather than left behind for photographs that are no longer
  distributed.
- **Six of the nine icons depict film, not a camera body.** `filmstocks`, `kodak`,
  `nichefilm`, `pentax`, `ricoh` and `sony` show film stock; only `leica` (M9), `fujifilm`
  (X100VI) and `hasselblad` (X2D II 100C) show a camera body. The `nichefilm` icon is the
  CineStill film product shot that gave the restructure its name.
- **Deferred to the next release.** The frosted two-bar main-screen UI theme — a replayed
  patch over the upstream layout — is not part of this build; it lands in a later version.

---

## v0.6.0 — 2026-09-13 · Brand packs: one APK per brand

The same code and the same `catalog/filters.json`, packaged into **8 separate APKs** by
camera brand and published alongside the all-in-one app (9 build targets). Each pack's
Android package name carries one extra segment (`...sonysoocrecipes.<id>`), so several packs
can **coexist** on the camera; each pack's launcher icon is that brand's best-known camera.

### Why

155 looks can only be stepped through on the camera by pressing a button, one at a time, and
that gets tiring. Split by brand, you install only the part you want and step through an
order of magnitude less. **What is split is the browsing entry point, not the data**: there
is still one catalog and one recipe engine. `tools/gen_recipes.py --pack` merely emits one
pack's groups.

### Packs and recipe counts

leica 20 · fujifilm 26 · ricoh 11 · kodak 20 · pentax 11 · ilford 5 · hasselblad 4 · sony 8

`canon-nikon` and `pana-olympus` each span two brands (each would first have to be split
into one pack per brand), while `other-stocks`, `cine` and `app-look` are not single-brand.
Those five groups go into **the all-in-one app only**; they are recorded in `packs.json`
under `unassigned_groups`, so the gap is visible rather than silently dropped.

### What you need to know

- **Installing several packs does not give you several cameras.** The camera's settings
  store is shared and only one recipe can be active at a time. Each pack's snapshot is
  isolated by package name and they do not overwrite each other — but they do not stack
  either.
- **A pack is not much smaller than the all-in-one.** Recipe data is the smallest thing in
  the APK (all 155 looks ≈ 21.6 KB, the APK ≈ 102 KB); the engine dominates. The point of a
  pack is "less to step through", not "smaller download".
- **The signing key is still single-use**, with the same caveat as v0.5.0.

### Implementation

- `catalog/packs.json` defines the packs; `tools/apply_pack.py` rewrites the package name,
  `app_name` and icon set in place; `tools/gen_recipes.py --pack` emits only that pack's
  groups; `tools/build_matrix.py` derives the release matrix from `packs.json`, so the
  matrix is never written into the YAML and adding a pack adds a build target automatically.
- The matrix builds packs in parallel in CI (`fail-fast: false`), but **any pack failing
  means nothing is published** — better no release than a Release missing a pack.
- Icons are **framed, not keyed out**: the subject is located from the photograph's own
  border colour, a square frame is opened to the subject's size and padded rather than
  cropped, and the rounded corners are drawn at 4× supersampling. Generator:
  `tools/build_pack_icons.py`; sources and per-image licences in
  `assets/app-icon-packs/CREDITS.md`.
- Icon licence rule: **PD / CC0 / CC BY only.** `CC BY-SA` is disqualified outright — the
  icon is an adaptation of the photograph, and share-alike would reach the whole app.
  fujifilm / hasselblad / sony are CC0 or PD (no obligation); the other five are CC BY, so
  their attribution travels with the APK.
- `tests/test_packs.py`, 31 cases. The most important one asserts that **every pack's recipe
  values are identical, value for value, to the all-in-one's** — a pack must be a subset,
  never a re-fit.

See `docs/BRAND-PACKS.md`.

## v0.5.0 — 2026-09-13 · Renamed to Sony SOOC Recipes

Renames this repository's on-camera app away from the upstream project's name:

- The in-camera display name, the APK filename and the Java package are now
  `Sony SOOC Recipes` / `SonySOOCRecipes` / `com.hairuoliu.sonysoocrecipes`.
- At build time `release.yml` renames the whole fork by sed plus `git mv`, including the JNI
  symbols `Java_com_voxivoid_recipelab_*` → `sonysoocrecipes`.
- Install docs, README, architecture docs, tooling and the generated catalog browser all use
  the new name; references to the upstream voxivoid project in prose became "the upstream
  project".
- The MIT attribution in `NOTICE.md` is kept, as are the raw URLs CI and `check_fidelity.py`
  use to fetch upstream sources.

## Development batch · Film stocks (2026-09-13, 38 added)

**38 added** (117 → 155; compilable 102 → 140), test cases 25 → 63. Groups unchanged.

Background: the user confirmed that the LUT collection in question (the camera-simulation set
and the Leica abbreviation set) is their own work under the pen name Roger Wang and may be
used freely, so the two batches skipped earlier were completed. The Dehancer film collection
was used as a reference for how each stock looks.

### 24 film stocks (after de-duplication)

Compared against the existing catalog: of Dehancer's 68 files, 30 stocks were already covered
(Portra/Gold/HP5/Velvia/Acros/Cinestill/Instax and others). The **uncovered** 24 were added:

- **Kodak +5**: Aerocolor IV 125 (aerial negative) · Eastman Double-X 5222 (cine black and
  white) · Plus-X Pan 125 · Ektar 25 (a different film from Ektar 100) · Supra 100
- **Fuji +5**: Reala 500D (motion-picture negative) · CDU-II cross-process · Fujicolor 100 ·
  industrial print 100 / 400
- **Other Stocks +14**: Adox Color Implosion · wet-plate collodion · Astrum CN 125 ·
  Konica Centuria / VX400 / Impresa · Lomochrome Metropolis / Purple · ORWO Chrom UT21 ·
  Polaroid Type 100 sepia · Prokudin-Gorsky 1906 · Rollei CN200 / Ortho 25 · Svema Type-42

### 14 Leica entries (after de-duplication)

Decoding the abbreviations: CNT/CLS/ETN = Contemporary/Classic/Eternal, which duplicate the
existing catalog and were skipped. The remaining 14 were added: B&W HC · B&W Natural ·
Greg WLM (warm black and white) · IA (hard black and white) · Blu (cool black and white) ·
Sel (pale silver) · Sepia · Bleach · Chrome · BRS (warm high contrast) · Natural ·
Silver (soft) · Teal · Vivid.

### Honest notes (written into each entry's `note`)

- **Lomochrome Purple's green→purple substitution**: the Sony settings space cannot do a
  per-hue substitution, so a magenta plus amber white-balance shift only approximates the
  character — the note says so.
- **Rollei Ortho 25's orthochromatic response** (insensitive to red) cannot be reproduced;
  only the hard, high-contrast look is kept.
- The whole batch is `authored-here` + `verified: false`, with reference measurements
  (contrast / saturation / colour cast) in the notes.

---

## Development batch · Camera simulation (2026-09-13, 18 added)

**18 "camera rendering simulation" recipes added** (99 → 117; compilable 84 → 102), plus a new
`pentax` group. All are `source: authored-here` + `verified: false`; test cases 7 → 25.

These recipes simulate **other camera bodies / in-body colour modes**: Pentax Custom Image,
Hasselblad HNCS, default Leica body rendering, and the GR line's cinematic grades.

### New group Pentax (11)

Approximations of the Pentax Custom Image catalog, parameterised from **Pentax's own public
descriptions** of each mode:

| id | Points from the official description |
|---|---|
| `pentax-bleach-bypass` | muted, high contrast, restrained colour (bleach bypass) |
| `pentax-muted` | high-key, low contrast, restrained saturation |
| `pentax-radiant` | high saturation and contrast, lifted overall, exaggerated hues |
| `pentax-reversal-film` | deep blacks; achieves reversal-film look through contrast, not saturation |
| `pentax-satobi` | 1960s–70s colour print: cyan-blue, dark yellow, faded red |
| `pentax-katen` | dense summer-sky blue with cloud detail (limited edition) |
| `pentax-kyushu` | autumnal red-toned blues and deep greens (limited edition) |
| `pentax-fuyuno` | high-key winter scene, restrained saturation (limited edition) |
| `pentax-harubeni` | cherry-blossom pink, hues shifted toward red (limited edition) |
| `pentax-gold` | richer yellow in the highlights (K-1 II limited edition) |
| `pentax-miyabi` | elegant, low contrast, colour that stays out of the way |

### Extensions to existing groups

- **Hasselblad** (1→4): HNCS LowSat · HiContrast · HiContrast LowSat
- **Leica** (4→6): M9 CCD (warm CCD rendering) · M240 STD
- **Ricoh GR** (14→16): GR Cinema Green · GR Cinema Yellow (the teal/warm-cinematic grades
  common in GR street photography)

### The licensing boundary (why these recipes are written the way they are)

The user provided a set of "camera simulation LUTs" as a reference. The Hasselblad / Leica
M9 / M240 / Pentax / Ricoh set is licensed **BY-NC-ND (no derivatives)** — converting a LUT's
values and publishing the result is a derivative work and not permitted. But **a camera mode
is a fact, not an expression**: Pentax publishes a description of how each Custom Image looks,
and these parameters were authored from those public descriptions, containing no third-party
LUT data. The 68 Dehancer film profiles and the Leica abbreviation set of unknown provenance
were not included (the former are proprietary commercial-plugin profiles and largely duplicate
the existing film groups).

### Other changes

- `tools/gen_recipes.py`: added the `pentax` constant to `GROUP_JAVA` (the generator needs a
  Java identifier per group)

---

## Development batch · Documentation (2026-09-13)

No recipe or APK behaviour changed (99 looks / 84 compilable; the APK is still the previous
one). This batch touches documentation only.

**No tag.** Pushing `v*` would make `release.yml` rebuild and publish an APK that is identical,
and running a multi-gigabyte toolchain purely for documentation is not worth it. To install
onto a camera, use the APK from the latest Release.

**The front page became English, with Chinese as a subpage**

`README.md` was rewritten as the English front page and `README.zh-CN.md` is the same content
in Chinese, each with an `English · 简体中文` switcher at the top. **The counts marker
`<!-- counts: total=99 compiled=84 -->` exists in both files** and `check_readme_counts.py`
now checks both — a translated page quietly keeping an old number is worse than no
translation at all.

**All of `docs/` gained a Chinese counterpart**

| Document | Contents |
|---|---|
| `docs/INSTALL.md` | the 5-step install flow, prerequisites per OS, a 13-row troubleshooting table |
| `docs/ARCHITECTURE.md` | data flow, how the two engines differ, the licensing boundary |
| `docs/FAQ.md` | 21 questions, safety-related ones first |
| `docs/ADDING-FILTERS.md` | full parameter table, test-case requirements, the 3 places a new group must be registered |

Each has a `.zh-CN.md` sibling.

**4 SVG diagrams**

`docs/assets/`: `parameters.svg` (what a recipe can and cannot change), `install-flow.svg`,
`architecture.svg`, `engines.svg`. All carry `@media (prefers-color-scheme: dark)` so they do
not turn into black-on-black on GitHub's dark theme.

**Gate 6 added: `tools/check_assets.py`**

Scans every `<img>` and markdown image in the docs; four classes of problem fail the build:

1. hotlinked images (images must live in `docs/assets/`, no third-party hosts) — **status
   badges are the one exception**, since they are generated per request and vendoring one
   would freeze a build status;
2. a reference to a file that does not exist;
3. a `samples/` filename violating the convention (must be `<recipe id>--off.jpg` /
   `--on.jpg`, with the id present in the catalog);
4. reported but not enforced: orphan images on disk that no document references.

**Sample images are not in place yet**

`docs/assets/samples/` is currently empty. The naming rule and how to contribute are in
`docs/assets/README.md`: same scene, same exposure, same white balance, with "recipe applied
or not" as the only variable.

---

## Development batch · First authored recipes (2026-09-13, 6 added)

**6 authored recipes added** (93 → 99; compilable 78 → 84)

| id | Group | How |
|---|---|---|
| `kodak-vision2-500t` | kodak | NEUTRAL base + K 3200 + gm+1 — greener and flatter than the existing Vision3 500T |
| `toy-camera-warm` | app-look | pe=1 Toy Camera (first use in the catalog), sub=2 warm |
| `toy-camera-cool` | app-look | pe=1, sub=1 cool |
| `part-color-red` | app-look | pe=6 Partial Colour (first use), sub=0 red |
| `posterization-color` | app-look | pe=3 Posterization (first use), sub=0 colour |
| `teal-mood` | app-look | pe=0, a clean teal cast via global ab−2 / gm+1 |

All are `source: authored-here` + `verified: false`, each with pinned values in
`tests/cases.json`.

**New group**: `app-look`.

**The APK is now built by CI and attached to a Release**

Until now this repository was "verifiable but not installable" — the gates could prove the
recipes were right but produced nothing you could put into a camera, because the toolchain
needs JDK 17 + build-tools 30.0.3 + **NDK r16b** (r16b is the last NDK that still ships the
GCC toolchain, which an Android 2.3.7 / API 10 target requires). Now a tag produces an APK:

```
https://github.com/HairuoLiu/sony-sooc-recipes/releases
```

The artifact was verified: a valid zip, `AndroidManifest.xml` as binary AXML, `classes.dex`
52 KB, `lib/armeabi/libsonysoocrecipes.so` 30 KB (armeabi being exactly the 2.3.7 ABI), and
complete v1 signing (`--min-sdk-version 10`; the camera does not accept v2/v3).

**Two traps, both written into the config files as comments**

1. `jni/platform` (ma1co/OpenMemories-Platform) is required — `Android.mk` includes its
   `vars.mk` and compiles its driver sources. But it carries a nested submodule pointing at
   `git.code.sf.net/p/stlport/code`, **which no longer resolves**, and git descends into it
   even without `--recursive` and fails the whole job. The fix is to clone `jni/platform`
   directly and pin it at the gitlink SHA upstream records. The stlport actually linked is
   **the one NDK r16b ships** (`APP_STL := stlport_static`); the submodule copy is unused.
2. The upstream commit is pinned to `6b5c8aa2`, recorded both in `filters.json`'s
   `fetched_rev` and in `release.yml`'s `UPSTREAM_SHA`. `TestPinnedUpstream` fails if the two
   drift apart.

**Tests**
- `tests/test_catalog.py`: 33 cases covering structural invariants, parameter ranges,
  provenance honesty, generator round-trip and upstream-pin consistency.
- `tests/cases.json`: pinned values for the recipes this repository authors.
  `TestAuthoredHaveCases` requires that an authored entry without a matching case fails.
- `tests/run_all.py`: every gate in one local run.
- CI gained Gate 1b.

**Fixes**
- `validate_catalog.py` no longer carries its own copy of the group list and reads `groups[]`
  instead. That copy silently rejected every new group.

**About Liit**: this began as an attempt to bring in the filters from Liit (a closed-source
commercial app by DAZZ PTE. LTD.). The conclusion was no — it is closed-source commercial
software, and its LUTs/curves have no carrying channel on an a6000 (no LUT path, no Picture
Profile, nowhere to store a curve). **Nothing was extracted and no filter name was copied.**
`NOTICE.md` records what was and was not used. This batch is original approximation within the
camera's parameter space, not a port.

---

## Development batch · Initial catalog (2026-09-13, 93 looks)

The first version.

- 93 looks gathered from two upstream projects: 77 from voxivoid/recipe-lab-sony-pmca
  (MIT, parameters transcribed in full) and 15 from ukiki0718-netizen/sony-a5100-film-studio
  (PolyForm Noncommercial, **names registered only, no parameters transcribed**, enforced by
  the validator).
- 1 authored recipe, `gr-moriyama`, filling the one genuinely complementary gap between the
  two upstreams.
- `catalog/filters.json` as the single source of truth, with `tools/gen_recipes.py`
  generating `Recipes.java` from it.
- `tools/check_fidelity.py` compares all 77 upstream recipes value for value: 0 drift.
- Five CI gates: validate → fidelity → generate → browser smoke → README counts.
- A filter browser at `catalog/index.html`, a single file openable over `file://`.
- Docs: `docs/INSTALL.md`, `ARCHITECTURE.md`, `ADDING-FILTERS.md`, `CHANNEL-COMPARISON.md`
  (a 13-dimension comparison of USB versus Wi-Fi ADB).
