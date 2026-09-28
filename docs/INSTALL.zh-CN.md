# 安装：把胶片配方装进你的索尼相机

<p align="center">
  <a href="INSTALL.md">English</a> · <b>简体中文</b>
</p>

这份指南带你把 **Sony SOOC Recipes** 装进相机——这个应用会把一整份胶片风格配方（Creative Style、
Picture Effect、白平衡、DRO……）写进你的相机，让你的老索尼微单直出就有胶片味。

**预计耗时：** 在 Windows 上一次性约 10–15 分钟。**下载一个文件、运行它、把相机插上** ——
配方和安装通道都打包在里头了，没有 APK 要下、不用先装 Sony-PMCA-RE、也没有命令要敲。

<p align="center">
  <img src="assets/install-flow.svg" width="720" alt="安装流程图">
  <br><sub>图：一次下载、一次点击、一条进度条</sub>
</p>

下面先把这条路径讲细，然后是给 macOS / Linux / 想自己开命令行的人的手动路线。想知道手动路线里
那两条底层通道的差别，读 [通道对比](CHANNEL-COMPARISON.md)——安装器替你自动走的是其中第一条。

---

## 开始之前

### 确认你的相机支持

按 `MENU` 找 **`Application`（应用程序）** 这一项。有，说明你的相机走 PlayMemories Camera
Apps（PMCA）通道，能收应用；没有，就到此为止——本仓库没有任何办法能给它装东西。

| 有 `MENU → Application` | 没有 |
|---|---|
| a6000 · a6300 · a6500 · a5100 · a5000<br>a7 / a7R / a7S / a7 II / a7R II / a7S II<br>NEX-5R · NEX-5T · NEX-6<br>RX100 III / IV / V · RX10 II / III · RX1R II<br>HX60 / HX90 / HX400 · WX500<br>a68 · a77 II · a99 II | 2012 年前的 NEX（NEX-3 / 5 / 5N / F3 / 3N / **7**）· a3000 · a3500<br>a6100 · a6400 · a6600 · a6700 · ZV-E10<br>a7 III 及之后全部 · a9 全系 · a1 全系<br>RX100 VA 及之后 · RX10 IV · RX0 · HX99 · ZV-1 全系 |

> **实话实说。** 没有 `Application` 菜单 = 装不了，句号。索尼 2021 年就关了自家应用商店，
> 2016 年末之后的机型（a6500、a99 II 是最后两台）全是签名固件，任何应用都进不去——不是本项目
> 不行，索尼自己也不行。网上说在 a6400 上跑起来的都是误传。
>
> 另一端也有边界：**PMCA 是从 2012 年秋的 NEX-5R / NEX-6 才开始的**。更早的 NEX-7、
> NEX-3 / 5 / 5N / F3、以及 a3000 / a3500 没有 Android 子系统，同样没有 `Application`
> 菜单——它们不在上表「支持」那一列里，**不是漏写**。

**已在真机确认的机型：α7S II**，同时装着九个品牌包。真机照片见
[README 的真机实拍](../README.zh-CN.md#真机实拍)。左列其余机型是**平台层面**支持
（机器有这个应用通道），不是逐台实测过——这两件事不是一回事。

### 你需要准备

- 一台电脑（**一键安装只支持 Windows**；macOS / Linux 走下面的手动路线）。
- 一根**能传数据**的 USB 线（a6000 是 micro-USB；三合一数据线里只有能传数据的那根能用）。
- 相机里**插好存储卡**。
- **充满电的电池。** 安装过程中相机会切几次模式。装到一半没电，恢复起来很难看——先充。

### 下载安装器

`SonySOOCRecipes-Base-CN.exe`，从本项目的 Releases 页面下：

https://github.com/HairuoLiu/sony-sooc-recipes/releases/latest

*（想要英文界面就下 `SonySOOCRecipes-Base-EN.exe`，内容一样。）*

**就这一个文件，也只有这一个下载。** 配方已经编译进去，跟相机走 USB 通信的 `pmca-console`
（也就是 Sony-PMCA-RE 的引擎）也打包在里面。不用先装任何东西，装完除了程序本身也不留残渣。

**它带的是 Base——6 个包、91 款观感。** 富士、Fuji Film、柯达、Niche Film、理光 GR、索尼。
每个包在相机上是独立应用，各有自己的 Android 包名，这正是它们能并存的原因；安装时你可以
把不想要的勾掉。其余的包——徕卡、宾得、哈苏、Cinema LUT、单色，以及装着全量目录的
all-in-one——单独分发。完整清单和取舍见 [BRAND-PACKS.md](BRAND-PACKS.md)。

### 运行

<p align="center">
  <img src="assets/install/zh-CN/01-connect-camera.png" width="330" alt="第 1 步：已识别到相机，下方有「重新检测」按钮">
  <img src="assets/install/zh-CN/02-choose-packs.png" width="330" alt="第 2 步：它带的包全部勾上，右上角有全选框">
  <img src="assets/install/zh-CN/03-installing.png" width="330" alt="第 3 步：进度条显示正在安装 1/6">
  <br><sub>连接 · 选择 · 安装 —— 从 .exe 到一机器观感，就这三屏。</sub>
</p>

1. **连接。** 插上准备好的相机，安装器自己会识别，这一步变绿。没识别到就按**重新检测**，
   排查清单在[下面](#如果安装器看不到相机)。
2. **选择。** 它带的包默认全勾。去掉不想要的；右上角的**全选**框可以一键清空/全选。
3. **安装。** 一条进度条加剩余计数，**大约十分钟**。干活的时候窗口可以最小化。
4. **完成。** 拔线、关机再开机，开拍。

> **实话实说。** 写包的时候相机屏幕会黑几次、自己切几次模式。这是正常的——别按键、别拔线。
> 某个包失败的话，完成页会点名；勾上**显示详情**可以看底层日志。

### 装之前先看一眼

> **不再提供 APK 下载。** 早期版本会发布一个个品牌包 APK，让你自己用 Sony-PMCA-RE 装。
> 那个下载撤掉了：安装器当场就把同样的事做完。要是哪篇教程让你去下
> `SonySOOCRecipes-<品牌>.apk`，它讲的是本仓库已经不再发布的版本。

> **两条真会咬人的：**
>
> 1. **相机上如果已经装了别处来的 Sony SOOC Recipes，先删掉。** 用不同 key 签的应用
>    **无法覆盖安装**。包之间同理：`…sonysoocrecipes.ricoh` 和 `…sonysoocrecipes.sony`
>    是*不同的包*、能并存，但同一个包装两份不行。
> 2. **装多个包不等于多台相机。** 相机的设置存储是共享的，同一时间只有一个配方生效。
>    包的差别在于**装进去什么**，不在于相机**能做什么**。

> **部分观感没上机验证过。** 每条配方自己写在 `catalog/filters.json` 的 `verified` 字段里
> ——本仓库自写的那些是 `false`，生成的 `Recipes.java` 里也逐条标了出来。先在可丢弃的素材上
> 试，别拿去拍不能重来的东西。**这个标记是源码注释，不是应用画的**——主屏徽标到底表示什么，
> 见 [FAQ](FAQ.zh-CN.md)。

> APK 里显示的版本号是**基础应用**的，不是本仓库的 tag。基础应用从 `AndroidManifest.xml` 读版本，
> 本仓库只替换配方表；认你下载的那个安装器，别认应用里的数字。

---

## 如果安装器看不到相机

| 你看到 | 怎么办 |
|---|---|
| **没识别到相机** | 依次查：线是**能传数据**的（不是纯充电）· `Setup → USB Connection` 在 **Mass Storage**、不是 PC Remote · 插了存储卡 · 相机开着且屏幕显示 `USB Mode` · 没有别的东西占着 USB 设备（照片、图像捕捉、Dropbox、Imaging Edge）。然后**重新检测**。 |
| **驱动**报错 | 在**显示详情**里把驱动切成 `libusb` 重试。Windows 上还不行，就用 [Zadig](https://zadig.akeo.ie) 装 libusb-win32 驱动再跑。 |
| 识别到了，装到一半失败 | 最常见的原因是机身上已经有旧版 Sony SOOC Recipes。在 `MENU → Application → Application Management → Manage and Remove` 删掉，再装一次。 |
| 一点反应都没有 | 按 `MENU` 看有没有 `Application` 这一项。没有的话这台机器跑不了应用——见上面的机型表。没有别的办法。 |

---

## 手动路线（macOS / Linux / 命令行）

安装器只有 Windows 版。它做的每一件事你自己也能做——而在 macOS 和 Linux 上这是*唯一*的路线，
因为预编译的 APK 已经不再发布了。所以手动路线从本仓库里把它们构建出来，用的工具和安装器里
那份一模一样：

```bash
git clone https://github.com/HairuoLiu/sony-sooc-recipes.git
cd sony-sooc-recipes
tools/build_all_local.sh          # 构建全部目标；脚本头部写了需要的工具链
```

构建完 `dist/` 里就是 `SonySOOCRecipes*.apk`。装哪个：全量版带全部观感，品牌包只带一个品牌的。
两份清单和取舍都在 [BRAND-PACKS.md](BRAND-PACKS.md)。

下面是完整的手动路线。**通道 A** 就是安装器在开的那条——走 USB、全程离线，第一次装只该用它。
**通道 B**（Wi-Fi ADB）是给反复重装用的，而且它永远替代不了通道 A：开 ADB 要先装
OpenMemories:Tweak，而 Tweak 本身就得走通道 A 装进去。

---

## 通道 A：USB + Sony-PMCA-RE

**安装器自动做的那件事，拆开讲。** 全程离线，不暴露任何网络服务，对所有 PMCA 机型通用，
且不需要任何前置应用。

### 1. 拿到 Sony-PMCA-RE

这是 ma1co 做的工具，用索尼自家应用商店同一条通道把应用写进相机。

- **Windows**：从 [ma1co/Sony-PMCA-RE releases](https://github.com/ma1co/Sony-PMCA-RE/releases)
  下载 `pmca-gui.exe`。免安装，直接运行。你还需要装 USB 驱动，按 ma1co 的 README 来：
  https://github.com/ma1co/Sony-PMCA-RE。
- **macOS**：同一页面有 macOS 版，测试程度不如 Windows。**先关掉所有会占用 USB 设备的程序**
  （照片、图像捕捉、Dropbox、Google Drive 等），否则相机会被它们先抢走。
- **Linux**：用 Python 源码（同时装好依赖，含 `libusb`）：
  ```bash
  git clone https://github.com/ma1co/Sony-PMCA-RE.git
  cd Sony-PMCA-RE && pip install -r requirements.txt
  ```
  驱动和权限等平台细节以 ma1co 的 README 为准；若 `libusb` 或设备权限出问题，那份 README 是
  权威来源。

> **实话实说。** 各系统的驱动、权限步骤不同，也可能随版本变化。不确定时，以 ma1co 的 README
> 为准：https://github.com/ma1co/Sony-PMCA-RE

### 2. 设置相机

1. 电池充满，**装上存储卡**
2. `Setup（工具箱图标）→ USB Connection → **Mass Storage**`
3. 开机，插上 USB 线（a6000 是 **micro-USB**，三合一数据线里只有能传数据的那根能用）
4. 相机屏幕显示 **USB Mode** 即为就绪

> **实话实说。** 之后走通道 B 时这个设置要改成 **MTP**。通道 A 期间保持 Mass Storage。

### 3. 安装

**图形界面**：打开 `pmca-gui.exe` → **Install app from file** → 选 APK → 等待

**命令行**（Linux 前加 `sudo`）：
```bash
python pmca-console.py install -f SonySOOCRecipes-<版本>.apk
```

过程中相机会闪黑、自己切换模式几次——**这是正常的，不要按任何键**。约一分钟后电脑
打印 `Task completed successfully`。

> **实话实说。** **以电脑的输出为准。** 相机通常停在 `Application Download / Connecting via
> USB...` 的界面上，看起来像卡死，其实不是。

### 4. 收尾

拔线，**关机再开机**。应用现在位于 `MENU → Application → Application List → Sony SOOC Recipes`。

---

## 装上之后怎么验证成功

1. 进 `MENU → Application → Application List`，确认列出了 **Sony SOOC Recipes**。
2. 打开它。进来就是**一条磨砂浮栏**——配方名、品牌、序号和参数摘要在同一行；转波轮实时画面
   立刻变化，按 **AEL** 或 **DISP** 循环切到精简胶囊与纯取景。
3. 确认配方真的写进去了：按 **Fn** 进列表，按**中心键**（或右键）打开设置编辑器，再按
   一次**中心键**存下，然后**关机再开机**。这个风格就成了相机在 P/A/S/M 和录像**所有模式**
   下的默认，应用关着也生效。

应用里你可能会看到的徽标：

| 徽标 | 含义 |
|---|---|
| 品牌名 —— `PENTAX`、`KODAK`、`LEICA` …（中文：宾得 / 柯达 / 徕卡 …） | 这款观感所属的类目。徽标只说这一件事；旧的 `ACTIVE` / `PREVIEW` / `PROTECTED` 状态词已移除。 |

一个要知道的后果：界面不再提示相机设置存储区是否处于写保护。如果某次写入看起来「没生效」，
这仍然是要查的第一件事——装 [OpenMemories-Tweak](https://github.com/ma1co/OpenMemories-Tweak)
关掉 *Backup protection*。

---

## 通道 B：Wi-Fi ADB

**只在通道 A 已打通、且你需要反复重装时才用。** 它是开发快车道，不是给终端用户准备的。

> **实话实说。** ADB 打开期间，同一局域网内任何机器都能对相机执行 adb 命令。只在可信网络上
> 开，用完立刻关。见 [通道对比 §安全提示](CHANNEL-COMPARISON.md#安全提示)。

### 1. 先用通道 A 装上 OpenMemories:Tweak

相机 USB 模式设为 **MTP**（注意不是 Mass Storage），接上电脑，打开 `pmca-gui`：

1. 选 **Install app** 页
2. 在应用列表里选 **OpenMemories: Tweak**
3. 点 **Install selected app**

不需要用固件更新或服务模式。

### 2. 在相机上开 ADB

1. 安全断开 USB，在 `MENU → Application → Application List` 打开 **OpenMemories: Tweak**
2. 相机先配好 Wi-Fi 接入点
3. 进 Tweak 的 **Developer** 页，打开 **Enable Wifi** 和 **Enable ADB**，**记下显示的 IP**
4. 电脑连同一个局域网，把相机休眠时间调长

> **实话实说。** 本应用只需要 ADB。**不用**开 Telnet、不用解除设置保护、不用改地区、不用解除
> 录制时限、不用改固件。

### 3. 用 adb 安装

```bash
adb connect CAMERA_IP:5555      # 换成相机此刻显示的地址，保留 :5555
adb devices                     # 目标应显示为 device
adb -s CAMERA_IP:5555 install -r SonySOOCRecipes-<版本>.apk
```

仓库自带一个把手：`tools/install-wifi.sh <apk> <相机IP>`，会做连接、就绪检查、安装、并提醒你
收尾关掉 ADB。

### 4. 收尾

```bash
adb disconnect CAMERA_IP:5555
```

**再去 Tweak 里关掉 ADB。** `adb disconnect` 只断开电脑这一侧，相机上的守护进程还在跑。

---

## 更新与卸载

- **USB 更新（通道 A）**：直接再跑一次安装即可。
- **ADB 更新（通道 B）**：`adb install -r` 秒级完成。
- **签名警告（重要）**：用*不同* key 签的 APK **无法覆盖安装**。安装器带的这些包共用一把 key，
  互相之间能干净升级；但任何来自旧版、签名不同的构建都换不掉。看到
  `INSTALL_FAILED_UPDATE_INCOMPATIBLE`，就**先卸载同包名的旧应用**（见下方「卸载」；卸载会清掉
  应用设置），再重装。
- **卸载**：用**相机自己的菜单**，不是安装器。
  `MENU → Application → Application Management → Manage and Remove` → 选中要删的那一项 → 移除。
  部分机型的 `Application Management` 在 `Application List` 下面（多一层），标签是本地化的
  （`Manage and Remove` / 中文界面「管理与移除」）。**  先退出应用**再操作。这会清掉应用自己的设置。

<p align="center">
  <img src="assets/hardware/01-a7sii-application-list.jpg" width="330" alt="α7S II 上的应用程序列表，「应用程序管理」就在列表里">
  <br><sub>α7S II 上就是这个样子：<b>应用程序管理</b>是应用程序列表<b>里面</b>的一项，
  这台机器上不需要再进别的子菜单。要卸载就进这一项。真机屏幕照片，不是效果图。 一台机身上并排放着九个品牌包——这正是「包名各不相同」要换来的并存，也意味着你不必背着全部九个。</sub>
</p>

> **实话实说 —— 装它的工具卸不掉它。** Sony-PMCA-RE **没有卸载命令**。它的全部子命令是
> `info`、`install`、`market`、`apk2spk`、`spk2apk`、`firmware`、`updatershell`、`serviceshell`、
> `guess_firmware`、`gps`、`stream`、`wifi`、`print_backup` —— `install` 是它唯一的方向。
> 所以你机器上的 `Manage and Remove` 项若没有、或是灰的，改走通道 B 用 ADB 卸载：
>
> ```bash
> adb connect CAMERA_IP:5555
> adb shell pm list packages | grep hairuoliu     # 看相机上装了哪几个包
> adb uninstall com.hairuoliu.sonysoocrecipes     # 或 ...sonysoocrecipes.<品牌>
> ```

> **实话实说。** 卸载应用**不会**自动回退你已经存进相机设置的配方。换回原样：应用里按
> TRASH + 中心键 + 关机重启；或 `Setup → Setting Reset → Camera Settings Reset`。

---

## 排错表

| 现象 | 可能原因 | 怎么办 |
|---|---|---|
| `Switching to app install mode` 之后紧跟 `This camera does not support apps` | 相机**拒绝**了「切到应用安装模式」这条 USB 命令——它的固件里没有应用通道。安装器只是转述这次拒绝，这句英文是安装器自己的说法。注意上面那行 `Switching to app install mode` 打印在命令**之前**，不是成功提示；此错误在传输 APK 前就直接退出，APK 根本没被送出。 | APK 侧没有任何可修的地方。按 `MENU` 看有没有 `Application`；没有的话这台机器根本装不了应用。机型清单与 2012 年分界线见 `docs/FAQ.zh-CN.md`。若机型确实在支持列却仍报此错（少见），依次查：`Setup → USB Connection` 设成 **Mass Storage**（别用 PC Remote）· 关掉相机的 Wi-Fi / Ctrl with Smartphone · 插入存储卡 · 退出会抢占 USB 驱动的程序（Photos / Dropbox / Imaging Edge）；仍不行则在 Windows 上用 Zadig 装 libusb-win32 驱动后重跑 `pmca-console install -d libusb -f <你的.apk>`。 |
| `No devices found` | USB 不是 **Mass Storage**、没插卡、相机没开，或线/口不对 | 设成 Mass Storage、插卡、开机显示 **USB Mode**、换线换口 |
| 驱动装不上（Windows） | USB 驱动缺失/被拦 | 按 ma1co 的 README 装驱动：https://github.com/ma1co/Sony-PMCA-RE |
| 卡在 `Waiting for camera to switch...` | 握手中途抽风 | 拔线，相机关机再开，重连，重跑 |
| 徽标显示 `PROTECTED` | 设置存储区写保护 | 装 OpenMemories-Tweak，关掉 *Backup protection*，重试 |
| 装完找不到应用 | 找错菜单 | 它在 `MENU → Application → Application List → Sony SOOC Recipes` |
| 应用打不开 / `no live preview: ...` | 有别程序占着相机 | 退出照片/图像捕捉等，重开应用 |
| 存了但风格没生效 | 相机还没重读设置 | **关机再开机** |
| 文字显示 `Â·` | 装的是修好文字编码之前的版本 | 用当前的安装器重装 |
| `adb: offline` / 超时 / 找不到设备 | 相机休眠、IP 变了、不在同一 Wi-Fi、ADB 没开，或访客网络隔离/VPN/终端本地网络权限 | `adb disconnect` 后重连；检查访客网络隔离、VPN、终端本地网络权限 |
| MTP 正常但 adb 找不到 | MTP 和 Wi-Fi ADB 是**两条不同的连接** | 按通道 B 第 2 步开 ADB |
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` | 签名不同 | 用同一密钥重建；或备份后在相机应用管理里卸载同包名旧应用（**卸载会清掉应用设置**） |
| RAW 套不上效果 | Picture Effect 类配方（应用里标 **PE**）只在 **JPEG** 画质下生效 | 用 JPEG 画质；RAW / RAW+JPEG 会被相机静默丢弃 |
| 饱和度滑块一碰就「掉档」 | 部分配方把饱和度推得比菜单滑块范围（±3）更远 | 菜单显示最接近的值，你一动滑块它就弹回正常范围；从应用里重新存储即可 |

---

## FAQ

**会不会变砖？**
不会。应用走索尼官方应用通道写设置，不碰固件、不碰 bootloader。

**会不会动固件？**
不会。整个过程不刷写、不修改固件。右边「不支持」列表里那些签名固件机型，根本就收不到任何应用。

**清掉出厂设置还在吗？**
你存进去的配方活在相机设置里。`Setup → Setting Reset → Camera Settings Reset` 会清掉它；
完整初始化也会清掉。应用本身靠卸载移除。

**RAW 会受影响吗？**
Picture Effect 类配方（应用里标 **PE**）只在 **JPEG** 输出下生效；RAW 或 RAW+JPEG 时相机会
静默忽略它。其余配方（Creative Style、白平衡、DRO）是相机设置，与文件格式无关都会生效。

**可逆吗？影响保修吗？**
它走的是索尼商店同一条通道，可以干净卸载。是否影响保修是索尼说了算；安装机制本身是非破坏性、
可移除的。
