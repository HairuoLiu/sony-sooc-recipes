# 更新日志

[English](CHANGELOG.md) · **简体中文**

每个条目记一次上传到 GitHub 的版本。版本号遵循语义化版本，但**配方值本身的变化**也视
为 minor——对使用者来说，一款滤镜的参数变了，比加个函数影响更大。

发布前必须跑 `python tests/run_all.py`，全部关卡加自测全绿才允许打 tag——自测会给每道关卡喂坏输入，证明它们真的会失败。

> `v0.5.0` 是本仓库对外发布的**首个版本**。它之前完成的开发批次没有对应的 Release，
> 因此不带版本号，以「开发批次」列在下方，内容与许可判断原样保留以便追溯。

---

## v0.82 — 2026-09-25 · 第十个包：电影滤镜

配方值相对 v0.81 的*观感*没有改动——但新增了九款 `authored-here` 配方，并多了一个品牌包来承载它们。

- **第十个品牌包：`cinema`（电影滤镜）。** 九个 `kino` 组配方——Kino Cool 4 … Kino Warm 4——编译进一个独立
  APK（`com.hairuoliu.sonysoocrecipes.cinema`）。发布现在共 **十一个** APK：全量版加十个单品牌包，较
  v0.81 的十个又多一个。
- **数据来自用户购买的 KinoLUT `.cube` 集，而非复制。** 共分析了 45 个 cube 文件（5 档曝光 × 9 档白平衡）：
  逐通道的白平衡增益满足 `gainG ≡ 1.000`（正好对应相机的 A/B 轴），中灰锚点相对 6500 K 偏移 −49.46 mired，
  九档覆盖 4500–6300 K、且 `gm +2`。每款配方的 `kelvin`/`ab`/`gm` 都由这些测量值填出。
- **诚实说明相机设置区做不到的事。** KinoLUT 标志性的*仅暗部*青调（≈ 13000 K）需要逐影调 LUT，而相机
  没有这种通道，因此**没有复现**——只匹配了中间调。拟合出的 3×3 矩阵大约只有原作的 65% 色度，而这正是
  这套引擎的天花板。九款**全部 `verified: false`**（尚未实机确认），且刻意没有走 Toy Camera 图片效果那条路。
- **不分发任何 LUT。** 这里只重写了相机存得下的参数值，`.cube` 文件本身从不随包发布。这是相机参数空间里的
  原创近似，不是 KinoLUT 的移植。
- **全量版现在编译 149 款配方、横跨 15 组**（含 `kino` 组）。见 `docs/packs/all-in-one.md`
  与 `docs/packs/cinema.md`。

*已知缺口：* 和自写部分一样，`kino` 配方**尚未在实机确认**——这些数值来自对 LUT 的推导，而非机身实跑。

---

## v0.81 — 2026-09-24 · 应用开始讲相机的话

不改任何配方值。这是一个语言版本，外加排在它后面的文档重写。

- **应用里的每一个字符串都跟随相机。** 140 款编译进包的配方、14 个分组名，以及所有界面文字，现在都有中文孪生版本。`Recipes.java` 在类加载时读一次 `java.util.Locale.getDefault()` 然后切换，所以**同一个 APK 同时服务两种语言**——不需要另外找中文版，也没有开关要设。机身停在英文，界面就是英文。
- **APK 里打包了子集化的中文字体。** Noto Sans SC 放在 `assets/fonts/`，只保留应用真正会画出来的 299 个字：两个文件各约 57 KB，而它们的来源可变字体有 **17.7 MB**。相机的应用存储只有几 MB，装不下未裁剪的字体——所以这一步才是「汉化能发出去」的前提。它的 OFL 许可和 Quicksand 的放在一起随包分发。
- **九个品牌包各自有了中文启动名**（徕卡风格、富士模拟、哈苏风格……），由 `tools/patch_i18n.py` 写入——刻意不放在 `apply_pack.py` 里，因为后者跑在包名存在之前，没有可依据的键。
- **修好了保真度关卡。** 给每个生成的 `new Recipe(...)` 多加一个字符串参数，把 `tools/check_fidelity.py` 的解析器弄坏了：它把中文名当成一个配方值来数，于是报出**全部 77 条上游配方漂移**，而实际上一个值都没动。这道关卡本地会被跳过（它需要上游 checkout），只在 CI 跑，所以仓库里没有任何东西能发现它。新增的 `TestFidelityParser` 会断言解析器仍然读得懂我们生成的 Java，并且断言译文不构成配方身份的一部分。
- **两份 README 重写并折叠。** 现在的卖点是这份目录真正的样子——机型模拟（徕卡、哈苏、富士、理光、宾得），胶片观感只是并排列出——而不是「155 个胶片滤镜」。每份 README 有五个次要章节被折进 `<details>`，首屏只留下决定要不要装的人真正需要的信息。

*已知缺口：* 中文显示**尚未在实机确认**。字符串和字体确实进了 APK，关卡也能证明它们被构建进去了，但还没有人把机身切到简体中文看一眼屏幕。最后这一步仍然需要一台相机。

---

## v0.8 — 2026-09-22 · 首页直接把东西摆出来，而不是描述它

只有文档——不改配方值，不改品牌包，不改代码。

- **两份 README 以双图开头**：相机自己的 Application List，旁边是应用主屏。原来在那位置的全是描述应用做什么的文字；这两张照片就是那个问题的答案，也是这个页面上唯一不是「声称」的东西。
- **仓库描述改为英文**，并围绕机型模拟重写——那是这个项目里别处拿不到的部分。

---

## v0.7.4 — 2026-09-21 · 预览图必须与 APK 用同一套尺寸

不改任何配方值，不改任何品牌包。这是一次结构评审后的仓库健康版本：三处能被测试守住的漏洞被守住，一个死文件被删掉。

- **`tools/preview_picker.py` 与 `assets/ui/PickerView.java` 不会再悄悄对不上。** 两个文件各自写了一遍浏览器的几何——内边距、头部与底部的预留、行高，以及 9/13/10 sp 三个字号——而预览是在没有相机时判断这些像素的唯一依据。新增的 `TestPreviewMirrorsTheBrowser` 会从两边各自把这六个值抽出来比对，只改一边就会失败，并且错误信息里直接给出两边各自的数值。v0.7.2 以来修掉的每一个视觉缺陷都是对着这份预览用眼睛看出来的，这正是两份拷贝必须绑在一起的原因。
- **上游 pin 的第三份拷贝现在也被守住了。** 同一个上游 SHA 写在 `catalog/filters.json`、`.github/workflows/release.yml` 和 `tools/build_apk.sh` 三处，但 `TestPinnedUpstream` 只认 YAML 的写法（`UPSTREAM_SHA:`），从不读 shell 里的 `UPSTREAM_SHA=`。也就是说本地构建完全可能克隆到和 CI 不同的上游，而全程关卡是绿的。新增的 `test_build_script_pins_the_same_sha` 补上了这一处。
- **`catalog/index.html` 现在标出了自己从哪来。** 它由 `tools/gen_browser.py` 生成、并且是有意提交的，此前却没有任何标记——手工改一下看起来完全合理，然后会在下次生成时被覆盖。生成器现在会输出 `AUTO-GENERATED` 头。`tests/run_all.py` 的「是否过期」关卡立刻发现了这个变化，这正是它在起作用。
- **删除 `docs/packs/_packs_data.json`**（5,081 行）。没有任何代码读它，也没有任何脚本生成它，而它里面写的还是 `catalog_version: 0.6.0`——目录早就走到 0.7.x 了。它等于同一批计数的又一份过期副本，而这个仓库一直在花力气保证这种计数只存在一处。需要的话仍可从 git 历史找回。

*评估过但刻意没做：* 重命名 `tools/validate_catalog.py`、`tools/patch_ui.py`，以及挪走 `catalog/ui-theme.json`。这三个名字在 CHANGELOG、两份 README、两份架构文档和测试里被引用约二十处，改名的改动量远大于它能带来的清晰度，而它们本来就在 `README.md` 的工具表里写清楚了，那才是真正会去找它们的地方。

---

## v0.7.2 — 2026-09-19 · 发布构建根本没把主屏装进去

**v0.7.0 的 APK 里并没有它自己宣布的磨砂双栏主屏。** 本地构建有，发布构建没有：`.github/workflows/release.yml`
把构建步骤又写了一遍，而那一遍漏了 `tools/patch_ui.py` 这一步——于是 v0.7.0 的十个 APK 装的是上游主屏，
而 CHANGELOG、README 和两份架构文档都写着相反的话。全程所有关卡都是绿的：主题的工具本身都被测过，但没有
任何东西测过「发布构建到底跑没跑它们」。本版不改任何配方值，也不改任何包。如果你装了 v0.7.0 的 APK，相机上
的配方就是这一版的配方；不同的是那块屏幕。

*（`v0.7.1` 打了 tag 但没有发布出任何东西：补回这一步之后，构建在 aapt 处理主题自己的布局时失败——见第三条
——所以修复落到了这一版。）*

- **`release.yml` 现在会重放主题**，位置与 `tools/build_apk.sh` 一致——`apply_pack` 之后、`gen_recipes` 之前。
- **`tests/test_catalog.py::TestBuildPipelinesAgree` 把两条管道钉在一起。** 它比较两条管道各自跑的变换工具及
  其顺序，并点名发布构建漏掉的那个。该测试跑在 `release.yml` 自己的「构建前关卡」job 里，所以此后一次缺步
  骤的发布会在构建之前就失败，而不是照常发布出去。
- **主题的布局从来没被编译过，而且根本编译不过。** `assets/ui/main.xml` 让标题指向 `@id/head`，而拥有
  `@+id/head` 的那条栏声明在它后面，aapt 按文档顺序单趟解析 id——于是构建的第一步 `R.java` 生成就失败了。
  此前没人发现，是因为没有任何一条会重放主题的管道真正跑过：CI 没有，本地也没有。现在 `head` 的第一次出现
  就带上 `+`，并由 `tests/test_ui_theme.py` 直接在布局文本上强制这条规则（aapt 本身需要 3 GB 的 NDK 工具链）。
- **字体的许可现在真的随字体走。** `patch_ui.py` 会整目录拷贝 `assets/fonts/`，于是 `OFL-Quicksand.txt`
  和它覆盖的两个 Quicksand 字面一起进 APK。OFL 唯一的再分发条件就是许可全文必须随字体同行，`NOTICE.md`
  也早已这么要求——但此前只拷了两个 `.ttf`，所以至今每一个 APK 都会把字体发出去、而把许可留在仓库里。

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
- **磨砂双栏主屏。** 应用主屏现在是磨砂双栏布局，以上游布局之上「重放补丁」的方式发布，而非作为源码提交。颜色、三个屏幕开关（`legend_visibility`、`app_title_visibility`、`tag_visibility`）与布局本体分别落在 `catalog/ui-theme.json` 与 `assets/ui/main.xml`；`tools/patch_ui.py` 在**两条构建管道**（本地的 `build_apk.sh`、打 tag 时的 `release.yml`）里、于 `apply_pack` 之后、`gen_recipes` 之前，把它们重放到上游 checkout 上。磨砂是「模拟」的（一层约 0.90 透明度的半透层，没有模糊——`minSdkVersion 10` 既无 RenderScript 也无 RenderEffect），字体是 Quicksand（SIL OFL 1.1），作为 raw 资源随包捆绑，`tests/test_ui_theme.py`（25 个用例）看守布局——丢一个 view id、一个 aapt 解析不了的颜色，或写错一个会让 aapt 无法 inflate、进而让应用启动即崩的可见性值，都不会流到相机上。*（**v0.7.0 的 APK** 里其实并没有这块屏幕：`release.yml` 漏了重放这一步，只有本地构建有。见上方 v0.7.2。）*

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
