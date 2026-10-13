# Changelog

All notable changes to the Trajectory Debug Workbench plugin family.

## [0.2.0] — 2026-08-14

**M4 收尾：浏览器 Debug 控制台与 RPC 通道。**

- **浏览器 RPC 传输**（typert 无关）：host 在 webserver 注册 `POST /api/trajectory-debug/rpc`，客户端 `fetch` 调用；方法覆盖回放/断点/改参/分叉对比/导出（`transport.ts`，6 个新测试）；
- **浏览器 Debug 控制台面板**：确定性回放（开始/下一步/跳转 + 步上下文）、断点管理（列表/添加/删除/resume）、改参重跑（seq + JSON 参数）、分叉对比（分叉 + 选 base/head + 差异摘要/工具变更/结果 diff）；
- **瀑布流打磨**：窗口化渲染（大会话流畅）、`#step=<seq>` 深链（点击行可深链、加载时自动滚动高亮）；
- **侧车持久化**：FileSidecar 继续承担（原文即"可选增强"项，storage-domain 迁移记录为内部可选项）；
- README 移除"M4（仅剩）"小节；新增英文 README（`README.md` 英文 + `README.zh.md` 中文配对，语言切换链接）。

## [0.1.0] — 2026-08-14

**里程碑 M1–M4 全部交付**（对应 `Doc/01-03` 设计文档 + `Doc/05-插件使用指南`）。

### 引擎（dsh-trajectory-debug-host）

- 确定性回放引擎：`stepBoundaries` / `deriveModelView` / `stepContextAt` / `buildTrajectoryPage`（零模型/零工具消耗）
- 性能折叠：工具成功率/分位数、失败归类、Token 分布、TTFT/解码、轮次统计（口径对齐 `dsh-session-stats`）
- 分叉对比引擎：`compareTrajectories` + JSON diff + 差异摘要
- 断点引擎：`agent/pre-step` waterfall 短路暂停/继续 + 超时自动放行
- 改参重跑：`rerunTool` 走 `ctx.tools.execute` 完整管线（策略 `record|sandbox|ask`，ask 无 live agent fail-closed）
- 分叉真实重跑：`sessions.fork` + `agents.resume` + `followup`，级联策略 `cascade: truncate|preserve`
- 投影单元：`trajectoryDebug/trajectory` + `trajectoryDebug/perf`（session-projection 注册表，浏览器零代码消费）
- 命令：`/trajectory [stepIndex]`、`/perf`
- 模型工具：`trajectory_search / trajectory_step / trajectory_perf`（`enableModelTools` 开启）
- 成本估算：`perf.cost`（可配 `tokenPriceTable`）
- trace 导出：`export('trace')`（OTel GenAI 语义 spans，Langfuse/LangSmith 就绪）
- 侧车：`MemorySidecar` / `FileSidecar`（原子 JSON 持久化）

### 服务（dsh-trajectory-debug）

- `ctx.trajectoryDebug` Service Definition + 全套 wire 类型

### 浏览器（dsh-client-ui-trajectory-debug）

- "Debug" 会话视图 Tab（order 20）：瀑布流 + 性能仪表盘，经投影推送实时渲染
- 客户端 bundle：`scripts/bundle-client.mjs`（esbuild 产出官方 `__ModuleLoader__` 格式，运行时仅外部依赖 `react`）

### 工程

- pnpm monorepo（5 包）、TS strict、lib-first 清单、双语文档
- 50 个单元测试 + 真实 dsh 进程冒烟（`scripts/smoke.mjs`）
- 运行时踩坑记录（Service 构造器即注册 / ctx.logger 可调用 / pnpm file: 拷贝 / pnpm 11 供应链策略）

### 生态（COMPARISON.md）

- 对比 dsh-message-edit / dsh-plugin-cost / dsh-deeplink / dsh-eval，落地成本估算、trace 导出、级联策略、命令锚点
