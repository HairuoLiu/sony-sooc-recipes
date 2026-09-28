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
  install-flow.svg        download the installer → run it → one click
  parameters.svg          what a look can be made of, and what it cannot
  hardware/               photos of a real body running the app  ← contributed
  samples/                before/after photographs        ← contributed
  install/en/             screenshots of the Windows installer, English build
  install/zh-CN/          the same three screens, Chinese build
  README.md               this file
```

---

## Sample photographs

**There are none yet, and this is the contribution that would help most.** Every look in the
catalog is a row of numbers until somebody points a body at a scene and shows what came out.
If you have a supported body and a spare ten minutes, this page is waiting for you.

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
install/<lang>/<NN>-<slug>.png        lang is en or zh-CN
```

`en/01-connect-camera.png`, `en/02-choose-packs.png`, `en/03-installing.png`, and the same
three names under `zh-CN/`, … Numbered so a reader can follow the order without being told.
PNG for UI captures — JPEG smears text.

**The language is a directory, not a filename suffix.** The two sets are the *same* three
screens of the *same* installer, differing only in the language it renders; a suffix would
let one set drift out of step with the other without anyone noticing that `03` no longer
matches `03`. One directory per language keeps the pairing obvious, and it is what lets the
English README show English screens while the Chinese README shows Chinese ones.

Crop to the window or screen that matters. A 4K desktop screenshot where the relevant
dialogue is 200 px wide is not a usable screenshot.

---

## Hardware photographs

```
hardware/<NN>-<body>-<slug>.jpg
```

`01-a7sii-application-list.jpg`, `02-a7sii-application-list-more.jpg`, … Numbered for reading
order, with the **body in the name**, because the body is the point of the file: it is the
evidence that a *named* camera runs this app. A photo that does not say which body it is
proves only that some camera somewhere did.

These are photographs of hardware, not screen captures, so the rule differs from `install/`:

- **Crop to the model marking plus the screen.** Keep the mark. Without it the picture loses
  the one thing it is evidence for, and the screen alone cannot carry it.
- **Do not correct the perspective into a flat rectangle.** A phone photo of a hinged screen
  is at an angle, and straightening it turns a document into a rendering. The angle is part
  of what makes it a photograph of a real body.
- **Do not tidy a badge out of the crop.** If the screen says `PROTECTED`, the file ships
  saying `PROTECTED`, and the caption explains what that means. A screenshot cropped to show
  only the happy path is a false claim; showing the real state and naming it is not.

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
- 安装截图：`install/<语言>/<两位序号>-<英文短名>.png`，语言目录是 `en` 或 `zh-CN`，
  序号保证阅读顺序。**语言做成目录、不做文件名后缀**：两套是同一个安装器的同样三屏，
  只差渲染语言；用后缀的话某一天 `03` 和 `03` 不再对应也没人看得出来
- 真机照片：`hardware/<两位序号>-<机身>-<英文短名>.jpg`，**机身名必须进文件名**——
  这张照片的全部价值就是"某一台**指名**的机器跑起来了"，不写机身的照片只能证明"某台机器跑起来了"

成对样张的唯一要求是**两张之间只有配方不同**：同一场景、同一光线、同一曝光、
同一白平衡。拍带有肤色、植物和中性灰的画面最能说明问题。

**真机照片的规矩和安装截图不同**（它是"拍硬件"，不是"截屏"）：裁到**机身型号字样 + 屏幕**，
字样必须留着；**不要把斜拍的屏幕拉平成矩形**——拉平就把一张实拍变成了渲染图；
**也不要把徽标裁掉**——屏幕上写着 `PROTECTED` 就让它带着 `PROTECTED` 发出去，
在图注里说明它是什么意思。只留"顺利路径"的截图是假声明，展示真实状态并讲清楚不是。

`tools/check_assets.py` 会检查：文档引用的图是否都存在、样张 id 是否能在注册表里找到。
改完图记得跑一遍。
