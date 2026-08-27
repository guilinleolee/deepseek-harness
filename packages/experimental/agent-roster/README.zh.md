# dsh-experimental-agent-roster

[English](README.md) | 中文

DSH 对天龙引擎 V2.5 镜像角色花名册的只读访问层。本包注册一个 Cordis Service，遍历 `dragon-assets/agents/` 下每个 `*.md`，解析最小 frontmatter + 一级标题 + 首段 + 能力清单，按天龙 00-99 数字编号暴露为强类型花名册。

这是一个实验性包。仅当宿主 composition 显式请求时才会被装载；release 包**不得**在 `dependencies` 中引用它。

## 读取哪些文件

`dragon-assets/agents/` 含 182 个 .md + 三个保留子目录（`shibazi/`、`zcf/`、`.gitnexus/`）。本包行为：

| 源 | 行为 |
|---|---|
| `dragon-assets/agents/*.md` | 解析为角色定义 |
| `dragon-assets/agents/{shibazi,zcf,.gitnexus}/` | 默认排除 |
| `dragon-assets/agents/<其他>/` | 出现在 `excludeSubdirs` 时排除 |
| `dragon-assets/agents/` 不存在 | `loadAll()` 返回空花名册 |

每个文件解析得到：

- **id** — 文件名去 `.md`
- **displayName** — 首个 `# 标题` 文本（中文名也保留在同字段）
- **description** — 标题后首个非标题段落
- **numericPrefix** — 标题前缀的 `NN` 或 `NN-NN`（如 `00`、`28-10`）
- **family** — 按数字前缀推导的桶（`core` 00-09, `platform` 10-15, `data` 16-19, `business` 22-25, `finance` 26-29, `social` 31-35, `sales` 38-40, `commerce` 45-47, `finance-2` 60-89, `hr` 90-99, 其他为 `unknown`）
- **capabilities** — `## 能力` 或 `## Capabilities` 段下的 bullets
- **license** — YAML frontmatter 中首条 `license:` 行
- **path** — 工作区相对路径

## 配置

| 字段 | 默认值 | 含义 |
|---|---|---|
| `dragonAssetsRoot` | `<workspace>/dragon-assets`（或 `$DRAGON_ASSETS_ROOT`）| 镜像根 |
| `excludeSubdirs` | `['shibazi', 'zcf', '.gitnexus']` | `agents/` 下要忽略的目录名 |

## Service API

```ts
import AgentRoster from '@deepseek-ai/dsh-experimental-agent-roster'

const fiber = await ctx.plugin(AgentRoster, { dragonAssetsRoot: '...' })

const roster = await ctx.agentRoster.loadAll()
const core = ctx.agentRoster.byFamily('core')
const matches = ctx.agentRoster.search({ text: '博主', limit: 10 })
const analyst = ctx.agentRoster.get('00-analyst')
```

`loadAll()` 幂等，可在上游重建后重复调用。`search()`、`get()`、`byFamily()` 操作内存中的花名册，不读磁盘。

## 模型体验

### 模型能看到什么

**无任何内容**——本 Service 是 DSH 内部组件，永远不会直接暴露给模型。调用方可以通过自己的工具选择性地把搜索结果暴露给模型。

### Token 影响

无。

### KV Cache 影响

无。

## 已知限制与延后工作

- **不在上游重建**——本包只读 `dragon-assets/agents/`，刷新需天龙维护者手动同步。
- **CN/EN 不分离**——displayName 和 displayNameZh 在双语标题时使用同一段文本。未来可通过 `## 中文名` 段拆分。
- **能力段依赖启发式**——只识别 `## 能力` 和 `## Capabilities`，其他标题忽略。自定义标题名的角色会被静默忽略。
- **License 只看 frontmatter**——未读 LICENSE 文件存在性；没有 `license:` 行的角色 `license === undefined`。
- **冻结快照**——花名册被深冻结，调用方需先克隆再修改。
- **Family 分桶是 opinionated**——00-99 范围源自 `dragon-engine CLAUDE.md §3`，不是声明表。若上游重新分桶，修改本包代码而不是调用点。
