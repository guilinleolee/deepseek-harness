# 获客运营 P1：线索台账 + AI 线索打分

状态：已实现

[English](2026-10-04-customer-acquisition-p1-leads-scoring.md) | 中文

## 背景

获客运营插件 P1 交付冻结清单中的模块 2 与模块 3——线索台账（16 个工具）与 AI 线索打分（11 个工具），与独立 GEO 会话（拥有 `packages/growth/customer-acquisition-geo/`）并行。数据契约、PermissionContext 缝、审计写入器、合规校验器均为 P0 只读物；冻结契约把打分语义钉在「一次 LLM 调用产出一个 run 及其分项」。

## 决策

- **两个模块服务借用 P0 域。** `LeadLedgerService` 与 `LeadScoringService` 是运行时 fiber 构造的普通类；域保持单开（storage-domain 不变量）于 `CustomerAcquisitionService` 内，其 `requireDomain()` 从 private 放宽为 public，模块借表而非重复打开。不新增 ctx 键，growth 分组 README 无需改动。
- **打分是经端口的一次模型调用。** 服务渲染模板的四类占位符（knowledge = 该线索文档，上限 4000 字符），调用 `PromptCompletion` 端口，严格校验 JSON 答案：维度全覆盖且各一次、不收未知维度、分数 0-100、理由非空。每个分项快照打分时的权重，此后改权重不歪曲历史；加权总分映射意向标签（≥80/≥60/≥30）回填线索。测试注入确定性假实现——没有任何测试触真实模型。
- **公海语义落在读规则里。** `lead_scope=own` 在所有读面（列表、详情、文档、打分历史）可见自己+公海，但只能写自己名下；给公海线索打分会提示先领取。purge 需回收站状态加 `can_delete_any_lead`，级联六张表。
- **种子只做 ICP+打分，按固定 id 幂等。** 三套行业包在挂载时各播种一套画像与一个提示词模板（`seed-*` id）；已存在的记录绝不触碰，用户修改跨重启保留。SOP 与文案模板留给 P3。
- **AI 路由是行级配置，不是常量。** `config.ai`（provider/model/timeoutMs/maxOutputTokens）在挂载时带默认值解析、越界 fail loud；内部调用经共享 `llm` Service Definition，使用 `@deepseek-ai/dsh-llm` + `@deepseek-ai/dsh-timeout`（两个已批准的 workspace 依赖，peer+dev）。

## 否决

- **第二次 `storageDomain.open`**——设施按域名强制单开；经 P0 服务借句柄使关闭方始终唯一。
- **模型协同打分**（工具把调用方模型的说法直接落库）——违背冻结契约「一次 LLM 调用产出 run」，且丢失服务端权重快照。
- **接受模型答案中的未知维度**——拒绝而非忽略：缺打或造出的维度会静默扭曲加权总分。
- **打分调用重试**——批量已按线索隔离失败；限流重试策略日后可加入端口，不动服务。

## 后果、风险与取舍

P0 组合测试现在桩掉 `llm`（运行时 fiber 注入它）并断言 31 个工具。工具清单第 10 节的模块 2 计数行写 14 个，而其明细小节定义了 16 个——以明细为准；冻结文档的计数行留给文档所有者对齐。列表面在内存中过滤（单机规模足够）。`lead_extract` 虽不落库也按清单记 `lead.extract` 审计；web 来源的线索/打分审计随 P4 面板 Remote 面落地。
