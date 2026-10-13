# Agent Note: The review view imports platform metric exports, judges them against account baselines, and reflows the conclusions into the topic bank

Status: implemented

English | [中文](2026-09-27-dsh-content-studio-review.zh.md)

## Problem

The 【复盘】 view (v2 plan, `D:\dsh-content-studio\docs\review-dev-prompt-v2.md`) closed the studio's operation loop: take the works the publish view already recorded, import each platform's creator-center metric exports, render a comparable dashboard, diagnose individual works with AI, generate a structured period report, and push the conclusions back into the topic bank. Three facts pinned the design before any code: the `.dsh-output.json` zero-contact ruling (six columns share its frozen schema), the interaction view's absence (comment analysis is a deferred dependency, not a stub to fake), and the metric-semantic trap that platform exports disagree on definitions — impressions cannot be summed across platforms and a missing metric must never read as zero.

## Decision

- **Storage is a theme-side sidecar plus a hidden global index.** `outputs/<theme>/assets/_review.json` (`formatVersion 0`, reject-unknown) carries the baselines, snapshots, and tasks; `outputs/_review-index.json` mirrors one row per task for the cross-theme history list and refreshes in the same commit sequence as the manifest write, with a scan-rebuild fallback. Deletes remove the task and its report file but keep every snapshot and binding — other tasks and the dashboard reuse them. All paths enter through the plain-name guards the gather face established.
- **Import is a two-step parse-then-commit with nothing stored in between.** `parseReviewImport` maps one RFC 4180 CSV through per-platform header-alias tables (bracketed qualifier suffixes like `标题（主）` normalize away), scales `万`/`w` suffixes, normalizes dates to UTC, and returns parsed rows plus numbered rejections plus the unmatched columns; the user confirms, and `commitReviewImport` lands rows as snapshots. The snapshot identity is `platform + platformWorkId + UTC day`: re-importing a work on the same day overwrites that day's snapshot (idempotent) while every older day survives, because long-tail detection is only as good as the snapshot history. Unknown columns are never silently dropped — they surface as checkboxes and the choice is recorded.
- **Only bound rows analyze.** A snapshot enters the pool only when its `contentId` is non-null; binding rides a three-method lineage (`url` → `title` → `manual`, mirroring the xhs-trail `ContentSource` shape) and currently lands through the manual face — the automatic matcher needs publish-task metadata the view does not read yet, so it is an explicit follow-up rather than a half-wired guess. Verdicts come from the persisted account baselines: viral at twice the baseline engagement rate, weak below half, and long-tail only for works published ≥30 days whose last-7-day interaction pace holds at least a fifth of its lifetime pace across ≥2 snapshots.
- **AI stays explicit, queued, and honest about failure.** Both calls (`analyzeReviewWork`, `generateReviewReport`) ride the shared `streamLlmText` helper with the rate-limit-only retry; the report prompt receives aggregate summaries plus top/bottom digests with 500-char excerpts — never full bodies — under a frozen six-section template (the audience section is pinned to a placeholder naming the missing interaction column). A failed AI call still lands a report: the client renders the data-only fallback from the aggregates, stores it, and marks the task `degraded`; a failed disk write leaves the text in the editor and the task `failed`. Report saves always create a new file, so the generated original is never overwritten.
- **The reflow is a plain topic-bank write.** One suggestion becomes one `TopicItemInput` with `source.type: "manual"`, tag `复盘`, riding the existing `contentTopics.put`; the interaction view's future insights feed is a read-side integration that stays deferred until that view ships.

## Deviations from the plan text

- The plan's M1 said "CSV/Excel"; this phase ships the CSV parser only. Excel support needs a new spreadsheet dependency, and the plan's own acceptance scenarios are CSV-based — the import UI copy states the CSV scope honestly. The header-alias tables carry the four platforms' known export column names as a documented baseline (the plan itself defers exact headers to real-export verification).
- The plan placed Chart.js under the UI conventions; the dashboard renders per-platform tables, rank lists, and verdict chips in the studio's existing card idiom instead. No studio column ships a chart library today, and pulling one into the bundle for one view was the worse trade — revisit only if the trend charts genuinely need axes.
- The plan's binding chapter promised automatic `url`→`title` matching at import time; the importer parses platform rows without work URLs in most export shapes, so the auto matcher needs the publish tasks' external links and is deferred as stated above. The `matchMethod` union and the per-snapshot lineage field are in place, so the matcher lands without a schema change.
- The plan's MCP chapter froze `fetchPlatformMetrics`; the interface lives in the plan and the gateway reserves no method — there is no dead RPC surface to maintain while no provider exists.

## Alternatives considered

**Writing task metadata into `.dsh-output.json`.** Rejected outright: the six-column ruling froze that file's schema against unknown writers, and a review task is cross-cutting bookkeeping, not output metadata. The sidecar pattern the publish face froze is strictly the same shape.

**Aggregating server-side for the report call.** The competitor face already settled the pattern: the client computes the aggregates (same pure functions the dashboard renders), and the AI consumes a digest. Server-side aggregation would duplicate the metric semantics in a second language layer for no trust gain — the gateway already validates every stored snapshot's shape.

**A new `contentReview` Remote package.** Rejected for the same reason the persona note rejected `contentPersonas`: twelve methods over files the other write faces already share locks and atomic-write conventions with; content-outputs is the single authorized write path for the studio.

## Consequences

The loop closes offline: import, dashboard, baselines, bindings, and the data-only report all work without an LLM, and every stored artifact survives browser changes because the manifest lives on disk. Costs: the enum tables and the six-section list exist twice (client `review/model.ts`, gateway `review/` modules) with the parity pinned by test, so a new platform must land in both; the automatic binder's absence leaves unbound works as a manual paste-the-id step until the follow-up; and CSV-only import means Excel users must re-export or save-as first. Cross-session note: the publish, template-library, and notes faces evolved in parallel inside the same packages; the review face touched only the shared assembly points (`ContentStudio.tsx`, client `index.ts`, `locales.ts`) additively and shares the topics face for its reflow.
