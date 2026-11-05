# Agent Note: Result snapshots carry the equity curve to the panel

Status: implemented

English | [中文](2026-10-13-quant-result-snapshots.zh.md)

## Problem

Phase 3 closed with an honest boundary: the panel rendered position weights and note lists because the durable domain held no equity history, and fabricating curves from tool outputs was explicitly rejected. The named prerequisite was a session-to-storage results channel. Until it existed, the panel could not show performance — the single most expected view of a research backtester.

## Decision

- **The channel is a domain table, not a transcript parse.** `quant_research` domain v3 adds `result_snapshots`: one record per successful `quant_run_backtest` carrying the run's parameters, headline metrics, and the equity curve downsampled to at most 240 points (`downsampleEquity`, deterministic stride, first and last points always survive). The table keeps the newest 50 snapshots (`SNAPSHOT_KEEP_LIMIT`), pruning oldest-first at save time. Walk-forward and optimization runs do not snapshot — only the tool with a full per-bar curve does.
- **The write rides the tool's success path and stays invisible to the model.** `quant_run_backtest` persists the snapshot inside its envelope body after the kernel returns; the model-visible output remains the plain report. A storage failure fails the tool loudly (misconfiguration fails loud), and the compliance gate is untouched — the Remote surface stays read-only by construction.
- **The Remote face grew two read methods.** `listResultSnapshots` projects summaries without equity points (list stays light); `getEquityCurve` returns one stored curve. Projections live in `./types` with the existing wire family (`ResultSnapshotSummaryValue`, `EquityCurveValue`).
- **The panel renders stored curves, reusing the sparkline.** A third panel section lists snapshot cards (symbol, SMA windows, total return, max drawdown, trade count, date); expanding fetches the curve once and draws it as an inline-SVG sparkline at card size. No new chart geometry — the existing `sparklinePoints` mapping already covers a line chart.
- **Domain v3 follows the established evolution stance**: additive table, version bump, no migration — a v2 medium rejects at open.

## Alternatives considered

**Parsing the session transcript for equity data.** Rejected: transcript data is not durable, not queryable by the panel's Remote face, and couples the panel to prompt-transcript internals.

**Snapshotting every tool (walk-forward, stress, optimize).** Deferred: those runs have different report shapes and the panel has one card kind; widening `kind` is additive when a second consumer appears.

**A separate equity-only table.** Rejected: metrics without their curve (or the reverse) invites divergent records; one snapshot row per run keeps the projection trivial.

## Consequences

Costs: the domain version is now 3 (v2 media reject at open — acceptable in the pre-release stance, and every composition in this repo opens the spec fresh); each backtest pays one small durable write. Verification: quant suite 265 vitest green (snapshot downsample/prune/order cases, the tool's snapshot-write case, and the Remote list/curve cases over the real storage stack), the panel suite covers the empty state and expand-to-curve, and the full workspace build regenerates the typert faces. The master build blockers this slice had to clear were pre-existing (`commander` wrongly purged from bundle/web-app while `startup.ts` still imports it; seven experimental/creation tsconfigs still referencing the deleted invariants package) — fixed in the same change so `build:lib:host` runs.
