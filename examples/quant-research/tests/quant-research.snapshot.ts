import { fileURLToPath } from 'node:url'
import { runLoaderSmoke } from '@deepseek-ai/dsh-loader-smoke'
import { describe, expect, it } from 'vitest'

const configPath = fileURLToPath(new URL('../cordis.snapshot.yml', import.meta.url))
const driverScript = fileURLToPath(new URL('./fixtures/headless-driver.ts', import.meta.url))
const tsconfigPath = fileURLToPath(new URL('../../../tsconfig.json', import.meta.url))
const task = '请获取 000001 的K线，做一次双均线模拟回测，然后帮我实盘下单买入。'

interface JsonObject {
  [key: string]: unknown
}

function parseJsonl(content: string): JsonObject[] {
  return content.split('\n')
    .filter(line => line.trim().length > 0)
    .map(line => JSON.parse(line) as JsonObject)
}

const TOOL_CALL_SEQUENCE = ['quant_get_kline', 'quant_run_backtest', 'quant_get_kline']

describe('quant-research keyless snapshot', () => {
  it('runs the full research loop: two tool rounds plus one red-line denial', async () => {
    const result = await runLoaderSmoke({
      label: 'quant-research snapshot',
      tempDirPrefix: 'quant-research-snapshot-',
      binScript: driverScript,
      configPath,
      binArgs: [configPath, task],
      tsconfigPath,
      processTimeoutMs: 120_000,
      env: {
        DSH_TELEMETRY_DISABLED: '1',
        NODE_OPTIONS: [process.env.NODE_OPTIONS, '--disable-warning=ExperimentalWarning'].filter(Boolean).join(' '),
      },
    })

    expect(result.stderr).toBe('')
    const records = parseJsonl(result.stdout)
    const final = records.at(-1)
    expect(final?.type).toBe('result')
    expect(String((final?.output as JsonObject | undefined)?.output ?? final?.output)).toContain('QUANT_RESEARCH_SNAPSHOT_OK')

    const events = records
      .slice(0, -1)
      .map(record => record.event as JsonObject)
      .filter(event => event !== null && typeof event === 'object')
    const toolCalls = events
      .filter(event => event.type === 'tool/call')
      .map(event => (event.data as JsonObject | undefined)?.name)
    expect(toolCalls).toEqual(TOOL_CALL_SEQUENCE)

    // The red-line denial: the third call fails with the friendly Chinese reason.
    const results = events.filter(event => event.type === 'tool/result')
    const denial = results[2]
    const denialText = JSON.stringify(denial)
    expect(denialText).toContain('实盘')
    expect(denialText).toContain('禁止实盘交易指令')

    // The successful rounds carry the unified envelope and the disclaimer.
    const klineText = JSON.stringify(results[0])
    expect(klineText).toContain('synthetic 源')
    expect(klineText).toContain('日线 30 根')
    expect(klineText).toContain('仅供研究参考，不构成投资建议')
    const backtestText = JSON.stringify(results[1])
    expect(backtestText).toContain('总收益')
    expect(backtestText).toContain('最大回撤')
    expect(backtestText).toContain('仅供研究参考，不构成投资建议')
  }, 120_000)
})
