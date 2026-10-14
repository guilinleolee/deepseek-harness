/**
 * The plugin's session-event vocabulary. `quant/kernel-fault` is a log-only
 * diagnostic: it records one Python-kernel plane fault so a session replay
 * can answer "why did this tool call fail" without the fault ever entering a
 * model request. The friendly failure itself rides the tool result.
 * @module @deepseek-ai/dsh-quant-research/events
 */

import type { QuantErrorCode } from './errors.ts'

declare module '@deepseek-ai/dsh-session/types' {
  interface SessionEventMap {
    /**
     * One Python-kernel plane fault (spawn failure, crash, deadline, or wire
     * violation), recorded at the moment the kernel client classified it.
     * Log-only: never model-visible, never a surface event, and never a
     * substitute for the tool result's friendly envelope.
     */
    'quant/kernel-fault': {
      /** The kernel request correlation id (a fresh UUID per request). */
      requestId: string
      /** The kernel operation that failed (`ping` / `get_kline` / `backtest`). */
      op: string
      /** The classified error tier. */
      code: QuantErrorCode
      /** The friendly Chinese message the tool layer will surface. */
      message: string
    }
  }
}
