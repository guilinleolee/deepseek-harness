/**
 * Human command plane: /trajectory, /perf, /breakpoint.
 *
 * Commands run in the UI command plane and their results never enter model
 * history (per the commands contract). They are registered only when a
 * command registry is mounted (`ctx.commands`).
 *
 * @module dsh-trajectory-debug-host/commands
 */

import type { Context } from '@deepseek-ai/cordis'
import type { CommandResult } from '@deepseek-ai/dsh-commands'
import type { DebugSession } from 'dsh-trajectory-debug'
import { adaptSession } from './adapt.ts'
import { analyzePerf } from './perf-analyzer.ts'
import { buildTrajectoryPage, stepBoundaries, stepContextAt } from './replay-engine.ts'

interface CommandHandlers {
  /** Summarize a session's trajectory (last N rows + step/turn counts). */
  summarizeTrajectory: (session: DebugSession, stepIndex?: number) => string
  /** Summarize the perf snapshot as text. */
  summarizePerf: (session: DebugSession) => string
}

/** Register the plugin's commands; returns the disposer or `undefined`. */
export function registerTrajectoryDebugCommands(ctx: Context, handlers: CommandHandlers): (() => void) | undefined {
  const registry = ctx.get('commands')
  if (registry === undefined) return undefined

  const disposers = [
    registry.register({
      name: 'trajectory',
      description: 'Show a trajectory summary for the current session; optional step index to inspect one step',
      handler: ({ agent, rawInput }): CommandResult => {
        const session = adaptSession(agent.session)
        const stepIndex = parseInt((rawInput ?? '').trim(), 10)
        return {
          kind: 'success',
          text: handlers.summarizeTrajectory(session, Number.isFinite(stepIndex) ? stepIndex : undefined),
        }
      },
    }),
    registry.register({
      name: 'perf',
      description: 'Show the performance snapshot for the current session',
      handler: ({ agent }): CommandResult => {
        const session = adaptSession(agent.session)
        return { kind: 'success', text: handlers.summarizePerf(session) }
      },
    }),
  ]
  return () => {
    for (const dispose of disposers) dispose()
  }
}

/** Default summary implementations shared by commands and the CLI-ish paths. */
export function summarizeTrajectory(session: DebugSession, stepIndex?: number): string {
  const { rows, stepCount, turnCount } = buildTrajectoryPage(session.events, {
    window: { offset: 0, limit: 8 },
  })
  const lines = rows.map((row) => {
    switch (row.kind) {
      case 'turn':
        return `#${row.turn} turn${row.reason ? ` (${row.reason})` : ''}`
      case 'step':
        return `  step ${row.step} [${row.status}]${row.modelMs !== undefined ? ` ${row.modelMs}ms` : ''}${row.inputTokens !== undefined ? ` ${row.inputTokens}→${row.outputTokens} tok` : ''}`
      case 'tool':
        return `    ${row.status === 'error' ? '❌' : '✅'} ${row.name}${row.durationMs !== undefined ? ` ${row.durationMs}ms` : ''}${row.result?.code !== undefined ? ` [${row.result.code}]` : ''}`
    }
  })
  const base = `trajectory: ${turnCount} turns / ${stepCount} steps\n${lines.join('\n')}`
  if (stepIndex === undefined) return base
  const steps = stepBoundaries(session.events).length
  if (stepIndex < 0 || stepIndex >= steps) return `${base}\nstep ${stepIndex} out of range (${steps} steps)`
  const context = stepContextAt(session.events, session.id, stepIndex)
  const toolLines = context.action.tools.map((tool) =>
    `    ${tool.status === 'error' ? '❌' : '✅'} ${tool.name} ${JSON.stringify(tool.args).slice(0, 160)}${tool.result?.code !== undefined ? ` [${tool.result.code}]` : ''}`,
  )
  return `${base}\n— step ${stepIndex} detail: history ${context.modelView.length} messages, ${context.action.tools.length} tool call(s)\n${toolLines.join('\n')}`
}

export function summarizePerf(session: DebugSession): string {
  const perf = analyzePerf(session.events, session.id, session.events.at(-1)?.seq)
  const toolLines = Object.entries(perf.tools)
    .sort((a, b) => b[1].calls - a[1].calls)
    .slice(0, 10)
    .map(([name, t]) => `  ${name}: ${t.calls} calls, ${t.failed} failed, p50 ${t.ms.p50}ms`)
  const failureLines = perf.failures.map((f) => `  ${JSON.stringify(f.category)} × ${f.count}`)
  return [
    `perf: ${perf.turns.steps} steps / ${perf.turns.count} turns`,
    `  tokens in ${perf.tokens.totalInput} / out ${perf.tokens.totalOutput}`,
    `  llm ${Math.round(perf.timing.llmMs)}ms, tools ${Math.round(perf.timing.toolMs)}ms, ttft ${Math.round(perf.timing.ttftMs)}ms`,
    ...(toolLines.length > 0 ? ['tools:', ...toolLines] : []),
    ...(failureLines.length > 0 ? ['failures:', ...failureLines] : []),
  ].join('\n')
}
