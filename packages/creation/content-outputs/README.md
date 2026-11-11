---
description: "Remote gateway over the content-creation outputs library: the read-only projection plus the workbench columns' write faces."
kind: "package-bundle"
---
# @deepseek-ai/dsh-content-outputs

English | [中文](README.zh.md)

## Summary

Remote gateway over the content-creation outputs library: the read-only projection the Content Studio library view reads, plus the authorized write faces of the workbench columns — information gathering, benchmark accounts, creation, personas, publishing, review, the global template library, interactions, and the opinion-monitoring faces.

## Table of Contents

- [Gather write face](#gather-write-face)
- [Create write face](#create-write-face)
- [Sentiment faces](#sentiment-faces)
- [Model Experience](#model-experience)
- [Known Limitations and Deferred Work](#known-limitations-and-deferred-work)
- [Dev Note](#dev-note)

-----

Remote gateway over the content-creation outputs library: the read-only projection the Content Studio library view reads, plus the authorized write faces of the workbench columns — information gathering, benchmark accounts, creation, personas, publishing, review, the global template library, and interactions. Each column's storage follows one convention: theme-scoped sidecar manifests (`_<column>.json`) under `outputs/<theme>/assets/`, hidden root-level indexes (`_<column>-index.json`), and `.dsh-output.json` never touched.

The library convention is one directory per creation under the library root (default `<dsh home>/outputs`, override with the `root` config field): finished files sit at the project root, intermediate material lives under `assets/`, and `.dsh-output.json` is the only metadata file (format version 0 — this backend rejects older and newer formats alike). Directory names beginning with `.` or `_` are system entries, never projects. The `contentOutputs/list` Remote scans the root on every call and returns projects in topic order; a malformed or future-format metadata file never hides its directory — the project projects with fallbacks and `hasMetadata: false`, and an unreadable directory is named in `problems`.

## Gather write face

All gather storage lives under `outputs/<theme>/assets/`: the `_gather.json` manifest and `*.html` body snapshots. Paths are guarded (plain theme name, plain file name, traversal rejected); every manifest replacement is quota-trimmed, committed under a file lock with an atomic rename, and on Windows the commit retries the antivirus/indexer pinning codes with backoff; orphaned temp files are swept at gateway start.

- `fetchFeed` fetches and parses one feed document server-side (RSS 2.0, Atom, RDF, JSON Feed) with the source's `ETag`/`Last-Modified` cursors; a 304 returns `notModified` and nothing else. The browser never fetches cross-origin feeds itself.
- `collectTopicEntries` runs one keyword topic-collection pass for a selection category: the category's RSS feeds (same allowlist) plus one page of weibo visitor search and bilibili public video search per keyword, keyword-matched and deduplicated against the bank's existing URLs and titles. Nothing is persisted here — the caller upserts the candidates through the topics Remote.
- `writeAsset` sanitizes `*.html` content through the sanitize-html allowlist and truncates it to the body cap before it reaches disk; other text files pass through with a hard size cap.
- `readGatherManifest` / `writeGatherManifest` read and replace the manifest; entries that fail validation are named in `problems`, and a caller must not write back over a manifest with problems.
- `moveAsset` / `deleteAsset` / `readAsset` cover renames inside one theme, deletion, and text reads.
- `processMaterial` runs one explicit, queued model call (summary, key points, topic score, tags) through the shared `llm` service; rate limits retry with `Retry-After`-aware backoff, and nothing is persisted by the call itself.

Retention: per source, the newest 50 `unread`/`read` materials stay in a theme; `favorite` and `picked` markers and their snapshots are never removed automatically.

## Create write face

`extractCreateCopy` fetches the article page behind a pasted link and reduces it to title plus visible prose through the gather sanitization allowlist — network reading only, nothing is persisted, and the fetch happens gateway-side because the browser cannot reach cross-origin article pages. Non-http(s) URLs are rejected before fetching; a non-2xx response, a page over the response-size cap, or prose past the stored-text cap (which truncates and flags `truncated`) are the only failure modes the caller sees.

## Sentiment faces

The opinion-monitoring storage is one root-level `_sentiment.json` manifest (tasks, mentions, alerts, settings, and the newest report; `formatVersion 0`) following the persona manifest rules: a malformed record is named in `problems` and never hides the rest, and every write refuses to touch a file whose current parse dropped records.

- `getSentiment` returns the projection (including the stored report) plus the single-slot `scanning` flag and the last scan's summary; `putSentimentTask` / `deleteSentimentTask` (cascades the task's mentions and alerts) / `setSentimentTaskEnabled` manage tasks; `putSentimentSettings` replaces the settings block (domain and account blacklists, thresholds, retention, the push master switch, webhook URLs, and the SMTP transport fields); `handleSentimentAlert` marks one alert handled.
- `scanSentiment` runs the whole pipeline once per enabled task over the task's `sources` flags: RSS feeds through the shared gather fetcher (30-entries-per-feed cap, keyword-group filtering), plus — when toggled — the platform searches. Before those searches, the keyword-expansion middleware widens the task's subjects into the terms real posters use (one LLM call per task per day, cached 24h, degrading to the raw subjects on any failure): the breadth round searches the first three expanded terms per source, and — when the task's negative mentions already aggregate into a level-1/2 alert — a depth round searches the next three terms and drills two more comment pages. The comment layer rides the matched entries' platform ids (weibo mblog id, bilibili bvid) and is read from the public weibo hotflow endpoint and bilibili's public comment endpoint (the video's aid is resolved from its bvid first); every comment page runs the same keyword filter, the domain and account blacklists, and the URL dedupe, so a comment joins the mentions, the classification, and the alert aggregation as its own platform row. Both are anonymous public web endpoints; the subject search is the retrieval filter, so social mentions skip the keyword groups but run the same two-stage classification. Every adapter degrades to an empty page on any failure, so a blocked source never fails the scan. Dedupe is per task+URL, retention and the 5,000-mention hard cap prune on every append, and a concurrent scan call rejects immediately. After persistence, when the push switch is on, the scan posts one text digest per configured channel — Dingtalk and WeCom group robots (plain-JSON text protocol) and one email via nodemailer when the SMTP host/recipient/password are all set (implicit TLS on 465, STARTTLS otherwise); a channel failure only logs — push is best-effort because the alerts are already stored.
- `sentimentStats` computes the dashboard projection: totals, polarity counts, the 14-day trend, and the per-platform top list.
- `generateSentimentReport` picks a template deterministically — the routine daily report, or the crisis brief when an unhandled level-1/2 alert exists — then generates one model call per section in parallel and binds the bodies into both the Markdown document and a structured `ir` (template name plus the sections' key/title/body), so reports stay comparable across days. Each section degrades on its own; a fully failed generation lands the deterministic data-only degraded template instead of an error, and the manifest keeps the newest report only.
- `adjudicateSentimentAlert` runs the on-demand debate over one alert: an optimistic reader (mitigating factors, false-positive arguments) and a cautious reader (escalation risks) write their stance in parallel, and a synthesis call weighs both into a verdict. It is never part of the scheduled scan — the user triggers it per alert. The verdict is stored on the alert (`adjudication`), a later run replaces the earlier one, and a failed stance or synthesis degrades to its failure note or a deterministic join of the two stances.

## Model Experience

### Explicit one-shot AI remotes

#### What the model sees

Every user click assembles exactly one framed request through the shared `llm` service: material processing, creation generation/rewrite/evaluation, competitor teardowns and reports, persona fill/resume/site/social/report, publish adaptation, review diagnosis and period reports, template generate/optimize/extract, and interaction reply drafts, sentiment/intent classification, insight extraction, and the sentiment scan's batched polarity refinement. Prompts are frozen gateway constants versioned per face (`processMaterial`, `generateCreateContent`, `analyzeCompetitorWork`), inputs are truncated to the configured character cap, and the JSON-contract faces parse strictly with per-field problems; a failed or rate-limited call surfaces to the caller and never blocks the filesystem operations.

#### Token effect

One request per click. The prompt skeletons are fixed constants, so tokens scale with the caller-supplied material excerpt, persona digest, thread lines, or insight batch; batch flows (three creation variants, 50-message classification, 200-message insight batches) pay per request.

#### KV Cache effect

None retained. Every call is an isolated one-shot with no shared conversation prefix, so there is no cross-call cache state to invalidate; the caller owns whatever it stores in the manifests.

## Known Limitations and Deferred Work

- **Projection stays read-only** — `list` never mutates; creating and updating output projects is still the agent's job through its own tools. The gather face writes only `assets/` system files, never deliverables.
- **Deliverable bytes still need a file surface** — the projection carries names and counts only.
- **Fresh format** — `formatVersion 0` manifests and metadata have no compatibility promise, per the repository's pre-release stance.

<a id="dev-note"></a>
### Dev Note

<details>
<summary>Working context for maintainers — click to expand</summary>

None.

</details>
