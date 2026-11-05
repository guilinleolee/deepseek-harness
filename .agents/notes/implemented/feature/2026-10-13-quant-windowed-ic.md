# Agent Note: Windowed cross-sectional IC reads regime stability

Status: implemented

English | [中文](2026-10-13-quant-windowed-ic.zh.md)

## Problem

The cross-sectional IC report aggregated the whole panel history into one ICIR. A factor can carry strong same-sign IC for two years, flip sign for the third, and still print a respectable full-sample mean — the single number hides the flip. The deferral was the standard remedy: split the IC series into windows and aggregate each, so regime dependence becomes visible.

## Decision

- **`ic_windows` (2-6, compliance-capped) slices the IC series after the fact.** `windowedIC` cuts the computed cross-IC points into equal-count contiguous windows (tail remainder drops), aggregates each independently through the existing `summarizeIC`, and records the date span. The panel math does not change — the same bars, factors, and forward returns feed the same per-date ICs; only the reporting gains a second lens.
- **The verdict is a sign read.** The window table renders per-window observations, mean IC, and ICIR, followed by one of three conclusions: signs hold positive (cross-window directional stability), signs hold negative (a stable inverse factor — value ranks returns in reverse), or signs flip (regime-bound; treat the full-sample verdict with caution). The verdict uses the ICIR sign, not the mean IC sign, because the ICIR is the signal-to-noise statement.
- **Degenerate dispersion clamps to zero, not infinity.** A window whose IC readings are (numerically) constant has a std near 1e-16, which would report an ICIR of ~1e16. `summarizeIC` now clamps any std below one basis point to zero, so such windows report ICIR 0 (no measurable dispersion, no conviction) — the same convention the existing zero-std branch already stated.
- **Compliance joins the cap into the existing chain.** `inspectCrossPanelCaps` gains the `ic_windows` integer check (2-6); no new rule function, no new tool — the parameter rides the already-capped tool.

## Alternatives considered

**Date-anchored windows (calendar halves/quarters).** Rejected: equal-count windows are deterministic against the panel's own trading calendar and need no timezone or holiday policy; a calendar split of a sparse panel could produce empty windows.

**Regime detection (volatility or trend buckets).** Deferred: bucketing by market state needs a state definition the plugin does not own; equal-count windows answer "does the factor's sign survive time" without inventing one.

**Reporting the window table always.** Rejected: for a short panel the windows are too thin to mean anything; the parameter keeps the default report tight and lets the caller opt into the regime lens.

## Consequences

Costs: `ic_windows` discards up to `windows - 1` tail readings (stated in the docs); the clamp changes no existing output — a zero-dispersion series reported ICIR 0 by convention before only when std was exactly 0, and near-zero std previously produced absurd ratios that no caller could use. Verification: 321 vitest green — new cases cover equal-count splits with date spans, tail-remainder dropping, invalid window counts, the three verdict branches (stable, inverse, flip), the degenerate-dispersion clamp, the compliance cap, and the tool-level `ic_windows` flow into the settled report. Bilingual README row extended; Agent Note trio recorded.
