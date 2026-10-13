# @deepseek-ai/dsh-customer-acquisition

[English](README.md) | 中文

DSH 的获客运营插件：合规边界内的 GEO 诊断、线索台账与 AI 线索打分，面向 OPC 交付一体打包。P0 交付地基——冻结的 v1 存储域、PermissionContext 能力缝、pre-execute 合规校验器、审计日志、四个模型可见工具，以及 Web 面板挂载的浏览器 Remote 网关。冻结数据契约与全量工具清单见 [docs/data-contract.md](docs/data-contract.md) 与 [docs/tools-manifest.md](docs/tools-manifest.md)。

## 安装

```sh
dsh plugin --profile web add @deepseek-ai/dsh-customer-acquisition
```

bundle patch 同时插入两行——本插件与 `@deepseek-ai/dsh-client-ui-customer-acquisition` 面板，一条命令安装完整功能，重启 profile 后生效。

## 配置

无。插件没有部署可变项：红线限值是代码常量并由合规校验器二次执行（见下），用户可调项全部存在域的 `settings` 全局槽中，运行时经 `customer_acquisition_settings_set` 或面板修改。

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

## 工具

| 名称 | 功能 |
|---|---|
| `customer_acquisition_settings_get` | 读取全局参数（P0 冒烟工具）。 |
| `customer_acquisition_settings_set` | 合并式修改全局参数；需 `can_manage_settings`，引用不存在的画像/模板即拒绝。 |
| `customer_acquisition_audit_list` | 分页、可过滤的审计日志查询。 |
| `customer_acquisition_audit_export` | 按相同过滤条件导出 Markdown 或防公式注入 CSV；需 `can_export`。 |

## Remote 面

`CustomerAcquisitionService` 经 `TypertRemoteService` 发布 `customerAcquisition.getSettings`、`customerAcquisition.updateSettings`、`customerAcquisition.listAuditLogs`；生成的 `./remote` 工件由浏览器面板挂载。每个写操作都经能力缝解析 web 操作者并写审计。

## Model Experience

### 本地获客运营状态

#### 模型看到什么

插件加载后四个工具（`customer_acquisition_settings_get/set`、`customer_acquisition_audit_list/export`）加入提示词组装，及其文本渲染：参数快照为字段清单、审计行为带时间戳的行、导出为表格/CSV 文档。合规校验器的拒绝以工具错误形式呈现，携带中文原因。

#### Token 影响

有界：插件加载期间每次组装请求多四个工具 schema（约 600 token）；结果分页（审计单页上限 100 行）。

#### KV Cache 影响

schema 进入提示词前缀的工具块；插件加载或卸载会使该点之后的可复用前缀失效，与任何工具注册一致。

## Known Limitations and Deferred Work

- **P0 范围**——冻结清单中的线索、打分、GEO、文案、SOP、看板工具尚未实现；域表已存在，但 P0 只有 settings 与 audit 有行为。各期按契约顺序 P1 → P2 → P3 → P4 落地。
- **种子模板未播种**——三套行业模板包（实体门店 / B2B 工厂商贸 / 软件服务商）随 P1/P3 到货；其固定 id 空间与幂等策略已在契约中冻结。
- **面板为占位**——Web 面板挂载 Remote 面，展示设置与最近审计；八页完整面板随 P4 交付。
- **本地操作者身份是平凡的**——`local-default` 持有全部能力；有意义的 `lead_scope` 强制从平台 Provider 与 P1 线索工具开始。
- **审计无限增长**——记录从不清理；保留策略等待具体部署需求。
- **抓取编排未接线**——P2 的 GEO 扫描器须先核实 web-fetch 的确切消费形态再复用；校验器的 URL 与上限规则已生效。
