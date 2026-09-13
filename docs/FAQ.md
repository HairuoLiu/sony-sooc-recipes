# FAQ: film recipes on your old Sony camera

<p align="center"><b>English</b> · <a href="FAQ.zh-CN.md">简体中文</a></p>

This is for the person holding an older Sony camera, tempted but a little nervous. Questions are written the way people actually ask them. Each answer gives the conclusion first, then the reason. Nothing here touches firmware or code — it is documentation only.

---

## Safety

### Will this brick my camera? Does it touch the firmware?

No, and no. The app writes ordinary camera settings through Sony's own PlayMemories Camera Apps (PMCA) channel — the same door Sony's app store used to use. It does not flash, patch, or alter the firmware or bootloader. The bodies in the "not supported" list simply cannot receive apps at all; that is a firmware signature lock, not something this project fights.

> **Honest note.** "No brick risk" means it does not modify firmware. It still writes into the camera's settings store, so treat it like any settings change — not like a firmware flash.

### I'm using something Sony never officially shipped for my camera. What about my warranty?

That is a question only Sony can answer for your region — we won't guess. What we can say: the install mechanism is the official app channel, it is non-destructive, and it uninstalls cleanly (the app leaves, and a stored recipe can be cleared). It is reversible, not a permanent modification.

> **Honest note.** Whether installing a third-party app affects warranty depends on local law and Sony policy. The technique itself leaves no firmware trace, but we make no warranty promise on Sony's behalf.

### What if the power dies or the cable unplugs halfway through?

Don't let it — charge the battery fully and use a data cable before you start. Because it writes settings (not firmware), a mid-install glitch will not brick the camera; at worst you get a half-installed app. If that happens, just run the USB install again from the computer — it picks up where it left off.

> **Honest note.** This is the one step where you should not walk away. The camera blanks to black and switches modes a few times; that is normal, not a freeze. Trust the computer's `Task completed successfully` message.

### Can I get everything back to factory stock? How?

Yes. There are two layers:

- **The recipe you stored:** in the app, press `TRASH` + center button, then power-cycle. Or from the camera, `Setup → Setting Reset → Camera Settings Reset`. Either way the style stops applying.
- **The app itself:** remove it from the camera's Application management. That clears the app's stored settings too.

So "back to stock" is always possible, with no special tools.

### Does it slow the camera down or drain the battery faster?

No. The recipe is just a set of values sitting in the camera's settings store — there is no background process and no extra computation while you shoot. The app only runs while you have it open to preview or store a recipe. Battery and speed are the same as before you installed anything.

---

## Will it work on my camera?

### How do I know if my camera is supported?

Press `MENU` and look for an **`Application`** entry. If it is there, your camera can receive apps and this works. If there is no `Application` menu, stop — no method in this repository can install anything on it.

| Has `MENU → Application` (supported) | Does not (unsupported) |
|---|---|
| a6000 · a6300 · a6500 · a5100 · a5000<br>a7 / a7R / a7S / a7 II / a7R II / a7S II<br>NEX-5R · NEX-5T · NEX-6<br>RX100 III / IV / V · RX10 II / III · RX1R II<br>HX60 / HX90 / HX400 · WX500<br>a68 · a77 II · a99 II | a6100 · a6400 · a6600 · a6700 · ZV-E10<br>a7 III and everything after · a9 series · a1 series<br>RX100 VA and after · RX10 IV · RX0 · HX99 · ZV-1 series |

> **Honest note.** "No `Application` menu" means you cannot install apps, full stop. Sony shut its own app store in 2021, and every body from late 2016 onward (a6500 and a99 II were the last two) ships signed firmware that rejects apps — not just this project, Sony itself cannot load apps onto them.

### Why won't it run on my a6400 / a7 III? Is there any workaround?

Those bodies have no `Application` menu — Sony removed the PMCA app channel and switched to signed firmware around late 2016. There is no software workaround; the channel literally does not exist on them. Reports of people running this on an a6400 are mistaken — that camera was never able to receive apps.

> **Honest note.** If a6400-style film looks are your goal, the only real path is a newer body with built-in profiles, or shoot flat and grade later. This repository cannot help those cameras.

### Do I need an internet connection? Do I need a computer?

You need a computer (Windows, macOS, or Linux) for the first install over USB, but the install itself is **fully offline** — the installer talks to the camera directly, no network involved. You do **not** need internet during installation. (You only need internet once, on the computer, to download the APK and the installer.)

### After installing, can I still use the camera normally? Does it affect video?

Yes, completely normally. A stored recipe applies as the camera's default look in **every** mode — P/A/S/M and movie — even with the app closed. It does not lock you out of any menu, and it does not change how the camera handles cards, focus, or playback.

> **Honest note.** The look applies to video too. If you later grade footage, remember the recipe is already "baked in" to the JPEG/8-bit output; shoot RAW if you want an unstyled image to grade.

---

## What do the recipes actually do?

### Are these recipes the same as real film?

No — they are **approximations** of a film look, not a copy of another company's color science. A 2014-era body cannot store Fujifilm or Kodak color science; it can only store what its settings store holds (Creative Style, saturation, contrast, sharpness, white balance, exposure compensation, DRO, Picture Effect, and one hidden Sony color matrix). We tune those to get close.

> **Honest note.** Think "a taste reminiscent of Portra," not "a Portra scan." The engine ceiling is real: a6000 has no Picture Profile menu and cannot store any tone curve, so everything is a reconstruction from available dials.

### Is this the same thing as Fujifilm film simulations?

No. Fujifilm bakes its simulations into the sensor pipeline; this project only writes menu settings into an old Sony. That is exactly why some things are impossible here: no color grain, no light leak, no vignette, no LUT files, no per-channel HSL, no true teal-orange split-toning, no local adjustments, no Log curves. Fujifilm's simulations live in hardware this camera does not have.

### Does it affect my RAW files?

It depends on the recipe. Picture Effect (PE) class recipes — marked **PE** in the app — apply only to **JPEG** output; on RAW or RAW+JPEG the camera silently ignores them. Other recipes (Creative Style, white balance, DRO) are ordinary camera settings and apply regardless of file format. So if your effect "disappeared" on RAW, it was a PE recipe.

> **Honest note.** Shoot JPEG (or RAW+JPEG) when you want a PE effect like Toy Camera, Part Color, or Posterization to show up.

### Why is there no grain?

Because the camera cannot do color grain, and its only grain source is the black-and-white `rough-mono` Picture Effect (`pe=7`). That gives a grainy B&W look, but there is no dial for colored grain. Anything claiming "film grain" on these bodies is leaning on high-ISO noise, not a grain texture.

### Why do some recipes say NOT VERIFIED?

Seven recipes in this catalog were written by the repository authors and have **not been tested on real hardware**: `gr-moriyama`, `kodak-vision2-500t`, Toy Camera (warm/cold), Part Color (red), Posterization, and Teal Mood. They show `NOT VERIFIED` in the app. The other 92 are matched value-for-value against the upstream project.

> **Honest note.** Try a NOT VERIFIED recipe on discardable footage before trusting it on something you cannot reshoot. They are approximations built inside the engine's limits, not broken — just unconfirmed on a real body.

### Can I tweak a recipe myself? Can I get back to the recipe afterward?

Yes to both. A recipe is just a bundle of menu values, so you can change any of it in the camera's own menus — saturation, white balance, Creative Style, and so on. The app also gives you a factory backup/restore, so you can reset a recipe you hand-edited back to its shipped values. You are never locked in.

> **Honest note.** One quirk: when `pe` (Picture Effect) is not `off`, the camera **ignores Creative Style**. That is the engine's normal behavior, not a bug — so a PE recipe and a Creative Style recipe are two separate families you cannot stack.

---

## Using it day to day

### Do I have to keep the app open every time I shoot?

No. You open the app once to preview and store a recipe; after that it lives in the camera's settings and applies even with the app closed. You only reopen the app when you want to switch looks or change values.

### Can I install several recipes at once? Is switching easy?

You install the app once, and it carries all 99 recipes. You store **one** recipe into the camera at a time (press the center button), and storing a new one overwrites the previous. Switching is quick: open the app, turn the dial to the look you want, press center, done — no reinstall needed.

> **Honest note.** Only one recipe is active at a time; there is no "layer several looks." If you want A for portraits and B for landscapes, you switch between them in the app as you shoot.

### What should I watch out for when updating to a new version?

The APK is built by CI with a **fresh, throwaway signing key every time** (there is no keystore). An APK signed with a different key **cannot overwrite** an existing install — you will see `INSTALL_FAILED_UPDATE_INCOMPATIBLE`. Fix: uninstall the same-package app in the camera's app management first, then install the new one (uninstalling clears the app's stored settings, so re-store your recipe afterward).

> **Honest note.** The version number shown inside the app is the **upstream** version, not this repository's tag. Trust the GitHub release tag, not the in-app number.

### Is Wi-Fi ADB safe?

It is safe **only on a trusted network, used briefly**. Opening ADB (via OpenMemories:Tweak) makes the camera listen for debug commands on LAN port `5555` — any machine on that network can then run `adb` against your camera, including uninstalling apps or reading the memory card. Use it on your own Wi-Fi, and when you are done, `adb disconnect` **and** turn ADB off inside Tweak. `adb disconnect` alone only drops your computer's side; the camera's daemon keeps running until you disable it.

> **Honest note.** The first install always goes over USB anyway — Tweak itself is installed by USB. ADB is a convenience for repeated reinstalls, not a requirement. On a public or guest network, stay on USB.

---

## Where do I start if I just want a certain look?

Open the filter browser at [`catalog/index.html`](catalog/index.html) — a single-file, no-dependency page that lists all 99 recipes with their groups and tones. Filter by brand (Kodak, Fujifilm, Ricoh GR, Ilford…), by color vs. mono, or by engine, then find the recipe whose name matches the film you have in mind.

If you are unsure, start from the look you already like: a warm everyday negative? Try `kodak-portra-400` or `fuji-superia-400`. A moody cinematic night? Try `cinestill-800t`. A clean black-and-white? Try `ilford-hp5` or `acros`. Pick one, install it, shoot a roll, and switch from there — the whole point is that trying the next look costs you nothing but a dial turn.
