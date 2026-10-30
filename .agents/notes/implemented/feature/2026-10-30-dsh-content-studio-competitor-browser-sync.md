# Agent Note: The competitors view imports browser-synced collections instead of growing an in-client crawler

Status: implemented

English | [中文](2026-10-30-dsh-content-studio-competitor-browser-sync.zh.md)

## Problem

The competitors view's phase-one collection path was manual import one work at a time, while the reserved MCP collection interface stayed unimplemented and TikHub endpoints reject free credit — real benchmark accounts (a 9万-follower XHS account was the reference case) could not enter the works library without heavy copying. Meanwhile a logged-in browser session sees everything a human sees: profile bio, follower counts, the works wall with like counts, note bodies, and comment sections. The risk was building collection into the client, where an in-page timer dies with the tab (the exact trap the phase-one design note already rejected) and anti-crawler responses poison the manifest.

## Decision

Keep the client a pure consumer and move collection out of process. The works library gains two affordances that both consume the same **version-1 sync payload** — `{ version: 1, platform, account: { name, homepageUrl?, bio?, followers? }, works: [{ platformWorkId, title, url?, publishedAt?, likes?, comments?, shares?, views?, body?, hotComments? }] }`:

- **Browser-sync import** (导入浏览器同步): a file-input button in the works library accepts the payload an out-of-band ego-browser collector writes. The collector lives outside the repo (it drives a logged-in session per platform), opens a fresh page per run, refuses to run when the browser window is minimized (a zero viewport silently breaks lazy-loading and wedges `page.evaluate`), takes note titles from the works wall (a detail page's `#detail-title` can render a sidebar recommendation), and reads interaction counts from `__INITIAL_STATE__` DOM state rather than `.count` elements that mix in recommended-feed numbers. A wall card rendering the literal text 赞 means zero likes, and `parseInt` already reads that correctly.
- **Account audit** (账号体检): an `audit` report kind alongside `account` and `compare`, whose client-built digest pairs registry facts (follower tier, positioning, monetization) with median-based distribution facts and whose system-prompt section bakes in the audit scoring rules — eight dimensions with fixed maxima, "data不足 scores 0", five verdict bands, medians never averages.

Every payload work upserts through the same `platform + accountId + platformWorkId` dedup path as manual import (title fallback included); the payload is a convenience export, not a trusted wire, so malformed entries are skipped and counted, never fatal. Entries carrying body text or hot comments land a `sync-<platformWorkId>.md` body asset — written **before** the manifest commit, so a committed work never points at a missing file — and the comment section flows into the existing AI teardown input, upgrading `commentInsight` from manual paste to auto-collection. A matched account backfills its follower tier, stamps `syncedAt`, and backfills positioning only when empty.

## Alternatives considered

**TikHub-first collection.** The paid API was probed with the real benchmark account: auth and routing work, but XHS endpoints are paid-only and reject free credit, and the API cannot see comment-section phrasing or profile hook copy — the operations-detail facts the audit values most. It stays as the scale transport (its collector variant is already written), not the default.

**An in-client crawler (page timers or an injected fetch loop).** Rejected again for the reason the phase-one note established: page-lived timers die with the tab, and anti-crawler responses would poison the manifest write path. The out-of-process collector keeps every failure mode in the tool, not in committed data.

**A new manifest schema for comments.** Storing harvested comments as a first-class manifest field would freeze a `formatVersion 0` shape around an input whose useful form is still moving. Embedding them in the body asset keeps the teardown input exactly where `analyzeCompetitorWork` already reads, with no schema change.

## Consequences

One collection payload serves two transports: the same collector contract now has a TikHub REST variant (list endpoints already carry 赞/藏/评, ready for when the account has balance), and a future host-side scheduler can write payloads without any client change. The sort select ranks works by saves as well as likes because the reference account's tutorial content collects ~1.5× what it likes — like-only rankings hid its real top works. Cost of the split: the collector's DOM selectors break on platform redesigns and the repo ships no collector, so the payload schema is documented in `importSyncPayload`'s JSDoc as the only stable surface. An audit report requires at least one imported work; the button disables otherwise.
