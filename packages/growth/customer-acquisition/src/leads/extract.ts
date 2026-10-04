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
  '示例：{"company_name":"杭州某某贸易有限公司","contact_name":"王经理","notes":"未识别预算"}。',
  '不要输出 JSON 以外的任何文字。你只解析本次提供的文本，不做任何推测性补全。',
].join('')

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
    throw new Error('抽取输出 JSON 解析失败，请重试')
  }
  // A brace-sliced body that parses at all is a JSON object by construction.
  const record = parsed as Record<string, unknown>
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
  return { fields, ...(notes.length === 0 ? {} : { notes: notes.join('；') }) }
}
