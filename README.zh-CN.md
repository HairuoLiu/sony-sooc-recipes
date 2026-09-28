# Sony SOOC Recipes · 索尼直出配方

<p align="center">
  <a href="README.md">English</a> · <b>简体中文</b>
</p>

<p align="center">
  <b>把你的索尼变成莱卡、哈苏、富士、理光、宾得——**164 款**别家相机色彩与胶片配方，直出 JPEG。</b>
  <br>
  <sub>**164 款**别家相机色彩与胶片配方，其中 **149 款可装进相机**——胶片观感与机型模拟，全部 SOOC</sub>
</p>

<!-- counts: total=164 compiled=149 -->

<p align="center">
  <img src="docs/assets/hardware/01-a7sii-application-list.jpg" width="320" alt="相机应用程序列表：每个品牌一个条目，一台机身上并排九个">
  <img src="docs/assets/hardware/03-a7sii-main-screen-cinestill-50d.jpg" width="320" alt="主屏选中 Cinestill 50D：Standard 风格，饱和度 −1、对比度 +1、白平衡 5600K">
  <br><sub><b>左边：</b>相机上的「应用程序列表」——每个品牌一个条目，一台机身上并排九个。<b>右边：</b>点进去落到的主屏，已经选中了一款观感。</sub>
</p>

**一个 Windows 文件，一次点击。** 下载安装器、双击运行、插上相机——它自己认出机身，一条进度条把观感写进相机。
**不用 APK、不用工具链、不用命令行**，配方就装在安装器里。

---

## 你有哪些胶片模拟

安装器把你的索尼变成别家相机。每个**品牌包**是一个独立应用，只装那个品牌的观感、包名不同、可在相机侧并存——
你只装自己拍的牌子。

### 免费安装器 —— Base（6 个包，91 款）

| Film simulation | 胶片模拟 | 款数 | 里面有什么 |
|---|---|---:|---|
| Fujifilm Style | 富士模拟 | 16 | Classic Chrome · Nostalgic Neg · Acros +R |
| Fuji Film Style | 富士胶片风格 | 10 | Pro 400H · Reala 500D · 工业打印 400 |
| Kodak Style | 柯达风格 | 20 | Portra 400 · Gold 200 · Double-X 5222 · Vision3 |
| Niche Film Style | 小众胶片风格 | 26 | Ilford HP5 · Cinestill 50D/800T · Lomochrome |
| Ricoh GR Style | 理光 GR 风格 | 11 | GR 正片 · 高反差黑白 · 森山风 |
| Sony Style | 索尼风格 | 8 | FL（胶片感）· IN（即时）· VV2 |

完整阵容还包括 **徕卡、哈苏、宾得、电影滤镜、单色** 等风格，以及**装了全部 149 款的「全量版」应用**——
单独分发。每一款都可筛选、可搜索：**[滤镜浏览器](catalog/index.html)**（单个 HTML 文件，下载后用浏览器打开即可）。

---

## 一键安装

**一个文件、一次点击。不用 APK、不用工具链、不用命令行。**

1. **下载** `SonySOOCRecipes-Base-CN.exe`：
   [Releases](https://github.com/HairuoLiu/sony-sooc-recipes/releases/latest)——这是**唯一**要下的东西。
   （要英文界面就用 `SonySOOCRecipes-Base-EN.exe`，同一个安装器。）
2. **准备相机** —— 充满电、机内插好 SD 卡、一根**能传数据**的 USB 线，并把相机设为
   `设置（工具箱）→ USB 连接 → 海量存储`。开机插线，等屏幕显示 `USB Mode`。
3. **双击运行安装器，一路点下去。** 它自己认出相机，然后列出它带的配方包（默认全选）；
   不要的取消勾选，点「下一步」。全部约 **10–15 分钟**，窗口可以最小化。
4. **拔线、关机再开机，开拍。** `MENU → 应用程序 → 应用程序列表` 里每个包一个条目，
   之后风格就是相机自己的行为，**P / A / S / M 和录像**全部模式生效。

> 🖼️ **想要更大、能左右翻的版本？** 打开
> [交互式安装演示](docs/install-walkthrough.html)——三步可翻页，底部说明同步滚动（用方向键或滑动）。

<p align="center">
  <img src="docs/assets/install/zh-CN/01-connect-camera.png" width="250" alt="安装器第 1 步：提示「相机已连接」，下方有「立即重新检测」按钮">
  <img src="docs/assets/install/zh-CN/02-choose-packs.png" width="250" alt="安装器第 2 步：它带的配方包列表，默认全选，右上角有「全选」">
  <img src="docs/assets/install/zh-CN/03-installing.png" width="250" alt="安装器第 3 步：进度条显示「正在安装 1/6」">
  <br><sub><b>第 1 步 · 连接相机</b> · <b>第 2 步 · 选择配方</b> · <b>第 3 步 · 正在安装</b></sub>
</p>

> **只支持 Windows。** 安装器是 Windows 程序（Windows 7 SP1 – 11），没有 macOS / Linux 版；预编译的 APK 也不再发布。

完整图文步骤、各系统前置条件和排错表见 **[安装指南](docs/INSTALL.zh-CN.md)**。
装之前如果这台机器上已经有别处来的 Sony SOOC Recipes，先删掉——见[卸载](#卸载)。

---

## 你该知道的几件事

- **语言跟随相机。** 把机身语言设为简体中文，配方名、分组名和界面文字会自动切换为中文——同一个应用，不需要另外下载「中文版」。机身保持英文则仍是英文。
- **安全。** 不碰固件、不解锁任何东西——写的都是你在机身菜单里本来就能手设的值，而且都可逆。但它仍是无人支持的第三方软件：先备份存储卡。其余问题见 **[常见问题](docs/FAQ.zh-CN.md#安全)**。
- **这些是近似，不是色彩科学。** 每款配方只能用这台相机**存得下来**的东西拼，是否忠实于它模仿的胶片由 `catalog/filters.json` 的 `verified` 字段逐条记录。完整来源与限制见 **[架构说明](docs/ARCHITECTURE.zh-CN.md)**。

---

## 真机实拍

<p align="center">
  <img src="docs/assets/hardware/01-a7sii-application-list.jpg" width="300" alt="应用程序列表：九个品牌包并排">
  <img src="docs/assets/hardware/03-a7sii-main-screen-cinestill-50d.jpg" width="300" alt="主屏选中 Cinestill 50D">
</p>

**已在真机确认的机型：α7S II** —— 装得上、打得开、九个包同时并存。实拍照片见
**[安装指南](docs/INSTALL.zh-CN.md)**。支持列表里的其他机型是**平台层面**支持，没有逐台实测过，这两件事不是一回事。

---

## 卸载

```
MENU → Application → Application Management → Manage and Remove → 选中要删的那一项 → 移除
```

如果那个菜单项没有、或者是灰的，走 ADB 卸载（`adb uninstall com.hairuoliu.sonysoocrecipes.<品牌>`）。
卸掉应用**不会**回退已经存进相机设置的配方——还回原样：在应用里按 **TRASH** + 中心键，关机重启，或
`Setup → Setting Reset → Camera Settings Reset`。完整流程见 **[安装指南](docs/INSTALL.zh-CN.md)**。

---

## 接下来看哪里

| 如果你想知道 | 去看 |
|---|---|
| 一步步安装，含所有前置条件 | [docs/INSTALL.zh-CN.md](docs/INSTALL.zh-CN.md) |
| 是否安全 / 提个问题 | [docs/FAQ.zh-CN.md](docs/FAQ.zh-CN.md) |
| 只装一个品牌而不是全部 | [docs/BRAND-PACKS.zh-CN.md](docs/BRAND-PACKS.zh-CN.md) |
| 一个数值怎么到达相机 | [docs/ARCHITECTURE.zh-CN.md](docs/ARCHITECTURE.zh-CN.md) |
| 浏览每一款观感 | [catalog/index.html](catalog/index.html) |

---

## 免责声明

**这是个人非官方项目，与任何厂商都无关联。** 不由索尼制作、认可或批准，也与配方名或包名里出现的富士、柯达、徕卡、哈苏、理光、宾得等品牌无关。
所有商标归各自所有者；这里出现这些名字，只是为了说明某款配方**想模仿什么**。配方是社区推导的近似，不是官方色彩科学。第三方软件、无任何担保，风险自负。你若转发，风险随之转移给你。
来源与许可：**[NOTICE.md](NOTICE.md)** · 图标：`assets/app-icon-packs/CREDITS.md`。

---

## 授权

本仓库代码 MIT。**本项目不改固件**，只写相机设置存储区里你本来就能手设的值。
装任何东西前先备份存储卡，先用可丢弃的素材试拍。软件按现状提供，不保证兼容性、色彩准确性或无侵权。
