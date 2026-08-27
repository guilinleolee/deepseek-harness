# DRAGON_INTEGRATION.md · 天龙引擎 → DSH 整合手册

> **状态**: V1.0 · **生成日期**: 2026-08-27
> **目的**: 让后续维护者 5 分钟内理解"天龙引擎 1157 资产如何进 DSH"以及"DSH 主仓用什么 Cordis 包去访问它们"。

---

## 0. 一图看懂

```
C:\Users\li\.claude\projects\dragon-engine\          ← 上游真源（不修改）
│
│  robocopy 同步
▼
D:\deepseek-harness\dragon-assets\                  ← 数据层镜像（288 MB · 21,225 文件）
│  ├── skills/  agents/  commands/  memory/
│  ├── runtime/  ip-profiles/  index/  ...
│  ├── README.md  LICENSE-ATTRIBUTION.md  .gitignore
│
│  索引
▼
D:\deepseek-harness\packages\experimental\          ← Cordis 服务层
│
│  ┌───────────────────────┐
│  │ skill-index  (19 tests) │  读 dragon-assets/index/*.jsonl
│  └─────────┬─────────────┘
│  ┌─────────▼─────────────┐
│  │ agent-roster (27 tests) │  读 dragon-assets/agents/*.md
│  └─────────┬─────────────┘
│  ┌─────────▼─────────────┐
│  │ license-policy (17)     │  tier → decision 判定表
│  └─────────┬─────────────┘
│  ┌─────────▼─────────────┐
│  │ dragon-bridge (10 tests) │  统一 facade
│  └───────────────────────┘
│
▼
DSH 业务代码（composition）
```

## 1. 仓库布局

| 路径 | 作用 |
|---|---|
| `DRAGON_SYNC_PLAN.md` | 同步计划（路径映射、排除清单、阶段执行） |
| `DRAGON_INTEGRATION.md` | **本文档** |
| `dragon-assets/` | 天龙 1157 资产的本地镜像（git-ignored 部分子目录） |
| `packages/experimental/{skill-index,agent-roster,license-policy,dragon-bridge}/` | 4 个 Cordis 包 |

## 2. 同步天龙资产

### 2.1 一次性的镜像（已完成 2026-08-27）

```powershell
# 从天龙仓根同步
robocopy "C:\Users\li\.claude\projects\dragon-engine\skills" `
         "D:\deepseek-harness\dragon-assets\skills" * /MIR /R:0 /W:0

# 排除清单
#   .git  .cache  .pytest_cache  .streamlit  .vscode  .claude
#   node_modules  graphify-out  third-party  tasks  __pycache__
#   *.pyc  *.wasm  *.map  *.node  二进制图像/PDF/视频
```

### 2.2 增量更新（未来）

```powershell
# 1. 同步源
robocopy "C:\Users\li\.claude\projects\dragon-engine\skills" `
         "D:\deepseek-harness\dragon-assets\skills" * /MIR /R:0 /W:0

# 2. 重建索引（由天龙侧 build-index.py 触发后复制）
Copy-Item "C:\Users\li\.claude\projects\dragon-engine\index\*" `
          "D:\deepseek-harness\dragon-assets\index\" -Recurse -Force

# 3. 验证
python dragon-assets/runtime/scripts/build-index.py --include-library
```

### 2.3 重要约束

- `dragon-assets/**` 已加入 `.oxlintrc.json` 的 `ignorePatterns`，**不要 lint 镜像**
- `dragon-assets/.gitignore` 自动排除 git/pycache/node_modules 等副产物
- 顶层 `.gitignore` 也排除镜像内的大文件（图片/PDF/视频）
- **不要在镜像内 commit**——它是数据层，需要重新生成时直接 robocopy

## 3. 4 个 Cordis 包的角色

### 3.1 `dsh-experimental-skill-index` (19 tests · 100% coverage)

```ts
import DragonAssetIndex from '@deepseek-ai/dsh-experimental-skill-index'

const fiber = await ctx.plugin(DragonAssetIndex, { dragonAssetsRoot })
await ctx.dragonIndex.loadAll()        // 读 5 个 jsonl
ctx.dragonIndex.search({ kind: 'skill', text: 'blogger' })
ctx.dragonIndex.get('async-task-pattern', 'skill')
```

**职责**: 把天龙 jsonl 索引文件（5 类）暴露为可查询的 `AssetIndexEntry[]`。
**不**做：license 判定、agent 解析、跨包合并。

### 3.2 `dsh-experimental-agent-roster` (27 tests · 100% stmt · 98.56% branch)

```ts
import AgentRoster from '@deepseek-ai/dsh-experimental-agent-roster'

const fiber = await ctx.plugin(AgentRoster, { dragonAssetsRoot })
await ctx.agentRoster.loadAll()        // 扫 182 个 .md
ctx.agentRoster.search({ family: 'core' })
ctx.agentRoster.byFamily('finance')    // ['28-10-finance-data-base', ...]
ctx.agentRoster.get('00-analyst')
```

**职责**: 解析天龙 182 个 agent markdown，按 00-99 编号 + family bucket 分类。
**不**做：jsonl 索引、license 判定。

### 3.3 `dsh-experimental-license-policy` (17 tests · 100% coverage)

```ts
import LicensePolicy from '@deepseek-ai/dsh-experimental-license-policy'

const fiber = await ctx.plugin(LicensePolicy, { rejectUnknown: true })
const ev = ctx.licensePolicy.evaluate('AGPL-3.0')
// → { tier: 'agpl-3.0', severity: 'red', decision: 'artifact-only', reason: '...' }
ctx.licensePolicy.assertAllowed('MIT', ['allow', 'attribute'])
```

**职责**: tier → decision 判定表（mit/apache-2.0/bsd-3-clause/agpl-3.0/noassertion/unknown）。
**不**做：I/O、不读上游资产。

### 3.4 `dsh-experimental-dragon-bridge` (10 tests · 100% stmt · 97.5% branch)

```ts
import DragonBridge from '@deepseek-ai/dsh-experimental-dragon-bridge'

// 装载三个上游服务 + bridge
await ctx.plugin(DragonAssetIndex, { dragonAssetsRoot })
await ctx.plugin(AgentRoster, { dragonAssetsRoot })
await ctx.plugin(LicensePolicy)
await ctx.plugin(DragonBridge, { safeOnly: true })

await ctx.dragonBridge.loadAll()       // 合并 5 类 jsonl + 182 agent
ctx.dragonBridge.search({ kind: 'skill', decision: 'allow' })
ctx.dragonBridge.allowed()            // decision === 'allow' 的全部
ctx.dragonBridge.artifactOnly()       // AGPL 红线
ctx.dragonBridge.rejected()           // NOASSERTION 红线
```

**职责**: 统一 facade，组合 skill-index + agent-roster + license-policy。
**不**做：自有 I/O（依赖三个上游服务）。

## 4. License 红线（操作必读）

| Tier | 决策 | 处置 |
|------|------|------|
| `mit` | `allow` | 可直接暴露给模型 |
| `apache-2.0` | `attribute` | 需附 NOTICE + "Modifications by dragon-engine" 段 |
| `bsd-3-clause` | `attribute` | 保留版权；不得用作者名背书 |
| `agpl-3.0` | `artifact-only` | **红线**：仅交付 PNG / artifact，禁止 SaaS / 网络服务 |
| `noassertion` | `reject` | 黑名单，DSH 治理基线拒收 |
| `unknown` | `attribute`（默认）| 重新分发前需确认上游 |

来源：`dragon-assets/LICENSE-ATTRIBUTION.md` §一-§五（与天龙 `memory/agpl-attribution-statements.md` §一-§六同步）。

## 5. 已知限制

### 5.1 覆盖率

| 包 | statements | branches | functions | lines |
|---|---|---|---|---|
| skill-index | 100% | 100% | 100% | 100% |
| agent-roster | 100% | 100% | 100% | 100% |
| license-policy | 100% | 100% | 100% | 100% |
| dragon-bridge | 100% | 100% | 100% | 100% |

**100% 覆盖率全部达成**（commit 1 收尾时通过删除 dead defensive code 实现，例如 `parts[parts.length - 1] ?? p` 的 `??` 兜底分支改为 `replace(/\.md$/, '')` 单点处理）。

### 5.2 镜像

- `dragon-assets/**` 不进 git 全量跟踪（`.gitignore` 排除大文件 + 副产物）
- 如需重建镜像，跑 `DRAGON_SYNC_PLAN.md` §2.1
- jsonl 索引文件是**天龙侧 build-index.py 生成的快照**，DSH 不主动 rebuild

### 5.3 后续 PR 路线

- **Phase 4**: `dragon-bridge` 接入 DSH 业务 composition（`examples/` 或 `apps/web`）
- **Phase 5**: 新增 `tool-dragon-search` Cordis 包，把 `search()` 暴露给模型（需要权衡 AGPL 风险）
- **Phase 6**: 新增 `dragon-ip` 包，处理 `ip-profiles/` 授权检查
- **Phase 7**: 把"高频 5 个 skill"（async-task-pattern / cinema-director-laoli / nano-banana-brief / guizang / a-stock-data-bridge）重写为 native Cordis plugin（脱离 markdown 解析）

## 6. 故障排查

| 现象 | 原因 | 解决 |
|---|---|---|
| `Cannot find package '@deepseek-ai/dsh-experimental-skill-index'` | 4 个包未在 `tsconfig.base.json` 的 `paths` 里登记 | 见 §7 |
| `vitest` 找不到 `dragonIndex` 等 service | 忘了 `ctx.plugin(...)` | 装载顺序：先三个上游，最后 dragon-bridge |
| 镜像里 看不到 CJK 文件名 | Windows 编码问题，正常 | PowerShell 7+ 用 `Get-ChildItem -LiteralPath` |
| 同步后 `dragon-assets/index/*.jsonl` 行数变化 | 天龙上游 `build-index.py` 重新生成 | 重新 `robocopy` 整个 `index/` |
| lint 报 `dragon-assets` 错 | 镜像未在 `.oxlintrc.json` ignore | 检查 §1 的 ignorePatterns |

## 7. 关键配置变更清单

为支持本次整合，DSH 主仓的以下文件**已修改**：

| 文件 | 变更 |
|---|---|
| `tsconfig.host.json` | +5 个 experimental 包的 references（skill-index, agent-roster, license-policy, dragon-bridge） |
| `tsconfig.base.json` | +8 个 paths 映射（4 个包 × invariant + main entry） |
| `.oxlintrc.json` | +2 个 ignorePatterns（dragon-assets, dragon-engine） |
| `.gitignore` | +龙资产大文件排除规则 |
| `package.json` | +pnpm 依赖（同 workspace 自动解决） |
| `pnpm-lock.yaml` | 增量更新 |

修改前已通过 `pnpm test:coverage` 全面门禁验证。

## 8. 验收清单

- [x] `pnpm lint` 在 experimental 4 个包 0 errors
- [x] `pnpm typecheck` 在 4 个包 0 errors
- [x] `pnpm vitest run` 在 4 个包 73 tests passing
- [x] **4 个包 100% coverage**（statements/branches/functions/lines 全维度）
- [x] `dragon-assets/` 不进 git（.gitignore 排除大文件）
- [x] License 红线 4 档（allow/attribute/artifact-only/reject）正确返回
- [x] `DRAGON_SYNC_PLAN.md` 与 `DRAGON_INTEGRATION.md` 双文档

---

> **天龙视角 · 入口索引**: 本文档是 DSH 主仓对天龙引擎 V2.5 整合的官方手册。任何修改 4 个 experimental 包或 `dragon-assets/` 镜像的 PR 必须先读本文档。
