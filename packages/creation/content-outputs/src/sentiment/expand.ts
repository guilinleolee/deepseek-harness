/**
 * The keyword-expansion middleware: before a scan's platform searches run,
 * one LLM call widens the task's subjects into the search variants real
 * posters actually use (colloquialisms, model nicknames, common misspellings,
 * competitor spellings). The output is a wire boundary — model text is
 * parsed defensively and any unusable answer degrades to the subject itself,
 * never to a failed scan. A per-task cache keeps the cost at one call per
 * day instead of one per scan.
 */

import type { SentimentTask } from './types.ts'
import { streamLlmText, type AiCallPolicy } from '../gather/ai.ts'
import type { Context } from '@deepseek-ai/cordis'

/** Prompt version of the keyword-expansion face. */
export const SENTIMENT_EXPAND_PROMPT_VERSION = 'sentiment-expand@1'

/** Character cap of one expanded search term (mirrors the term cap of a task). */
export const SENTIMENT_EXPAND_TERM_CAP = 100

/** Expanded terms kept at most; the rest is dropped. */
export const SENTIMENT_EXPAND_CAP = 8

/** How many of the expanded terms each platform search consumes per scan. */
export const SENTIMENT_EXPAND_SEARCH_TERMS = 3

/** Cache lifetime of one expansion per task, in milliseconds. */
export const SENTIMENT_EXPAND_TTL_MS = 24 * 60 * 60 * 1000

/** Timeout reason code carried by aborted sentiment LLM calls. */
const EXPAND_AI_TIMEOUT_CODE = 'SENTIMENT_AI_TIMEOUT'

const EXPAND_SYSTEM_PROMPT = [
  '你是企业舆情监控助手。给出要监控的公司/品牌/产品（监控主体），',
  '输出网友在社交平台讨论它们时最可能使用的搜索词变体：口语叫法、产品昵称、常见别名、易混淆的同类词。',
  '要求：',
  '- 只输出一个 JSON 对象，形如 {"terms":["变体1","变体2",...]}；',
  '- 变体必须包含原始主体本身的写法，总数量 3-8 个；',
  '- 每个变体不超过 20 个字，不要解释，不要输出其他任何文字。',
].join('\n')

/** Injection face for tests: the LLM call defaults to the shared one. */
export interface ExpandDeps {
  readonly now?: () => number
  /** The expansion LLM call; injectable for tests. */
  readonly expand?: typeof expandWithLlm
}

/** One cached expansion per task+subjects key. */
const cache = new Map<string, { readonly terms: readonly string[]; readonly at: number }>()

/**
 * Parse the model answer into search terms: a JSON object with a string
 * array under `terms`, each trimmed, capped, deduplicated (case-folded),
 * and never empty. An unusable body yields an empty array — the caller
 * falls back to the raw subjects.
 * @param text - exact model text output.
 */
export function parseExpandOutput(text: string): readonly string[] {
  const stripped = text.trim().replace(/^```(?:json)?\s*/u, '').replace(/\s*```$/u, '')
  const start = stripped.indexOf('{')
  const end = stripped.lastIndexOf('}')
  if (start === -1 || end <= start) return []
  let parsed: unknown
  try {
    parsed = JSON.parse(stripped.slice(start, end + 1))
  } catch {
    return []
  }
  if (typeof parsed !== 'object' || parsed === null) return []
  const terms = (parsed as Record<string, unknown>).terms
  if (!Array.isArray(terms)) return []
  const seen = new Set<string>()
  const result: string[] = []
  for (const raw of terms) {
    if (typeof raw !== 'string') continue
    const term = raw.trim()
    const key = term.toLowerCase()
    if (term.length === 0 || term.length > SENTIMENT_EXPAND_TERM_CAP || seen.has(key)) continue
    seen.add(key)
    result.push(term)
    if (result.length >= SENTIMENT_EXPAND_CAP) break
  }
  return result
}

/** One LLM expansion call, kept injectable so tests can stub the model. */
export async function expandWithLlm(
  ctx: Context,
  policy: AiCallPolicy,
  subjects: readonly string[],
): Promise<readonly string[]> {
  const framed = subjects.join('、')
  const output = await streamLlmText(ctx, policy, EXPAND_SYSTEM_PROMPT, framed, EXPAND_AI_TIMEOUT_CODE)
  return parseExpandOutput(output)
}

/**
 * Expand one task's subjects into platform search terms, cached per task
 * for a day. Any failure (timeout, unusable model body, empty output)
 * degrades to the raw subjects, so a scan never fails or skips a source
 * because of this stage.
 * @param ctx - context exposing the registered llm service.
 * @param policy - the resolved AI call policy.
 * @param task - the task whose subjects to widen.
 * @param deps - injected clock for tests.
 * @returns the search terms; at least one, at most `SENTIMENT_EXPAND_CAP`.
 */
export async function expandTaskTerms(
  ctx: Context,
  policy: AiCallPolicy,
  task: SentimentTask,
  deps: ExpandDeps = {},
): Promise<readonly string[]> {
  const fallback = task.subjects.length > 0 ? task.subjects.slice(0, SENTIMENT_EXPAND_CAP) : []
  if (fallback.length === 0) return fallback
  const now = deps.now?.() ?? Date.now()
  const key = `${task.id}:${task.updatedAt}`
  const cached = cache.get(key)
  if (cached !== undefined && now - cached.at < SENTIMENT_EXPAND_TTL_MS) return cached.terms
  // A failed expansion is not cached: the next scan retries the model, so a
  // transient outage never pins the degraded terms for a day.
  try {
    const expanded = await (deps.expand ?? expandWithLlm)(ctx, policy, task.subjects)
    if (expanded.length === 0) return fallback
    if (cache.size >= 256) for (const [staleKey, entry] of cache) if (now - entry.at >= SENTIMENT_EXPAND_TTL_MS) cache.delete(staleKey)
    cache.set(key, { terms: expanded, at: now })
    return expanded
  } catch {
    return fallback
  }
}
