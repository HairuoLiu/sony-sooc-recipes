# 单色风格
<p align="center"><a href="monochrome.md">English</a> · <b>简体中文</b></p>

## 概要

| | |
|---|---|
| 应用名 | 单色风格 |
| 包名 | com.hairuoliu.sonysoocrecipes.monochrome |
| **随哪一档分发** | 仅完整版安装器 —— 免费的 Base 里没有 |
| 已编译配方数 | 32 |
| 来源组 | 7 个（一份横跨 Fuji Sim、Kodak、Ricoh GR、Leica、Pana / Olympus、Other Stocks、Ilford 的筛选清单） |
| 目录版本 | 0.6.0（更新于 2026-09-13） |

**一句话：** 这个包编译了 **32** 款黑白配方——目录里所有 `tone: mono` 的黑白与褐调观感——从七个组里收进一个应用。它不是单品牌包，而是一份**按滤镜 id 手挑的清单**：这些配方来自 Fuji Sim（Acros）、柯达、理光 GR、徕卡、松下 / 奥林巴斯（L.单色D）、Other Stocks 和伊尔福，因为黑白观感本来就是多个品牌各自贡献，而不是某一家的专属领地。

## 这些数字怎么来的

和别的包不同，单色包**不拥有任何一个组**。它是一份手挑的滤镜清单——共 35 个 id，从七个组里取：

- **Fuji Sim** —— Acros 及其黄 / 红 / 绿滤镜变体；
- **Kodak** —— Tri-X 400、T-Max、Tri-X 1600（迫冲）、Eastman Double-X 5222、Plus-X Pan 125；
- **Ricoh GR** —— 高反差、硬调、柔调黑白，外加森山风；
- **Leica** —— Monochrom、黑白高反差 / 自然、Greg WLM、IA、Blu、Sel、褐调；
- **Pana / Olympus** —— L.Monochrome D；
- **Other Stocks** —— 安布罗式湿版、宝丽来 Type 100 褐调、Rollei Ortho 25、Svema Type-42；
- **Ilford** —— HP5、FP4、Delta 100、Delta 3200、Pan F 50。

其中三个 id（`fs-acros`、`fs-gr-hcbw`、`fs-gr-moriyama`）是 `film-studio-matrix` 条目——仅登记、不可再分发——编译不进任何东西，所以清单里的 35 个 id 变成 **32 款已编译配方**。

按清单挑的包刻意跨组，这意味着它**按设计就要和品牌包共享配方**。品牌包保留自己的黑白配方（Leica Style 里仍有 Leica Monochrom；Kodak Style 里仍有 Tri-X），而这个包把同样的配方重新收在一起并列呈现。这不是重复——全量版、每个品牌包、这个包都读同一份 catalog——它只是同一份数据的另一种*视图*。它取的组里有两组（`pana-olympus`、`other-stocks`）平时出于商标原因不进任何品牌包；这里按 id 一次取一两个，正是它作为「清单包」而非普通「组包」存在的原因。

## 配方

这里的每一款都是黑白或褐调观感。除少数外，全部落在相机的 **MONO** 或 **SEPIA** 创意风格上（例外用 **rough-mono** 图片效果 `pe=7` 出粗颗粒黑白）。下面的关键设置直接取自 catalog，与应用实际应用的内容一致。

| 名称 | 中文 | 类型 | 是什么 / 关键设置 |
|------|------|------|---------------------------|
| Acros | 黑白 ACROS | 黑白 | Acros —— Creative **MONO**, sat 0, con 1, sharp 1, DRO Lv6。 |
| Acros +Ye (yellow filter) | ACROS 黄滤镜 | 黑白 | Acros +Ye（黄滤镜）—— Creative **MONO**, sat 0, con 1, sharp 1, DRO Lv6。 |
| Acros +R (red filter) | ACROS 红滤镜 | 黑白 | Acros +R（红滤镜）—— Creative **MONO**, sat 0, con 0, sharp 0, PE 7, DRO Lv6。 |
| Acros +G (green filter) | ACROS 绿滤镜 | 黑白 | Acros +G（绿滤镜）—— Creative **MONO**, sat 0, con 1, sharp 1, DRO Lv6。 |
| Sepia | 棕褐色 | 黑白 | Sepia —— Creative **SEPIA**, sat 0, con 0, sharp 0, DRO Lv6。 |
| Kodak Tri-X 400 | 柯达 Tri-X 400 | 黑白 | Kodak Tri-X 400 —— Creative **MONO**, sat 0, con 2, sharp 2, EV 1, DRO Lv6。 |
| Kodak T-Max | 柯达 T-Max | 黑白 | Kodak T-Max —— Creative **MONO**, sat 0, con 2, sharp 3, DRO Lv6。 |
| Kodak Tri-X 1600 (pushed) | 柯达 Tri-X 1600（迫冲） | 黑白 | Kodak Tri-X 1600（迫冲）—— Creative **MONO**, sat 0, con 0, sharp 0, PE 7, EV 1, DRO Lv6。 |
| Kodak Eastman Double-X 5222 | 柯达 Eastman Double-X 5222 | 黑白 | 从《辛德勒的名单》到《罗马》都在用的黑白电影负片：硬朗、颗粒感、高反差。现有目录有 Tri-X 但没有这款 cine 黑白。本仓库自写，未在实机验证。 —— Creative **MONO**, sat 0, con 2, sharp 1, DRO Lv3。 |
| Kodak Plus-X Pan 125 | 柯达 Plus-X 125 | 黑白 | 比 Tri-X 更柔软细腻的经典黑白负片（1979 年过期版）：反差平、锐度收。与 Double-X 一软一硬正好互补。本仓库自写，未在实机验证。 —— Creative **MONO**, sat 0, con 0, sharp -1, DRO Lv4。 |
| GR Hi-Contrast B&W | GR 高反差黑白 | 黑白 | GR Hi-Contrast B&W —— Creative **MONO**, sat 0, con 3, sharp 1, PE 7, DRO Lv6。 |
| GR Hard Monotone | GR 硬调黑白 | 黑白 | GR Hard Monotone —— Creative **MONO**, sat 0, con 2, sharp 2, DRO Lv6。 |
| GR Soft Monotone | GR 柔调黑白 | 黑白 | GR Soft Monotone —— Creative **MONO**, sat 0, con -2, sharp -1, DRO Lv6。 |
| GR Moriyama (grainy B&W) | GR 森山风 | 黑白 | 本仓库新写的配方，用于补上游唯一缺口（胶片工坊有、上游项目没有）。未在实机上验证，落地前请先在可丢弃素材上试拍。 —— Creative **MONO**, sat 0, con 3, sharp 1, PE 7, EV -1, DRO Lv6。 |
| Leica Monochrom | 徕卡 Monochrom | 黑白 | Leica Monochrom —— Creative **MONO**, sat 0, con 2, sharp 1, DRO Lv6。 |
| Leica B&W HC | 徕卡 黑白高反差 | 黑白 | 徕卡风格的高反差黑白。参考测量：纯黑白、反差 1.20。本仓库自写，未在实机验证。 —— Creative **MONO**, sat 0, con 2, sharp 1, DRO Lv1。 |
| Leica B&W Natural | 徕卡 黑白自然 | 黑白 | 徕卡风格的自然反差黑白。参考测量：纯黑白、反差 1.02。本仓库自写，未在实机验证。 —— Creative **MONO**, sat 0, con 0, sharp 0, DRO Lv4。 |
| Leica Greg WLM (warm mono) | 徕卡 Greg WLM（暖调黑白） | 黑白 | 暖调黑白：轻微琥珀偏移（测量 R-G +0.014）、反差适中。原名 Greg WLM 保留在名称里。本仓库自写，未在实机验证。 —— Creative **MONO**, sat 0, con 1, sharp 0, DRO Lv3。 |
| Leica IA (hard mono) | 徕卡 IA（硬黑白） | 黑白 | 徕卡包里反差最高的一支黑白（测量 1.25），DRO 关死。比 B&W HC 更硬一档。本仓库自写，未在实机验证。 —— Creative **MONO**, sat 0, con 3, sharp 1。 |
| Leica Blu (cool mono) | 徕卡 Blu（冷调黑白） | 黑白 | 冷调黑白：测量显示近黑白（饱和 0.19）带蓝倾向。MONO + 蓝向白平衡微调。本仓库自写，未在实机验证。 —— Creative **MONO**, sat 0, con 0, sharp 0, DRO Lv3。 |
| Leica Sel (pale silver) | 徕卡 Sel（淡银） | 黑白 | 淡银灰调：测量饱和 0.14、黑位抬、反差平。整体提亮一档。本仓库自写，未在实机验证。 —— Creative **MONO**, sat 0, con 0, sharp -1, EV 1, DRO Lv5。 |
| Leica Sepia | 徕卡 褐调 | 黑白 | 暖褐调：测量饱和 0.20、暖偏（B-G -0.051）。索尼自带 SEPIA 风格直接用。本仓库自写，未在实机验证。 —— Creative **SEPIA**, sat 0, con 0, sharp 0, DRO Lv4。 |
| Pana L.Monochrome D | 松下 L.单色D | 黑白 | Pana L.Monochrome D —— Creative **MONO**, sat 0, con 3, sharp 1, DRO Lv6。 |
| Ambrotype (wet plate) | 安布罗式湿版 | 黑白 | 1850 年代的湿版火棉胶工艺：暖褐近黑白、反差软、黑位抬。MONO 风格 + 琥珀白平衡微调制造暖调。本仓库自写，未在实机验证。 —— Creative **MONO**, sat 0, con 0, sharp -1, DRO Lv5。 |
| Polaroid Type 100 Sepia | 宝丽来 Type 100 褐调 | 黑白 | 宝丽来撕拉片的褐调版本（2009 年）：整体提亮、反差极软。参考测量：反差 0.74、饱和 0.27。本仓库自写，未在实机验证。 —— Creative **SEPIA**, sat 0, con -2, sharp -1, EV 1, DRO Lv6。 |
| Rollei Ortho 25 | Rollei Ortho 25 | 黑白 | 正色黑白胶片：红光记录不到、天空亮、肤色深。索尼做不了正色响应，这里只保留它的高反差硬朗观感，红通道行为无法复现。本仓库自写，未在实机验证。 —— Creative **MONO**, sat 0, con 2, sharp 1, DRO Lv2。 |
| Svema Type-42 | Svema Type-42 | 黑白 | 苏联 Svema 黑白胶片（1991 年过期）：测量显示基本纯黑白（饱和 0.11）、反差高（1.28）。本仓库自写，未在实机验证。 —— Creative **MONO**, sat 0, con 2, sharp 0, DRO Lv3。 |
| Ilford HP5 | 伊尔福 HP5 | 黑白 | Ilford HP5 —— Creative **MONO**, sat 0, con 1, sharp 0, EV 1, DRO Lv6。 |
| Ilford FP4 | 伊尔福 FP4 | 黑白 | Ilford FP4 —— Creative **MONO**, sat 0, con 1, sharp 1, DRO Lv6。 |
| Ilford Delta 100 | 伊尔福 Delta 100 | 黑白 | Ilford Delta 100 —— Creative **MONO**, sat 0, con 1, sharp 1, DRO Lv6。 |
| Ilford Delta 3200 | 伊尔福 Delta 3200 | 黑白 | Ilford Delta 3200 —— Creative **MONO**, sat 0, con 3, sharp -2, EV 2, DRO Lv6。 |
| Ilford Pan F 50 | 伊尔福 Pan F 50 | 黑白 | Ilford Pan F 50 —— Creative **MONO**, sat 0, con 2, sharp 2, DRO Lv6。 |

## 诚实声明 —— 这些配方做不到什么

这些都是社区推导的*近似*，不是任何胶片的真实响应。引擎天花板与本项目别处一样：2014 年的机身存不下色调曲线，所以每款观感只能用设置存储区真正容得下的东西拼。对黑白具体来说：

- **没有真正的银盐颗粒纹理。** 那些带颗粒的观感（Acros +R、Tri-X 1600、GR 高反差和森山风）靠相机的 `rough-mono` 图片效果来出*一种*颗粒，但那是引擎唯一的颗粒源，不是某款胶片的颗粒。彩色颗粒做不到——相机没有这种旋钮。
- **正色响应和分色调行为无法复现。** Rollei Ortho 25 的「不感红」、徕卡家族的暖 / 冷调，都只保留*性格*；底层的光谱或分影调行为超出引擎能力。
- **大多未经实机验证。** 少数上游配方（Acros、伊尔福几款、柯达 Tri-X / T-Max）与上游项目逐值对齐、可信任；Leica Monochrom 在 catalog 里标着 `verified: true`。本仓库自写的那批（`gr-moriyama`、柯达 Double-X / Plus-X、徕卡黑白家族、安布罗式、Rollei Ortho 25、Svema、宝丽来 Type 100 褐调）都是 `verified: false`——因为最后一步（这些数值在机身上到底落得如何）离了机身观察不到。每款的状态记在 `catalog/filters.json` 的 `verified` 字段里，不在屏幕上。

**怎么补上：** 日光下拍一张灰卡，应用某款观感，看渲染出的灰；在配方里微调 `con` / `sharp` / 白平衡，再重应用。

## 来源与许可

这个包**没有引入任何新的配方值**。它只是对全量版和每个品牌包已经在发那份 catalog 的另一种选法——同样的参数集、同样的来源（77 款上游逐值对齐、72 款自写），只是按 `tone: mono` 归集，而不是按品牌。它的启动图标是**用户提供的封面图**——本包是跨品牌选集、没有单一产品可如实拍摄，所以在 2026-09-27 之前用的是仓库里画的光圈（与 `cinema` 包的手绘图标同理），2026-09-28 起换成一张用户提供的黑白胶片条绘图，同样抠图后放在与其他包一致的深色圆角底板上。完整的来源与许可边界见 **[NOTICE.md](../../NOTICE.md)**。

---

**目录菜单：** [README.md](README.md) · [README.zh-CN.md](README.zh-CN.md)
**品牌包索引：** [../BRAND-PACKS.md](../BRAND-PACKS.md) · [../BRAND-PACKS.zh-CN.md](../BRAND-PACKS.zh-CN.md)
