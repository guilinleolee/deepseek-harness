/**
 * The pre-execute compliance gate (research-only red lines): one
 * `tools/pre-execute` listener that inspects every `quant_*` call and denies
 * the paths the red lines forbid — real-trading or broker-API markers in any
 * argument string, and hard parameter caps — regardless of what the parameter
 * schema would later accept. Rules are pure functions so each red line gets a
 * direct illegal-path unit test; the listener denies with a friendly Chinese
 * reason and hands each denial to the audit callback for the durable trail.
 * @module @deepseek-ai/dsh-quant-research/compliance
 */

/* jscpd:ignore-start */
import type { Context } from '@deepseek-ai/cordis'
import type { ToolExecution } from '@deepseek-ai/dsh-tools'
import { randomUUID } from 'node:crypto'
import type { KvTable } from '@deepseek-ai/dsh-storage-domain'
import { ComplianceDenialId } from './domain/spec.ts'
import type { ComplianceDenial } from './domain/spec.ts'

/** Tool-name prefix owned by this plugin's compliance gate. */
export const TOOL_PREFIX = 'quant_'

/** Hard cap on one kline/backtest request's bar count; not configurable. */
export const BARS_HARD_LIMIT = 1500
/** Hard cap on one backtest's starting cash; not configurable. */
export const INITIAL_CASH_HARD_LIMIT = 1e12
/** Hard cap on the backtest fee rate; not configurable. */
export const FEE_RATE_HARD_LIMIT = 0.05
/** Hard bounds for the VaR/CVaR confidence level; not configurable. */
export const CONFIDENCE_LIMITS = { min: 0.8, max: 0.99, default: 0.95 } as const
/** Hard bounds for a stress shock's total magnitude; not configurable. */
export const SHOCK_LIMITS = { min: 0.01, max: 0.5, default: 0.1 } as const
/** Hard cap for one rebalance target weight (no single-name overconcentration); not configurable. */
export const WEIGHT_POSITION_HARD_LIMIT = 1
/** Hard cap for the rebalance targets' weight sum (no leverage); not configurable. */
export const WEIGHT_TOTAL_HARD_LIMIT = 1

/** Argument substrings that indicate real-trading or broker-API intent. */
export const BROKER_MARKERS: readonly string[] = [
  '实盘',
  '券商',
  'place_order',
  'submit_order',
  'cancel_order',
]

/** The gate's decision, shaped like `PreToolDecision` minus `ask`. */
export type ComplianceVerdict = { readonly kind: 'allow' } | { readonly kind: 'deny'; readonly reason: string }

/** Unvalidated tool arguments as seen by `tools/pre-execute`. */
type RawArgs = ToolExecution['arguments']

/**
 * Collect every string reachable in the frozen argument value. Marker
 * scanning is depth-first over objects and arrays, so no nesting shape can
 * carry a broker marker past the gate.
 * @param value - the raw argument value.
 * @param into - the accumulator for recursion.
 * @returns every string found in the value.
 */
export function collectArgStrings(value: unknown, into: string[] = []): string[] {
  if (typeof value === 'string') into.push(value)
  else if (Array.isArray(value)) {
    for (const item of value) collectArgStrings(item, into)
  } else if (value !== null && typeof value === 'object') {
    for (const item of Object.values(value as Record<string, unknown>)) collectArgStrings(item, into)
  }
  return into
}

/**
 * Red line 1 (research-only): no argument string may carry real-trading or
 * broker-API intent. The plugin has no order path at all; the marker scan is
 * the loud refusal when a prompt tries to smuggle one in.
 * @param args - raw tool arguments.
 * @returns the verdict for the marker rule.
 */
export function inspectBrokerMarkers(args: RawArgs): ComplianceVerdict {
  for (const text of collectArgStrings(args)) {
    for (const marker of BROKER_MARKERS) {
      if (text.includes(marker)) {
        return {
          kind: 'deny',
          reason: `量化研究插件仅支持研究与模拟回测，禁止实盘交易指令（检测到「${marker}」）`,
        }
      }
    }
  }
  return { kind: 'allow' }
}

/**
 * Red line 2 (bar cap): the kline bar count is capped at the hard limit even
 * if a caller smuggles a larger or non-integer number past the schema.
 * @param args - raw tool arguments.
 * @returns the verdict for the bar-cap rule.
 */
export function inspectBarCap(args: RawArgs): ComplianceVerdict {
  const bars = (args as Record<string, unknown>)['bars']
  if (bars === undefined) return { kind: 'allow' }
  if (typeof bars !== 'number' || !Number.isSafeInteger(bars) || bars < 1 || bars > BARS_HARD_LIMIT) {
    return { kind: 'deny', reason: `bars 必须是 1-${BARS_HARD_LIMIT} 的整数（合规硬上限）` }
  }
  return { kind: 'allow' }
}

/**
 * Red line 3 (backtest caps): starting cash and fee rate stay at or below
 * the hard caps even if a caller smuggles larger values past the schema.
 * @param args - raw tool arguments.
 * @returns the verdict for the backtest-cap rule.
 */
export function inspectBacktestCaps(args: RawArgs): ComplianceVerdict {
  const record = args as Record<string, unknown>
  const cash = record['initial_cash']
  if (cash !== undefined
    && (typeof cash !== 'number' || !Number.isFinite(cash) || cash <= 0 || cash > INITIAL_CASH_HARD_LIMIT)) {
    return { kind: 'deny', reason: `initial_cash 必须是 0-${INITIAL_CASH_HARD_LIMIT} 的数值（合规硬上限）` }
  }
  const feeRate = record['fee_rate']
  if (feeRate !== undefined
    && (typeof feeRate !== 'number' || !Number.isFinite(feeRate) || feeRate < 0 || feeRate > FEE_RATE_HARD_LIMIT)) {
    return { kind: 'deny', reason: `fee_rate 必须是 0-${FEE_RATE_HARD_LIMIT} 之间的数值（合规硬上限）` }
  }
  return { kind: 'allow' }
}

/** Rules per tool name; a tool absent from the map passes untouched. */
const RULES: Readonly<Record<string, readonly ((args: RawArgs) => ComplianceVerdict)[]>> = Object.freeze({
  quant_get_kline: [inspectBrokerMarkers, inspectBarCap],
  quant_compute_indicator: [inspectBrokerMarkers, inspectBarCap],
  quant_run_backtest: [inspectBrokerMarkers, inspectBarCap, inspectBacktestCaps],
  quant_assess_risk: [inspectBrokerMarkers, inspectBarCap, inspectConfidenceCap],
  quant_stress_test: [inspectBrokerMarkers, inspectBarCap, inspectShockCap],
  quant_execute_rebalance: [inspectBrokerMarkers, inspectWeightCaps],
  quant_compute_factor: [inspectBrokerMarkers, inspectBarCap],
  quant_factor_ic: [inspectBrokerMarkers, inspectBarCap],
  quant_compare_backtests: [inspectBrokerMarkers, inspectBarCap],
  quant_research_report: [inspectBrokerMarkers, inspectBarCap],
})

/**
 * Red line 4 (risk-parameter caps): the VaR/CVaR confidence stays inside the
 * hard bounds even if a caller smuggles extremes past the schema.
 * @param args - raw tool arguments.
 * @returns the verdict for the confidence rule.
 */
export function inspectConfidenceCap(args: RawArgs): ComplianceVerdict {
  const confidence = (args as Record<string, unknown>)['confidence']
  if (confidence === undefined) return { kind: 'allow' }
  if (typeof confidence !== 'number' || !Number.isFinite(confidence)
    || confidence < CONFIDENCE_LIMITS.min || confidence > CONFIDENCE_LIMITS.max) {
    return {
      kind: 'deny',
      reason: `confidence 必须是 ${String(CONFIDENCE_LIMITS.min)}-${String(CONFIDENCE_LIMITS.max)} 之间的数值（合规硬上限）`,
    }
  }
  return { kind: 'allow' }
}

/**
 * Red line 5 (stress-magnitude cap): a stress shock's total magnitude stays
 * inside the hard bounds even if a caller smuggles extremes past the schema.
 * @param args - raw tool arguments.
 * @returns the verdict for the shock rule.
 */
export function inspectShockCap(args: RawArgs): ComplianceVerdict {
  const shock = (args as Record<string, unknown>)['shock']
  if (shock === undefined) return { kind: 'allow' }
  if (typeof shock !== 'number' || !Number.isFinite(shock)
    || shock < SHOCK_LIMITS.min || shock > SHOCK_LIMITS.max) {
    return {
      kind: 'deny',
      reason: `shock 必须是 ${String(SHOCK_LIMITS.min)}-${String(SHOCK_LIMITS.max)} 之间的数值（合规硬上限）`,
    }
  }
  return { kind: 'allow' }
}

/**
 * Red line 6 (no leverage, long-only): every rebalance target weight stays
 * within `[0, 1]` and the weights' sum stays within `[0, 1]` — the virtual
 * book never goes short or levered, regardless of what the schema accepts.
 * @param args - raw tool arguments.
 * @returns the verdict for the weight-cap rule.
 */
export function inspectWeightCaps(args: RawArgs): ComplianceVerdict {
  const targets = (args as Record<string, unknown>)['targets']
  if (targets === undefined) return { kind: 'allow' }
  if (!Array.isArray(targets)) {
    return { kind: 'deny', reason: 'targets 必须是目标权重列表（合规硬上限：仅限多头、无杠杆）' }
  }
  let total = 0
  for (const item of targets) {
    const weight = (item as Record<string, unknown> | null)?.['weight']
    if (typeof weight !== 'number' || !Number.isFinite(weight) || weight < 0 || weight > WEIGHT_POSITION_HARD_LIMIT) {
      return {
        kind: 'deny',
        reason: `每个目标权重必须是 0-${String(WEIGHT_POSITION_HARD_LIMIT)} 之间的数值（合规硬上限：仅限多头、无杠杆）`,
      }
    }
    total += weight
  }
  if (total > WEIGHT_TOTAL_HARD_LIMIT + 1e-9) {
    return { kind: 'deny', reason: `目标权重合计 ${total.toFixed(4)} 超过 ${String(WEIGHT_TOTAL_HARD_LIMIT)}（合规硬上限：不允许杠杆）` }
  }
  return { kind: 'allow' }
}

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

/** Fields the audit caller supplies; id and timestamp are filled here. */
export interface ComplianceDenialInput {
  /** The denied tool name. */
  readonly toolName: string
  /** The friendly Chinese reason the gate returned. */
  readonly reason: string
  /** Calling agent id, when the execution carried one. */
  readonly agentId?: string
}

/**
 * Append one denial record durably. The id and timestamp are filled here so
 * the audit trail stays uniform across callers; failures are the callback's
 * to handle and never un-deny the call.
 * @param table - the compliance-denial table handle.
 * @param input - tool name, reason, and agent id.
 * @param now - the denial timestamp in epoch milliseconds (injected for tests).
 * @param newId - the id factory (injected for tests).
 * @returns resolution after the record is durable.
 */
export function recordComplianceDenial(
  table: KvTable<ComplianceDenialId, ComplianceDenial>,
  input: ComplianceDenialInput,
  now: number = Date.now(),
  newId: () => string = () => randomUUID(),
): Promise<void> {
  const record: ComplianceDenial = {
    id: ComplianceDenialId(newId()),
    tool_name: input.toolName,
    reason: input.reason,
    ...(input.agentId === undefined ? {} : { agent_id: input.agentId }),
    denied_at: now,
  }
  return table.put(record.id, record)
}

/**
 * Build the gate's audit callback: every denial lands in the domain table,
 * and a failed write is warn-and-continue — the medium rejected the record,
 * so containment must never un-deny the call.
 * @param table - the compliance-denial table handle.
 * @param logger - the fiber logger receiving the write-failure warning.
 * @returns the audit callback for {@link installQuantComplianceGate}.
 */
export function denialAuditCallback(
  table: KvTable<ComplianceDenialId, ComplianceDenial>,
  logger: { warn(message: string): void },
): (name: string, reason: string, agentId?: string) => void {
  return (name, reason, agentId) => {
    void recordComplianceDenial(table, {
      toolName: name,
      reason,
      ...(agentId === undefined ? {} : { agentId }),
    })
      .catch((error: unknown) => {
        logger.warn(`quant-research: 拒绝审计写入失败：${String(error)}`)
      })
  }
}

/**
 * Install the compliance gate on one context. The waterfall listener
 * delegates every call it does not own (`next()` is mandatory), denies owned
 * calls that fail a rule, and hands each denial to the audit callback so the
 * durable trail records enforcement actions too.
 * @param ctx - the runtime fiber's context carrying `tools/pre-execute`.
 * @param onDeny - receives the denied tool name, reason, and calling agent id when known.
 * @returns the listener's disposer.
 */
export function installQuantComplianceGate(
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
/* jscpd:ignore-end */
