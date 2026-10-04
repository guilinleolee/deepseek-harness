# @deepseek-ai/dsh-customer-acquisition

[English](README.md) | 中文

DSH 的获客运营插件：合规边界内的 GEO 诊断、线索台账与 AI 线索打分，面向 OPC 交付一体打包。P0 交付地基——冻结的 v1 存储域、PermissionContext 能力缝、pre-execute 合规校验器、审计日志，以及 Web 面板挂载的浏览器 Remote 网关。P1 新增线索台账（模块 2）与 AI 线索打分（模块 3）：27 个模型可见工具、三套行业模板幂等种子、按调用粒度的归属人权限。冻结数据契约与全量工具清单见 [docs/data-contract.md](docs/data-contract.md) 与 [docs/tools-manifest.md](docs/tools-manifest.md)。

## 安装

```sh
dsh plugin --profile web add @deepseek-ai/dsh-customer-acquisition
```

bundle patch 同时插入两行——本插件与 `@deepseek-ai/dsh-client-ui-customer-acquisition` 面板，一条命令安装完整功能，重启 profile 后生效。

## 配置

行级配置（插件行的 `config:`）调整 AI 面（线索抽取、线索打分）内部模型调用的路由：

```yaml
- name: '@deepseek-ai/dsh-customer-acquisition'
  config:
    ai:
      provider: deepseek
      model: deepseek-chat
      timeoutMs: 120000
      maxOutputTokens: 2000
```

全部字段可选、默认值如上（`provider` = 已注册的 LLM provider 路由，`timeoutMs` = 单次调用截止，限 1000-300000，`maxOutputTokens` = 输出上限，限 256-32000）；越界值在插件加载时 fail loud。红线限值（页数上限、超时上限、批量上限）是代码常量并由合规校验器二次执行——不可配置。运行时用户可调项全部存在域的 `settings` 全局槽中，经 `customer_acquisition_settings_set` 修改。

## 存储域

`ctx.storageDomain.open(customerAcquisitionDomainSpec)` 打开 `customer_acquisition` 域（version 1）：十三张 KV 表（`leads`、`lead_followups`、`lead_documents`、`score_runs`、`score_run_items`、`icp_profiles`、`score_templates`、`content_templates`、`generated_contents`、`sop_templates`、`sop_tasks`、`geo_scans`、`geo_reports`、`audit_logs`）加 `settings` 全局槽。记录 schema 全部为 zod；开放枚举（`source`、文案 `type`、`industry`）以普通字符串存储，新增已知值不需要 bump 域版本。契约已冻结：任何结构性变更必须 bump 版本并经所有者确认。

## PermissionContext 能力缝

`ctx.permissionContext` 是本包拥有的 Service Definition：`resolve(request): Promise<ResolvedOperator>`，返回 `{ userId, displayName, capabilities }`。内置 `LocalPermissionProvider` 对每次调用恒返回本地默认用户（`local-default`）并持有全量能力——无登录、无角色。卡巴格企业平台经自己的 bundle patch 以同名键替换 Provider，把平台角色映射到 `capabilities`；本插件不感知角色名、不引用任何平台私有包。每次工具执行与每个写 Remote 方法都按调用解析操作者；list 与写路径在服务端按 `lead_scope` 过滤 `owner_id`。

## 合规校验器（红线）

一个 `tools/pre-execute` 监听器执行全部 `customer_acquisition_*` 调用的红线，其余调用经 `next()` 委托：

1. **抓取边界**——GEO 诊断只接受用户显式提供的 http(s) 网址（主机名非空）；页数上限 20、单页超时 10 秒（同样编入 settings schema，存储值不可能越限）。抓取本体随 P2 落地，复用 web fetch 能力：串行并发 1、响应体上限 2 MiB、robots.txt `Disallow` 跳过、不做域名自动发现。
2. **无自动化触达**——不引入自动私信、加好友、账号自动化依赖；单测断言依赖清单干净。
3. **无发送通道**——生成物仅为文本；源码扫描单测断言 `src/` 无 SMTP/邮件/短信实现。
4. **模板可编辑**——四张模板表已在冻结域中；CRUD 工具随 P1/P3 落地。
5. **数据本地**——业务数据只存本域，无其他写入方。
6. **审计日志**——每次变更与每次合规拒绝追加一条 `audit_logs` 记录（含 `source` 与 `operator_user_id`），经两个审计工具与面板可查询、可导出。

每条红线至少一个非法路径单测。

## 线索台账（模块 2）

`LeadLedgerService` 是线索、跟进与挂接资料的唯一权威；16 个 `customer_acquisition_lead_*` 工具是它的薄投影。归属权限在服务端逐调用强制：`lead_scope=own` 的操作者只能读自己名下与公海（`owner_id` 缺省）的线索、只能写自己名下的；公海经 `lead_assign` 领取，`lead_transfer` 不带目标归属人即释放回公海。删除是软删（回收站）——`lead_restore` 恢复，`lead_purge` 物理删除线索及其全部跟进、文档、打分记录、生成产物与 SOP 任务，需 `can_delete_any_lead`。挂接资料（单份 2 万字符）是打分与文案生成的知识注入源。`lead_extract` 只解析本次提供的文本——一次模型调用，无任何网络采集——只返回字段不写库，确认后经 `lead_create` 落库。导出渲染 Markdown 表格或防公式注入 CSV 并写审计。

## AI 线索打分（模块 3）

打分是每条线索一次模型调用：服务解析 ICP 画像与提示词模板（显式 id → 启用中的全局默认 → 行业精确匹配 → 无行业模板 → 任一启用），渲染模板的 `{{lead}}`/`{{icp_profile}}`/`{{dimensions}}`/`{{knowledge}}` 占位符，严格校验 JSON 答案（维度全覆盖且各一次、分数 0-100、理由非空），落库时逐分项保存权重快照——之后改权重不歪曲历史，历史可复算。加权总分映射意向标签（≥80 高、≥60 中、≥30 低、否则无效）并回填线索。`score_batch` 串行至多 50 条，单条失败不中断批次。画像与模板 CRUD 需 `can_manage_global_templates`；被任何打分记录引用的画像/模板拒绝删除（请停用）。三套行业包——实体门店、B2B 工厂商贸、软件服务商——挂载时按固定 `seed-*` id 幂等播种，绝不覆盖用户修改。

## 工具

| 名称 | 功能 |
|---|---|
| `customer_acquisition_settings_get` | 读取全局参数（P0 冒烟工具）。 |
| `customer_acquisition_settings_set` | 合并式修改全局参数；需 `can_manage_settings`，引用不存在的画像/模板即拒绝。 |
| `customer_acquisition_audit_list` | 分页、可过滤的审计日志查询。 |
| `customer_acquisition_audit_export` | 按相同过滤条件导出 Markdown 或防公式注入 CSV；需 `can_export`。 |
| `customer_acquisition_lead_create` / `lead_update` / `lead_get` / `lead_list` | 台账 CRUD：多维筛选、关键词搜索、分页。 |
| `customer_acquisition_lead_delete` / `lead_restore` / `lead_purge` | 回收站生命周期；purge 级联清除全部关联记录。 |
| `customer_acquisition_lead_assign` / `lead_transfer` | 公海领取与归属转移。 |
| `customer_acquisition_lead_extract` | 从一段用户提供的文本抽取字段；模型驱动，不写库。 |
| `customer_acquisition_lead_export` | 按筛选条件导出 Markdown 或防注入 CSV；需 `can_export`。 |
| `customer_acquisition_lead_document_add` / `lead_document_list` / `lead_document_remove` | 挂接纯文本知识资料。 |
| `customer_acquisition_lead_followup_add` / `lead_followup_list` | 跟进记录，按时间倒序。 |
| `customer_acquisition_score_one` / `score_batch` | AI 打分：权重快照 + 意向回填；批量串行、单条失败隔离。 |
| `customer_acquisition_score_history` | 打分历史全留存，含逐维度权重快照。 |
| `customer_acquisition_icp_create` / `icp_update` / `icp_list` / `icp_delete` | ICP 画像；权重须合计 100，被引用即拒删。 |
| `customer_acquisition_score_template_create` / `score_template_update` / `score_template_list` / `score_template_delete` | 打分提示词模板（四类占位符）；被引用即拒删。 |

## Remote 面

`CustomerAcquisitionService` 经 `TypertRemoteService` 发布 `customerAcquisition.getSettings`、`customerAcquisition.updateSettings`、`customerAcquisition.listAuditLogs`；生成的 `./remote` 工件由浏览器面板挂载。每个写操作都经能力缝解析 web 操作者并写审计。

## Model Experience

### 本地获客运营状态

#### 模型看到什么

插件加载后 31 个工具加入提示词组装——四个 P0 settings/audit 工具加 27 个线索台账与打分工具——及其文本渲染：线索概要为一行摘要、打分结果为总分加逐维度行、导出为表格/CSV 文档、抽取结果为字段清单。合规校验器与能力检查的拒绝以工具错误形式呈现，携带中文原因。三套行业种子在首次启动后即为可直接使用的画像与模板。

#### Token 影响

有界：插件加载期间每次组装请求多 31 个工具 schema（约 4k token）；列表类单页上限 100 行，打分渲染随画像维度数伸缩（通常 5-6 行）。

#### KV Cache 影响

schema 进入提示词前缀的工具块；插件加载或卸载会使该点之后的可复用前缀失效，与任何工具注册一致。

## Known Limitations and Deferred Work

- **P1 范围**——冻结清单中的 GEO、文案、SOP、看板工具尚未实现；域表已存在，但只有线索、打分、settings、audit 有行为。各期按契约顺序 P2 → P3 → P4 落地。
- **种子只覆盖 ICP 与打分**——三套行业包播种画像与提示词模板；SOP 与文案模板随 P3 在同一 id 空间下到货。
- **面板为占位**——Web 面板挂载 Remote 面，展示设置与最近审计；八页完整面板随 P4 交付，线索/打分的 Remote 读写也在那时落地。
- **打分需要可达的模型路由**——`ai.provider`/`ai.model` 必须指向已注册且有凭据的路由；否则打分与抽取按调用失败，批量按线索隔离。
- **本地操作者身份是平凡的**——`local-default` 持有全部能力；有意义的 `lead_scope` 强制从平台 Provider 注入真实用户开始。
- **审计无限增长**——记录从不清理；保留策略等待具体部署需求。
- **抓取编排未接线**——P2 的 GEO 扫描器须先核实 web-fetch 的确切消费形态再复用；校验器的 URL 与上限规则已生效。
