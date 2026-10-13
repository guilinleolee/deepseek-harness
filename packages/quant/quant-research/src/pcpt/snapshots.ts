/**
 * Persisted backtest result snapshots: the channel that carries a finished
 * run's parameters, headline metrics, and downsampled equity curve into the
 * domain, so the browser panel can draw historical equity cards without any
 * model-visible output change. Plain table functions.
 * @module @deepseek-ai/dsh-quant-research/pcpt/snapshots
 */

import { randomUUID } from 'node:crypto'
import type { KvTable } from '@deepseek-ai/dsh-storage-domain'
import { ResultSnapshotId } from '../domain/spec.ts'
import type { ResultSnapshot } from '../domain/spec.ts'
import type { BacktestReport } from './backtest.ts'

/** The result-snapshots table handle. */
export type ResultSnapshotsTable = KvTable<ResultSnapshotId, ResultSnapshot>

/** Hard cap on stored equity points per snapshot (keeps the record small). */
export const EQUITY_SNAPSHOT_MAX_POINTS = 240

/** Hard cap on retained snapshots; the oldest fall off first. */
export const SNAPSHOT_KEEP_LIMIT = 50

/** The report-facing parameters a snapshot records. */
export interface SnapshotParamsInput {
  /** Fast SMA window. */
  readonly fast: number
  /** Slow SMA window. */
  readonly slow: number
  /** Backtest bar count. */
  readonly bars: number
  /** Initial cash. */
  readonly initialCash: number
  /** Per-side fee rate. */
  readonly feeRate: number
}

/** Fields a snapshot save needs from a finished run. */
export interface SnapshotSaveInput {
  /** The analyzed symbol. */
  readonly symbol: string
  /** The run's parameters. */
  readonly params: SnapshotParamsInput
  /** The finished backtest report. */
  readonly report: BacktestReport
}

/**
 * Downsample an equity curve to at most {@link EQUITY_SNAPSHOT_MAX_POINTS}
 * points, keeping the first point, the last point, and evenly spaced picks
 * in between (deterministic stride; the last point always survives).
 * @param equity - the full per-bar equity curve.
 * @returns the downsampled curve, in order.
 */
export function downsampleEquity(
  equity: readonly { readonly date: string; readonly value: number }[],
): { date: string; value: number }[] {
  if (equity.length <= EQUITY_SNAPSHOT_MAX_POINTS) {
    return equity.map(point => ({ date: point.date, value: point.value }))
  }
  const last = equity.length - 1
  const stride = (last - 1) / (EQUITY_SNAPSHOT_MAX_POINTS - 2)
  const points: { date: string; value: number }[] = []
  for (let index = 0; index < EQUITY_SNAPSHOT_MAX_POINTS - 1; index += 1) {
    const pick = Math.min(last - 1, Math.round(index * stride))
    points.push({ date: equity[pick]!.date, value: equity[pick]!.value })
  }
  const finalPoint = equity[last]!
  points.push({ date: finalPoint.date, value: finalPoint.value })
  return points
}

/**
 * Persist one backtest result snapshot and prune the table to the newest
 * {@link SNAPSHOT_KEEP_LIMIT} entries.
 * @param table - the result-snapshots table.
 * @param input - symbol, parameters, and the finished report.
 * @param now - the save timestamp (injected for tests).
 * @param newId - the id factory (injected for tests).
 * @returns the stored snapshot.
 */
export async function saveSnapshot(
  table: ResultSnapshotsTable,
  input: SnapshotSaveInput,
  now: number = Date.now(),
  newId: () => string = () => randomUUID(),
): Promise<ResultSnapshot> {
  const snapshot: ResultSnapshot = {
    id: ResultSnapshotId(newId()),
    kind: 'backtest',
    symbol: input.symbol,
    params: {
      fast: input.params.fast,
      slow: input.params.slow,
      bars: input.params.bars,
      initial_cash: input.params.initialCash,
      fee_rate: input.params.feeRate,
    },
    metrics: { ...input.report.metrics, final_equity: input.report.final_equity },
    equity: downsampleEquity(input.report.equity),
    created_at: now,
  }
  await table.put(snapshot.id, snapshot)
  const stale = [...table.entries()]
    .map(([id, record]) => ({ id, created_at: record.created_at }))
    .sort((left, right) => right.created_at - left.created_at)
    .slice(SNAPSHOT_KEEP_LIMIT)
  for (const entry of stale) {
    await table.delete(entry.id)
  }
  return snapshot
}

/**
 * List all snapshots, newest first.
 * @param table - the result-snapshots table.
 * @returns the snapshots, newest first.
 */
export function listSnapshots(table: ResultSnapshotsTable): ResultSnapshot[] {
  return [...table.entries()].map(([, snapshot]) => snapshot)
    .sort((left, right) => right.created_at - left.created_at)
}

/**
 * Fetch one snapshot's equity curve.
 * @param table - the result-snapshots table.
 * @param id - the snapshot id.
 * @returns the stored snapshot.
 * @throws when the snapshot does not exist.
 */
export function requireSnapshot(table: ResultSnapshotsTable, id: string): ResultSnapshot {
  const snapshot = table.get(ResultSnapshotId(id))
  if (snapshot === undefined) {
    throw new Error(`未找到回测快照：${id}`)
  }
  return snapshot
}
