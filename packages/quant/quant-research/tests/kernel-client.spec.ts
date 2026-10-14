import { describe, expect, it } from 'vitest'
import type { Writable } from 'node:stream'
import { QuantKernelClient } from '../src/kernel-client/client.ts'
import type { KernelProcess, SpawnKernel } from '../src/kernel-client/client.ts'
import {
  KERNEL_PROTOCOL_VERSION, ResponseParser, encodeRequest, kernelErrorToQuantCode, parseResponseLine,
} from '../src/kernel-client/protocol.ts'
import { QuantError } from '../src/errors.ts'

function okResponse(id: string, result: unknown): string {
  return `${JSON.stringify({ id, ok: true, result })}\n`
}

function errorResponse(id: string, code: string, message: string): string {
  return `${JSON.stringify({ id, ok: false, error: { code, message } })}\n`
}

interface FakeProcessOptions {
  readonly stdoutText?: string
  readonly stderrText?: string
  readonly neverExits?: boolean
  readonly noStdin?: boolean
  readonly stdoutReader?: undefined
  respondAfterFirstPoll?: boolean
}

function fakeProcess(options: FakeProcessOptions = {}): { process: KernelProcess } {
  let polls = 0
  let terminated = false
  const exits = options.neverExits !== true
  let requestId = ''
  const respond = (fallback: string): string => fallback.replaceAll('r-1', requestId)
  const process: KernelProcess = {
    stdin: options.noStdin === true ? undefined : ({
      write: (chunk: string) => {
        try {
          const parsed: unknown = JSON.parse(chunk.endsWith('\n') ? chunk.slice(0, -1) : chunk)
          requestId = String((parsed as { id: unknown }).id)
        } catch {
          requestId = ''
        }
      },
      end: () => {},
    } as unknown as Writable),
    stdout: options.stdoutReader ?? {
      readFrom: (offset: number) => {
        polls += 1
        const text = options.respondAfterFirstPoll === true && polls < 2 ? '' : respond(options.stdoutText ?? '')
        return { text, nextOffset: offset + text.length, lossy: false }
      },
    },
    stderr: {
      readFrom: () => ({ text: options.stderrText ?? '', nextOffset: (options.stderrText ?? '').length, lossy: false }),
    },
    waitForExit: (signal?: AbortSignal): Promise<boolean> => new Promise((resolve) => {
      const timer = setInterval(() => {
        if (exits || terminated) {
          clearInterval(timer)
          resolve(true)
          return
        }
        if (signal?.aborted) {
          clearInterval(timer)
          resolve(false)
        }
      }, 1)
    }),
    terminate: () => { terminated = true },
  }
  return { process }
}

function spawnReturning(process: KernelProcess): { spawn: SpawnKernel; specs: unknown[] } {
  const specs: unknown[] = []
  const spawn: SpawnKernel = (spec) => {
    specs.push(spec)
    return process
  }
  return { spawn, specs }
}

function client(spawn: SpawnKernel, requestTimeoutMs = 1_000): QuantKernelClient {
  return new QuantKernelClient({
    spawn,
    command: 'python3',
    scriptPath: '/opt/quant/kernel-py/main.py',
    requestTimeoutMs,
    // A real macrotask: an instantly-resolved sleep would starve the event
    // loop and the deadline timer could never fire.
    sleep: ms => new Promise((resolve) => { setTimeout(resolve, Math.min(ms, 2)) }),
  })
}

describe('protocol codec', () => {
  it('encodes one request line', () => {
    const line = encodeRequest({ protocol: KERNEL_PROTOCOL_VERSION, id: 'r-1', op: 'ping', params: {} })
    expect(line.endsWith('\n')).toBe(true)
    expect(JSON.parse(line)).toEqual({ protocol: 1, id: 'r-1', op: 'ping', params: {} })
  })

  it('parses a line across split chunks', () => {
    const parser = new ResponseParser()
    const full = okResponse('r-1', { a: 1 })
    const cut = Math.floor(full.length / 2)
    expect(parser.push(full.slice(0, cut))).toEqual([])
    const responses = parser.push(full.slice(cut))
    expect(responses).toEqual([{ id: 'r-1', ok: true, result: { a: 1 } }])
  })

  it('skips blank lines', () => {
    const parser = new ResponseParser()
    expect(parser.push('\n\n')).toEqual([])
  })

  it('throws a KERNEL error on malformed json', () => {
    expect(() => parseResponseLine('not-json')).toThrow(QuantError)
    expect(() => parseResponseLine('not-json')).toThrow(/无法解析/)
  })

  it('throws a KERNEL error on schema-invalid responses', () => {
    expect(() => parseResponseLine('{"id":"","ok":true}')).toThrow(/不符合协议/)
    expect(() => parseResponseLine('{"id":"r","ok":"maybe"}')).toThrow(/不符合协议/)
  })

  it('maps every kernel error code', () => {
    expect(kernelErrorToQuantCode('NETWORK_ERROR')).toBe('NETWORK')
    expect(kernelErrorToQuantCode('DATA_ERROR')).toBe('DATA')
    expect(kernelErrorToQuantCode('CONFIG_ERROR')).toBe('CONFIG')
    expect(kernelErrorToQuantCode('BAD_REQUEST')).toBe('DATA')
    expect(kernelErrorToQuantCode('SOMETHING_ELSE')).toBe('KERNEL')
  })
})

describe('QuantKernelClient.request', () => {
  it('spawns the interpreter with an explicit spec and returns the matched result', async () => {
    const { process } = fakeProcess({ stdoutText: okResponse('r-1', { value: 42 }) })
    const { spawn, specs } = spawnReturning(process)
    const kernel = client(spawn)
    const result = await kernel.request('ping', {}, undefined)
    expect(result).toEqual({ value: 42 })
    const spec = specs[0] as {
      argv: string[]
      cwd: string
      stdio: { stdin: string }
      graceMs: number
      env: Record<string, string>
    }
    expect(spec.argv).toEqual(['python3', '/opt/quant/kernel-py/main.py'])
    expect(spec.cwd).toBe('/opt/quant/kernel-py')
    expect(spec.stdio.stdin).toBe('pipe')
    expect(spec.graceMs).toBeGreaterThan(0)
    // The scrubbed parent env: the kernel needs the ambient PATH but never a secret.
    expect(typeof (spec.env ?? {})['PATH']).toBe('string')
    expect(Object.keys(spec.env ?? {}).some(key => /SECRET|TOKEN|PASSWORD/i.test(key))).toBe(false)
  })

  it('returns the kernel error as its mapped tier', async () => {
    const { process } = fakeProcess({ stdoutText: errorResponse('r-1', 'DATA_ERROR', '标的不存在') })
    const { spawn } = spawnReturning(process)
    const kernel = client(spawn)
    await expect(kernel.request('get_kline', {}, undefined)).rejects.toThrow(/量化内核拒绝请求：标的不存在/)
  })

  it('reports a crash with the stderr tail', async () => {
    const { process } = fakeProcess({ stdoutText: '', stderrText: 'Traceback: boom' })
    const { spawn } = spawnReturning(process)
    const kernel = client(spawn)
    const error = await kernel.request('ping', {}, undefined).catch((caught: unknown) => caught) as QuantError
    expect(error).toBeInstanceOf(QuantError)
    expect(error.code).toBe('KERNEL')
    expect(error.message).toContain('异常退出')
    expect((error.cause as { stderrTail: string }).stderrTail).toContain('boom')
  })

  it('cancels on its own deadline and terminates the tree', async () => {
    const { process } = fakeProcess({ neverExits: true })
    const { spawn } = spawnReturning(process)
    const kernel = client(spawn, 30)
    const error = await kernel.request('ping', {}, undefined).catch((caught: unknown) => caught) as QuantError
    expect(error.code).toBe('CANCELLED')
    expect(error.message).toContain('超时')
    expect(typeof process.waitForExit).toBe('function')
  })

  it('cancels with the caller-facing message when the outer signal fired first', async () => {
    const { process } = fakeProcess({ neverExits: true })
    const { spawn } = spawnReturning(process)
    const kernel = client(spawn, 60_000)
    const controller = new AbortController()
    setTimeout(() => { controller.abort() }, 20)
    const error = await kernel.request('ping', {}, controller.signal).catch((caught: unknown) => caught) as QuantError
    expect(error.code).toBe('CANCELLED')
    expect(error.message).toContain('已取消')
  })

  it('throws KERNEL on a mismatched correlation id', async () => {
    const { process } = fakeProcess({ stdoutText: okResponse('other-id', {}) })
    const { spawn } = spawnReturning(process)
    await expect(client(spawn).request('ping', {}, undefined)).rejects.toThrow(/不匹配的请求 id/)
  })

  it('throws KERNEL when the child has no stdin', async () => {
    const { process } = fakeProcess({ noStdin: true })
    const { spawn } = spawnReturning(process)
    await expect(client(spawn).request('ping', {}, undefined)).rejects.toThrow(/标准输入/)
  })

  it('throws KERNEL when the child has no stdout reader', async () => {
    const process: KernelProcess = {
      ...fakeProcess().process,
      stdout: undefined,
    }
    const { spawn } = spawnReturning(process)
    await expect(client(spawn).request('ping', {}, undefined)).rejects.toThrow(/标准输出/)
  })

  it('maps a spawn failure to a KERNEL error', async () => {
    const spawn: SpawnKernel = () => {
      throw new Error('python not found')
    }
    await expect(client(spawn).request('ping', {}, undefined)).rejects.toThrow(/无法启动量化内核/)
  })
})

describe('late responses', () => {
  it('keeps polling until the response arrives', async () => {
    const { process } = fakeProcess({ stdoutText: okResponse('r-1', 1), respondAfterFirstPoll: true })
    const { spawn } = spawnReturning(process)
    // The default poll sleep (a real timer) drives this loop.
    const kernel = new QuantKernelClient({
      spawn,
      command: 'python3',
      scriptPath: '/opt/quant/kernel-py/main.py',
      requestTimeoutMs: 2_000,
    })
    await expect(kernel.request('ping', {}, undefined)).resolves.toBe(1)
  })

  it('tolerates a child without a stderr reader on crash', async () => {
    const base = fakeProcess({ stdoutText: '' }).process
    const process: KernelProcess = { ...base, stderr: undefined }
    const { spawn } = spawnReturning(process)
    const error = await client(spawn).request('ping', {}, undefined).catch((caught: unknown) => caught) as QuantError
    expect(error.code).toBe('KERNEL')
    expect((error.cause as { stderrTail: string }).stderrTail).toBe('')
  })
})
