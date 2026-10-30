# Agent Note：gather 写面把素材收进 `assets/_gather.json`，浏览器侧除源与任务配置外不持久化任何东西

Status: implemented

[English](2026-09-25-dsh-content-gather.md) | 中文

## 问题

内容创作工作台没有信息收集入口：选题情报只存在于模型的回答里，没有任何东西把它持久化。gather 视图需要一种现有接缝都不提供的形态——RSS/Atom 抓取无法在浏览器里跑（跨源 feed 没有 CORS 响应头，主流阅读器全部在服务端抓取），每条素材的正文快照和 AI 加工结果要写进作品库旁边，而源/任务配置既不该在浏览器数据被清掉后留下残影，也不该因为工作台偶然关开而丢东西。

## 决策

`packages/creation/content-outputs` 在其 Remote 上扩展出 gather 写面——本特性唯一被授权的写路径：`fetchFeed`（条件请求游标 `ETag`/`Last-Modified` 进，条目草稿加下一轮游标出；304 以 `notModified` 空列表应答）、`writeAsset`/`readAsset`（逐文件、路径硬限制在 `outputs/<主题>/assets/` 内；`*.html` 落盘前经 sanitize-html 白名单清洗）、`readGatherManifest`/`writeGatherManifest`（`assets/_gather.json`，`formatVersion 0`）、`moveAsset`、`deleteAsset`，以及 `processMaterial`（AI 面走共享 `llm` 服务：显式逐次调用，p-queue 并发 1，仅对限流用 p-retry 且优先尊重 provider `Retry-After`）。清单写入在存储层做限额修剪——每源保留最新 50 条 `unread`/`read`；`favorite`/`picked` 及其快照永不清理——被修剪条目的快照只在修剪后的清单持久化之后才删除，所以崩溃最多留下一个未被引用的文件，绝不会出现被引用却缺失的文件。原子性复用排期网关的模式：`withFileLock` + `writeFileAtomic`，Windows 重命名被杀软/索引器短暂占计时按 100ms 倍增重试五次，网关启动时清扫孤儿 `.tmp`。

并行选题库提示词第七节的三条契约一并带上：素材 id 稳定持久（feed guid，否则规范化链接的 SHA-1——原始 guid 一并保留以便换策略重算）；素材列表/详情布局是可复用的 `SplitDetail` 组件（选题库的详情面板将复用同一接缝）；每张卡片和详情都有「加入选题库」入口，挂预订契约名 `addToTopicBank(materialId)`，在本期以待开放 toast 应答，选题库上线后接入即可。

浏览器侧（`packages/client/ui-content-studio/src/client/`，gather 视图现已移除）曾拥有其余一切，且除此之外不持久化任何东西：源、任务、任务日志只存在 `content-studio.gather.` 前缀下，写入失败（配额/隐私模式）降级为内存并在界面上说明；清空浏览器数据只丢源与任务，磁盘上的素材完整保留。控制器是一个可观察状态对象，快照在每次变更时重建（若 `getSnapshot` 每次返回新对象，`useSyncExternalStore` 会无限重渲染——渲染测试抓住了这一点）。采集只在工作台打开期间进行：30 秒主循环，`visibilitychange` 暂停/恢复，重开工作台后对超间隔任务带 `since` 游标补跑一次——是补偿，不是后台轮询。源级失败启动 1h → 2h → 4h 指数退避（封顶 24h）并门控定时运行；手动触发是用户的显式意图，越过该门控。推送素材到创作视图会在清单里把它标为 `picked`，并给创作视图一个仅含 id、标题、链接的引用（共享 studio controller 上的 `PickedMaterial`——载荷永远不含正文）。

## 被否决的备选方案

**浏览器内直接抓 feed。** 被 CORS 现实否决：几乎没有 feed 带 `Access-Control-Allow-Origin`，浏览器侧抓取在大多数真实源上必然失败。Miniflux、FreshRSS、Folo 都是服务端抓取；网关承担这一角色，且不引入任何自有网络代码。

**手写清洗器。** 否决：删 `script`/`iframe` 挡不住 `javascript:`/`data:` URI、SVG/MathML 变异向量和 DOM clobbering。网关侧由白名单（sanitize-html）决定什么能存活；渲染侧 DOMPurify（`USE_PROFILES: {html: true}`、`KEEP_CONTENT: false`）作为第二层。

**源/任务配置落盘。** 否决：outputs 库是 agent 的写面，把浏览器侧配置混进去会让 agent 的文件空间与瞬态 UI 状态耦合。清空浏览器数据只丢源与任务——花了网络 I/O 换来的素材完整保留。

**用 `moveAsset(theme, from, to)` 做跨主题迁移。** 写面的 move 已泛化为显式 `fromTheme`/`toTheme`（同主题重命名是特例），因为浏览器没有其他被授权的方式来搬移已存快照；视图目前经授权的 `readAsset` → `writeAsset` → `deleteAsset` 链完成重绑定，泛化后的 move 留待直接使用。

## 后果

gather 视图是第一个写进作品库项目目录的插件表面：只含采集素材的主题会以无元数据的作品卡片（`hasMetadata: false`）出现在作品库，作品库视图本就为此保留修复提示。调度器对自身限制保持诚实——关闭工作台即停止采集，文案如实说明。web 浏览器 e2e 车道暂无 gather 场景（该车道需要完整 web 构建；CI 内由 jsdom 渲染测试覆盖视图的选中、布局与选题库契约），渲染侧 CSP 属于宿主页面，插件交付 DOMPurify 这一层，页面级策略留给外壳。
