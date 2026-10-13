# 获客运营 · 数据契约 v1（已冻结）

状态：**已冻结**（2026-10-04 用户确认）。本文档自此为只读物；此后任何字段/枚举/接口变更必须走「bump domain version + 报告确认」流程（见第 8 节）。
覆盖投喂：第 4 节红线常量、第 6 节数据契约、第 9 节 PermissionContext 缝、第 10 节知识注入。
工具定义见同目录 [tools-manifest.md](./tools-manifest.md)。

---

## 0. 平台机制对齐说明（投喂基线 vs 仓库实测，以仓库为准）

按投喂要求逐条核实了「平台事实基线」，以下 4 处与投喂表述不一致，本契约与工具清单一律按仓库实测书写：

| # | 投喂表述 | 仓库实测 | 本契约取用 |
|---|---|---|---|
| 1 | `defineTool({ parameters(zod), … })` | 工具 parameters **不用 zod**，是 `ParameterSchemaSpec` 逐属性字面量 DSL（`{ type, required, description, enum, oneOf, additionalProperties }`）；zod 只用于 storage domain 记录 schema 与 schemastery 插件 Config（`packages/core/tools/src/schema.ts`） | 域 schema 用 zod（第 3 节）；工具参数用 ParameterSchemaSpec（tools-manifest） |
| 2 | 「Node 侧 `ctx.remote.$mount()` 暴露 Remote」 | `$mount()` 是**浏览器侧**动作；Node 侧声明 `TypertRemoteService` 子类 + `@Remote()` 方法，tsdown 构建期生成 `lib/typert.host.js` 与 `lib/typert.remote-client.js`，typert loader 在包挂载时自动注册进 `ctx.typert`（先例 `packages/creation/content-outputs`） | 功能等价，实施按先例：Node 包声明服务，浏览器 UI 包 `$mount` 生成工件 |
| 3 | 「`defineDomain({ version, tables, zod schema })`」含索引/迁移语义 | domain 是**纯 KV 表**：`domainTable<K, V>(zodSchema)`，无索引、无唯一约束、无就地迁移；version 不匹配 = 拒开（fail loud）。另有 `global` 单例槽（schema + initial）适合承载 settings（`packages/storage/storage-domain/src/spec.ts`） | 见第 2、3、8 节：唯一性由记录内 superRefine 自查；settings 走 global 槽而非表 |
| 4 | 「从 packages/context 的 request context 取当前操作者」 | `packages/context` 只有提示词上下文插件，无通用请求上下文容器。请求级事实的真实载体：工具路径 `exec.agent`（Agent 实例）；web 路径 user message `source.rpcId`；进程内发起链 `ctx.agents.currentInitiator()` | PermissionContext 的 `OperatorRequest` 基于这两个真实载体设计（第 7 节） |

另有两处 P0 骨架相关确认（不影响本契约）：`ui-slots` 的 register 参数无 title/icon/route 字段（展示文案走 locale 命名空间），8 页面板对齐 ui-content-studio 先例 = `sidebar.footer.action` 入口 + `shell.overlay` 全屏工作台内部分页；`dsh.client.inject` 数组元素是 npm 包名（模块图边），非 slot 名。

P2 开工前需另行核实：`ctx.web` fetch 服务的精确消费形态（投喂模块 1 要求抓取复用它）。

---

## 1. 域声明总览

```ts
// packages/growth/customer-acquisition/src/domain/spec.ts
export const customerAcquisitionDomainSpec = defineDomain({
  name: 'customer_acquisition',   // 合法：UNIT_NAME_RE = /^[a-z][a-z0-9_]*$/
  version: 1,
  global: {                        // settings 单例槽（替代投喂中的 settings 表，见对齐说明 #3）
    schema: customerAcquisitionSettingsSchema,
    initial: { geo_max_pages: 10, geo_page_timeout_ms: 10_000, sop_todo_write_enabled: true },
  },
  tables: {
    leads:              domainTable<LeadId, Lead>(leadSchema),
    lead_followups:     domainTable<FollowupId, LeadFollowup>(leadFollowupSchema),
    lead_documents:     domainTable<DocumentId, LeadDocument>(leadDocumentSchema),
    score_runs:         domainTable<ScoreRunId, ScoreRun>(scoreRunSchema),
    score_run_items:    domainTable<ScoreRunItemId, ScoreRunItem>(scoreRunItemSchema),
    icp_profiles:       domainTable<IcpProfileId, IcpProfile>(icpProfileSchema),
    score_templates:    domainTable<ScoreTemplateId, ScoreTemplate>(scoreTemplateSchema),
    content_templates:  domainTable<ContentTemplateId, ContentTemplate>(contentTemplateSchema),
    generated_contents: domainTable<GeneratedContentId, GeneratedContent>(generatedContentSchema),
    sop_templates:      domainTable<SopTemplateId, SopTemplate>(sopTemplateSchema),
    sop_tasks:          domainTable<SopTaskId, SopTask>(sopTaskSchema),
    geo_scans:          domainTable<GeoScanId, GeoScan>(geoScanSchema),
    geo_reports:        domainTable<GeoReportId, GeoReport>(geoReportSchema),
    audit_logs:         domainTable<AuditLogId, AuditLog>(auditLogSchema),
  },
})
```

与投喂第 6 节的差异（均需确认，汇总见第 9 节）：

- `settings` 由表改为域 `global` 槽（机制更贴合，字段不变）。
- 新增 `lead_documents` 表：投喂第 7 节模块 2「客户资料、行业文档以纯文本形式挂线索」在第六节没有存储落点，补此表承接（第 10 节知识注入的数据源）。
- `sop_tasks` 补 `title` 字段：投喂字段清单无任务标题/内容位，任务清单没有它不可读。
- `geo_reports` 补 `report_md` 字段：Markdown 诊断报告是核心产物且 geo_history/geo_compare 依赖历史留存，投喂字段清单未列。
- 全表统一补 `created_at`（投喂已列的表按投喂为准）/`updated_at` 惯例字段（`audit_logs`、`lead_followups`、`generated_contents` 等纯追加记录只有 `created_at`）。

打开与关闭（对齐 message-feedback 先例）：

```ts
protected async [Service.init](): Promise<void> {
  const domain = await this.ctx.storageDomain.open(customerAcquisitionDomainSpec)
  this.ctx.effect(() => async () => { await domain.close() }, 'customer-acquisition.domainClose')
  this.leads = domain.table('leads')
  // …
  await this.seedIndustryTemplates(domain)   // 幂等种子，见第 5 节
}
```

---

## 2. 通用约定

### 2.1 Branded id

全部跨边界 id 用 `Branded<B>`（`@deepseek-ai/dsh-brand`），集中在 `src/domain/ids.ts`：

```ts
export type UserId              = Branded<'UserId'>
export type LeadId              = Branded<'LeadId'>
export type FollowupId          = Branded<'FollowupId'>
export type DocumentId          = Branded<'DocumentId'>
export type ScoreRunId          = Branded<'ScoreRunId'>
export type ScoreRunItemId      = Branded<'ScoreRunItemId'>
export type IcpProfileId        = Branded<'IcpProfileId'>
export type ScoreTemplateId     = Branded<'ScoreTemplateId'>
export type ContentTemplateId   = Branded<'ContentTemplateId'>
export type GeneratedContentId  = Branded<'GeneratedContentId'>
export type SopTemplateId       = Branded<'SopTemplateId'>
export type SopTaskId           = Branded<'SopTaskId'>
export type GeoScanId           = Branded<'GeoScanId'>
export type GeoReportId         = Branded<'GeoReportId'>
export type AuditLogId          = Branded<'AuditLogId'>
```

- 生成：`crypto.randomUUID()`，zod 侧 `z.string().min(1).transform(v => v as LeadId)`（message-feedback 同模式）。
- 预置种子用**固定字符串 id**（第 5 节），因此 id 校验是 `min(1)` 而非 uuid。
- 表 key = 记录 id 本身：`domain.table('leads').put(lead.id, lead)`。

### 2.2 时间戳

epoch 毫秒整数（对齐 message-feedback 的 `nonNegativeSafeInteger`）；`updated_at >= created_at` 由各表 refine 断言。所有写经 `KvTable.update(key, fn)` 原子读改写；记录级 last-write-wins，无字段级冲突检测（单机语义）。

### 2.3 枚举策略：封闭 vs 可扩展

按 AGENTS.md「closed unions end in assertNever; merge-extensible fall through a documented default」分两类：

| 类别 | 字段 | 介质层 schema | 说明 |
|---|---|---|---|
| **封闭**（业务状态机，加值 = bump version） | `intent_level`、`leads.status`、`sop_tasks.status`、`variant`、`geo_scans.status`、`severity`、`audit_logs.source`、`opportunity_stage`、`decision_role` | `z.enum([...])` 严格拒绝未知值 | 状态流转有明确机内语义 |
| **开放**（预期增长，加值**不** bump version） | `leads.source`、`content type`（`content_templates.type` / `generated_contents.type`）、`industry`、`company_size`、`audit_logs.action`、`object_type`、`findings.category` | `z.string().min(1)`，已知值收敛为导出常量表 | 工具参数不写封闭 `enum`，改在 description 列已知值；UI 对未知值原样展示（fall through） |

开放枚举已知值常量表（`src/domain/vocab.ts`，UI 下拉与工具 description 共用）：

```ts
export const KNOWN_LEAD_SOURCES   = ['manual', 'form', 'chat', 'email', 'referral', 'geo_scan'] as const
export const KNOWN_CONTENT_TYPES  = ['wecom_first_touch', 'sms_followup', 'email_drip',
  'short_video_script', 'xiaohongshu_post', 'website_product_intro', 'customer_case'] as const
export const KNOWN_COMPANY_SIZES  = ['1-10', '11-50', '51-200', '201-1000', '1000+'] as const
```

### 2.4 KV 查询与分页

- 无索引：列表 = `entries()` 内存过滤 + 排序 + 切片；规模假设为单机万级记录内。
- 排序：默认 `created_at` 降序；list 工具统一 `limit`（default 20, max 100）/ `offset`，返回 `{ items, total }`。

### 2.5 审计埋点

所有**写操作**记 `audit_logs`（create/update/delete/restore/purge/assign/transfer/document 增删/score/content generate/sop 任务流转/模板 CRUD/settings set/GEO scan 启动）；读操作不记（防日志膨胀）。`action` 采用 `<entity>.<verb>` 点分约定（开放值），如 `lead.create`、`geo.scan.start`。

### 2.6 默认用户（单机模式）

```ts
export const DEFAULT_USER_ID = 'local-default' as UserId
export const DEFAULT_USER_DISPLAY_NAME = '本地用户'
```

Local Provider（第 7 节）恒返回它；单机模式下所有 `owner_id` 与 `audit_logs.operator_user_id` 恒为该值。

---

## 3. 表 schema 细稿

以下 zod 细稿即未来 `src/domain/spec.ts` 的实现基线。公共助手：

```ts
const epochMs = z.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER)
const brandedId = <B extends string>() => z.string().min(1).transform(v => v as Branded<B>)
const auditTrail = { created_at: epochMs, updated_at: epochMs }   // 可变表使用
```

### 3.1 leads

```ts
export const intentLevelSchema = z.enum(['high', 'mid', 'low', 'invalid'])
export const leadStatusSchema = z.enum(['active', 'archived', 'recycled'])
// 提议值（投喂未定稿）：won/lost 表示「已成交/已流失」，供看板转化率口径
export const opportunityStageSchema = z.enum(['new', 'contacted', 'nurturing', 'qualified', 'won', 'lost'])
export const decisionRoleSchema = z.enum(['decision_maker', 'influencer', 'end_user', 'gatekeeper', 'unknown'])

export const leadSchema = z.object({
  id: brandedId<LeadId>(),
  owner_id: brandedId<UserId>().optional(),          // absent = 公海
  source: z.string().min(1),                          // 开放枚举，已知值 KNOWN_LEAD_SOURCES
  company_name: z.string().min(1),
  contact_name: z.string().optional(),
  phone: z.string().optional(),                       // 宽松存储（用户手输脏字符不 fail loud），UI/extract 负责格式提示
  email: z.string().optional(),
  industry: z.string().optional(),                    // 自由文本；模板匹配 = 行业完全匹配优先，否则回退未标行业模板
  company_size: z.string().optional(),                // 开放枚举，已知值 KNOWN_COMPANY_SIZES
  demand_desc: z.string().optional(),
  budget_range: z.string().optional(),                // 自由文本（货币档位因行业而异，不做枚举）
  decision_role: decisionRoleSchema.optional(),
  intent_level: intentLevelSchema.optional(),         // 打分后回填；未打分 = absent
  tags: z.array(z.string().min(1)).refine(
    tags => new Set(tags).size === tags.length,
    { message: 'duplicate lead tag' },
  ),
  opportunity_stage: opportunityStageSchema.default('new'),
  next_followup_at: epochMs.optional(),
  status: leadStatusSchema.default('active'),         // 'recycled' 即回收站；purge = 整记录 delete
  ...auditTrail,
}).refine(lead => lead.updated_at >= lead.created_at, { path: ['updated_at'] })
```

软删语义：`lead_delete` 置 `status='recycled'` 并记审计；`lead_restore` 回 `active`；`lead_purge` 从表移除（需 `can_delete_any_lead`）。回收站 = `status='recycled'` 的筛选视图，无独立表。

### 3.2 lead_followups

```ts
export const leadFollowupSchema = z.object({
  id: brandedId<FollowupId>(),
  lead_id: brandedId<LeadId>(),
  content: z.string().min(1),
  created_at: epochMs,               // 即跟进时间；追加型表，无 updated_at
})
```

### 3.3 lead_documents（投喂缺口，待确认）

```ts
export const leadDocumentSchema = z.object({
  id: brandedId<DocumentId>(),
  lead_id: brandedId<LeadId>(),
  title: z.string().min(1),
  content: z.string().min(1).max(20_000),   // 存储上限；注入提示词时另截 KNOWLEDGE_INJECT_MAX_CHARS
  ...auditTrail,
})
```

### 3.4 score_runs / score_run_items

量纲：ICP 权重合计 100；每维度原始分 0-100，`total = Σ(原始分 × 权重 / 100)`，故 `total ∈ [0, 100]`。打分为一次 LLM 调用产出一个 run 及其 items。

```ts
export const scoreRunSchema = z.object({
  id: brandedId<ScoreRunId>(),
  lead_id: brandedId<LeadId>(),
  icp_profile_id: brandedId<IcpProfileId>(),
  template_id: brandedId<ScoreTemplateId>(),
  total: z.number().min(0).max(100),
  reason: z.string().min(1),                 // 整体文字理由
  intent_tag: intentLevelSchema,             // 自动回填 leads.intent_level
  created_at: epochMs,
})

export const scoreRunItemSchema = z.object({
  id: brandedId<ScoreRunItemId>(),
  run_id: brandedId<ScoreRunId>(),
  dimension_id: z.string().min(1),           // 引用 icp_profiles.dimensions[].id
  score: z.number().min(0).max(100),         // 该维度原始分
  weight: z.number().min(0).max(100),        // 打分时的权重快照（画像后改权重不歪曲历史）
  reason: z.string().min(1),                 // 分项理由
  created_at: epochMs,
})
```

`weight` 快照是投喂「打分历史全留存，可回溯每次理由」的落实：历史分项按当时权重复算。

### 3.5 icp_profiles

```ts
export const icpDimensionSchema = z.object({
  id: z.string().min(1),                     // 画像内唯一（superRefine 查重）
  name: z.string().min(1),
  description: z.string().min(1),
  weight: z.number().min(0).max(100),
})

export const icpProfileSchema = z.object({
  id: brandedId<IcpProfileId>(),
  name: z.string().min(1),
  industry: z.string().optional(),
  dimensions: z.array(icpDimensionSchema).min(1),
  enabled: z.boolean(),
  ...auditTrail,
}).superRefine(profile => {
  // 1) dimension id 去重  2) Σweight === 100（±0.01 浮点容差），否则拒绝保存（fail loud）
})
```

### 3.6 score_templates

```ts
export const scoreTemplateSchema = z.object({
  id: brandedId<ScoreTemplateId>(),
  name: z.string().min(1),
  industry: z.string().optional(),
  prompt_text: z.string().min(1),    // 占位符 {{lead}} {{icp_profile}} {{dimensions}} {{knowledge}}
  enabled: z.boolean(),
  ...auditTrail,
})
```

占位符语法统一 `{{name}}`；渲染时未提供的占位符替换为空串并在服务层记审计摘要。`{{knowledge}}` 注入规则见第 6 节。

### 3.7 content_templates

```ts
export const contentTemplateVariableSchema = z.object({
  name: z.string().min(1),
  description: z.string().min(1),
  example: z.string().optional(),
})

export const contentTemplateSchema = z.object({
  id: brandedId<ContentTemplateId>(),
  name: z.string().min(1),
  industry: z.string().optional(),
  type: z.string().min(1),           // 开放枚举，已知值 KNOWN_CONTENT_TYPES（7 种）
  body: z.string().min(1),           // {{variable}} 占位
  variables: z.array(contentTemplateVariableSchema),
  enabled: z.boolean(),
  ...auditTrail,
})
```

### 3.8 generated_contents

```ts
export const contentVariantSchema = z.enum(['A', 'B'])

export const generatedContentSchema = z.object({
  id: brandedId<GeneratedContentId>(),
  lead_id: brandedId<LeadId>(),
  type: z.string().min(1),                        // 与 content_templates.type 同词表
  variant: contentVariantSchema,
  content: z.string().min(1),                     // email_drip 的多轮序列整体存一条，正文内以「## 第 N 轮」分节
  template_id: brandedId<ContentTemplateId>().optional(),  // 无模板生成路径 absent
  created_at: epochMs,
})
```

红线 3 落点：本表与生成工具**只产文本，无发送通道**；CI grep 断言本插件源码无 SMTP/邮件 API/短信网关实现。

### 3.9 sop_templates

```ts
export const sopRuleSchema = z.object({
  intent_level: intentLevelSchema,               // 模板内唯一（superRefine 查重）
  cadence: z.string().min(1),                    // 节奏描述，如「D+1 微信问候，D+3 案例推送，D+7 邀约」
  points: z.array(z.string().min(1)).min(1),     // 跟进要点
  questions: z.array(z.string().min(1)),         // 沟通提问清单
  risks: z.array(z.string().min(1)),             // 风险提示
})

export const sopTemplateSchema = z.object({
  id: brandedId<SopTemplateId>(),
  name: z.string().min(1),
  industry: z.string().optional(),
  rules: z.array(sopRuleSchema).min(1),
  enabled: z.boolean(),
  ...auditTrail,
})
```

### 3.10 sop_tasks

```ts
export const sopTaskStatusSchema = z.enum(['pending', 'done', 'deferred', 'dropped'])

export const sopTaskSchema = z.object({
  id: brandedId<SopTaskId>(),
  lead_id: brandedId<LeadId>(),
  title: z.string().min(1),            // 投喂缺口，待确认：任务标题（含跟进要点引用）
  status: sopTaskStatusSchema.default('pending'),
  planned_at: epochMs,
  note: z.string().optional(),
  ...auditTrail,
})
```

todo 联动：`sop_todo_write_enabled`（settings）开启时，`sop_generate_tasks` 同步向 DSH todo 能力写任务；面板内始终呈现本表任务列表（以 packages/todo 实际 API 为准，P3 开工前核对）。

### 3.11 geo_scans / geo_reports

```ts
export const geoScanStatusSchema = z.enum(['running', 'done', 'failed'])

export const geoScanSchema = z.object({
  id: brandedId<GeoScanId>(),
  url: z.string().min(1),                    // 仅用户显式提供；http/https
  status: geoScanStatusSchema,
  started_at: epochMs,
  finished_at: epochMs.optional(),
  error: z.string().optional(),              // failed 原因
})

export const geoSeveritySchema = z.enum(['high', 'mid', 'low'])

export const geoFindingSchema = z.object({
  id: z.string().min(1),
  category: z.string().min(1),               // 开放：llms_txt / robots / sitemap / content / structure / freshness / faq / case
  severity: geoSeveritySchema,
  title: z.string().min(1),
  detail: z.string().min(1),
  evidence_page: z.string().optional(),      // 证据页 URL
})

export const geoArtifactsSchema = z.object({
  faq_material: z.string().optional(),       // FAQ 知识素材（Markdown）
  brand_kit: z.string().optional(),          // 品牌知识素材（Markdown）
  tasks: z.array(z.string().min(1)),         // 优化任务清单
})

export const geoReportSchema = z.object({
  id: brandedId<GeoReportId>(),
  scan_id: brandedId<GeoScanId>(),
  score: z.number().min(0).max(100),         // GEO 综合分
  findings: z.array(geoFindingSchema),
  llms_txt: z.string().optional(),           // 可直接部署的 llms.txt 产物；无可生成时 absent
  artifacts: geoArtifactsSchema,
  report_md: z.string().min(1),              // 投喂缺口，待确认：完整 Markdown 诊断报告留存
  pages_fetched: z.number().int().nonnegative(),      // 投喂把抓取页数与 robots 记录列在报告侧
  robots_skipped_paths: z.array(z.string()),          // robots 遵循记录：因 Disallow 被跳过的路径
  created_at: epochMs,
})
```

### 3.12 audit_logs

```ts
export const auditSourceSchema = z.enum(['web', 'agent', 'acp'])

export const auditLogSchema = z.object({
  id: brandedId<AuditLogId>(),
  source: auditSourceSchema,
  operator_user_id: brandedId<UserId>(),     // 单机恒 DEFAULT_USER_ID；平台 = 真实登录用户
  action: z.string().min(1),                 // 开放值，<entity>.<verb> 约定
  object_type: z.string().min(1),            // 开放值：lead / followup / document / score_run / content / sop_task / icp_profile / score_template / content_template / sop_template / geo_scan / settings
  object_id: z.string().optional(),          // 对象不可解析时 absent（如 settings）
  summary: z.string().min(1),
  created_at: epochMs,
})
```

平台审计员角色直接消费本表（第 9 节）；`audit_list` / `audit_export` 是平台无关的通用出口。

### 3.13 settings（global 槽）

```ts
export const customerAcquisitionSettingsSchema = z.object({
  default_icp_profile_id: z.string().min(1).optional(),
  default_score_template_id: z.string().min(1).optional(),
  geo_max_pages: z.number().int().min(1).max(20).default(10),          // 红线封顶 20
  geo_page_timeout_ms: z.number().int().min(1_000).max(10_000).default(10_000),  // 红线封顶 10s，只许更短
  sop_todo_write_enabled: z.boolean().default(true),
})
```

红线数值是 schema 上限而非配置项：`max(20)` / `max(10_000)` 编译进 zod，任何配置放大在打开域时 fail loud；抓取并发（1）与响应体上限（2MB）为代码常量，不设配置。

---

## 4. 红线常量与校验锚点（投喂第 4 节 → 代码常量）

| 红线 | 常量/位置 | 校验落点 |
|---|---|---|
| 单任务页数 ≤ 20 | `GEO_MAX_PAGES_HARD_LIMIT = 20`；settings.geo_max_pages schema `max(20)` | pre-execute 校验器 + 工具参数校验 |
| 单页超时 10s | `GEO_PAGE_TIMEOUT_MS_HARD_LIMIT = 10_000`；settings `max(10_000)` | 同上 |
| 串行并发 1 | `GEO_FETCH_CONCURRENCY = 1`（常量，无配置） | 抓取编排（P2） |
| 响应体 ≤ 2MB | `GEO_RESPONSE_MAX_BYTES = 2 * 1024 * 1024`（常量） | 同上 |
| 仅用户显式 URL + robots.txt Disallow 不抓 | 抓取编排前置检查；跳过路径记 `geo_reports.robots_skipped_paths` | pre-execute + 抓取编排（P2）+ 单测 |
| 禁批量采集手机号/邮箱、禁自动发现新域名 | pre-execute 校验器拒绝非本任务 URL 集合的请求 | pre-execute + 单测 |
| 禁自动化触达/发送通道 | 不引入依赖；CI grep 断言无 SMTP/邮件 API/短信实现 | CI 门禁（P0 建断言） |
| 模板可编辑 | 四类模板全部 storageDomain 表 + CRUD 工具 + 面板管理页 | P1/P3 |
| 数据本地 | 业务数据仅 `ctx.storageDomain('customer_acquisition')` | 架构约束，评审把关 |
| 审计日志 | 第 3.12 节 + 2.5 埋点规则 + pre-execute 兜底记录器 | P0 |

pre-execute 合规校验器（P0 交付）统一挂在 `ctx.on('tools/pre-execute', …)`，仅拦截 `customer_acquisition_*` 前缀工具；不关心的调用一律 `return next()`。每条红线至少 1 个「非法路径被拒绝」单测（投喂验收 10）。

---

## 5. 预置行业模板种子

幂等种子在域打开后执行：按固定 id 检查，缺失才写入；已存在（含被用户改过的）一律跳过，尊重用户修改。id 固定保证重复启动不重复播种。

| 套 | 前缀 | 内容 |
|---|---|---|
| 实体门店 | `seed-retail` | icp_profiles + score_templates + sop_templates + content_templates 各若干 |
| B2B 工厂商贸 | `seed-b2b-trade` | 同上 |
| 软件服务商 | `seed-software` | 同上 |

种子 id 形如 `seed-retail-icp`、`seed-b2b-trade-score`、`seed-software-sop`、`seed-retail-content-wecom`。模板正文（提示词/权重/节奏/文案）在 P1/P3 实装时随种子文件落盘，契约只冻结 id 空间与幂等策略。

---

## 6. 知识注入（投喂第 10 节）

- 注入上限常量：`KNOWLEDGE_INJECT_MAX_CHARS = 4_000`（打分与生成时，按线索聚合 lead_documents，超限截断并标注 `[已截断]`）。
- v1 无向量库/embedding/RAG：`{{knowledge}}` 占位符 = 该线索文档的顺序拼接文本。
- 预留接口（本期不实现，仅保证缝存在）：

```ts
/** Future: back this with an external vector MCP server via packages/mcp/mcp-client; signatures and tables unchanged. */
export interface KnowledgeProvider {
  retrieve(query: string, leadId: LeadId): Promise<string[]>
}
```

---

## 7. PermissionContext 缝（投喂第 9 节 → Service Definition）

三角色标准姿势：Service Definition（本包）+ Local Provider（本包默认）+ Consumer（全部工具与 Remote 方法）。ctx 键：`permissionContext`。

```ts
// —— Service Definition（src/permission/types.ts）——

/** How the operator reached this execution. */
export type OperatorChannel = 'agent' | 'web' | 'acp'

/**
 * Per-call operator reference. Built from the two real request-scoped carriers:
 * tool path passes `exec.agent`; the web Remote path passes the gateway rpcId.
 * No implementation may cache the resolved operator across calls.
 */
export interface OperatorRequest {
  via: OperatorChannel
  agentId?: string
  rpcId?: string
}

export interface OperatorCapabilities {
  /** 'all' = every lead; 'own' = only leads whose owner_id matches the operator. */
  lead_scope: 'all' | 'own'
  can_manage_global_templates: boolean
  can_delete_any_lead: boolean
  can_export: boolean
  can_manage_settings: boolean
}

export interface ResolvedOperator {
  userId: UserId
  displayName: string
  capabilities: OperatorCapabilities
}

export abstract class PermissionContextService extends Service {
  abstract resolve(request: OperatorRequest): Promise<ResolvedOperator>
}
```

**Local Provider**（单机模式）：`resolve` 恒返回 `{ userId: DEFAULT_USER_ID, displayName: DEFAULT_USER_DISPLAY_NAME, capabilities: 全量 }`。无缓存、无状态。

**解析粒度**：每次工具 `execute` 第一步、每个 `ctx.remote` 写方法入口各 resolve 一次；不得在插件启动时解析一次全局缓存（投喂红线）。web Remote 路径由服务端强制：每个读写方法按 `lead_scope` 过滤 `owner_id`，UI 隐藏入口仅是辅助。

**lead_scope 数据隔离规则**（服务端强制，两种模式同代码）：

- `own`：list 只返回 `owner_id = 自己` 或公海（owner absent）的线索；读/写他人线索拒绝；可将公海线索 assign 给自己。
- `all`：全量可见；`transfer` 可改任意归属。
- 公海（`owner_id` absent）在单机模式退化为「默认用户可领取的池子」，接口行为不变。

**平台侧 Provider 实现说明**（交付文档引此节）：平台实现 `PermissionContextService` 同名子类（Cordis 同一 ctx 键仅允许一个 Provider，平台 bundle patch 以同 id 行替换本插件的 local-provider 行即完成注入）；「角色 → capabilities」映射表（主账号/管理员/业务操作员/只读）由平台侧维护，插件不感知角色名；平台审计员直接消费 `audit_logs`。插件代码不 import 任何平台私有包。

---

## 8. 变更迁移规则

平台 storage 语义：**无就地迁移**。打开域时介质 stamp 的 version ≠ spec.version → 拒开（fail loud）。

1. **什么变更必须 bump version**：新增/删除表；任何字段增删改（含 optional 化）；封闭枚举加值；global schema 结构变更。开放枚举（2.3）加已知值**不** bump（介质层就是 string）。
2. **bump 的恢复路径**（pre-release 无兼容承诺，AGENTS.md 立场）：删除旧介质文件后重启，域以新 version 重建（json backend 介质为 Harness home 下 `customer_acquisition.json`，域名即 unit 名）。bump 提交必须附「删除介质」的交付说明。
3. **交付期数据保全**（v1 不建）：如未来需要保数据升级，另立项做「旧域导出/导入」工具，不改 backends。
4. 本契约冻结后，执行会话发现任何必须改表的场景：停下报告，等 bump 确认，不得擅改。

---

## 9. 待确认项汇总（本次产出的新增决策）

除投喂第 6 节原列字段外，本契约新增了以下决策，**逐项请确认**（全部可改，改后重新出稿）：

| # | 决策 | 理由 |
|---|---|---|
| 1 | settings 用域 `global` 槽而非表 | 平台机制正配（单值 + initial + schema）；字段不变 |
| 2 | 新增 `lead_documents` 表 | 投喂第 7 节「纯文本挂线索」缺存储落点 |
| 3 | `sop_tasks` 补 `title` 字段 | 投喂字段清单无任务标题位，任务清单不可读 |
| 4 | `geo_reports` 补 `report_md` 字段 | Markdown 报告是核心产物，历史对比依赖留存 |
| 5 | `score_run_items` 补 `weight` 快照 | 打分历史按当时权重可复算（投喂「历史可回溯」的落实） |
| 6 | `audit_logs` 补 `object_type` 字段 | 裸 object id 无类型不可查不可导 |
| 7 | `opportunity_stage` 值集 = new/contacted/nurturing/qualified/won/lost | 投喂未定稿；won/lost 供看板转化口径 |
| 8 | `decision_role` 值集 = decision_maker/influencer/end_user/gatekeeper/unknown | 投喂未定稿 |
| 9 | `phone`/`email`/`budget_range` 宽松存储（不强校验格式） | 用户手输脏字符 fail loud 会阻塞录入；格式提示在 UI/extract 层 |
| 10 | score 量纲 = 维度原始分 0-100 × 权重%，total ∈ [0,100] | 权重合计 100 的自然推论 |
| 11 | score_batch 上限 50 条/次、串行逐条打分 | LLM 成本与耗时可控 |
| 12 | 默认用户 id = `local-default` | 单机恒定值，平台模式不使用 |
| 13 | 种子 id 空间 `seed-<套>-<类>` + 幂等策略 | 预置 3 套行业模板的可回溯落点 |
| 14 | 读操作不记审计 | 防日志膨胀；写操作全覆盖 |
