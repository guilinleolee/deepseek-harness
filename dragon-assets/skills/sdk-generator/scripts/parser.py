"""
OpenAPI Specification Parser
解析OpenAPI 3.x规范文件，提取API元数据
"""
import json
import yaml
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field


@dataclass
class SchemaObject:
    """OpenAPI Schema对象"""
    name: str
    type: str
    format: str | None = None
    description: str | None = None
    properties: dict[str, Any] = field(default_factory=dict)
    required: list[str] = field(default_factory=list)
    items: dict | None = None
    enum: list | None = None
    ref: str | None = None  # $ref path
    oneOf: list | None = None  # oneOf composition
    allOf: list | None = None  # allOf composition
    anyOf: list | None = None  # anyOf composition


@dataclass
class ParameterObject:
    """OpenAPI Parameter对象"""
    name: str
    location: str  # query, path, header, cookie
    required: bool = False
    schema: dict | None = None
    description: str | None = None
    example: Any = None


@dataclass
class RequestBodyObject:
    """OpenAPI RequestBody对象"""
    required: bool = False
    content_type: str = "application/json"
    schema: dict | None = None
    description: str | None = None
    examples: dict | None = None


@dataclass
class ResponseObject:
    """OpenAPI Response对象"""
    status_code: str
    description: str | None = None
    content_type: str = "application/json"
    schema: dict | None = None


@dataclass
class EndpointObject:
    """单个API端点"""
    path: str
    method: str  # get, post, put, patch, delete, options, head
    operation_id: str | None = None
    summary: str | None = None
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    parameters: list[ParameterObject] = field(default_factory=list)
    request_body: RequestBodyObject | None = None
    responses: list[ResponseObject] = field(default_factory=list)
    security: list[dict] = field(default_factory=list)
    deprecated: bool = False


@dataclass
class APISpec:
    """完整API规范"""
    title: str
    version: str
    description: str | None = None
    base_url: str | None = None
    endpoints: list[EndpointObject] = field(default_factory=list)
    schemas: dict[str, SchemaObject] = field(default_factory=dict)
    security_schemes: dict[str, dict] = field(default_factory=dict)
    info: dict = field(default_factory=dict)


class OpenAPIParser:
    """OpenAPI 3.x规范解析器"""

    def __init__(self, spec_path: str | Path):
        self.spec_path = Path(spec_path)
        self.spec: dict = {}
        self._load_spec()

    def _load_spec(self) -> None:
        """加载规范文件"""
        with open(self.spec_path, "r", encoding="utf-8") as f:
            content = f.read()
            if self.spec_path.suffix in [".yaml", ".yml"]:
                self.spec = yaml.safe_load(content)
            elif self.spec_path.suffix == ".json":
                self.spec = json.loads(content)
            else:
                # 尝试自动检测
                try:
                    self.spec = json.loads(content)
                except json.JSONDecodeError:
                    self.spec = yaml.safe_load(content)

    def _resolve_ref(self, ref: str) -> dict:
        """解析$ref引用"""
        if not ref.startswith("#/"):
            return {}
        parts = ref.lstrip("#/").split("/")
        current = self.spec
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part, {})
            else:
                return {}
        return current

    def _parse_schema(self, name: str, schema: dict) -> SchemaObject:
        """解析Schema对象"""
        ref = schema.get("$ref")
        if ref:
            resolved = self._resolve_ref(ref)
            ref_name = ref.split("/")[-1]
            return SchemaObject(
                name=name,
                type=resolved.get("type", "object"),
                format=resolved.get("format"),
                description=resolved.get("description"),
                properties=resolved.get("properties", {}),
                required=resolved.get("required", []),
                items=resolved.get("items"),
                enum=resolved.get("enum"),
                ref=ref_name,
                oneOf=resolved.get("oneOf"),
                allOf=resolved.get("allOf"),
                anyOf=resolved.get("anyOf")
            )
        return SchemaObject(
            name=name,
            type=schema.get("type", "object"),
            format=schema.get("format"),
            description=schema.get("description"),
            properties=schema.get("properties", {}),
            required=schema.get("required", []),
            items=schema.get("items"),
            enum=schema.get("enum"),
            oneOf=schema.get("oneOf"),
            allOf=schema.get("allOf"),
            anyOf=schema.get("anyOf")
        )

    def _parse_parameter(self, param: dict) -> ParameterObject:
        """解析Parameter对象"""
        return ParameterObject(
            name=param["name"],
            location=param["in"],
            required=param.get("required", False),
            schema=param.get("schema"),
            description=param.get("description"),
            example=param.get("example")
        )

    def _parse_request_body(self, body: dict) -> RequestBodyObject:
        """解析RequestBody对象"""
        content = body.get("content", {})
        json_content = content.get("application/json", {})
        return RequestBodyObject(
            required=body.get("required", False),
            content_type="application/json",
            schema=json_content.get("schema"),
            description=body.get("description"),
            examples=json_content.get("examples")
        )

    def _parse_response(self, status_code: str, response: dict) -> ResponseObject:
        """解析Response对象"""
        content = response.get("content", {})
        json_content = content.get("application/json", {})
        return ResponseObject(
            status_code=status_code,
            description=response.get("description"),
            content_type="application/json",
            schema=json_content.get("schema")
        )

    def _parse_endpoint(self, path: str, method: str, operation: dict) -> EndpointObject:
        """解析单个API端点"""
        params = operation.get("parameters", [])
        parameters = [self._parse_parameter(p) for p in params if isinstance(p, dict)]

        request_body = None
        if "requestBody" in operation:
            request_body = self._parse_request_body(operation["requestBody"])

        responses = []
        for status_code, response in operation.get("responses", {}).items():
            responses.append(self._parse_response(status_code, response))

        return EndpointObject(
            path=path,
            method=method.lower(),
            operation_id=operation.get("operationId"),
            summary=operation.get("summary"),
            description=operation.get("description"),
            tags=operation.get("tags", []),
            parameters=parameters,
            request_body=request_body,
            responses=responses,
            security=operation.get("security", []),
            deprecated=operation.get("deprecated", False)
        )

    def parse(self) -> APISpec:
        """解析完整规范"""
        info = self.spec.get("info", {})
        servers = self.spec.get("servers", [])
        base_url = servers[0].get("url") if servers else None

        # 解析 schemas
        schemas = {}
        components = self.spec.get("components", {})
        schema_objects = components.get("schemas", {})
        for name, schema in schema_objects.items():
            schemas[name] = self._parse_schema(name, schema)

        # 解析 endpoints
        endpoints = []
        paths = self.spec.get("paths", {})
        methods = ["get", "post", "put", "patch", "delete", "options", "head"]
        for path, path_item in paths.items():
            for method in methods:
                if method in path_item:
                    operation = path_item[method]
                    endpoint = self._parse_endpoint(path, method, operation)
                    endpoints.append(endpoint)

        # 解析 security schemes
        security_schemes = components.get("securitySchemes", {})

        return APISpec(
            title=info.get("title", "API"),
            version=info.get("version", "1.0.0"),
            description=info.get("description"),
            base_url=base_url,
            endpoints=endpoints,
            schemas=schemas,
            security_schemes=security_schemes,
            info=info
        )

    def get_tag_groups(self) -> dict[str, list[EndpointObject]]:
        """按tag分组端点"""
        groups: dict[str, list[EndpointObject]] = {}
        spec = self.parse()
        for endpoint in spec.endpoints:
            for tag in endpoint.tags:
                if tag not in groups:
                    groups[tag] = []
                groups[tag].append(endpoint)
        return groups

    def get_endpoint_by_id(self, operation_id: str) -> EndpointObject | None:
        """根据operationId查找端点"""
        spec = self.parse()
        for endpoint in spec.endpoints:
            if endpoint.operation_id == operation_id:
                return endpoint
        return None

    def get_auth_types(self) -> list[str]:
        """获取认证类型列表"""
        schemes = self.parse().security_schemes
        auth_types = []
        for name, scheme in schemes.items():
            auth_type = scheme.get("type")
            if auth_type == "http":
                scheme_name = scheme.get("scheme", "").lower()
                if scheme_name == "bearer":
                    auth_types.append("bearer")
                elif scheme_name == "basic":
                    auth_types.append("basic")
            elif auth_type == "apiKey":
                auth_types.append("api_key")
            elif auth_type == "oauth2":
                auth_types.append("oauth2")
        return list(set(auth_types))
