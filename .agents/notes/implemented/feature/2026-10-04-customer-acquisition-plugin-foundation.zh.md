# 获客运营插件地基（P0）

Status: implemented

[English](2026-10-04-customer-acquisition-plugin-foundation.md) | 中文

## 背景

获客运营功能——GEO 诊断、线索台账、AI 线索打分——以合规优先的业务插件形态面向 OPC 交付。投喂说明在实现前冻结了数据契约与 47 工具清单，并要求六条红线（抓取边界、禁自动触达、无发送通道、模板可编辑、数据本地、审计留存）落为可执行校验而非口号。P0 打下后续各期共用的地基。

## 决策

- **一对包、一个合规门。** `@deepseek-ai/dsh-customer-acquisition` 拥有冻结的 `customer_acquisition` 域（13 张 KV 表 + settings 全局槽，version 1）、`permissionContext` Service Definition 与内置 Local Provider、审计写入器、pre-execute 合规校验器、四个 P0 工具与 Typert Remote 网关；`@deepseek-ai/dsh-client-ui-customer-acquisition` 在浏览器侧挂载它。两包落在新 `growth/` 分组。GEO 抓取将落为兄弟包（`customer-acquisition-geo`），保证 P1 与 P2 的文件所有权永不相交。
- **权限缝即多用户方案。** 单机 DSH 每次调用解析为持全量能力的 `local-default`；卡巴格平台以同名 ctx 键替换 Provider，在插件之外把平台角色映射到 `capabilities`。插件不感知角色名、不引用任何平台私有包。
- **红线集中在一个 pre-execute 监听器**，规则为每工具纯函数，每条非法路径都有直接单测；参数 schema 保持描述性（DSL 无范围约束），执行权归校验器。
- **settings 走域 `global` 槽**而非表；开放枚举（`source`、文案 `type`）以普通字符串存储并配已知值词表，增长永不触发域版本 bump。

## 否决项

- **工具参数用 zod** —— harness 的 `ParameterSchemaSpec` DSL 拥有该边界；zod 留在域记录侧。清单按此书写。
- **每实体一个 action-dispatch 工具** —— 47 个单动作工具对齐仓库 `team_task_*`/`schedule_*` 风格，模型可见 schema 无歧义。
- **删除被引用模板** —— 打分历史或生成产物引用模板时拒绝删除，调用方改为停用，保证历史可复算（分项带权重快照）。

## 后果、风险与取舍

KV 域无索引、无就地迁移：bump 版本即重建介质（pre-release 立场），列表在内存过滤——单机规模下可接受，部署规模超出后再议。合规拒绝的审计对操作者做尽力解析，且绝不撤销拒绝本身。抓取编排（P2）复用前仍须核实 web-fetch 的消费形态；URL 与上限规则现已生效。
