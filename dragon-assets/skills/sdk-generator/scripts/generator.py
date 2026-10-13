#!/usr/bin/env python3
"""
SDK Generator CLI
命令行工具：基于OpenAPI规范生成多语言SDK
"""
import argparse
import shutil
import sys
from pathlib import Path
from typing import Literal

from .parser import OpenAPIParser, APISpec
from .codegen import TypeScriptGenerator, PythonGenerator, GoGenerator, DEFAULT_TYPE_MAPPING
from .template_engine import TemplateEngine, TemplateContext, create_context_from_spec


def resolve_spec_path(spec_path: str | None, known_paths: list[Path]) -> Path | None:
    """解析规范文件路径"""
    if spec_path:
        path = Path(spec_path)
        if path.exists():
            return path

    # 尝试常见位置
    candidates = [
        Path("openapi.yaml"),
        Path("openapi.yml"),
        Path("openapi.json"),
        Path("api.yaml"),
        Path("api.yml"),
        Path("api.json"),
        Path("spec/openapi.yaml"),
        Path("spec/api.yaml"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def generate_sdk(
    spec_path: str,
    language: Literal["typescript", "python", "go", "all"],
    output_dir: str,
    template_dir: str | None = None,
    auth: str = "api_key",
    retry: str = "exponential",
    rate_limit: int = 100
) -> None:
    """生成SDK"""
    # 解析规范
    parser = OpenAPIParser(spec_path)
    spec = parser.parse()
    context = create_context_from_spec(spec, parser=parser, auth_types=parser.get_auth_types())
    context.language = language

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 渲染模板生成SDK
    engine = TemplateEngine(templates_dir=None)
    target_languages = ["typescript", "python", "go"] if language == "all" else [language]

    for lang in target_languages:
        lang_dir = output_path / lang
        lang_dir.mkdir(parents=True, exist_ok=True)

        for template_name, output_filename in [
            ("client", f"{lang}-client.ts" if lang == "typescript" else f"{lang}_client.py" if lang == "python" else "client.go"),
            ("api", f"{lang}-api.ts" if lang == "typescript" else f"{lang}_api.py" if lang == "python" else "api.go"),
            ("types", f"{lang}-types.ts" if lang == "typescript" else f"{lang}_models.py" if lang == "python" else "models.go"),
            ("index", f"index.ts" if lang == "typescript" else f"__init__.py" if lang == "python" else "sdk.go"),
        ]:
            output_file = lang_dir / output_filename
            try:
                engine.render_to_file(template_name, context, output_file)
                print(f"  Generated: {lang}/{output_filename}")
            except FileNotFoundError:
                print(f"  Skipped: {lang}/{output_filename} (template not found)")

    print(f"\nSDK generated successfully in: {output_path}")


def generate_incremental(
    spec_path: str,
    language: Literal["typescript", "python", "go"],
    output_dir: str,
    endpoints: list[str] | None = None,
    exclude_tags: list[str] | None = None
) -> None:
    """增量生成：只生成指定端点"""
    # 解析规范
    parser = OpenAPIParser(spec_path)
    spec = parser.parse()

    # 过滤端点
    if endpoints:
        spec.endpoints = [e for e in spec.endpoints if e.path in endpoints or e.operation_id in endpoints]
    if exclude_tags:
        spec.endpoints = [e for e in spec.endpoints if not any(t in exclude_tags for t in e.tags)]

    # 使用TemplateEngine渲染模板
    engine = TemplateEngine(templates_dir=None)
    context = create_context_from_spec(spec, parser=parser, auth_types=parser.get_auth_types())
    context.language = language

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    lang_dir = output_path / language
    lang_dir.mkdir(parents=True, exist_ok=True)

    for template_name, output_filename in [
        ("client", f"{language}-client.ts" if language == "typescript" else f"{language}_client.py" if language == "python" else "client.go"),
        ("api", f"{language}-api.ts" if language == "typescript" else f"{language}_api.py" if language == "python" else "api.go"),
        ("types", f"{language}-types.ts" if language == "typescript" else f"{language}_models.py" if language == "python" else "models.go"),
        ("index", f"index.ts" if language == "typescript" else f"__init__.py" if language == "python" else "sdk.go"),
    ]:
        output_file = lang_dir / output_filename
        try:
            engine.render_to_file(template_name, context, output_file)
            print(f"  Generated: {language}/{output_filename}")
        except FileNotFoundError:
            print(f"  Skipped: {language}/{output_filename} (template not found)")

    print(f"Incremental SDK generated: {len(spec.endpoints)} endpoints")


def main():
    parser = argparse.ArgumentParser(
        description="SDK Generator - Generate multi-language SDKs from OpenAPI spec",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate TypeScript SDK
  python generator.py --spec openapi.yaml --lang typescript --out ./generated/ts-sdk

  # Generate Python SDK
  python generator.py --spec openapi.yaml --lang python --out ./generated/py-sdk

  # Generate Go SDK
  python generator.py --spec openapi.yaml --lang go --out ./generated/go-sdk

  # Generate all languages
  python generator.py --spec openapi.yaml --lang all --out ./generated

  # Incremental generation
  python generator.py --spec openapi.yaml --lang typescript --out ./generated/ts-sdk \\
      --endpoints /users /users/{id}

  # With custom options
  python generator.py --spec openapi.yaml --lang typescript --out ./sdk \\
      --auth oauth2 --retry exponential --rate-limit 100
"""
    )

    parser.add_argument(
        "--spec", "-s",
        help="Path to OpenAPI spec file (YAML or JSON)"
    )
    parser.add_argument(
        "--lang", "-l",
        choices=["typescript", "python", "go", "all"],
        default="typescript",
        help="Target language (default: typescript)"
    )
    parser.add_argument(
        "--out", "-o",
        help="Output directory"
    )
    parser.add_argument(
        "--template",
        help="Custom template directory"
    )
    parser.add_argument(
        "--auth",
        choices=["api_key", "bearer", "basic", "oauth2", "none"],
        default="api_key",
        help="Authentication type (default: api_key)"
    )
    parser.add_argument(
        "--retry",
        choices=["exponential", "fixed", "linear", "none"],
        default="exponential",
        help="Retry strategy (default: exponential)"
    )
    parser.add_argument(
        "--rate-limit",
        type=int,
        default=100,
        help="Rate limit (requests per second, default: 100)"
    )
    parser.add_argument(
        "--endpoints",
        nargs="+",
        help="Only generate specified endpoints"
    )
    parser.add_argument(
        "--exclude-tags",
        nargs="+",
        help="Exclude endpoints with these tags"
    )
    parser.add_argument(
        "--show-info",
        action="store_true",
        help="Show spec information without generating"
    )

    args = parser.parse_args()

    # 如果没有指定spec，尝试自动查找
    spec_path = args.spec
    if not spec_path:
        candidates = [
            "openapi.yaml", "openapi.yml", "openapi.json",
            "api.yaml", "api.yml", "api.json",
            "spec/openapi.yaml", "spec/api.yaml"
        ]
        for candidate in candidates:
            if Path(candidate).exists():
                spec_path = candidate
                print(f"Auto-detected spec: {spec_path}")
                break

    if not spec_path:
        print("Error: OpenAPI spec file not found.")
        print("Please specify with --spec or place spec file in current directory.")
        sys.exit(1)

    if not Path(spec_path).exists():
        print(f"Error: Spec file not found: {spec_path}")
        sys.exit(1)

    # 显示信息模式
    if args.show_info:
        parser_obj = OpenAPIParser(spec_path)
        spec = parser_obj.parse()
        print(f"\nAPI: {spec.title} v{spec.version}")
        if spec.description:
            print(f"Description: {spec.description}")
        print(f"Base URL: {spec.base_url or 'Not specified'}")
        print(f"Endpoints: {len(spec.endpoints)}")
        print(f"Schemas: {len(spec.schemas)}")
        print(f"Auth types: {parser_obj.get_auth_types()}")
        print("\nTags:")
        for tag, endpoints in parser_obj.get_tag_groups().items():
            print(f"  {tag}: {len(endpoints)} endpoints")
        return

    # 输出目录
    output_dir = args.out
    if not output_dir:
        output_dir = f"./generated/{args.lang}"

    # 生成SDK
    if args.endpoints or args.exclude_tags:
        generate_incremental(
            spec_path,
            args.lang,
            output_dir,
            args.endpoints,
            args.exclude_tags
        )
    else:
        generate_sdk(
            spec_path,
            args.lang,
            output_dir,
            args.template,
            args.auth,
            args.retry,
            args.rate_limit
        )


if __name__ == "__main__":
    main()
