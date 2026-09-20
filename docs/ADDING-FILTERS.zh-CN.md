# 新增一款配方（Recipe）

<p align="center"><a href="ADDING-FILTERS.md">English</a> · <b>简体中文</b></p>

本指南讲如何向 `catalog/filters.json`（唯一事实来源）新增一款胶片风格 recipe。APK 由
该文件生成，你**不要手改**生成的 `Recipes.java`。

开始前两件要事：

- **只改 `catalog/filters.json`，其余别碰。** 不要动 `tools/`、`tests/`、`.github/`、
  `README.md` 及其它 docs。测试、生成器、CI 会把你的 catalog 改动编译成构建产物——
  那些机器不在本次编辑范围内。
- **recipe 是近似，不是复刻。** 这台相机没有 Picture Profile 菜单、没有色调曲线、没有
  LUT 通道、没有 Log。仓库里每一个「柯达」「富士」「徕卡」都是只用相机能持久存储的设置
  拼出来的。动笔写参数前先读 `docs/MAPPING-RECIPES.md`，那是引擎「能做什么、不能做什么」
  的权威说明。

---

## 1. 什么时候该加、什么时候不该加

catalog 现在已有 **155 款 / 14 组 / 两套引擎**。很多风格区间已经饱和。再添一款
「又一款褪色暖负片」并不能增加覆盖度——只会稀释仓库。catalog 是参考资料，不是堆料场。

`docs/MAPPING-RECIPES.md` §1.2 把最初那批 recipe-lab（一份快照）归成 12 个视觉区间。以下区间
**已经满员**（不要再往里加）：

- **区间 3 — 低饱和褪色 / 电影感**（classic-chrome、eterna、gr-negative-film、nikon-flat、
  rec709-video、gr-bleach-bypass）。通用「褪色」已覆盖。
- **区间 8 — 高调柔光 / 粉彩褪色**（soft-high-key、fuji-pro-400h、olympus-pale-light、
  gr-retro、polaroid-instax、nostalgic-neg）。通用「柔光」已覆盖。
- **区间 2 — 暖调日常负片**（kodak-gold-200、kodak-ultramax-400、kodak-colorplus-200、
  kodak-portra-400/800、fuji-superia-400、agfa-vista-200、leica-classic）。

相对地，该文档 §1.3 列出**真正空白、值得补**的区间——这些也是最初目录里唯一通过评审的自写项：

| 该加的 | `pe` | 为何不重复 |
|---|---|---|
| 玩具相机（暗角 + 偏色） | `1` | 全库 93 款上游都没用过，是这台相机唯一能出暗角的渠道 |
| 局部色彩（只留某色相） | `6` | 相机上唯一「保留单色」的路线，此前未用 |
| 海报化 | `3` | 扁平色阶分离，此前未用 |
| 青调（干净全局偏青） | `0` + `ab`/`gm` | 现有只有 `gr-cross-process` 偏绿品红，不是干净青调 |
| 水彩 / 插画 | `13` / `12` | niche，但确实未用 |

> **实话实说。** 如果你的想法是「又一款褪色暖负片」，别开 PR。仓库已经有了。有价值的
> 新增是上表里的 `pe` 驱动效果，或一个明显不同的区间。拿不准先在 issue 里问。

---

## 2. 去重检查

写任何 JSON 前先做这一步。

1. 读 `docs/MAPPING-RECIPES.md` §1.2，找到你的想法属于哪个区间。
2. 在 catalog 里按品牌和大致参数形状搜一下：
   ```bash
   grep -n '"name": "Kodak' catalog/filters.json
   ```
3. 确认没有现成条目在 `sat`/`con` 上与你目标相差 ±1、且 `style` + `wb` 意图相同。
   （如 `kodak-gold-200` 是 `STD, sat 2, con 1, ab 3, gm 1, ev 1`——比这还接近就是重复，
   不是变体。）
4. 检查 `id` 未被占用：catalog 里每个 `id` 必须唯一；生成器还要求 recipe-lab 条目之间
   **`name`**（显示字符串，不是 `id`）全局唯一。同名会让两款在 App 列表里无法区分。
5. 通过 1–4 就继续；通不过就放弃这个想法，或重构成空白区间。

---

## 3. 完整参数表

每个 recipe-lab 条目都带这些字段。下表是**相机实际存储的真值域**；「菜单可达」说明用户
能否从机内菜单复现该值（滑块只到 ±3——超出部分仅 APK 可写，用户手动调不进去）。

| 字段 | 取值域 | 含义 | 在相机上你会看到什么 |
|---|---|---|---|
| `style` | `STD` `VIVID` `NEUTRAL` `PORTRAIT` `LANDSCAPE` `MONO` `CLEAR` `DEEP` `LIGHT` `SUNSET` `NIGHT` `AUTUMN` `SEPIA` | Creative Style（创意风格）——色调底子 | 创意风格选择器；存为枚举值（1..13） |
| `sat` | −16…+16（核心）；菜单仅 ±3 | 相对风格默认的饱和度 | 饱和度滑块；**超出 ±3 时滑块显示最接近值，用户一碰就丢了这个额外幅度** |
| `con` | −16…+16（核心）；菜单仅 ±3 | 相对风格默认的对比度 | 对比度滑块 |
| `sharp` | −16…+16（核心）；菜单仅 ±3 | 相对风格默认的锐度 | 锐度滑块 |
| `matrix` | `0` 标准 / `1` 备用 | 索尼未公开的备用色彩矩阵（约 +45% 彩度、蓝绿串色）。仅对 `VIVID CLEAR DEEP LIGHT SUNSET NIGHT AUTUMN` 生效 | 任何菜单里都看不见；只有 APK 写 |
| `wb.mode` | `AUTO` / `K` | 白平衡模式 | `AUTO` → 无 kelvin；`K` → 色温模式 |
| `wb.kelvin` | 2500…9900 | 色温，仅 `wb.mode = K` 时 | K 模式色温；`AUTO` 要求 `kelvin = 0` |
| `wb.ab` | −7…+7 | 琥珀(+) / 蓝(−) 微调 | 白平衡 A/B 偏移 |
| `wb.gm` | −7…+7 | 绿(+) / 品红(−) 微调 | 白平衡 G/M 偏移 |
| `pe` | 0…13 | Picture Effect（图片效果）索引（下表） | 另一族效果；非零时**相机会忽略 Creative Style** |
| `sub` | 视 `pe` 而定 | 效果子参数 | 仅部分效果使用（下表） |
| `ev` | −5…+5（1 单位 = ⅓ EV） | 曝光补偿 | 存储的曝光补偿 |
| `dro` | `0` 关 / `1`–`5` 档位 / `6` 自动 | DRO（动态范围优化） | DRO 菜单 |

`pe` 索引表（存的就是运行时效果索引——这正是相机记录的）：

| `pe` | 名称 | `sub` 取值 | 备注 |
|---|---|---|---|
| 0 | off | — | style/sat/con/sharp/matrix 全生效 |
| 1 | toy-camera | 0 normal · 1 cool · 2 warm · 3 green · 4 magenta | 自带暗角 + 偏色；**全机唯一暗角渠道** |
| 2 | pop-color | — | — |
| 3 | posterization | 0 color · 1 b&w | — |
| 4 | retro-photo | — | 内置褪色/发黄观感 |
| 5 | soft-high-key | 0 blue · 1 pink · 2 green | 高调提亮 |
| 6 | part-color | 0 red · 1 green · 2 blue · 3 yellow | 局部色彩 |
| 7 | rough-mono | — | 粗颗粒黑白（唯一颗粒来源） |
| 8 | soft-focus | — | — |
| 9 | hdr-art | — | — |
| 10 | richtone-mono | — | — |
| 11 | miniature | — | — |
| 12 | illust | — | — |
| 13 | watercolor | — | — |

直接取自 catalog 的真值例子：

- `kodak-gold-200`（暖调日常负片）：`STD, sat 2, con 1, sharp 0, matrix 0,
  wb AUTO kelvin 0 ab 3 gm 1, pe 0, sub 0, ev 1, dro 6`。
- `olympus-pop-art`（极端饱和，仅 APK）：`VIVID, sat +8, matrix 1` —— `sat +8` 超出菜单
  ±3，用户手动复现不了。
- `eterna-bleach-bypass`：`NEUTRAL, sat -9, con 3` —— catalog 里最极端的 `sat`。
- `teal-mood`（自写）：`NEUTRAL, sat -3, ab -2, gm 1` —— 留在菜单 ±3 内，与多数上游极端值不同。

> **实话实说。** `sat`/`con`/`sharp` 核心接受 −16…+16，但机身菜单只到 ±3。现有条目最
> 远到 `sat -9`（eterna-bleach-bypass）和 `sat +8`（olympus-pop-art）。它们能存住只是因为
> APK 写了进去；用户一开菜单就丢失这段范围。希望用户能复现的配方尽量留在 ±3 内；要超出，
> 在 `note` 里讲清楚。

---

## 4. 两条路径

### 路径 A — 转录已有上游配方

当你要记录的观感上游（recipe-lab，MIT）已有、你只是如实登记时用。

1. 从上游 `Recipes.java`（或你信任的来源）取**精确**参数块。不要四舍五入、不要「整理」、
   不要重新调优——转录漂移就是这个仓库存在要防的失败模式。
2. 设 `"source": "recipe-lab"`、`"verified": true`，保持 `engine: "recipe-lab"`。
3. 跑保真关卡，证明你没挪动任何值：
   ```bash
   curl -sSLf -o build/upstream-Recipes.java \
     https://raw.githubusercontent.com/voxivoid/recipe-lab-sony-pmca/6b5c8aa2900019d98496c7047a90ce73d2d6a725/src/com/voxivoid/recipelab/Recipes.java
   python tools/check_fidelity.py --upstream build/upstream-Recipes.java
   ```
   要取**钉死的那个 SHA**（`catalog/filters.json` 里的 `sources.recipe-lab.fetched_rev`），
   而不是某个分支：分支会移动，拿移动目标比对，会把上游自己的改动报成你的漂移。`-f` 也别省
   ——没有它，404 会被写进文件里，下一条命令随后吐出一个什么都没说明的解析错误。
   它是**语义级**对比（构造函数默认值已展开）。任何真实漂移都会以 `MISSING` 打印并失败。
   你的新配方会列在 `ADDED` 下——这是正常的。引擎把 77 款上游配方当作硬锚点；除非你真的
   增删了上游转录，否则别动这个数。
4. `source: recipe-lab` 不需要 `note`，也不需要 `tests/cases.json` 条目——保真检查就是它的
   规格说明。

### 路径 B — 自己写一款

当观感上游没有、你要从目标「味道」拼出来时用。

1. 从目标出发，不是从数字出发。先在 `docs/MAPPING-RECIPES.md` §1.2 定区间，再用 §2.1
   「视觉目标 → 参数手段」表推导出字段值。例如「手机 App 风的干净青调」→ §2.1 说这台相机
   没有真分色调，只有全局 `ab`/`gm`；于是 `NEUTRAL, sat -3, ab -2, gm 1`（这正是
   `teal-mood`）。
2. 记住硬性引擎规则：**`pe ≠ 0` 时，相机会忽略 `style` 以及 `sat`/`con`/`sharp`/`matrix`
   滑块。** 所以任何 `pe` 配方把这些都设 `0`，交给 `pe` + `sub` 干活。钉成 `0` 也能防止后来
   的贡献者「好心」去调相机根本看不到的值。
3. 你必须诚实地设三个字段：
   - `"source": "authored-here"`
   - `"verified": false`（自写款都还没上过机）
   - `"note"`：一句人话说明它在近似什么、且未经实机验证，例如*「本仓库自写。手机 App 青调；
     这台相机没有真分色调，所以这是靠 ab/gm 的干净全局偏青。未在实机验证。」*
4. 你还**必须**写一条钉死的 test case（见 §6）。否则 `TestAuthoredHaveCases` 会让测试套件
   失败、CI 变红。

> **实话实说。** 路径 B 的配方在生成的 Java 里会标 `NOT VERIFIED ON HARDWARE`。CI 绿只代表
> 文件一致，不代表颜色对。上机验证（`INSTALL.md` 第 8 节）仍是把 `verified` 翻成 `true` 前的
> 必做项。

---

## 5. 登记配方，step by step

编辑 `catalog/filters.json`。`"filters"` 数组就是列表；把你的对象插进对应 `group` 的块内。

1. **顺序有讲究——每个组必须连续。** 生成器每个组只发一段 Java 数组，依赖同组 recipe-lab
   条目都挨在一起。把条目插进它所在组的**已有连续段内**；绝不要把一组拆成两段。
   （film-studio-matrix 条目可随意穿插——它们不编译——但 recipe-lab 必须连续。）一旦破坏
   连续性，`gen_recipes.py` 会在构建前就明确报错退出。
2. **命名。**
   - `id`：小写连字符、自解释、全 catalog 唯一（如 `teal-mood`、`toy-camera-warm`）。别和
     已有 `id` 撞。
   - `name`：App 里显示的名字。必须**在 recipe-lab 条目间全局唯一**（生成器写进 Java 的是
     `name` 不是 `id`）。两个 recipe-lab 同名，App 列表分不清，测试也会失败。
   - 可选 `name_zh`：给人看的中文名。
   - `group`：必须是 `groups[]` 里声明过的组 id（现有 13 个：sony、fuji-sim、fuji-film、
     kodak、cine、ricoh-gr、leica、hasselblad、canon-nikon、pana-olympus、other-stocks、
     ilford、app-look）。
3. **完整字段形态**（recipe-lab）：
   ```json
   { "id": "teal-mood", "name": "Teal Mood", "name_zh": "青调", "group": "app-look",
     "engine": "recipe-lab", "source": "authored-here", "tone": "color",
     "verified": false,
     "note": "本仓库自写。手机 App 青调；这台相机没有真分色调，所以这是靠 ab/gm 的干净全局偏青。未在实机验证。",
     "recipe": { "style": "NEUTRAL", "sat": -3, "con": 0, "sharp": 0, "matrix": 0,
                 "wb": { "mode": "AUTO", "kelvin": 0, "ab": -2, "gm": 1 },
                 "pe": 0, "sub": 0, "ev": 0, "dro": 6 } }
   ```
4. **新增一个品牌分组**要同步三处编辑——漏一处 CI 就挂：
   - `catalog/filters.json` 的 `groups[]`：加 `{ "id": "<kebab>", "label": "<显示>" }`。
   - `tools/gen_recipes.py` 的 `GROUP_JAVA`：加映射 `"<kebab>": "<JAVACONST>"`（生成器对
     无 Java 常量的组会直接退出）。
   - `README.md` **和** `README.zh-CN.md` 的分组表：两处都加同一行——两份 README 都带
     这张表，而 `tools/check_readme_counts.py` 读的是英文那份。
   `validate_catalog.py` 从 `groups[]` 读分组，所以你**不用**改校验器。（本次文档任务要求你
   不要改 `tools/` 和 `README.md`——如果你的新增需要新分组，请开 issue 让维护者做那两处编辑；
   你只在此处加 `groups[]` 那一行。）

> **实话实说。** `film-studio`（PolyForm Noncommercial）条目**绝不能**带 `recipe` 对象。只登记
> 名字。一旦给 `film-studio` 条目附上参数，校验器立刻报错——这条边界是法律性的，不是风格偏好。

---

## 6. 写钉死的 test case

`tests/cases.json` 是本仓库自写配方的规格说明。上游配方由 `check_fidelity.py` 锁死；自写的
没有上游，所以这个文件**就是**契约。规则 `TestAuthoredHaveCases` 强制：**`"source": "authored-here"`
的条目若没有对应 case，测试套件失败**；而指向非 `authored-here` 的 case 是死重，同样失败。

case 是 catalog 条目「识别字段 + recipe」的完整精确副本：

```json
{
  "id": "teal-mood",
  "why": "干净的全局青调。刻意不是分色调：这台相机没有色调曲线，只有全局 ab/gm，所以 note 里写明了。sat -3 留在机身 ±3 滑块内，与几个超出该范围、只能由 APK 写入的上游配方不同。",
  "fields": {
    "name": "Teal Mood",
    "group": "app-look",
    "engine": "recipe-lab",
    "source": "authored-here",
    "tone": "color",
    "verified": false
  },
  "recipe": {
    "style": "NEUTRAL",
    "sat": -3,
    "con": 0,
    "sharp": 0,
    "matrix": 0,
    "wb": { "mode": "AUTO", "kelvin": 0, "ab": -2, "gm": 1 },
    "pe": 0,
    "sub": 0,
    "ev": 0,
    "dro": 6
  }
}
```

case 的规则：

- `id` 必须等于 catalog 的 `id`。
- `recipe` 必须列全**十个**键（`style sat con sharp matrix wb pe sub ev dro`）及其 `wb`
  对象——`test_case_recipes_are_complete` 会拒收不完整的 recipe，因为不完整的会让其余字段
  悄悄漂移。
- `fields` 应列上你想钉死的所有非默认识别字段（`name group engine source tone verified`，
  有 `cross_ref` 也加上）。
- case 和 catalog **一起、刻意地**改。`test_every_case_matches_the_catalog` 在两者不一致时失败。

直接抄现有文件里的 `gr-moriyama`、`kodak-vision2-500t`、`toy-camera-warm`、`toy-camera-cool`、
`part-color-red`、`posterization-color`、`teal-mood` 当模板。

---

## 7. 本地验证——九道关卡

跑提交前脚本。它会**跑完全部九道**再汇总报告——不在第一道失败时停下，这样一道关卡坏了也不会掩盖另一道：

```bash
python tests/run_all.py
```

| 关卡 | 命令 | 拦什么 |
|---|---|---|
| 校验 | `tools/validate_catalog.py` | 结构错误（枚举非法、取值越界、cross_ref 断、组不连续）和来源错误（`film-studio` 条目带 `recipe`、矩阵引擎被误标 MIT）。`sat` 超出菜单 ±3、`pe` 忽略创意风格 打印为**note 而非 error**——那是设计内行为。 |
| 测试 | `tests/test_catalog.py` | 每个 filter 的不变量，加钉死值。`TestAuthoredHaveCases` 拦下任何无 case 的 `authored-here` 条目，以及任何不指向 `authored-here` 的 case。 |
| UI 主题 | `tests/test_ui_theme.py` | 磨砂双栏主屏保留 `MainActivity` 用 `findViewById` 绑定的每个 view id、布局引用的每个 drawable / string 都能解析、每个颜色都是 `#AARRGGBB`。可见性值写错会让 aapt 无法 inflate 布局、应用启动即崩。任何环境都跑，从不跳过。 |
| 生成 Java | `tools/gen_recipes.py --check --fork` | 磁盘上的 `Recipes.java` 与 catalog 应生成的不一致。**未 checkout `build/recipe-lab-sony-pmca` 时跳过**（保真检查同理）。 |
| 浏览器 | `tools/gen_browser.py` + `tests/smoke_browser.js` | `catalog/index.html` 过期或渲染失败。`node` 不在 PATH 时**跳过**。 |
| README 计数 | `tools/check_readme_counts.py` | `README.md` 里的数字与 catalog 不再匹配。 |
| 资源 | `tools/check_assets.py` | 文档引用了不存在的图片、热链了第三方图床（状态徽章除外），或 `docs/assets/samples/` 里的文件没按 `<recipe-id>--off.jpg` / `--on.jpg` 命名、且 id 不在 catalog 中，或图标集缺某个密度。 |
| 双语文档 | `tools/check_docs.py` | 英文文档没有 `.zh-CN.md` 双生且没声明原因、双生的英文原文已消失、共用 `docs/assets/*.svg` 里写死了某种语言、或图里画着的数字已被 catalog 超过。 |
| 自测 | `tests/test_gates.py` | 某道关卡对坏输入不再失败。它给每道关卡喂一份必须拒绝的输入并断言非零退出——放在最后跑，因为它是唯一会临时写探测文件的关卡。 |

「生成 Java」与「浏览器」两关在缺前置时**跳过**（会大声提示），缺工具不是 catalog 坏了。九关全过，才是推送前的门槛。

若「生成 Java」这关因无 fork 被跳过、而你仍想给路径 A 配方做保真证明，按 §4 手动跑 `check_fidelity.py`。

---

## 8. 提交与发布

- **一个 PR 一款**，或同一品牌的一组。别把无关参数改动混进一个提交——保真关卡会点名每处
  漂移值，混在一起难定位。
- **commit message 惯例：**
  ```
  feat(recipes): add Teal Mood

  Closes #NN
  ```
  新增用 `feat(recipes):`。引用确立该空白区间的 issue。
- **打 tag → CI 构建 APK。** 推送 tag 触发 release workflow：它在钉死的 commit 上 clone 上游、
  重新生成 `Recipes.java`、构建 APK，并挂到 GitHub Release 上。钉死的上游 SHA 同时存在于
  `catalog/filters.json`（`sources.recipe-lab.fetched_rev`）和 `.github/workflows/release.yml`
  （`UPSTREAM_SHA`）；`TestPinnedUpstream` 在两者漂移时失败。你通常不该改 `.github/`——若必须
  移动 pin，请与维护者协调。
- **上机验证仍归你。** CI 绿只证明文件一致，不证明颜色对。走 USB / Sony-PMCA-RE 通道
  （`INSTALL.md`）装进去，存储配方，**关机再开机**（重启后消失的配方说明根本没写进去），
  在可丢弃素材上拍 JPEG，满意后把 `verified` 翻成 `true` 并在 `note` 记上机型 + 固件号。

---

## 9. 「做不到」清单——声称配方前先读

这台相机的设置存储区没有任何字段承载以下效果，也没有 Picture Profile / LUT 通道。
`docs/MAPPING-RECIPES.md` §2.2 有完整 13 项。人们最常想硬凑、而**绝不能**做的是：

- **真·彩色颗粒** —— 只有 `pe=7` rough-mono 给颗粒，且是黑白。别发「彩色颗粒」配方；高 ISO
  噪点不是颗粒纹理。
- **漏光 / 暗角** —— 没有叠加层。唯一近似是 `pe=1` toy-camera，自带暗角 + 偏色。标成近似，
  永远别写成「漏光」。
- **色调曲线 / S 曲线 / Log** —— a6000 存不下曲线。无路可走。
- **真·青橙分色调** —— 只有全局 `ab`/`gm`；你没法把青放阴影、橙放高光。干净全局青（如
  `teal-mood`）是诚实的；声称分色调是不诚实的。
- **HSL 分色相、LUT、局部/渐变、clarity、双重曝光、色散** —— 都无法表达。

> **实话实说。** 如果你的目标观感依赖上面任一项，在 `note` 里讲明，并只描述相机真能存储的
> 近似。发布声称硬件做不到的效果的配方，是本仓库唯一不会做的事。

权威映射与完整约束清单见 `docs/MAPPING-RECIPES.md`。
