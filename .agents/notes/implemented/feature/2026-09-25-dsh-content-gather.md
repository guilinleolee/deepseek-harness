# Agent Note: The gather write face collects into `assets/_gather.json` and the browser owns nothing durable but sources and tasks

Status: implemented

English | [中文](2026-09-25-dsh-content-gather.zh.md)

## Problem

The Content Studio workbench had no information-collection surface: topic intel lived in the model's skill answers, and nothing persisted it. The gather view needs a shape no existing seam offers — RSS/Atom fetching that cannot run in the browser (cross-origin feeds are CORS-blocked, so every mainstream reader fetches server-side), per-material body snapshots and AI enrichment written next to the works library, and source/task configuration that must survive neither a cleared browser nor a vanished workbench opening by accident.

## Decision

`packages/creation/content-outputs` extends its Remote with the gather write face — the single authorized write path for the feature: `fetchFeed` (conditional-request cursors `ETag`/`Last-Modified` in, drafts plus next cursors out; a 304 answers `notModified` with zero items), `writeAsset`/`readAsset` (per-file, path-guarded to `outputs/<theme>/assets/`; `*.html` is sanitized through the sanitize-html allowlist before it touches disk), `readGatherManifest`/`writeGatherManifest` (`assets/_gather.json`, `formatVersion 0`), `moveAsset`, `deleteAsset`, and `processMaterial` (the AI face riding the shared `llm` service: explicit per call, p-queue concurrency 1, p-retry on rate limits only with provider `Retry-After` honored first). The manifest write is quota-trimmed at the storage layer — per source, newest 50 `unread`/`read` entries; `favorite`/`picked` and their snapshots are never removed — and dropped snapshots are deleted only after the trimmed manifest is durable, so a crash can leave an untracked file but never a tracked-but-missing one. Atomicity is the schedule gateway's pattern again: `withFileLock` + `writeFileAtomic` with Windows rename-pin retry (EPERM/EACCES/EBUSY, 100 ms doubling, five tries), plus an orphan-`.tmp` sweep at gateway start.

Three contract points come from the parallel topic-bank prompt §7 and are built in now: every material id is stable and durable (the feed guid, else the SHA-1 of the normalized link — kept beside the raw guid so the strategy can be recomputed), the material list/detail layout is the reusable `SplitDetail` component (the topic bank's side panel will render through the same seam), and the 「加入选题库」 entry exists on every card and the detail pane under the reserved `addToTopicBank(materialId)` contract name, answering with the pending toast until the topic bank plugs its handler in.

The browser half (`packages/client/ui-content-studio/src/client/gather/`) owns everything else and nothing durable beyond it: sources, tasks, and task logs live under the `content-studio.gather.` prefix only, degrade to in-memory when writes fail (the view says so), and disappear on a browser-data wipe while the on-disk materials survive. The controller is one observable state object whose snapshot is rebuilt per mutation (a fresh object per `getSnapshot` would make `useSyncExternalStore` re-render forever — caught by the render test). Collection runs only while the workbench is open: a master tick every 30 s, `visibilitychange` pauses and resumes it, and reopening after a gap runs overdue interval tasks once with their `since` cursor — compensation, not background polling. Source-level failures start the 1 h → 2 h → 4 h backoff (capped 24 h) that gates scheduled runs; a manual trigger is the user's explicit intent and overrides the gate. Pushing a material to the create view marks it `picked` in the manifest and hands the create view an id-titled reference (`PickedMaterial` on the shared studio controller — the payload is the id, title, and URL, never the body).

## Alternatives considered

**Fetching feeds in the browser.** Rejected by the CORS reality: virtually no feed carries `Access-Control-Allow-Origin`, so a browser-side fetch would fail on most real sources. Miniflux, FreshRSS, and Folo all fetch server-side; the gateway consumes that role with no new network code of its own.

**A hand-rolled sanitizer.** Rejected: deleting `script`/`iframe` cannot cover `javascript:`/`data:` URIs, SVG/MathML mutation vectors, or DOM clobbering. The allowlist (sanitize-html) decides what survives at the gateway; DOMPurify (`USE_PROFILES: {html: true}`, `KEEP_CONTENT: false`) re-runs at render as the second layer.

**Storing source/task configuration on disk.** Rejected: the outputs library is the agent's write surface, and mixing browser-owned configuration into it would couple the agent's file space to transient UI state. Clearing browser data loses only sources and tasks — the materials, which cost network I/O, stay complete.

**Cross-theme material rebinding through `moveAsset(theme, from, to)`.** The write face's move is generalized to explicit `fromTheme`/`toTheme` (same-theme rename remains the special case), because the browser has no other authorized way to relocate a stored snapshot; the view itself currently rebinds via the authorized `readAsset` → `writeAsset` → `deleteAsset` chain, so the generalized move stands ready for direct use.

## Consequences

The gather view is the first plugin surface that writes into the works library's project directories: a theme with only gathered materials projects as a metadata-less library card (`hasMetadata: false`), which the library view already renders with a repair hint. The scheduler is honest about its limits — closing the workbench stops collection, and the copy says so. The web browser e2e lane has no gather scenario yet (the lane needs a full web build; the jsdom render test covers the view's selection, layout, and topic-bank contract in CI today), and the render-side CSP belongs to the host page, so the plugin ships the DOMPurify layer and leaves the page-level policy to the shell.
