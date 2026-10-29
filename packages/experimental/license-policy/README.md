---
description: "Pure license governance for the [dragon-engine V2.5](https://github.com/guilinleolee/dragon-engine) mirror."
kind: "package-reference"
---
# dsh-experimental-license-policy

English | [中文](README.zh.md)

## Summary

Pure license governance for the [dragon-engine V2.5](https://github.com/guilinleolee/dragon-engine) mirror. This package owns the tier-to-decision table that downstream code (skill loaders, tool publishers, the dragon bridge) enforces at the boundary.

## Table of Contents

- [Tier → decision matrix](#tier--decision-matrix)
- [Service API](#service-api)
- [Config](#config)
- [Dev Note](#dev-note)

-----

This is an experimental package. It only mounts when its owning composition asks for it; no release package may declare it as a dependency.

## Tier → decision matrix

| Tier | Severity | Default decision | Reason |
|------|----------|------------------|--------|
| `mit` | green | `allow` | Zero red-line; surface to the model freely |
| `apache-2.0` | green | `attribute` | Carry NOTICE + "Modifications by dragon-engine" |
| `bsd-3-clause` | green | `attribute` | Preserve copyright; do not use author names for endorsement |
| `agpl-3.0` | red | `artifact-only` | **Red-line**: deliver as PNG / artifact only; never deploy as a network service |
| `noncommercial` | black | `reject` | CC BY-NC family: commercial use forbidden, so the asset may not enter a paid delivery |
| `proprietary` | black | `reject` | All rights reserved: redistribution to a third party forbidden |
| `noassertion` | black | `reject` | Blocked under DSH ecosystem governance baseline |
| `unknown` | amber | `attribute` (or `reject` with `rejectUnknown`) | Confirm upstream before redistribution |

The matrix is the source of truth for `dragon-assets/LICENSE-ATTRIBUTION.md` §一-§五. When that document changes, update this package and bump the snapshot.

`noncommercial` and `proprietary` exist because a tier the policy cannot express collapses into `unknown`, whose default decision is `attribute` — that is, loadable. The dragon-assets registry holds ten such assets (the CC BY-NC family and the Anthropic-licensed document skills), so a policy that cannot name them cannot refuse them.

## Service API

```
import LicensePolicy from '@deepseek-ai/dsh-experimental-license-policy'

const fiber = await ctx.plugin(LicensePolicy, { rejectUnknown: true })

// Classify
const tier = ctx.licensePolicy.normalize('Apache-2.0')   // → 'apache-2.0'

// Evaluate
const evaluation = ctx.licensePolicy.evaluate('AGPL-3.0')
// → { tier: 'agpl-3.0', severity: 'red', decision: 'artifact-only', reason: '...' }

// Boundary assertion
ctx.licensePolicy.assertAllowed('MIT', ['allow', 'attribute'])
// throws when the decision is outside the allowed set
```

## Config

| Field | Default | Meaning |
|---|---|---|
| `rejectUnknown` | `false` | When `true`, upgrade `unknown` decisions to `reject` instead of `attribute` |
| `agplAttribution` | `dragon-assets/LICENSE-ATTRIBUTION.md` §三 | Override the AGPL red-line notice text |

## Model Experience

None, as the policy is a pure decision table; consumers own any surfaced decision text.

#### KV Cache effect

None.

## Known Limitations and Deferred Work

- **Pure service only** — this package owns no I/O. Discovery of license markers (frontmatter sniff, LICENSE file walk, upstream metadata) belongs in `skill-index` and `agent-roster`; the policy only classifies what callers hand it.
- **Tier detection is textual** — `normalize()` matches against a small set of keywords; exotic licenses (`LGPL-3.0`, `MPL-2.0`, `Unlicense`) currently collapse to `unknown`. A future revision can extend the table.
- **No governance provenance** — the policy does not remember who set `rejectUnknown`. Callers that flip the switch should log the reason alongside the decision.
- **AGPL notice is in English only** — Chinese / multilingual translations live in `dragon-assets/LICENSE-ATTRIBUTION.md` §三; this package carries the English default and accepts overrides.
- **Boundary is advisory** — the policy returns a decision; it does not enforce one. Downstream code (loaders, publishers, the dragon bridge) is responsible for refusing `artifact-only` / `reject` decisions at the actual deployment boundary.


<a id="dev-note"></a>
### Dev Note

<details>
<summary>Working context for maintainers — click to expand</summary>

None.

</details>
