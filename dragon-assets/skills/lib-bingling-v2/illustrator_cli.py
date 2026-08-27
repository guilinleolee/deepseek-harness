# -*- coding: utf-8 -*-
"""
老李配图生成器 CLI
用法：
    python illustrator_cli.py analyze "文章内容"
    python illustrator_cli.py shot "文章内容"
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from illustrator_engine import LaoLiIllustrator


def main():
    parser = argparse.ArgumentParser(description="老李配图生成器")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="分析内容，识别认知锚点")
    analyze_parser.add_argument("content", nargs="?", help="文章内容")

    # shot 命令
    shot_parser = subparsers.add_parser("shot", help="生成Shot List")
    shot_parser.add_argument("content", nargs="?", help="文章内容")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if not args.content:
        print("[ERROR] 需要提供内容"); return 1

    illustrator = LaoLiIllustrator()

    if args.command == "analyze":
        print("\n🔍 正在分析内容...")
        anchors = illustrator.analyze(args.content)
        print(f"\n✅ 识别到 {len(anchors)} 个认知锚点：\n")
        for i, anchor in enumerate(anchors, 1):
            print(f"{i}. [{anchor.type.value}] {anchor.concept}")
            print(f"   位置: {anchor.position}")

    elif args.command == "shot":
        print("\n📋 正在生成Shot List...")
        shots = illustrator.generate_shot_list(args.content)
        print(illustrator.print_shot_list(shots))

    return 0


if __name__ == "__main__":
    sys.exit(main())
