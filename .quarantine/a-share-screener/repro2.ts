import { ScreenerService } from './src/service.ts'
import { openMemoryStore } from './src/cache/cache.ts'
import { StrategyRegistry } from './src/strategies/registry.ts'
import { runScreening } from './src/tools/screen.ts'
import { credentialRef } from '@deepseek-ai/dsh-credentials'

async function main() {
  const store = openMemoryStore()
  store.bootstrap()
  store.putStock({ symbol: '000001.SZ', name: 'A', market: 'SZ', industry: 'X', listDate: new Date('1991-04-03'), isST: false, isSuspended: false })
  store.putBar('000001.SZ', { date: new Date('2025-01-02'), open: 10, high: 11, low: 9, close: 10.5, volume: 1e6, amount: 1e7 })
  const reg = new StrategyRegistry()
  reg.register({ id: 'all-pass', label: 'all-pass', filters: [() => ({ passed: true, score: 5, evidence: ['ok'] })] })
  const svc = new ScreenerService({ cacheRoot: '.', defaultLimit: 10, defaultUniverse: { kind: 'all' }, jobOutputLimitBytes: 1024, tokenRef: credentialRef('TUSHARE_TOKEN'), store, registry: reg })
  const strategy = svc.strategies.get('all-pass')
  console.log('strategy:', strategy?.filters.length)
  const filters = strategy?.filters ?? []
  for (const f of filters) console.log('filter outcome:', f({ stock: { symbol: 'X', name: 'X', market: 'SZ', industry: 'X', listDate: new Date(), isST: false, isSuspended: false }, bars: [], quote: { symbol: 'X', price: 0, change: 0, changePercent: 0, volume: 0, amount: 0, timestamp: new Date() } }))
  const hooks = runScreening(svc, 'all-pass', { kind: 'all' }, 10, new AbortController().signal)
  const out = await hooks.done
  console.log('output:', out.output)
}

main()
