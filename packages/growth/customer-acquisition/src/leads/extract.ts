/**
 * Lead field extraction from user-pasted text (tools manifest §5
 * `lead_extract`): the fixed system prompt stating the output contract, the
 * prompt framing, and the strict JSON-output parser. Only the text handed
 * to this call is ever parsed — no network access, no discovery, no batch
 * collection (red lines 1-2). The model's answer is a JSON boundary:
 * anything that is not the requested object rejects here.
 * @module @deepseek-ai/dsh-customer-acquisition/leads/extract
 */

import { decisionRoleSchema } from '../domain/spec.ts'
import type { ExtractedLeadFields } from './types.ts'

/** Input-text cap enforced before any model call (tools manifest §5). */
export const EXTRACT_MAX_CHARS = 10_000

/** The known decision-role values; anything else is dropped into notes. */
const KNOWN_DECISION_ROLES: readonly string[] = decisionRoleSchema.options

/** The extraction output contract the model must follow. */
export const EXTRACT_SYSTEM_PROMPT = [
  '你是获客线索录入助手。从用户提供的文本（表单内容、聊天记录或邮件正文）中抽取线索字段：',
  'company_name（公司名）、contact_name（联系人）、phone（电话）、email（邮箱）、industry（行业）、',
  'company_size（规模档位）、demand_desc（需求描述，50 字内概括）、budget_range（预算档位）、decision_role（决策角色）。',
  'decision_role 只能是 decision_maker/influencer/end_user/gatekeeper/unknown 之一。',
  '只输出一个 JSON 对象：识别到的字段放进去，未识别的字段不要出现；另加 notes 字段说明歧义与未识别情况。',
  '【键名必须逐字使用上述英文键名（company_name/contact_name/...），禁止使用中文或任何其他键名】',
  '示例：{"company_name":"杭州某某贸易有限公司","contact_name":"王经理","notes":"未识别预算"}。',
  '不要输出 JSON 以外的任何文字（不要 markdown 代码块标记、不要解释）。你只解析本次提供的文本，不做任何推测性补全。',
].join('')

/**
 * Key matchers, most specific first. Models drift from the English contract
 * keys (echoing Chinese keys from the input, or variants like `companyName`);
 * each record key maps to the first matcher it hits.
 */
const KEY_MATCHERS: readonly (readonly [RegExp, string])[] = Object.freeze([
  [/company_size|规模|size/i, 'company_size'],
  [/budget|预算/i, 'budget_range'],
  [/demand|需求/i, 'demand_desc'],
  [/decision|决策/i, 'decision_role'],
  [/company|公司|店名|企业/i, 'company_name'],
  [/contact|联系人|联络/i, 'contact_name'],
  [/phone|电话|手机|tel/i, 'phone'],
  [/e-?mail|邮箱|邮件/i, 'email'],
  [/industry|行业/i, 'industry'],
  [/note|备注|说明/i, 'notes'],
])

/**
 * Map one model-emitted key to its canonical contract key.
 * @param rawKey - the key exactly as the model emitted it.
 * @returns the canonical key, or the raw key when nothing matches.
 */
export function canonicalKeyOf(rawKey: string): string {
  for (const [pattern, canonical] of KEY_MATCHERS) {
    if (pattern.test(rawKey)) return canonical
  }
  return rawKey
}

/**
 * Repair the common flash-model JSON slips while never touching string
 * values: escape literal line breaks inside strings, and normalize
 * full-width separators（，：、）that sit at structural positions (immediately
 * before the next quote). Value-internal full-width punctuation is safe —
 * the patterns only fire where a quote follows.
 * @param slice - a brace-delimited JSON-looking body.
 * @returns the repaired body.
 */
export function repairJsonBody(slice: string): string {
  const newlineEscaped = repairJsonNewlines(slice)
  return newlineEscaped
    .replace(/，(?=\s*")/g, ',')
    .replace(/：(?=\s*")/g, ':')
    .replace(/、(?=\s*")/g, ',')
}

/**
 * Frame the user prompt: the raw text plus an optional source hint.
 * @param text - the user-provided raw text.
 * @param sourceHint - optional source hint (form/chat/email).
 * @returns the complete user-prompt text.
 */
export function frameExtractPrompt(text: string, sourceHint?: string): string {
  return [
    sourceHint === undefined ? '' : `来源提示：${sourceHint}`,
    '待抽取文本：',
    text,
  ].filter(part => part.length > 0).join('\n\n')
}

/** Extraction result: recognized fields plus ambiguity notes. */
export interface ExtractOutput {
  fields: ExtractedLeadFields
  notes?: string
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
 * Escape literal newlines/carriage returns that the model left inside JSON
 * string values (invalid JSON, but a common flash-model slip). Outside
 * strings the text is untouched.
 * @param slice - a brace-delimited JSON-looking body.
 * @returns the body with in-string raw line breaks escaped.
 */
export function repairJsonNewlines(slice: string): string {
  let out = ''
  let inString = false
  let escaped = false
  for (const ch of slice) {
    if (inString) {
      if (escaped) {
        escaped = false
        out += ch
        continue
      }
      if (ch === '\\') {
        escaped = true
        out += ch
        continue
      }
      if (ch === '"') {
        inString = false
        out += ch
        continue
      }
      if (ch === '\n') {
        out += '\\n'
        continue
      }
      if (ch === '\r') {
        out += '\\r'
        continue
      }
      out += ch
      continue
    }
    if (ch === '"') inString = true
    out += ch
  }
  return out
}

/**
 * Parse the model's extraction answer into recognized fields. Unknown
 * decision-role values and non-string values are dropped (the role into
 * notes); every kept value is trimmed and non-empty.
 * @param raw - exact model text output.
 * @returns the recognized fields and notes; fails friendly on non-JSON output.
 */
export function parseExtractOutput(raw: string): ExtractOutput {
  const slice = jsonObjectSlice(raw)
  if (slice === undefined) throw new Error('抽取输出不是有效的 JSON 对象，请重试')
  let parsed: unknown
  try {
    parsed = JSON.parse(slice)
  } catch {
    // Flash-model slips: literal line breaks inside string values, or
    // full-width separators at structural positions. One repair pass, then
    // fail loud if the body still will not parse.
    try {
      parsed = JSON.parse(repairJsonBody(slice))
    } catch {
      throw new Error('抽取输出 JSON 解析失败，请重试')
    }
  }
  // A brace-sliced body that parses at all is a JSON object by construction.
  let record = parsed as Record<string, unknown>
  // Normalize drifted keys (Chinese echoes, English variants) into canonical
  // contract keys via the matcher table.
  const normalized: Record<string, unknown> = {}
  for (const [rawKey, value] of Object.entries(record)) {
    normalized[canonicalKeyOf(rawKey)] = value
  }
  record = normalized
  // Flash models often wrap the answer under arbitrary natural-language keys
  //（"报名信息"、"抽取结果"…）or nest one level deep; descend through
  // single-object wrappers until a level actually carries field keys.
  for (let depth = 0; depth < 3; depth += 1) {
    const recordKeys = Object.keys(record)
    if (recordKeys.length !== 1) break
    const soleKey = recordKeys[0]
    if (soleKey === undefined) break
    const sole: unknown = record[soleKey]
    if (sole === null || typeof sole !== 'object' || Array.isArray(sole)) break
    record = sole as Record<string, unknown>
  }
  const notes: string[] = []
  const fields: ExtractedLeadFields = {}
  const fieldKeys = [
    'company_name', 'contact_name', 'phone', 'email', 'industry',
    'company_size', 'demand_desc', 'budget_range',
  ] as const
  for (const key of fieldKeys) {
    const value = record[key]
    if (typeof value === 'string' && value.trim().length > 0) fields[key] = value.trim()
  }
  const role = record.decision_role
  if (typeof role === 'string' && KNOWN_DECISION_ROLES.includes(role)) {
    fields.decision_role = role
  } else if (typeof role === 'string' && role.trim().length > 0) {
    notes.push(`decision_role「${role.trim()}」不在已知取值中，已忽略`)
  }
  if (typeof record.notes === 'string' && record.notes.trim().length > 0) {
    notes.unshift(record.notes.trim())
  }
  if (fields.company_name === undefined) {
    notes.push(`未识别 company_name；模型输出的键：${Object.keys(record).join('、') || '（无）'}`)
  }
  return { fields, ...(notes.length === 0 ? {} : { notes: notes.join('；') }) }
}
