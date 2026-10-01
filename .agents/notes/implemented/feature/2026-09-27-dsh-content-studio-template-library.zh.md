# Agent Note：全局模板库把骨架资产放在输出库之外，且正文——而非变量表——是唯一事实

Status: implemented

[English](2026-09-27-dsh-content-studio-template-library.md) | 中文

## 问题

内容创作各栏目一直在重复发明初始化骨架：创作工作台长出了自己的 `_templates.json`，【互动】方案把回复话术暂存在 localStorage，往后每个栏目都会再加一套。模板库方案（v2，`D:\dsh-content-studio\docs\template-library-dev-prompt-v2.md`）要求一个全局资产库——带版本历史的变量骨架、导入导出、跨栏目弹窗调用——并受其评审的四条冻结约束：分类标签必须落盘（localStorage 禁令）、AI 不得进入保存主路径、数据契约先冻结再开发、跨栏目集成要有声明的接口而非各栏目自行猜测。

## 决策

- **模板库刻意放在输出库之外。**其余全局存储（`_schedule.json`、`_topics.json`、`_personas.json`）都放在输出库根、借扫描器的 `_` 前缀盲区隐身。模板改放 `<dsh home>/templates/`（Config `templatesRoot`，与 `root` 同法解析）：它们是骨架资产而非主题数据，输出扫描永远不该投影它们，主题清理也永远不该扫走它们。文件布局：`templates.json`（`formatVersion 0`，版本未知或解析丢记录即拒写，同 persona）、共享标签的 `taxonomy.json`、以及每次手动保存一份全量快照 `history/<id>/<version>.json`（保留最近 20 份）。九个面挂在 content-outputs Remote（`listTemplates` / `putTemplate` / `setTemplateStatus` / `deleteTemplate` / `getTemplateHistory` / `putTemplateTags` / `exportTemplates` / `importTemplates` / `processTemplateAi`），与其他写面同一载体。
- **正文是唯一事实。**围栏、行内代码、转义三感知的扫描器（`client/template/model.ts`）从 Markdown 正文推导活跃占位符集合；`reconcileVariables` 把已存元数据对齐到它——已知名字保留元数据，未知占位符生成新条目，占位符已消失的元数据进入显式的 `unused` 区（编辑器展示，绝不自动删除）。这是 AI-Gist 的 `reconcilePromptVariables` 思路（已核验 `yarin-zhang/AI-Gist`，889★）：元数据跟随正文，因为能与正文相矛盾的变量表就是第二份事实。渲染永不进入代码区域，未填或未知的名字以 `unresolved` 上报而非擅自猜测。
- **AI 显式、仅草稿、可降级。**`processTemplateAi`（generate / optimize / extract）走共享的一次性 LLM 助手，仅对限流重试；结果落入预览面板，由用户采纳进编辑器或放弃——AI 调用不落任何盘，与 persona 面一致。无 AI 时手动路径完整：直接编辑正文即可完成模板（reconcile 会接住手写的占位符），缺 key 只降级辅助功能，从不降级存储本身。
- **弹窗是契约，不是耦合。**栏目用 `TemplatePickTarget` 打开它——分类、目标字段名、`hasContent()`、可选的 `apply`——弹窗走 列表 → 变量填写（必填未满足禁用确认）→ 宿主字段有内容时先覆盖确认 的流程。弹窗从不写盘：它把渲染结果交给宿主，由宿主决定落在哪。无 `apply` 的目标是"仅复制"降级，未接入的栏目也能低成本用上弹窗。弹窗在工作台 surface 层渲染一次；首个消费者是创作栏目编辑器工具栏（分类 `creation`，填充正文）。
- **冲突与生命周期规则显式化。**导入以 `id` 为判定键，三种策略（跳过 / 覆盖并取 `max(版本)+1` / 换新 id 加后缀唯一名另存）；非法条目记名跳过，绝不连坐整包。`putTemplate` 拒绝重复显示名与未知 id（过期客户端必须重载，不能复活已删模板）。归档走独立的 `setTemplateStatus` 面，不产生快照——生命周期是簿记，不是编辑。

## 与方案文本的偏离

- 方案中的逐栏目 **field manifest**（可填充字段清单 + 结构化 `{title, body, tags, meta}` 渲染输出）本期落地为单目标的 `TemplatePickTarget`：M1 只有一个消费者、一个目标字段。结构化输出等第二个消费者出现时（M2）再定形，避免围绕单一用途过早固化。
- 方案的转义写法是 `{\{name}}`；实现用 `\{{name}}`（左花括号前置反斜杠，Handlebars 惯例），方案文档已同步改正。
- `putTemplate` 拒绝带客户端提供的 id 创建（persona 语义）；导入面直写记录——所以模板包能恢复原始 id，而表单路径不能注入 id。
- 原地再生的 typert 产物同时携带了并行发布栏目的方法——每包一份共享产物，定向再生无法只重发单个特性。

## 备选方案

**独立的 `contentTemplates` Remote 包。**否决：九个方法、几个文件，全部共享 content-outputs 已有的原子写/锁约定；第五个包只会重复挂载/peer/注册链，换不来任何隔离收益。

**内嵌版本数组（创作 `_create.json` 模式）。**对本库否决：create 为单个工作文档内嵌 30 份草稿有上限保护，而模板库是多数记录、每条都需要耐久的全文历史——独立快照文件让清单保持小巧，也让级联删除变成一次 `rm`。

**网关侧渲染。**在网关渲染正文能集中替换逻辑，但为浏览器本已持有的数据把一次文本变换推到线路调用之后；扫描/对齐/渲染三个纯函数住在库视图与弹窗共享的一个客户端模块里，网关在自己的边界上对每条存储记录重新校验。

## 后果

任何栏目现在都能从可版本化、可导出的骨架初始化表单，且不触碰业务数据；【互动】的 localStorage 预置表在 M2 有了真正的迁移目标。代价：分类清单存在两份（按 bundle 纯净门禁在客户端镜像线类型，顺序由共享常量钉住）；`unused` 变量元数据在被显式删除前一直保留，废弃占位符会按设计留在编辑器里；每次保存写一份全量快照——用磁盘换一个永远不需要 diff 引擎的回滚。跨会话备注：发布栏目在本工作期间于同一批文件中落地了它的面；模板面只触碰了自己的模块、共享接线文件（增量条目）与双语字典（追加块），定向 typert 再生从当前源码同时重发了两个特性的方法。
