/**
 * Plugin configuration (`config:` on the `quant-research` bundle row).
 * Deployment-varying tunables are validated by Schemastery at load and then
 * range- and membership-checked by {@link resolveConfig}, so a bad value
 * fails loud before any registration. API keys never live here — they resolve
 * through the credentials capability inside the Python kernel at request time.
 * @module @deepseek-ai/dsh-quant-research/config
 */

import z from '@deepseek-ai/schemastery'
import { join } from 'node:path'
import { QuantError } from './errors.ts'

/** Market-data source selection; `synthetic` is the deterministic offline walk. */
export type QuantDataSource = 'synthetic' | 'akshare'

/** The closed data-source set; membership is enforced in {@link resolveConfig}. */
export const DATA_SOURCES: readonly QuantDataSource[] = ['synthetic', 'akshare']

/** Inclusive validation bounds plus the default for one numeric tunable. */
export interface NumericLimits {
  /** Smallest accepted value. */
  readonly min: number
  /** Largest accepted value. */
  readonly max: number
  /** Value used when the field is omitted. */
  readonly default: number
}

/** Model-facing tool-call budget (the `timeoutMs` each tool declares). */
export const TOOL_TIMEOUT_MS_LIMITS: NumericLimits = { min: 1_000, max: 600_000, default: 120_000 }
/** Per-request Python-kernel deadline; below the tool budget so the tool cancels last. */
export const KERNEL_REQUEST_TIMEOUT_MS_LIMITS: NumericLimits = { min: 1_000, max: 600_000, default: 90_000 }
/** Kernel-side retries for one flaky data-source fetch. */
export const SOURCE_MAX_RETRIES_LIMITS: NumericLimits = { min: 0, max: 5, default: 2 }
/** Consecutive data-source failures that trip the circuit breaker. */
export const FUSE_THRESHOLD_LIMITS: NumericLimits = { min: 1, max: 20, default: 5 }
/** Backtest starting cash when the caller omits it. */
export const DEFAULT_CASH_LIMITS: NumericLimits = { min: 1, max: 1e12, default: 1_000_000 }
/** Backtest per-trade fee rate when the caller omits it. */
export const FEE_RATE_LIMITS: NumericLimits = { min: 0, max: 0.01, default: 0.0003 }

/** Deployment tunables for the plugin; every field is optional with a resolved default. */
export interface Config {
  /** Market-data source; omit for the deterministic offline walk. */
  dataSource?: QuantDataSource
  /** Python interpreter used to run the kernel; omit for the platform default. */
  kernelCommand?: string
  /** Directory the kernel uses for its kline cache; omit for `<dshHome>/quant-research/cache`. */
  cacheDir?: string
  /** Model-facing tool-call budget in milliseconds. */
  toolTimeoutMs?: number
  /** Per-request kernel deadline in milliseconds; must stay below `toolTimeoutMs`. */
  kernelRequestTimeoutMs?: number
  /** Kernel-side retries for one flaky data-source fetch. */
  sourceMaxRetries?: number
  /** Consecutive data-source failures that trip the circuit breaker. */
  fuseThreshold?: number
  /** Backtest starting cash when a call omits it. */
  defaultCash?: number
  /** Backtest per-trade fee rate when a call omits it. */
  feeRate?: number
}

/** Schemastery validation for {@link Config}; invalid shapes fail plugin load. */
export const Config: z<Config> = z.object({
  dataSource: z.union(['synthetic', 'akshare'] as const).default('synthetic'),
  kernelCommand: z.string(),
  cacheDir: z.string(),
  toolTimeoutMs: z.number(),
  kernelRequestTimeoutMs: z.number(),
  sourceMaxRetries: z.number(),
  fuseThreshold: z.number(),
  defaultCash: z.number(),
  feeRate: z.number(),
})

/** Fully resolved configuration; every field is present and validated. */
export interface ResolvedConfig {
  /** Market-data source. */
  dataSource: QuantDataSource
  /** Python interpreter command. */
  kernelCommand: string
  /** Kernel kline-cache directory. */
  cacheDir: string
  /** Model-facing tool-call budget in milliseconds. */
  toolTimeoutMs: number
  /** Per-request kernel deadline in milliseconds. */
  kernelRequestTimeoutMs: number
  /** Kernel-side fetch retries. */
  sourceMaxRetries: number
  /** Circuit-breaker trip threshold. */
  fuseThreshold: number
  /** Backtest starting cash default. */
  defaultCash: number
  /** Backtest fee-rate default. */
  feeRate: number
}

/**
 * Platform-appropriate Python command: Windows names the launcher `python`,
 * every other platform uses the `python3` convention.
 * @param platform - the `process.platform` value to resolve for.
 * @returns the default kernel command.
 */
export function defaultKernelCommand(platform: NodeJS.Platform): string {
  return platform === 'win32' ? 'python' : 'python3'
}

/**
 * Check one numeric tunable against its bounds.
 * @param name - the config field name, for the error message.
 * @param value - the provided value, when present.
 * @param limits - the inclusive bounds and default.
 * @returns the provided value, or the default.
 */
function resolveNumber(name: string, value: number | undefined, limits: NumericLimits): number {
  if (value === undefined) return limits.default
  if (!Number.isFinite(value) || value < limits.min || value > limits.max) {
    throw new QuantError(
      'CONFIG',
      `配置项 ${name} 必须是 ${limits.min}-${limits.max} 之间的数值，收到 ${String(value)}`,
    )
  }
  return value
}

/**
 * Resolve and validate the full plugin configuration. Pure: the platform and
 * the default home directory arrive as parameters, so tests cover every
 * branch without touching process state.
 * @param config - the bundle-row config, when provided.
 * @param environment - the platform and home directory the defaults resolve against.
 * @returns the resolved configuration.
 * @throws {@link QuantError} code `CONFIG` on any invalid field.
 */
export function resolveConfig(
  config: Config | undefined,
  environment: { platform: NodeJS.Platform; dshHome: string },
): ResolvedConfig {
  const raw = config ?? {}
  if (raw.dataSource !== undefined && !DATA_SOURCES.includes(raw.dataSource)) {
    throw new QuantError(
      'CONFIG',
      `配置项 dataSource 只允许 ${DATA_SOURCES.join(' / ')}，收到 ${raw.dataSource}`,
    )
  }
  const toolTimeoutMs = resolveNumber('toolTimeoutMs', raw.toolTimeoutMs, TOOL_TIMEOUT_MS_LIMITS)
  const kernelRequestTimeoutMs = resolveNumber(
    'kernelRequestTimeoutMs',
    raw.kernelRequestTimeoutMs,
    KERNEL_REQUEST_TIMEOUT_MS_LIMITS,
  )
  if (kernelRequestTimeoutMs >= toolTimeoutMs) {
    throw new QuantError(
      'CONFIG',
      `配置项 kernelRequestTimeoutMs（${String(kernelRequestTimeoutMs)}）必须小于 toolTimeoutMs（${String(toolTimeoutMs)}），否则工具会先于内核超时`,
    )
  }
  return {
    dataSource: raw.dataSource ?? 'synthetic',
    kernelCommand: raw.kernelCommand ?? defaultKernelCommand(environment.platform),
    cacheDir: raw.cacheDir ?? join(environment.dshHome, 'quant-research', 'cache'),
    toolTimeoutMs,
    kernelRequestTimeoutMs,
    sourceMaxRetries: resolveNumber('sourceMaxRetries', raw.sourceMaxRetries, SOURCE_MAX_RETRIES_LIMITS),
    fuseThreshold: resolveNumber('fuseThreshold', raw.fuseThreshold, FUSE_THRESHOLD_LIMITS),
    defaultCash: resolveNumber('defaultCash', raw.defaultCash, DEFAULT_CASH_LIMITS),
    feeRate: resolveNumber('feeRate', raw.feeRate, FEE_RATE_LIMITS),
  }
}
