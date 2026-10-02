# Agent Note: Drift local-plugin spec normalization

Status: implemented

[中文](2026-10-02-kabage-drift-local-plugin-spec-normalization.zh.md) | English

## Problem

The drift check's `plugin-version` comparison matched the desired spec against the installed spec as raw strings. The two sides never match for local-path plugins: the desired store records what `plugin-push` resolved (a `\` absolute path on Windows), while the profile `package.json` dependency is written by the package manager as `link:` + `/` — the same directory in two spellings. Every guard/admin-tools deploy therefore raised fresh `plugin-version` drift on all target instances, and `mergeDiffs` preserves first detection, so each false positive aged past `driftStaleHours` into a red alarm within 24 hours of a successful, verified deploy.

## Decision

The comparison moved into `introspect.pluginSpecDrifts(desired, effective)`, which normalizes both sides before comparing: strip a leading `link:`, unify `\` to `/`. Everything else is unchanged — bare-package-name desired specs still skip the version check (existence stays with `plugin-missing`/`plugin-extra`), a still-different path still reports `plugin-version`, and `detail` keeps both original spellings so the report stays diagnosable. The inline loop in supervisor's drift pass is replaced by a call to the function; behavior elsewhere (merge, staleness, console rendering) is untouched.

## Alternatives considered

**Hand-normalizing the desired store (`data/plugins.json`) to the `link:` form.** Rejected: `plugin-push` rewrites the spec through `resolve()` on every push, so the alignment would not survive the next deploy, and the store would then misstate what the CLI accepts (`isLocalPathSpec` rejects `link:` input).

**Accepting `link:` specs in `plugin-push`.** Rejected: it widens the CLI surface to fix a reporting bug, and the install path would need to re-derive what the spec already encodes.

**Ignoring the diff as cosmetic.** Rejected: the drift page is the deploy-success signal (staged → activated → drift-aligned); a false positive that auto-escalates to red trains the operator to ignore the page.

## Consequences

Drift on linked local plugins now reports aligned right after a verified push + activate; the fix was exercised against the live deployment it came from (guard on e01–e03, admin-tools on e01 went from 4 fresh yellow `plugin-version` entries to none). Genuine version drift still fires — proven by the new `test/drift-spec-verify.mjs` (6 checks), which pins the normalization, the bare-name skip, the still-reported case with original spellings in `detail`, and the missing-plugin handoff to `compareSets`. No config or on-disk format changes; running suites are unaffected (the drift path previously had no executed coverage — this file is its first).
