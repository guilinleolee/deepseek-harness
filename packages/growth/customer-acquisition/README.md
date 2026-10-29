---
description: "Customer-acquisition operations for DSH: compliance-enforced GEO diagnosis, a lead ledger, and AI lead scoring, delivered as one plugin for OPC deployments."
kind: "package-bundle"
---
# @deepseek-ai/dsh-customer-acquisition

English | [中文](README.zh.md)

## Summary

Customer-acquisition operations for DSH: compliance-enforced GEO diagnosis, a lead ledger, and AI lead scoring, delivered as one plugin for OPC deployments. P0 shipped the foundation — the frozen v1 storage domain, the PermissionContext seam, the pre-execute compliance gate, the audit trail, and the browser Remote gateway the web panel mounts. P1 adds the lead ledger (module 2) and AI lead scoring (module 3): 27 model-facing tools, the preset three-industry template seeds, and per-call owner scoping. The frozen data contract and the full tool manifest live in [docs/data-contract.md](docs/data-contract.md) and [docs/tools-manifest.md](docs/tools-manifest.md).

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Domain](#domain)
- [PermissionContext seam](#permissioncontext-seam)
- [Compliance gate (red lines)](#compliance-gate-red-lines)
- [Lead ledger (module 2)](#lead-ledger-module-2)
- [AI lead scoring (module 3)](#ai-lead-scoring-module-3)
- [Tools](#tools)
- [Remote face](#remote-face)
- [Dev Note](#dev-note)

-----

## Installation

```sh
dsh plugin --profile web add @deepseek-ai/dsh-customer-acquisition
```

The bundle patch inserts both rows — this plugin and the `@deepseek-ai/dsh-client-ui-customer-acquisition` panel — so one command installs the whole feature. Restart the profile to load them.

## Configuration

Row config (`config:` on the plugin row) tunes the internal model calls the AI faces make (lead extraction, lead scoring):

```yaml
- name: '@deepseek-ai/dsh-customer-acquisition'
  config:
    ai:
      provider: deepseek
      model: deepseek-chat
      timeoutMs: 120000
      maxOutputTokens: 2000
```

Every field is optional and defaults as shown (`provider` = the registered LLM provider route, `timeoutMs` = the per-call deadline bounded to 1000-300000, `maxOutputTokens` = the output cap bounded to 256-32000); out-of-range values fail the plugin at load. The red-line limits (page cap, timeout cap, batch cap) are constants enforced in code and re-checked by the compliance gate — they are not configurable. Everything user-adjustable at runtime lives in the `settings` global slot of the domain, changeable through `customer_acquisition_settings_set`.

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

## Lead ledger (module 2)

`LeadLedgerService` is the single authority for leads, follow-ups, and attached documents; the 16 `customer_acquisition_lead_*` tools are thin projections of it. Ownership is enforced server-side on every call: `lead_scope=own` operators read only their own leads plus the pool (`owner_id` absent) and write only their own; the pool is claimed through `lead_assign`, released through `lead_transfer` without a target owner. Delete is soft (recycle bin) — `lead_restore` brings a lead back, `lead_purge` physically removes it with every follow-up, document, score run, generated copy, and SOP task, and requires `can_delete_any_lead`. Attached documents (20 000 chars each) are the knowledge source injected into scoring and copy generation. `lead_extract` parses only the text handed to it — one model call, no network collection — and returns fields without storing; the caller confirms through `lead_create`. Export renders Markdown tables or formula-guarded CSV and audits itself.

## AI lead scoring (module 3)

Scoring is one model call per lead: the service resolves the ICP profile and prompt template (explicit id → enabled global default → exact industry match → industry-absent → any enabled), renders the template's `{{lead}}`/`{{icp_profile}}`/`{{dimensions}}`/`{{knowledge}}` placeholders, validates the JSON answer (every dimension scored exactly once, finite 0-100 scores, non-empty reasons), and persists the run with a per-item weight snapshot — history stays reproducible when weights change later. The weighted total maps to an intent tag (≥80 high, ≥60 mid, ≥30 low, else invalid) written back to the lead. `score_batch` runs up to 50 leads serially; one failure never aborts the batch. ICP profile and template CRUD gate on `can_manage_global_templates`; a profile or template referenced by any run refuses deletion (disable it instead). Three industry packs — retail, B2B manufacturing/trade, software services — seed idempotently at mount under fixed `seed-*` ids and never overwrite user edits.

## Tools

| name | what it does |
|---|---|
| `customer_acquisition_settings_get` | Read the global settings (the P0 smoke tool). |
| `customer_acquisition_settings_set` | Merge a partial settings update; requires `can_manage_settings`, rejects unknown profile/template ids. |
| `customer_acquisition_audit_list` | Paged, filtered audit-log queries. |
| `customer_acquisition_audit_export` | Full-filter export as Markdown or formula-guarded CSV; requires `can_export`. |
| `customer_acquisition_lead_create` / `lead_update` / `lead_get` / `lead_list` | Ledger CRUD with multi-dimension filters, keyword search, and paging. |
| `customer_acquisition_lead_delete` / `lead_restore` / `lead_purge` | Recycle-bin lifecycle; purge cascades every associated record. |
| `customer_acquisition_lead_assign` / `lead_transfer` | Pool claiming and ownership transfer. |
| `customer_acquisition_lead_extract` | Fields from one user-provided text snippet; model-backed, nothing stored. |
| `customer_acquisition_lead_export` | Filtered export as Markdown or guarded CSV; requires `can_export`. |
| `customer_acquisition_lead_document_add` / `lead_document_list` / `lead_document_remove` | Plain-text knowledge attached to a lead. |
| `customer_acquisition_lead_followup_add` / `lead_followup_list` | Follow-up notes, newest first. |
| `customer_acquisition_score_one` / `score_batch` | AI scoring with weight snapshots and intent write-back; batch is serial with per-lead failure isolation. |
| `customer_acquisition_score_history` | Fully retained runs with per-dimension snapshots. |
| `customer_acquisition_icp_create` / `icp_update` / `icp_list` / `icp_delete` | ICP profiles; weights must sum to 100, referenced profiles refuse deletion. |
| `customer_acquisition_score_template_create` / `score_template_update` / `score_template_list` / `score_template_delete` | Scoring prompt templates with the four placeholders; referenced templates refuse deletion. |

## Remote face

`CustomerAcquisitionService` publishes `customerAcquisition.getSettings`, `customerAcquisition.updateSettings`, and `customerAcquisition.listAuditLogs` through `TypertRemoteService`; the generated `./remote` artifact mounts them in the browser panel. Every write resolves the web operator through the seam and audits.

## Model Experience

### Local customer-acquisition state

#### What the model sees

Thirty-one tools joined to prompt assembly when the plugin loads — the four P0 settings/audit tools plus the 27 lead-ledger and scoring tools — and their text renders: lead refs as one-line summaries, score outcomes as headline plus per-dimension lines, exports as fenced Markdown/CSV documents, and extraction results as field lists. Denials from the compliance gate and capability checks surface as tool errors carrying the Chinese reason. The three industry seed packs appear as ready-to-use profiles and templates on first run.

#### Token effect

Bounded: 31 tool schemas (~4k tokens) in every assembled request while the plugin is loaded; list faces cap at 100 rows per page and score renders scale with the profile's dimension count (typically 5-6 lines).

#### KV Cache effect

The schemas join the tool block of the prompt prefix; loading or unloading the plugin invalidates the reusable prefix from that point, as any tool registration does.

## Known Limitations and Deferred Work

- **P1+P3 scope** — GEO diagnosis lives in the sibling `customer-acquisition-geo` package, and the dashboard tool lands with P4; the copy and SOP tools shipped with P3.
- **Seeds cover ICP, scoring, SOP, and copy** — the three industry packs seed profiles, prompt templates, follow-up SOPs, and two copy templates each.
- **Panel is a placeholder** — the web surface mounts the Remote face and shows settings plus recent audit entries; the eight-page panel ships with P4, and the lead/scoring Remote reads and writes land there.
- **Scoring needs a reachable model route** — `ai.provider`/`ai.model` must name a registered route with credentials; scoring, extraction, and copy generation fail per call otherwise, and batch failures isolate by lead.
- **Copy sender falls back to the template example** — `{{sender_name}}` resolves from the global `sender_name` setting (`settings_set`) first, then the template's `variables[].example`; with neither, the placeholder stays visible and is flagged as skip.
- **Todo linkage is forward-only** — DSH todos are the agent's own `todo_write` checklist with no writable service; `sop_generate_tasks` returns a ready-to-forward list when the settings flag is on, and `todo_written` stays false.
- **SOP generation is idempotent by title** — when a lead already has an open (pending/deferred) task of the same title, the point is skipped and reported in `skipped`; done/dropped points may be generated again.
- **Operator identity is trivial locally** — `local-default` holds every capability; meaningful `lead_scope` enforcement begins when platform providers inject real users.
- **Audit growth is unbounded** — records are never pruned; retention policy waits for a concrete deployment requirement.


<a id="dev-note"></a>
### Dev Note

<details>
<summary>Working context for maintainers — click to expand</summary>

None.

</details>
