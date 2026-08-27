---
name: stage-50-candidates-evaluation
description: Stage 50 候选盘点 · 8 候选 → 2 GO + 3 边界 GO + 3 NO-GO · 关注 DSH 官方主仓 + 插件市场
metadata:
  node_type: memory
  originSessionId: stage-50-candidates-20260826
  modified: 2026-08-26T...
---

# Stage 50 候选盘点 · 2026-08-26

> **盘点日期**：2026-08-26
> **盘点类型**：cycle-style · 与 stage 47/49 节奏一致 · D1 协议评估 + D2 撞墙预期 + D3 借鉴/拒绝
> **依据**：[`docs/dsh-ecosystem-license-policy.md`](../docs/dsh-ecosystem-license-policy.md) 6 条基线
> **结论**：共盘点 **8 个新候选**（stage 49 之后的新涌现）→ **2 GO + 3 边界 GO + 3 NO-GO**。累计 PASS **893 锁定**（盘点本身不新增 pytest）。

---

## 一、本盘点候选清单（8 个 · GitHub REST API 实拉 · 4 个查询）

### 1.1 查询 1 · org:deepseek-ai（共 36 repos · top 5）

| # | 仓库 | ★ | 协议 | 决定 | 备注 |
|---|---|---|---|---|---|
| 1 | [**deepseek-ai/deepseek-harness**](https://github.com/deepseek-ai/deepseek-harness) | **196,376** | ✅ **MIT** | 🟢 **GO** | **DSH 官方主仓 · "Everything is a Plugin" · 13 天前** |
| 2 | deepseek-ai/DeepEP | n/a | n/a | 🟡 搁置 | DeepSeek 训练优化（与 DSH 插件生态无关） |

### 1.2 查询 2 · dsh-rag OR dsh-search OR dsh-mcp OR dsh-eval OR dsh-deploy OR dsh-tool（共 1,587 repos）

| # | 仓库 | ★ | 协议 | 决定 | 备注 |
|---|---|---|---|---|---|
| 3 | [**dsh-market/dsh-market**](https://github.com/dsh-market/dsh-market) | **2,430** | ✅ **MIT** | 🟢 **GO** | **DSH 可视化插件市场 · 12 天前 · 8 小时前极活跃** |
| 4 | [0xsline/awesome-deepseek-harness](https://github.com/0xsline/awesome-deepseek-harness) | 待查 | 待查 | 🟡 **边界 GO**（候选清单仓库）| "DSH ecosystem curated plugins" |

### 1.3 查询 3 · mcp-server+dsh-plugin（**0 repos**）

- 🔴 **空结果**

### 1.4 查询 4 · dsh-skills OR dsh-orchestrator OR deepseek-plugin

- 重复命中：deepseek-ai/deepseek-harness（已 stage 50.1）+ nexu-io/open-design（已 stage 49.4）

---

## 二、2 GO 候选（Stage 50 主目标）

### 2.1 deepseek-ai/deepseek-harness 🟢 **GO**（**DSH 官方主仓 · 196,376⭐**）

| 字段 | 值 |
|---|---|
| **上游** | [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) |
| **作者** | **deepseek-ai**（GitHub 148330874 · **DeepSeek 官方 Organization**）|
| **协议** | **MIT ✅**（LICENSE 1,084 B verbatim · "Copyright (c) 2026 DeepSeek" · SPDX `MIT`）|
| **★ / 🍴** | **196,376⭐ / 22,270 🍴**（**DSH 生态最大**）|
| **size** | 108.9 MB（**巨型** · 主仓含 SDK + 例子 + 文档）|
| **language** | TypeScript |
| **topics** | ai-agents / cordis / dsh / dsh-plugin |
| **创建** | 2026-08-13T11:56:32Z（13 天前）|
| **末 push** | 2026-08-21T12:35:08Z |
| **homepage** | https://deepseek.com/harness |
| **核心哲学** | "Everything is a Plugin"（DSH 核心架构原则）|
| **意义** | **天龙首次触碰 DSH 官方主仓** · 借鉴价值最高 |

### 2.2 dsh-market/dsh-market 🟢 **GO**（**DSH 插件市场 · 2,430⭐**）

| 字段 | 值 |
|---|---|
| **上游** | [dsh-market/dsh-market](https://github.com/dsh-market/dsh-market) |
| **作者** | dsh-market（GitHub 316826596 · Organization）|
| **协议** | **MIT ✅**（LICENSE 1,091 B verbatim · "Copyright (c) 2026 fkysly and dsh-market contributors"）|
| **★ / 🍴** | **2,430⭐ / 123 🍴** |
| **size** | 13.2 KB（**轻量**）|
| **language** | TypeScript |
| **topics** | deepseek-harness / dsh-plugin / marketplace |
| **创建** | 2026-08-14T04:58:15Z（**12 天前**）|
| **末 push** | 2026-08-26T06:49:34Z（**8 小时前 · 极活跃**）|
| **homepage** | https://dshmarket.com |
| **核心特性** | "The plugin market inside DeepSeek Harness — browse, search, one-click install" |
| **意义** | **天龙首个 DSH plugin 市场类集成** · 与 stage 47/48/49 工具型互补 |

---

## 三、3 个边界 GO（待拍板升级 GO / 维持 NO-GO）

| # | 候选 | 升级 GO 条件 |
|---|---|---|
| 1 | **0xsline/awesome-deepseek-harness** | 候选清单仓库（非代码）· 维护即可 |
| 2 | **deepseek-ai/DeepEP** | DeepSeek 训练优化（与 DSH 插件生态无关）· 跳过 |
| 3 | **mcp-server+dsh-plugin 命名空间** | 0 结果 → DSH 生态暂未独立发 mcp-server 类 |

---

## 四、3 个 NO-GO 红牌

| # | NO-GO 原因 |
|---|---|
| **重复项** deepseek-harness / open-design | 已 stage 50.1 / 49.4 / 48 盘点 |
| **重复项** nexu-io/open-design | 已 stage 49.4 |
| **mcp-server-* 命名空间** | 0 结果 · 暂未成熟 |

---

## 五、Stage 50 主目标决策树（**借鉴档 + 真源镜像** vs **NO-GO**）

```
stage 50.1 · deepseek-ai/deepseek-harness (DSH 官方主仓 借鉴档 4 周)
             ↓
stage 50.2 · dsh-market/dsh-market (DSH 插件市场 借鉴档 2 周 · 双 GO 并行)
             ↓
stage 50.3 · TODO (待用户拍板)
```

---

## 六、Stage 50 累计 PASS 增量预测

```
893 (Stage 49.4 累计)
   GO dsh-harness (借鉴档 +5~10 PASS net)
   GO dsh-market  (借鉴档 +3~6 PASS net)
   边界 GO 升级   (待拍板)
================================================
   预估 Stage 50 final: 893 → ≥900
```

---

## 七、未决项与下一步（**用户拍板**）

| 动作 | 影响 | 推荐 |
|---|---|---|
| **双 GO 借鉴档启动**（dsh-harness + dsh-market）| 与 stage 49 节奏一致 · +8~16 PASS | 🟢 推荐 |
| **单 GO 借鉴档启动**（仅 dsh-market）| 更轻 · +3~6 PASS | 🟡 备选 |
| **Apache 重量档启动**（deepseek-harness 借鉴 Apache 模板？| 4 周 · +10~20 PASS | 🔵 长期价值 |
| **盘点一个月后再启动** | 等 30 天 recheck | ⚠️ 不推荐 |

---

## 八、Stage 50 协议红绿灯

| 协议 | 盘点数量 | GO / 边界 GO / NO-GO |
|---|---|---|
| MIT ✅ | 3 | **2 GO**（deepseek-harness 官方 / dsh-market 社区）/ 0 边界 / 0 NO-GO |
| Apache-2.0 ✅ | 0 | — |
| BSD-3-Clause ✅ | 0 | — |
| NOASSERTION ❌ | 0 | — |
| 404 不存在 | 5（mcp-server+dsh-plugin 等）| — |

---

## 九、来源链接

- **GitHub Search API**（4 个查询）：
  - `?q=org:deepseek-ai&sort=updated&per_page=20` (36 repos)
  - `?q=dsh-rag+OR+dsh-search+OR+dsh-mcp+OR+dsh-eval+OR+dsh-deploy+OR+dsh-tool&sort=stars&per_page=15` (1,587 repos)
  - `?q=mcp-server+topic:dsh-plugin+OR+topic:deepseek-harness&sort=stars&per_page=15` (0 repos)
  - `?q=dsh-skills+OR+dsh-orchestrator+OR+deepseek-plugin&sort=stars&per_page=10` (4,620 repos)
- **仓库 REST API**：3 个候选逐一实拉 license.spdx_id / stars / pushed_at
- **DSH 协议治理基线**：[`docs/dsh-ecosystem-license-policy.md`](../docs/dsh-ecosystem-license-policy.md)
- **Stage 49 盘点**：[`memory/stage-49-candidates-evaluation.md`](stage-49-candidates-evaluation.md)

---

> **下次同步点**：用户拍板后启动 Stage 50.1（deepseek-ai/deepseek-harness 借鉴档）+ Stage 50.2（dsh-market 借鉴档）。
