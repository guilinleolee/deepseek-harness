/**
 * Trajectory Debug Workbench — wire types and Service Definition.
 *
 * The engines of this plugin family operate on the {@link DebugEvent} log
 * model: a **minimal, version-pinned mirror** of the DSH `SessionEvent`
 * vocabulary that the engines actually consume. Keeping the engines DSH-free
 * makes them churn-resistant (DSH is in developer preview with breaking
 * changes) and unit-testable without a harness runtime. The host provider
 * adapts real `Session` events into this model at the boundary
 * (`dsh-trajectory-debug-host/src/adapt-event.ts`).
 *
 * All wire payloads are plain JSON (no classes, no functions) so they can
 * cross the typert Remote boundary and render directly in the browser.
 *
 * @module dsh-trajectory-debug
 */

/* ─────────────────────────── branding ─────────────────────────── */

/** Local branded-id helper (swap for `@deepseek-ai/dsh-brand` when pinned). */
export type Brand<T extends string> = string & { readonly __brand?: T }

/** A session's durable identity. */
export type SessionId = Brand<'SessionId'>
/** An event's sequence number within its session log (0-based, contiguous). */
export type EventSeq = number & { readonly __brand?: 'EventSeq' }
/** A tool call's identity within a step. */
export type CallId = Brand<'CallId'>
/** A debug breakpoint's identity (sidecar-scoped). */
export type BreakpointId = Brand<'BreakpointId'>
/** A fork-variant's identity. */
export type VariantId = Brand<'VariantId'>
/** A re-run experiment's identity (sidecar-scoped). */
export type ExperimentId = Brand<'ExperimentId'>

/* ─────────────────────────── JSON ─────────────────────────── */

/** Lossless JSON value (mirrors DSH `JsonValue`). */
export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue }

/** Token usage reported by a provider. */
export interface TokenUsage {
  input: number
  output: number
  total?: number
}

/* ─────────────────────── event vocabulary ─────────────────────── */

/**
 * The minimal event log model this plugin family folds over.
 * `seq` is contiguous; `time` is the wall-clock epoch ms of the event.
 */
export interface DebugEventBase {
  readonly seq: EventSeq
  /** Epoch ms. May be 0 when the source event carried no timestamp. */
  readonly time: number
}

export type TurnEndReason =
  | 'completed'
  | 'aborted'
  | 'blocked'
  | 'error'
  | 'max-tokens'
  | 'interrupted'

export interface DebugTurnStart extends DebugEventBase {
  readonly type: 'turn/start'
  readonly turn: number
}

export interface DebugTurnEnd extends DebugEventBase {
  readonly type: 'turn/end'
  readonly turn: number
  readonly reason: TurnEndReason
  readonly error?: { name: string; code?: string; message: string }
}

export interface DebugStepStart extends DebugEventBase {
  readonly type: 'step/start'
  readonly turn: number
  readonly step: number
}

export interface DebugStepEnd extends DebugEventBase {
  readonly type: 'step/end'
  readonly turn: number
  readonly step: number
}

/** A human prompt, a synthetic injection, or an entered goal round. */
export interface DebugUserMessage extends DebugEventBase {
  readonly type: 'user/message'
  readonly turn?: number
  readonly content: string
  /** source discriminator: direct | injected | goal-round | tool-feedback */
  readonly source?: string
}

/** A model-request retry inside a step (log-only, non-surface). */
export interface DebugLlmRetry extends DebugEventBase {
  readonly type: 'llm/retry'
  readonly turn: number
  readonly step: number
  readonly reason?: string
}

export interface DebugAssistantChunk extends DebugEventBase {
  readonly type: 'assistant/chunk'
  readonly step: number
  readonly kind: 'text' | 'reasoning' | 'tool-call' | 'usage'
  /** Delta text for text/reasoning chunks. */
  readonly text?: string
  readonly usage?: TokenUsage
}

export interface DebugAssistantMessage extends DebugEventBase {
  readonly type: 'assistant/message'
  readonly turn: number
  readonly step: number
  readonly usage?: TokenUsage
  readonly provider?: string
  readonly model?: string
}

export interface DebugToolCall extends DebugEventBase {
  readonly type: 'tool/call'
  readonly step: number
  readonly callId: CallId
  readonly name: string
  readonly args: JsonValue
  readonly argsTruncated?: boolean
}

export interface DebugToolResult extends DebugEventBase {
  readonly type: 'tool/result'
  readonly step: number
  readonly callId: CallId
  readonly isError: boolean
  /** Stable error code for classification (FsErrorCode, WebError, …). */
  readonly code?: string
  readonly message?: string
  /** Canonical success value (truncated/redacted preview). */
  readonly value?: JsonValue
  readonly contentPreview?: string
  /** Spill locator when the full content was persisted out of line. */
  readonly spillLocator?: string
}

/** The union of events the engines consume. Unknown events are skipped. */
export type DebugEvent =
  | DebugTurnStart
  | DebugTurnEnd
  | DebugStepStart
  | DebugStepEnd
  | DebugUserMessage
  | DebugLlmRetry
  | DebugAssistantChunk
  | DebugAssistantMessage
  | DebugToolCall
  | DebugToolResult

/** Read-side session model the seam operates on (adapted from a DSH Session). */
export interface DebugSession {
  readonly id: SessionId
  readonly events: readonly DebugEvent[]
}

/* ─────────────────────── trajectory rows ─────────────────────── */

export interface TurnRecord {
  kind: 'turn'
  seq: EventSeq
  turn: number
  reason?: TurnEndReason
  time: number
  durationMs?: number
}

export type StepStatus = 'running' | 'ok' | 'error' | 'aborted' | 'max-tokens'

export interface StepRecord {
  kind: 'step'
  seq: EventSeq
  turn: number
  step: number
  status: StepStatus
  modelMs?: number
  ttftMs?: number
  decodeMs?: number
  inputTokens?: number
  outputTokens?: number
  reasoningSnippet?: string
  messageSeq?: EventSeq
}

export interface ToolCallRecord {
  kind: 'tool'
  seq: EventSeq
  step: number
  callId: CallId
  name: string
  args: JsonValue
  argsTruncated?: boolean
  durationMs?: number
  status: 'ok' | 'error' | 'pending' | 'blocked'
  result?: ToolResultRecord
}

export interface ToolResultRecord {
  isError: boolean
  code?: string
  message?: string
  value?: JsonValue
  contentPreview?: string
  spillLocator?: string
}

export type TrajectoryRow = TurnRecord | StepRecord | ToolCallRecord

export interface TrajectoryPage {
  readonly sessionId: SessionId
  readonly asOfSeq: EventSeq
  readonly rows: readonly TrajectoryRow[]
  /** Total step count in the log (for the overview bar). */
  readonly stepCount: number
  readonly turnCount: number
}

/** Filter grammar the browser sends; parsed host-side. */
export interface TrajectoryFilter {
  readonly toolName?: string
  readonly status?: StepStatus | 'error'
  readonly minDurationMs?: number
  readonly maxDurationMs?: number
  readonly errorCode?: string
  readonly seqMin?: number
  readonly seqMax?: number
}

export interface TrajectoryQuery {
  readonly window: { offset: number; limit: number }
  readonly filter?: TrajectoryFilter
}

/* ─────────────────────── breakpoints ─────────────────────── */

export type BreakpointSpec =
  | { readonly at: 'step'; readonly seq: EventSeq }
  | { readonly at: 'turn'; readonly turn: number }
  | { readonly at: 'tool'; readonly callId: CallId; readonly mode: 'pre' | 'post' }

export interface Breakpoint {
  readonly id: BreakpointId
  readonly sessionId: SessionId
  readonly spec: BreakpointSpec
  readonly enabled: boolean
}

export type PauseCause = 'user' | 'timeout' | 'cancelled'

/* ─────────────────────── replay ─────────────────────── */

export interface ReplayCursor {
  readonly sessionId: SessionId
  readonly variantId?: VariantId
  /** Next event seq to consume (the current step's start). */
  readonly nextSeq: EventSeq
  /** 0-based step index. */
  readonly stepIndex: number
}

/** Model-visible message at a boundary (mirrors DSH `Message`). */
export interface DebugMessage {
  readonly role: 'user' | 'assistant' | 'tool'
  readonly content: string
  readonly toolCall?: { name: string; args: JsonValue; callId?: CallId }
  readonly toolResult?: { callId?: CallId; isError: boolean; preview: string }
}

export interface StepContext {
  readonly seq: EventSeq
  /** The model view at this boundary: everything the model had seen. */
  readonly modelView: readonly DebugMessage[]
  /** The step's own action: the assistant message and its tool calls. */
  readonly action: {
    readonly assistant?: { provider?: string; model?: string; text: string }
    readonly tools: readonly ToolCallRecord[]
  }
  readonly nextCursor: ReplayCursor
}

export interface ReplayFrame {
  readonly cursor: ReplayCursor
  readonly context?: StepContext
  readonly status: 'stepped' | 'started' | 'finished' | 'stale' | 'interrupted'
}

/* ─────────────────────── variants & compare ─────────────────────── */

export type VariantStatus = 'frozen' | 'live' | 'failed'

export interface Variant {
  readonly id: VariantId
  readonly sessionId: SessionId
  readonly parentSessionId?: SessionId
  readonly boundarySeq: EventSeq
  readonly label: string
  readonly status: VariantStatus
  readonly createdAt: number
  /** Set when live-resume failed (status 'failed'). */
  readonly error?: string
}

export interface ForkRequest {
  readonly boundarySeq: EventSeq
  readonly label?: string
  /** When set, the fork resumes as a live agent with this instruction. */
  readonly instruction?: string
  /** Cascade strategy for later inputs after the boundary (live resume):
   * 'truncate' (default) drops them; 'preserve' replays every later
   * user/message into the new branch in order. */
  readonly cascade?: 'truncate' | 'preserve'
}

export interface ToolChange {
  readonly step: number
  readonly name: string
  readonly kind: 'added' | 'removed' | 'args-changed' | 'result-changed'
  readonly diff: readonly string[]
}

export interface ResultDiff {
  readonly step: number
  readonly callId: CallId
  readonly basePreview: string
  readonly headPreview: string
  readonly changed: boolean
}

export interface CompareResult {
  readonly base: VariantId
  readonly head: VariantId
  readonly baseStepCount: number
  readonly headStepCount: number
  readonly stepsChanged: readonly number[]
  readonly toolsChanged: readonly ToolChange[]
  readonly resultDiffs: readonly ResultDiff[]
  readonly tokens: {
    readonly base: TokenUsage
    readonly head: TokenUsage
  }
  readonly timing: {
    readonly base: number
    readonly head: number
    readonly llmBase: number
    readonly llmHead: number
  }
  readonly summary: string
}

/* ─────────────────────── performance ─────────────────────── */

export interface ToolPerf {
  readonly calls: number
  readonly ok: number
  readonly failed: number
  readonly ms: { avg: number; p50: number; p90: number; p95: number }
}

export type FailureCategory =
  | { readonly kind: 'tool'; readonly code: string }
  | { readonly kind: 'turn'; readonly reason: TurnEndReason }
  | { readonly kind: 'sandbox'; readonly code: string }
  | { readonly kind: 'timeout' }
  | { readonly kind: 'aborted' }

export interface FailureAgg {
  readonly category: FailureCategory
  readonly count: number
  readonly sampleSeqs: readonly EventSeq[]
}

export interface PerfSnapshot {
  readonly sessionId: SessionId
  readonly asOfSeq: EventSeq
  readonly tools: Record<string, ToolPerf>
  readonly failures: readonly FailureAgg[]
  readonly tokens: {
    readonly totalInput: number
    readonly totalOutput: number
    readonly byStep: readonly number[]
    readonly byToolType: Record<string, number>
  }
  /** Estimated spend (optional; only when a price table is configured). */
  readonly cost?: {
    readonly input: number
    readonly output: number
    readonly total: number
    readonly currency: string
  }
  readonly timing: {
    readonly llmMs: number
    readonly ttftMs: number
    readonly ttftSteps: number
    readonly decodeMs: number
    readonly decodeTokens: number
    readonly toolMs: number
  }
  readonly turns: {
    readonly count: number
    readonly steps: number
    readonly maxTokensEnds: number
    readonly retries: number
  }
}

/* ─────────────────────── misc ─────────────────────── */

export type ExportFormat = 'json' | 'csv' | 'markdown' | 'trace'

export interface ExportPayload {
  readonly sessionId: SessionId
  readonly format: ExportFormat
  readonly content: string
}

/** An executed re-run experiment (sidecar record, never in the session log). */
export interface ExperimentRecord {
  id: ExperimentId
  sessionId: SessionId
  seq: EventSeq
  toolName: string
  oldArgs: JsonValue
  newArgs: JsonValue
  oldResult?: ToolResultRecord
  newResult?: ToolResultRecord
  diff: readonly string[]
  ts: number
}

/** Result of {@link TrajectoryDebugService.rerunTool}. */
export type InterventionResult = ExperimentRecord
