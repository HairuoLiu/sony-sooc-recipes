# APK 清单 — 每个下载包里到底有什么

<p align="center"><a href="README.md">English</a> · <b>简体中文</b></p>

本文件夹记录 **当前代码树附带的每一个 APK**：全量版（all-in-one）加九个单品牌包。
品牌包是*同一个应用、同一份配方*，只是按品牌各构建一次，拥有各自的 Android 包名和各自的
启动图标，因此你只需安装自己真正在用的那个品牌。关于「什么是品牌包」、为什么包名必须不同、
以及「一台相机同一时间只有一个生效配方」这条安装前必读警告，见
**[../BRAND-PACKS.zh-CN.md](../BRAND-PACKS.zh-CN.md)**。

下表每个数字都由 `catalog/filters.json`（目录版本 **0.6.0**，更新于 2026-09-13）实时算出，
并由 CI 校验。所谓*已编译配方*，是指 APK 真正能应用的配方——使用设置存储引擎
（`recipe-lab`）。另有 15 条 `film-studio-matrix` 条目仅以名称登记（仅供查阅、不可再分发），
**不会出现在任何 APK 中**，因此不计入下列任何数字。

## 下载列表

| APK（应用名） | 包名 | 已编译配方数 | 分组数 | 子页面 |
|---|---|---:|---|---|
| **Sony SOOC Recipes**（全量版） | `com.hairuoliu.sonysoocrecipes` | **140** | 14 | [all-in-one](all-in-one.zh-CN.md) |
| Leica Looks | `com.hairuoliu.sonysoocrecipes.leica` | **20** | 1 | [leica](leica.zh-CN.md) |
| Fujifilm Looks | `com.hairuoliu.sonysoocrecipes.fujifilm` | **16** | 1 | [fujifilm](fujifilm.zh-CN.md) |
| Fuji Film Looks | `com.hairuoliu.sonysoocrecipes.filmstocks` | **10** | 1 | [filmstocks](filmstocks.zh-CN.md) |
| Ricoh GR Looks | `com.hairuoliu.sonysoocrecipes.ricoh` | **11** | 1 | [ricoh](ricoh.zh-CN.md) |
| Kodak Looks | `com.hairuoliu.sonysoocrecipes.kodak` | **20** | 1 | [kodak](kodak.zh-CN.md) |
| Pentax Looks | `com.hairuoliu.sonysoocrecipes.pentax` | **11** | 1 | [pentax](pentax.zh-CN.md) |
| Cinestill + Ilford Looks | `com.hairuoliu.sonysoocrecipes.ilford` | **9** | 2 | [ilford](ilford.zh-CN.md) |
| Hasselblad Looks | `com.hairuoliu.sonysoocrecipes.hasselblad` | **4** | 1 | [hasselblad](hasselblad.zh-CN.md) |
| Sony Looks | `com.hairuoliu.sonysoocrecipes.sony` | **8** | 1 | [sony](sony.zh-CN.md) |

**140 + 20 + 16 + 10 + 11 + 20 + 11 + 9 + 4 + 8 = 249** 条「配方列表」，但底层目录其实只有
**155** 个滤镜条目（140 已编译 + 15 仅供查阅）。总和大于 155，是因为品牌包只是共享目录上的
*视图*，而非副本——全量版里的 140 条配方，与各个单品牌包里的配方是同一批，只是汇在一处还是
拆成十处呈现的区别。

## 如何阅读子页面

每个子页面都写明该 APK 的：

- 精确的**已编译配方数**与来源分组；
- 对**每个配方是什么**的一到两句话说明——它模仿的是哪款胶片或创意风格、是彩色还是黑白、
  主导观感如何；
- 每个风格背后的**关键设置**（创意风格、色调，以及值得注意的饱和度／对比度／锐度／色彩矩阵／
  图片效果调整），全部直接取自目录，与实际 APK 应用的内容一致。

> **诚实声明。** 这些都是社区推导出的*近似*，并非任何品牌色彩科学的复制。a6000 级别的机身
> 没有 Picture Profile 菜单，也无法存储色调曲线，因此每个风格都只能用机身真正"存得下"的项目
> 拼出来。下面的说明只讲每个风格"追求什么观感"，并不是参数说明书。
