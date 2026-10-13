---
license: UNKNOWN
triggers: ["dspy minimax config", "DSPy MiniMax 配置技能 (V8.63)"]
---
# DSPy MiniMax 配置技能 (V8.63)

## 概述

本技能提供 MiniMax 大模型与 DSPy 的集成配置，支持声明式 LM 配置、结构化输出和多模块组合。

## MiniMax 模型信息

| 模型 | API ID | 类型 | 特点 |
|------|--------|------|------|
| **MiniMax-M2** | `MiniMax-M2` | 推理模型 | 支持CoT推理，性价比高 |
| MiniMax-M2.5 | `MiniMax-M2.5` | 通用模型 | 更强推理能力 |
| MiniMax-M2.7 | `MiniMax-M2.7` | 高级推理 | 最新一代推理模型 |

## DSPy 配置

### 基础配置

```python
import dspy

# MiniMax 配置 (V8.63 - 正确格式)
minimax = dspy.LM(
    'openai/MiniMax-M2',           # 使用 openai/ 前缀
    api_key='sk-cp-YOUR_API_KEY',  # MiniMax API Key
    base_url='https://api.minimax.chat/v1',  # MiniMax API 端点
    max_tokens=1024,
    temperature=0.1,
    timeout=30
)

dspy.configure(lm=minimax)
```

### 配置验证

```python
# 验证配置
result = minimax("What is 2+2?")
print(result)
# 输出: "4"
```

## 完整使用示例

### 1. 基本问答

```python
import dspy

# 配置
minimax = dspy.LM(
    'openai/MiniMax-M2',
    api_key='YOUR_API_KEY',
    base_url='https://api.minimax.chat/v1'
)
dspy.configure(lm=minimax)

# 使用
class QA(dspy.Signature):
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()

qa = dspy.Predict(QA)
result = qa(question="What is the capital of Japan?")
print(result.answer)  # Tokyo
```

### 2. 思维链推理

```python
from dspy import ChainOfThought

class MathProblem(dspy.Signature):
    problem: str = dspy.InputField()
    answer: str = dspy.OutputField(desc="Detailed solution and final answer")

cot = dspy.ChainOfThought(MathProblem)
result = cot(problem="If a train travels 120km in 2 hours, what is its speed?")
print(result.answer)
```

### 3. 类型化输出 (枚举)

```python
from typing import Literal

class SentimentAnalysis(dspy.Signature):
    text: str = dspy.InputField()
    sentiment: Literal["positive", "negative", "neutral"] = dspy.OutputField()
    confidence: float = dspy.OutputField()

analyzer = dspy.ChainOfThought(SentimentAnalysis)
result = analyzer(text="This product exceeded all my expectations!")
print(result.sentiment)   # positive
print(result.confidence)   # 0.95
```

### 4. 结构化数据提取

```python
class PersonExtractor(dspy.Signature):
    text: str = dspy.InputField()
    name: str = dspy.OutputField()
    age: int = dspy.OutputField()
    occupation: str = dspy.OutputField()

extract = dspy.Predict(PersonExtractor)
result = extract(text="Dr. Sarah Chen, 35, is a senior researcher at Stanford.")
print(f"Name: {result.name}")
print(f"Age: {result.age}")
print(f"Role: {result.occupation}")
```

### 5. ReAct Agent

```python
from dspy import Tool, ReAct

# 定义工具
calculator = Tool(
    name="calculator",
    desc="Perform arithmetic calculations",
    func=lambda x: str(eval(x))
)

# 使用 ReAct
class QuerySolver(dspy.Signature):
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()

react = dspy.ReAct(QuerySolver, tools=[calculator])
result = react(question="If I have 5 apples and buy 3 more, how many do I have?")
print(result.answer)
```

## 天龙引擎集成

### 天龙岗位受益

| 岗位 | MiniMax + DSPy 能力 |
|------|-------------------|
| **01调研师** | 结构化信息提取 + 推理链分析 |
| **02架构师** | 架构方案评估 + 决策推理 |
| **07记录师** | 内容摘要 + 实体提取 |

### 调用方式

```python
# 在天龙引擎中配置 MiniMax
/[@构建师] 配置 DSPy MiniMax
```

## 常见问题

### Q: 报错 "LLM Provider NOT provided"

**原因**: 使用了错误的模型格式
**解决**: 使用 `openai/MiniMax-M2` 格式

```python
# 错误 ❌
dspy.LM('MiniMax-M2', api_key=api_key)

# 正确 ✅
dspy.LM('openai/MiniMax-M2', api_key=api_key, base_url='https://api.minimax.chat/v1')
```

### Q: 报错 "unknown model"

**原因**: 模型名拼写错误
**解决**: 确认使用 `MiniMax-M2` (M大写)

```python
# 错误 ❌
'minimax-M2'
'MiniMax-01'
'minimax-01'

# 正确 ✅
'MiniMax-M2'
```

### Q: 报错 "plan not supported"

**原因**: API Key 没有该模型的访问权限
**解决**: 在 MiniMax 控制台开通对应模型的访问权限

## API Key 获取

1. 访问 [MiniMax Platform](https://platform.minimaxi.com)
2. 注册/登录账户
3. 创建 API Key
4. 确保账户有足够额度

## 模型对比

| 模型 | 优势 | 适用场景 |
|------|------|---------|
| **MiniMax-M2** | 推理能力强 | 复杂分析、CoT任务 |
| MiniMax-M2.5 | 平衡性能 | 一般问答、摘要 |
| MiniMax-M2.7 | 最高精度 | 高要求推理任务 |
