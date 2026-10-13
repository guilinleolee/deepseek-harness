# dsh-experimental-dragon-bridge

[English](README.md) | 中文

DSH 对天龙引擎 V2.5 镜像的**统一门面**。合并 `@deepseek-ai/dsh-experimental-skill-index`、`@deepseek-ai/dsh-experimental-agent-roster`、`@deepseek-ai/dsh-experimental-license-policy` 三个包，调用方通过一次 `search()` 即可跨 skill / agent / command / hook / plugin 五类检索，并由 policy 守好 AGPL / NOASSERTION 边界。

这是一个实验性包。仅当宿主 composition 显式请求时才会被装载；release 包**不得**在 `dependencies` 中引用它。

## 依赖

本包是纯门面，三个上游包必须先注册；`loadAll()` 触发每个 sibling 的 refresh 并复用其结果。典型 composition：

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

// 跨 kind 筛选
const mitSkills = ctx.dragonBridge.search({ kind: 'skill', license: 'mit' })
const artifactsOnly = ctx.dragonBridge.search({ decision: 'artifact-only' })

// 桶访问器
ctx.dragonBridge.allowed()        // decision === 'allow'
ctx.dragonBridge.attributed()     // decision === 'attribute'
ctx.dragonBridge.artifactOnly()   // decision === 'artifact-only'
ctx.dragonBridge.rejected()       // decision === 'reject'
```

每个 asset 都携带源记录（skill/command/hook/plugin 用 `AssetIndexEntry`，agent 用 `AgentRole`）、归一化后的 license tier、以及完整的 `LicenseEvaluation`，便于调用方在工具描述里展示 attribution 文本。

## 配置

| 字段 | 默认值 | 含义 |
|---|---|---|
| `safeOnly` | `false` | 为 `true` 时，默认 `search()` 自动过滤掉 `artifact-only` 与 `reject`；显式传 `decision` 可覆盖该过滤。|

## 跨包契约

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

bridge 通过 Cordis 注入依赖；`ctx.dragonIndex`、`ctx.agentRoster`、`ctx.licensePolicy` 必须在 `loadAll()` 之前都存活。

## 模型体验

### 模型能看到什么

**无任何直接内容**。调用方可以通过自己的工具选择性地把 `search()` 结果暴露给模型；本包是 service，不是 tool。

### Token 影响

无。

### KV Cache 影响

无。

## 已知限制与延后工作

- **无实时变更通知**——`loadAll()` 是唯一的刷新路径；bridge 不订阅 `skills/change` 或任何 sibling 事件流。未来可把 `skills/change` 接到内部失效。
- **AGPL 资产仍出现在搜索结果中**——除非显式 `safeOnly: true`，bridge 默认**不**静默丢弃 `artifact-only` 资产。默认行为保留审计可见性；调用方需自行决定是否对模型暴露。
- **Skill 的 description 兜底**——bridge 的 `text` 匹配在 index 条目无 `description` 字段时会回退到 `displayName`。未来 schema 升级后可统一字段。
- **无模糊搜索**——`search({ text })` 是字面子串匹配。Embedding 检索需要新 sibling 包（Phase 4+）。
- **单次 policy 决策**——bridge 在 `loadAll()` 时一次性评估 license；上游 policy 变更后需手动让 bridge cache 失效。
