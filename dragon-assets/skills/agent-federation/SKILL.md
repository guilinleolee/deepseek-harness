---
license: MIT
name: agent-federation
version: 2.0.0
description: |
  Agent 联邦协作 V2。覆盖两层：Level 0 跨机器分布式联邦（V1 遗留，Raft 共识 + 故障转移）+ Level 1 Team-of-Teams 联邦（V2 新增，基于 DSH AgentTeams plugin 的 task-driven cross-team coordination）。
author: 天龙引擎团队
created: 2026-05-08
updated: 2026-08-13
runtime: dsh-agent-teams >= 0.1.13 (Level 1 only)
references:
  level_0_upstream: ruflo agent federation
  level_1_target: NanmiCoder/dsh-agent-teams

triggers:
  - "agent federation"
  - "Agent联邦协作技能包"
  - "跨 team 联邦"
---

# Agent 联邦协作技能包

> **版本说明**：
> - **V2（2026-08-13，当前）**：双层联邦。
>   - **Level 0**（V1 遗留）：跨机器分布式联邦（Raft + 故障转移 + 负载均衡）
>   - **Level 1**（V2 新增）：Team-of-Teams 联邦（DSH AgentTeams plugin 演进路线）
> - **V1（2026-05-08）**：仅 Level 0 跨机器联邦。

---

# V2 Level 1 · Team-of-Teams 联邦（DSH AgentTeams plugin）

> **本节是 V2 全新内容**：DSH AgentTeams plugin 0.1.13 不直接支持跨 team 协调。本节定义 **task-driven cross-team coordination** 的天龙规范与未来路线。

## V2 L1 §1. 核心场景

| 场景 | 描述 | 触发条件 |
|---|---|---|
| **Pipeline Federation** | Team A 的最后 task 完成 → 启动 Team B 的第一个 task | A 完成 → B 启动 |
| **Broadcast Federation** | Team A 的某 task 输出广播给 N 个下游 team | A 完成 → B1, B2, ..., BN 启动 |
| **Gather Federation** | 多个 team 并行跑，captain 等待全部完成再聚合 | N 个 team 全部完成 → 聚合 |
| **Saga Federation** | Team A 失败 → 触发 Team B 补偿（rollback） | A 失败 → B 启动 |

## V2 L1 §2. Pipeline Federation（最常见）

```
Team A (research)               Team B (build)
   T1: 竞品调研 ✅                  T1': API 设计
       ↓                              ↓
   T2: 综合报告 ✅ ──trigger──→    T2': API 实现
                                  T3': 部署
```

**当前 DSH plugin 0.1.13 实现方式**（v1.0 兼容层）：

```typescript
// Team A：执行完所有 task
agent_teams_create({ name: 'team-a-research' })
// ... 注册 members / 入队 tasks ...
// ... 所有 task completed ...

// captain 显式启动 Team B（联邦边界）
agent_teams_create({ name: 'team-b-build' })
agent_teams_add_member({ name: 'architect', template: 'agents/02-architect.md' })
// ...
```

**captain 代码逻辑**（在 captain prompt 里实现）：

```typescript
// captain 在 Team A 最后一个 task update_task({ status: 'completed' }) 后
const teamAStatus = agent_teams_status({ team: 'team-a-research' })
if (teamAStatus.allCompleted) {
  // 触发 Team B
  agent_teams_create({ name: 'team-b-build', description: `Pipeline from team-a` })
  // ... 注册 B 的 members + tasks ...
}
```

**未来 V2.1 路线**（plugin 原生支持）：

```typescript
// 假想 API（plugin 0.2+ 提案）
agent_teams_create({
  name: 'team-b-build',
  federation: {
    trigger: { team: 'team-a-research', task: 'T2-comprehensive-report', status: 'completed' },
    mode: 'pipeline',
  },
})
```

## V2 L1 §3. Broadcast Federation（扇出）

```typescript
// 假想 API（plugin 0.2+ 提案）
agent_teams_create({
  name: 'team-b1-translation',
  federation: {
    trigger: { team: 'team-a-research', task: 'T2-final-report', status: 'completed' },
    mode: 'broadcast',
    fanout: ['team-b2-summary', 'team-b3-visual'],
  },
})
```

## V2 L1 §4. Gather Federation（聚合）

```typescript
// captain 等所有 team 完成
const teams = ['team-a-research', 'team-a-competitor', 'team-a-user']
const allDone = teams.every(t => agent_teams_status({ team: t }).allCompleted)
if (allDone) {
  // captain 综合产出
  const outputs = teams.map(t => agent_teams_status({ team: t }).outputs)
  // ... 综合 ...
}
```

## V2 L1 §5. Saga Federation（补偿）

```typescript
// captain 监控失败
if (agent_teams_status({ team: 'team-a-build' }).hasFailed) {
  // 触发补偿 team
  agent_teams_create({
    name: 'team-rollback',
    federation: { trigger: { team: 'team-a-build' }, mode: 'saga' },
  })
}
```

## V2 L1 §6. Level 1 vs Level 0

| 维度 | Level 0（V1）| Level 1（V2）|
|---|---|---|
| 调度单位 | 机器（Node A/B/C）| Team（captain 边界）|
| 拓扑 | 分布式集群 | Team-of-Teams DAG |
| 共识机制 | Raft / Paxos | task dependency（DSH plugin）|
| 故障转移 | 节点宕机 | task 失败 → captain 接管 |
| 实施复杂度 | 高（需自建集群）| 低（DSH plugin 自动）|
| 当前可用 | ✅ V1.0 已实现 | ⚠️ V1.0 兼容层 + V2.1 提案 |

---

# V1 Level 0 · 跨机器分布式联邦（legacy）

> **本节保留**：V1 是 2026-05-08 集成自 ruflo agent federation 的跨机器分布式联邦实现。当天龙引擎需要**多机部署**（如不同项目分布在不同机器）时仍可使用。

## L1: 使用场景

**适用场景**：跨机器任务分发、多Agent联邦协作、故障转移与恢复、负载均衡调度、联邦共识决策。

**触发关键词**：`联邦`、`跨机器`、`故障转移`、`负载均衡`、`联邦共识`、`Agent迁移`、`集群调度`、`多机协作`。

## L2: 详细文档

### 2.1 核心能力矩阵

| 能力 | 说明 | 命令 |
|------|------|------|
| **联邦注册** | Agent加入联邦、发现邻居节点 | `/federation-join` |
| **跨机器调度** | 任务分发至远程Agent执行 | `/federation-schedule` |
| **故障转移** | Agent宕机时自动迁移任务 | `/federation-failover` |
| **负载均衡** | 基于性能的智能任务分发 | `/federation-balance` |
| **联邦共识** | 多节点状态一致性决策 | `/federation-consensus` |
| **Agent迁移** | 有状态Agent在节点间迁移 | `/federation-migrate` |
| **集群监控** | 联邦状态实时监控面板 | `/federation-monitor` |

### 2.2 联邦架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent联邦架构                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐ │
│  │  Node A    │◄────►│  Node B    │◄────►│  Node C    │ │
│  │  (Leader)  │      │ (Follower) │      │ (Follower) │ │
│  │  :8080     │      │  :8081     │      │  :8082     │ │
│  └──────┬──────┘      └──────┬──────┘      └──────┬──────┘ │
│         │                       │                       │         │
│         └───────────────────────┼───────────────────────┘         │
│                                 │                                 │
│                    ┌────────────┴────────────┐                   │
│                    │     联邦共识层         │                   │
│                    │  (Raft/Gossip/Paxos)  │                   │
│                    │  状态同步/故障检测/选举  │                   │
│                    └───────────────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 联邦命令参考

```bash
# 节点管理
/federation-join --node "http://node-b:8081" --role "follower"
/federation-leave --node-id "node-uuid"
/federation-nodes --status all

# 任务调度
/federation-schedule --agent "research-agent" --task "调研报告" --target "node-c"
/federation-batch --tasks 10 --strategy "load-balance"
/federation-cancel --task-id "task-123"

# 故障转移
/federation-failover --node "node-b" --mode "automatic"
/federation-health --node "all" --threshold 0.7
/federation-recover --failed-node "node-b"

# 负载均衡
/federation-balance --strategy "cpu-aware" --rebalance-interval 30s
/federation-balance --strategy "capability-match" --task "code-review"
/federation-stats --node "node-a" --metrics "cpu,memory,tasks"

# 联邦共识
/federation-consensus --action "deploy" --value "v2.1.0" --quorum 3
/federation-consensus --action "abort" --task-id "task-456" --quorum 2

# Agent迁移
/federation-migrate --agent-id "agent-789" --from "node-a" --to "node-c"
/federation-migrate --checkpoint --agent-id "agent-789"
/federation-resume --agent-id "agent-789" --node "node-c"

# 监控
/federation-monitor --view "dashboard"
/federation-alert --condition "cpu>90" --action "rebalance"
```

### 2.4 与Swarm编排协同

```yaml
联邦 + Swarm 双层编排:
  联邦层 (Agent Federation):
    - 跨机器任务调度
    - 故障转移保证
    - 负载均衡
    - 联邦共识决策

  Swarm层 (Swarm Coordination):
    - 同一机器内多Agent协作
    - 冲突解决
    - 任务分派

  协同模式:
    Swarm(机内协作) → 联邦(跨机调度) → 结果聚合
```

### 2.5 故障转移流程

```
┌─────────────────────────────────────────────────────────────┐
│                    故障转移流程                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 健康检测                                               │
│     └── 心跳超时(>10s) → 标记为失联                       │
│                                                             │
│  2. 故障确认                                               │
│     └── 连续3次检测失败 → 确认故障                          │
│                                                             │
│  3. 任务迁移                                               │
│     └── 查找候补节点 → 迁移执行中任务 → 恢复状态           │
│                                                             │
│  4. 负载重平衡                                             │
│     └── 重新计算负载 → 均衡分发待处理任务                   │
│                                                             │
│  5. 故障恢复                                               │
│     └── 节点重新上线 → 同步状态 → 逐步接收新任务           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.6 负载均衡策略

| 策略 | 算法 | 适用场景 |
|------|------|---------|
| **Round Robin** | 轮询分发 | 节点性能相近 |
| **CPU-Aware** | CPU使用率加权 | 异构集群 |
| **Capability-Match** | 任务需求匹配Agent能力 | 专业任务分发 |
| **Least-Load** | 最少任务数优先 | 动态负载 |
| **Affinity** | 就近调度优先 | 状态共享任务 |

### 2.7 与天龙引擎协同

```yaml
天龙引擎协同:
  09-02编排协调师:
    - 联邦调度作为编排底层
    - Swarm + 联邦双层协同
    - 编排决策通过联邦共识执行

  ruflo Swarm:
    - 机内Swarm协作
    - 跨机Agent Federation
    - 统一的协调层

  09-01原型设计师:
    - 联邦拓扑可视化设计
    - 故障转移流程图
```

---

**Skill版本**: V1.0 → V2.0.0
**来源**: ruflo agent federation + 分布式Agent集群
**创建日期**: 2026-05-08
**更新日期**: 2026-08-13
**岗位**: 09-02 编排协调师
**天龙引擎版本**: V11.2

---

## 版本历史

| 版本 | 日期 | 变更 |
|---|---|---|
| V2.0.0 | 2026-08-13 | 新增 Level 1 Team-of-Teams 联邦（DSH AgentTeams plugin 演进路线）|
| V1.0.0 | 2026-05-08 | 初始版本（仅 Level 0 跨机器分布式联邦）|

## 参考资料

- **Level 1 runtime**：[NanmiCoder/dsh-agent-teams](https://github.com/NanmiCoder/dsh-agent-teams)
- **Level 0 上游**：ruflo agent federation
- **天龙集成报告**：`analysis/dsh-agent-teams-upgrade-analysis.md`
