#!/usr/bin/env python3
"""Validate a market daily review Markdown report."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    ("title", r"^#\s+.*(复盘|收盘)", "一级标题需要标明复盘或收盘报告"),
    ("summary", r"^##\s*(?:\d+[.、]\s*)?摘要", "缺少摘要"),
    ("index", r"^##\s*(?:\d+[.、]\s*)?指数", "缺少指数概览章节"),
    ("breadth", r"^##\s*(?:\d+[.、]\s*)?市场宽度", "缺少市场宽度与情绪章节"),
    ("themes", r"^##\s*(?:\d+[.、]\s*)?(行业|概念)", "缺少行业与概念热点章节"),
    ("lhb", r"^##\s*(?:\d+[.、]\s*)?(龙虎榜|大宗)", "缺少龙虎榜与大宗交易章节"),
    ("margin", r"^##\s*(?:\d+[.、]\s*)?(两融|融资融券|北向)", "缺少两融与北向章节"),
    ("risk", r"^##\s*(?:\d+[.、]\s*)?(异动|风险)", "缺少异动与风险提示章节"),
    ("data_notes", r"^##\s*(?:\d+[.、]\s*)?数据说明", "缺少数据说明章节"),
]


def validate(text: str) -> list[str]:
    """校验报告完整性"""
    issues: list[str] = []

    if len(text.strip()) < 500:
        issues.append("报告内容过短，可能不是完整复盘")

    for _key, pattern, message in REQUIRED_SECTIONS:
        if not re.search(pattern, text, flags=re.MULTILINE):
            issues.append(message)

    if not re.search(r"(数据来源|来源接口|使用接口|Pandadata)", text):
        issues.append("缺少数据来源或来源接口说明")

    if not re.search(r"(数据日|数据截止|生成时间|截止时间)", text):
        issues.append("缺少数据日或数据截止时间说明")

    if re.search(r"(两融|融资融券|北向)", text) and not re.search(r"(T\+1|数据日)", text):
        issues.append("两融或北向数据需要标注 T+1 或实际数据日")

    if not re.search(r"(不构成投资建议|不提供操作建议|仅作.*事实)", text):
        issues.append("缺少非投资建议/事实归纳声明")

    return issues


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="Path to the Markdown report")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="启用严格模式，检查更多细节"
    )
    args = parser.parse_args()

    try:
        text = args.report.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        print(f"ERROR: report not found: {args.report}", file=sys.stderr)
        return 2

    issues = validate(text)

    # 严格模式额外检查
    if args.strict:
        # 检查表格是否有数据
        if re.search(r"\|\s*-\s*\|", text):
            # 有分隔线，检查是否有实际数据行
            table_rows = re.findall(r"\|[^|]+\|", text)
            if len(table_rows) < 5:  # 标题 + 分隔线 + 至少3行数据
                issues.append("表格数据不足，可能存在空表格")

        # 检查是否有日期格式
        if not re.search(r"\d{4}-\d{2}-\d{2}", text):
            issues.append("缺少标准格式日期 (YYYY-MM-DD)")

    if issues:
        print("FAIL")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
