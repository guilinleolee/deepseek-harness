"""
命令行入口
"""

import sys
import argparse
from typing import List, Optional

from . import fetch_article, fetch_batch, clear_cache
from .models import Article


def cmd_fetch(args) -> None:
    """获取单篇文章"""
    url = args.url
    use_cache = not args.no_cache

    print(f"获取文章: {url}")
    article = fetch_article(url, use_cache=use_cache)

    if article:
        print(f"\n✓ 获取成功")
        print(f"标题: {article.title}")
        print(f"作者: {article.author}")
        print(f"公众号: {article.account_name}")
        print(f"字数: {article.word_count}")
        print(f"来源: {article.source}")

        # 保存到文件
        if args.output:
            if args.output.endswith('.json'):
                article.save_json(args.output)
                print(f"\n已保存JSON: {args.output}")
            elif args.output.endswith('.md'):
                article.save_markdown(args.output)
                print(f"\n已保存Markdown: {args.output}")
            else:
                article.save_markdown(args.output)
                print(f"\n已保存: {args.output}")
    else:
        print("\n✗ 获取失败")
        sys.exit(1)


def cmd_batch(args) -> None:
    """批量获取文章"""
    urls = []

    # 从文件读取
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
    # 从命令行参数
    elif args.urls:
        urls = args.urls
    else:
        print("错误: 请提供URL列表（-f file.txt 或 url1 url2 ...）")
        sys.exit(1)

    print(f"批量获取 {len(urls)} 篇文章...")

    articles = fetch_batch(
        urls,
        use_cache=not args.no_cache,
        concurrent=args.concurrent
    )

    # 统计
    success = sum(1 for a in articles if a)
    failed = len(articles) - success

    print(f"\n✓ 成功: {success}")
    print(f"✗ 失败: {failed}")

    # 显示结果
    if args.show_list:
        for i, article in enumerate(articles):
            if article:
                print(f"[{i+1}] {article.title}")
            else:
                print(f"[{i+1}] <获取失败>")


def cmd_cache(args) -> None:
    """缓存管理"""
    if args.action == "clear":
        count = clear_cache()
        print(f"✓ 已清理 {count} 条缓存")
    elif args.action == "stats":
        from . import get_default_fetcher
        fetcher = get_default_fetcher()
        stats = fetcher.get_cache_stats()
        print(f"缓存统计:")
        print(f"  L1内存: {stats.get('l1', {}).get('size', 0)} 条")
        print(f"  L2磁盘: {stats.get('l2', {}).get('total', 0)} 条")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="微信公众号文章获取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # fetch命令
    fetch_parser = subparsers.add_parser('fetch', help='获取单篇文章')
    fetch_parser.add_argument('url', help='文章URL')
    fetch_parser.add_argument('-o', '--output', help='保存文件路径')
    fetch_parser.add_argument('--no-cache', action='store_true', help='不使用缓存')
    fetch_parser.set_defaults(func=cmd_fetch)

    # batch命令
    batch_parser = subparsers.add_parser('batch', help='批量获取文章')
    batch_parser.add_argument('-f', '--file', help='URL列表文件')
    batch_parser.add_argument('urls', nargs='*', help='URL列表')
    batch_parser.add_argument('-c', '--concurrent', type=int, default=3, help='并发数')
    batch_parser.add_argument('--no-cache', action='store_true', help='不使用缓存')
    batch_parser.add_argument('--show-list', action='store_true', help='显示结果列表')
    batch_parser.set_defaults(func=cmd_batch)

    # cache命令
    cache_parser = subparsers.add_parser('cache', help='缓存管理')
    cache_parser.add_argument('action', choices=['clear', 'stats'], help='操作')
    cache_parser.set_defaults(func=cmd_cache)

    # 解析参数
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 执行命令
    args.func(args)


if __name__ == "__main__":
    main()
