/**
 * One-shot model calls behind the plugin's internal AI faces (lead field
 * extraction and AI lead scoring). Calls ride the shared `llm` Service
 * Definition — no new model interface. The provider route is deployment
 * policy: declared in the bundle-row config (`config.ai`), validated here,
 * never hardcoded per call. One call = one deadline; the caller's
 * cancellation signal composes in through `deadline`'s upstream input.
 * @module @deepseek-ai/dsh-customer-acquisition/llm/oneshot
 */

import type { Context } from '@deepseek-ai/cordis'
import { BlockAssembler, createUserMessage, LlmError } from '@deepseek-ai/dsh-llm'
import { deepFreeze } from '@deepseek-ai/dsh-util-values'
import type { FinishReason, GenerateOptions } from '@deepseek-ai/dsh-llm'
import { deadline } from '@deepseek-ai/dsh-timeout'

/** Abort reason code carried by an AI call that outlived its deadline. */
export const AI_TIMEOUT_CODE = 'CUSTOMER_ACQUISITION_AI_TIMEOUT'

/** Deployment policy for the plugin's internal model calls (row config `ai`). */
export interface AiPolicyConfig {
  /** Registered LLM provider route; defaults to `deepseek`. */
  readonly provider?: string
  /** Model id within the provider route; defaults to `deepseek-chat`. */
  readonly model?: string
  /** End-to-end call deadline in milliseconds (1000–300000); defaults to 120000. */
  readonly timeoutMs?: number
  /** Model-output token cap for one call (256–32000); defaults to 2000. */
  readonly maxOutputTokens?: number
}

/** Validated policy after explicit default resolution. */
export interface ResolvedAiPolicy {
  provider: string
  model: string
  timeoutMs: number
  maxOutputTokens: number
}

/** Bounds of the per-call deadline and output cap. */
export const AI_TIMEOUT_MS_MIN = 1_000
/** Bounds of the per-call deadline and output cap. */
export const AI_TIMEOUT_MS_MAX = 300_000
/** Bounds of the per-call deadline and output cap. */
export const AI_MAX_OUTPUT_TOKENS_MIN = 256
/** Bounds of the per-call deadline and output cap. */
export const AI_MAX_OUTPUT_TOKENS_MAX = 32_000

/**
 * Resolve the declared AI policy into its validated form, defaults applied.
 * @param config - the declared row policy; every field optional.
 * @returns the validated policy, fail loud on out-of-range values.
 */
export function resolveAiPolicy(config: AiPolicyConfig | undefined): ResolvedAiPolicy {
  const provider = config?.provider ?? 'deepseek'
  const model = config?.model ?? 'deepseek-chat'
  const timeoutMs = config?.timeoutMs ?? 120_000
  const maxOutputTokens = config?.maxOutputTokens ?? 2_000
  if (provider.trim().length === 0) throw new Error('customer-acquisition ai.provider 不能为空')
  if (model.trim().length === 0) throw new Error('customer-acquisition ai.model 不能为空')
  if (!Number.isInteger(timeoutMs) || timeoutMs < AI_TIMEOUT_MS_MIN || timeoutMs > AI_TIMEOUT_MS_MAX) {
    throw new Error(`customer-acquisition ai.timeoutMs 必须是 ${AI_TIMEOUT_MS_MIN}-${AI_TIMEOUT_MS_MAX} 的整数`)
  }
  if (!Number.isInteger(maxOutputTokens)
    || maxOutputTokens < AI_MAX_OUTPUT_TOKENS_MIN
    || maxOutputTokens > AI_MAX_OUTPUT_TOKENS_MAX) {
    throw new Error(
      `customer-acquisition ai.maxOutputTokens 必须是 ${AI_MAX_OUTPUT_TOKENS_MIN}-${AI_MAX_OUTPUT_TOKENS_MAX} 的整数`,
    )
  }
  return { provider, model, timeoutMs, maxOutputTokens }
}

/**
 * The plugin's AI faces speak one prompt-completion port; the service layer
 * renders prompts and parses JSON, this port only turns text into text. The
 * optional per-call signal composes into the call deadline's upstream.
 */
export interface PromptCompletion {
  /**
   * Run one model call with the given user prompt and return its text output.
   * @param prompt - the complete user-prompt text.
   * @param signal - caller cancellation signal, when the call has one.
   * @returns the model's text output.
   */
  complete(prompt: string, signal?: AbortSignal): Promise<string>
}

/**
 * Terminal model finish reasons that mean the call failed, surfaced as
 * friendly Chinese errors because tool callers see them verbatim.
 * @param finish - the model call's finish reason.
 * @returns the failure as an `Error`, or undefined for a clean `stop`.
 */
export function finishFailure(finish: FinishReason): Error | undefined {
  switch (finish.kind) {
    case 'stop': return undefined
    case 'max-tokens': return new Error('模型输出达到 token 上限被截断，请重试或调大 ai.maxOutputTokens')
    case 'tool-calls': return new Error('模型意外请求了工具调用，AI 处理失败')
    case 'aborted': return new Error('模型调用已取消')
    case 'error': return new Error(`模型调用失败：${finish.failure.message}`)
    default: return new Error(`模型调用返回了不支持的结果（${String((finish as { kind?: unknown }).kind)}）`)
  }
}

/**
 * Build the production {@link PromptCompletion}: one framed call per
 * `complete`, streaming text out under the configured policy.
 * @param ctx - context exposing the registered LLM service.
 * @param policy - the validated call policy.
 * @param system - the face's fixed system prompt (output contract).
 * @returns the completion port.
 */
export function llmPromptCompletion(
  ctx: Context,
  policy: ResolvedAiPolicy,
  system: string,
): PromptCompletion {
  return {
    async complete(prompt: string, signal?: AbortSignal): Promise<string> {
      const messages = [createUserMessage({
        content: [{ type: 'text', text: prompt }],
        source: { kind: 'user' },
      })]
      using callDeadline = deadline(signal, policy.timeoutMs, AI_TIMEOUT_CODE)
      const options: GenerateOptions = deepFreeze({
        provider: policy.provider,
        model: policy.model,
        messages,
        system,
        maxTokens: policy.maxOutputTokens,
        signal: callDeadline.signal,
      })
      const assembler = new BlockAssembler()
      for await (const chunk of ctx.llm.stream(options)) {
        callDeadline.signal.throwIfAborted()
        assembler.push(chunk)
      }
      callDeadline.signal.throwIfAborted()
      const failure = finishFailure(assembler.finish)
      if (failure !== undefined) throw failure
      const blocks = assembler.blocks()
      return blocks
        .filter((block): block is Extract<(typeof blocks)[number], { type: 'text' }> => block.type === 'text')
        .map(block => block.text)
        .join(' ')
    },
  }
}

/** Re-exported so callers can recognize rate-limit failures without importing dsh-llm. */
export { LlmError }
