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
- **本项目做的改动**：新增了 72 款自写配方（最初的一批是 `gr-moriyama`、
  `kodak-vision2-500t`、`toy-camera-warm`、`toy-camera-cool`、`part-color-red`、
  `posterization-color`、`teal-mood`），全部标 `verified: false`；把配方表从手写 Java
  改为由 JSON 生成。**哪些是自写的、请以 `catalog/filters.json` 的 `verified` 字段为准
  （今天 164 款里有 72 款为 false）**——早先这里写的是「7 款」，那是配方库还很小时的
  遗留数字，catalog 涨上去之后没人重算。手写计数会腐烂，字段不会。

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
| 149 款可编译配方参数 | voxivoid（77）+ 本项目（72） | MIT | ✔ |
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

品牌包（`docs/BRAND-PACKS.md`）的启动图标，由 `tools/build_pack_icons.py` 生成进
`assets/app-icon-packs/<icon_set>/`。图标随 APK 一起发布，所以一旦用了带许可义务的素材，署名就必须随
APK 走 —— 它会进本文件（下方表格）与每个包的发布说明。**目前十个包中，九个用用户专门为本项目提供的商业产品照片 / 厂商官方渲染图，全部保留权利、未授予任何许可**；`cinema` 包为原创手绘图标，不基于任何第三方照片，同样无第三方权利、无署名义务。因此没有任何 CC BY 照片在发布之列、
也没有法定署名义务；风险由发布方承担。逐张的取舍与权利说明见 `assets/app-icon-packs/CREDITS.md`。

| 包 (`id`) | 品牌 | 图标描绘 | 作者 / 来源 | 许可 | 来源页 |
|---|---|---|---|---|---|
| `leica` | Leica | Leica M9 | sketch.vip（M9 产品渲染） | **保留全部权利**——用户提供，未授予许可 | sketch.vip M9 渲染图 |
| `fujifilm` | Fujifilm | X100VI | fujifilm-x.b-cdn.net（X100VI 产品缩略图，480×480） | **保留全部权利**——用户提供，未授予许可 | fujifilm-x.b-cdn.net X100VI 产品缩略图 |
| `filmstocks` | Fuji Film | Fujifilm 胶卷（三个胶卷罐并排） | 用户提供的产品图 | **保留全部权利**——用户提供，未授予许可 | 用户提供的产品图 |
| `ricoh` | Ricoh | Ricoh 相机（用户来图） | 用户提供的产品图 | **保留全部权利**——用户提供，未授予许可 | 用户提供的产品图 |
| `kodak` | Kodak | Gold 400 / 400 胶卷罐 | prophotosupply.com（Kodak Gold 400 产品照片） | **保留全部权利**——用户提供，未授予许可 | prophotosupply.com Kodak Gold 400 |
| `pentax` | Pentax | Pentax 相机（用户来图，自带透明底） | 用户提供的产品图 | **保留全部权利**——用户提供，未授予许可 | 用户提供的产品图 |
| `nichefilm` | Niche Film | CineStill 胶卷 + 复古胶片（CineStill film product shot） | 用户提供的产品图 | **保留全部权利**——用户提供，未授予许可 | 用户提供的产品图 |
| `hasselblad` | Hasselblad | X2D II 100C | cameraelectronic.com.au（官方 X2D II 100C 渲染，Shopify CDN） | **保留全部权利**——用户提供，未授予许可 | cameraelectronic.com.au 产品页（Shopify CDN） |
| `sony` | Sony | Sony 相机 | 用户提供的产品图 | **保留全部权利**——用户提供，未授予许可 | 用户提供的产品图 |
| `cinema` | Cinema LUT | 原创手绘图标（original drawn artwork） | 本项目原创 / original artwork by this project | **原创作品，无第三方权利**——不基于任何第三方照片 | n/a |

十个包全部有图标，**九张是用户提供的商业照片 / 厂商渲染图、一张（`cinema`）是原创手绘，均保留全部权利、未授予任何许可**，
因此**没有法定署名义务**（分销风险由发布方承担）。曾经用 Wikimedia Commons **CC BY 2.0** 照片的
`ricoh` 与 `pentax` 也已换成用户来图，本表格里不再有任何 CC BY 素材 —— 但这不等于可以松懈：下表与
`CREDITS.md` 必须逐张保持真实，一旦换回带许可义务的图，署名义务立刻恢复。

被否决过的一张：`File:Fujifilm X100-IMG 6097.jpg`（作者 Rama）是 **CC BY-SA 2.0 (fr)**，已下载并渲染
后被撤下 —— 图标是对照片的改编，而「相同方式共享」会从改编件波及到分发它的整个应用。已换成上表中
用户提供的 X100VI 产品缩略图。不要再启用它。

几点必须说清的边界：

- **`CC BY` 允许商用，但必须署名。** 不署名就商用违反许可。目前十张图标里**没有 CC BY 素材**，这条
  义务处于「空置」状态；将来若引入任何 `CC BY` 照片，署名必须随 APK 走 —— 本表格是一处，每个包的
  发布说明是另一处。同理，改用回 CC BY 素材时，被替换掉的那一行必须同步移除，不能留下幽灵署名。
- **`CC BY-SA` 被刻意排除。** 它的「相同方式共享」条款会波及整个 App，而不只是那张图标，所以品牌包
  图标一律不用 `CC BY-SA` 照片。
- **全量版默认图标（`assets/app-icon/`）是本仓库原创作**，由 `tools/build_app_icon.py` 从源照片生成，
  不依赖上述任何素材，无需此类署名。
- 品牌包图标**也抠掉了背景**，与全量版默认图标同样渲染为透明剪影（抠图用
  `tools/cut_camera_covers.py`，渲染用 `tools/build_pack_icons.py`），见 `docs/BRAND-PACKS.md` §7。
- 再分发这些包的人，自行承担对应的商标与署名风险（见 `docs/BRAND-PACKS.md` §8）。

---

## 六、界面字体（随 APK 分发）

主屏那套圆润字形是 **Quicksand**（Regular + Bold 两个字重），随 APK 一起分发，所以它的
许可与署名必须跟着 APK 走 —— 和品牌包图标是同一个道理。

| 项目 | 内容 |
|---|---|
| 字体 | Quicksand（Regular 400 / Bold 700） |
| 许可 | **SIL Open Font License 1.1**，OFL 允许自由再分发，包括打包进商业软件 |
| 许可全文 | 已随仓库分发：`assets/fonts/OFL-Quicksand.txt` |
| 版权 | Copyright 2011 The Quicksand Project Authors（<https://github.com/andrew-paglinawan/QuicksandFamily>），保留字体名 "Quicksand" |
| 取得来源 | Google Fonts 上游仓库 `ofl/quicksand/` |
| 分发的文件 | `assets/fonts/Quicksand-Regular.ttf`（79 KB）、`assets/fonts/Quicksand-Bold.ttf`（79 KB） |

**为什么必须打包字体，而不是在 XML 里指定**：本项目的 `minSdkVersion` 是 10
（Android 2.3.7）。Gingerbread 系统只带 Droid Sans 系列，**没有任何圆体可选**；
`android:fontFamily` 与 `res/font` 是 API 26 才有的东西，这里都用不了。所以字体以
原始资源（asset）形式打包，由 `tools/patch_ui.py` 在构建时拷进 `assets/fonts/` 并在
Java 里绑定到各个视图。上游的打包命令原本不带 `-A`，该脚本已同步修改 `build.sh` 与
`build.cmd`。

**OFL 对本仓库的影响**：OFL 不要求使用它的软件开源，也不禁止商用；它只要求（a）再分发
时附带许可全文 —— 已放进 `assets/fonts/OFL-Quicksand.txt`，且 `tools/patch_ui.py` 整目录拷贝
`assets/fonts/`，该文件会连字体一起进 APK；（b）不得单独出售字体本身
（我们不这么做）；（c）衍生字体不得再使用保留字体名（我们未修改字体文件）。
因此**本仓库整体仍是 MIT**，字体只是随附的一件 OFL 素材 —— 与第五节那些第三方图片同理，它随 APK
分发，所以许可义务必须与 APK 同行，而不是只留在本文件里。

**如果要换字体**：把另一套 **OFL 或 Apache-2.0** 的 `.ttf` 放进 `assets/fonts/`，改
`catalog/ui-theme.json` 里的 `font_regular` / `font_bold` 两个键即可，其余不用动。
同理请一并更新本节表格与许可文件 —— **不要用没有明确再分发许可的字体**。
