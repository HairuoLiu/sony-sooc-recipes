# 品牌包 —— 每个品牌一份小应用

<p align="center"><a href="BRAND-PACKS.md">English</a> · <b>简体中文</b></p>

> **先把实话放在最前面。** 品牌包**仍然是用同一份配方、同一个 App** —— 只是按品牌各构建
> 一次，各自带一张启动图标和各自的 Android 包名，好让你只装自己真正用的那个品牌。全量版
> App **不会消失**；它保持品牌中立，仍是默认下载。装三个包之前，请先读
> [§3](#3-设置存储是共享的--一台相机同一时间只能有一个配方生效)，别指望装三个包就得到三台相机 —— 你得不到。

本文说明品牌包是什么、为什么必须那样构建、它能装什么不能装什么、转换到底怎么发生、图标从哪来、
商标的实情，以及怎么构建或新增一个包。如果只是想装一个，看 [docs/INSTALL.zh-CN.md](INSTALL.zh-CN.md)。

---

## 1. 品牌包是什么 —— 以及它明确不是什么

品牌包是**同一份上游 checkout** 和**同一份 `catalog/filters.json`**，按品牌各构建一次，
每个带一个不同的 Android 包名，好让多个包能并存在相机上。没有 fork。全量版 App 和单个品牌包
之间，全部差异只有三样：

1. Android **包名** —— `com.hairuoliu.sonysoocrecipes` 变成 `com.hairuoliu.sonysoocrecipes.<id>`；
2. **`app_name`** 字符串（例如 `Leica Looks`）；
3. **启动图标** —— 每个包展示该品牌最知名的相机。

`tools/apply_pack.py` 在一个全新的、已经改过包名的 checkout 上做这个转换；
`tools/gen_recipes.py --pack <id>` 随后只把该包的组写进 `Recipes.java`。其余一切 —— 引擎、
原生库、设置存储区的映射 —— 与全量版 App **逐字节相同**。

**它明确不是一个 fork。** 没有独立分支，没有第二份 catalog，没有按品牌拷贝的配方。这些包只是
同一份代码、同一份 catalog 的**不同视图**。这正是设计的核心：事实来源只有一个，一个包只是它的
一份更窄的构建。如果你发现自己去改「某个包专属」的代码，那是理解错了 —— 改的是
`catalog/filters.json`，不是某个包。

---

## 2. 为什么包名必须不同（并存安装）

Android 用**包名**来识别一个已装应用，而不是用图标或显示名。两个共享同一包名的 APK 无法并存：
装第二个会被系统当作**对第一个的更新**，静默覆盖掉它。全量版已经占着
`com.hairuoliu.sonysoocrecipes`，所以一个用同名构建的 Leica 包会覆盖它，而一个用同名构建的
Fujifilm 包又会覆盖 Leica 包 —— 最后你只剩一个 App，且是最后装的那一个。

每个品牌的后缀（`...sonysoocrecipes.leica`、`...sonysoocrecipes.fujifilm` …）才让「只装你想要的
品牌」这句话有意义。包名不同，相机就把每个包当作独立应用，Leica、Kodak、Ricoh 三个包可以同装，
各自一张图标，互不相踩。没有它，整个品牌包的想法就塌回「一个已装 App」 —— 而这恰恰是要逃离的
「155 款配方，滚半天」的处境。

---

## 3. 设置存储是共享的 —— 一台相机同一时间只能有一个配方生效

**这是用户最容易搞错的一点，所以放在前面。**

相机的**设置存储区在包之间共享**。每个包保有自己的存储**快照** —— `getFilesDir()` 是按包隔离的，
所以一个包的快照文件不会覆盖另一个的 —— 但存储区本身是相机里一个物理实体，同一时间**只能有一个
配方在相机上生效**。

直说后果：

- 装三个包**不会**给你三台相机。它给你三个启动器，写的都是**同一个**设置存储区。
- 切换包**不会**切换配方。打开 Ricoh 包选了个风格，再打开 Leica 包，你会发现相机上还是 Ricoh
  那个风格 —— 因为 Leica 包读写的是同一个存储区。
- 一个包是对**浏览**的便利，不是对**配方**的隔离。它收窄你滚动的列表，但不隔离结果。

选「装哪个包」关乎**你点哪个图标、滚动哪一份配方子集**，而不是拥有几台独立的相机。如果你想要
早上 Leica、下午 Kodak，你两个都装，但切换生效配方还是老办法 —— 打开一个包、选个风格、关机重启。
发布说明里也写了同一句话，因为这是最容易混淆的一点。

---

## 4. 品牌包一览

今天共 9 个包，都从 catalog 构建。「**编译进的配方数**」是该包实际写进 `Recipes.java` 的数量 ——
扣掉属于另一套引擎（`film-studio-matrix`，仅登记）以及仅登记给其他品牌的条目之后。它**不等于**
该组的总条目数，数字偏小不是 bug（见下表下方的说明）。

| `id` | `app_name` | 来源组 | 编译进的配方数 |
|---|---|---|---|
| `leica` | Leica Looks | `leica` | 20 |
| `fujifilm` | Fujifilm Looks | `fuji-sim` | 16 |
| `filmstocks` | Fuji Film Looks | `fuji-film` | 10 |
| `ricoh` | Ricoh GR Looks | `ricoh-gr` | 11 |
| `kodak` | Kodak Looks | `kodak` | 20 |
| `pentax` | Pentax Looks | `pentax` | 11 |
| `ilford` | Cinestill + Ilford Looks | `ilford`, `cine` | 9 |
| `hasselblad` | Hasselblad Looks | `hasselblad` | 4 |
| `sony` | Sony Looks | `sony` | 8 |

有三个数字比组的总条目小（或两组合计），这是预期的：

- **`fujifilm`** 的 `fuji-sim` 组共有 26 条，但只有 **16** 条可编译；另 10 条属于 `fuji-film`，
  现在已拆成独立的 `filmstocks` 包。所以这个包含 16 条。
- **`ricoh`** 的 `ricoh-gr` 有 16 条，其中 **11** 条可编译（另 5 条是 `film-studio-matrix`
  仅登记）。
- **`ilford`** 现在跨两个组：`ilford` 的 **5** 条加上 `cine` 的 **4** 条（电影感风格家族，
  并非伊尔福产品），共 9 条。

所以某个包的数字看起来低时，先看看它的组是不是混进了另一套引擎，再怀疑是不是丢了东西。
`tools/gen_recipes.py --pack <id>` 会打印实际写出的组，并在某个请求的组没贡献任何可编译配方时
给出警告。

---

## 5. 一个包能装什么、不能装什么

一个包是 catalog 里**单品牌**的一片。铁律：**一个包的组必须全属于同一品牌**，因为包的图标和它的
`app_name`（`<Brand> Looks`）标榜的就是这一个品牌。一个包把 Leica 和 Kodak 配方塞在「Leica
Looks」名下，等于对自己的内容撒谎。

**刻意不进任何包的组。** 这些仍可在全量版 App 里用到，全量版照常构建、照常发布。`catalog/packs.json`
把它们记在 `unassigned_groups` 里并附理由，而不是悄悄删掉，好让这个缺口显在数据里，而不是藏在
一份 bug 报告里：

| 组 | 为什么还不是包（暂时） |
|---|---|
| `canon-nikon` | 跨两个品牌 —— 得先拆成每个品牌一个包 |
| `pana-olympus` | 跨两个品牌 —— 同理要拆 |
| `other-stocks` | 混血胶片（Agfa、Polaroid、Ferrania …），没有单一品牌 |
| `app-look` | 不是相机品牌 —— 是社交 / App 滤镜风 |

`canon-nikon` 和 `pana-olympus` 是唯一有清晰路径变成包的：各自拆成 `canon` 与 `nikon`（或
`panasonic` 与 `olympus`）组，然后各写一个包条目。其余两个是类别组、不是品牌，基本不可能成为包。

一个包也不能装 `film-studio-matrix` 条目 —— 那些仅登记、哪都编译不进，自然不会出现在写出的
`Recipes.java` 里。

---

## 6. 转换到底怎么发生

`tools/apply_pack.py --pack <id>` 在一个全新 checkout 里改写包名与 App 名，并移动源码树。它
**就地、有破坏性**，所以 `tools/build_apk.sh` 给每个包单独的 checkout 目录。有意思的是*怎么*改写，
因为里面藏着四个容易漏的坑。

### 6.1 四种分隔符形式

包名在上游树里以四种写法出现，改名必须四种都命中，否则构建就崩：

| 形式 | 例子 | 出现在 |
|---|---|---|
| 点 | `com.hairuoliu.sonysoocrecipes` | `AndroidManifest.xml`、每个 Java 的 `package` 行、JNI 异常查找、`res/layout` 里的自定义视图类名 |
| 斜杠 | `com/hairuoliu/sonysoocrecipes` | `build.sh`、`check-version.sh`、`jni.cpp` 里的一个目录路径 |
| 反斜杠 | `com\hairuoliu\sonysoocrecipes` | `build.cmd` |
| 下划线 | `com_hairuoliu_sonysoocrecipes` | JNI 导出符号（`Java_com_a_b_…_NativeBackup_read`） |

漏了斜杠形式，`javac`/`aapt` 就死；漏了下划线形式，应用启动时会崩 —— 原生层找不到它的异常类。
`apply_pack.py` 用一组模式一次性改写全部四种，而不是四个手写的 `sed`，正是为了防止漏掉任何一个。

### 6.2 原生库名的陷阱

这是一个「看起来像改名、其实不是」的坑。裸 token `sonysoocrecipes` **同时也是原生库名**：
`jni/Android.mk` 里的 `LOCAL_MODULE`、`NativeBackup.java` 里的 `System.loadLibrary`、两个构建脚本
里的 `libsonysoocrecipes.so`。一个只改**裸 token** 的幼稚改名会把库变成 `libsonysoocrecipes.leica.so`
—— 而**点号在可加载的库名里不合法**，于是应用启动时会以 `UnsatisfiedLinkError` 毙命。

这就是为什么四种模式全都锚定在**完整包名**（`com.hairuoliu.sonysoocrecipes`）上，绝不锚定在尾部
的 `sonysoocrecipes` 上。原生库名是故意原样保留的。`apply_pack.py --check` 一旦发现 `jni/Android.mk`
或 `build.sh` 里出现 `.leica.so`（或任何 `.<id>.so`）就直接判失败。

### 6.3 子包嵌套

因为一个包的包名是基包加一段，所以**目标**源码目录物理上就在源码目录**里面**：

```
src/com/hairuoliu/sonysoocrecipes/        （基包）
        └── leica/                        （包 —— 嵌套在基包之内）
```

把 `…/sonysoocrecipes` 直接移到 `…/sonysoocrecipes/leica` 会被拒绝（不能把一个目录移进它自己的子目录）。
`apply_pack.py` 借一个同级临时名（`…/sonysoocrecipes__pack_tmp`）中转，再移到位。这个移动也是受保护的：
第二次运行只有在 Java 源码还直接躺在基包目录里时才会移动，所以部分失败后的重跑是续做而不是再嵌深一层。

### 6.4 幂等与 `--check`

转换**按构造就是幂等的**。每个模式锚定完整包名，且当后面已经跟着另一个包段时拒绝再次触发，所以跑两遍
不会产生 `…sonysoocrecipes.leica.leica`，部分失败后的重跑是补完而不是损坏或重复追加。

`apply_pack.py --check` 校验一个 checkout 是否已**是**这个包且自洽 —— 它问的是「再跑一次转换还会改东西吗？」
（不是「基包名还出现吗？」），并确认 manifest 声明了包包名、源码树已移动、原生库名完好无损。在 CI 里、
以及对 checkout 做过任何手动改动后，都用它。另有 `--dry-run` 只报告不改写。

---

## 7. 图标 —— 从哪来、怎么生成、以及归属义务

每个包的启动图标，是用**该品牌最知名相机的照片**构建的——`filmstocks`、`kodak`、`ilford`
这三个包是胶片罐而非相机（它们是按胶片命名，不是按机身）。**九个包现在全部**用**用户专门提供的、
保留全部权利的商业照片，未授予任何许可** —— `ricoh` 与 `pentax` 是最后两张 Wikimedia Commons
照片，也已换成用户来图，所以**没有任何自由许可图片随任一 APK 发布**。逐张来源与「放宽许可」的约定记在
`assets/app-icon-packs/CREDITS.md` 里；而因为图标随 APK 一起发布，许可与署名必须**随 APK 走**：它进
`NOTICE.md`，也进每个包的发布说明。

图标集由 `tools/build_pack_icons.py` 生成（它是 `tools/build_app_icon.py` 的按包对应版，后者构建
全量版那套）。每套是五个固定像素尺寸的文件：

| 文件 | 密度 | 尺寸 |
|---|---|---|
| `ic_launcher-mdpi.png` | mdpi | 48 |
| `ic_launcher-hdpi.png` | hdpi | 72 |
| `ic_launcher-xhdpi.png` | xhdpi | 96 |
| `ic_launcher-xxhdpi.png` | xxhdpi | 144 |
| `icon-512.png` | 商店列表图 | 512 |

**对抠图要诚实。** 全量版图标由 `tools/build_app_icon.py` 构建，**抠掉了纯白背景**（透明 RGBA
可绘制）。本版本起，品牌包图标**也**做了抠图——每张都是从源照片里裁出的透明剪影，与全量版风格一致，
而非保留整张矩形照片。不要说品牌包图标是矩形照片；它们不是。

**归属义务目前九个包一个都不适用——但只要再用带许可的图，它立刻回来。** 九个包现在全部用用户提供的、
保留全部权利的商业照片；未授予任何许可，因此没有署名义务，只有发布方承担分发风险。`ricoh` 与
`pentax` 过去是例外：它们用的是 Wikimedia Commons 上的 **CC BY 2.0** 照片（Ricoh GR，作者
Kārlis Dambrāns；Pentax K1000，作者 Terry Presley），必须署名。这两张如今也都换成了用户来图，
所以当下发布的素材里没有任何带许可的内容。相应的署名行也已在 `NOTICE.md` 与 `CREDITS.md` 里同步删掉 ——
**为一张早已不发布的照片保留署名，是另一种形式的虚假标注，同样是缺陷。**

因此这条义务是「休眠」而非「废除」。`CC BY` 只有**带署名**才允许商用，将来若引入 CC BY 素材，署名
必须随行于 `NOTICE.md` 和每个包的发布说明，许可全文也要随 APK 发布。`CC BY-SA`
被**刻意排除**在品牌包图标之外：它的相同方式共享条款会波及整个 App，而不只是图标。全量版默认图标
是原创作，无需此类署名。

---

## 8. 命名与商标 —— 实话实说

`app_name` 用 **`<Brand> Looks`** 形式，而不是裸品牌名或相机型号数字。理由很窄也很实际：用一个商标
给分发的 App 命名，**暗示背书**，而背书才是真能让一个项目被下架的风险。`Leica Looks` 描述的是这个
App 拿 Leica 的味道做了什么；单独的 `Leica` 会让人以为 Leica 做了或认可了它。

**直说：`<Brand> Looks` 形式是降低风险，不是获得许可。** 在 App 名里用品牌名仍然是商标使用。指示性
或描述性使用 —— 如实说明这个 App 是*为*什么用的 —— 在某些司法辖区是一种*抗辩*，不是*许可*，而应用
商店比法院更严。全量版 App 保持品牌中立（`Sony SOOC Recipes`）并仍是默认下载，正是为了让项目的主分发
不挂任何一个品牌的名。

任何**再分发**这些包的人 —— 重新发布 APK，或把它们塞进别的产品里 —— 自己承担那份商标风险。本文档
不会让那风险消失，只是让它显形。

---

## 9. 构建一个包

你多半不必自己构建。CI 在一个 `v*` tag 上构建每个包（见下）。但本地：

```bash
tools/build_apk.sh --pack leica        # 构建一个品牌包，在它自己的 checkout 里
tools/build_apk.sh --all-packs         # 全量版 App + packs.json 里的每个包
```

`--pack <id>` 给这个包单独的 checkout（`build/recipe-lab-sony-pmca-<id>`），就地转换不会踩到全量版。
`--all-packs` 先构建全量版，再构建从 `catalog/packs.json` 读出的每个包（不是写死的）。

### CI 怎么做

`.github/workflows/release.yml` 在一个 `v*` tag 上构建 APK。构建矩阵**在运行时从
`catalog/packs.json` 推导**：一个 `targets` 作业产出全量版一项 + 每个包一项。随后一个 `apk` 作业
**每个矩阵项跑一个作业**，各自在独立 runner 上、各自全新克隆到固定版本的上游并套用该包的转换。由此
得到两个性质：

- **失败隔离。** `fail-fast: false` 意味着一个坏包只自己失败；它不会挡住其他包，也不会挡住全量版。
- **无 YAML 漂移。** 包列表只存在于 `catalog/packs.json`。在那儿加一个包，下一次 tag 自动被纳入，**无需
  改动工作流文件** —— 本仓库禁止把这份列表抄进 YAML，因为那份抄本会在一有人改 JSON 时就漂移。

每个包的发布说明（在 `release` 作业里生成）重申 [§3](#3-设置存储是共享的--一台相机同一时间只能有一个配方生效)
的共享设置警告，并列出每个包 APK 与其 SHA-256。

---

## 10. 新增一个包

假设你想加一个 `contax` 包。一步步：

1. **改 `catalog/packs.json`。** 往 `packs` 里加一条：
   ```json
   { "id": "contax", "app_name": "Contax Looks", "groups": ["contax"], "icon_set": "contax" }
   ```
   `app_name` 用 `<Brand> Looks` 形式（§8）。`groups` 必须**只有一个品牌** —— 如果该品牌配方当前
   在一个还跨另一品牌的组里（如 `canon-nikon`），先在 `catalog/filters.json` 里把它拆开。

2. **确认组是单品牌且可编译。** 跑 `tools/gen_recipes.py --pack contax` 看输出：它打印写出的组，并在
   某个请求的组没贡献任何可编译配方时（例如全是 `film-studio-matrix` 条目）报警。零配方的包是个坏包。

3. **生成图标集。** 产出 `assets/app-icon-packs/contax/`，五个文件分别为 48 / 72 / 96 / 144 / 512 px（§7）。
   首选：把抠好的 `contax.png` 放进 `camera-covers/cutout/`（见 `tools/cut_camera_covers.py`），
   `tools/build_pack_icons.py` 会自动采用并渲染成透明剪影；没有抠图则回退到加边框的 `master.jpg`。
   把来源与许可记进 `assets/app-icon-packs/CREDITS.md`、`NOTICE.md` 和该包发布说明。
   **不要**用 `CC BY-SA` 照片——图标是对照片的改编，相同方式共享会波及整个应用。

4. **跑关卡。** `tools/check_assets.py` 现在会检查图标集。缺整套目录只是*note*（该包回退到默认图标），
   但一套已存在却缺文件或尺寸不对就是*error*。打 tag 前关卡必须过。

5. **本地构建做 sanity check。** `tools/build_apk.sh --pack contax`，若留着 checkout，再用
   `apply_pack.py --check` 确认 APK 的包名。

6. **打 tag 发布。** 推一个 `v*` tag。`release.yml` 的矩阵自动纳入新包 —— 无需改工作流。发布说明会点名它。

这就是全部的改动面：一条 JSON、一套图标、一行署名。代码库里别的都不动。
