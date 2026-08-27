/**
 * Breakpoint manager: live interception of running agents.
 *
 * Step and turn breakpoints pause an agent BEFORE its next model step by
 * short-circuiting the `agent/pre-step` waterfall (not calling `next()`).
 * While paused, the agent loop awaits our gate; the UI resumes it through
 * the service (`resume`), which resolves the gate so `next()` runs.
 *
 * Platform facts this implementation relies on (verified against dsh-agent):
 * - `agent/pre-step` is a waterfall: not calling `next()` blocks the step;
 * - listeners registered on the host context receive every agent, so we
 *   filter by `payload.agent.session.id`;
 * - tool parameters cannot be rewritten in the pipeline, so "edit args" is
 *   deliberately NOT implemented here (see the intervention executor).
 *
 * Breakpoint DEFINITIONS persist in the sidecar; the paused state is
 * process-local (a live `agent/*` state) and never durable.
 *
 * @module dsh-trajectory-debug-host/breakpoint-manager
 */

import type { Context } from '@deepseek-ai/cordis'
import type { Agent } from '@deepseek-ai/dsh-agent'
import type { Breakpoint, BreakpointId, BreakpointSpec, PauseCause, SessionId } from 'dsh-trajectory-debug'

interface BreakpointEntry {
  breakpoint: Breakpoint
  /** Resolved (turn, step) for `at: 'step'` specs (seq → step boundary). */
  turnStep?: { turn: number; step: number }
}

interface PauseGate {
  promise: Promise<PauseCause>
  resolve: (cause: PauseCause) => void
  timer?: ReturnType<typeof setTimeout>
}

export interface BreakpointManagerOptions {
  /** How long an agent may stay paused before auto-resume. */
  timeoutMs?: number
}

export class BreakpointManager {
  private readonly breakpoints = new Map<SessionId, Map<BreakpointId, BreakpointEntry>>()
  private readonly paused = new Map<SessionId, PauseGate>()
  private readonly timeoutMs: number
  private nextId = 0

  constructor(options: BreakpointManagerOptions = {}) {
    this.timeoutMs = options.timeoutMs ?? 10 * 60 * 1000
  }

  /** Register live listeners; returns the disposer (unload = unregister). */
  install(ctx: Context): () => void {
    const off = ctx.on('agent/pre-step', async (payload, next) => {
      const sessionId = payload.agent.session.id
      const hit = this.matchingBreakpoint(sessionId, payload.turn, payload.step)
      if (hit === undefined) return next()
      const gate = this.pause(sessionId)
      ctx.emit('trajectory-debug/paused', {
        sessionId,
        turn: payload.turn,
        step: payload.step,
      })
      const cause = await gate.promise
      ctx.emit('trajectory-debug/resumed', { sessionId, cause })
      return next()
    })
    return off
  }

  set(sessionId: SessionId, spec: BreakpointSpec, turnStep?: { turn: number; step: number }): BreakpointId {
    const id = `bp-${++this.nextId}` as BreakpointId
    const entry: BreakpointEntry = {
      breakpoint: { id, sessionId, spec, enabled: true },
      turnStep,
    }
    let bySession = this.breakpoints.get(sessionId)
    if (bySession === undefined) {
      bySession = new Map()
      this.breakpoints.set(sessionId, bySession)
    }
    bySession.set(id, entry)
    return id
  }

  remove(sessionId: SessionId, id: BreakpointId): void {
    this.breakpoints.get(sessionId)?.delete(id)
  }

  list(sessionId: SessionId): Breakpoint[] {
    return [...(this.breakpoints.get(sessionId)?.values() ?? [])].map((e) => e.breakpoint)
  }

  isPaused(sessionId: SessionId): boolean {
    return this.paused.has(sessionId)
  }

  /** Resume a paused agent (user decision). No-op when not paused. */
  resume(sessionId: SessionId, cause: PauseCause): void {
    const gate = this.paused.get(sessionId)
    if (gate === undefined) return
    if (gate.timer !== undefined) clearTimeout(gate.timer)
    this.paused.delete(sessionId)
    gate.resolve(cause)
  }

  /** Abandon all pause gates (e.g. host disposal). */
  cancelAll(): void {
    for (const sessionId of [...this.paused.keys()]) this.resume(sessionId, 'cancelled')
  }

  private matchingBreakpoint(sessionId: SessionId, turn: number, step: number): Breakpoint | undefined {
    const bySession = this.breakpoints.get(sessionId)
    if (bySession === undefined) return undefined
    for (const entry of bySession.values()) {
      if (!entry.breakpoint.enabled) continue
      const spec = entry.breakpoint.spec
      if (spec.at === 'turn' && spec.turn === turn) return entry.breakpoint
      if (spec.at === 'step' && entry.turnStep !== undefined && entry.turnStep.turn === turn && entry.turnStep.step === step) {
        return entry.breakpoint
      }
    }
    return undefined
  }

  private pause(sessionId: SessionId): PauseGate {
    const existing = this.paused.get(sessionId)
    if (existing !== undefined) return existing
    let resolve!: (cause: PauseCause) => void
    const promise = new Promise<PauseCause>((r) => {
      resolve = r
    })
    const gate: PauseGate = { promise, resolve }
    gate.timer = setTimeout(() => {
      // Timeout auto-resume keeps the agent from hanging forever.
      this.resume(sessionId, 'timeout')
    }, this.timeoutMs)
    this.paused.set(sessionId, gate)
    return gate
  }
}

/** Helper: the agent behind a payload (kept for future tool-breakpoint use). */
export function agentSessionId(agent: Agent): SessionId {
  return agent.session.id
}
