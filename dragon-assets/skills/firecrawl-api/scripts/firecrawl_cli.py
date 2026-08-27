#!/usr/bin/env python3
"""
Firecrawl API 统一CLI入口
天龙引擎V8.62集成 - 2026-03-30
来源: https://github.com/firecrawl/firecrawl (100k+ Stars)
"""

import argparse
import json
import os
import sys
from pathlib import Path

def load_env():
    """加载环境变量"""
    env_path = Path.home() / ".claude" / ".env"
    if env_path.exists():
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    try:
                        key, value = line.strip().split('=', 1)
                        os.environ.setdefault(key, value)
                    except:
                        pass

    api_key = os.environ.get('FIRECRAWL_API_KEY')
    if not api_key:
        config_path = Path.home() / ".claude" / "firecrawl_config.json"
        if config_path.exists():
            with open(config_path, encoding='utf-8') as f:
                config = json.load(f)
                api_key = config.get('api_key', '')

    if not api_key:
        print("Warning: FIRECRAWL_API_KEY not set")
        print("Set: export FIRECRAWL_API_KEY='fc-xxx'")
        print("Get: https://firecrawl.dev/dashboard")
        return None
    return api_key

def create_app():
    """创建Firecrawl实例"""
    api_key = load_env()
    if not api_key:
        return None
    from firecrawl import Firecrawl
    return Firecrawl(api_key=api_key)

def cmd_map(args):
    """Map URL发现"""
    app = create_app()
    if not app:
        sys.exit(1)

    print(f"Discovering URLs: {args.url}")
    if args.limit:
        result = app.map(args.url, limit=args.limit)
    else:
        result = app.map(args.url)

    if result and hasattr(result, 'urls'):
        urls = result.urls
        print(f"\nFound {len(urls)} URLs:")
        for i, url in enumerate(urls[:50], 1):
            print(f"  {i}. {url}")
        if len(urls) > 50:
            print(f"  ... and {len(urls) - 50} more")

        output_file = Path(args.output) if args.output else Path(f"map_results.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({'url': args.url, 'urls': urls, 'count': len(urls)}, f, indent=2, ensure_ascii=False)
        print(f"\nSaved: {output_file}")
    else:
        print("No URLs found or error occurred")

def cmd_scrape(args):
    """Scrape单页提取"""
    app = create_app()
    if not app:
        sys.exit(1)

    formats = args.format.split(',') if args.format else ['markdown']
    print(f"Scraping: {args.url}")
    print(f"Formats: {formats}")

    try:
        result = app.scrape(args.url, formats=formats)

        if result:
            content = None
            if hasattr(result, 'content'):
                content = result.content
            elif hasattr(result, 'markdown'):
                content = result.markdown

            if content:
                print("\n" + "="*60)
                print("Content (first 2000 chars):")
                print("="*60)
                print(content[:2000] if len(content) > 2000 else content)
                if len(content) > 2000:
                    print(f"\n... ({len(content)} total chars)")

            if hasattr(result, 'metadata'):
                meta = result.metadata
                print("\nMetadata:")
                for key in ['title', 'description', 'language']:
                    val = getattr(meta, key, None) if hasattr(meta, key) else meta.get(key)
                    if val:
                        print(f"  {key}: {val}")

            output_file = Path(args.output) if args.output else None
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    if hasattr(result, 'model_dump'):
                        json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)
                    else:
                        json.dump(str(result), f)
                print(f"\nSaved: {output_file}")
        else:
            print("Scrape failed or returned empty")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def cmd_search(args):
    """Search网页搜索"""
    app = create_app()
    if not app:
        sys.exit(1)

    print(f"Searching: {args.query}")
    result = app.search(args.query, limit=args.limit or 10)

    if result and hasattr(result, 'data'):
        items = result.data
        print(f"\nFound {len(items)} results:")
        for i, item in enumerate(items[:10], 1):
            title = getattr(item, 'title', 'N/A') if hasattr(item, 'title') else item.get('title', 'N/A')
            url = getattr(item, 'url', 'N/A') if hasattr(item, 'url') else item.get('url', 'N/A')
            print(f"  {i}. {title}")
            print(f"     {url}")

        output_file = Path(args.output) if args.output else Path(f"search_results.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            if hasattr(result, 'model_dump'):
                json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)
            else:
                json.dump(str(result), f)
        print(f"\nSaved: {output_file}")

def cmd_extract(args):
    """Extract自然语言提取"""
    app = create_app()
    if not app:
        sys.exit(1)

    urls = [args.url] if args.url else []
    if args.urls:
        with open(args.urls) as f:
            urls_data = json.load(f)
            urls = urls_data if isinstance(urls_data, list) else urls_data.get('urls', [])

    if not urls:
        print("Error: No URLs provided")
        sys.exit(1)

    schema = None
    if args.schema:
        if args.schema.endswith('.json'):
            with open(args.schema) as f:
                schema = json.load(f)
        else:
            schema = json.loads(args.schema)

    print(f"Extracting from {len(urls)} URLs")
    print(f"Prompt: {args.prompt}")

    try:
        result = app.extract(urls, prompt=args.prompt, schema=schema)

        if result:
            print("\n" + "="*60)
            print("Extracted Data:")
            print("="*60)
            if hasattr(result, 'data'):
                data = result.data
                if isinstance(data, dict):
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                else:
                    print(data)
            else:
                print(result)

            output_file = Path(args.output) if args.output else Path("extract_result.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                if hasattr(result, 'model_dump'):
                    json.dump(result.model_dump(), f, indent=2, ensure_ascii=False)
                else:
                    json.dump(str(result), f)
            print(f"\nSaved: {output_file}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def cmd_crawl(args):
    """Crawl全站爬取"""
    if not args.url and not args.status:
        print("Error: URL or --status required")
        sys.exit(1)

    app = create_app()
    if not app:
        sys.exit(1)

    if args.status:
        print(f"Checking crawl status: {args.status}")
        result = app.get_crawl_status(args.status)
        if result:
            print(f"Status: {getattr(result, 'status', 'unknown')}")
        return

    print(f"Starting crawl: {args.url}")
    print(f"Limit: {args.limit or 'unlimited'}")

    try:
        job = app.crawl(args.url, limit=args.limit or 100)
        job_id = getattr(job, 'job_id', str(job))
        print(f"\nCrawl started: {job_id}")
        print(f"Check status: python firecrawl_cli.py crawl --status {job_id}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Firecrawl API CLI - LLM-Ready Web Scraping',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Map
    p = subparsers.add_parser('map', help='Discover URLs')
    p.add_argument('url', help='Target URL')
    p.add_argument('--limit', type=int, help='Max URLs')
    p.add_argument('--output', '-o', help='Output file')

    # Scrape
    p = subparsers.add_parser('scrape', help='Scrape page')
    p.add_argument('url', help='Target URL')
    p.add_argument('--format', '-f', default='markdown', help='Formats: markdown,html,json')
    p.add_argument('--output', '-o', help='Output file')

    # Search
    p = subparsers.add_parser('search', help='Search web')
    p.add_argument('query', help='Search query')
    p.add_argument('--limit', type=int, help='Max results')
    p.add_argument('--output', '-o', help='Output file')

    # Extract
    p = subparsers.add_parser('extract', help='Extract structured data')
    p.add_argument('url', nargs='?', help='Target URL')
    p.add_argument('--urls', help='URLs JSON file')
    p.add_argument('--prompt', '-p', required=True, help='Extraction prompt')
    p.add_argument('--schema', '-s', help='JSON Schema file or string')
    p.add_argument('--output', '-o', help='Output file')

    # Crawl
    p = subparsers.add_parser('crawl', help='Crawl website')
    p.add_argument('url', nargs='?', help='Target URL')
    p.add_argument('--limit', type=int, help='Max pages')
    p.add_argument('--status', help='Check job status')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print("\n" + "="*60)
        print("Firecrawl API CLI - V8.62")
        print("="*60)
        print("Commands:")
        print("  map <url>             Discover URLs")
        print("  scrape <url>          Scrape page")
        print("  search <query>         Search web")
        print("  extract <url> -p PROMPT Extract data")
        print("  crawl <url>           Crawl website")
        print()
        print("Setup:")
        print("  export FIRECRAWL_API_KEY='fc-xxx'")
        print()
        sys.exit(0)

    commands = {
        'map': cmd_map,
        'scrape': cmd_scrape,
        'search': cmd_search,
        'extract': cmd_extract,
        'crawl': cmd_crawl,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
