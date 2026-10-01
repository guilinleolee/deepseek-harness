# Agent Note: Three structural breakpoints closed — the benchmark view collects into the topic bank, the publish handoff carries the creation topic, and the benchmark-account view gains its nav entry

Status: implemented

English | [中文](2026-09-28-dsh-content-studio-loop-closure.zh.md)

## Problem

The 2026-09-27 requirements audit left four structural breakpoints in the studio's cross-column loop, three of them code-side: the benchmark view's 收录为选题 still wrote only an `idea-<id>.md` asset file (the plan's own placeholder target, never switched to the now-existing topic bank), the create→publish handoff hardcoded `topicId: null` so the publish view's reflow button was unreachable dead code, and the fully-built `CompetitorsView` had no `NAV_ITEMS` entry — an orphan view behind a rendering branch. This change closes those three; the fourth (the workbench's narrow data sources) stays with the dashboard work.

## Decision

- **The benchmark switch is the plan's own "only the write target changes."** `competitorWorkToTopicInput` (pure, in `competitors.ts`) builds a `benchmark`-source `TopicItemInput`: the work id as `refId`, the work link when present, and a create-time snapshot carrying the title plus the first differentiated topic suggestion. `addIdea` now checks the bank for the same `refId` before putting — one benchmark work yields one topic, ever — then still writes the idea file and the `collectedIdeaRef` marker, so the existing disable/retry UX survives and the audit trail remains. A half-done round (topic landed, file write failed) converges: the retry finds the topic, skips the put, and backfills only the marker. The shared `topics` face rides the injected competitor face rather than a second gateway handle.
- **The publish handoff carries the creation topic end to end.** `PickedManuscript` gains an optional `topicId`; the create view sends `manifest.topicRef?.topicId` when the editor has a linked topic; the publish form stores it on `NewTaskForm` and passes it to `createTask`. Manual entries (manuscript-card starts) carry `null` — a task only reflows the topic it was actually born from. With a non-null id, the previously dead 回流 button becomes reachable and flips the topic to `done` through the existing idempotent write.
- **The nav entry is the one-liner it promised to be.** `competitors` sits right after the benchmark capability slice in `NAV_ITEMS`; the locale keys were already pinned and waiting.

## Deviations from the plan text

None new. The benchmark switch executes the competitor plan v2's standing instruction ("选题库交付后仅切换写入目标"), the handoff topicId is the audit's own breakpoint fix, and the dual write (topic + idea file) keeps the v2 marker semantics instead of dropping them.

## Alternatives considered

**Dropping the idea file once the bank exists.** Rejected: the file is the per-work collected marker the retry-disable keys on and the theme-local audit copy; the topic snapshot carries the same content for the bank side, so the file costs nothing and keeps both projections honest.

**Reflowing to a distinct 已发布 topic status.** Out of scope here: `TopicStatus` has no published member, and the audit explicitly deferred that contract decision — the reflow continues to land on `done` until the status union is revisited.

## Consequences

The cross-column loop closes for real: benchmark → topic bank, topic → create → publish → topic reflow are all live paths now. Costs: the publish form trusts the handoff's topicId (a stale linked topic id surfaces only when the reflow write rejects), and `addIdea` now reads before it writes — one extra `topics.list()` per collection, negligible at workbench scale. Verification: 581/581 across the three packages (three new builder cases), client typecheck clean, bundle rebuilt.
