#!/usr/bin/env python3
"""
独立推广渠道查询工具
用法:
  python query_channels.py --category cn_community
  python query_channels.py --keyword "独立开发"
  python query_channels.py --platform overseas
  python query_channels.py --scene "独立开发者首发"
  python query_channels.py --list           # 列出所有渠道
  python query_channels.py --stats        # 统计信息
"""

import json
import argparse
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(os.path.dirname(SCRIPT_DIR), "data", "channels.json")


def load_channels():
    if not os.path.exists(DATA_FILE):
        print(f"错误: 找不到数据文件 {DATA_FILE}")
        print("请先运行 parse_channels.py 下载数据")
        return None
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def keyword_match(text, keyword):
    """模糊匹配（忽略大小写）"""
    if not text or not keyword:
        return False
    return keyword.lower() in text.lower()


def filter_channels(channels, category=None, keyword=None, platform=None, scene=None):
    """过滤渠道"""
    results = channels

    if category:
        results = [c for c in results if c.get("category") == category]

    if keyword:
        results = [
            c
            for c in results
            if keyword_match(c.get("name", ""), keyword)
            or keyword_match(c.get("description", ""), keyword)
            or keyword_match(c.get("url", ""), keyword)
        ]

    if platform:
        platform = platform.lower()
        if platform == "cn":
            results = [
                c
                for c in results
                if c.get("category", "").startswith("cn_")
            ]
        elif platform == "overseas":
            results = [
                c
                for c in results
                if not c.get("category", "").startswith("cn_")
            ]
        elif platform == "ai":
            results = [
                c
                for c in results
                if c.get("category", "") == "ai_directory"
                or "AI" in c.get("name", "")
                or "AI" in c.get("description", "")
            ]

    if scene:
        scene = scene.lower()
        scene_keywords = {
            "首发": ["product hunt", "hacker news", "少数派", "掘金", "首发"],
            "独立开发": ["独立", "indie", "maker", "产品发现"],
            "出海": ["product hunt", "reddit", "indie", "overseas"],
            "社区": ["社区", "forum", "v2ex", "reddit"],
            "导航": ["导航", "directory", "目录"],
            "资源": ["资源", "工具", "tools", "导航"],
        }
        matched_kw = scene_keywords.get(scene, [scene])
        results = [
            c
            for c in results
            if any(
                keyword_match(c.get("name", "") + " " + c.get("description", ""), kw)
                for kw in matched_kw
            )
        ]

    return results


def print_channel(c, index=None):
    """打印单个渠道"""
    prefix = f"[{index}] " if index else ""
    name = c.get("name", "未知")
    url = c.get("url", "")
    desc = c.get("description", "")
    cat = c.get("category_cn", c.get("category", ""))

    # 高亮关键词（如果指定了）
    print(f"{prefix}{name}")
    print(f"    分类: {cat}")
    print(f"    URL:  {url}")
    if desc:
        print(f"    描述: {desc}")
    print()


def print_stats(data):
    """打印统计信息"""
    channels = data.get("channels", [])
    total = len(channels)

    # 按分类统计
    stats = {}
    for ch in channels:
        cat = ch.get("category_cn", ch.get("category", "未知"))
        stats[cat] = stats.get(cat, 0) + 1

    print(f"\n📊 渠道统计")
    print(f"   总数: {total}")
    print(f"   分类:")
    for cat, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"   - {cat}: {count}")


CATEGORY_ALIASES = {
    "cn_website": "国内网站",
    "cn_directory": "网址导航",
    "cn_community": "社区论坛",
    "overseas_website": "海外网站",
    "ai_directory": "AI导航",
    "overseas_directory": "海外目录",
    "overseas_community": "海外社区",
    "reddit": "Reddit",
    "website": "cn_website",
    "directory": "cn_directory",
    "community": "cn_community",
    "all": None,
}

PLATFORM_ALIASES = {
    "cn": "cn",
    "国内": "cn",
    "overseas": "overseas",
    "海外": "overseas",
    "ai": "ai",
    "ai导航": "ai",
    "all": None,
}


def resolve_category(value):
    if not value:
        return None
    value = value.lower().strip()
    # 先精确匹配
    if value in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[value]
    # 再模糊匹配
    for key, cat_id in CATEGORY_ALIASES.items():
        if key in value or value in key:
            return cat_id
    return value


def resolve_platform(value):
    if not value:
        return None
    value = value.lower().strip()
    return PLATFORM_ALIASES.get(value, value)


def main():
    parser = argparse.ArgumentParser(
        description="独立推广渠道查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python query_channels.py --list
  python query_channels.py --stats
  python query_channels.py --category cn_community
  python query_channels.py --keyword "独立开发"
  python query_channels.py --scene "独立开发者首发"
        """,
    )
    parser.add_argument("--list", action="store_true", help="列出所有渠道")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    parser.add_argument(
        "--category", "-c", type=str, help="按分类筛选 (cn_website/cn_community/overseas_website/ai_directory/reddit 等)"
    )
    parser.add_argument("--keyword", "-k", type=str, help="关键词搜索（名称/描述/URL）")
    parser.add_argument(
        "--platform",
        "-p",
        type=str,
        help="按平台筛选 (cn/overseas/ai)",
    )
    parser.add_argument(
        "--scene", "-s", type=str, help="按场景推荐 (首发/独立开发/出海/社区/导航/资源)"
    )
    parser.add_argument(
        "--limit", "-n", type=int, default=50, help="最多显示数量 (默认50)"
    )

    args = parser.parse_args()

    data = load_channels()
    if not data:
        return 1

    # 默认行为：列出 + 统计
    if not any([args.list, args.stats, args.category, args.keyword, args.platform, args.scene]):
        args.stats = True
        args.list = True

    channels = data.get("channels", [])

    if args.stats:
        print_stats(data)

    if args.list or args.category or args.keyword or args.platform or args.scene:
        # 构建过滤条件
        cat = resolve_category(args.category) if args.category else None
        plat = resolve_platform(args.platform) if args.platform else None

        results = filter_channels(
            channels,
            category=cat,
            keyword=args.keyword,
            platform=plat,
            scene=args.scene,
        )

        total = len(results)
        shown = min(total, args.limit)

        if args.keyword or args.category or args.platform or args.scene:
            print(f"\n🔍 找到 {total} 个匹配渠道")

        print(f"\n📋 渠道列表 (显示 {shown}/{total}):")
        print("=" * 60)

        for i, ch in enumerate(results[:args.limit], 1):
            print_channel(ch, i)

        if total > args.limit:
            print(f"... 还有 {total - args.limit} 个渠道 (使用 --limit 增加显示数量)")

    return 0


if __name__ == "__main__":
    exit(main())