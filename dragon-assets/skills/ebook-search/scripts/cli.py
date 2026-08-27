#!/usr/bin/env python3
"""
ebook-search CLI - 电子书搜索命令行工具
"""

import argparse
import json
import sys
import subprocess
from pathlib import Path

# 脚本目录
SCRIPT_DIR = Path(__file__).parent


def main():
    parser = argparse.ArgumentParser(
        prog="ebook-search",
        description="电子书搜索工具 - 支持Z-Library和Libgen双引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  ebook-search "Python编程"              # 搜索书籍
  ebook-search "Python编程" -f pdf       # 只搜索PDF格式
  ebook-search "Stephen King" -t author  # 按作者搜索
  ebook-search "机器学习" -e libgen      # 只用Libgen搜索
  ebook-search "深度学习" -j             # JSON格式输出

下载:
  ebook-search download --url "..."      # 从链接下载
  ebook-search download --input results.json --index 1  # 从搜索结果下载

更多帮助请访问: https://github.com/your-repo/ebook-search
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # 搜索命令
    search_parser = subparsers.add_parser("search", help="搜索电子书")
    search_parser.add_argument("query", help="搜索关键词")
    search_parser.add_argument("--engine", "-e", choices=["zlibrary", "libgen", "both"],
                              default="both", help="搜索引擎")
    search_parser.add_argument("--type", "-t", choices=["title", "author"],
                              default="title", help="搜索类型")
    search_parser.add_argument("--format", "-f", help="格式过滤")
    search_parser.add_argument("--language", "-l", help="语言过滤")
    search_parser.add_argument("--year-from", type=int, help="起始年份")
    search_parser.add_argument("--year-to", type=int, help="结束年份")
    search_parser.add_argument("--json", "-j", action="store_true", help="JSON输出")
    search_parser.add_argument("--save", "-s", help="保存结果到文件")

    # 下载命令
    download_parser = subparsers.add_parser("download", help="下载电子书")
    download_parser.add_argument("--url", "-u", help="下载链接")
    download_parser.add_argument("--index", "-i", type=int, help="搜索结果索引")
    download_parser.add_argument("--input", "-f", help="搜索结果JSON文件")
    download_parser.add_argument("--output", "-o", help="下载目录")
    download_parser.add_argument("--notebooklm", "-n", action="store_true",
                                help="上传到NotebookLM")
    download_parser.add_argument("--title", "-t", help="书籍标题")

    # 版本命令
    parser.add_argument("--version", "-v", action="version", version="%(prog)s 1.0.0")

    args = parser.parse_args()

    # 默认搜索命令
    if not args.command:
        # 如果直接带参数，当作搜索
        if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
            args.command = "search"
            args.query = sys.argv[1]
            # 解析其他参数
            i = 2
            while i < len(sys.argv):
                if sys.argv[i] in ['-e', '--engine'] and i + 1 < len(sys.argv):
                    args.engine = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-t', '--type'] and i + 1 < len(sys.argv):
                    args.type = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-f', '--format'] and i + 1 < len(sys.argv):
                    args.format = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] in ['-j', '--json']:
                    args.json = True
                    i += 1
                else:
                    i += 1
        else:
            parser.print_help()
            return 0

    # 执行搜索
    if args.command == "search":
        search_script = SCRIPT_DIR / "search.py"
        cmd = [sys.executable, str(search_script), args.query]
        cmd.extend(["--engine", args.engine])
        cmd.extend(["--type", args.type])

        if args.format:
            cmd.extend(["--format", args.format])
        if args.language:
            cmd.extend(["--language", args.language])
        if args.year_from:
            cmd.extend(["--year-from", str(args.year_from)])
        if args.year_to:
            cmd.extend(["--year-to", str(args.year_to)])
        if args.json:
            cmd.append("--json")

        result = subprocess.run(cmd)

        # 保存结果
        if args.save and result.returncode == 0:
            # 重新运行获取JSON
            cmd.append("--json")
            json_result = subprocess.run(cmd, capture_output=True, text=True)
            if json_result.returncode == 0:
                with open(args.save, 'w', encoding='utf-8') as f:
                    f.write(json_result.stdout)
                print(f"\n💾 结果已保存到: {args.save}", file=sys.stderr)

        return result.returncode

    # 执行下载
    elif args.command == "download":
        download_script = SCRIPT_DIR / "download.py"
        cmd = [sys.executable, str(download_script)]

        if args.url:
            cmd.extend(["--url", args.url])
        if args.index:
            cmd.extend(["--index", str(args.index)])
        if args.input:
            cmd.extend(["--input", args.input])
        if args.output:
            cmd.extend(["--output", args.output])
        if args.notebooklm:
            cmd.append("--notebooklm")
        if args.title:
            cmd.extend(["--title", args.title])

        result = subprocess.run(cmd)
        return result.returncode

    return 0


if __name__ == "__main__":
    sys.exit(main())