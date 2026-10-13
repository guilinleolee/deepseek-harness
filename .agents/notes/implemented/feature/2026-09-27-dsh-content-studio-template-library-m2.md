# Agent Note: Template library M2 — the picker's structured draft, the topic bank as the second consumer, and a bundled starter pack

Status: implemented

English | [中文](2026-09-27-dsh-content-studio-template-library-m2.zh.md)

## Problem

M1 shipped the global template library with a single consumer and a single-target picker contract, deliberately leaving three M2 items open: the v2 plan's structured render output (`{title, body, tags}`), a second column to prove the contract generalizes, and the freemium distribution vehicle (a shareable pack). The 统一评估 for the create workbench's `_templates.json` and the 互动 plan's localStorage reply templates was also still open.

## Decision

- **The structured output is picker-computed, not host-computed.** `pickerConfirm` now hands every host a `TemplatePickDraft { title, body, tags, values, template }`: `title` is the filled `{{title}}` variable with a fallback to the template's own name, `tags` carries the template's tag names resolved against the loaded taxonomy, and the raw `values` remain for multi-field hosts. Computing this in the picker (once) means every future consumer shares one title/tags convention instead of re-deriving it — the modal states the rule in its fill step.
- **The topic bank is the second consumer, via prefill — never a direct put.** 头部与空态各一个「从模板新建」入口 opens the picker for category `topic`; the structured draft fills the create form (title, description, tags), and the form stays the user-editable draft state — the 渲染不落盘 iron rule survives the second integration. Two supporting changes: `submitCreate` now carries the optional fields (empty values produce exactly the old shape, so the quick-add path is unchanged byte-for-byte), and the create form renders the extra fields only when they hold content, keeping the one-field quick-add untouched.
- **A real semantic fix fell out of the second consumer: required now means body-active.** `missingRequired` blocked a pick whenever any declared required variable was unfilled — including variables whose placeholder no longer appears in the body. A body-truth library whose picker enforces metadata-truth requirements is inconsistent; the check now filters to placeholders the body actually uses (`missingRequired(body, variables, values)`), and the modal's disabled-confirm shares the same call.
- **The starter pack is data, not a feature branch.** `starter-pack.ts` bundles eight skeletons across six categories with stable readable ids (`starter-*`); the library header and the empty state trigger `importStarterPack()`, which rides the normal import face with the `skip` strategy — re-imports are idempotent, and paid packs later reuse the exact same `dsh-template-pack` format and face. A pack spec pins envelope shape, id stability, category membership, tag references, and — using the library's own scanner — that every body placeholder has declared metadata.
- **统一评估结论：不统一。** The create workbench's `_templates.json` keeps its placeholder whitelist (`assertTemplateBody`, double-validated at save and generation, consumed by the gateway's framed-prompt pipeline) — unifying would either break that wire validation or force free-form variables into the pipeline. The 互动 plan's localStorage stopgap is recommended for retirement before that column ships: its templates should come from the library (category `interaction`) through the same picker, at zero migration cost. Both conclusions are recorded in the plan document (§5).

## Deviations from the plan text

- The plan's per-column **field manifest** (a declared list of fillable fields) resolved to the structured draft plus the `values`-by-name convention instead: with two consumers, the fields a host fills are exactly `title`/`body`/`tags` — a manifest registry would re-state what the draft type already says. A third consumer needing a different shape reopens this.
- **日历 stays un-integrated, by ruling**: schedule entries are time-boxing tuples (title/time/platform) with no body field for a skeleton to fill; revisit if the planned calendar v2 (events as derived views) lands a note-like surface.

## Alternatives considered

**Host-computed title/tags.** Letting each host derive the title fallback and resolve tag names would put the convention in N places instead of one; the first divergence (a host treating an empty title differently) is exactly the drift the structured draft exists to prevent.

**Direct topic creation on apply.** Skipping the form and calling `topics.put` with the rendered draft would save a click but violate the render-never-writes rule, and it would strip the user's chance to edit the AI-shaped skeleton before it becomes a record; the prefilled form is the draft state the rule requires.

**Migrating `_templates.json` into the library.** Moving the create workbench's generation templates under the library's free-variable schema would delete the whitelist the gateway validates at both save and generation time; keeping two stores costs one extra panel, while a broken generation contract costs the create column's prompt quality.

## Consequences

Two columns initialize real drafts from versioned templates, an empty library is one click from useful, and the pack format has a shipped reference implementation for the freemium channel. Costs: the starter pack ships inside the client bundle (~data, ids frozen once published — a renamed starter id re-imports as a duplicate); the title/tags convention lives in the picker for every future host; and required-variable semantics changed (body-active only), which a template relying on required-but-unused placeholders to block saves would notice — none exists in the wild. Cross-session note: the publish and review columns landed in the same files during this work; the M2 changes touch only the template module, additive wiring in the shared files, one append-only locale block per dictionary, and the topic bank's create path (back-compatible).
