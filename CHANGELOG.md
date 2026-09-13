# Changelog

每个条目记一次上传到 GitHub 的版本。版本号遵循语义化版本，但**配方值本身的变化**也视
为 minor——对使用者来说，一款滤镜的参数变了，比加个函数影响更大。

发布前必须跑 `python tests/run_all.py`，五道关卡全绿才允许打 tag。

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

**测试**
- `tests/test_catalog.py`：31 条用例，含结构不变量、参数范围、来源诚实性、生成器往返。
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
