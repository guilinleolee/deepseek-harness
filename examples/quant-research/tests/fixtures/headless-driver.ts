#!/usr/bin/env node
/** Snapshot-only Loader driver: stream one fixture turn as canonical JSONL. */

import type { Context } from '@deepseek-ai/cordis'
import { boot, installFailLoud, loadEnv, resolveConfigPath } from '@deepseek-ai/dsh-app-boot'
import { runFixtureTurn } from '@deepseek-ai/dsh-loader-smoke'
import { CallId } from '@deepseek-ai/dsh-llm'
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
    callId: CallId('quant-optimize-start'),
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
      callId: CallId('quant-optimize-read'),
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
      callId: CallId('quant-optimize-deny'),
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
} catch (error: unknown) {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`)
  process.exitCode = 1
} finally {
  await ctx?.fiber.dispose()
  uninstallFailLoud()
}
