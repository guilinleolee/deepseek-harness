# Agent Note: Cross-sectional IC evaluates factors across a panel

Status: implemented

English | [中文](2026-10-13-quant-cross-sectional-ic.zh.md)

## Problem

The factor-IC tool answered one narrow question — does factor X predict symbol Y's own future? — through a single-symbol time-series IC. The standard factor-research question is cross-sectional: at the same moment, do the factor's values rank the symbols in the order their forward returns realize? A factor can look strong in time series and carry no cross-sectional discriminating power (or point the other way), and only the panel view separates those cases.

## Decision

- **A new tool, not a mode of the old one.** `quant_factor_cross_ic` (18th tool) starts one background job that fetches each panel symbol's bars (one kernel subprocess per symbol, 2-10 symbols, compliance-capped by `inspectCrossPanelCaps` — array shape, dedupe, and a horizon cap 1-20 join the existing bar and broker-marker rules). The old single-symbol `quant_factor_ic` keeps its contract; the two ICs have different denominators and merging them would blur both.
- **Pure panel math in `paat/cross-ic.ts`.** `alignPanel` intersects the symbols' dates (missing dates drop rows, fewer than two shared days fails loud); `factorOnDates` reuses the audited `computeFactor` per symbol with no lookahead; `crossSectionIC` computes each date's Spearman between the cross-section of factor values and the cross-section of horizon-day forward returns; `summarizeIC` aggregates mean IC, dispersion, ICIR, positive share, and the t-statistic (0 by convention when the IC series has no dispersion). All four are table-grade pure functions pinned by unit tests without a kernel.
- **The report carries the reading discipline.** The markdown states that cross-sectional IC measures same-instant ranking power across symbols (not the time-series notion), renders the aggregate plus the last six section ICs, and gives a direct verdict against the |ICIR| ≥ 0.5 experience threshold — including the negative-direction warning when a factor ranks inversely.
- **JobKind `quant-cross-ic`, start-envelope parity.** The tool follows the optimize/walk-forward job pattern exactly: preflight validation before any job starts, one AbortController fanned across every symbol fetch, the friendly CONFIG envelope when no jobs runtime is composed, and a start card carrying job id, panel, factor, and the collection hint.

## Alternatives considered

**Extending `quant_factor_ic` with a `symbols` array.** Rejected: the tool's parameters, output schema, and compliance rules are single-symbol; an array mode would fork the schema in place and make the denial reasons ambiguous about which cap fired.

**Computing the panel in the kernel (one op).** Deferred: the kernel already ships audited per-symbol bars; the cross-section is a rank correlation over aligned arrays that TypeScript computes exactly. A kernel op would add a wire shape without changing a single number.

**Rolling-window cross-sectional IC (regime stability).** Deferred with the other rolling items: the aggregate over the full panel already exposes stability through the IC dispersion; windowed IC waits for a consumer.

## Consequences

Costs: one kernel subprocess per panel symbol per run (up to 10), all inside one cancellable job. Verification: 312 quant vitest green — 12 new cases covering alignment (intersection, sorted dates, loud failure), perfect-ordering IC, degenerate and invalid horizons, the null-summary branch, the report verdicts, the compliance caps, and the tool's job lifecycle end to end (fetch order, start card, settled markdown). Tool count moves 17 → 18 with the registration, apply-spec, and README counts moved together; bilingual README plus the Agent Note trio are re-paired.
