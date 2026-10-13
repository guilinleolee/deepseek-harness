#!/usr/bin/env python3
"""
Firecrawl Scrape Client - 单页内容提取
将URL转换为LLM-ready格式（Markdown/HTML/JSON）
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

def scrape_url(url: str, formats=None, api_key: str = None):
    """提取URL内容"""
    if formats is None:
        formats = ['markdown']

    try:
        from firecrawl import Firecrawl
        key = api_key or load_api_key()
        if not key:
            raise ValueError("FIRECRAWL_API_KEY not set")

        app = Firecrawl(api_key=key)
        result = app.scrape(url, formats=formats)
        return result
    except ImportError:
        print("❌ firecrawl-py 未安装")
        print("   请运行: pip install firecrawl-py")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='🔥 Firecrawl Scrape - 单页内容提取')
    parser.add_argument('url', help='目标URL')
    parser.add_argument('--format', '-f', default='markdown',
                        help='输出格式: markdown, html, json, screenshot (逗号分隔多格式)')
    parser.add_argument('--api-key', help='Firecrawl API Key (可选)')
    parser.add_argument('--output', '-o', help='输出文件')
    parser.add_argument('--metadata', action='store_true', help='只显示元数据')
    parser.add_argument('--content', action='store_true', help='只显示内容')
    args = parser.parse_args()

    formats = args.format.split(',')

    print(f"📄 正在提取: {args.url}")
    print(f"   格式: {formats}")

    result = scrape_url(args.url, formats, args.api_key)

    if result:
        # 元数据
        metadata = result.get('metadata', {})
        print("\n📊 页面元数据:")
        print(f"   标题: {metadata.get('title', 'N/A')}")
        print(f"   描述: {metadata.get('description', 'N/A')[:100]}...")
        print(f"   语言: {metadata.get('language', 'N/A')}")
        print(f"   来源: {metadata.get('source', 'N/A')}")

        # 内容输出
        if not args.metadata:
            print("\n" + "="*60)

            if 'markdown' in formats and 'markdown' in result:
                print("Markdown 内容:")
                print("="*60)
                content = result['markdown']
                print(content[:3000] if len(content) > 3000 else content)
                if len(content) > 3000:
                    print(f"\n... (共 {len(content)} 字符，已截断显示)")

            elif 'html' in formats and 'html' in result:
                print("HTML 内容 (前1000字符):")
                print("="*60)
                content = result['html']
                print(content[:1000])
                print(f"\n... (共 {len(content)} 字符)")

            elif 'json' in formats and 'json' in result:
                print("JSON 数据:")
                print("="*60)
                print(json.dumps(result['json'], indent=2, ensure_ascii=False)[:2000])

        # 保存结果
        output_file = args.output
        if not output_file:
            if 'markdown' in formats:
                output_file = f"scrape_{hash(args.url)}.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.get('markdown', ''))
            else:
                output_file = f"scrape_{hash(args.url)}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)

        if output_file:
            print(f"\n💾 结果已保存: {output_file}")

        # 链接提取
        if 'links' in result and result['links']:
            links = result['links']
            print(f"\n🔗 发现 {len(links)} 个链接:")
            for link in links[:10]:
                print(f"   - {link}")
            if len(links) > 10:
                print(f"   ... 还有 {len(links) - 10} 个链接")

    else:
        print("❌ 内容提取失败")

if __name__ == '__main__':
    main()
