# Agent Note: The cross-section moves into the kernel

Status: implemented

English | [中文](2026-10-13-quant-kernel-cross-ic.zh.md)

## Problem

The cross-IC tool ran its panel math in TypeScript while every symbol's fetch was already a kernel round trip — one subprocess per symbol for bars, then the host re-implemented alignment, the four factors, and the rank correlation. The deferral was explicit: sink the panel computation into the kernel so the correlation runs beside the audited simulator, in one request.

## Decision

- **One new kernel op: `cross_section_ic`.** `kernel-py/pcpt/cross_ic.py` mirrors the TypeScript pipeline exactly — shared-date alignment (intersection, sorted), the four audited factors (momentum, volatility, volume_ratio, price_position with their windows and null warmups), per-date Spearman between the factor cross-section and the horizon-day forward-return cross-section, and the aggregate (mean IC, std, ICIR, positive share, t-stat) with the same sub-basis-point dispersion clamp. The TS `KernelOp` union and the HANDLERS map grow together.
- **The numbers must agree; the conventions must agree.** The kernel carries the same hard caps (panel 2-10, horizon 1-20) as `inspectCrossPanelCaps`, rejects unknown factors and too-few shared dates with `PanelError` (a `ValueError` subclass, so the wire maps it to BAD_REQUEST), and its own pytest pins the perfect-ordering panel, alignment drops, the degenerate clamp, the caps, and the loud failure.
- **The TS pipeline becomes a thin projection.** `runCrossSectionICKernel` issues the one request with the per-symbol bar map; `projectKernelIC` renames the kernel's snake_case summary onto the TS vocabulary (`mean_ic` → `meanIC`, …) so the report formatter, the windowed-IC lens, and the compliance chain are untouched. The pure TS functions (`alignPanel`, `crossSectionIC`, `summarizeIC`) stay exported and tested — they are the executable spec the kernel mirrors.
- **The tool's job body shrinks to fetch + one request.** Per-symbol `get_kline` fetches remain (the audited data path), then a single `cross_section_ic` call replaces the host-side factor/align/correlate block. The start envelope, compliance rules, snapshots boundary, and report shape are unchanged.

## Alternatives considered

**Deleting the TS pure functions and keeping only the kernel path.** Rejected: the pure functions are the specification the kernel is verified against, they keep the report/windowed lens testable without a Python runtime, and removing them would leave the kernel unmirrored.

**Batching the kline fetches into the same op.** Deferred: the fetch path carries the circuit breaker, cache, and retries; folding it into the op would duplicate that policy in Python for one less round trip.

**A wire schema version bump.** Not needed: the op is additive; the protocol version carries it.

## Consequences

Costs: the kernel now owns a second math module to keep in sync — mitigated by the mirroring tests on both sides (33 kernel pytest, 321 TS vitest) and the shared conventions stated in both doc blocks. A cross-IC run costs one subprocess for the whole panel instead of N (fetches still one each). Verification: TS 321 green with the tool fakes asserting the new op sequence (three fetches then one panel request carrying the full bar map); kernel 33 pytest green including the new cross-IC cases. Bilingual README row updated; Agent Note trio recorded.
