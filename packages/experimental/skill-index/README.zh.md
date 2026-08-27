# dsh-experimental-skill-index

[English](README.md) | 中文

DSH 对天龙引擎 V2.5 镜像资产索引的只读访问层。本包注册一个 Cordis Service，读取 `dragon-assets/index/` 下五个 `*.jsonl` 文件并以可查询快照的形式暴露。

这是一个实验性包。仅当宿主 composition 显式请求时才会被装载；release 包**不得**在 `dependencies` 中引用它。

## 读取哪些文件

`dragon-assets/` 镜像包含天龙引擎 `scripts/build-index.py` 生成的五个 jsonl 文件：

| 文件 | 资产数 | 示例 |
|---|---|---|
| `SKILLS.jsonl` | 784 | async-task-pattern, cinema-director-laoli, a-stock-data-bridge |
| `AGENTS.jsonl` | 187 | 00-analyst, 35-06-blogger-distiller, 28-10-finance-data-base |
| `HOOKS.jsonl` | 90 | session-start, preToolUse guard, postToolUse |
| `COMMANDS.jsonl` | 156 | /check, /review, /commit-push-pr |
| `PLUGINS.jsonl` | 7 | code-review, feature-dev, hookify |

本包并发读取所有五个文件，冻结快照后提供查询接口。索引由天龙上游刷新；本包**只读不写**。

## 配置

| 字段 | 默认值 | 含义 |
|---|---|---|
| `dragonAssetsRoot` | `<workspace>/dragon-assets`（或环境变量 `$DRAGON_ASSETS_ROOT`）| 镜像文件系统根 |

## Service API

```ts
import DragonAssetIndex from '@deepseek-ai/dsh-experimental-skill-index'

const fiber = await ctx.plugin(DragonAssetIndex, { dragonAssetsRoot: '...' })

const snapshot = await ctx.dragonIndex.loadAll()
const matches = ctx.dragonIndex.search({ kind: 'skill', text: 'blogger', limit: 5 })
const skill = ctx.dragonIndex.get('async-task-pattern', 'skill')
```

`loadAll()` 幂等，上游重新生成后可重复调用。`search()` 与 `get()` 操作内存中的快照，不读磁盘。快照对象已被深冻结，调用方需先克隆再修改。

## 模型体验

### 模型能看到什么

**无任何内容**——本 Service 是 DSH 内部组件，永远不会直接暴露给模型。调用方可以通过自己的工具选择性地把搜索结果暴露给模型；本包仅负责读路径。

### Token 影响

无。

### KV Cache 影响

无。

## 已知限制与延后工作

- **不在上游重建索引**——本包只读 `dragon-assets/index/*.jsonl`，刷新需天龙维护者手动跑 `build-index.py`。
- **无 schema migration**——服务接受 jsonl 中的所有字段；未来新增字段以 `unknown` 类型暴露，直到添加强类型访问器。
- **无模型可见工具**——本包只交付 Service Definition。把它与暴露 `search()` 的 `tool-dragon-search` Cordis 包配对是未来决策。
- **同步 JSON.parse 循环**——服务一次性解析整个索引。几千条资产内可接受；如索引超过 ~50k 条资产需考虑流式解析。
- **无 CJK 路径校验**——服务原样返回路径。Windows 上的调用方在传入 `fs` 前必须自行校验。
- **AGPL-3.0 与 MIT 资产共存**——调用方在执行任何 AGPL 标签资产前必须按 `license` 过滤（详见计划中的 `dsh-experimental-license-policy` 包）。
