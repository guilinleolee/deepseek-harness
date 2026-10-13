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

const TOOL_CALL_SEQUENCE = [
  'quant_get_kline', 'quant_run_backtest', 'quant_assess_risk', 'quant_stress_test',
  'quant_compute_factor',
  'quant_get_kline',
]

describe('quant-research keyless snapshot', () => {
  it('runs the full research loop: five tool rounds plus one red-line denial', async () => {
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
    const resultIndex = records.findIndex(record => record.type === 'result')
    const final = records[resultIndex]
    expect(final).toBeDefined()
    expect(String((final?.output as JsonObject | undefined)?.output ?? final?.output)).toContain('QUANT_RESEARCH_SNAPSHOT_OK')

    const events = records
      .slice(0, resultIndex)
      .map(record => record.event as JsonObject)
      .filter(event => event !== null && typeof event === 'object')
    const toolCalls = events
      .filter(event => event.type === 'tool/call')
      .map(event => (event.data as JsonObject | undefined)?.name)
    expect(toolCalls).toEqual(TOOL_CALL_SEQUENCE)

    // The red-line denial: the fifth call fails with the friendly Chinese reason.
    const results = events.filter(event => event.type === 'tool/result')
    const denial = results[5]
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
    const riskText = JSON.stringify(results[2])
    expect(riskText).toContain('历史模拟法')
    expect(riskText).toContain('VaR')
    const stressText = JSON.stringify(results[3])
    expect(stressText).toContain('压力测试')
    expect(stressText).toContain('crash')
    expect(stressText).toContain('冲击 20.00%')
    const factorText = JSON.stringify(results[4])
    expect(factorText).toContain('momentum')
    expect(factorText).toContain('仅供研究参考')

    // The driver-phase optimize round: one real background job through the
    // composed jobs registry, plus one grid-cap denial through the gate.
    const optimizeCheck = records.find(record => record.type === 'quant-optimize-check')
    expect(optimizeCheck).toBeDefined()
    expect(optimizeCheck?.code).toBe(0)
    expect(optimizeCheck?.combos).toBe(16)
    expect(String(optimizeCheck?.jobId)).toMatch(/^quant-optimize-\d+$/)
    expect(String(optimizeCheck?.startText)).toContain('共 16 组合')
    expect(String(optimizeCheck?.jobText)).toContain('[status: completed')
    expect(String(optimizeCheck?.jobText)).toContain('# 参数寻优报告：000001')
    expect(String(optimizeCheck?.jobText)).toContain('过拟合风险')
    expect(String(optimizeCheck?.jobText)).toContain('仅供研究参考')
    expect(String(optimizeCheck?.deniedText)).toContain('合规硬上限')

    // The driver-phase walk-forward round: one real background job that
    // splits, runs the grid on train, picks the best, and runs one backtest
    // on test — plus one train-ratio denial through the gate.
    const wfCheck = records.find(record => record.type === 'quant-walk-forward-check')
    expect(wfCheck).toBeDefined()
    expect(wfCheck?.code).toBe(0)
    expect(wfCheck?.combos).toBe(16)
    expect(wfCheck?.trainRatio).toBe(0.7)
    expect(String(wfCheck?.jobId)).toMatch(/^quant-walk-forward-\d+$/)
    expect(String(wfCheck?.startText)).toContain('训练 70% / 测试 30%')
    expect(String(wfCheck?.jobText)).toContain('[status: completed')
    expect(String(wfCheck?.jobText)).toContain('# Walk-forward 验证报告：000001')
    expect(String(wfCheck?.jobText)).toContain('过拟合差距')
    expect(String(wfCheck?.jobText)).toContain('仅供研究参考')
    expect(String(wfCheck?.deniedText)).toContain('train_ratio')
  }, 180_000)
})
