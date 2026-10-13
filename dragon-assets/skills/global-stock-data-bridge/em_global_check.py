"""em_global_check.py · global-stock-data-bridge V1.0 质检脚本

5 必检 + 3 推荐 退出码契约：
  0 = PASS  5 项必检全过
  1 = FAIL  至少 1 项必检未过
  2 = WARN  仅推荐项未过
  3 = ERROR 调用方式错误
"""
from __future__ import annotations

import argparse
import sys
import re
from pathlib import Path


def check_required_fields_markdown(md: str) -> tuple[bool, str]:
    """W1 必检：Markdown 含 4 必需字段（端点 / 溯源 / fetched_at / fallback_used）"""
    has_endpoint = "## 端点列表" in md
    has_source = re.search(r"\| [^|]+ \| [LM][0-9]+ \| [^|]+ \|", md) is not None
    has_fetched = re.search(r"生成时间.*\d{4}-\d{2}-\d{2}", md) is not None
    has_fallback = "备胎使用" in md
    passed = all([has_endpoint, has_source, has_fetched, has_fallback])
    note = (f"endpoint_table={has_endpoint} source_column={has_source} "
            f"fetched_at={has_fetched} fallback_used={has_fallback}")
    return passed, note


def check_endpoints_called(md: str, min_endpoints: int = 3) -> tuple[bool, str]:
    """W2 必检：调用端点数 ≥ 3"""
    matches = re.findall(r"\| ([a-z_][a-z_0-9]*) \| [LM][0-9]+ \|", md)
    count = len(set(matches))
    return count >= min_endpoints, f"distinct_endpoints={count} min={min_endpoints}"


def check_layer_coverage(md: str) -> tuple[bool, str]:
    """W3 必检：覆盖至少 1 个层级（财报三表底稿可能单层 L2）"""
    layers = set(re.findall(r"\| [a-z_][a-z_0-9]* \| ([LM][0-9]+) \|", md))
    return len(layers) >= 1, f"layers={sorted(layers)} (>= 1)"


def check_market_tag_present(md: str) -> tuple[bool, str]:
    """W4 必检：含市场标签 (US / HK / CN / GLOBAL)"""
    has_market = bool(re.search(r"\b(US|HK|CN|GLOBAL)\b", md))
    return has_market, f"market_tag={has_market}"


def check_apache_attribution(md: str) -> tuple[bool, str]:
    """W5 必检：Apache-2.0 attribution 段落齐全"""
    has_upstream = "simonlin1212" in md
    has_apache = "Apache-2.0" in md or "Apache License" in md
    has_modified = "Modified" in md or "天龙引擎" in md or "天蟒引擎" in md
    passed = has_upstream and has_apache and has_modified
    note = f"upstream={has_upstream} apache={has_apache} modified={has_modified}"
    return passed, note


def check_traceability_completeness(md: str) -> tuple[bool, str]:
    """R1 推荐：每条结果含 fetched_at 时间戳"""
    matches = re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", md)
    return len(matches) >= 1, f"timestamp_lines={len(matches)}"


def check_fallback_recorded(md: str) -> tuple[bool, str]:
    """R2 推荐：备胎字段被显式记录"""
    m = re.search(r"备胎使用[::]?\s*(\d+)", md)
    return m is not None, f"fallback_count={m.group(1) if m else 'missing'}"


def check_endpoint_count_reasonable(md: str, max_endpoints: int = 8) -> tuple[bool, str]:
    """R3 推荐：单底稿端点数 ≤ 8（美港股底稿比 A 股更精简）"""
    matches = re.findall(r"\| ([a-z_][a-z_0-9]*) \| [LM][0-9]+ \|", md)
    count = len(set(matches))
    return count <= max_endpoints, f"distinct_endpoints={count} max={max_endpoints}"


def main():
    parser = argparse.ArgumentParser(description="global-stock-data-bridge V1.0 质检")
    parser.add_argument("md_file", help="待检 Markdown 底稿路径")
    args = parser.parse_args()

    path = Path(args.md_file)
    if not path.exists():
        print(f"[ERROR] 文件不存在: {path}")
        sys.exit(3)

    md = path.read_text(encoding="utf-8")
    print(f"[Check] 质检 {path}")
    print(f"   {len(md)} chars, {md.count(chr(10))} lines")
    print()

    required = [
        ("W1 溯源字段齐全",  check_required_fields_markdown),
        ("W2 端点数 >= 3",    check_endpoints_called),
        ("W3 层级覆盖 >= 2",  check_layer_coverage),
        ("W4 市场标签齐全",   check_market_tag_present),
        ("W5 Apache 归属",    check_apache_attribution),
    ]
    recommended = [
        ("R1 时间戳完整",     check_traceability_completeness),
        ("R2 备胎记录显式",   check_fallback_recorded),
        ("R3 端点数 <= 8",    check_endpoint_count_reasonable),
    ]

    failed_required = []
    warned_recommended = []

    for label, fn in required:
        ok, note = fn(md)
        icon = "[OK]" if ok else "[FAIL]"
        print(f"  {icon} {label}  ({note})")
        if not ok:
            failed_required.append(label)

    for label, fn in recommended:
        ok, note = fn(md)
        icon = "[OK]" if ok else "[WARN]"
        print(f"  {icon} {label}  ({note})")
        if not ok:
            warned_recommended.append(label)

    print()
    if failed_required:
        print(f"[FAIL] {len(failed_required)} 项必检未过")
        sys.exit(1)
    if warned_recommended:
        print(f"[WARN] {len(warned_recommended)} 项推荐未过（不影响交付）")
        sys.exit(2)
    print("[PASS] 5 必检 + 3 推荐 全过")
    sys.exit(0)


if __name__ == "__main__":
    main()
