# Agent 集成指南

> 本文档说明如何将 pandadata-api 集成到不同的 Agent 框架

---

## Claude Code / Codex 集成

### 方式一：Skill 调用

```markdown
# 在 Agent prompt 中引用
使用 pandadata-api skill 获取股票数据。
调用方法：runtime.call("get_stock_daily", code="600519", date="2026-08-18")
```

### 方式二：直接导入

```python
# 在 Claude Code 的 mcp_settings.json 中配置
{
  "mcpServers": {
    "pandadata": {
      "command": "python",
      "args": ["-m", "pandadata_mcp"]
    }
  }
}
```

## Cursor 集成

### Cursor Rules 配置

在 `.cursorrules` 或 `cursor/rules/stock-analysis.mdc` 中添加：

```markdown
# Stock Analysis Rules

## Data Source
- 使用 pandadata-api 获取 A 股数据
- API Key 配置在环境变量 PANDADATA_API_KEY

## Call Pattern
```
runtime.call(method, **kwargs)
```

## Error Handling
- 限流时使用指数退避重试
- 数据缺失时标注 "N/A" 并说明原因
```

## OpenAI 集成

### Function Calling

```python
import json

# 定义 function calling schema
functions = [
    {
        "name": "get_stock_data",
        "description": "获取股票行情数据",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "股票代码，如 600519"
                },
                "date": {
                    "type": "string",
                    "description": "日期，格式 YYYY-MM-DD"
                }
            },
            "required": ["code"]
        }
    }
]

# 调用
def get_stock_data(code: str, date: str = None):
    runtime = PandadataRuntime()
    return runtime.call("get_stock_daily", code=code, date=date or "")
```

---

## LangChain 集成

### Tool 封装

```python
from langchain.tools import Tool
from pandadata_runtime import PandadataRuntime

runtime = PandadataRuntime()

stock_tool = Tool(
    name="stock_data",
    func=lambda params: runtime.call(**json.loads(params)),
    description="获取股票行情数据，输入 JSON 格式参数"
)

# 使用
tools = [stock_tool]
```

---

## CrewAI 集成

### 自定义 Tool

```python
from crewai.tools import BaseTool
from pydantic import Field
from pandadata_runtime import PandadataRuntime

class StockDataTool(BaseTool):
    name: str = "stock_data"
    description: str = "获取股票行情数据"

    def _run(self, code: str, date: str = None) -> str:
        runtime = PandadataRuntime()
        result = runtime.call("get_stock_daily", code=code, date=date or "")
        return json.dumps(result, ensure_ascii=False)

# 在 Agent 中使用
stock_agent = Agent(
    role="股票分析师",
    goal="分析股票数据",
    tools=[StockDataTool()]
)
```

---

## AutoGen 集成

###  Function Agent

```python
import autogen

runtime = PandadataRuntime()

def get_stock_data(code: str, date: str = None):
    """获取股票数据"""
    result = runtime.call("get_stock_daily", code=code, date=date or "")
    return json.dumps(result, ensure_ascii=False)

# 注册函数
autogen.agentchat.register_function(
    get_stock_data,
    caller=analyst_agent,
    executor=orchestrator,
    name="get_stock_data",
    description="获取股票行情数据"
)
```

---

## Dify 集成

### API 工具配置

```json
{
  "api_url": "https://api.pandadata.wiki/v1/call",
  "method": "POST",
  "headers": {
    "Authorization": "Bearer {{PANDADATA_API_KEY}}"
  },
  "request_body": {
    "method": "{{method}}",
    "params": {{params}}
  }
}
```

---

## Coze 集成

### Bot 工具配置

在 Coze 平台的 Bot 编辑器中：
1. 添加"自定义工具"
2. 配置 API 端点
3. 设置参数映射
4. 配置响应解析

---

## 输出格式适配

### 表格输出

```python
def format_as_table(data: dict) -> str:
    """格式化为表格"""
    if not data:
        return "无数据"

    lines = ["| 字段 | 值 |", "| --- | --- |"]
    for key, value in data.items():
        lines.append(f"| {key} | {value} |")

    return "\n".join(lines)
```

### Markdown 输出

```python
def format_as_markdown(data: dict, title: str = "") -> str:
    """格式化为 Markdown"""
    lines = [f"## {title}\n"] if title else []

    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"### {key}")
            for k, v in value.items():
                lines.append(f"- **{k}**: {v}")
        else:
            lines.append(f"- **{key}**: {value}")

    return "\n".join(lines)
```
