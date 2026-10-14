# Agent Note: The real panel mounts its own Remote face and draws inline SVG

Status: implemented

English | [中文](2026-10-09-quant-real-panel.zh.md)

## Problem

The quant-research panel was a placeholder card stating what would ship later, and the core package exported `QuantResearchService` without ever mounting it — the Remote wire had been removed in an earlier slice because nothing consumed it. The named phase-3 remainder was "the real panel with the core package's Remote face," and the chart question (echarts vs bundle size) was an explicitly deferred review item.

## Decision

- **Self-contained Remote assembly, the customer-acquisition pattern.** The browser plugin mounts the core package's Remote contribution itself (`ctx.remote.$mount(quantResearchRemote)`), then runs the panel body on a fiber that injects the exact namespace (`remote.quantResearch` — Cordis snapshots a namespace service only into fibers whose inject lists that name). The gateway closures unwrap the `{ok, value|error}` envelope and name the failed method in the error. No api-remotes change, no shared registry edit: one plugin carries its server face with it.
- **The core package mounts the service it exports.** `apply()` now instantiates `QuantResearchService` as a service fiber (`ctx.plugin(QuantResearchService).await()`), and the service gained `@Remote('listNotes')` beside the two account methods. Wire types (`AccountSummaryValue`, `NoteSummaryValue`, …) moved to a new `src/types.ts` exposed through a `./types` subpath — the plain-projection family (no branded ids, no readonly aliases) so the generated Remote client and the panel share one type family. The `files` allowlist grew the typert artifacts (`lib/typert.*`, `lib/types/**/*.js`) — the typert build fails loud when a Remote package does not ship its generated faces.
- **Inline SVG, no chart library.** `charts.tsx` renders a position-weight bar row (HTML/CSS tracks, percent widths from a pure `barGeometry` function) and a sparkline (an SVG polyline from a pure `sparklinePoints` mapping). Zero new dependencies; the geometry functions are unit-pinned so tests assert coordinates without rendering. The echarts question resolves to "not yet" — recorded as a limitation, not a decision in code.
- **Honest data boundary: position weights, not equity curves.** The durable domain stores accounts, orders, and notes — no equity history — so the panel draws what exists (position market-value weights per account, note lists) instead of fabricating a curve. Equity-curve cards are named as waiting on a session-to-storage results channel.
- **Coverage to the gate, not to the exclusion list.** The client package reached per-file 100% with tests: an apply-spec bench (fake `$mount`, fake namespace, slot declarations) drives mount ordering, gateway unwrapping including the failure branch, shared-controller injection, and disposer teardown; panel tests drive load/cancel/retry, empty states, expansion refetch, and the non-Error rejection stringify. The `v8 ignore` comments that survived carry reasons (the cancelled-read guard).

## Alternatives considered

**echarts (lazy-imported).** Rejected: the repo carried zero chart dependencies, the panel needs two small static visuals, and ~1MB (even tree-shaken) buys tooltips the read-only surface does not need. Revisit if interactive exploration lands.

**Equity-curve cards from tool outputs.** Rejected for this slice: backtest/optimize results live in the session transcript, not the durable domain; piping them into storage is a separate channel with its own retention questions. Drawing them from nothing was the alternative that lost.

**Mounting the service only in the web profile.** Rejected: `apply()` is the plugin's one composition path; a profile-conditional mount would make the panel's Remote namespace exist only in some compositions and turn a missing face into a runtime surprise instead of a load-time guarantee.

## Consequences

Costs: the core plugin now opens the domain twice (plugin body + service fiber) — the apply spec asserts both opens and both closes; the Remote surface is read-only by construction (two account reads + one notes read), so the panel cannot bypass the compliance gate. Verification: the core package is 259 vitest green (4 new service cases over the real storage stack), the client package is 25 vitest green with per-file 100% coverage on both packages, `verify-client-packages` passes with the corrected dependency split (static client inputs are devDependencies only), and the full workspace build regenerates the typert faces. Deferred: equity-curve cards (needs a results channel), interactive charts, and tool-output cards in the panel.
