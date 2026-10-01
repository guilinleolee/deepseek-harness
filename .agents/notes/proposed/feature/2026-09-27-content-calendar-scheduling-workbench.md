# Agent Note: The content calendar becomes a scheduling workbench whose events are the stored schedule items themselves

Status: proposed

English | [中文](2026-09-27-content-calendar-scheduling-workbench.zh.md)

## Problem

The content-studio calendar was a bare month grid over `_schedule.json`, while the calendar column's development prompt (v1) asked for a full scheduling workbench — month/week/list views, drag rescheduling, filters, conflict warnings, CSV export, and bidirectional linkage with the topic bank and the publish view. The v1 data model was unimplementable as written: it called calendar events both a derived view over source data and a stored entity with its own metadata, declared sync "one-way" while also writing backwards, left "delete the calendar event" resurrecting on the next sync, and mixed stored statuses with the render-time overdue state in one enum. An implementer must invent the missing model, and every invention drifts differently.

The concurrent-development constraint raises the stakes: the topic bank already writes schedule items and links them via `scheduleItemId`, the publish view (parallel work) extends `_schedule.json` records with an optional `publishTaskId`, and the outputs metadata file `.dsh-output.json` is off-limits to every column. The calendar had to pick a data model that adds no second truth to that surface.

## Proposal

**A calendar event is the stored `ScheduleItem` — nothing else.** The schedule item is the only stored fact per event; the calendar's sole owned data is the day note, kept in a new `_calendar.json` sidecar at the library root (`{ formatVersion: 0, notes: { [scheduleItemId]: { text, updatedAt } } }`), served through two new `contentSchedule` Remote methods (`getNotes`/`putNote`) with the same file lock, atomic write, unknown-version rejection, and `problems` reporting as the schedule file. An empty note write clears the entry; a note for a deleted item stays stored but inert. Because the event is the stored item, "delete the calendar event" simply deletes it — v1's resurrection problem cannot exist — and the explicit "delete and clear the topic plan date" action covers the one case where the linked topic should forget the date.

**Overdue and conflicts are render-time derivations, never stored.** `calendar.ts` (the existing pure module, still no React and no IO) gains the week grid, the overdue rule (plan day passed, never published), the conflict rule (same platform and day, two `scheduled` items within 120 minutes — a module constant — or three or more `scheduled` items crowding one day, all-day items counting only toward the crowd), list filtering, CSV export (UTF-8 with BOM, CRLF, fixed Chinese columns), and a versioned localStorage view-configuration migration that falls back whole on anything unrecognized. The view/filter configuration is the only localStorage use (the topic bank's ruled precedent); business data never touches it.

**Rescheduling confirms, then writes through the gateways.** Dragging a chip asks a confirm dialog, then `contentSchedule.put` moves the item; when a topic links back via `scheduleItemId`, a second `contentTopics.put` carries the new plan date, and a failure of that second write toasts without rolling back the first. FullCalendar stays out: the plugin's no-new-runtime-dependencies ruling holds, drag-and-drop is native HTML5 DnD like the topic-bank kanban, and the MIT-licensed FullCalendar remains the recorded fallback should hand-rolled views stop carrying their weight. AI scheduling advice ships as a disabled placeholder — the plugin gains no AI calls — and the publish linkage is limited to reading the optional `publishTaskId` for a jump target that lights up when the publish view lands.

## Alternatives considered

**v1's hybrid: derived events plus an overrides record in `<主题>/.dsh-output.json`.** Rejected twice over: `.dsh-output.json` is every column's zero-touch file with a strict metadata gate, and the hybrid needs a synchronization engine plus a tombstone mechanism to keep deletes from resurrecting — all to represent facts the schedule item already stores.

**Adopting FullCalendar for the views.** The month/week/list faces and drag are MIT and battle-tested, but the plugin ruled out new runtime dependencies when the topic bank hand-rolled its kanban DnD; three views over one items array do not yet justify reversing that ruling, and the CSS would fight the `--dsw-alias-*` token system.

**Extending `ScheduleItem` with a note field.** One fewer file, but the item schema is the frozen cross-column contract (topic bank and publish both hold code against it), and a note is calendar-owned annotation, not schedule fact — mixing them makes every column's reads carry the calendar's payload.

## Acceptance criteria

- The left nav carries the 内容日历 entry, and the view renders month, week, and list tabs over the same `_schedule.json` items the topic bank and publish views write.
- A drag between month cells asks for confirmation, then moves the entry and — for a `content`-kind entry — rewrites the linked topic's `planDate` through the topics face; declining moves nothing.
- The overdue mark appears on any unpublished entry whose date has passed, computed at render time and never stored.
- Two entries on one platform within 120 minutes, or three or more scheduled entries on one day, raise the conflict banner and chip outline; widening the window needs no data change.
- The filter stack (type, platform chips, status chips, date range, search, overdue-only) composes, persists per browser with its version key, and falls back whole on an unknown version.
- CSV export lands in the chosen theme's `assets/` as UTF-8 with BOM and CRLF rows, opening in Excel without mojibake.
- Day notes survive a close/reopen of the workbench: an empty write clears, an unknown `_calendar.json` version rejects to a named problem, and the entries never lose their schedule truth.

## Risks

- The drag→topic `planDate` rewrite crosses two files under two faces; the schedule write commits first, so a failed topic write leaves the entry moved with the topic's plan date stale — visible on the next topic-bank open, repaired by the next edit, but not transactional.
- The conflict window is a module constant, not a `Config` field, because the client fiber has no config plumbing; deployments wanting a different window need a code change until the constant moves behind configuration.
- The topic-bank jump from a calendar entry is the degraded, parameterless form — it opens the bank, not the specific topic; wiring the parametrized jump is the topic-bank v2 follow-up this note inherits.
- Notes live beside the schedule in `_calendar.json`; a user editing that file by hand can orphan note entries, which surface as named problems rather than silently reappearing.

## Testing

`calendar.client.spec.ts` pins the week grid, the overdue rule, both conflict rules, every filter dimension, the CSV shape (BOM, CRLF, quoting, note join), and the whole-fallback configuration migration; `content-schedule` gains `calendar-notes.spec.ts` (absent-file read, unknown-version and broken-shape rejection, per-entry problems, upsert/clear/timestamp behavior) beside the existing store tests, and the client package's suite — including the apply-assembly and dictionary-pinning tests — passes in full.
