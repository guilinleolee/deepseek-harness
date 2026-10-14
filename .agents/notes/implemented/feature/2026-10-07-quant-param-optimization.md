# Agent Note: Parameter optimization rides the jobs runtime as one audited grid per kernel process

Status: implemented

English | [中文](2026-10-07-quant-param-optimization.zh.md)

## Problem

Phase 1 established that heavy backtest work must not grow a daemon: "if backtests grow heavy, the jobs runtime (phase 2's parameter optimization) is the sanctioned long-work path, not a daemon." Parameter grid search is that promised workload. The obvious shape — one kernel process per combination, or a blocking tool that loops `runBacktest` — would spawn up to 200 interpreters per request and hold the model's tool budget hostage for the whole search. A second shape — moving the search into the Python kernel as an independent engine — would fork the trade model the plugin had just finished auditing.

## Decision

- **The grid is one kernel request, not one process per combination.** A new `backtest_grid` op walks the caller-supplied `(fast, slow)` list and re-invokes the SAME audited `run_backtest` per combination, returning metrics only — per-combo equity curves and fills are dropped on the wire so 200 combinations stay a bounded response line. The TS side (`src/pcpt/optimize.ts`) owns grid enumeration, validation, ranking, and the markdown summary, so replays re-derive the report from the same kernel numbers.
- **The tool starts a job; it does not block.** `quant_optimize_params` validates everything first, then starts one cancellable background job on the host's `ctx.jobs` registry (kind `quant-optimize`, resolved per call through `deps.jobs?.()` because the jobs service may mount after the plugin). The job fetches the bars once, sends one `backtest_grid` request, and settles `completed` (ranked markdown), `killed` (AbortController), or `failed` (friendly detail). Without a composed jobs runtime the tool returns the friendly config envelope naming `@deepseek-ai/dsh-jobs-local` / `dsh-tool-jobs` rather than degrading into a blocking call.
- **The gate resolves the grid against the tool's exact defaults.** A partial smuggle (only `slow_max: 250`, only `slow_step: 1`) explodes the resolved grid while every visible field looks legal, so `inspectGridCaps` re-derives the effective axes from `DEFAULT_GRID_SPEC` — the same frozen object the tool applies — and enforces integer axes, window bounds, axis ordering, the whole fast range strictly below the whole slow range, and the 200-combination cap. `DEFAULT_GRID_SPEC` lives in `compliance.ts` beside `CONFIDENCE_LIMITS` because the gate must own the defaults it enforces against; `FAST/SLOW_WINDOW_LIMITS` moved there with it, re-exported through `pcpt/backtest.ts` to keep the public API stable.
- **The snapshot drives the job lifecycle from the driver, not the scripted model.** Completion-notice delivery timing is the one nondeterministic edge of a background-job transcript; instead of racing it, the headless driver starts a real `quant_optimize_params` call through `ctx.tools.execute`, polls `job_output` to settlement, and drives one grid-cap denial through the real gate — the same pattern the pwsh snapshot established for `run_in_background`. The scripted model rounds stay untouched.

## Alternatives considered

**One kernel process per combination.** Rejected: 200 process spawns at ~200 ms each is a minute of pure interpreter startup per search, and the per-request process contract exists for statelessness, not for fan-out.

**A TS-side simulator loop calling the existing `backtest` op.** Rejected: same spawn cost, plus it serializes on the tool's cooperative deadline.

**An independent grid engine in the kernel.** Rejected: the plugin's central audit property is that every simulated fill comes from one trade model; a second engine would fork it exactly when parameter search multiplies the surface being trusted.

**Scripting the optimize round into the mock model.** Rejected: the model would need `job_output` rounds whose result timing depends on job settlement racing the notice-injection lane; the driver-owned phase keeps the transcript deterministic without weakening the composition (registry, kernel, gate all real).

## Consequences

Costs: the optimize report is top-N only (full curves for a chosen pair require one extra `quant_run_backtest`); a host that wants optimization must compose the jobs plugins (the tool fails friendly without them); and the gate's default-resolved grid check means `DEFAULT_GRID_SPEC` changes must land in `compliance.ts` — enforced by construction, since the tool imports the same object. Verification: 21 new vitest cases (pure grid functions, gate rule, kernel round trip, job lifecycle including kill and failure) with the new code at full coverage — the package suite is 237 green plus 28 kernel pytest (three new: grid equivalence to single runs, grid validation, wire round trip); the keyless snapshot grew the driver-phase optimize round with the ranked report, the overfitting warning, and the denial asserted. One pre-existing break was fixed in passing: the snapshot's `TOOL_CALL_SEQUENCE` had not been updated for the factor round the previous slice added, so the snapshot test was failing on the branch head before this change. Deferred: chart cards and the real panel remain the named Phase-3 remainder.
