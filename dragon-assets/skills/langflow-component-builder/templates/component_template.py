#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangFlow Component Builder - 自定义组件生成器
快速生成LangFlow自定义Python组件代码
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import argparse
from typing import Dict, Any

# 组件模板库
TEMPLATES = {
    "llm": '''from langflow.base import Component
from langflow.inputs import StrInput, SecretStrInput, IntInput, FloatInput
from langflow.schema import Data


class {class_name}Component(Component):
    """{description}"""

    display_name = "{display_name}"
    description = "{description}"
    icon = "Sparkles"
    name = "{name}"

    inputs = [
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            required=True,
            helper_message="请输入您的API Key"
        ),
        StrInput(
            name="model",
            display_name="模型",
            value="{default_model}",
            options=["claude-3-opus", "claude-3-sonnet", "gpt-4", "gpt-3.5-turbo"],
            helper_message="选择要使用的模型"
        ),
        StrInput(
            name="system_prompt",
            display_name="系统提示",
            value="你是一个有帮助的AI助手。",
            multiline=True,
            helper_message="设置AI的角色和行为"
        ),
        StrInput(
            name="user_message",
            display_name="用户消息",
            required=True,
            multiline=True,
            helper_message="输入您想要AI回答的内容"
        ),
        FloatInput(
            name="temperature",
            display_name="温度",
            value=0.7,
            range=(0, 2.0),
            helper_message="控制输出的随机性"
        ),
        IntInput(
            name="max_tokens",
            display_name="最大Token数",
            value=1000,
            range=(1, 4096),
            helper_message="限制输出的最大长度"
        ),
    ]

    outputs = [
        Output(
            display_name="AI响应",
            name="response",
            method="call_llm"
        ),
    ]

    def call_llm(self) -> Data:
        \"\"\"调用LLM并返回响应\"\"\"
        # TODO: 实现LLM调用逻辑
        api_key = self.api_key
        model = self.model
        system_prompt = self.system_prompt
        user_message = self.user_message
        temperature = self.temperature
        max_tokens = self.max_tokens

        # 示例实现
        response_text = f"[模拟响应] 基于 {model} 模型生成"

        return Data(text=response_text)
''',

    "processor": '''from langflow.base import Component
from langflow.inputs import StrInput, TableInput, IntInput
from langflow.schema import Data


class {class_name}Component(Component):
    """{description}"""

    display_name = "{display_name}"
    description = "{description}"
    icon = "Database"
    name = "{name}"

    inputs = [
        StrInput(
            name="operation",
            display_name="操作",
            options=["filter", "transform", "aggregate", "sort"],
            value="transform",
            helper_message="选择数据处理操作"
        ),
        TableInput(
            name="input_data",
            display_name="输入数据",
            required=True,
            helper_message="输入要处理的数据表格"
        ),
        StrInput(
            name="field",
            display_name="字段名",
            helper_message="指定操作的字段"
        ),
        IntInput(
            name="limit",
            display_name="限制数量",
            value=100,
            range=(1, 10000),
            helper_message="限制输出记录数"
        ),
    ]

    outputs = [
        Output(
            display_name="处理结果",
            name="result",
            method="process_data"
        ),
    ]

    def process_data(self) -> Data:
        \"\"\"处理数据并返回结果\"\"\"
        operation = self.operation
        input_data = self.input_data
        field = self.field
        limit = self.limit

        # TODO: 实现数据处理逻辑
        result = f"[{operation}] 处理了 {len(input_data)} 条数据"

        return Data(text=result)
''',

    "api": '''from langflow.base import Component
from langflow.inputs import StrInput, SecretStrInput, IntInput
from langflow.schema import Data
import requests


class {class_name}Component(Component):
    """{description}"""

    display_name = "{display_name}"
    description = "{description}"
    icon = "Globe"
    name = "{name}"

    inputs = [
        StrInput(
            name="base_url",
            display_name="API地址",
            required=True,
            placeholder="https://api.example.com",
            helper_message="API的基础URL"
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            helper_message="API密钥（如果需要）"
        ),
        StrInput(
            name="endpoint",
            display_name="端点",
            value="/",
            helper_message="API端点路径"
        ),
        StrInput(
            name="method",
            display_name="请求方法",
            options=["GET", "POST", "PUT", "DELETE"],
            value="GET",
            helper_message="HTTP请求方法"
        ),
        IntInput(
            name="timeout",
            display_name="超时时间(秒)",
            value=30,
            range=(1, 300),
            helper_message="请求超时时间"
        ),
    ]

    outputs = [
        Output(
            display_name="响应",
            name="response",
            method="call_api"
        ),
    ]

    def call_api(self) -> Data:
        \"\"\"调用API并返回响应\"\"\"
        base_url = self.base_url.rstrip("/")
        endpoint = self.endpoint
        method = self.method.upper()
        api_key = self.api_key
        timeout = self.timeout

        headers = {{}}
        if api_key:
            headers["Authorization"] = f"Bearer {{api_key}}"

        # TODO: 实现API调用逻辑
        url = f"{{base_url}}{{endpoint}}"
        # response = requests.request(method, url, headers=headers, timeout=timeout)

        result = f"[模拟响应] {{method}} {{url}}"

        return Data(text=result)
''',

    "rag": '''from langflow.base import Component
from langflow.inputs import StrInput, SecretStrInput, IntInput, DropdownInput
from langflow.schema import Data


class {class_name}Component(Component):
    """{description}"""

    display_name = "{display_name}"
    description = "{description}"
    icon = "BookOpen"
    name = "{name}"

    inputs = [
        StrInput(
            name="query",
            display_name="查询",
            required=True,
            multiline=True,
            helper_message="输入检索查询"
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            required=True,
            helper_message="LLM API密钥"
        ),
        DropdownInput(
            name="vector_store",
            display_name="向量数据库",
            options=["Pinecone", "Weaviate", "Chroma", "Milvus", "Qdrant"],
            value="Chroma",
            helper_message="选择向量数据库"
        ),
        StrInput(
            name="index_name",
            display_name="索引名称",
            value="default",
            helper_message="向量数据库索引名"
        ),
        IntInput(
            name="top_k",
            display_name="返回数量",
            value=5,
            range=(1, 100),
            helper_message="返回最相关的K条结果"
        ),
    ]

    outputs = [
        Output(
            display_name="检索结果",
            name="results",
            method="rag_search"
        ),
        Output(
            display_name="生成响应",
            name="response",
            method="generate_response"
        ),
    ]

    def rag_search(self) -> Data:
        \"\"\"执行向量检索\"\"\"
        query = self.query
        vector_store = self.vector_store
        index_name = self.index_name
        top_k = self.top_k

        # TODO: 实现向量检索逻辑
        results = [
            {{"content": "[模拟文档1]", "score": 0.95}},
            {{"content": "[模拟文档2]", "score": 0.88}},
        ]

        return Data(data=results)

    def generate_response(self) -> Data:
        \"\"\"基于检索结果生成响应\"\"\"
        results = self.rag_search()
        query = self.query

        # TODO: 实现RAG生成逻辑
        response = f"[RAG响应] 基于 {len(results.data)} 条检索结果生成"

        return Data(text=response)
''',
}


def generate_component(template_type: str, name: str, display_name: str,
                      description: str, **kwargs) -> str:
    """生成组件代码"""
    if template_type not in TEMPLATES:
        raise ValueError(f"未知模板类型: {template_type}")

    # 生成类名
    class_name = "".join(word.title() for word in name.split("_"))

    # 默认模型
    default_model = kwargs.get("default_model", "claude-3-sonnet")

    template = TEMPLATES[template_type]
    code = template.format(
        class_name=class_name,
        name=name,
        display_name=display_name,
        description=description,
        default_model=default_model,
    )

    return code


def main():
    parser = argparse.ArgumentParser(description="LangFlow Component Builder")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 生成组件
    parser_generate = subparsers.add_parser("generate", help="生成组件代码")
    parser_generate.add_argument("--type", "-t", required=True,
                                 choices=["llm", "processor", "api", "rag"],
                                 help="组件类型")
    parser_generate.add_argument("--name", "-n", required=True,
                                 help="组件名称 (snake_case)")
    parser_generate.add_argument("--display-name", "-d", required=True,
                                 help="显示名称")
    parser_generate.add_argument("--description", required=True,
                                 help="组件描述")
    parser_generate.add_argument("--output", "-o", default=None,
                                 help="输出文件路径")

    # 列出模板
    subparsers.add_parser("list", help="列出可用模板")
    subparsers.add_parser("template", help="显示模板信息")

    args = parser.parse_args()

    if args.command == "generate":
        code = generate_component(
            template_type=args.type,
            name=args.name,
            display_name=args.display_name,
            description=args.description,
        )

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(code)
            print(f"✅ 组件已生成: {args.output}")
        else:
            print(code)

    elif args.command == "list":
        print("\n📋 可用模板:")
        for i, t in enumerate(TEMPLATES.keys(), 1):
            desc = {
                "llm": "LLM调用组件 - 调用OpenAI/Claude等模型",
                "processor": "数据处理组件 - 过滤/转换/聚合数据",
                "api": "API集成组件 - 调用外部API接口",
                "rag": "RAG组件 - 检索增强生成",
            }.get(t, "")
            print(f"  {i}. {t}: {desc}")

    elif args.command == "template":
        print("\n📝 模板详情:")
        print("""
1. llm - LLM调用组件
   用于调用各种LLM API (OpenAI, Claude, Gemini等)

2. processor - 数据处理组件
   用于数据过滤、转换、聚合等操作

3. api - API集成组件
   用于调用外部REST API

4. rag - RAG组件
   用于构建检索增强生成系统
""")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
