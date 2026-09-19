# Brand packs — one small app per camera brand

<p align="center"><b>English</b> · <a href="BRAND-PACKS.zh-CN.md">简体中文</a></p>

> **Honest note up front.** A brand pack is *still the same app with the same recipes* —
> it is just built once per brand with its own launcher icon and its own Android package
> name, so you can install only the brand you actually use. The all-in-one app is **not
> going away**; it stays brand-neutral and remains the default download. Read
> [§3](#3-the-shared-settings-caveat--one-camera-one-active-recipe) before you install
> three packs expecting three cameras — you will not get them.

This document explains what a brand pack is, why it has to be built the way it is, what
it can and cannot contain, how the transform works, how the icons are sourced, the
trademark reality, and how to build or add one. If you only want to install one, see
[docs/INSTALL.md](INSTALL.md).

---

## 1. What a brand pack is — and what it explicitly is not

A brand pack is the **same upstream checkout** and the **same `catalog/filters.json`**,
built once per camera brand, each with a distinct Android package name so several packs
can sit side by side on the camera. Nothing is forked. The entire difference between the
all-in-one app and a single brand pack is three things:

1. the Android **package name** — `com.hairuoliu.sonysoocrecipes` becomes
   `com.hairuoliu.sonysoocrecipes.<id>`;
2. the **`app_name`** string (e.g. `Leica Looks`);
3. the **launcher icon** — each pack shows that brand's most famous camera.

`tools/apply_pack.py` performs the transform on a fresh, already-rebranded checkout;
`tools/gen_recipes.py --pack <id>` then emits only that pack's groups into `Recipes.java`.
Everything else — the engine, the native library, the settings-store map — is
byte-identical to the all-in-one app.

**It is explicitly not a fork.** There is no separate branch, no second catalog, no
per-brand copy of the recipes. The packs are *views* over one codebase and one catalog.
That is the whole point: there is exactly one source of truth, and a pack is just a
narrower build of it. If you ever find yourself editing pack-specific code, you have
misunderstood the design — change `catalog/filters.json`, not a pack.

---

## 2. Why the package name must differ (side-by-side install)

Android identifies an installed app by its **package name**, not by its icon or its
display name. Two APKs that share a package name cannot coexist: installing the second
is treated by the system as an **update of the first**, and it silently replaces it. The
all-in-one app already occupies `com.hairuoliu.sonysoocrecipes`, so a Leica pack built
with that same name would overwrite it, and a Fujifilm pack built with it would overwrite
the Leica one in turn. You would end up with one app — whichever installed last.

The per-brand suffix (`...sonysoocrecipes.leica`, `...sonysoocrecipes.fujifilm`, …) is what
makes "install only the brand you want" mean anything. With distinct package names, the
camera treats each pack as a separate app, and you can have the Leica, Kodak and Ricoh
packs installed at once, each with its own icon, none clobbering the others. Without it,
the entire brand-pack idea collapses into a single installed app — which is exactly the
"155 recipes, tedious to scroll through" situation the packs were meant to escape.

---

## 3. The shared-settings caveat — one camera, one active recipe

**This is the thing users get wrong, so it comes early.**

The camera's **settings store is shared between packs.** Each pack keeps its *own
snapshot* of that store — `getFilesDir()` is per-package, so one pack's snapshot file does
not overwrite another's — but the store itself is one physical thing in the camera. Only
**one recipe can be active on the camera at a time.**

Consequences, stated plainly:

- Installing three packs does **not** give you three cameras. It gives you three launchers
  that all write the *same* settings store.
- Switching packs does **not** switch recipes. Opening the Ricoh pack and picking a look,
  then opening the Leica pack, shows you the Ricoh look is still on the camera — because
  the Leica pack reads and writes the same store.
- A pack is a *convenience for browsing*, not a *sandbox for recipes*. It narrows the list
  you scroll through; it does not isolate the result.

The pack choice is about **which icon you tap and which subset of recipes you scroll**, not
about having several independent cameras. If you want Leica in the morning and Kodak in the
afternoon, you install both, but you still switch the active recipe the usual way — by
opening a pack, picking a look, and power-cycling. The release notes say the same thing,
because this is the single most common point of confusion.

---

## 4. The pack table

Nine packs today, built from the catalog. The *compiled recipe count* is the number
actually emitted into `Recipes.java` for that pack — after dropping entries that belong to
the other engine (`film-studio-matrix`, reference-only) and entries that are reference-only
for another brand. It is **not** the same as the group's total entry count, and a smaller
number is not a bug (see the notes below the table).

| `id` | `app_name` | Source groups | Compiled recipes |
|---|---|---|---|
| `leica` | Leica Looks | `leica` | 20 |
| `fujifilm` | Fujifilm Looks | `fuji-sim` | 16 |
| `filmstocks` | Fuji Film Looks | `fuji-film` | 10 |
| `ricoh` | Ricoh GR Looks | `ricoh-gr` | 11 |
| `kodak` | Kodak Looks | `kodak` | 20 |
| `pentax` | Pentax Looks | `pentax` | 11 |
| `ilford` | Cinestill + Ilford Looks | `ilford`, `cine` | 9 |
| `hasselblad` | Hasselblad Looks | `hasselblad` | 4 |
| `sony` | Sony Looks | `sony` | 8 |

Three counts are smaller than — or add up differently from — their group sizes, and that is expected:

- **`fujifilm`** lists 26 entries in `fuji-sim`, but only **16** are compilable; the other 10
  belong to `fuji-film`, which is now the separate `filmstocks` pack. So this pack holds 16.
- **`ricoh`** lists 16 entries in `ricoh-gr`, of which **11** are compilable (the other 5
  are `film-studio-matrix` reference-only).
- **`ilford`** now spans two groups: **5** from `ilford` plus **4** from `cine` (a
  motion-picture look family, not an Ilford product), for 9 in the pack.

So if a pack's number looks low, check whether its group mixes in the other engine before
assuming something was dropped. `tools/gen_recipes.py --pack <id>` prints the emitted
group(s) and warns when a requested group contributed nothing compilable.

---

## 5. What a pack can and cannot contain

A pack is a single-brand slice of the catalog. The defining rule: **a pack's groups must
all belong to one brand**, because the pack's icon and its `app_name` (`<Brand> Looks`)
advertise exactly one brand. A pack that mixed Leica and Kodak recipes under a "Leica
Looks" name would be lying about what it contains.

**Groups deliberately in no pack.** These stay reachable in the all-in-one app, which is
still built and still published. `catalog/packs.json` records them in `unassigned_groups`
with reasons rather than omitting them, so the gap is visible in the data instead of in a
bug report:

| Group | Why it is not a pack (yet) |
|---|---|
| `canon-nikon` | Spans two brands — it has to be split into one pack per brand first |
| `pana-olympus` | Spans two brands — same split required |
| `other-stocks` | Mixed heritage stocks (Agfa, Polaroid, Ferrania …) with no single brand |
| `app-look` | Not a camera brand — social / app filter looks |

`canon-nikon` and `pana-olympus` are the only ones with a clear path to becoming packs:
split each into `canon` and `nikon` (or `panasonic` and `olympus`) groups, then each gets
its own pack entry. The other two are category groups, not brands, and are unlikely ever
to be packs.

A pack also cannot contain `film-studio-matrix` entries — those are reference-only and
compile nowhere, so they simply do not appear in the emitted `Recipes.java`.

---

## 6. How the transform works

`tools/apply_pack.py --pack <id>` rewrites the package name and the app name inside a
fresh checkout and moves the source tree. It is **destructive and in place**, which is why
`tools/build_apk.sh` gives each pack its own checkout directory. The interesting part is
*how* the rename is written, because four easy-to-miss traps sit in it.

### 6.1 The four separator forms

The package string appears in the upstream tree in four spellings, and the rename must
catch every one or the build breaks:

| Form | Example | Where it appears |
|---|---|---|
| dotted | `com.hairuoliu.sonysoocrecipes` | `AndroidManifest.xml`, every Java `package` line, JNI exception lookup, custom-view class names in `res/layout` |
| slashed | `com/hairuoliu/sonysoocrecipes` | `build.sh`, `check-version.sh`, a directory path inside `jni.cpp` |
| backslash | `com\hairuoliu\sonysoocrecipes` | `build.cmd` |
| underscore | `com_hairuoliu_sonysoocrecipes` | the JNI export symbols (`Java_com_a_b_…_NativeBackup_read`) |

Miss the slashed form and `javac`/`aapt` die; miss the underscore form and the app crashes
on launch when the native layer cannot find its exception class. `apply_pack.py` rewrites
all four from one set of patterns rather than four hand-written `sed` calls, precisely so
none is forgotten.

### 6.2 The native library name trap

This is the trap that looks like a rename but is not. The bare token `sonysoocrecipes` is
**also the native library name**: `LOCAL_MODULE` in `jni/Android.mk`,
`System.loadLibrary` in `NativeBackup.java`, and `libsonysoocrecipes.so` in both build
scripts. A naive rename that rewrites the *bare token* would turn the library into
`libsonysoocrecipes.leica.so` — and **a dot is not legal in a loadable library name**, so
the app would die with `UnsatisfiedLinkError` on launch.

That is why every one of the four patterns is anchored on the **full package**
(`com.hairuoliu.sonysoocrecipes`), never on the trailing `sonysoocrecipes` alone. The
library name is left untouched on purpose. `apply_pack.py --check` fails hard if it finds
`.leica.so` (or any `.<id>.so`) in `jni/Android.mk` or `build.sh`.

### 6.3 Sub-package nesting

Because a pack package is the base package plus one segment, the *destination* source
directory is physically **inside** the source directory:

```
src/com/hairuoliu/sonysoocrecipes/        (base)
        └── leica/                        (pack — nested inside the base)
```

A plain move of `…/sonysoocrecipes` to `…/sonysoocrecipes/leica` refuses (you cannot move a
directory into its own child). `apply_pack.py` routes through a sibling temp name
(`…/sonysoocrecipes__pack_tmp`) and then moves it into place. The move is also guarded: a
second run only moves when Java sources are still sitting directly in the base directory,
so re-running after a partial failure resumes instead of nesting one level deeper.

### 6.4 Idempotency and `--check`

The transform is **idempotent by construction**. Each pattern is anchored on the full
package and refuses to fire when another pack segment already follows, so running it twice
cannot produce `…sonysoocrecipes.leica.leica`, and re-running after a partial failure
finishes the job instead of corrupting or double-appending.

`apply_pack.py --check` verifies a checkout is *already* this pack and self-consistent —
it asks "would running the transform change anything?" (not "does the base package appear
anywhere?"), and confirms the manifest declares the pack package, the source tree moved,
and the library name survived untouched. Use it in CI and after any manual edit to a
checkout. `--dry-run` reports every change without writing.

---

## 7. Icons — where they come from, how they are generated, and the attribution obligation

Each pack's launcher icon is built from a photograph of that brand's best-known camera — or,
for `filmstocks`, `kodak` and `ilford`, from a film canister rather than a camera (those three
packs are named after film stock, not a body). Two packs (`ricoh`, `pentax`) still use a
**freely-licensed photograph on Wikimedia Commons**; the other seven (`leica`, `fujifilm`,
`filmstocks`, `kodak`, `ilford`, `hasselblad`, `sony`) use **all-rights-reserved commercial
photographs supplied by the user**, with no licence granted. The attributions and the relaxed
licence rule are recorded in
`assets/app-icon-packs/CREDITS.md`, and — because the icon ships inside the APK — the
attribution must **travel with the APK**: it goes in `NOTICE.md` and in the per-pack
release notes.

The icon sets are generated by `tools/build_pack_icons.py` (the per-pack counterpart of
`tools/build_app_icon.py`, which builds the all-in-one set). Each set is five files at
fixed pixel sizes:

| File | Density | Size |
|---|---|---|
| `ic_launcher-mdpi.png` | mdpi | 48 |
| `ic_launcher-hdpi.png` | hdpi | 72 |
| `ic_launcher-xhdpi.png` | xhdpi | 96 |
| `ic_launcher-xxhdpi.png` | xxhdpi | 144 |
| `icon-512.png` | store listing | 512 |

**Be honest about the keying.** The all-in-one icon, built by `tools/build_app_icon.py`,
is **keyed out of its plain-white background** (a transparent RGBA drawable). As of this
release the pack icons are **also** keyed — each is a transparent silhouette cut from its
source photograph, matching the all-in-one's style rather than keeping the rectangular photo.
Do not describe the pack icons as rectangular photographic tiles; they are not.

**The attribution obligation is real — but it now applies to only two of the nine packs.**
Seven packs (`leica`, `fujifilm`, `filmstocks`, `kodak`, `ilford`, `hasselblad`, `sony`) use
all-rights-reserved commercial photographs supplied by the user; no licence was granted, so
there is no attribution obligation — only the publisher's risk of distributing them. The
other two packs keep their original Wikimedia Commons photographs and still require a credit:

- **Ricoh** — Ricoh GR (2013), CC BY 2.0 (author: Kārlis Dambrāns)
- **Pentax** — Pentax K1000, CC BY 2.0 (author: Terry Presley)

`CC BY` permits commercial use **only with attribution**, so the credit must ride along in
`NOTICE.md` and the per-pack release notes. `CC BY-SA` is deliberately **excluded** from
the pack icons: its share-alike term would reach the whole app, not just the icon. The
default all-in-one icon needs no such attribution because it is original artwork in this
repo.

---

## 8. Naming and trademark — the honest statement

The `app_name` uses a **`<Brand> Looks`** form rather than a bare brand name or a camera
model number. The reason is narrow and practical: naming a distributed app after a
trademark *implies endorsement*, and endorsement is the risk that actually gets a project
taken down. "Leica Looks" describes what the app does with Leica's style; "Leica" alone
would suggest Leica made or blessed it.

**State this plainly: the `<Brand> Looks` form is risk reduction, not a clearance.** Using
a brand name in an app's name is still trademark use. Nominative or descriptive use —
truthfully saying what the app is *for* — is a *defence* in some jurisdictions, not a
*permission*, and app stores are stricter than courts. The all-in-one app stays
brand-neutral (`Sony SOOC Recipes`) and remains the default download precisely so the
project's main distribution carries no single brand's name.

Anyone who **redistributes** these packs — republishing the APKs, or shipping them inside
another product — takes on that trademark risk themselves. This document does not make that
risk go away; it only makes it visible.

---

## 9. Building a pack

You rarely have to. CI builds every pack on a `v*` tag (see below). But locally:

```bash
tools/build_apk.sh --pack leica        # build one brand pack, in its own checkout
tools/build_apk.sh --all-packs         # the all-in-one app + every pack from packs.json
```

`--pack <id>` gives the pack its own checkout (`build/recipe-lab-sony-pmca-<id>`) so the
in-place transform cannot clobber the all-in-one. `--all-packs` builds the all-in-one
first, then every pack read from `catalog/packs.json` (not hardcoded).

### How CI does it

`.github/workflows/release.yml` builds the APKs on a `v*` tag. The build matrix is
**derived at run time from `catalog/packs.json`** by a `targets` job: it emits one entry
for the all-in-one plus one per pack. A second `apk` job then runs **one job per matrix
entry**, each on an independent runner, each cloning upstream fresh at the pinned revision
and applying that pack's transform. Two properties follow:

- **Failure isolation.** `fail-fast: false` means a broken pack fails on its own; it does
  not block the other packs or the all-in-one.
- **No YAML drift.** The pack list lives only in `catalog/packs.json`. Adding a pack there
  is picked up by the next tag with **no edit to the workflow file** — the repo forbids
  copying the list into the YAML, because that copy would drift the moment someone edits
  the JSON.

Per-pack release notes (generated in the `release` job) restate the shared-settings caveat
from [§3](#3-the-shared-settings-caveat--one-camera-one-active-recipe) and list every pack
APK with its SHA-256.

---

## 10. Adding a new pack

Say you want a `contax` pack. Step by step:

1. **Edit `catalog/packs.json`.** Add an entry to `packs`:
   ```json
   { "id": "contax", "app_name": "Contax Looks", "groups": ["contax"], "icon_set": "contax" }
   ```
   Use the `<Brand> Looks` form for `app_name` (§8). The `groups` must be **one brand
   only** — if the brand's recipes currently live in a group that also spans another brand
   (like `canon-nikon`), split that group in `catalog/filters.json` first.

2. **Confirm the groups are single-brand and compilable.** Run
   `tools/gen_recipes.py --pack contax` and read its output: it prints the emitted group(s)
   and warns if a requested group contributed no compilable recipe (e.g. all
   `film-studio-matrix` entries). A pack with zero recipes is a broken pack.

3. **Generate the icon set.** Produce `assets/app-icon-packs/contax/` with the five files
   at 48 / 72 / 96 / 144 / 512 px (§7). Preferred: drop a keyed `contax.png` cut-out into
   `camera-covers/cutout/` (see `tools/cut_camera_covers.py`) — `tools/build_pack_icons.py`
   picks it up and renders a transparent silhouette. With no cut-out it falls back to the
   framed `master.jpg`. Record the source's provenance and licence in
   `assets/app-icon-packs/CREDITS.md`, `NOTICE.md` and the per-pack release notes. Do
   **not** use a `CC BY-SA` photo — the icon is an adaptation of the photograph, so
   share-alike would reach the whole app.

4. **Run the gate.** `tools/check_assets.py` now checks icon sets. A missing set directory
   is a *note* (the pack falls back to the default icon), but a set that exists with a
   missing or wrong-size file is an *error*. The gate must pass before you tag.

5. **Build locally to sanity-check.** `tools/build_apk.sh --pack contax`, then confirm the
   APK's package name with `apply_pack.py --check` if you kept the checkout.

6. **Tag to publish.** Push a `v*` tag. The `release.yml` matrix picks the new pack up
   automatically — no workflow edit needed. The per-pack release notes will name it.

That is the whole change surface: one JSON entry, an icon set, and an attribution line.
Nothing else in the codebase moves.
