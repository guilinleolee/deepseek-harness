---
name: stage-54-candidates-evaluation
description: Stage 54 候选盘点 · 8 候选 → 1 GO + 4 边界 GO + 3 NO-GO · 关注 graph-memory + Herdeny/awesome-dsh-plugins 生态
metadata:
  node_type: memory
  type: evaluation
  originSessionId: stage-54-candidates-20260826
  modified: 2026-08-26T21:50:00.000Z
---

# Stage 54 候选盘点 · 2026-08-26

> **盘点日期**：2026-08-26
> **盘点类型**：cycle-style · 与 stage 47/49/50/51/53 节奏一致 · D1 协议评估 + D2 撞墙 + D3 借鉴/拒绝
> **依据**：[`docs/dsh-ecosystem-license-policy.md`](../docs/dsh-ecosystem-license-policy.md) 6 条基线
> **结论**：共盘点 **8 个新候选**（stage 53 之后）→ **1 GO + 4 边界 GO + 3 NO-GO**。累计 PASS **967 锁定**（盘点本身 0 PASS）。

---

## 一、本盘点候选清单（8 个 · GitHub REST API 实拉 · 4 个查询）

### 1.1 查询 1 · topic:ai-agents+language:python（800+ repos · top 5）

| # | 仓库 | ★ | 协议 | 决定 | 备注 |
|---|---|---|---|---|---|
| 1 | DataTalksClub/ai-dev-tools-zoomcamp | 1,430 | n/a | 🔴 **NO-GO**（教学仓库，非 DSH 生态）| 2026-08-31 cohort |
| 2 | razzant/ouroboros | 1,229 | n/a | 🔴 **NO-GO**（**自创建 agent** · 与 stage 47 univer 多 Unit 范式重叠）| Born Feb 16, 2026 |
| 3 | zjunlp/LightMem | 1,097 | MIT | 🟡 **边界 GO**（"Lightweight Memory-Augmented Generation" · ICLR 2026 · 与 stage 41 mneme-heat-engine 互补）| 待 D1+D2 |
| 4 | Human-Agent-Society/CORAL | 926 | n/a | 🟡 **边界 GO**（"autoresearch + multi-agent evolution" · 与 stage 43 dsh-agent-teams 协同）| COLM 2026 |
| 5 | karanb192/itr-wala | 725 | n/a | 🔴 **NO-GO**（印度税务工具 · 非 DSH 生态）| — |

### 1.2 查询 2 · deepseek-harness+topic:coding-agent（20+ repos · top 3）

| # | 仓库 | ★ | 协议 | 决定 | 备注 |
|---|---|---|---|---|---|
| 6 | **adoresever/graph-memory** | **576** | MIT | 🟢 **GO 候选** | "**Deepseek Harness、Openclaw 知识图谱记忆插件。2026 年 4 月受邀发布在清华大学讨论会**。Knowledge Graph Context Engine for OpenClaw — extracts structured triples from conversations, compresses context 75%, enables cross-session experience reuse" |
| 7 | Herdeny/awesome-dsh-plugins-2026 | 7 | CC0 | 🟡 **边界 GO**（"Curated list of DSH plugins for 2026, with quality check" · 治理类 · 类似 stage 50.3 0xsline/awesome）| 2 forks |

### 1.3 查询 3 · deepseek-harness+topic:cordis（5 repos · 1 个新候选）

| # | 仓库 | ★ | 协议 | 决定 | 备注 |
|---|---|---|---|---|---|
| 8 | ZHIZHU4410/deepseek-balance | 0 | 待查 | 🟡 **边界 GO**（"DeepSeek 余额监控插件：官方余额 API + 峰谷配色（2026-08-23 起周末全天低谷价）+ 30s 自动刷新" · 与 stage 45.1 dsh-balance-meter 高度重叠）| 重复项 |

---

## 二、1 GO 候选（Stage 55 主目标）

### 2.1 adoresever/graph-memory 🟢 **GO 候选**（**576⭐ · MIT · 知识图谱记忆引擎**）

| 字段 | 值 |
|---|---|
| **上游** | https://github.com/adoresever/graph-memory |
| **作者** | adoresever（GitHub ID）|
| **最近更新** | 2026-08-26（**活跃** · 受邀发布清华大学讨论会 2026-04）|
| **协议** | **MIT ✅**（GitHub API `license.spdx_id: mit`）|
| **★ / 🍴** | **576⭐ / 82 🍴**（中型生态）|
| **language** | TypeScript |
| **topics** | ai-agents / deepseek-harness / openclaw / knowledge-graph / memory |
| **核心能力** | "Knowledge Graph Context Engine for OpenClaw — extracts structured triples from conversations, compresses context 75%, enables cross-session experience reuse" |
| **意义** | **天龙 stage 41 mneme-heat-engine 升级路线 · 75% context 压缩 + 跨 session 经验复用 · 与 dsh-agent-teams captain 协同** |

### 2.2 借鉴档策略（与 stage 41/45/46/48/49.x/50.x/52 同模式）

- **不镜像真源**（避免 TypeScript monorepo 复杂度）
- **借鉴清单**：
  1. **Triple 抽取器**（结构化提取对话三元组：实体-关系-实体）
  2. **上下文压缩器**（按图谱节点重要性排序，压缩 75%）
  3. **跨 session 经验复用**（基于图谱 hash 匹配）
  4. **DSH 集成模式**（通过 skill 注入到 OpenClaw runtime）

---

## 三、4 边界 GO + 3 NO-GO 详情

### 3.1 边界 GO（4 个 · 待 D1+D2 详尽评估）

| # | 仓库 | 待评估项 | 协同方向 |
|---|---|---|---|
| 3 | zjunlp/LightMem | D1 协议（MIT ✅ 待查完整）· D2 集成路径（ICLR 2026，论文导向） | 与 stage 41 mneme-heat-engine 互补（一个是 heat 衰减，一个是图谱压缩）|
| 4 | Human-Agent-Society/CORAL | D1 协议 · D2 多 agent runtime 集成 | 与 stage 43 dsh-agent-teams captain 协同 |
| 7 | Herdeny/awesome-dsh-plugins-2026 | D1 协议（CC0 ✅）· D2 治理类维护档（类似 stage 50.3 0xsline） | 候选清单维护 |
| 8 | ZHIZHU4410/deepseek-balance | D1 协议 · D2 与 stage 45.1 dsh-balance-meter-bridge 协同 | 余额监控 |

### 3.2 NO-GO 红牌（3 个）

| # | 仓库 | NO-GO 原因 |
|---|---|---|
| 1 | DataTalksClub/ai-dev-tools-zoomcamp | 教学仓库 · **非 DSH 生态** · 与 stage 17 Apache 模板无关 |
| 2 | razzant/ouroboros | 自创建 agent · **与 stage 47 univer 多 Unit 范式重叠** · 不增量 |
| 5 | karanb192/itr-wala | 印度税务工具 · **非 DSH 生态** · 垂直领域工具 |

---

## 四、Stage 55 启动建议

### 4.1 推荐路径

```bash
# 借鉴档（4 周节奏）
Stage 55.1 · adoresever/graph-memory 借鉴档
  ├─ W1: triple_extractor.py（实体-关系抽取）
  ├─ W2: graph_compressor.py（context 压缩 75%）
  ├─ W3: cross_session_reuse.py（跨 session 经验匹配）
  └─ W4: 端到端 + 6 PASS pytest
```

### 4.2 预期收益

- **累计 PASS +8**：triple 抽取 + 图谱压缩 + 跨 session 匹配 + 端到端 + 兼容性
- **协同 stage 41 mneme-heat-engine**：从 heat 衰减模型升级为图谱持久化记忆
- **协同 stage 43 dsh-agent-teams**：captain 用 graph-memory 上下文压缩做决策

### 4.3 风险

| 风险 | 缓解 |
|---|---|
| 上游 TypeScript monorepo 复杂度 | 借鉴档模式（仅借鉴设计精神，不嵌入源码）|
| ICLR 2026 论文复现 | 已有开源 reference code · 直接借鉴 |
| context 75% 压缩语义损失 | 借鉴后天龙需自建质量评估（task-specific）|

---

## 五、本盘点不新增 PASS

按 stage 47/49/50/51/53 节奏：盘点本身 0 PASS（治理类）。

**累计 PASS 967 锁定**（维持）。

---

## 六、来源链接

- 上游 graph-memory：https://github.com/adoresever/graph-memory
- 上游 LightMem：https://github.com/zjunlp/LightMem
- 上游 CORAL：https://github.com/Human-Agent-Society/CORAL
- 上游 awesome-dsh-plugins：https://github.com/Herdeny/awesome-dsh-plugins-2026
- DSH 协议治理基线：`docs/dsh-ecosystem-license-policy.md`
