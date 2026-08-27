"""
Code Generation Core
根据解析后的API规范生成SDK代码
"""
import re
from typing import Any
from pathlib import Path
from dataclasses import dataclass
from .parser import APISpec, EndpointObject, ParameterObject, SchemaObject, ResponseObject


@dataclass
class TypeMapping:
    """类型映射配置"""
    openapi_types: dict[str, str]
    typescript_types: dict[str, str]
    python_types: dict[str, str]
    go_types: dict[str, str]

    def get_ts(self, openapi_type: str, openapi_format: str | None = None) -> str:
        """获取TypeScript类型"""
        if openapi_format == "date-time":
            return "string"
        if openapi_format == "date":
            return "string"
        if openapi_format == "uuid":
            return "string"
        return self.typescript_types.get(openapi_type, "unknown")

    def get_python(self, openapi_type: str, openapi_format: str | None = None) -> str:
        """获取Python类型"""
        if openapi_format == "date-time":
            return "datetime"
        if openapi_format == "date":
            return "date"
        if openapi_format == "uuid":
            return "str"
        return self.python_types.get(openapi_type, "Any")

    def get_go(self, openapi_type: str, openapi_format: str | None = None) -> str:
        """获取Go类型"""
        type_map = {
            "string": "string",
            "integer": "int",
            "number": "float64",
            "boolean": "bool",
            "array": "[]interface{}",
            "object": "map[string]interface{}"
        }
        if openapi_format == "date-time":
            return "string"
        if openapi_format == "date":
            return "string"
        if openapi_format == "uuid":
            return "string"
        return type_map.get(openapi_type, "interface{}")


# 默认类型映射
DEFAULT_TYPE_MAPPING = TypeMapping(
    openapi_types={
        "string": "string",
        "integer": "integer",
        "number": "number",
        "boolean": "boolean",
        "array": "array",
        "object": "object"
    },
    typescript_types={
        "string": "string",
        "integer": "number",
        "number": "number",
        "boolean": "boolean",
        "array": "T[]",
        "object": "Record<string, any>"
    },
    python_types={
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "list",
        "object": "dict"
    },
    go_types={
        "string": "string",
        "integer": "int",
        "number": "float64",
        "boolean": "bool",
        "array": "[]interface{}",
        "object": "map[string]interface{}"
    }
)


class CodeGenerator:
    """代码生成器基类"""

    def __init__(self, spec: APISpec, type_mapping: TypeMapping | None = None):
        self.spec = spec
        self.type_mapping = type_mapping or DEFAULT_TYPE_MAPPING

    def _to_camel_case(self, text: str) -> str:
        """转驼峰命名"""
        parts = re.split(r"[_\-\s]+", text)
        return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])

    def _to_snake_case(self, text: str) -> str:
        """转蛇形命名"""
        text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", text)
        text = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", text)
        return text.lower().replace("-", "_").replace(" ", "_")

    def _to_pascal_case(self, text: str) -> str:
        """转帕斯卡命名"""
        parts = re.split(r"[_\-\s]+", text)
        return "".join(p.capitalize() for p in parts)

    def _format_description(self, desc: str | None, indent: int = 0) -> str:
        """格式化描述"""
        if not desc:
            return ""
        prefix = " " * indent
        # 简单处理：每80字符换行
        lines = []
        current = prefix + " * "
        for word in desc.split():
            if len(current) + len(word) + 1 > 80:
                lines.append(current)
                current = prefix + " * " + word + " "
            else:
                current += word + " "
        if current.strip() != "*":
            lines.append(current.rstrip())
        return "\n".join(lines)

    def _generate_param_type(self, param: ParameterObject) -> str:
        """生成参数类型"""
        schema = param.schema or {}
        param_type = schema.get("type", "string")
        nullable = "null" if not param.required else ""
        if param_type == "array":
            items = schema.get("items", {})
            item_type = items.get("type", "string")
            ts_type = self.type_mapping.get_ts(item_type, items.get("format"))
            base = f"({ts_type})[]"
        else:
            ts_type = self.type_mapping.get_ts(param_type, schema.get("format"))
            base = ts_type
        if nullable:
            return f"({base} | null)" if " | " not in base else f"{base} | null"
        return base

    def _generate_response_type(self, response: ResponseObject) -> str:
        """生成响应类型"""
        schema = response.schema or {}
        schema_type = schema.get("type", "object")
        ts_type = self.type_mapping.get_ts(schema_type, schema.get("format"))
        if schema_type == "array":
            items = schema.get("items", {})
            item_type = items.get("type", "string")
            item_ts = self.type_mapping.get_ts(item_type, items.get("format"))
            return f"{item_ts}[]"
        return ts_type

    def _generate_function_signature(self, endpoint: EndpointObject) -> dict[str, str]:
        """生成函数签名"""
        params = []
        param_names = []

        # 路径参数
        for p in endpoint.parameters:
            if p.location == "path":
                param_type = self._generate_param_type(p)
                param_names.append(p.name)
                params.append(f"{p.name}: {param_type}")

        # 查询参数
        query_params = [p for p in endpoint.parameters if p.location == "query"]
        if query_params:
            param_names.append("params")
            params.append(f"params?: {{ " + "; ".join(
                f"{p.name}?: {self._generate_param_type(p)}" for p in query_params
            ) + " }")

        # 请求体
        if endpoint.request_body:
            param_names.append("data")
            schema = endpoint.request_body.schema or {}
            schema_type = schema.get("type", "object")
            body_type = self.type_mapping.get_ts(schema_type)
            params.append(f"data?: {body_type}")

        return {
            "params": ", ".join(params),
            "param_names": param_names
        }


class TypeScriptGenerator(CodeGenerator):
    """TypeScript SDK代码生成器"""

    def generate_types(self) -> str:
        """生成类型定义"""
        lines = ["// Type definitions"]

        # 生成schema类型
        for name, schema in self.spec.schemas.items():
            type_name = self._to_pascal_case(name)
            if schema.type == "object" and schema.properties:
                lines.append(f"export interface {type_name} {{")
                for prop_name, prop_schema in schema.properties.items():
                    prop_type = self.type_mapping.get_ts(
                        prop_schema.get("type", "string"),
                        prop_schema.get("format")
                    )
                    required = prop_name in schema.required
                    nullable = "" if required else "?"
                    desc = prop_schema.get("description")
                    if desc:
                        lines.append(f"  /** {desc} */")
                    lines.append(f"  {prop_name}{nullable}: {prop_type};")
                lines.append("}")
            elif schema.enum:
                lines.append(f"export type {type_name} = " + " | ".join(
                    f"'{v}'" if isinstance(v, str) else str(v) for v in schema.enum
                ) + ";")
            else:
                lines.append(f"export type {type_name} = {self.type_mapping.get_ts(schema.type)};")
            lines.append("")

        return "\n".join(lines)

    def generate_api_class(self, tag: str | None = None) -> str:
        """生成API类"""
        endpoints = self.spec.endpoints
        if tag:
            endpoints = [e for e in endpoints if tag in e.tags]
            if not endpoints:
                return ""

        lines = []
        class_name = self._to_pascal_case(tag or "Default") + "Api"

        lines.append(f"export class {class_name} {{")
        lines.append("  private client: ApiClient;")

        # 构造函数
        lines.append("")
        lines.append("  constructor(client: ApiClient) {")
        lines.append("    this.client = client;")
        lines.append("  }")

        # 方法
        for endpoint in endpoints:
            if endpoint.deprecated:
                continue
            method = endpoint.method
            path = endpoint.path
            op_id = endpoint.operation_id or f"{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}"

            # 方法签名
            sig = self._generate_function_signature(endpoint)

            # JSDoc
            if endpoint.summary or endpoint.description:
                lines.append("")
                lines.append("  /**")
                if endpoint.summary:
                    lines.append(f"   * {endpoint.summary}")
                if endpoint.description:
                    for desc_line in endpoint.description.split("\n"):
                        lines.append(f"   * {desc_line}")
                lines.append("   */")

            lines.append(f"  async {self._to_camel_case(op_id)}({sig['params']}): Promise<any> {{")

            # 动态路径参数处理
            path_params = [p for p in endpoint.parameters if p.location == "path"]
            if path_params:
                param_list = ", ".join(f"'{p.name}', {p.name}" for p in path_params)
                lines.append(f"    const _path = `{path}`.replace({{{param_list}}});")
                path = "_path"

            # 请求构建
            if method == "get":
                lines.append(f"    return this.client.{method}('{path}', {{ params }});")
            elif endpoint.request_body:
                lines.append(f"    return this.client.{method}('{path}', {{ data, params }});")
            else:
                lines.append(f"    return this.client.{method}('{path}');")

            lines.append("  }")

        lines.append("}")
        return "\n".join(lines)

    def generate_client(self) -> str:
        """生成客户端类"""
        auth_types = self.spec.security_schemes or {}
        has_auth = len(auth_types) > 0

        lines = [
            "import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';",
            "",
            "// API Client",
            "export class ApiClient {",
            "  private http: AxiosInstance;",
            "  private baseUrl: string;",
            "",
            "  constructor(config: ApiClientConfig) {",
            "    this.baseUrl = config.baseUrl;",
            "    this.http = axios.create({",
            "      baseURL: config.baseUrl,",
            "      timeout: config.timeout || 30000,",
            "    });",
            "  }",
            ""
        ]

        # 添加认证拦截器
        if has_auth:
            lines.extend([
                "  private setAuth(auth: AuthConfig) {",
                "    this.http.interceptors.request.use((config) => {",
                "      if (auth.type === 'bearer') {",
                "        config.headers.Authorization = `Bearer ${auth.token}`;",
                "      } else if (auth.type === 'api_key') {",
                "        if (auth.headerName) {",
                "          config.headers[auth.headerName] = auth.apiKey;",
                "        } else {",
                "          config.params = { ...config.params, api_key: auth.apiKey };",
                "        }",
                "      } else if (auth.type === 'basic') {",
                "        config.auth = { username: auth.username!, password: auth.password! };",
                "      }",
                "      return config;",
                "    });",
                "  }",
                ""
            ])

        # HTTP方法
        methods = ["get", "post", "put", "patch", "delete"]
        for method in methods:
            lines.extend([
                f"  async {method}(url: string, options?: {{ data?: any; params?: any }}) {{",
                f"    return this.http.{method}(url, options);",
                "  }",
                ""
            ])

        lines.extend([
            "}",
            "",
            "// Configuration types",
            "export interface ApiClientConfig {",
            "  baseUrl: string;",
            "  timeout?: number;",
            "}",
            "",
            "export interface AuthConfig {",
            "  type: 'bearer' | 'api_key' | 'basic';",
            "  token?: string;",
            "  apiKey?: string;",
            "  headerName?: string;",
            "  username?: string;",
            "  password?: string;",
            "}"
        ])

        return "\n".join(lines)

    def generate(self) -> dict[str, str]:
        """生成完整SDK"""
        files = {}
        files["client.ts"] = self.generate_client()
        files["types.ts"] = self.generate_types()

        # 按tag生成API类
        tags = set()
        for e in self.spec.endpoints:
            tags.update(e.tags)
        for tag in tags:
            files[f"{self._to_snake_case(tag)}_api.ts"] = self.generate_api_class(tag)

        return files


class PythonGenerator(CodeGenerator):
    """Python SDK代码生成器"""

    def generate_types(self) -> str:
        """生成类型定义"""
        lines = ['"""Type definitions"""', "from dataclasses import dataclass", "from typing import Optional, List, Any, Dict", ""]

        for name, schema in self.spec.schemas.items():
            class_name = self._to_pascal_case(name)
            if schema.type == "object" and schema.properties:
                lines.append(f"@dataclass")
                lines.append(f"class {class_name}:")
                for prop_name, prop_schema in schema.properties.items():
                    prop_type = self.type_mapping.get_python(
                        prop_schema.get("type", "string"),
                        prop_schema.get("format")
                    )
                    required = prop_name in schema.required
                    if not required:
                        prop_type = f"Optional[{prop_type}] = None"
                    else:
                        prop_type = f"{prop_type}"
                    desc = prop_schema.get("description")
                    if desc:
                        lines.append(f"    \"\"\"{desc}\"\"\"")
                    lines.append(f"    {self._to_snake_case(prop_name)}: {prop_type}")
                lines.append("")
            elif schema.enum:
                enum_values = ", ".join(f'"{v}"' if isinstance(v, str) else str(v) for v in schema.enum)
                lines.append(f"{class_name} = Literal[{enum_values}]")
                lines.append("")

        return "\n".join(lines)

    def generate_api_class(self, tag: str | None = None) -> str:
        """生成API类"""
        endpoints = self.spec.endpoints
        if tag:
            endpoints = [e for e in endpoints if tag in e.tags]
            if not endpoints:
                return ""

        class_name = self._to_pascal_case(tag or "Default") + "Api"
        lines = [
            '"""API client"""',
            "import httpx",
            "from typing import Optional, Dict, Any",
            "from .types import *",
            "",
            f"class {class_name}:",
            "    def __init__(self, base_url: str, api_key: str | None = None):",
            "        self.base_url = base_url",
            "        self.client = httpx.Client(",
            "            base_url=base_url,",
            "            headers={'X-API-Key': api_key} if api_key else {},",
            "            timeout=30.0",
            "        )",
            ""
        ]

        for endpoint in endpoints:
            if endpoint.deprecated:
                continue
            method = endpoint.method
            path = endpoint.path
            op_name = self._to_snake_case(endpoint.operation_id or path.replace("/", "_").replace("{", "").replace("}", ""))

            sig = self._generate_function_signature(endpoint)
            sig_python = sig["params"].replace("?", "")

            if endpoint.summary:
                lines.append(f'    """{endpoint.summary}"""')
            lines.append(f"    def {op_name}({sig_python}) -> Any:")
            lines.append(f'        """')

            # 参数文档
            for p in endpoint.parameters:
                lines.append(f"        :param {p.name}: {p.description or p.location}")

            lines.append(f'        """')

            # 请求构建
            if method == "get":
                lines.append(f"        return self.client.get('{path}', params=params)")
            elif endpoint.request_body:
                lines.append(f"        return self.client.{method}('{path}', json=data, params=params)")
            else:
                lines.append(f"        return self.client.{method}('{path}')")
            lines.append("")

        lines.append("    def close(self):")
        lines.append("        self.client.close()")

        return "\n".join(lines)

    def generate_client(self) -> str:
        """生成主客户端"""
        lines = [
            '"""API Client"""',
            "import httpx",
            "from typing import Optional, Dict, Any",
            "from .types import *",
            ""
        ]

        api_classes = []
        for tag in set(e.tags[0] for e in self.spec.endpoints if e.tags):
            class_name = self._to_pascal_case(tag) + "Api"
            lines.append(f"from .{self._to_snake_case(tag)}_api import {class_name}")
            api_classes.append(class_name)
        lines.append(f"__all__ = {sorted(api_classes)}")

        lines.extend([
            "",
            "class APIClient:",
            "    def __init__(self, base_url: str, api_key: str | None = None):",
            "        self.base_url = base_url",
            "        self.client = httpx.Client(",
            "            base_url=base_url,",
            "            headers={'X-API-Key': api_key} if api_key else {},",
            "            timeout=30.0",
            "        )",
            "    def close(self):",
            "        self.client.close()",
            "    def __enter__(self):",
            "        return self",
            "    def __exit__(self, *args):",
            "        self.close()"
        ])

        return "\n".join(lines)

    def generate(self) -> dict[str, str]:
        """生成完整SDK"""
        files = {}
        files["__init__.py"] = ""
        files["types.py"] = self.generate_types()
        files["client.py"] = self.generate_client()

        tags = set()
        for e in self.spec.endpoints:
            tags.update(e.tags)
        for tag in tags:
            files[f"{self._to_snake_case(tag)}_api.py"] = self.generate_api_class(tag)

        return files


class GoGenerator(CodeGenerator):
    """Go SDK代码生成器"""

    def generate_types(self) -> str:
        """生成类型定义"""
        lines = ["package sdk", "", "// Types"]

        for name, schema in self.spec.schemas.items():
            type_name = self._to_pascal_case(name)
            if schema.type == "object" and schema.properties:
                lines.append(f"type {type_name} struct {{")
                for prop_name, prop_schema in schema.properties.items():
                    prop_type = self.type_mapping.get_go(
                        prop_schema.get("type", "string"),
                        prop_schema.get("format")
                    )
                    go_field_name = self._to_pascal_case(prop_name)
                    desc = prop_schema.get("description")
                    if desc:
                        lines.append(f"\t// {desc}")
                    lines.append(f"\t{go_field_name} {prop_type} `json:\"{prop_name}\"`")
                lines.append("}")
                lines.append("")
            elif schema.enum:
                lines.append(f"type {type_name} string")
                lines.append(f"const ({{")
                for v in schema.enum:
                    v_name = self._to_pascal_case(f"{name}_{v}")
                    lines.append(f'\t{v_name} {type_name} = "{v}"')
                lines.append("})")
                lines.append("")

        return "\n".join(lines)

    def generate_client(self) -> str:
        """生成客户端"""
        lines = [
            "package sdk",
            "",
            "import (",
            '\t"bytes"',
            '\t"encoding/json"',
            '\t"fmt"',
            '\t"io"',
            '\t"net/http"',
            ")",
            "",
            "type Client struct {",
            "\tBaseURL string",
            "\tHTTPClient *http.Client",
            "\tAPIKey string",
            "}",
            "",
            "func NewClient(baseURL, apiKey string) *Client {",
            "\treturn &Client{",
            "\t\tBaseURL: baseURL,",
            "\t\tHTTPClient: &http.Client{},",
            "\t\tAPIKey: apiKey,",
            "\t}",
            "}",
            ""
        ]

        # 请求方法
        lines.extend([
            "func (c *Client) doRequest(method, path string, body interface{}) ([]byte, error) {",
            "\tvar reqBody io.Reader",
            "\tif body != nil {",
            "\t\tjsonData, err := json.Marshal(body)",
            "\t\tif err != nil {",
            "\t\t\treturn nil, err",
            "\t\t}",
            "\t\treqBody = bytes.NewBuffer(jsonData)",
            "\t}",
            "",
            "\treq, err := http.NewRequest(method, c.BaseURL+path, reqBody)",
            "\tif err != nil {",
            "\t\treturn nil, err",
            "\t}",
            "",
            "\treq.Header.Set(\"Content-Type\", \"application/json\")",
            "\tif c.APIKey != \"\" {",
            "\t\treq.Header.Set(\"X-API-Key\", c.APIKey)",
            "\t}",
            "",
            "\tresp, err := c.HTTPClient.Do(req)",
            "\tif err != nil {",
            "\t\treturn nil, err",
            "\t}",
            "\tdefer resp.Body.Close()",
            "",
            "\trespBody, err := io.ReadAll(resp.Body)",
            "\tif err != nil {",
            "\t\treturn nil, err",
            "\t}",
            "",
            "\tif resp.StatusCode >= 400 {",
            "\t\treturn nil, fmt.Errorf(\"error: status %d, body: %s\", resp.StatusCode, respBody)",
            "\t}",
            "",
            "\treturn respBody, nil",
            "}",
            ""
        ])

        # 按tag生成方法
        tags = set()
        for e in self.spec.endpoints:
            tags.update(e.tags)

        for tag in tags:
            endpoints = [e for e in self.spec.endpoints if tag in e.tags]
            if not endpoints:
                continue

            type_name = self._to_pascal_case(tag)
            lines.append(f"type {type_name}Client struct {{")
            lines.append("\tclient *Client")
            lines.append("}")
            lines.append("")
            lines.append(f"func (c *Client) {type_name}() *{type_name}Client {{")
            lines.append(f"\treturn &{type_name}Client{{client: c}}")
            lines.append("}")
            lines.append("")

            for endpoint in endpoints:
                if endpoint.deprecated:
                    continue
                method = endpoint.method
                path = endpoint.path
                func_name = self._to_pascal_case(endpoint.operation_id or f"{tag}_{method}")

                # 确定返回类型
                resp_type = "map[string]interface{}"
                for r in endpoint.responses:
                    if r.status_code.startswith("2"):
                        resp_type = self._generate_go_response_type(r)
                        break

                lines.append(f"func (c *{type_name}Client) {func_name}(params map[string]interface{{}}) ({resp_type}, error) {{")
                lines.append(f'\trespBody, err := c.client.doRequest("{method.upper()}", "{path}", params)')
                lines.append("\tif err != nil {")
                lines.append("\t\treturn nil, err")
                lines.append("\t}")
                lines.append("")
                lines.append(f'\tvar result {resp_type}')
                lines.append("\tjson.Unmarshal(respBody, &result)")
                lines.append("\treturn result, nil")
                lines.append("}")
                lines.append("")

        return "\n".join(lines)

    def _generate_go_response_type(self, response: ResponseObject) -> str:
        """生成Go响应类型"""
        schema = response.schema or {}
        schema_type = schema.get("type")
        if schema_type == "array":
            return "[]map[string]interface{}"
        return "map[string]interface{}"

    def generate(self) -> dict[str, str]:
        """生成完整SDK"""
        files = {}
        files["types.go"] = self.generate_types()
        files["client.go"] = self.generate_client()
        files["go.mod"] = f"module sdk\n\ngo 1.21"
        return files
