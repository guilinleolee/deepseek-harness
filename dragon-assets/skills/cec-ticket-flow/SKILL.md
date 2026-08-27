---
license: UNKNOWN
name: cec-ticket-flow
description: 天龙CEC v1.5打通技能——paperclip-ticket/heartbeat/org与~/customers/客户目录的全链路流程编排
github_repo: dragon-engine/cec
github_hash: pending
last_updated: 2026-08-10
source_type: dragon-engine-original
triggers: ["cec-ticket-flow", "CEC工单流", "天龙CEC v1.5", "customer ticket flow", "FDE ticket orchestration"]
---

# 天龙 CEC v1.5 工单流（cec-ticket-flow）

天龙 CEC v1.5 核心 skill。把天龙 paperclip 三件套（ticket + heartbeat + org）与天龙 CEC v1.0 客户目录（~/customers/<name>/）全链路打通。

## L0: 一句话描述 (≤15字)
CEC v1.5工单全链编排

## L1: 使用场景 (50-100字)
用于天龙 CEC v1.5，把客户项目（~/customers/<name>/）与天龙工单系统（paperclip-ticket）打通。覆盖每客户工单池创建、状态机流转、自动 AAR 触发、健康度联动。与 [[agents/39-forward-deployed-engineer]] [[agents/41-customer-success-architect]] 和 `/cec-ticket` command 协同使用。

## L2: 详细文档

### 架构概览

```
┌────────────────────────────────────────────────────────┐
│              天龙 CEC v1.5 打通架构                     │
├────────────────────────────────────────────────────────┤
│  ~/customers/<name>/                                    │
│  ├── profile.md       ──┐                              │
│  ├── interviews/       ──┤                              │
│  ├── fieldbook/       ──┼──→ customer-stage-detector hook
│  │   land.md → ...   ──┤    │                         │
│  ├── health/         ──┤    ▼                         │
│  ├── aar/             ──┘    paperclip-ticket          │
│  └── tickets/                 自动创建工单              │
│      ├── index.md              │                     │
│      ├── backlog/              ▼                     │
│      ├── in-progress/    工单状态机                   │
│      ├── review/         backlog → in_progress        │
│      ├── completed/      → review → completed        │
│      └── cancelled/              │                     │
│                                  ▼                     │
│                          ticket-health-bridge hook   │
│                                  │                     │
│                                  ▼                     │
│                          health/dashboard.md 自动更新 │
│                          + AAR 自动触发                │
└────────────────────────────────────────────────────────┘
```

### 三件套整合

#### 1. paperclip-ticket（工单持久化）

**职责**：工单 CRUD + 状态流转 + 审计

**数据模型扩展**（v1.5 新增字段）：
```typescript
interface Ticket {
  // v1.0 字段（保留）
  id: string;
  companyId: string;
  title: string;
  description?: string;
  status: 'backlog' | 'in_progress' | 'review' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  assigneeAgentId?: string;
  executionLockedAt?: Date;
  startedAt?: Date;
  completedAt?: Date;
  createdAt: Date;
  updatedAt: Date;

  // v1.5 新增字段
  customer?: string;           // 客户名（关联 ~/customers/<name>/）
  fdeStage?: string;           // FDE 阶段：land/discover/plan/build/ship/close
  sourceType?: 'fieldbook' | 'aar' | 'manual';
  sourceFile?: string;         // 触发源文件路径
  healthImpact?: 'positive' | 'neutral' | 'negative';
  cancelReason?: string;       // 取消原因
}
```

#### 2. paperclip-heartbeat（心跳调度）

**职责**：每阶段超时监控 + 自动升级

**v1.5 用法**：
```bash
# 添加客户项目心跳（每天检查进度）
/heartbeat add 39-fde "0 9 * * *" \
  --customer dragon-engine-v1 \
  --stage land \
  --timeout 7d

# 添加 AAR 心跳（每周末触发 AAR 提醒）
/heartbeat add 41-csa "0 17 * * 5" \
  --task "review-aar-staleness"
```

#### 3. paperclip-org（组织架构）

**职责**：天龙 agent ↔ 客户角色映射

**v1.5 用法**：
```bash
# 定义客户专属汇报关系
/org report 39-fde dragon-engine-v1  # FDE 向客户方 owner 汇报
/org budget 39-fde --customer dragon-engine-v1 100000  # 给客户分配预算
```

### 工单池目录结构

每个客户目录下新增 `tickets/` 子目录：

```
~/customers/dragon-engine-v1/
└── tickets/
    ├── index.md                # 工单索引（按状态/优先级）
    ├── backlog/                # 待办
    │   ├── T-2026-08-10-12345.md
    │   └── ...
    ├── in-progress/            # 进行中
    ├── review/                 # 复核
    ├── completed/              # 已完成
    └── cancelled/              # 已取消
```

### 工单文件格式

每个工单 = 一个 `.md` 文件：

```markdown
---
ticket_id: T-2026-08-10-12345
title: "dragon-engine-v1 - discover 阶段"
status: backlog | in_progress | review | completed | cancelled
priority: low | medium | high | urgent
assignee_agent: 39-forward-deployed-engineer
created_at: 2026-08-10T14:00:00Z
updated_at: 2026-08-10T14:00:00Z
fde_stage: discover
customer: dragon-engine-v1
source_type: fieldbook
source_file: fieldbook/discover.md
health_impact: positive
---

# T-2026-08-10-12345 - discover 阶段

## 描述
天龙 CEC v1.5 自动创建工单 - dragon-engine-v1 的 FDE discover 阶段。

## 验收标准
- [ ] discover 阶段 fieldbook 完成
- [ ] 客户访谈 ≥ 3 场
- [ ] problem-statement 已提炼
- [ ] assignee agent 确认

## 关联文档
- [fieldbook/discover.md](../../fieldbook/discover.md)
- [problem-statement.md](../../problem-statement.md)

## 历史
- 2026-08-10 14:00 - 工单创建（customer-stage-detector hook）
- 2026-08-10 14:30 - 分配给 39-fde
- 2026-08-10 18:00 - 标记 completed
```

### 两个 hook 协同

#### customer-stage-detector（postToolUse）

**触发时机**：Write/Edit 工具完成后
**监听路径**：`~/customers/<name>/fieldbook/<stage>.md` 或 `~/customers/<name>/aar/*.md`
**动作**：
1. 防抖 5 秒（避免短时间内重复创建）
2. 解析客户 + 阶段
3. 在 `tickets/backlog/` 下创建工单
4. 更新 `tickets/index.md`

**FDE 阶段 → assignee agent 映射**：
```javascript
const stageAgentMap = {
  land: '39-forward-deployed-engineer',
  discover: '39-forward-deployed-engineer',
  plan: '02-architect',
  build: '03-builder',
  ship: '16-devops',
  close: '41-customer-success-architect',
};
```

#### ticket-health-bridge（postToolUse）

**触发时机**：Write/Edit 修改工单 frontmatter 后
**监听路径**：`~/customers/<name>/tickets/**/*.md`
**动作**：

| 状态变化 | 动作 |
|---|---|
| → completed | 更新 `health/dashboard.md` |
| → cancelled | 记录异常到 dashboard.md |
| → review | 准备 AAR 提醒（打印建议） |

### FDE 六阶段完整工单流

```
客户签约
  ↓
land 阶段完成（land.md 创建）
  ↓ customer-stage-detector
  ↓ 创建 T-XXX 工单 → 39-fde
  ↓ ticket-health-bridge（completed 时）
  ↓ 更新 dashboard.md
discover 阶段（discover.md）
  ↓ 自动流转
plan 阶段（plan.md）
  ↓ 自动流转
build 阶段（build.md）
  ↓ 自动流转
ship 阶段（ship.md）
  ↓ 自动流转
close 阶段（AAR.md）
  ↓ 触发 AAR
  ↓ 更新健康度到战略象限
```

### 与天龙既有 agent 联动

| FDE 阶段 | 工单 assignee | 完成时联动 |
|---|---|---|
| land | [[agents/39-forward-deployed-engineer]] | 触发 discover 工单 |
| discover | [[agents/39-forward-deployed-engineer]] + [[agents/32-user-insight]] | 触发 plan 工单 |
| plan | [[agents/02-architect]] | 触发 build 工单 |
| build | [[agents/03-builder]] + [[agents/04-validator]] | 触发 ship 工单 |
| ship | [[agents/16-devops]] + [[agents/07-scribe]] | 触发 close 工单 |
| close | [[agents/41-customer-success-architect]] + [[agents/04-validator]] | 更新 [[account-health-dashboard]] |

### 使用示例

#### 场景 1：天龙自优化（自指项目）

```bash
# Step 1: 客户进场
/customer-onboard dragon-engine-v1

# Step 2: 手动创建 fieldbook（天龙自动监听）
# Write fieldbook/land.md → customer-stage-detector 创建 T-001 工单
# Write fieldbook/discover.md → 自动创建 T-002 工单
# ... 六个阶段全部自动创建工单

# Step 3: 查看工单池
ls ~/customers/dragon-engine-v1/tickets/backlog/
# → T-2026-08-10-12345.md  (discover)
# → T-2026-08-10-12346.md  (plan)

# Step 4: 手动流转工单（标记 completed）
# Edit T-002 frontmatter → status: completed
# → ticket-health-bridge 自动更新 dashboard.md
```

#### 场景 2：真实客户项目

```bash
# Step 1: 客户进场
/customer-onboard acme-corp

# Step 2: 启用 paperclip-heartbeat 监控
/heartbeat add 39-fde "0 9 * * *" --customer acme-corp --timeout 7d

# Step 3: 启用 paperclip-org 预算
/org budget 39-fde --customer acme-corp 500000

# Step 4: 全流程天龙自动跟进
# （天龙 CEC v1.5 自动创建工单 + 自动流转 + 自动触发 AAR）
```

### 失败模式（红线）

- ❌ **手动创建工单时跳过 hook** → 工单与 fieldbook 不同步
- ❌ **hook 失败时不报错** → 工单丢失无声
- ❌ **dashboard.md 被覆盖** → 健康度历史丢失
- ❌ **状态机死锁**（某阶段工单不完成，下一阶段不创建）→ 需超时机制（heartbeat）
- ❌ **工单池目录结构破坏** → 所有天龙联动失效

### 关键技巧

1. **依赖 hook 即可，不要手动维护工单** —— hook 是单一来源
2. **dashboard.md 不要手动改** —— 由 ticket-health-bridge 自动更新
3. **异常工单及时标 cancelled** —— 不影响健康度评分
4. **每阶段完成后立即 mark completed** —— 触发健康度更新

## 天龙岗位升级

| 阶段 | 调用 |
|---|---|
| 工单创建 | customer-stage-detector hook（自动） |
| 状态流转 | `/cec-ticket update <id> --status` |
| 健康度更新 | ticket-health-bridge hook（自动） |
| AAR 触发 | [[agents/41-customer-success-architect]] + `/aar` command |
| 工单池管理 | [[agents/09-04-chief-of-staff]] 协调 |

## 反向链接

- [[09-天龙-CEC-v1.5-paperclip-ticket-打通方案]] — v1.5 整体方案
- [[08-天龙引擎-CEC客户工程中心-蓝图]] — CEC v1.0/v1.5 演进
- [[paperclip-ticket]] — 工单系统基础
- [[paperclip-heartbeat]] — 心跳监控
- [[paperclip-org]] — 组织架构
- [[account-health-dashboard]] — 健康度联动
- [[agents/39-forward-deployed-engineer]] — FDE 子代理
- [[agents/41-customer-success-architect]] — CS 架构师
- [[06-FDE-AAR复盘机制]] — AAR 自动触发