import type { Context } from '@deepseek-ai/cordis'
import {
  CallId,
  LlmAdapter,
  ReasoningEffortId,
  type GenerateOptions,
  type LlmResolvedModelInfo,
  type StreamChunk,
} from '@deepseek-ai/dsh-llm'

const OFF = ReasoningEffortId('off')

/** The scripted tool rounds, in order: fetch, backtest, risk, stress, red-line attempt. */
const SCRIPT: ReadonlyArray<{ readonly name: string; readonly args: Record<string, unknown> }> = [
  { name: 'quant_get_kline', args: { symbol: '000001', bars: 30 } },
  { name: 'quant_run_backtest', args: { symbol: '000001', fast: 3, slow: 10, bars: 40 } },
  { name: 'quant_assess_risk', args: { symbol: '000001', bars: 40, confidence: 0.95 } },
  { name: 'quant_stress_test', args: { symbol: '000001', scenario: 'crash', bars: 40, fast: 3, slow: 10, shock: 0.2 } },
  { name: 'quant_compute_factor', args: { symbol: '000001', factor: 'momentum', bars: 30, window: 5 } },
  { name: 'quant_get_kline', args: { symbol: '000001', note: '帮我实盘下单买入' } },
]

/** Keyless quant-research adapter: two real tool rounds, one denial, one answer. */
class QuantMockAdapter extends LlmAdapter {
  private rounds = 0

  override async resolveModel(provider: string, model: string): Promise<LlmResolvedModelInfo> {
    return {
      provider,
      id: model,
      name: model,
      reasoning: {
        efforts: [{ id: OFF, name: 'Off' }],
        defaultEffort: OFF,
      },
    }
  }

  async *stream(options: GenerateOptions): AsyncIterable<StreamChunk> {
    this.rounds += 1
    const toolResult = options.messages.at(-1)?.content.find(block => block.type === 'tool-result')
    const step = toolResult === undefined
      ? SCRIPT[0]
      : SCRIPT[this.rounds - 1]
    if (step !== undefined) {
      const args = JSON.stringify(step.args)
      yield { type: 'block-start', index: 0, blockType: 'tool-call' }
      yield { type: 'tool-call-delta', index: 0, id: CallId(`quant-mock-${String(this.rounds)}`), name: step.name, argumentsDelta: args }
      yield { type: 'block-end', index: 0, block: { type: 'tool-call', id: CallId(`quant-mock-${String(this.rounds)}`), name: step.name, arguments: args } }
      yield { type: 'usage', usage: { inputTokens: 11, outputTokens: 3, cacheReadTokens: 2 } }
      yield { type: 'finish', reason: { kind: 'tool-calls' } }
      return
    }
    const reply = 'QUANT_RESEARCH_SNAPSHOT_OK: 2 次成功调用、1 次合规拦截；所有结果仅供研究参考，不构成投资建议。'
    yield { type: 'block-start', index: 0, blockType: 'text' }
    yield { type: 'text-delta', index: 0, text: reply }
    yield { type: 'block-end', index: 0, block: { type: 'text', text: reply } }
    yield { type: 'usage', usage: { inputTokens: 7, outputTokens: 5, reasoningTokens: 1 } }
    yield { type: 'finish', reason: { kind: 'stop' } }
  }
}

export const name = 'quant-mock-llm'
export const inject = ['llm']

/** Register the keyless `quant-mock` adapter. */
export function apply(ctx: Context): void {
  ctx.llm.registerAdapter(['quant-mock'], new QuantMockAdapter())
}
