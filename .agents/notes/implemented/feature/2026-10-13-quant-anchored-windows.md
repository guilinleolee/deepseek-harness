# Agent Note: Anchored rolling windows and per-window snapshots

Status: implemented

English | [中文](2026-10-13-quant-anchored-windows.zh.md)

## Problem

Two deferrals from the rolling-walk-forward slice: the train leg was expanding-only (a fixed-length anchored window was the conservative alternative with no knob), and rolling runs wrote no result snapshots (so the panel's equity cards — the flagship Phase4 surface — stayed blind to every rolling run, showing only single backtests).

## Decision

- **`anchor` pins the train length; absence keeps expanding.** `quant_walk_forward` gains `anchor` (30-1000 bars, `inspectAnchorCap` compliance-capped). With `windows >= 2` and an anchor, `splitAnchoredWindows` walks the series in `segmentLength = floor((n - anchor) / windows)` steps: window *i* trains on the `anchor` bars ending where its test segment starts — fixed length, sliding position, no overlap between test segments, no lookahead. The report's split section and the job label both state the mode; the expanding default is byte-for-byte unchanged.
- **Validation mirrors the split.** `validateAnchoredParams` checks the window count, the anchor bounds, that the anchor covers the widest slow window (grid warmup), that each test segment does too, and delegates the grid invariants to the existing `validateGridSpec` against the anchor length.
- **Rolling runs snapshot every window.** `runRollingWalkForward` takes an optional `onWindow(result, barsUsed)` hook; the tool passes a closure persisting each window's out-of-sample report through the audited `saveSnapshot` channel (params = the window's re-selected pair plus the bars its two legs covered). The aggregate markdown remains the model-visible output; the snapshots are the durable side channel, capped by the same keep-50 pruning. A snapshot write failure fails the job loudly — a rolling report with silently missing windows would misstate the panel.
- **The tool return carries the shape.** The start envelope adds `anchor` only when anchored, so callers and tests can distinguish the two modes without inferring from geometry.

## Alternatives considered

**A separate `quant_walk_forward_anchored` tool.** Rejected for the same reason as before: one integer's worth of mode difference does not justify a second tool surface, a second JobKind, and a second rule chain.

**Snapshots for the aggregate (one record per rolling run).** Rejected: the snapshot schema carries one equity curve; the aggregate document is markdown. Per-window records reuse the existing schema exactly and give the panel one card per out-of-sample segment — which is the point.

**Silently skipping a failed window snapshot.** Rejected: partial persistence would show a rolling run as fewer windows than it had, with no indication. Failing loud matches the plugin's storage stance.

## Consequences

Costs: an anchored run uses only `anchor + segmentLength * windows` bars (the tail shorter than one segment drops — stated in the split section); every rolling run now writes up to 10 snapshot records. Verification: 316 vitest green — new cases cover the anchored geometry (fixed length, sliding position, non-overlapping tests, no lookahead), the anchored validation bounds, the anchor compliance cap, the tool-level anchored job with its mode label, and the rolling job's per-window snapshot writes (two windows → two stored records). Bilingual README updated; the deferral list loses its first two entries.
