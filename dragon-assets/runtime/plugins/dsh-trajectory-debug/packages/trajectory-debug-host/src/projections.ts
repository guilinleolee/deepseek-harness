/**
 * Projection units for the session-projection registry.
 *
 * Registers `trajectoryDebug/trajectory` and `trajectoryDebug/perf` units so
 * the standard projection carriers (history tail page, `session/projection`
 * push frames) can serve the debug views. The units fold raw `SessionEvent`s
 * through the SAME fold primitives as the on-demand engine, so registry drive
 * and engine can never disagree.
 *
 * Contract notes honored here:
 * - `init/apply/view` are synchronous and `apply` returns the same reference
 *   for unrelated events (same-reference gate);
 * - state is plain JSON (the fold states use Records/arrays, no Maps/Sets);
 * - `stateVersion` bumps whenever fold semantics or state shape change.
 *
 * NOTE on typing: the `SessionProjectionMap` keys are declared with `any`
 * rather than via declaration merging, because pulling the projection type
 * table into this package's program drags the HOST `Context` merge
 * (dsh-session) into browser bundles. The wire value types remain the
 * plugin's own `TrajectoryRow`/`PerfSnapshot`; clients read them with local
 * type assertions.
 *
 * The registry is an optional capability: when `ctx.sessionProjections` is
 * absent (headless assemblies), this module registers nothing.
 *
 * @module dsh-trajectory-debug-host/projections
 */

import { z } from 'zod'
import type { Context } from '@deepseek-ai/cordis'
import type { SessionEvent } from '@deepseek-ai/dsh-session'
import type { PerfSnapshot, TrajectoryRow } from 'dsh-trajectory-debug'
import { adaptEvent } from './adapt.ts'
import { applyPerf, createPerfState, finalizePerf, type PerfFoldState } from './perf-analyzer.ts'
import { applyTrajectory, createTrajectoryState, finalizeTrajectory, type TrajectoryFoldState } from './replay-engine.ts'

export interface TrajectoryProjectionValue {
  rows: TrajectoryRow[]
  stepCount: number
  turnCount: number
}

// The definitions are plain objects on purpose: `ProjectionDefinition<K, S>`
// constrains K to `keyof SessionProjectionMap`, which is `never` without
// domain augmentation (the table is merge-extensible). The `as never` at the
// register boundary bridges that type-level constraint; the runtime accepts
// any string key.
const trajectoryDefinition = {
  key: 'trajectoryDebug/trajectory',
  schema: z.custom<TrajectoryProjectionValue>(() => true),
  stateVersion: 1,
  init: () => createTrajectoryState(),
  apply: (state: TrajectoryFoldState, event: SessionEvent) => applyTrajectory(state, adaptEvent(event)),
  view: (state: TrajectoryFoldState): TrajectoryProjectionValue => {
    const { rows, stepCount, turnCount } = finalizeTrajectory(state)
    return { rows, stepCount, turnCount }
  },
}

const perfDefinition = {
  key: 'trajectoryDebug/perf',
  schema: z.custom<PerfSnapshot>(() => true),
  stateVersion: 1,
  init: () => createPerfState(),
  apply: (state: PerfFoldState, event: SessionEvent) => applyPerf(state, adaptEvent(event)),
  view: (state: PerfFoldState): PerfSnapshot => finalizePerf(state),
}

/** Register both units; returns the disposer, or `undefined` when the
 * projection registry is not mounted.
 *
 * The `register` key constraint is type-level only (the projection table is
 * empty without domain augmentation, so `keyof` is `never`); the runtime
 * accepts any string key, hence the `never` bridge at this boundary. */
export function registerTrajectoryDebugProjections(ctx: Context): (() => void) | undefined {
  const registry = ctx.get('sessionProjections')
  if (registry === undefined) return undefined
  const disposers = [
    registry.register(trajectoryDefinition as never),
    registry.register(perfDefinition as never),
  ]
  return () => {
    for (const dispose of disposers) dispose()
  }
}
