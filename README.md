# Sony SOOC Recipes · 索尼直出配方

**把胶片滤镜编译成 APK，装进你那台老索尼，让直出就能看。**

针对索尼 PlayMemories Camera Apps（PMCA）机型 —— a6000 · a6300 · a6500 · a5100 ·
NEX · RX100 III–V · a7 II 一代 —— 一个装进相机内部的应用，**93 款**胶片与机型风格配方，
其中 **78 款可直接编译进 APK**。

关掉应用、关机重启，风格依然是相机在 P/A/S/M 和录像**全部模式**下的默认。
直出的 JPEG 就带滤镜。

> SOOC = Straight Out Of Camera，直出。
> 这不是「后期套 LUT」，是把风格写进相机，拍的时候就定了。

---

## 它解决什么问题

a6000 的直出和屏幕有多难看你心里有数。索尼 2021 年关了应用商店，这批老机器在软件
层面被彻底放弃——但它们有 Android 底层，装得进东西。

本项目把散落在社区里的配方汇总成**一份数据**，再编译成 APK 装回去。

---

## 快速开始

```bash
git clone https://github.com/HairuoLiu/sony-sooc-recipes.git
cd sony-sooc-recipes
python tools/validate_catalog.py     # 校验配方表
python tools/gen_recipes.py --stdout # 看一眼会生成什么
```

**只想把滤镜装进相机？** 直接看 **[安装指南](docs/INSTALL.md)**：

1. 按 `MENU` 找有没有 **`Application`** 这一项 —— 没有就装不了，别往下走了
2. 走 **USB + Sony-PMCA-RE** 通道（全程离线、通用、无需前置应用）
3. 打开应用，波轮选配方，中心键存储，**关机再开机**

**两条安装通道的区别**（这是本项目被问得最多的一个问题）：
见 **[通道对比](docs/CHANNEL-COMPARISON.md)**。
一句话：**USB 是「能不能装上」，Wi-Fi ADB 是「装上多快」**。ADB 永远无法取代 USB，
因为开 ADB 所需的 OpenMemories:Tweak 本身就得用 USB 装。**第一次走 USB。**

---

## 配方一览

93 款，12 个品牌组。完整可筛选的列表打开 **[滤镜浏览器](catalog/index.html)**。
（GitHub 上直接打开是源码，下载后用浏览器打开即可。）

| 品牌组 | 数量 | 代表 |
|---|---|---|
| **Sony** | 8 | FL (film-like) · IN (instant) · VV2 |
| **Fuji Sim** | 26 | Classic Chrome · Nostalgic Neg · Acros +R |
| **Fuji Film** | 5 | Pro 400H · Superia 400 · Natura 1600 |
| **Kodak** | 14 | Portra 400 · Gold 200 · Ektar 100 · Tri-X |
| **Cine** | 4 | Cinestill 800T · Cinestill 50D · Rec709 |
| **Ricoh GR** | 13 | GR 正片 · 高反差黑白 · 森山风 |
| **Leica** | 4 | Monochrom · Classic · Eternal |
| **Hasselblad** | 1 | HNCS Natural |
| **Canon / Nikon** | 5 | Canon Faithful · Nikon Flat |
| **Pana / Olympus** | 4 | L.Monochrome D · Pop Art |
| **Other Stocks** | 3 | Agfa Vista 200 · Polaroid / Instax |
| **Ilford** | 5 | HP5 · Delta 3200 · Pan F 50 |

（数量含仅登记的胶片工坊风格；编译进 APK 的是 78 款。）

---

## 必须先说清楚的限制

**这些是「某个味道的近似」，不是别家色彩科学的复制品。**

a6000 没有 Picture Profile 菜单，也存不下色调曲线。每一款配方只能用这台相机
**存得下来**的东西拼：创意风格、饱和度、对比度、锐度、白平衡与微调、曝光补偿、
DRO、图片效果，外加一个索尼从未在菜单里公开的色彩矩阵开关。

**做不到的**（不是没做，是这台机器做不到）：Log 曲线（S-Log / V-Log / Blackmagic）、
带色调的黑白（硒调、蓝晒）、真正的胶片颗粒、索尼摄像机那条 *Cinematone* gamma。

其他已知限制：

- **没有强度档位**。想淡一点只能在应用里手改参数芯片，或不用这款
- **PE 类配方要 JPEG**。图片效果开启时相机忽略创意风格，且 RAW / RAW+JPEG 下效果被静默丢弃
- **a5100 少了 Fn 和 AEL 两个键**，品牌列表浏览和隐藏面板用不了，波轮能滚完全部配方
- **本项目不改固件**，不解锁任何东西，只写你本来就能手设的那些值
- 详见 [架构说明 §已知限制](docs/ARCHITECTURE.md#六已知限制诚实清单)

---

## 项目结构

```
catalog/filters.json   ★ 唯一事实来源 —— 所有配方都登记在这里
catalog/index.html       可浏览的滤镜浏览器（单文件，无依赖，浅色主题）
docs/                    安装 · 通道对比 · 架构 · 加滤镜流程
tools/                   校验器 · 代码生成器 · 保真比对 · 安装把手 · 构建脚本
```

**数据流**：`catalog/filters.json` →（生成）→ `Recipes.java` →（编译）→ APK →（USB / ADB）→ 相机

手改 `Recipes.java` 是错的——它随时会被重新生成。要加滤镜，改注册表。
见 **[加一款滤镜](docs/ADDING-FILTERS.md)**。

### 三道 CI 关卡

| 关卡 | 拦住什么 |
|---|---|
| `validate_catalog.py` | 枚举写错、数值越界、分组顺序断裂、**许可声明不诚实** |
| `gen_recipes.py --check` | 有人手改了 `Recipes.java`，或忘了重新生成 |
| `check_fidelity.py` | **某个配方的数值被悄悄改动** —— 最关键的一关 |

保真比对会把上游 `Recipes.java` 拉下来，双方**展开成完整 15 值形式**后逐个对照
（上游偶尔把默认值写全，必须按语义比对而非文本）。当前状态：

> **77 条上游配方逐值一致，0 漂移。**

---

## 数据来自哪里

| 上游 | 贡献 | 许可 | 可否再分发 |
|---|---|---|---|
| [voxivoid/recipe-lab-sony-pmca](https://github.com/voxivoid/recipe-lab-sony-pmca) | **77 款配方参数**、设置存储区反向工程、应用本体 | **MIT** | ✔ |
| [ukiki0718-netizen/sony-a5100-film-studio](https://github.com/ukiki0718-netizen/sony-a5100-film-studio) | 15 款风格的取向与命名、四档强度设计、机型验证范围与许可披露方式 | PolyForm Noncommercial | ✘ 仅登记 |
| [bonyback1/sony-pmca-ricoh-mod](https://github.com/bonyback1/sony-pmca-ricoh-mod) | 硬件色彩矩阵与共同 Gamma 的处理方法 | Apache-2.0 | ✔ |
| [ma1co/Sony-PMCA-RE](https://github.com/ma1co/Sony-PMCA-RE) | 应用安装通道、固件与设置转储 | MIT | ✔ |
| [ma1co/OpenMemories-Tweak](https://github.com/ma1co/OpenMemories-Tweak) | Wi-Fi ADB 与开发者开关 | MIT | ✔ |

**没有 ma1co 就没有这一切。** 他公开地反向工程了索尼的 PlayMemories 平台并给出了
宽松许可——本项目只是站在上面。

**筛选与许可边界见 [NOTICE.md](NOTICE.md)。** 简版：

- 本仓库**自己的代码**是 MIT
- 上游 `recipe-lab` 的配方参数是 MIT，可自由再分发
- 胶片工坊的 15 款**只登记名称与来源，不转录其拟合参数**——许可（非商用）与技术
  （数值是给它的矩阵/Gamma 管线拟合的，放进「写设置」的引擎根本不成立）两重原因
- 那 15 款里，Recipe Lab 唯缺的是理光**森山风**，本仓库补写了近似版 `gr-moriyama`，
  标着 `verified: false`（**未在实机验证**）

**本项目与索尼、富士、柯达、理光等公司无任何关联，未获其背书。**

---

## 授权

本仓库代码 MIT。**本项目不改固件**，只写相机设置存储区里你本来就能手设的值。

装任何东西前先备份存储卡，先用可丢弃的素材试拍。软件按现状提供，
不保证兼容性、色彩准确性或无侵权。
