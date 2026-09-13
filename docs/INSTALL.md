# 安装：把滤镜装进索尼相机

两条通道，**先读 [通道对比](CHANNEL-COMPARISON.md) 再动手**。简版结论：第一次装走 A，之后想反复重装再开 B。

- [通道 A：USB + Sony-PMCA-RE（推荐，通用）](#通道-ausb--sony-pmca-re)
- [通道 B：Wi-Fi ADB（可选，仅用于反复迭代）](#通道-bwi-fi-adb)
- [装上之后怎么用](#装上之后怎么用)
- [排错表](#排错表)

---

## 前置检查：你的相机能不能装

按 `MENU` 找 **`Application`（应用程序）** 这一项。

| 有 `MENU → Application` | 没有 |
|---|---|
| a6000 · a6300 · a6500 · a5100 · a5000<br>a7 / a7R / a7S / a7 II / a7R II / a7S II<br>NEX-5R · NEX-5T · NEX-6<br>RX100 III / IV / V · RX10 II / III · RX1R II<br>HX60 / HX90 / HX400 · WX500<br>a68 · a77 II · a99 II | a6100 · a6400 · a6600 · a6700 · ZV-E10<br>a7 III 及之后全部 · a9 全系 · a1 全系<br>RX100 VA 及之后 · RX10 IV · RX0 · HX99 · ZV-1 全系 |

**没有这个菜单项 = 装不了。** 索尼 2021 年就关了自家应用商店，2016 年末之后的机型
（a6500、a99 II 是最后两台）全部是签名固件，任何应用都装不进去——本项目不行，
索尼自己也不行。网上说在 a6400 上跑起来的都是误传。

> 副产物：这些机型也不可能有 4K 菜单、Log 曲线或机内 LUT 文件。能用什么，取决于
> 相机**存得下来**什么，详见 [架构说明](ARCHITECTURE.md)。

---

## 通道 A：USB + Sony-PMCA-RE

**这是所有人第一次安装都应该走的通道。** 全程离线，不暴露任何网络服务，对所有
PMCA 机型通用，且不需要任何前置应用。

### 1. 拿到 APK

从本仓库的 Releases 下载 `RecipeLab-<版本>.apk`。

（本仓库只发布滤镜数据与构建工具；APK 由 CI 依据 `catalog/filters.json` 生成。
若还没有发布版本，见 [架构说明](ARCHITECTURE.md) 自行构建。）

> **装之前，两条会真咬人的：**
>
> 1. **签名用的一次性 key。** CI 没配 keystore，每次构建临时生成一把。用不同 key 签的
>    APK **无法覆盖安装**——如果相机上已经装过别处来的 RecipeLab，得先在相机里把它删掉
>    再装这个。
> 2. **有 7 款配方没上机验证过**：`gr-moriyama`、`kodak-vision2-500T`、Toy Camera
>    暖/冷、Part Color 红、Posterization、Teal Mood。它们在相机里显示为
>    `NOT VERIFIED`。先在可丢弃的素材上试，别拿去拍不能重来的东西。
>
> APK 里显示的版本号是**上游**的，不是本仓库的 tag。上游从 `AndroidManifest.xml`
> 读版本，本仓库只替换配方表；认 tag 就行。

### 2. 拿到安装器 Sony-PMCA-RE

这是 ma1co 做的工具，用索尼自家应用商店同一条通道把应用写进相机。

- **Windows**：从 [ma1co/Sony-PMCA-RE releases](https://github.com/ma1co/Sony-PMCA-RE/releases)
  下载 `pmca-gui.exe`。免安装，直接运行。
- **macOS**：同一页面有 macOS 版，测试程度不如 Windows。**先关掉所有会占用 USB 设备的程序**
  （照片、图像捕捉、Dropbox、Google Drive 等），否则相机会被它们先抢走。
- **Linux**：用 Python 源码
  ```bash
  git clone https://github.com/ma1co/Sony-PMCA-RE.git
  cd Sony-PMCA-RE && pip install -r requirements.txt
  ```

### 3. 设置相机

1. 电池充满，**装上存储卡**
2. `Setup（工具箱图标）→ USB Connection → **Mass Storage**`
3. 开机，插上 USB 线（a6000 是 **micro-USB**，三合一数据线里只有能传数据的那根能用）
4. 相机屏幕显示 **USB Mode** 即为就绪

### 4. 安装

**图形界面**：打开 `pmca-gui.exe` → **Install app from file** → 选 APK → 等待

**命令行**（Linux 前加 `sudo`）：
```bash
python pmca-console.py install -f RecipeLab-<版本>.apk
```

过程中相机会闪黑、自己切换模式几次——**这是正常的，不要按任何键**。约一分钟后电脑
打印 `Task completed successfully`。

> **以电脑的输出为准。** 相机通常停在 `Application Download / Connecting via USB...`
> 的界面上，看起来像卡死，其实不是。

### 5. 收尾

拔线，**关机再开机**。应用现在位于 `MENU → Application → Application List → Recipe Lab`。

---

## 通道 B：Wi-Fi ADB

**只在通道 A 已打通、且你需要反复重装时才用。** 它是开发快车道，不是给终端用户准备的。

> **安全前提**：ADB 打开期间，同一局域网内任何机器都能对相机执行 adb 命令。只在可信
> 网络上开，用完立刻关。见 [通道对比 §安全提示](CHANNEL-COMPARISON.md#安全提示)。

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

> 本应用只需要 ADB。**不用**开 Telnet、不用解除设置保护、不用改地区、不用解除录制时限、
> 不用改固件。

### 3. 用 adb 安装

```bash
adb connect CAMERA_IP:5555      # 换成相机此刻显示的地址，保留 :5555
adb devices                     # 目标应显示为 device
adb -s CAMERA_IP:5555 install -r RecipeLab-<版本>.apk
```

仓库自带一个把手：`tools/install-wifi.sh <apk> <相机IP>`，会做连接、就绪检查、安装、
并提醒你收尾关掉 ADB。

### 4. 收尾

```bash
adb disconnect CAMERA_IP:5555
```

**再去 Tweak 里关掉 ADB。** `adb disconnect` 只断开电脑这一侧，相机上的守护进程还在跑。

---

## 装上之后怎么用

在 `MENU → Application → Application List` 打开 **Recipe Lab**。

| 按键 | 作用 |
|---|---|
| **波轮** | 滚动配方，任何位置都能用；实时画面立刻变化 |
| **Fn** | 打开品牌列表（左品牌 / 右配方）—— **a5100 没有 Fn 键，用不到** |
| **中心键** | **存储**当前正在预览的配方 |
| **AEL** | 隐藏面板 —— **a5100 没有 AEL 键** |
| **上下** | 在配方行和参数芯片行之间移动 |
| **TRASH** | 暂存出厂风格，再按中心键存储 |
| **快门** | 对当前预览拍一张 |
| **MENU** | 退出应用 |

**存完之后关机再开机**，这个风格就成了相机在 P/A/S/M 和录像**所有模式**下的默认，
应用关着也生效。

**徽标含义**：

| 徽标 | 含义 |
|---|---|
| `ACTIVE` | 相机里已经是这些值 |
| `PREVIEW` | 只是在看，按中心键才会保存 |
| `PROTECTED` | 相机设置存储区被写保护——装 [OpenMemories-Tweak](https://github.com/ma1co/OpenMemories-Tweak) 关掉 *Backup protection* |

**换回原样**：应用里按 TRASH + 中心键 + 关机重启；或 `Setup → Setting Reset → Camera Settings Reset`。

---

## 排错表

| 现象 | 处理 |
|---|---|
| `No devices found` | USB 必须是 **Mass Storage**；卡要插着；相机开机且显示 **USB Mode**；换线换口 |
| 卡在 `Waiting for camera to switch...` | 拔线，相机关机再开，重连，重跑 |
| 徽标显示 `PROTECTED` | 装 OpenMemories-Tweak，关掉 *Backup protection*，重试 |
| 存了但风格没生效 | **关机再开机** |
| 面板显示 `no live preview: ...` | 有别的程序占着相机，退出应用重开 |
| 文字显示 `Â·` | 旧版本，装最新 Release 的 APK |
| `adb: offline` / 超时 / 找不到设备 | 相机休眠了 / IP 变了 / 不在同一 Wi-Fi / ADB 没开；`adb disconnect` 后重连；检查访客网络隔离、VPN、终端本地网络权限 |
| MTP 正常但 adb 找不到 | MTP 和 Wi-Fi ADB 是**两条不同的连接**；按通道 B 第 2 步开 ADB |
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` | 签名不同。用同一密钥重建；或备份后在相机应用管理里卸载同包名旧应用（**卸载会清掉应用设置**） |
| RAW 文件套不上效果 | Picture Effect 类配方（应用里标 **PE**）只在 **JPEG** 画质下生效，RAW / RAW+JPEG 会被相机静默丢弃 |
| 饱和度滑块一碰就「掉档」 | 部分配方把饱和度推得比菜单滑块范围（±3）更远。菜单显示最接近的值，你一动滑块它就弹回正常范围，那份额外的力度就丢了 —— 从应用里重新存储即可 |
