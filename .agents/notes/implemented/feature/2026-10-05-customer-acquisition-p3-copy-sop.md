# Customer-acquisition P3: nurture copy + follow-up SOP

Status: implemented

English | [中文](2026-10-05-customer-acquisition-p3-copy-sop.zh.md)

## Context

P3 of the 获客运营 plugin ships modules 4 and 5 — nurture-copy generation with A/B variants and follow-up SOP task orchestration — after P1 merged and P2 landed as the sibling geo package. The copy flows ride the same PromptCompletion port and row-config AI route P1 established; the SOP flows are deterministic (no model calls).

## Decision

- **Copy generation reuses the P1 AI posture wholesale.** One model call per artifact through the PromptCompletion port: template chain (explicit id → enabled of that type → type+industry → industry-absent → any), lead fields plus knowledge injection, strict empty-output rejection, artifact persisted under the lead with the template id recorded. Red line 3 holds: text out, no send channel.
- **SOP generation is deterministic cadence math.** The template's rule for the lead's intent level drives one task per follow-up point; `D+N` offsets parse from the cadence text and schedule tasks; points beyond the parsed offsets clamp to the last offset. Unscored leads refuse with "score first"; pool leads must be claimed. `todo_written` stays false — DSH todos are the agent's own `todo_write` checklist with no writable service, so the tool returns a ready-to-forward list when the settings flag is on (platform fact recorded in the README).
- **SOP template deletion has no reference guard** — the frozen sop_tasks schema carries no template id, so deletion cannot orphan history; generated tasks are independent rows. Content templates keep the reference guard because generated copies do record their template id.
- **Seeds extend the same id space** — each industry gains one follow-up SOP (rules for every intent level) and two copy templates (wecom first-touch plus an industry-specific second), seeded with the same skip-if-present strategy.

## Rejected

- **Writing todos programmatically** — no service exists; faking `todo_written=true` would lie in the audit trail. The render forwards a usable list instead.
- **Reference-guarding SOP template deletion** — no foreign key exists to guard on; guarding a guard would be theater.
- **Per-type system prompts** — one copywriting system prompt plus per-type guides in the user prompt keeps the prompt assembly in one place.

## Consequences, risks, trade-offs

The tools registry now carries 44 tools (4 P0 + 27 P1/P3-name... see P1 note for the manifest count reconciliation). Copy generation shares the scoring service's model route, so an unreachable route fails copy per call. Task scheduling trusts the cadence text's `D+N` markers; cadences without markers schedule everything at day 0.
