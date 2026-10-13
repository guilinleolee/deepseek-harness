---
name: cec-ticket
description: 天龙CEC v1.5工单管理——封装paperclip-ticket+hook联动，提供统一CLI
invokable: true
allowed-tools: Read, Write, Edit, Bash, TodoWrite
argument-hint: [子命令] [客户名] [可选参数]
model: sonnet
---
# 天龙 CEC v1.5 工单管理（cec-ticket）

天龙 CEC v1.5 统一工单 CLI。封装 [[paperclip-ticket]] + customer-stage-detector hook + ticket-health-bridge hook + cec-ticket-flow skill，提供客户项目工单的统一操作入口。

## 子命令

```
cec-ticket <子命令> [参数]

子命令:
  list           列出客户工单池
  create         手动创建工单
  status         查看工单详情
  update         更新工单状态
  assign         分配工单
  history        查看工单历史
  dashboard      查看健康度仪表盘
  pool-init      初始化客户工单池
  flow           查看完整工单流
```

## 参数

- **子命令**: $1 (必需)
- **客户名**: $2 (按子命令决定是否必需)
- **工单 ID**: $3 (按子命令决定是否必需)

## 子命令详解

### 1. list - 列出客户工单池

```bash
# 列出某客户所有工单
/cec-ticket list dragon-engine-v1

# 按状态过滤
/cec-ticket list dragon-engine-v1 --status backlog
/cec-ticket list dragon-engine-v1 --status in_progress

# 按优先级过滤
/cec-ticket list dragon-engine-v1 --priority high
```

**输出**：
```
📋 dragon-engine-v1 工单池（12 个）

[backlog] 3 个
  - T-2026-08-10-12345 - discover 阶段 (high) → 39-fde
  - T-2026-08-10-12346 - plan 阶段 (high) → 02-architect
  - T-2026-08-10-12347 - build 阶段 (high) → 03-builder

[in_progress] 2 个
  - T-2026-08-10-12348 - ship 阶段 (urgent) → 16-devops
  - T-2026-08-10-12349 - close 阶段 (medium) → 41-csa

[completed] 1 个
  - T-2026-08-10-12344 - land 阶段 (medium) → 39-fde ✅
```

### 2. create - 手动创建工单

```bash
# 基础创建
/cec-ticket create dragon-engine-v1 "客户访谈补充" \
  --stage discover \
  --priority medium \
  --assignee 39-fde

# 紧急工单
/cec-ticket create dragon-engine-v1 "客户紧急需求" \
  --stage build \
  --priority urgent \
  --assignee 03-builder
```

**注意**：正常流程无需手动创建——customer-stage-detector hook 自动监听 fieldbook/ 变化。

### 3. status - 查看工单详情

```bash
/cec-ticket status T-2026-08-10-12345
```

**输出**：
```
📋 工单详情
================
ID: T-2026-08-10-12345
Title: dragon-engine-v1 - discover 阶段
Status: in_progress
Priority: high
Assignee: 39-fde
FDE Stage: discover
Customer: dragon-engine-v1
Source: fieldbook/discover.md
Created: 2026-08-10 14:00:00
Updated: 2026-08-10 14:30:00
```

### 4. update - 更新工单状态

```bash
# 流转到 in_progress
/cec-ticket update T-2026-08-10-12345 --status in_progress

# 流转到 review
/cec-ticket update T-2026-08-10-12345 --status review

# 流转到 completed（自动触发 ticket-health-bridge）
/cec-ticket update T-2026-08-10-12345 --status completed

# 流转到 cancelled（自动记录异常）
/cec-ticket update T-2026-08-10-12345 --status cancelled --reason "客户取消"
```

**联动**：
- → review: 准备 AAR 提醒
- → completed: 自动更新 [[account-health-dashboard]]
- → cancelled: 记录到 dashboard.md 异常项

### 5. assign - 分配工单

```bash
# 分配给指定 agent
/cec-ticket assign T-2026-08-10-12345 39-fde

# 重新分配
/cec-ticket assign T-2026-08-10-12345 02-architect
```

**联动**：可触发 [[paperclip-heartbeat]] 创建心跳监控。

### 6. history - 查看工单历史

```bash
/cec-ticket history T-2026-08-10-12345
```

**输出**：
```
📜 工单历史
================
2026-08-10 14:00 - 创建（customer-stage-detector hook）
2026-08-10 14:30 - 分配给 39-fde
2026-08-10 16:00 - 状态变更：backlog → in_progress
2026-08-10 18:00 - 状态变更：in_progress → completed
2026-08-10 18:00 - dashboard.md 自动更新
```

### 7. dashboard - 查看健康度仪表盘

```bash
/cec-ticket dashboard dragon-engine-v1
```

**输出**：
```
📊 dragon-engine-v1 健康度
================================
最近 3 次评分：

| 日期       | 使用 | 满意 | 续约 | 扩单 | 总分  | 象限  |
|------------|------|------|------|------|-------|-------|
| 2026-08-10 | 8.5  | 9.5  | 9.75 | 7.0  | 34.75 | 战略  |
| 2026-08-15 | 9.0  | 9.5  | 9.75 | 8.0  | 36.25 | 战略  |

工单进度：
- 完成：4/6 (67%)
- 进行中：1/6
- 待办：1/6
```

### 8. pool-init - 初始化客户工单池

```bash
# 初始化某客户的工单池（仅首次需要）
/cec-ticket pool-init dragon-engine-v1
```

**动作**：
1. 在 `~/customers/<name>/tickets/` 下创建子目录
2. 创建 `index.md`
3. 触发 [[paperclip-org]] 设定客户方汇报关系

### 9. flow - 查看完整工单流

```bash
/cec-ticket flow dragon-engine-v1
```

**输出**：
```
🌊 dragon-engine-v1 FDE 工单流
================================

[✅ land] T-...-12344 (2026-08-10 13:00)
   ↓
[🔄 discover] T-...-12345 (2026-08-10 14:00, in_progress)
   ↓
[⏳ plan] T-...-12346 (backlog)
   ↓
[⏳ build] T-...-12347 (backlog)
   ↓
[⏳ ship] T-...-12348 (backlog)
   ↓
[⏳ close] T-...-12349 (backlog)
```

## 执行流程

### 主流程：list（默认）

1. 验证客户目录存在（`~/customers/$2/`）
2. 检查工单池是否初始化（`tickets/` 目录）
3. 扫描所有 `tickets/*/` 下的 `.md` 文件
4. 按状态分组展示
5. 显示健康度简报

### 主流程：update

1. 验证工单存在
2. 解析 frontmatter
3. 更新 status 字段 + updated_at
4. 触发 ticket-health-bridge hook（自动）
5. 显示联动结果

### 主流程：pool-init

1. 验证客户目录存在
2. 创建 `tickets/` 子目录结构
3. 生成 `index.md`
4. 可选：调用 [[paperclip-org]] 设定汇报关系

## 与既有 command 的关系

| 既有 command | CEC v1.5 联动 |
|---|---|
| [[agents/38-sales-manager]] | /pre-sales-survey → 创建客户后调用 /cec-ticket pool-init |
| [[agents/39-forward-deployed-engineer]] | /fde-flow → 自动触发 customer-stage-detector |
| [[agents/41-customer-success-architect]] | /aar → 触发 close 阶段工单 |

## 与 hook 联动

| 操作 | 触发的 hook |
|---|---|
| Write/Edit fieldbook/*.md | customer-stage-detector（创建工单） |
| Write/Edit tickets/**/*.md | ticket-health-bridge（联动 dashboard） |

## 在天龙 memory 追加

```
## [YYYY-MM-DD] cec-ticket | $CUSTOMER - $ACTION
- 工单: $TICKET_ID
- 操作: $ACTION
- 联动: hook 触发结果
```

## 使用示例

```bash
# 完整工作流
/cec-ticket pool-init dragon-engine-v1
# → 写 fieldbook/land.md → hook 自动创建工单
/cec-ticket list dragon-engine-v1
# → 查看工单池

# 流转工单
/cec-ticket update T-2026-08-10-12345 --status completed
# → ticket-health-bridge 自动更新 dashboard

# 健康度检查
/cec-ticket dashboard dragon-engine-v1
# → 查看战略象限
```

## 反向链接

- [[09-天龙-CEC-v1.5-paperclip-ticket-打通方案]] — v1.5 整体方案
- [[08-天龙引擎-CEC客户工程中心-蓝图]] — CEC 演进
- [[cec-ticket-flow]] — v1.5 skill
- [[paperclip-ticket]] — 工单系统基础
- [[paperclip-heartbeat]] — 心跳监控
- [[paperclip-org]] — 组织架构
- [[account-health-dashboard]] — 健康度联动
- [[agents/39-forward-deployed-engineer]] — FDE 子代理
- [[agents/41-customer-success-architect]] — CS 架构师
- [[agents/09-04-chief-of-staff]] — 编排协调