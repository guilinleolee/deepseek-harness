# Agent Note：选题库把退役的「选题规划」切片变成由存储驱动的栏目——基于 `_topics.json` 的表格与看板，并接通 gather 入库

Status: implemented

[English](2026-09-25-dsh-content-topic-bank.md) | 中文

## 问题

工作台的「选题」导航此前是一张只有两张提示词卡的静态页面，选题没有任何持久化归宿：从信息收集和对标账号攒来的灵感无处打分、无处排期、也无法推送进创作。存储接缝本身已经就位——`contentTopics` Remote 读写库根的 `_topics.json`（store 100% 覆盖、`formatVersion 0` 拒载门控、坏记录进 `problems` 点名）——但没有任何东西消费它。缺的是整个前端：双视图、插件首个详情侧边面板、新增/编辑/删除、批量操作、排期联动、Markdown 导出、导航 id 更换与能力卡迁移、带参跨视图跳转，以及此前只以待开放 toast 应答的 gather 侧预订契约 `addToTopicBank`。

## 决策

视图（`TopicBankView`）经由与其他视图一致的注入面（信封解包）消费网关，快照用视图局部组件状态——加载/错误/空三态照 `ContentLibrary` 一等公民处理，`problems` 渲染为点名丢弃记录的告警条。不新增控制器：与内容库、日历一样，视图挂载即重取。视图与筛选配置持久化到 `dsh-content-studio.topicBank.config`，加载走带版本号的迁移——一个归一化函数要么完整识别存储对象、要么整体回默认值，截断的或未来版本的脏状态永远到不了组件。

两个面都渲染在 gather 阶段建立的 `SplitDetail` 复用布局上。表格按规格列展示；看板从单一来源配置 `TOPIC_STATUSES` 渲染五栏，用原生 HTML5 拖拽事件移动卡片——不新增任何依赖。跨栏拖动是一次乐观状态翻转加一次 Remote `put`；写入失败回滚到先前的快照对象并 toast，UI 永不对持久化说谎。选题库的全部逻辑——筛选（来源/状态/分数区间/标签/关键词、周/月计划窗口）、看板分组、配置迁移、Markdown 导出——都住在与 `calendar.ts`、`create.ts` 并列的 React 无关模块 `topic-bank.ts` 里。

导出 schema 严格且自逆：`planDate` 保持不带引号的 `YYYY-MM-DD`，分数保持裸数字，其余标量一律双引号并转义 `\` 与 `"`，标签是带引号的行内数组。`parseTopicsMarkdown` 只接受本 schema 自己的输出，往返无损由测试钉住。导出经 contentOutputs 路径硬限制的 `writeAsset` 写入所选主题的 `assets/`——不给插件开第二个写面。

排期联动刻意做成单向。设置或修改 `planDate` 时 `put` 一条 `content` 类型排期，其 id 由客户端生成（gather 的 id 方案——排期 store 接受任意非空 id，自备 id 让选题侧无需在返回快照里按标题/日期碰撞扫描即可记住 `scheduleItemId`）。日历对自身四种状态保持权威，两个方向都不做状态同步。删除选题弹出确认框，级联勾选框（默认勾选）先移除关联排期；级联失败则中止删除。

跨视图跳转沿用既有的 `pickMaterial` 模式：共享 studio controller 上新增 `pickTopic`/`pickedTopic`/`clearPickedTopic`，CreateView 把选题的标题、简介、描述折叠进粘贴入口后即清除。create 视图本就有预填面，规格中的剪贴板降级路径因此没有成为代码。导航把 `topics` 换为 `topicBank`；两张能力卡以空态引导页的形式存活，仍经 `CapabilityPage` 渲染——「目录 id 即词条词干」的约定与其钉住测试原样保持。过时的 `nav.topics` / `topics.title` 词条删除，另有一个词条钉住测试在新旧两本词典里逐一枚举全部 `topicBank.*` / `topic.*` 词干。

gather 契约就此闭环：ContentStudio 现在把预订的 `addToTopicBank` 处理器注入 `GatherView`，处理器把素材经 `gatherMaterialToTopicInput` 映射为一条 `idea` 状态的选题——素材的稳定 id 作 `source.refId`，链接作 `source.url`，携带 `gatheredAt` 的创建时快照作 `source.snapshot`。无处理器时的待开放 toast 保留为兜底，接通后的反馈走 gather 视图自己的 notice 通道（三个新词条）。【AI 优化选题】渲染为禁用态并提示开放版本，手动打分落 `{ source: "manual", factors: null }`；AI 打分保持 P2 的字段形态、不做实现。

## 被否决的备选方案

**看板引入拖拽库。** 被规格的零依赖规则否决：原生 `dragstart`/`dragover`/`drop` 足以覆盖跨栏移动，乐观 `put` 覆盖了库在此几何下能提供的一切。

**扫描排期 `put` 返回快照找新建 id。** 否决：按标题加日期匹配在编辑后会错配。客户端自备 id 是确定性的，代价只是品牌边界上的一次 cast。

**省掉导出解析器。** 解析器的存在是为了让发射器诚实——严格 schema 由往返测试强制，而不是靠文字承诺。它不是外来文件导入器，对其他输入一律拒绝。

**给选题库配控制器。** 否决：与 gather 调度器不同，选题库没有定时器、没有跨槽位生命周期、没有后台状态；视图局部状态加挂载重取与内容库/日历面一致，让每个复杂度层级只保留一种模式。

## 后果

三条导航入口现在以真实数据面开场，一条 gather 素材有了两条进入创作的路径——直接推送，或归一化为可打分、可排期的选题。分数列对自身能力保持诚实：仅手动值标记 `source: "manual"`，未评行显示「未评」，AI 入口写明开放时点。本包的 jsdom 测试道在其他处仍带着先于逐文件门控的 GUI 覆盖欠账（AccountSelect、CompetitorsView 等）；就本次变更而言，纯函数模块分支全覆盖，视图经 jsdom 渲染测试（含拖拽回滚）覆盖，web 浏览器 e2e 道不新增场景——与 gather 先例一致，该道需要完整 web 构建。
