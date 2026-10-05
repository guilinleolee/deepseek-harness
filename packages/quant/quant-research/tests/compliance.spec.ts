import { describe, expect, it, vi } from 'vitest'
import {
  BROKER_MARKERS, collectArgStrings, denialAuditCallback, inspectBarCap, inspectBacktestCaps,
  inspectBrokerMarkers, inspectConfidenceCap, inspectShockCap, inspectToolCall,
  installQuantComplianceGate, recordComplianceDenial,
} from '../src/compliance.ts'
import type { KvTable } from '@deepseek-ai/dsh-storage-domain'
import type { ComplianceDenial, ComplianceDenialId } from '../src/domain/spec.ts'

function rawArgs(args: Record<string, unknown>): ToolExecutionLike {
  return args
}
type ToolExecutionLike = { readonly [key: string]: unknown }

describe('collectArgStrings', () => {
  it('collects nested strings in objects and arrays', () => {
    const strings = collectArgStrings({
      symbol: '000001',
      nested: { note: '帮我实盘下单', list: ['a', 1, ['deep', { deeper: '券商接口' }]] },
      empty: null,
    })
    expect(strings).toContain('000001')
    expect(strings).toContain('帮我实盘下单')
    expect(strings).toContain('券商接口')
    expect(strings).toContain('a')
    expect(strings).toContain('deep')
  })
})

describe('inspectBrokerMarkers', () => {
  it.each(BROKER_MARKERS)('denies the marker %s at any depth', (marker) => {
    const expectedReason: unknown = expect.stringContaining(marker)
    const verdict = inspectBrokerMarkers(rawArgs({ note: { text: `请${marker}买入` } }))
    expect(verdict).toEqual({ kind: 'deny', reason: expectedReason })
  })

  it('allows clean arguments', () => {
    expect(inspectBrokerMarkers(rawArgs({ symbol: '000001', bars: 120 }))).toEqual({ kind: 'allow' })
  })
})

describe('inspectBarCap', () => {
  it('allows an absent bar count', () => {
    expect(inspectBarCap(rawArgs({}))).toEqual({ kind: 'allow' })
  })

  it('allows in-range integers', () => {
    expect(inspectBarCap(rawArgs({ bars: 250 }))).toEqual({ kind: 'allow' })
  })

  it('denies non-integers and out-of-range values', () => {
    expect(inspectBarCap(rawArgs({ bars: 1.5 }))).toMatchObject({ kind: 'deny' })
    expect(inspectBarCap(rawArgs({ bars: 0 }))).toMatchObject({ kind: 'deny' })
    expect(inspectBarCap(rawArgs({ bars: 1501 }))).toMatchObject({ kind: 'deny' })
    expect(inspectBarCap(rawArgs({ bars: 'many' }))).toMatchObject({ kind: 'deny' })
  })
})

describe('inspectBacktestCaps', () => {
  it('allows absent and in-range caps', () => {
    expect(inspectBacktestCaps(rawArgs({}))).toEqual({ kind: 'allow' })
    expect(inspectBacktestCaps(rawArgs({ initial_cash: 100_000, fee_rate: 0.001 }))).toEqual({ kind: 'allow' })
  })

  it('denies cash beyond the hard cap', () => {
    expect(inspectBacktestCaps(rawArgs({ initial_cash: 1e13 }))).toMatchObject({ kind: 'deny' })
    expect(inspectBacktestCaps(rawArgs({ initial_cash: 'lots' }))).toMatchObject({ kind: 'deny' })
  })

  it('denies fee rates beyond the hard cap', () => {
    expect(inspectBacktestCaps(rawArgs({ fee_rate: 0.06 }))).toMatchObject({ kind: 'deny' })
    expect(inspectBacktestCaps(rawArgs({ fee_rate: -0.01 }))).toMatchObject({ kind: 'deny' })
  })
})

describe('inspectConfidenceCap', () => {
  it('allows absent and in-range confidence levels', () => {
    expect(inspectConfidenceCap(rawArgs({}))).toEqual({ kind: 'allow' })
    expect(inspectConfidenceCap(rawArgs({ confidence: 0.95 }))).toEqual({ kind: 'allow' })
  })

  it('denies out-of-range and non-numeric confidence', () => {
    expect(inspectConfidenceCap(rawArgs({ confidence: 0.5 }))).toMatchObject({ kind: 'deny' })
    expect(inspectConfidenceCap(rawArgs({ confidence: 0.999 }))).toMatchObject({ kind: 'deny' })
    expect(inspectConfidenceCap(rawArgs({ confidence: 'high' }))).toMatchObject({ kind: 'deny' })
  })
})

describe('inspectShockCap', () => {
  it('allows absent and in-range shocks', () => {
    expect(inspectShockCap(rawArgs({}))).toEqual({ kind: 'allow' })
    expect(inspectShockCap(rawArgs({ shock: 0.2 }))).toEqual({ kind: 'allow' })
  })

  it('denies out-of-range and non-numeric shocks', () => {
    expect(inspectShockCap(rawArgs({ shock: 0.005 }))).toMatchObject({ kind: 'deny' })
    expect(inspectShockCap(rawArgs({ shock: 0.6 }))).toMatchObject({ kind: 'deny' })
    expect(inspectShockCap(rawArgs({ shock: null }))).toMatchObject({ kind: 'deny' })
  })
})

describe('inspectToolCall', () => {
  it('passes tools outside the plugin namespace', () => {
    expect(inspectToolCall('bash', { command: '实盘下单' })).toEqual({ kind: 'allow' })
  })

  it('passes unknown quant tools untouched', () => {
    expect(inspectToolCall('quant_future_tool', {})).toEqual({ kind: 'allow' })
  })

  it('applies the marker rule to every owned tool', () => {
    for (const name of [
      'quant_get_kline', 'quant_compute_indicator', 'quant_run_backtest',
      'quant_assess_risk', 'quant_stress_test',
    ]) {
      expect(inspectToolCall(name, { note: '实盘' }).kind).toBe('deny')
    }
  })

  it('runs the backtest caps only on the backtest tool', () => {
    expect(inspectToolCall('quant_get_kline', { bars: 999_999 }).kind).toBe('deny')
    expect(inspectToolCall('quant_compute_indicator', { bars: 999_999 }).kind).toBe('deny')
    const verdict = inspectToolCall('quant_run_backtest', { bars: 10, initial_cash: 1e13 })
    const expectedReason: unknown = expect.stringContaining('initial_cash')
    expect(verdict).toMatchObject({ kind: 'deny', reason: expectedReason })
    expect(inspectToolCall('quant_assess_risk', { bars: 10, confidence: 0.5 }).kind).toBe('deny')
    expect(inspectToolCall('quant_stress_test', { bars: 10, shock: 0.9 }).kind).toBe('deny')
    expect(inspectToolCall('quant_get_kline', { confidence: 0.5 })).toEqual({ kind: 'allow' })
  })
})

describe('recordComplianceDenial', () => {
  it('writes one record with the injected id and timestamp', async () => {
    const puts: Array<[string, ComplianceDenial]> = []
    const table = {
      put: vi.fn(async (key: ComplianceDenialId, value: ComplianceDenial) => {
        puts.push([key, value])
      }),
    } as unknown as KvTable<ComplianceDenialId, ComplianceDenial>
    await recordComplianceDenial(
      table,
      { toolName: 'quant_run_backtest', reason: '实盘指令', agentId: 'agent-7' },
      1_700_000_000_000,
      () => 'fixed-id',
    )
    expect(puts).toHaveLength(1)
    expect(puts[0]?.[0]).toBe('fixed-id')
    expect(puts[0]?.[1]).toEqual({
      id: 'fixed-id',
      tool_name: 'quant_run_backtest',
      reason: '实盘指令',
      agent_id: 'agent-7',
      denied_at: 1_700_000_000_000,
    })
  })

  it('omits the agent key when the execution had no agent', async () => {
    const put = vi.fn(async (_key: ComplianceDenialId, _value: ComplianceDenial) => {})
    await recordComplianceDenial(
      { put } as unknown as KvTable<ComplianceDenialId, ComplianceDenial>,
      { toolName: 'quant_get_kline', reason: 'bars 超上限' },
      1,
    )
    expect(put).toHaveBeenCalled()
    const record = put.mock.calls[0]?.[1] as unknown as Record<string, unknown>
    expect('agent_id' in record).toBe(false)
  })
})

describe('denialAuditCallback', () => {
  const table = (put: ReturnType<typeof vi.fn>): KvTable<ComplianceDenialId, ComplianceDenial> =>
    ({ put }) as unknown as KvTable<ComplianceDenialId, ComplianceDenial>

  it('writes one record per denial', async () => {
    const put = vi.fn(async (_key: ComplianceDenialId, _value: ComplianceDenial) => {})
    const warn = vi.fn()
    const audit = denialAuditCallback(table(put), { warn })
    audit('quant_get_kline', 'bars 超上限', 'agent-2')
    await new Promise((resolve) => { setTimeout(resolve, 0) })
    expect(put).toHaveBeenCalledTimes(1)
    expect(warn).not.toHaveBeenCalled()
    expect(put.mock.calls[0]?.[1]).toMatchObject({ tool_name: 'quant_get_kline', reason: 'bars 超上限' })
  })

  it('warns and continues when the audit write fails', async () => {
    const put = vi.fn(async (_key: ComplianceDenialId, _value: ComplianceDenial): Promise<void> => {
      throw new Error('medium unavailable')
    })
    const warn = vi.fn()
    const audit = denialAuditCallback(table(put), { warn })
    audit('quant_run_backtest', '实盘指令')
    await new Promise((resolve) => { setTimeout(resolve, 0) })
    expect(warn).toHaveBeenCalledWith(expect.stringContaining('拒绝审计写入失败'))
  })
})

describe('installQuantComplianceGate', () => {
  function capture(): { listener: (exec: never, next: () => Promise<string>) => Promise<string | { kind: 'deny'; reason: string }>; onDeny: ReturnType<typeof vi.fn> } {
    let captured: ((exec: never, next: () => Promise<string>) => Promise<string | { kind: 'deny'; reason: string }>) | undefined
    const ctx = {
      on: vi.fn((_event: string, fn: never) => {
        captured = fn
        return () => {}
      }),
    } as never
    const onDeny = vi.fn()
    installQuantComplianceGate(ctx, onDeny)
    if (captured === undefined) throw new Error('gate did not register its listener')
    return { listener: captured, onDeny }
  }

  it('delegates calls outside the namespace via next()', async () => {
    const { listener, onDeny } = capture()
    const next = vi.fn(async () => 'delegated')
    const result = await listener({ name: 'bash', arguments: {}, agent: undefined } as never, next)
    expect(result).toBe('delegated')
    expect(next).toHaveBeenCalledTimes(1)
    expect(onDeny).not.toHaveBeenCalled()
  })

  it('allows owned calls that pass every rule', async () => {
    const { listener, onDeny } = capture()
    const next = vi.fn(async () => 'delegated')
    const result = await listener(
      { name: 'quant_get_kline', arguments: { symbol: '000001', bars: 10 }, agent: undefined } as never,
      next,
    )
    expect(result).toBe('delegated')
    expect(onDeny).not.toHaveBeenCalled()
  })

  it('denies owned calls that fail a rule and audits the denial', async () => {
    const { listener, onDeny } = capture()
    const next = vi.fn(async () => 'delegated')
    const result = await listener(
      { name: 'quant_run_backtest', arguments: { symbol: 'x', note: '实盘下单' }, agent: { id: 'agent-1' } } as never,
      next,
    )
    const expectedReason: unknown = expect.stringContaining('实盘')
    expect(result).toMatchObject({ kind: 'deny', reason: expectedReason })
    expect(next).not.toHaveBeenCalled()
    expect(onDeny).toHaveBeenCalledWith('quant_run_backtest', expect.stringContaining('实盘'), 'agent-1')
  })
})
