import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { Context } from '@deepseek-ai/cordis'
import Storage from '@deepseek-ai/dsh-storage'
import * as StorageJson from '@deepseek-ai/dsh-storage-json'
import * as StorageDomain from '@deepseek-ai/dsh-storage-domain'
import { QuantResearchService } from '../src/service.ts'
import { saveNote } from '../src/pet/notes.ts'
import { saveSnapshot } from '../src/pcpt/snapshots.ts'
import type { Account, BacktestReport } from '../src/index.ts'
import type { ResultSnapshot } from '../src/domain/spec.ts'

export interface Harness {
  readonly ctx: Context
  readonly service: QuantResearchService
  seedAccount(account: Account): Promise<void>
  seedNote(input: { title: string; body: string; symbol?: string; tags?: string[] }): Promise<void>
  seedSnapshot(symbol: string, id: string, createdAt: number, report?: Partial<BacktestReport>): Promise<ResultSnapshot>
  dispose(): Promise<void>
}

/** Compose the real storage stack and the service over it. */
export async function setupHarness(): Promise<Harness> {
  const root = await mkdtemp(join(tmpdir(), 'dsh-quant-service-test-'))
  const ctx = new Context()
  try {
    await ctx.plugin(Storage)
    await ctx.plugin(StorageJson, { root })
    await ctx.plugin(StorageDomain, { backend: 'json' })
    await ctx.plugin(QuantResearchService).await()
    const service = ctx.quantResearch
    // Seed through the service's own domain handle: the reservation is
    // single-open, so a second open() would trip 'already-open'.
    const domain = service.requireDomain()
    return {
      ctx,
      service,
      async seedAccount(account) {
        await domain.table('accounts').put(account.id, account)
      },
      async seedNote(input) {
        await saveNote(domain.table('research_notes'), input)
      },
      async seedSnapshot(symbol, id, createdAt, reportOverrides) {
        const full: BacktestReport = {
          symbol,
          fast: 3,
          slow: 10,
          initial_cash: 100_000,
          final_equity: 105_000,
          equity: [{ date: '2024-01-01', value: 100_000 }, { date: '2024-01-02', value: 105_000 }],
          trades: [],
          metrics: { total_return: 0.05, annual_return: 0.4, max_drawdown: 0.03, sharpe: 1.2, win_rate: 0.6, trade_count: 4 },
          ...reportOverrides,
        }
        return await saveSnapshot(
          domain.table('result_snapshots'),
          { symbol, params: { fast: 3, slow: 10, bars: 60, initialCash: 100_000, feeRate: 0.0005 }, report: full },
          createdAt,
          () => id,
        )
      },
      async dispose() {
        await ctx.fiber.dispose()
        await rm(root, { recursive: true, force: true })
      },
    }
  } catch (error) {
    await ctx.fiber.dispose()
    await rm(root, { recursive: true, force: true })
    throw error
  }
}
