# 加一款滤镜

整个流程只有一步是真正「需要动脑」的：**想清楚参数**。其余全是自动的。

---

## 1. 确认目标引擎

先回答：这款味道能不能用**相机存得下来的东西**拼出来？

Recipe Lab 引擎能用的只有这些（这是全部，没有别的）：

| 参数 | 字段 | 范围 | 说明 |
|---|---|---|---|
| 创意风格 | `style` | `STD` `VIVID` `NEUTRAL` `PORTRAIT` `LANDSCAPE` `MONO` `CLEAR` `DEEP` `LIGHT` `SUNSET` `NIGHT` `AUTUMN` `SEPIA` | 存下来的是枚举值 |
| 饱和度 | `sat` | −16…+16 | 菜单只到 ±3，超出部分相机会接受但菜单显示最接近值 |
| 对比度 | `con` | −16…+16 | 同上 |
| 锐度 | `sharp` | −16…+16 | 同上 |
| 色彩矩阵 | `matrix` | `0` / `1` | `1` = PP3 备用色彩矩阵（约 +45% 彩度，蓝绿串色）。只在特定风格上生效 |
| 白平衡模式 | `wb.mode` | `AUTO` / `K` | `K` 时要给 `wb.kelvin` |
| 白平衡 · 色温 | `wb.kelvin` | 2500…9900 | |
| 白平衡 · 琥珀/蓝 | `wb.ab` | −7…+7 | 正 = 琥珀(A)，负 = 蓝(B) |
| 白平衡 · 绿/品红 | `wb.gm` | −7…+7 | 正 = 绿(G)，负 = 品红(M) |
| 图片效果 | `pe` | `0`…`13` | 见下表 |
| 效果子参数 | `sub` | 视 `pe` 而定 | |
| 曝光补偿 | `ev` | −5…+5（1/3 EV 步进） | 存的是步进数，不是 EV 值 |
| DRO | `dro` | `0` 关 / `1`–`5` 档位 / `6` 自动 | |

`pe` 取值表（`Picture Effect`，存下来的就是运行时的索引）：

| 值 | 名称 | `sub` |
|---|---|---|
| 0 | off | — |
| 1 | toy-camera | 0 normal · 1 cool · 2 warm · 3 green · 4 magenta |
| 2 | pop-color | — |
| 3 | posterization | 0 color · 1 b&w |
| 4 | retro-photo | — |
| 5 | soft-high-key | 0 blue · 1 pink · 2 green |
| 6 | part-color | 0 red · 1 green · 2 blue · 3 yellow |
| 7 | **rough-mono**（粗颗粒黑白） | — |
| 8 | soft-focus | — |
| 9 | hdr-art | — |
| 10 | richtone-mono | — |
| 11 | miniature | — |
| 12 | illust | — |
| 13 | watercolor | — |

**用不了 `pe` 拼不出来的效果，就别硬凑**。Log 曲线、色调黑白、颗粒都不是这台相机
能存的——承认做不到，比放一个不准的近似进去更有价值。

---

## 2. 想参数：从参考帧反推

1. **找参考**。一张你想要的成品图，或一款已知胶片/机身的样片。
2. **先判黑白还是彩色**。黑白一律 `style: MONO`，然后只调 `con` / `pe`。
3. **定风格底子**。偏艳丽 → `VIVID`；偏清淡 → `NEUTRAL`；肤色优先 → `PORTRAIT`；
   通透干净 → `CLEAR`；厚重 → `DEEP`；高调 → `LIGHT`。
4. **调饱和与对比**。两者的组合就能表达大部分「味道」。
5. **微调色偏**。暖调 → `ab` 正；冷调 → `ab` 负；绿调 → `gm` 正。
6. **需要眩光/褪色感**才上 `pe`，并记住：**`pe` 一开，`sat`/`con`/`sharp`/`matrix` 全部失效**。
   这不是 bug，是相机行为。
7. **需要压暗背景**才动 `ev` 和 `dro`。

### 上游的做法可以参考

`catalog/filters.json` 里现成的 78 款就是最好的参照系。几条经验：

- 柯达彩色负片系列普遍 `ab` 取正 1–3，配 `ev` +1 到 +2（明亮、暖、略过曝的味道）
- 富士 Classic Chrome 是 `NEUTRAL` + `sat -5` + `con 2` + `ab -1` + `ev -1`
- 褪色怀旧系（Nostalgic Neg / GR Retro / Polaroid）都用 `pe: 4`（retro-photo）
- 重颗粒黑白（Tri-X 1600 / GR Hi-Contrast）用 `pe: 7`（rough-mono）
- 富士 Pro 400H 是唯一用到 `sub` 的：`pe: 5` + `sub: 2`（soft high-key 绿调）

---

## 3. 写进注册表

编辑 `catalog/filters.json`，在对应品牌分组**内部**追加一条（顺序必须是分组连续，
生成器依赖这一点）：

```json
{ "id": "kodak-portra-160-vc", "name": "Kodak Portra 160 VC", "group": "kodak",
  "engine": "recipe-lab", "source": "authored-here", "tone": "color", "verified": false,
  "note": "在可丢弃素材上试拍后再标 verified",
  "recipe": { "style": "STD", "sat": 1, "con": 1, "sharp": 0, "matrix": 0,
              "wb": { "mode": "AUTO", "kelvin": 0, "ab": 2, "gm": 0 },
              "pe": 0, "sub": 0, "ev": 1, "dro": 6 } }
```

字段说明：

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | ✔ | 全表唯一，kebab-case |
| `name` | ✔ | 应用里显示的名字 |
| `name_zh` | | 中文名，给人看的 |
| `group` | ✔ | 必须是 `groups` 里声明过的 id |
| `engine` | ✔ | `recipe-lab`（会被编译进 APK）/ `film-studio-matrix`（仅登记） |
| `source` | ✔ | `recipe-lab`（上游原有）/ `authored-here`（本仓库新写）/ `film-studio`（仅登记） |
| `tone` | ✔ | `color` / `mono`，用于浏览器筛选 |
| `verified` | ✔ | **是否已在真机上验证过**。自己新写的一律填 `false` |
| `cross_ref` | | 指向另一引擎里的对应款 |
| `recipe` | 引擎为 `recipe-lab` 时必填 | 见上表 |

---

## 4. 跑三道关卡

```bash
python tools/validate_catalog.py
python tools/gen_recipes.py --check
python tools/check_fidelity.py --upstream build/upstream-Recipes.java
```

第 1 关会告诉你参数是否越界；它会输出 **note** 而不是 error 的，是引擎的既有行为
（例如饱和度超出菜单滑块范围、`pe` 让创意风格失效），不是错误。

第 3 关会把 `authored-here` 的条目算作「expected added」，不该失败。

---

## 5. 重新生成并构建

```bash
python tools/gen_recipes.py --fork build/recipe-lab-sony-pmca
tools/build_apk.sh
```

---

## 6. 上机验证（**不能跳过**）

任何东西都替代不了真机。CI 全绿**只证明文件一致，不证明色彩正确**。

1. 用 [通道 A](INSTALL.md#通道-ausb--sony-pmca-re) 装进相机
2. 打开 Recipe Lab，波轮滚到新配方
3. 按中心键存储，屏幕上方出现 `Stored x value`
4. **关机再开机** —— 这是真正的验证。重启后消失的配方说明根本没存进去
5. 在可丢弃的场景拍 JPEG 看效果
6. 满意了，把 `verified` 改成 `true`，`note` 里写上验证的机型和固件号

> 上游项目里查不到的行为、按键、色调，都必须在真机上跑一遍才知道。
> 一个绿 CI 不等于这款滤镜好看。

---

## 7. 提交

```
feat(recipes): add Kodak Portra 160 VC

Closes #12
```

一次加一款，或一次加同一品牌的一组。别在一个提交里混入无关的参数改动——
第 3 关会点名每一处数值漂移，混在一起不好定位。
