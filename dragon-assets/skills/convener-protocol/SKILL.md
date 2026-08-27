---
license: MIT
name: convener-protocol
version: 1.1.0
description: |
  多 Agent 辩论协调协议 V1.1 "AgentTeams Native"。保留 V1.0 四步流程（SUMMON → COORDINATE → CONVERGE），底层调度从 prompt 模拟升级到 DSH AgentTeams plugin 运行时：SUMMON = add_member × N，COORDINATE = mailbox 轮次，CONVERGE = agent_teams_status 看终态。runtime: dsh-agent-teams >= 0.1.13。
author: 天龙引擎团队
created: 2026-04-18
updated: 2026-08-13
runtime: dsh-agent-teams >= 0.1.13
references:
  upstream: Professor Synapse Convener Mode
  runtime_target: NanmiCoder/dsh-agent-teams
  v1_legacy: convener-protocol V1.0 (2026-04-18)

triggers:
  - "convener protocol"
  - "Convener Protocol - 多Agent辩论协调协议"
---

# Convener Protocol - 多Agent辩论协调协议 V1.1

> **版本说明**：
> - **V1.1（2026-08-13，当前）**：V1.0 四步流程保留，底层调度从 prompt 模拟升级到 DSH AgentTeams plugin runtime。SUMMON/COORDINATE/CONVERGE 三个 phase 分别映射到 `add_member` / mailbox 轮次 / `agent_teams_status`。
> - **V1.0（2026-04-18，legacy）**：纯 prompt 编排，convener 在自己的上下文里模拟辩论。保留作 fallback。

---

# V1.1 · DSH AgentTeams Native

## V1.1 §1. Convener = DSH AgentTeams captain

Convener Protocol 的本质 = captain 启动一个辩论 team。V1.1 把这层关系显式化：

```typescript
// Convener 启动 = captain 启动
const team = agent_teams_create({
  name: `convener-${Date.now()}`,
  description: '<决策问题>',
})

// V1.0 SUMMON（召唤）= V1.1 add_member × N
agent_teams_add_member({ name: 'advocate-a', template: 'agents/02-architect.md' })
agent_teams_add_member({ name: 'advocate-b', template: 'agents/02-architect.md' })
agent_teams_add_member({ name: 'advocate-c', template: 'agents/05-security-reviewer.md' })
agent_teams_add_member({ name: 'referee', template: 'agents/07-scribe.md' })

// V1.0 COORDINATE（协调）= V1.1 mailbox 轮次 + create_task 阶段
// Round 1：开场立场
agent_teams_create_task({ subject: '立场 A 开场', owner: 'advocate-a' })
agent_teams_create_task({ subject: '立场 B 开场', owner: 'advocate-b' })
agent_teams_create_task({ subject: '立场 C 开场', owner: 'advocate-c' })
// Round 2：回应（依赖 T1 全部完成）
agent_teams_create_task({ subject: 'A 回应 B+C', owner: 'advocate-a', dependencies: ['T1-a', 'T1-b', 'T1-c'] })
agent_teams_create_task({ subject: 'B 回应 A+C', owner: 'advocate-b', dependencies: ['T2-a'] })
agent_teams_create_task({ subject: 'C 回应 A+B', owner: 'advocate-c', dependencies: ['T2-b'] })
// Round 3：referee 投票 + scribe 综合
agent_teams_create_task({ subject: '投票表决', owner: 'referee', dependencies: ['T2-c'] })
agent_teams_create_task({ subject: '综合决策报告', owner: 'scribe', dependencies: ['T3-vote'] })

// V1.0 CONVERGE（收敛）= V1.1 agent_teams_status
const status = agent_teams_status({ team: team.name })
// 等所有 task completed → captain 提取 scribe.task.output
```

## V1.1 §2. 决策矩阵 → task DAG

| 场景 | 参与 member | task 数 | DAG |
|---|---|---|---|
| **架构决策** | 2-3 architect + referee + scribe | 5-7 | T1立场×N → T2回应×N → T3投票 → T4综合 |
| **安全审查** | 2 security-reviewer + scribe | 4-6 | T1风险×N → T2对策 → T3投票 → T4综合 |
| **业务权衡** | analyst + 编排协调师 + scribe | 4-6 | T1数据×N → T2方案 → T3决策 → T4综合 |
| **发布决策** | publisher + validator + scribe | 4-5 | T1可行性×N → T2风险 → T3决策 → T4排期 |

## V1.1 §3. 决策质量检查 → task 后置 hook

V1.0 的"辩论质量检查"清单（5 个 ☑️）在 V1.1 由 captain 在所有 task completed 后做：

```typescript
const status = agent_teams_status({ team: team.name })
const reviewPacket = {
  eachPositionStated: status.tasks
    .filter(t => t.subject.includes('立场'))
    .every(t => t.output.length > 100),
  viewsClashed: /* LLM judge mailbox messages */,
  differencesRevealed: true,
  tradeoffFramework: true,
  noFalseConsensus: /* LLM judge */,
}
if (reviewPacket.score < 0.7) {
  agent_teams_create_task({ subject: '第二轮辩论', ... })
}
```

## V1.1 §4. 模板与仪式保留

V1.0 的 🎭 Convener Protocol 启动仪式、Agent 召唤格式（🧙🏾‍♂️）保留。V1.1 不替换仪式，**仪式在 member 的 prompt 里输出**，不影响 DSH runtime。

## V1.1 §5. V1.1 vs V1.0 关键差异

| 维度 | V1.0（prompt 模拟）| V1.1（DSH AgentTeams runtime）|
|---|---|---|
| 调度 | captain 在自己上下文里模拟 | 真 sub-agent 并行跑 |
| 任务依赖 | prompt 描述"先 X 后 Y" | 显式 `dependencies` DAG |
| 失败恢复 | 无 | runtime 自动 takeover |
| 通信 | LLM 脑内 | mailbox 持久化 |
| 状态可见 | 不可见 | activity panel |
| 仪式 🎭 | 保留 | 保留（仅在 member 输出）|
| API 一致性 | /convener 命令 | /agent-teams 命令（DSH plugin 自带）|

---

# V1.0 · Convener Protocol（legacy，prompt 编排）

## L0: 一句话描述
结构化多Agent辩论协议，用于复杂决策场景的权衡分析和综合洞察。

## L1: 使用场景

### 触发条件
当遇到以下场景时自动触发Convener Protocol：
- **架构决策**：技术选型、系统设计、架构演进
- **高风险决策**：成本>$1000、工期>2周、涉及多方利益
- **多方意见不一致**：团队成员、Agent之间存在分歧
- **复杂权衡**：多个方案各有优劣，难以直接判断

### 不适用场景
- 简单明确的任务（单一Agent直接执行）
- 时间紧迫的紧急决策
- 已有明确最佳实践的标准问题

## L2: 详细文档

### 核心原理

Convener Protocol源自Professor Synapse的Convener Mode，核心思想是：
> **不假设自己是全知全能的，而是通过主持结构化辩论，让多个视角相互碰撞，最终得出更全面的权衡分析。**

```
┌─────────────────────────────────────────────────────────────┐
│              Convener Protocol 四步流程                        │
├─────────────────────────────────────────────────────────────┤
│  Step 1: 识别需要的视角                                      │
│    - 确定哪些领域/角色适用于该决策                           │
│    - 检查是否有现成的专家Agent                               │
│    - 使用agent-template创建缺失的Agent                       │
│                                                             │
│  Step 2: 框架辩论                                           │
│    - 清晰陈述决策问题                                        │
│    - 定义成功标准和评估维度                                  │
│    - 预先承认问题的复杂性                                    │
│                                                             │
│  Step 3: 促进交流                                           │
│    - 让每个Agent陈述开场立场                                │
│    - 促使Agent回应彼此的具体观点                            │
│    - 明确揭示分歧而不掩盖                                    │
│                                                             │
│  Step 4: 综合结果                                           │
│    - 总结共识和分歧                                         │
│    - 用明确的权衡框架呈现选项                                │
│    - 适当给出建议，但最终让用户决定                          │
└─────────────────────────────────────────────────────────────┘
```

### 与天龙引擎现有能力的协同

| 天龙组件 | Convener协同方式 |
|---------|-----------------|
| **09-05求是协调师** | 矛盾分析法→Convener辩论→综合权衡 |
| **09-01魔鬼代言人** | 单Agent质疑→多Agent辩论升级 |
| **maodun-fenxi** | 主要矛盾识别→触发Convener |
| **jizhong-bingli** | 优先级决策→Convener确认 |

### Agent召唤格式

```
🧙🏾‍♂️: [Align on my goal]. [Delegate task(s) to agent].

---

[emoji]: [Actionable response or deliverable]. [Feedback question] or would you like to proceed to [Next step]?
```

### Convener响应模板

```markdown
## 🎭 Convener Protocol 启动

### 📋 决策问题
[清晰陈述需要决策的问题]

### 📊 成功标准
| 维度 | 权重 | 说明 |
|------|------|------|
| 成本 | XX% | 预算限制 |
| 时间 | XX% | 交付周期 |
| 质量 | XX% | 技术质量 |
| 风险 | XX% | 风险控制 |

### 👥 参与Agent
| Agent | 角色 | 代表视角 |
|-------|------|---------|
| [Agent-1] | [角色名] | [视角描述] |
| [Agent-2] | [角色名] | [视角描述] |

### 🔄 辩论过程

#### Agent-1 开场
[立场陈述+论据]

#### Agent-2 开场
[立场陈述+论据]

#### Agent-1 回应
[对Agent-2观点的回应]

#### Agent-2 回应
[对Agent-1观点的回应]

### ⚖️ 权衡分析

| 选项 | 优势 | 劣势 | 适用场景 |
|------|------|------|---------|
| Option 1 | ... | ... | ... |
| Option 2 | ... | ... | ... |
| Hybrid | ... | ... | ... |

### 🎯 Convener建议
[基于辩论的权衡建议，但保留用户最终决定权]

### ❓ 待确认
1. [确认问题1]
2. [确认问题2]
```

### 停止辩论的时机

辩论应适时停止，避免无限循环：

- ✅ 立场清晰且稳定
- ✅ 权衡被充分阐述
- ✅ Agent开始重复自己
- ✅ 核心分歧已明确

### 辩论质量检查

辩论结束后，Convener应自检：

```
辩论质量检查:
□ 每个Agent是否充分表达了立场？
□ Agent之间是否有真正的观点碰撞？
□ 分歧是否被明确揭示而非掩盖？
□ 权衡框架是否清晰可衡量？
□ 是否避免了"虚假共识"？
```

## 参考文件

- [references/convener-protocol.md](references/convener-protocol.md) - 完整协议文档
- [references/debate-template.md](references/debate-template.md) - 辩论模板
- [references/synthesize-template.md](references/synthesize-template.md) - 综合权衡模板

## 触发命令

```bash
/convener [决策问题]        # 启动多Agent辩论
/convener-quick           # 快速权衡分析（两个Agent）
/convener-full           # 完整辩论（3+个Agent）
```

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-04-18 | 初始版本，基于Professor Synapse Convener Protocol |

---

## 版本历史

| 版本 | 日期 | 协议 | 变更 |
|---|---|---|---|
| V1.1.0 | 2026-08-13 | DSH AgentTeams | SUMMON/COORDINATE/CONVERGE → runtime 映射 |
| V1.0.0 | 2026-04-18 | prompt 编排 | Professor Synapse Convener Mode（4 步流程）|

## 参考资料

- **V1.1 runtime**：[NanmiCoder/dsh-agent-teams](https://github.com/NanmiCoder/dsh-agent-teams)
- **V1.0 上游**：Professor Synapse Convener Mode
- **天龙集成报告**：`analysis/dsh-agent-teams-upgrade-analysis.md`
