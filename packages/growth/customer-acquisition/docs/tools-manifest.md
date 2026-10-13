# 获客运营 · Consumer 工具定义清单 v1（待确认稿）

状态：**已确认冻结**（2026-10-04）。新增/改名/改参走报告确认流程。
参数与输出一律使用 `ParameterSchemaSpec` / `ValueSchemaSpec` 字面量 DSL（`packages/core/tools/src/schema.ts`），**不是 zod**（与投喂基线的差异见 [data-contract.md](./data-contract.md) 第 0 节）。全部经 `defineTool({...})` + `ctx.tools.register()` 注册，注册即 effect。

> **实施注记（P0 实测）**：DSL 的数值/字符串节点只支持 `enum`/`const`/`description`/`title`/`default`/`examples` 注解，**没有 `min`/`max`/`minLen`/`maxLen` 范围注解**。本文代码块中的范围写法是文档化记号：实施时范围写进参数 `description`，由 execute 内校验、storage zod schema 与 pre-execute 合规门三层强制（P0 已按此落地）。同理，output schema 内 `required: true` 只允许出现在对象属性位置，数组 `items` 位置不接受。

数据契约见 [data-contract.md](./data-contract.md)；文中「契约 §n」指其章节。

---

## 1. 命名与风格约定

- 前缀 `customer_acquisition_`（防撞名、会话内成组），实体 + 动作：`customer_acquisition_<entity>_<action>`。对齐仓库先例（`team_task_create`、`schedule_create`、平台业务插件 `user_list` 的 snake_case 中文描述风格）。
- description 用中文（业务插件先例 `kabage-admin-tools` 同风格），写给模型：说清功能、输入约束、红线行为。
- `presentCall` 统一 generic 卡：`{ card: 'generic', title: <中文名>, detail: <一行参数摘要> }`。
- `output.render(args, value)` 统一返回 `[{ type: 'text', text: <人读 Markdown> }]`；`output.schema` 是 canonical JSON 值的 schema，execute 只返回该值。
- 本插件无文件产出 → 无 `locations`；无 diff/terminal 语义 → 全部 generic render intent。
- 工具 `timeoutMs`：涉 LLM 生成的 120s，GEO 抓取 300s，其余默认。

## 2. 公共约定

**执行骨架**（每个工具 execute 第一步到最后一步，写一次全局遵守）：

1. `const operator = await ctx.permissionContext.resolve({ via: 'agent', agentId: exec.agent?.id })` —— 每次调用解析，无缓存（契约 §7）。
2. 服务层按 `capabilities` 过滤/授权（下表逐工具标注）。
3. 操作域表；写路径追加 `audit_logs`（契约 §2.5）。
4. 返回 canonical 值；参数/权限拒绝抛 `Error(友好中文文案)`。

**权限标注**（capabilities 见契约 §7）：`scope:own-filter` = list 按 lead_scope 过滤 owner_id；`写他人需 all/can_delete_any_lead` 等逐条标注。

**分页**：`limit`（default 20, max 100）/ `offset`，返回 `{ items, total }`；默认 `created_at` 降序。

**分页 envelope 与线索概要投影**（多处引用）：

```ts
const PAGE = {
  total: { type: 'integer', description: '过滤后的记录总数（不含分页截断）' },
}
// LeadRef：线索概要投影，lead_list / score_batch / 看板等复用
const LeadRef = {
  id: { type: 'string' }, company_name: { type: 'string' },
  contact_name: { type: 'string' }, source: { type: 'string' },
  industry: { type: 'string' }, intent_level: { type: 'string' },
  opportunity_stage: { type: 'string' }, owner_id: { type: 'string' },
  status: { type: 'string' }, tags: { type: 'array', items: { type: 'string' } },
  next_followup_at: { type: 'integer' }, updated_at: { type: 'integer' },
}
```

**枚举写法**：封闭枚举用 DSL `enum`；开放枚举（`source`/`type`/`industry`/`company_size`，契约 §2.3）用 `type: 'string'` + description 列已知值，执行层只校验非空。

**红线声明**：GEO 与 extract 类工具 description 内嵌合规语义（红线 1/2）；全插件无发送通道（红线 3）由 CI grep 断言，不靠 description。

---

## 3. P0 范围（本批 4 个 + pre-execute 校验器 + audit 埋点；`settings_get` 兼冒烟工具）

### `customer_acquisition_settings_get` — P0 · 冒烟 · audit 无（读）

```ts
description: '读取获客运营插件的全局参数：默认 ICP 画像、默认打分模板、GEO 诊断的页数与超时上限、SOP 待办联动开关。'
parameters: {}
output: { schema: { type: 'object', properties: {
  settings: { type: 'object', properties: {
    default_icp_profile_id: { type: 'string' },
    default_score_template_id: { type: 'string' },
    geo_max_pages: { type: 'integer' },
    geo_page_timeout_ms: { type: 'integer' },
    sop_todo_write_enabled: { type: 'boolean' },
  }, additionalProperties: false },
}, additionalProperties: false } }
```

render：一行参数清单。权限：所有操作者。

### `customer_acquisition_settings_set` — P0 · 需 `can_manage_settings` · audit `settings.update`

```ts
description: '修改获客运营插件的全局参数。只更新传入的字段，其余保持不变；页数上限不超过 20、单页超时不超过 10 秒（合规硬上限，配置只允许更保守）。'
parameters: {
  default_icp_profile_id: { type: 'string', description: '默认 ICP 画像 id；需为已存在的画像' },
  default_score_template_id: { type: 'string', description: '默认打分模板 id；需为已存在的模板' },
  geo_max_pages: { type: 'integer', description: 'GEO 单次诊断页数上限，1-20', min: 1, max: 20 },
  geo_page_timeout_ms: { type: 'integer', description: 'GEO 单页抓取超时毫秒数，1000-10000', min: 1000, max: 10000 },
  sop_todo_write_enabled: { type: 'boolean', description: 'SOP 生成任务时是否同步写入 DSH 待办' },
}
output: 同 settings_get（返回更新后的全量 settings）。
```

引用不存在的画像/模板 id → 友好拒绝（misconfiguration fails loud）。

### `customer_acquisition_audit_list` — P0 · audit 查询 · audit 无（读）

```ts
description: '查询获客运营插件的操作审计日志。可按来源（web/agent/acp）、操作者、动作前缀、对象类型与时间范围过滤，按时间倒序分页返回。'
parameters: {
  source: { type: 'string', enum: ['web', 'agent', 'acp'], description: '操作来源过滤' },
  operator_user_id: { type: 'string', description: '按操作者过滤' },
  action_prefix: { type: 'string', description: '按动作前缀过滤，如 lead. / geo. / settings.' },
  object_type: { type: 'string', description: '按对象类型过滤，如 lead / score_run / settings' },
  from: { type: 'integer', description: '起始时间（epoch 毫秒，含）' },
  to: { type: 'integer', description: '结束时间（epoch 毫秒，含）' },
  limit: { type: 'integer', description: '每页条数，默认 20，最大 100', min: 1, max: 100 },
  offset: { type: 'integer', description: '偏移量，默认 0', min: 0 },
}
output: { schema: { type: 'object', properties: {
  items: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'string' }, source: { type: 'string' }, operator_user_id: { type: 'string' },
    action: { type: 'string' }, object_type: { type: 'string' }, object_id: { type: 'string' },
    summary: { type: 'string' }, created_at: { type: 'integer' },
  }, additionalProperties: false } },
  total: PAGE.total,
}, additionalProperties: false } }
```

### `customer_acquisition_audit_export` — P0 · 需 `can_export` · audit 无（读）

```ts
description: '按 customer_acquisition_audit_list 相同的过滤条件导出审计日志全文，支持 Markdown 表格与 CSV 两种格式；CSV 已做公式注入防护。仅导出，不发送。'
parameters: { /* 同 audit_list 全部过滤参数 */ format: { type: 'string', enum: ['markdown', 'csv'], description: '导出格式' } }
output: { schema: { type: 'object', properties: {
  format: { type: 'string' }, count: { type: 'integer' }, content: { type: 'string', description: '导出全文' },
}, additionalProperties: false } }
```

---

## 4. 模块 1 · GEO 诊断（P2，独立子包 `packages/growth/customer-acquisition-geo/`）

### `customer_acquisition_geo_scan` — P2 · audit `geo.scan.start`

```ts
description: '对用户显式提供的网站执行 GEO（生成式引擎优化）诊断并产出报告。合规边界：仅处理本次调用中用户显式给出的 URL；串行抓取（并发 1）、单页超时 10 秒、响应体上限 2MB、单次最多 20 页；抓取前检查 robots.txt，Disallow 路径跳过并记录；不自动发现新域名，不批量采集手机号/邮箱。输出：GEO 综合分（0-100）、短板发现清单、可部署的 llms.txt、FAQ/品牌知识素材、优化任务清单。'
parameters: {
  url: { type: 'string', required: true, description: '用户显式提供的站点 URL（http/https）' },
  max_pages: { type: 'integer', description: '最多抓取页数，默认 10，上限 20', min: 1, max: 20 },
}
timeoutMs: 300_000
output: { schema: { type: 'object', properties: {
  scan_id: { type: 'string' }, score: { type: 'integer' },
  findings_count: { type: 'integer' }, pages_fetched: { type: 'integer' },
  robots_skipped_paths: { type: 'array', items: { type: 'string' } },
  llms_txt: { type: 'string', description: '可直接部署的 llms.txt；无可生成时为空串' },
  report_md: { type: 'string', description: '完整 Markdown 诊断报告' },
}, additionalProperties: false } }
```

render：报告 Markdown 原文。抓取编排复用 DSH web fetch 服务（P2 开工前核对其消费形态）；边界控制全在插件层。

### `customer_acquisition_geo_history` — P2 · audit 无（读）

```ts
description: '查询历史 GEO 诊断记录（含每轮得分与状态），按开始时间倒序分页返回。'
parameters: {
  url_filter: { type: 'string', description: '按 URL 前缀过滤' },
  from: { type: 'integer' }, to: { type: 'integer' },
  limit: { type: 'integer', min: 1, max: 100 }, offset: { type: 'integer', min: 0 },
}
output: { schema: { type: 'object', properties: {
  items: { type: 'array', items: { type: 'object', properties: {
    scan_id: { type: 'string' }, report_id: { type: 'string' }, url: { type: 'string' },
    status: { type: 'string' }, score: { type: 'integer' }, pages_fetched: { type: 'integer' },
    started_at: { type: 'integer' },
  }, additionalProperties: false } },
  total: PAGE.total,
}, additionalProperties: false } }
```

### `customer_acquisition_geo_report_get` — P2 · audit 无（读）

```ts
description: '按报告 id 读取一轮 GEO 诊断的完整报告：综合分、全部发现项、llms.txt 产物、FAQ/品牌素材、优化任务清单与 Markdown 报告原文。'
parameters: { report_id: { type: 'string', required: true } }
output: { schema: { type: 'object', properties: {
  report: { type: 'object', properties: {
    id: { type: 'string' }, scan_id: { type: 'string' }, url: { type: 'string' },
    score: { type: 'integer' }, findings: { type: 'array', items: { type: 'object', properties: {
      category: { type: 'string' }, severity: { type: 'string' }, title: { type: 'string' },
      detail: { type: 'string' }, evidence_page: { type: 'string' },
    }, additionalProperties: false } },
    llms_txt: { type: 'string' }, report_md: { type: 'string' },
    robots_skipped_paths: { type: 'array', items: { type: 'string' } }, created_at: { type: 'integer' },
  }, additionalProperties: false },
}, additionalProperties: false } }
```

### `customer_acquisition_geo_compare` — P2 · audit 无（读）

```ts
description: '对比两轮 GEO 诊断报告：总分变化、已解决与新增的短板、逐项差异摘要。两份报告须来自同一站点。'
parameters: {
  report_a_id: { type: 'string', required: true, description: '基线报告 id' },
  report_b_id: { type: 'string', required: true, description: '对比报告 id' },
}
output: { schema: { type: 'object', properties: {
  score_a: { type: 'integer' }, score_b: { type: 'integer' }, score_delta: { type: 'integer' },
  resolved: { type: 'array', items: { type: 'string' } },
  introduced: { type: 'array', items: { type: 'string' } },
  summary_md: { type: 'string' },
}, additionalProperties: false } }
```

render：summary_md 原文。

---

## 5. 模块 2 · 线索台账（P1，14 个）

### `customer_acquisition_lead_create` — P1 · scope:按传入 owner 授权 · audit `lead.create`

```ts
description: '创建一条线索记录并返回完整字段。company_name 必填；source 记录线索来源，已知值 manual/form/chat/email/referral/geo_scan。tags 整体传入（数组去重）。'
parameters: {
  company_name: { type: 'string', required: true },
  source: { type: 'string', description: '线索来源；缺省 manual。已知值：manual/form/chat/email/referral/geo_scan' },
  contact_name: { type: 'string' }, phone: { type: 'string' }, email: { type: 'string' },
  industry: { type: 'string' }, company_size: { type: 'string', description: '已知值：1-10/11-50/51-200/201-1000/1000+' },
  demand_desc: { type: 'string' }, budget_range: { type: 'string' },
  decision_role: { type: 'string', enum: ['decision_maker', 'influencer', 'end_user', 'gatekeeper', 'unknown'] },
  tags: { type: 'array', items: { type: 'string' } },
  opportunity_stage: { type: 'string', enum: ['new', 'contacted', 'nurturing', 'qualified', 'won', 'lost'] },
  next_followup_at: { type: 'integer', description: '下次跟进时间（epoch 毫秒）' },
  owner_id: { type: 'string', description: '归属人；缺省为当前操作者（单机即默认用户）。lead_scope=own 时不可指定他人' },
}
output: { schema: { type: 'object', properties: { lead: { type: 'object', properties: LeadRef, additionalProperties: false } }, additionalProperties: false } }
```

### `customer_acquisition_lead_update` — P1 · 写他人线索需 all · audit `lead.update`

```ts
description: '更新线索的可编辑字段，只覆盖传入的字段。tags 为整体替换语义（传空数组即清空）。source 与 id 不可修改。intent_level 由打分流程回填，此处不接受。'
parameters: {
  lead_id: { type: 'string', required: true },
  company_name: { type: 'string' }, contact_name: { type: 'string' }, phone: { type: 'string' },
  email: { type: 'string' }, industry: { type: 'string' }, company_size: { type: 'string' },
  demand_desc: { type: 'string' }, budget_range: { type: 'string' },
  decision_role: { type: 'string', enum: ['decision_maker', 'influencer', 'end_user', 'gatekeeper', 'unknown'] },
  tags: { type: 'array', items: { type: 'string' }, description: '整体替换' },
  opportunity_stage: { type: 'string', enum: ['new', 'contacted', 'nurturing', 'qualified', 'won', 'lost'] },
  next_followup_at: { type: 'integer' },
}
output: 同 lead_create。
```

### `customer_acquisition_lead_get` — P1 · scope:own 拒绝读他人 · audit 无（读）

```ts
description: '读取一条线索的完整字段，附带最近 5 条跟进记录与全部挂接文档的标题列表；文档正文与全部跟进用 list 类工具分页查看。'
parameters: { lead_id: { type: 'string', required: true } }
output: { schema: { type: 'object', properties: {
  lead: { type: 'object', properties: LeadRef, additionalProperties: false },
  demand_desc: { type: 'string' }, budget_range: { type: 'string' },
  followups: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'string' }, content: { type: 'string' }, created_at: { type: 'integer' } }, additionalProperties: false } },
  documents: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'string' }, title: { type: 'string' } }, additionalProperties: false } },
}, additionalProperties: false } }
```

### `customer_acquisition_lead_list` — P1 · scope:own-filter · audit 无（读）

```ts
description: '按多维度筛选线索列表：状态、来源、行业、意向等级、标签（任一匹配）、归属与时间范围，支持公司名/联系人关键词模糊搜索，按创建时间倒序分页。status 缺省只看 active；回收站传 status=recycled。'
parameters: {
  status: { type: 'string', enum: ['active', 'archived', 'recycled'] },
  source: { type: 'string' }, industry: { type: 'string' },
  intent_level: { type: 'string', enum: ['high', 'mid', 'low', 'invalid'] },
  tag: { type: 'string', description: '标签任一匹配' },
  owner: { type: 'string', enum: ['me', 'pool', 'all'], description: '归属过滤：me=我的；pool=公海（无归属人）；all=全部。缺省按操作者能力决定' },
  q: { type: 'string', description: '公司名/联系人模糊搜索' },
  created_from: { type: 'integer' }, created_to: { type: 'integer' },
  limit: { type: 'integer', min: 1, max: 100 }, offset: { type: 'integer', min: 0 },
}
output: { schema: { type: 'object', properties: { items: { type: 'array', items: { type: 'object', properties: LeadRef, additionalProperties: false } }, total: PAGE.total }, additionalProperties: false } }
```

### `customer_acquisition_lead_delete` — P1 · 写他人需 all 或 `can_delete_any_lead` · audit `lead.delete`

```ts
description: '将线索移入回收站（软删除，status 置 recycled），不物理清除；可随时用 restore 恢复。'
parameters: { lead_id: { type: 'string', required: true } }
output: { schema: { type: 'object', properties: { lead_id: { type: 'string' }, status: { type: 'string' } }, additionalProperties: false } }
```

### `customer_acquisition_lead_restore` — P1 · 同 delete 权限 · audit `lead.restore`

```ts
description: '将回收站中的线索恢复为 active。'
parameters: { lead_id: { type: 'string', required: true } }
output: 同 lead_delete（status 返回 active）。
```

### `customer_acquisition_lead_purge` — P1 · 需 `can_delete_any_lead` · audit `lead.purge`

```ts
description: '物理删除一条线索及其跟进、文档、打分、内容、SOP 任务等全部关联记录，不可恢复。仅回收站（recycled）状态的线索可清除。'
parameters: { lead_id: { type: 'string', required: true } }
output: { schema: { type: 'object', properties: { purged: { type: 'boolean' } }, additionalProperties: false } }
```

### `customer_acquisition_lead_assign` — P1 · 公海领取 · audit `lead.assign`

```ts
description: '把一条公海线索（无归属人）分配给指定操作者。线索已有归属人时拒绝，应改用 transfer。'
parameters: {
  lead_id: { type: 'string', required: true },
  owner_id: { type: 'string', required: true, description: '目标归属人 id' },
}
output: { schema: { type: 'object', properties: { lead_id: { type: 'string' }, owner_id: { type: 'string' } }, additionalProperties: false } }
```

### `customer_acquisition_lead_transfer` — P1 · own 可转出自己名下；all 任意 · audit `lead.transfer`

```ts
description: '转移线索归属人。owner_id 省略表示释放到公海。'
parameters: {
  lead_id: { type: 'string', required: true },
  owner_id: { type: 'string', description: '目标归属人 id；省略 = 释放到公海' },
}
output: 同 lead_assign（owner_id 可空串表示公海）。
```

### `customer_acquisition_lead_extract` — P1 · 红线 1/2 声明 · audit `lead.extract`

```ts
description: '从用户粘贴的一段文本（表单内容/聊天记录/邮件正文）中抽取线索字段：公司名、联系人、电话、邮箱、行业、规模、需求描述、预算、决策角色。仅解析用户本次提供的文本，不做任何网络采集或批量提取；只返回识别结果，不写库——确认后用 lead_create 落库。'
parameters: {
  text: { type: 'string', required: true, description: '用户提供的原始文本，≤10000 字符', maxLen: 10000 },
  source_hint: { type: 'string', description: '来源提示（form/chat/email），辅助歧义消解' },
}
output: { schema: { type: 'object', properties: {
  fields: { type: 'object', properties: {
    company_name: { type: 'string' }, contact_name: { type: 'string' }, phone: { type: 'string' },
    email: { type: 'string' }, industry: { type: 'string' }, company_size: { type: 'string' },
    demand_desc: { type: 'string' }, budget_range: { type: 'string' },
    decision_role: { type: 'string' },
  }, additionalProperties: false },
  notes: { type: 'string', description: '抽取歧义与未识别字段的说明' },
}, additionalProperties: false } }
```

timeoutMs 120_000（内部 LLM 抽取）。

### `customer_acquisition_lead_export` — P1 · 需 `can_export` · audit `lead.export`

```ts
description: '按 lead_list 相同的筛选条件导出线索为 Markdown 表格或 CSV（含表头，电话/邮箱防公式注入）。仅导出文本，不发送。'
parameters: { /* 同 lead_list 筛选参数 */ format: { type: 'string', enum: ['markdown', 'csv'], required: true } }
output: { schema: { type: 'object', properties: {
  format: { type: 'string' }, count: { type: 'integer' }, content: { type: 'string' },
}, additionalProperties: false } }
```

### `customer_acquisition_lead_document_add` — P1 · 写他人需 all · audit `lead.document.add`

```ts
description: '给线索挂接一份纯文本资料（客户资料、行业文档、往来摘要等），供打分与文案生成时注入上下文；单份上限 20000 字符。'
parameters: {
  lead_id: { type: 'string', required: true },
  title: { type: 'string', required: true },
  content: { type: 'string', required: true, maxLen: 20000 },
}
output: { schema: { type: 'object', properties: { document: { type: 'object', properties: {
  id: { type: 'string' }, lead_id: { type: 'string' }, title: { type: 'string' } }, additionalProperties: false } }, additionalProperties: false } }
```

### `customer_acquisition_lead_document_list` — P1 · scope:own-filter · audit 无（读）

```ts
description: '列出一个线索挂接的全部文档；默认只回标题与字数，传 include_content 时返回正文。'
parameters: {
  lead_id: { type: 'string', required: true },
  include_content: { type: 'boolean', description: '默认 false' },
}
output: { schema: { type: 'object', properties: { items: { type: 'array', items: { type: 'object', properties: {
  id: { type: 'string' }, title: { type: 'string' }, char_count: { type: 'integer' }, content: { type: 'string' },
}, additionalProperties: false } } }, additionalProperties: false } }
```

### `customer_acquisition_lead_document_remove` — P1 · 写他人需 all · audit `lead.document.remove`

```ts
description: '从线索上移除一份挂接文档（物理删除该文档记录）。'
parameters: { document_id: { type: 'string', required: true } }
output: { schema: { type: 'object', properties: { removed: { type: 'boolean' } }, additionalProperties: false } }
```

### `customer_acquisition_lead_followup_add` — P1 · 投喂缺口补（契约待确认项 15） · audit `lead.followup.add`

```ts
description: '为线索追加一条跟进记录（内容为本次沟通摘要/结论）。'
parameters: {
  lead_id: { type: 'string', required: true },
  content: { type: 'string', required: true, minLen: 1 },
}
output: { schema: { type: 'object', properties: { followup: { type: 'object', properties: {
  id: { type: 'string' }, lead_id: { type: 'string' }, created_at: { type: 'integer' } }, additionalProperties: false } }, additionalProperties: false } }
```

### `customer_acquisition_lead_followup_list` — P1 · scope:own-filter · audit 无（读）

```ts
description: '分页查看一个线索的全部跟进记录，按时间倒序。'
parameters: { lead_id: { type: 'string', required: true }, limit: { type: 'integer', min: 1, max: 100 }, offset: { type: 'integer', min: 0 } }
output: { schema: { type: 'object', properties: { items: { type: 'array', items: { type: 'object', properties: {
  id: { type: 'string' }, content: { type: 'string' }, created_at: { type: 'integer' } }, additionalProperties: false } }, total: PAGE.total }, additionalProperties: false } }
```

---

## 6. 模块 3 · AI 线索打分（P1，11 个）

打分量纲与 ICP 权重校验见契约 §3.4/§3.5。模板类 CRUD 的删除保护统一规则：**被历史记录引用即拒绝删除**（fail loud），提示改用 enabled=false 停用。

### `customer_acquisition_score_one` — P1 · scope:own 拒绝打他人线索 · audit `score.run`

```ts
description: '按选定的 ICP 画像与打分模板对一条线索做 AI 打分：输出总分（0-100）、逐维度得分与理由，并自动回填意向标签（high/mid/low/invalid）。画像与模板省略时依次取：全局默认 → 按线索行业匹配 → 启用中的任一套。线索挂接的资料会按上限注入上下文。'
parameters: {
  lead_id: { type: 'string', required: true },
  icp_profile_id: { type: 'string' }, score_template_id: { type: 'string' },
}
timeoutMs: 120_000
output: { schema: { type: 'object', properties: {
  run: { type: 'object', properties: {
    id: { type: 'string' }, total: { type: 'number' }, intent_tag: { type: 'string' }, reason: { type: 'string' },
  }, additionalProperties: false },
  items: { type: 'array', items: { type: 'object', properties: {
    dimension_id: { type: 'string' }, name: { type: 'string' }, score: { type: 'number' },
    weight: { type: 'number' }, reason: { type: 'string' },
  }, additionalProperties: false } },
}, additionalProperties: false } }
```

### `customer_acquisition_score_batch` — P1 · 同上 · audit `score.batch`

```ts
description: '对最多 50 条线索逐条串行执行与 score_one 相同的 AI 打分并批量回填意向标签。单条失败不中断批次，失败清单随结果返回。'
parameters: {
  lead_ids: { type: 'array', required: true, items: { type: 'string' }, description: '线索 id 列表，1-50 条', maxLen: 50 },
  icp_profile_id: { type: 'string' }, score_template_id: { type: 'string' },
}
timeoutMs: 600_000
output: { schema: { type: 'object', properties: {
  runs: { type: 'array', items: { type: 'object', properties: {
    lead_id: { type: 'string' }, run_id: { type: 'string' }, total: { type: 'number' }, intent_tag: { type: 'string' },
  }, additionalProperties: false } },
  failed: { type: 'array', items: { type: 'object', properties: {
    lead_id: { type: 'string' }, error: { type: 'string' } }, additionalProperties: false } },
}, additionalProperties: false } }
```

### `customer_acquisition_score_history` — P1 · scope:own-filter · audit 无（读）

```ts
description: '回溯打分历史：按线索列出每次打分的总分、意向标签、整体理由与逐维度分项（含打分时的权重快照）。'
parameters: {
  lead_id: { type: 'string' }, run_id: { type: 'string' },
  limit: { type: 'integer', min: 1, max: 100 }, offset: { type: 'integer', min: 0 },
}
output: { schema: { type: 'object', properties: {
  items: { type: 'array', items: { type: 'object', properties: {
    run: { type: 'object', properties: {
      id: { type: 'string' }, lead_id: { type: 'string' }, total: { type: 'number' },
      intent_tag: { type: 'string' }, reason: { type: 'string' }, created_at: { type: 'integer' },
    }, additionalProperties: false },
    items: { type: 'array', items: { type: 'object', properties: {
      dimension_id: { type: 'string' }, score: { type: 'number' }, weight: { type: 'number' }, reason: { type: 'string' },
    }, additionalProperties: false } },
  }, additionalProperties: false } },
  total: PAGE.total,
}, additionalProperties: false } }
```

### `customer_acquisition_icp_create` — P1 · 需 `can_manage_global_templates` · audit `icp.create`

```ts
description: '新建一套 ICP 客户画像：若干评分维度及权重。权重必须合计为 100（±0.01），否则拒绝保存；维度 id 在画像内唯一。'
parameters: {
  name: { type: 'string', required: true },
  industry: { type: 'string', description: '适用行业；省略 = 通用' },
  dimensions: { type: 'array', required: true, minLen: 1, items: { type: 'object', properties: {
    id: { type: 'string', required: true, description: '维度标识，画像内唯一，如 budget_scale' },
    name: { type: 'string', required: true }, description: { type: 'string', required: true },
    weight: { type: 'number', required: true, min: 0, max: 100 },
  }, additionalProperties: false } },
  enabled: { type: 'boolean', description: '默认 true' },
}
output: { schema: { type: 'object', properties: { profile: { type: 'object', properties: {
  id: { type: 'string' }, name: { type: 'string' }, enabled: { type: 'boolean' } }, additionalProperties: false } }, additionalProperties: false } }
```

### `customer_acquisition_icp_update` — P1 · 同上 · audit `icp.update`

```ts
description: '修改 ICP 画像：名称、行业、启用状态，或整体替换维度列表（权重仍须合计 100）。历史打分不受影响（分项保存了当时的权重快照）。'
parameters: {
  icp_profile_id: { type: 'string', required: true },
  name: { type: 'string' }, industry: { type: 'string' }, enabled: { type: 'boolean' },
  dimensions: { type: 'array', minLen: 1, items: { /* 同 create */ } },
}
output: 同 icp_create。
```

### `customer_acquisition_icp_list` — P1 · audit 无（读）

```ts
description: '列出全部 ICP 画像（含维度与权重、启用状态）。'
parameters: { enabled_only: { type: 'boolean', description: '默认 false' } }
output: { schema: { type: 'object', properties: { items: { type: 'array', items: { type: 'object', properties: {
  id: { type: 'string' }, name: { type: 'string' }, industry: { type: 'string' }, enabled: { type: 'boolean' },
  dimensions: { type: 'array', items: { type: 'object', properties: {
    id: { type: 'string' }, name: { type: 'string' }, description: { type: 'string' }, weight: { type: 'number' },
  }, additionalProperties: false } },
}, additionalProperties: false } } }, additionalProperties: false } }
```

### `customer_acquisition_icp_delete` — P1 · 需 `can_manage_global_templates` · audit `icp.delete`

```ts
description: '删除一套 ICP 画像。已被打分历史引用时拒绝删除，提示改用 icp_update 停用（enabled=false）。'
parameters: { icp_profile_id: { type: 'string', required: true } }
output: { schema: { type: 'object', properties: { deleted: { type: 'boolean' } }, additionalProperties: false } }
```

### 打分模板 CRUD（4 个，与 ICP 同构） — P1 · 需 `can_manage_global_templates`

- `customer_acquisition_score_template_create` · audit `score_template.create`

```ts
description: '新建打分提示词模板。prompt_text 支持 {{lead}}（线索 JSON）、{{icp_profile}}（画像）、{{dimensions}}（维度清单）、{{knowledge}}（线索资料注入）占位符。'
parameters: {
  name: { type: 'string', required: true }, industry: { type: 'string' },
  prompt_text: { type: 'string', required: true, minLen: 1 },
  enabled: { type: 'boolean' },
}
output: { schema: { type: 'object', properties: { template: { type: 'object', properties: {
  id: { type: 'string' }, name: { type: 'string' }, enabled: { type: 'boolean' } }, additionalProperties: false } }, additionalProperties: false } }
```

- `customer_acquisition_score_template_update` · audit `score_template.update`：`score_template_id` required + 同 create 可选字段。
- `customer_acquisition_score_template_list`：`enabled_only?` → items（id/name/industry/prompt_text/enabled）。
- `customer_acquisition_score_template_delete` · 同 ICP 删除保护（被 score_runs 引用即拒）。

---

## 7. 模块 4 · 培育文案（P3，6 个） · 红线 3：仅生成，永不发送

### `customer_acquisition_content_generate` — P3 · scope:own 拒绝为他人线索生成 · audit `content.generate`

```ts
description: '为一条线索按模板个性化生成培育文案。type 已知值：wecom_first_touch（企微初次触达话术）/ sms_followup（跟进回访短信）/ email_drip（多阶段邮件培育序列，一次生成完整多轮，正文按「## 第 N 轮」分节）/ short_video_script（短视频脚本）/ xiaohongshu_post（小红书图文）/ website_product_intro（官网产品介绍）/ customer_case（客户案例）。variant 为 A/B 版本标记，一次调用生成一个版本；线索资料自动注入上下文。产物仅是文本，本插件不提供任何发送能力。'
parameters: {
  lead_id: { type: 'string', required: true },
  type: { type: 'string', required: true, description: '文案类型（见描述已知值）' },
  variant: { type: 'string', required: true, enum: ['A', 'B'], description: 'A/B 版本标记' },
  template_id: { type: 'string', description: '文案模板 id；省略时按行业匹配启用的模板' },
}
timeoutMs: 120_000
output: { schema: { type: 'object', properties: {
  content: { type: 'object', properties: {
    id: { type: 'string' }, type: { type: 'string' }, variant: { type: 'string' },
    content: { type: 'string' }, template_id: { type: 'string' },
  }, additionalProperties: false },
}, additionalProperties: false } }
```

### `customer_acquisition_content_list_by_lead` — P3 · scope:own-filter · audit 无（读）

```ts
description: '查看一个线索名下的全部历史生成产物，可按类型过滤，按生成时间倒序分页。'
parameters: {
  lead_id: { type: 'string', required: true }, type: { type: 'string' },
  limit: { type: 'integer', min: 1, max: 100 }, offset: { type: 'integer', min: 0 },
}
output: { schema: { type: 'object', properties: { items: { type: 'array', items: { type: 'object', properties: {
  id: { type: 'string' }, type: { type: 'string' }, variant: { type: 'string' },
  content: { type: 'string' }, template_id: { type: 'string' }, created_at: { type: 'integer' },
}, additionalProperties: false } }, total: PAGE.total }, additionalProperties: false } }
```

### 文案模板 CRUD（4 个） — P3 · 需 `can_manage_global_templates`

- `customer_acquisition_content_template_create` · audit `content_template.create`

```ts
description: '新建文案模板。body 支持 {{变量}} 占位；variables 声明每个占位变量的名称、说明与示例。type 已知值同 content_generate 描述。'
parameters: {
  name: { type: 'string', required: true }, type: { type: 'string', required: true },
  industry: { type: 'string' }, body: { type: 'string', required: true, minLen: 1 },
  variables: { type: 'array', items: { type: 'object', properties: {
    name: { type: 'string', required: true }, description: { type: 'string', required: true },
    example: { type: 'string' },
  }, additionalProperties: false } },
  enabled: { type: 'boolean' },
}
output: { schema: { type: 'object', properties: { template: { type: 'object', properties: {
  id: { type: 'string' }, name: { type: 'string' }, type: { type: 'string' }, enabled: { type: 'boolean' } }, additionalProperties: false } }, additionalProperties: false } }
```

- `customer_acquisition_content_template_update` · audit `content_template.update`：`content_template_id` required + 同 create 可选字段（body/variables 整体替换）。
- `customer_acquisition_content_template_list`：`type?`/`enabled_only?` → items（id/name/type/industry/body/variables/enabled）。
- `customer_acquisition_content_template_delete` · audit `content_template.delete`：被 generated_contents 引用即拒，提示停用。

---

## 8. 模块 5 · 跟进 SOP（P3，7 个）

### `customer_acquisition_sop_generate_tasks` — P3 · scope:own 拒绝 · audit `sop.tasks.generate`

```ts
description: '按线索的意向等级与 SOP 模板生成跟进任务清单：每条任务含标题（跟进要点）、计划时间（按模板节奏排期）与备注（沟通提问清单、风险提示）。线索未打分（无意向等级）时拒绝并提示先打分。全局设置开启待办联动时同步写入 DSH 待办。'
parameters: {
  lead_id: { type: 'string', required: true },
  sop_template_id: { type: 'string', description: '省略时按行业匹配启用的 SOP 模板' },
}
output: { schema: { type: 'object', properties: {
  intent_level: { type: 'string' },
  created: { type: 'array', items: { type: 'object', properties: {
    task_id: { type: 'string' }, title: { type: 'string' }, planned_at: { type: 'integer' },
    todo_written: { type: 'boolean' },
  }, additionalProperties: false } },
}, additionalProperties: false } }
```

### `customer_acquisition_sop_task_list` — P3 · scope:own-filter · audit 无（读）

```ts
description: '查看 SOP 跟进任务：按线索、状态过滤，按计划时间升序分页返回。'
parameters: {
  lead_id: { type: 'string' },
  status: { type: 'string', enum: ['pending', 'done', 'deferred', 'dropped'] },
  limit: { type: 'integer', min: 1, max: 100 }, offset: { type: 'integer', min: 0 },
}
output: { schema: { type: 'object', properties: { items: { type: 'array', items: { type: 'object', properties: {
  id: { type: 'string' }, lead_id: { type: 'string' }, title: { type: 'string' }, status: { type: 'string' },
  planned_at: { type: 'integer' }, note: { type: 'string' }, created_at: { type: 'integer' },
}, additionalProperties: false } }, total: PAGE.total }, additionalProperties: false } }
```

### `customer_acquisition_sop_task_update` — P3 · scope:own 拒绝改他人线索任务 · audit `sop.task.update`

```ts
description: '流转 SOP 任务状态（pending/done/deferred/dropped），可调整计划时间与备注。'
parameters: {
  task_id: { type: 'string', required: true },
  status: { type: 'string', enum: ['pending', 'done', 'deferred', 'dropped'] },
  planned_at: { type: 'integer' }, note: { type: 'string' },
}
output: { schema: { type: 'object', properties: { task: { type: 'object', properties: {
  id: { type: 'string' }, status: { type: 'string' }, planned_at: { type: 'integer' } }, additionalProperties: false } }, additionalProperties: false } }
```

### SOP 模板 CRUD（4 个） — P3 · 需 `can_manage_global_templates`

- `customer_acquisition_sop_template_create` · audit `sop_template.create`

```ts
description: '新建 SOP 跟进模板：按意向等级（high/mid/low/invalid）各给一条规则，含跟进节奏描述、跟进要点、沟通提问清单与风险提示；等级在模板内不可重复。'
parameters: {
  name: { type: 'string', required: true }, industry: { type: 'string' },
  rules: { type: 'array', required: true, minLen: 1, items: { type: 'object', properties: {
    intent_level: { type: 'string', required: true, enum: ['high', 'mid', 'low', 'invalid'] },
    cadence: { type: 'string', required: true, description: '节奏，如「D+1 微信问候，D+3 案例推送，D+7 邀约」' },
    points: { type: 'array', required: true, items: { type: 'string' } },
    questions: { type: 'array', items: { type: 'string' } },
    risks: { type: 'array', items: { type: 'string' } },
  }, additionalProperties: false } },
  enabled: { type: 'boolean' },
}
output: { schema: { type: 'object', properties: { template: { type: 'object', properties: {
  id: { type: 'string' }, name: { type: 'string' }, enabled: { type: 'boolean' } }, additionalProperties: false } }, additionalProperties: false } }
```

- `customer_acquisition_sop_template_update` · audit `sop_template.update`：`sop_template_id` required + rules 整体替换等可选字段。
- `customer_acquisition_sop_template_list`：`enabled_only?` → items（id/name/industry/rules/enabled）。
- `customer_acquisition_sop_template_delete` · audit `sop_template.delete`：被 sop_tasks 来源引用即拒（沿用统一删除保护），提示停用。

---

## 9. 模块 6 · 获客数据看板（P4，1 个）

### `customer_acquisition_report_overview` — P4 · scope:own-filter（own 只统计自己+公海） · audit 无（读）

```ts
description: '汇总获客数据看板七项指标：线索总量、区间新增趋势、意向分布、来源分布、打分分数分布、SOP 任务完成率、GEO 诊断统计（诊断轮次与平均分）。支持日/周/月/自定义区间与按行业、来源下钻。'
parameters: {
  period: { type: 'string', required: true, enum: ['today', 'week', 'month', 'custom'] },
  from: { type: 'integer', description: '自定义区间起（epoch 毫秒）；period=custom 时必填' },
  to: { type: 'integer', description: '自定义区间止；period=custom 时必填' },
  group_by: { type: 'string', enum: ['none', 'industry', 'source'], description: '下钻维度，默认 none' },
}
output: { schema: { type: 'object', properties: {
  totals: { type: 'object', properties: {
    lead_count: { type: 'integer' }, new_in_period: { type: 'integer' },
    intent_distribution: { type: 'json', description: '{ high, mid, low, invalid } 计数' },
    source_distribution: { type: 'json', description: '{ <source>: count }' },
    score_distribution: { type: 'json', description: '{ bucket: count }，按 0-59/60-74/75-89/90-100 分桶' },
    tasks: { type: 'json', description: '{ total, done, deferred, dropped, completion_rate }' },
    geo: { type: 'json', description: '{ scan_count, avg_score, last_score }' },
  }, additionalProperties: false },
  breakdown: { type: 'json', description: 'group_by 时的分组明细；group_by=none 时为 null' },
}, additionalProperties: false } }
```

render：Markdown 指标表；Web 看板走 Remote 同一聚合服务，不经工具。

---

## 10. 工具总账

| 模块 | 工具数 | 期数 |
|---|---|---|
| P0：settings ×2 + audit ×2（含冒烟 `settings_get`） | 4 | P0 |
| GEO 诊断 | 4 | P2 |
| 线索台账（含 extract/export/documents/followups） | 14 | P1 |
| AI 打分（score ×3 + icp ×4 + score_template ×4） | 11 | P1 |
| 培育文案（generate/list + 模板 ×4） | 6 | P3 |
| SOP（任务 ×3 + 模板 ×4） | 7 | P3 |
| 看板 | 1 | P4 |
| **合计** | **47** | |

红线落点核对：红线 1（抓取边界）→ geo_scan description + pre-execute + 参数 schema 上限；红线 2/3（无自动触达/无发送）→ 全清单无任何发送/私信/加好友类工具；红线 4（模板可编辑）→ 16 个模板 CRUD 工具；红线 5（数据本地）→ 全部读写走 storageDomain；红线 6（审计）→ audit_list/audit_export + 全部写路径埋点（各工具标注的 audit action）。

## 11. 待确认项汇总（工具清单侧）

| # | 决策 | 理由 |
|---|---|---|
| 15 | 新增 `lead_followup_add/list` 两个工具 | lead_followups 表在投喂第 6 节存在但第 7 节无写入口/查入口，表会变死表 |
| 16 | 工具总数 47，模板 CRUD 按「每实体四动作」展开而非合并 action 参数 | 对齐仓库单动作单工具先例（team_task_*/schedule_*），模型调用歧义最小 |
| 17 | 删除保护：模板被历史引用即拒删、提示停用 | KV 无外键级联，物理删除会断历史回溯链（契约 §3.4 权重快照的配套） |
| 18 | `lead_update` 不接受修改 `source`/`intent_level` | source 是录入事实；intent_level 只由打分回填 |
