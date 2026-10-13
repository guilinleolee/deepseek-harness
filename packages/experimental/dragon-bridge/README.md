# dsh-experimental-dragon-bridge

English | [中文](README.zh.md)

The single facade for the [dragon-engine V2.5](https://github.com/guilinleolee/dragon-engine) mirror inside DSH. Combines `@deepseek-ai/dsh-experimental-skill-index`, `@deepseek-ai/dsh-experimental-agent-roster`, and `@deepseek-ai/dsh-experimental-license-policy` so a consumer can search across skills, agents, commands, hooks, and plugins in one call and trust the AGPL / NOASSERTION gate.

This is an experimental package. It only mounts when its owning composition asks for it; no release package may declare it as a dependency.

## Dependencies

The bridge is a pure facade. The three upstream packages must be registered first; `loadAll()` triggers each sibling's refresh and reuses the results. A typical composition:

```ts
import DragonAssetIndex from '@deepseek-ai/dsh-experimental-skill-index'
import AgentRoster from '@deepseek-ai/dsh-experimental-agent-roster'
import LicensePolicy from '@deepseek-ai/dsh-experimental-license-policy'
import DragonBridge from '@deepseek-ai/dsh-experimental-dragon-bridge'

await ctx.plugin(DragonAssetIndex, { dragonAssetsRoot })
await ctx.plugin(AgentRoster, { dragonAssetsRoot })
await ctx.plugin(LicensePolicy)
await ctx.plugin(DragonBridge)
```

## Service API

```ts
const assets = await ctx.dragonBridge.loadAll()

// Cross-kind filtering
const mitSkills = ctx.dragonBridge.search({ kind: 'skill', license: 'mit' })
const artifactsOnly = ctx.dragonBridge.search({ decision: 'artifact-only' })

// Bucket accessors
ctx.dragonBridge.allowed()        // decision === 'allow'
ctx.dragonBridge.attributed()     // decision === 'attribute'
ctx.dragonBridge.artifactOnly()   // decision === 'artifact-only'
ctx.dragonBridge.rejected()       // decision === 'reject'
```

Each asset carries the source entry (`AssetIndexEntry` for skills/commands/hooks/plugins, `AgentRole` for agents), the resolved license tier, and the full `LicenseEvaluation` so callers can show attribution text in tool descriptions.

## Config

| Field | Default | Meaning |
|---|---|---|
| `safeOnly` | `false` | When `true`, default `search()` filters out `artifact-only` and `reject` decisions; explicit `decision` overrides the filter. |

## Cross-package contract

```
┌─────────────────┐      ┌──────────────────┐
│  skill-index    │      │  agent-roster    │
│  (jsonl parse)  │      │  (md parse)      │
└────────┬────────┘      └────────┬─────────┘
         │                        │
         ▼                        ▼
   ┌─────────────────────────────────────┐
   │            dragonBridge            │
   │  loadAll() →  wrap  →  cache        │
   └────────────────┬────────────────────┘
                    ▼
         ┌────────────────────┐
         │   license-policy   │
         │  (tier → decision) │
         └────────────────────┘
```

The bridge depends on the three services through Cordis injection; `ctx.dragonIndex`, `ctx.agentRoster`, and `ctx.licensePolicy` must all be live before `loadAll()` runs.

## Model Experience

### What the model sees

Nothing directly. Consumers may choose to surface `search()` results to the model through their own tools; the bridge is a service, not a tool.

### Token effect

None.

### KV Cache effect

None.

## Known Limitations and Deferred Work

- **No real-time change notifications** — `loadAll()` is the only refresh path; the bridge does not subscribe to `skills/change` or any sibling event stream. A future revision can wire `skills/change` to an internal invalidation.
- **AGPL assets stay in the search results** — the bridge never silently drops `artifact-only` entries unless `safeOnly: true`. Default behavior preserves audit visibility; consumers must decide whether to surface them.
- **Description fallback for skills** — the bridge's `text` matcher falls back to `displayName` when the index entry has no `description` field. Future schema may normalize both sides under a single field.
- **No fuzzy search** — `search({ text })` is a literal substring match. Embedding-based retrieval would require a new sibling package (Phase 4+).
- **One-shot policy decision** — the bridge evaluates the license once at `loadAll()` time. If the upstream policy changes, the bridge cache must be invalidated manually.
