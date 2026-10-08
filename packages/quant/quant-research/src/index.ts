/**
 * Quant research plugin: kernel-backed market data, deterministic TypeScript
 * indicators, the daily SMA-cross backtester with its risk/stress/factor/PET
 * suite, and jobs-runtime parameter optimization — all for research-only
 * workflows. The plugin opens the `quant_research` storage domain (the
 * compliance-denial audit trail), registers the `quant_*` tools, and
 * installs the pre-execute compliance gate enforcing the research-only red
 * lines. No real-broker path exists anywhere in the plugin.
 * @module @deepseek-ai/dsh-quant-research
 */

import { createRequire } from 'node:module'
import { dirname, join } from 'node:path'
import type { Context } from '@deepseek-ai/cordis'
import { defaultDshHome } from '@deepseek-ai/dsh-home-paths'
import { resolveConfig } from './config.ts'
import type { Config } from './config.ts'
import { denialAuditCallback, installQuantComplianceGate } from './compliance.ts'
import { quantResearchDomainSpec } from './domain/spec.ts'
import { DataSourceBreaker } from './pdat/datasource.ts'
import { QuantKernelClient } from './kernel-client/client.ts'
import { registerQuantTools } from './tools.ts'

export { Config, DATA_SOURCES, defaultKernelCommand, resolveConfig } from './config.ts'
export type { Config as QuantResearchConfig, QuantDataSource, ResolvedConfig } from './config.ts'
export { KERNEL_REQUEST_TIMEOUT_MS_LIMITS, TOOL_TIMEOUT_MS_LIMITS } from './config.ts'
export {
  ENVELOPE_CODES, QuantError, errorEnvelope, isQuantError, okEnvelope,
} from './errors.ts'
export type { QuantErrorCode, QuantEnvelope } from './errors.ts'
export {
  AccountId, OrderId, accountSchema, complianceDenialSchema, orderSchema, quantResearchDomainSpec,
} from './domain/spec.ts'
export type { Account, ComplianceDenial, ComplianceDenialId, Order } from './domain/spec.ts'
export {
  BARS_HARD_LIMIT, BROKER_MARKERS, CONFIDENCE_LIMITS, DEFAULT_GRID_SPEC, FAST_WINDOW_LIMITS, FEE_RATE_HARD_LIMIT,
  GRID_COMBO_HARD_LIMIT, INITIAL_CASH_HARD_LIMIT, SHOCK_LIMITS, SLOW_WINDOW_LIMITS, TOOL_PREFIX, collectArgStrings,
  denialAuditCallback, inspectBarCap, inspectBacktestCaps, inspectBrokerMarkers, inspectConfidenceCap,
  inspectGridCaps, inspectShockCap, inspectToolCall, installQuantComplianceGate, recordComplianceDenial,
} from './compliance.ts'
export type { ComplianceDenialInput, ComplianceVerdict, GridAxisSpec } from './compliance.ts'
export {
  KERNEL_PROTOCOL_VERSION, ResponseParser, encodeRequest, kernelErrorToQuantCode, parseResponseLine,
} from './kernel-client/protocol.ts'
export type { KernelOp, KernelRequest, KernelResponse } from './kernel-client/protocol.ts'
export {
  KERNEL_POLL_INTERVAL_MS, KERNEL_STDERR_MAX_BYTES, KERNEL_STDOUT_MAX_BYTES,
  KERNEL_TERMINATE_GRACE_MS, QuantKernelClient,
} from './kernel-client/client.ts'
export type { KernelProcess, QuantKernelClientOptions, SpawnKernel } from './kernel-client/client.ts'
export {
  BARS_MIN, DataSourceBreaker, fetchKline, klineBarSchema, klineSeriesSchema,
  validateBars, validateSymbol,
} from './pdat/datasource.ts'
export type { FetchKlineOptions, KlineBar } from './pdat/datasource.ts'
export { atr, boll, ema, macd, rsi, sma } from './paat/indicators.ts'
export type { Series } from './paat/indicators.ts'
export {
  DEFAULT_FACTOR_WINDOWS, FACTOR_NAMES, computeFactor, momentum, pricePosition, volumeRatio, volatility,
} from './paat/factors.ts'
export type { FactorName, FactorSeries } from './paat/factors.ts'
export { informationRatio, rollingIC, spearman } from './paat/ic.ts'
export type { ICPeriod } from './paat/ic.ts'
export {
  runBacktest, validateBacktestParams,
} from './pcpt/backtest.ts'
export {
  CONFIDENCE_LIMITS as PRT_CONFIDENCE_LIMITS, DEFAULT_STRESS_SEGMENT, SHOCK_LIMITS as PRT_SHOCK_LIMITS,
  TRADING_DAYS_PER_YEAR, annualVolatility, concentrationBreaches, dailyReturns, empiricalQuantile,
  historicalCVar, historicalVar, maxDrawdown, shockBars, validateStressParams,
} from './prt/risk.ts'
export type { StressParams, StressScenario } from './prt/risk.ts'
export {
  applyTrades, cashDelta, createAccount, listAccounts, requireAccount,
} from './pet/service.ts'
export {
  deleteNote, exportNotesMarkdown, listNotes, renderNoteMarkdown, saveNote,
} from './pet/notes.ts'
export type { NoteSaveInput } from './pet/notes.ts'
export type { ResearchNote } from './domain/spec.ts'
export type { AccountCreateInput } from './pet/service.ts'
export type { PetPosition } from './pet/rebalance.ts'
export {
  computeRebalanceTrades, latestClose,
} from './pet/rebalance.ts'
export type { RebalanceInput, RebalancePlan, RebalanceTarget, RebalanceTrade } from './pet/rebalance.ts'
export type { ApprovalAsk } from './tools.ts'
export type {
  BacktestMetrics, BacktestParams, BacktestReport, BacktestTrade, EquityPoint,
} from './pcpt/backtest.ts'
export { compareBacktests, formatBacktestReport } from './pcpt/report.ts'
export {
  DEFAULT_RANK_METRIC, RANK_METRICS, TOP_N_LIMITS, axisLength, enumerateGrid, formatOptimizationSummary,
  rankGridResults, runBacktestGrid, validateGridSpec,
} from './pcpt/optimize.ts'
export type { GridComboResult, GridSpec, RankMetric } from './pcpt/optimize.ts'
export {
  DEFAULT_BACKTEST_BARS, DEFAULT_BACKTEST_FAST, DEFAULT_BACKTEST_SLOW, DEFAULT_KLINE_BARS,
  accountCreateTool, accountStateTool, assessRiskTool, computeFactorTool, computeIndicatorTool,
  compareBacktestsTool, executeRebalanceTool, exportReportTool, factorICTool, getKlineTool, listNotesTool,
  optimizeParamsTool, registerQuantTools, researchReportTool, runBacktestTool, stressTestTool,
} from './tools.ts'
export type { JobsStartFace, QuantToolDeps } from './tools.ts'
export { QuantResearchService, type AccountSummaryValue } from './service.ts'

/** Cordis plugin name used by loader diagnostics. */
export const name = 'quant-research'

/** Services required before the plugin body runs (`approval` backs the PET review flow). */
export const inject = ['storageDomain', 'subprocess', 'approval']

/**
 * Locate the kernel entry script shipped inside this package. Resolution goes
 * through this package's own manifest, so it works from a workspace source
 * tree and from an installed profile alike.
 * @param createRequireAt - the `createRequire` factory (injected for tests).
 * @returns the absolute path of `kernel-py/main.py`.
 */
export function resolveKernelScriptPath(
  createRequireAt: (filename: string | URL) => ReturnType<typeof createRequire> = createRequire,
): string {
  const require = createRequireAt(import.meta.url)
  const manifest = require.resolve('@deepseek-ai/dsh-quant-research/package.json')
  return join(dirname(manifest), 'kernel-py', 'main.py')
}

/**
 * Compose the plugin: resolve the config, open the `quant_research` domain,
 * and run a runtime fiber that registers the three research tools and the
 * compliance gate. Every registration is an effect; the returned disposer
 * unwinds the runtime fiber and closes the domain.
 * @param ctx - host context providing storage and the subprocess capability.
 * @param config - bundle-row config; see {@link Config} for the tunables.
 * @returns resolution to the disposer releasing every registration.
 * @throws {@link QuantError} code `CONFIG` when the config is invalid.
 */
export async function apply(ctx: Context, config?: Config): Promise<() => Promise<void>> {
  const resolved = resolveConfig(config, { platform: process.platform, dshHome: defaultDshHome() })
  const domain = await ctx.storageDomain.open(quantResearchDomainSpec)
  const runtimeFiber = await ctx.plugin({
    name: 'quant-research:runtime',
    inject: ['tools', 'approval'],
    apply: (runtimeCtx: Context) => {
      const kernel = new QuantKernelClient({
        // Adapt the subprocess handle onto the kernel process face: the
        // collected readers live under `handle.collected`.
        spawn: (spec) => {
          const handle = ctx.subprocess.spawn(spec)
          return {
            stdin: handle.stdin,
            stdout: handle.collected.stdout,
            stderr: handle.collected.stderr,
            waitForExit: signal => handle.waitForExit(signal),
            terminate: () => { handle.terminate() },
          }
        },
        command: resolved.kernelCommand,
        scriptPath: resolveKernelScriptPath(),
        requestTimeoutMs: resolved.kernelRequestTimeoutMs,
      })
      const breaker = new DataSourceBreaker(resolved.fuseThreshold)
      const unregisterTools = registerQuantTools(runtimeCtx, {
        config: resolved,
        kernel,
        breaker,
        accounts: domain.table('accounts'),
        orders: domain.table('orders'),
        notes: domain.table('research_notes'),
        approval: runtimeCtx.approval,
        // Resolved per call: the jobs service may mount after this plugin.
        jobs: () => runtimeCtx.get('jobs'),
      })
      const uninstallGate = installQuantComplianceGate(
        runtimeCtx,
        denialAuditCallback(domain.table('compliance_denials'), runtimeCtx.logger),
      )
      return () => {
        unregisterTools()
        uninstallGate()
      }
    },
  }).await()
  return async () => {
    await runtimeFiber.dispose()
    await domain.close()
  }
}
