# Agent Note: GitHub-sourced skills, plugins, and MCPs installed through the dragon engine commit only to the fork

Status: implemented

English | [中文](2026-11-12-github-sourced-packages-fork-only.zh.md)

## Problem

The dragon-assets mirror and the platform plugin tree accumulate content the user sources externally: skills, plugins, and MCP servers downloaded from GitHub and installed through the dragon engine (deliverable-skill sync, `plugin-push`, instance profiles). This content is data or fork-only product surface, not upstream DeepSeek Harness contribution. Nothing in the tree records that boundary, so a broad `git add -A` during an upgrade merge could stage it and a push to `upstream` would carry it into the DeepSeek Harness repository.

## Decision

Everything installed through the dragon engine commits only to the user's fork (`guilinleolee/deepseek-harness`), never to upstream (`deepseek-ai/deepseek-harness`). Concretely:

- dragon-assets mirror data, downloaded skills/plugins/MCP servers, and their generated indexes live under `dragon-assets/` and `platform/plugins/` and are excluded from the pairing corpus, the concrete-terms corpus, and the staged whitespace check (each exclusion recorded in its gate or manifest).
- Pushes of commits carrying this content target `fork` only.
- The pairing manifest excludes `dragon-assets/` and `dragon-engine/` from the bilingual corpus; upstream-facing gates that cannot carry mirror data name these directories in their own exclusions rather than relying on this note.

The boundary is the content's origin (downloaded from GitHub), not its location: a fork-authored plugin like `kabage-content-studio` follows the same rule when it exists only for the platform, while upstream-contribution-ready code follows the normal PR flow.

## Alternatives considered

- Filter mirror content out at push time (a pre-push hook that strips dragon-assets paths from `git push upstream`): rejected — a push-time filter hides the boundary inside tooling and leaves the staged content in the history, where an amended or forced push would still carry it; refusing the push states the rule where the violation happens.
- Keep the mirror outside the repository (a sibling directory referenced by config): rejected — the dragon-engine tooling indexes `dragon-assets/` in-tree, and an out-of-tree mirror breaks the index-sync gates and the instance skill paths that resolve through the repo.
- Leave the boundary undocumented and rely on review: rejected — the upgrade merges in this fork stage broad `git add -A` sweeps, and a recorded rule is what makes the boundary checkable rather than tribal knowledge.
## Consequences

A mechanical `git push upstream` from any branch carrying mirror content would publish data the upstream repository does not maintain; the rule forbids that push rather than filtering content at push time. The exclusions above keep the fork's gates green without treating mirror content as maintained prose. If a downloaded skill graduates into a maintained contribution, it moves out of `dragon-assets/` into the maintained tree and loses these exclusions.
