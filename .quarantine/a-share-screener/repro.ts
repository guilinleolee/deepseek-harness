import { ScreenerService } from './src/service.ts'
import { openMemoryStore } from './src/cache/cache.ts'
import { StrategyRegistry } from './src/strategies/registry.ts'
import { runScreening } from './src/tools/screen.ts'
import { credentialRef } from '@deepseek-ai/dsh-credentials'
import type { OHLCV, StockBasicInfo, Filter } from './src/types.ts'

async function main() {
  const store = openMemoryStore()
  store.bootstrap()
  const stock: StockBasicInfo = { symbol: '000001.SZ', name: 'A', market: 'SZ', industry: 'X', listDate: new Date('1991-04-03'), isST: false, isSuspended: false }
  const bar: OHLCV = { date: new Date('2025-01-02'), open: 10, high: 11, low: 9, close: 10.5, volume: 1e6, amount: 1e7 }
  store.putStock(stock)
  store.putBar(stock.symbol, bar)
  const reg = new StrategyRegistry()
  const f = ((() => ({ passed: true, score: 5, evidence: ['ok'] })) as unknown) as Filter
  ;(f as Filter & { displayName: string }).displayName = 'a'
  reg.register({ id: 'all-pass', label: 'all-pass', filters: [f] })
  const svc = new ScreenerService({
    cacheRoot: '.',
    defaultLimit: 10,
    defaultUniverse: { kind: 'all' },
    jobOutputLimitBytes: 1024,
    tokenRef: credentialRef('TUSHARE_TOKEN'),
    store,
    registry: reg,
  })
  console.log('registered:', svc.strategies.list().map((s) => s.id))
  const hooks = runScreening(svc, 'all-pass', { kind: 'all' }, 10, new AbortController().signal)
  const out = await hooks.done
  console.log('output:', out.output)
}

main()
