#!/usr/bin/env node
/** Snapshot-only Loader driver: stream one fixture turn as canonical JSONL. */

import type { Context } from '@deepseek-ai/cordis'
import { boot, installFailLoud, loadEnv, resolveConfigPath } from '@deepseek-ai/dsh-app-boot'
import { runFixtureTurn } from '@deepseek-ai/dsh-loader-smoke'
import { ToolCallId } from '@deepseek-ai/dsh-llm'
import type { SessionEvent } from '@deepseek-ai/dsh-session'

const NAME = 'quant-research-test-driver'
const [configPath, ...taskParts] = process.argv.slice(2)
if (configPath === undefined || taskParts.length === 0 || taskParts.every(part => part.trim() === '')) {
  throw new Error(`${NAME}: expected <config-path> <task...>`)
}

/** Concatenate one tool result's text blocks. */
function textOf(result: { content: { type: string; text?: string }[] }): string {
  return result.content.filter(block => block.type === 'text').map(block => block.text ?? '').join('')
}

const uninstallFailLoud = installFailLoud(NAME)
let ctx: Context | undefined
try {
  loadEnv(NAME)
  ctx = await boot(NAME, resolveConfigPath(configPath, undefined))
  const result = await runFixtureTurn(ctx, {
    task: taskParts.join(' '),
    onEvent: (sessionId: string, event: SessionEvent) => {
      process.stdout.write(`${JSON.stringify({ type: 'session_event', sessionId, event })}\n`)
    },
  })
  process.stdout.write(`${JSON.stringify(result)}\n`)

  // Phase-3 optimize round: one real background job through the composed
  // jobs registry and the same kernel path. The driver owns the pacing, so
  // no completion-notice lane is involved (the job has no owner agent).
  const optimize = await ctx.tools.execute({
    signal: new AbortController().signal,
    callId: ToolCallId('quant-optimize-start'),
    name: 'quant_optimize_params',
    arguments: { symbol: '000001', bars: 80, top_n: 5 },
  })
  const startText = textOf(optimize as never)
  const envelope = (optimize as unknown as { value: { code: number; data: { job_id: string; combos: number } } }).value
  let jobText = ''
  const deadline = Date.now() + 30_000
  while (Date.now() < deadline) {
    const read = await ctx.tools.execute({
      signal: new AbortController().signal,
      callId: ToolCallId('quant-optimize-read'),
      name: 'job_output',
      arguments: { job_id: envelope.data.job_id },
    })
    jobText = textOf(read as never)
    if (jobText.includes('[status: completed')) break
    await new Promise(resolve => setTimeout(resolve, 50))
  }

  // The grid-cap red line on the same tool, through the real gate.
  let deniedText = ''
  try {
    const denied = await ctx.tools.execute({
      signal: new AbortController().signal,
      callId: ToolCallId('quant-optimize-deny'),
      name: 'quant_optimize_params',
      arguments: { symbol: '000001', bars: 9999 },
    })
    deniedText = textOf(denied as never)
  } catch (error: unknown) {
    deniedText = error instanceof Error ? error.message : String(error)
  }

  process.stdout.write(`${JSON.stringify({
    type: 'quant-optimize-check',
    code: envelope.code,
    jobId: envelope.data.job_id,
    combos: envelope.data.combos,
    startText,
    jobText,
    deniedText,
  })}\n`)

  // Phase-3 walk-forward round: one real background job that splits the
  // fetched bars, runs the grid on the train leg, picks the best, and runs
  // one backtest on the test leg — collected through job_output.
  const walkForward = await ctx.tools.execute({
    signal: new AbortController().signal,
    callId: ToolCallId('quant-walk-forward-start'),
    name: 'quant_walk_forward',
    arguments: { symbol: '000001', bars: 250, top_n: 5 },
  })
  const wfStartText = textOf(walkForward as never)
  const wfEnvelope = (walkForward as unknown as { value: { code: number; data: { job_id: string; combos: number; train_ratio: number } } }).value
  let wfJobText = ''
  const wfDeadline = Date.now() + 30_000
  while (Date.now() < wfDeadline) {
    const read = await ctx.tools.execute({
      signal: new AbortController().signal,
      callId: ToolCallId('quant-walk-forward-read'),
      name: 'job_output',
      arguments: { job_id: wfEnvelope.data.job_id },
    })
    wfJobText = textOf(read as never)
    if (wfJobText.includes('[status: completed')) break
    await new Promise(resolve => setTimeout(resolve, 50))
  }

  // The train-ratio red line on the same tool, through the real gate.
  let wfDeniedText = ''
  try {
    const denied = await ctx.tools.execute({
      signal: new AbortController().signal,
      callId: ToolCallId('quant-walk-forward-deny'),
      name: 'quant_walk_forward',
      arguments: { symbol: '000001', train_ratio: 0.3 },
    })
    wfDeniedText = textOf(denied as never)
  } catch (error: unknown) {
    wfDeniedText = error instanceof Error ? error.message : String(error)
  }

  process.stdout.write(`${JSON.stringify({
    type: 'quant-walk-forward-check',
    code: wfEnvelope.code,
    jobId: wfEnvelope.data.job_id,
    combos: wfEnvelope.data.combos,
    trainRatio: wfEnvelope.data.train_ratio,
    startText: wfStartText,
    jobText: wfJobText,
    deniedText: wfDeniedText,
  })}\n`)

  // Phase-4/5 cross-sectional IC round: one real background job over a
  // synthetic two-symbol panel through the composed jobs registry and the
  // cross_section_ic kernel op, collected through job_output.
  const crossIC = await ctx.tools.execute({
    signal: new AbortController().signal,
    callId: ToolCallId('quant-cross-ic-start'),
    name: 'quant_factor_cross_ic',
    arguments: { symbols: ['000001', '600519'], bars: 120, horizon: 5, ic_windows: 2 },
  })
  const icStartText = textOf(crossIC as never)
  const icEnvelope = (crossIC as unknown as { value: { code: number; data: { job_id: string; symbols: string[]; horizon: number } } }).value
  let icJobText = ''
  const icDeadline = Date.now() + 30_000
  while (Date.now() < icDeadline) {
    const read = await ctx.tools.execute({
      signal: new AbortController().signal,
      callId: ToolCallId('quant-cross-ic-read'),
      name: 'job_output',
      arguments: { job_id: icEnvelope.data.job_id },
    })
    icJobText = textOf(read as never)
    if (icJobText.includes('[status: completed')) break
    await new Promise(resolve => setTimeout(resolve, 50))
  }

  // The panel-cap red line on the same tool, through the real gate.
  let icDeniedText = ''
  try {
    const denied = await ctx.tools.execute({
      signal: new AbortController().signal,
      callId: ToolCallId('quant-cross-ic-deny'),
      name: 'quant_factor_cross_ic',
      arguments: { symbols: ['000001'], bars: 120 },
    })
    icDeniedText = textOf(denied as never)
  } catch (error: unknown) {
    icDeniedText = error instanceof Error ? error.message : String(error)
  }

  // The snapshot lifecycle read: the persisted results of the rounds above.
  const snapshotList = await ctx.tools.execute({
    signal: new AbortController().signal,
    callId: ToolCallId('quant-snapshot-list'),
    name: 'quant_list_snapshots',
    arguments: {},
  })
  const snapshotListText = textOf(snapshotList as never)

  process.stdout.write(`${JSON.stringify({
    type: 'quant-cross-ic-check',
    code: icEnvelope.code,
    jobId: icEnvelope.data.job_id,
    symbols: icEnvelope.data.symbols,
    horizon: icEnvelope.data.horizon,
    startText: icStartText,
    jobText: icJobText,
    deniedText: icDeniedText,
    snapshotListText,
  })}\n`)
} catch (error: unknown) {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`)
  process.exitCode = 1
} finally {
  await ctx?.fiber.dispose()
  uninstallFailLoud()
}
