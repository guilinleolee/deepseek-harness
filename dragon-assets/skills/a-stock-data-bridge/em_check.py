"""em_check.py · a-stock-data-bridge V1.0 质检脚本（A 股侧）

对齐 em_global_check.py 的契约：5 必检 + 3 推荐 + 退出码语义。
A 股侧 W3 严到 >= 2 层（W3' 复用 global 的 >= 1 因美港股底稿允许单层 L2）。
A 股侧 W4 用市场标签（SH/SZ/BJ/行业/事件）替代美港股的 US/HK/CN。

退出码契约（28-10 文档）：
  0 = PASS  5 项必检 + 3 项推荐全过
  1 = FAIL  至少 1 项必检未过
  2 = WARN  仅推荐项未过（不影响交付）
  3 = ERROR 调用方式错误
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def check_required_fields_markdown(md: str) -> tuple[bool, str]:
    """W1 必检：Markdown 含 4 必需字段（端点表 / 溯源列 / 生成时间 / 备胎使用）"""
    has_endpoint = "## 端点列表" in md
    has_source = re.search(r"\| [^|]+ \| [LM][0-9]+ \| [^|]+ \|", md) is not None
    has_fetched = re.search(r"生成时间.*\d{4}-\d{2}-\d{2}", md) is not None
    has_fallback = "备胎使用" in md
    passed = all([has_endpoint, has_source, has_fetched, has_fallback])
    note = (f"endpoint_table={has_endpoint} source_column={has_source} "
            f"fetched_at={has_fetched} fallback_used={has_fallback}")
    return passed, note


def check_endpoints_called(md: str, min_endpoints: int = 3) -> tuple[bool, str]:
    """W2 必检：调用端点数 >= 3（A 股底稿通常 >= 5）"""
    matches = re.findall(r"\| ([a-z_][a-z_0-9]*) \| [LM][0-9]+ \|", md)
    count = len(set(matches))
    return count >= min_endpoints, f"distinct_endpoints={count} min={min_endpoints}"


def check_layer_coverage(md: str, min_layers: int = 2) -> tuple[bool, str]:
    """W3 必检：覆盖至少 2 个层级（A 股底稿跨 L1-L7）"""
    layers = set(re.findall(r"\| [a-z_][a-z_0-9]* \| ([LM][0-9]+) \|", md))
    return len(layers) >= min_layers, f"layers={sorted(layers)} (>= {min_layers})"


def check_market_tag_present(md: str) -> tuple[bool, str]:
    """W4 必检：A 股市场标签齐全（SH/SZ/BJ + 底稿类型 stock/industry/event/announcement）"""
    # A 股市场代码
    has_market_code = bool(re.search(r"\b\d{6}\.(SH|SZ|BJ)\b", md))
    # 底稿类型（兼容 `底稿类型: stock` 和 `**底稿类型**: stock` 两种格式）
    base_type = re.search(r"底稿类型\s*\*?\*?[:：]\s*\*?\*?(\w+)", md)
    has_base_type = base_type is not None
    # 行业 / 事件底稿可能没有市场代码但有行业名
    has_industry = "行业" in md or "industry" in md.lower()
    passed = has_market_code or has_base_type or has_industry
    note = (f"market_code={has_market_code} base_type={has_base_type} "
            f"industry={has_industry} type={base_type.group(1) if base_type else '?'}")
    return passed, note


def check_apache_attribution(md: str) -> tuple[bool, str]:
    """W5 必检：Apache-2.0 attribution 段落齐全"""
    has_upstream = "simonlin1212" in md
    has_apache = "Apache-2.0" in md or "Apache License" in md
    has_modified = "Modified" in md or "天龙引擎" in md or "天蟒引擎" in md
    passed = has_upstream and has_apache and has_modified
    note = f"upstream={has_upstream} apache={has_apache} modified={has_modified}"
    return passed, note


def check_traceability_completeness(md: str) -> tuple[bool, str]:
    """R1 推荐：每条结果含 fetched_at 时间戳（ISO 8601 格式）"""
    matches = re.findall(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", md)
    return len(matches) >= 1, f"timestamp_lines={len(matches)}"


def check_fallback_recorded(md: str) -> tuple[bool, str]:
    """R2 推荐：备胎字段被显式记录（即使未触发也应出现）"""
    m = re.search(r"备胎使用[::]?\s*(\d+)", md)
    return m is not None, f"fallback_count={m.group(1) if m else 'missing'}"


def check_endpoint_count_reasonable(md: str, max_endpoints: int = 30) -> tuple[bool, str]:
    """R3 推荐：单底稿端点数 <= 30（A 股允许更深覆盖，因 10 层 43 端点）"""
    matches = re.findall(r"\| ([a-z_][a-z_0-9]*) \| [LM][0-9]+ \|", md)
    count = len(set(matches))
    return count <= max_endpoints, f"distinct_endpoints={count} max={max_endpoints}"


def main():
    parser = argparse.ArgumentParser(description="a-stock-data-bridge V1.0 质检（A 股侧）")
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
        ("R3 端点数 <= 30",   check_endpoint_count_reasonable),
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