# Agent Note: Walk-forward validation splits one sample to keep the optimization honest

Status: implemented

English | [中文](2026-10-08-quant-walk-forward.zh.md)

## Problem

`quant_optimize_params` carries the warning "网格最优参数来自同一段历史样本，存在过拟合风险" — a grid search over one sample finds the best parameters for that sample, but nothing tests whether they survive out-of-sample. Without a validation leg, the plugin's optimization story is incomplete in exactly the way the warning names.

## Decision

- **One split, two kernel requests, no new op.** `quant_walk_forward` slices the fetched bars at `train_ratio` (0.5–0.9, default 0.7), runs `runBacktestGrid` on the train leg (metrics only — the audited grid engine), ranks, picks the best `(fast, slow)`, then runs one single `runBacktest` on the test leg with those parameters (full report, so the OOS equity and fills are real). Two short-lived Python processes — the same one-request-one-process contract as `optimizeParamsTool` — not one per leg per combination.
- **The overfitting gap is the report's load-bearing section.** `formatWalkForwardSummary` renders the train ranking table (reusing `formatOptimizationSummary`), the OOS metrics, and a direct "过拟合差距" section: return and Sharpe deltas between train and test. The report's header warns that the test leg is one sample path, not a guarantee; a negative gap larger than noise is the signal that the train-optimal parameters are overfit.
- **The gate adds a train-ratio rule on top of the grid rules.** `inspectTrainRatioCap` enforces `train_ratio ∈ [0.5, 0.9]` so the test leg cannot be starved (ratio too high) or over-fed (ratio too low) by a smuggled value. `TRAIN_RATIO_LIMITS` lives in `compliance.ts` beside `CONFIDENCE_LIMITS` and `SHOCK_LIMITS` — the gate owns the constants it enforces. The walk-forward tool reuses `inspectBrokerMarkers`, `inspectBarCap`, and `inspectGridCaps` unchanged (the argument shape is identical to `quant_optimize_params`).
- **The snapshot mirrors the optimize driver phase.** The headless driver starts a real `quant_walk_forward` call through `ctx.tools.execute`, polls `job_output` to settlement, and drives one train-ratio denial through the real gate — the same pattern the optimize round established, keeping completion-notice timing out of the transcript.

## Alternatives considered

**Rolling-window re-optimization (anchored or expanding).** Rejected for this slice: it multiplies the kernel-request count by the window count and complicates the report (aggregated OOS metrics vs one path); one split is the minimum that tests the overfitting claim, and rolling is named as a deferred limitation.

**A new `walk_forward` kernel op that folds train→rank→test into one process.** Rejected: the `backtest_grid` + `backtest` ops are already the audited engines; a folded op would either duplicate the simulator or grow the kernel, and the two-request cost is one extra process spawn (the same contract, not a new one).

**Test leg via `backtest_grid` (metrics only).** Rejected: the OOS report owes its reader the equity curve and fills for the chosen pair, not just headline metrics — `runBacktest` returns the full report.

## Consequences

Costs: walk-forward is one split, not rolling (named as a limitation); the test leg's parameters come from the train ranking, so a pathological train grid (all combinations lose) still picks a "best" that loses less — the gap section makes this visible. Verification: 18 new vitest cases (split, validation, gate rule, runWalkForward round trip, formatting including the empty-ranked fallback, and the full tool lifecycle with cancel/failure/no-jobs paths) with the new code at full coverage — the package suite is 255 green, the kernel pytest suite is unchanged at 28 (no kernel change), and the keyless snapshot grew a `quant-walk-forward-check` driver phase asserting the split, the OOS report, the overfitting gap, and the train-ratio denial. Deferred: rolling-window re-optimization, chart cards, and the real panel.
