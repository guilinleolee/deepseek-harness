# Agent Note: The topic bank turns the retired 选题规划 slice into a store-driven column — table and kanban over `_topics.json` with the gather join wired

Status: implemented

English | [中文](2026-09-25-dsh-content-topic-bank.zh.md)

## Problem

The workbench's 选题 nav entry was a static two-card prompt page, and no durable surface existed for topics: ideas collected from gathers and rivals had nowhere to be scored, scheduled, or pushed into creation. The storage seam itself already existed — the `contentTopics` Remote over the library's `_topics.json` (store 100% covered, `formatVersion 0` gate, bad records named in `problems`) — but nothing consumed it. What was missing was the whole frontend: two views, the plugin's first detail side panel, create/edit/delete, batch actions, schedule linkage, Markdown export, the nav-id swap with its capability-card relocation, a parameterized cross-view handoff, and the reserved gather-side `addToTopicBank` contract that had answered only a pending toast.

## Decision

The view (`TopicBankView`) consumes the gateway through the same injected, envelope-unwrapped face every other view uses, with view-local component state for the snapshot — `loading` / `error` / `empty` as first-class states copying `ContentLibrary`, `problems` rendered as a warning bar that names dropped records. No new controller: the bank refetches on view mount like the library and calendar do. View and filter configuration persists to `dsh-content-studio.topicBank.config` and reloads through a versioned migration — one normalize function either fully recognizes the stored object or the defaults come back whole, so no truncated or future-versioned state ever reaches the components.

Both faces render through the reusable `SplitDetail` layout the gather phase established. The table carries the spec'd columns; the kanban renders five columns from the single-source `TOPIC_STATUSES` config and moves cards with native HTML5 drag events — no dependency added. A move is an optimistic status flip followed by the Remote `put`; a failed write restores the prior snapshot object and toasts, so the UI never lies about durability. All bank logic — filtering (source, status, score range, tag, keyword, week/month plan window), kanban grouping, config migration, and the Markdown export — lives in the React-free `topic-bank.ts` beside `calendar.ts` and `create.ts`.

The export schema is strict and self-inverse: `planDate` stays an unquoted `YYYY-MM-DD`, scores stay bare numbers, every other scalar is double-quoted with `\` and `"` escaped, and tags are a quoted inline array. `parseTopicsMarkdown` accepts only this schema's own output, and round-trip tests pin the losslessness. Exports write through contentOutputs' path-guarded `writeAsset` into the chosen theme's `assets/` — no second write face for the plugin.

Schedule linkage is deliberately one-way. Setting or changing a topic's `planDate` puts a `content` schedule item whose id the client generates (the gather id scheme — the calendar store accepts any non-empty id, so supplying one lets the topic bank remember `scheduleItemId` without scanning the returned snapshot for a title/date match). The calendar stays authoritative for its own four statuses; no status sync runs in either direction. Deleting a topic offers a confirm box whose cascade checkbox (default on) removes the linked calendar entry first; a failed cascade aborts the delete.

Cross-view handoff follows the established `pickMaterial` pattern: `pickTopic`/`pickedTopic`/`clearPickedTopic` joined the shared studio controller, and CreateView folds the topic's title, pitch, and description into its paste entry once, then clears. The create view already owns a prefill face, so the spec's clipboard-degradation fallback never becomes code. Navigation swaps `topics` for `topicBank`; the two capability cards survive as the empty-state guide, rendered through `CapabilityPage`, which keeps the catalog-id-equals-locale-stem convention and its pinning test intact. The stale `nav.topics` / `topics.title` dictionary keys are removed, and a locale-pin test enumerates every new `topicBank.*` / `topic.*` stem in both dictionaries.

The gather contract closes the loop: ContentStudio now passes the reserved `addToTopicBank` handler into `GatherView`, which maps the material through `gatherMaterialToTopicInput` — the material's stable id as `source.refId`, its link as `source.url`, and a create-time snapshot carrying `gatheredAt` — into an `idea`-status topic. The pending toast remains as the no-handler fallback, and feedback for the wired path rides the gather view's own notice channel (three new notice keys). The 【AI 优化选题】 button renders disabled with its pending-version title, and manual scoring stamps `{ source: "manual", factors: null }`; AI scoring stays a P2 field shape with no implementation.

## Alternatives considered

**A drag-and-drop library for the kanban.** Rejected by the spec's zero-dependency rule: native `dragstart`/`dragover`/`drop` cover column-to-column moves, and the optimistic put covers everything a library would add for this geometry.

**Scanning the schedule `put` snapshot for the created id.** Rejected: matching on title plus date can mis-resolve after edits. A client-supplied id is deterministic and costs one cast at the branded boundary.

**Skipping the export parser.** The parser exists to keep the emitter honest — the strict schema is enforced by a round-trip test, not by prose. It is not a foreign-file importer and rejects anything else.

**A controller for the topic bank.** Rejected: unlike the gather scheduler, the bank has no timer, no cross-slot lifetime, and no background state; view-local state plus refetch matches the library/calendar surfaces and keeps one pattern per complexity level.

## Consequences

Three nav rows now lead with real data surfaces instead of prompt cards, and a gather material reaches creation through two paths — pushed directly, or normalized into a scored, scheduled topic. The score column is honest about its limits: manual-only values read as `source: "manual"`, unscored rows say 未评, and the AI entry says when it will open. The package's jsdom lane still carries pre-existing GUI-coverage debt elsewhere (AccountSelect, CompetitorsView, and friends predate the per-file gate on this tree); within this change, the pure module is branch-exercised, the view runs through jsdom render tests including the drag rollback, and the web browser e2e lane gains no scenario — consistent with the gather precedent, it needs a full web build.
