/**
 * Fork comparison engine: align two trajectories by step ordinal and produce
 * the change sets, result diffs, token/timing deltas and a human summary.
 *
 * Alignment is by step ordinal — both sides derive from the same fork root,
 * so step numbers are directly comparable. Tool calls within a step align by
 * position (the order the model emitted them).
 *
 * @module dsh-trajectory-debug-host/diff-engine
 */

import type {
  CompareResult,
  DebugEvent,
  DebugToolResult,
  ResultDiff,
  ToolChange,
  VariantId,
} from 'dsh-trajectory-debug'
import { analyzePerf } from './perf-analyzer.ts'
import { stepBoundaries, toolCallsIn, toolResultsIn } from './replay-engine.ts'

/** Deep JSON diff → list of human-readable path descriptions. */
export function jsonDiff(base: unknown, head: unknown, path = '$'): string[] {
  if (Object.is(base, head)) return []
  if (base === undefined && head !== undefined) return [`${path}: added ${describe(head)}`]
  if (head === undefined && base !== undefined) return [`${path}: removed ${describe(base)}`]
  if (base === null || head === null || typeof base !== 'object' || typeof head !== 'object') {
    return [`${path}: changed ${describe(base)} → ${describe(head)}`]
  }
  if (Array.isArray(base) && Array.isArray(head)) {
    const changes: string[] = []
    const max = Math.max(base.length, head.length)
    for (let i = 0; i < max; i += 1) {
      if (base[i] === undefined) changes.push(`${path}[${i}]: added ${describe(head[i])}`)
      else if (head[i] === undefined) changes.push(`${path}[${i}]: removed ${describe(base[i])}`)
      else changes.push(...jsonDiff(base[i], head[i], `${path}[${i}]`))
    }
    return changes
  }
  const a = base as Record<string, unknown>
  const b = head as Record<string, unknown>
  const keys = new Set([...Object.keys(a), ...Object.keys(b)])
  const changes: string[] = []
  for (const key of keys) changes.push(...jsonDiff(a[key], b[key], `${path}.${key}`))
  return changes
}

function describe(value: unknown): string {
  if (value === null) return 'null'
  if (typeof value === 'string') {
    const trimmed = value.length > 40 ? `${value.slice(0, 40)}…` : value
    return JSON.stringify(trimmed)
  }
  if (typeof value === 'object') return JSON.stringify(value).slice(0, 60)
  return String(value)
}

function previewOf(result: DebugToolResult | undefined): string {
  if (result === undefined) return ''
  if (result.contentPreview !== undefined) return result.contentPreview
  if (result.message !== undefined) return result.message
  return result.value === undefined ? '' : String(result.value)
}

export interface CompareOptions {
  base: VariantId
  head: VariantId
}

/** Compare two trajectories (both derived from one fork root). */
export function compareTrajectories(
  baseEvents: readonly DebugEvent[],
  headEvents: readonly DebugEvent[],
  opts: CompareOptions,
): CompareResult {
  const baseBoundaries = stepBoundaries(baseEvents)
  const headBoundaries = stepBoundaries(headEvents)
  const basePerf = analyzePerf(baseEvents)
  const headPerf = analyzePerf(headEvents)

  const stepsChanged: number[] = []
  const toolsChanged: ToolChange[] = []
  const resultDiffs: ResultDiff[] = []
  const maxSteps = Math.max(baseBoundaries.length, headBoundaries.length)

  for (let stepIndex = 0; stepIndex < maxSteps; stepIndex += 1) {
    const b = baseBoundaries[stepIndex]
    const h = headBoundaries[stepIndex]
    if (b === undefined || h === undefined) {
      // One side lacks this step entirely.
      if (b !== undefined || h !== undefined) stepsChanged.push(stepIndex)
      continue
    }
    const baseCalls = toolCallsIn(baseEvents, b)
    const headCalls = toolCallsIn(headEvents, h)
    const baseResults = new Map(toolResultsIn(baseEvents, b).map((r) => [r.callId, r]))
    const headResults = new Map(toolResultsIn(headEvents, h).map((r) => [r.callId, r]))

    let changed = false
    const maxCalls = Math.max(baseCalls.length, headCalls.length)
    for (let i = 0; i < maxCalls; i += 1) {
      const bc = baseCalls[i]
      const hc = headCalls[i]
      if (bc === undefined && hc !== undefined) {
        toolsChanged.push({ step: stepIndex, name: hc.name, kind: 'added', diff: [] })
        changed = true
        continue
      }
      if (bc !== undefined && hc === undefined) {
        toolsChanged.push({ step: stepIndex, name: bc.name, kind: 'removed', diff: [] })
        changed = true
        continue
      }
      if (bc === undefined || hc === undefined) continue
      if (bc.name !== hc.name) {
        toolsChanged.push({
          step: stepIndex,
          name: `${bc.name} → ${hc.name}`,
          kind: 'args-changed',
          diff: [`${bc.name} → ${hc.name}`],
        })
        changed = true
        continue
      }
      const argDiff = jsonDiff(bc.args, hc.args)
      if (argDiff.length > 0) {
        toolsChanged.push({ step: stepIndex, name: bc.name, kind: 'args-changed', diff: argDiff })
        changed = true
      }
      const br = baseResults.get(bc.callId)
      const hr = headResults.get(hc.callId)
      const basePreview = previewOf(br)
      const headPreview = previewOf(hr)
      const resultChanged = br?.isError !== hr?.isError || basePreview !== headPreview
      if (resultChanged) {
        resultDiffs.push({ step: stepIndex, callId: hc.callId, basePreview, headPreview, changed: true })
        changed = true
      }
    }
    if (changed) stepsChanged.push(stepIndex)
  }

  const tokenBase = basePerf.tokens.totalInput + basePerf.tokens.totalOutput
  const tokenHead = headPerf.tokens.totalInput + headPerf.tokens.totalOutput
  const summary = [
    `B 比 A ${headBoundaries.length > baseBoundaries.length ? `多 ${headBoundaries.length - baseBoundaries.length} 步` : headBoundaries.length < baseBoundaries.length ? `少 ${baseBoundaries.length - headBoundaries.length} 步` : '步数相同'}`,
    toolsChanged.length === 0 ? '工具调用无变化' : `工具变更 ${toolsChanged.length} 处`,
    resultDiffs.length === 0 ? '结果无差异' : `结果差异 ${resultDiffs.length} 处`,
    `Token ${tokenBase} → ${tokenHead}（${tokenHead - tokenBase >= 0 ? '+' : ''}${tokenHead - tokenBase}）`,
    `耗时 ${Math.round(basePerf.timing.llmMs + basePerf.timing.toolMs)}ms → ${Math.round(headPerf.timing.llmMs + headPerf.timing.toolMs)}ms`,
  ].join('；')

  return {
    base: opts.base,
    head: opts.head,
    baseStepCount: baseBoundaries.length,
    headStepCount: headBoundaries.length,
    stepsChanged,
    toolsChanged,
    resultDiffs,
    tokens: {
      base: { input: basePerf.tokens.totalInput, output: basePerf.tokens.totalOutput },
      head: { input: headPerf.tokens.totalInput, output: headPerf.tokens.totalOutput },
    },
    timing: {
      base: Math.round(basePerf.timing.llmMs + basePerf.timing.toolMs),
      head: Math.round(headPerf.timing.llmMs + headPerf.timing.toolMs),
      llmBase: Math.round(basePerf.timing.llmMs),
      llmHead: Math.round(headPerf.timing.llmMs),
    },
    summary,
  }
}
