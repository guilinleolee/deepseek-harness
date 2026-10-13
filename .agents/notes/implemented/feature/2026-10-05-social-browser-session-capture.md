# Agent Note: Social-profile capture lands as a browser-session read behind a frequency gate, not a scraper

Status: implemented

English | [中文](2026-10-05-social-browser-session-capture.zh.md)

## Problem

The persona social analysis could only fetch profile URLs anonymously, and every supported homepage (小红书/抖音/微博/公众号/B站/头条) answered with a JS anti-bot shell or a login wall — the analysis honestly reported "no readable content" and the feature was dead on arrival. The 2026-10-05 scraping research pinned the compliant path: the user reads THEIR OWN profile through THEIR OWN logged-in browser session, locally, at low frequency; signature reversal is the criminal-law dividing line and is never implemented.

## Decision

- **One wire face, two input kinds.** The `social` AI operation now takes optional `profiles` (pre-captured labeled sections) alongside `links`; captured platforms are analyzed as-is and their links are not refetched, so the anonymous-fetch path remains as the automatic fallback and `manual-paste` remains the terminal fallback.
- **Four Remote faces on `contentOutputs`**: `socialStatuses` (per-platform session presence + today's counter), `socialStartLogin` (launches a HEADED browser the user logs into themselves; returns before completion, callers poll statuses), `socialCapture` (headless logged-in read of one profile URL, returns the labeled section text), `socialForget`. The user's session storage states persist as 0600 JSON under `<dsh home>/social-states/` — credentials and captured data never leave the machine.
- **Login detection keys on cookies, not DOM.** Each platform's "logged in" signal is the presence of one well-known session cookie (`web_session`/`sessionid`/`SUB`/`SESSDATA`), stable across redesigns. DOM extraction snippets are community-documented logged-in shapes with fallbacks and are the acknowledged field-iteration surface; every failure path degrades to a message pointing at the manual fallback.
- **The frequency gate counts attempts, not successes.** `consumeCapture` runs before the browser opens: a hard per-platform daily cap (config `maxDailyCaptures`, default 3, 1–10) rejects with a message that names the cap; counters persist 0600 and roll over on the local day. Low frequency is the compliance posture that keeps logged-in reads off the platforms' risk radar.
- **头条 stays out** of the capture platform set by design (byte-dance VM signing, no official API, lowest value density); its step-2 row keeps the plain link path and the manual-paste guidance.

## Alternatives considered

**Signature-reversal adapters (x-s/x-bogus/a1) for anonymous HTTP.** Rejected permanently: it is the judicial dividing line for 非法获取计算机信息系统数据罪, a commercial product distributing such code is the heavier "providing tools" exposure, and every platform algorithm update breaks it wholesale.

**Third-party paid data APIs (新榜/蝉妈妈/灰豚).** Rejected: no public API or pricing, Xiaohongshu-side services were shut down in the official crackdown (compliance contagion), and their granularity (market/directory data) does not match single-user self-profiles.

**Encrypting the storage states.** Deferred: the established dsh pattern for credential-adjacent local files is 0600 + user-home directory (the personas manifest works the same way); adding a key-management layer for one file class is deferred until a threat model demands it.

## Consequences

Costs: the four DOM extractors are the acknowledged maintenance surface — a platform redesign degrades that one platform to manual paste with a specific error message (登录已过期 vs 页面结构可能已改版), never a silent failure; captures are ephemeral wizard state (not persisted on the wire — the adopted fields are the persistence), so a wizard closed before adoption loses the captured text only. Verification: 96 tests across both packages (sessions round-trip, frequency cap and day rollover, section rendering, capture orchestration with a fake browser, expired-vs-redesign distinction, profiles-vs-links social analysis, step-2 wiring), typecheck and lint clean on touched files, typert artifacts regenerated for the new faces.
