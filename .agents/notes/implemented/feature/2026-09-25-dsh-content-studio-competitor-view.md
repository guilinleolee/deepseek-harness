# Agent Note: The competitors view keeps benchmark-account state on disk beside the works, not in the browser

Status: implemented

English | [中文](2026-09-25-dsh-content-studio-competitor-view.zh.md)

## Problem

The Content Studio workbench had 对标 (a copy-prompt teardown card) but no actual benchmark-account workflow: no rival-account registry, no works library, no AI teardown, no account panorama or two-account face-off. The competitor plan (V2, `D:\dsh-content-studio\docs\competitor-dev-prompt-v2.md`) asked for a second information column with three hard edges: domestic platforms have no RSS and aggressive anti-crawling, so collection must not be the load-bearing path; browser-side scheduling dies with the tab; and work-level state (dedup keys, metric snapshots, analysis results, collection cursors) has no home in the on-disk conventions — `OutputMetadata` is one topic-level object and schema-frozen.

## Decision

A new `competitors` view rides the existing workbench overlay nav (registered in the `NAV_ITEMS` array, no new slot). Three packages, the same faces the gather view already established:

- **content-outputs grows a competitor write face** (`readCompetitorManifest` / `writeCompetitorManifest` / `readAsset` / `analyzeCompetitorWork` / `generateCompetitorReport`), reusing the gather face's path guards, atomic-locked commit, and the extracted `streamLlmText` one-shot helper with its rate-limit-only retry. The manifest is `<theme>/assets/_competitors.json` (`formatVersion 0`): `syncedAt` per account, `works[]` (identity `platform + accountId + platformWorkId`, append-only metric snapshots, persisted analysis as `none|done|failed` — `pending|running` stay view-local), and `reports[]`. The store never trims: works carry user markers.
- **Phase-one collection is manual import** — a form writes the body through the existing `writeAsset` and upserts the manifest; title-key fallback dedup catches re-imports that learned the real platform id later. MCP scraping stays a reserved interface (five method signatures in the plan), implemented by nobody this phase.
- **Heat is account-relative** (`heatByWork`): interaction score `likes + 2·comments + 3·shares` (+views/100 reach), ranked against the account's own last-30 distribution with P90/P50 thresholds; fewer than four works read normal. Cross-platform absolute values are never compared.
- **AI stays explicit and degradable**: teardown takes title + body + stats plus optionally pasted hot comments (`commentInsight: "unavailable"` is a legal persisted value); reports consume per-account digests capped at 1000 characters — raw work text never enters a report prompt. Queue concurrency stays 1.
- **收录为选题 lands as an `idea-<id>.md` asset** with a structured YAML header (`kind: topic-idea`, source account, platform, source work id) so the topic bank or gather view can index it later; the 【选题库】 column does not exist yet, so the button records `gatheredRef` and disables.

`_competitors.json` joins `_gather.json` in the scanner's `_`-prefix blind spot: the library never renders it, `assetCount` never counts it.

## Alternatives considered

**Work-level state in `.dsh-output.json`, as the plan's storage chapter literally says.** Rejected against the frozen reality: `OutputMetadata` is a single topic-level object (`title/kind/platform/status/tags/summary`) and the gather prompt's 禁用清单 forbids widening it. The `_`-prefixed sidecar beside the material is the established convention for per-entry state.

**`assets/works|analysis|reports/` subdirectories, as the plan draws them.** The gateway's asset guard allows one plain file name inside `assets/`; prefixed flat names (`cw-*`, `ca-*`, `cr-*`, `idea-*`) keep the single guard and the gather convention intact.

**Browser-side scheduled collection (the plan's phase-one 模块 6).** A timer that dies with the tab is a false promise; the view does catch-up-on-open (compare `syncedAt` against the account interval, banner + one-tap mark-collected) and real scheduling moves to the host side in phase two.

**AI teardown concurrency 2, as the plan allows.** The gather face already standardizes one model call at a time with 429-first retry policy; upstream quota is the real constraint, and 1 ≤ 2.

## Consequences

Rival analysis works with zero collection infrastructure — paste a work, get a structured teardown, a panorama, and a face-off — and every collected artifact survives browser changes because the manifest lives beside the material. Costs: the account registry still lives in localStorage (JSON export/import shipped as the backup; server-side storage remains phase two); report rendering is pre-wrap text, not styled markdown; and the `_competitors.json` reader must not write back while `problems` is non-empty, since dropped entries would be lost. Cross-session note: while this view landed, a parallel session was mid-flight on the same package's `create/` write face; both faces extend `ContentOutputsGateway` independently and share only the extracted AI helper.
