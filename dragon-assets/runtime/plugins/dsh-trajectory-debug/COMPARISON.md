# 竞品对比与差异化改进（v0.2）

> 依据 [Awesome DeepSeek Harness](https://github.com/0xsline/awesome-deepseek-harness)（README.zh-CN）与社区 `dsh-plugin` topic 生态盘点。
> 对比时间：2026-08（DSH v0.1.0-rc.6 时代）。

## 1. 同类项目盘点

| 项目 | 仓库 | 定位 | 与本插件重叠 | 差异/可借鉴 |
|---|---|---|---|---|
| **dsh-message-edit** | [Moeblack/dsh-message-edit](https://github.com/Moeblack/dsh-message-edit) | 基于事件溯源的消息编辑/重生成/重试 + 版本时间线 + 分支树 | **最大**：fork 分支、重试任意回合、分支树、conversation.view Tab（order 15） | 他们没有轨迹可视化/单步回放/断点/性能面板；我们缺他们的**级联策略**（truncate/preserve）与**消息文本编辑** |
| **官方 ui-trajectory** | DSH 内置 | 只读轨迹台账 | 数据源同源（事件溯源） | 官方只读、无调试；我们补上了调试闭环 |
| **dsh-plugin-cost** / **dsh-balance-meter** | [yweilai77-dev](https://github.com/yweilai77-dev/dsh-plugin-cost) / [Ghost011118](https://github.com/Ghost011118/dsh-balance-meter) | 会话成本/余额显示 | 我们的 perf 面板有 Token 无价格 | 借鉴：**价格表 × Token 花费估算** |
| **dsh-eval** | [hccccc01333/dsh-eval](https://github.com/hccccc01333/dsh-eval) | Agent 评测平台：trace 指标 + run 对比/报告 | compare 引擎 + 耗时/失败指标 | 借鉴：**OTel GenAI trace 导出**（喂 Langfuse/LangSmith/评测平台） |
| **dsh-deeplink** | [dsh-external/dsh-deeplink](https://github.com/dsh-external/dsh-deeplink) | URL 参数直达 WebUI 会话/工作区 | 我们 PRD 有 `dsh://session/<id>#step=<seq>` 深链未落地 | 借鉴：锚点/深链规范 |
| **dsh-session-search** / **session-chatlog** | [dsh-external](https://github.com/dsh-external/dsh-session-search) | 跨会话只读搜索 / 聊天记录 | 我们的 F8 过滤/搜索（会话内） | 未来增强：跨会话搜索 |
| **dsh-diff-viewer** | [dsh-external/dsh-diff-viewer](https://github.com/dsh-external/dsh-diff-viewer) | Web diff 查看器 | 我们的 compare 结果 diff | 未来增强：复用其渲染 |

## 2. 定位总结

**官方 trajectory = 看；dsh-message-edit = 改；trajectory-debug = 查 + 调试 + 量化。**

- 独有：确定性单步回放（零 Token）、断点暂停/继续、工具级改参重跑（沙箱内真实执行）、性能分析引擎（成功率/失败归类/Token/TTFT/分位数）、fork 分叉对比引擎、投影推送实时瀑布流、`trajectory_*` 模型工具、trace 导出。
- 对齐差距：级联策略（已补）、成本估算（已补）、深链/锚点（命令侧已补）、trace 导出（已补）。

## 3. 已执行的改进（v0.2）

| # | 改进 | 依据 | 落点 |
|---|---|---|---|
| 1 | `perf.cost` 成本估算：可配 `tokenPriceTable`（$/1M token） | dsh-plugin-cost / dsh-balance-meter | `perf-analyzer.ts` `analyzePerf(…, price)`；`PerfSnapshot.cost` |
| 2 | `export('trace')`：OTel GenAI 语义 spans（turn/llm/tool span，gen_ai.* 属性，错误码） | dsh-eval 的 trace 指标思路 | 新增 `trace-export.ts`；可喂 Langfuse/LangSmith |
| 3 | `ForkRequest.cascade: 'truncate'\|'preserve'`：preserve 在新分支按序重放边界后的后续用户输入 | dsh-message-edit 级联策略 | `forkVariant` + `resumeVariant(followups[])` |
| 4 | `/trajectory <stepIndex>`：命令支持单步锚点查看 | dsh-deeplink 深链思路 + 我们 PRD 的 step 锚点 | `commands.ts` |
| 5 | 浏览器视图 `order` 30→20（Trajectory 10 与 message-edit 15 之后、Prompt Studio 之前） | 生态 tab 顺序协调 | `client/index.ts` |
| 6 | 对比引擎边界测试：空 base、单侧步、结果翻转 isError、多轮对比 | 工程门禁 | `diff-engine.spec.ts` |
| 7 | 新测试：cost 估算 2 例、trace 3 例、cascade 2 例、export trace 1 例 | — | perf/trace/provider specs |

**测试规模**：39 → **48**（+9）。全门禁（build/typecheck/test）与真实进程 smoke 通过。

## 4. 后续可借鉴清单（未做，记录）

- **消息文本编辑**（dsh-message-edit）：编辑已落定 user/assistant 文本后分支重跑——需要事件级改写通道，列入 M5 候选；
- **跨会话搜索**（dsh-session-search）：把 `trajectory_search` 扩到 session-query 的跨会话索引；
- **深链解析到浏览器**（dsh-deeplink）：`dsh://session/<id>#step=<seq>` 在 web 端锚点定位（依赖 typert/UI 接线）；
- **diff 渲染复用**（dsh-diff-viewer）：compare 结果接入其 diff 组件。

## 5. 生态互链

- 本插件发布后打 `dsh-plugin` topic 并提交到 [awesome-deepseek-harness](https://github.com/0xsline/awesome-deepseek-harness) 与 [awesome-dsh-plugin](https://github.com/awesome-dsh-plugin/awesome-dsh-plugin)。
