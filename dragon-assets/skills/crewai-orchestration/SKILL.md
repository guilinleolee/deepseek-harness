---
license: UNKNOWN
github_repo: joaomdmoura/crewAI
github_hash: cb46a1c4babef8c51db6499d7a81f2c36b01bdef
last_updated: 2026-04-25
source_type: derived
triggers: ["crewai orchestration", "CrewAI 多Agent协作框架集成"]
---
# CrewAI 多Agent协作框架集成

## 技能描述
CrewAI 多Agent协作框架集成，增强天龙09-02编排协调师能力，支持复杂多Agent工作流编排。

---

## 触发词
- `crewai`
- `多agent协作`
- `agent团队`
- `工作流编排`

---

## 核心能力

### 1. Agent定义
- 角色和目标设定
- 背景故事配置
- 工具绑定
- LLM模型选择

### 2. Task任务系统
- 任务描述和预期输出
- Agent分配
- 任务依赖管理
- 输出格式定义

### 3. Crew团队编排
- 顺序执行（Sequential）
- 层级执行（Hierarchical）
- 自定义流程

### 4. Tools工具集成
- 自定义工具创建
- 第三方工具绑定
- 工具结果传递

---

## 与天龙引擎协作

### 协作架构

```
┌─────────────────────────────────────────────────────────────┐
│                    天龙引擎 + CrewAI 协作                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户请求                                                    │
│     │                                                       │
│     ▼                                                       │
│  ┌─────────────┐                                            │
│  │ 09-02 编排  │ → 工作流设计、任务分发                      │
│  │   协调师    │                                            │
│  └──────┬──────┘                                            │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              CrewAI 执行层                           │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐             │    │
│  │  │ Agent 1 │  │ Agent 2 │  │ Agent 3 │             │    │
│  │  │ (分析师) │  │ (构建师) │  │ (验证师) │             │    │
│  │  └────┬────┘  └────┬────┘  └────┬────┘             │    │
│  │       │            │            │                   │    │
│  │       └────────────┼────────────┘                   │    │
│  │                    ▼                                 │    │
│  │            结果聚合和交付                            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 路由策略

```yaml
# 何时使用 CrewAI
use_crewai_when:
  - 多个Agent需要并行执行
  - 任务有明确的依赖关系
  - 需要专业化分工（分析→开发→测试）
  - 输出需要多Agent协作生成

# 何时使用天龙原生
use_dragon_when:
  - 单Agent任务
  - 需要TDD铁律
  - 复杂批判性思维
  - 需要审查门禁
```

---

## 代码示例

### Agent定义

```python
from crewai import Agent, Task, Crew

# 定义天龙分析师Agent
analyst_agent = Agent(
    role='业务分析师',
    goal='分析需求并拆解为可执行任务',
    backstory="""你是天龙引擎的首席分析师，擅长问题拆解和需求分析。
    你遵循CREATE框架，确保每个需求都被完整理解。""",
    verbose=True,
    allow_delegation=False,
    llm='claude-3-5-sonnet'
)

# 定义天龙构建师Agent
builder_agent = Agent(
    role='软件工程师',
    goal='根据规范编写高质量代码',
    backstory="""你是天龙引擎的首席构建师，遵循TDD铁律。
    你先写测试，再写实现代码。""",
    verbose=True,
    allow_delegation=True,
    llm='claude-3-5-sonnet'
)

# 定义天龙验证师Agent
validator_agent = Agent(
    role='QA工程师',
    goal='验证代码质量和功能正确性',
    backstory="""你是天龙引擎的首席验证师，负责极端找茬。
    你测试边界条件、异常流程和性能极限。""",
    verbose=True,
    allow_delegation=False,
    llm='claude-3-5-sonnet'
)
```

### Task任务定义

```python
# 分析任务
analysis_task = Task(
    description='分析用户需求：{requirements}',
    expected_output='结构化的需求分析文档，包含用户故事和验收标准',
    agent=analyst_agent
)

# 开发任务
development_task = Task(
    description='根据需求分析实现功能',
    expected_output='通过所有测试的代码实现',
    agent=builder_agent,
    context=[analysis_task]  # 依赖分析任务
)

# 验证任务
validation_task = Task(
    description='验证实现是否符合需求',
    expected_output='测试报告和质量检查结果',
    agent=validator_agent,
    context=[development_task]  # 依赖开发任务
)
```

### Crew团队编排

```python
# 创建工作流团队
dev_crew = Crew(
    agents=[analyst_agent, builder_agent, validator_agent],
    tasks=[analysis_task, development_task, validation_task],
    process=Process.sequential,  # 顺序执行
    verbose=True
)

# 执行工作流
result = dev_crew.kickoff(inputs={
    'requirements': '实现用户登录功能，支持邮箱和手机号登录'
})

print(result)
```

---

## 安装与配置

### 安装

```bash
pip install crewai crewai-tools
```

### 配置

```bash
# 设置API密钥
export OPENAI_API_KEY=your-key
export ANTHROPIC_API_KEY=your-key
```

### 与天龙引擎集成

```yaml
# .claude/crewai-config.yaml
crewai:
  enabled: true
  default_process: sequential
  agents:
    - name: 天龙分析师
      id: analyst
      role: 需求分析
      llm: claude-3-5-sonnet

    - name: 天龙构建师
      id: builder
      role: 代码实现
      llm: claude-3-5-sonnet

    - name: 天龙验证师
      id: validator
      role: 质量验证
      llm: claude-3-5-sonnet
```

---

## 使用方式

### 自然语言触发

```bash
# 编排多Agent任务
[@09-02] 使用CrewAI编排用户认证功能开发流程

# 定义Agent团队
/crewai-create-team --agents "分析师,构建师,验证师"

# 执行工作流
/crewai-run --workflow "用户登录功能"
```

### 命令行调用

```bash
# 启动CrewAI工作流
crewai run --config .claude/crewai-config.yaml
```

---

## 预期收益

| 指标 | 当前 | CrewAI集成后 | 提升 |
|------|------|-------------|------|
| **并行任务效率** | 基准 | +150% | 多Agent并行执行 |
| **工作流可追溯** | 低 | 高 | 完整日志记录 |
| **任务协调** | 手动 | 自动 | +100% |

---

## 与天龙岗位映射

| CrewAI概念 | 天龙对应 | 说明 |
|-----------|---------|------|
| Agent | 天龙岗位 | 角色定义 |
| Task | 天龙任务 | 具体工作 |
| Crew | 09-02编排协调师 | 团队编排 |
| Process | 工作流模式 | 执行顺序 |
| Tools | 天龙Skills | 能力扩展 |

---

**版本**: v1.0
**来源**: [joaomdmoura/crewAI](https://github.com/joaomdmoura/crewAI)
**最后更新**: 2026-03-09