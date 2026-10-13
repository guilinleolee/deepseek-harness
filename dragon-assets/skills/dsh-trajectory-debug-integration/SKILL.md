---
name: dsh-trajectory-debug-integration
description: |
  DSH 生态首个"运行层可调试性"技能。把 DeepSeek Harness 的 event-sourced 会话变成可调试资产：
  瀑布轨迹视图、确定性单步回放（零 token / 零工具）、断点、sandboxed edit-and-rerun、fork 对比、性能分析、
  OTel GenAI trace 导出、`trajectory_*` 模型工具（供 Agent 自审自己运行）。
  上游：devmom/dsh-trajectory-debug · MIT ✅ · 5 npm 子包 · 56/56 vitest PASS。
metadata:
  version: "1.0.0"
  date: "2026-08-24"
  upstream: devmom/dsh-trajectory-debug
  license: MIT
  reference: https://github.com/devmom/dsh-trajectory-debug
  integration_stage: 40
  integration_source: dragon-engine/stage-40-trajectory-debug.md
  node_required: ">=22.19"
  package_manager: pnpm@9.15.0
  install_command: "dsh plugin --profile web add dsh-trajectory-debug-bundle"
---

# dsh-trajectory-debug-integration · V1.0

> **TL;DR**：天龙引擎 DSH 生态首个集成插件。安装后获得 `/trajectory`、`/perf` 两个斜杠命令 + "Debug" 对话视图 Tab + 3 个模型自身工具（self-audit），填补天龙"运行层可调试性"空白。

---

## L0: 一句话描述 (≤15字)

DSH 会话轨迹调试，零 token 回放。

---

## L1: 使用场景 (50-100 字)

当用户需要：
- 看 DSH 会话的完整 waterfall（turn / step / tool 级别）
- 在 token 烧掉之前**先**回放某一步的模型视图 + tool action
- 在不重启的情况下**改一个 tool 输入并重跑**
- fork 出两条分支做差异对比（prompt A vs prompt B）
- 给 deepseek/AI agent 的失败归因 + 性能百分位
- 把 DSH 运行轨迹导出给 Langfuse/LangSmith 做 trace 分析

---

## L2: 能力矩阵（13 项 · 上游 v0.2.0）

### 2.1 引擎层（trajectory-debug-host）

| 能力 | API | 实现 |
|---|---|---|
| **瀑布视图** | `buildTrajectoryPage(sessionId, opts)` | turn / step / tool 行 + 状态 + 时延 + tokens + 错误码 + 过滤分页 |
| **确定性回放** | `stepContextAt(seq)` + `ReplayCursor` | **零 token / 零工具** —— 模型视图 + action |
| **性能分析** | `analyzePerf(sessionId, price?)` | 成功率 / 分位数 / 失败归类 / token 分布 / TTFT / decode / cost |
| **Fork 对比** | `compareTrajectories(base, head)` | 步对齐 + 工具变更 + JSON diff + 摘要 |
| **断点** | `BreakpointManager.set|remove|list|resume` | `agent/pre-step` waterfall 短路 + 超时放行 |
| **编辑重跑** | `rerunTool({seq, params, strategy: 'record'\|'sandbox'\|'ask'})` | 走完整 `ctx.tools.execute` 管线 |
| **Fork + Live Resume** | `sessions.fork` + `agents.resume` + `followup` | cascade: `truncate\|preserve` |
| **投影（projection）** | `trajectoryDebug/trajectory` + `trajectoryDebug/perf` | 浏览器零折叠消费 |

### 2.2 命令层

| 命令 | 行为 |
|---|---|
| `/trajectory [stepIndex]` | 跳到会话的第 N 步看模型视图 + action（无 stepIndex = 列表）|
| `/perf` | 性能 dashboard：成功率 / 分位数 / token / TTFT / cost |

### 2.3 模型自身工具（self-audit · 关键差异化）

| 工具 | 用途 |
|---|---|
| `trajectory_search(query)` | 在当前会话轨迹中搜索 step / tool / error |
| `trajectory_step(seq)` | 跳到第 N 步上下文（供 agent 自审用）|
| `trajectory_perf()` | 拉取当前会话性能快照（token / 失败 / TTFT）|

> **启用条件**：`enableModelTools: true`（opt-in，安全默认关闭）

### 2.4 导出 + 持久化

| 能力 | 端点 |
|---|---|
| **OTel GenAI trace** | `export('trace')` → Langfuse / LangSmith 兼容 |
| **Sidecar 持久化** | `MemorySidecar` / `FileSidecar`（原子 JSON 写）|

### 2.5 浏览器 UI

- "Debug" 对话视图 Tab（order 20）
- waterfall + perf dashboard 实时渲染（投影推送）
- replay / breakpoint / rerun / fork-compare 控制台
- 浏览器 RPC：host 在 webserver 注册 `POST /api/trajectory-debug/rpc`（typert 无关）

---

## L3: 安装

### 3.1 npm 直接装（推荐）

```bash
dsh plugin --profile web add dsh-trajectory-debug-bundle
dsh web --dump-config   # 期望看到 trajectory-debug-host / -remotes / ui-trajectory-debug 三行
```

完成后重启 `dsh web`，Debug tab 自动出现在 conversation view 环上。

### 3.2 源码检入（天龙自家镜像）

```bash
# 真源已落 dragon-engine/skills/dsh-trajectory-debug-integration/
cd "C:\Users\li\.claude\projects\dragon-engine\skills\dsh-trajectory-debug-integration"

# 检查完整性
node --check packages/trajectory-debug-host/lib/index.js
corepack pnpm check     # 期望: build + typecheck + test = 0/0/0 + 56/56 vitest PASS

# 复制到 DSH profile
dsh plugin --profile web add .
```

---

## L4: 触发词（15 类 · 路由到本 skill）

```
/trajectory             /perf                      trajectory
DSH 调试                 DSH 性能                   回放
断点                    重跑                       fork 对比
OTel trace              Langfuse                   agent 自审
模型工具                  stepContext                compareTrajectories
BreakpointManager
```

---

## L5: 下游协同（13 个天龙岗位 / skill）

| 下游 | 协同方式 |
|---|---|
| **00-analyst v2**（新增）| 顶层方法论"DSH 插件运行轨迹分析" |
| **04-validator V9.05**（新增）| FMEA + 失败归因 + 断点重跑闭环 |
| **07-scribe V11.12**（新增）| trajectory 作为 L0 之前的 L'前层 |
| **09-03 meta-reviewer v2.0**（新增）| `/perf` 作为天龙引擎自身巡检入口 |
| **09-04 chief-of-staff v2.0**（新增）| `trajectory_search` 模型工具自审自己的决策链 |
| **40-01-mcp-orchestrator v2**（新增）| 第 11 MCP 服务：trajectory-debug webserver RPC |
| **session-distiller V1.1**（新增）| `distill_from_trajectory(session_id)` 直接读 trajectory JSON |
| **meta-prism V1.1**（新增）| `cross_check_with_trajectory(claim, session_id)` AI-slop 交叉验证 |
| **dsh-plugin-development V3.2**（新增）| §5 trajectory-debug 模式教程 |
| **paperclip-cost-control V1.0**（新增）| 接 `analyzePerf(price)` 输出真实运行成本 |
| **trajectory-replay-recorder.js**（新增 hook）| 把 replay session id 写入 session-distiller L0 |
| **anysearch V2**（潜在）| trajectory_search 与 anysearch.search 双通道 |
| **agent-reach V1.5.0**（潜在）| 把 perf 输出灌给雪球 / 小红书监控博主 |

---

## L6: 配置

### 6.1 启用模型工具（默认关闭）

```json5
// ~/.dsh/config.json 或 plugin patch
{
  "enableModelTools": true
}
```

### 6.2 价格表（cost 估算）

```yaml
# ~/.dsh/skills/dsh-trajectory-debug/price.yaml
providers:
  openai:
    input: 2.5      # $/1M tokens
    output: 10.0
  anthropic:
    input: 3.0
    output: 15.0
  deepseek:
    input: 0.14
    output: 0.28
```

---

## L7: 合规边界（MIT 一档）

| 条款 | 落点 |
|---|---|
| **LICENSE verbatim** | `skills/dsh-trajectory-debug-integration/LICENSE`（1,117 B · 21 行）|
| **版权声明** | `Copyright (c) 2026 Trajectory Debug Workbench contributors` |
| **作者署名** | 措辞 A **「由 devmom 个人维护，与 DSH 官方无关」** |
| **NOTICE 豁免** | MIT 无强制，单文件 LICENSE 即可 |

---

## L8: DONT 护栏（6 条）

- ❌ **不要**改写源码会话（model-visible == recorded 不变式）；fork 是唯一修改通道
- ❌ **不要**把 trajectory JSON 当生产数据用（projection 才是稳定形态）
- ❌ **不要**默认开启 `enableModelTools`（每 step 多一次 LLM 调用；opt-in）
- ❌ **不要**在 prod 环境用 `strategy: 'ask'`（无 live agent 时 fail-closed）
- ❌ **不要**写 FILE sidecar 路径到 git（`sidecar: 'memory'` 默认推荐）
- ❌ **不要**用 DSH 商标或"官方"措辞（措辞 A 是边界）

---

## L9: 验证

```bash
# 测试套件 7 文件 / 56 个 case（与 README 一致）
pnpm test
#  → Test Files  7 passed (7)
#  →      Tests  56 passed (56)
```

详见 [`stage-40-trajectory-debug.md §五`](../../memory/stage-40-trajectory-debug.md)。

---

## L10: 参考链接

- **上游仓库**：https://github.com/devmom/dsh-trajectory-debug
- **上游 LICENSE**：https://raw.githubusercontent.com/devmom/dsh-trajectory-debug/master/LICENSE
- **上游 CHANGELOG**：https://raw.githubusercontent.com/devmom/dsh-trajectory-debug/master/CHANGELOG.md
- **上游 COMPARISON**：https://raw.githubusercontent.com/devmom/dsh-trajectory-debug/master/COMPARISON.md
- **天龙主题文件**：[`memory/stage-40-trajectory-debug.md`](../../memory/stage-40-trajectory-debug.md)
- **天龙 dsh-plugin-development SKILL**：[`skills/dsh-plugin-development/SKILL.md`](../dsh-plugin-development/SKILL.md)（V3.2 起含 trajectory-debug 模式）
