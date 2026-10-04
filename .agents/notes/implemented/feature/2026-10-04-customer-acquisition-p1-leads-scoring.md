# Customer-acquisition P1: lead ledger + AI lead scoring

Status: implemented

English | [中文](2026-10-04-customer-acquisition-p1-leads-scoring.zh.md)

## Context

P1 of the 获客运营 plugin ships modules 2 and 3 of the frozen manifest — the lead ledger (16 tools) and AI lead scoring (11 tools) — in parallel with a separate GEO session that owns `packages/growth/customer-acquisition-geo/`. The data contract, the PermissionContext seam, the audit writer, and the compliance gate are P0 read-onlys; the frozen contract pins scoring semantics to "one LLM call produces one run and its items".

## Decision

- **Two module services borrow the P0 domain.** `LeadLedgerService` and `LeadScoringService` are plain classes constructed in the runtime fiber; the domain stays single-open (a storage-domain invariant) inside `CustomerAcquisitionService`, whose `requireDomain()` widened from private to public so the modules borrow tables instead of re-opening. No new context keys, so the growth group README stays untouched.
- **Scoring is one model call per lead through a port.** The service renders the template's four placeholders (knowledge = the lead's documents, capped at 4 000 chars), calls a `PromptCompletion` port, and strictly validates the JSON answer: every dimension scored exactly once, no unknown dimensions, finite 0-100 scores, non-empty reasons. Each item snapshots the weight at scoring time, so later weight edits never distort history; the weighted total maps to the intent tag (≥80/≥60/≥30) written back to the lead. Tests inject a deterministic fake — no test touches a real model.
- **Pool semantics live in the read rule.** `lead_scope=own` reads own-plus-pool everywhere (list, detail, documents, scoring history) but writes only its own leads; scoring a pool lead asks the operator to claim it first. Purge requires the recycle-bin state plus `can_delete_any_lead` and cascades six tables.
- **Seeds are ICP+scoring only, idempotent by fixed seed id.** The three industry packs mount-time seed one profile and one prompt template each under `seed-*` ids; a present record is never touched, so user edits survive restarts. SOP and copy templates stay with P3.
- **The AI route is row config, not a constant.** `config.ai` (provider/model/timeoutMs/maxOutputTokens) resolves with defaults at mount and fails loud out of range; the internal calls ride the shared `llm` Service Definition via `@deepseek-ai/dsh-llm` + `@deepseek-ai/dsh-timeout` (both approved workspace additions, peer+dev).

## Rejected

- **A second `storageDomain.open`** — the facility enforces single-open per name; borrowing the handle through the P0 service keeps exactly one closer.
- **Model-in-the-loop scoring** (tool persists whatever the calling agent claims) — it would contradict the frozen contract's "one LLM call produces a run" and lose the server-side weight snapshot.
- **Extra unknown dimensions in the model answer** — rejected, not ignored: an unscored or invented dimension would silently skew the weighted total.
- **Retries around scoring calls** — batch already isolates per-lead failures; rate-limit retry policy can join the port later without touching services.

## Consequences, risks, trade-offs

P0 composition tests now stub `llm` (the runtime fiber injects it) and assert 31 tools. The lead manifest's §10 count line says 14 module-2 tools while its detailed sections define 16 — the detailed definitions win; the frozen doc's count line stays as-is for its owner to reconcile. List faces filter in memory (fine at single-machine scale). Extract audits as `lead.extract` though nothing is stored, per the manifest; web-source lead/score auditing arrives with the P4 panel Remote face.
