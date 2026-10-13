#!/usr/bin/env python3
"""
PPT Template Marketplace CLI

模板市场命令行客户端
"""

import argparse
import json
import sys
from pathlib import Path


def cmd_stats(args):
    """统计信息"""
    from marketplace_server import TemplateMarketplace, DB_PATH, TEMPLATES_DIR
    marketplace = TemplateMarketplace(DB_PATH, TEMPLATES_DIR)
    result = marketplace.get_stats()

    print(f"\n{'='*40}")
    print(f"  📊 模板市场统计")
    print(f"{'='*40}")
    print(f"总模板数: {result.get('total_templates', 0)}")
    print(f"已发布: {result.get('published_templates', 0)}")
    print(f"待审核: {result.get('pending_templates', 0)}")
    print(f"总下载: {result.get('total_downloads', 0)}")


def cmd_list(args):
    """列出模板"""
    from marketplace_server import TemplateMarketplace, TemplateType, TemplateStatus, DB_PATH, TEMPLATES_DIR
    marketplace = TemplateMarketplace(DB_PATH, TEMPLATES_DIR)

    type_filter = None
    if args.type:
        try:
            type_filter = TemplateType(args.type)
        except ValueError:
            pass

    templates = marketplace.list_templates(
        type=type_filter,
        category=args.category,
        search=args.search,
        page=args.page,
        page_size=args.page_size
    )

    if not templates:
        print("未找到模板")
        return

    print(f"\n{'='*60}")
    print(f"  找到 {len(templates)} 个模板")
    print(f"{'='*60}\n")

    for t in templates:
        status_icon = {
            "draft": "📝",
            "pending": "⏳",
            "approved": "✅",
            "rejected": "❌",
            "archived": "📦"
        }.get(t.status.value, "📄")

        print(f"{status_icon} [{t.type.value.upper()}] {t.name}")
        print(f"   摘要: {t.summary[:50] if t.summary else ''}...")
        print(f"   作者: {t.author} | 下载: {t.downloads} | 评分: {t.rating:.1f}")
        print(f"   标签: {', '.join(t.tags)}")
        print()


def cmd_publish(args):
    """发布模板"""
    from marketplace_server import TemplateMarketplace, TemplateType, DB_PATH, TEMPLATES_DIR
    marketplace = TemplateMarketplace(DB_PATH, TEMPLATES_DIR)

    if not args.name:
        print("错误: 请指定模板名称 --name")
        sys.exit(1)

    if not args.files:
        print("错误: 请指定模板文件 --files")
        sys.exit(1)

    files = [f.strip() for f in args.files.split(',')]
    tags = args.tags.split(',') if args.tags else []

    template = marketplace.publish_template(
        name=args.name,
        type=TemplateType(args.type or 'brand'),
        summary=args.summary or '',
        author=args.author or 'anonymous',
        files=files,
        category=args.category or 'general',
        tags=tags,
        description=args.description or ''
    )

    print(f"\n✅ 模板发布成功!")
    print(f"   ID: {template.id}")
    print(f"   名称: {template.name}")
    print(f"   状态: {template.status.value}")
    print(f"   等待审核中...")


def cmd_get(args):
    """获取模板详情"""
    from marketplace_server import TemplateMarketplace, DB_PATH, TEMPLATES_DIR
    marketplace = TemplateMarketplace(DB_PATH, TEMPLATES_DIR)
    template = marketplace.get_template(args.id)

    if not template:
        print(f"错误: 找不到模板 {args.id}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  模板详情: {template.name}")
    print(f"{'='*60}")
    print(f"ID: {template.id}")
    print(f"类型: {template.type.value}")
    print(f"状态: {template.status.value}")
    print(f"作者: {template.author}")
    print(f"摘要: {template.summary}")
    print(f"描述: {template.description}")
    print(f"标签: {', '.join(template.tags)}")
    print(f"分类: {template.category}")
    print(f"下载: {template.downloads}")
    print(f"评分: {template.rating:.1f} ({template.rating_count}人)")
    print(f"创建: {template.created_at}")
    print(f"版本: {template.version}")


def cmd_rate(args):
    """评分"""
    from marketplace_server import TemplateMarketplace, DB_PATH, TEMPLATES_DIR
    marketplace = TemplateMarketplace(DB_PATH, TEMPLATES_DIR)

    if args.rating < 1 or args.rating > 5:
        print("错误: 评分必须在1-5之间")
        sys.exit(1)

    success = marketplace.rate_template(
        template_id=args.id,
        user_id=args.user or 'anonymous',
        rating=args.rating,
        comment=args.comment or ''
    )

    if success:
        print(f"\n✅ 评分成功! 您给这个模板打了 {args.rating} 星。")
    else:
        print(f"\n❌ 评分失败")


def cmd_favorite(args):
    """收藏"""
    from marketplace_server import TemplateMarketplace, DB_PATH, TEMPLATES_DIR
    marketplace = TemplateMarketplace(DB_PATH, TEMPLATES_DIR)

    if args.remove:
        success = marketplace.unfavorite(args.id, args.user or 'anonymous')
        if success:
            print(f"\n✅ 已取消收藏!")
    else:
        success = marketplace.favorite(args.id, args.user or 'anonymous')
        if success:
            print(f"\n✅ 收藏成功!")
        else:
            print(f"\n⚠️ 已收藏过该模板")


def main():
    parser = argparse.ArgumentParser(
        description='PPT模板市场CLI客户端',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # list命令
    list_parser = subparsers.add_parser('list', help='列出模板')
    list_parser.add_argument('--type', '-t', choices=['brand', 'layout', 'deck', 'chart'],
                           help='模板类型')
    list_parser.add_argument('--category', '-c', help='分类')
    list_parser.add_argument('--search', '-s', help='搜索关键词')
    list_parser.add_argument('--page', '-p', type=int, default=1, help='页码')
    list_parser.add_argument('--page-size', type=int, default=20, help='每页数量')

    # publish命令
    pub_parser = subparsers.add_parser('publish', help='发布模板')
    pub_parser.add_argument('--name', '-n', required=True, help='模板名称')
    pub_parser.add_argument('--type', '-t', default='brand', help='类型')
    pub_parser.add_argument('--summary', help='摘要')
    pub_parser.add_argument('--author', default='anonymous', help='作者')
    pub_parser.add_argument('--files', required=True, help='文件路径(逗号分隔)')
    pub_parser.add_argument('--category', default='general', help='分类')
    pub_parser.add_argument('--tags', help='标签(逗号分隔)')
    pub_parser.add_argument('--description', help='描述')

    # get命令
    get_parser = subparsers.add_parser('get', help='获取模板详情')
    get_parser.add_argument('id', help='模板ID')

    # rate命令
    rate_parser = subparsers.add_parser('rate', help='评分')
    rate_parser.add_argument('id', help='模板ID')
    rate_parser.add_argument('rating', type=int, help='评分(1-5)')
    rate_parser.add_argument('--user', '-u', default='anonymous', help='用户ID')
    rate_parser.add_argument('--comment', '-c', help='评论')

    # favorite命令
    fav_parser = subparsers.add_parser('favorite', help='收藏')
    fav_parser.add_argument('id', help='模板ID')
    fav_parser.add_argument('--user', '-u', default='anonymous', help='用户ID')
    fav_parser.add_argument('--remove', action='store_true', help='取消收藏')

    # stats命令
    subparsers.add_parser('stats', help='统计信息')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        'list': cmd_list,
        'publish': cmd_publish,
        'get': cmd_get,
        'rate': cmd_rate,
        'favorite': cmd_favorite,
        'stats': cmd_stats
    }

    commands[args.command](args)


if __name__ == '__main__':
    main()
