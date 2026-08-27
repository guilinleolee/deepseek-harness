---
license: UNKNOWN
triggers: ["langflow component builder", "LangFlow Component Builder"]
---
# LangFlow Component Builder

## 功能描述

LangFlow自定义Python组件开发 - 基于LangFlow BaseComponent开发自定义AI组件，注册到LangFlow组件库。

## 核心能力

1. **组件开发** - 基于LangFlow BaseComponent创建自定义组件
2. **组件注册** - 注册组件到LangFlow组件库
3. **属性配置** - 定义组件可配置属性
4. **模板系统** - 提供常用组件模板

## 技术基础

```python
from langflow.base import Component
from langflow.inputs import StrInput, IntInput, FloatInput
from langflow.schema import Data

class MyCustomComponent(Component):
    display_name = "我的自定义组件"
    description = "组件描述"
    icon = "settings"

    inputs = [
        StrInput(name="api_key", display_name="API Key", required=True),
        StrInput(name="prompt", display_name="提示词"),
        IntInput(name="max_tokens", display_name="最大Token数", value=1000),
    ]

    outputs = [
        Output(display_name="结果", name="result", method="build_result"),
    ]

    def build_result(self) -> Data:
        # 实现逻辑
        return Data(text="结果文本")
```

## 组件类型模板

### 1. LLM组件模板

```python
from langflow.base import Component
from langflow.inputs import StrInput, SecretStrInput
from langflow.schema import Data

class LLMComponentTemplate(Component):
    display_name = "LLM组件"
    description = "调用LLM的通用组件"
    icon = "Sparkles"

    inputs = [
        SecretStrInput(name="api_key", display_name="API Key", required=True),
        StrInput(name="model", display_name="模型", value="gpt-4"),
        StrInput(name="system_prompt", display_name="系统提示"),
        StrInput(name="user_prompt", display_name="用户提示"),
    ]

    outputs = [
        Output(display_name="响应", name="response", method="call_llm"),
    ]

    def call_llm(self) -> Data:
        # 调用LLM逻辑
        pass
```

### 2. 数据处理组件模板

```python
from langflow.base import Component
from langflow.inputs import StrInput, TableInput
from langflow.schema import Data

class DataProcessorComponent(Component):
    display_name = "数据处理器"
    description = "处理和转换数据"
    icon = "Database"

    inputs = [
        StrInput(name="operation", display_name="操作",
                  options=["filter", "transform", "aggregate"]),
        TableInput(name="data", display_name="输入数据"),
    ]

    outputs = [
        Output(display_name="结果", name="result", method="process"),
    ]

    def process(self) -> Data:
        # 数据处理逻辑
        pass
```

### 3. API集成组件模板

```python
from langflow.base import Component
from langflow.inputs import StrInput, SecretStrInput
from langflow.schema import Data

class APIComponentTemplate(Component):
    display_name = "API集成"
    description = "调用外部API"
    icon = "Globe"

    inputs = [
        StrInput(name="base_url", display_name="API地址", required=True),
        SecretStrInput(name="api_key", display_name="API Key"),
        StrInput(name="endpoint", display_name="端点"),
        StrInput(name="method", display_name="方法", value="GET"),
    ]

    outputs = [
        Output(display_name="响应", name="response", method="call_api"),
    ]

    def call_api(self) -> Data:
        # API调用逻辑
        pass
```

### 4. RAG组件模板

```python
from langflow.base import Component
from langflow.inputs import StrInput, SecretStrInput
from langflow.schema import Data

class RAGComponentTemplate(Component):
    display_name = "RAG组件"
    description = "检索增强生成"
    icon = "BookOpen"

    inputs = [
        StrInput(name="query", display_name="查询", required=True),
        SecretStrInput(name="api_key", display_name="API Key"),
        StrInput(name="vector_store", display_name="向量数据库"),
    ]

    outputs = [
        Output(display_name="结果", name="result", method="rag_search"),
    ]

    def rag_search(self) -> Data:
        # RAG逻辑
        pass
```

## 组件开发流程

```bash
# 1. 创建组件文件
touch my_component.py

# 2. 编写组件代码
# 编辑 my_component.py

# 3. 放置到LangFlow自定义组件目录
# ~/.langflow/custom_components/

# 4. 重启LangFlow
langflow run

# 5. 在LangFlow界面中使用
# Components → Custom → 我的自定义组件
```

## 最佳实践

### 属性类型

| 类型 | 用途 | 示例 |
|------|------|------|
| `StrInput` | 字符串输入 | 提示词、描述 |
| `SecretStrInput` | 密钥输入 | API Key |
| `IntInput` | 整数输入 | 最大Token数 |
| `FloatInput` | 浮点数输入 | 温度参数 |
| `BoolInput` | 布尔输入 | 是否启用 |
| `TableInput` | 表格输入 | 数据列表 |
| `FileInput` | 文件输入 | 上传文件 |

### 输出类型

| 类型 | 用途 | 返回 |
|------|------|------|
| `Data` | 通用数据 | 文本、JSON |
| `TextOutput` | 文本输出 | 纯文本 |
| `TableOutput` | 表格输出 | CSV/DataFrame |

## 命令速查

```bash
# 组件开发
/langflow-component init <name>  # 初始化新组件
/langflow-component validate <file> # 验证组件代码
/langflow-component template <type> # 生成组件模板

# 组件管理
/langflow-component list         # 列出自定义组件
/langflow-component register <file> # 注册组件
/langflow-component unregister <name> # 取消注册

# 模板
/langflow-component template llm          # LLM组件模板
/langflow-component template processor    # 数据处理模板
/langflow-component template api          # API集成模板
/langflow-component template rag          # RAG组件模板
```

## 与天龙引擎协同

```yaml
# 构建师开发自定义组件
[@构建师] 使用 langflow-component 创建自定义RAG组件

# 组件注册后自动同步
[@编排师] 在LangFlow中使用自定义组件设计工作流

# 组件模板复用
[@构建师] 加载 llm 模板快速创建LLM调用组件
```

## 适用岗位

- 03 构建师
- 10-02 AI研究员
- 09-02 编排协调师

## 版本

v1.0.0 | 2026-03-29
