# @deepseek-ai/dsh-customer-acquisition

English | [中文](README.zh.md)

Customer-acquisition operations for DSH: compliance-enforced GEO diagnosis, a lead ledger, and AI lead scoring, delivered as one plugin for OPC deployments. P0 ships the foundation — the frozen v1 storage domain, the PermissionContext seam, the pre-execute compliance gate, the audit trail, four model-facing tools, and the browser Remote gateway the web panel mounts. The frozen data contract and the full tool manifest live in [docs/data-contract.md](docs/data-contract.md) and [docs/tools-manifest.md](docs/tools-manifest.md).

## Installation

```sh
dsh plugin --profile web add @deepseek-ai/dsh-customer-acquisition
```

The bundle patch inserts both rows — this plugin and the `@deepseek-ai/dsh-client-ui-customer-acquisition` panel — so one command installs the whole feature. Restart the profile to load them.

## Configuration

None. The plugin has no deployment-varying tunables: the red-line limits are constants enforced in code and re-checked by the compliance gate (see below), and everything user-adjustable lives in the `settings` global slot of the domain, changeable at runtime through `customer_acquisition_settings_set` or the panel.

## Domain

`ctx.storageDomain.open(customerAcquisitionDomainSpec)` opens the `customer_acquisition` domain (version 1): thirteen KV tables (`leads`, `lead_followups`, `lead_documents`, `score_runs`, `score_run_items`, `icp_profiles`, `score_templates`, `content_templates`, `generated_contents`, `sop_templates`, `sop_tasks`, `geo_scans`, `geo_reports`, `audit_logs`) plus the `settings` global slot. Every record schema is zod; open enums (`source`, content `type`, `industry`) store plain strings so new known values never bump the domain version. The contract is frozen: any structural change requires a version bump and owner confirmation.

## PermissionContext seam

`ctx.permissionContext` is a Service Definition owned by this package: `resolve(request): Promise<ResolvedOperator>` with `{ userId, displayName, capabilities }`. The bundled `LocalPermissionProvider` answers every call with the constant local default user (`local-default`) holding the full capability set — no login, no roles. The Kabage enterprise platform replaces the provider under the same key via its own bundle patch and maps its roles onto `capabilities`; this plugin never sees role names and imports no platform-private package. Every tool execute and every mutating Remote method resolves the operator per call; list and write paths filter `owner_id` server-side by `lead_scope`.

## Compliance gate (red lines)

One `tools/pre-execute` listener owns enforcement for every `customer_acquisition_*` call and delegates the rest via `next()`:

1. **Fetch boundary** — the GEO scan accepts only an explicitly provided http(s) URL with a host; the page count is capped at 20 and the per-page timeout at 10s (also encoded in the settings schema, so a stored value cannot exceed them). Fetching itself arrives with P2 and reuses the web fetch capability with serial concurrency 1, a 2 MiB body cap, robots.txt `Disallow` skipping, and no domain auto-discovery.
2. **No automated outreach** — the plugin ships no auto-messaging, friend-request, or account-automation dependency; a unit test asserts the dependency lists stay clean.
3. **No send channel** — generated copy is text-only; a source scan test asserts no SMTP/mail/SMS implementation enters `src/`.
4. **Editable templates** — the four template tables exist in the frozen domain; CRUD tools land with P1/P3.
5. **Local data** — all business data stays in this domain; nothing else writes it.
6. **Audit trail** — every mutation and every compliance denial appends one `audit_logs` record with `source` and `operator_user_id`, queryable and exportable through the two audit tools and the panel.

Each red line has at least one illegal-path unit test.

## Tools

| name | what it does |
|---|---|
| `customer_acquisition_settings_get` | Read the global settings (the P0 smoke tool). |
| `customer_acquisition_settings_set` | Merge a partial settings update; requires `can_manage_settings`, rejects unknown profile/template ids. |
| `customer_acquisition_audit_list` | Paged, filtered audit-log queries. |
| `customer_acquisition_audit_export` | Full-filter export as Markdown or formula-guarded CSV; requires `can_export`. |

## Remote face

`CustomerAcquisitionService` publishes `customerAcquisition.getSettings`, `customerAcquisition.updateSettings`, and `customerAcquisition.listAuditLogs` through `TypertRemoteService`; the generated `./remote` artifact mounts them in the browser panel. Every write resolves the web operator through the seam and audits.

## Model Experience

### Local customer-acquisition state

#### What the model sees

Four tools (`customer_acquisition_settings_get/set`, `customer_acquisition_audit_list/export`) joined to prompt assembly when the plugin loads, plus their text renders: the settings snapshot as a field list, audit rows as dated lines, and exports as a fenced table/CSV document. Denials from the compliance gate surface as tool errors carrying the Chinese reason.

#### Token effect

Bounded: four tool schemas (~600 tokens) in every assembled request while the plugin is loaded; results are paged (audit list caps at 100 rows per page).

#### KV Cache effect

The schemas join the tool block of the prompt prefix; loading or unloading the plugin invalidates the reusable prefix from that point, as any tool registration does.

## Known Limitations and Deferred Work

- **P0 scope** — the lead, scoring, GEO, copy, SOP, and dashboard tools of the frozen manifest are not implemented yet; the domain tables exist but only settings and audit carry P0 behavior. Phases land in order P1 → P2 → P3 → P4 per the data contract.
- **Seed templates not sown** — the three industry template packs (retail / B2B trade / software) arrive with P1/P3; their fixed id space and idempotent strategy are frozen in the contract.
- **Panel is a placeholder** — the web surface mounts the Remote face and shows settings plus recent audit entries; the eight-page panel ships with P4.
- **Operator identity is trivial locally** — `local-default` holds every capability; meaningful `lead_scope` enforcement begins when platform providers and the P1 lead tools arrive.
- **Audit growth is unbounded** — records are never pruned; retention policy waits for a concrete deployment requirement.
- **Fetch orchestration not wired** — the P2 GEO scanner must verify the exact web-fetch consumption form before reuse; the gate's URL and cap rules are already in force.
