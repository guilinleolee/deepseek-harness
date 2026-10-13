---
license: UNKNOWN
name: claude-api
description: Anthropic Claude API patterns for Python and TypeScript. Covers Messages API, streaming, tool use, vision, extended thinking, batches, prompt caching, and Claude Agent SDK.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["claude api", "Claude API — Anthropic Claude API模式"]
---

# Claude API — Anthropic Claude API模式

> 来源: [affaan-m/everything-claude-code/skills/claude-api](https://github.com/affaan-m/everything-claude-code)

## 功能概述

Anthropic Claude API和SDK使用模式，涵盖Messages API、流式响应、工具调用、视觉识别、扩展思考、批处理、提示缓存及Claude Agent SDK。

## 何时使用

- 构建调用Claude API的应用程序
- 代码导入`anthropic`(Python)或`@anthropic-ai/sdk`(TypeScript)
- 询问Claude API模式、工具调用、流式响应或视觉识别
- 实现Claude Agent SDK的Agent工作流
- 优化API成本、Token使用或延迟

## 模型选择

| 模型 | ID | 最佳场景 |
|------|-----|---------|
| Opus 4.1 | `claude-opus-4-1` | 复杂推理、架构、研究 |
| Sonnet 4 | `claude-sonnet-4-0` | 平衡编码、大多数开发任务 |
| Haiku 3.5 | `claude-3-5-haiku-latest` | 快速响应、高吞吐、成本敏感 |

**默认选择Sonnet 4**，除非任务需要深度推理(Opus)或速度/成本优化(Haiku)。

## Python SDK

### 安装与基础消息

```python
import anthropic

client = anthropic.Anthropic()  # 从环境变量读取ANTHROPIC_API_KEY

message = client.messages.create(
    model="claude-sonnet-4-0",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Explain async/await in Python"}
    ]
)
print(message.content[0].text)
```

### 流式响应

```python
with client.messages.stream(
    model="claude-sonnet-4-0",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a haiku about coding"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### 系统提示

```python
message = client.messages.create(
    model="claude-sonnet-4-0",
    max_tokens=1024,
    system="You are a senior Python developer. Be concise.",
    messages=[{"role": "user", "content": "Review this function"}]
)
```

## TypeScript SDK

### 安装与基础消息

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const message = await client.messages.create({
  model: "claude-sonnet-4-0",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Explain async/await in TypeScript" }],
});
console.log(message.content[0].text);
```

### 流式响应

```typescript
const stream = client.messages.stream({
  model: "claude-sonnet-4-0",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Write a haiku" }],
});

for await (const event of stream) {
  if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
    process.stdout.write(event.delta.text);
  }
}
```

## 工具调用

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["location"]
        }
    }
]

message = client.messages.create(
    model="claude-sonnet-4-0",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "What's the weather in SF?"}]
)

# 处理工具调用响应
for block in message.content:
    if block.type == "tool_use":
        result = get_weather(**block.input)
        # 将结果发回
```

## 视觉识别

```python
import base64

with open("diagram.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

message = client.messages.create(
    model="claude-sonnet-4-0",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_data}},
            {"type": "text", "text": "Describe this diagram"}
        ]
    }]
)
```

## 扩展思考

```python
message = client.messages.create(
    model="claude-sonnet-4-0",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    messages=[{"role": "user", "content": "Solve this math problem step by step..."}]
)

for block in message.content:
    if block.type == "thinking":
        print(f"Thinking: {block.thinking}")
    elif block.type == "text":
        print(f"Answer: {block.text}")
```

## 提示缓存

```python
message = client.messages.create(
    model="claude-sonnet-4-0",
    max_tokens=1024,
    system=[
        {"type": "text", "text": large_system_prompt, "cache_control": {"type": "ephemeral"}}
    ],
    messages=[{"role": "user", "content": "Question about the cached context"}]
)
# 检查缓存使用
print(f"Cache read: {message.usage.cache_read_input_tokens}")
```

## 批处理API

处理大批量异步请求，**50%成本节省**：

```python
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"request-{i}",
            "params": {
                "model": "claude-sonnet-4-0",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}]
            }
        }
        for i, prompt in enumerate(prompts)
    ]
)

# 轮询完成状态
while True:
    status = client.messages.batches.retrieve(batch.id)
    if status.processing_status == "ended":
        break
    time.sleep(30)
```

## Claude Agent SDK

构建多步骤Agent：

```python
import anthropic

tools = [{
    "name": "search_codebase",
    "description": "Search the codebase",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"]
    }
}]

client = anthropic.Anthropic()
messages = [{"role": "user", "content": "Review the auth module"}]

while True:
    response = client.messages.create(
        model="claude-sonnet-4-0",
        max_tokens=4096,
        tools=tools,
        messages=messages,
    )
    if response.stop_reason == "end_turn":
        break
    # 处理工具调用并继续循环
```

## 成本优化

| 策略 | 节省 | 使用场景 |
|------|------|---------|
| 提示缓存 | 缓存token高达90% | 重复系统提示或上下文 |
| 批处理API | 50% | 非时间敏感批量处理 |
| Haiku替代Sonnet | ~75% | 简单任务、分类、提取 |
| 缩短max_tokens | 视情况 | 输出已知很短时 |
| 流式响应 | 无（相同成本） | 更好UX，相同价格 |

## 错误处理

```python
import time
from anthropic import APIError, RateLimitError, APIConnectionError

try:
    message = client.messages.create(...)
except RateLimitError:
    time.sleep(60)  # 退避重试
except APIConnectionError:
    pass  # 网络问题，带退避重试
except APIError as e:
    print(f"API error {e.status_code}: {e.message}")
```

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **10-02 AI研究员** | Claude API调用 | 工具调用 + Agent SDK |
| **03构建师** | 应用集成 | Python/TypeScript SDK |
| **01调研师** | API调用 | 批处理 + 成本优化 |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 Claude API体系                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   模型选择:                                                  │
│   ├── Opus 4.1 → 复杂推理、架构、研究                     │
│   ├── Sonnet 4 → 平衡编码、默认选择                       │
│   └── Haiku 3.5 → 快速响应、成本优化                      │
│                                                             │
│   成本优化:                                                 │
│   ├── 提示缓存 → 高达90%节省                              │
│   ├── 批处理API → 50%节省                                │
│   └── Haiku替代 → ~75%节省                               │
│                                                             │
│   协同技能:                                                 │
│   ├── /context7              → 最新API文档              │
│   ├── /agent-harness-construction → Agent架构            │
│   └── /ai-router             → 模型智能路由              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心命令

```bash
# API调用
[@AI研究员] 使用Claude API实现这个工具调用
[@构建师] 使用Python SDK集成Claude

# 成本优化
[@AI研究员] 使用批处理API处理这批请求
[@AI研究员] 为这个场景选择最优模型

# Agent开发
[@AI研究员] 使用Claude Agent SDK构建多步骤Agent
[@AI研究员] 添加扩展思考到这个复杂推理任务
```

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.68+ | **来源**: ECC
