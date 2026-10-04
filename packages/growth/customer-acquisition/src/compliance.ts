/**
 * The pre-execute compliance gate (data contract §4, feed-in red lines 1-3):
 * one `tools/pre-execute` listener that inspects every `customer_acquisition_*`
 * call and denies the illegal paths the red lines forbid, regardless of what
 * the parameter schema would later accept. Rules are pure functions so each
 * red line gets a direct illegal-path unit test; the listener denies with a
 * friendly Chinese reason and audits the denial.
 * @module @deepseek-ai/dsh-customer-acquisition/compliance
 */

import type { ToolExecution } from '@deepseek-ai/dsh-tools'
import type { Context } from '@deepseek-ai/cordis'

/** Tool-name prefix owned by this plugin's compliance gate. */
export const TOOL_PREFIX = 'customer_acquisition_'

/** Hard red-line constants (data contract §4); not configurable. */
export const GEO_MAX_PAGES_HARD_LIMIT = 20
/** Hard red-line constants (data contract §4); not configurable. */
export const GEO_PAGE_TIMEOUT_MS_HARD_LIMIT = 10_000
/** Hard red-line constants (data contract §4); not configurable. */
export const GEO_RESPONSE_MAX_BYTES = 2 * 1024 * 1024
/** Hard red-line constants (data contract §4); not configurable. */
export const GEO_FETCH_CONCURRENCY = 1
/** Batch-scoring size cap enforced before any model call. */
export const SCORE_BATCH_HARD_LIMIT = 50

/** The gate's decision, shaped like `PreToolDecision` minus `ask`. */
export type ComplianceVerdict = { readonly kind: 'allow' } | { readonly kind: 'deny'; readonly reason: string }

/** Unvalidated tool arguments as seen by `tools/pre-execute`. */
type RawArgs = ToolExecution['arguments']

/**
 * Read one property from the frozen argument object.
 * @param args - raw tool arguments.
 * @param key - property name.
 * @returns the property value, or `undefined`.
 */
function arg(args: RawArgs, key: string): unknown {
  return (args as Record<string, unknown>)[key]
}

/**
 * Red line 1 (fetch boundary): the GEO scan may only address a URL the user
 * explicitly provided in this call — a non-empty http(s) URL. Non-http
 * schemes, empty, and missing hosts are denied here before any fetch exists.
 * @param args - raw tool arguments.
 * @returns the verdict for the URL rule.
 */
function inspectGeoScanUrl(args: RawArgs): ComplianceVerdict {
  const url = arg(args, 'url')
  if (typeof url !== 'string' || url.trim().length === 0) {
    return { kind: 'deny', reason: '必须提供用户显式给出的网址（url 不能为空）' }
  }
  let parsed: URL
  try {
    parsed = new URL(url)
  } catch {
    return { kind: 'deny', reason: `url 不是合法网址：${url}` }
  }
  if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
    return { kind: 'deny', reason: `仅允许 http/https 网址，收到协议「${parsed.protocol}」` }
  }
  if (parsed.hostname.length === 0) {
    return { kind: 'deny', reason: 'url 缺少主机名，无法执行诊断' }
  }
  return { kind: 'allow' }
}

/**
 * Red line 1 (page cap): the effective page count is capped at the hard
 * limit even if a caller smuggles a larger number past the schema.
 * @param args - raw tool arguments.
 * @returns the verdict for the page-cap rule.
 */
function inspectGeoScanPageCap(args: RawArgs): ComplianceVerdict {
  const maxPages = arg(args, 'max_pages')
  if (maxPages === undefined) return { kind: 'allow' }
  if (typeof maxPages !== 'number' || !Number.isInteger(maxPages) || maxPages < 1 || maxPages > GEO_MAX_PAGES_HARD_LIMIT) {
    return { kind: 'deny', reason: `max_pages 必须是 1-${GEO_MAX_PAGES_HARD_LIMIT} 的整数（合规硬上限）` }
  }
  return { kind: 'allow' }
}

/**
 * Red line 1 (config caps): the settings write may only loosen GEO limits
 * down to the red-line values, never past them.
 * @param args - raw tool arguments.
 * @returns the verdict for the settings-cap rule.
 */
function inspectSettingsCaps(args: RawArgs): ComplianceVerdict {
  const maxPages = arg(args, 'geo_max_pages')
  if (maxPages !== undefined
    && (typeof maxPages !== 'number' || !Number.isInteger(maxPages) || maxPages < 1 || maxPages > GEO_MAX_PAGES_HARD_LIMIT)) {
    return { kind: 'deny', reason: `geo_max_pages 必须是 1-${GEO_MAX_PAGES_HARD_LIMIT} 的整数（合规硬上限）` }
  }
  const timeoutMs = arg(args, 'geo_page_timeout_ms')
  if (timeoutMs !== undefined
    && (typeof timeoutMs !== 'number' || !Number.isInteger(timeoutMs) || timeoutMs < 1_000 || timeoutMs > GEO_PAGE_TIMEOUT_MS_HARD_LIMIT)) {
    return { kind: 'deny', reason: `geo_page_timeout_ms 必须是 1000-${GEO_PAGE_TIMEOUT_MS_HARD_LIMIT} 的整数（合规硬上限）` }
  }
  return { kind: 'allow' }
}

/**
 * Batch-size cap: scoring runs serially, one model call per lead; the batch
 * is denied beyond the hard limit instead of silently truncating.
 * @param args - raw tool arguments.
 * @returns the verdict for the batch-size rule.
 */
function inspectScoreBatchCap(args: RawArgs): ComplianceVerdict {
  const leadIds = arg(args, 'lead_ids')
  if (leadIds === undefined) return { kind: 'allow' }
  if (!Array.isArray(leadIds) || leadIds.length < 1 || leadIds.length > SCORE_BATCH_HARD_LIMIT) {
    return { kind: 'deny', reason: `lead_ids 必须是 1-${SCORE_BATCH_HARD_LIMIT} 条线索的列表` }
  }
  return { kind: 'allow' }
}

/** Rules per tool name; a tool absent from the map passes untouched. */
const RULES: Readonly<Record<string, readonly ((args: RawArgs) => ComplianceVerdict)[]>> = Object.freeze({
  customer_acquisition_geo_scan: [inspectGeoScanUrl, inspectGeoScanPageCap],
  customer_acquisition_settings_set: [inspectSettingsCaps],
  customer_acquisition_score_batch: [inspectScoreBatchCap],
})

/**
 * Decide one tool call against the red lines. Non-plugin tools always pass;
 * the listener uses this to decide whether to `next()` or deny.
 * @param name - the tool name.
 * @param args - the raw (already frozen) tool arguments.
 * @returns `allow` for calls the gate does not own or that pass every rule.
 */
export function inspectToolCall(name: string, args: RawArgs): ComplianceVerdict {
  if (!name.startsWith(TOOL_PREFIX)) return { kind: 'allow' }
  const rules = RULES[name]
  if (rules === undefined) return { kind: 'allow' }
  for (const rule of rules) {
    const verdict = rule(args)
    if (verdict.kind === 'deny') return verdict
  }
  return { kind: 'allow' }
}

/**
 * Install the compliance gate on one context. The waterfall listener
 * delegates every call it does not own (`next()` is mandatory), denies owned
 * calls that fail a rule, and hands each denial to the audit callback so red
 * line 6 records enforcement actions too.
 * @param ctx - the runtime fiber's context carrying `tools/pre-execute`.
 * @param onDeny - receives the denied tool name, reason, and calling agent id when known.
 * @returns the listener's disposer.
 */
export function installComplianceGate(
  ctx: Context,
  onDeny: (name: string, reason: string, agentId?: string) => void,
): () => void {
  return ctx.on('tools/pre-execute', async (exec, next) => {
    if (!exec.name.startsWith(TOOL_PREFIX)) return next()
    const verdict = inspectToolCall(exec.name, exec.arguments)
    if (verdict.kind === 'allow') return next()
    onDeny(exec.name, verdict.reason, exec.agent?.id)
    return { kind: 'deny', reason: verdict.reason }
  })
}
