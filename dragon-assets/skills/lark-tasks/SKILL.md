---
license: UNKNOWN
triggers: ["lark tasks", "Lark Tasks Skill"]
---
# Lark Tasks Skill

> 飞书/Lark 任务操作能力 - 任务/任务列表/子任务/评论管理

## 核心能力

| 能力 | 功能 | 使用场景 |
|------|------|---------|
| **任务列表管理** | 创建/更新/删除任务列表 | 项目管理 |
| **任务管理** | 创建/更新/删除任务 | 任务追踪 |
| **子任务管理** | 创建/管理子任务 | 任务拆分 |
| **评论管理** | 添加/删除评论 | 任务讨论 |

## 安装要求

```bash
npm install -g openclaw
node --version  # >= 22
```

## 配置

### 飞书开放平台权限

- `task:task` - 任务操作
- `task:task:readonly` - 任务只读
- `task:list` - 任务列表操作

### 环境变量

```bash
export LARK_APP_ID="your_app_id"
export LARK_APP_SECRET="your_app_secret"
```

## 命令参考

### 任务列表管理

```bash
# 创建任务列表
/lark-tasks create-list --name "V8.33开发任务" --description "版本开发任务追踪"

# 获取任务列表
/lark-tasks list-lists

# 更新任务列表
/lark-tasks update-list --list-id "list_xxx" --name "新名称"

# 删除任务列表
/lark-tasks delete-list --list-id "list_xxx"
```

### 任务管理

```bash
# 创建任务
/lark-tasks create --list-id "list_xxx" \
  --title "完成API文档" \
  --description "编写用户认证模块的API文档" \
  --due-date "2026-03-20" \
  --assignees '["ou_xxx"]'

# 更新任务
/lark-tasks update --task-id "task_xxx" \
  --status "completed"

# 删除任务
/lark-tasks delete --task-id "task_xxx"

# 查询任务
/lark-tasks query --list-id "list_xxx" \
  --status "in_progress" \
  --assignee "ou_xxx"
```

### 子任务管理

```bash
# 创建子任务
/lark-tasks create-subtask --task-id "task_xxx" \
  --title "编写登录接口文档"

# 完成子任务
/lark-tasks complete-subtask --subtask-id "sub_xxx"

# 删除子任务
/lark-tasks delete-subtask --subtask-id "sub_xxx"
```

### 评论管理

```bash
# 添加评论
/lark-tasks comment --task-id "task_xxx" \
  --content "已完成初稿，请审核"

# 删除评论
/lark-tasks delete-comment --comment-id "cmt_xxx"
```

## Python API

```python
from lark_tasks import LarkTasks

# 初始化
tasks = LarkTasks(app_id, app_secret)

# 创建任务列表
list_id = tasks.create_list(
    name="V8.33开发任务",
    description="版本开发任务追踪"
)

# 创建任务
task_id = tasks.create(
    list_id=list_id,
    title="完成API文档",
    description="编写用户认证模块的API文档",
    due_date="2026-03-20",
    assignees=["ou_xxx"],
    priority="high",
    tags=["文档", "API"]
)

# 创建子任务
tasks.create_subtask(
    task_id=task_id,
    title="编写登录接口文档"
)

# 更新任务状态
tasks.update(task_id=task_id, status="completed")

# 查询任务
results = tasks.query(
    list_id=list_id,
    status="in_progress",
    assignee="ou_xxx"
)

# 添加评论
tasks.comment(task_id=task_id, content="已完成初稿，请审核")

# 获取任务详情
task_detail = tasks.get(task_id=task_id)
```

## 天龙岗位映射

| 岗位 | 使用场景 | 匹配度 |
|------|---------|--------|
| **50-01 产品策划** | 需求任务管理、迭代追踪 | ⭐⭐⭐⭐⭐ |
| **90-01 人力资源总监** | 招聘任务管理、入职任务 | ⭐⭐⭐⭐⭐ |
| **08 发布师** | 发布任务清单、里程碑追踪 | ⭐⭐⭐⭐ |
| **03 构建师** | 开发任务追踪 | ⭐⭐⭐⭐ |

## 使用示例

### 示例1：迭代任务管理

```python
# 创建迭代任务列表
sprint_list = tasks.create_list(
    name="Sprint 2026-03",
    description="3月份迭代任务"
)

# 批量创建任务
sprint_tasks = [
    {"title": "用户登录功能", "assignee": "张三", "due": "2026-03-15"},
    {"title": "数据导出功能", "assignee": "李四", "due": "2026-03-18"},
    {"title": "性能优化", "assignee": "王五", "due": "2026-03-20"}
]

for t in sprint_tasks:
    tasks.create(list_id=sprint_list, **t)

# 获取迭代进度
progress = tasks.get_progress(list_id=sprint_list)
print(f"完成率: {progress['completion_rate']}%")
```

### 示例2：发布任务清单

```python
# 创建发布任务清单
release_list = tasks.create_list(name="V8.33发布清单")

# 添加发布任务
release_tasks = [
    {"title": "代码审查", "section": "开发"},
    {"title": "测试验证", "section": "测试"},
    {"title": "文档更新", "section": "文档"},
    {"title": "发布公告", "section": "运营"}
]

for t in release_tasks:
    task_id = tasks.create(list_id=release_list, title=t["title"])
    tasks.add_section(task_id=task_id, name=t["section"])
```

### 示例3：个人任务同步

```python
# 从本地TODO同步到飞书
tasks.sync_from_local(
    list_id="list_xxx",
    todo_file="./TODO.md",
    mapping={
        "P0": "high",
        "P1": "medium",
        "P2": "low"
    }
)
```

## 任务状态

| 状态 | 说明 |
|------|------|
| `todo` | 待办 |
| `in_progress` | 进行中 |
| `completed` | 已完成 |
| `cancelled` | 已取消 |

## 任务优先级

| 优先级 | 说明 |
|--------|------|
| `high` | 高优先级 |
| `medium` | 中优先级 |
| `low` | 低优先级 |

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| 1.0.0 | 2026-03-14 | 初始版本，支持任务列表/任务/子任务/评论管理 |