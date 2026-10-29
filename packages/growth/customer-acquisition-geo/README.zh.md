---
description: "GEO（生成式引擎优化）网站诊断——获客运营功能的模块 1。对用户显式提供的站点做边界受控的串行抓取，确定性分析 AI 检索可见度（llms.txt / robots.txt / sitemap 存在性、品牌/产品/FAQ/案例内容、结构与时效性），产出 0-100 综合分、Markdown 诊断报告、可直接部署的 `"
kind: "package-bundle"
---
# @deepseek-ai/dsh-customer-acquisition-geo

[English](README.md) | 中文

## 概述

GEO（生成式引擎优化）网站诊断——获客运营功能的模块 1。对用户显式提供的站点做边界受控的串行抓取，确定性分析 AI 检索可见度（llms.txt / robots.txt / sitemap 存在性、品牌/产品/FAQ/案例内容、结构与时效性），产出 0-100 综合分、Markdown 诊断报告、可直接部署的 `llms.txt`、知识素材与优化任务清单。单向依赖主包 [`@deepseek-ai/dsh-customer-acquisition`](../customer-acquisition/README.zh.md) 的冻结存储域与审计链路；主包不依赖本包。

## 目录

- [安装](#安装)
- [合规边界（红线 1）](#合规边界红线-1)
- [工具](#工具)
- [开发备注](#dev-note)

-----

## 安装

```sh
dsh plugin --profile web add @deepseek-ai/dsh-customer-acquisition-geo
```

bundle patch 同时插入两行——主插件（若缺失）与本模块，重启 profile 后生效。

## 合规边界（红线 1）

一个 `tools/pre-execute` 校验器加爬虫本体共同执行抓取红线，与参数 schema 允许什么无关：仅处理本次调用显式给出的 http(s) 网址；串行抓取（并发 1）；单页超时 ≤ 10 秒；响应体 ≤ 2 MiB；单次最多 20 页（代码常量 + settings 上限双重封顶）；每次抓取前检查 `robots.txt`，`Disallow` 路径跳过并记入报告；不做跨域名发现；不采集手机号/邮箱。每条规则至少一个非法路径单测。

## 工具

| 名称 | 功能 |
|---|---|
| `customer_acquisition_geo_scan` | 执行一次有界诊断：综合分、发现清单、llms.txt、素材、任务清单与完整 Markdown 报告。 |
| `customer_acquisition_geo_history` | 扫描历史分页查询，按开始时间倒序，支持 URL 前缀与时间窗口过滤。 |
| `customer_acquisition_geo_report_get` | 读取一轮报告全文：发现项、产物、跳过路径、报告原文。 |
| `customer_acquisition_geo_compare` | 同站点两轮对比：分差、已解决与新增短板、差异摘要。 |

## Model Experience

### 本地 GEO 状态

#### 模型看到什么

插件加载后四个工具加入提示词组装；scan 的渲染是完整 Markdown 报告，history 每轮一行，compare 渲染摘要。抓取超时以中文工具错误呈现。

#### Token 影响

有界：插件加载期间每次组装请求多四个工具 schema（约 700 token）；报告渲染随发现项数量伸缩。

#### KV Cache 影响

schema 进入提示词前缀的工具块；插件加载或卸载会使该点之后的可复用前缀失效，与任何工具注册一致。

## Known Limitations and Deferred Work

- **分析器是确定性的，不是模型驱动的**——发现项来自结构与内容启发式；LLM 参与的内容质量评估可日后经同一服务接口加入。
- **站点覆盖以单次扫描为界**——超出 `max_pages` 的页面、JS 渲染内容与起始域名之外的子域按设计不在范围内。
- **报告存入共享域**——保留策略跟随主包审计的立场（在有部署需求之前不清理）。


<a id="dev-note"></a>
### 开发备注

<details>
<summary>维护者工作上下文 —— 点击展开</summary>

无。

</details>
