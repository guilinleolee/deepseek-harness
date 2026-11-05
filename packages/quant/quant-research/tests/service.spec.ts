import { describe, expect, it } from 'vitest'
import { AccountId } from '../src/domain/spec.ts'
import { setupHarness } from './service-helpers.ts'

const account = (name: string, positions: { symbol: string; shares: number; avg_cost: number }[] = []) => ({
  id: AccountId(`id-${name}`),
  name,
  cash: 500_000,
  initial_cash: 1_000_000,
  positions,
  created_at: 1_700_000_000_000,
  updated_at: 1_700_000_000_000,
})

describe('QuantResearchService over the real storage domain', () => {
  it('lists accounts sorted by name and projects equity from positions', async () => {
    const harness = await setupHarness()
    try {
      await harness.seedAccount(account('研究二号'))
      await harness.seedAccount(account('研究一号', [{ symbol: '000001', shares: 1_000, avg_cost: 10 }]))
      const { accounts } = await harness.service.listAccountsRemote()
      expect(accounts.map(a => a.name).sort()).toEqual(['研究一号', '研究二号'])
      const positioned = accounts.find(a => a.name === '研究一号')
      expect(positioned).toMatchObject({ cash: 500_000, equity: 510_000 })
      expect(positioned?.positions).toEqual([{ symbol: '000001', shares: 1_000, avg_cost: 10, market_value: 10_000 }])
    } finally {
      await harness.dispose()
    }
  })

  it('reads one account by id, by name, and fails loud on a miss', async () => {
    const harness = await setupHarness()
    try {
      await harness.seedAccount(account('研究一号'))
      const byId = await harness.service.getAccountStateRemote({ account_id: 'id-研究一号' })
      expect(byId.name).toBe('研究一号')
      const byName = await harness.service.getAccountStateRemote({ name: '研究一号' })
      expect(byName.account_id).toBe('id-研究一号')
      await expect(harness.service.getAccountStateRemote({ name: '不存在' }))
        .rejects.toThrow('未找到账户')
    } finally {
      await harness.dispose()
    }
  })

  it('lists notes newest-first with symbol null and tags copied', async () => {
    const harness = await setupHarness()
    try {
      await harness.seedNote({ title: '第一篇', body: 'b1', symbol: '000001', tags: ['strategy'] })
      await harness.seedNote({ title: '第二篇', body: 'b2' })
      const { notes } = await harness.service.listNotesRemote()
      expect(notes).toHaveLength(2)
      expect(notes[0]?.title).toBe('第二篇')
      expect(notes[0]?.symbol).toBeNull()
      expect(notes[1]).toMatchObject({ title: '第一篇', symbol: '000001', tags: ['strategy'] })
    } finally {
      await harness.dispose()
    }
  })

  it('returns empty projections for an empty domain', async () => {
    const harness = await setupHarness()
    try {
      const accounts = await harness.service.listAccountsRemote()
      const notes = await harness.service.listNotesRemote()
      const snapshots = await harness.service.listResultSnapshotsRemote()
      expect(accounts).toEqual({ accounts: [] })
      expect(notes).toEqual({ notes: [] })
      expect(snapshots).toEqual({ snapshots: [] })
    } finally {
      await harness.dispose()
    }
  })

  it('lists result snapshots newest first without equity points and reads one curve', async () => {
    const harness = await setupHarness()
    try {
      await harness.seedSnapshot('000001', 'r-old', 1_000)
      await harness.seedSnapshot('600519', 'r-new', 2_000)
      const { snapshots } = await harness.service.listResultSnapshotsRemote()
      expect(snapshots.map(s => s.result_id)).toEqual(['r-new', 'r-old'])
      expect(snapshots[0]).toMatchObject({
        symbol: '600519',
        params: { fast: 3, slow: 10, bars: 60, initial_cash: 100_000, fee_rate: 0.0005 },
        metrics: { total_return: 0.05, trade_count: 4, final_equity: 105_000 },
        created_at: 2_000,
      })
      expect(snapshots[0]).not.toHaveProperty('equity')

      const curve = await harness.service.getEquityCurveRemote({ result_id: 'r-old' })
      expect(curve).toMatchObject({
        result_id: 'r-old',
        symbol: '000001',
        equity: [{ date: '2024-01-01', value: 100_000 }, { date: '2024-01-02', value: 105_000 }],
      })
      await expect(harness.service.getEquityCurveRemote({ result_id: 'missing' }))
        .rejects.toThrow('未找到回测快照')
    } finally {
      await harness.dispose()
    }
  })
})
