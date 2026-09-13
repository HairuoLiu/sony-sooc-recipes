# 架构：为什么这样做，以及它能做到什么、做不到什么

## 一、两个上游项目，两种完全不同的原理

这是理解整个项目最重要的一件事：**它们改的不是同一个东西。**

|  | Recipe Lab | 胶片工坊 / Film Studio |
|---|---|---|
| 作者 | [voxivoid](https://github.com/voxivoid/recipe-lab-sony-pmca) | [ukiki0718-netizen](https://github.com/ukiki0718-netizen/sony-a5100-film-studio) |
| 改什么 | **相机设置存储区**：创意风格 + 饱和度/对比度/锐度、白平衡与微调、曝光补偿、DRO、图片效果，外加一个索尼从未在菜单公开的色彩矩阵开关 | **图像处理管线**：3×3 硬件色彩矩阵 + 1024 点共同 Gamma 曲线 |
| 本质 | 等于「帮你飞快地在菜单里设好一堆值」 | 真正的逐像素色彩处理 |
| 生效范围 | 关机重启后依然是相机默认，**P/A/S/M 与录像全模式**，应用关着也生效 | 拍照与实验性录像，带 30/50/70/100% 强度 |
| 强度档位 | 无（一组固定值） | 有，四档 |
| 机型覆盖 | a6000 / a6500 / a5100 / a7 II 已实机验证 | **只有 a5100 固件 1.10** |
| 依赖 | 无额外依赖 | 需要一个**不随仓库分发**的基础 APK（bonyback1 的 Ricoh 模组，基于索尼「照片效果+」） |
| 许可 | **MIT** | **PolyForm Noncommercial 1.0.0**（非 OSI 开源，禁止商用）+ 富士/索尼权利独立保留 |
| 能否自由再分发 | 可以 | 不能 |

### Recipe Lab 的天花板，必须先说清楚

a6000 没有 Picture Profile 菜单，也存不下色调曲线。所以每一款配方**只能用这台相机
存得下来的东西拼出来**：创意风格、饱和度、对比度、锐度、白平衡、曝光补偿、图片效果，
和一个隐藏色彩开关。

**因此这些是「某个味道的近似」，不是别家色彩科学的复制品。**

明确做不到的：
- Log 曲线（S-Log、V-Log、Blackmagic Film、Cinelike D）
- 带色调的黑白（硒调、蓝晒）
- 索尼摄像机那条 *Cinematone* gamma —— 固件里有，但 a6000 的相机层既不列出也不接受

### 为什么本项目选 Recipe Lab 引擎

1. **许可干净**：MIT，可以自由 fork、再分发、发布 APK。
2. **覆盖面广**：一个 APK 覆盖全部 PMCA 机型，而不是绑死一台固件。
3. **可生成**：77 款配方就是一个 Java 数组里的 77 行，天生适合从数据生成。
4. **可反复安装**：不依赖任何需要单独获取的基础 APK，不存在「你自己去找个 base.apk」的
   法律灰区。

胶片工坊的路线更「硬核」——色彩矩阵是真处理——但它绑死一台固件、需要一个不分发的
基础 APK、且许可是非商用。所以本仓库把它作为**参考目录**收录（见下），不作为引擎。

---

## 二、目录结构

```
sony-sooc-recipes/
├── catalog/
│   ├── filters.json          ★ 唯一事实来源。所有配方都登记在这里
│   ├── index.html            可浏览的滤镜浏览器（单文件，无依赖）
│   └── README.md             字段说明
├── docs/
│   ├── INSTALL.md            双通道安装
│   ├── CHANNEL-COMPARISON.md USB vs Wi-Fi ADB，含结论
│   ├── ARCHITECTURE.md       本文件
│   └── ADDING-FILTERS.md     加滤镜的完整流程
├── tools/
│   ├── validate_catalog.py   校验注册表（CI 关卡 1）
│   ├── gen_recipes.py        注册表 → Recipes.java（CI 关卡 2）
│   ├── check_fidelity.py     与真实上游逐值比对（CI 关卡 3）
│   ├── install-wifi.sh       Wi-Fi ADB 安装把手
│   └── build_apk.sh          调上游 build.sh 并套用生成的 Recipes.java
├── .github/workflows/ci.yml  三道关卡
├── LICENSE                   MIT（本仓库代码）
└── NOTICE.md                 上游归属与许可边界
```

---

## 三、数据流

```
catalog/filters.json
        │
        │  tools/gen_recipes.py
        ▼
build/recipe-lab-sony-pmca/src/com/voxivoid/recipelab/Recipes.java
        │
        │  tools/build_apk.sh  →  上游 build.sh
        │  (JDK 17 + Android SDK build-tools 30.0.3 + platform API 28 + NDK r16b)
        ▼
RecipeLab-<版本>.apk     ──  签名密钥只在本机，永不入库
        │
        │  Sony-PMCA-RE (USB)   或   adb install -r (Wi-Fi)
        ▼
相机设置存储区  ──  关机重启后依然生效
```

**手改 `Recipes.java` 是错的。** 它随时可以被重新生成、被 CI 判定为过期。要加滤镜，
改的是 `catalog/filters.json`。

---

## 四、三道 CI 关卡

| 关卡 | 脚本 | 拦住什么 |
|---|---|---|
| 1. 注册表合法 | `validate_catalog.py` | 枚举值写错、数值越界、分组顺序断裂、许可声明不诚实 |
| 2. 生成可用 | `gen_recipes.py --check` | 有人手改了 `Recipes.java`，或忘了重新生成 |
| 3. 保真 | `check_fidelity.py` | **某个配方的数值被悄悄改动**，导致 APK 拍出来的颜色和上游不一致 |

第 3 关是最关键的一关。它把上游 `Recipes.java` 拉下来，把双方的配方**展开成完整
15 值形式**后逐个比对——上游偶尔把默认值写全（比如 `Provia` 和 `Kodak T-Max` 明明
`pe=0,ev=0,dro=6` 却写满 14 个参数），我们的生成器按简写惯例折叠，两者语义相同，
所以比对必须在**语义层**做，否则会误报。

当前状态：**77 条上游配方逐值一致，0 漂移。**

---

## 五、胶片工坊的 15 款风格怎么处理

| 情况 | 处理 |
|---|---|
| 10 款富士参考风格 | 与 Recipe Lab 已有配方**一一对应**（`cross_ref` 字段），仅登记名称与来源 |
| 理光 正片/负片/高反差黑白/正负逆冲 | 同样已有对应配方 |
| **理光 森山风（Moriyama Daido Style）** | **Recipe Lab 原版没有** —— 这是两个项目间唯一真正互补的一项 |

因此本仓库补写了 `gr-moriyama`，用 Recipe Lab 的参数空间做近似（粗颗粒黑白效果）。
它标着 `"verified": false`，**未在实机上验证**，落地前请在可丢弃素材上先试拍。

那 15 款的**拟合参数一律不转录**。原因不只是许可，还有技术层面的：胶片工坊的数值是
针对它的矩阵/Gamma 管线拟合的，放进「写设置」的引擎里根本不成立。`validate_catalog.py`
里有硬性检查——`source: film-studio` 的条目一旦带上 `recipe` 字段就直接报错。

---

## 六、已知限制（诚实清单）

1. **色彩是近似，不是复制。** 一台 2014 年的机器存不下富士或柯达的色彩科学。
2. **没有强度调节。** 想淡一点，只能在应用里手动改芯片值，或者不用这款。
3. **PE 类配方要 JPEG。** 图片效果开启时创意风格会被相机忽略，且 RAW / RAW+JPEG 下
   效果会被静默丢弃。应用里标 **PE** 的就是这类。
4. **a5100 少了两个键。** 它没有 Fn 也没有 AEL，所以品牌列表浏览和隐藏面板用不了，
   但波轮能滚完全部配方。
5. **`gr-moriyama` 未验证。**
6. **本项目不改固件**，不解锁任何东西，只写相机设置存储区里你本来就能手设的那些值。
