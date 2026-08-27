/**
 * Model-facing tools (P2, opt-in via `enableModelTools`).
 *
 * Let the agent inspect its own trajectory and performance — aimed at plugin
 * developers debugging their own tools. All three tools are read-only and
 * render text; none executes anything.
 *
 * NOTE on scope: these tools register into the GLOBAL tools layer on the host
 * context, so every session sees them once enabled. That is the documented
 * trade-off of the opt-in flag; the per-session agent-preset split remains a
 * later refinement.
 *
 * @module dsh-trajectory-debug-host/model-tools
 */

import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'
import type { DebugSession, JsonValue } from 'dsh-trajectory-debug'
import { adaptSession } from './adapt.ts'
import { summarizePerf } from './commands.ts'
import { buildTrajectoryPage, stepBoundaries, stepContextAt } from './replay-engine.ts'

/** Resolves a DebugSession from a sessionId (the model passes the id). */
export type SessionResolver = (sessionId: string) => DebugSession | undefined

export interface ModelToolsContext {
  resolveSession: SessionResolver
}

/** Text-only output renderer (ContentBlock[] per the tools contract). */
function textResult(text: string): {
  schema: { type: 'string' }
  render: () => Array<{ type: 'text'; text: string }>
} {
  return {
    schema: { type: 'string' },
    render: () => [{ type: 'text', text }],
  }
}

/** Register the three read-only trajectory tools; returns the disposer. */
export function registerTrajectoryModelTools(ctx: Context, modelCtx: ModelToolsContext): () => void {
  const disposers: Array<() => void> = []

  disposers.push(
    ctx.tools.register(defineTool({
      name: 'trajectory_search',
      description:
        'Search a session\'s trajectory ledger: filter tool calls by name, error code or status, and get matching rows with timing and results.',
      parameters: {
        sessionId: { type: 'string', required: true, description: 'Session id to search (same session unless debugging another).' },
        toolName: { type: 'string', description: 'Only rows of this tool name.' },
        errorCode: { type: 'string', description: 'Only tool results with this error code.' },
        status: { type: 'string', description: 'Filter by tool status: ok | error | pending.' },
        limit: { type: 'integer', description: 'Max rows to return (default 20).' },
      },
      output: textResult(''),
      isConcurrencySafe: () => true,
      async execute(args: { sessionId: string; toolName?: string; errorCode?: string; status?: 'ok' | 'error' | 'pending'; limit?: number }) {
        const session = modelCtx.resolveSession(args.sessionId)
        if (session === undefined) {
          return 'trajectory_search: session not found'
        }
        const { rows, stepCount, turnCount } = buildTrajectoryPage(session.events, {
          window: { offset: 0, limit: args.limit ?? 20 },
          filter: {
            toolName: args.toolName,
            errorCode: args.errorCode,
            status: args.status === 'error' ? 'error' : args.status === 'ok' ? 'ok' : undefined,
          },
        })
        const lines = rows.map((row) => {
          switch (row.kind) {
            case 'turn':
              return `#${row.turn} turn${row.reason !== undefined ? ` (${row.reason})` : ''}`
            case 'step':
              return `step ${row.step} [${row.status}]${row.modelMs !== undefined ? ` ${row.modelMs}ms` : ''}`
            case 'tool':
              return `  ${row.status === 'error' ? '❌' : '✅'} ${row.name}${row.durationMs !== undefined ? ` ${row.durationMs}ms` : ''}${row.result?.code !== undefined ? ` [${row.result.code}]` : ''}${row.result?.contentPreview !== undefined ? ` — ${row.result.contentPreview.slice(0, 120)}` : ''}`
          }
        })
        return [`trajectory_search: ${turnCount} turns / ${stepCount} steps, ${rows.length} rows shown`, ...lines].join('\n')
      },
    })),
  )

  disposers.push(
    ctx.tools.register(defineTool({
      name: 'trajectory_step',
      description:
        'Inspect one step of a session: what the model had seen before the step (history) and what the step did (tool calls + results).',
      parameters: {
        sessionId: { type: 'string', required: true, description: 'Session id.' },
        stepIndex: { type: 'integer', required: true, description: '0-based step index.' },
      },
      output: textResult(''),
      isConcurrencySafe: () => true,
      async execute(args: { sessionId: string; stepIndex: number }) {
        const session = modelCtx.resolveSession(args.sessionId)
        if (session === undefined) return 'trajectory_step: session not found'
        const steps = stepBoundaries(session.events).length
        if (args.stepIndex < 0 || args.stepIndex >= steps) {
          return `trajectory_step: step ${args.stepIndex} out of range (${steps} steps)`
        }
        const context = stepContextAt(session.events, session.id, args.stepIndex)
        const history = context.modelView.length
        const toolLines = context.action.tools.map((tool) =>
          `  ${tool.status === 'error' ? '❌' : '✅'} ${tool.name} ${JSON.stringify(tool.args).slice(0, 200)}${tool.result?.code !== undefined ? ` [${tool.result.code}]` : ''}`,
        )
        return [
          `trajectory_step ${args.stepIndex}: history ${history} messages, ${context.action.tools.length} tool call(s)`,
          ...toolLines,
        ].join('\n')
      },
    })),
  )

  disposers.push(
    ctx.tools.register(defineTool({
      name: 'trajectory_perf',
      description: 'Performance snapshot of a session: tool success rates, failure categories, token totals and timing.',
      parameters: {
        sessionId: { type: 'string', required: true, description: 'Session id.' },
      },
      output: textResult(''),
      isConcurrencySafe: () => true,
      async execute(args: { sessionId: string }) {
        const session = modelCtx.resolveSession(args.sessionId)
        if (session === undefined) return 'trajectory_perf: session not found'
        return summarizePerf(session)
      },
    })),
  )

  return () => {
    for (const dispose of disposers) dispose()
  }
}

/** Default resolver over a live SessionStore (the provider supplies it). */
export function createSessionResolver(sessions: { get(id: string): { id: string; events: readonly unknown[] } | undefined }): SessionResolver {
  return (sessionId) => {
    const session = sessions.get(sessionId)
    return session === undefined ? undefined : adaptSession(session as never)
  }
}
