# Agent Note：【互动】视图以库根 `_interactions.json` 为唯一真源，建成统一粉丝收件箱，本期消息唯一来源为手动导入 CSV

Status: implemented

[English](2026-09-28-dsh-content-studio-interaction.md) | 中文

## 问题

【互动】视图（规划 `D:\dsh-content-studio\docs\interaction-dev-prompt-v1.md`，开工前已刷新为 v1.1）是内容创作工作台最后一个未实现栏目：把各平台的粉丝评论、私信、@提及聚合成一个收件箱，AI 回复草稿继承绑定画像的语气，会话生命周期全部显式管理，用户洞察回流选题库。三件事在写代码前就钉死了设计：本期消息只来自手动 CSV 导入（无平台 API、无抓取、无自动发送）、AI 上游限速与配额耗尽是常态、规划第三章的冻结契约必须逐字落地——v1 文本明言不得发明代码看不见的机制。

## 决策

- **存储是唯一的库根系统文件。** `_interactions.json`（`formatVersion: 0`，未知版本整体拒载）承载会话（消息内嵌、`sentAt` 升序、会话按最新在前）、AI 洞察与 `summary` 派生缓存——缓存在每次读写时由存储层重算，工作台徽标只读，任何写方都无法使其漂移。单条坏会话丢弃并记入 `problems`；坏信封按空清单加载并命名拒因；写入整体拒绝，存储层从不代为修复。文件走与其他库根条目相同的原子写锁，`.dsh-output.json` 与主题目录零接触。
- **导入是解析-确认两步，去重与楼中楼规则冻结在解析器里。** CSV 契约是本插件自有格式（精确表头名，无别名表），仅收 UTF-8——解码出现替换符即整批拒绝（GBK 导出），不做转码猜测；单次上限 5000 行；逐行部分成功，拒绝行按物理行号（1 起）报告。会话身份 = `platform + external_user_id`；消息去重 = `platform + external_message_id`（已存在的 id 原地更新内容与时间，文件内重复折叠为末行）。楼中楼 `in_reply_to` 对库内与本批解析，未解析的父消息保留为命名警告、绝不丢弃。提交在文件锁内执行，两个导入方无法交错。
- **AI 全部显式触发、排队、逐调用如实报告。** 三个面走共享 `llm` Service Definition 与全列共用的流式/重试策略：回复草稿（固定 3 条候选，画像 digest 与推荐句式作语气基底、风格参数冲突时让位，可选模板库骨架参与输出框架）；sentiment/intent 批量识别（每批 50 条，单批输出损坏降级为 `unknown` 不中断循环）；洞察提取（每批 200 条，高频问题/痛点/兴趣方向，客户端按 label 合并计数、`generatedAt` 只盖一次）。三者计入共享 freemium 配额——草稿每次 1、识别每 50 条 1、洞察每批 1——且都不阻塞任何本地操作。
- **发送先本地存档，再敲一扇锁死的门。** 发送按钮追加 `out` 消息、`unread|pendingReply → replied`，然后才调用预留的 `sendInteractionReply` 面——恒失败的 `InteractionChannel` stub 返回 `MCP_NOT_CONFIGURED`，toast 告知回复已本地存档，状态流转从不依赖该调用。MCP 拉取入口以禁用态渲染，措辞沿用选题库 AI 占位模式。
- **回流是普通的选题库写入，带一个新来源家族。** 一条洞察成为一条 `TopicItemInput`：`source.type: "interaction"`、会话 id 作 `refId`、带创建时快照；选题库的 source 联合新增该成员（存储校验、客户端表、筛选器与 locale 标签同步）——正是规划 8.2 预期的多来源扩展。

## 与规划文本的偏离

- 规划二.2 要求新建网关包 `@deepseek-ai/dsh-content-interactions`（content-topics 先例）。未建：review/publish/template/persona 四面均以 content-outputs 为单一授权写面落地（review 笔记明确否决过同样的拆包），拆包还会切断本面依赖的 AI/配额/锁共享。规划自己的方法集条款写明"最小集，实现时微调"；实际交付 `readInteractions`/`writeInteractions`/`parseInteractionImport`/`commitInteractionImport`/`generateInteractionReply`/`classifyInteractions`/`extractInteractionInsights`/`sendInteractionReply`/`exportInteractionCsv` 九法。
- 规划二.4 与五.1 把回复模板放在 localStorage 预置表——v1 定稿时模板库尚不存在。模板库同日上线且分类表预留了 `interaction` 类，因此草稿区消费共享的 `TemplatePickerModal`（`category: 'interaction'`，渲染正文作生成骨架），localStorage 模板表取消——开工前已作为 v1.1 裁决 1 记录。
- 导出 CSV 构建器放在 `exportInteractionCsv` 面之后而非客户端：导入解析器是格式的唯一所有者，round-trip 保证应在同一模块内可测；客户端只负责落点（经 `writeAsset` 写入选定主题 `assets/`）。
- 识别循环逐批写盘（进度可持久），洞察循环内存合并、最后一次性盖章写入；识别单批失败该批消息保持 `unknown`、循环继续，洞察单批失败该批退出合并、最终 notice 报告部分失败。

## 备选方案

**按规划原稿新建 `contentInteractions` 包。** 否决，理由同 review 笔记的记录：九个方法服务的文件与七个兄弟面共享库根、写锁与 AI 策略；拆包要么复制流式/配额管线，要么被迫做 bundle 纯净门禁禁止的跨包内部导入。

**把回复草稿存在清单之外。** 否决：草稿是消息历史的一部分，必须活过浏览器更换；每会话一个 sidecar 会成倍新增需要 scanner 隐身的文件，毫无收益。其他面已在用的整清单写入配上整体校验，同样覆盖草稿。

**导入时自动分类。** 否决：规划把两套标签定为显式按钮操作，配额是真金白银的预算，导入必须完全离线可用。未分类占位（`unknown`、`source: "user"`、无 `aiMeta`）不参与渲染，不会伪装成判定。

## 后果

栏目离线闭环：导入、收件箱、筛选、标签、备注、收藏、状态流转、发送存档全部无需 LLM；真源在磁盘上，所有会话活过浏览器更换。代价：枚举表存在两份（客户端 `interaction-model.ts` 镜像网关表，由对账测试钉住），新增平台需双侧同步并补 CSV 列校验；识别与洞察循环计入共享配额桶，重收件箱会与草稿生成共享同一日预算；规划的导航带参跳转（第九章）按文档降级形态落地——ref 以文本展示，因为 `onNavigate(view, params)` 仍不存在。跨会话说明：本面只增量触碰共享装配点（`ContentStudio.tsx`、客户端 `index.ts`、`locales.ts`、content-topics 来源联合），期间兄弟会话正在做对标→选题推送；template-store spec 的过期夹具由其本人会话在我两次读取之间自行修复，本会话未代改。
