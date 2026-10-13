#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电子书搜索脚本 - 双引擎搜索 (Z-Library + Library Genesis)
支持：书名搜索、作者搜索、格式过滤、语言过滤
"""

import argparse
import json
import sys
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Windows编码问题修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 尝试导入搜索库
try:
    from libgen_api import LibgenSearch
    LIBGEN_AVAILABLE = True
except ImportError:
    LIBGEN_AVAILABLE = False
    print("[WARN] libgen-api 未安装，Libgen搜索不可用", file=sys.stderr)

try:
    import zlibrary
    ZLIBRARY_AVAILABLE = True
except ImportError:
    ZLIBRARY_AVAILABLE = False
    print("[WARN] zlibrary 未安装，Z-Library搜索不可用", file=sys.stderr)


@dataclass
class BookResult:
    """统一的搜索结果格式"""
    title: str
    author: str
    format: str
    size: str
    year: Optional[str] = None
    language: Optional[str] = None
    source: str = "unknown"
    download_url: Optional[str] = None
    id: Optional[str] = None
    rating: Optional[float] = None
    downloads: Optional[int] = None

    def to_dict(self) -> Dict:
        return asdict(self)


class LibgenSearcher:
    """Library Genesis 搜索器"""

    # 多个镜像站点
    MIRRORS = [
        "https://libgen.is",
        "https://libgen.st",
        "https://libgen.rs",
        "https://libgen.li",
        "https://libgen.bz",
    ]

    def __init__(self):
        self.searcher = None
        if LIBGEN_AVAILABLE:
            self.searcher = LibgenSearch()

    def search(self, query: str, search_type: str = "title",
               filters: Optional[Dict] = None) -> List[BookResult]:
        """搜索书籍"""
        if not LIBGEN_AVAILABLE or not self.searcher:
            return []

        results = []
        last_error = None

        # 尝试多个镜像
        for mirror in self.MIRRORS:
            try:
                if search_type == "author":
                    raw_results = self.searcher.search_author(query)
                else:
                    if filters:
                        raw_results = self.searcher.search_title_filtered(
                            query, filters, exact_match=False
                        )
                    else:
                        raw_results = self.searcher.search_title(query)

                for book in raw_results[:20]:  # 限制结果数量
                    try:
                        results.append(BookResult(
                            title=book.get('Title', 'Unknown'),
                            author=book.get('Author', 'Unknown'),
                            format=book.get('Extension', 'Unknown').upper(),
                            size=book.get('Size', 'Unknown'),
                            year=book.get('Year'),
                            language=book.get('Language'),
                            source="Libgen",
                            download_url=book.get('Mirror_1') or book.get('Mirror_2'),
                            id=book.get('ID')
                        ))
                    except Exception as e:
                        continue

                if results:
                    return results

            except Exception as e:
                last_error = e
                continue

        if last_error and not results:
            print(f"[ERROR] Libgen所有镜像均不可用: {last_error}", file=sys.stderr)
            print("[TIP] 可能需要代理或VPN访问", file=sys.stderr)

        return results


class ZlibrarySearcher:
    """Z-Library 搜索器"""

    def __init__(self):
        self.lib = None

    async def init(self, email: str = None, password: str = None):
        """初始化并登录"""
        if not ZLIBRARY_AVAILABLE:
            return False

        try:
            self.lib = zlibrary.AsyncZlib()
            if email and password:
                await self.lib.login(email, password)
            return True
        except Exception as e:
            print(f"Z-Library初始化错误: {e}", file=sys.stderr)
            return False

    async def search(self, query: str, filters: Optional[Dict] = None) -> List[BookResult]:
        """搜索书籍"""
        if not self.lib:
            return []

        results = []
        try:
            # 构建搜索参数
            search_params = {"q": query, "count": 20}

            if filters:
                if "year_from" in filters:
                    search_params["from_year"] = filters["year_from"]
                if "year_to" in filters:
                    search_params["to_year"] = filters["year_to"]
                if "language" in filters:
                    from zlibrary import Language
                    lang_map = {
                        "english": Language.ENGLISH,
                        "chinese": Language.CHINESE,
                        "russian": Language.RUSSIAN,
                        "german": Language.GERMAN,
                        "french": Language.FRENCH,
                    }
                    if filters["language"].lower() in lang_map:
                        search_params["lang"] = [lang_map[filters["language"].lower()]]
                if "format" in filters:
                    from zlibrary import Extension
                    ext_map = {
                        "pdf": Extension.PDF,
                        "epub": Extension.EPUB,
                        "mobi": Extension.MOBI,
                    }
                    if filters["format"].lower() in ext_map:
                        search_params["extensions"] = [ext_map[filters["format"].lower()]]

            paginator = await self.lib.search(**search_params)
            books = await paginator.next()

            for book in books:
                try:
                    results.append(BookResult(
                        title=book.name,
                        author=book.authors[0] if book.authors else "Unknown",
                        format=book.extension.upper() if hasattr(book, 'extension') else "Unknown",
                        size=f"{book.size} {book.size_unit}" if hasattr(book, 'size') else "Unknown",
                        year=str(book.year) if hasattr(book, 'year') and book.year else None,
                        language=book.language if hasattr(book, 'language') else None,
                        source="Z-Library",
                        download_url=book.url if hasattr(book, 'url') else None,
                        id=str(book.id) if hasattr(book, 'id') else None,
                        rating=book.rating if hasattr(book, 'rating') else None,
                        downloads=book.downloads if hasattr(book, 'downloads') else None
                    ))
                except Exception:
                    continue
        except Exception as e:
            error_msg = str(e)
            if "log in" in error_msg.lower() or "login" in error_msg.lower():
                print("[ERROR] Z-Library需要先登录", file=sys.stderr)
                print("[TIP] 请运行: python zlibrary-to-notebooklm/scripts/login.py", file=sys.stderr)
            else:
                print(f"[ERROR] Z-Library搜索错误: {e}", file=sys.stderr)

        return results


def format_results_table(results: List[BookResult]) -> str:
    """格式化结果为表格"""
    if not results:
        return "未找到相关书籍"

    lines = []
    lines.append("\n📚 搜索结果：")
    lines.append("-" * 100)
    lines.append(f"{'#':<3} {'书名':<40} {'作者':<20} {'格式':<6} {'大小':<10} {'来源':<15}")
    lines.append("-" * 100)

    for i, book in enumerate(results, 1):
        title = book.title[:38] + "..." if len(book.title) > 40 else book.title
        author = book.author[:18] + "..." if len(book.author) > 20 else book.author
        lines.append(f"{i:<3} {title:<40} {author:<20} {book.format:<6} {book.size:<10} {book.source:<15}")

    lines.append("-" * 100)
    lines.append(f"\n共找到 {len(results)} 个结果")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="电子书搜索工具 - 支持Z-Library和Libgen双引擎"
    )
    parser.add_argument("query", help="搜索关键词（书名或作者）")
    parser.add_argument("--engine", "-e", choices=["zlibrary", "libgen", "both"],
                       default="both", help="搜索引擎 (默认: both)")
    parser.add_argument("--type", "-t", choices=["title", "author"],
                       default="title", help="搜索类型 (默认: title)")
    parser.add_argument("--format", "-f", help="格式过滤 (pdf, epub, mobi)")
    parser.add_argument("--language", "-l", help="语言过滤 (english, chinese, etc.)")
    parser.add_argument("--year-from", type=int, help="起始年份")
    parser.add_argument("--year-to", type=int, help="结束年份")
    parser.add_argument("--json", "-j", action="store_true", help="JSON格式输出")
    parser.add_argument("--limit", "-n", type=int, default=20, help="结果数量限制")

    args = parser.parse_args()

    # 构建过滤条件
    filters = {}
    if args.format:
        filters["format"] = args.format
    if args.language:
        filters["language"] = args.language
    if args.year_from:
        filters["year_from"] = args.year_from
    if args.year_to:
        filters["year_to"] = args.year_to

    all_results = []

    # Libgen 搜索
    if args.engine in ["libgen", "both"]:
        print("🔍 正在搜索 Library Genesis...", file=sys.stderr)
        libgen = LibgenSearcher()
        libgen_results = libgen.search(args.query, args.type, filters)
        all_results.extend(libgen_results)
        print(f"  ✅ Libgen: 找到 {len(libgen_results)} 个结果", file=sys.stderr)

    # Z-Library 搜索
    if args.engine in ["zlibrary", "both"]:
        print("🔍 正在搜索 Z-Library...", file=sys.stderr)
        async def search_zlib():
            zlib = ZlibrarySearcher()
            if await zlib.init():
                return await zlib.search(args.query, filters)
            return []
        zlib_results = asyncio.run(search_zlib())
        all_results.extend(zlib_results)
        print(f"  ✅ Z-Library: 找到 {len(zlib_results)} 个结果", file=sys.stderr)

    # 限制结果数量
    all_results = all_results[:args.limit]

    # 输出结果
    if args.json:
        print(json.dumps([r.to_dict() for r in all_results], ensure_ascii=False, indent=2))
    else:
        print(format_results_table(all_results))

    return 0 if all_results else 1


if __name__ == "__main__":
    sys.exit(main())