# dsh-experimental-license-policy

[English](README.md) | 中文

天龙引擎 V2.5 镜像的纯 License 治理层。本包持有"tier → decision"判定表，供下游（skill 加载器、工具发布器、dragon-bridge）在边界处强制执行。

这是一个实验性包。仅当宿主 composition 显式请求时才会被装载；release 包**不得**在 `dependencies` 中引用它。

## Tier → 决策矩阵

| Tier | 严重度 | 默认 decision | 说明 |
|------|--------|--------------|------|
| `mit` | green | `allow` | 零红线；可自由暴露给模型 |
| `apache-2.0` | green | `attribute` | 需携带 NOTICE + "Modifications by dragon-engine" |
| `bsd-3-clause` | green | `attribute` | 保留版权；禁止用作者名背书 |
| `agpl-3.0` | red | `artifact-only` | **红线**：仅交付 PNG / artifact，禁止部署为网络服务 |
| `noassertion` | black | `reject` | DSH 生态治理基线下拒绝 |
| `unknown` | amber | `attribute`（或 `reject` 当 `rejectUnknown=true`）| 再分发前需确认上游 |

该矩阵是 `dragon-assets/LICENSE-ATTRIBUTION.md` §一-§五 的真相源。如该文档变化，本包必须同步更新并 bump 快照。

## Service API

```ts
import LicensePolicy from '@deepseek-ai/dsh-experimental-license-policy'

const fiber = await ctx.plugin(LicensePolicy, { rejectUnknown: true })

// 分类
const tier = ctx.licensePolicy.normalize('Apache-2.0')   // → 'apache-2.0'

// 评估
const evaluation = ctx.licensePolicy.evaluate('AGPL-3.0')
// → { tier: 'agpl-3.0', severity: 'red', decision: 'artifact-only', reason: '...' }

// 边界断言
ctx.licensePolicy.assertAllowed('MIT', ['allow', 'attribute'])
// 当 decision 不在 allowed 集合时抛错
```

## 配置

| 字段 | 默认值 | 含义 |
|---|---|---|
| `rejectUnknown` | `false` | 为 `true` 时将 `unknown` decision 升级为 `reject` |
| `agplAttribution` | `dragon-assets/LICENSE-ATTRIBUTION.md` §三 | 覆盖 AGPL 红线声明文本 |

## 模型体验

### 模型能看到什么

**无任何内容**——本策略是纯判定表。消费者（加载器、发布器）可在工具描述里暴露 decision 文本，但模型 prompt 不会包含原始策略。

### Token 影响

无。

### KV Cache 影响

无。

## 已知限制与延后工作

- **仅 Service，无 I/O**——本包不读盘。License 标记的发现（frontmatter 嗅探、LICENSE 文件遍历、上游元数据）属于 `skill-index` 和 `agent-roster`；本策略只分类调用方传进来的字符串。
- **Tier 检测基于文本**——`normalize()` 仅匹配一组关键字；冷门 License（`LGPL-3.0`、`MPL-2.0`、`Unlicense`）当前会落到 `unknown`。未来可扩展。
- **无治理出处记录**——本策略不记住谁设了 `rejectUnknown`。切换该开关的调用方应同时记录原因。
- **AGPL 声明仅英文**——中文/多语言版本在 `dragon-assets/LICENSE-ATTRIBUTION.md` §三；本包持英文默认并接受覆盖。
- **边界是建议性**——本策略返回 decision，不强制执行。下游（加载器、发布器、dragon-bridge）负责在实际部署边界处拒绝 `artifact-only` / `reject` decision。
