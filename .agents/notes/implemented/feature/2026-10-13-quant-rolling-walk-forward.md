# Agent Note: Rolling walk-forward re-optimizes per window

Status: implemented

English | [中文](2026-10-13-quant-rolling-walk-forward.zh.md)

## Problem

`quant_walk_forward` validated exactly one train/test split: the caller got one out-of-sample path for one parameter choice. The named deferral was rolling-window re-optimization — the honest test of "re-pick parameters every period", which is how the strategy would actually be traded. A single split can flatter a lucky parameter pair; a rolling report shows whether re-selection survives out of sample at all.

## Decision

- **One tool, one new parameter.** `quant_walk_forward` gains `windows` (2-10, compliance-capped); `windows >= 2` switches the job to expanding-window rolling. The default `1` keeps the shipped single-split behavior byte-for-byte — tool count stays 17, the JobKind stays `quant-walk-forward`, and existing callers see no change.
- **Expanding windows, geometric and auditable.** The bars trim to `floor(n / (windows + 1)) * (windows + 1)`; segment 0 is the initial train leg and each following segment is one window's out-of-sample test. Window *i* re-runs the full grid on all history before its test segment — including earlier test segments — so later windows re-optimize on more history and no window ever sees its own future. One segment length must cover the widest slow window on both the initial train leg and every test leg.
- **The aggregation is the verdict.** The report renders a per-window table (re-selected parameters, train return, out-of-sample return, gap, Sharpe, drawdown) plus an aggregate section: mean/median out-of-sample return, mean gap, positive-window share, and a direct conclusion — a non-negative mean gap with a positive majority reads as out-of-sample stability; anything else reads as overfitting. The disclaimer states the load-bearing reframe: rolling out-of-sample measures the *re-selection strategy itself*, not one lucky pair.
- **Compliance treats `windows` as a first-class cap.** `inspectRollingWindowsCap` denies non-integers and out-of-bounds counts before any job starts, joined to the existing `quant_walk_forward` rule chain; `ROLLING_WINDOWS_LIMITS` lives in `compliance.ts` beside the other hard caps.
- **Rolling runs do not write result snapshots.** The snapshot channel carries single-run full-curve reports; a rolling job produces an aggregate document, and widening the snapshot `kind` waits for a consumer.

## Alternatives considered

**A separate `quant_walk_forward_rolling` tool.** Rejected: the two modes share the grid, the ranking, the job lifecycle, and the disclaimer; a second tool doubles the surface for one integer's worth of difference and pushes mode selection onto the model.

**Anchored (fixed-length) train windows.** Deferred: the expanding window is strictly the more conservative estimate (more training data per window) and needs no new length parameter. Anchored windows would add a second shape knob before any caller has asked for it.

**Parallel window execution.** Rejected: each window's grid is one kernel subprocess and the job is cancellable; sequential windows keep the abort semantics trivially correct and the kernel fan-out identical to the audited single-split path.

## Consequences

Costs: a rolling run is `windows` grids + `windows` single backtests (one kernel subprocess each, up to 20 for the cap) — the start envelope already communicates the shape, and the job stays cancellable throughout. Verification: 300 quant vitest green — 9 new cases covering the segment geometry (equal cuts, expanding trains, remainder trimming, no lookahead), the rolling validation, the compliance cap, the per-window pipeline call order, and the tool-level rolling job with its aggregate detail line. Bilingual README updated; the deferred item moves from "rolling is missing" to "anchored windows and rolling snapshots".
