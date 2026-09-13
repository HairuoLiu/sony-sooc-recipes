# 配方参数空间映射手册（MAPPING-RECIPES）

> 用途：把「想要的视觉风格」映射到 a6000 那一代老索尼微单**实际存得下、菜单里能复现**的设置项上。
> 适用机型：a6000 / a6300 / a6500 / a5100 / a7 II（2016 年末前机型，之后签名固件装不了）。
> 引擎边界：本仓库只用 **recipe-lab（设置存储区引擎）** 的可达项；film-studio-matrix 是另一套硬件矩阵引擎，本文档的「参数手段」仅指 recipe-lab 可达项。

---

## 增补（写在前面）

第 1 部分的清单是**最初的 93 款**。此后新增 6 款，达 **99 款 / 13 组**：

| 新增 | 组 | 关键手段 |
|---|---|---|
| `kodak-vision2-500t` | kodak | NEUTRAL 底 + K 3200 + gm+1，比既有 Vision3 500T 更绿、更平 |
| `toy-camera-warm` | app-look | **pe=1** 玩具相机（全库首次使用），sub=2 暖调 |
| `toy-camera-cool` | app-look | **pe=1**，sub=1 冷调 |
| `part-color-red` | app-look | **pe=6** 局部色彩（全库首次使用），sub=0 红 |
| `posterization-color` | app-look | **pe=3** 海报化（全库首次使用），sub=0 彩色 |
| `teal-mood` | app-look | pe=0，全局 ab−2 / gm+1 的干净青调 |

因此 1.2 末尾「`pe` 使用现状」的统计已经过期：现在被用到的是
`0 / 1 / 3 / 4 / 5 / 6 / 7`，仍未使用的为 `2 / 8 / 9 / 10 / 11 / 12 / 13`。

**这一批的起因**：有人问能不能把手机滤镜 App「Liit」的滤镜搬进来。结论是不能，原因写在
`NOTICE.md`——它是闭源商业软件，且其 LUT/曲线在 a6000 上根本没有承载通道。能做的是
反过来问：手机 App 那些观感里，**相机其实做得到而我们一直没做的是什么**。答案是索尼的
「照片效果」引擎——1.3 节点名的 pe=1/3/6 空白，就是这么被填上的。

---

## 0. 引擎天花板（决定映射可行边界）

a6000 上**没有 Picture Profile 菜单，存不下任何色调曲线**。配方只能用相机「存得下来」的项拼出来，所有风格都是**近似**，不是别家色彩科学的复制品。

可用维度（全部为全局、不可分区域/分通道）：

| 维度 | 取值 | 说明 |
|---|---|---|
| `style` 创意风格 | STD(1) VIVID(2) NEUTRAL(3) PORTRAIT(4) LANDSCAPE(5) MONO(6) CLEAR(7) DEEP(8) LIGHT(9) SUNSET(10) NIGHT(11) AUTUMN(12) SEPIA(13) | 底色调 |
| `sat` / `con` / `sharp` | 相对创意风格默认值增减 | 三滑块 |
| `matrix` | 0=标准，1=索尼未公开的另一套（实测更「胶片味」/浓郁） | 隐藏开关 |
| `wb.mode` | AUTO（kelvin=0）或 K（kelvin=具体色温） | 白平衡 |
| `wb.ab` / `wb.gm` | A+ / B- ，G+ / M- | 白平衡微调 |
| `pe` 图片效果 | 0=off … 13=watercolor | **pe≠0 时创意风格失效** |
| `sub` / `ev` / `dro` | 子档 / 曝光补偿（1 单位=1/3EV）/ DRO | 辅助 |

---

## 第 1 部分：覆盖度盘点

### 1.1 完整清单（93 款，按 group）

总数：recipe-lab 引擎 78 款 + film-studio-matrix 引擎 15 款（富士 10 + 理光 5）。

**sony（recipe-lab, 8）**

| id | name | group | tone | engine | source |
|---|---|---|---|---|---|
| factory-st | FACTORY (ST) | sony | color | recipe-lab | recipe-lab |
| sony-pt-portrait | Sony PT (portrait) | sony | color | recipe-lab | recipe-lab |
| sony-nt-neutral | Sony NT (neutral) | sony | color | recipe-lab | recipe-lab |
| sony-vv-vivid | Sony VV (vivid) | sony | color | recipe-lab | recipe-lab |
| sony-vv2 | Sony VV2 | sony | color | recipe-lab | recipe-lab |
| sony-fl-film-like | Sony FL (film-like) | sony | color | recipe-lab | recipe-lab |
| sony-in-instant | Sony IN (instant) | sony | color | recipe-lab | recipe-lab |
| sony-sh-soft-high-key | Sony SH (soft high-key) | sony | color | recipe-lab | recipe-lab |

**fuji-sim（recipe-lab, 16）**

| id | name | group | tone | engine | source |
|---|---|---|---|---|---|
| provia | Provia | fuji-sim | color | recipe-lab | recipe-lab |
| velvia | Velvia | fuji-sim | color | recipe-lab | recipe-lab |
| astia | Astia | fuji-sim | color | recipe-lab | recipe-lab |
| classic-chrome | Classic Chrome | fuji-sim | color | recipe-lab | recipe-lab |
| classic-negative | Classic Negative | fuji-sim | color | recipe-lab | recipe-lab |
| nostalgic-neg | Nostalgic Neg | fuji-sim | color | recipe-lab | recipe-lab |
| reala-ace | Reala Ace | fuji-sim | color | recipe-lab | recipe-lab |
| pro-neg-std | Pro Neg Std | fuji-sim | color | recipe-lab | recipe-lab |
| pro-neg-hi | Pro Neg Hi | fuji-sim | color | recipe-lab | recipe-lab |
| eterna | Eterna | fuji-sim | color | recipe-lab | recipe-lab |
| eterna-bleach-bypass | Eterna Bleach Bypass | fuji-sim | color | recipe-lab | recipe-lab |
| acros | Acros | fuji-sim | mono | recipe-lab | recipe-lab |
| acros-ye | Acros +Ye | fuji-sim | mono | recipe-lab | recipe-lab |
| acros-r | Acros +R | fuji-sim | mono | recipe-lab | recipe-lab |
| acros-g | Acros +G | fuji-sim | mono | recipe-lab | recipe-lab |
| sepia | Sepia | fuji-sim | mono | recipe-lab | recipe-lab |

**fuji-film（recipe-lab, 5）**

| id | name | group | tone | engine | source |
|---|---|---|---|---|---|
| fuji-pro-400h | Fuji Pro 400H | fuji-film | color | recipe-lab | recipe-lab |
| fuji-fortia-50 | Fuji Fortia 50 | fuji-film | color | recipe-lab | recipe-lab |
| fuji-superia-400 | Fuji Superia 400 | fuji-film | color | recipe-lab | recipe-lab |
| fuji-c200 | Fuji C200 | fuji-film | color | recipe-lab | recipe-lab |
| fuji-natura-1600 | Fuji Natura 1600 | fuji-film | color | recipe-lab | recipe-lab |

**kodak（recipe-lab, 14）**

| id | name | group | tone | engine | source |
|---|---|---|---|---|---|
| kodak-portra-160 | Kodak Portra 160 | kodak | color | recipe-lab | recipe-lab |
| kodak-portra-400 | Kodak Portra 400 | kodak | color | recipe-lab | recipe-lab |
| kodak-portra-800 | Kodak Portra 800 | kodak | color | recipe-lab | recipe-lab |
| kodak-gold-200 | Kodak Gold 200 | kodak | color | recipe-lab | recipe-lab |
| kodak-ultramax-400 | Kodak Ultra Max 400 | kodak | color | recipe-lab | recipe-lab |
| kodak-colorplus-200 | Kodak Color Plus 200 | kodak | color | recipe-lab | recipe-lab |
| kodak-ektar-100 | Kodak Ektar 100 | kodak | color | recipe-lab | recipe-lab |
| kodak-ektachrome-e100 | Kodak Ektachrome E100 | kodak | color | recipe-lab | recipe-lab |
| kodachrome-64 | Kodachrome 64 | kodak | color | recipe-lab | recipe-lab |
| kodak-vision3-500t | Kodak Vision3 500T (daylight) | kodak | color | recipe-lab | recipe-lab |
| kodak-vision-200t-asteroid-city | Kodak Vision 200T (Asteroid City) | kodak | color | recipe-lab | recipe-lab |
| kodak-trix-400 | Kodak Tri-X 400 | kodak | mono | recipe-lab | recipe-lab |
| kodak-tmax | Kodak T-Max | kodak | mono | recipe-lab | recipe-lab |
| kodak-trix-1600-pushed | Kodak Tri-X 1600 (pushed) | kodak | mono | recipe-lab | recipe-lab |

**cine（recipe-lab, 4）**

| id | name | group | tone | engine | source |
|---|---|---|---|---|---|
| cinestill-50d | Cinestill 50D (Blue Velvet) | cine | color | recipe-lab | recipe-lab |
| cinestill-800t | Cinestill 800T | cine | color | recipe-lab | recipe-lab |
| classic-cinema | Classic Cinema | cine | color | recipe-lab | recipe-lab |
| rec709-video | Rec709 Video (flat-ish) | cine | color | recipe-lab | recipe-lab |

**ricoh-gr（recipe-lab, 9；含 1 款 authored-here）**

| id | name | group | tone | engine | source |
|---|---|---|---|---|---|
| gr-positive-film | GR Positive Film | ricoh-gr | color | recipe-lab | recipe-lab |
| gr-negative-film | GR Negative Film | ricoh-gr | color | recipe-lab | recipe-lab |
| gr-bleach-bypass | GR Bleach Bypass | ricoh-gr | color | recipe-lab | recipe-lab |
| gr-retro | GR Retro | ricoh-gr | color | recipe-lab | recipe-lab |
| gr-cross-process | GR Cross Process | ricoh-gr | color | recipe-lab | recipe-lab |
| gr-hi-contrast-bw | GR Hi-Contrast B&W | ricoh-gr | mono | recipe-lab | recipe-lab |
| gr-hard-monotone | GR Hard Monotone | ricoh-gr | mono | recipe-lab | recipe-lab |
| gr-soft-monotone | GR Soft Monotone | ricoh-gr | mono | recipe-lab | recipe-lab |
| gr-moriyama | GR Moriyama (grainy B&W) | ricoh-gr | mono | recipe-lab | authored-here（verified:false） |

**leica（recipe-lab, 4）**

| id | name | group | tone | engine | source |
|---|---|---|---|---|---|
| leica-contemporary | Leica Contemporary | leica | color | recipe-lab | recipe-lab |
| leica-classic | Leica Classic | leica | color | recipe-lab | recipe-lab |
| leica-eternal | Leica Eternal | leica | color | recipe-lab | recipe-lab |
| leica-monochrom | Leica Monochrom | leica | mono | recipe-lab | recipe-lab |

**hasselblad（recipe-lab, 1）**

| id | name | group | tone | engine | source |
|---|---|---|---|---|---|
| hasselblad-hncs-natural | Hasselblad HNCS Natural | hasselblad | color | recipe-lab | recipe-lab |

**canon-nikon（recipe-lab, 5）**

| id | name | group | tone | engine | source |
|---|---|---|---|---|---|
| canon-standard | Canon Standard | canon-nikon | color | recipe-lab | recipe-lab |
| canon-portrait | Canon Portrait | canon-nikon | color | recipe-lab | recipe-lab |
| canon-faithful | Canon Faithful | canon-nikon | color | recipe-lab | recipe-lab |
| nikon-flat | Nikon Flat | canon-nikon | color | recipe-lab | recipe-lab |
| nikon-vivid | Nikon Vivid | canon-nikon | color | recipe-lab | recipe-lab |

**pana-olympus（recipe-lab, 4）**

| id | name | group | tone | engine | source |
|---|---|---|---|---|---|
| pana-l-monochrome-d | Pana L.Monochrome D | pana-olympus | mono | recipe-lab | recipe-lab |
| pana-l-classicneo | Pana L.ClassicNeo | pana-olympus | color | recipe-lab | recipe-lab |
| olympus-pop-art | Olympus Pop Art | pana-olympus | color | recipe-lab | recipe-lab |
| olympus-pale-light | Olympus Pale & Light | pana-olympus | color | recipe-lab | recipe-lab |

**other-stocks（recipe-lab, 3）**

| id | name | group | tone | engine | source |
|---|---|---|---|---|---|
| agfa-vista-200 | Agfa Vista 200 | other-stocks | color | recipe-lab | recipe-lab |
| agfa-ultra-100 | Agfa Ultra 100 | other-stocks | color | recipe-lab | recipe-lab |
| polaroid-instax | Polaroid / Instax | other-stocks | color | recipe-lab | recipe-lab |

**ilford（recipe-lab, 5）**

| id | name | group | tone | engine | source |
|---|---|---|---|---|---|
| ilford-hp5 | Ilford HP5 | ilford | mono | recipe-lab | recipe-lab |
| ilford-fp4 | Ilford FP4 | ilford | mono | recipe-lab | recipe-lab |
| ilford-delta-100 | Ilford Delta 100 | ilford | mono | recipe-lab | recipe-lab |
| ilford-delta-3200 | Ilford Delta 3200 | ilford | mono | recipe-lab | recipe-lab |
| ilford-pan-f-50 | Ilford Pan F 50 | ilford | mono | recipe-lab | recipe-lab |

**film-studio-matrix 引擎（15：fuji-sim 10 + ricoh-gr 5，source 均为 film-studio）**

| id | name | group | tone | engine | source |
|---|---|---|---|---|---|
| fs-provia | PROVIA | fuji-sim | color | film-studio-matrix | film-studio |
| fs-velvia | Velvia | fuji-sim | color | film-studio-matrix | film-studio |
| fs-astia | ASTIA | fuji-sim | color | film-studio-matrix | film-studio |
| fs-classic-chrome | CLASSIC CHROME | fuji-sim | color | film-studio-matrix | film-studio |
| fs-reala-ace | REALA ACE | fuji-sim | color | film-studio-matrix | film-studio |
| fs-pro-neg-std | PRO Neg. Std | fuji-sim | color | film-studio-matrix | film-studio |
| fs-classic-neg | CLASSIC Neg. | fuji-sim | color | film-studio-matrix | film-studio |
| fs-eterna | ETERNA | fuji-sim | color | film-studio-matrix | film-studio |
| fs-eterna-bb | ETERNA BLEACH BYPASS | fuji-sim | color | film-studio-matrix | film-studio |
| fs-acros | ACROS | fuji-sim | mono | film-studio-matrix | film-studio |
| fs-gr-positive | GR Positive Film | ricoh-gr | color | film-studio-matrix | film-studio |
| fs-gr-negative | Negative Film | ricoh-gr | color | film-studio-matrix | film-studio |
| fs-gr-hcbw | High Contrast B&W | ricoh-gr | mono | film-studio-matrix | film-studio |
| fs-gr-moriyama | Moriyama Daido Style | ricoh-gr | mono | film-studio-matrix | film-studio |
| fs-gr-cross | Cross Process | ricoh-gr | color | film-studio-matrix | film-studio |

> 注：`cross_ref` 字段的 recipe-lab / film-studio 成对条目是同一风格的两种引擎实现，并非重复配方。

### 1.2 风格谱系分析（已覆盖区间）

按视觉区间归类现有 93 款：

1. **标准/中性彩色**：factory-st、sony-nt-neutral、canon-faithful、reala-ace、fuji-c200、rec709-video。
2. **暖调日常负片（A/B 偏琥珀+品红）**：kodak-gold-200、kodak-ultramax-400、kodak-colorplus-200、kodak-portra-400/800、fuji-superia-400、agfa-vista-200、leica-classic、pana-l-classicneo。
3. **低饱和褪色/电影感**：sony-fl-film-like、classic-chrome、eterna、eterna-bleach-bypass、gr-negative-film、nikon-flat、leica-eternal、rec709-video、classic-cinema、gr-bleach-bypass（褪色+强反差）。
4. **强饱和冲撞（VIVID+matrix1）**：velvia、fuji-fortia-50、kodak-ektar-100、agfa-ultra-100、olympus-pop-art、sony-vv2、nikon-vivid。
5. **深浓/风景（DEEP/LANDSCAPE）**：kodachrome-64、leica-classic。
6. **冷调/电影夜景（K 钨丝 + 蓝偏）**：cinestill-800t、cinestill-50d、kodak-vision3-500t、kodak-vision-200t-asteroid-city。
7. **青绿/品红偏（逆冲感）**：gr-cross-process（ab-2, gm+4）——本库唯一接近「青橙」的项。
8. **高调柔光/粉彩褪色（pe 4/5 + 正 ev）**：sony-sh-soft-high-key、fuji-pro-400h、olympus-pale-light、gr-retro、polaroid-instax、sony-in-instant、nostalgic-neg、kodak-vision-200t-asteroid-city。
9. **棕褐/单色暖**：sepia（SEPIA 风格）。
10. **高反差黑白**：acros、gr-hi-contrast-bw、gr-hard-monotone、leica-monochrom、pana-l-monochrome-d、ilford-delta-3200。
11. **普通/细颗粒黑白**：ilford-hp5/fp4/delta-100/pan-f-50、kodak-trix-400、kodak-tmax、acros-ye/r/g、gr-soft-monotone。
12. **粗颗粒黑白（pe7 rough-mono）**：gr-moriyama、kodak-trix-1600-pushed、gr-hi-contrast-bw、acros-r。

**图片效果 `pe` 使用现状**：仅 `0`（关闭）、`4`（retro-photo）、`5`（soft-high-key）、`7`（rough-mono）四种被使用。`1 toy-camera / 2 pop-color / 3 posterization / 6 part-color / 8 soft-focus / 9 hdr-art / 10 richtone-mono / 11 miniature / 12 illust / 13 watercolor` **全部未被任何配方使用**。

### 1.3 空白区间 & 真正值得新增的「手机滤镜 App 风」

手机滤镜 App 的典型特征：高光提亮 / 褪色 / 低对比 / 偏色 / 强颗粒 / 漏光感。

对照现有覆盖：

- **高光提亮 / 褪色 / 低对比**：已被区间 3、8 充分覆盖（classic-chrome、eterna、gr-negative、soft-high-key、pale-light 等）。**不要再新增通用「褪色」配方**，会稀释仓库。
- **强颗粒（彩色）**：**完全做不到**（只有黑白 pe7 有颗粒），无新增空间。
- **漏光 / 暗角**：设置存储区无字段；但 **`pe=1 toy-camera` 自带暗角+偏色+提饱和**，是当前唯一能模拟「漏光/暗角感」的渠道，且**未被使用** → 真正空白、值得新增。
- **真·青橙分色调**：做不到（仅全局 ab/gm）；但可新增一个**全局冷青偏**（ab 负向、gm 略正）的「青调 mood」条目，作为 gr-cross-process 之外的另一种偏色，且诚实标注非分色调。

**结论——真正值得新增、且不重复现有 93 款的条目（按价值排序）：**

| 建议新增 | pe | 对应手机滤镜特征 | 理由（为何不重复） |
|---|---|---|---|
| `toy-camera` 玩具相机 | 1 | 漏光/暗角/偏色/强饱和 | pe1 全库未用，是漏光+暗角唯一近似手段 |
| `part-color` 局部色彩 | 6 | 只保留某色相 | pe6 全库未用，标志性手机效果 |
| `posterization` 海报 | 3 | 色阶分离/扁平插画感 | pe3 未用 |
| `teal-mood` 青调（全局偏青） | 0 + ab-/gm+ | 青橙冷调 | 现有仅 gr-cross-process 偏绿品红，无干净青调 |
| `watercolor` / `illust` | 13 / 12 | 水彩/插画 | pe12/13 未用，niche 但可补 |

> 不建议新增：更多「褪色」「柔光」「暖负片」通用配方（已饱和）；任何「彩色颗粒」「漏光」「暗角」靠设置实现的声称（见 2.2，做不到）。

---

## 第 2 部分：映射规则手册

### 2.1 视觉目标 → 参数手段 对照表

| 想要的视觉目标 | 参数手段 | 理由 / 注意 |
|---|---|---|
| 褪色 / 低饱和 | 降 `sat`（NEUTRAL 或 STD 底），或 `pe=4` retro-photo | sat 直接控全局饱和；NEUTRAL 比 VIVID 更平；retro-photo 自带褪色+偏黄 |
| 提亮高光（高调） | `pe=5` soft-high-key，或 `LIGHT` 底 + 正 `ev`，或 `dro=6` | soft-high-key 是提亮高光的最直接手段；ev 是整体曝光非只高光 |
| 压暗部同时提亮高光（S 曲线） | **做不到**；近似：`con` 升 + `dro` 降档（3/5）+ 正 `ev` | 真 S 曲线=色调曲线，a6000 存不下 |
| 高反差 | `con` +2~+3；黑白用 `MONO` 底 + `con`+3 | con 是直接反差滑块 |
| 粗颗粒黑白 | `pe=7` rough-mono + 高 ISO | 设置区唯一颗粒来源，仅黑白 |
| 彩色颗粒 | **做不到** | 无彩色颗粒字段 |
| 暖调日常负片 | `PORTRAIT`/`STD` 底 + `ab` +2~+3 + `gm` +1 | ab 琥珀、gm 品红共同暖化肤色 |
| 强饱和冲撞 | `VIVID` 底 + `sat` +3~+5 + `matrix=1` | matrix1 增浓，VIVID 底提供高饱和起点 |
| 冷调/电影夜景 | `wb.mode=K` 低色温（3200）+ `gm`-1，或 `K` 5600 + `ab`-2（蓝调） | K 模式直接定色温；ab 负向偏蓝 |
| 青橙分离（split-tone） | **真分色调做不到**；近似：全局 `ab` 负向（青）+ `gm` 正向（品红）；或单一暖调用低 kelvin | 只有全局 ab/gm，无法阴影青/高光橙分置 |
| 漏光 / 暗角 | **设置区无字段**；近似：`pe=1` toy-camera（自带暗角+偏色） | toy-camera 是唯一近似渠道 |
| 偏色玩具感 | `pe=4` retro-photo / `pe=5` soft-high-key / `pe=1` toy-camera | 图片效果自带整体偏色 |
| 单色保留（局部色彩） | `pe=6` part-color | 仅图片效果提供，style 此时失效 |
| 海报 / 色阶分离 | `pe=3` posterization | 扁平图形感 |
| 插画 / 水彩 | `pe=12` illust / `pe=13` watercolor | 绘画感 |
| HDR 绘画 | `pe=9` hdr-art | HDR 风 |
| 微缩景观（移轴虚化） | `pe=11` miniature | 上下虚化，与色彩无关 |
| 柔和焦点 | `pe=8` soft-focus | 柔光 |
| 强反差褪色（bleach bypass） | `NEUTRAL` 底 + `sat` 大降（-8/-9）+ `con` +3 | 褪色与硬反差并存 |
| 隐藏胶片味矩阵 | `matrix=1` | 索尼未公开色彩矩阵，实测更浓；仅 recipe-lab |

> **关键约束**：`pe≠0` 时 `style`（创意风格）会被相机忽略。因此所有 pe 类配方是独立于 sat/con/matrix 的「另一族」，不能把 VIVID 底和 pe 叠加使用。

### 2.2 「做不到」清单（手机滤镜 App 常见但 a6000 无法实现）

每一项都因为设置存储区没有对应字段，且 a6000 无 Picture Profile / 无 LUT 通道：

| 效果 | 为何做不到 | 近似手段（若有） |
|---|---|---|
| 真实彩色颗粒 | 设置区无颗粒层；pe 颗粒仅 `rough-mono` 黑白 | 无（彩色只能靠高 ISO 噪点，非颗粒纹理） |
| 漏光（light leak） | 无叠加层字段 | `pe=1` toy-camera（暗角+偏色近似，非漏光） |
| 暗角（vignette） | 无暗角字段 | `pe=1` toy-camera 自带暗角 |
| 色调曲线 / S 曲线 / Log | a6000 无 Picture Profile，存不下曲线 | 无 |
| HSL 分通道（按色相调饱和/色相） | 只有全局 `sat` | 无 |
| 真·青橙分色调（split-toning） | 只有全局 `ab`/`gm` | 全局偏青或全局偏暖，无法两区分离 |
| 双重曝光 | 无 | 无 |
| 色散 / 紫边（chromatic aberration） | 镜头光学，不可设 | 无 |
| 灰尘 / 划痕 / 做旧纹理 | 无纹理层 | 无 |
| 光晕 / glow | 无 | `pe=8` soft-focus 近似柔光，非光晕 |
| LUT 文件 | 无 LUT 通道 | 无 |
| 局部处理 / 渐变滤镜 | 无蒙版 | 无 |
| 清晰度 / 结构（clarity） | 仅全局 `sharp` | 无 |

### 2.3 参数取值的「安全范围」（从现有 93 款反推）

> 范围指仓库已实际使用并验证可存的区间；新增配方建议不超出。

| 参数 | 实测使用区间 | 菜单可达性 |
|---|---|---|
| `sat` | **[-9, +8]** | 机身菜单滑块仅 ±3；超出 ±3 只能由 APK 写入，**机身菜单无法手调** |
| `con` | [-3, +3] | 与菜单 ±3 一致 |
| `sharp` | [-2, +3] | 菜单可覆盖 |
| `ab`（A+/B-） | [-2, +3] | 建议新增不超 [-3, +3] |
| `gm`（G+/M-） | [-2, +4] | gr-cross-process 用到 +4；建议不超 [-3, +4] |
| `ev`（1/3EV 单位） | [-1, +3]（即 -1/3 ~ +1 EV） | 菜单 EV 补偿域更大（±3EV），配方内保持温和 |
| `kelvin`（K 模式） | [2500, 5600] | AUTO 时 kelvin=0 |
| `dro` | {3, 5, 6} | 另有 off=0 与 等级 1-5；auto=6 |
| `matrix` | {0, 1} | 隐藏开关 |
| `pe` | 0-13 全量允许 | pe≠0 时 style 失效 |
| `sub` | 各 pe 专用子档（如 fuji-pro-400h sub=2），缺省 0 | 仅部分 pe 用得到 |

### 2.4 疑似越界参数（现有 93 款里 `sat` 超菜单 ±3）

以下条目的 `sat` 绝对值 > 3，**只能在 APK 写入、机身菜单手调不到**（机身创意风格滑块封顶 ±3）。按现行引擎仍能存能显，但用户「按菜单复现」时会卡住，列此提醒：

- sony-fl-film-like `sat=-4`
- classic-chrome `sat=-5`
- sony-in-instant `sat=-6`
- eterna `sat=-6`
- gr-bleach-bypass `sat=-8`
- eterna-bleach-bypass `sat=-9`
- velvia `sat=+5`
- fuji-fortia-50 `sat=+6`
- agfa-ultra-100 `sat=+6`
- olympus-pop-art `sat=+8`

另：`gr-cross-process` 的 `gm=+4` 也超出机身白平衡微调常见 ±3 域，属同一类「仅 APK 可写」项，提醒核实。

> 不建议自行修改这些条目；若要使之「菜单调得动」，只能把 sat 收进 ±3，会损失风格强度。

### 2.5 新增条目的命名与登记规范

1. **id 命名**：小写连字符，语义自解释，例如 `toy-camera`、`part-color-warm`、`teal-mood`。避免与现有 id 撞名（见 1.1）。
2. **group 归属判断**：
   - 仿某胶片/相机品牌的 → 归入对应 group（kodak / fuji-film / ricoh-gr …）。
   - 纯手机滤镜 App 风、不绑定品牌 → 归入 `app-look`（已登记）。新增组时记得同步三处：
     `filters.json` 的 `groups[]`、`tools/gen_recipes.py` 的 `GROUP_JAVA`、以及本仓库的
     README 分组表。`validate_catalog.py` 现在从 `groups[]` 读取，不需要再改。
3. **「本仓库自写」条目必填**：
   - `"source": "authored-here"`
   - `"verified": false`
   - `"note"`: 写明「未在实机验证，落地前请先在可丢弃素材上试拍」及风格依据。
   - 例：参照 `gr-moriyama`（已登记为 authored-here + verified:false + note）。
4. **recipe 字段完整性**（recipe-lab 引擎）：必须含 `style, sat, con, sharp, matrix, wb{mode,kelvin,ab,gm}, pe, sub, ev, dro` 全字段；`pe≠0` 时 `style` 仍记录以备查，但相机会忽略。
5. **参数取值**：遵守 2.3 安全范围；如需超出 ±3（如强褪色），明确写入 note 并标注「仅 APK 可写、菜单不可调」，避免用户困惑。
6. **去重检查**：新增前对照 1.2 谱系，确认不是区间 3/8 已饱和的「又一款褪色柔光」；重复项会稀释仓库价值。
