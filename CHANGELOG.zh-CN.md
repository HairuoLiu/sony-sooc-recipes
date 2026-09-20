# 更新日志

[English](CHANGELOG.md) · **简体中文**

每个条目记一次上传到 GitHub 的版本。版本号遵循语义化版本，但**配方值本身的变化**也视
为 minor——对使用者来说，一款滤镜的参数变了，比加个函数影响更大。

发布前必须跑 `python tests/run_all.py`，七道关卡加自测全绿才允许打 tag——自测会给每道关卡喂坏输入，证明它们真的会失败。

> `v0.5.0` 是本仓库对外发布的**首个版本**。它之前完成的开发批次没有对应的 Release，
> 因此不带版本号，以「开发批次」列在下方，内容与许可判断原样保留以便追溯。

---

## v0.7.0 — 2026-09-19 · 品牌包重组，与全套新图标素材

- **第九个品牌包：`filmstocks`（Fuji Film Style）。** 富士包一拆为二。`fujifilm` 现在只含相机
  *模拟*——来自 `fuji-sim` 组的 16 款已编译配方；富士真实*胶卷*（来自 `fuji-film` 组的 10 款已编译
  配方）移到新的 `filmstocks` 包。发布现在共 **十个** APK：全量版加九个单品牌包，较 v0.6.0 的九个又多一个。
- **`ilford` 被 `nichefilm`（Niche Film Style）取代。** 旧的 `ilford` 包（「Cinestill + Ilford
  Looks」，`ilford` + `cine` 两组，9 款配方）改名为 `nichefilm`，并吸收 `other-stocks`（17 款已编译的
  复古/小众胶片配方——Agfa、Polaroid、Ferrania 等），使 `ilford`、`cine`、`other-stocks` 三组合计
  **26** 款。原因：该包图标是一张 CineStill 胶卷产品图，从来都对不上「Cinestill + Ilford」这个名字；
  把这批小众/复古胶片归到一个包里，既修正了这个名实不符，也给 `other-stocks` 安了家（它此前只随全量版发布）。
  `cine` 是电影感风格家族、并非伊尔福产品，`other-stocks` 则是一堆混血胶片品牌、背后没有单一品牌。
- **所有包的 App 名从「<X> Looks」统一改为「<X> Style」。** 九个包一致，让名字读作风格描述、
  而非背书意味。
- **新的启动图标落在深色拉圆角底上。** 每个包图标都是从其源素材里抠出的机身或胶片剪影，再压到一块近黑的圆角底（RGB 28,28,30 ≈ #1C1C1E）上，让深色主体在深色壁纸上依旧清晰。旧的纯透明剪影仍可用 `--no-bg` 生成。
- **九个包图标全部用用户提供的商业素材。**   `leica`、`fujifilm`、`filmstocks`、`kodak`、`nichefilm`、
  `hasselblad`、`sony`、`ricoh`、`pentax` 现在用的是用户专门提供的、保留全部权利的商业照片 / 厂商官方渲染，
  未授予任何许可。风险由发布方承担；诚实的来源与「放宽许可」的约定见 `assets/app-icon-packs/CREDITS.md`。
  `ricoh` 与 `pentax` 是最后两张 Wikimedia Commons **CC BY 2.0** 照片，如今也已换掉，所以**没有任何
  自由许可图片随任一 APK 发布、也不再有署名义务**；它们原先的署名行是**删除**而非保留——为一张早已不发布的
  照片留着署名，本身就是虚假标注。
- **九个图标里六个是胶片、不是机身。** `filmstocks`、`kodak`、`nichefilm`、`pentax`、`ricoh`、
  `sony` 展示的是胶片；只有 `leica`（M9）、`fujifilm`（X100VI）、`hasselblad`（X2D II 100C）展示机身。
  `nichefilm` 的图标正是那张 CineStill 胶卷产品图，也是这次重组名字的由来。
- **推迟到下个版本。** 磨砂双栏主屏 UI 主题（叠在上游布局之上的一次性补丁）不在本次构建中，将在后续版本落地。

---

## v0.6.0 — 2026-09-13 · 品牌包：一个品牌一个 APK

同一份代码、同一份 `catalog/filters.json`，按相机品牌打包成 **8 个独立 APK**，与全量版
一起发布（9 个构建目标）。每个包的 Android 包名多一段（`...sonysoocrecipes.<id>`），所以
几个包能在相机上**并存**；每个包的启动图标是那个品牌最知名的一台相机。

### 为什么做

155 款配方在相机上只能靠按键逐个翻，翻起来很累。按品牌拆包后，装自己需要的那一份，
要翻的量少一个数量级。**拆的是浏览入口，不是数据**：仍是一份 catalog、一个配方引擎，
`tools/gen_recipes.py --pack` 只是把某个包的组生成进去。

### 包与配方数

leica 20 · fujifilm 26 · ricoh 11 · kodak 20 · pentax 11 · ilford 5 · hasselblad 4 · sony 8

`canon-nikon`、`pana-olympus` 各跨两个品牌（要先拆成单品牌包才能归属），`other-stocks`、
`cine`、`app-look` 非单一品牌——这五组**只进全量版**，记录在 `packs.json` 的
`unassigned_groups` 里，缺口可见而不是静默丢掉。

### 必须知道的

- **装多个包不等于多台相机。** 相机的设置存储是共享的，同一时间只有一个配方生效；
  各包的快照按包名隔离、互不覆盖，但不会叠加。
- **包不比全量版小多少。** 配方数据是 APK 里最小的东西（全部 155 款 ≈ 21.6 KB，
  APK ≈ 102 KB），大头是引擎。包的意义是「要翻的少」，不是「下载的小」。
- **签名 key 仍是一次性的**，与 v0.5.0 相同的注意事项。

### 实现

- `catalog/packs.json` 定义包；`tools/apply_pack.py` 就地改写包名 / app_name / 图标；
  `tools/gen_recipes.py --pack` 只生成该包的组；`tools/build_matrix.py` 从 packs.json
  派生发布矩阵（矩阵不写死在 YAML 里，加一个包自动多一个构建目标）。
- 发布矩阵在 CI 里按包并行构建（`fail-fast: false`），任一包失败则**不发布**——
  宁可不发，也不发一个缺包的 Release。
- 图标**不抠图**：用照片自身边框色找主体、按主体尺寸开方形框并补边、4× 超采样圆角。
  生成器 `tools/build_pack_icons.py`，素材与逐张许可见 `assets/app-icon-packs/CREDITS.md`。
- 图标许可规则：**只要 PD / CC0 / CC BY**。`CC BY-SA` 一律否决——图标是对照片的改编，
  share-alike 会波及整个应用。fujifilm / hasselblad / sony 为 CC0 或 PD（零义务），
  其余五张 CC BY（署名随 APK 走）。
- `tests/test_packs.py` 31 条，其中最关键的一条断言**每个包的配方值与全量版逐值一致**：
  包必须是子集，不能是重新拟合。

详见 `docs/BRAND-PACKS.md`（中文版 `BRAND-PACKS.zh-CN.md`）。

## v0.5.0 — 2026-09-13 · 重命名为 Sony SOOC Recipes

将本仓库的相机端 App 从上游项目名重命名为 **Sony SOOC Recipes**：

- 相机内显示名、APK 文件名、Java 包名统一为 `Sony SOOC Recipes` / `SonySOOCRecipes` / `com.hairuoliu.sonysoocrecipes`。
- `release.yml` 在 CI 构建时通过 sed + `git mv` 把 fork 整体改名（含 JNI 符号 `Java_com_voxivoid_recipelab_*` → `sonysoocrecipes`）。
- 安装说明、README、架构文档、工具脚本与生成的目录浏览器均改用新名称；正文对上游 voxivoid 项目的引用改写为「上游项目 / upstream project」。
- 保留 `NOTICE.md` 的 MIT 法定署名，以及 CI / `check_fidelity.py` 联网抓取上游源码所用的 raw-URL。

## 开发批次 · 胶片（2026-09-13，新增 38 款）

**新增 38 款**（117 → 155，可编译 102 → 140），测试用例 25 → 63。分组不变。

背景：用户确认其 LUT 收藏（相机模拟系列与徕卡缩写名合集）为本人（Roger Wang 笔名）
创作、可自由使用，此前跳过的两批于是补齐。Dehancer 胶片合集按胶片种类观感做参考。

### 胶片 24 款（去重后）

与现有目录比对：Dehancer 68 个文件里 30 个胶片已覆盖（Portra/Gold/HP5/Velvia/
Acros/Cinestill/Instax 等），收录**未覆盖**的 24 款：

- **Kodak +5**：Aerocolor IV 125（航空负片）· Eastman Double-X 5222（cine 黑白）·
  Plus-X Pan 125 · Ektar 25（与 Ektar 100 是两支胶片）· Supra 100
- **Fuji +5**：Reala 500D（电影负片）· CDU-II 交叉冲洗 · Fujicolor 100 ·
  工业打印 100 / 400
- **Other Stocks +14**：Adox Color Implosion · 安布罗湿版 · Astrum CN 125 ·
  柯尼卡 Centuria / VX400 / Impresa · Lomochrome Metropolis / Purple ·
  ORWO Chrom UT21 · 宝丽来 Type 100 褐调 · Prokudin-Gorskiy 1906 ·
  Rollei CN200 / Ortho 25 · Svema Type-42

### 徕卡包 14 款（去重后）

缩写名解码：CNT/CLS/ETN = Contemporary/Classic/Eternal，与现有目录重复，跳过。
收录其余 14 款：B&W HC · B&W Natural · Greg WLM（暖调黑白）· IA（硬黑白）·
Blu（冷调黑白）· Sel（淡银）· Sepia · Bleach · Chrome · BRS（暖调高反差）·
Natural · Silver（柔）· Teal · Vivid。

### 诚实说明（写进了各条目 note）

- **Lomochrome Purple 的绿→紫置换**：索尼设置区做不了逐色相置换，只能用品红+琥珀
  白平衡整体偏移近似气质——note 里写明了。
- **Rollei Ortho 25 的正色响应**（红光不感光）：无法复现，只保留高反差硬朗观感。
- 全批 `authored-here` + `verified: false`，note 附参考测量值（反差/饱和/色偏）。

---

## 开发批次 · 相机模拟（2026-09-13，新增 18 款）

**新增 18 款「相机调色模拟」配方**（99 → 117，可编译 84 → 102），新增组 `pentax`。
全部 `source: authored-here` + `verified: false`，测试用例 7 → 25 条。

这批配方的定位：模拟**其他相机机身 / 机身内色彩模式**的观感——宾得 Custom Image、
哈苏 HN CS、徕卡机身默认渲染、GR 系的电影调。

### 新增组 Pentax（11 款）

宾得 Custom Image 目录的近似，参数依据**宾得官方对各模式的公开描述**：

| id | 官方描述要点 |
|---|---|
| `pentax-bleach-bypass` | 低调、高反差、色彩收敛（漂白旁路冲洗） |
| `pentax-muted` | 高调、低反差、饱和收敛 |
| `pentax-radiant` | 高饱和高反差、整体提亮、夸大色相 |
| `pentax-reversal-film` | 黑位深，靠反差而非饱和度还原反转片 |
| `pentax-satobi` | 60-70 年代彩照：青蓝、暗黄、褪色红 |
| `pentax-katen` | 夏空的浓郁蓝与白云细节（特别版） |
| `pentax-kyushu` | 秋意的红调蓝与深绿（特别版） |
| `pentax-fuyuno` | 高调冬景、饱和收敛（特别版） |
| `pentax-harubeni` | 樱花粉、色相向红偏移（特别版） |
| `pentax-gold` | 高光区黄调更浓郁（K-1 II 特别版） |
| `pentax-miyabi` | 雅致、低反差、颜色不抢戏 |

### 既有组的扩充

- **Hasselblad**（1→4）：HNCS LowSat · HiContrast · HiContrast LowSat
- **Leica**（4→6）：M9 CCD（暖调 CCD 渲染）· M240 STD
- **Ricoh GR**（14→16）：GR Cinema Green · GR Cinema Yellow（GR 街拍圈常见的青绿/暖黄电影调）

### 合规边界（这批配方为什么这样写）

用户提供了一批「相机模拟 LUT」作参考。其中哈苏/徕卡 M9/M240/宾得/理光一套的
许可为 **BY-NC-ND（禁止演绎）**——把 LUT 数值转换后发布即构成衍生作品，不可以。
但**相机模式本身是事实而非表达**：宾得官方页面公开描述每个 Custom Image 的观感，
我们按这些公开描述自写参数，不含任何第三方 LUT 的数据。Dehancer 胶片 68 款与出处
不明的 Leica 缩写名合集未收录（前者是商业插件专有 profile 且与现有胶片组大量重复）。

### 其他改动

- `tools/gen_recipes.py`：`GROUP_JAVA` 补 `pentax` 常量（生成器每个组需要一个 Java 标识符）

---

## 开发批次 · 文档（2026-09-13）

配方与 APK 一行未改（99 款 / 84 款可编译，APK 仍是上一版那个）。这一版只动文档。

**不打 tag。** 打 `v*` 会触发 `release.yml` 重新构建并发布 APK，而 APK 没有任何变化——
只为文档跑一次 3 GB 工具链没有意义。要装相机就用最新 Release 的 APK。

**主页改成英文，中文作为子页面**

`README.md` 重写为英文主页，`README.zh-CN.md` 是同一份内容的中文版，两页顶部都有
`English · 简体中文` 切换。**计数标记 `<!-- counts: total=99 compiled=84 -->` 两个文件
各有一份**，`check_readme_counts.py` 现在两边都查——翻译页悄悄留着旧数字，比没有翻译更糟。

**docs/ 全部补成中英双份**

| 文档 | 内容 |
|---|---|
| `docs/INSTALL.md` | 5 步安装流程、各系统前置条件、13 行排错表 |
| `docs/ARCHITECTURE.md` | 数据流、两个引擎的机制差别、许可边界 |
| `docs/FAQ.md` | 21 个问答，安全类问题排在最前 |
| `docs/ADDING-FILTERS.md` | 完整参数表、测试用例要求、新增组要同步的 3 处 |

每个都有 `.zh-CN.md` 兄弟文件。

**4 张 SVG 图**

`docs/assets/`：`parameters.svg`（配方能改什么、改不了什么）、`install-flow.svg`、
`architecture.svg`、`engines.svg`。全部带 `@media (prefers-color-scheme: dark)`，
GitHub 深色模式下不会变成黑底黑字。

**新增第 6 道关卡：`tools/check_assets.py`**

扫所有文档里的 `<img>` 和 markdown 图片，四类问题直接失败：

1. 外链图片（图片必须进 `docs/assets/`，不许挂第三方图床）——**状态徽章是唯一例外**，
   它是按请求生成的，本地化就等于把构建状态冻住；
2. 引用了不存在的文件；
3. `samples/` 里命名不合规（必须是 `<配方 id>--off.jpg` / `--on.jpg`，且 id 在目录里存在）；
4. 只报不拦：磁盘上有但没有任何文档引用的孤儿图。

**样张还没到位**

`docs/assets/samples/` 目前是空的。命名规则和投稿方式写在 `docs/assets/README.md`：
同一场景、同一曝光、同一白平衡，只有「上没上配方」这一个变量。

---

## 开发批次 · 首批自写配方（2026-09-13，新增 6 款）

**新增 6 款自写配方**（93 → 99，可编译 78 → 84）

| id | 组 | 手段 |
|---|---|---|
| `kodak-vision2-500t` | kodak | NEUTRAL 底 + K 3200 + gm+1，比既有 Vision3 500T 更绿、更平 |
| `toy-camera-warm` | app-look | pe=1 玩具相机（全库首次使用），sub=2 暖调 |
| `toy-camera-cool` | app-look | pe=1，sub=1 冷调 |
| `part-color-red` | app-look | pe=6 局部色彩（首次使用），sub=0 红 |
| `posterization-color` | app-look | pe=3 海报化（首次使用），sub=0 彩色 |
| `teal-mood` | app-look | pe=0，全局 ab−2 / gm+1 的干净青调 |

全部 `source: authored-here` + `verified: false`，并在 `tests/cases.json` 里有对应的钉死值。

**新增组**：`app-look`（App Look）。

**APK 现在由 CI 构建并挂在 Release 上**

此前这个仓库一直是「可验证、不可安装」——五道关卡能证明配方是对的，但产不出能装进相机
的东西，因为工具链要 JDK 17 + build-tools 30.0.3 + **NDK r16b** 约 3 GB（r16b 是最后一个
还带 GCC 工具链的 NDK，Android 2.3.7 / API 10 的目标必须用 GCC）。现在推 tag 就有 APK：

```
https://github.com/HairuoLiu/sony-sooc-recipes/releases
```

产物已核验：有效 zip、`AndroidManifest.xml` 为二进制 AXML、`classes.dex` 52 KB、
`lib/armeabi/libsonysoocrecipes.so` 30 KB（armeabi 正是 2.3.7 的 ABI）、v1 签名齐全
（`--min-sdk-version 10`，相机不认 v2/v3）。

**两个坑，都写在配置文件的注释里了**

1. `jni/platform`（ma1co/OpenMemories-Platform）是必需的——`Android.mk` 要 include 它的
   `vars.mk` 和驱动源码。但它带一个嵌套子模块指向 `git.code.sf.net/p/stlport/code`，
   **那个地址已经不存在了**，而 git 即使不加 `--recursive` 也会钻进去然后整个 job 失败。
   解法是直接克隆 `jni/platform` 并钉在上游记录的 gitlink SHA 上。构建真正链接的 stlport
   是 **NDK r16b 自带的**（`APP_STL := stlport_static`），那份子模块副本用不上。
2. 上游 commit 钉死为 `6b5c8aa2`，同时写在 `filters.json` 的 `fetched_rev` 和
   `release.yml` 的 `UPSTREAM_SHA`。`TestPinnedUpstream` 会在两者漂移时跑不过。

**测试**
- `tests/test_catalog.py`：33 条用例，含结构不变量、参数范围、来源诚实性、生成器往返、
  上游 pin 一致性。
- `tests/cases.json`：本仓库自写配方的钉死值。`TestAuthoredHaveCases` 规定——自写条目
  没有对应 case 就跑不过。
- `tests/run_all.py`：本地一次跑完五道关卡。
- CI 新增 Gate 1b。

**修复**
- `validate_catalog.py` 不再自带一份分组名单，改为读 `groups[]`。之前那份副本会让每个
  新分组都被静默拒绝。

**关于 Liit**：起因是希望把它（DAZZ PTE. LTD. 的闭源商业 App）的滤镜搬进来。结论是不行——
它是闭源商业软件，且其 LUT/曲线在 a6000 上没有承载通道（无 LUT 路径、无 Picture Profile、
存不下曲线）。**没有提取任何东西，也没有复制任何滤镜名**。NOTICE.md 记录了用与没用什么。
这一批是相机参数空间里的原创近似，不是移植。

---

## 开发批次 · 初始目录（2026-09-13，93 款）

首个版本。

- 汇总两个上游项目共 93 款风格：voxivoid/recipe-lab-sony-pmca 的 77 款（MIT，参数全量转录）、
  ukiki0718-netizen/sony-a5100-film-studio 的 15 款（PolyForm Noncommercial，**仅登记名称，
  不转录参数**，由校验器强制）。
- 自写 1 款 `gr-moriyama`，补上两个上游之间唯一真正互补的缺口。
- `catalog/filters.json` 作为唯一事实来源，由 `tools/gen_recipes.py` 生成 `Recipes.java`。
- `tools/check_fidelity.py` 对上游 77 款逐值比对，确认 0 漂移。
- 五道 CI 关卡：validate → fidelity → generate → browser smoke → README counts。
- 滤镜浏览器 `catalog/index.html`，单文件、`file://` 可直接打开。
- 文档：`docs/INSTALL.md`、`ARCHITECTURE.md`、`ADDING-FILTERS.md`、`CHANNEL-COMPARISON.md`
  （USB 与 Wi-Fi ADB 的 13 维度对照）。
