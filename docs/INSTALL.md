# Installation: putting film recipes on your Sony camera

<p align="center">
  <b>English</b> · <a href="INSTALL.zh-CN.md">简体中文</a>
</p>

This guide walks you through installing **Sony SOOC Recipes** — an app that writes a catalog of
film-style recipes (Creative Style, Picture Effect, white balance, DRO…) into your camera,
so older Sony bodies can produce film-like output straight out of the camera.

**What this takes:** about 10–15 minutes, once, on Windows. **Download one file, run it, plug the
camera in** — the installer carries the recipes and the install channel inside it, so there is no
APK to fetch, no Sony-PMCA-RE to install first, and nothing to type.

<p align="center">
  <img src="assets/install-flow.svg" width="720" alt="installation flow">
  <br><sub>Figure: the whole path — one download, one click, a progress bar</sub>
</p>

The rest of this page is that flow in detail, then the manual route for macOS, Linux and anyone
who would rather drive the tools themselves. Read [CHANNEL-COMPARISON.md](CHANNEL-COMPARISON.md)
if you want to understand the two low-level channels the manual route offers — the installer takes
the first of them for you, automatically.

---

## Before you start

### Confirm your camera is supported

Press `MENU` and look for an **`Application`** entry. If it is there, your camera uses the
PlayMemories Camera Apps (PMCA) channel and can receive apps. If it is not, stop here — no
method in this repository can install anything on it.

| Has `MENU → Application` | Does not |
|---|---|
| a6000 · a6300 · a6500 · a5100 · a5000<br>a7 / a7R / a7S / a7 II / a7R II / a7S II<br>NEX-5R · NEX-5T · NEX-6<br>RX100 III / IV / V · RX10 II / III · RX1R II<br>HX60 / HX90 / HX400 · WX500<br>a68 · a77 II · a99 II | Pre-2012 NEX (NEX-3 / 5 / 5N / F3 / 3N / **7**) · a3000 · a3500<br>a6100 · a6400 · a6600 · a6700 · ZV-E10<br>a7 III and everything after · a9 series · a1 series<br>RX100 VA and after · RX10 IV · RX0 · HX99 · ZV-1 series |

> **Honest note.** "No `Application` menu" means you cannot install apps, full stop. Sony shut
> down its own app store in 2021, and every body from late 2016 onward (a6500 and a99 II were
> the last two) ships signed firmware that rejects apps — not just this project, Sony itself
> cannot load apps onto them. Reports of people running this on an a6400 are mistaken.
>
> There is a boundary on the other end too: **PMCA starts with the autumn-2012 NEX-5R / NEX-6.**
> The earlier NEX-7, NEX-3 / 5 / 5N / F3, and the a3000 / a3500 have no Android subsystem and
> no `Application` menu either — their absence from the supported column above is **not an omission**.

**Confirmed on a real body: the α7S II**, with nine brand packs installed side by side. Photographs
of it running are in the [README](../README-English.md#on-a-real-camera). Everything else in the left
column is *platform* support — the body has the app channel — rather than a body-by-body test,
and those are not the same claim.

### What you need

- A computer (Windows, macOS, or Linux).
- A **data-capable USB cable** (a6000 uses micro-USB; the charging-only wire in a 3-in-1 kit
  will not work).
- A **memory card** inserted in the camera.
- A **fully charged battery.** Installation toggles the camera's mode a few times. If power
  dies mid-install, recovery is unpleasant — charge first.

### Download the installer

`SonySOOCRecipes-Base-EN.exe`, from the project's Releases page:

https://github.com/HairuoLiu/sony-sooc-recipes/releases/latest

*(Reading Chinese? `SonySOOCRecipes-Base-CN.exe` is the same installer with a Chinese interface.)*

**It is one file, and it is the only download.** The recipes are compiled in, and so is
`pmca-console` — the Sony-PMCA-RE engine that talks to the camera over USB. Nothing has to be
installed first, and nothing is left behind except the program itself.

**What it carries: Base — 6 packs, 91 looks.** Fujifilm, Fuji Film, Kodak, Niche Film, Ricoh GR
and Sony. Each is a separate app on the camera with its own Android package name, which is exactly
what lets them sit side by side, and you can untick any of them during the install. The remaining
packs — Leica, Pentax, Hasselblad, Cinema LUT and Monochrome, plus the all-in-one app that holds
the whole catalog — are distributed separately. The full list and the reasoning are in
[BRAND-PACKS.md](BRAND-PACKS.md).

### Run it

<p align="center">
  <img src="assets/install/en/01-connect-camera.png" width="330" alt="Step 1: Camera connected, with a Detect Again button">
  <img src="assets/install/en/02-choose-packs.png" width="330" alt="Step 2: the packs it carries, all ticked, with a Select All box">
  <img src="assets/install/en/03-installing.png" width="330" alt="Step 3: a progress bar reading Installing 1/6">
  <br><sub>Connect · Choose · Install — the three screens between the .exe and a camera full of looks.</sub>
</p>

1. **Connect.** Plug the prepared camera in; the installer detects it on its own and the step
   turns green. If it does not, press **Detect Again** — the checklist is
   [below](#if-the-installer-cannot-see-the-camera).
2. **Choose.** Every pack it carries is ticked. Untick what you do not want; the **Select All**
   box at the top right clears or restores the lot.
3. **Install.** One progress bar and a count of what is left. **About ten minutes.** The window
   can be minimised while it works.
4. **Finish.** Unplug, power off and on again, and shoot.

> **Honest note.** The camera blanks to black and switches modes a few times while the packs are
> written. That is normal — do not press anything and do not unplug. If a pack fails, the finish
> screen names it; tick **Show Details** for the underlying log.

### Read these three before installing

> **The APK downloads are withdrawn.** Earlier versions published a per-brand APK for you to
> install yourself with Sony-PMCA-RE. That download is gone: the installer does the same job in
> place. If a guide points you at `SonySOOCRecipes-<brand>.apk`, it describes a version this
> repository no longer publishes.

> **Two things actually bite people.**
>
> 1. **If the camera already has a Sony SOOC Recipes from somewhere else, remove it first.** An
>    app signed with a different key **cannot overwrite** an existing install. That is also true
>    between packs: `…sonysoocrecipes.ricoh` and `…sonysoocrecipes.sony` are *different packages*
>    and install side by side, but two copies of the same one do not.
> 2. **Several packs do not give you several cameras.** The camera's settings store is shared, and
>    only one recipe can be active at a time. Packs differ in what they *ship*, not in what the
>    camera can *do*.

> **Some looks are not verified on hardware.** Every recipe answers this for itself, in the
> `verified` field of `catalog/filters.json` — the ones this repository wrote itself are `false`,
> and each is marked in the generated `Recipes.java`. Try those on discardable footage before
> trusting them on something you cannot reshoot. The marker is a source comment, not a label the
> app draws; see the [FAQ](FAQ.md) for what the badge on the main screen actually means.

> The version number shown inside the app is the **base app's** version, not this project's. The
> base app reads its version from `AndroidManifest.xml`; this repository only swaps the recipe
> table. Trust the installer you downloaded, not the in-app number.

---

## If the installer cannot see the camera

| What you see | What to do |
|---|---|
| **No camera detected** | Check, in this order: the cable is **data-capable** (not charge-only) · `Setup → USB Connection` is on **Mass Storage**, not PC Remote · a memory card is in · the camera is powered on and its screen says `USB Mode` · nothing else is holding the USB device (Photos, Image Capture, Dropbox, Imaging Edge). Then **Detect Again**. |
| A **driver** error | In **Show Details**, switch the driver to `libusb` and retry. If it still fails on Windows, install the libusb-win32 driver with [Zadig](https://zadig.akeo.ie) and run again. |
| It detects the camera, then fails part-way | The most common cause is an older Sony SOOC Recipes already on the body. Remove it in `MENU → Application → Application Management → Manage and Remove`, then install again. |
| Nothing at all happens | Press `MENU` and look for an `Application` entry. If there is none, this body cannot run apps — see the model table above. No workaround exists. |

---

## Doing it by hand (macOS, Linux, or the command line)

The installer is Windows-only. Everything it does you can do yourself — and on macOS and Linux
that is the only route, because the pre-built APKs are no longer published. So the manual route
starts by building them from this repository, with the same tooling that produced the copies
inside the installer:

```bash
git clone https://github.com/HairuoLiu/sony-sooc-recipes.git
cd sony-sooc-recipes
tools/build_all_local.sh          # every target; the script's header lists the toolchain
```

That writes `SonySOOCRecipes*.apk` into `dist/`. Which to install: the all-in-one carries every
look, a pack carries one brand's. Both lists, and the reasoning, are in
[BRAND-PACKS.md](BRAND-PACKS.md).

What follows is the manual route in full. **Channel A** is the one the installer drives — USB,
offline, and the only one a first install should use. **Channel B** (Wi-Fi ADB) is for repeated
reinstalls, and it can never replace Channel A: enabling ADB needs OpenMemories:Tweak, which
itself installs over Channel A.

---

## Channel A: USB + Sony-PMCA-RE

**What the installer automates, spelled out.** Fully offline, exposes no network
service, works on every PMCA body, and requires no pre-installed app.

### 1. Get the installer, Sony-PMCA-RE

This is ma1co's tool. It uses the very same channel Sony's own app store used to push apps into
the camera.

- **Windows:** download `pmca-gui.exe` from
  [ma1co/Sony-PMCA-RE releases](https://github.com/ma1co/Sony-PMCA-RE/releases). No install —
  just run it. You also need the USB driver; install it per ma1co's README
  (https://github.com/ma1co/Sony-PMCA-RE).
- **macOS:** the same page has a macOS build, though it is less tested than Windows. **Close
  every app that grabs the USB device first** (Photos, Image Capture, Dropbox, Google Drive…),
  or they snatch the camera before the installer can.
- **Linux:** use the Python source (also installs the libraries, including `libusb`):
  ```bash
  git clone https://github.com/ma1co/Sony-PMCA-RE.git
  cd Sony-PMCA-RE && pip install -r requirements.txt
  ```
  Platform-specific driver/permission details follow ma1co's README; if `libusb` or device
  permissions misbehave, that README is the authority.

> **Honest note.** Exact driver and permission steps differ per OS and can change. When in
> doubt, follow ma1co's README: https://github.com/ma1co/Sony-PMCA-RE

### 2. Prepare the camera

1. Charge the battery and **insert the memory card**.
2. `Setup (the toolbox icon) → USB Connection → **Mass Storage**`.
3. Power on, plug in the USB cable (a6000 is **micro-USB**; use the wire in the 3-in-1 kit that
   actually transfers data).
4. The screen shows **USB Mode** — you are ready.

> **Honest note.** If you later follow Channel B, this setting changes to **MTP**. Keep it on
> Mass Storage for Channel A.

### 3. Install

**Graphical interface:** open `pmca-gui.exe` → **Install app from file** → select the APK → wait.

**Command line** (prefix with `sudo` on Linux):
```bash
python pmca-console.py install -f SonySOOCRecipes-<version>.apk
```

The camera will blank to black and switch modes a few times — **this is normal, do not press
anything.** After about a minute the computer prints `Task completed successfully`.

> **Honest note.** **Trust the computer's output.** The camera usually sits on an
> `Application Download / Connecting via USB...` screen that looks frozen. It is not.

### 4. Finish

Unplug, **power off and on again.** The app now lives at
`MENU → Application → Application List → Sony SOOC Recipes`.

---

## Verify it worked

1. Open `MENU → Application → Application List` and confirm **Sony SOOC Recipes** is listed.
2. Launch it. You land on the **single frosted bar** — name, brand, position and the
   parameter summary on one line. Turn the dial and the preview changes immediately; press
   **AEL** or **DISP** to cycle through the compact pill and the pure viewfinder.
3. To confirm a recipe is really written into the camera: press **Fn** for the list, **center**
   (or right) to open the settings editor, **center** again to store, then **power off and
   on.** The style now applies as the camera's default in **every** mode (P/A/S/M and movie),
   even with the app closed.

Badge you may see in the app:

| Badge | Meaning |
|---|---|
| a brand name — `PENTAX`, `KODAK`, `LEICA` … (宾得 / 柯达 / 徕卡 … in Chinese) | the group this look belongs to. That is all the badge says; the old `ACTIVE` / `PREVIEW` / `PROTECTED` status words are gone. |

One consequence worth knowing: the app no longer tells you on screen whether the camera's
setting storage is write-protected. If a write looks like it did not stick, that is still the
first thing to check — install [OpenMemories-Tweak](https://github.com/ma1co/OpenMemories-Tweak)
and turn off *Backup protection*.

---

## Channel B: Wi-Fi ADB

**Only use this after Channel A works and you need to reinstall repeatedly.** It is the
developer fast lane, not something an end user needs.

> **Honest note.** While ADB is on, any machine on the same LAN can run `adb` commands against
> your camera. Turn it on only on a trusted network and turn it off the moment you are done —
> see the Security note in [CHANNEL-COMPARISON.md](CHANNEL-COMPARISON.md).

### 1. Install OpenMemories:Tweak via Channel A first

Set the camera USB mode to **MTP** (not Mass Storage), connect, open `pmca-gui`:

1. Go to the **Install app** tab.
2. Pick **OpenMemories: Tweak** from the list.
3. Click **Install selected app**.

No firmware update or service mode needed.

### 2. Enable ADB on the camera

1. Safely disconnect USB, open **OpenMemories: Tweak** from
   `MENU → Application → Application List`.
2. Connect the camera to a Wi-Fi access point first.
3. In Tweak's **Developer** page, enable **Enable Wifi** and **Enable ADB**, and **note the IP
   shown**.
4. Put the computer on the same LAN; lengthen the camera's sleep timer.

> **Honest note.** This app needs only ADB. You do **not** need Telnet, setting protection
> off, region change, record-limit removal, or firmware modification.

### 3. Install over ADB

```bash
adb connect CAMERA_IP:5555      # replace with the camera's shown address, keep :5555
adb devices                     # the target should show as "device"
adb -s CAMERA_IP:5555 install -r SonySOOCRecipes-<version>.apk
```

The repository also ships a helper: `tools/install-wifi.sh <apk> <camera-ip>` — it connects,
checks readiness, installs, and reminds you to shut ADB down afterward.

### 4. Finish

```bash
adb disconnect CAMERA_IP:5555
```

**Then go back into Tweak and turn ADB off.** `adb disconnect` only drops the computer's side;
the daemon on the camera keeps running until you disable it in Tweak.

---

## Updating and uninstalling

- **Update over USB (Channel A):** just run the install again.
- **Update over ADB (Channel B):** `adb install -r` is near-instant.
- **Signature warning (important):** an APK signed with a *different* key cannot overwrite an
  existing install. The packs the installer ships share one key, so they upgrade over one another
  cleanly — but anything installed from an older, differently-signed build cannot be replaced.
  If you see `INSTALL_FAILED_UPDATE_INCOMPATIBLE`, **uninstall the same-package-name app first**
  (see *Uninstall* below; uninstalling clears the app's stored settings), then reinstall.
- **Uninstall:** the camera's own menu, not the installer.
  `MENU → Application → Application Management → Manage and Remove` → pick the entry → remove.
  On some bodies `Application Management` sits one level deeper, under `Application List`, and
  the label is localised (`Manage and Remove` / 管理与移除). Leave the app first. This clears
  the app's stored settings.

<p align="center">
  <img src="assets/hardware/01-a7sii-application-list.jpg" width="330" alt="The Application List on an A7S II, with Application Management as an entry in the list">
  <br><sub>What it looks like on an α7S II: <b>Application Management</b> (应用程序管理) is an
  entry <i>in</i> the Application List, not behind another submenu on this body. That is the one
  to open. A photograph of the real screen, not a mockup. Nine packs installed side by side on one body — that is what the different package names buy you, and why you never have to carry all of them.</sub>
</p>

> **Honest note — the tool that installed it cannot remove it.** Sony-PMCA-RE has **no uninstall
> command**. Its complete command set is `info`, `install`, `market`, `apk2spk`, `spk2apk`,
> `firmware`, `updatershell`, `serviceshell`, `guess_firmware`, `gps`, `stream`, `wifi`,
> `print_backup` — `install` is the only direction it goes. So if the camera's
> `Manage and Remove` item is missing or greyed out on your body, run the uninstall over ADB
> (Channel B) instead:
>
> ```bash
> adb connect CAMERA_IP:5555
> adb shell pm list packages | grep hairuoliu     # which packs are on the body
> adb uninstall com.hairuoliu.sonysoocrecipes     # or ...sonysoocrecipes.<brand>
> ```

> **Honest note.** Uninstalling the app does **not** automatically revert a recipe you already
> stored into the camera's settings. To go back to stock: in the app press TRASH + center,
> then power-cycle; or `Setup → Setting Reset → Camera Settings Reset`.

---

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| `This camera does not support apps`, right after `Switching to app install mode` | The camera **refused** the "switch to app-install mode" USB command — its firmware has no app channel. The installer only relays that refusal; the wording is its own. Note the preceding `Switching to app install mode` line is printed **before** the command, so it is not a success message, and this failure returns before the APK is transferred — the APK is never sent. | Nothing on the APK side to fix. Press `MENU` and look for `Application`. If it is missing, the body cannot run apps at all — see the model list and the 2012 boundary in `docs/FAQ.md`. If the model *is* in the supported column and it still errors (rare), check in order: `Setup → USB Connection` set to **Mass Storage** (not PC Remote) · camera Wi-Fi / Ctrl with Smartphone off · memory card inserted · quit anything that grabs the USB driver (Photos / Dropbox / Imaging Edge); if it still fails on Windows, install the libusb-win32 driver with Zadig and rerun `pmca-console install -d libusb -f <your.apk>`. |
| `No devices found` | USB not in **Mass Storage**, no card, camera off, or wrong cable/port | Set Mass Storage, insert card, power on to **USB Mode**, try another cable/port |
| Driver won't install (Windows) | Missing/blocked USB driver | Follow ma1co's README driver steps: https://github.com/ma1co/Sony-PMCA-RE |
| Stuck at `Waiting for camera to switch...` | Mid-handshake glitch | Unplug, power cycle the camera, reconnect, rerun |
| Badge shows `PROTECTED` | Setting storage write-protected | Install OpenMemories-Tweak, turn off *Backup protection*, retry |
| Installed but can't find the app | Looking in wrong menu | It is at `MENU → Application → Application List → Sony SOOC Recipes` |
| App won't open / `no live preview: ...` | Another program holds the camera | Quit Photos/Image Capture/etc., reopen the app |
| Stored a recipe but no effect | Camera hasn't re-read settings | **Power off and on** |
| Garbled text `Â·` | A build from before the text encoding was fixed | Reinstall from the current installer |
| `adb: offline` / timeout / no device | Camera slept, IP changed, not same Wi-Fi, ADB off, or guest-network/VPN isolation | `adb disconnect` then reconnect; check guest isolation, VPN, and terminal local-network permission |
| MTP works but `adb` can't find it | MTP and Wi-Fi ADB are **two different connections** | Enable ADB per Channel B step 2 |
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` | Different signing key | Same key rebuild, or uninstall the same-package app first (clears settings) |
| RAW not affected by effect | Picture Effect recipes (marked **PE**) apply only to **JPEG** | Use JPEG quality; RAW / RAW+JPEG silently drops the effect |
| Saturation slider "drops a notch" when touched | Some recipes push saturation beyond the menu range (±3) | Menu shows the closest value; re-store from the app to keep the extra punch |

---

## FAQ

**Will this brick my camera?**
No. The app writes settings through Sony's official app channel; it does not touch firmware or
bootloader.

**Does it modify the firmware?**
No. Nothing in this process flashes or alters firmware. The signed-firmware bodies in the
"Does not" column simply cannot receive apps at all.

**Is it still there after a factory reset?**
A recipe you stored lives in the camera's settings. `Setup → Setting Reset → Camera Settings
Reset` clears it; a full initialization clears it too. The app itself is removed by
uninstalling.

**Does it affect RAW files?**
Picture Effect class recipes (marked **PE** in the app) only take effect in **JPEG** output; on
RAW or RAW+JPEG the camera silently ignores them. Other recipes (Creative Style, white balance,
DRO) are camera settings and apply regardless of file format.

**Is it reversible / safe for warranty?**
It uses the same channel Sony's store used and uninstalls cleanly. Whether it affects warranty
is a question for Sony; the install mechanism itself is non-destructive and removable.
