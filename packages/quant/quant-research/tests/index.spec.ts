import { describe, expect, it, vi } from 'vitest'
import { Context } from '@deepseek-ai/cordis'
import { resolveConfig } from '../src/config.ts'
import { apply, inject, name, resolveKernelScriptPath } from '../src/index.ts'
import { apply as invariantApply } from '../src/invariant.ts'

describe('plugin surface', () => {
  it('declares the plugin identity and service requirements', () => {
    expect(name).toBe('quant-research')
    expect(inject).toEqual(['storageDomain', 'subprocess'])
  })

  it('locates the shipped kernel script inside the package', () => {
    const scriptPath = resolveKernelScriptPath()
    expect(scriptPath.replace(/\\/g, '/')).toMatch(/kernel-py\/main\.py$/)
  })

  it('honors an injected require factory', () => {
    const fakeRequire = Object.assign(() => {}, { resolve: () => 'file:///opt/pkg/package.json' })
    const scriptPath = resolveKernelScriptPath(() => fakeRequire as never)
    expect(scriptPath.replace(/\\/g, '/')).toMatch(/kernel-py\/main\.py$/)
  })
})

function preparedContext(): {
  ctx: Context
  register: ReturnType<typeof vi.fn>
  close: ReturnType<typeof vi.fn>
  open: ReturnType<typeof vi.fn>
} {
  const ctx = new Context()
  const close = vi.fn(async () => {})
  const open = vi.fn(async () => ({
    table: () => ({ put: vi.fn(async () => {}) }),
    close,
  }))
  const register = vi.fn(() => () => {})
  ctx.provide('storageDomain', { open } as never)
  ctx.provide('subprocess', { spawn: vi.fn() } as never)
  ctx.provide('tools', { register } as never)
  return { ctx, register, close, open }
}

describe('apply', () => {
  it('composes the runtime, registers the three tools, and unwinds on dispose', async () => {
    const { ctx, register, close, open } = preparedContext()
    const disposer = await apply(ctx, resolveConfig(undefined, { platform: 'linux', dshHome: '/tmp' }))
    expect(open).toHaveBeenCalledTimes(1)
    const names = register.mock.calls.map(call => (call[0] as { name: string }).name)
    expect(names).toEqual(['quant_get_kline', 'quant_compute_indicator', 'quant_run_backtest'])
    await disposer()
    expect(close).toHaveBeenCalledTimes(1)
  })

  it('fails loud before opening the domain on an invalid config', async () => {
    const { ctx, open } = preparedContext()
    await expect(apply(ctx, { toolTimeoutMs: 0 })).rejects.toThrow(/toolTimeoutMs/)
    expect(open).not.toHaveBeenCalled()
  })
})

describe('kernel round trip through apply', () => {
  it('drives get_kline through the composed kernel and the subprocess seam', async () => {
    const bars = [{ date: '2024-01-02', open: 1, high: 2, low: 0.5, close: 1.5, volume: 10 }]
    const ctx = new Context()
    const registered: Array<{ name: string; execute?: (args: unknown, exec: unknown) => Promise<unknown> }> = []
    let spawnedPath = ''
    ctx.provide('storageDomain', {
      open: vi.fn(async () => ({ table: () => ({ put: vi.fn(async () => {}) }), close: vi.fn(async () => {}) })),
    } as never)
    ctx.provide('tools', {
      register: vi.fn((tool: { name: string; execute?: (args: unknown, exec: unknown) => Promise<unknown> }) => {
        registered.push(tool)
        return () => {}
      }),
    } as never)
    ctx.provide('subprocess', {
      spawn: (spec: { argv: string[] }) => {
        spawnedPath = spec.argv[1] ?? ''
        let requestId = ''
        return {
          stdin: {
            write: (chunk: string) => {
              const parsed: unknown = JSON.parse(chunk.trim())
              requestId = String((parsed as { id: unknown }).id)
            },
            end: () => {},
          },
          collected: {
            stdout: {
              readFrom: () => ({
                text: `${JSON.stringify({ id: requestId, ok: true, result: bars })}\n`,
                nextOffset: 0,
                lossy: false,
              }),
            },
            stderr: { readFrom: () => ({ text: '', nextOffset: 0, lossy: false }) },
          },
          waitForExit: () => Promise.resolve(true),
          terminate: () => {},
        }
      },
    } as never)

    const disposer = await apply(ctx)
    const kline = registered.find(tool => tool.name === 'quant_get_kline')
    expect(kline).toBeDefined()
    const value = await kline?.execute?.(
      { symbol: '000001', bars: 5 },
      { signal: new AbortController().signal },
    ) as { code: number; data: { count: number; series: unknown[] } }
    expect(value.code).toBe(0)
    expect(value.data.count).toBe(1)
    expect(spawnedPath.replace(/\\/g, '/')).toMatch(/kernel-py\/main\.py$/)
    await disposer()
  })
})

describe('invariant companion', () => {
  it('reserves package ownership through the invariants service', async () => {
    const ctx = new Context()
    const register = vi.fn(() => () => {})
    ctx.provide('invariants', { register } as never)
    const disposer = await invariantApply(ctx)
    expect(register).toHaveBeenCalledWith('@deepseek-ai/dsh-quant-research', expect.anything())
    expect(typeof disposer).toBe('function')
  })
})
