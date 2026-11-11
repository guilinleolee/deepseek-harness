# dsh-lead-generation · 实现蓝图 v0.1

> 目标：实现一个可加载的 v0.1 DSH 插件，含 5 工具 + 审批门控 + 哈希绑定。
> 本蓝图面向"接力实施"——任何拿到本文的工程师/Agent 都能从这里推进。

---

## 一、目录结构

```
packages/extensions/dsh-lead-generation/
├── package.json
├── cordis.patch.yml
├── tsconfig.json
├── README.md
├── src/
│   ├── index.ts                       # name / inject / Config / apply
│   ├── invariant.ts                   # 仓库硬性门禁
│   ├── state.ts                       # 任务状态机 + 持久化
│   ├── config.ts                      # Config schema (schemastery)
│   ├── approval.ts                    # 哈希绑定 + 审批状态读取
│   ├── tools/
│   │   ├── lg_create_task.ts
│   │   ├── lg_prospect.ts
│   │   ├── lg_research.ts
│   │   ├── lg_score.ts
│   │   └── lg_draft.ts
│   └── synth/
│       └── seed.ts                    # 合成客户数据（演练用，v0.1 默认数据源）
└── tests/
    ├── composition.spec.ts            # REAL-composition 测试（必需）
    └── fixtures/
        └── cordis.yml                 # 测试专用 cordis 装配
```

---

## 二、阶段拆分（接力推进）

| 阶段 | 依赖 | 估时 | 输出 |
|---|---|---|---|
| **P0 包骨架** | — | 1-2h | package.json + cordis.patch.yml + tsconfig + index.ts stub |
| **P1 invariant** | P0 | 1h | src/invariant.ts 通过 `verify-package-invariants` |
| **P2 state.ts** | P0 | 2-3h | 任务状态机 + 原子写 + 验收测试 |
| **P3 lg_create_task** | P0, P2 | 1-2h | 创建任务，幂等返回 task_id |
| **P4 lg_prospect + seed** | P0, P2, P3 | 2-3h | 合成客户列表落盘 |
| **P5 lg_research** | P0, P2, P4 | 1h | 公司档案落盘 |
| **P6 lg_score** | P0, P2, P5 | 1h | 评分落盘（合成评分，规则见 rehearsal/scoring-rules.md） |
| **P7 lg_draft** | P0, P2, P6 | 2-3h | 草稿落盘 + draftHash 计算 |
| **P8 审批门控** | P0, P2 | 2-3h | approved_hashes.json + 下游工具入口断言 |
| **P9 REAL-composition 测试** | 所有 | 2-3h | tests/composition.spec.ts（Loader 启动 + 端到端） |
| **P10 文档** | 所有 | 1-2h | README + Model Experience + Known Limitations |

**总估时**：15-22h（1 名熟练工程师 2-3 工作日；不熟练或调试门禁 1 周）

---

## 三、关键文件骨架

### 3.1 `package.json`（关键字段）

```json
{
  "name": "@deepseek-ai/dsh-lead-generation",
  "version": "0.1.1-rc.2",
  "type": "module",
  "main": "lib/index.js",
  "types": "lib/types/index.d.ts",
  "exports": {
    ".": {
      "types": "./lib/types/index.d.ts",
      "default": "./lib/index.js"
    },
    "./invariant": {
      "types": "./lib/types/invariant.d.ts",
      "default": "./lib/invariant.js"
    },
    "./src/*": "./src/*",
    "./package.json": "./package.json"
  },
  "files": [
    "lib/index.js",
    "lib/invariant.js",
    "cordis.patch.yml",
    "lib/types/**/*.d.ts"
  ],
  "license": "MIT",
  "dsh": {
    "bundle": {
      "patch": "./cordis.patch.yml"
    }
  },
  "peerDependencies": {
    "@deepseek-ai/cordis": "workspace:^",
    "@deepseek-ai/dsh-tools": "workspace:^",
    "@deepseek-ai/dsh-system-prompt": "workspace:^",
    "@deepseek-ai/dsh-llm": "workspace:^"
  }
}
```

**注意**：
- `dsh.bundle.patch` 必须存在（仓库 `verify-cordis-config` 门禁）
- peerDependencies 用 `workspace:^`（非硬编码 `0.1.0-rc.6`）
- TODO(scope-clarify): 是否需要 `@deepseek-ai/dsh-storage-json` peerDependency？修正文档说"改用"，但具体是否需要依赖待 P2 验证

### 3.2 `cordis.patch.yml`

```yaml
# Sales-development lead-generation pipeline. Dry-run gates every outbound
# connector; downstream tools refuse draft content without an approved hash.
- insert:
    - id: lead-gen
      name: '@deepseek-ai/dsh-lead-generation'
      config:
        storagePath: !!js dshHomePath('lead-gen/state.json')
        approvalsPath: !!js dshHomePath('lead-gen/approved_hashes.json')
        dryRun: true
        agentKnowledge: false
        agentConfig: false
        synthSeedCount: 30
```

**注意**：
- `storagePath` / `approvalsPath` 走 `dshHomePath()` 而非硬编码 `~/.dsh/...`
- 顶层是数组，**不是对象**
- TODO(scope-clarify): `dshHomePath` 是否真是这个函数名？需 P0 验证

### 3.3 `src/index.ts`（最小骨架）

```typescript
/**
 * Sales-development lead-generation pipeline.
 * Five model-facing tools driving a 5-stage state machine with hash-bound approval.
 *
 * @module @deepseek-ai/dsh-lead-generation
 */
import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'dsh-lead-generation'
export const inject = ['tools', 'systemPrompt']

export interface Config {
  storagePath: string
  approvalsPath: string
  dryRun: boolean
  agentKnowledge: boolean
  agentConfig: boolean
  synthSeedCount: number
}

export function apply(ctx: Context, config: Config): void {
  ctx.systemPrompt.section({
    name: 'lead-gen:guidance',
    order: 110,
    text: `You operate a 5-stage lead-generation pipeline. ` +
      `Stages: parsing → prospecting → drafting → approval → closed. ` +
      `Tools refuse to advance unless their prerequisite stage completed and ` +
      `(after drafting) every draft carries an approved hash.`,
  })

  // TODO(scope-clarify): 注册 5 个工具（P3-P7）
  // TODO(scope-clarify): 注册持久化、审批读取、合成数据源（P2 / P4 / P8）
}
```

### 3.4 `src/state.ts`（核心算法骨架）

```typescript
/**
 * Task state machine and atomic persistence.
 */
import { writeFileAtomic, readWholeText } from '@deepseek-ai/dsh-fs-local'  // 已确认
import { createHash } from 'node:crypto'
import { resolveLocalTarget } from '@deepseek-ai/dsh-fs-local'  // 用于路径 → LocalTarget

export type Stage = 'parsing' | 'prospecting' | 'research' | 'scoring' | 'drafting' | 'approval' | 'closed'

const STAGE_ORDER: readonly Stage[] = [
  'parsing', 'prospecting', 'research', 'scoring', 'drafting', 'approval', 'closed',
]

export interface Task {
  taskId: string
  industry: string
  region: string
  count: number
  stage: Stage
  prospects?: Prospect[]
  dossiers?: Record<string, Dossier>
  scores?: Record<string, Score>
  drafts?: Record<string, Draft>
  approvedAt?: Record<string, { hash: string; approvedAt: string }>
  createdAt: string
}

export interface Prospect { id: string; name: string; country: string; category: string; /* ... */ }
export interface Dossier { size: string; platform: string; teamSize: number; /* ... */ }
export interface Score { total: number; tier: 'A' | 'B' | 'C' | 'D' }
export interface Draft { prospectId: string; body: string; draftHash: string; /* ... */ }

export class TaskState {
  constructor(private storagePath: string) {}

  async load(taskId: string): Promise<Task | undefined> { /* TODO(scope-clarify) */ }
  async save(task: Task): Promise<void> { /* TODO(scope-clarify): 原子写 */ }

  /**
   * Entry assertion for every downstream tool.
   * Refuses if `currentStage` is not `expectedStage`.
   */
  assertStage(task: Task, expectedStage: Stage): void {
    if (task.stage !== expectedStage) {
      throw new Error(
        `task ${task.taskId} expected stage ${expectedStage}, currently ${task.stage}`,
      )
    }
  }

  /**
   * Idempotent task creation.
   */
  async createOrLoad(args: { industry: string; region: string; count: number }): Promise<Task> { /* TODO */ }
}

/**
 * Compute draft content hash. Hex SHA-256 of the canonical body.
 */
export function computeDraftHash(body: string): string {
  return 'sha256:' + createHash('sha256').update(body, 'utf8').digest('hex')
}

/**
 * Returns the next stage in the pipeline, or throws if already terminal.
 */
export function nextStage(current: Stage): Stage {
  const idx = STAGE_ORDER.indexOf(current)
  if (idx < 0 || idx === STAGE_ORDER.length - 1) {
    throw new Error(`task already at terminal stage: ${current}`)
  }
  const next = STAGE_ORDER[idx + 1]
  if (next === undefined) throw new Error(`stage order broken at ${current}`)
  return next
}
```

### 3.5 `src/approval.ts`（哈希绑定骨架）

```typescript
/**
 * Approval gate. Reads approved_hashes.json; downstream tools call
 * `assertAllDraftsApproved()` at entry.
 */
import { readWholeText, resolveLocalTarget } from '@deepseek-ai/dsh-fs-local'  // 已确认
import { computeDraftHash } from './state.js'

export interface ApprovalsFile {
  version: number
  approvals: Record<string, { draftHash: string; approvedAt: string }>
}

export class ApprovalGate {
  constructor(private approvalsPath: string) {}

  async load(): Promise<ApprovalsFile> { /* TODO(scope-clarify) */ }

  /**
   * Entry assertion. For each prospect's current draft body, the recorded
   * approval's hash must match `computeDraftHash(currentBody)`.
   * Any mismatch throws with a clear, locatable message.
   */
  async assertAllDraftsApproved(drafts: Record<string, { body: string }>): Promise<void> {
    const file = await this.load()
    for (const [prospectId, draft] of Object.entries(drafts)) {
      const currentHash = computeDraftHash(draft.body)
      const approval = file.approvals[prospectId]
      if (approval === undefined) {
        throw new Error(`prospect ${prospectId} has no approval record; approve the draft first`)
      }
      if (approval.draftHash !== currentHash) {
        throw new Error(
          `prospect ${prospectId} draft hash changed: `
          + `was ${approval.draftHash}, now ${currentHash}; re-approve the new version`,
        )
      }
    }
  }
}
```

### 3.6 `src/tools/lg_create_task.ts`（最小工具骨架）

```typescript
import { defineTool } from '@deepseek-ai/dsh-tools'
import { TaskState } from '../state.js'

export function buildLgCreateTask(state: TaskState) {
  return defineTool({
    name: 'lg_create_task',
    description: 'Create or resume a lead-generation task. '
      + 'Idempotent on (industry, region, count). '
      + 'Returns the existing taskId if a matching task already exists. '
      + 'No side effects beyond the task record itself.',
    parameters: {
      industry: { type: 'string', required: true },
      region: { type: 'string', required: true },
      count: { type: 'integer', required: true, minimum: 1, maximum: 200 },
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          taskId: { type: 'string', required: true },
          stage: { type: 'string', required: true },
        },
      },
      render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }],
    },
    async execute(args) {
      const task = await state.createOrLoad(args)
      return { taskId: task.taskId, stage: task.stage }
    },
  })
}
```

---

## 四、关键技术澄清（已逐项核对源码）

> 本节记录 Q1-Q5 的源码验证结论。所有结论均可追溯到 `D:\deepseek-harness\packages\` 下指定文件与行号。

### Q1：`defineTool` 参数 DSL ✅

- **DSL 是 `@deepseek-ai/schemastery`**（`packages/core/tools/src/index.ts` 第 8 行 `import z from '@deepseek-ai/schemastery'`）
- `defineTool<S extends ParameterSchemaSpec, O extends ValueSchemaSpec>`：`packages/core/tools/src/schema.ts` 第 545 行
- `parameters` 字段是 `ParameterSchemaSpec`，**编译为 implicit open object root**——可直接写 `{ foo: { type: 'string', required: true } }`
- `output.schema` 是 `ValueSchemaSpec`，**严格 additionalProperties: false**
- `output.render(args, value): ContentBlock[]` 必须返回 ContentBlock 数组
- 可选实现 `presentCall` / `presentResult` 控制 UI 渲染意图（`packages/core/tools/src/schema.ts` 第 527-535 行）

### Q2：存储后端 ✅

**结论：用 `fs-local` 的 `writeFileAtomic` + 自写 JSON 解析**，**不**用 `storage-json`。

| 包 | 适用场景 | 不适用原因 |
|---|---|---|
| `@deepseek-ai/dsh-storage-json` | hub 模型，多个 unit 文件（`<root>/<unit>.json`） | 我们的任务是单文件 `state.json` |
| `@deepseek-ai/dsh-fs-local` | 暴露 `writeFileAtomic`、`readWholeText`、`probe` 等基础原语 | ✅ 适配 |

- `writeFileAtomic` 路径：`packages/fs/fs-local/src/fsio.ts` 第 533 行
- **无 `readJsonFile` helper**——必须 `JSON.parse(await readWholeText(target))`，且要在 `try/catch` 里处理 `SyntaxError`，命名清楚吞掉什么

### Q3：`dshHomePath` 可用性 ✅

- `app-boot` 通过 `ctx.provide('dshHomePath', dshHomePath)` 注入到 Context（`packages/boot/app-boot/src/index.ts` 第 770 行）
- 任何 plugin config 用 `!!js dshHomePath(...)` 都能访问
- **但**：插件**不应**自己拼 `dshHomePath(...)` 到 `cordis.patch.yml` 的 config 里——应该让使用方的 cordis.yml 注入
- `app-boot/boot(NAME, absoluteConfigPath)` 是标准启动入口

### Q4：REAL-composition 测试 ✅

**标准模板**（`packages/boot/app-boot/tests/app-boot.spec.ts` 第 662-684 行）：

```typescript
writeFileSync(join(dir, 'capture.mjs'), `
  export const name = "capture"
  export function apply(ctx, config) { ctx.provide("capturedPath", config.path) }
`)
writeFileSync(join(dir, 'cordis.yml'), `
  - id: capture
    name: ./capture.mjs
    config:
      path: !!js dshHomePath('sessions')
`)
ctx = await boot(NAME, join(dir, 'cordis.yml'))
expect(ctx.get('capturedPath')).toBe(join(dshHome, 'sessions'))
```

**我们的 composition 测试**：
- `tests/composition.spec.ts` 用 vitest 写
- 每个测试用例：`tmp()` 临时目录 + `.mjs` fixture 插件 + `cordis.yml` + `boot()` 启动 + 断言
- 注意 `vi.stubEnv('DSH_HOME', dshHome)` 必须设置环境变量

### Q5：`invariant.ts` ✅

**标准模板**（`packages/interaction/tool-ask-user/src/invariant.ts`）：

```typescript
import type { Context } from '@deepseek-ai/cordis'
import type { InvariantInstaller } from '@deepseek-ai/dsh-invariants'

const PACKAGE_NAME = '@deepseek-ai/dsh-lead-generation'
export const name = 'dsh-lead-generation-invariant'
export const inject = ['invariants']

/**
 * No runtime invariant: this model-facing adapter has no independent lifecycle
 * stream; execution relations are owned by the capability seam it calls.
 */
const install: InvariantInstaller = () => {}

export const apply = (ctx: Context): Promise<() => void> =>
  Promise.resolve(ctx.invariants.register(PACKAGE_NAME, install))
```

工具型插件统一采用"No runtime invariant: ..."注释 + 空 `install()`。**绝对不能留空无注释**——`verify-package-invariants` 门禁会失败。

---

## 五、推荐接力路径

> ⚠️ **不要一次性写完 v0.1**。每次只推进 1 个阶段，**跑通测试再进下一段**。

```
P0 (1-2h) → pnpm typecheck 通过
   ↓
P1 (1h) → pnpm run hygiene / verify-package-invariants 通过
   ↓
P2 (2-3h) → 单元测试 state.ts 通过
   ↓
P3 (1-2h) → lg_create_task 注册成功（手动冒烟）
   ↓
P4-P7 (每段 1-3h) → 每段 REAL-composition 测试新加 1 个
   ↓
P8 (2-3h) → 审批门控测试：草稿未审批时下游工具拒绝
   ↓
P9 (2-3h) → 完整端到端 REAL-composition：创建任务 → 跑完所有阶段
   ↓
P10 (1-2h) → README + 文档门禁通过
```

每个 Pn 完成后**立即 commit**，避免一次性大提交。

---

## 六、当前会话窗口产出清单

```
D:\deepseek-harness\packages\extensions\dsh-lead-gen\
├── PRD-corrections.md          # 技术修正（268 行）
├── commercialization.md         # 商业化方案（278 行）
├── IMPLEMENTATION_PLAN.md       # 实现蓝图（本文件，已含 Q1-Q5 源码验证）
└── rehearsal\                   # 离线演练产物
    ├── vertical.md              # 30 客户画像
    ├── scoring-rules.md         # 评分细则
    ├── drafts\*.md              # 5 封开发信
    ├── approval-log.md          # 审批演练
    └── SUMMARY.md               # 演练总结
```

**全部 9 个文件均为文档**，无 `.ts` 代码。

---

## 七、下次会话接力 P0 的最小可执行清单

> P0-P10 中所有未决问题已在 §四澄清。下次接力时**无需再做调研**，可直接进入 P0。

### P0 步骤（1-2h）

```
1. mkdir D:\deepseek-harness\packages\extensions\dsh-lead-generation
2. cd 上述目录
3. 写 package.json（按 §3.1 骨架，peerDependencies 用 workspace:^）
4. 写 cordis.patch.yml（按 §3.2 骨架）
5. 写 tsconfig.json（extends tsconfig.base.json，rootDir: src，outDir: lib/types）
6. 写 src/index.ts（按 §3.3 骨架，apply() 仅注册 systemPrompt section + 占位 TODO）
7. pnpm install（工作区根目录）
8. pnpm --filter @deepseek-ai/dsh-lead-generation typecheck
9. 失败则读错误修复（最常见的：exports 字段、tsconfig paths）
```

### P1 步骤（1h）

```
1. 复制 §4 Q5 的 invariant.ts 模板
2. pnpm run hygiene（验证 verify-package-invariants 通过）
3. git add . && git commit -m "feat(lead-gen): package skeleton + invariant"
```

### P2 步骤（2-3h）

```
1. 实现 §3.4 state.ts 的 load() / save() / createOrLoad() / assertStage() / nextStage()
2. 写 tests/state.spec.ts（vitest 单元测试，不走 boot）
3. 关键测试场景：
   - createOrLoad 幂等（相同 industry/region/count 返回相同 taskId）
   - 不同参数生成不同 taskId
   - assertStage 在错误阶段抛错
   - nextStage 终止态抛错
4. pnpm --filter @deepseek-ai/dsh-lead-generation test
```

### P3-P7（每段 1-3h）

每完成一段，**加 1 个 REAL-composition 测试用例**到 `tests/composition.spec.ts`，参照 §4 Q4 的 fixture 模板。

### P8（2-3h）

审批门控：每个下游工具入口断言 `await approvalGate.assertAllDraftsApproved(drafts)`，fixture 测试覆盖"未审批"、"改稿后 hash 变化"两个场景。

### P9（2-3h）

端到端 composition 测试：从 `lg_create_task` 一直跑到 `lg_close`，断言状态文件、批准文件、最终结案报告全部落盘。

### P10（1-2h）

```
README.md 必含：
- 安装命令（pnpm install + bundle 装配）
- 配置项表（来自 §3.1 Config）
- 工具清单（5 个 lg_* 工具）
- Model Experience 段落（来自 packages/AGENTS.md）
- Known Limitations 段落（来自 packages/AGENTS.md）
```

---

## 八、关键风险提醒

| 风险 | 缓解 |
|---|---|
| `pnpm install` 把整个 workspace 重建一遍，耗时 5-15min | 用 `--filter @deepseek-ai/dsh-lead-generation` 限定 |
| `verify-package-invariants` 在 P0 后立刻失败 | 提前写好 `src/invariant.ts`（按 §4 Q5 模板），**不要留空** |
| `defineTool` 类型推导严格，parameters 写错字段不报错但工具注册失败 | 参照 `packages/interaction/tool-ask-user/src/index.ts` 第 21-80 行的精确字段名 |
| `presentCall` / `presentResult` 未实现导致 UI 默认渲染丑陋 | v0.1 不实现（仓库规则说"decided up front"，未定可暂留默认） |
| REAL-composition 测试的 `tmp()` 临时目录清理 | vitest 的 `afterEach(() => rmSync(...))`，参考 `app-boot.spec.ts` 第 685 行 |

---

## 九、为何到此停手

写代码本身不是难事。但**写能通过仓库所有门禁的代码，需要至少一次完整的 pnpm install + typecheck + hygiene + test 循环**——单次会话跑不完，且中间任何一步失败都需重新调研。

把"调研完毕、代码未写"的状态作为接力点，让下次会话（或你本人）能**直接动手**，避免重复劳动。