# Agent Note: The publish view freezes the phase-2 MCP package instead of faking an upload

Status: implemented

English | [中文](2026-09-27-dsh-content-studio-publish.zh.md)

## Problem

The Content Studio had five shipped views (gather, benchmark accounts, topic bank, persona, create) and no distribution story: a finalized manuscript sat in the theme root with nothing carrying it to the platforms it was written for. The request prompt (v1) promised real multi-platform publishing, but the real upload channel is a phase-2 MCP service that does not exist yet, scheduling has no background process to fire it, and the v1 text stored account cards in localStorage — colliding with the studio's own cross-device-state lesson and freezing no data contract up front. The rewrite (`D:\dsh-content-studio\docs\publish-dev-prompt-v2.md`) reframed the column around one honest question: what does "publish" mean when nothing actually uploads?

## Decision

- **Honest phase semantics.** 执行发布 builds the frozen `PublishPackage` (every leg's derived draft must already exist, or the build rejects) and moves the task to the terminal `recorded` status, with UI copy that says the channel is not connected. Nothing pretends an upload happened. The phase-2 execution states (`executing` `partialSuccess` `success` `failed`) are deliberately absent from the status unions — closed unions with the four phase-1 states only, so a later phase extends them without re-auditing consumers.
- **Theme-side sidecar, global index, no `.dsh-output.json` touch.** Tasks live in `assets/_publish.json` (`formatVersion 0`, unknown versions refuse to load) like gather/create/persona sidecars; the global `_publish-index.json` is a projection for the cross-theme history list, refreshed under the same writer lock as the manifest write, rebuildable by scan when corrupt. Derived drafts land in `assets/publish/<taskId>/<platformId>.md` with path guards on both ids. The metadata file is never readable through the new `readPublishSource` face.
- **Account cards on disk, not localStorage.** `_publish-profiles.json` holds alias, enabled, and adaptation overrides — no credentials by design, so nothing blocks persistence; the v1 localStorage plan was simply the studio's own lesson violated. Platform rules are a data-driven registry (`publish/model.ts` `PLATFORM_PROFILES`); adding a platform is appending a row, which is what makes "support overseas platforms later" a true statement.
- **Append-only attempts are the idempotency basis.** Every adapt, edit, and record appends an `attempts` entry; a retry adds a new entry and never rewrites the log. A failed adaptation touches only its own leg (failure isolation), the queue is one call at a time with the shared rate-limit-only retry, and adaptation charges the create quota gate's generation budget — the freemium seam stays in one place.

## Deviations from the plan text

- The plan wrote publish-task metadata into `.dsh-output.json`; the sidecar is the shipped choice, matching the frozen-schema ruling every earlier view made (and the parse-reject gate that file enforces).
- The plan's 回流 target status "已发布上线" does not exist in the topic bank's five-state union; the reflow writes `done` through the existing `contentTopics.put`, reusing the create view's idempotent path.
- Scheduled tasks this phase write the calendar entry (optional `publishTaskId` field added to `ScheduleItemInput`) and surface due tasks when the view opens; nothing auto-fires — the plan's own anti-fake-scheduling ruling, same as the benchmark view took.
- The banned-word pre-check rides the create view's local `banned-words.ts` lexicon rather than a new check; the plan's "hide if the upstream face is unreachable" degradation applies to the whole panel.

## Alternatives considered

**Publish-task metadata inside `.dsh-output.json`.** Rejected: that file's schema rejects unknown versions outright and is the work-level projection the library view reads; embedding a mutable task list there would couple distribution churn to work metadata and fight the parse-reject gate every other view avoids with a sidecar.

**A browser-side scheduler that auto-fires due tasks.** Rejected: with no upload channel, an auto-fire could only mark tasks published falsely, and a page-scoped timer is a scheduler that dies when the tab closes. Due tasks surface on view open and the user executes them — the same honest-ruling the benchmark view took for monitoring.

**Storing the MCP package at record time.** Rejected in favor of rebuilding it on demand: the package is a pure projection of the derived drafts and task facts, so a stored copy would drift the moment a draft is re-adapted; `buildPublishPackage` reads fresh and fails loud on any missing leg.

## Consequences

The distribution loop is now executable end to end without any upload channel: manuscript pool → task → per-platform adaptation → hand edit → package build → `recorded` → topic reflow, all under 100% offline capability except the explicit AI adaptations. Costs: the platform registry exists only client-side this phase, so the AI prompt's style hints ride the request (a future server-side consumer re-freezes them into the wire type); the global index is a cache and its rebuild-on-corruption path is a scan of every theme; and deletion keeps derived drafts on disk by contract, so purging them is a separate manual step. The shared-file lesson applied again mid-flight: the create view grew one optional `onSendToPublish` prop, the studio controller one more handoff pair, and the nav one entry — the smallest mergeable surface available while a parallel session worked the same package.
