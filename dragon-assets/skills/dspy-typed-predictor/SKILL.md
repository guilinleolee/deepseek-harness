---
license: UNKNOWN
triggers: ["dspy typed predictor", "DSPy TypedPredictor 类型化输出技能"]
---
# DSPy TypedPredictor 类型化输出技能

## 概述

DSPy 通过类型注解实现结构化输出解析，确保 LM 输出符合预期类型。

## 类型注解语法

```python
from typing import Literal, Optional

# 枚举类型
class Sentiment(dspy.Signature):
    text: str = dspy.InputField()
    sentiment: Literal["positive", "negative", "neutral"] = dspy.OutputField()

# 数值类型
class MathQA(dspy.Signature):
    question: str = dspy.InputField()
    answer: float = dspy.OutputField()

# 可选类型
class ExtractInfo(dspy.Signature):
    text: str = dspy.InputField()
    title: Optional[str] = dspy.OutputField()
    author: Optional[str] = dspy.OutputField()

# 列表类型
class ListQA(dspy.Signature):
    question: str = dspy.InputField()
    items: list[str] = dspy.OutputField()

# 字典类型
class EntityExtractor(dspy.Signature):
    text: str = dspy.InputField()
    entity: dict[str, str] = dspy.OutputField()
```

## 常用类型模式

### 1. 枚举/分类

```python
from typing import Literal

class TextClassifier(dspy.Signature):
    """Classify text into categories."""
    text: str = dspy.InputField()
    category: Literal[
        "technology",
        "business",
        "sports",
        "entertainment",
        "health"
    ] = dspy.OutputField()
    confidence: float = dspy.OutputField()
```

### 2. 结构化数据

```python
from typing import TypedDict

class Person(TypedDict):
    name: str
    age: int
    occupation: str

class ExtractPerson(dspy.Signature):
    text: str = dspy.InputField()
    person: Person = dspy.OutputField()
```

### 3. JSON Schema

```python
class StructuredQA(dspy.Signature):
    text: str = dspy.InputField()
    result: dict = dspy.OutputField(desc="JSON object with keys: summary, entities, sentiment")
```

## 输出验证

```python
# DSPy v3.1.3 使用 ChainOfThought + 类型注解实现类型安全
from dspy import ChainOfThought

typed_qa = ChainOfThought(MathQA)

# 使用 TypedPredictor (如需独立验证)
try:
    from dspy.functional import TypedPredictor
    typed_qa = TypedPredictor(MathQA)
except ImportError:
    # 回退到 ChainOfThought
    typed_qa = ChainOfThought(MathQA)

result = typed_qa(question="What is 2+2?")
print(result.answer)  # 类型已通过 Signature 注解保证
```

## 与 LangChain 输出解析对比

| 维度 | DSPy 类型化输出 | LangChain OutputParser |
|------|----------------|----------------------|
| **定义方式** | Signature + 类型注解 | Parser 类 |
| **验证时机** | 自动验证 | 手动调用 |
| **错误处理** | 自动重试 | 需手动处理 |
| **类型安全** | 强类型 (Literal/Type) | 弱类型 |

## 天龙引擎使用场景

| 场景 | 示例 |
|------|------|
| **数据分析** | 结构化提取数值、列表、字典 |
| **信息抽取** | 实体、关系、事件 |
| **分类任务** | 情感分析、主题分类 |
| **问答系统** | 精确答案类型 |

## 示例：完整类型化问答

```python
import dspy
from typing import Literal

# 定义类型化 Signature
class NewsAnalyzer(dspy.Signature):
    """Analyze news articles."""
    headline: str = dspy.InputField()
    category: Literal["politics", "economy", "tech", "sports", "other"] = dspy.OutputField()
    sentiment: Literal["positive", "negative", "neutral"] = dspy.OutputField()
    key_entities: list[str] = dspy.OutputField()
    summary: str = dspy.OutputField()

# 使用
analyzer = dspy.ChainOfThought(NewsAnalyzer)
result = analyzer(headline="Tech stocks surge on AI breakthrough")

# 访问结果
print(f"Category: {result.category}")      # economy
print(f"Sentiment: {result.sentiment}")  # positive
print(f"Entities: {result.key_entities}") # ["AI", "Tech stocks"]
```

## 最佳实践

1. **明确的类型边界**: 使用 Literal 限制枚举值
2. **合理的默认值**: Optional 类型提供默认值
3. **描述性文档**: desc 字段帮助 LM 理解期望格式
4. **类型化验证**: 使用 ChainOfThought + Literal 类型注解实现类型安全

## DSPy v3.1.3 兼容说明

在 DSPy v3.1.3 中，类型化输出通过以下方式实现：

```python
# 方式1: ChainOfThought + Literal 类型 (推荐)
from dspy import ChainOfThought
from typing import Literal

class Sentiment(dspy.Signature):
    text: str = dspy.InputField()
    sentiment: Literal["positive", "negative", "neutral"] = dspy.OutputField()

analyzer = ChainOfThought(Sentiment)

# 方式2: 使用 TypedPredictor (如可用)
try:
    from dspy.functional import TypedPredictor
    analyzer = TypedPredictor(Sentiment)
except ImportError:
    analyzer = ChainOfThought(Sentiment)
```
