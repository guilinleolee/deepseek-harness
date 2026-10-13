# Agent Note: The persona wizard's step 1 gains the own-site evidence block — the wizard fetches the user's blog or company website and extracts persona fields from it

Status: implemented

English | [中文](2026-10-03-persona-own-site-extraction.zh.md)

## Problem

The persona form already carried `site.url` and `site.pastedText` on the wire, and `buildFactsText` already fed the pasted text into the report facts — but the input sat in wizard step 2 among social links, and the 解析 button was a disabled placeholder ("网页抓取后续版本开放"). A user with a blog or company website had no way to let the analysis read it: they could only retype what the site already says.

## Decision

- **The site block lives in step 1, next to the résumé block.** Both are evidence about "who am I" — a private résumé and a public site — while step 2 stays purely social links. No wire field moved; only the DOM and the labels did (`企业官网` → `官网 / 博客`, since the field serves personal blogs too).
- **One new AI operation, `site`, fetches and extracts in the gateway.** `persona/site.ts` normalizes the user-typed address (scheme-less input gets `https://`; only http(s) passes, so `file:`/`data:`/`javascript:` reject before a request is built), fetches with a declared user agent, a 30 s deadline, and a 2 MiB cap, drops the `<head>`, and reduces the body to visible text through the shared gather sanitizer. `PersonaAiProcessor` gains a `site` case: fetch, then one extraction call whose JSON contract matches the résumé face (`persona-site@1`; `whoAmI` is allowed, unlike the generic fill). Fetching rides the same single-slot queue and rate-limit retry as the model call; fetch failures are not retried.
- **The fetched text is persisted, not just consumed.** The result carries the fetched text back; the controller writes it into the paste textarea (capped at the wire's 100 k), so the saved form, the report facts (`官网 / 博客` URL line added; the pasted line relabeled `官网内容`), and any later analysis read one content. A fetch that comes back empty returns no `text`, so the user's pasted fallback survives. Without a URL the pasted text is analyzed as-is — the textarea doubles as the fallback for login-walled sites.
- **The adoption path is the existing one.** Candidates land in the shared fill-preview panel (`origin: 'site'`) and reach the form only when adopted; nothing AI-generated enters the save path implicitly. No consent gate: the analyzed content is the public page the user pointed at, unlike the résumé's personal data.

## Alternatives considered

**Two remotes (`fetchSiteText` + an AI op taking text), like the gather face's split.** Rejected: the persona face is one explicit button per call, and splitting would force the client to sequence two calls, carry the fetched text in transient state, and distinguish fetch-vs-AI failures that both surface as one notice anyway.

**Fetching inside `report` when `site.url` is set.** Rejected: the report would gain a network dependency and non-determinism per generation, and regenerating could silently change conclusions the user already read. The persisted-text route gives the report the same content deterministically.

## Consequences

Costs: the gateway now makes outbound requests on behalf of a user-typed URL — same trust level as the gather face's feed URLs (a local user's own tool), guarded by scheme validation, the deadline, and the size cap. `htmlToText` flattens paragraphs into one blob, which the extraction prompt tolerates (the gather face ships the same trade). Verification: 53 tests across the two packages (fetch/normalize cases, the `site` operation, controller flow, step-1 view wiring), both packages typecheck clean, oxlint clean on touched files.
