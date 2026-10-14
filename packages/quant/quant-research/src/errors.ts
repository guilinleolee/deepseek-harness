/**
 * Tiered error vocabulary and the unified `{code, msg, data}` envelope every
 * `quant_*` tool returns. Codes follow the plugin's error tiers: `NETWORK`
 (data-source transport), `DATA` (missing/invalid market data), `KERNEL`
 (Python kernel process plane), `RISK` (red-line or risk denial), `CONFIG`
 (invalid deployment configuration), plus `CANCELLED` (cooperative timeout or
 abort) and `INTERNAL` (an unexpected in-process fault — the honest fallback a
 closed union needs). User-facing messages stay friendly Chinese; technical
 detail rides the error's `cause` into diagnostics, never into the envelope.
 * @module @deepseek-ai/dsh-quant-research/errors
 */

/** Error tiers carried by {@link QuantError} and the tool envelope's `code`. */
export type QuantErrorCode =
  | 'NETWORK'
  | 'DATA'
  | 'KERNEL'
  | 'RISK'
  | 'CONFIG'
  | 'CANCELLED'
  | 'INTERNAL'

/** Numeric wire code for the envelope: 0 is success, non-zero maps one tier. */
export const ENVELOPE_CODES: Readonly<Record<QuantErrorCode, number>> = Object.freeze({
  NETWORK: 1001,
  DATA: 1002,
  KERNEL: 1003,
  RISK: 1004,
  CONFIG: 1005,
  CANCELLED: 1006,
  INTERNAL: 1999,
})

/** One tiered plugin failure: every `quant_*` failure path throws this class. */
export class QuantError extends Error {
  /** The error tier; also the envelope `code`'s symbolic half. */
  readonly code: QuantErrorCode

  /**
   * @param code - the error tier.
   * @param message - friendly Chinese message safe for the model and the user.
   * @param options - standard `ErrorOptions`; `cause` carries technical detail for diagnostics only.
   */
  constructor(code: QuantErrorCode, message: string, options?: ErrorOptions) {
    super(message, options)
    this.name = 'QuantError'
    this.code = code
  }
}

/**
 * Narrow an unknown thrown value to {@link QuantError}.
 * @param error - the caught value.
 * @returns true when the value is a plugin tiered error.
 */
export function isQuantError(error: unknown): error is QuantError {
  return error instanceof QuantError
}

/** Successful envelope payload carrier (a type alias so `data` stays assignable to JSON wire values). */
export type QuantEnvelope<T> = {
  /** 0 on success; the tier's numeric code on failure. */
  readonly code: number
  /** Friendly message; `'ok'` on success. */
  readonly msg: string
  /** The tool's structured result, or `null` on failure. */
  readonly data: T | null
}

/**
 * Wrap one successful result value.
 * @param data - the tool's structured result.
 * @returns the success envelope.
 */
export function okEnvelope<T>(data: T): QuantEnvelope<T> {
  return { code: 0, msg: 'ok', data }
}

/**
 * Project any thrown value onto the failure envelope. `QuantError`s keep
 * their tier and message; anything else collapses to `INTERNAL` with a
 * generic message so raw stack traces never reach the model or the user.
 * @param error - the caught value.
 * @returns the failure envelope with `data: null`.
 */
export function errorEnvelope(error: unknown): QuantEnvelope<never> {
  if (isQuantError(error)) {
    return { code: ENVELOPE_CODES[error.code], msg: error.message, data: null }
  }
  return {
    code: ENVELOPE_CODES.INTERNAL,
    msg: '量化研究插件内部错误，请稍后重试或查看会话诊断记录',
    data: null,
  }
}
