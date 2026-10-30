---
description: "Content Studio 网页工作台：一个浏览器插件，以左侧导航渲染舆情、对标、选题库、创作、发布、复盘、互动、账号、画像与模板各视图，全部经 content-outputs Remote 读写产物库。"
kind: "package-bundle"
---

# @deepseek-ai/dsh-client-ui-content-studio

[English](README.md) | 中文

## 概述

Content Studio 是内容创作领域的网页工作台：一次安装即加入一个侧边栏入口，打开后是全帧页面，左侧导航渲染工作台首页、舆情、对标、选题库、创作、发布、复盘、互动、账号、画像与模板各视图，全部经插件自挂载的 `contentOutputs` / `contentSchedule` / `contentTopics` Remote 读写产物库。随附的 web profile 已包含它；装入其他 DSH web profile 只需一条命令。点击能力项会把含【…】填空标记的结构化指令模板复制到剪贴板——由于 composer 预填通道尚不存在，"粘贴到会话输入框"是用户的一步操作。

## 目录

- [使用本包](#use-this-package)
- [理解实现](#understand-the-implementation)
- [进一步探索](#further-exploration)
- [模型体验](#model-experience)
- [已知限制与延期工作](#known-limitations-and-deferred-work)
- [开发备注](#dev-note)

-----

<a id="use-this-package"></a>
## 使用本包

内容创作工作台插件：侧边栏入口 + 全帧创作工作台页面。入口填充侧栏外壳的 `sidebar.footer.action` 槽（宽栏时为带文字的行，窄栏时为图标），工作台填充框架的加法位 `shell.overlay` 槽——两处都是增量挂载，不替换任何现有界面。

一条命令即可装入任何 DSH web profile：`dsh plugin --profile web add @deepseek-ai/dsh-client-ui-content-studio`——本包声明了 `dsh.bundle.patch`，其 insert 清单会一并带上两个 host Remote 网关（`content-outputs`、`content-schedule`），无需任何手工步骤。

本插件是**自包含的 Remote 装配**：`apply` 通过 `ctx.remote.$mount()` 挂载自己的两个 host 贡献（`contentOutputs`、`contentSchedule`）——沿用 api-remotes 确立的模式——浏览器 bundle 自带完整服务端通信面，任何树内 BFF 装配都无需感知本插件的存在。

工作台表面由左侧内联导航渲染各视图——工作台首页、舆情、对标、选题库、创作、发布、复盘、互动、账号、画像、模板。**开始创作**是双意图能力菜单：成品页签按媒介分组（图文与视觉、文章写作、视频、音频），运营页签按流程阶段分组（发现与选题、策划与定位、发布与质检、数据与复盘）。每项能力带成熟度徽标——**已验证**、**可用**、**需配置**、**接入中**——让选择在运行前就有预期。点击会把含【…】填空标记的结构化指令模板复制到剪贴板；由于 composer 预填通道尚不存在，"粘贴到会话输入框"是用户的一步操作。

Escape 或头部关闭按钮收起页面；关闭态渲染 null，槽位注册保持挂载。两个目标槽都由其他插件声明，因此 `apply` 通过单个 `slots.inject()` 生成器按声明生命周期原子安装两个注册，组件共享一个注入的开关控制器。

**复盘**（Review）视图补完运营闭环：各平台指标导出以「解析预览—确认导入」两步流导入 CSV（未知列以勾选框呈现、坏行具名不静默丢弃），只有绑定到创作内容 ID 的作品进入分析池；看板、单作品 AI 诊断与固定六节的周期报告全部以持久化的账号基准线判定（互动率达基准两倍为爆款、低于一半为低表现、发布满 30 天按增速闸门判长尾）。AI 调用失败仍会落一份纯数据版报告；结论一键回流产入选题库，爆款模板存入 `assets/review/templates/`。存储位于主题的 `_review.json` sidecar 与隐藏全局索引——绝不触碰 `.dsh-output.json`。

对标视图新增第四小节**「声量对比」**：词行取竞品账号赛道标签的并集，每行两侧对照——我的舆情提及中命中该词的条数（标题或摘要，每次进入读一次 `getSentiment`）与该主题素材库中标题命中该词的作品数——两侧都是两个栏目已拥有的数据，因此该小节只是一个可选注入读面加一张表，每个空态都如实指路（先扫描 / 先补账号标签）。

对标作品库在手动导入之外新增两个采集入口。**排序下拉**按发布时间、互动分或最新收藏量排序——教程类账号收藏远多于点赞，只按赞排会漏掉真正的爆款。**「导入浏览器同步」**接受带外 ego-browser 采集脚本产出的 version-1 JSON（账号名称/平台/粉丝数/简介加作品数组：平台 ID、标题、点赞）：每条作品走与手动导入相同的去重路径 upsert，命中的账号回填粉丝量级（定位仅在为空时回填简介），并盖 `syncedAt` 使补采横幅消停。该 payload 只是便捷导出、不是可信传输——坏条目跳过并如实计数，绝不中断。采集脚本本身不在本包内：它按平台驱动一个已登录浏览器会话；作品行现在展示每条作品最新快照的赞/藏/评三元组。账号卡片的**「账号体检」**按钮运行八维健康体检——`audit` 报告类型的摘要把账号档案（粉丝量级、定位、变现方式）与基于中位数的分布事实配对，报告与其余两种类型一样落在「分析报告」页。

**企业舆情分析**（Sentiment）视图是基于 `_sentiment.json` 面的舆情监测面板：监控任务管理（带极性偏置的关键词组、每任务数据源勾选——RSS 源之外可选微博访客搜索与 B 站公开热搜，各按第一个监控主体抓一页匿名公开数据、被风控即降级空页，账号黑名单对社媒作者生效）、带情感占比与 14 天趋势及平台 TOP 榜的看板、每行链接原文的分类明细列表、按任务+日聚合的负面事件告警收件箱（热度对照配置阈值定 1–4 级；每行提供一键「转选题」，经共享 topics Remote 以 `idea` 状态、`舆情` 标签回流选题库）、AI 报告页（一次网关调用在存量快照上渲染五节日报，附 Markdown 下载链接；模型调用回退数据版模板时显式展示降级横幅）、以及设置表单（推送总开关、钉钉/企微 webhook 地址、SMTP 传输字段、阈值、域名与账号黑名单、保留天数）。扫描为手动优先——一个按钮驱动网关的单槽扫描（经共享 gather 抓取器取 RSS、词典预筛、批量 LLM 精析歧义条目、告警聚合，新告警落盘后向每个已配置渠道（webhook 与 SMTP 邮件）各推一条汇总）。全部数据经 `contentOutputs` 舆情 Remote 落盘，没有任何模拟环节。

<a id="model-experience"></a>
## 模型体验

间接地，经由其按钮触发的 `dsh-content-outputs` Remote：该网关在共享 `llm` 服务上组装每个框架化请求，本包只拥有点击、进行中状态与重试入口。

#### KV Cache 影响

无；本包不组装也不发送任何 provider 请求，不拥有任何请求前缀。

<a id="known-limitations-and-deferred-work"></a>
## 已知限制与延期工作

每个条目说明当前包的约束，而非一般对比或任务清单。

- **无 composer 交接**——点击能力项是复制指令而非预填会话草稿；运行时补上 draft/prefill 通道即可消除粘贴一步。
- **能力目录为静态数据**——菜单项是随包发布的数据，不是从已挂载的技能注册表派生的，因此在目录 RPC 出现之前成熟度徽标需手工维护。
- **单实例状态**——开关状态存于每次 apply 的一个控制器实例；该页面不区分会话，也不持有会话上下文。

<a id="understand-the-implementation"></a>
## 理解实现

<details>
<summary>实现细节——点击展开</summary>

插件先经 `ctx.remote.$mount()` 挂载自己的 host Remote 贡献（`contentOutputs`、`contentSchedule`、`contentTopics`），再在按精确服务名声明各命名空间的工作台 fiber 上运行控制器与两个槽位注册。两个目标槽（`sidebar.footer.action`、`shell.overlay`）都由其他插件声明，因此 `apply` 通过单个 `slots.inject()` 生成器按声明生命周期原子安装两个注册，组件共享一个注入的开关控制器。Escape 或头部关闭按钮收起页面；关闭态渲染 null，槽位注册保持挂载。

| 文件 | 职责 |
|---|---|
| [`src/client/index.ts`](src/client/index.ts) | 浏览器侧：Remote 挂载、网关闭包与槽位注册 |
| [`src/client/ContentStudio.tsx`](src/client/ContentStudio.tsx) | 页面外壳：导航、身份注入与各视图挂载 |
| [`src/client/capabilities.ts`](src/client/capabilities.ts) | 静态能力目录与成熟度徽标 |
| [`src/client/locales.ts`](src/client/locales.ts) | 全页面文案经其路由的类型化词典 |
| [`tests/apply.client.spec.ts`](tests/apply.client.spec.ts) | 槽位注册、注入面与信封解包行为 |

</details>

-----

<a id="further-exploration"></a>
## 进一步探索

- [creation 组 README](../../creation/README.zh.md) — 本页面读写的产物域。
- [content-outputs 包](../../creation/content-outputs/README.zh.md) — 每个写面背后的 Remote 网关。
- [Slots 子系统页](../../../docs/subsystems/slots.zh.md) — 两个槽位安装所用的注册接缝。
- [双语 UI 文案决策备注](../../../.agents/notes/implemented/architecture/2026-08-23-locale-owned-client-ui-copy.zh.md) — 为什么所有标签都走词典。

-----

<a id="dev-note"></a>
### 开发备注

<details>
<summary>维护者工作上下文——点击展开</summary>

无。

</details>
