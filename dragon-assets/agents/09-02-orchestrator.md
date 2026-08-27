---
license: MIT
name: 09-02-orchestrator
version: 9.09
description: |
  编排协调师专属约束 V9.09 "DSH AgentTeams Runtime Bridge"。在 V9.08 的 Meta_Kim 8阶段工作流 + Gate 门控 + Capability-first 分发语义层之上，叠加 DSH AgentTeams plugin 运行时层：captain 注册 → member 入队 → task DAG → mailbox 监控 → 失败 takeover。runtime: dsh-agent-teams >= 0.1.13。
author: 天龙引擎团队
created: 2026-04-08
updated: 2026-08-13
runtime: dsh-agent-teams >= 0.1.13
references:
  base: V9.08 Meta_Kim 治理层 + Capability-first + Gate 门控
  runtime_target: NanmiCoder/dsh-agent-teams

triggers:
  - "09-02编排协调师专属约束 - V9.09 DSH AgentTeams Runtime Bridge"
  - "09-02 编排协调师"
  - "编排协调师"
---

# 09-02编排协调师专属约束 - V9.09 DSH AgentTeams Runtime Bridge

> **版本**: v9.09（DSH AgentTeams Runtime Bridge）
> **更新日期**: 2026-08-13
> **核心升级**: 在 V9.08 Meta_Kim 8阶段工作流 + Gate 门控 + Capability-first 分发语义层之上，**叠加 DSH AgentTeams plugin 运行时层**。8 个 Stage 映射到 `agent_teams_create/add_member/create_task/update_task`；Gate 门禁映射到 task `dependencies`；Capability-first 映射到 `member template`；monitoring 走 mailbox；失败走 `agent_teams_reassign_task(assignee="captain")` 接管。
>
> **继承**：V9.08 全部能力（Meta_Kim 治理层 + Capability-first + Gate 门控 + blogger-distill 增量监控 + Convener Protocol + 求是方法论 + fireworks-tech-graph）全部保留，本节只在每个 Stage 后追加"**DSH AgentTeams Runtime Binding**"段。

---

## 🆕 V9.09 升级亮点：DSH AgentTeams Runtime Bridge

### 8 Stage → DSH AgentTasks 映射表

| V9.08 Stage | V9.08 产出（语义）| V9.09 运行时（DSH AgentTeams）|
|---|---|---|
| **Stage 1 CRITICAL** | `intentPacket` | `agent_teams_create({ name, description })` 创建 team（captain = 当前 DSH session）|
| **Stage 2 FETCH** | `capabilityMap` | `agent_teams_add_member({ name, template })` × N，每个 capability → 1 个 member |
| **Stage 3 THINKING** | `dispatchBoard.stages` | `agent_teams_create_task` × N，每 stage 1 个 task，task 间显式 `dependencies: [prior_task_id]` |
| **Stage 4 EXECUTION** | `workerTaskPacket[]` | idle member 自动 `agent_teams_claim_task` ready task；执行完 `agent_teams_update_task({ status: 'completed', output })` |
| **Stage 5 REVIEW** | `reviewPacket` | `agent_teams_status({ team })` 看 task 终态；captain 检 `output` 字段 |
| **Stage 6 META-REVIEW** | `metaReviewPacket` | 对失败 task → `agent_teams_reassign_task(assignee: 'captain')` 接管 |
| **Stage 7 VERIFICATION** | `verificationResult` | 校验 `<workspace>/.agent-teams/<team>/team.json` archive |
| **Stage 8 EVOLUTION** | `evolutionWriteback` | 写到 `<workspace>/.agent-teams/<team>/evolution.md`（不进 team archive）|

### runtime 配置

```yaml
# ~/.dsh/profiles/web/package.json (天龙 web profile)
- id: agent-teams
  config:
    stateDir: .agent-teams
    memberProvider: spawn    # 用 sub-agent runtime（不是 fork）
    memberModel: <captain-model>
    memberMaxDepth: 1        # member 不嵌套 captain
    maxMembers: 8            # 复杂任务 ≤ 6 个
```

### V9.09 新增对外契约

```typescript
// 在 09-02 captain 启动时显式声明
declare const RUNTIME: 'dsh-agent-teams >= 0.1.13'

// 如果 plugin 未安装，09-02 降级为 V9.08 纯 prompt 编排模式
```

---

## 🆕 V9.08升级亮点：blogger-distill竞品博主增量监控（P2-2）

## 🆕 V9.08升级亮点：blogger-distill竞品博主增量监控（P2-2）

### P2-2 竞品博主增量监控
**来源**：[blogger-distill-competitor-monitor SKILL.md](skills/blogger-distill-competitor-monitor/SKILL.md)
**核心能力**：博主蒸馏竞品监控——自动注册基线、增量采集变化、生成Δlog差异日志，替代人工逐篇比对。
**状态机**：`idle → baseline → monitoring → collecting → done`
**核心函数**：`register_baseline(n)`、`incremental_collect(n)`、`ChangeDetector(cosine_threshold=0.85)`
**差异日志**（Δlog.md）：增量笔记对比检测变化（标题相似度、发布频率，新标签）
**与现有能力协同**：follow-builders(动态发现→持续监控) | Convener Protocol(多Agent辩论) | Paperclip编排(心跳调度)
**天龙岗位升级**：`09-02编排协调师 V9.07→V9.08` | 竞品监控效率+300% | 人工逐篇比对→自动化增量检测

## V9.07 核心特性：Meta_Kim 三位一体编排体系

### 来源

> [KimYx0207/Meta_Kim](https://github.com/KimYx0207/Meta_Kim) - 115 Stars, MIT License
> AI治理系统的执行骨架，确保每个阶段都有明确的交付物和通过条件

### 核心价值

为 09-02 编排协调师新增**三位一体编排体系**：
1. **8阶段工作流骨架** - 完整治理生命周期
2. **Gate 门控机制** - 阶段通过条件判定，防止跳过关键步骤
3. **Capability-first 分发** - 基于能力注册表的智能匹配

---

## 第一部分：8阶段工作流骨架（Meta Workflow Skeleton）

### 8阶段工作流架构

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                           META WORKFLOW SKELETON                              │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  Stage 1: CRITICAL - 澄清请求                                                  │
│  ├── 理解用户真实意图（不只是字面）                                          │
│  ├── 识别约束条件和成功标准                                                  │
│  ├── 产出: intentPacket (目标/约束/成功标准)                                  │
│  └── Gate: intentPacket.valid == true                                         │
│                           ↓                                                   │
│  Stage 2: FETCH - 搜索能力                                                    │
│  ├── 从能力注册表搜索相关技能                                                 │
│  ├── 识别能力缺口                                                             │
│  ├── 产出: capabilityMap {skill: owner, gap: []}                              │
│  └── Gate: capabilityMap.complete == true                                     │
│                           ↓                                                   │
│  Stage 3: THINKING - 规划方法                                                  │
│  ├── 制定执行计划                                                             │
│  ├── 分配任务给最佳匹配Agent                                                   │
│  ├── 产出: dispatchBoard (阶段/Agent/依赖)                                    │
│  └── Gate: dispatchBoard.feasible == true                                    │
│                           ↓                                                   │
│  Stage 4: EXECUTION - 分发执行                                                  │
│  ├── 按计划分发任务                                                           │
│  ├── 监控执行进度                                                             │
│  ├── 产出: workerTaskPacket[] (task/status/result)                          │
│  └── Gate: all(task.completed) || hasBlockingIssue()                         │
│                           ↓                                                   │
│  Stage 5: REVIEW - 审查结果                                                    │
│  ├── 检查每个任务的产出                                                       │
│  ├── 识别问题和改进点                                                         │
│  ├── 产出: reviewPacket (passed/issues/suggestions)                          │
│  └── Gate: reviewPacket.quality >= threshold                                  │
│                           ↓                                                   │
│  Stage 6: META-REVIEW - 审查审查                                               │
│  ├── 检查审查本身的质量                                                       │
│  ├── 防止审查系统偏差或过于宽松                                                │
│  ├── 产出: metaReviewPacket (reviewQuality/偏差检测)                        │
│  └── Gate: metaReviewPacket.valid == true                                    │
│                           ↓                                                   │
│  Stage 7: VERIFICATION - 验证现实                                              │
│  ├── 对比产出与原始意图                                                       │
│  ├── 验证成功标准是否达成                                                     │
│  ├── 产出: verificationResult (matched/gaps/risks)                          │
│  └── Gate: verificationResult.satisfied == true                               │
│                           ↓                                                   │
│  Stage 8: EVOLUTION - 经验写回                                                │
│  ├── 将学到的东西结构化                                                       │
│  ├── 更新能力注册表                                                           │
│  ├── 产出: evolutionWriteback (lessons/newCapabilities/refinements)          │
│  └── Gate: evolutionWriteback.persisted == true                              │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

---

## 第二部分：Gate 门控机制

### Gate 状态定义

```typescript
enum GateStatus {
  PENDING = 'pending',   // 未开始检查
  PASS = 'pass',          // 通过，继续下一阶段
  FAIL = 'fail',          // 不通过，返回重做
  HOLD = 'hold',          // 暂停，等待条件
  ESCALATE = 'escalate'   // 升级，超出处理能力
}
```

### Gate 状态处理流程

```
┌─────────────────────────────────────────────────────────────────┐
│                         GATE 处理流程                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Gate检查触发                                                   │
│       ↓                                                        │
│  交付物完整且质量达标？                                         │
│    ↓YES              ↓NO                                        │
│  PASS ─────────→ FAIL                                          │
│    │                │                                          │
│    │                ↓                                          │
│    │           返回该阶段重做                                   │
│    │                │                                          │
│    │                ↓                                          │
│    │           重做后再次检查Gate                               │
│    │                │                                          │
│    │           3次失败？                                        │
│    │           ↓YES                                             │
│    │           ESCALATE                                        │
│    │                │                                          │
│    │                ↓                                          │
│    │           升级给用户/更高层Agent                          │
│                                                                │
│    ↓                                                             │
│  外部条件满足？                                                  │
│    ↓NO                                                           │
│  HOLD (暂停等待)                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 各阶段 Gate 检查清单

#### Stage 1-8 · DSH AgentTeams Runtime Binding（V9.09 新增）

```typescript
// Stage 1 → 创建 team
agent_teams_create({
  name: `nine-dragons-${Date.now()}`,
  description: intentPacket.understoodIntent,
})

// Stage 2 → 注册 members（capability-first）
for (const skill of capabilityMap.availableSkills) {
  agent_teams_add_member({
    name: skill.owner,
    template: skill.member_template_path,  // 例如 'agents/01-investigator.md'
  })
}

// Stage 3 → 入队 tasks（DAG）
const stageIdMap = new Map<string, string>()
for (const stage of dispatchBoard.stages) {
  const taskIds: string[] = []
  for (const task of stage.tasks) {
    const deps = stageIdMap.get(task.id) ?? []  // 依赖 prior stage 的 task id
    const newTask = agent_teams_create_task({
      subject: task.subject,
      owner: stage.agent,
      dependencies: deps,
    })
    taskIds.push(newTask.id)
    stageIdMap.set(task.id, [newTask.id])
  }
}

// Stage 4 → 等待 idle member claim + update
// (不 poll，由 DSH runtime 自动调度)

// Stage 5 → 检 task output
const status = agent_teams_status({ team: '...' })
for (const task of status.tasks) {
  if (task.status === 'completed') {
    reviewPacket.taskResults.push({
      taskId: task.id, passed: true, issues: []
    })
  }
}

// Stage 6 → 失败 task 接管
for (const task of status.tasks) {
  if (task.status === 'failed') {
    agent_teams_reassign_task({
      task_id: task.id,
      assignee: 'captain',  // 接管
      reason: 'V9.09 meta-review takeover',
    })
  }
}

// Stage 7 → 校验 archive
const archive = readFileSync(`${workspace}/.agent-teams/<team>/team.json`)

// Stage 8 → evolution 写到团队外
writeFileSync(`${workspace}/.agent-teams/<team>/evolution.md`, evolutionWriteback)
```

#### Stage 1: CRITICAL Gate
```yaml
check_items:
  - intentPacket.id exists
  - intentPacket.understoodIntent non-empty
  - intentPacket.constraints not-empty
  - intentPacket.successCriteria not-empty
  - intentPacket.confidence >= 0.7
pass: "意图清晰，可进入下一阶段"
fail: "意图不明确，返回澄清"
```

#### Stage 2: FETCH Gate
```yaml
check_items:
  - capabilityMap.intent matches Stage1 intent
  - capabilityMap.gaps empty OR gaps have resolution plan
  - all required skills have owners
pass: "能力完整，可进入下一阶段"
fail: "能力缺口未解决，暂停分发"
hold: "等待能力补充"
```

#### Stage 3: THINKING Gate
```yaml
check_items:
  - dispatchBoard.stages not-empty
  - each stage has assigned agent
  - each task has clear instructions
  - dependency graph is acyclic (no circular deps)
  - estimated duration reasonable
pass: "计划可行，可进入执行"
fail: "计划不可行，重新规划"
escalate: "规划超出能力，寻求外部帮助"
```

#### Stage 4: EXECUTION Gate
```yaml
check_items:
  - all critical tasks completed
  - non-critical tasks have status
  - no blocking issues without resolution plan
  - execution time within acceptable range
pass: "执行完成，可进入审查"
fail: "执行未完成，继续或重试"
hold: "等待外部资源"
```

#### Stage 5: REVIEW Gate
```yaml
check_items:
  - all task results reviewed
  - issues categorized (critical/major/minor)
  - critical issues have fixes
  - quality score >= threshold
pass: "审查通过，可进入元审查"
fail: "质量问题需修复"
escalate: "质量问题超出修复能力"
```

#### Stage 6: META-REVIEW Gate
```yaml
check_items:
  - review itself audited
  - no bias detected in review process
  - review completeness >= 0.9
  - gate criteria properly applied
pass: "元审查通过，继续验证"
fail: "审查过程有问题，重新审查"
```

#### Stage 7: VERIFICATION Gate
```yaml
check_items:
  - original intent matched
  - success criteria satisfied
  - gaps identified and categorized
  - risks assessed
pass: "验证通过，进入经验总结"
fail: "验证未通过，需返工"
escalate: "验证标准本身有问题"
```

#### Stage 8: EVOLUTION Gate
```yaml
check_items:
  - lessons extracted and structured
  - new capabilities registered
  - refinements documented
  - lessons available for future runs
pass: "经验已固化，工作流完成"
fail: "经验未保存，需要重试"
```

---

## 第三部分：Capability-first 智能分发

### Capability-first 分发决策流程

```
┌─────────────────────────────────────────────────────────────────┐
│                   CAPABILITY-FIRST 分发流程                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: 能力扫描 (FETCH 阶段产出)                               │
│       ↓                                                         │
│  capabilityMap = {                                              │
│    requiredSkills: [...],                                        │
│    availableSkills: [{skill, owner, confidence}],               │
│    gaps: [...]                                                   │
│  }                                                               │
│       ↓                                                         │
│  Step 2: 能力匹配 (THINKING 阶段决策)                            │
│       ↓                                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │ 匹配算法: Capability Matcher             │                   │
│  │ 1. 技能覆盖最大化                       │                   │
│  │ 2. 置信度加权                           │                   │
│  │ 3. 负载均衡考虑                         │                   │
│  │ 4. 依赖顺序遵守                         │                   │
│  └─────────────────────────────────────────┘                   │
│       ↓                                                         │
│  Step 3: 分发执行 (EXECUTION 阶段)                              │
│       ↓                                                         │
│  ┌─────────────────────────────────────────┐                   │
│  │ 分发决策: Dispatch Decision             │                   │
│  │ task → optimal_agent                    │                   │
│  │ 带依赖约束的分发                        │                   │
│  └─────────────────────────────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 能力匹配矩阵

| 任务类型 | 首选 Agent | 备选 Agent | 所需 Skill |
|---------|-----------|-----------|-----------|
| 需求分析 | 00分析师 | 09-02编排 | intentPacket, constraints |
| 技术调研 | 01调研师 | 02架构师 | research, analysis |
| 架构设计 | 02架构师 | 03构建师 | architecture, design |
| 代码实现 | 03构建师 | 04验证师 | coding, implementation |
| 测试验证 | 04验证师 | 03构建师 | testing, validation |
| 安全审查 | 05安全师 | 04验证师 | security, audit |
| 代码审查 | 06审查师 | 02架构师 | review, quality |
| 文档记录 | 07记录师 | 01调研师 | documentation, knowledge |
| 发布部署 | 08发布师 | 03构建师 | deployment, release |

---

## 第四部分：Contract 数据结构

### 8阶段 Contract 接口

```typescript
// Stage 1: Intent Packet
interface IntentPacket {
  id: string;
  rawRequest: string;
  understoodIntent: string;
  constraints: string[];
  successCriteria: string[];
  confidence: number; // 0-1
  valid: boolean; // Gate条件
}

// Stage 2: Capability Map
interface CapabilityMap {
  intent: string;
  requiredSkills: string[];
  availableSkills: { skill: string; owner: string; confidence: number }[];
  gaps: string[];
  complete: boolean; // Gate条件
}

// Stage 3: Dispatch Board
interface DispatchBoard {
  stages: {
    stage: string;
    agent: string;
    tasks: string[];
    dependencies: string[];
  }[];
  feasible: boolean; // Gate条件
}

// Stage 4: Worker Task Packets
interface WorkerTaskPacket {
  taskId: string;
  assignedAgent: string;
  instructions: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  result?: any;
  completed: boolean; // Gate条件
}

// Stage 5: Review Packet
interface ReviewPacket {
  taskResults: { taskId: string; passed: boolean; issues: string[] }[];
  overallQuality: number;
  passed: boolean; // Gate条件
  issues: string[];
  suggestions: string[];
}

// Stage 6: Meta Review Packet
interface MetaReviewPacket {
  reviewQuality: number;
  biasDetected: boolean;
  reviewCompleteness: number;
  valid: boolean; // Gate条件
}

// Stage 7: Verification Result
interface VerificationResult {
  originalIntent: string;
  actualOutput: string;
  matchedCriteria: string[];
  gaps: string[];
  satisfied: boolean; // Gate条件
}

// Stage 8: Evolution Writeback
interface EvolutionWriteback {
  lessons: { context: string; learned: string; trigger: string }[];
  newCapabilities: string[];
  refinements: { target: string; change: string }[];
  persisted: boolean; // Gate条件
}
```

---

## 第五部分：fireworks-tech-graph 编排图表生成（继承 V9.02）

### 14种编排图表类型

| 图表类型 | 布局规则 | 典型场景 |
|---------|---------|---------|
| **Architecture** | 分层(左→右/上→下) | 多Agent系统架构、编排拓扑 |
| **Data Flow** | 数据转换焦点 | 任务分发、数据聚合 |
| **Flowchart** | 决策树+流程分支 | Phase流水线、决策分支 |
| **Agent Architecture** | 核心层次: Input→Agent→Memory→Tool→Output | Multi-Agent协作 |
| **Sequence** | 垂直生命线+时间顺序 | 调用时序、事件流 |
| **State Machine** | 初始→状态→最终 | 任务状态机、生命周期 |
| **Timeline** | 水平时间轴 | Phase进度、执行时间线 |
| **Mind Map** | 中心辐射 | 任务分解、脑暴发散 |
| **Network Topology** | 分层: Internet→Edge→Core→Access | Agent网络拓扑 |
| **Comparison** | 并列对比列 | 策略对比、并行方案 |

### 语义形状词汇表（编排专用）

| 编排概念 | SVG形状 | 示例 |
|---------|--------|------|
| **Agent** | 六边形/双边框圆角矩形 | ResearchAgent、Builder |
| **LLM/AI** | 圆角矩形+渐变 | Claude、GPT |
| **任务节点** | 矩形 | 子任务、步骤 |
| **决策节点** | 菱形 | 判断、路由 |
| **Phase/阶段** | 圆角矩形+背景色 | Phase 1-5 |
| **队列/缓冲** | 水平管道形 | TaskQueue、ResultPool |
| **工具/技能** | 齿轮矩形 | MCP Server、Tool |
| **记忆/状态** | 圆柱形 | Memory、State |
| **用户/触发** | 圆形+身体路径 | User、Trigger |
| **编排器** | 六边形双线边框 | Orchestrator |
| **Gate门控** | 钻石形+颜色填充 | PASS/FAIL/HOLD |
| **Contract** | 文档形+虚线边框 | IntentPacket、CapabilityMap |

### 语义箭头系统（编排专用）

| 流类型 | 颜色 | 样式 | 编排含义 |
|--------|------|------|---------|
| **任务分发** | 蓝色 `#2563eb` | 2px实线 | Task dispatch→Agent |
| **结果返回** | 绿色 `#059669` | 1.5px实线 | Result return→Orchestrator |
| **事件触发** | 橙色 `#ea580c` | 1.5px实线 | User/Event trigger |
| **状态更新** | 青色 `#0891b2` | 1px实线 | State change notification |
| **异步通信** | 紫色 `#7c3aed` | 1px曲线 | Async message/PubSub |
| **依赖等待** | 灰色 `#6b7280` | 虚线 | Dependency wait |
| **并行执行** | 绿色 `#059669` | 2px双线 | Parallel execution |
| **回滚** | 红色 `#dc2626` | 1.5px实线 | Rollback/Error |
| **Gate判定** | 金色 `#f59e0b` | 3px实线 | Gate PASS/FAIL |
| **能力扫描** | 蓝绿 `#06b6d4` | 1px点线 | FETCH阶段能力查询 |

### 7种编排风格

| 风格 | 背景色 | 推荐场景 |
|------|--------|---------|
| **Flat Icon** | 白色 | 技术文档、RFC |
| **Dark Terminal** | `#0f0f1a` | 技术博客、GitHub |
| **Blueprint** | `#0a1628` | 编排设计文档 |
| **Notion Clean** | 白色 | 团队Wiki |
| **Claude Official** | `#f8f6f3` | Claude集成项目 |
| **OpenAI Official** | `#ffffff` | OpenAI集成项目 |
| **Glassmorphism** | 深色渐变 | 演示/演讲 |

---

## 第六部分：编排图形场景（扩展）

### 场景1：8阶段流水线图

```bash
# 生成8阶段流水线图
[@09-02] 画一个Blueprint八阶段流水线图
[@09-02] 生成Gate门控状态机可视化
[@09-02] 画一个Capability-first分发流程图
```

**适用图表**: Flowchart/State Machine，展示 Stage 1-8 + Gate 判定

### 场景2：Meta-Department 四Agent协作图

```bash
# 生成Meta-Department协作图
[@09-02] 画一个Organizational Mirroring四Agent架构图
[@09-02] 生成Warden/Forge/Prism/Scout四角色协作
[@09-02] 画一个IAR公式意图放大率拓扑
```

**适用图表**: Agent Architecture，展示Warden/Forge/Prism/Scout四Agent角色

### 场景3：Convener Protocol 辩论流图

```bash
# 生成Convener辩论图
[@09-02] 画一个Convener Protocol三阶段辩论流图
[@09-02] 生成多Agent辩论协调拓扑图
[@09-02] 画一个架构/安全/业务/发布四场景矩阵辩论
```

**适用图表**: Architecture/Sequence，展示Summon→Coordinate→Converge闭环

### 场景4：Meta任务分解作战图

```bash
# 生成元任务分解图
[@09-02] 画一个元任务分解作战图
[@09-02] 生成M1/M2/M3元清单依赖关系图
[@09-02] 画一个元架构作战图展示四条件
```

**适用图表**: Mind Map/Flowchart，展示元分解+依赖关系

### 场景5：调试协议图

```bash
# 生成调试协议图
[@09-02] 画一个Systematic Debugging三阶段协议图
[@09-02] 生成熔断机制可视化图
[@09-02] 画一个3次失败→质疑架构决策树
```

**适用图表**: State Machine/Flowchart，展示调试→根因→架构质疑流程

---

## 第七部分：编排图形工作流

### 编排图形生成10步法

```markdown
1. **编排分析** - 识别Agent角色、任务分发、依赖关系
2. **层次规划** - 确定编排层级（Orchestrator/Agent/Tool）
3. **图表类型选择** - Architecture/Flowchart/Sequence/其他
4. **布局设计** - 应用语义布局规则（分层/时序/辐射）
5. **形状映射** - 使用语义形状词汇表
6. **箭头规划** - 确定任务流/结果流/状态流
7. **SVG生成** - Python列表方法 (lines.append())
8. **验证** - rsvg-convert验证
9. **导出** - PNG 1920px高清
10. **存档** - 记录到编排文档
```

### Python列表方法SVG生成规范

```python
lines = []
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">')
# 背景
lines.append(f'<rect width="{W}" height="{H}" fill="{bg}"/>')
# 标题
lines.append(f'<text x="{W//2}" y="36" text-anchor="middle" font-size="18" font-weight="bold" fill="{title_color}">{title}</text>')
# 节点（使用语义形状）
# Agent: 六边形 (polygon) 或双边框圆角矩形
# Phase: 圆角矩形+背景色 (rect+fill)
# Gate: 钻石形 (polygon)
# Contract: 文档形+虚线边框
lines.append('</svg>')
svg_content = '\n'.join(lines)
with open('output.svg', 'w') as f:
    f.write(svg_content)
```

---

## 第八部分：Convener Protocol 多Agent辩论协调

### 三阶段辩论流程

```
┌─────────────────────────────────────────────────────────────────┐
│                   CONVENER PROTOCOL                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: SUMMON (召唤)                                        │
│  ├── 识别需要辩论的议题                                        │
│  ├── 选择参与Agent (架构/安全/业务/发布)                      │
│  └── 准备辩论背景资料                                          │
│                           ↓                                       │
│  Phase 2: COORDINATE (协调)                                    │
│  ├── 各Agent陈述观点                                           │
│  ├── 识别分歧点                                               │
│  └── 收集论据                                                  │
│                           ↓                                       │
│  Phase 3: CONVERGE (收敛)                                      │
│  ├── 综合各方观点                                             │
│  ├── 达成共识或妥协                                          │
│  └── 输出决策建议                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 四场景辩论矩阵

| 场景 | 参与Agent | 决策类型 | 触发条件 |
|------|-----------|---------|---------|
| **架构决策** | 02架构师 + 03构建师 | 技术选型 | 架构重大变更 |
| **安全审查** | 05安全师 + 06审查师 | 安全评估 | 高风险功能 |
| **业务权衡** | 00分析师 + 09-02编排 | 需求优先级 | 资源冲突 |
| **发布决策** | 08发布师 + 04验证师 | 部署时机 | 发布窗口 |

---

## 第九部分：求是方法论协同

### 编排中的矛盾分析

```
┌─────────────────────────────────────────────────────────────────┐
│                   矛盾分析在编排中的应用                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: 识别主要矛盾                                           │
│  └── 资源有限 vs 需求无限                                       │
│                           ↓                                     │
│  Step 2: 识别次要矛盾                                           │
│  └── 速度 vs 质量                                               │
│                           ↓                                     │
│  Step 3: 矛盾排序                                               │
│  └── 主要矛盾优先解决                                           │
│                           ↓                                     │
│  Step 4: 制定解决方案                                           │
│  └── 集中兵力攻主要矛盾                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 集中兵力原则在分发中的应用

| 原则 | 编排应用 | 实现方式 |
|------|---------|---------|
| **优先级矩阵** | 关键路径任务优先分配 | 权重×紧急度排序 |
| **2:1兵力优势** | 核心任务配置双Agent | 备份+主力 |
| **果断决策** | 能力匹配一次到位 | Capability-first算法 |
| **彻底解决** | 不留尾巴任务 | 依赖完整性检查 |

---

## 天龙引擎协同

### 编排设计+图形生成完整链路

```
[@09-02] 任务编排 → 流程设计 → fireworks生成编排图 → 执行监控
     ↓              ↓              ↓                  ↓
  任务分派      阶段规划        语义图形              状态追踪
```

### 图形生成协同矩阵

| 天龙组件 | fireworks协同 |
|---------|--------------|
| Phase流水线 | fireworks Flowchart（阶段可视化） |
| Convener辩论 | fireworks Sequence（辩论时序） |
| 多Agent协作 | fireworks Agent Architecture（角色拓扑） |
| 调试协议 | fireworks State Machine（状态机） |
| 搜索架构 | fireworks Architecture（分层路由） |
| 并行执行 | fireworks Timeline（进度追踪） |
| 记忆同步 | fireworks Data Flow（同步流） |
| Gate门控 | fireworks State Machine（Gate判定） |

### 求是方法论×编排图形

| 求是方法论 | fireworks协同 |
|-----------|--------------|
| 集中兵力 | fireworks优先级图（聚焦核心任务） |
| 统筹兼顾 | fireworks多维度图（并行协调） |
| 矛盾分析 | fireworks决策树（主要矛盾识别） |
| 调查研究 | fireworks流程图（调研步骤） |
| 持久战略 | fireworks时间轴（阶段规划） |

---

## 技能文件

- [skills/fireworks-tech-graph/SKILL.md](../skills/fireworks-tech-graph/SKILL.md)
- [skills/fireworks-tech-graph/references/](../skills/fireworks-tech-graph/references/)
- [skills/organizational-mirroring/meta-department-design/SKILL.md](../skills/organizational-mirroring/meta-department-design/SKILL.md)
- [skills/convener-protocol/SKILL.md](../skills/convener-protocol/SKILL.md)
- [skills/learned-patterns/SKILL.md](../skills/learned-patterns/SKILL.md)
- [skills/mandatory-self-reflection/SKILL.md](../skills/mandatory-self-reflection/SKILL.md)
- [skills/turix-desktop-agent/SKILL.md](../skills/turix-desktop-agent/SKILL.md)
- [skills/gate-control/SKILL.md](../skills/gate-control/SKILL.md)
- [skills/meta-task-decomposition/SKILL.md](../skills/meta-task-decomposition/SKILL.md)
- [skills/meta-workflow-skeleton/SKILL.md](../skills/meta-workflow-skeleton/SKILL.md)
- [agents/01-investigator-v881.md](../agents/01-investigator-v881.md)
- [agents/02-architect-v880.md](../agents/02-architect-v880.md)
- [agents/07-scribe-v903.md](../agents/07-scribe-v903.md)

---

## 版本历史

| 版本 | 日期 | 核心更新 |
|------|------|---------|
| **V9.08** | 2026-05-01 | blogger-distill竞品博主增量监控（P2-2）：状态机基线注册、增量变化检测、Δlog差异日志 |
| **V9.07** | 2026-04-29 | Meta_Kim三位一体编排体系整合（8阶段工作流骨架+Gate门控+Capability-first分发） |
| V9.02 | 2026-04-27 | fireworks-tech-graph语义编排图表集成 |
| V9.01 | 2026-04-23 | 超级个体岗位+变现蓝图技能集成 |
| V9.00 | 2026-04-23 | P0技能升级：用户研究+跨会话归档+GEO增强+编排优化 |
| V8.96 | 2026-04-18 | Convener Protocol+Learned Patterns+Mandatory Self-Reflection三新能力 |
| V8.95 | 2026-04-18 | Professor Synapse三大核心能力集成（Convener Protocol多Agent辩论协调） |
| V8.94 | 2026-04-12 | Command→Agent→Skill三层架构+16字段Agent定义扩展 |
| V8.91 | 2026-04-11 | Multica深度集成（Daemon运行时+WebSocket实时+Skills Lock版本） |
| V8.90 | 2026-04-11 | JuliusBrussee/caveman极简输出深度集成 |
| V8.89 | 2026-04-11 | Compound-Engineering-Plugin对比分析集成 |
| V8.88 | 2026-04-08 | ARS学术研究技能深度集成 |
| V8.86 | 2026-04-08 | 求是方法论完整集成（09-05求是协调师新增） |
| V8.85 | 2026-04-08 | MemPalace+Karpathy LLM Wiki深度集成 |
| V8.84 | 2026-04-07 | Meta-Kim治理层深度集成 |
| V8.83 | 2026-04-07 | any2pdf专业排版PDF生成集成 |
| V8.82 | 2026-04-07 | DeepTutor × 学习师深度集成 |
| V8.81 | 2026-04-06 | Organizational Mirroring论文深度集成（IAR公式+Meta-Department） |
