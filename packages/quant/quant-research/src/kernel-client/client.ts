/**
 * The kernel client: one request, one short-lived Python process. The kernel
 * is stateless, so every {@link QuantKernelClient.request} spawns a fresh
 * interpreter via the subprocess capability, writes one request line, reads
 * response lines to the matching correlation id, and tears the process tree
 * down through the seam's terminate ladder — the cooperative `exec.signal`
 * deadline and the client's own timer both end in the same `terminate()`,
 * and no self-written kill logic exists. Spawn failures, crashes, protocol
 * violations, and deadlines all classify into the plugin's error tiers.
 * @module @deepseek-ai/dsh-quant-research/kernel-client/client
 */

import { randomUUID } from 'node:crypto'
import { dirname } from 'node:path'
import type { Writable } from 'node:stream'
import type { SubprocessOutputReader, SubprocessSpawnSpec } from '@deepseek-ai/dsh-subprocess'
import { scrubbedParentEnv } from '@deepseek-ai/dsh-subprocess'
import { QuantError } from '../errors.ts'
import {
  KERNEL_PROTOCOL_VERSION,
  ResponseParser,
  encodeRequest,
  kernelErrorToQuantCode,
} from './protocol.ts'
import type { KernelOp } from './protocol.ts'

/** Collected stdout cap: one response line plus slack; a runaway kernel loses its tail. */
export const KERNEL_STDOUT_MAX_BYTES = 16 * 1024 * 1024
/** Collected stderr cap: the diagnostic tail only; detail lives in the kernel's own logs. */
export const KERNEL_STDERR_MAX_BYTES = 64 * 1024
/** The terminate ladder's grace window before escalation, handed to the subprocess seam. */
export const KERNEL_TERMINATE_GRACE_MS = 2_000
/** How often the read loop polls the collected streams between exits. */
export const KERNEL_POLL_INTERVAL_MS = 20

/**
 * The process face the client drives — the structural subset of the
 * subprocess seam's handle this module touches, so tests can substitute an
 * in-memory process.
 */
export interface KernelProcess {
  /** The child's stdin when spawned piped. */
  readonly stdin: Writable | undefined
  /** Offset-based stdout reader when spawned collecting. */
  readonly stdout: SubprocessOutputReader | undefined
  /** Offset-based stderr reader when spawned collecting. */
  readonly stderr: SubprocessOutputReader | undefined
  /**
   * Wait until the process tree exits.
   * @param signal - optional bound; `false` when the signal fires first.
   * @returns true when the tree exited.
   */
  waitForExit(signal?: AbortSignal): Promise<boolean>
  /** Tree-scoped termination (SIGTERM → grace → kill; Windows `taskkill /T /F`). */
  terminate(): void
}

/** Spawns one kernel process for the given spec. */
export type SpawnKernel = (spec: SubprocessSpawnSpec) => KernelProcess

/** Resolved kernel-client dependencies. */
export interface QuantKernelClientOptions {
  /** The spawn seam (the subprocess capability's `spawn`). */
  readonly spawn: SpawnKernel
  /** Python interpreter command. */
  readonly command: string
  /** Absolute path of the kernel's `main.py`. */
  readonly scriptPath: string
  /** Per-request deadline in milliseconds. */
  readonly requestTimeoutMs: number
  /** Sleep used by the read loop (tests shrink it; defaults to a real timer). */
  readonly sleep?: (ms: number) => Promise<void>
}

/**
 * Spawn-and-talk client for the quant research kernel. One instance per
 * plugin; no persistent child exists between requests.
 */
export class QuantKernelClient {
  private readonly options: QuantKernelClientOptions

  /**
   * @param options - spawn seam, interpreter command, script path, and deadline.
   */
  constructor(options: QuantKernelClientOptions) {
    this.options = options
  }

  /**
   * Run one kernel operation to completion. The process is always reaped:
   * the `finally` block terminates the tree and waits for exit on every path.
   * @param op - the operation to run.
   * @param params - operation parameters; the caller validated them already.
   * @param signal - the caller's cancellation (the tool execution's `exec.signal`).
   * @returns the kernel's result value.
   * @throws {@link QuantError} — `CANCELLED` on deadline/abort, `KERNEL` on
   * spawn failure, crash, or protocol violation, or the kernel error's own tier.
   */
  async request(op: KernelOp, params: Record<string, unknown>, signal?: AbortSignal): Promise<unknown> {
    const id = randomUUID()
    const deadline = new AbortController()
    const onExternalAbort = (): void => { deadline.abort() }
    signal?.addEventListener('abort', onExternalAbort, { once: true })
    const timer = setTimeout(() => { deadline.abort() }, this.options.requestTimeoutMs)
    const sleep = this.options.sleep ?? ((ms: number) => new Promise<void>((resolve) => { setTimeout(resolve, ms) }))
    const handle = this.spawn()
    try {
      this.writeRequest(handle, { protocol: KERNEL_PROTOCOL_VERSION, id, op, params })
      let stdoutOffset = 0
      const parser = new ResponseParser()
      for (;;) {
        const response = this.drain(handle, parser, () => stdoutOffset, (next) => { stdoutOffset = next }, id)
        if (response !== undefined) return response
        if (deadline.signal.aborted) {
          throw this.abortedError(op, id, signal?.aborted === true)
        }
        const exited = await Promise.race([
          handle.waitForExit(deadline.signal).then(settled => settled),
          sleep(KERNEL_POLL_INTERVAL_MS).then(() => false),
        ])
        if (exited) {
          const final = this.drain(handle, parser, () => stdoutOffset, (next) => { stdoutOffset = next }, id)
          if (final !== undefined) return final
          throw this.crashError(handle, op, id)
        }
      }
    } finally {
      clearTimeout(timer)
      signal?.removeEventListener('abort', onExternalAbort)
      handle.terminate()
      await handle.waitForExit()
    }
  }

  /**
   * Spawn the kernel process, mapping a spawn failure to its tier.
   * @returns the fresh process handle.
   */
  private spawn(): KernelProcess {
    try {
      return this.options.spawn({
        argv: [this.options.command, this.options.scriptPath],
        cwd: dirname(this.options.scriptPath),
        stdio: {
          stdin: 'pipe',
          stdout: { maxBytes: KERNEL_STDOUT_MAX_BYTES },
          stderr: { maxBytes: KERNEL_STDERR_MAX_BYTES },
        },
        graceMs: KERNEL_TERMINATE_GRACE_MS,
        env: scrubbedParentEnv(),
      })
    } catch (error: unknown) {
      throw new QuantError('KERNEL', '无法启动量化内核进程，请检查 kernelCommand 配置与 Python 环境', { cause: error })
    }
  }

  /**
   * Write one request line to the child's stdin.
   * @param handle - the process handle.
   * @param request - the request to write.
   */
  private writeRequest(
    handle: KernelProcess,
    request: {
      protocol: typeof KERNEL_PROTOCOL_VERSION
      id: string
      op: KernelOp
      params: Record<string, unknown>
    },
  ): void {
    const stdin = handle.stdin
    if (stdin === undefined) {
      throw new QuantError('KERNEL', '量化内核进程缺少标准输入通道')
    }
    stdin.write(encodeRequest(request))
    stdin.end()
  }

  /**
   * Read any newly collected stdout and return the response matching `id`.
   * A mismatched id, a malformed line, or a kernel error response throws.
   * @param handle - the process handle.
   * @param parser - the incremental response parser.
   * @param offset - getter for the current stdout read offset.
   * @param advance - setter recording the consumed offset.
   * @param id - the correlation id to match.
   * @returns the matched result value, or `undefined` when no complete response exists yet.
   */
  private drain(
    handle: KernelProcess,
    parser: ResponseParser,
    offset: () => number,
    advance: (next: number) => void,
    id: string,
  ): unknown {
    const reader = handle.stdout
    if (reader === undefined) {
      throw new QuantError('KERNEL', '量化内核进程缺少标准输出通道')
    }
    const read = reader.readFrom(offset())
    advance(read.nextOffset)
    for (const response of parser.push(read.text)) {
      if (response.id !== id) {
        throw new QuantError('KERNEL', '量化内核返回了不匹配的请求 id', { cause: { expected: id, actual: response.id } })
      }
      if (response.ok) return response.result
      throw new QuantError(
        kernelErrorToQuantCode(response.error.code),
        `量化内核拒绝请求：${response.error.message}`,
      )
    }
    return undefined
  }

  /**
   * Build the error for a cancelled or timed-out request.
   * @param op - the operation that was running.
   * @param id - the correlation id.
   * @param externallyAborted - true when the caller's own signal fired first.
   * @returns the `CANCELLED` error.
   */
  private abortedError(op: KernelOp, id: string, externallyAborted: boolean): QuantError {
    return new QuantError(
      'CANCELLED',
      externallyAborted
        ? `量化研究调用已取消（${op}）`
        : `量化内核请求超时（${String(this.options.requestTimeoutMs)}ms），已终止内核进程`,
      { cause: { op, requestId: id } },
    )
  }

  /**
   * Build the error for a process that exited without answering, carrying
   * the stderr diagnostic tail as the cause.
   * @param handle - the exited process handle.
   * @param op - the operation that was running.
   * @param id - the correlation id.
   * @returns the `KERNEL` error.
   */
  private crashError(handle: KernelProcess, op: KernelOp, id: string): QuantError {
    const stderr = handle.stderr?.readFrom(0).text ?? ''
    return new QuantError(
      'KERNEL',
      '量化内核进程异常退出，未返回结果',
      { cause: { op, requestId: id, stderrTail: stderr.slice(-2_000) } },
    )
  }
}
