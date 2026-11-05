# Agent Note：示例组合回到当前架构上

状态：已实现

[English](2026-10-14-quant-example-revival.md) | 中文

## 问题

量化研究示例——在真实组合上跑的无钥端到端 driver——是基于 upstream 合并前的架构写的，在 Phase3-4 某次合并链中悄悄停跑：vitest 通道不再包含它、组合引用了已退役的包、模型 fixture 用了不存在的 API。插件本身的单测完备，但唯一一个启动整套栈（内核子进程、存储、门禁、jobs 注册表、模型循环）的测试已经熄火——而这正是仓库"模型可见变更更新快照"规则所要的覆盖。

## 决策

- **spec 迁入 expected 通道、采用 golden 命名。** upstream 的 `refactor(test): reserve snapshots for session recordings`（1cfe0f9942）把示例快照测试改名为 `*.golden.e2e.ts`、把录制会话回放挪进 `snapshots/`；量化示例是 owner-local 组装期望输出（无录制会话），因此加入 `vitest.expected.config.ts` 的 `examples/*/tests/**/*.golden.e2e.ts` include。spec 从 `quant-research.snapshot.ts` 改名为 `quant-research.golden.e2e.ts`。
- **组合骑上当前包。** 退役的 `dsh-agent-spine-demo` 行改为声明式 `dsh-agent-loop` 加一个启动 agent（persona 走 `system-prompt` 的 `personaPrefix`——demo 的 `persona`/`workspaceContext`/`dshHome` 旋钮已不存在）；合并后的 `dsh-settings` 行删除（它现在注入 `configEditor` + `profileContext`，本组合不提供这两个服务，且插件不读设置）；`llm`、`session`、`agent`、`session-projection`、`tools` 服务枢纽作为显式行加入。`examples/package.json` 作为唯一 workspace 伞回归，让 plain-Node 对 cordis.yml 包的解析可用——原伞文件记录的模式。
- **mock 骑上当前 LLM 形状。** `CallId` 改为 `ToolCallId`；工具结果现在是 `role: 'tool'` 消息（旧 `content.find(block => block.type === 'tool-result')` 永不匹配，于是 mock 永远重放第一轮——超时把其他所有失败都藏住了）。
- **driver 补齐 Phase4/5 阶段。** optimize 与 walk-forward 之后：一个双标的（`000001`/`600519`）横截面 IC 任务带 `ic_windows: 2`（经 `cross_section_ic` 内核 op）、一次面板上限拒绝、一次 `quant_list_snapshots` 读取断言上述轮次的持久化结果。spec 断言启动卡片、落定 markdown（含分窗稳定性节）、拒绝理由与快照列表。
- **双重 domain open 在源头闭合。** 复活示例暴露出 `apply()` 打开 domain 两次（插件体 + 服务 fiber），而 storage-domain 设施按名单开——单测从不启动真实组合，只有示例抓得住。`QuantResearchService` 现在接受调用方已打开的句柄；`apply()` 把自己的 domain 传给服务 fiber，apply spec 改为一次 open / 一次 close。

## 考虑过的替代方案

**删除示例。** 否决：它是插件唯一的组合级测试（启动顺序、服务注入、经真实接缝的内核子进程、真实工具分发上的门禁），也是仓库对模型可见变更的既定政策。

**改录一个会话快照。** 否决：这里的价值是脚本化模型驱动下的活组合栈，不是回放录制；expected 通道正是为这种形状存在的。

**保留服务自己的 open、禁用插件体的。** 否决：工具层的 domain 句柄承载各表；让它依赖服务会倒转 apply() disposer 已记录的所有权。

## 后果

代价：示例回到 beaten path 上——upstream 再退役还会再打到它，但现在可见（通道会跑它）。验证：golden spec 在当前 master tip 上端到端通过（五个工具轮、三个后台任务阶段、三次拒绝、快照列表）；quant 单测以共享 domain 设计保持 330 绿；内核 pytest 33 绿。expected 通道的预存失败（未构建 `lib/` 缺 typert 产物）与本次工作无关且未变化——该通道需要先 `build`。
