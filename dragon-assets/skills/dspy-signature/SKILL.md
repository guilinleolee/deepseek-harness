---
license: UNKNOWN
name: dspy-signature
version: 2.0.0
description: |
  DSPy Signature 声明式提示词技能 V2.0，集成 VADPs2.0 八字段框架
  (Role/Personality/Goal/Success Criteria/Constraints/Output/Stop Rules/Context)，
  超越传统 InputField/OutputField/desc 三字段，扩展 Stop Rules/Success Criteria/Constraints/Personality。
author: 天龙引擎团队
created: 2026-05-08
updated: 2026-05-08
category: ai-programming
triggers:
  - "用户提到「DSPy Signature声明式接口」时"
  - "用户需要将提示词升级为VADPs2.0八字段时"
---

# DSPy Signature 声明式提示词技能 V2.0

## L0: 一句话
用 Python 类替代脆弱提示字符串，集成 VADPs2.0 八字段声明式接口。

## L1: 使用场景
DSPy Signature 是声明式提示词抽象层，替代脆弱的字符串模板。V2.0 在传统 InputField/OutputField/desc 三字段基础上，扩展 VADPs2.0 八字段（Role/Personality/Goal/Success Criteria/Constraints/Output/Stop Rules/Context），支持停止规则、成功标准、约束条件等高级字段，实现从"写提示词"到"编程 LM"的范式转变。适用复杂多轮对话、结构化抽取、ChainOfThought 推理等场景。V2.0 通过六步工作流（背景→角色→目标→约束→输出→验证）和六维25点评分体系，确保 Signature 质量可量化、可迭代。

## L2: 详细文档

### VADPs2.0 八字段扩展

```python
import dspy
from typing import List

class QA(dspy.Signature):
    """[VADPs2.0] Answer questions based on context."""
    # Role: 角色定义
    # Personality: 输出风格/个性
    # Goal: 核心目标
    # Success Criteria: 成功标准（V2.0新增）
    # Constraints: 约束条件（V2.0新增）
    # Stop Rules: 停止规则（V2.0新增）
    # Output: 输出格式规范
    # Context: 上下文要求

    # InputField + 扩展字段
    context: str = dspy.InputField(
        desc="relevant background information",
        role="知识库检索结果",
        personality="简洁专业，引用来源",
    )
    question: str = dspy.InputField(
        desc="user's question",
        role="用户查询",
        personality="准确清晰",
    )

    # OutputField + 扩展字段
    answer: str = dspy.OutputField(
        desc="concise answer",
        role="知识助手",
        personality="严谨但不失友好，引用[1]标注来源",
        success_criteria="答案直接相关、无幻觉、引用来源",
        stop_rules="遇到不确定信息时回答「根据现有资料无法确定」并停止",
        constraints="禁止编造事实、必须引用context中的来源",
    )
    reasoning: str = dspy.OutputField(
        desc="step-by-step reasoning",
        role="推理引擎",
        stop_rules="推理步骤不超过5步，超出则截断",
    )
```

### VADPs2.0 六步工作流

```
Stage 1: 背景分析 (Context)
  → 分析输入输出类型、推理复杂度、多轮需求
Stage 2: 角色定义 (Role)
  → 定义 Role 字段：知识助手/推理引擎/分析师/审核员
Stage 3: 目标设定 (Goal + Success Criteria)
  → 设定 Goal 字段 + Success Criteria 量化标准
Stage 4: 约束制定 (Constraints + Stop Rules)
  → 制定 Constraints 禁止项 + Stop Rules 截断条件
Stage 5: 输出规范 (Output)
  → 定义 OutputField 格式 + Personality 风格
Stage 6: 执行验证 (Eval-Harness)
  → 用 eval-harness pass@k 验证质量
```

### 六维25点评分体系

| 维度 | 权重 | 检查项 |
|------|------|--------|
| 结果契合度 | 25% | 答案与 context 相关性、Stop Rules 遵守率 |
| 上下文保真度 | 15% | InputField desc 描述准确性 |
| 可执行性 | 20% | Signature 可被 Predict/ChainOfThought 调用 |
| 约束与停止规则 | 15% | Stop Rules 截断率、Constraints 违规率 |
| 输出可控性 | 15% | OutputField 格式一致性、Personality 遵守率 |
| 验证与迭代性 | 10% | pass@k 评估通过率 |

## 概述

DSPy Signature 是声明式提示词抽象，用 Python 代码替代脆弱的提示词字符串。

## 核心概念

### Signature 语法

```python
# 基础格式: "input -> output"
"question -> answer"

# 多输入
"context, question -> answer"

# 带类型注解
"query: str, context: List[str] -> answer: float"

# 多输出
"context, question -> rationale: str, answer: str"
```

### 字段描述

```python
class ExtractInfo(dspy.Signature):
    """Extract structured information from text."""
    text: str = dspy.InputField(desc="the text to extract from")
    title: str = dspy.OutputField(desc="the main title")
    entities: list[dict] = dspy.OutputField(desc="a list of entities")
```

## 天龙引擎使用方式

### 1. 简单问答 Signature

```python
class SimpleQA(dspy.Signature):
    """Answer questions concisely."""
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()
```

### 2. 带推理的问答

```python
class ReasonedQA(dspy.Signature):
    """Answer questions with reasoning."""
    question: str = dspy.InputField()
    reasoning: str = dspy.OutputField(desc="step by step reasoning")
    answer: str = dspy.OutputField()
```

### 3. 结构化抽取

```python
class EntityExtractor(dspy.Signature):
    """Extract entities from text."""
    text: str = dspy.InputField(desc="input text")
    people: list[str] = dspy.OutputField(desc="list of person names")
    organizations: list[str] = dspy.OutputField(desc="list of org names")
    dates: list[str] = dspy.OutputField(desc="list of dates")
```

## 与 LangChain 对比

| 维度 | DSPy Signature | LangChain Prompt |
|------|---------------|------------------|
| **定义方式** | Python 类 | 字符串模板 |
| **类型安全** | 强类型 | 动态 |
| **可优化性** | 自动编译 | 手动调优 |
| **可复用性** | 模块化 | 部分 |

## 安装

```bash
pip install dspy-ai
```

## 快速开始

```python
import dspy

# 配置语言模型
dspy.settings.configure(lm=dspy.OpenAI('gpt-4'))

# 定义 Signature
class QA(dspy.Signature):
    """Answer questions based on context."""
    context: str = dspy.InputField()
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()

# 使用
qa = dspy.Predict(QA)
result = qa(context="...", question="...")
```

## 最佳实践

1. **清晰的字段描述**: InputField 和 OutputField 都应包含 desc
2. **类型注解**: 使用类型提示提高输出解析准确性
3. **单一职责**: 每个 Signature 只做一件事
4. **可组合**: 模块化设计便于组合使用

## 与天龙引擎协同

- 10-01 提示词架构师: Signature 作为标准接口
- 01调研师: 结构化输出验证
- 07记录师: TypedPredictor 增强结构化输出
