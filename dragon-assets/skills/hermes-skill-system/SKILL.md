---
license: UNKNOWN
triggers: ["hermes skill system", "hermes-skill-system"]
---
# hermes-skill-system

## 元信息

```yaml
name: hermes-skill-system
description: Hermes自改进技能系统 - 自动创建、自我优化、Skills Hub市场集成
version: 1.0.0
category: autonomous-ai-agents
source: NousResearch/hermes-agent
stars: 21.7k
```

## 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ Hermes Skills System 自改进闭环                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  触发条件                                                    │
│  ├── 复杂任务后 (5+ tool calls)                            │
│  ├── 用户纠正后 (当用户教你时)                              │
│  └── 自然语言请求 ("创建技能处理X")                         │
│                      ↓                                      │
│  技能创建                                                    │
│  ├── 分析任务模式                                           │
│  ├── 生成SKILL.md模板                                       │
│  └── 写入 ~/.hermes/skills/                                │
│                      ↓                                      │
│  技能自我改进                                               │
│  ├── 使用中学习改进                                         │
│  ├── 用户反馈驱动优化                                       │
│  └── 跨任务技能合并                                         │
│                      ↓                                      │
│  Skills Hub市场                                             │
│  ├── 官方/社区技能浏览                                      │
│  ├── GitHub/skills-sh/clawhub多源                         │
│  └── 安全扫描安装                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## SKILL.md格式规范

```yaml
---
name: my-custom-skill
description: Brief description under 100 chars
version: 1.0.0
platforms: [macos, linux]  # Optional
metadata:
  hermes:
    tags: [python, automation]
    category: devops
    triggers:
      - "when user asks about X"
      - "complex task pattern Y"
---
# Skill Title

## When to Use
When to invoke this skill (2-3 sentences).

## Procedure
Step-by-step instructions:
1. First step
2. Second step
3. Third step

## Pitfalls
Common mistakes to avoid:
- Pitfall 1
- Pitfall 2

## Verification
How to verify the skill worked correctly.
```

## 渐进式加载 (Progressive Disclosure)

```yaml
Level 0: 技能列表 (名称+描述) ~3k tokens
Level 1: 完整内容+元数据
Level 2: 特定参考文件
```

## 触发自动创建

```python
# 检测条件
if tool_calls >= 5 and not_existing_skill():
    suggest_skill_creation()
elif user_correction and can_generalize():
    extract_pattern_and_create_skill()
```

## Skills Hub命令

```bash
# 浏览技能
hermes skills browse

# 搜索技能
hermes skills search kubernetes

# 安装技能
hermes skills install nousresearch/hermes-agent/skills/github
hermes skills install github:owner/repo/skills/skill-name

# 审计技能安全
hermes skills audit
```

## 天龙引擎集成

### 适用岗位
- **09-02 编排协调师** - 子Agent编排技能创建
- **01调研师** - 研究技能自动生成
- **07记录师** - 记忆技能优化

### 调用方式

```bash
# 手动触发技能创建
[@编排协调师] 创建一个处理API文档生成的技能
[@编排协调师] 从这次复杂任务中提取可复用技能

# 浏览Skills Hub
[@编排协调师] 搜索GitHub集成相关技能
[@编排协调师] 安装NousResearch的autonomous-ai-agents技能

# 技能管理
[@编排协调师] 查看已安装技能列表
[@编排协调师] 审计所有技能安全性
```

## 技能自动创建流程

```python
# 1. 模式检测
def detect_pattern(task_history):
    """从任务历史中检测可复用的模式"""
    # 分析: 重复操作序列
    # 检测: 条件分支和异常处理
    # 提取: 核心步骤和参数

# 2. 技能生成
def generate_skill(pattern, context):
    """生成SKILL.md格式的技能文件"""
    skill = {
        "name": infer_name(pattern),
        "description": summarize_purpose(pattern),
        "triggers": extract_triggers(pattern),
        "procedure": formalize_steps(pattern),
        "pitfalls": extract_warnings(pattern),
    }
    return format_skill_md(skill)

# 3. 自我改进
def improve_skill(skill_name, feedback):
    """使用反馈持续改进技能"""
    # 合并相似技能
    # 优化触发条件
    # 更新步骤和警告
```

## 与现有系统协同

| 天龙组件 | Hermes协同 | 效果 |
|---------|-----------|------|
| **V8.5 Autogenesis** | 技能自改进 | 手动→自动演化 |
| **V8.6 claude-mem** | 技能记忆 | 持久化+检索 |
| **V8.74 Supermemory** | 跨平台技能 | 事实提取+矛盾解决 |
| **V8.75 OpenSpace** | Skills Hub | 云端技能市场 |

## 核心命令

```bash
# 创建技能 (自然语言)
create-skill "当用户要求分析代码时，自动执行以下步骤..."

# 浏览市场
browse-skills --source github --category autonomous-ai-agents

# 安装技能
install-skill nousresearch/hermes-agent/skills/github

# 审计安全
audit-skills --all

# 技能自我改进
improve-skill <skill-name> --feedback "这个步骤可以优化为..."
```

## 预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| 技能复用率 | 30% | 80% | +167% |
| 新技能创建时间 | 30分钟 | 3分钟 | -90% |
| 任务自动化覆盖率 | 60% | 90% | +50% |
