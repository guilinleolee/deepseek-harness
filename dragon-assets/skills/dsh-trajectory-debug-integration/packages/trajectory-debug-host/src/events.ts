import type { ExperimentRecord, PauseCause, SessionId } from 'dsh-trajectory-debug'

/**
 * Live coordination events produced by this plugin family (host side).
 *
 * These are **not** session-log events: they are real-time notifications for
 * the browser (like `agent/*`), emitted by the host provider and forwarded to
 * the client through the remote-event allowlist. They carry no durable
 * content and never enter the session transcript.
 *
 * @module dsh-trajectory-debug-host/events
 */

declare module '@deepseek-ai/cordis' {
  interface Events {
    /** An agent paused at a breakpoint (step or turn boundary). */
    'trajectory-debug/paused'(payload: {
      sessionId: SessionId
      turn: number
      step: number
    }): void
    /** A paused agent resumed (user decision or timeout). */
    'trajectory-debug/resumed'(payload: {
      sessionId: SessionId
      cause: PauseCause
    }): void
    /** A re-run experiment settled (record stored in the sidecar). */
    'trajectory-debug/experiment'(payload: {
      record: ExperimentRecord
    }): void
  }
}
