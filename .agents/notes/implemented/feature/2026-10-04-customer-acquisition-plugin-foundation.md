# Customer-acquisition plugin foundation (P0)

Status: implemented

English | [中文](2026-10-04-customer-acquisition-plugin-foundation.zh.md)

## Context

The 获客运营 (customer-acquisition) feature — GEO diagnosis, lead ledger, AI lead scoring — ships as a compliance-first business plugin for OPC deployments. The feed-in brief froze a data contract and a 47-tool manifest before implementation and demands six red lines (bounded fetching, no automated outreach, no send channel, editable templates, local data, audit trail) as executable checks, not prose. P0 lays the foundation both later phases build on.

## Decision

- **One package pair, one compliance gate.** `@deepseek-ai/dsh-customer-acquisition` owns the frozen `customer_acquisition` domain (13 KV tables + the settings global slot, version 1), the `permissionContext` Service Definition with a bundled local provider, the audit writer, the pre-execute compliance gate, the four P0 tools, and the Typert Remote gateway; `@deepseek-ai/dsh-client-ui-customer-acquisition` mounts it in the browser. Both land in a new `growth/` group. GEO scanning will be a sibling package (`customer-acquisition-geo`) so P1 and P2 file ownership never intersects.
- **The permission seam is the multi-user story.** Single-machine DSH resolves every call to `local-default` with full capabilities; the Kabage platform replaces the provider under the same context key and maps its roles onto `capabilities` outside the plugin. The plugin never sees role names and imports no platform-private package.
- **Red lines live in one pre-execute listener** with pure per-tool rule functions, so every illegal path has a direct unit test; parameter schemas stay descriptive (the DSL has no range constraints) and the gate owns enforcement.
- **Settings went to the domain `global` slot** instead of a table, and open enums (`source`, content `type`) store plain strings with known-value vocabularies so growth never bumps the domain version.

## Rejected

- **zod for tool parameters** — the harness `ParameterSchemaSpec` DSL owns that boundary; zod stays on the domain-record side. Manifest written accordingly.
- **One action-dispatch tool per entity** — 47 single-action tools match the repo's `team_task_*`/`schedule_*` style and keep model-facing schemas unambiguous.
- **Deleting referenced templates** — deletion is refused when score runs or generated content reference a template; callers disable it instead, keeping history reproducible (per-item weight snapshots).

## Consequences, risks, trade-offs

The KV domain has no indexes or in-place migration: a version bump rebuilds the medium (pre-release stance), and list faces filter in memory — fine at single-machine scale, revisited only if a deployment outgrows it. Compliance-denial audits resolve the operator best-effort and never un-deny a call. Fetch orchestration (P2) still must verify the web-fetch consumption form before reuse; the URL and cap rules are already in force.
