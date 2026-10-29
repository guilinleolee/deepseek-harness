---
description: "获客运营插件组：面向 OPC 交付的获客闭环能力，合规红线为设计前提。"
kind: "package-group"
---
# Growth

[English](README.md) | 中文

## 概述

获客运营业务插件组：面向 OPC 交付的获客闭环能力（GEO 诊断、线索台账、AI 线索打分、培育文案、SOP 跟进、数据看板），合规红线（无抓取越界、无自动触达、无发送通道、审计留存）为设计前提。

## 目录

- [包](#包)
- [开发备注](#dev-note)

-----

| 包 | 职责 | `ctx` 键 |
|---|---|---|
| [`customer-acquisition/`](customer-acquisition/README.zh.md) | 获客运营存储域、PermissionContext 能力缝、合规校验器、P0 工具、Remote 网关 | `customerAcquisition`、`permissionContext` |
| [`customer-acquisition-geo/`](customer-acquisition-geo/README.zh.md) | GEO 诊断模块：边界受控的串行爬虫、确定性分析器、四个模型可见工具 | `geoDiagnosis` |

<a id="dev-note"></a>
### 开发备注

<details>
<summary>维护者工作上下文 —— 点击展开</summary>

无。

</details>
