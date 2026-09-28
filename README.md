<h1 align="center">sony-sooc-recipes</h1>

<p align="center">
  <b>Turn a Sony camera Sony stopped updating into the cameras you wish it were — Leica, Hasselblad, Fujifilm, Ricoh, Pentax and more — with 164 film and camera looks, straight out of camera.</b>
  <br>
  <sub>164 looks · 149 installable · 15 groups — film stocks &amp; other cameras' colour, straight-out-of-camera JPEG</sub>
</p>

<!-- counts: total=164 compiled=149 -->
<!-- The line above is checked against catalog/filters.json by CI. Change the catalog,
     change this line — a mismatch fails the build. Do not reword it. -->

<p align="center">
  <b>English</b> · <a href="README.zh-CN.md">简体中文</a>
</p>

<p align="center">
  <a href="https://github.com/HairuoLiu/sony-sooc-recipes/actions/workflows/ci.yml"><img src="https://github.com/HairuoLiu/sony-sooc-recipes/actions/workflows/ci.yml/badge.svg" alt="catalog gates"></a>
  <a href="https://github.com/HairuoLiu/sony-sooc-recipes/releases/latest"><img src="https://img.shields.io/badge/download-Windows%20installer-2f81f7" alt="download the Windows installer"></a>
  <img src="https://img.shields.io/badge/license-MIT-3fb950" alt="MIT licence">
</p>

<p align="center">
  <img src="docs/assets/hardware/01-a7sii-application-list.jpg" width="300" alt="The camera's Application List: every brand Style pack installed side by side — Hasselblad Style, Ricoh GR Style, Kodak Style, Leica Style, Niche Film Style, Pentax Style and more">
  <img src="docs/assets/hardware/03-a7sii-main-screen-cinestill-50d.jpg" width="300" alt="The screen you land on inside one pack — Cinestill 50D (Blue Velvet) selected on the frosted main screen">
  <br><sub>
  <b>Left:</b> the Application List — one entry per brand pack, nine of them on one body.
  <b>Right:</b> the screen you land in when you open one — a real look already selected.
  </sub>
</p>

Sony closed its PlayMemories Camera Apps store in 2021, and every body made before late 2016
lost its app channel. Those bodies still run an Android userspace, which means they can still
be given a new personality. This project turns a Sony into the cameras you reach for — a Leica
monochrome, a Hasselblad natural, a Fujifilm colour, a Ricoh GR contrast, a Pentax reversal — and
folds 164 film looks in besides.

**It installs from one Windows file, in one click.** Download the installer, run it, plug the
camera in: it finds the body by itself, shows the packs it carries with every one already
ticked, and writes them across USB behind a single progress bar. There is no APK to fetch, no
Sony-PMCA-RE to install first, and no command line — **the recipes ship inside the installer.**

The free installer is **Base — 6 packs, 91 looks**: Fujifilm, Fuji Film, Kodak, Niche Film,
Ricoh GR and Sony. Each pack carries its own recipe table under its own package name, so they
install side by side and you take only the brands you actually shoot. The remaining packs —
Leica, Pentax, Hasselblad, Cinema LUT and Monochrome, plus the all-in-one app that holds the
whole catalog — ship separately.

After that the look is not an app running in the background — it is simply what the camera
does. Close the app, power-cycle, and your JPEG comes out graded in **P, A, S, M and video**.

**Language follows the camera.** Put the body into 简体中文 and every recipe name, group
and on-screen label switches to Chinese — the same app, no separate download to hunt for.
A body left in English stays English.

> **Honest note.** These are approximations, not anybody's colour science. An a6000 has no
> Picture Profile menu and cannot store a tone curve, so each look is assembled from what the
> body can actually hold. **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** is where those
> limits are drawn out — read it if you want to know why something looks the way it does.

---

## Does your camera work?

Press `MENU` and look for an **`Application`** entry.

| It has `MENU → Application` | It does not |
|---|---|
| a6000 · a6300 · a6500 · a5100 · a5000<br>a7 · a7R · a7S · a7 II · a7R II · a7S II<br>NEX-5R · NEX-5T · NEX-6<br>RX100 III / IV / V · RX10 II / III · RX1R II<br>HX60 / HX90 / HX400 · WX500<br>a68 · a77 II · a99 II | a6100 · a6400 · a6600 · a6700 · ZV-E10<br>a7 III and everything after it · a9 · a1<br>RX100 VA and later · RX10 IV · RX0 · HX99 · ZV-1 |

**No `Application` entry means nothing fits, and that is final.** Bodies after late 2016 run
signed firmware. Not this project, not Sony's own store. Reports of this working on an a6400
are misreports.

**Confirmed on a real body: the α7S II** — installs, launches, nine packs side by side. Photographs
in [On a real camera](#on-a-real-camera). The rest of the left column is supported by the
platform rather than tested body by body, and the two are not the same claim.

---

## Install

**One file. One click. No APK, no toolchain, no command line.**

<p align="center">
  <img src="docs/assets/install-flow.svg" width="760" alt="installation flow">
</p>

1. **Download** `SonySOOCRecipes-Base-EN.exe` from
   [Releases](https://github.com/HairuoLiu/sony-sooc-recipes/releases/latest). It is the only
   download there is: the recipes and the install channel both live inside it. *(Reading
   Chinese? `SonySOOCRecipes-Base-CN.exe` is the same installer in Chinese.)*
2. **Prepare the body** — battery charged, memory card in, a **data-capable** USB cable, and
   `Setup (the toolbox icon) → USB Connection → **Mass Storage**`. Power on, plug in, and wait
   for the screen to say `USB Mode`.
3. **Run the installer and click through it.** It finds the camera by itself, then lists the
   packs it carries — every one already ticked. Untick anything you do not want and press
   **Next**. About **10–15 minutes** for the lot; the window can be minimised.
4. **Unplug, power off and on, and shoot.** `MENU → Application → Application List` now holds
   one entry per pack, and the looks are simply how the camera behaves in **P, A, S, M and
   video**.

<p align="center">
  <img src="docs/assets/install/en/01-connect-camera.png" width="250" alt="Step 1 of the installer: it reports Camera connected and offers a Detect Again button">
  <img src="docs/assets/install/en/02-choose-packs.png" width="250" alt="Step 2 of the installer: a table of the packs it carries, every one ticked, with a Select All box">
  <img src="docs/assets/install/en/03-installing.png" width="250" alt="Step 3 of the installer: a progress bar reading Installing 1/6, with a Cancel button and a Show Details checkbox">
  <br><sub>
  <b>1 · Connect</b> — it finds the body itself. <b>2 · Choose</b> — every pack it carries,
  ticked; untick what you do not want. <b>3 · Install</b> — one progress bar, 10–15 minutes.
  </sub>
</p>

> **Windows only.** The installer is a Windows program, Windows 7 SP1 through 11. There is no
> macOS or Linux build of it, and the pre-built APKs are no longer published — on those
> platforms the route is to build from this repository, where `tools/build_apk.sh` turns
> `catalog/filters.json` into the same APKs and
> [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) documents the pipeline.

> **The APK downloads are withdrawn.** Earlier versions of this project published a per-brand
> APK for you to install yourself with Sony-PMCA-RE. That download is gone: the installer does
> the same job in place, and shipping the recipes pre-built is what makes the install a single
> click. A guide that points at `SonySOOCRecipes-<brand>.apk` is describing a version this
> repository no longer publishes.

> **Before you install.** If the body already carries a Sony SOOC Recipes from somewhere else,
> remove it first — an app signed with a different key cannot overwrite one that is already
> there. See [Uninstall](#uninstall).

Mid-install the camera blanks to black and switches modes a few times. That is normal: do not
press anything and do not unplug. If the installer reports no camera, check the cable, the
Mass Storage setting and the card, then press **Detect Again**.

Detailed walkthrough, per-OS prerequisites and a troubleshooting table:
**[docs/INSTALL.md](docs/INSTALL.md)**. Already have Wi-Fi ADB running? It is faster for
reinstalls, and it can never replace USB — **[docs/CHANNEL-COMPARISON.md](docs/CHANNEL-COMPARISON.md)**
says why in six lines.

**Will it brick my camera?** No firmware is touched and nothing is unlocked: the app writes
values you could set by hand in the body menus, and everything is reversible. It is still
third-party software on hardware with no supported update path — keep a backup of anything
you care about. **[docs/FAQ.md](docs/FAQ.md#safety)** answers the rest.

---

## What's inside

164 looks in 15 groups — film stocks and the colour of other cameras alike. The hook is the
camera simulation: a Sony that shoots like a **Leica**, **Hasselblad**, **Fujifilm**, **Ricoh GR**
or **Pentax**, not just a film stock. **[The filter browser](catalog/index.html)** lists every one,
searchable and filterable — it is a single self-contained HTML file, so download it and open it
locally rather than viewing the source on GitHub.

<details>
<summary>Show all 164 looks, grouped (full table)</summary>

| Group | Count | Representative looks |
|---|---|---|
| **Sony** | 8 | FL (film-like) · IN (instant) · VV2 |
| **Fuji Sim** | 26 | Classic Chrome · Nostalgic Neg · Acros +R |
| **Fuji Film** | 10 | Pro 400H · Reala 500D · Industrial Print 400 |
| **Kodak** | 20 | Portra 400 · Gold 200 · Double-X 5222 · Vision3 · Ektar 25 |
| **Cine** | 4 | Cinestill 800T · Cinestill 50D · Rec709 |
| **Ricoh GR** | 16 | GR Positive Film · High-contrast B&W · Moriyama · Cinema Green/Yellow |
| **Leica** | 20 | Monochrom · M9 CCD · B&W HC · Chrome · Teal |
| **Hasselblad** | 4 | HNCS Natural · LowSat · HiContrast |
| **Canon / Nikon** | 5 | Canon Faithful · Nikon Flat |
| **Pentax** | 11 | Bleach Bypass · Radiant · Reversal Film · Harubeni · Fuyuno |
| **Pana / Olympus** | 4 | L.Monochrome D · Pop Art |
| **Other Stocks** | 17 | Adox · Lomochrome · ORWO · Rollei · Svema · Ambrotype |
| **Ilford** | 5 | HP5 · Delta 3200 · Pan F 50 |
| **Kino LUT** | 9 | Kino Cool 4 … Kino Warm 4 |
| **App Look** | 5 | Toy Camera warm/cool · Part Color red · Posterization · Teal Mood |

**149** of those are installable; the rest are registered by name only. Rather have one brand
than everything? Each pack carries one brand's looks under its own package name, so they sit
side by side on the body — the free installer ships six of them. What each pack contains is
listed in **[docs/packs/README.md](docs/packs/README.md)**, and the full pack list, with the
reasoning behind it, is in **[docs/BRAND-PACKS.md](docs/BRAND-PACKS.md)**.

</details>

> **Honest note.** Whether a *look* is faithful to the film it imitates is recorded per recipe,
> in the `verified` field of `catalog/filters.json`. Seventy-two were written here and not one
> has been confirmed on hardware yet. The app prints none of that — the marker survives only
> as a comment in the generated source, which is why nothing above says it either. The badge
> on the main screen is the look's brand — 宾得 / 柯达 / 徕卡 … (EN `PENTAX` / `KODAK` /
> `LEICA` …), and it reports nothing else: the old `ACTIVE` / `PREVIEW` / `PROTECTED` status
> words are gone.

---

## Using it

Open the app, pick a group, scroll with the control wheel, press the centre button to store,
then power-cycle — some settings only settle after a restart. That is the whole loop.

- **A "Strength" dial, 0–100 % (step 5, default 100 %).** It scales the look's saturation,
  contrast, sharpness and exposure-compensation offsets by that ratio before they reach the
  camera — 100 % is the recipe exactly as authored, 50 % halves every adjustment, 0 % is
  neutral. The value is remembered in the app's own settings and is not written to the camera.
- **Picture Effect looks need JPEG.** With a Picture Effect active, RAW and RAW+JPEG quietly
  discard the effect.
- **The a5100 has no Fn or AEL button**, so brand-list browsing and the hidden panel are
  unreachable there. The control wheel still reaches every look.

### Three screens

Opening the app gives you a **single frosted bar** straight away — one slim floating pill
holding the whole readout on one line: the look's name, its brand badge (`宾得` / `柯达` /
`徕卡` …; EN `PENTAX` / `KODAK` / `LEICA` …) and its position. The pill hugs the text —
no vertical padding, no font leading — and the live view keeps the rest of the frame.
Press **AEL** or **DISP** to cycle the overlay: the bar → the compact pill → the pure
viewfinder (nothing on screen at all) → the bar. Press **up** to move from the name onto
the parameters — the selected one is marked with an outlined capsule; **left / right**
then move between parameters.

Press **Fn** and you get the **recipe browser**: one white single-column list holding every
look this app carries, grouped by category. Each row carries its name, a one-line summary of
what it does to the image, and whether it is `CS` or `PE` — Creative Style also applies to
RAW, Picture Effect only reaches JPEG. The highlighted row also carries a **设置** / `SET` chip.

| Key | Does |
| --- | --- |
| ↑ ↓ or either dial | move through every look |
| centre button · right | open the settings editor on the highlighted look |
| ← · Fn · MENU · AEL · DISP | close the browser |

The **editor** is a vertical list of every parameter — label on the left, its current value
always on the right — shown on its own so the frame stays open while you dial a value. The
list is walked with its own axis: **↑ ↓** move the selection up and down the list, **← →**
(or either dial) change the value on the selected row, `ENTER` stores and drops straight
back to the pure viewfinder, `Fn` throws the changes away and returns to the browser.
Nothing is hidden here: parameters a Picture Effect overrides (style, saturation, contrast,
sharpness, matrix, strength) are still listed, greyed out, with their value readable and a
*（不能改动）* / *(read-only)* note under it — so a GR high-contrast look shows all its rows
instead of looking like it lost half of them. The rows never leave the middle box: the
recipe title above the list and the key legend below it cannot be painted over. Every route
that stores a look ends with the overlay hidden, so nothing is left covering the picture.

The browser is a separate screen rather than a restyle of the main one: it takes its own
colours from `catalog/ui-theme.json` and leaves the main screen exactly as it was.

---

## Uninstall

<details>
<summary>Show the uninstall steps — and how to put the camera's colours back</summary>


Two different things come off, and removing one does not remove the other: the **app**, and
the **look it stored**. Putting the camera's colours back is a separate step.

```
MENU → Application → Application Management → Manage and Remove → pick the entry → remove
```

On some bodies `Application Management` sits one level deeper, under `Application List`, and
the label is localised. Leave the app first — get back to the shooting screen — rather than
removing it while it is open.

**Sony-PMCA-RE cannot uninstall, and that is not an oversight you can work around.** The tool
the installer drives underneath has no uninstall command: its entire command set is `info`,
`install`, `market`, `apk2spk`, `spk2apk`, `firmware`, `updatershell`, `serviceshell`,
`guess_firmware`, `gps`, `stream`, `wifi`, `print_backup`. If that menu item is missing or
greyed out, the route is ADB — turn it on with
[OpenMemories-Tweak](https://github.com/ma1co/OpenMemories-Tweak), then
`adb uninstall com.hairuoliu.sonysoocrecipes` (or `...sonysoocrecipes.<brand>`). The full flow,
and how to reset the stored look, is in **[docs/INSTALL.md](docs/INSTALL.md)**.

</details>

---

## On a real camera

<details>
<summary>Show the photos from a real α7S II</summary>


The two shots at the top of this page are the maintainer's own α7S II. The three below
round it out — the Application List scrolled past the first frame, and the FN browser in
two different packs. None are renders or mockups.

<p align="center">
  <img src="docs/assets/hardware/02-a7sii-application-list-more.jpg" width="300" alt="The same Application List scrolled on: Fuji Film Style, Fujifilm Style, Hasselblad Style, Kodak Style, Leica Style and the PlayMemories Camera Apps entry">
  <br><sub>
  The <b>Application List</b> scrolled — the rest of the nine packs on this body (Kodak Style,
  Leica Style, Hasselblad Style, the Fujifilm and Fuji Film entries, and the PlayMemories
  Camera Apps entry). The first frame is the photograph at the top of this page.
  </sub>
</p>

<p align="center">
  <img src="docs/assets/hardware/04-a7sii-browser-cine.jpg" width="300" alt="The FN recipe browser reading RECIPES 26, in the CINE group, with Cinestill 50D (Blue Velvet) selected">
  <img src="docs/assets/hardware/05-a7sii-browser-ricoh-gr.jpg" width="300" alt="The FN recipe browser reading RECIPES 11, in the RICOH GR group, with GR Positive Film selected">
  <br><sub>
  The <b>FN browser</b> — a screen of its own, opened with the <b>Fn</b> key. On the left, the
  Niche Film Style pack: 26 looks, scrolled to its 4-look CINE group. On the right, the Ricoh GR
  Style pack: 11 looks, all of them RICOH GR. Same app, same body, different pack.
  </sub>
</p>

- **The counts on screen are the catalog's.** `CINE · 4` is the catalog's four `cine` recipes,
  and `RECIPES · 26` is the Niche Film Style pack — ilford 5, cine 4, other-stocks 17. The Ricoh
  screen says `RECIPES · 11` because the `ricoh-gr` group's sixteen entries include five that are
  reference-only and compile into nothing; only the eleven that compile reach the camera. That
  split is `catalog/filters.json`, not a rounding.
- **The values on screen are the catalog's.** Cinestill 50D (Blue Velvet) reads
  `Standard · −1/+1 · 5600K B2` — which is `sat −1, con +1, wb 5600K, ab −2` in the catalog. GR
  Positive Film reads `Standard · +3/+2 · A2` against `sat 3, con 2, wb ab 2`.
- **Packs coexist, and you only need one.** Nine brand packs installed side by side on one body.
  That is what the different package names exist to make possible — seen rather than asserted.
  It also means you never have to carry all of them: each pack holds one brand's looks, so the
  browser on the camera stays as short as the brand you actually shoot.
- **The badge says `PROTECTED`.** The camera's settings store was write-protected, so this was
  being *previewed*, not stored; the fix is OpenMemories:Tweak with *Backup protection* off. It
  stays in the crop because it is what the screen said.
- **It does not make the looks verified.** That a *body* runs the app is one claim; a *look*
  being faithful to its film is another, recorded per recipe in `verified`.

</details>

---

## Read next

<details>
<summary>Show where to go next (docs index)</summary>


| If you want to | Go to |
|---|---|
| install step by step, with every prerequisite and a fix for what went wrong | [docs/INSTALL.md](docs/INSTALL.md) |
| know whether it is safe, or ask something nobody has answered yet | [docs/FAQ.md](docs/FAQ.md) |
| carry one brand instead of all of them | [docs/BRAND-PACKS.md](docs/BRAND-PACKS.md) |
| understand how a value reaches the camera's settings store | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| see how a `.cube` file becomes ten integers | [docs/LUT-TO-SETTINGS.md](docs/LUT-TO-SETTINGS.md) |
| add a look, or contribute a before/after photo pair | [docs/ADDING-FILTERS.md](docs/ADDING-FILTERS.md) |

Everything here is generated from `catalog/filters.json` and held in place by gates that run
locally and again on every push. That machinery is written down rather than hidden — none of it
is needed to put a look on a camera.

</details>

---

## Origin and licence

<details>
<summary>Show upstream sources and licences</summary>


| Upstream | Contribution | Licence | Redistributed |
|---|---|---|---|
| [voxivoid/recipe-lab-sony-pmca](https://github.com/voxivoid/recipe-lab-sony-pmca) | **77 recipe parameter sets**, the settings-store reverse engineering, the app itself | **MIT** | ✔ |
| [ma1co/Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE) | the install channel, firmware and settings dumping | MIT | ✘ external tool |
| [ma1co/OpenMemories-Tweak](https://github.com/ma1co/OpenMemories-Tweak) | Wi-Fi ADB and developer toggles | MIT | ✘ external tool |
| [ukiki0718-netizen/sony-a5100-film-studio](https://github.com/ukiki0718-netizen/sony-a5100-film-studio) | names and provenance of 15 looks | PolyForm Noncommercial | ✘ name only |
| [bonyback1/sony-pmca-ricoh-mod](https://github.com/bonyback1/sony-pmca-ricoh-mod) | the hardware matrix + shared gamma method | Apache-2.0 | ✘ reference only |

**Audited 2026-09-28: upstream has moved on, and the pin is deliberate.** The build is pinned to
`6b5c8aa` (2026-09-12, `v1.1.0-dev.8` on upstream's `development` branch); voxivoid has since
released through **v1.4.0** (2026-09-27). What changed there is **value re-tuning, not new looks**:

- **No recipe was added or removed.** 77 recipes in the same 12 groups at the pin, at v1.4.0, and
  on `main` today. No Pentax group was added either, and upstream's `Hasselblad` group still holds
  a single recipe — ours holds four (1 upstream + 3 written here).
- **21 of the 77 were re-tuned** — largely pulling saturation back from values that render as flat
  grey on an α7S II (`−9`/`−8`/`−6` → `−6`/`−4`) and re-picking the Creative Style base
  (*Classic Chrome* `Neutral −5` → `Standard −1`; *Kodak Ultra Max 400* `+3/+1` → `0/0`;
  *Classic Cinema* `Neutral −4` + `5000 K` → `Standard` + `6000 K`). By group: Sony 1, Fuji Sim 6,
  Fuji Film 2, Kodak 8, Cine 3, Ricoh GR 1.
- **The `SEPIA` enum was corrected**: upstream had guessed `13`, it is `14`, and `13` is now
  marked unidentified — so a recipe storing `13` no longer displays as "Sepia".

**Those 21 re-tunings are not in this build.** The catalog reproduces the *pinned* revision, so
these packs shoot the pre-v1.2.0 values. `tools/check_fidelity.py` compares against that same
pinned SHA and therefore reports **0 drift** — green by construction, not proof that we match
upstream's newest release. Porting the 21 is a deliberate decision, not a bug fix: it changes what
21 recipes do on the body.

Brand names in recipe names — Sony, Fujifilm, Kodak, Ricoh, Leica, Hasselblad, Canon, Nikon,
Panasonic, Olympus, Agfa, Ilford, Cinestill, Polaroid, Instax — are trademarks of their
owners, used here only to describe the look a recipe aims at. **This project is not affiliated
with or endorsed by any of them.** Every value is a community-derived approximation, not
official colour science. Full provenance: **[NOTICE.md](NOTICE.md)** ·
**[CHANGELOG](CHANGELOG.md)**.

</details>

---

## Disclaimer

**This is an unofficial personal project, and it is not affiliated with anyone.** It is not
made, endorsed, sponsored or approved by Sony, nor by Fujifilm, Kodak, Leica, Hasselblad,
Ricoh, Pentax, Canon, Nikon, Panasonic, Olympus, Ilford, Cinestill or any other brand named
in a recipe or a pack. Every trademark belongs to its owner; those names are used here only
to describe the look a recipe aims at.

- **The recipes are approximations, not anybody's colour science.** They are community-derived
  and, where they imitate a film or another camera, they imitate it by eye — see the `verified`
  field in `catalog/filters.json` for which ones have even been checked on a body. Nobody has
  measured them against the thing they name.
- **The `<Brand> Style` pack names are risk reduction, not clearance.** Naming an app after a
  trademark is still trademark use. The reasoning, and what it does *not* buy you, is in
  [docs/BRAND-PACKS.md §8](docs/BRAND-PACKS.md).
- **Third-party software, no warranty, on hardware with no supported update path.** Nothing
  here touches firmware or unlocks anything — it writes values you could set by hand — but it
  is still unsupported software. Back up your card, test on footage you can lose, and install
  at your own risk.
- **If you redistribute these apps, the risk moves to you.** The icons are user-supplied,
  all-rights-reserved images and the names are trademarks; republishing the packs — or shipping
  them inside another product — is your call and your exposure.

Provenance and licences: **[NOTICE.md](NOTICE.md)** · icons: `assets/app-icon-packs/CREDITS.md`.

---

## Licence

This repository's own code, data structure and documentation: **[MIT](LICENSE)**.

Recipe *values* come from upstream and keep the upstream licence — see [NOTICE.md](NOTICE.md).
Fifteen matrix looks are recorded by name only and are **not** redistributable.
