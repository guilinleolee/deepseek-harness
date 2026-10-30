---
description: "内容创作产物库的 Remote 网关：只读投影加上各栏目获授权的写入面。"
kind: "package-bundle"
---
# @deepseek-ai/dsh-content-outputs

[English](README.md) | 中文

## 概述

内容创作产物库的 Remote 网关：面向「内容库」视图的只读投影，加上各栏目获授权的写入面——信息收集、对标账号、创作、画像、发布、复盘、全局模板库、互动与舆情各面。

## 目录

- [收集写面](#gather-写面)
- [创作写面](#创作写面)
- [舆情面](#舆情面)
- [模型体验](#model-experience)
- [已知限制与暂缓事项](#known-limitations-and-deferred-work)
- [开发备注](#dev-note)

-----

内容创作产物库的 Remote 网关：面向「内容库」视图的只读投影，加上各栏目获授权的写入面——信息收集、对标账号、创作、画像、发布、复盘、全局模板库与互动。每个栏目的存储遵循同一约定：主题级 sidecar 清单（`_<栏目>.json`）位于 `outputs/<主题>/assets/`，隐藏的根级索引（`_<栏目>-index.json`），且绝不触碰 `.dsh-output.json`。

库约定：库根目录（默认 `<dsh home>/outputs`，可用 `root` 配置项覆盖）下一次创作一个目录——成品文件放项目根，中间素材放 `assets/`，`.dsh-output.json` 是唯一元数据文件（format 版本 0——本后端同样拒绝更旧与更新的格式）。以 `.` 或 `_` 开头的目录名是系统条目，不是项目。`contentOutputs/list` Remote 每次调用直接扫描库根，按主题名序返回项目；损坏或未来格式的元数据不会隐藏其目录——项目以回退值投影并标记 `hasMetadata: false`，无法读取的目录在 `problems` 中具名报告。

## Gather 写面

gather 的全部存储都位于 `outputs/<主题>/assets/` 下：`_gather.json` 清单与 `*.html` 正文快照。路径受守卫（主题名与文件名必须是单一名称段，拒绝穿越）；清单整体替换一律先做限额裁剪，再经文件锁加原子重命名提交；Windows 上对杀软/索引器造成的瞬时占用按退避重试；网关启动时清扫孤儿临时文件。

- `fetchFeed` 在网关侧拉取并解析一份 feed 文档（RSS 2.0、Atom、RDF、JSON Feed），携带源上的 `ETag`/`Last-Modified` 游标；命中 304 只返回 `notModified`。浏览器自身从不抓取跨源 feed。
- `collectTopicEntries` 为一个选题分类跑一次关键词收集：分类的 RSS 源（同一白名单）加上每个关键词一页微博访客搜索与 B 站公开视频搜索，按关键词匹配并对照选题库已有的 URL 与标题去重。本方法不落盘——调用方经 topics Remote 将候选 upsert 进选题库。
- `writeAsset` 对 `*.html` 内容先经 sanitize-html 白名单清洗并截断到正文上限再落盘；其他文本文件只受硬性大小上限约束。
- `readGatherManifest` / `writeGatherManifest` 读取与整体替换清单；校验失败的条目在 `problems` 中具名，调用方不得在存在 problems 时基于该读取结果写回。
- `moveAsset` / `deleteAsset` / `readAsset` 覆盖主题内重命名、删除与文本读取。
- `processMaterial` 经共享 `llm` 服务执行一次显式、排队的模型调用（摘要、要点、选题分、标签）；限流按 `Retry-After` 感知退避重试，调用本身不落任何盘。

保留策略：每源每主题保留最近 50 条 `unread`/`read` 素材；`favorite` 与 `picked` 标记及其快照永不自动清理。

## 创作写面

`extractCreateCopy` 拉取粘贴链接背后的文章页，经 gather 清洗白名单还原为标题加可见正文——只做网络读取，不落任何盘；抓取固定在网关侧，因为浏览器无法访问跨源文章页。非 http(s) URL 在发起请求前即被拒绝；非 2xx 响应、超过响应体积上限的页面、超过存量文本上限的正文（截断并置 `truncated`）是调用方仅有的失败形态。

## 舆情面

舆情监测的存储是根级一个 `_sentiment.json` 清单（任务、提及、告警、设置与最新一份报告；`formatVersion 0`），沿用画像清单规则：坏记录具名进 `problems` 且绝不隐藏其余记录，写入拒绝触碰当前解析已丢记录的文件。

- `getSentiment` 返回投影（含存量报告）加单槽 `scanning` 标志与最近一次扫描摘要；`putSentimentTask` / `deleteSentimentTask`（级联删除该任务的提及与告警）/ `setSentimentTaskEnabled` 管理任务；`putSentimentSettings` 整体替换设置块（域名与账号黑名单、阈值、保留天数、推送总开关、webhook 地址、SMTP 传输字段）；`handleSentimentAlert` 标记一条告警已处理。
- `scanSentiment` 按每个启用任务的 `sources` 标志跑完整管线：RSS 源经共享 gather 抓取器（每源 30 条上限、关键词组过滤），勾选时另跑平台搜索。平台搜索前，关键词扩词中间件把任务主体扩成网友真实会用的搜索词（每任务每天一次 LLM 调用，缓存 24 小时，任何失败都回退到原始主体）：广度轮按每个源搜前三个扩展词；当该任务的负面提及已聚合出 1/2 级告警时，深度轮再搜后三个词并多下钻两页评论。评论层借匹配条目的平台 id（微博 mblog id、B 站 bvid）读取公开的微博 hotflow 端点与 B 站公开评论端点（先用 bvid 换出 aid）；每页评论走同一关键词过滤、域名与账号黑名单与 URL 去重，因此评论以独立平台行进入提及、分类与告警聚合。两者都是匿名公开 web 端点；主体搜索即检索过滤，社媒提及跳过关键词组但走同一两级分类。任何适配器在失败下降级为空页，被挡的源不能使扫描失败。去重按任务+URL，保留窗口与 5000 条硬上限在每次追加时裁剪，并发扫描立即拒绝。落盘后若推送开关开启，向每个已配置渠道各发一条汇总——钉钉与企业微信群机器人（纯 JSON 文本协议），以及收件人/主机/密码齐备时经 nodemailer 发一封邮件（465 隐式 TLS，其余 STARTTLS）；渠道失败仅记日志——告警已存储，推送尽力而为。
- `sentimentStats` 计算看板投影：总数、各极性计数、14 天趋势、平台 TOP 榜。
- `generateSentimentReport` 确定性选模板——常规日报，或存在未处理的 1/2 级告警时的危机专项——再按节并行生成，每节一次模型调用，正文同时绑成 Markdown 与结构化 `ir`（模板名加各节的 key/标题/正文），报告因此可跨天对比。每一节各自降级；整份生成失败才落确定性的数据版降级模板而非报错，清单只保留最新一份报告。
- `adjudicateSentimentAlert` 按需对一条告警做辩论：乐观视角（可缓释因素、误报可能）与审慎视角（升级风险）并行各出一段判断，再由综合调用权衡出结论。它不进定时扫描——由用户在告警中心逐条触发。结论存回告警的 `adjudication` 字段，重复研判覆盖旧结论；任一视角或综合失败都降级为失败说明或两段立场的确定性拼接。

## Model Experience

### 显式一次性 AI Remote

#### What the model sees

每次用户点击恰好组装一个框架化请求，走共享 `llm` 服务：素材处理、创作生成/改写/评估、对标拆解与报告、画像补全/简历解析/官网解析/社媒主页解析/报告、发布适配、复盘诊断与周期报告、模板生成/优化/提炼，以及互动回复草稿、语气/诉求识别与洞察提取、舆情扫描的批量情感精析。提示词是按面版本化的网关冻结常量（`processMaterial`、`generateCreateContent`、`analyzeCompetitorWork`），输入按配置字符上限截断，JSON 契约面严格解析并逐字段记入 problems；失败或限流的调用向调用方报错，绝不阻塞文件操作。

#### Token effect

一次点击一次请求。提示词骨架是固定常量，token 随调用方提供的素材摘录、画像摘要、会话行或洞察批次伸缩；批量流程（三版创作、50 条识别批、200 条洞察批）按请求计费。

#### KV Cache effect

无保留。每次调用都是隔离的一次性请求，没有可跨调用失效的共享会话前缀；调用方自行拥有其写入清单的内容。

## Known Limitations and Deferred Work

- **投影保持只读**——`list` 永不变更；创建与更新产物项目仍是 agent 通过自身工具完成的职责。gather 写面只写 `assets/` 下的系统文件，从不写成品。
- **成品字节仍需文件服务面**——投影只携带名字与计数。
- **全新格式**——清单与元数据的 `formatVersion 0` 无兼容性承诺，遵循仓库的预发布立场。

<a id="dev-note"></a>
### 开发备注

<details>
<summary>维护者工作上下文 —— 点击展开</summary>

无。

</details>
