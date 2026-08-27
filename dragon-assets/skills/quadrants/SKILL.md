---
license: UNKNOWN
name: quadrants
description: Quadrants 任务管理系统 - 基于 Eisenhower Matrix 的任务优先级管理。支持四象限分类、批量操作、API集成。触发词：quadrants、任务管理、优先级、eisenhower、四象限
github_repo: wanikua/boluobobo-ai-court-tutorial
github_hash: 9d30b0e45894f305b4dd689c57299fe8f281bd68
last_updated: 2026-04-25
source_type: derived
triggers: ["quadrants", "Quadrants Skill"]
---

# Quadrants Skill

> 来源: [boluobobo-ai-court-tutorial](https://github.com/wanikua/boluobobo-ai-court-tutorial)
> 集成日期: 2026-03-11
> 天龙引擎版本: V8.17

## 核心价值

基于 Eisenhower Matrix（艾森豪威尔矩阵）的任务优先级管理系统，帮助天龙引擎实现智能任务分类和调度。

### 四象限分类

| 象限 | 紧急度 | 重要度 | 行动 |
|------|--------|--------|------|
| **Q1: 立即执行** | 高 (>50) | 高 (>50) | 紧急+重要 → 立即处理 |
| **Q2: 计划安排** | 低 (≤50) | 高 (>50) | 不紧急+重要 → 计划后续 |
| **Q3: 委托他人** | 高 (>50) | 低 (≤50) | 紧急+不重要 → 委托处理 |
| **Q4: 删除放弃** | 低 (≤50) | 低 (≤50) | 不紧急+不重要 → 放弃 |

## 与天龙引擎协同

### 匹配岗位

| 天龙岗位 | 匹配度 | 升级内容 |
|----------|--------|---------|
| **08发布师** | ⭐⭐⭐⭐⭐ | 任务调度优化、优先级可视化 |
| **09-02编排协调师** | ⭐⭐⭐⭐⭐ | 多任务编排、资源分配 |
| **50-01产品策划** | ⭐⭐⭐⭐ | Sprint 任务管理、需求优先级 |
| **00分析师** | ⭐⭐⭐⭐ | 任务分析、优先级评估 |

### 与 TodoWrite 协同

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Quadrants（任务优先级可视化）                       │
│   - 四象限分类 + 优先级评分                                   │
│   - 适合：任务规划、Sprint 管理                               │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: TodoWrite（任务执行追踪）                           │
│   - 任务状态 + 进度追踪                                       │
│   - 适合：日常任务、执行监控                                   │
└─────────────────────────────────────────────────────────────┘
```

## 安装

### 1. 获取 API Key

访问 https://quadrants.ch 获取 API Key。

### 2. 配置环境变量

```bash
# 添加到 ~/.bashrc 或 TOOLS.md
export QUADRANTS_API_URL="https://quadrants.ch"
export QUADRANTS_API_KEY="your-api-key"
```

## 使用方式

### 命令行

```bash
# 列出所有项目
bash skills/quadrants/scripts/quadrants-cli.sh projects

# 获取项目任务
bash skills/quadrants/scripts/quadrants-cli.sh tasks <projectId>

# 获取优先任务（前5个）
bash skills/quadrants/scripts/quadrants-cli.sh priority

# 创建任务
bash skills/quadrants/scripts/quadrants-cli.sh create <projectId> "任务描述" <urgency> <importance>

# 批量创建任务
bash skills/quadrants/scripts/quadrants-cli.sh bulk-create <projectId> '<json-tasks>'

# 完成任务
bash skills/quadrants/scripts/quadrants-cli.sh complete <taskId>

# 更新任务
bash skills/quadrants/scripts/quadrants-cli.sh update <taskId> '{"urgency": 80, "importance": 90}'

# 删除任务
bash skills/quadrants/scripts/quadrants-cli.sh delete <taskId>

# 项目概览
bash skills/quadrants/scripts/quadrants-cli.sh overview <projectId>
```

### Agent 调用示例

```bash
# 08发布师 - 任务调度
[@发布师] 使用 Quadrants 查看当前优先任务

# 09-02编排协调师 - 多任务编排
[@09-02] 使用 Quadrants 创建任务：优化数据库查询，紧急度80，重要度90

# 50-01产品策划 - Sprint 管理
[@产品策划] 使用 Quadrants 查看项目概览
```

### 自然语言映射

| 用户说 | 映射命令 |
|--------|---------|
| "加个任务" / "add a task" | `create` |
| "今天做什么" / "what should I do today" | `priority` |
| "完成了" / "done" / "mark complete" | `complete` |
| "看看项目" / "show projects" | `projects` |
| "任务概览" | `overview` |

## 天龙岗位集成建议

### 心跳集成 (HEARTBEAT.md)

```markdown
# 定期检查优先任务
- 使用 Quadrants priority 命令检查紧急任务
- 提醒用户处理 Q1 象限任务
```

### Cron 定时任务

```bash
# 每天早上 9 点发送任务简报
0 9 * * * bash skills/quadrants/scripts/quadrants-cli.sh priority | mail -s "今日优先任务" user@example.com
```

### 与编排模板协同

```yaml
# 在 bug-fix 编排模板中使用
orchestration: bug-fix
steps:
  - step: 1
    action: 使用 Quadrants 创建任务追踪 bug 修复
    quadrant: Q1  # 紧急+重要
```

## 批量创建任务格式

```json
[
  {"description": "修复登录 bug", "urgency": 90, "importance": 85},
  {"description": "更新文档", "urgency": 30, "importance": 70},
  {"description": "优化性能", "urgency": 50, "importance": 80},
  {"description": "清理代码", "urgency": 20, "importance": 40}
]
```

## 预期收益

| 指标 | 当前 | 集成后 | 提升 |
|------|------|--------|------|
| **任务优先级清晰度** | 基础 | 四象限可视化 | **质的飞跃** |
| **任务分配效率** | 手动 | 自动分类 | **+50%** |
| **团队协作** | 基础 | 统一优先级 | **+30%** |