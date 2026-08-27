---
license: UNKNOWN
name: autogenesis
description: |
github_repo: SkyworkAI/DeepResearchAgent
github_hash: d4376664b885eb1db310aace66173911703d0a7e
last_updated: 2026-04-25
source_type: derived
triggers: ["autogenesis", "Autogenesis - 自演化协议"]
---

# Autogenesis - 自演化协议

基于 [SkyworkAI/DeepResearchAgent](https://github.com/SkyworkAI/DeepResearchAgent) 的自演化协议。

## 核心理念

> 解耦"什么演化"和"如何演化"，让Agent系统能够自我优化。

## 双层协议架构

```
┌─────────────────────────────────────────────────────────────┐
│ SEPL (Self Evolution Protocol Layer) - 自演化协议层          │
│ 闭环接口：提议 → 评估 → 提交改进（支持回滚）                  │
├─────────────────────────────────────────────────────────────┤
│ RSPL (Resource Substrate Protocol Layer) - 资源协议层        │
│ Prompts | Agents | Tools | Environments | Memory            │
│ 作为版本化资源，有明确的状态、生命周期和版本接口              │
└─────────────────────────────────────────────────────────────┘
```

## 迭代循环

```yaml
Act: Agent使用LLM和可用工具产生行动/输出
Observe: 捕获结果、轨迹、中间推理和环境反馈
Optimize: 使用优化器更新prompts/solutions/variables
Remember: 将摘要/洞察/记录持久化到memory
```

## 核心组件

### 1. 资源注册表（Registry）

```python
# 所有资源都是协议注册的版本化资源
MEMORY_SYSTEM = Registry("memory_system")
TOOL = Registry("tool")
ENVIRONMENT = Registry("environment")
AGENT = Registry("agent")
PROMPT = Registry("prompt")
```

### 2. 优化器（Optimizers）

| 优化器 | 适用场景 | 原理 |
|--------|---------|------|
| **TextGrad** | 提示词优化 | 文本梯度下降 |
| **Reflection** | 策略优化 | 自我反思改进 |
| **GRPO** | 强化学习 | 群体相对策略优化 |
| **Reinforce++** | 策略优化 | 策略梯度方法 |

### 3. 记忆系统（Memory）

```yaml
记忆类型:
  Session Memory: 会话级记忆
  Event Memory: 事件记录
  Long-term Memory: 持久化知识

记忆操作:
  Store: 存储经验/洞察
  Retrieve: 检索相关记忆
  Summarize: 总结关键信息
```

## 与天龙引擎协同

### 与V7.1持续改进循环协同

| Autogenesis | 天龙V7.1 | 协同效果 |
|-------------|----------|---------|
| **迭代循环** | lessons.md机制 | 自动记录优化经验 |
| **Remember** | Claudeception | 技能自动进化 |
| **Optimize** | 无 | **新增能力** |
| **版本追踪** | 无 | **新增能力** |

### 与V7.4批判性思维协同

| Autogenesis | 天龙V7.4 | 协同效果 |
|-------------|----------|---------|
| **Observe** | 魔鬼代言人 | 双重验证机制 |
| **评估** | 可证伪性 | 优化质量保障 |

### 与天龙岗位映射

| 天龙岗位 | Autogenesis能力 | 升级效果 |
|----------|----------------|---------|
| **01调研师** | Reflection优化 | 调研方法自动进化 |
| **02架构师** | TextGrad优化 | 设计决策持续优化 |
| **07记录师** | Memory系统 | 知识管理标准化 |
| **所有Agent** | 自演化协议 | **能力自我提升** |

## 使用方式

### 基础使用

```bash
# 启动自演化优化
/autogenesis

# 优化指定Agent
[@调研师] 自演化优化

# 自然语言触发
帮我优化这个Agent的提示词
让这个Agent自我进化
```

### TextGrad提示词优化

```python
# 自动提取可优化变量
# 执行Agent任务
# 计算损失
# 生成梯度
# 更新提示词
```

### 优化参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `optimization_steps` | 3 | 优化迭代次数 |
| `optimizer_model` | gpt-4o | 优化器使用的模型 |
| `require_grad` | True | 标记可优化变量 |

## 优化器详解

### TextGrad优化器

```yaml
工作原理:
  1. 变量提取: 从prompt对象中提取require_grad=True的变量
  2. 执行Agent: 使用当前提示词运行Agent
  3. 计算损失: 基于执行结果和任务目标评估
  4. 生成梯度: 将损失反馈作为梯度
  5. 更新提示词: 使用文本梯度下降优化

适用场景:
  - 系统提示词优化
  - Agent消息模板优化
  - 任务描述优化
```

### Reflection优化器

```yaml
工作原理:
  1. 执行任务并记录轨迹
  2. 自我反思识别问题
  3. 生成改进建议
  4. 应用改进并验证

适用场景:
  - 策略优化
  - 工作流改进
  - 错误修复
```

## 输出结构

```
~/workdir/optimization_logs/
├── step_1/
│   ├── execution_result.json    # 执行结果
│   ├── loss_calculation.json    # 损失计算
│   └── gradient.json            # 梯度信息
├── step_2/
│   └── ...
└── summary.json                 # 优化摘要
```

## 注意事项

### 提示词变量标记

```yaml
# 在提示词模板中标记可优化变量
- name: agent_context_rules
  type: system_prompt_module
  description: Agent上下文规则
  require_grad: true  # ✅ 设置为true才会被优化
  template: null
  variables: AGENT_CONTEXT_RULES
```

### 成本考虑

每次优化迭代调用：
- Agent执行：使用Agent模型
- 损失计算：使用优化器模型
- 提示词更新：使用优化器模型

推荐优化步骤数：3-4次

## 设计目标

- **可组合**：添加/替换agents、tools、environments、memory无需重写
- **可检查**：结构化轨迹和记忆事件便于分析失败和改进步骤
- **可演化**：显式优化器+持久化记忆支持迭代优化

## 版本历史

| 版本 | 变更 |
|------|------|
| v1.0.0 | 初始版本，融合自演化协议 |