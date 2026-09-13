# Assets — 配图规范 / image conventions

Diagrams in this repository are SVG so they stay sharp, stay small, and do not depend on
any external host. Photographs are JPEG. Nothing here may be hotlinked from a third-party
image host — a README whose pictures rot is worse than a README with no pictures.

`tools/check_assets.py` fails the build when a document points at a file that is not here.

---

## Layout

```
docs/assets/
  architecture.svg        how the catalog becomes camera settings
  engines.svg             the two engines compared
  install-flow.svg        download → check → install → verify
  parameters.svg          what a look can be made of, and what it cannot
  samples/                before/after photographs        ← contributed
  install/                screenshots of the install flow  ← contributed
  README.md               this file
```

---

## Sample photographs

Two files per look, named so the pair is unmistakable:

```
samples/<recipe-id>--off.jpg     the same scene with the look NOT applied
samples/<recipe-id>--on.jpg      ...and applied
```

`<recipe-id>` must match an `id` in `catalog/filters.json` exactly — `kodak-gold-200`,
`classic-chrome`, `teal-mood`. `tools/check_assets.py` verifies this, so a typo becomes a
build failure instead of a mystery orphan file.

**What makes a pair worth publishing:**

- Same scene, same light, same focal length, same exposure, same white balance.
- The only difference between the two frames is the stored look.
- Shoot a subject with skin, foliage and something neutral — a grey card if you have one.
  Flat walls and sunsets both hide what a look actually does.

**Format:** JPEG, quality ~85, long edge 1600–2400 px. Big enough to judge colour, small
enough that cloning the repository stays pleasant. Under ~600 KB per file.

---

## Install screenshots

```
install/<NN>-<slug>.png
```

`01-connect-usb.png`, `02-pmca-re-install.png`, `03-app-on-camera.png`, … Numbered so a
reader can follow the order without being told. PNG for UI captures — JPEG smears text.

Crop to the window or screen that matters. A 4K desktop screenshot where the relevant
dialogue is 200 px wide is not a usable screenshot.

---

## Contributing images

1. Add the files following the naming above.
2. Run `python tools/check_assets.py` — it confirms every referenced image exists and
   every sample id resolves.
3. Reference them from the docs:

```markdown
<p align="center">
  <img src="assets/samples/kodak-gold-200--on.jpg" width="720" alt="Kodak Gold 200">
  <br><sub>Kodak Gold 200, applied. Same scene, same exposure.</sub>
</p>
```

4. Open a PR. Please only submit photographs you took, or that you have permission to
   publish.

---

## 中文说明（简体）

本目录只放**仓库自带**的图：示意图一律用 SVG（清晰、体积小、不依赖外部图床），
照片用 JPEG。**禁止外链图床**——图片会失效的 README 比没有图的 README 更糟。

- 示意图：`architecture.svg` / `engines.svg` / `install-flow.svg` / `parameters.svg`
- 实拍样张：`samples/<配方 id>--off.jpg` 和 `--on.jpg` 成对，id 必须与
  `catalog/filters.json` 里的 `id` 完全一致
- 安装截图：`install/<两位序号>-<英文短名>.png`，序号保证阅读顺序

成对样张的唯一要求是**两张之间只有配方不同**：同一场景、同一光线、同一曝光、
同一白平衡。拍带有肤色、植物和中性灰的画面最能说明问题。

`tools/check_assets.py` 会检查：文档引用的图是否都存在、样张 id 是否能在注册表里找到。
改完图记得跑一遍。
