# Agent Note: 信息收集视图落在既有工作台 overlay 内——网关侧写面、浏览器侧配置、不做后台轮询

Status: implemented

[English](2026-09-25-dsh-content-studio-gather.md) | 中文

## 问题

内容创作工作台需要一个信息收集面：RSS/Atom 源管理、采集任务、按 outputs 主题组织的素材库，服务创作者在动笔前的选题情报采集。约束严格：不加槽位、不改 DSH core、浏览器内不做跨源抓取（feed 不带 CORS 头）、不做后台轮询、AI 在上游额度不稳时必须可失败可重试，且运行环境是 Windows 本机——杀软与搜索索引器会瞬时占用刚关闭的文件。

## 决策

**既有 overlay 内加一个视图；既有网关上加一个写面。** gather 视图是 `ui-content-studio` 的 `shell.overlay` 页面里新增的一个 `NAV_ITEMS` 项——不加槽位、不加 footer action、不改 manifest。全部服务端行为落在 `packages/creation/content-outputs` 的六个新 `@Remote` 方法加 `processMaterial`（`fetchFeed`、`writeAsset`、`readGatherManifest`、`writeGatherManifest`、`moveAsset`、`deleteAsset`、`readAsset`——最后一个随竞品写面补入）。`list()` 投影除提示词预留的一处修正外保持不变：`_` 前缀文件不再计入素材数、不再作为成品渲染，`_gather.json` 对作品库不可见。

**存储分两层。** 源、任务、运行日志只存浏览器侧，统一前缀 `content-studio.gather.`，经一个存储模块读写（写入失败——配额、隐私模式——降级为仅内存并由界面提示）。素材只存磁盘清单 `outputs/<主题>/assets/_gather.json`（formatVersion 0）。清空浏览器数据只丢配置；已读/收藏/待创作是清单条目的字段，随素材保留，且每次合并只追加、不触碰既有条目，用户状态因此也在每次刷新后保留。

**条件请求优先于指定的 fetch 载体——偏离。** 提示词指定消费 `packages/web` 的 fetch 能力；该接面刻意不暴露任何请求/响应头，因此 ETag/Last-Modified 游标、304 处理、`Retry-After`——同一提示词的失败语义与验收清单都要求它们——经它无法实现。`fetchFeed` 改在网关内使用 Node 全局 fetch（截止时间、大小上限、调用方回传的按源游标）。硬约束全部保留：仅网关侧抓取、`packages/web` 零改动、浏览器侧零 feed 访问；改变的只是网关内的库选择。

**原子写用仓库自有包——偏离。** 提示词点名 `write-file-atomic`；仓库已拥有 `@deepseek-ai/dsh-atomic-write`（同目录独占创建临时文件、原子重命名、跨进程锁、失败清理临时文件），且 `content-schedule` 已在使用。在同一产物树上并存两套原子写协议是多余的，gather 存储改为构建在自有包之上，并在包内补足它缺的三件事：Windows EPERM/EACCES/EBUSY 重命名重试（100ms 起倍增、最多 5 次）、按文件串行、网关启动时的孤儿临时文件清扫。fsync 维持该包既有的范围外立场（其内已留 TODO）。

**AI 走 `llm` Service Definition，而非 agent 轮次。** 浏览器侧不存在补全通道；唯一现实路径是 node 侧网关消费 `llm`——session-title 一次性调用模式。`processMaterial` 执行一次框架化调用（内置技能提示词作为 system），p-queue 排队同一时刻并发 1，仅对上游限流重试（p-retry，优先遵从 provider `Retry-After`，指数退避封顶 30s，最多 4 次）。技能提示词是网关内的模块常量而非注册进技能注册表——注册表技能是 agent 可见的 loader 工具，显式按钮流程不需要。结果在模型边界做 JSON 校验；失败以 RPC 错误返回，界面呈现"未生成"加重试按钮。

**调度语义。** 页面打开期间，30 秒主节拍运行到期的定时间隔任务；`visibilitychange` 暂停/恢复；重新打开时对每个超期任务以其 `since` 游标补跑一次——这是补偿，不是轮询。关闭工作台经页面组件的 effect 清理函数释放调度器，无定时器残留。失败语义：失败的源保留其全部素材，任务记 `failed` 并附错误摘要，源按 1h → 2h → 4h → 24h 退避；304 视为成功，只刷新游标与 `lastFetchedAt`。界面文案把"仅工作台打开时采集"作为产品事实陈述。

**清洗，两层。** 网关侧，`sanitize-html` 白名单（仅 http/https scheme、强制 `rel="noopener noreferrer"`、非白名单标签连同内容丢弃）先于任何 `*.html` 快照落盘，正文截断于 100,000 字符。渲染侧，DOMPurify（`USE_PROFILES: {html: true}`、`KEEP_CONTENT: false`）。提示词的第三层——页面 CSP——无法由客户端插件实现：工作台渲染在壳层已解析完成的文档内，动态注入的 `meta` CSP 按规范被忽略；CSP 响应头属于壳层服务器的职责，不在本次改动范围内。推送至创作只携带 id、标题与 URL——从不携带正文——经既有开关控制器的扩展（`pickMaterial`/`pickedMaterial`/`clearPickedMaterial`）完成，创作视图在复制的指令前加一行素材引用。

## 考虑过的替代方案

**浏览器侧抓取（v1 提示词的做法）。** 否决：多数 feed 不带 CORS 头；所有同类参考实现（Miniflux、FreshRSS、Folo）都是服务端抓取。

**在 `content-outputs` 里建第二个 Typert 网关类承载 AI。** bundle 补丁每包只加载一个插件（default export），第二个服务类不会实例化，除非发明"父服务拉起子服务"的机制。单网关类在 `static inject` 携带 `llm` 保持加载机制不变；`llm` 服务经 base bundle 存在于每个 profile。

**只在客户端做限额。** 两侧都裁剪：客户端保证界面计数一致，网关保证 favorite/picked 豁免在持久层被强制执行、与调用方无关。被裁条目的快照删除只发生在裁剪后的清单提交之后（网关侧），崩溃可能留下孤儿文件，但绝不会留下悬空引用。

## 后果

gather 面是纯插件：从 roster 移除即整体消失，DSH core、BFF 与 `packages/web` 零改动。代价：feed 条件请求依赖源站遵循 ETag/Last-Modified（部分静态服务器忽略，此类源每次都传全量文档）；AI 质量取决于 profile 配置的 provider/model（`provider`/`model` 配置字段，默认 DeepSeek 路由）；且"每包一插件"的加载规则意味着今后同类写面都会共享网关的 `llm` 注入——竞品写面已经如此，它消费的正是这里抽取的共享 `streamLlmText` 与重试策略。
