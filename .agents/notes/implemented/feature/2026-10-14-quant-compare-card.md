# Agent Note: The panel compares two snapshots on one scale

Status: implemented

English | [中文](2026-10-14-quant-compare-card.zh.md)

## Problem

Each equity card drew exactly one stored curve. Comparing two runs — the point of persisting snapshots — meant eyeballing two separate sparklines with independent y-scales, which is not a comparison at all: a 5% and a 12% return curve can look identical when each maps its own min/max onto the same pixels.

## Decision

- **`CompareLines` joins the chart family.** A second inline-SVG component in `charts.tsx`: two polylines on one shared value scale with a color-keyed legend row beneath. The geometry (`compareLinesPoints`) is a pure function like its siblings — the union min/max over both series maps onto the padded height, and both series spread over the full width — so unit tests pin coordinates without rendering. Zero new dependencies.
- **The comparison is a card-local select, not a global mode.** Expanding a snapshot card fetches its curve as before; a compare select (listing the other snapshots with their headline return) fetches the chosen curve once and overlays both. The Remote face, the service, and the tool surface are untouched — this is presentation over data the panel already reads.
- **One shared scale, two full-width curves.** The union range is the only honest way to overlay two equity curves; per-series scaling was the bug being fixed. Shorter series still spread across the full width (their last point lands at the right edge), so date ranges differ visibly through line density.
- **Colors ride the design tokens.** The primary curve uses the accent token with a literal fallback; the comparison uses the danger token — two hues that the theme system already guarantees are distinct.

## Alternatives considered

**Normalizing both curves to returns (rebased to 1.0).** Deferred: rebasing hides the absolute-cash difference between runs with different `initial_cash`; the shared-absolute-scale overlay keeps that visible. A rebased mode is one pure function away if a caller wants it.

**A cross-card "pin to compare" interaction.** Rejected for now: it needs panel-global selection state and drag-and-drop affordances; the card-local select answers the same question with existing Remote reads.

**Rendering both curves in one polyline set with dashed styles.** Rejected: dashes are indistinguishable at sparkline density; two colors plus a legend are the minimum honest encoding.

## Consequences

Costs: one extra Remote read per comparison (the second curve), cached in card state so re-selecting does not refetch the primary. Verification: 330 vitest green — new cases pin the shared-scale geometry (union range over the padded band, full-width spread for both series), the two-polyline-plus-legend render with the empty-input null branch, and the card flow end to end (expand → select → both curves with the other snapshot's label). Bilingual README updated; Agent Note trio recorded.
