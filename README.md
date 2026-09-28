<h1 align="center">sony-sooc-recipes</h1>

<p align="center">
  <b>Turn your Sony into a Leica, Hasselblad, Fujifilm, Ricoh or Pentax — with 164 film and camera looks, straight out of camera.</b>
  <br>
  <sub>164 looks · 149 installable · 15 groups — film stocks &amp; other cameras' colour, SOOC JPEG</sub>
</p>

<!-- counts: total=164 compiled=149 -->

<p align="center">
  <b>English</b> · <a href="README.zh-CN.md">简体中文</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/HairuoLiu/sony-sooc-recipes/actions/workflows/ci.yml"><img src="https://github.com/HairuoLiu/sony-sooc-recipes/actions/workflows/ci.yml/badge.svg" alt="catalog gates"></a>
  <a href="https://github.com/HairuoLiu/sony-sooc-recipes/releases/latest"><img src="https://img.shields.io/badge/download-Windows%20installer-2f81f7" alt="download the Windows installer"></a>
  <img src="https://img.shields.io/badge/license-MIT-3fb950" alt="MIT licence">
</p>

<p align="center">
  <img src="docs/assets/hardware/01-a7sii-application-list.jpg" width="320" alt="The camera's Application List: every brand Style pack installed side by side">
  <img src="docs/assets/hardware/03-a7sii-main-screen-cinestill-50d.jpg" width="320" alt="Inside one pack: a real look already selected on the frosted main screen">
  <br><sub><b>Left:</b> one entry per brand pack, nine of them on one body. <b>Right:</b> the screen you land in when you open one — a look already selected.</sub>
</p>

**One Windows file, one click.** Download the installer, run it, plug the camera in — it finds the body by
itself and writes the looks across USB behind a single progress bar. **No APK to fetch, no toolchain, no
command line.** The recipes ship *inside* the installer.

---

## What film simulations you get

The installer turns your Sony into other cameras. Each **brand pack** is one app that carries that brand's
looks under its own name, so they install side by side and you take only the brands you actually shoot.

### Free installer — Base (6 packs, 91 looks)

| Film simulation | 胶片模拟 | Looks | A taste of what's inside |
|---|---|---:|---|
| Fujifilm Style | 富士模拟 | 16 | Classic Chrome · Nostalgic Neg · Acros +R |
| Fuji Film Style | 富士胶片风格 | 10 | Pro 400H · Reala 500D · Industrial Print 400 |
| Kodak Style | 柯达风格 | 20 | Portra 400 · Gold 200 · Double-X 5222 · Vision3 |
| Niche Film Style | 小众胶片风格 | 26 | Ilford HP5 · Cinestill 50D/800T · Lomochrome |
| Ricoh GR Style | 理光 GR 风格 | 11 | GR Positive Film · High-contrast B&W · Moriyama |
| Sony Style | 索尼风格 | 8 | FL (film-like) · IN (instant) · VV2 |

The full lineup also includes **Leica, Hasselblad, Pentax, Cinema LUT and Monochrome** styles, plus an
**all-in-one app that carries all 149 looks** — available separately.
Every look, searchable and filterable: **[the filter browser](catalog/index.html)** (a single HTML file —
download and open it locally rather than viewing the source on GitHub).

---

## Install in one click

**One file. One click. No APK, no toolchain, no command line.**

1. **Download** `SonySOOCRecipes-Base-EN.exe` from
   [Releases](https://github.com/HairuoLiu/sony-sooc-recipes/releases/latest) — the only download there is.
   *(Reading Chinese? `SonySOOCRecipes-Base-CN.exe` is the same installer in Chinese.)*
2. **Prepare the body** — charged battery, memory card in, a **data-capable** USB cable, and
   `Setup → USB Connection → Mass Storage`. Power on, plug in, wait for `USB Mode`.
3. **Run the installer and click through.** It finds the camera, lists its packs (all ticked); untick
   what you don't want and press **Next**. About **10–15 minutes**; the window can be minimised.
4. **Unplug, power off and on, and shoot.** `MENU → Application → Application List` now holds one entry
   per pack, and the looks are simply how the camera behaves in **P, A, S, M and video**.

> 🖼️ **Want a bigger, swipeable view?** Open the
> [interactive install walkthrough](docs/install-walkthrough.html) — flip through the three steps with synced
> captions (arrow keys or swipe).

<p align="center">
  <img src="docs/assets/install/en/01-connect-camera.png" width="250" alt="Step 1: Camera connected, with a Detect Again button">
  <img src="docs/assets/install/en/02-choose-packs.png" width="250" alt="Step 2: the packs it carries, all ticked, with a Select All box">
  <img src="docs/assets/install/en/03-installing.png" width="250" alt="Step 3: a progress bar reading Installing 1/6">
  <br><sub><b>1 · Connect</b> · <b>2 · Choose</b> · <b>3 · Install</b></sub>
</p>

> **Windows only.** The installer is a Windows program (Windows 7 SP1 – 11); there is no macOS or Linux
> build. The pre-built APKs are no longer published — the installer does the same job in place.

Detailed steps, prerequisites and troubleshooting: **[docs/INSTALL.md](docs/INSTALL.md)**.
Before installing, if the body already carries a Sony SOOC Recipes from elsewhere, remove it first — see
**[Uninstall](#uninstall)**.

---

## Good to know

- **Language follows the camera.** Set the body to 简体中文 and every recipe name, group and label
  switches to Chinese — the same app, no separate download. A body left in English stays English.
- **Safe.** No firmware is touched and nothing is unlocked: it writes values you could set by hand, and
  everything is reversible. Still third-party software on hardware with no supported update path — back up
  your card. **[docs/FAQ.md](docs/FAQ.md#safety)** answers the rest.
- **These are approximations, not colour science.** Each look is assembled from what the body can store —
  see the `verified` field in `catalog/filters.json` for which have even been checked on a body. Full
  provenance and limits: **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**.

---

## On a real camera

<p align="center">
  <img src="docs/assets/hardware/01-a7sii-application-list.jpg" width="300" alt="Application List with nine brand packs side by side">
  <img src="docs/assets/hardware/03-a7sii-main-screen-cinestill-50d.jpg" width="300" alt="Main screen with Cinestill 50D selected">
</p>

**Confirmed on a real α7S II** — installs, launches, nine packs side by side. Photographs in
**[docs/INSTALL.md](docs/INSTALL.md)**. The rest of the supported column is *platform* support, not a
body-by-body test.

---

## Uninstall

```
MENU → Application → Application Management → Manage and Remove → pick the entry → remove
```

If that menu item is missing or greyed out, uninstall over ADB
(`adb uninstall com.hairuoliu.sonysoocrecipes.<brand>`). Removing the app does **not** undo a stored look —
to reset colours, in the app press **TRASH** + centre button, power-cycle, or
`Setup → Setting Reset → Camera Settings Reset`. Full flow: **[docs/INSTALL.md](docs/INSTALL.md)**.

---

## Where to go next

| If you want to | Go to |
|---|---|
| install step by step, with every prerequisite | [docs/INSTALL.md](docs/INSTALL.md) |
| know whether it is safe / ask a question | [docs/FAQ.md](docs/FAQ.md) |
| carry one brand instead of all of them | [docs/BRAND-PACKS.md](docs/BRAND-PACKS.md) |
| understand how a value reaches the camera | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| browse every look | [catalog/index.html](catalog/index.html) |

---

## Disclaimer

**Unofficial personal project, not affiliated with anyone.** Not made, endorsed or approved by Sony, nor by
Fujifilm, Kodak, Leica, Hasselblad, Ricoh, Pentax or any brand named in a recipe. Every trademark belongs
to its owner; names are used only to describe the look a recipe aims at. The recipes are community-derived
approximations, not official colour science. Third-party software with no warranty — install at your own
risk. If you redistribute, the risk moves to you.
Provenance and licences: **[NOTICE.md](NOTICE.md)** · icons: `assets/app-icon-packs/CREDITS.md`.

---

## Licence

This repository's own code, data structure and documentation: **[MIT](LICENSE)**. Recipe *values* come
from upstream and keep the upstream licence — see [NOTICE.md](NOTICE.md). Fifteen matrix looks are
recorded by name only and are **not** redistributable.
