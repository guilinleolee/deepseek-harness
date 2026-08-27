---
license: UNKNOWN
triggers: ["dspy react", "DSPy ReAct 工具调用 Agent 技能"]
---
# DSPy ReAct 工具调用 Agent 技能

## 概述

DSPy ReAct 模块实现 ReAct (Reasoning + Acting) 模式，让 LM 能够自主使用工具完成任务。

## ReAct 核心思想

```
┌─────────────────────────────────────────────────────────────┐
│                    ReAct 循环                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Thought → Action → Observation → Thought → ...              │
│                                                             │
│  1. Thought: 分析当前状态，决定下一步                       │
│  2. Action: 执行工具调用                                   │
│  3. Observation: 观察结果                                   │
│  4. 重复直到得到答案                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 基础用法

```python
import dspy

# 定义工具
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for information."""
    # 实现搜索逻辑
    return "Wikipedia results..."

def calculate(expression: str) -> str:
    """Evaluate a math expression."""
    return str(eval(expression))

# 创建 ReAct Agent
react = dspy.ReAct(
    "question -> answer",
    tools=[search_wikipedia, calculate]
)

# 执行
result = react(question="What is the population of Tokyo?")
```

## 完整示例：研究助手

```python
import dspy

# 定义多个工具
class Tools:
    def search_web(self, query: str) -> str:
        """Search the web for information."""
        # 使用搜索引擎
        return "Search results..."

    def get_weather(self, city: str) -> str:
        """Get current weather for a city."""
        # 调用天气 API
        return f"Weather in {city}: sunny, 25°C"

    def calculate(self, expr: str) -> str:
        """Calculate a mathematical expression."""
        return str(eval(expr))

tools = Tools()

# 创建 ReAct 程序
class ResearchAssistant(dspy.Module):
    def __init__(self):
        self.react = dspy.ReAct(
            "question -> answer: str, sources: list[str]",
            tools=[
                tools.search_web,
                tools.get_weather,
                tools.calculate
            ]
        )

    def forward(self, question):
        return self.react(question=question)

# 使用
assistant = ResearchAssistant()
result = assistant(question="Compare the weather in Tokyo and New York")
```

## 工具定义规范

```python
# 好的工具定义
def search_wikipedia(query: str) -> str:
    """
    Search Wikipedia for information about a topic.

    Args:
        query: The search query to look up on Wikipedia

    Returns:
        A string containing relevant Wikipedia excerpts
    """
    ...

# 包含描述的工具
def extract_article(self, url: str, fields: list[str]) -> dict:
    """
    Extract structured information from a web article.

    Args:
        url: The URL of the article to extract from
        fields: List of fields to extract (title, author, date, content)

    Returns:
        A dictionary with the extracted fields
    """
    ...
```

## RAG + ReAct 组合

```python
class RagReact(dspy.Module):
    def __init__(self):
        self.retrieve = dspy.Retrieve(k=5)
        self.react = dspy.ReAct(
            "context, question -> answer",
            tools=[
                self._search_external,
                self._calculate
            ]
        )

    def _search_external(self, query: str) -> str:
        """Search external sources."""
        return "External search results..."

    def _calculate(self, expr: str) -> str:
        """Perform calculations."""
        return str(eval(expr))

    def forward(self, question):
        # 先检索上下文
        context = self.retrieve(question).passages

        # 再用 ReAct 推理
        return self.react(context=context, question=question)
```

## 与其他 Agent 框架对比

| 维度 | DSPy ReAct | LangChain Agent | AutoGPT |
|------|-----------|----------------|---------|
| **工具定义** | Python 函数 | Tool 对象 | Plugin 系统 |
| **推理过程** | 可观察 | 黑盒 | 黑盒 |
| **优化能力** | Teleprompter | 无 | 无 |
| **模块化** | 强 | 中等 | 弱 |

## 天龙引擎使用场景

| 场景 | 工具示例 |
|------|---------|
| **调研任务** | 搜索、网页抓取、API调用 |
| **数据分析** | SQL查询、计算、图表生成 |
| **自动化任务** | 文件操作、系统命令 |
| **研究助手** | 文献检索、计算、绘图 |

## 最佳实践

1. **清晰的工具描述**: docstring 帮助 LM 理解何时使用
2. **类型提示**: 明确的输入输出类型
3. **错误处理**: 工具应返回有意义的错误信息
4. **组合使用**: 与 RAG、Retrieval 等模块组合
