---
license: MIT
name: hierarchical-delegation
version: 2.0.0
description: |
  层级授权协议 V2。把 V1 的"3 层拓扑 + IAR 公式"语义层映射到 DSH AgentTeams 运行时：captain = Layer 3 CEO Gateway，lead member = Layer 2 Department Manager，specialist member = Layer 1 Worker。task dependencies 显式保证 1→D→W 信息流。
author: 天龙引擎团队
created: 2026-04-06
updated: 2026-08-13
runtime: dsh-agent-teams >= 0.1.13
references:
  upstream: Jin, Yongxun (2026) - Organizational Mirroring paper
  upgrade_target: NanmiCoder/dsh-agent-teams

triggers:
  - "hierarchical delegation"
  - "Hierarchical Delegation Protocol - 层级授权协议"
  - "层级授权"
---

# Hierarchical Delegation Protocol - 层级授权协议

> **版本说明**：
> - **V2（2026-08-13，当前）**：V1 语义层 + DSH AgentTeams 运行时。3 层拓扑 → captain/lead-member/specialist-member；信息流 1→D→W → task `dependencies` DAG。
> - **V1（2026-04-06，legacy 语义层）**：纯 prompt 编排。3 层架构 + IAR 公式 + 三层记忆隔离。保留供参考。

**当前推荐**：先看 V2 §1-§4（DSH AgentTeams runtime bridge），需要原始语义层论文细节时看 V1（文末保留）。

---

# V2 · 层级授权 × DSH AgentTeams Runtime Bridge

## V2 §1. 三层拓扑 → AgentTeams 角色

| V1 层 | 语义层职责 | DSH AgentTeams 角色 |
|---|---|---|
| Layer 3 CEO Gateway | 战略意图解析、跨部门协调 | **captain**（= 当前 DSH session）|
| Layer 2 Department Manager | 任务分解、Worker 分配 | **lead-member**（1 个，captain 注册）|
| Layer 1 Worker | 任务执行、结果输出 | **specialist-member**（D × W 个）|
| Meta-Department | 质量监督、评估审查 | **meta-reviewer-member**（独立监督，captain 不调度）|

**关键映射**：

```typescript
// captain（Layer 3）
agent_teams_create({ name: `hierarchical-${Date.now()}` })

// 1 个 lead-member（Layer 2，对应 1 个 Department）
agent_teams_add_member({
  name: `lead-${departmentId}`,
  template: 'agents/<department-lead>.md',  // 例如 agents/03-builder.md
  reasoning_effort: 'high',
})

// D × W 个 specialist-members（Layer 1）
agent_teams_add_member({
  name: `worker-${departmentId}-${workerId}`,
  template: 'agents/<specialist>.md',
})

// 1 个 meta-reviewer-member（Meta Layer，独立监督）
agent_teams_add_member({
  name: 'meta-reviewer',
  template: 'agents/09-03-meta-reviewer.md',
})
```

## V2 §2. 信息流 1 → D → W → task DAG

V1 公式：**IAR = 8 × D + 2 × W**（CEO 分发 + Manager 分发 + Worker 数量）

V2 把这层信息流映射为 AgentTeams tasks：

```typescript
// Step 1: captain 把"用户战略指令"拆成 D 个 Department tasks
for (let d = 0; d < D; d++) {
  agent_teams_create_task({
    subject: `T-3-${d}: ${departmentDirective[d]}`,
    owner: `lead-${departmentId[d]}`,  // 部门经理
  })
}

// Step 2: 每个 lead-member 把"部门指令"拆成 W 个 Worker tasks
// （在 lead-member 内部触发，不是 captain 创建）
// agent_teams_create_task 由 lead-member 调用

// Step 3: specialist-member 执行 Worker tasks
// agent_teams_claim_task + agent_teams_update_task
```

**dependency 约束**：
- T-3-d（Department） → T-2-d-w（Worker）：依赖关系
- T-2-d-w → T-1-w（执行）：依赖关系
- meta-reviewer task：**不依赖任何 task**，独立 review 全部 completed task

```typescript
agent_teams_create_task({
  subject: `T-2-${d}-${w}: ${workerDirective[d][w]}`,
  owner: `worker-${d}-${w}`,
  dependencies: [`T-3-${d}`],  // 显式依赖 Department task
})

agent_teams_create_task({
  subject: `meta-review-${d}-${w}`,
  owner: 'meta-reviewer',
  dependencies: [`T-2-${d}-${w}`],  // 依赖 Worker task 完成
})
```

## V2 §3. 三层记忆隔离 → AgentTeams mailbox 边界

V1 的"每层独立记忆"在 V2 通过 **mailbox 边界**实现：

```
Layer 3 captain mailbox  ←→  Layer 2 lead-member mailbox
       ↑                                ↓
   (meta-reviewer 独立)           Layer 1 worker mailbox
```

- **captain → lead-member**：`agent_teams_send_message({ to: 'lead-X', content })`
- **lead-member → worker**：`agent_teams_send_message({ to: 'worker-X-Y', content })`
- **worker → captain**：通过 task `update_task({ status: 'completed', output })`，不直接发 mailbox
- **meta-reviewer → captain**：通过 task `update_task({ status: 'completed', output: reviewPacket })`

**关键约束**：禁止跨层 mailbox（worker 不能直接发 lead-member 之外的 lead-member；lead-member 不能直接给 worker 发任务外的消息）。

## V2 §4. 预期收益（V1 + V2 runtime）

| 指标 | 扁平拓扑 | V1 语义层 | V2 + DSH AgentTeams |
|---|---|---|---|
| 通信链路 | 156 | 13 | **13**（实际落盘可验证）|
| 记忆污染 | 存在 | 0%（语义约束）| **0%（mailbox 边界强制）**|
| IAR | ~1 | 16-44 | **16-44**（captain 决策决定上限）|
| 协调成本 | 高 | 低 | **极低**（runtime 自动调度）|
| 状态可观测 | 不可见 | 不可见 | **可见**（activity panel）|
| 失败接管 | 无 | 无 | **runtime 自动 takeover** |

---

# V1.0 · 层级授权协议（语义层，legacy fallback）

> **本节保留**：V1 是 2026-04-06 集成自 OpenClaw Framework 的原始语义层论文实现。当 DSH plugin 不可用时，仍可按 V1 的"prompt 编排"方式运行层级拓扑。

### L0: 一句话描述
信息通过管理层级流动，每层过滤压缩，实现IAR最大化

### L1: 使用场景

**适用场景**:
- 大型复杂任务需要多层级分解
- 需要降低通信复杂度（N-1链路而非N*(N-1)）
- 需要防止记忆污染和上下文混乱

**触发条件**:
- Agent数量>5
- 任务涉及多部门协作
- 需要最大化IAR（意图放大率）

### L2: 核心架构

```
┌─────────────────────────────────────────────────────────────────┐
│                  Hierarchical Delegation Protocol                      │
│                       层级授权协议 (通信链路优化)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 3: CEO Gateway (CEO网关)                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 输入: 单一自然语言指令                                    │   │
│  │ 处理: 战略意图解析、部门级任务分配                        │   │
│  │ 输出: D个部门级指令 (D = 部门数)                        │   │
│  │ 压缩率: 1 → D (100%/D)                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Layer 2: Department Manager (部门经理)                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 输入: 1个部门级指令                                       │   │
│  │ 处理: 任务分解、Worker分配                               │   │
│  │ 输出: W个任务级指令 (W = 每部门Worker数)                 │   │
│  │ 压缩率: 1 → W (100%/W)                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Layer 1: Worker (执行者)                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 输入: 1个任务级指令                                      │   │
│  │ 处理: 任务执行、结果输出                                 │   │
│  │ 输出: 执行结果 + 状态报告                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Meta Layer: Meta-Department (元部门)                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 功能: 质量监督、评估审查                                 │   │
│  │ 位置: 独立于执行层级，平行监督                          │   │
│  │ 输出: 质量报告 → 驱动演化                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 通信链路对比

```yaml
# 扁平拓扑 (Fully Connected)
flat_topology:
  agents: 13
  links: "13 * (13-1) = 156"  # 全连接
  memory_pollution: true
  context_confusion: high

# 层级拓扑 (Hierarchical)
hierarchical_topology:
  agents: 13
  links: "CEO-3Managers + 3Managers-10Workers = 13"  # 树状
  memory_pollution: false
  context_confusion: none

# 优化效果
optimization:
  link_reduction: "156 → 13"
  reduction_rate: "91.7%"
  memory_pollution_elimination: "100%"
```

### 信息流动模型

```python
# 层级信息流动
class HierarchicalDelegation:
    """
    层级授权协议的信息流动模型
    每层执行：输入 → 过滤 → 压缩 → 输出
    """

    def __init__(self, D, W):
        self.D = D  # 部门数
        self.W = W  # 每部门Worker数

    def calculate_iar(self):
        """
        IAR = Total Actions / Human Directives
        Total Actions = 8*D + 2*W (论文公式)
        """
        return 8 * self.D + 2 * self.W

    def delegation_flow(self, directive):
        """
        层级授权流程

        Phase 1: CEO Gateway (Layer 3)
        输入: 1个战略指令
        输出: D个部门级指令
        压缩率: 1/D
        """
        department_directives = []
        for d in range(self.D):
            dept_intent = self.parse_intent(directive, department=d)
            department_directives.append(dept_intent)

        return department_directives

    def manager_flow(self, dept_directive):
        """
        部门经理流程 (Layer 2)

        输入: 1个部门级指令
        输出: W个任务级指令
        压缩率: 1/W
        """
        task_directives = []
        tasks = self.decompose(dept_directive)
        for task in tasks[:self.W]:  # 限制Worker数
            task_directives.append(self.create_task_directive(task))

        return task_directives

    def worker_flow(self, task_directive):
        """
        Worker流程 (Layer 1)

        输入: 1个任务级指令
        输出: 执行结果
        压缩率: 1/1 (无压缩)
        """
        result = self.execute(task_directive)
        return {
            "status": "completed",
            "result": result,
            "metrics": self.collect_metrics(result)
        }
```

### 三层记忆隔离

```yaml
memory_isolation:
  Layer_3_CEO:
    memory_type: "战略记忆"
    content:
      - 战略方向
      - 公司目标
      - 跨部门协调
    isolation: "完全隔离"

  Layer_2_Manager:
    memory_type: "战术记忆"
    content:
      - 部门目标
      - 任务分配
      - 进度追踪
    isolation: "部门内共享"

  Layer_1_Worker:
    memory_type: "执行记忆"
    content:
      - 任务细节
      - 代码实现
      - 测试结果
    isolation: "完全隔离"

  Meta_Department:
    memory_type: "元记忆"
    content:
      - 质量评估
      - 模式识别
      - 演化建议
    isolation: "独立存储"
```

### 授权边界定义

```yaml
delegation_boundaries:
  CEO_Gateway:
    can_delegate:
      - "战略方向"
      - "部门目标"
      - "资源分配"
    cannot_delegate:
      - "具体代码实现"
      - "测试执行"
      - "日常操作"

  Department_Manager:
    can_delegate:
      - "任务分解"
      - "Worker分配"
      - "进度监控"
    cannot_delegate:
      - "跨部门协调"
      - "战略决策"
      - "资源申请"

  Worker:
    can_delegate:
      - "子任务细分"
      - "工具选择"
    cannot_delegate:
      - "任务完成"
      - "结果报告"
      - "问题上报"
```

### 与Intent Amplification集成

```
┌─────────────────────────────────────────────────────────────┐
│ Hierarchical Delegation × Intent Amplification                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户指令: "本周聚焦用户增长"                               │
│       ↓                                                     │
│  CEO Gateway (层级授权)                                    │
│  ├── 解析战略意图                                           │
│  ├── D=3个部门级指令分发                                   │
│  └── IAR贡献: 8*D = 24                                   │
│       ↓                                                     │
│  Department Manager (层级授权)                              │
│  ├── 每部门W=4个Worker任务分配                             │
│  └── IAR贡献: 2*W = 8                                     │
│       ↓                                                     │
│  Workers (执行)                                             │
│  ├── 12个任务并行执行                                      │
│  └── IAR贡献: 12                                          │
│       ↓                                                     │
│  IAR = 8*3 + 2*4 = 32                                    │
│  (理论值: 32, 实际值: 28-36)                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 天龙引擎整合

**CEO Gateway实现**:
| 组件 | 天龙引擎对应 | 职责 |
|------|-------------|------|
| CEO Gateway | 09-02编排协调师 | 战略意图解析 |
| Department Manager | 各部门首席(Manager) | 任务分解 |
| Worker | 专业Agent | 执行交付 |
| Meta-Department | 09-03元审查师 | 质量监督 |

**天龙组织对齐**:
```yaml
天龙组织对齐:
  Layer_3:
   天龙: "09-02编排协调师"
   职责: "战略方向入口、跨部门协调"

  Layer_2:
    Game_Manager: "游戏部门首席"
    AI_Manager: "AI部门首席"
    Life_Manager: "生活部门首席"

  Layer_1:
    Game_Workers: "B/L/V/N Agent"
    AI_Workers: "T/Q/I/F Agent"
    Life_Workers: "Co/Ne Agent"

  Meta:
    Warden: "09-03-01 Warden"
    Forge: "09-03-02 Forge"
    Prism: "09-03-03 Prism"
    Scout: "09-03-04 Scout"
```

### 使用命令

```bash
# 启动层级授权
/hierarchical-delegation start --directive "本周聚焦用户增长"

# 查看授权链路
/hierarchical-delegation links

# 检查通信约束
/hierarchical-delegation check --from CEO --to Worker

# 查看压缩率统计
/hierarchical-delegation stats
```

### 核心原则

| 原则 | 说明 | 天龙引擎对应 |
|------|------|-------------|
| **信息向上过滤** | 每层向上报告摘要，抑制噪声 | Manager→CEO汇报 |
| **决策向下授权** | 每层自主决策，CEO只给方向 | 部门自治 |
| **记忆严格隔离** | 跨层不共享工作记忆 | 07记录师 |
| **链路最小化** | 树状结构，禁止越级通信 | 通信协议强制 |
| **元部门独立** | 质量监督独立于执行链 | 09-03元审查师 |

### 与现有系统协同

| 天龙组件 | 协同方式 | 效果 |
|---------|---------|------|
| **Intent Amplification** | IAR公式驱动 | 8D+2W最大化 |
| **Meta-Department** | 元部门质量监督 | 独立评估 |
| **Organizational Mirroring** | 组织镜像架构 | 层级拓扑 |
| **Independent Memory** | 记忆隔离 | 防污染 |

### 预期收益

| 指标 | 扁平拓扑 | 层级授权 | 提升 |
|------|---------|---------|------|
| **通信链路** | 156 | 13 | **-91.7%** |
| **记忆污染** | 存在 | 0% | **完全消除** |
| **IAR** | ~1 | 16-44 | **+1500-4300%** |
| **协调成本** | 高 | 低 | **-80%** |
| **上下文清晰度** | 混乱 | 清晰 | **质的飞跃** |

---

**版本历史**: V1.0 (2026-04-06) - 初始集成，基于Organizational Mirroring论文

---

## 版本历史

| 版本 | 日期 | 协议 |
|---|---|---|
| V2.0.0 | 2026-08-13 | DSH AgentTeams plugin runtime + V1 语义层 |
| V1.0.0 | 2026-04-06 | OpenClaw Framework 语义层（Organizational Mirroring 论文）|

## 参考资料

- **V2 runtime**：[NanmiCoder/dsh-agent-teams](https://github.com/NanmiCoder/dsh-agent-teams)
- **V1 上游**：OpenClaw Framework（Jin, Yongxun 2026）
- **天龙集成报告**：`analysis/dsh-agent-teams-upgrade-analysis.md`
- **09-02 编排协调师 V9.09**：`agents/09-02-orchestrator.md`（与本 skill 联动）
