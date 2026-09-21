# Agent Note: 落云宗月度 Token 配额以 Relay 每请求检查硬停，用量抽取带缓冲上限

Status: implemented

[中文](2026-09-21-luoyunzong-quota-metering.zh.md) | English

## Problem

Task-book stage 4: monthly per-person token quotas with hard-stop semantics (decision 2), reset on the server's local timezone (decision 6), enforced at the Relay — with the acceptance criteria that tampering with instance-local state cannot affect enforcement and that the over-quota error is readable to the employee. The Relay already owned a per-request checkpoint (virtual-key auth, model authorization) from stage 3; the open questions were how usage gets metered without trusting instances, how the hard stop behaves exactly at the line, and how the metering path could be verified without any funded upstream (all available upstream keys return 429 with no usage payload).

## Decision

Quota enforcement joined the Relay's existing per-request chain: virtual-key auth → model authorization → monthly quota → forward. The account record may carry `monthlyTokens` (absent = unlimited, e.g. admins; `0` = immediate stop); when the current month's usage (`tokensIn + tokensOut`) meets the line, the request is rejected with a readable OpenAI-shaped 429 (`insufficient_quota`, Chinese message "本月 Token 额度已用完（used/quota）…"). Usage is metered server-side: the Relay tees each upstream response — SSE responses are scanned line-by-line for the terminal usage object, JSON responses are buffered whole with an 8 MiB tap cap — and records `{tokensIn, tokensOut, requests}` per account under a `YYYY-MM` key derived from the server's local timezone into `data/usage.json` (single-process serialized read-modify-write with atomic rename; a promise-chain mutex). Streaming requests get `stream_options: {include_usage: true}` injected unless the caller already set it, so compliant upstreams report usage on the final chunk. Metering failure degrades to under-counting only — it never blocks a request. `set-quota` writes the account file the gateway and Relay already reread per request (mtime-fresh), so quota changes take effect on the next request; `list-usage` renders per-account used/quota/remaining.

Verification used a controlled mock upstream (a 30-line fixture server, registered as a normal upstream and removed afterwards) so the real Relay path — auth, allowlist, quota check, forward, tap — ran end to end: non-stream JSON and stream SSE usage both recorded (admin +100/+20 per call across both modes); a 500-token member firing a 120-token model five times passed five times (120→600) and was hard-stopped on the sixth with the readable 600/500 error; a `--tokens 0` account was rejected immediately despite holding a perfectly valid key — demonstrating the enforcement point is the server-side counter, i.e. instance-local state cannot influence it by construction. The month key was confirmed against local time (`2026-09`); rollover is by-construction month-key separation.

## Alternatives considered

**Request-count quotas.** Rejected: the screenshots' semantics (and the 模型与权限 page's per-direction pricing columns) are token-based; the Relay already records separate `tokensIn`/`tokensOut`, which the later console pricing layer can multiply without schema change.

**Trusting instance-side meters.** Rejected outright — the task book's security principle ("server-side enforcement, never instance self-restraint") exists precisely because an instance runs arbitrary agent code; the counter lives only in the Relay's data directory.

**Blocking in-flight requests at the quota line.** Rejected by decision 2's wording: checks run at request admission; a forwarded request finishes. This also keeps the implementation race-free — the admission check reads committed usage only.

**Pricing multipliers now.** Deferred: billing display belongs to the console; the metering schema already separates directions.

## Consequences

Stage 4's acceptance criteria hold keylessly and the hard-stop loop was demonstrated live end to end (five 200s then a readable 429 at 600/500; quota-0 accounts stopped instantly). Costs and deferred items: usage accounting tolerates relay crashes only up to the last committed request (a forwarded-but-unrecorded response under-counts — acceptable at MVP scale, the control-plane DB will make this transactional); cache-read/cache-write token classes from upstream `prompt_tokens_details` are not yet split out (the pricing multipliers will want them); cross-month rollover is by month-key construction rather than observed live. Separately, load testing exposed a latent stage-1 defect worth naming: the disk sampler walked pnpm-heavy instance homes synchronously every 60 s and starved the event loop for tens of seconds — requests were only being served between walks. The walk is now async (`fs/promises`) at a 120 s interval.
