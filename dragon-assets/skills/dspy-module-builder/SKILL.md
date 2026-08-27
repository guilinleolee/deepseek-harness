---
license: UNKNOWN
triggers: ["dspy module builder", "DSPy Module Builder 模块化程序构建技能"]
---
# DSPy Module Builder 模块化程序构建技能

## 概述

DSPy Module 是可组合的构建块，将多个 Signature 组合成复杂的程序。

## 内置模块类型

| 模块 | 功能 | 使用场景 |
|------|------|---------|
| `Predict` | 基础生成 | 简单任务 |
| `ChainOfThought` | 链式推理 | 复杂推理 |
| `ReAct` | 工具使用Agent | 自主执行 |
| `ProgramOfThought` | 代码推理 | 数学/逻辑 |
| `Parallel` | 并行执行 | 效率优化 |
| `Refine` | 迭代改进 | 精炼输出 |

## 基础模块使用

```python
import dspy

# 定义 Signature
class QA(dspy.Signature):
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()

# 使用 Predict
predict = dspy.Predict(QA)
result = predict(question="What is 2+2?")

# 使用 ChainOfThought（推理链）
cot = dspy.ChainOfThought(QA)
result = cot(question="Why is the sky blue?")
```

## 模块组合

```python
class MultiHopRAG(dspy.Module):
    def __init__(self, k=3):
        # 定义检索和生成模块
        self.retrieve = dspy.Retrieve(k=k)
        self.hop1 = dspy.ChainOfThought("query -> hop1_result")
        self.hop2 = dspy.ChainOfThought("query, hop1_result -> hop2_result")
        self.final = dspy.ChainOfThought("query, hop1_result, hop2_result -> answer")

    def forward(self, query):
        # 多跳检索
        ctx = self.retrieve(query).passages
        hop1 = self.hop1(query=query, context=ctx)
        hop2 = self.hop2(query=query, hop1_result=hop1.hop1_result)
        return self.final(
            query=query,
            hop1_result=hop1.hop1_result,
            hop2_result=hop2.hop2_result
        )
```

## Parallel 模块

```python
# 并行执行多个模块
class ParallelQA(dspy.Module):
    def __init__(self):
        self.math = dspy.ChainOfThought("question -> answer: float")
        self.reasoning = dspy.ChainOfThought("question -> reasoning")

    def forward(self, question):
        # 并行执行
        math_result, reasoning_result = dspy.Parallel(
            self.math, self.reasoning
        )(question=question)

        return dspy.Prediction(
            answer=math_result.answer,
            reasoning=reasoning_result.reasoning
        )
```

## Refine 模块

```python
# 迭代精炼输出
class RefinedRAG(dspy.Module):
    def __init__(self):
        self.generate = dspy.ChainOfThought("context, question -> answer")
        self.refine = dspy.Refine("context, question, answer -> refined_answer")

    def forward(self, context, question):
        # 首先生成
        initial = self.generate(context=context, question=question)

        # 然后精炼
        refined = self.refine(
            context=context,
            question=question,
            answer=initial.answer
        )

        return refined
```

## 与天龙引擎协同

| 岗位 | 协同方式 |
|------|---------|
| **10-01 提示词架构师** | 模块化程序设计 |
| **10-02 AI研究员** | 多阶段程序构建 |
| **02 架构师** | 模块依赖管理 |

## 最佳实践

1. **单一职责**: 每个模块只做一件事
2. **可组合**: 模块之间通过 forward 组合
3. **可优化**: 所有模块都支持 Teleprompter 优化
4. **类型安全**: 使用 TypedPredictor 确保输出类型
