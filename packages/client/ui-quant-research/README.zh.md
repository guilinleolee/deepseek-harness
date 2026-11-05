---
description: "量化研究的 Web 面板插件：侧边栏入口加一块仅供研究的占位面板。"
kind: "package-bundle"
---
# @deepseek-ai/dsh-client-ui-quant-research

[English](README.md) | 中文

## 概述

量化研究的 Web 面板插件：一个侧边栏入口加一块声明"仅供研究"范围的框架级占位面板。Phase 1 交付挂载点与免责声明；图表、报表卡片与核心包的 Remote 面随 Phase 2 到来。node 半边是空 apply（让插件可出现在宿主 cordis.yml），用户可见内容全部在以 `./client` 导出的浏览器半边。

## 目录

- [Installation](#installation)
- [Surface](#surface)
- [Model Experience](#model-experience)
- [Known Limitations and Deferred Work](#known-limitations-and-deferred-work)
- [Dev Note](#dev-note)

-----

<a id="installation"></a>
## 安装

与核心插件经 bundle patch 一并安装：

```sh
dsh plugin --profile web add @deepseek-ai/dsh-quant-research
```

<a id="surface"></a>
## 面板

- `sidebar.footer.action` 入口在两种侧边栏状态下（宽行与图标栏）都可打开面板。
- `shell.overlay` 面呈现占位卡片：仅供研究免责声明、无实盘交易声明与后续阶段内容。Escape 或关闭按钮收起。

两组注册共享一个开闭控制器，并随声明生命周期安装。

<a id="model-experience"></a>
## 模型体验

### 占位面板

#### What the model sees

Nothing. The `sidebar.footer.action` entry and the `shell.overlay` surface are presentational; phase 1 adds no prompts, tools, or Remote reads.

#### Token effect

Zero direct tokens on every request.

#### KV Cache effect

Independent of live requests: the panel never touches a request prefix.

<a id="known-limitations-and-deferred-work"></a>
## 已知限制与延期工作

- **占位即设计** —— 真实面板（K 线/指标/收益卡片、回测报表）随 Phase 2 落地，连同核心包的 Remote 面与其 locale 字典。
- **暂无 locale 字典** —— 占位文案为固定中文；locale 命名空间随真实面板到来。

<a id="dev-note"></a>
### 开发备注

<details>
<summary>Working context for maintainers — click to expand</summary>

None.

</details>
