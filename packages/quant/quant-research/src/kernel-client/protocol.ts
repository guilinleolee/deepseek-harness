/**
 * The Python kernel's NDJSON wire contract: request encoding, incremental
 * response parsing, and the error-code mapping. One request per kernel
 * process; the process answers exactly one response line on stdout, so a
 * mismatched correlation id is a protocol violation. The process/wire edge
 * is a validated boundary — every response passes the zod schema before any
 * caller sees it.
 * @module @deepseek-ai/dsh-quant-research/kernel-client/protocol
 */

import { z } from 'zod'
import type { QuantErrorCode } from '../errors.ts'
import { QuantError } from '../errors.ts'

/** The wire protocol version the TS side speaks; the kernel rejects others. */
export const KERNEL_PROTOCOL_VERSION = 1

/** Operations the kernel serves in phase 1. */
export type KernelOp = 'ping' | 'get_kline' | 'backtest'

/** One kernel request line. */
export interface KernelRequest {
  /** Wire protocol version. */
  readonly protocol: typeof KERNEL_PROTOCOL_VERSION
  /** Correlation id; a fresh UUID per request. */
  readonly id: string
  /** The operation to run. */
  readonly op: KernelOp
  /** Operation parameters (already validated by the tool layer). */
  readonly params: Record<string, unknown>
}

/** Kernel-side error codes. */
export type KernelErrorCode = 'NETWORK_ERROR' | 'DATA_ERROR' | 'CONFIG_ERROR' | 'BAD_REQUEST'

/** One failed kernel response. */
export interface KernelResponseError {
  /** The correlation id. */
  readonly id: string
  /** Failure marker. */
  readonly ok: false
  /** The kernel's error tier and friendly message. */
  readonly error: { readonly code: KernelErrorCode; readonly message: string }
}

/** One successful kernel response. */
export interface KernelResponseSuccess {
  /** The correlation id. */
  readonly id: string
  /** Success marker. */
  readonly ok: true
  /** The operation result; its shape is validated by the calling module. */
  readonly result: unknown
}

/** One kernel response line. */
export type KernelResponse = KernelResponseSuccess | KernelResponseError

const kernelResponseSchema = z.discriminatedUnion('ok', [
  z.object({ id: z.string().min(1), ok: z.literal(true), result: z.unknown() }),
  z.object({
    id: z.string().min(1),
    ok: z.literal(false),
    error: z.object({ code: z.string(), message: z.string() }),
  }),
])

/**
 * Encode one request as its wire line (compact JSON plus the newline).
 * @param request - the request to encode.
 * @returns the line to write to the kernel's stdin.
 */
export function encodeRequest(request: KernelRequest): string {
  return `${JSON.stringify(request)}\n`
}

/**
 * Incremental response parser: feed stdout chunks, receive every complete
 * response line. Malformed lines throw — a kernel that emits non-protocol
 * output has failed its contract.
 */
export class ResponseParser {
  private buffer = ''

  /**
   * Feed one stdout chunk.
   * @param chunk - raw stdout text (any split across lines).
   * @returns every complete response the chunk completed.
   */
  push(chunk: string): KernelResponse[] {
    this.buffer += chunk
    const responses: KernelResponse[] = []
    for (;;) {
      const newline = this.buffer.indexOf('\n')
      if (newline < 0) break
      const line = this.buffer.slice(0, newline)
      this.buffer = this.buffer.slice(newline + 1)
      if (line.trim().length === 0) continue
      responses.push(parseResponseLine(line))
    }
    return responses
  }
}

/**
 * Parse one complete response line.
 * @param line - one JSON line without its newline.
 * @returns the validated response.
 * @throws {@link QuantError} code `KERNEL` when the line is not valid protocol JSON.
 */
export function parseResponseLine(line: string): KernelResponse {
  let parsed: unknown
  try {
    parsed = JSON.parse(line)
  } catch (error: unknown) {
    throw new QuantError('KERNEL', '量化内核返回了无法解析的输出', { cause: error })
  }
  const result = kernelResponseSchema.safeParse(parsed)
  if (!result.success) {
    throw new QuantError('KERNEL', '量化内核返回了不符合协议的响应', { cause: result.error })
  }
  // Wire-validated; the error tier narrows through kernelErrorToQuantCode at
  // the call site, so the looser zod code string widens safely here.
  return result.data as KernelResponse
}

/**
 * Map a kernel error tier onto the plugin's error tiers.
 * @param code - the kernel's error code string.
 * @returns the matching plugin error tier; unknown codes collapse to `KERNEL`.
 */
export function kernelErrorToQuantCode(code: string): QuantErrorCode {
  switch (code) {
    case 'NETWORK_ERROR':
      return 'NETWORK'
    case 'DATA_ERROR':
      return 'DATA'
    case 'CONFIG_ERROR':
      return 'CONFIG'
    case 'BAD_REQUEST':
      return 'DATA'
    default:
      return 'KERNEL'
  }
}
