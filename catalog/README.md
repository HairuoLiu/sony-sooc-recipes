# 滤镜注册表

`filters.json` 是本仓库的**唯一事实来源**。`Recipes.java` 由它生成，APK 由
`Recipes.java` 编译。要加滤镜，改这里 —— 不要改 Java。

```bash
python tools/validate_catalog.py      # 校验
python tools/gen_recipes.py --stdout  # 看生成结果
```

---

## 顶层字段

| 字段 | 说明 |
|---|---|
| `version` | 注册表格式版本 |
| `engines` | 两种引擎的说明、限制与许可 |
| `sources` | 每个上游仓库的作者、许可、取得版本、可否再分发 |
| `style_constants` | 创意风格的存下来枚举值（来自上游反向工程） |
| `pe_constants` | 图片效果的运行时索引 |
| `dro_constants` | DRO：`0` 关 / `6` 自动 |
| `groups` | 品牌分组，**顺序即 APK 内的分组顺序** |
| `filters` | 全部滤镜 |

---

## 单条滤镜

```json
{
  "id": "kodak-gold-200",
  "name": "Kodak Gold 200",
  "name_zh": "柯达金 200",
  "group": "kodak",
  "engine": "recipe-lab",
  "source": "recipe-lab",
  "tone": "color",
  "verified": true,
  "cross_ref": null,
  "note": null,
  "recipe": {
    "style": "STD", "sat": 2, "con": 1, "sharp": 0, "matrix": 0,
    "wb": { "mode": "AUTO", "kelvin": 0, "ab": 3, "gm": 1 },
    "pe": 0, "sub": 0, "ev": 1, "dro": 6
  }
}
```

| 字段 | 必填 | 取值 | 说明 |
|---|---|---|---|
| `id` | ✔ | kebab-case，全表唯一 | 生成器与文档的引用键 |
| `name` | ✔ | 字符串 | 相机应用里显示的名字 |
| `name_zh` | | 字符串 | 中文名，仅供浏览器显示 |
| `group` | ✔ | `groups[].id` 之一 | 分组 |
| `engine` | ✔ | `recipe-lab` \| `film-studio-matrix` | 见下 |
| `source` | ✔ | `recipe-lab` \| `authored-here` \| `film-studio` | 来源 |
| `tone` | ✔ | `color` \| `mono` | 浏览器筛选用 |
| `verified` | ✔ | `true` \| `false` | **是否已在真机上验证** |
| `cross_ref` | | 另一个 `id` | 跨引擎的对应款 |
| `note` | | 字符串 | 浏览器里显示的备注 |
| `recipe` | 见下 | 对象 | 仅 `recipe-lab` 需要 |
| `strengths` | 见下 | `[30,50,70,100]` | 仅 `film-studio-matrix` 需要 |

### `engine` 的两种取值

| 值 | 含义 | 会进 APK 吗 |
|---|---|---|
| `recipe-lab` | 写相机设置存储区。需要 `recipe` 对象 | **会** |
| `film-studio-matrix` | 色彩矩阵 / Gamma 路线。**仅登记**，不含参数 | 不会 |

`film-studio-matrix` 条目**不允许**带 `recipe` 字段 —— `validate_catalog.py` 会直接报错。
原因是双重的：上游许可是非商用，且那批数值是为另一条管线拟合的，搬过来在技术上不成立。
见 [NOTICE.md](../NOTICE.md)。

### `recipe` 的字段约束

| 字段 | 范围 | 备注 |
|---|---|---|
| `style` | `STD` `VIVID` `NEUTRAL` `PORTRAIT` `LANDSCAPE` `MONO` `CLEAR` `DEEP` `LIGHT` `SUNSET` `NIGHT` `AUTUMN` `SEPIA` | |
| `sat` `con` `sharp` | −16…+16 | 菜单只到 ±3；超出部分相机会接受，但菜单显示最接近值 |
| `matrix` | `0` \| `1` | `1` = PP3 备用色彩矩阵 |
| `wb.mode` | `AUTO` \| `K` | `AUTO` 时 `kelvin` 必须为 `0` |
| `wb.kelvin` | 2500…9900 | |
| `wb.ab` `wb.gm` | −7…+7 | `ab` 正 = 琥珀，`gm` 正 = 绿 |
| `pe` | `0`…`13` | `pe != 0` 时相机忽略创意风格，且只用 JPEG |
| `sub` | 视 `pe` | `pe=off` 时 `sub` 必须为 `0` |
| `ev` | −5…+5 | 1/3 EV 步进数 |
| `dro` | `0`…`6` | `0` 关 / `1`–`5` 档位 / `6` 自动 |

---

## 分组顺序是有约束的

`recipe-lab` 条目**必须按 `groups` 声明的顺序连续排列**。生成器据此产出
`GROUP_START` / `GROUP_COUNT` 静态块；断裂会直接报错。

`film-studio-matrix` 条目可以和同品牌的 `recipe-lab` 条目交错 —— 它们不参与生成，
交错反而让浏览器里每个品牌更集中。

---

## 校验器的三种输出级别

| 级别 | 含义 | 会让 `validate_catalog.py` 失败吗 |
|---|---|---|
| `ERROR` | 注册表坏了或许可声明不诚实 | **会** |
| `warn` | 发布前值得看一眼 | 不会 |
| `note` | **引擎的既有行为，不是缺陷**。例如：饱和度超出菜单滑块范围；`pe != 0` 时创意风格失效。上游自家的配方就是有意这么写的 | 不会 |

`note` 是给**写新配方的人**看的 —— 它告诉你「你设了这个，但它不会有效果」。

---

## 品牌包元数据（`packs.json`）

`filters.json` 描述「有哪些配方」；`packs.json` 描述「这些配方怎么按品牌切成一份份独立 APK」。
它也是品牌包构建矩阵的**唯一事实来源**：`.github/workflows/release.yml` 在运行时从这份文件
推导矩阵，绝不把包列表抄进 YAML。详见 [../docs/BRAND-PACKS.md](../docs/BRAND-PACKS.md)。

### 顶层字段

| 字段 | 说明 |
|---|---|
| `package_base` | 基包名 `com.hairuoliu.sonysoocrecipes`；每个包的包名是它加一段 `.id` |
| `packs` | 品牌包数组，每个包一项 |
| `unassigned_groups` | 故意不进任何包的组，附理由（不是漏写） |

### 一个包（`packs[]` 的一项）

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | ✔ | 包标识，也是包名后缀、源码子目录名、图标集目录名 |
| `app_name` | ✔ | 装到相机上显示的名字，约定用 `<Brand> Looks` 形式（见 BRAND-PACKS §8） |
| `groups` | ✔ | 该包编译进的 `groups[].id` 列表，**必须同属一个品牌** |
| `icon_set` | ✔ | 图标集目录名，对应 `assets/app-icon-packs/<icon_set>/` |

`groups` 引用的组必须存在于 `filters.json` 的 `groups`，且是单品牌组。**跨两个品牌的组**
（如 `canon-nikon`、`pana-olympus`）不能直接做包，要先拆成每个品牌一个组。`film-studio-matrix`
条目编译不进任何包，所以一个组若只含这类条目，该包这一组会贡献 0 款可编译配方。

### `unassigned_groups`

这些是刻意不进任何包的组，仍可在全量版 App 里用到。记在这里而不是删掉，好让缺口显在数据里：

| 组 | 理由 |
|---|---|
| `canon-nikon` | 跨两个品牌——要先拆成各一个包 |
| `pana-olympus` | 跨两个品牌——同理要拆 |
| `other-stocks` | 混血胶片，无单一品牌 |
| `cine` | 不是相机品牌，是电影感风格家族 |
| `app-look` | 不是相机品牌，是社交 / App 滤镜风 |

新增一个包时，往 `packs` 加一项即可；`release.yml` 的矩阵会自动纳入，无需改工作流。
