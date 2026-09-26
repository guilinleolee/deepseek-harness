import { mkdtemp, readFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterAll, describe, expect, it } from 'vitest'
import {
  CREATE_QUOTA_FILENAME, CreateQuotaError, CreateQuotaGate, localDayKey, normalizeQuotaState, resolveQuotaConfig,
} from '../src/create/quota.ts'
import type { CreateQuotaConfig } from '../src/create/quota.ts'

const dirs: string[] = []

afterAll(async () => {
  await Promise.all(dirs.map(dir => rm(dir, { recursive: true, force: true })))
})

describe('resolveQuotaConfig', () => {
  it('applies the defaults and validates the bounds', () => {
    expect(resolveQuotaConfig({})).toEqual({ freeDailyGenerates: 10, freeDailyRewrites: 50, paidTierEnabled: false })
    expect(() => resolveQuotaConfig({ freeDailyGenerates: -1 })).toThrow('freeDailyGenerates')
    expect(() => resolveQuotaConfig({ freeDailyGenerates: 1001 })).toThrow('freeDailyGenerates')
    expect(() => resolveQuotaConfig({ freeDailyRewrites: 5001 })).toThrow('freeDailyRewrites')
  })
})

describe('localDayKey and normalizeQuotaState', () => {
  it('formats the local day and resets on any other day or shape', () => {
    expect(localDayKey(new Date(2026, 8, 5))).toBe('2026-09-05')
    expect(normalizeQuotaState(null, '2026-09-25')).toEqual({ date: '2026-09-25', generates: 0, rewrites: 0 })
    expect(normalizeQuotaState({ date: '2026-09-24', generates: 9, rewrites: 9 }, '2026-09-25')).toEqual({ date: '2026-09-25', generates: 0, rewrites: 0 })
    expect(normalizeQuotaState({ date: '2026-09-25', generates: 3, rewrites: 'x' }, '2026-09-25')).toEqual({ date: '2026-09-25', generates: 3, rewrites: 0 })
    expect(normalizeQuotaState({ date: '2026-09-25', generates: -4, rewrites: 2 }, '2026-09-25')).toEqual({ date: '2026-09-25', generates: 0, rewrites: 2 })
  })
})

describe('CreateQuotaGate', () => {
  async function makeGate(config: CreateQuotaConfig = {}): Promise<{ gate: CreateQuotaGate; root: string }> {
    const root = await mkdtemp(join(tmpdir(), 'dsh-create-quota-'))
    dirs.push(root)
    return { gate: new CreateQuotaGate(root, config), root }
  }

  it('accumulates counters and rejects once the free daily budget is spent', async () => {
    const { gate, root } = await makeGate({ freeDailyGenerates: 2, freeDailyRewrites: 1 })
    await gate.consumeGenerate(1)
    await gate.consumeGenerate(1)
    await expect(gate.consumeGenerate(1)).rejects.toThrow(CreateQuotaError)
    const stored = JSON.parse(await readFile(join(root, CREATE_QUOTA_FILENAME), 'utf8')) as { generates?: number; rewrites?: number }
    expect(stored).toMatchObject({ generates: 2, rewrites: 0 })
    await gate.consumeRewrite()
    await expect(gate.consumeRewrite()).rejects.toThrow('rewrite budget')
  })

  it('charges a batch by its units and lets the paid tier bypass both counters', async () => {
    const { gate } = await makeGate({ freeDailyGenerates: 3 })
    await gate.consumeGenerate(3)
    await expect(gate.consumeGenerate(1)).rejects.toThrow('generation budget')
    const paid = new CreateQuotaGate((await mkdtemp(join(tmpdir(), 'dsh-create-quota-'))), {
      freeDailyGenerates: 0, freeDailyRewrites: 0, paidTierEnabled: true,
    })
    await paid.consumeGenerate(5)
    await paid.consumeRewrite()
  })

  it('gates the paid-tier features behind the switch', async () => {
    const free = await makeGate({})
    await expect(free.gate.requirePaidFeature('batch')).rejects.toThrow('paid tier is not enabled: batch')
    await expect(free.gate.requirePaidFeature('evaluation')).rejects.toThrow('not enabled: evaluation')
    const paid = await makeGate({ paidTierEnabled: true })
    await expect(paid.gate.requirePaidFeature('batch')).resolves.toBeUndefined()
  })
})
