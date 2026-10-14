import { describe, expect, it } from 'vitest'
import { join } from 'node:path'
import {
  DEFAULT_CASH_LIMITS, FEE_RATE_LIMITS, FUSE_THRESHOLD_LIMITS,
  KERNEL_REQUEST_TIMEOUT_MS_LIMITS, SOURCE_MAX_RETRIES_LIMITS, TOOL_TIMEOUT_MS_LIMITS,
  defaultKernelCommand, resolveConfig,
} from '../src/config.ts'
import { ENVELOPE_CODES } from '../src/errors.ts'

const ENV_LINUX = { platform: 'linux' as const, dshHome: '/home/tester/.dsh' }
const ENV_WIN = { platform: 'win32' as const, dshHome: 'C:/Users/tester/.dsh' }

describe('defaultKernelCommand', () => {
  it('names the platform launcher', () => {
    expect(defaultKernelCommand('win32')).toBe('python')
    expect(defaultKernelCommand('linux')).toBe('python3')
    expect(defaultKernelCommand('darwin')).toBe('python3')
  })
})

describe('resolveConfig', () => {
  it('resolves every default', () => {
    const resolved = resolveConfig(undefined, ENV_LINUX)
    expect(resolved).toEqual({
      dataSource: 'synthetic',
      kernelCommand: 'python3',
      cacheDir: join(ENV_LINUX.dshHome, 'quant-research', 'cache'),
      toolTimeoutMs: TOOL_TIMEOUT_MS_LIMITS.default,
      kernelRequestTimeoutMs: KERNEL_REQUEST_TIMEOUT_MS_LIMITS.default,
      sourceMaxRetries: SOURCE_MAX_RETRIES_LIMITS.default,
      fuseThreshold: FUSE_THRESHOLD_LIMITS.default,
      defaultCash: DEFAULT_CASH_LIMITS.default,
      feeRate: FEE_RATE_LIMITS.default,
    })
  })

  it('resolves the windows python launcher and a provided cache dir', () => {
    const resolved = resolveConfig({ kernelCommand: 'py', cacheDir: 'D:/cache' }, ENV_WIN)
    expect(resolved.kernelCommand).toBe('py')
    expect(resolved.cacheDir).toBe('D:/cache')
    expect(resolveConfig(undefined, ENV_WIN).kernelCommand).toBe('python')
  })

  it('keeps provided values inside the bounds', () => {
    const resolved = resolveConfig({
      dataSource: 'akshare',
      toolTimeoutMs: 5_000,
      kernelRequestTimeoutMs: 4_000,
      sourceMaxRetries: 1,
      fuseThreshold: 2,
      defaultCash: 100_000,
      feeRate: 0.001,
    }, ENV_LINUX)
    expect(resolved.dataSource).toBe('akshare')
    expect(resolved.toolTimeoutMs).toBe(5_000)
    expect(resolved.kernelRequestTimeoutMs).toBe(4_000)
    expect(resolved.sourceMaxRetries).toBe(1)
    expect(resolved.fuseThreshold).toBe(2)
    expect(resolved.defaultCash).toBe(100_000)
    expect(resolved.feeRate).toBe(0.001)
  })

  it('rejects an unknown data source', () => {
    expect(() => resolveConfig({ dataSource: 'wind' as never }, ENV_LINUX)).toThrow(/dataSource/)
    expect(() => resolveConfig({ dataSource: 'wind' as never }, ENV_LINUX)).toThrow(/synthetic \/ akshare/)
  })

  it('rejects out-of-range numerics with the field name', () => {
    expect(() => resolveConfig({ toolTimeoutMs: 0 }, ENV_LINUX)).toThrow(/toolTimeoutMs/)
    expect(() => resolveConfig({ toolTimeoutMs: 601_000 }, ENV_LINUX)).toThrow(/toolTimeoutMs/)
    expect(() => resolveConfig({ kernelRequestTimeoutMs: Number.NaN }, ENV_LINUX)).toThrow(/kernelRequestTimeoutMs/)
    expect(() => resolveConfig({ sourceMaxRetries: 6 }, ENV_LINUX)).toThrow(/sourceMaxRetries/)
    expect(() => resolveConfig({ fuseThreshold: 0 }, ENV_LINUX)).toThrow(/fuseThreshold/)
    expect(() => resolveConfig({ defaultCash: -1 }, ENV_LINUX)).toThrow(/defaultCash/)
    expect(() => resolveConfig({ feeRate: 0.02 }, ENV_LINUX)).toThrow(/feeRate/)
  })

  it('requires the kernel deadline to stay below the tool budget', () => {
    expect(() => resolveConfig({ toolTimeoutMs: 5_000, kernelRequestTimeoutMs: 5_000 }, ENV_LINUX))
      .toThrow(/kernelRequestTimeoutMs/)
  })
})

describe('envelope codes', () => {
  it('cover every tier exactly once', () => {
    expect(Object.keys(ENVELOPE_CODES)).toEqual([
      'NETWORK', 'DATA', 'KERNEL', 'RISK', 'CONFIG', 'CANCELLED', 'INTERNAL',
    ])
    expect(ENVELOPE_CODES['INTERNAL']).toBeGreaterThan(ENVELOPE_CODES['NETWORK'])
  })
})
