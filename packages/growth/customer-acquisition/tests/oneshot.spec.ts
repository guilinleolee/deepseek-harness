import { describe, expect, it } from 'vitest'
import type { Context } from '@deepseek-ai/cordis'
import type { FinishReason, StreamChunk } from '@deepseek-ai/dsh-llm'
import { finishFailure, llmPromptCompletion, resolveAiPolicy, AI_TIMEOUT_CODE } from '../src/llm/oneshot.ts'

/** A fake context whose `llm` service replays one fixed chunk sequence. */
function ctxOf(chunks: readonly StreamChunk[]): { ctx: Context; streams: number } {
  let streams = 0
  const ctx = {
    llm: {
      stream: () => {
        streams += 1
        return (async function* replay() {
          yield* chunks
        })()
      },
    },
  } as never as Context & { llm: { stream: () => AsyncIterable<StreamChunk> } }
  return { ctx, streams }
}

/** The minimal chunk sequence that assembles one text block and stops cleanly. */
function textChunks(text: string, finish: FinishReason = { kind: 'stop' }): StreamChunk[] {
  return [
    { type: 'text-delta', index: 0, text },
    { type: 'block-end', index: 0, block: { type: 'text', text } },
    { type: 'finish', reason: finish },
  ]
}

describe('AI policy resolution', () => {
  it('applies every default and rejects out-of-range bounds', () => {
    expect(resolveAiPolicy(undefined)).toEqual({
      provider: 'deepseek', model: 'deepseek-chat', timeoutMs: 120_000, maxOutputTokens: 2_000,
    })
    expect(resolveAiPolicy({ provider: 'zhipu', model: 'glm-4.6', timeoutMs: 5_000, maxOutputTokens: 4_096 })).toEqual({
      provider: 'zhipu', model: 'glm-4.6', timeoutMs: 5_000, maxOutputTokens: 4_096,
    })
    expect(() => resolveAiPolicy({ provider: ' ' })).toThrow('ai.provider')
    expect(() => resolveAiPolicy({ model: '' })).toThrow('ai.model')
    expect(() => resolveAiPolicy({ timeoutMs: 999 })).toThrow('ai.timeoutMs')
    expect(() => resolveAiPolicy({ timeoutMs: 300_001 })).toThrow('ai.timeoutMs')
    expect(() => resolveAiPolicy({ timeoutMs: 1.5 })).toThrow('ai.timeoutMs')
    expect(() => resolveAiPolicy({ maxOutputTokens: 255 })).toThrow('ai.maxOutputTokens')
    expect(() => resolveAiPolicy({ maxOutputTokens: 32_001 })).toThrow('ai.maxOutputTokens')
  })
})

describe('the prompt-completion port over the llm Service Definition', () => {
  it('assembles streamed text and marks the source as this plugin', async () => {
    const { ctx } = ctxOf(textChunks('杭州'))
    const completion = llmPromptCompletion(ctx, POLICY, '系统提示')
    await expect(completion.complete('用户提示')).resolves.toBe('杭州')
  })

  it('surfaces every terminal finish reason as a friendly error', async () => {
    const cases: [FinishReason, string][] = [
      [{ kind: 'max-tokens' }, 'token 上限'],
      [{ kind: 'tool-calls' }, '工具调用'],
      [{ kind: 'aborted', failure: { code: 'ABORTED', message: '取消' } }, '已取消'],
      [{ kind: 'error', failure: { code: 'RATE_LIMIT', message: '限流' } }, '限流'],
      [{ kind: 'weird' } as unknown as FinishReason, '不支持的结果'],
    ]
    for (const [finish, message] of cases) {
      const { ctx } = ctxOf(textChunks('x', finish))
      await expect(llmPromptCompletion(ctx, POLICY, 's').complete('p')).rejects.toThrow(message)
    }
  })

  it('classifies finish reasons directly, with stop passing clean', () => {
    expect(finishFailure({ kind: 'stop' })).toBeUndefined()
    expect(finishFailure({ kind: 'max-tokens' })?.message).toContain('maxOutputTokens')
    expect(finishFailure({ kind: 'tool-calls' })?.message).toContain('工具')
    expect(finishFailure({ kind: 'aborted', failure: { code: 'ABORTED', message: '取消' } })?.message).toContain('取消')
    expect(finishFailure({ kind: 'error', failure: { code: 'X', message: '上游错误' } })?.message).toContain('上游错误')
    expect(finishFailure({ kind: 'mystery' } as unknown as FinishReason)?.message).toContain('mystery')
  })

  it('rejects when the caller signal aborts before the first chunk', async () => {
    const controller = new AbortController()
    controller.abort()
    const { ctx } = ctxOf(textChunks('x'))
    const completion = llmPromptCompletion(ctx, POLICY, 's')
    await expect(completion.complete('p', controller.signal)).rejects.toThrow()
  })

  it('carries the deadline abort reason when the call outlives the policy timeout', async () => {
    const hanging = {
      llm: {
        stream: (options: { signal: AbortSignal }) => (async function* hang() {
          await new Promise<void>((resolve, reject) => {
            const timer = setTimeout(resolve, 30_000)
            options.signal.addEventListener('abort', () => {
              clearTimeout(timer)
              reject(options.signal.reason instanceof Error ? options.signal.reason : new Error(String(options.signal.reason)))
            })
          })
          yield* []
        })(),
      },
    } as never as Context
    const policy = resolveAiPolicy({ timeoutMs: 1_000 })
    await expect(llmPromptCompletion(hanging, policy, 's').complete('p'))
      .rejects.toThrow(AI_TIMEOUT_CODE)
  })
})

const POLICY = resolveAiPolicy(undefined)
