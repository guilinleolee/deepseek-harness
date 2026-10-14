/**
 * Sales-development lead-generation pipeline.
 * Five model-facing tools driving a five-stage state machine with hash-bound approval.
 *
 * @module @deepseek-ai/dsh-lead-generation
 */
import type { Context } from '@deepseek-ai/cordis'
import z from '@deepseek-ai/schemastery'
// Declaration merge only: makes ctx.systemPrompt visible for section registration.
import type {} from '@deepseek-ai/dsh-system-prompt'
import { TaskState } from './state.ts'
import { buildLgCreateTask } from './tools/lg_create_task.ts'
import { buildLgProspect } from './tools/lg_prospect.ts'

export const name = 'lead-gen'
export const inject = ['tools', 'systemPrompt']

/**
 * Plugin configuration.
 * `storagePath` and `approvalsPath` have NO default: a `process.cwd()` fallback
 * would scatter task files wherever the process happens to start. Assemblies
 * state the locations explicitly through `dshHomePath('lead-gen/...')`.
 */
export interface Config {
  /** Path to the JSON file holding the per-task state records. */
  storagePath: string
  /** Path to the JSON file holding the per-prospect approval hashes. */
  approvalsPath: string
  /** Hard gate on every outbound connector; the agent has no `send` tools. */
  dryRun: boolean
  /** Allow the agent to write new entries into the knowledge base. */
  agentKnowledge: boolean
  /** Allow the agent to reconfigure outbound connectors. */
  agentConfig: boolean
  /** Synthetic seed count used when no real data source is mounted. */
  synthSeedCount: number
}

export const Config: z<Config> = z.object({
  storagePath: z.string().required(),
  approvalsPath: z.string().required(),
  dryRun: z.boolean().default(true),
  agentKnowledge: z.boolean().default(false),
  agentConfig: z.boolean().default(false),
  synthSeedCount: z.natural().min(1).max(200).default(30),
})

const GUIDANCE = `
You operate a five-stage lead-generation pipeline:
  parsing → prospecting → research → scoring → drafting → approval → closed.

Each stage has exactly one tool. Tools refuse to advance unless their
prerequisite stage completed, and (after drafting) every draft carries an
approved content hash. Outbound senders are intentionally absent: you have
no \`send_email\`, \`send\`, or connector dispatch tool. Every approval is a
persistent fact written to the approvals file, not a transient decision.
`

/** Register the guidance section and the v0.1 `lg_create_task` tool. */
export function apply(ctx: Context, config: Config): void {
  ctx.systemPrompt.section({
    name: 'lead-gen:guidance',
    order: 110,
    text: GUIDANCE.trim(),
  })

  const state = new TaskState(config.storagePath)
  ctx.tools.register(buildLgCreateTask(state))
  ctx.tools.register(buildLgProspect(state))

  // TODO(p5-p7): wire `lg_research`, `lg_score`, `lg_draft`.
  // TODO(p8): wire the approval gate; downstream tools must assert at entry.
}
