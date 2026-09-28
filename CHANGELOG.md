# Changelog

**English** · [简体中文](CHANGELOG.zh-CN.md)

Each entry records one version uploaded to GitHub. Version numbers follow semantic
versioning, with one exception: a **change to a recipe's values** also counts as a minor
bump. For someone using this, a look whose parameters moved matters more than a new
function does.

`python tests/run_all.py` must pass all of its gates before a tag is pushed — including the
self-test that proves the gates still fail on broken input.

> **History was reset at 1.0.0.** The pre-1.0 `v0.x` tags were a long run of iterating
> toward the first release, and their history carried more noise than signal. This log
> begins at 1.0.0 with the project's whole prior state folded into one entry.

---

## 1.0.0 — first release

The first tagged release: the whole catalog, the bilingual UI, and the brand-pack split,
all in one place.

- **164 film looks, 149 compiled.** The catalog spans 15 brand groups across two engines —
  the settings-store engine (`recipe-lab`, 149 looks) and the matrix engine
  (`film-studio-matrix`, 15 reference-only entries recorded by name). Every recipe value is
  generated into `Recipes.java` from `catalog/filters.json`, never hand-edited.
- **Bilingual follows the camera.** Put the body into 简体中文 and every recipe name, group
  and on-screen label switches to Chinese — the same APK, no separate download. An English
  body stays English.
- **One APK, or one per brand.** The all-in-one carries everything; seven brand packs
  (`fujifilm`, `filmstocks`, `kodak`, `pentax`, `nichefilm`, `sony`, `cinema`) ship the same
  code with one brand's looks inside. Four more (`leica`, `ricoh`, `hasselblad`,
  `monochrome`) are held back with `publish: false` and ship separately.
- **Confirmed on a real body: the α7S II.** Installs, launches, and runs several packs side
  by side — photographed, not mocked. The rest of the supported model list is platform
  support, not a per-body test claim.
- **A single slim bar, three fields, hugging the text.** The main screen is one frosted pill
  reading `name · brand · position`, with a vertical settings editor whose keys follow the
  list (↑ ↓ walk, ← → and the wheel/dial change the value), and the whole UI bundled in a
  font the camera can render.
- **No unverified claim disguised.** The `verified` field in `catalog/filters.json` records,
  per recipe, whether it was written here and not yet confirmed on hardware — 72 of 164
  today — and the README says so rather than hiding it.
