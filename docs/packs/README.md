# APK catalog — what is inside every download

<p align="center"><b>English</b> · <a href="README.zh-CN.md">简体中文</a></p>

This folder documents **every APK the current tree publishes**: the all-in-one app
plus nine single-brand packs. A brand pack is *the same app with the same recipes*,
built once per brand with its own Android package name and its own launcher icon, so you
can install only the brand you actually use. See **[../BRAND-PACKS.md](../BRAND-PACKS.md)**
for what a pack is, why the package name must differ, and the one-camera-one-active-recipe
caveat before you install three packs expecting three cameras.

Every number below is computed from `catalog/filters.json` at catalog version **0.6.0**
(updated 2026-09-13) and is checked by CI. A *compiled recipe* is one the APK can actually
apply — it uses the settings-store engine (`recipe-lab`). The 15 `film-studio-matrix`
entries are recorded by name only (reference-only, non-redistributable) and appear in **no**
APK, so they are excluded from every count here.

## The downloads

| APK (app name) | Package name | Compiled recipes | Groups | Page |
|---|---|---:|---|---|
| **Sony SOOC Recipes** (all-in-one) | `com.hairuoliu.sonysoocrecipes` | **140** | 14 | [all-in-one](all-in-one.md) |
| Leica Style | `com.hairuoliu.sonysoocrecipes.leica` | **20** | 1 | [leica](leica.md) |
| Fujifilm Style | `com.hairuoliu.sonysoocrecipes.fujifilm` | **16** | 1 | [fujifilm](fujifilm.md) |
| Fuji Film Style | `com.hairuoliu.sonysoocrecipes.filmstocks` | **10** | 1 | [filmstocks](filmstocks.md) |
| Ricoh GR Style | `com.hairuoliu.sonysoocrecipes.ricoh` | **11** | 1 | [ricoh](ricoh.md) |
| Kodak Style | `com.hairuoliu.sonysoocrecipes.kodak` | **20** | 1 | [kodak](kodak.md) |
| Pentax Style | `com.hairuoliu.sonysoocrecipes.pentax` | **11** | 1 | [pentax](pentax.md) |
| Niche Film Style | `com.hairuoliu.sonysoocrecipes.nichefilm` | **26** | 3 | [nichefilm](nichefilm.md) |
| Hasselblad Style | `com.hairuoliu.sonysoocrecipes.hasselblad` | **4** | 1 | [hasselblad](hasselblad.md) |
| Sony Style | `com.hairuoliu.sonysoocrecipes.sony` | **8** | 1 | [sony](sony.md) |

**140 + 20 + 16 + 10 + 11 + 20 + 11 + 26 + 4 + 8 = 266** recipe-listings, but the underlying
catalog holds **155** filter entries (140 compiled + 15 reference-only). The sum exceeds
155 because a brand pack is a *view* over the shared catalog, not a copy — the 140 all-in-one
recipes are the same recipes you also find inside the individual packs, just presented in one
place instead of ten.

## How to read a sub-page

Each sub-page above states, for that APK:

- the exact **compiled recipe count** and the source group(s);
- a one-to-two-sentence description of **what each recipe is** — the film or Creative Style
  it aims at, whether it is colour or black-and-white, and its dominant character;
- the **key settings** behind each look (Creative Style, tone, and the notable saturation /
  contrast / sharpness / colour-matrix / picture-effect adjustments), drawn straight from the
  catalog so they match what the APK actually applies.

> **Honest note.** These are community-derived *approximations*, not copies of any brand's
> colour science. An a6000-class body has no Picture Profile menu and cannot store a tone
> curve, so every look is assembled from what the body can actually hold. The descriptions
> below say what each look is *going for*; they are not spec sheets.
