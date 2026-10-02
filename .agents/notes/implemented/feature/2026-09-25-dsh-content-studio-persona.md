# Agent Note: The persona view stores account personas as one global manifest, and the packed prompt is rendered where it is previewed

Status: implemented

English | [中文](2026-09-25-dsh-content-studio-persona.zh.md)

## Problem

The 画像 view was a free-text textarea in browser storage (`dsh-content-studio.persona`), injected verbatim into copied instructions. The persona plan (v2, `D:\dsh-content-studio\docs\persona-dev-prompt-v2.md`) upgraded it to a full persona manager — four-step wizard, AI field fill, résumé extraction, a derived Markdown report, and selection for the create face — under three frozen edges: cross-device state must live on disk (not localStorage), the topic-level `.dsh-output.json` is schema-frozen work metadata that a cross-topic entity must not touch, and the create face's published contract (`stable id + revision + digest, read through a gateway`) has to be satisfied or the create side keeps its inline path forever.

## Decision

- **One global manifest, `~/.dsh/outputs/_personas.json`** (`formatVersion 0`), beside `_schedule.json` in the scanner's `_`-prefix blind spot. Everything is embedded — résumé text, pasted website text, and the report in full — so a persona never references a file, nothing dangles on delete, and the manifest alone is a complete backup. The write face lives on the content-outputs Remote (`listPersonas` / `getPersona` / `putPersona` / `putPersonaReport` / `deletePersona` / `processPersonaAi`), same carrier as every other write face. `putPersona` is the form save: the gateway bumps `revision`, recomputes the ≤200-character deterministic `digest` (fixed field order, no banned-word/red-line details, suffixed `（vN）`), and owns timestamps. Report edits ride the separate `putPersonaReport` — revision and digest stay, so the staleness banner (`revision > report.sourceRevision`) tracks form changes only. A write refuses to touch a manifest whose parse dropped entries or whose version is unknown: a save must never silently delete user personas.
- **The packed prompt is rendered client-side** (`persona/prompt.ts`, `persona-prompt@1`) — the wizard's live preview and the future create-side injection read one rendering. The digest, in contrast, is derived by the gateway after the revision increment, which is exactly why the revision suffix creates no circularity. The enum/label tables exist twice (client `persona/model.ts`, gateway `persona/types.ts`) because the client bundle purity gate forbids cross-plugin value imports; a cross-check test pins the two tables to byte equality.
- **AI is explicit and outside the save path.** Fill (blank fields only — `whoAmI` can never be generic-filled, résumé extraction only), résumé extraction (gated behind an explicit consent checkbox), and report generation each ride `processPersonaAi` behind the shared `streamLlmText` helper with the rate-limit-only retry. Candidates land in a preview panel for per-field adoption; adopted values carry `source: "ai"` plus the prompt version, and any user edit flips provenance back to `user`. Saving never waits on AI.
- **The old free text is imported, not dropped**: first boot with a non-empty legacy key shows a one-tap import (the text becomes `style.customText`), and the key is cleared after the write lands. With a persona selected, `withIdentity` injects its packed prompt; the inline text remains the fallback, so the create view needs no change this phase.

## Latent bug this work uncovered (fixed across all four AI faces)

p-retry v8 hands `shouldRetry` / `onFailedAttempt` a frozen failure context (`{ error, attemptNumber, … }`), not the raw error — but `isRateLimitError` / `retryAfterMs` expected the raw error. The rate-limit retry therefore never fired, in the gather, competitor, and create AI faces alike; every non-rate-limit failure surfaced identically, and real 429s burned all attempts on a single try. The helpers now unwrap `context.error` when present. No test had exercised the loop; the persona retry test was the first to run it.

## Deviations from the plan text

- The plan named a `contentPersonas` gateway; the face rides the content-outputs Remote under `*Persona*` names, matching gather/competitor/create and the plan's own "or merge into the existing creation gateway package" alternative.
- The plan's storage chapter put assets under the topic directory; that whole chapter was already superseded by the plan's 〇.2 locked decision — nothing persona-related exists under `<主题>/`.
- The plan's `assetCount` `_`-filter fix was already landed by the gather work (`content-outputs/src/scan.ts`), so this phase only kept the regression coverage that already exists.
- Quota metering for the four persona AI actions stays unplanned until P1 by the plan itself; the freemium gate (`create/quota.ts`) is owned by the create column and was left untouched.

## Alternatives considered

**A separate `contentPersonas` Remote package.** Rejected: four methods and one file do not justify a new package, mount, and peer-dependency chain while content-outputs already carries the other three write faces under the same lock/atomic-write conventions.

**Gateway-side packed-prompt storage.** Storing the rendered prompt next to the fields would duplicate content and drift the moment either changes; the prompt is a pure function of stored fields, and the single renderer serves preview and injection.

**Client-computed digest.** Rejected: the digest is durable data consumed by the create face's `profileRef`; deriving it where the revision is assigned keeps one authority and honors the plan's `（vN）` suffix.

## Consequences

Persona management works with zero network dependency — create, fill, report, and select all survive missing API keys, 429s, and offline runs, and every persona survives browser changes because the manifest lives on disk with the report embedded. Costs: the enum/label tables are duplicated across the client and the gateway (pinned to equality by test, but a new platform or preset must land in both); the résumé face stores extracted text only, so the original file is the user's to keep; and the refuse-on-problems write policy means a corrupted manifest blocks saves until the bad records are repaired by hand. Cross-session note: the create column's `create/` write face and quota gate evolved in parallel inside the same packages; the persona face shares only the extracted AI helper and touched nothing under `create/`, and the p-retry v8 helper fix in `gather/ai.ts` repairs all four AI faces at once.
