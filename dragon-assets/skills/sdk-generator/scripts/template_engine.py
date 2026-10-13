"""
Template Engine Wrapper
封装Handlebars模板系统用于代码生成
支持完整的Handlebars风格helpers：
  - 变量替换: {{var}}
  - each块: {{#each items}}...{{/each}}
  - if块: {{#if cond}}...{{/if}}
  - unless块: {{#unless cond}}...{{/unless}}
  - eq helper: {{#eq a b}}...{{/eq}}
  - helpers: {{pascal_name "..."}}, {{snake_name "..."}}, {{camel_name "..."}}
  - upper/lower: {{upper "..."}}, {{lower "..."}}
"""
import json
import re
import re as _re
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field

from .codegen import DEFAULT_TYPE_MAPPING


# ── Case transformation helpers ────────────────────────────────────────────────

def _to_pascal_case(s: str) -> str:
    """hello_world → HelloWorld"""
    return "".join(word.capitalize() for word in re.split(r"[_\-\s]+", s) if word)


def _to_snake_case(s: str) -> str:
    """HelloWorld → hello_world, HELLO_WORLD → hello_world"""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    return re.sub(r"[_\-\s]+", "_", s).strip("_").lower()


def _to_camel_case(s: str) -> str:
    """hello_world → helloWorld"""
    parts = re.split(r"[_\-\s]+", s)
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:] if p)


# ── TemplateContext ────────────────────────────────────────────────────────────

@dataclass
class TemplateContext:
    """模板上下文数据"""
    api_name: str
    api_version: str
    base_url: str
    description: str | None
    schemas: list[dict[str, Any]]
    endpoints: list[dict[str, Any]]
    auth_types: list[str]
    language: str
    # Handlebars-style helpers registry (name -> callable)
    _helpers: dict[str, callable] = field(default_factory=dict)
    # Auth
    auth: bool = False
    auth_type: str = ""
    # Per-tag contexts for grouped API generation
    tag_contexts: list[dict[str, Any]] = field(default_factory=list)

    def register_helper(self, name: str, fn: callable) -> None:
        self._helpers[name] = fn


class TemplateEngine:
    """完整Handlebars风格模板引擎

    支持:
      - 变量替换: {{var}}
      - HTML转义: {{&var}} (不转义)
      - Raw输出: {{{raw}}} (三花括号，不转义)
      - each块: {{#each items}}...{{/each}}
      - if块: {{#if cond}}...{{else}}...{{/if}}
      - unless块: {{#unless cond}}...{{/unless}}
      - eq helper: {{#eq a b}}...{{/eq}}
      - 内联helpers: {{pascal_name "..."}}, {{camel_name "..."}}, {{snake_name "..."}}
      - upper/lower: {{upper "..."}}, {{lower "..."}}
      - 自定义helpers: engine.register_helper("my_helper", fn)
    """

    # 编译时确定的regex（避免重复编译开销）
    _RE_BLOCK = re.compile(r'\{\{#(\w+)\s*([^}]*)\}\}(.*?)\{\{/\1\}\}', re.DOTALL)
    _RE_INL   = re.compile(r'\{\{(\{?)([^}]+)\}\}')
    _RE_LIT   = re.compile(r'^\s*"(.*)"\s*$')

    _BUILTINS: dict[str, callable] = {}

    def __init__(self, template_dir: str | Path | None = None):
        self.template_dir = Path(template_dir) if template_dir else None
        self._templates: dict[str, str] = {}

    # ── 内置helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def _pascal_name(arg: str) -> str:
        return "".join(word.capitalize() for word in re.split(r"[-_\s]+", arg) if word)

    @staticmethod
    def _snake_name(arg: str) -> str:
        s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", arg)
        s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
        return re.sub(r"[-_\s]+", "_", s).strip("_").lower()

    @staticmethod
    def _camel_name(arg: str) -> str:
        parts = re.split(r"[-_\s]+", arg)
        return parts[0].lower() + "".join(p.capitalize() for p in parts[1:] if p)

    @staticmethod
    def _upper(arg: str) -> str:
        return arg.upper()

    @staticmethod
    def _lower(arg: str) -> str:
        return arg.lower()

    # 填充builtins（首次实例化时）
    @classmethod
    def _fill_builtins(cls) -> None:
        if not cls._BUILTINS:
            cls._BUILTINS = {
                "pascal_name": cls._pascal_name,
                "snake_name": cls._snake_name,
                "camel_name": cls._camel_name,
                "upper": cls._upper,
                "lower": cls._lower,
            }

    # ── 核心: 取值 + 调用helpers ─────────────────────────────────────────────

    def _get(self, raw: str, ctx: dict[str, Any]) -> str:
        """解析 "key" 或 "key.sub" 或 helperName arg，并求值。"""
        raw = raw.strip()
        # 内联helper调用: pascal_name "hello"
        m = re.match(r"(\w+)\s+(.+)", raw)
        if m:
            hname, harg = m.group(1), m.group(2).strip()
            # 取literal参数
            lit = harg.strip('"').strip("'")
            # builtin优先
            if hname in self._BUILTINS:
                return str(self._BUILTINS[hname](lit))
            # 自定义
            if hname in ctx.get("_helpers", {}):
                return str(ctx["_helpers"][hname](lit))
            return raw
        # 属性路径: api.name
        parts = raw.split(".")
        val: Any = ctx
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p, "")
            elif hasattr(val, p):
                val = getattr(val, p, "")
            else:
                return ""
            if val is None:
                return ""
        return str(val) if val is not None else ""

    def _lit(self, raw: str) -> str:
        """解析字面量: "hello" -> hello"""
        raw = raw.strip()
        if self._RE_LIT.match(raw):
            return raw.strip('"').strip("'")
        return raw

    def _call(self, name: str, arg: str, ctx: dict[str, Any]) -> str:
        """调用helper并返回字符串结果。"""
        if name == "eq":
            parts = [p.strip() for p in arg.split()]
            if len(parts) == 2:
                a, b = self._lit(parts[0]), self._lit(parts[1])
                return "true" if a == b else "false"
            return "false"
        if name in self._BUILTINS:
            return str(self._BUILTINS[name](self._lit(arg)))
        if name in ctx.get("_helpers", {}):
            return str(ctx["_helpers"][name](self._lit(arg)))
        return ""

    # ── Block helpers ─────────────────────────────────────────────────────────

    def _each(self, body: str, args: str, ctx: dict[str, Any]) -> str:
        items_key = args.strip()
        items: Any = ctx.get(items_key, [])
        if not isinstance(items, (list, tuple)):
            items = [items]
        out_lines = []
        for idx, item in enumerate(items):
            item_ctx = dict(ctx)
            item_ctx["@index"] = idx
            item_ctx["@first"] = (idx == 0)
            item_ctx["@last"] = (idx == len(items) - 1)
            if isinstance(item, dict):
                item_ctx.update(item)
            elif isinstance(item, str):
                item_ctx["@value"] = item
            out_lines.append(self._render(body, item_ctx))
        return "\n".join(out_lines)

    def _if(self, body: str, args: str, ctx: dict[str, Any]) -> str:
        raw = args.strip()
        val = self._get(raw, ctx)
        truthy = bool(val and val != "false" and val != "0")
        branches = re.split(r"\{\{else\}\}", body, maxsplit=1)
        if truthy:
            return self._render(branches[0], ctx)
        elif len(branches) > 1:
            return self._render(branches[1], ctx)
        return ""

    def _unless(self, body: str, args: str, ctx: dict[str, Any]) -> str:
        raw = args.strip()
        val = self._get(raw, ctx)
        truthy = bool(val and val != "false" and val != "0")
        return "" if truthy else self._render(body, ctx)

    def _eq(self, body: str, args: str, ctx: dict[str, Any]) -> str:
        parts = [p.strip() for p in args.split()]
        if len(parts) == 2:
            a, b = self._lit(parts[0]), self._lit(parts[1])
            if a == b:
                return self._render(body, ctx)
        return ""

    def _block(self, name: str, args: str, body: str, ctx: dict[str, Any]) -> str:
        if name == "each":   return self._each(body, args, ctx)
        if name == "if":     return self._if(body, args, ctx)
        if name == "unless": return self._unless(body, args, ctx)
        if name == "eq":    return self._eq(body, args, ctx)
        return ""

    # ── 多pass渲染管线 ──────────────────────────────────────────────────────

    def _raw_pass(self, tmpl: str, ctx: dict[str, Any]) -> str:
        """Pass 1: {{{raw}}} -> 不转义输出。"""
        def replacer(m):
            inner = m.group(1)
            val = self._get(inner, ctx)
            return str(val) if val else ""
        return re.sub(r"\{\{\{(.*?)}}}\}", replacer, tmpl, flags=re.DOTALL)

    def _var_pass(self, tmpl: str, ctx: dict[str, Any]) -> str:
        """Pass 2: {{var}} / {{&var}} -> HTML转义或原样输出。"""
        def replacer(m):
            esc, inner = m.group(1), m.group(2).strip()
            val = self._get(inner, ctx)
            if esc == "&":
                return str(val) if val else ""
            # HTML转义
            s = str(val).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
            return s
        return self._RE_INL.sub(replacer, tmpl)

    def _inl_pass(self, tmpl: str, ctx: dict[str, Any]) -> str:
        """Pass 3: {{helper arg}} -> 调用内联helpers。"""
        def replacer(m):
            esc, inner = m.group(1), m.group(2).strip()
            if esc:
                return m.group(0)  # 跳过 {{&...}} / {{{...}}}
            parts = inner.split(None, 1)
            if not parts:
                return m.group(0)
            hname, arg = parts[0], (parts[1] if len(parts) > 1 else "")
            result = self._call(hname, arg, ctx)
            return result if result else m.group(0)
        return self._RE_INL.sub(replacer, tmpl)

    def _block_pass(self, tmpl: str, ctx: dict[str, Any]) -> str:
        """Pass 4: {{#each}}{{#if}}{{#eq}}... -> 执行block helpers。"""
        def replacer(m):
            name, args, body = m.group(1), m.group(2).strip(), m.group(3)
            return self._block(name, args, body, ctx)
        return self._RE_BLOCK.sub(replacer, tmpl)

    def _render(self, tmpl: str, ctx: dict[str, Any]) -> str:
        """对给定ctx执行完整4-pass管线。"""
        r = self._block_pass(tmpl, ctx)
        r = self._inl_pass(r, ctx)
        r = self._raw_pass(r, ctx)
        r = self._var_pass(r, ctx)
        return r

    # ── 公共API ─────────────────────────────────────────────────────────────

    def load_template(self, name: str) -> str:
        """加载模板文件"""
        if self.template_dir and (self.template_dir / name).exists():
            with open(self.template_dir / name, "r", encoding="utf-8") as f:
                self._templates[name] = f.read()
                return self._templates[name]
        return ""

    def render_string(self, tmpl: str, ctx: TemplateContext) -> str:
        """直接渲染模板字符串（用于测试）。"""
        self._fill_builtins()
        context_dict = {
            "api_name": ctx.api_name,
            "api_version": ctx.api_version,
            "base_url": ctx.base_url or "",
            "description": ctx.description or "",
            "auth_types_json": json.dumps(ctx.auth_types),
            "auth": len(ctx.auth_types) > 0,
            "schemas": ctx.schemas,
            "endpoints": ctx.endpoints,
            "_helpers": ctx._helpers,
            "tag_contexts": ctx.tag_contexts,
        }
        return self._render(tmpl, context_dict)

    def render(self, template_name: str, ctx: TemplateContext) -> str:
        """渲染模板文件"""
        self._fill_builtins()
        tmpl = self.load_template(template_name)
        return self.render_string(tmpl, ctx)

    def render_to_file(self, template_name: str, ctx: TemplateContext, output_path: str | Path) -> None:
        """渲染并写入文件"""
        content = self.render(template_name, ctx)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)


def create_context_from_spec(spec, parser=None, auth_types: list[str] | None = None) -> TemplateContext:
    """从解析后的规范创建模板上下文

    Args:
        spec: APISpec对象 或 原始OpenAPI dict（支持直接传入dict自动解析）
        parser: 可选的OpenAPIParser实例，用于获取tag分组
        auth_types: 可选的认证类型列表，默认为空列表
    """
    from .parser import OpenAPIParser, APISpec

    # Accept both APISpec dataclass objects and raw dicts
    if isinstance(spec, dict):
        # Create a temporary spec file for OpenAPIParser to parse
        import json, tempfile, os
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(spec, f)
            tmp_path = f.name
        try:
            api_parser = OpenAPIParser(tmp_path)
            spec = api_parser.parse()
        finally:
            os.unlink(tmp_path)

    # ── Schema dict enrichment ──────────────────────────────────────────────
    schemas = []
    for idx, (name, schema) in enumerate(spec.schemas.items()):
        go_type = DEFAULT_TYPE_MAPPING.get_go(schema.type or "object", schema.format)
        python_type = DEFAULT_TYPE_MAPPING.get_python(schema.type or "object", schema.format)
        ts_type = DEFAULT_TYPE_MAPPING.get_ts(schema.type or "object", schema.format)

        # item_type 用于 array items
        item_ot = schema.items.get("type", "string") if schema.items else "string"
        item_fmt = schema.items.get("format") if schema.items else None
        item_go = DEFAULT_TYPE_MAPPING.get_go(item_ot, item_fmt)

        # Go zero-value
        if go_type == "string":
            zero_val = '""'
        elif go_type in ("int", "int64", "float64"):
            zero_val = "0"
        elif go_type == "bool":
            zero_val = "false"
        else:
            zero_val = "nil"

        # ── enrich properties ──────────────────────────────────────────────
        enriched_props = []
        for pname, pval in (schema.properties or {}).items():
            pgo = DEFAULT_TYPE_MAPPING.get_go(pval.get("type", "string"), pval.get("format"))
            if pgo == "string":
                pz = '""'
            elif pgo in ("int", "int64", "float64"):
                pz = "0"
            elif pgo == "bool":
                pz = "false"
            else:
                pz = "nil"
            enriched_props.append({
                "name": pname,
                "pascal_name": _to_pascal_case(pname),
                "go_type": pgo,
                "json_name": pname,
                "zero_value": pz,
                "required": pname in (schema.required or []),
            })

        # ── enrich enum values ──────────────────────────────────────────
        enriched_enum = []
        for ev in (schema.enum or []):
            enriched_enum.append({
                "value": ev,
                "upper_value": ev.upper(),
                "pascal_name": _to_pascal_case(ev),
            })

        # ── enrich oneOf / allOf ─────────────────────────────────────────
        enriched_oneof = []
        for oi, one_ref in enumerate((schema.oneOf or [])):
            enriched_oneof.append({
                "idx": oi + 1,
                "go_type": DEFAULT_TYPE_MAPPING.get_go(
                    one_ref.get("type", "object"), one_ref.get("format")
                ),
            })

        schemas.append({
            "name": name,
            "type": schema.type,
            "format": schema.format,
            "description": schema.description,
            "required": schema.required,
            "properties": enriched_props,
            "enum": enriched_enum,
            "ref": schema.ref,
            # ── template-ready computed fields ──
            "pascal_name": _to_pascal_case(name),
            "snake_name": _to_snake_case(name),
            "camel_name": _to_camel_case(name),
            "go_type": go_type,
            "python_type": python_type,
            "ts_type": ts_type,
            "json_name": name,
            "upper_value": name.upper(),
            "zero_value": zero_val,
            "item_go_type": item_go,
            "idx": idx + 1,
            # oneOf / allOf
            "oneOf": enriched_oneof,
            "allOf": schema.allOf or [],
        })

    # ── Endpoint dict enrichment ────────────────────────────────────────
    endpoints = []
    for ep in spec.endpoints:
        # ── path params ──────────────────────────────────────────────────
        path_params = []
        for p in ep.parameters:
            if p.location == "path":
                pg = DEFAULT_TYPE_MAPPING.get_go(p.type or "string", p.format)
                if pg == "string":
                    pz = '""'
                elif pg in ("int", "int64", "float64"):
                    pz = "0"
                elif pg == "bool":
                    pz = "false"
                else:
                    pz = "nil"
                path_params.append({
                    "original": "{" + p.name + "}",   # e.g. {pet_id}
                    "snake_name": _to_snake_case(p.name),
                    "go_type": pg,
                    "zero_value": pz,
                })

        # ── query params ──────────────────────────────────────────────────
        query_params = []
        for p in ep.parameters:
            if p.location == "query":
                qg = DEFAULT_TYPE_MAPPING.get_go(p.type or "string", p.format)
                if qg == "string":
                    qz = '""'
                elif qg in ("int", "int64", "float64"):
                    qz = "0"
                elif qg == "bool":
                    qz = "false"
                else:
                    qz = "nil"
                query_params.append({
                    "name": p.name,
                    "pascal_name": _to_pascal_case(p.name),
                    "go_type": qg,
                    "zero_value": qz,
                })

        # ── request body fields ────────────────────────────────────────────
        req_fields = []
        if ep.request_body is not None:
            request_body_schema = ep.request_body.schema or {}
            for fname, fval in request_body_schema.get("properties", {}).items():
                fg = DEFAULT_TYPE_MAPPING.get_go(fval.get("type", "string"), fval.get("format"))
                if fg == "string":
                    fz = '""'
                elif fg in ("int", "int64", "float64"):
                    fz = "0"
                elif fg == "bool":
                    fz = "false"
                else:
                    fz = "nil"
                req_fields.append({
                    "name": fname,
                    "pascal_name": _to_pascal_case(fname),
                    "go_type": fg,
                    "json_name": fname,
                    "zero_value": fz,
                    "required": ep.request_body.required,
                })

        endpoints.append({
            "path": ep.path,
            "method": ep.method,
            "operation_id": ep.operation_id,
            "summary": ep.summary,
            "description": ep.description,
            "tags": ep.tags,
            "deprecated": ep.deprecated,
            "parameters": [
                {
                    "name": p.name,
                    "location": p.location,
                    "required": p.required,
                    "description": p.description,
                }
                for p in ep.parameters
            ],
            "has_request_body": ep.request_body is not None,
            "response_codes": [r.status_code for r in ep.responses],
            # ── template-ready computed fields ──
            "snake_operation_id": _to_snake_case(ep.operation_id),
            "pascal_operation_id": _to_pascal_case(ep.operation_id),
            "pascal_method": ep.method.capitalize(),
            "path_params": path_params,
            "query_params": query_params,
            "request_body_fields": req_fields,
        })

    # ── Auth context ───────────────────────────────────────────────────
    auth_types = auth_types or []
    auth = len(auth_types) > 0
    auth_type = auth_types[0] if auth_types else ""

    # ── Per-tag contexts ────────────────────────────────────────────────
    tag_contexts: list[dict[str, Any]] = []
    if parser is not None:
        tag_groups = parser.get_tag_groups()
        for tag_name, tag_endpoints in tag_groups.items():
            # Build a filtered endpoints list for this tag
            tag_ep_dicts = []
            for ep_dict in endpoints:
                # Match endpoints that have this tag
                ep_obj = None
                for e in spec.endpoints:
                    if e.operation_id == ep_dict.get("operation_id"):
                        ep_obj = e
                        break
                if ep_obj and tag_name in (ep_obj.tags or []):
                    tag_ep_dicts.append(ep_dict)

            if tag_ep_dicts:
                tag_contexts.append({
                    "tag_name": tag_name,
                    "tag_title": "".join(word.capitalize() for word in re.split(r"[-_\s]+", tag_name)),
                    "tag_description": "",  # can be enriched from spec.tags
                    "pascal_tag": "".join(word.capitalize() for word in re.split(r"[-_\s]+", tag_name)),
                    "snake_tag": _to_snake_case(tag_name),
                    "endpoints": tag_ep_dicts,
                    "auth": auth,
                    "auth_type": auth_type,
                })

    return TemplateContext(
        api_name=spec.title,
        api_version=spec.version,
        base_url=spec.base_url or "",
        description=spec.description,
        schemas=schemas,
        endpoints=endpoints,
        auth_types=auth_types,
        language="",
        auth=auth,
        auth_type=auth_type,
        tag_contexts=tag_contexts,
    )
