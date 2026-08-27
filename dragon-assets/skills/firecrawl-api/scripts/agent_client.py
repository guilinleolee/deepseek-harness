#!/usr/bin/env python3
"""
Firecrawl Agent Client - 自然语言数据提取
使用AI从网页中提取结构化数据
"""

import argparse
import json
import os
import sys
from pathlib import Path

def load_api_key():
    """加载API Key"""
    api_key = os.environ.get('FIRECRAWL_API_KEY')
    if not api_key:
        config_path = Path.home() / ".claude" / "firecrawl_config.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                api_key = config.get('api_key')
    return api_key

def extract_with_agent(prompt: str, urls: list, schema=None, model='spark-1-mini', api_key: str = None):
    """使用Agent提取数据"""
    try:
        from firecrawl import Firecrawl
        key = api_key or load_api_key()
        if not key:
            raise ValueError("FIRECRAWL_API_KEY not set")

        app = Firecrawl(api_key=key)
        result = app.agent(
            prompt=prompt,
            schema=schema,
            urls=urls,
            model=model
        )
        return result
    except ImportError:
        print("❌ firecrawl-py 未安装")
        print("   请运行: pip install firecrawl-py")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='🔥 Firecrawl Agent - 自然语言数据提取')
    parser.add_argument('url', nargs='?', help='目标URL')
    parser.add_argument('--prompt', '-p', required=True, help='提取指令')
    parser.add_argument('--schema', '-s', help='JSON Schema文件或JSON字符串')
    parser.add_argument('--urls', help='URL列表JSON文件')
    parser.add_argument('--model', default='spark-1-mini',
                       choices=['spark-1-mini', 'spark-1-pro'],
                       help='AI模型')
    parser.add_argument('--api-key', help='Firecrawl API Key (可选)')
    parser.add_argument('--output', '-o', help='输出文件')
    parser.add_argument('--raw', action='store_true', help='显示原始输出')
    args = parser.parse_args()

    # 解析URLs
    urls = []
    if args.urls:
        urls_path = Path(args.urls)
        if urls_path.exists():
            with open(urls_path) as f:
                data = json.load(f)
                urls = data if isinstance(data, list) else data.get('urls', [])
        else:
            urls = [args.urls]
    elif args.url:
        urls = [args.url]

    if not urls:
        print("❌ 请指定URL (--url 或 --urls)")
        sys.exit(1)

    # 解析Schema
    schema = None
    if args.schema:
        schema_path = Path(args.schema)
        if schema_path.exists():
            with open(schema_path) as f:
                schema = json.load(f)
        else:
            try:
                schema = json.loads(args.schema)
            except json.JSONDecodeError:
                print(f"❌ 无效的JSON Schema: {args.schema}")
                sys.exit(1)

    print(f"🤖 Firecrawl Agent 数据提取")
    print(f"   URL数: {len(urls)}")
    print(f"   Prompt: {args.prompt}")
    print(f"   模型: {args.model}")
    if schema:
        print(f"   Schema: {json.dumps(schema, indent=2)[:200]}...")

    result = extract_with_agent(args.prompt, urls, schema, args.model, args.api_key)

    if result:
        print("\n" + "="*60)
        print("提取结果:")
        print("="*60)

        if isinstance(result, dict):
            # 结构化输出
            if args.raw:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                # 格式化显示
                for key, value in result.items():
                    print(f"\n📌 {key}:")
                    if isinstance(value, list):
                        for i, item in enumerate(value[:10], 1):
                            print(f"   {i}. {item}")
                        if len(value) > 10:
                            print(f"   ... 还有 {len(value) - 10} 项")
                    elif isinstance(value, dict):
                        for k, v in value.items():
                            print(f"   {k}: {v}")
                    else:
                        print(f"   {value}")
        else:
            print(result)

        # 保存结果
        output_file = args.output or f"agent_result_{hash(args.prompt)}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n💾 结果已保存: {output_file}")

    else:
        print("❌ 数据提取失败")

if __name__ == '__main__':
    main()
