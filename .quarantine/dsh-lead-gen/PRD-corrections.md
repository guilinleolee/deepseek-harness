# DSH 智能获客插件 · PRD 技术修正（PATCH）

> 本文是对 `产品需求文档（PRD）：DSH 智能获客插件` 的**逐项技术修正**。
> 凡与原 PRD 冲突处，以本文为准。修正依据：已逐项核对本机 `D:\deepseek-harness` 源码。

---

## 修订对照表

| 编号 | 严重度 | 原 PRD 表述 | 修正后 | 依据 |
|---|---|---|---|---|
| P0-1 | 🔴 阻断 | 第二章将 `ctx.httpServer.register()` 列为四大能力接缝之一 | **删除** | 全仓 grep `httpServer` 在 `packages/` 内零能力命中 |
| P0-2 | 🔴 阻断 | `peerDependencies` 锁 `0.1.0-rc.6` | 改为 `workspace:^`（如需 semver 锁则用 `>=0.1.1-rc.2 <0.2`） | `package.json` 实际版本 `0.1.1-rc.2`；`tool-workflow/package.json` 使用 `workspace:^` 是仓库规范写法 |
| P0-3 | 🔴 阻断 | 自建 `lg_review_drafts` / `lg_continue_after_approval` + 哈希绑定 + 自建 `lg_audit_log` | 复用原生 `@deepseek-ai/dsh-user-approval` + `tool-ask-user`；删除自建审计 | `packages/interaction/user-approval/src/index.ts` 第 192 行 `class ApprovalService` 已托管 ask/decided 审计对 |
| P1-1 | 🟠 设计 | 9 阶段中 6 个共用 `lg_next_step` | 拆为语义化工具：`lg_prospect` / `lg_research` / `lg_score` / `lg_draft` / `lg_plan_followup` / `lg_prepare_quote` / `lg_close`；状态机强制力移到每个工具的入口断言 | 仓库 AGENTS.md：description 须写明副作用；tool render 是 `args` 的纯函数 |
| P1-2 | 🟠 设计 | 自写 `~/.dsh/lead-gen/state.json` 原子写 | 改用 `@deepseek-ai/dsh-storage-json` | 仓库已有官方持久化包，`packages/storage/storage-json` |
| P1-3 | 🟠 设计 | `DSH_LG_AGENT_KNOWLEDGE=1` 等环境变量旁路 | **删除全部 `DSH_LG_*` 环境变量** | 仓库 AGENTS.md：*No hardcoded tunables in plugins*，部署差异必须 `Config` 字段+cordis.yml |
| P1-4 | 🟠 合规 | 无 `src/invariant.ts` | 目录补 `src/invariant.ts` | `verify-package-invariants` 门禁 |
| P1-5 | 🟠 合规 | 测试仅 1 个 `tests/smoke.test.ts` | 补 1 个 REAL-composition 测试（真实 cordis.yml 过 Loader） | `packages/AGENTS.md` + `docs/testing.md` |
| P2-1 | 🟡 风格 | `cordis.patch.yml` 写法缺注释 | 加注释说明 row 用途，参考 `packages/bundle/base/cordis.patch.yml` | 仓库风格 |
| P2-2 | 🟡 风格 | `defineTool` 描述缺失前置/副作用 | 按仓库 `tool-ask-user/src/index.ts` 第 16-17 行的描述风格补全 | `docs/cookbook/adding-a-tool.md` |

---

## 修正一：删除 `ctx.httpServer` 整章

**原 PRD 第二章**：

> | `ctx.httpServer.register()`（可选） | 提供面板数据路由 `/plugins/lead-gen/state`（Web UI 可视化） |

**修正**：本机 DSH 不存在 `httpServer` 服务注入。Web 面板能力由 **client bundle 体系**承载：`packages/client/ui-*`（43 个），例如 `ui-jobs`、`ui-plan`、`ui-workflow-run`。

**正确做法**（仅二选一）：

- **方案 A（推荐）**：v0.1 不做面板，仅 host 端工具。客户通过审计日志 + 状态文件查看进度。
- **方案 B**：v0.2 增加一个 `ui-lead-gen-board` client bundle 作为独立 deliverable，与本插件并列发布，**不依赖本插件的 host 代码提供路由**。

---

## 修正二：依赖版本对齐

**原 PRD 第六章 6.4**：

> 必须在 `peerDependencies` 中锁 `@deepseek-ai/dsh-tools` 到 `0.1.0-rc.6` 或 `>=0.1.0-rc.6 <0.2`

**修正**：本机 `package.json` 与 `packages/core/tools/package.json` 实际版本均为 `0.1.1-rc.2`；`0.1.0-rc.6` 不存在。仓库 workspace 包统一用 `workspace:^` 协议。

**正确写法**（参照 `packages/workflow/tool-workflow/package.json` 第 30-39 行）：

```json
"peerDependencies": {
  "@deepseek-ai/dsh-tools": "workspace:^",
  "@deepseek-ai/dsh-system-prompt": "workspace:^",
  "@deepseek-ai/dsh-storage-json": "workspace:^",
  "@deepseek-ai/cordis": "workspace:^"
}
```

如需 semver 锁（用于发布到 npm 注册表），改为 `">=0.1.1-rc.2 <0.2"`。**开发期永远用 `workspace:^`**。

---

## 修正三：审批与审计复用原生接缝

**原 PRD 第 3.1 / 3.3 / 6.4**：

- `lg_review_drafts`：列出草稿，发起人工审批
- `lg_continue_after_approval`：**校验草稿哈希**，不通过则拒绝
- `lg_audit_log`：查询审计事件列表

**修正后总判断**：

- **审计** 完全删除——`@deepseek-ai/dsh-user-approval` 服务内嵌 `approval/asked` + `approval/decided` 两个 session 事件，自动进入 session 日志
- **审批问题** 复用 `tool-ask-user`（基于 `ctx.userQuestions`）——一次可问多个问题，每问有 `id`，答案原样回填
- **哈希绑定** 不再通过 `approval.request()` 实现——`approval.request()` 是 **readonly 同进程问题**，只能返回 `'allowed-once'` 一种放行结果，没有"哈希校验失败则拒绝"的钩子点

**正确的"草稿哈希绑定"实现路径**：

1. 模型生成草稿后，落盘到状态文件 `tasks/<id>/drafts/<n>.md`
2. 计算 `sha256(草稿正文)` 作为 `draftHash`
3. `lg_draft` 在 tool result 里返回 `draftHash`（**不是校验，是告知**）
4. **人工审批阶段用 `ask_user_question`**（非 `approval.request()`），UI 列出 5 封草稿
5. 人工改稿后的版本用 `lg_draft` 重新生成并落盘（hash 自动变更）
6. 后续阶段 `lg_plan_followup` / `lg_close` 在 `apply()` 入口断言：当前状态文件中所有草稿必须有一对 `approved_at` 时间戳与对应 hash 记录
7. 模型层无法绕过——因为没有工具跳过这个断言

**关键设计点**：审批**不是状态机的一道关**，而是**对落盘内容的持久化标记 + 后续工具的入口断言**。`approval.request()` 用于"是否发送这封邮件"这种对外动作的临时放行，不用于"内容是否被人类审过"这种持久化事实。

---

## 修正四：工具语义化拆分

**原 PRD 3.1**：9 阶段中 6 个共用 `lg_next_step`。

**修正后工具清单**（v0.1 MVP 4 阶段；其余 5 阶段挪至迭代二）：

| 工具 | 状态机位置 | 入口断言 | 主要副作用 |
|---|---|---|---|
| `lg_create_task` | 起始 | 无 | 写入任务记录，生成 task_id |
| `lg_prospect` | parsing → prospecting | task 存在 + 阶段=parsing | 写入候选客户列表 |
| `lg_research` | prospecting → research | 阶段=prospecting + 客户列表非空 | 写入公司档案 |
| `lg_score` | research → scoring | 阶段=research + 档案完整 | 写入评分 |
| `lg_draft` | scoring → drafting | 阶段=scoring + 评分存在 | 写入草稿 + 落盘 + 返回 draftHash |
| `lg_plan_followup` | drafting → followup | 阶段=drafting + **所有草稿有 approved_at + hash 匹配** | 写入跟进计划 |
| `lg_prepare_quote` | followup → quoting | 阶段=followup | 写入报价素材 |
| `lg_close` | quoting → closed | 阶段=quoting | 写入结案报告 |
| `lg_get_task` | 任意 | 无 | 只读 |
| `lg_knowledge_search` | 任意 | 无 | 只读 |
| `lg_connector_status` | 任意 | 无 | 只读 |

**注意**：`lg_review_drafts` 删除——改用 `ask_user_question` 在工具**之间**（不是工具内部）执行。

**为什么删除 `lg_review_drafts`**：
- 它是一个"工具内提问"的反模式。`tool-ask-user` 是为此而生的——在工具**调用前**由模型决定问什么，而不是把 UI 逻辑塞进插件自己的工具。
- 哈希校验已在每个下游工具的入口断言，状态机强制力不来自"必须先调审批工具"，而来自"下游工具拒绝未审批内容"。

---

## 修正五：环境变量旁路删除

**原 PRD 第四章**：

> **环境变量替代方案**：
> - `DSH_LG_AGENT_KNOWLEDGE=1` 启用 Agent 知识写入
> - `DSH_LG_AGENT_CONFIG=1` 启用 Agent connector 配置
> - `DSH_LG_DATA_FILE=./custom.json` 自定义状态路径

**修正**：**全部删除**。仓库 AGENTS.md 明确规定：

> No hardcoded tunables in plugins: deployment-varying choices are validated Config fields changeable from cordis.yml; a `DEFAULT_*` constant or test hook is not configurability.

**正确做法**：通过 cordis.yml 注入（参照 `packages/bundle/base/cordis.patch.yml` 第 188-192 行 `approval` 行的写法）：

```yaml
- id: lead-gen
  name: '@deepseek-ai/dsh-lead-generation'
  config:
    storage: !!js dshHomePath('lead-gen/state.json')
    dryRun: true
    agentKnowledge: false
    agentConfig: false
```

---

## 修正六：持久化复用 `storage-json`

**原 PRD 第二章 / 第四章**：

> 任务状态持久化在 `~/.dsh/lead-gen/state.json`（自己拼路径，原子写）

**修正**：本机已有 `@deepseek-ai/dsh-storage-json`，直接依赖。

**示例用法**（伪代码，需对照 `storage-json` 的实际 API 落地）：

```typescript
import { Storage } from '@deepseek-ai/dsh-storage-json'
const storage = new Storage({ path: ctx.config.storage })
await storage.set('tasks/<id>', { state: 'prospecting', ... })
```

`storage-json` 的存储位置由 cordis.yml 注入（见修正五），插件代码**不再硬编码 `~/.dsh/...`**。

---

## 修正七：合规门禁补齐

### `src/invariant.ts`

仓库硬性要求（`packages/AGENTS.md`）：

> Every package owns `./invariant`. Register the manifest name; check an event/data relation or give empty installers package-specific `No runtime invariant:` reasons.

**最小骨架**（具体 event 名待 `index.ts` 落地后填）：

```typescript
/**
 * Runtime invariants for dsh-lead-generation.
 * @module @deepseek-ai/dsh-lead-generation/invariant
 */
import { createInvariant } from '@deepseek-ai/dsh-runtime-diagnostics/invariant'
export const manifest = createInvariant({
  name: '@deepseek-ai/dsh-lead-generation',
})
```

如果当前没有可断言的 event/data 关系，按仓库规则写明 `No runtime invariant: <原因>`，**不能留空**。

### REAL-composition 测试

仓库硬性要求（`packages/AGENTS.md`）：

> Product-visible plugins require a non-unit REAL-composition test. Hand-built `ctx.plugin(...)` suites are insufficient. Boot test-only `cordis.yml` through the Loader and app/process.

**最小可接受测试集**：

| 测试名 | 断言 |
|---|---|
| `composition.boot.spec.ts` | 通过 Loader 加载 `tests/fixtures/cordis.yml`，断言插件注册成功、`lg_create_task` 出现在 `ctx.tools` |
| `composition.draft-hash.spec.ts` | 同上环境，跑完 `lg_create_task → lg_prospect → lg_research → lg_score → lg_draft`，断言落盘文件存在、状态文件记录了 `draftHash` |
| `composition.approval-gate.spec.ts` | 同上环境，断言直接调 `lg_plan_followup` 在无 approved 草稿时被拒绝（**不依赖 ask_user_question**） |

---

## 修正八：`cordis.patch.yml` 示例改写

**原 PRD 6.2 给出的写法**：

```yaml
- insert:
    - id: dsh-lead-generation
      name: dsh-lead-generation
      config:
        dataFile: ~/.dsh/lead-gen/state.json
        dryRun: true
```

**问题**：
1. `name` 应为完整的 npm 包名
2. 缺注释（其它 bundle row 都有注释说明 row 用途）
3. `dataFile` 用了硬编码 `~`，违反 "no hardcoded tunables"
4. 没遵循"row 的 `config` 整体替换"语义

**正确写法**（参照 `cordis.patch.yml` 整体风格）：

```yaml
# Sales-development lead-generation pipeline. Dry-run gates every outbound
# connector; downstream tools refuse draft content without an approved hash.
- insert:
    - id: lead-gen
      name: '@deepseek-ai/dsh-lead-generation'
      config:
        storage: !!js dshHomePath('lead-gen/state.json')
        dryRun: true
        agentKnowledge: false
        agentConfig: false
```

---

## 验收标准（v0.1 必满足）

依据 §四 业务缺口分析，补全可度量验收项：

| 指标 | 目标 |
|---|---|
| 插件安装 | `pnpm install` 成功，零警告 |
| 离线启动 | 合成数据下，5 封草稿端到端 ≤ 5 分钟 |
| 工具 schema | 全部 `defineTool`，描述包含"何时调用 / 前置 / 副作用" |
| 状态机强制 | 跳过 `lg_draft` 直接调 `lg_plan_followup` 必失败（REAL 测试断言） |
| 哈希绑定 | 改稿后原 `approved_at` 记录自动失效（REAL 测试断言） |
| Dry-run | 任何对外发送类操作返回 `blocked-dry-run`，无真实副作用（REAL 测试断言） |
| 审计 | 一次端到端运行后 session log 出现 `approval/asked` + `approval/decided` 对 |
| 测试 | 1 单元 + 3 REAL-composition，全绿 |
| 文档 | README 含 Model Experience 段落、Known Limitations 段落 |

---

## 版本号策略

| 阶段 | 版本 |
|---|---|
| 当前开发 | 跟随仓库主分支（`0.1.1-rc.2`） |
| v0.1 发布 | `0.1.1-rc.3` |
| v0.1 稳定后 | `0.1.1` |
| 私有部署授权版 | `0.1.2-licensed.<license-id>` |

**禁止** 锁定到 `0.1.0-rc.6`——此版本在本机不存在，会导致 install 失败。