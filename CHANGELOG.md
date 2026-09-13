# Changelog

每个条目记一次上传到 GitHub 的版本。版本号遵循语义化版本，但**配方值本身的变化**也视
为 minor——对使用者来说，一款滤镜的参数变了，比加个函数影响更大。

发布前必须跑 `python tests/run_all.py`，六道关卡全绿才允许打 tag。

---

## v0.4.0 — 2026-09-13 · 胶片批次

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

## v0.3.0 — 2026-09-13 · 相机模拟批次

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

## v0.2.1 — 2026-09-13 · 文档

配方与 APK 一行未改（99 款 / 84 款可编译，APK 仍是 v0.2.0 那个）。这一版只动文档。

**不打 tag。** 打 `v*` 会触发 `release.yml` 重新构建并发布 APK，而 APK 没有任何变化——
只为文档跑一次 3 GB 工具链没有意义。要装相机就去 v0.2.0 的 Release 页下载。

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

## v0.2.0 — 2026-09-13

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
`lib/armeabi/librecipelab.so` 30 KB（armeabi 正是 2.3.7 的 ABI）、v1 签名齐全
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

## v0.1.0 — 2026-09-13

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
