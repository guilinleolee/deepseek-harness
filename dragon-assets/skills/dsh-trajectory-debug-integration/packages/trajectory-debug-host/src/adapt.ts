/**
 * Adapter: DSH `Session`/`SessionEvent` → this plugin's `DebugSession`/`DebugEvent`.
 *
 * The adapter is the ONLY place that touches DSH's real event vocabulary. It
 * is deliberately defensive: DSH is in developer preview and its event data
 * shapes may drift, so each mapping narrows with safe fallbacks and unknown
 * or unmapped events are dropped (`null`). The engines downstream never see
 * raw DSH events, which keeps them stable and unit-testable.
 *
 * @module dsh-trajectory-debug-host/adapt
 */

import type { Session, SessionEvent, SessionId } from '@deepseek-ai/dsh-session'
import type {
  CallId,
  DebugEvent,
  DebugSession,
  JsonValue,
  TokenUsage,
  TurnEndReason,
} from 'dsh-trajectory-debug'

/** Map one DSH event to our model, or `null` when the plugin ignores it. */
export function adaptEvent(event: SessionEvent): DebugEvent | null {
  const base = { seq: event.seq as DebugEvent['seq'], time: event.time }
  switch (event.type) {
    case 'turn/start': {
      const d = event.data as { turn?: number }
      return { ...base, type: 'turn/start', turn: d.turn ?? 0 }
    }
    case 'turn/end': {
      const d = event.data as {
        turn?: number
        reason?: { kind?: string }
        error?: { name?: string; code?: string; message?: string }
      }
      return {
        ...base,
        type: 'turn/end',
        turn: d.turn ?? 0,
        reason: normalizeTurnEndReason(d.reason?.kind),
        error: d.error ? { name: d.error.name ?? 'Unknown', code: d.error.code, message: d.error.message ?? '' } : undefined,
      }
    }
    case 'step/start': {
      const d = event.data as { turn?: number; step?: number }
      return { ...base, type: 'step/start', turn: d.turn ?? 0, step: d.step ?? 0 }
    }
    case 'step/end': {
      const d = event.data as { turn?: number; step?: number }
      return { ...base, type: 'step/end', turn: d.turn ?? 0, step: d.step ?? 0 }
    }
    case 'user/message': {
      const d = event.data as { turn?: number; content?: unknown; source?: { kind?: string } | string }
      return {
        ...base,
        type: 'user/message',
        turn: d.turn,
        content: stringifyContent(d.content),
        source: typeof d.source === 'string' ? d.source : (d.source as { kind?: string })?.kind,
      }
    }
    // NOTE: DSH rc.6 has no durable `llm/retry` session event in the base
    // vocabulary (it is a plugin-merged, log-only extension); the adapter
    // maps it when the host assembly provides the type. Until then, retry
    // accounting uses the llm-retry merged event if present — see perf-analyzer.
    case 'assistant/chunk': {
      const d = event.data as {
        step?: number
        kind?: string
        text?: string
        delta?: string
        usage?: TokenUsage
      }
      const kind = d.kind
      if (kind === 'usage') {
        return { ...base, type: 'assistant/chunk', step: d.step ?? 0, kind: 'usage', usage: d.usage }
      }
      if (kind === 'reasoning-delta' || kind === 'reasoning') {
        return { ...base, type: 'assistant/chunk', step: d.step ?? 0, kind: 'reasoning', text: d.text ?? d.delta ?? '' }
      }
      if (kind === 'text-delta' || kind === 'text') {
        return { ...base, type: 'assistant/chunk', step: d.step ?? 0, kind: 'text', text: d.text ?? d.delta ?? '' }
      }
      // tool-call deltas, block boundaries and finish markers are not needed
      // by the engines (tool/call events carry the authoritative call).
      return null
    }
    case 'assistant/message': {
      const d = event.data as {
        turn?: number
        step?: number
        usage?: TokenUsage
        provider?: string
        model?: string
      }
      return {
        ...base,
        type: 'assistant/message',
        turn: d.turn ?? 0,
        step: d.step ?? 0,
        usage: d.usage,
        provider: d.provider,
        model: d.model,
      }
    }
    case 'tool/call': {
      const d = event.data as {
        step?: number
        callId?: string
        name?: string
        args?: JsonValue
        argsTruncated?: boolean
      }
      if (!d.name) return null
      return {
        ...base,
        type: 'tool/call',
        step: d.step ?? 0,
        callId: (d.callId ?? `call-${event.seq}`) as CallId,
        name: d.name,
        args: d.args ?? null,
        argsTruncated: d.argsTruncated,
      }
    }
    case 'tool/result': {
      const d = event.data as unknown as {
        step?: number
        callId?: string
        isError?: boolean
        code?: string
        message?: unknown
        value?: JsonValue
        contentPreview?: string
        spillLocator?: string
      }
      return {
        ...base,
        type: 'tool/result',
        step: d.step ?? 0,
        callId: (d.callId ?? `call-${event.seq}`) as CallId,
        isError: d.isError ?? false,
        code: d.code,
        message: messageText(d.message),
        value: d.value,
        contentPreview: d.contentPreview,
        spillLocator: d.spillLocator,
      }
    }
    default:
      return null
  }
}

/** Adapt a live DSH session into the plugin's read-side model. */
export function adaptSession(session: Session | { id: SessionId; events: readonly SessionEvent[] }): DebugSession {
  return {
    id: session.id,
    events: session.events.flatMap((event) => {
      const adapted = adaptEvent(event)
      return adapted === null ? [] : [adapted]
    }),
  }
}

function normalizeTurnEndReason(kind: string | undefined): TurnEndReason {
  switch (kind) {
    case 'completed':
    case 'aborted':
    case 'blocked':
    case 'error':
    case 'max-tokens':
    case 'interrupted':
      return kind
    default:
      return 'completed'
  }
}

function stringifyContent(content: unknown): string {
  if (typeof content === 'string') return content
  if (Array.isArray(content)) {
    // Content blocks: keep the text portions, drop images/attachments.
    const texts = content
      .filter((block): block is { type?: string; text?: unknown } => typeof block === 'object' && block !== null)
      .filter((block) => block.type === 'text' || block.type === undefined)
      .map((block) => (typeof block.text === 'string' ? block.text : ''))
      .join('\n')
    return texts || JSON.stringify(content)
  }
  return JSON.stringify(content)
}

/** DSH tool results carry a message object; extract a stable text preview. */
function messageText(message: unknown): string | undefined {
  if (typeof message === 'string') return message
  if (message !== null && typeof message === 'object') {
    const text = (message as { text?: unknown }).text
    if (typeof text === 'string') return text
  }
  return undefined
}
