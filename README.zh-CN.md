# Sony SOOC Recipes · 索尼直出配方

<p align="center">
  <b>简体中文</b> · <a href="README-English.md">English version</a>
  &nbsp;·&nbsp;
  <img src="https://img.shields.io/badge/catalog%20gates-passing-3fb950" alt="catalog gates">
  <a href="https://github.com/HairuoLiu/sony-sooc-recipes/releases/latest"><img src="https://img.shields.io/badge/download-Windows%20installer-2f81f7" alt="下载 Windows 安装器"></a>
  <img src="https://img.shields.io/badge/license-MIT-3fb950" alt="MIT 许可">
</p>

<!-- counts: total=164 compiled=149 -->

<p align="center">
  <img src="docs/assets/hardware/01-a7sii-application-list.jpg" width="430" alt="相机应用程序列表：每个品牌一个条目，一台机身上并排九个">
  <img src="docs/assets/hardware/02-a7sii-live-preview.jpg" width="430" alt="应用主屏：极简的实时预览，左右滑动切换滤镜">
  <br><sub><b>左边：</b>相机上的「应用程序列表」——每个品牌一个条目，一台机身上并排九个。<b>右边：</b>打开一款配方，落到能左右切换滤镜的实时预览主屏。</sub>
</p>

**一个 Windows 文件，一次点击。** 下载安装器、双击运行、插上相机——它自己认出机身，一条进度条把观感写进相机。**不用 APK、不用工具链、不用命令行**，配方就装在安装器里。
观感写的是相机自己的设置，所以**拍 JPEG 或 RAW+JPEG 都能直出成片**：JPEG 带风格，RAW 保留无风格原片；应用里标 **PE** 的效果只在 JPEG 上显现。

---

## 你有哪些胶片模拟

安装器把你的索尼变成别家相机。每个**品牌包**是一个独立应用，只装那个品牌的观感、包名不同、可在相机侧并存——你只装自己拍的牌子。

### 免费安装器 —— Base（6 个包，91 款）

| 胶片模拟 | 款数 | 里面有什么 |
|---|---:|---|
| 富士模拟 | 16 | 经典正片 · 怀旧负片 · ACROS 红滤镜 |
| 富士胶片风格 | 10 | Pro 400H · Reala 500D · 工业打印 400 |
| 柯达风格 | 20 | Portra 400 · Gold 200 · Vision3 500T |
| 小众胶片风格 | 26 | 伊尔福 HP5 · Cinestill 800T · Lomochrome |
| 理光 GR 风格 | 11 | GR 正片 · GR 高反差黑白 · GR 森山风 |
| 索尼风格 | 8 | FL（胶片感）· IN（即显）· VV2 |

上面 6 个包、91 款是**免费安装器现在带的**。整个项目一共收录 **164 款**（其中 **149 款可装进相机**），
剩下的会在改动和设计测试做完后陆续放出；**「全量版」应用目前还在研究中**，尚未发布。
**★ 顺手点个 Star**，更新发布时你会收到提醒。

---

## 一键安装

**一个文件、一次点击。不用 APK、不用工具链、不用命令行。**

### 第 1 步 · 下载安装器
从 [Releases](https://github.com/HairuoLiu/sony-sooc-recipes/releases/latest) 下载 `SonySOOCRecipes-Base-CN.exe`——这是**唯一**要下的东西。要英文界面就用 `SonySOOCRecipes-Base-EN.exe`，同一个安装器。

### 第 2 步 · 连接相机
充满电、机内插好 SD 卡、一根**能传数据**的 USB 线，并把相机设为 `设置（工具箱）→ USB 连接 → 海量存储`。开机插线，等屏幕显示 `USB Mode`。

<p align="center">
  <img src="docs/assets/install/zh-CN/01-connect-camera.png" alt="安装器第 2 步：提示「相机已连接」，下方有「立即重新检测」按钮">
</p>

### 第 3 步 · 选择配方包
双击运行安装器，它自己认出相机，然后列出它带的配方包（默认全选）；不要的取消勾选，点「下一步」。全部约 **10–15 分钟**，窗口可以最小化。

<p align="center">
  <img src="docs/assets/install/zh-CN/02-choose-packs.png" alt="安装器第 3 步：它带的配方包列表，默认全选，右上角有「全选」">
</p>

### 第 4 步 · 开始安装
点「下一步」后进度条开始走，约 **10–15 分钟**，窗口可以最小化。

<p align="center">
  <img src="docs/assets/install/zh-CN/03-installing.png" alt="安装器第 4 步：进度条显示「正在安装 1/6」">
</p>

### 第 5 步 · 拔线开拍
`MENU → 应用程序 → 应用程序列表` 里每个包一个条目，之后风格就是相机自己的行为，**P / A / S / M 和录像**全部模式生效。

> **只支持 Windows。** 安装器是 Windows 程序（Windows 7 SP1 – 11），没有 macOS / Linux 版；预编译的 APK 也不再发布。

完整图文步骤、各系统前置条件和排错表见 **[安装指南](docs/INSTALL.zh-CN.md)**。
装之前如果这台机器上已经有别处来的 Sony SOOC Recipes，先删掉——见[卸载](#卸载)。

---

## 真机实拍

<p align="center">
  <img src="docs/assets/hardware/03-a7sii-recipe-browser.jpg" width="430" alt="点进一款观感，看到它的配方——每个参数都列出来">
  <img src="docs/assets/hardware/04-a7sii-parameter-editor.jpg" width="430" alt="参数修改界面：支持 JPG / RAW 切换，各种参数可微调">
  <br><sub><b>左边：</b>点进一款观感，看到它的配方——每个参数都列出来。<b>右边：</b>参数修改界面，支持 JPG / RAW 切换，各种参数可微调。</sub>
</p>

**已在真机确认的机型：α7S II** —— 装得上、打得开、九个包同时并存。实拍照片见 **[安装指南](docs/INSTALL.zh-CN.md)**。支持列表里的其他机型是**平台层面**支持，没有逐台实测过，这两件事不是一回事。

---

<details>
<summary><b>卸载</b></summary>

## 卸载

```
MENU → Application → Application Management → Manage and Remove → 选中要删的那一项 → 移除
```

如果那个菜单项没有、或者是灰的，走 ADB 卸载（`adb uninstall com.hairuoliu.sonysoocrecipes.<品牌>`）。
卸掉应用**不会**回退已经存进相机设置的配方——还回原样：在应用里按 **TRASH** + 中心键，关机重启，或
`Setup → Setting Reset → Camera Settings Reset`。完整流程见 **[安装指南](docs/INSTALL.zh-CN.md)**。

</details>

---

## 免责声明

**这是个人非官方项目，与任何厂商都无关联。** 不由索尼制作、认可或批准，也与配方名或包名里出现的富士、柯达、徕卡、哈苏、理光、宾得等品牌无关。
所有商标归各自所有者；这里出现这些名字，只是为了说明某款配方**想模仿什么**。配方是社区推导的近似，不是官方色彩科学。第三方软件、无任何担保，风险自负。你若转发，风险随之转移给你。
来源与许可：**[NOTICE.md](NOTICE.md)**。

---

## 授权

本仓库代码 MIT。**本项目不改固件**，只写相机设置存储区里你本来就能手设的值。
装任何东西前先备份存储卡，先用可丢弃的素材试拍。软件按现状提供，不保证兼容性、色彩准确性或无侵权。
