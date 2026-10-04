/**
 * The GEO fetch-boundary pre-execute validator (feed-in red line 1, GEO
 * scope): a `tools/pre-execute` listener owned by this package that guards
 * every `customer_acquisition_geo_*` call. The main package's compliance gate
 * enforces the shared URL/page caps too; this gate owns the GEO-specific
 * edges — the batch-collection guard (`urls` array), the id-shaped read
 * tools — so every red line has at least one denied illegal path in tests.
 * Runtime edges that arguments cannot express (serial concurrency, per-page
 * timeout, response size, robots.txt, same-origin discovery) are enforced in
 * the crawler (`fetcher.ts`), which is what pre-execute cannot see.
 * @module @deepseek-ai/dsh-customer-acquisition-geo/boundary
 */

import type { ToolExecution } from '@deepseek-ai/dsh-tools'
import type { Context } from '@deepseek-ai/cordis'
import {
  GEO_MAX_PAGES_HARD_LIMIT,
  type ComplianceVerdict,
} from './main-package.ts'

/** Tool-name prefix owned by this boundary gate. */
export const GEO_TOOL_PREFIX = 'customer_acquisition_geo_'

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
 * Red line 1 (explicit URL, no batch): `customer_acquisition_geo_scan` must
 * address exactly one user-provided http(s) URL. An array, a missing value, a
 * non-http scheme, or a `urls`-style batch parameter is denied before any
 * fetch exists.
 * @param args - raw tool arguments.
 * @returns the verdict for the explicit-URL rule.
 */
function inspectScanUrl(args: RawArgs): ComplianceVerdict {
  if (arg(args, 'urls') !== undefined) {
    return { kind: 'deny', reason: '不支持批量诊断：一次只处理一个用户显式提供的网址（url），不接受 urls 列表' }
  }
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
 * Red line 1 (page cap): the requested page count stays within the hard
 * limit even if a caller smuggles a larger number past the schema.
 * @param args - raw tool arguments.
 * @returns the verdict for the page-cap rule.
 */
function inspectScanPageCap(args: RawArgs): ComplianceVerdict {
  const maxPages = arg(args, 'max_pages')
  if (maxPages === undefined) return { kind: 'allow' }
  if (typeof maxPages !== 'number' || !Number.isInteger(maxPages) || maxPages < 1 || maxPages > GEO_MAX_PAGES_HARD_LIMIT) {
    return { kind: 'deny', reason: `max_pages 必须是 1-${GEO_MAX_PAGES_HARD_LIMIT} 的整数（合规硬上限）` }
  }
  return { kind: 'allow' }
}

/** Every required-id read tool: `<param>` must be a non-empty string. */
const ID_PARAM_BY_TOOL: Readonly<Record<string, readonly string[]>> = Object.freeze({
  customer_acquisition_geo_report_get: ['report_id'],
  customer_acquisition_geo_compare: ['report_a_id', 'report_b_id'],
})

/**
 * Read tools resolve one or two known reports; an empty or non-string id is
 * denied so a malformed lookup fails at the gate instead of downstream.
 * @param name - the geo tool name.
 * @param args - raw tool arguments.
 * @returns the verdict for the id rule, or `allow` when the tool has none.
 */
function inspectIdParams(name: string, args: RawArgs): ComplianceVerdict {
  const params = ID_PARAM_BY_TOOL[name]
  if (params === undefined) return { kind: 'allow' }
  for (const param of params) {
    const value = arg(args, param)
    if (typeof value !== 'string' || value.trim().length === 0) {
      return { kind: 'deny', reason: `${param} 必须是非空字符串（报告 id）` }
    }
  }
  return { kind: 'allow' }
}

/** Rules per geo tool name; a tool absent from the map passes untouched. */
const RULES: Readonly<Record<string, readonly ((args: RawArgs) => ComplianceVerdict)[]>> = Object.freeze({
  customer_acquisition_geo_scan: [inspectScanUrl, inspectScanPageCap],
})

/**
 * Decide one geo tool call against the fetch boundary. Non-geo tools always
 * pass; the listener uses this to decide whether to `next()` or deny.
 * @param name - the tool name.
 * @param args - the raw (already frozen) tool arguments.
 * @returns `allow` for calls the gate does not own or that pass every rule.
 */
export function inspectGeoToolCall(name: string, args: RawArgs): ComplianceVerdict {
  if (!name.startsWith(GEO_TOOL_PREFIX)) return { kind: 'allow' }
  const rules = RULES[name]
  if (rules !== undefined) {
    for (const rule of rules) {
      const verdict = rule(args)
      if (verdict.kind === 'deny') return verdict
    }
  }
  return inspectIdParams(name, args)
}

/**
 * Install the GEO boundary gate on one context. The waterfall listener
 * delegates every call it does not own (`next()` is mandatory), denies owned
 * calls that fail a rule, and hands each denial to the audit callback so red
 * line 6 records enforcement actions too.
 * @param ctx - the runtime fiber's context carrying `tools/pre-execute`.
 * @param onDeny - receives the denied tool name, reason, and calling agent id when known.
 * @returns the listener's disposer.
 */
export function installGeoBoundaryGate(
  ctx: Context,
  onDeny: (name: string, reason: string, agentId?: string) => void,
): () => void {
  return ctx.on('tools/pre-execute', async (exec, next) => {
    if (!exec.name.startsWith(GEO_TOOL_PREFIX)) return next()
    const verdict = inspectGeoToolCall(exec.name, exec.arguments)
    if (verdict.kind === 'allow') return next()
    onDeny(exec.name, verdict.reason, exec.agent?.id)
    return { kind: 'deny', reason: verdict.reason }
  })
}
