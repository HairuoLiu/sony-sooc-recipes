# NOTICE — 来源、归属与许可边界

本文件说明这个仓库里**每一部分材料的来源和权利状态**。它不是一个法律意见，
但它必须诚实——任何一处不诚实的声明，都会让下游使用者承担他们不知道的风险。

---

## 一、本仓库自己的代码

`tools/`、`docs/`、`catalog/index.html`、`catalog/filters.json` 的结构与文档部分、
CI 配置 —— 均为本项目原创，采用 **[MIT](LICENSE)**。

`catalog/filters.json` 里的**配方参数值**来自上游（见第二节），本项目对它们的贡献是
汇总、结构化、校验与生成。

---

## 二、逐项来源

### voxivoid/recipe-lab-sony-pmca — 77 款配方参数

- **许可**：MIT
- **可否再分发**：可以
- **取得版本**：`development` 分支，对应 v1.0.0（稳定版）/ v1.1.0-dev.8
- **本项目使用了什么**：
  - 77 款配方的参数值（`style` / `sat` / `con` / `sharp` / `matrix` / `wb` / `pe` / `ev` / `dro` / `sub`）
  - 设置存储区的地图（槽位 ID、图片配置文件开关行为、色彩矩阵测量结果）—— 仅作为
    文档与校验规则的依据，未复制代码
  - `Recipes.java` 的**类结构**（构造函数重载、常量表、`GROUP_START`/`GROUP_COUNT` 静态块）
    —— 生成的 `Recipes.java` 是它的直接派生物，因此保留 MIT 头与署名
- **作者**：André Domingues（[voxivoid](https://github.com/voxivoid)）
- **本项目做的改动**：新增 7 款配方（`gr-moriyama`、`kodak-vision2-500t`、
  `toy-camera-warm`、`toy-camera-cool`、`part-color-red`、`posterization-color`、
  `teal-mood`，全部标 `verified: false`）；把配方表从手写 Java 改为由 JSON 生成

### ukiki0718-netizen/sony-a5100-film-studio — 15 款风格的登记

- **许可**：PolyForm Noncommercial 1.0.0（**非 OSI 定义的开源许可，禁止商用**）
  + 上游理光参数为 Apache-2.0 + 富士 / 索尼权利独立保留
- **可否再分发**：**不可以**
- **取得版本**：`main` @ v0.2.0-alpha
- **本项目使用了什么**（**仅此而已**）：
  - 15 款风格的**名称、品牌归属与来源标注**
  - 四档强度（30/50/70/100%）这一**设计事实**的描述
  - 机型验证范围与许可披露**做法**上的借鉴
- **本项目明确没有做什么**：
  - **未转录任何拟合参数**（3×3 矩阵值、1024 点 Gamma 曲线，一个都没有）
  - **未分发任何 LUT 文件**
  - **未分发其基础 APK**
- **为什么连参数都不转录**：不只是许可问题。那批数值是为它自己的矩阵 / Gamma 管线
  拟合的，放进 Recipe Lab 这种「写相机设置」的引擎里在技术上根本不成立。
  `tools/validate_catalog.py` 里有硬性检查：`source: film-studio` 的条目一旦带上
  `recipe` 字段就直接报错。
- **那份非商用许可对本项目的影响**：本仓库不包含它的可编译内容，因此本仓库整体
  不受该许可约束。但**如果你打算商用**，请不要从它那里衍生任何东西。

### bonyback1/sony-pmca-ricoh-mod — 方法论参考

- **许可**：Apache-2.0 · **可否再分发**：可以
- **取得版本**：`7c565898562c73c5073c54dfc831c8c3df9c24cf`
- **本项目使用了什么**：仅作为「硬件色彩矩阵 + 共同 Gamma」这一路线的**方法论参考**。
  本项目走的是设置存储区路线，未使用其代码或参数。

### ma1co 的工具链

| 项目 | 许可 | 用途 |
|---|---|---|
| [Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE) | MIT | 应用安装通道、固件与设置转储 |
| [OpenMemories-Tweak](https://github.com/ma1co/OpenMemories-Tweak) | MIT | Wi-Fi ADB 与开发者开关 |
| [OpenMemories-Platform](https://github.com/ma1co/OpenMemories-Platform) | MIT | `Backup_read/write`、`CameraEx` —— 上游 Recipe Lab 通过 git submodule 引用 |
| [OpenMemories-Framework](https://github.com/ma1co/OpenMemories-Framework) | MIT | `ScalarInput` 按键码与相机 API 参考 |

这些都是**外部工具，不是本仓库的依赖**。用户自行获取。

**没有 ma1co 就没有这一切。** 他反向工程了索尼的 PlayMemories 平台并公开文档化、
给了宽松许可，还持续维护了 nex-hack 社区早年积累的研究。

### 第三方品牌名称

配方名称里的 Sony、Fujifilm、Kodak、Ricoh、Leica、Hasselblad、Canon、Nikon、
Panasonic、Olympus、Agfa、Ilford、Cinestill、Polaroid、Instax 等，均为**各自权利人
的商标**，此处仅用于描述该配方试图接近的**视觉风格**。

**本项目与上述任何公司无关联，未获其授权或背书。** 任何配方的参数值都是本社区
自行推导的近似值，不是官方色彩科学，也不来自官方 LUT 的再分发。

### 相机模拟与胶片批次（18 款 + 38 款）— 自写近似，参数不转录

18 款「相机调色模拟」（Pentax 11、哈苏 HNCS 3、徕卡机身 2、GR 电影调 2）
与 38 款胶片 / 徕卡包（胶片 24 + 徕卡包 14）均由本项目**自写**，参考是仓库所有者本人的
LUT 收藏与各厂商对机身色彩模式、胶片种类的**公开描述**。

- **参考 LUT 的权利状态**：相机模拟系列（哈苏 / 徕卡 M9 / M240 / 宾得 / 理光 GR）
  与徕卡缩写名合集为**仓库所有者本人以 Roger Wang 名义创作并发布**的作品，按其本人
  意愿可自由使用；Dehancer 胶片合集为商业插件的导出件，仅作各胶片种类的观感参考。
- **本项目怎么用的**：对参考 LUT 做的是**特征层面的分析**（反差、饱和增减、色偏方向、
  肤色行为），加上胶片 / 机身模式的公开描述，然后**自己写**相机能存下的参数值
  （风格 / 饱和 / 对比 / 锐度 / 白平衡微调 / 曝光 / DRO，约十个数）。
- **本项目明确没有做什么**：
  - **未转录、转码或拟合任何 LUT 的数值表**——相机设置区也存不下曲线，转录在技术上
    就不成立
  - **未分发任何 LUT 文件**
- 条目全部 `source: authored-here`、`verified: false`，命名描述其试图接近的观感。

### 富士 LUT 相关

胶片工坊的富士参考风格源自富士官方公开的 GFX ETERNA 55 v1.10 LUT（F-Log2 33Grid）。

本仓库**不分发**该 LUT 的任何原始文件、衍生文件或拟合参数表。仅在文档中标注了这一
参考关系的存在。

### Veres Deni Alex

上游 Recipe Lab 的许多配方（柯达、富士、Cinestill、Ilford、电影系）以
[veresdenialex.com](https://www.veresdenialex.com/) 的胶片模拟配方与并排参考帧为灵感与
基准。Recipe Lab 里的数值是为 a6000 能存下的东西**重新推导**的，不是他的配方。
本项目沿用这一关系，在此一并致谢。

### Liit（DAZZ PTE. LTD.）— 仅作为风格灵感，其数据未进入本仓库

- **性质**：闭源商业 App（iOS / macOS），免费 + Liit Pro 订阅。**不是开源项目**，
  公开渠道下不存在其源代码仓库。
- **可否再分发**：不可以。
- **本项目使用了什么**：
  - 其公开描述中提到的一个风格名「Kodak Vision 2」——只是一个名字。
  - 对「手机滤镜 App 常见观感」（暗角、局部色彩、偏色、扁平化）这一**审美类别**的
    归纳，用于判断本仓库缺什么。
- **本项目明确没有做什么**：
  - **未下载、解包、逆向或以任何方式提取其 IPA、LUT、曲线或配置文件**
  - **未复制其任何滤镜名称**（除上述公开描述里已写明的「Kodak Vision 2」外）
  - **未使用其任何数值**
- **为什么做不到，也不该做**：
  1. 法律上，它的滤镜是私有资产，提取并再分发会侵犯其权利。
  2. 技术上，即便拿到其 3D LUT 或曲线，a6000 的设置存储区也**无法承载**——没有 LUT
     通道、没有 Picture Profile、存不下曲线。拿来了也用不上。
- **因此本仓库的做法是**：以「手机 App 风」这一审美方向为参考，在相机能存的参数空间里
  **重新写**近似配方（`source: authored-here`、`verified: false`），并把它们归入
  App Look 组。它们是**本仓库的原创近似**，不是 Liit 滤镜的移植。

---

## 三、汇总

| 材料 | 来源 | 许可 | 本仓库是否分发其内容 |
|---|---|---|---|
| 本仓库代码与文档 | 原创 | MIT | ✔ |
| 140 款可编译配方参数 | voxivoid（77）+ 本项目（63） | MIT | ✔ |
| `Recipes.java` 类结构 | voxivoid | MIT | ✔（生成物，保留署名） |
| 15 款胶片工坊风格 | ukiki0718 | PolyForm NC | ✘ 仅名称与来源标注 |
| 理光模组方法论 | bonyback1 | Apache-2.0 | ✘ 仅参考 |
| 外部安装工具 | ma1co | MIT | ✘ 用户自行获取 |
| Liit（DAZZ PTE. LTD.） | 闭源商业 | 专有 | ✘ 仅风格方向启发，见上文 |
| 相机模拟 / 徕卡包 LUT | 仓库所有者本人（Roger Wang 笔名） | 本人授权 | ✘ 仅特征分析，无数值转录 |
| Dehancer 胶片导出件 | 商业插件 | 专有 | ✘ 仅胶片种类观感参考，见上文 |

---

## 四、反馈

发现权利问题请开 issue，标题以 `[rights]` 开头。会优先处理。

---

## 五、品牌包图标素材

品牌包（`docs/BRAND-PACKS.md`）的启动图标，是用 Wikimedia Commons 上各品牌最知名相机的**自由许可
照片**构建的，由 `tools/build_pack_icons.py` 生成进 `assets/app-icon-packs/<icon_set>/`。图标随 APK
一起发布，所以署名必须随 APK 走 —— 它进本文件（下方表格），也进每个包的发布说明。

| 包 (`id`) | 品牌 | 相机型号 | 作者 | 许可 | 来源页 |
|---|---|---|---|---|---|
| `fujifilm` | Fujifilm | FinePix X100 | frank mckenna（frankiefoto，经 Unsplash） | **CC0**（无需署名） | https://commons.wikimedia.org/wiki/File:Fujifilm_FinePix_X100_with_Fujinon_Asph_Super_EBC_23mm_F2_(Unsplash_JbTBJYOEc28).jpg |
| `hasselblad` | Hasselblad | 500C | Holger Ellgaard | 公有领域（PD-self，无需署名） | https://commons.wikimedia.org/wiki/File:Hasselblad_500C.jpg |
| `ilford` | Ilford | Sporti | Matthew Paul Argall | CC BY 4.0（https://creativecommons.org/licenses/by/4.0/） | https://commons.wikimedia.org/wiki/File:Ilford_Sporti_camera.jpg |
| `kodak` | Kodak | Instamatic 255-X | 2538O | **CC0**（无需署名） | https://commons.wikimedia.org/wiki/File:Kodak_Instamatic_255-X.jpg |
| `leica` | Leica | M3 | Hannes Grobe | CC BY 3.0（https://creativecommons.org/licenses/by/3.0/） | https://commons.wikimedia.org/wiki/File:Leica-m3_hg.JPG |
| `pentax` | Pentax | K1000 | Terry Presley | CC BY 2.0（https://creativecommons.org/licenses/by/2.0/） | https://commons.wikimedia.org/wiki/File:Pentax_K1000_(6301325288).jpg |
| `ricoh` | Ricoh | GR（2013） | Kārlis Dambrāns | CC BY 2.0（https://creativecommons.org/licenses/by/2.0/） | https://commons.wikimedia.org/wiki/File:Ricoh_GR_(16159018330).jpg |
| `sony` | Sony | α7（ILCE-7） | Henry Söderlund | CC BY 2.0（https://creativecommons.org/licenses/by/2.0/） | https://commons.wikimedia.org/wiki/File:Sony_A7,_A7R,_A7S_-_by_Henry_S%C3%B6derlund_(14700037048).jpg |

八个包全部有图标。其中 `fujifilm`、`hasselblad`、`kodak` 三张是 CC0 或公有领域，**没有署名义务**；
其余五张是 CC BY，署名是许可条件，必须随 APK 走。逐张的取舍说明见
`assets/app-icon-packs/CREDITS.md`。

被否决过的一张：`File:Fujifilm X100-IMG 6097.jpg`（作者 Rama）是 **CC BY-SA 2.0 (fr)**，已下载并渲染
后被撤下 —— 图标是对照片的改编，而「相同方式共享」会从改编件波及到分发它的整个应用。已换成上表中
的 CC0 照片。不要再启用它。

几点必须说清的边界：

- **`CC BY` 允许商用，但必须署名。** 不署名就商用违反许可。署名随 APK 走：本表格是一处，每个包的
  发布说明是另一处。
- **`CC BY-SA` 被刻意排除。** 它的「相同方式共享」条款会波及整个 App，而不只是那张图标，所以品牌包
  图标一律不用 `CC BY-SA` 照片。
- **全量版默认图标（`assets/app-icon/`）是本仓库原创作**，由 `tools/build_app_icon.py` 从源照片生成，
  不依赖上述任何素材，无需此类署名。
- 品牌包图标**没有**抠掉背景（全量版默认图标才抠），见 `docs/BRAND-PACKS.md` §7。
- 再分发这些包的人，自行承担对应的商标与署名风险（见 `docs/BRAND-PACKS.md` §8）。
