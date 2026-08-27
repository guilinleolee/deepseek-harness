#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_dashboard.py · 天龙引擎 内容数据复盘 命令
================================================

自媒体工作台第⑤层：发布内容的数据复盘。
- 记录发布内容（平台/标题/类型/各互动数据）
- 查看内容列表
- 汇总统计（KPI + 平台分布 + TOP内容）

调用：
    python scripts/run_dashboard.py add --platform xiaohongshu --title "..." \
        --type 图文 --link https://... --views 1200 --likes 85 \
        --comments 23 --favorites 40 --shares 5 --fans 12 --note "..."
    python scripts/run_dashboard.py list
    python scripts/run_dashboard.py stats
    python scripts/run_dashboard.py stats --platform douyin

输出：
    ~/viral-content-reports/dashboard/posts.csv

仅用 Python 标准库（argparse / csv / pathlib / datetime）。
要求 Python ≥ 3.8。
"""
from __future__ import annotations

import argparse
import sys
import os
import csv
from pathlib import Path
from datetime import datetime

# Windows GBK 兼容：强制 UTF-8 输出
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


SCRIPT_DIR = Path(__file__).resolve().parent
DRAGON_ROOT = SCRIPT_DIR.parent

# Windows 兼容：home directory fallback
def _get_home_dir() -> Path:
    """获取用户主目录，多重 fallback"""
    try:
        home = Path.home()
        if home and home.exists():
            return home
    except (RuntimeError, ValueError):
        pass
    userprofile = os.environ.get("USERPROFILE")
    if userprofile and Path(userprofile).exists():
        return Path(userprofile)
    home_env = os.environ.get("HOME")
    if home_env and Path(home_env).exists():
        return Path(home_env)
    drive = os.environ.get("HOMEDRIVE")
    path = os.environ.get("HOMEPATH")
    if drive and path:
        combined = Path(drive + path)
        if combined.exists():
            return combined
    fallback = Path("C:/Users/li")
    if fallback.exists():
        return fallback
    return Path(os.environ.get("TEMP", "C:/Windows/Temp"))


HOME_DIR = _get_home_dir()
DASHBOARD_DIR = HOME_DIR / "viral-content-reports" / "dashboard"
POSTS_CSV = DASHBOARD_DIR / "posts.csv"

# CSV 列定义
FIELDS = [
    "id", "date", "platform", "title", "type", "link",
    "views", "likes", "comments", "favorites", "shares", "fans",
    "note",
]

# 平台中文映射
PLATFORMS = {
    "xiaohongshu": "小红书",
    "douyin": "抖音",
    "wechat": "公众号",
    "zhihu": "知乎",
    "bilibili": "B站",
    "video": "视频号",
    "weibo": "微博",
}

# 内容类型
TYPES = ["图文", "短视频", "长视频", "文章", "动态", "其他"]


def load_posts() -> list[dict]:
    """读取现有 CSV（不存在则返回空）"""
    if not POSTS_CSV.exists():
        return []
    try:
        with open(POSTS_CSV, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            return [row for row in reader]
    except (OSError, csv.Error):
        return []


def save_posts(posts: list[dict]) -> None:
    """保存全部记录到 CSV"""
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    with open(POSTS_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(posts)


def _to_int(v) -> int:
    """安全转 int"""
    try:
        return int(float(v or 0))
    except (ValueError, TypeError):
        return 0


def cmd_add(args) -> int:
    """添加一条内容记录"""
    posts = load_posts()
    new_id = max((_to_int(p.get("id")) for p in posts), default=0) + 1

    record = {
        "id": new_id,
        "date": args.date or datetime.now().strftime("%Y-%m-%d"),
        "platform": args.platform,
        "title": args.title,
        "type": args.type,
        "link": args.link or "",
        "views": _to_int(args.views),
        "likes": _to_int(args.likes),
        "comments": _to_int(args.comments),
        "favorites": _to_int(args.favorites),
        "shares": _to_int(args.shares),
        "fans": _to_int(args.fans),
        "note": args.note or "",
    }
    posts.append(record)
    save_posts(posts)

    print(f"✅ 已记录内容 #{new_id}")
    print(f"   {PLATFORMS.get(args.platform, args.platform)} · {record['date']} · {record['title'][:30]}")
    print(f"   阅读 {record['views']} | 点赞 {record['likes']} | 评论 {record['comments']} | 收藏 {record['favorites']} | 转发 {record['shares']}")
    print(f"   涨粉 {record['fans']}")
    print(f"   数据文件: {POSTS_CSV}")
    return 0


def cmd_list(args) -> int:
    """列出内容记录"""
    posts = load_posts()
    if not posts:
        print(f"📭 暂无内容记录（{POSTS_CSV}）")
        print("   用 add 子命令添加：python scripts/run_dashboard.py add --help")
        return 0

    # 过滤平台
    if args.platform:
        posts = [p for p in posts if p.get("platform") == args.platform]

    print(f"📋 内容记录（{len(posts)} 条）")
    if args.platform:
        print(f"   平台: {PLATFORMS.get(args.platform, args.platform)}")
    print()
    for p in posts:
        print(f"  #{p['id']} [{p['date']}] {PLATFORMS.get(p['platform'], p['platform'])} "
              f"《{p['title'][:25]}》")
        print(f"      阅读 {p['views']} | 赞 {p['likes']} | 评 {p['comments']} | "
              f"藏 {p['favorites']} | 转 {p['shares']} | 涨粉 {p['fans']}")
    return 0


def cmd_stats(args) -> int:
    """汇总统计"""
    posts = load_posts()
    if not posts:
        print(f"📭 暂无内容记录（{POSTS_CSV}）")
        return 0

    if args.platform:
        posts = [p for p in posts if p.get("platform") == args.platform]
        label = PLATFORMS.get(args.platform, args.platform)
    else:
        label = "全部平台"

    n = len(posts)
    total_views = sum(_to_int(p.get("views")) for p in posts)
    total_likes = sum(_to_int(p.get("likes")) for p in posts)
    total_comments = sum(_to_int(p.get("comments")) for p in posts)
    total_favs = sum(_to_int(p.get("favorites")) for p in posts)
    total_shares = sum(_to_int(p.get("shares")) for p in posts)
    total_fans = sum(_to_int(p.get("fans")) for p in posts)
    total_interact = total_likes + total_comments + total_favs + total_shares
    interact_rate = total_interact / total_views * 100 if total_views else 0

    print(f"📊 数据复盘 · {label}（{n} 条内容）")
    print("=" * 50)
    print(f"  总阅读:   {total_views:,}")
    print(f"  总互动:   {total_interact:,}（赞+评+藏+转）")
    print(f"  互动率:   {interact_rate:.1f}%")
    print(f"  总涨粉:   +{total_fans}")
    print()

    # 平台分布
    if not args.platform:
        by_platform: dict[str, dict] = {}
        for p in posts:
            plat = PLATFORMS.get(p.get("platform", ""), p.get("platform", "其他"))
            d = by_platform.setdefault(plat, {"count": 0, "views": 0, "interact": 0})
            d["count"] += 1
            d["views"] += _to_int(p.get("views"))
            d["interact"] += (_to_int(p.get("likes")) + _to_int(p.get("comments"))
                              + _to_int(p.get("favorites")) + _to_int(p.get("shares")))
        print(f"  平台分布:")
        for plat, d in by_platform.items():
            rate = d["interact"] / d["views"] * 100 if d["views"] else 0
            print(f"    {plat}: {d['count']}条 | 阅读 {d['views']:,} | 互动率 {rate:.1f}%")

    # TOP 内容（按互动率）
    print()
    scored = []
    for p in posts:
        views = _to_int(p.get("views"))
        interact = (_to_int(p.get("likes")) + _to_int(p.get("comments"))
                    + _to_int(p.get("favorites")) + _to_int(p.get("shares")))
        rate = interact / views * 100 if views else 0
        scored.append((rate, p))
    scored.sort(key=lambda x: x[0], reverse=True)

    print(f"  🏆 TOP 3 内容（按互动率）:")
    for rate, p in scored[:3]:
        print(f"    [{rate:.1f}%] 《{p['title'][:25]}》{PLATFORMS.get(p['platform'], p['platform'])}")
    print()
    print(f"  数据文件: {POSTS_CSV}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="天龙引擎 内容数据复盘（记录/列表/统计）"
    )
    sub = parser.add_subparsers(dest="action", help="子命令")

    # add
    p_add = sub.add_parser("add", help="添加内容记录")
    p_add.add_argument("--platform", required=True, choices=list(PLATFORMS.keys()),
                       help="平台：小红书/抖音/公众号/知乎/B站/视频号/微博")
    p_add.add_argument("--title", required=True, help="内容标题")
    p_add.add_argument("--type", choices=TYPES, default="图文", help="内容类型")
    p_add.add_argument("--date", help="发布日期（默认今天 YYYY-MM-DD）")
    p_add.add_argument("--link", default="", help="内容链接")
    p_add.add_argument("--views", default=0, help="阅读/播放量")
    p_add.add_argument("--likes", default=0, help="点赞数")
    p_add.add_argument("--comments", default=0, help="评论数")
    p_add.add_argument("--favorites", default=0, help="收藏数")
    p_add.add_argument("--shares", default=0, help="转发数")
    p_add.add_argument("--fans", default=0, help="涨粉数")
    p_add.add_argument("--note", default="", help="备注（选题来源等）")

    # list
    p_list = sub.add_parser("list", help="列出内容记录")
    p_list.add_argument("--platform", choices=list(PLATFORMS.keys()), help="按平台过滤")

    # stats
    p_stats = sub.add_parser("stats", help="汇总统计")
    p_stats.add_argument("--platform", choices=list(PLATFORMS.keys()), help="按平台统计")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.action:
        print("❌ 缺少子命令")
        print("用法: python scripts/run_dashboard.py <add|list|stats> [参数]")
        return 1

    if args.action == "add":
        return cmd_add(args)
    elif args.action == "list":
        return cmd_list(args)
    elif args.action == "stats":
        return cmd_stats(args)
    else:
        print(f"❌ 未知子命令: {args.action}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
