# Agent Note: The gather view lands inside the workbench overlay with a gateway-side write face, browser-side configuration, and no background polling

Status: implemented

English | [中文](2026-09-25-dsh-content-studio-gather.zh.md)

## Problem

The Content Studio workbench needed an information-collection surface (信息收集): RSS/Atom source management, collection tasks, and a material library per outputs theme, for creators who gather topic intelligence before writing. The constraints were strict: no new slots, no DSH core changes, no cross-origin fetching in the browser (feeds ship no CORS headers), no background polling, AI that can fail loudly under unstable upstream quota, and Windows-local disk semantics where antivirus and the search indexer briefly pin just-closed files.

## Decision

**One new view in the existing overlay; one write face on the existing gateway.** The gather view is a new `NAV_ITEMS` entry in `ui-content-studio`'s `shell.overlay` surface — no slot, no footer action, no manifest change. All server behavior lives in `packages/creation/content-outputs` as six new `@Remote` methods plus `processMaterial` (`fetchFeed`, `writeAsset`, `readGatherManifest`, `writeGatherManifest`, `moveAsset`, `deleteAsset`, `readAsset` — the last added with the competitor face). The `list()` projection is unchanged except one fix the spec anticipated: `_`-prefixed files no longer count as assets or render as deliverables, so `_gather.json` is invisible to the library.

**Storage split.** Sources, tasks, and run logs live only in browser storage under `content-studio.gather.` through one storage module (write failure — quota, private mode — demotes to in-memory and the UI says so). Materials live only in the on-disk manifest `outputs/<theme>/assets/_gather.json` (formatVersion 0). Clearing browser data loses only configuration; read/favorite/picked state is part of the manifest entry and survives, and every merge appends without touching existing entries, so user state also survives every refresh.

**Conditional requests beat the mandated fetch vehicle — deviation.** The prompt mandated consuming `packages/web`'s fetch capability; that seam deliberately exposes no request or response headers, so ETag/Last-Modified cursors, 304 handling, and `Retry-After` — all required by the same prompt's failure semantics and acceptance list — are unsatisfiable through it. `fetchFeed` therefore uses Node's global fetch inside the gateway (deadline, size cap, per-source cursors echoed by the caller). The hard constraints — gateway-only fetching, zero changes to `packages/web`, no browser-side feed access — are preserved; only the library choice inside the gateway changed.

**Atomic writes via the owned package — deviation.** The prompt named `write-file-atomic`; the repository already owns `@deepseek-ai/dsh-atomic-write` (same-directory exclusive-create temp, atomic rename, cross-process lock, temp cleanup on failure) and `content-schedule` already uses it. Two atomic-write protocols over one outputs tree would be one protocol too many, so the gather store builds on the owned package and adds, in-package, exactly what it lacks: Windows EPERM/EACCES/EBUSY rename retry (100 ms doubling, five tries), per-file serialization, and an orphan-temp sweep at gateway start. fsync remains out of scope, as it already is repo-wide (logged TODO in the owned package).

**AI through the `llm` Service Definition, not an agent turn.** There is no browser-side completion channel; the only realistic path is a node-side gateway consuming `llm` — the session-title one-shot pattern. `processMaterial` runs one framed call (built-in skill prompt as system), queued one at a time (p-queue), retrying only upstream rate limits (p-retry, provider `Retry-After` honored first, exponential capped at 30 s, four retries). The skill prompt is a module constant in the gateway rather than a registry-registered skill: registry skills are agent-visible loader tools, which the explicit-button flow does not need. Results are JSON-validated at the model boundary; failures return as RPC errors the UI renders as "not generated" with a retry button.

**Scheduler semantics.** A 30 s master tick runs interval tasks while the surface is open; `visibilitychange` pauses and resumes it; reopening after a gap runs every overdue task once with its `since` cursor — compensation, not polling. Closing the workbench disposes the scheduler from the surface component's effect cleanup; no timer survives. Failure semantics: a failed source keeps all its materials, the task logs `failed` with the error, and the source earns 1 h → 2 h → 4 h → 24 h backoff; a 304 counts as success and only refreshes cursors and `lastFetchedAt`. The copy states "runs only while the workbench is open" as a product fact.

**Sanitization, two layers.** Gateway-side, `sanitize-html` with an allowlist (http/https schemes only, `rel="noopener noreferrer"` forced, non-allowlisted tags dropped with content) before any `*.html` snapshot reaches disk, truncated at 100,000 characters. Render-side, DOMPurify (`USE_PROFILES: {html: true}`, `KEEP_CONTENT: false`). The prompt's third layer — a page CSP — is not implementable from a client plugin: the workbench renders inside the shell's already-parsed document, and dynamically injected `meta` CSP is ignored by spec; a CSP header belongs to the shell server, outside this change's scope. The pushed-to-create handoff carries id, title, and URL only — never the body — through an extension of the existing open/close controller (`pickMaterial`/`pickedMaterial`/`clearPickedMaterial`), and the create view prepends a one-line material reference to copied instructions.

## Alternatives considered

**Browser-side fetching (prompt v1's approach).** Rejected: most feeds lack CORS headers; every reference reader (Miniflux, FreshRSS, Folo) fetches server-side.

**A second Typert gateway class in `content-outputs` for AI.** The bundle patch loads exactly one plugin per package (the default export), so a second service class would never instantiate without inventing a parent-starts-child mechanism. One gateway class carrying `llm` in `static inject` keeps the loading story unchanged; the `llm` service is present in every profile via the base bundle.

**Quota only in the client.** Both sides trim: the client so its UI counts match, the gateway so the favorite/picked exemption is enforced at the durability layer regardless of caller. Dropped-entry snapshot deletion happens gateway-side only after the trimmed manifest commits, so a crash can strand a file but never a reference.

## Consequences

The gather surface is a pure plugin: dropping it from a roster removes the feature entirely, and the DSH core, the BFF, and `packages/web` are untouched. Costs: feed conditional requests depend on sources honoring ETag/Last-Modified (some static servers ignore them, and each such run transfers the full document); AI quality rides whatever provider/model the profile config sets (`provider`/`model` config fields, defaulting to the DeepSeek route); and the one-plugin-per-package load rule means every future write face of this kind will share the gateway's `llm` injection — the competitor face already does, and it consumes the same shared `streamLlmText`/retry policy extracted here.
