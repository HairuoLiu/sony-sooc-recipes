# 安装通道对比：USB + Sony-PMCA-RE  vs  Wi-Fi ADB

> 结论先行：**这两条不是并列的选项，而是「入口」和「快车道」的关系。**
> **给使用者装一次 → 走 USB。自己反复刷固件级改动 → 先走 USB 打通，再开 Wi-Fi ADB 迭代。**

---

## 为什么会这样

装 Tweak（开 ADB 的那个应用）这一步**本身就得走 USB + Sony-PMCA-RE**。
也就是说 ADB 永远无法取代 USB —— 它只能接在 USB 之后。任何把两者并列比较的说法，
都漏掉了这个前置依赖。

```
        ① 一次，必须有线                        ② 之后，可选无线
   ┌──────────────────────────┐        ┌──────────────────────────┐
   │  USB + Sony-PMCA-RE      │───────▶│  Wi-Fi ADB (via Tweak)   │
   │  · 装任意 APK            │        │  · 反复重装 APK          │
   │  · 也能装 OpenMemories   │        │  · 需要先有 Tweak        │
   │    :Tweak（开 ADB 用）   │        │  · 相机需连 Wi-Fi        │
   └──────────────────────────┘        └──────────────────────────┘
          唯一入口                              迭代加速
```

---

## 逐项对比

| 维度 | USB + Sony-PMCA-RE | Wi-Fi ADB（经 OpenMemories:Tweak） |
|---|---|---|
| 本质 | 索尼自家应用商店关闭前的**同一条安装通道** | 相机 Android 层的**调试桥**（`adbd`） |
| 前置条件 | 无。相机开机即可 | **必须先装 OpenMemories:Tweak**（用 USB 装），再在 Tweak→Developer 开 Wi-Fi + ADB |
| 支持的机型 | 全部 PMCA 机型：a6000 / a6300 / a6500 / a5100 / a5000 / a7 系列 / NEX-5R/5T/6 / RX100 III–V / RX10 II–III / HX 系列… | 同上，但需该机型具备 Wi-Fi 且 Tweak 能装上 |
| 线材 | 需要。a6000 是 **micro-USB**，得用能传数据的线（纯充电线不行） | 不需要 |
| 相机端设置 | `Setup → USB Connection → **Mass Storage**` | 先配好 Wi-Fi 接入点 → Tweak 里 Enable Wifi + Enable ADB |
| 每次安装耗时 | 约 1 分钟。相机会闪黑、自动切模式几次（**正常，别按任何键**） | 数秒。`adb install -r` |
| 成功判据 | **看电脑**打印 `Task completed successfully`；相机停在 `Connecting via USB...` 像是卡住其实不是 | 看 `adb devices` 为 `device` + 安装末尾 `Success` |
| 操作性风险 | 低。全程离线，不暴露网络服务 | **中**。相机在局域网 5555 端口监听调试守护进程 |
| 典型故障 | `No devices found`、卡在 `Waiting for camera to switch...`、徽标显示 `PROTECTED` | `offline`、IP 变了、相机休眠、访客网络隔离、VPN、终端无本地网络权限 |
| 更新已装应用 | 可以，但每次都要插线 | 用 `adb install -r`，秒级 |
| 用完后 | 拔线即可 | **必须 `adb disconnect` 并在 Tweak 里关掉 ADB**，否则守护进程一直开着 |
| 跨平台 | Win / Mac / Linux（macOS 版测试较少；Linux 走 Python 源码） | 任何有 `adb` 的系统 |

---

## 什么时候用哪个

### 用 USB + Sony-PMCA-RE
- 第一次给相机装任何东西
- 给别人的相机装（不需要对方动网络设置，不需要解释 IP 和端口）
- 相机所在网络不可信，或干脆没网络
- ADB 各种连不上、懒得排查时——USB 是永远能用的兜底
- **徽标显示 `PROTECTED` 时**：需要先装 OpenMemories:Tweak 关掉 *Backup protection*，再回来装

### 用 Wi-Fi ADB
- 仓库的开发迭代（改配方 → 重新生成 → 重装，一天十几次）
- 相机装在脚架上、接线够不着的时候
- 想远程启动应用：`adb shell am start -W -n <包名>/<Activity>`

### 都不要用
- 相机不支持 PlayMemories Camera Apps（a6100/a6400/a6600/a6700/ZV-E10、a7 III 及之后、RX100 VA 及之后……）
  → 连 `MENU → Application` 都没有，任何通道都装不进去。**判断标准就是这个菜单项。**

---

## 安全提示

Wi-Fi ADB 打开期间，同一局域网内任何能连上 `相机IP:5555` 的机器都能对相机执行
adb 命令——包括卸载应用、读取存储卡文件。因此：

1. 只在**可信网络**上开 ADB
2. 用完就 `adb disconnect <IP>:5555`，并在 Tweak 里关掉 ADB
3. 不在公共 Wi-Fi、访客网络、酒店网络上开
4. 分享截图或日志前**遮住相机 IP**（本项目所有文档一律用 `CAMERA_IP` 占位符）

`adb disconnect` 只是断开电脑这一侧，**不等于关闭相机上的守护进程**——还得在
Tweak 里关。这一点两个上游项目的文档都特别强调过。

---

## 一句话总结

**USB 是「能不能装上」的问题，ADB 是「装上多快」的问题。**
先解决前者，再按需获得后者。
