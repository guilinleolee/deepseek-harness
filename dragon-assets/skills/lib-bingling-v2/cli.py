# -*- coding: utf-8 -*-
"""
lib-bingling-v2 CLI - 用以致学图文生成器命令行入口
用法：
    python cli.py cover "标题" [-s "副标题"] [-p gongzhonghao] [-j zhuji] [-l full-title]
    python cli.py quote "金句" [-a 李秉凌] [-p xiaohongshu] [-j wudao]
    python cli.py jingjie "七境名" [-p xiaohongshu] [-j wudao]
"""
import argparse
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from generator_v2 import (
    generate_cover,
    generate_quote_card,
    generate_jingjie_card,
    generate_lianpo_thumbnail,
    JINGJIE_COLORS,
    SPECIAL_PALETTES,
    ALL_PALETTES,
    PLATFORM_SIZES,
    LAYOUTS,
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="lib-bingling-v2",
        description="用以致学图文生成器 V2.0",
    )
    subparsers = p.add_subparsers(dest="command", help="子命令")

    # cover 子命令
    cover_parser = subparsers.add_parser("cover", help="生成封面图")
    cover_parser.add_argument("title", nargs="?", default="", help="主标题")
    cover_parser.add_argument("-s", "--subtitle", default="", help="副标题")
    cover_parser.add_argument("-p", "--platform", default="gongzhonghao",
                            choices=list(PLATFORM_SIZES.keys()), help="平台")
    cover_parser.add_argument("-j", "--jingjie", default="zhuji",
                            choices=list(JINGJIE_COLORS.keys()), help="七境配色")
    cover_parser.add_argument("-P", "--palette", default=None,
                            choices=list(SPECIAL_PALETTES.keys()), help="特殊配色")
    cover_parser.add_argument("-l", "--layout", default="full-title",
                            choices=list(LAYOUTS.keys()), help="版式骨架")
    cover_parser.add_argument("-c", "--color-scheme", default="dark", choices=["dark", "light"], help="配色主题")
    cover_parser.add_argument("-o", "--output", default="", help="输出路径")
    cover_parser.add_argument("--no-brand", action="store_true", help="不添加品牌标识")
    cover_parser.add_argument("--list-platforms", action="store_true", help="列出平台")
    cover_parser.add_argument("--list-palettes", action="store_true", help="列出配色")
    cover_parser.add_argument("--list-layouts", action="store_true", help="列出版式")

    # quote 子命令
    quote_parser = subparsers.add_parser("quote", help="生成金句卡片")
    quote_parser.add_argument("quote", nargs="?", default="", help="金句内容")
    quote_parser.add_argument("-a", "--author", default="李秉凌", help="金句来源")
    quote_parser.add_argument("-p", "--platform", default="pengyouquan",
                            choices=list(PLATFORM_SIZES.keys()), help="平台")
    quote_parser.add_argument("-j", "--jingjie", default="wudao",
                            choices=list(JINGJIE_COLORS.keys()), help="七境配色")
    quote_parser.add_argument("-P", "--palette", default=None,
                            choices=list(SPECIAL_PALETTES.keys()), help="特殊配色")
    quote_parser.add_argument("-o", "--output", default="", help="输出路径")
    quote_parser.add_argument("--no-brand", action="store_true", help="不添加品牌标识")

    # jingjie 子命令
    jingjie_parser = subparsers.add_parser("jingjie", help="生成七境主题卡")
    jingjie_parser.add_argument("title", nargs="?", default="", help="主标题")
    jingjie_parser.add_argument("-j", "--jingjie", default="wudao",
                               choices=list(JINGJIE_COLORS.keys()), help="修炼七境")
    jingjie_parser.add_argument("-p", "--platform", default="xiaohongshu",
                               choices=list(PLATFORM_SIZES.keys()), help="平台")
    jingjie_parser.add_argument("-o", "--output", default="", help="输出路径")

    # list 子命令
    list_parser = subparsers.add_parser("list", help="列出所有选项")
    list_parser.add_argument("--platforms", action="store_true", help="列出平台")
    list_parser.add_argument("--palettes", action="store_true", help="列出配色")
    list_parser.add_argument("--layouts", action="store_true", help="列出版式")
    list_parser.add_argument("--jingjie", action="store_true", help="列出七境")

    return p


def list_platforms():
    print("\n📐 支持的平台尺寸：")
    print("-" * 60)
    for k, v in PLATFORM_SIZES.items():
        print(f"  {k:25s}  {v['ratio']:6s}  {v['width']}x{v['height']}  {v['desc']}")


def list_palettes():
    print("\n🎨 配色方案（12套）：")
    print("-" * 60)
    print("\n【老李七境系列】")
    for k, v in JINGJIE_COLORS.items():
        print(f"  {k:12s}  {v['cn']:15s}  主色 {v['main']}  强调 {v['accent']}")
    print("\n【特殊主题】")
    for k, v in SPECIAL_PALETTES.items():
        print(f"  {k:12s}  {v['cn']:10s}  主色 {v['main']}  {v['desc']}")


def list_layouts():
    print("\n📐 版式骨架（8种）：")
    print("-" * 60)
    for k, v in LAYOUTS.items():
        print(f"  {k:15s}  {v['name']:10s}  {v['desc']}")


def list_jingjie():
    print("\n🧭 修炼七境：")
    print("-" * 60)
    for k, v in JINGJIE_COLORS.items():
        print(f"  {k:12s}  {v['cn']:15s}  {v['element']}")


def auto_output_path(prefix, platform, jingjie, ext="png"):
    return f"bingling-{prefix}-{platform}-{jingjie}.{ext}"


def main():
    args = build_parser().parse_args()

    if not args.command or args.command == "list":
        if hasattr(args, 'platforms') and args.platforms:
            list_platforms()
        elif hasattr(args, 'palettes') and args.palettes:
            list_palettes()
        elif hasattr(args, 'layouts') and args.layouts:
            list_layouts()
        elif hasattr(args, 'jingjie') and args.jingjie:
            list_jingjie()
        else:
            # 列出所有
            list_platforms()
            list_palettes()
            list_layouts()
            list_jingjie()
        return 0

    if args.command == "cover":
        if args.list_platforms:
            list_platforms()
            return 0
        if args.list_palettes:
            list_palettes()
            return 0
        if args.list_layouts:
            list_layouts()
            return 0

        title = args.title
        if not title:
            print("[ERROR] 需要提供标题"); return 1

        output = args.output or auto_output_path("cover", args.platform, args.jingjie)

        print(f"[封面生成] title={title} platform={args.platform} jingjie={args.jingjie} layout={args.layout}")

        out = generate_cover(
            title=title,
            subtitle=args.subtitle,
            jingjie=args.jingjie,
            palette=args.palette,
            platform=args.platform,
            layout=args.layout,
            color_scheme=args.color_scheme,
            brand_mark=not args.no_brand,
            output=output
        )
        print(f"[成功] 已生成: {out}")
        return 0

    elif args.command == "quote":
        quote = args.quote
        if not quote:
            print("[ERROR] 需要提供金句内容"); return 1

        output = args.output or auto_output_path("quote", args.platform, args.jingjie)

        print(f"[金句卡片] quote={quote} platform={args.platform} jingjie={args.jingjie}")

        out = generate_quote_card(
            quote=quote,
            author=args.author,
            jingjie=args.jingjie,
            palette=args.palette,
            platform=args.platform,
            brand_mark=not args.no_brand,
            output=output
        )
        print(f"[成功] 已生成: {out}")
        return 0

    elif args.command == "jingjie":
        title = args.title
        if not title:
            print("[ERROR] 需要提供标题"); return 1

        output = args.output or auto_output_path("jingjie", args.platform, args.jingjie)

        print(f"[七境卡片] title={title} jingjie={args.jingjie} platform={args.platform}")

        out = generate_jingjie_card(
            title=title,
            jingjie=args.jingjie,
            platform=args.platform,
            output=output
        )
        print(f"[成功] 已生成: {out}")
        return 0

    else:
        print(f"[ERROR] 未知命令: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
