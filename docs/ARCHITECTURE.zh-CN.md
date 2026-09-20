# 架构：为什么这样设计，以及它能做到什么、做不到什么

<p align="center"><a href="ARCHITECTURE.md">English</a> · <b>简体中文</b></p>

> **实话实说。** 这个项目不复制别家的色彩科学。它把「胶片风格配方」汇总成一份数据，编译成
> APK，装进 2016 年末以前的索尼微单（a6000 / a6300 / a6500 / a5100 / NEX / RX100 III–V / a7 II）。
> 下面每一个风格，都是**只用相机存得下来的设置拼出来的近似**——不是某个 LUT、Log 曲线或别家
> 色彩矩阵的复制品。在下结论之前，请先读 [§5](#5-引擎天花板这台相机做不到什么)。

本文解释这套架构：两套引擎、一条配方到底往相机里写了什么、硬件的硬天花板、数据模型、CI 关卡，
以及**为什么**项目是这个形状。如果你只是想加一款滤镜，去读 [`docs/ADDING-FILTERS.md`](ADDING-FILTERS.md)。

---

## 1. 这段在干嘛

这一节帮你定位。文件其余部分是参考：读完你应该明白，一份 JSON 怎么变成十年前那块传感器上的
颜色，以及这条路的终点在哪。

本仓库共有 **155 款配方**，分 **14 组**、走 **两套引擎**：

- **140 款**会编译进 App（引擎 `recipe-lab`）：其中 **77 款**逐值抄自开源上游项目，**63 款**
  由本仓库自写（含相机模拟、胶片、品牌包与手机 App 风几个批次）。
- **15 款**是「只登记」的条目（引擎 `film-studio-matrix`）：只记名字，不编译、不写参数。

---

## 2. 全景：数据从注册表流到相机的设置存储区

这一节用一张图把整条路径讲完。唯一的真相来源是 `catalog/filters.json`，它下游的一切都从它生成。

<p align="center">
  <img src="assets/architecture.svg" width="760" alt="architecture">
  <br><sub>图：数据从注册表到相机设置存储区的路径</sub>
</p>

```
catalog/filters.json
        │
        │  tools/gen_recipes.py
        ▼
build/recipe-lab-sony-pmca/src/com/hairuoliu/sonysoocrecipes/Recipes.java
        │
        │  tools/build_apk.sh  →  上游 build.sh
        │  (JDK 17 + Android SDK build-tools 30.0.3 + platform API 28 + NDK r16b)
        ▼
SonySOOCRecipes-<tag>.apk          ──  签名密钥只在本机，永不入库
        │
        │  Sony-PMCA-RE (USB)   或   adb install -r (Wi-Fi)
        ▼
相机设置存储区  ──  关机重启后依然生效
```

**手改 `Recipes.java` 是错的。** 它随时可重新生成，且会被 CI 判为过期。要改配方，改的是
`catalog/filters.json`。

---

## 3. 两套引擎，两种完全不同的原理

这一节是最重要的一件事：**两个上游项目改的不是同一个东西**，不是同一种技巧的两个口味。

<p align="center">
  <img src="assets/engines.svg" width="760" alt="engines">
  <br><sub>图：写设置的引擎 vs. 改硬件矩阵的引擎</sub>
</p>

| | 上游项目 | 胶片工坊 / Film Studio |
|---|---|---|
| 作者 | [voxivoid](https://github.com/voxivoid/recipe-lab-sony-pmca) | [ukiki0718-netizen](https://github.com/ukiki0718-netizen/sony-a5100-film-studio) |
| 改什么 | **相机持久化设置存储区**：创意风格 + 饱和度/对比度/锐度、白平衡与微调、曝光补偿、DRO、图片效果，外加一个索尼从未在菜单公开的色彩矩阵开关 | 机内**图像处理管线**：3×3 硬件色彩矩阵 + 1024 点共同 Gamma 曲线 |
| 本质 | 等于「帮你飞快地在菜单里设好一堆值」 | 真正的逐像素色彩处理 |
| 生效范围 | 关机重启后依然是相机默认，**P/A/S/M 与录像全模式**，应用关着也生效 | 拍照与实验性录像，带 **30 / 50 / 70 / 100%** 四档强度 |
| 强度档位 | 无（一组固定值） | ✅ 四档 |
| 机型覆盖 | a6000 / a6500 / a5100 / a7 II 已实机验证（据 `catalog`）；覆盖全部 PMCA 机型 | **只有 a5100 固件 1.10** |
| 依赖 | 无额外依赖 | 需要一个**不随仓库分发**的基础 APK（bonyback1 的 Ricoh 模组，基于索尼「照片效果+」） |
| 许可 | **MIT** | **PolyForm Noncommercial 1.0.0**（非 OSI 开源，禁止商用）+ 富士/索尼权利独立保留 |
| 能否再分发 | ✅ 可以 | ❌ 不能 |

### 为什么本项目以「上游项目」为引擎

1. **许可干净**：MIT，可以自由 fork、再分发、发布 APK。
2. **覆盖面广**：一个 APK 覆盖全部 PMCA 机型，而不是绑死一台固件。
3. **可生成**：77 款配方就是 Java 数组里的 77 行，天生适合从数据生成。
4. **可反复安装**：不依赖任何需要单独获取的基础 APK，不存在「你自己去找个 base.apk」的法律灰区。

胶片工坊的路线更「硬核」——色彩矩阵是真处理——但它绑死一台固件、需要一个不分发的
基础 APK、且许可是非商用。所以本仓库把它作为**参考目录**收录（见 [§6](#6-数据模型一条配方长什么样)），
不作为引擎。

> **实话实说。** 那 15 款胶片工坊风格只登记「名字与取向」。它们的拟合参数一律不转录进本仓库——
> 不只是因为许可，更因为那些数值是为另一条管线（矩阵 + Gamma）拟合的，放进写设置的引擎里
> 根本不成立。`validate_catalog.py` 会在 `film-studio` 条目一旦带上 `recipe` 对象时直接报错。

---

## 4. 配方到底改了什么

这一节逐项列出 `recipe-lab` 配方写入的每一个字段，以及相机（或上游引擎）真正强制的合法范围。
这些范围直接来自 `tools/validate_catalog.py`。

| 字段 | 合法范围 | 作用 |
|---|---|---|
| `style` | `STD` `VIVID` `NEUTRAL` `PORTRAIT` `LANDSCAPE` `MONO` `CLEAR` `DEEP` `LIGHT` `SUNSET` `NIGHT` `AUTUMN` `SEPIA` | 创意风格（存下来的枚举） |
| `sat` `con` `sharp` | −16…+16 | 创意风格滑块。菜单只到 ±3；相机会接受更大值，但屏幕滑块会吸附到最近的菜单值，手碰一下就丢掉了额外的力度 |
| `matrix` | `0` \| `1` | `1` = 备用（PP3）色彩矩阵，约 +45% 色度并带蓝/绿串扰。只在 `VIVID` `CLEAR` `DEEP` `LIGHT` `SUNSET` `NIGHT` `AUTUMN` 上生效 |
| `wb.mode` | `AUTO` \| `K` | `AUTO` 时 `kelvin` 必须为 `0`；`K` 设定色温 |
| `wb.kelvin` | 2500…9900 | 色温（Kelvin，仅 `wb.mode = "K"` 时） |
| `wb.ab` `wb.gm` | −7…+7 | 白平衡微调：`ab` 琥珀(+)/蓝(−)，`gm` 绿(+)/品红(−) |
| `pe` | `0`…`13` | 图片效果（运行时索引）。**`pe != 0` 时相机会忽略创意风格并禁用 RAW——只用 JPEG** |
| `sub` | 视 `pe` 而定 | 图片效果子参数。`pe=0` 强制 `sub=0`。只有 `pe` ∈ {1,3,5,6} 有子参数（数量 5/2/3/4） |
| `ev` | −5…+5 | 曝光补偿，1/3 EV 步进（持久化） |
| `dro` | `0`…`6` | DRO：`0` 关 / `1`–`5` 档位 / `6` 自动（持久化） |

### 你必须记住的一条引擎行为

> **实话实说。** `pe != 0` 时，相机会**忽略创意风格**——于是 `sat` / `con` / `sharp` 和 `matrix`
> 虽然写进去了但没有可见效果，并且 RAW 会被静默丢弃。带 `pe` 的配方只能拍 JPEG。这是上游相机的
> 既有行为，不是本仓库的 bug；`validate_catalog.py` 遇到这种情况只给一条 `note`（不是 error）。

---

## 5. 引擎天花板：这台相机做不到什么

这一节故意不修饰。你最需要的是边界，不是好话。根子在硬件：a6000 **没有 Picture Profile 菜单**，
存不下任何色调曲线。一款配方只能用这台机器存得下来的东西拼。

**所有风格都是近似，不是复制品。** 具体而言，通过这些机型与这套引擎，以下都做不到：

- **Log 曲线**（S-Log、V-Log、Blackmagic Film、Cinelike D）——存不下色调曲线。
- **带色调的黑白**（硒调、蓝晒）——只有全局 `ab`/`gm`，无法针对影调。
- **索尼摄像机那条 *Cinematone* gamma**——固件里有，但 a6000 的相机层既不列出也不接受。
- **真实（彩色）颗粒**——设置存储区里没有叠加层。`pe=7`（粗颗粒黑白）只在黑白下伪造「颗粒感」。
- **漏光 / 真正的暗角叠加**——暗角只有走 `pe=1` 玩具相机才出现，而它会强制带自己的偏色；没有独立的漏光层。
- **LUT 文件**——相机完全不支持 LUT。
- **HSL 分通道**——只有一个全局饱和度滑块加一个全局 `ab`/`gm` 偏移。
- **真·青橙分色调**——只有单一全局 `ab`/`gm` 偏色；可以伪造青调（见 `teal-mood`），但做不出真正的双色调曲线。
- **局部处理**——这条引擎没有任何区域感知能力。
- **带图片效果或矩阵风格的 RAW**——RAW / RAW+JPEG 会静默丢弃它们，只用 JPEG。

> **实话实说。** 如果你想要的效果需要上面任何一项，这台相机 + 这套引擎给不了。这就是天花板，
> 直说以免你白拍一场才发现。

---

## 6. 数据模型：一条配方长什么样

这一节展示 `catalog/filters.json` 的形状，并给出三条真实条目（数值逐字取自文件，未编造）。

### 顶层字段

| 字段 | 说明 |
|---|---|
| `version` | 注册表格式版本 |
| `engines` | 两套引擎的说明、限制与许可 |
| `sources` | 每个上游的作者、许可、取得版本、可否再分发 |
| `style_constants` / `pe_constants` / `dro_constants` | 存下来的枚举（来自上游反向工程） |
| `groups` | 品牌分组，**顺序即 APK 内的分组顺序** |
| `filters` | 全部滤镜 |

### 单条滤镜

| 字段 | 必填 | 取值 | 说明 |
|---|---|---|---|
| `id` | ✔ | kebab-case，全表唯一 | 生成器与文档的引用键 |
| `name` | ✔ | 字符串 | 相机应用里显示的名字 |
| `name_zh` | | 字符串 | 中文名，仅供浏览器显示 |
| `group` | ✔ | `groups[].id` 之一 | 分组 |
| `engine` | ✔ | `recipe-lab` \| `film-studio-matrix` | 见 §3 |
| `source` | ✔ | `recipe-lab` \| `authored-here` \| `film-studio` | 来源 |
| `tone` | ✔ | `color` \| `mono` | 浏览器筛选用 |
| `verified` | ✔ | `true` \| `false` | **是否已在真机上验证** |
| `cross_ref` | | 另一个 `id` | 跨引擎的对应款 |
| `note` | | 字符串 | 浏览器里显示的备注 |
| `recipe` | recipe-lab 需要 | 对象 | 参数（见 §4） |
| `strengths` | film-studio 需要 | `[30,50,70,100]` | 四档强度 |

`film-studio-matrix` 条目**不允许**带 `recipe` 字段——`validate_catalog.py` 会直接报错。

### 真实例子——一条极简的 recipe-lab 配方（全零基线）

```json
{
  "id": "factory-st", "name": "FACTORY (ST)", "name_zh": "出厂标准",
  "group": "sony", "engine": "recipe-lab", "source": "recipe-lab",
  "tone": "color", "verified": true,
  "recipe": { "style": "STD", "sat": 0, "con": 0, "sharp": 0, "matrix": 0,
              "wb": { "mode": "AUTO", "kelvin": 0, "ab": 0, "gm": 0 },
              "pe": 0, "sub": 0, "ev": 0, "dro": 6 }
}
```

### 真实例子——白平衡微调 + 曝光补偿，仍走创意风格

```json
{
  "id": "kodak-gold-200", "name": "Kodak Gold 200", "name_zh": "柯达金 200",
  "group": "kodak", "engine": "recipe-lab", "source": "recipe-lab",
  "tone": "color", "verified": true,
  "recipe": { "style": "STD", "sat": 2, "con": 1, "sharp": 0, "matrix": 0,
              "wb": { "mode": "AUTO", "kelvin": 0, "ab": 3, "gm": 1 },
              "pe": 0, "sub": 0, "ev": 1, "dro": 6 }
}
```

### 真实例子——开启矩阵开关 + 跨引擎对应款

```json
{
  "id": "velvia", "name": "Velvia", "group": "fuji-sim",
  "engine": "recipe-lab", "source": "recipe-lab", "tone": "color",
  "verified": true, "cross_ref": "fs-velvia",
  "recipe": { "style": "VIVID", "sat": 5, "con": 1, "sharp": 0, "matrix": 1,
              "wb": { "mode": "AUTO", "kelvin": 0, "ab": 0, "gm": 0 },
              "pe": 0, "sub": 0, "ev": 0, "dro": 6 }
}
```

### 真实例子——一条 film-studio-matrix 条目（只登记名字，无参数）

```json
{
  "id": "fs-provia", "name": "PROVIA", "group": "fuji-sim",
  "engine": "film-studio-matrix", "source": "film-studio", "tone": "color",
  "verified": true, "cross_ref": "provia",
  "strengths": [30, 50, 70, 100],
  "note": "富士 GFX ETERNA 55 v1.10 LUT 拟合的 3x3 矩阵 + 1024 点 Gamma。100% 保留上游参数。"
}
```

### 分组顺序是有约束的

`recipe-lab` 条目**必须按 `groups` 声明的顺序连续排列**——生成器据此产出
`GROUP_START` / `GROUP_COUNT` 静态块，断了就直接报错。`film-studio-matrix` 条目可以和同品牌的
`recipe-lab` 条目交错（它们不参与编译），反而让浏览器里每个品牌更集中。

---

## 7. 管道与关卡：从改一个数字到发布 APK

这一节把一次改动从 `filters.json` 追到签名 APK，并点名每一道能拦下它的关卡。共 **8 道 CI 关卡**，
外加发布构建。

| # | 关卡 | 脚本 | 拦住什么 |
|---|---|---|---|
| 1 | 注册表合法 | `validate_catalog.py` | 枚举值写错、数值越界、分组连续性断裂、许可声明不诚实、`film-studio` 条目带参数 |
| 1b | 自写配方用例 | `tests/test_catalog.py` | `authored-here` 的配方在 `tests/cases.json` 里没有钉死值，或值与用例漂移。`TestAuthoredHaveCases` 规定自写条目没 case 就跑不过 |
| 1c | UI 主题（`run UI theme test cases`） | `tests/test_ui_theme.py` | 磨砂双栏主屏：布局保留 `MainActivity` 绑定的每个 view id、每个引用的 drawable / string 都能解析、每个颜色都是 `#AARRGGBB`。可见性值写错会让 aapt 无法 inflate、应用启动即崩。编号取 1c 而非 2，因为它和 1、1b 是同类：都是对受版本控制的输入做的廉价静态检查、跑在同一个 job 里；而关卡 2 已经是 Recipes.java 那一步 |
| 3 | 保真 | `check_fidelity.py` | **某个配方数值被悄悄改动**，导致 APK 拍出来的颜色和上游不一致。逐值比对，并展开成完整 15 值形式，使简写拼写一致 |
| 4 | 浏览器 | `gen_browser.py` + `tests/smoke_browser.js` | 单文件浏览器里的拼写错误会发出空白页；`catalog/index.html` 过期也会失败 |
| 5 | README 计数 | `check_readme_counts.py` | README 的配方计数与注册表对不上 |
| 6 | Assets | `check_assets.py` | 文档里指向不存在的图片；从第三方主机外链图片（状态徽章除外——徽章是按请求实时生成的，固化其中一个会冻结构建状态）；`docs/assets/samples/` 下文件名不按 `<recipe-id>--off.jpg` / `--on.jpg` 命名、且该 id 存在于注册表 |
| 7 | 双语文档 | `check_docs.py` | 英文文档没有 `.zh-CN.md` 双生、也没在 `ENGLISH_ONLY` 里说明原因；双生的英文原文已消失；共用的 `docs/assets/*.svg` 里写进了中文（图是两种语言共用的）；图里画着的数字已被注册表超过。它无法判断译文是否**忠实**，也没假装能 |

顺序：

1. 你改 `catalog/filters.json`（绝不要改 `Recipes.java`）。
2. 每次 push/PR 到 `catalog/`、`tools/`、`tests/` 时跑关卡 1 + 1b。「UI 主题」关卡
   （`tests/test_ui_theme.py`，CI 里叫 `run UI theme test cases`）同属这套本地关卡家族，看守主屏
   布局（见 [§10](#10-主屏是重放补丁而不是提交的源码)）。
3. 关卡 3 拉取上游 `Recipes.java`，逐值比对保真。
4. `gen_recipes.py` 重新生成 `Recipes.java`，产物作为 artifact 上传供检视。
5. 关卡 4 重新生成并对浏览器做冒烟测试。
6. 关卡 5 核对 README 计数。
7. 关卡 6 扫描所有 README 与 `docs/*.md` 里的图片引用，遇到指向不存在的文件、第三方外链
   （状态徽章除外）、或 `docs/assets/samples/` 下命名错误的样例时失败。
8. 关卡 7 检查双语文档集：每份文档要么有 `.zh-CN.md` 双生、要么在 `ENGLISH_ONLY` 里说明原因；
   共用的 `docs/assets/*.svg` 图里不得出现译文（图是两种语言共用的）；图里画着的数字仍与注册表一致。
9. 推送 `v*` tag 时，`release.yml` 重跑关卡 1+1b，然后按**固定的 `UPSTREAM_SHA`** 克隆上游、
   改包名、应用品牌包变换与启动图标、重放磨砂主屏（`patch_ui.py`）、重新生成、用 JDK 17 +
   build-tools 30.0.3 + NDK r16b 构建，并把 `SonySOOCRecipes-<tag>.apk` 与 SHA-256 校验和挂到
   GitHub Release。

> **实话实说。** 上游版本固定在**两处**——`catalog/filters.json`（`sources.recipe-lab.fetched_rev`）
> 和 `release.yml`（`UPSTREAM_SHA`）——而且 `test_catalog.py`（`TestPinnedUpstream`）会在两处不一致时
> 失败。一个 tag 必须构建在它被验证过的那个上游版本上；不固定版本，下个月可能构建出不同的 APK。
>
> **构建步骤本身**也因为同样的理由被写了两遍，并带着同样的风险：一遍在 `tools/build_apk.sh`，一遍在
> `release.yml`。同文件里的 `TestBuildPipelinesAgree` 把两者钉在一起，而这个测试不是假想的——它之所以
> 存在，是因为这种漂移已经发生过：`release.yml` 漏了 `patch_ui.py` 这一步，于是 **v0.7.0 的 APK 装的是
> 上游的主屏**，而本文件、CHANGELOG 和 README 都写着磨砂双栏主屏已经发布。当时所有关卡都是绿的：主题的
> 工具本身都被测过，但没有任何东西测过「发布构建到底跑没跑它们」。

**品牌包。** 同一条管道也按品牌各构建一份 App。`catalog/packs.json` 列出各包，`release.yml` 在
运行时从这份文件推导构建矩阵 —— 每个包一项加全量版一项，每项各自全新克隆上游并依次跑 `apply_pack.py`、
`patch_ui.py`、`gen_recipes.py --pack <id>`。一个包与全量版的区别只在包名、`app_name` 与启动图标；
*为什么*见 [docs/BRAND-PACKS.zh-CN.md](BRAND-PACKS.zh-CN.md)。关卡 6（`check_assets.py`）现在也覆盖
`assets/app-icon/` 与每个 `assets/app-icon-packs/<icon_set>/`，所以缺一个密度或一套孤儿图标集会
让构建失败。

---

## 8. 仓库布局

这一节把目录树列出来，方便对应上面的路径。

```
sony-sooc-recipes/
├── assets/app-icon/          启动图标集——透明 RGBA，4 个密度 + 512 px 主图
├── assets/app-icon-packs/    各品牌包的启动图标集，每个 icon_set 一个目录
├── catalog/
│   ├── filters.json          ★ 唯一事实来源。所有配方都登记在这里
│   ├── packs.json             品牌包定义（id、app_name、groups、icon_set）+ unassigned_groups
│   ├── index.html            可浏览的滤镜浏览器（单文件，无依赖）
│   └── README.md             字段说明
├── docs/
│   ├── INSTALL.md                  双通道安装
│   ├── INSTALL.zh-CN.md            中文安装说明
│   ├── ARCHITECTURE.md             英文版
│   ├── ARCHITECTURE.zh-CN.md       中文版（本文件）
│   ├── BRAND-PACKS.md              品牌包——为什么、怎么做、商标、图标
│   ├── BRAND-PACKS.zh-CN.md        品牌包中文版
│   ├── ADDING-FILTERS.md           加滤镜的完整流程
│   ├── ADDING-FILTERS.zh-CN.md     中文版
│   ├── FAQ.md                      常见问题
│   ├── FAQ.zh-CN.md                中文常见问题
│   ├── CHANNEL-COMPARISON.md       USB vs Wi-Fi ADB，含结论
│   ├── MAPPING-RECIPES.md          把想要的风格映射到相机可复现的设置
│   ├── LUT-TO-SETTINGS.md          一个 .cube 怎么变成配方，以及过程中丢了什么
│   └── assets/                     配图 + README（architecture.svg、engines.svg、parameters.svg、install-flow.svg）
├── tools/
│   ├── validate_catalog.py   校验注册表（CI 关卡 1）
│   ├── cataloglib.py         共享的 catalog/packs 读取：计数与 load_pack 各只有一份
│   ├── gen_recipes.py        注册表 → Recipes.java（CI 关卡 2 步骤）；--pack 收窄到单个品牌
│   ├── check_fidelity.py     与上游逐值比对（CI 关卡 3）
│   ├── gen_browser.py        生成浏览器（CI 关卡 4）
│   ├── check_readme_counts.py 核对 README 计数（CI 关卡 5）
│   ├── check_assets.py       文档图片 / 资源引用 + 图标集关卡（CI 关卡 6）
│   ├── check_docs.py         双生覆盖、共用图、图内计数（CI 关卡 7）
│   ├── install-wifi.sh       Wi-Fi ADB 安装把手
│   ├── apply_pack.py         为一个品牌包改写包名与 App 名
│   ├── patch_ui.py           把磨砂双栏主屏重放到上游 checkout（在 apply_pack 之后、gen_recipes 之前）；给上游 aapt 调用补 `-A assets`
│   ├── preview_ui.py         渲染重放后的主屏，让你不用相机也能看到
│   ├── build_app_icon.py     按源照片重新生成全量版启动图标集
│   └── build_apk.sh          调上游 build.sh；--pack / --all-packs 构建品牌包
├── tests/
│   ├── test_catalog.py       33 条用例 + 不变量（CI 关卡 1b）
│   ├── test_packs.py         包转换、发布矩阵与子集用例（CI + release）
│   ├── test_gates.py         自测：给每道关卡喂坏输入，断言失败
│   ├── test_ui_theme.py      磨砂双栏主屏：view id、drawable / string、#AARRGGBB 颜色（25 个用例）
│   ├── cases.json            自写配方的钉死值
│   └── smoke_browser.js      浏览器冒烟测试（CI 关卡 4）
├── .github/workflows/
│   ├── ci.yml                全部门关，按 job 拆分
│   └── release.yml           推 tag 自动构建 APK 挂 Release
├── LICENSE                   MIT（本仓库代码）
└── NOTICE.md                 上游归属与许可边界
```

---

## 9. 为什么这样设计

这一节解释两个不显然的决策：单一事实来源，以及**不入库**的生成物。

**单一事实来源。** 配方过去总丢，因为大家手改上游 fork 里的 `Recipes.java`。让 `catalog/filters.json`
成为唯一可以定义一款配方的地方，意味着只有一份东西要改、要审、要信。生成器是 `Recipes.java`
**唯一的写手**。

**生成物不入库。** `Recipes.java` 和 APK 都是构建产物。提交它们会让它们与注册表漂移——而 CI 的
关卡 1b / 关卡 3 正是为了抓这种漂移而存在。生成的 Java 在 CI（以及本地按需）产出并作为 artifact
上传；APK 只由 `release.yml` 产出并挂到 GitHub Release，从不入库。签名密钥只在本机，永不入库。

**来源诚实是「测出来」的，不是「写出来」的。** MIT（上游项目，逐值抄录、由保真检查锁死）与
PolyForm Noncommercial（胶片工坊，只记名字）之间的那条线，是一个**测试**，不是一段话。模糊它
是本仓库唯一会变得不宜托管的错误，所以 `validate_catalog.py` 与 `test_catalog.py` 会为此让构建失败。

---

## 10. 主屏是重放补丁，而不是提交的源码

这一节解释为什么应用的磨砂双栏主屏不在源码树里，以及它每部分的成因。如果你只想改个颜色或开关，
去改 `catalog/ui-theme.json` 和 `assets/ui/main.xml`；下面写的都是「为什么」。

### 为什么是重放补丁

主屏是在构建时把补丁重放到上游 checkout 上得到的。它**不是**落在仓库里的源码。驱动它的是三份被
跟踪的输入：`catalog/ui-theme.json`（所有颜色，加三个屏幕开关）、`assets/ui/main.xml`（布局本体）和
`assets/fonts/`（随包字体，以及必须与字体同行的许可文本）。
`tools/patch_ui.py` 把这些重放到 checkout 上，`tools/preview_ui.py` 把重放结果渲染出来，让你
不用相机也能看到。

它是补丁、而不是在 `build/` 下手改的原因：`build/` 被 gitignore，而 `tools/build_apk.sh` 在每次
构建前把 checkout 重置到钉死的上游版本——`prepare_fork` 会跑 `git reset --hard` 和
`git clean -fdxq`。在 `build/` 下手改的东西活不过一次构建：下一次构建直接把它扔掉。所以真正算数的
只有被跟踪的输入，而布局的唯一写手是 `patch_ui.py`。这和 `filters.json` → `Recipes.java` 的「单一
事实来源」纪律一脉相承，只是又往下沉了一层。

`patch_ui.py` 在**两条管道**里都跑——本地是 `build_apk.sh`，打 tag 时是 `release.yml`，这正是
`TestBuildPipelinesAgree` 存在的意义——位置是 **`apply_pack` 之后、`gen_recipes` 之前**。这个顺序不是随便的：
布局用全限定类名引用应用的自定义 view，而 `apply_pack` 会按品牌包重命名那个类名、并从 checkout 自带的
`AndroidManifest.xml` 里填包名。一份在重命名之前就写死类名的布局，会匹配不上该包实际打出来的任何类。

### 磨砂是「模拟」的，不是模糊

`minSdkVersion 10`（Gingerbread）既没有 RenderScript（API 11+），也没有 RenderEffect（API 31+），
所以根本没有模糊可用。这里的「磨砂玻璃」条，是模糊出现之前的磨砂玻璃长什么样：一层约 0.90 透明度的
半透层、一道很淡的渐变高光、以及读起来像玻璃板的圆内角。这个高透明度是刻意的，不是装饰——条后面的
相机画面可能任意亮或暗，而只要透明度够高，合成结果就保持亮，于是深色文字在任意场景下都保住对比度。
把透明度调低，这个保证就不成立了：亮背景会透上来，文字没入其中。

### 字体是随包捆绑的，而 aapt 缺个 flag 会静默失败

字体是 **Quicksand**（SIL OFL 1.1），Regular + Bold，一对约 157 KB，作为 raw 资源放在
`assets/fonts/` 下，在 Java 里用 `Typeface.createFromAsset` 绑到各 view 上。API 10 不自带圆体系统
字体，`android:fontFamily` / `res/font` 又是 API 26 的东西，所以根本没有系统路线拿到圆体——字体必须
随 APK 走。后果：每个 APK 的体积大约就是这两个 `.ttf` 的大小。

关键的是，`patch_ui.py` 还会给上游 `build.sh` / `build.cmd` 的 aapt 调用补上 `-A assets`。上游根本
不发布 `assets/` 目录，而 aapt 遇到缺失的 assets 目录会**静默忽略**，而不是报错。万一这个 flag 丢了，
应用不会崩——它静默地渲染成 Droid Sans。这个静默回退是这里唯一一个全程没有任何报错信息的失败模式：
构建照样成功，关卡照样通过，只有拿屏幕和设计稿比对的人才会发现。这个 flag 是设计与「悄悄用错字体」
之间唯一的屏障。

许可文本走同一条路，理由更硬：`patch_ui.py` 把 `assets/fonts/` **整个目录**拷进去，所以
`OFL-Quicksand.txt` 会跟着它覆盖的字体一起进 APK。OFL 唯一的再分发条件就是许可全文必须随字体同行，
而留在仓库里的许可义务等于没履行——见 [NOTICE.md](../NOTICE.md)。它同时也是最不容易被发现的失败：
少一个文本文件，应用的任何表现都不会变。

### 三个开关，以及一个会要命的错值

主题文件里三个屏幕开关：`legend_visibility`（目前是 `"gone"`——芯片下方那排字形与标签；没有触摸屏，
导航靠相机的波轮和拨盘，所以那排是唯一提醒你 ENTER 和 AEL/DISP 是干嘛的屏幕提示）、`app_title_visibility`，
以及 `tag_visibility`（配方名后面的 CS / PE 小标：CS = Creative Style，相机自家的观感引擎，能进 RAW；
PE = Picture Effect，只在 JPEG 上落得下来）。一个写错的可见性值不是软失败——它会让 aapt 无法
**inflate** 布局，应用启动即崩。这个失败正是关卡要拦的。

### 看守这一切的关卡

`tests/test_ui_theme.py` 是唯一挡在「`catalog/ui-theme.json` / `assets/ui/` 里一个坏颜色或一个丢掉的
view id」与「一个在相机上无法 inflate 布局的 APK」之间的东西。因为 `build/` 在每次构建前被清空，所以
`run_all.py` 里没有任何别的东西会注意到主题坏掉。关卡强制四件事：布局保留 `MainActivity` 用 `findViewById`
绑定的每个 view id；布局引用的每个 drawable 和 string 都能解析；每个颜色都是 `#AARRGGBB`；以及每个 `@id/x`
引用都出现在同一文件里更早的 `@+id/x` 之后。（25 个用例。）
它像 catalog 与 assets 关卡一样在本地跑——CI 里作为名为 `run UI theme test cases` 的一步跑。

第四条规则是 aapt 的静态替身，而它之所以存在，是因为一次真实的失败：布局里有一个 view 指向 `@id/head`，
而拥有 `@+id/head` 的那条栏声明在它后面，aapt 又是按文档顺序单趟解析 id 的。它在上游构建的第一步——
生成 `R.java` 时——就失败了，也就是说这个主题根本编译不过；而只要没有任何一条会跑 `patch_ui.py` 的管道被
真正执行过，这件事就一直看不见。aapt 本身在这里跑不起来（要 3 GB 的 NDK r16b），所以规则改成在文本上检。

> **实话实说。** 这是唯一一个丢了也不会让 CI 变红的关卡：静默的 `-A assets` 回退意味着缺字体时发出去的是
> Droid Sans，全程无报错。布局和颜色的校验都是机械的；字体的 flag 才是得靠人工盯的那部分。
