/**
 * Trace export: OpenTelemetry GenAI semantic-convention compatible spans.
 *
 * Produces a `resourceSpans` document consumable by Langfuse / LangSmith /
 * any OTel GenAI collector. One span per turn (INTERNAL), per model call
 * (CLIENT, gen_ai.* attributes with token usage) and per tool call (CLIENT,
 * with status + error code). Times come from the event log timestamps; the
 * export is read-only and never touches the session.
 *
 * Field names follow the OTel GenAI semantic conventions
 * (gen_ai.operation.name, gen_ai.request.model, gen_ai.usage.input_tokens,
 * gen_ai.usage.output_tokens).
 *
 * @module dsh-trajectory-debug-host/trace-export
 */

import type { DebugEvent, PerfSnapshot } from 'dsh-trajectory-debug'
import { analyzePerf } from './perf-analyzer.ts'

export interface TraceSpan {
  name: string
  kind: 'INTERNAL' | 'CLIENT'
  startTimeUnixNano: string
  endTimeUnixNano: string
  parentSpanId?: string
  attributes: Record<string, string | number | boolean>
}

export interface TraceDocument {
  readonly resourceSpans: ReadonlyArray<{
    readonly resource: { readonly attributes: Record<string, string> }
    readonly scopeSpans: ReadonlyArray<{
      readonly scope: { readonly name: string }
      readonly spans: readonly TraceSpan[]
    }>
  }>
  readonly sessionId: string
  readonly summary: PerfSnapshot
}

const NS_PER_MS = 1_000_000

function nano(time: number): string {
  return String(Math.round(time * NS_PER_MS))
}

/** Build the trace document for one session's event log. */
export function buildTrace(events: readonly DebugEvent[], sessionId: string): TraceDocument {
  const spans: TraceSpan[] = []
  const openTurns = new Map<number, { span: TraceSpan; modelSpans: TraceSpan[]; toolSpans: TraceSpan[] }>()
  // callId → { time, name } so the result span can carry the real tool name.
  const toolStart = new Map<string, { time: number; name: string }>()
  // Events are processed in seq order; tool results belong to the current turn.
  let currentTurn = 0

  for (const event of events) {
    switch (event.type) {
      case 'turn/start': {
        currentTurn = event.turn
        const span: TraceSpan = {
          name: `turn.${event.turn}`,
          kind: 'INTERNAL',
          startTimeUnixNano: nano(event.time),
          endTimeUnixNano: nano(event.time),
          attributes: { 'dsh.turn': event.turn },
        }
        spans.push(span)
        openTurns.set(event.turn, { span, modelSpans: [], toolSpans: [] })
        break
      }
      case 'assistant/message': {
        const bucket = openTurns.get(event.turn)
        if (bucket !== undefined) {
          const span: TraceSpan = {
            name: `llm.${event.model ?? 'unknown'}`,
            kind: 'CLIENT',
            startTimeUnixNano: nano(event.time),
            endTimeUnixNano: nano(event.time),
            attributes: {
              'gen_ai.operation.name': 'chat',
              'dsh.turn': event.turn,
              'dsh.step': event.step,
              'gen_ai.usage.input_tokens': event.usage?.input ?? 0,
              'gen_ai.usage.output_tokens': event.usage?.output ?? 0,
            },
          }
          if (event.model !== undefined) span.attributes['gen_ai.request.model'] = event.model
          bucket.modelSpans.push(span)
        }
        break
      }
      case 'tool/call': {
        toolStart.set(event.callId, { time: event.time, name: event.name })
        break
      }
      case 'tool/result': {
        const entry = toolStart.get(event.callId)
        toolStart.delete(event.callId)
        const span: TraceSpan = {
          name: `tool.${entry?.name ?? event.callId}`,
          kind: 'CLIENT',
          startTimeUnixNano: nano(entry?.time ?? event.time),
          endTimeUnixNano: nano(event.time),
          attributes: {
            'gen_ai.agent.name': 'dsh-trajectory-debug',
            'dsh.tool.name': entry?.name ?? '',
            'dsh.step': event.step,
            'dsh.tool.ok': event.isError ? false : true,
          },
        }
        if (event.code !== undefined) span.attributes['dsh.tool.error.code'] = event.code
        openTurns.get(currentTurn)?.toolSpans.push(span)
        break
      }
      default:
        break
    }
  }

  // Parent linkage + close turn spans at their last child end.
  for (const [, bucket] of openTurns) {
    for (const span of [...bucket.modelSpans, ...bucket.toolSpans]) {
      span.parentSpanId = bucket.span.name
      const end = BigInt(span.endTimeUnixNano)
      const start = BigInt(bucket.span.startTimeUnixNano)
      if (end > start) bucket.span.endTimeUnixNano = span.endTimeUnixNano
    }
    spans.push(...bucket.modelSpans, ...bucket.toolSpans)
  }

  return {
    resourceSpans: [
      {
        resource: { attributes: { 'service.name': 'deepseek-harness', 'dsh.session.id': sessionId } },
        scopeSpans: [{ scope: { name: 'trajectory-debug' }, spans }],
      },
    ],
    sessionId,
    summary: analyzePerf(events, sessionId),
  }
}

/** Render the trace document as pretty JSON for export. */
export function renderTraceJson(events: readonly DebugEvent[], sessionId: string): string {
  return JSON.stringify(buildTrace(events, sessionId), null, 2)
}
