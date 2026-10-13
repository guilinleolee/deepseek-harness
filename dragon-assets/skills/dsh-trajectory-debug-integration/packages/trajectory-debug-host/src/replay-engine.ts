/**
 * Deterministic replay engine.
 *
 * Pure functions over the plugin's `DebugEvent` log model: step boundaries,
 * trajectory rows (waterfall data), the model view at a boundary, and step
 * context for single-step replay. **No LLM calls, no tool execution** — the
 * engine only projects recorded events, so replay is zero-token and side
 * effect free by construction.
 *
 * The same fold primitives back the projection units (`projections.ts`) so
 * the registry drive and the on-demand engine can never disagree.
 *
 * @module dsh-trajectory-debug-host/replay-engine
 */

import type {
  CallId,
  DebugAssistantMessage,
  DebugEvent,
  DebugMessage,
  DebugToolCall,
  DebugToolResult,
  SessionId,
  StepContext,
  ToolCallRecord,
  ToolResultRecord,
  TrajectoryFilter,
  TrajectoryRow,
  TrajectoryQuery,
  TurnRecord,
  VariantId,
} from 'dsh-trajectory-debug'

/* ─────────────────────────── step boundaries ─────────────────────────── */

export interface StepBoundary {
  step: number
  turn: number
  startSeq: number
  endSeq: number
}

/** Index of every step: (startSeq..endSeq) inclusive, ordered by seq. */
export function stepBoundaries(events: readonly DebugEvent[]): StepBoundary[] {
  const boundaries: StepBoundary[] = []
  let current: StepBoundary | null = null
  for (const event of events) {
    if (event.type === 'step/start') {
      if (current !== null) boundaries.push(current)
      current = { step: event.step, turn: event.turn, startSeq: event.seq, endSeq: event.seq }
    } else if (current !== null) {
      current.endSeq = event.seq
    }
  }
  if (current !== null) boundaries.push(current)
  return boundaries
}

/** The step boundary that CONTAINS `seq` (or is exactly `seq`), if any. */
export function resolveStepBoundary(
  events: readonly DebugEvent[],
  seq: number,
): StepBoundary | undefined {
  const boundaries = stepBoundaries(events)
  // binary search: last boundary with startSeq <= seq
  let lo = 0
  let hi = boundaries.length - 1
  let found: StepBoundary | undefined
  while (lo <= hi) {
    const mid = (lo + hi) >> 1
    const b = boundaries[mid]
    if (!b) break
    if (b.startSeq <= seq) {
      found = b
      lo = mid + 1
    } else {
      hi = mid - 1
    }
  }
  return found
}

/* ─────────────────────────── trajectory fold ─────────────────────────── */

export interface TrajectoryFoldState {
  rows: TrajectoryRow[]
  stepCount: number
  turnCount: number
  /** open step (seq → row index) so assistant/message can finalize it. */
  openStep: { startSeq: number; rowIndex: number; turn: number; step: number; firstChunkTime?: number } | null
  /** open tool call: callId → row index + call time (JSON-safe record). */
  openCalls: Record<string, { rowIndex: number; time: number }>
  /** accumulated assistant text per step (chunk deltas). */
  textByStep: Record<number, string>
  /** accumulated reasoning per step. */
  reasoningByStep: Record<number, string>
  /** chunk usage per step. */
  usageByStep: Record<number, { input: number; output: number }>
  /** step/start time per step (for modelMs/ttft). */
  stepStartTime: Record<number, number>
  /** seen turn ends with reasons. */
  turnReasons: Record<number, NonNullable<TurnRecord['reason']>>
}

export function createTrajectoryState(): TrajectoryFoldState {
  return {
    rows: [],
    stepCount: 0,
    turnCount: 0,
    openStep: null,
    openCalls: {},
    textByStep: {},
    reasoningByStep: {},
    usageByStep: {},
    stepStartTime: {},
    turnReasons: {},
  }
}

/** Fold ONE event into the state. Unrelated events return the same state. */
export function applyTrajectory(state: TrajectoryFoldState, event: DebugEvent | null): TrajectoryFoldState {
  if (event === null) return state
  switch (event.type) {
    case 'turn/start': {
      state.rows.push({ kind: 'turn', seq: event.seq, turn: event.turn, time: event.time })
      return state
    }
    case 'turn/end': {
      state.turnReasons[event.turn] = event.reason
      const row = state.rows.findLast((r) => r.kind === 'turn' && r.turn === event.turn)
      if (row && row.kind === 'turn') {
        row.reason = event.reason
        row.durationMs = Math.max(0, event.time - row.time)
      }
      return state
    }
    case 'step/start': {
      state.stepCount += 1
      state.stepStartTime[event.step] = event.time
      state.rows.push({
        kind: 'step',
        seq: event.seq,
        turn: event.turn,
        step: event.step,
        status: 'running',
      })
      state.openStep = { startSeq: event.seq, rowIndex: state.rows.length - 1, turn: event.turn, step: event.step }
      return state
    }
    case 'step/end': {
      finalizeStep(state, event.time)
      state.openStep = null
      return state
    }
    case 'assistant/chunk': {
      if (event.kind === 'text') {
        const text = (state.textByStep[event.step] ?? '') + event.text
        state.textByStep[event.step] = text
      } else if (event.kind === 'reasoning') {
        const text = (state.reasoningByStep[event.step] ?? '') + (event.text ?? '')
        state.reasoningByStep[event.step] = text
      } else if (event.kind === 'usage') {
        const u = state.usageByStep[event.step] ?? { input: 0, output: 0 }
        state.usageByStep[event.step] = {
          input: u.input + (event.usage?.input ?? 0),
          output: u.output + (event.usage?.output ?? 0),
        }
      }
      if (state.openStep && state.openStep.step === event.step && state.openStep.firstChunkTime === undefined) {
        state.openStep.firstChunkTime = event.time
      }
      return state
    }
    case 'assistant/message': {
      const usage = event.usage
      if (usage) {
        state.usageByStep[event.step] = { input: usage.input, output: usage.output }
      }
      const row = state.rows[state.openStep?.rowIndex ?? -1]
      if (row && row.kind === 'step' && row.step === event.step) {
        row.messageSeq = event.seq
        row.status = 'ok'
        row.modelMs = Math.max(0, event.time - (state.stepStartTime[event.step] ?? event.time))
      }
      if (state.openStep) state.openStep.firstChunkTime ??= event.time
      return state
    }
    case 'tool/call': {
      state.rows.push({
        kind: 'tool',
        seq: event.seq,
        step: event.step,
        callId: event.callId,
        name: event.name,
        args: event.args,
        argsTruncated: event.argsTruncated,
        status: 'pending',
      })
      state.openCalls[event.callId] = { rowIndex: state.rows.length - 1, time: event.time }
      return state
    }
    case 'tool/result': {
      const entry = state.openCalls[event.callId]
      delete state.openCalls[event.callId]
      if (entry === undefined) return state
      const row = state.rows[entry.rowIndex]
      if (row && row.kind === 'tool' && row.callId === event.callId) {
        row.status = event.isError ? 'error' : 'ok'
        row.durationMs = Math.max(0, event.time - entry.time)
        row.result = toResultRecord(event)
      }
      return state
    }
    default:
      return state
  }
}

/** Finalize open step/turn when the log ends mid-step (crash recovery view). */
export function finalizeTrajectory(state: TrajectoryFoldState): { rows: TrajectoryRow[]; stepCount: number; turnCount: number } {
  if (state.openStep !== null) finalizeStep(state, undefined)
  let turns = 0
  for (const row of state.rows) {
    if (row.kind === 'turn' && row.reason !== undefined) turns += 1
  }
  state.turnCount = turns
  return { rows: state.rows, stepCount: state.stepCount, turnCount: turns }
}

function finalizeStep(state: TrajectoryFoldState, endTime: number | undefined): void {
  const open = state.openStep
  if (open === null) return
  const row = state.rows[open.rowIndex]
  if (row && row.kind === 'step') {
    const text = state.textByStep[open.step]
    const reasoning = state.reasoningByStep[open.step]
    const usage = state.usageByStep[open.step]
    if (text !== undefined || reasoning !== undefined || usage !== undefined) {
      row.status = 'ok'
    }
    if (reasoning !== undefined) row.reasoningSnippet = reasoning.slice(0, 200)
    if (usage) {
      row.inputTokens = usage.input
      row.outputTokens = usage.output
    }
    const start = state.stepStartTime[open.step]
    if (start !== undefined && endTime !== undefined) {
      row.modelMs ??= Math.max(0, endTime - start)
    }
    if (start !== undefined && open.firstChunkTime !== undefined) {
      row.ttftMs = Math.max(0, open.firstChunkTime - start)
      const end = endTime ?? open.firstChunkTime
      row.decodeMs = Math.max(0, end - open.firstChunkTime)
    }
  }
}

/** Build the waterfall data: fold whole log → filter → window. */
export function buildTrajectoryPage(
  events: readonly DebugEvent[],
  query: TrajectoryQuery,
): { rows: TrajectoryRow[]; stepCount: number; turnCount: number } {
  const state = createTrajectoryState()
  for (const event of events) applyTrajectory(state, event)
  const { rows, stepCount, turnCount } = finalizeTrajectory(state)
  const filter = query.filter
  const filtered = filter === undefined ? rows : rows.filter((row) => matchesFilter(row, filter))
  const offset = Math.max(0, query.window.offset)
  return {
    rows: filtered.slice(offset, offset + query.window.limit),
    stepCount,
    turnCount,
  }
}

function matchesFilter(row: TrajectoryRow, filter: TrajectoryFilter): boolean {
  if (filter.seqMin !== undefined && row.seq < filter.seqMin) return false
  if (filter.seqMax !== undefined && row.seq > filter.seqMax) return false
  // Tool-targeting filters (name / error code / durations) narrow the ledger
  // to tool rows only; turn/step rows are excluded when any is set.
  const toolOnly =
    filter.toolName !== undefined ||
    filter.errorCode !== undefined ||
    filter.minDurationMs !== undefined ||
    filter.maxDurationMs !== undefined
  if (toolOnly && row.kind !== 'tool') return false
  switch (row.kind) {
    case 'tool':
      if (filter.toolName !== undefined && row.name !== filter.toolName) return false
      if (filter.status === 'error' && row.status !== 'error') return false
      if (filter.minDurationMs !== undefined && (row.durationMs ?? 0) < filter.minDurationMs) return false
      if (filter.maxDurationMs !== undefined && (row.durationMs ?? Infinity) > filter.maxDurationMs) return false
      if (filter.errorCode !== undefined && row.result?.code !== filter.errorCode) return false
      return true
    case 'step':
      if (filter.status !== undefined && filter.status !== 'error' && row.status !== filter.status) return false
      return true
    default:
      return true
  }
}

/* ─────────────────────────── model view ─────────────────────────── */

/** The model's message history at a boundary (seq < `beforeSeq`). */
export function deriveModelView(events: readonly DebugEvent[], beforeSeq: number): DebugMessage[] {
  const textByStep: Record<number, string> = {}
  for (const event of events) {
    if (event.type === 'assistant/chunk' && event.kind === 'text') {
      textByStep[event.step] = (textByStep[event.step] ?? '') + event.text
    }
  }
  const view: DebugMessage[] = []
  for (const event of events) {
    if (event.seq >= beforeSeq) break
    switch (event.type) {
      case 'user/message':
        view.push({ role: 'user', content: event.content })
        break
      case 'assistant/message':
        view.push({ role: 'assistant', content: textByStep[event.step] ?? '' })
        break
      case 'tool/call':
        view.push({ role: 'tool', content: '', toolCall: { name: event.name, args: event.args, callId: event.callId } })
        break
      case 'tool/result':
        view.push({
          role: 'tool',
          content: event.contentPreview ?? event.message ?? '',
          toolResult: { callId: event.callId, isError: event.isError, preview: event.contentPreview ?? event.message ?? '' },
        })
        break
      default:
        break
    }
  }
  return view
}

/* ─────────────────────────── step context ─────────────────────────── */

export function toolCallsIn(events: readonly DebugEvent[], boundary: StepBoundary): DebugToolCall[] {
  const out: DebugToolCall[] = []
  for (const event of events) {
    if (event.seq < boundary.startSeq) continue
    if (event.seq > boundary.endSeq) break
    if (event.type === 'tool/call') out.push(event)
  }
  return out
}

export function toolResultsIn(events: readonly DebugEvent[], boundary: StepBoundary): DebugToolResult[] {
  const out: DebugToolResult[] = []
  for (const event of events) {
    if (event.seq < boundary.startSeq) continue
    if (event.seq > boundary.endSeq) break
    if (event.type === 'tool/result') out.push(event)
  }
  return out
}

/** Assemble the step context at a 0-based step index. */
export function stepContextAt(
  events: readonly DebugEvent[],
  sessionId: SessionId,
  stepIndex: number,
  variantId?: VariantId,
): StepContext {
  const boundaries = stepBoundaries(events)
  const boundary = boundaries[stepIndex]
  if (boundary === undefined) throw new RangeError(`step index ${stepIndex} out of range (${boundaries.length} steps)`)
  const modelView = deriveModelView(events, boundary.startSeq)
  const textByStep: Record<number, string> = {}
  for (const event of events) {
    if (event.type === 'assistant/chunk' && event.kind === 'text') {
      textByStep[event.step] = (textByStep[event.step] ?? '') + event.text
    }
  }
  const assistantMessage = events.find(
    (e): e is DebugAssistantMessage =>
      e.type === 'assistant/message' && e.seq >= boundary.startSeq && e.seq <= boundary.endSeq,
  )
  const calls = toolCallsIn(events, boundary)
  const results = new Map(toolResultsIn(events, boundary).map((r) => [r.callId, r]))
  const tools: ToolCallRecord[] = calls.map((call) => {
    const result = results.get(call.callId)
    return {
      kind: 'tool',
      seq: call.seq,
      step: call.step,
      callId: call.callId,
      name: call.name,
      args: call.args,
      argsTruncated: call.argsTruncated,
      status: result === undefined ? 'pending' : result.isError ? 'error' : 'ok',
      durationMs: result === undefined ? undefined : Math.max(0, result.time - call.time),
      result: result === undefined ? undefined : toResultRecord(result),
    }
  })
  const nextBoundary = boundaries[stepIndex + 1]
  const nextSeq = nextBoundary === undefined ? (events.at(-1)?.seq ?? 0) + 1 : nextBoundary.startSeq
  return {
    seq: boundary.startSeq,
    modelView,
    action: {
      assistant:
        assistantMessage === undefined
          ? undefined
          : { provider: assistantMessage.provider, model: assistantMessage.model, text: textByStep[assistantMessage.step] ?? '' },
      tools,
    },
    nextCursor: {
      sessionId,
      variantId,
      nextSeq,
      stepIndex: stepIndex + 1,
    },
  }
}

/* ─────────────────────────── helpers ─────────────────────────── */

function toResultRecord(result: DebugToolResult): ToolResultRecord {
  return {
    isError: result.isError,
    code: result.code,
    message: result.message,
    value: result.value,
    contentPreview: result.contentPreview,
    spillLocator: result.spillLocator,
  }
}
