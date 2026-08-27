#!/usr/bin/env python3
"""
Web Scraping SKILL - 命令行接口

Usage:
    python scrape.py single <url> [--selector SELECTOR]
    python scrape.py batch <file> [--output OUTPUT]
    python scrape.py monitor <urls>...
"""

import sys
import argparse
from pathlib import Path

# 添加核心模块路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.fetcher import ScraplingFetcher


def cmd_single(args):
    """单页爬取命令"""
    print(f"🎯 爬取: {args.url}")

    fetcher = ScraplingFetcher(stealth=True)

    try:
        result = fetcher.fetch_single(args.url, args.selector)
        print(f"✅ 成功!")
        print(f"📄 结果:\n{result[:500]}")

        # 导出结果
        if args.output:
            import json
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump({'url': args.url, 'data': result}, f, ensure_ascii=False, indent=2)
            print(f"💾 已保存到: {args.output}")

    except Exception as e:
        print(f"❌ 失败: {e}")
        sys.exit(1)


def cmd_batch(args):
    """批量爬取命令"""
    print(f"📦 批量爬取: {args.file}")

    # 读取URL列表
    with open(args.file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"📋 共 {len(urls)} 个URL")

    fetcher = ScraplingFetcher(stealth=True)

    try:
        results = fetcher.fetch_batch(urls, delay=args.delay)

        # 导出结果
        output = args.output or "batch_results.json"
        fetcher.export_results(results, output, format=args.format)
        print(f"✅ 完成! 结果已保存到: {output}")

        # 打印统计
        fetcher.print_stats()

    except Exception as e:
        print(f"❌ 失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Web Scraping SKILL - 命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  单页爬取:  python scrape.py single https://example.com --selector "h1"
  批量爬取:  python scrape.py batch urls.txt --output results.json
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # single 命令
    parser_single = subparsers.add_parser('single', help='单页爬取')
    parser_single.add_argument('url', help='目标URL')
    parser_single.add_argument('--selector', '-s', help='CSS选择器')
    parser_single.add_argument('--output', '-o', help='输出文件路径')
    parser_single.set_defaults(func=cmd_single)

    # batch 命令
    parser_batch = subparsers.add_parser('batch', help='批量爬取')
    parser_batch.add_argument('file', help='URL列表文件')
    parser_batch.add_argument('--output', '-o', help='输出文件路径', default='batch_results.json')
    parser_batch.add_argument('--format', '-f', choices=['json', 'csv', 'excel'], default='json', help='输出格式')
    parser_batch.add_argument('--delay', '-d', type=float, default=2.0, help='请求间隔(秒)')
    parser_batch.set_defaults(func=cmd_batch)

    # 解析参数
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 执行命令
    args.func(args)


if __name__ == "__main__":
    main()
