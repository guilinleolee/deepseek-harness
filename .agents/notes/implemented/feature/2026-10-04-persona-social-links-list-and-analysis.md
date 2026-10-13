# Agent Note: The persona wizard's social links become a fixed per-platform list, and the last step gains one-click social-profile analysis

Status: implemented

English | [中文](2026-10-04-persona-social-links-list-and-analysis.zh.md)

## Problem

Wizard step 2 rendered each social link as a dropdown-plus-inputs row: the platform `<select>` opened over the form (the pain point in field reports), every row demanded an 账号简介 nobody had for a homepage URL, and the row machinery (add / remove / pick a platform) existed only to express "platform → URL", a mapping fixed by the platform union. Meanwhile the last step had no way to use those links: the user filled their social homepages and the analysis never read them.

## Decision

- **Step 2 is a fixed list: one labeled URL row per platform, no dropdown, no bio, no add/remove.** The rows render from the frozen `PERSONA_PLATFORMS` table with the shared Chinese labels, so the list cannot drift from the picker vocabulary. `setLinkUrl(platform, url)` upserts the underlying `PersonaLink` rows — a row exists only while its URL is non-empty, one row per platform — and `inputFromForm` drops URL-less links, so blank rows are never saved. The `bio` field stays on the wire type (stored entries keep theirs; the report facts still render it) but no new UI writes it. The wizard draft buffer keeps version 1: the form shape is unchanged and old drafts load.
- **A new `social` AI operation analyzes the homepages at the last step.** The step-4 footer gains 「分析社媒主页」 next to the generic fill button — explicit, matching the plugin's no-implicit-AI rule, and idempotent to re-run. The gateway fetches each link (the same fetcher as the site face: declared UA, 30 s deadline, 2 MiB cap, http(s) only), sections each readable page under its platform label with a per-section 2 500-character cap so every link gets a fair share of the model input, and skips login-walled or empty pages — one unreachable homepage never kills the batch; a batch with no readable section rejects. One extraction call (`persona-social@1`, same JSON contract as the site face) runs over the joined sections; the prompt says the material is fragmentary profile text and demands conservative, grounded values. The fetched sections are ephemeral: unlike the site face, nothing is persisted back into the form — the links themselves are already stored, and only adopted fields reach the entry.

## Alternatives considered

**Auto-running the analysis on entering step 4.** Rejected: it would spend a model call plus N page fetches on every navigation into the step and contradict the explicit-trigger convention the audit pinned ("AI 显式触发不进保存主路径"). The button lives on the last step, which is where the requirement aimed.

**Rendering only the platforms selected in step 1.** Rejected: a user can hold a social account on a platform they do not operate; the fixed list keeps that expressible and needs no add affordance. The row-per-platform list is also the direct answer to the dropdown complaint.

**Persisting fetched social text like the site face does.** Rejected: up to eight profile pages of ephemeral text would bloat the entry; the site face persists because its text feeds the report facts, while social insight arrives through adopted fields.

## Consequences

Costs: the fixed list is eight rows tall where the old form was one row per added link — vertical space traded for zero hidden state; social platforms' anti-scraping means some fetches return login shells, which the skip logic absorbs silently (the user sees fewer sections, not an error). A stored entry with two links on one platform (legacy data predating the uniqueness rule) shows only the first and keeps both until that platform's row is edited. Verification: 61 tests across the two packages (per-platform upsert, blank-row filtering, the `social` operation with skip/reject cases, step-2 list wiring, the step-4 button flow), both packages typecheck clean, oxlint clean on touched files, typert artifacts regenerated for the new wire member.
