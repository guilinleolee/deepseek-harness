# Customer-acquisition P4: the data dashboard and the eight-page workbench

Status: implemented

English | [中文](2026-10-06-customer-acquisition-p4-dashboard.zh.md)

## Context

P4 closes the customer-acquisition plugin's manifest §9: a `customer_acquisition_report_overview` tool the agent can call, plus the eight-page workbench the operator sees in the web panel. The foundation (P0), the lead ledger and AI scoring (P1), the bounded GEO website diagnosis (P2), and the nurture-copy and follow-up-SOP modules (P3) all feed their domain tables into one aggregation seam; P4 is the read-only top of that pyramid — every write stays where it was, the dashboard never mutates.

## Decision

- **One aggregation service feeds both surfaces.** `ReportService` is a stateless read over the open domain: the seven manifest metrics (lead volume, windowed new-lead trend, intent/source/score distributions, SOP task outcomes, GEO roll-up) collapse into one `OverviewValue` per call. The `report_overview` tool serves the agent; `@Remote getOverview` plus the per-module `@Remote list*` faces serve the panel. No second aggregation path, no cached projection — the panel re-reads on every selector change.
- **The ledger's list scope is the dashboard's scope.** `lead_scope=own` operators see their own leads plus the pool in every metric that filters by lead (counts, intent, source, score, tasks); GEO metrics are site-level and shared because a scan's URL is not an operator's property. The panel resolves the web operator per call, so the same Remote face serves every employee without a per-role variant.
- **Window and drill-down are request-time, not stored.** `period` (today/week/month/custom) and `group_by` (none/industry/source) ride on `OverviewRequest`; the service resolves the window from the injected clock (deterministic in tests) and groups in memory. A custom range without both bounds fails loud; an inverted range fails loud. No persistence, no migration.
- **The wire types live on the public type subpath.** The Typert generator requires every `@Remote` boundary type to be exported from a public non-root type subpath, so the overview types moved from `src/report/types.ts` into `src/types.ts` beside the other wire projections, the panel faces re-export their ledger/scoring boundary types, Remote parameters drop their default values (optional instead), and the read faces carry explicit array return types instead of `ReturnType` lookups. The lib/typert.remote-client artifact carries the 14 Remote methods the panel mounts.
- **The workbench is one shared open/close controller plus eight branch-free pages.** `useRemoteRead` owns the loading/ok/failed lifecycle for every page; `ReadFallback` renders the two non-ok states identically everywhere, so each page renders its value table directly. The overview page carries period and drill-down selectors and refetches on change; the GEO page opens one report inline; the settings page writes the page cap through `updateSettings` with non-integer rejection. The placeholder P0 panel retires.

## Rejected

- **A second aggregation over a materialized projection table** — the domain already holds every record; a projection table would duplicate state and require migration on every upstream change. The aggregation is cheap enough to recompute per call.
- **Per-role panel variants** — the same Remote face serves every operator because the list scope is the operator's, not the panel's. A role-branched UI would duplicate the read wiring for no gain.
- **`ReturnType<Service['method']>` on the Remote faces** — the Typert generator must see the boundary type by name, so the return types are explicit arrays; `ReturnType` would hide them behind an alias the generator cannot re-export.
- **Default-valued Remote parameters** — the Typert generator rejects default values on `@Remote` parameters; the panel's `?` optional form carries the same "omit to use defaults" contract without tripping the generator.

## Consequences, risks, trade-offs

The dashboard is read-only and idempotent; every page is a pure function of its Remote read, so the panel never writes through the dashboard. The shared read hook means a new page costs one read closure and one value table — the loading and failure states are already wired. The aggregation trusts the domain tables' `created_at` for windowing and `intent_level` for the intent distribution; a record with an unset intent passes (the bucket is zero-filled). The typert boundary-type rule is now load-bearing: any future `@Remote` face that introduces a new boundary type must re-export it from `src/types.ts` or the generator fails at build. The eight-page bundle is 220 KB / 39 KB gzip — the content-studio precedent holds.
