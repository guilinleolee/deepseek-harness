# Agent Note: The global template library keeps skeleton assets outside the outputs library, and the body — not the variable table — is the source of truth

Status: implemented

English | [中文](2026-09-27-dsh-content-studio-template-library.zh.md)

## Problem

The Content Studio columns kept reinventing initialization scaffolds: the create workbench grew its own `_templates.json`, the 互动 plan parked reply templates in localStorage as a stopgap, and every future column would add another. The template-library plan (v2, `D:\dsh-content-studio\docs\template-library-dev-prompt-v2.md`) called for one global asset store — variable skeletons with version history, import/export, and a cross-column picker — under four frozen edges from its review: taxonomy must live on disk (the localStorage ban), AI must stay outside the save path, data contracts freeze before implementation, and the cross-column integration needs a declared interface instead of per-column guesswork.

## Decision

- **The library lives outside the outputs library on purpose.** Every other global store (`_schedule.json`, `_topics.json`, `_personas.json`) sits at the outputs root under the scanner's `_`-prefix blind spot. Templates go to `<dsh home>/templates/` (Config `templatesRoot`, resolved like `root`) instead: they are skeleton assets, not theme data, so no outputs scan may ever project them and no theme teardown may ever sweep them. Files: `templates.json` (`formatVersion 0`, refuse-write on unknown versions or dropped records, per persona), `taxonomy.json` for the shared tags, and one full-record snapshot per manual save under `history/<id>/<version>.json`, trimmed to the newest 20. Nine faces ride the content-outputs Remote (`listTemplates` / `putTemplate` / `setTemplateStatus` / `deleteTemplate` / `getTemplateHistory` / `putTemplateTags` / `exportTemplates` / `importTemplates` / `processTemplateAi`), same carrier as every other write face.
- **The body is the source of truth.** A fence-aware, inline-code-aware, escape-aware scanner (`client/template/model.ts`) derives the active placeholder set from the Markdown body; `reconcileVariables` aligns stored metadata to it — known names keep their metadata, unknown placeholders get fresh entries, and metadata whose placeholder disappeared parks in an explicit `unused` section shown in the editor but never auto-deleted. This is AI-Gist's `reconcilePromptVariables` insight (verified at `yarin-zhang/AI-Gist`, 889★): metadata follows the body, because a variable table that can disagree with the text is a second truth. Rendering never touches code regions and reports unfilled-or-unknown names as `unresolved` instead of guessing.
- **AI is explicit, draft-only, and degradable.** `processTemplateAi` (generate / optimize / extract) rides the shared one-shot LLM helper with rate-limit-only retry; results land in a preview panel the user adopts into the editor or discards — nothing is persisted by an AI call, mirroring the persona face. The manual path is complete without AI: a template is fully writable by editing the body text directly (the reconcile loop picks up hand-written placeholders), so a missing key degrades the assistive features, never the store.
- **The picker is a contract, not a coupling.** A column opens it with a `TemplatePickTarget` — category, target label, `hasContent()`, and an optional `apply` — and the modal walks list → variable fill (required names block confirmation) → overwrite confirmation when the host field holds content. The picker never writes: it hands the rendered body to the host, which owns the merge. A target without `apply` is the copy-only fallback, so un-integrated columns can still adopt the modal cheaply. The modal renders once at the workbench surface; the first consumer is the create column's editor toolbar (category `creation`, filling the draft body).
- **Conflict and lifecycle rules are explicit.** Import is keyed by `id` with three strategies (skip / overwrite at `max(versions)+1` / rename under a fresh id and a suffixed unique name); invalid entries are named and skipped, never fatal to the batch. `putTemplate` rejects duplicate display names and unknown ids (a stale client reloads, never resurrects). Archiving rides a separate `setTemplateStatus` face that writes no snapshot — lifecycle is bookkeeping, not an edit.

## Deviations from the plan text

- The plan's per-column **field manifest** (a list of fillable fields and a structured `{title, body, tags, meta}` render output) shipped as the single-target `TemplatePickTarget`: M1 has exactly one consumer and one target field. The structured output returns with the second consumer (M2), before the shape ossifies around one use.
- The plan's escape syntax was `{\{name}}`; the implementation uses `\{{name}}` (a backslash before the opening braces, the Handlebars convention) — the plan document was corrected to match.
- `putTemplate` rejects creating with a client-supplied id (persona semantics); the import face writes records directly, which is why packs can restore original ids while the form path cannot inject them.
- The typert artifacts regenerated in place carry the parallel publish session's methods too — one shared artifact per package, so the focused regeneration could not scope to one feature's faces.

## Alternatives considered

**A `contentTemplates` Remote package.** Rejected: the face is nine methods on files that share the atomic-write/lock conventions content-outputs already owns; a fifth package would repeat the mount/peer/registration chain for no isolation gain.

**Embedded version arrays (the create `_create.json` pattern).** Rejected for this store: create caps at 30 embedded drafts for one working document, while a template library holds many records each needing durable full-text history — separate snapshot files keep the manifest small and make cascade delete one `rm`.

**Gateway-side rendering.** Rendering the body in the gateway would centralize the substitution but put a text transform behind a wire call for data the browser already holds; the scanner/reconcile/renderer live in one client module the library view and the picker share, and the gateway re-validates every stored record at its own boundary.

## Consequences

Every column can now initialize a form from a versioned, exportable skeleton without touching business data, and the 互动 stopgap has a real target to migrate onto in M2. Costs: the category list exists twice (client mirror of the wire enum, per the bundle purity gate — order pinned by the shared constant); `unused` variable metadata persists until explicitly removed, so abandoned placeholders linger in the editor by design; and each save writes one full snapshot, trading disk for a rollback story that never needs a diff engine. Cross-session note: the publish column landed its faces in the same files during this work; the template face touched only its own module, the shared wiring files (additive entries), and the locale dictionaries (append-only blocks), and the focused typert regeneration re-emitted both features' methods from the current source.
