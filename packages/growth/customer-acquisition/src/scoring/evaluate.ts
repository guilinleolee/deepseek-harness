/**
 * Scoring output evaluation (data contract §3.4): the fixed system prompt
 * stating the model's JSON output contract, the strict output parser, the
 * weighted-total computation, and the intent-tag thresholds. The model's
 * answer is a JSON boundary: items must cover exactly the profile's
 * dimensions with finite 0-100 scores, or the call rejects with a friendly
 * error — no invented or defaulted scores.
 * @module @deepseek-ai/dsh-customer-acquisition/scoring/evaluate
 */

import type { IcpProfile } from '../domain/spec.ts'
import type { IntentLevel } from '../leads/types.ts'

/** Total score at or above which a lead tags `high` intent. */
export const SCORE_INTENT_HIGH_MIN = 80
/** Total score at or above which a lead tags `mid` intent. */
export const SCORE_INTENT_MID_MIN = 60
/** Total score at or above which a lead tags `low` intent. */
export const SCORE_INTENT_LOW_MIN = 30

/**
 * Map a weighted total to the lead's intent tag (自动意向标签).
 * @param total - the weighted total in [0, 100].
 * @returns the intent level.
 */
export function intentTagFor(total: number): IntentLevel {
  if (total >= SCORE_INTENT_HIGH_MIN) return 'high'
  if (total >= SCORE_INTENT_MID_MIN) return 'mid'
  if (total >= SCORE_INTENT_LOW_MIN) return 'low'
  return 'invalid'
}

/** Chinese label per intent level, reused in audit summaries and renders. */
export const INTENT_LABELS: Readonly<Record<IntentLevel, string>> = Object.freeze({
  high: '高意向',
  mid: '中意向',
  low: '低意向',
  invalid: '无效',
})

/** The scorer's fixed output contract; the template prompt carries the business specifics. */
export const SCORE_SYSTEM_PROMPT = [
  '你是获客线索评分引擎。依据给定的 ICP 画像维度对线索逐项打分：每个维度 0-100 的整数分与一句话理由，',
  '并给出整体理由。总分 = Σ(维度分 × 权重 / 100)。意向标签映射：总分 ≥80 高意向、≥60 中意向、≥30 低意向、<30 无效。',
  '只输出一个 JSON 对象，形如 {"items":[{"dimension_id":"维度id","score":85,"reason":"一句话理由"}],"reason":"整体理由"}，',
  '"items" 必须覆盖全部给定维度且不新增维度，不要输出 JSON 以外的任何文字。',
].join('')

/** One parsed per-dimension score. */
export interface ParsedScoreItem {
  dimension_id: string
  score: number
  reason: string
}

/** One parsed model scoring answer, before persistence. */
export interface ParsedScoreOutput {
  items: ParsedScoreItem[]
  reason: string
  total: number
}

/**
 * Whether one raw model answer carries a JSON object body.
 * @param text - exact model text output.
 * @returns the object body slice, or undefined when no object exists.
 */
function jsonObjectSlice(text: string): string | undefined {
  const fenced = text.trim().replace(/^```(?:json)?\s*/u, '').replace(/\s*```$/u, '')
  const start = fenced.indexOf('{')
  const end = fenced.lastIndexOf('}')
  if (start === -1 || end <= start) return undefined
  return fenced.slice(start, end + 1)
}

/**
 * Parse and validate one model scoring answer against the profile: every
 * dimension scored exactly once, finite 0-100 scores, non-empty reasons.
 * @param raw - exact model text output.
 * @param profile - the ICP profile the prompt was built from.
 * @returns the items, the overall reason, and the weighted total.
 */
export function parseScoreOutput(raw: string, profile: IcpProfile): ParsedScoreOutput {
  const slice = jsonObjectSlice(raw)
  if (slice === undefined) throw new Error('打分输出不是有效的 JSON 对象，请重试')
  let parsed: unknown
  try {
    parsed = JSON.parse(slice)
  } catch {
    throw new Error('打分输出 JSON 解析失败，请重试')
  }
  if (typeof parsed !== 'object' || parsed === null) throw new Error('打分输出不是 JSON 对象')
  const record = parsed as Record<string, unknown>
  if (!Array.isArray(record.items)) throw new Error('打分输出缺少 items 数组')
  if (typeof record.reason !== 'string' || record.reason.trim().length === 0) {
    throw new Error('打分输出缺少整体理由（reason）')
  }
  const byDimension = new Map<string, { score: number; reason: string }>()
  for (const entry of record.items) {
    if (typeof entry !== 'object' || entry === null) throw new Error('打分输出 items 含非对象元素')
    const item = entry as Record<string, unknown>
    const dimensionId = item.dimension_id
    if (typeof dimensionId !== 'string' || dimensionId.length === 0) {
      throw new Error('打分输出 items 含缺少 dimension_id 的元素')
    }
    if (byDimension.has(dimensionId)) throw new Error(`打分输出对维度 ${dimensionId} 重复打分`)
    const score = item.score
    if (typeof score !== 'number' || !Number.isFinite(score) || score < 0 || score > 100) {
      throw new Error(`维度 ${dimensionId} 的打分不是 0-100 的数字`)
    }
    const reason = item.reason
    if (typeof reason !== 'string' || reason.trim().length === 0) {
      throw new Error(`维度 ${dimensionId} 缺少打分理由`)
    }
    byDimension.set(dimensionId, { score, reason: reason.trim() })
  }
  for (const dimensionId of byDimension.keys()) {
    if (!profile.dimensions.some(dimension => dimension.id === dimensionId)) {
      throw new Error(`打分输出包含未知维度 ${dimensionId}`)
    }
  }
  const items: ParsedScoreItem[] = []
  let total = 0
  for (const dimension of profile.dimensions) {
    const scored = byDimension.get(dimension.id)
    if (scored === undefined) throw new Error(`打分输出缺少维度 ${dimension.id}（${dimension.name}）的评分`)
    const rounded = Math.round(scored.score * 100) / 100
    total += rounded * dimension.weight
    items.push({ dimension_id: dimension.id, score: rounded, reason: scored.reason })
  }
  return {
    items,
    reason: record.reason.trim(),
    total: Math.round((total / 100) * 100) / 100,
  }
}
