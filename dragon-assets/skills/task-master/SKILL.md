---
license: UNKNOWN
name: task-master
description: PRD自动解析 + 智能任务管理。将产品需求文档自动转换为可执行任务列表，支持依赖追踪、状态管理和实时研究。
github_repo: eyaltoledano/claude-task-master
github_hash: c0c98d367c55296bfe69e65680625b6db437af02
last_updated: 2026-04-25
source_type: derived
argument-hint: PRD文档路径或需求描述
triggers: ["task master", "Task Master - PRD智能解析与任务管理"]
---

# Task Master - PRD智能解析与任务管理

## 🎯 核心价值

填补天龙引擎在**PRD自动解析**的关键空白，实现从需求文档到可执行任务列表的自动化转换。

## 📊 能力矩阵

| 能力 | 描述 | 天龙岗位受益 |
|------|------|-------------|
| **PRD解析** | 自动提取需求 → 生成任务列表 | 00分析师、50-01产品策划 |
| **任务追踪** | pending/in-progress/done状态管理 | 03构建师、08发布师 |
| **依赖处理** | 子任务创建 + 依赖关系图 | 02架构师 |
| **实时研究** | Tavily集成 + 项目上下文 | 01调研师 |
| **跨标签移动** | 任务重组和优先级调整 | 09-02编排协调师 |

## 🚀 安装方式

### 方式1: MCP集成（推荐）

```json
// .claude/mcp.json 或 .cursor/mcp.json
{
  "mcpServers": {
    "task-master": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "your-key",
        "TASK_MASTER_TOOLS": "standard"
      }
    }
  }
}
```

### 方式2: CLI全局安装

```bash
npm install -g task-master-ai
task-master init
```

### 方式3: 项目本地安装

```bash
npm install task-master-ai
npx task-master init
```

## 📋 核心命令

### 项目初始化

```bash
# 初始化项目
task-master init

# 创建示例PRD
task-master init --with-sample
```

### PRD解析

```bash
# 解析PRD文件生成任务
task-master parse-prd docs/prd.md

# 从URL解析PRD
task-master parse-prd --url https://...

# 解析并设置优先级
task-master parse-prd docs/prd.md --priority high
```

### 任务管理

```bash
# 列出所有任务
task-master list

# 列出特定状态任务
task-master list --tag pending
task-master list --tag in-progress
task-master list --tag done

# 查看下一个任务
task-master next

# 查看特定任务
task-master show 1,3,5

# 查看任务详情
task-master show 1 --verbose
```

### 任务操作

```bash
# 移动任务到新状态
task-master move --id=5 --to-tag=in-progress
task-master move --id=5 --to-tag=done

# 批量移动
task-master move --from=pending --to-tag=in-progress --ids=1,2,3

# 设置任务优先级
task-master set-priority --id=5 --level=high

# 添加子任务
task-master add-subtask --parent=5 --title="实现登录API"
```

### 实时研究

```bash
# 研究特定主题（结合项目上下文）
task-master research "React最佳实践"

# 研究并关联到任务
task-master research "OAuth2实现" --task-id=5
```

## ⚙️ 配置选项

### 工具加载模式

```bash
# 环境变量设置
TASK_MASTER_TOOLS=all       # 完整36个工具
TASK_MASTER_TOOLS=standard  # 标准15个工具（推荐）
TASK_MASTER_TOOLS=core      # 核心7个工具
```

### 核心工具列表（7个）

| 工具 | 功能 |
|------|------|
| `init` | 项目初始化 |
| `parse-prd` | PRD解析 |
| `list` | 任务列表 |
| `next` | 下一个任务 |
| `show` | 任务详情 |
| `move` | 状态移动 |
| `research` | 实时研究 |

## 🔄 与天龙引擎协同

### 工作流集成

```yaml
天龙Task-Master工作流:
  1. [@分析师] 分析需求 → 编写PRD
     # 使用批判性思维6大维度验证需求

  2. /task-master parse-prd docs/prd.md
     # 自动生成任务列表

  3. [@架构师] 审核任务依赖
     # 调整任务顺序和依赖关系

  4. [@构建师] 逐任务执行
     # task-master next → 执行 → task-master move

  5. [@验证师] 验收任务
     # task-master move --to-tag=done

  6. [@发布师] 发布汇总
     # task-master list --tag=done → 发布报告
```

### 与现有Skill协同

| 天龙Skill | task-master协同方式 |
|-----------|-------------------|
| **paperclip-ticket** | task-master作为前端，paperclip作为后端存储 |
| **deep-research** | task-master research调用deep-research方法论 |
| **planning-with-files** | task-master输出到task_plan.md |
| **TodoWrite** | task-master任务同步到TodoWrite |

## 📝 使用示例

### 示例1: 从需求描述创建任务

```bash
# 用户描述需求
"我想做一个用户认证系统，支持邮箱登录、OAuth和JWT"

# 天龙调用
[@分析师] 解析需求并生成PRD
/task-master parse-prd --from-description "用户认证系统..."

# 输出任务列表
## Task 1: 设计认证系统架构 (high priority)
## Task 2: 实现邮箱登录API
## Task 3: 集成OAuth提供商
## Task 4: 实现JWT token管理
## Task 5: 编写认证中间件
## Task 6: 单元测试和E2E测试
```

### 示例2: 任务依赖管理

```bash
# 查看任务依赖
task-master show 3 --dependencies

# 输出
Task 3: 集成OAuth提供商
  - 依赖: Task 1 (架构设计)
  - 依赖: Task 2 (邮箱登录API)
  - 子任务:
    - 3.1 配置Google OAuth
    - 3.2 配置GitHub OAuth
    - 3.3 实现OAuth回调处理
```

### 示例3: 实时研究

```bash
# 研究最佳实践
task-master research "JWT安全最佳实践" --task-id=4

# 输出
## 研究结果: JWT安全最佳实践
1. 使用短期token (15-30分钟)
2. 实现refresh token轮换
3. 存储在httpOnly cookie中
4. 验证token签名和过期时间
5. 实现token黑名单机制

关联任务: Task 4 - JWT token管理
建议操作: 更新任务描述添加安全要求
```

## 🔧 高级配置

### 自定义任务模板

```json
// .task-master/templates.json
{
  "taskTemplate": {
    "fields": ["title", "description", "priority", "assignee", "tags"],
    "required": ["title", "description"],
    "defaults": {
      "priority": "medium",
      "tags": ["feature"]
    }
  }
}
```

### 集成CI/CD

```yaml
# .github/workflows/task-sync.yml
name: Sync Tasks
on:
  issues:
    types: [opened, closed]

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npx task-master sync --from=github-issues
```

## 📊 预期收益

| 指标 | 手动方式 | task-master | 提升 |
|------|---------|-------------|------|
| **PRD解析时间** | 30分钟 | 3分钟 | **-90%** |
| **任务遗漏率** | 20% | 5% | **-75%** |
| **任务追踪效率** | 手动Excel | 自动化 | **质的飞跃** |
| **需求变更响应** | 1小时 | 5分钟 | **-92%** |

## 🔗 相关资源

- **GitHub**: https://github.com/eyaltoledano/claude-task-master
- **NPM**: https://www.npmjs.com/package/task-master-ai
- **文档**: https://task-master.dev/docs

---

**版本**: v1.0.0
**创建时间**: 2026-03-27
**集成版本**: 天龙引擎 V8.57