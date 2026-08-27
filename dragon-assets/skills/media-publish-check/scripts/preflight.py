#!/usr/bin/env python3
"""Locate review candidates without assigning final compliance risk."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RULES = SKILL_ROOT / "references" / "term-patterns.json"
PRIORITY_ORDER = {"urgent": 4, "high": 3, "normal": 2, "low": 1}
PLATFORMS = ("all", "douyin", "xiaohongshu", "weixin-video-accounts", "kuaishou")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find review candidates in Chinese social content.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", type=Path, help="UTF-8 text file to scan")
    source.add_argument("--text", help="Text to scan directly")
    parser.add_argument("--platform", choices=PLATFORMS, default="all")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--context", type=int, default=28, help="Characters around a hit")
    return parser.parse_args()


def load_text(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    try:
        return args.file.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit(f"Input must be UTF-8 text: {exc}") from exc
    except OSError as exc:
        raise SystemExit(f"Cannot read input: {exc}") from exc


def load_rules(path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot load rules from {path}: {exc}") from exc
    if not isinstance(data, list):
        raise SystemExit("Rules file must contain a JSON array")
    required = {"id", "category", "priority", "platforms", "pattern", "review", "action"}
    for index, rule in enumerate(data):
        missing = required - set(rule)
        if missing:
            raise SystemExit(f"Rule {index} is missing fields: {sorted(missing)}")
        if rule["priority"] not in PRIORITY_ORDER:
            raise SystemExit(f"Rule {rule['id']} has invalid priority")
        if not set(rule["platforms"]).issubset(PLATFORMS):
            raise SystemExit(f"Rule {rule['id']} has invalid platform scope")
        try:
            re.compile(rule["pattern"], re.IGNORECASE)
        except re.error as exc:
            raise SystemExit(f"Rule {rule['id']} has invalid regex: {exc}") from exc
    return data


def rule_applies(scopes: list[str], platform: str) -> bool:
    if platform == "all":
        return "all" in scopes
    return "all" in scopes or platform in scopes


def line_and_column(text: str, position: int) -> tuple[int, int]:
    line = text.count("\n", 0, position) + 1
    previous_newline = text.rfind("\n", 0, position)
    column = position + 1 if previous_newline < 0 else position - previous_newline
    return line, column


def compact_context(text: str, start: int, end: int, radius: int) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    snippet = re.sub(r"\s+", " ", text[left:right]).strip()
    return ("…" if left else "") + snippet + ("…" if right < len(text) else "")


def deduplicate(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop lower-priority hits fully contained by a stronger hit."""
    ranked = sorted(
        hits,
        key=lambda item: (-PRIORITY_ORDER[item["priority"]], item["start"], -(item["end"] - item["start"])),
    )
    kept: list[dict[str, Any]] = []
    for hit in ranked:
        covered = any(
            other["start"] <= hit["start"]
            and other["end"] >= hit["end"]
            and PRIORITY_ORDER[other["priority"]] > PRIORITY_ORDER[hit["priority"]]
            for other in kept
        )
        if not covered:
            kept.append(hit)
    return sorted(
        kept,
        key=lambda item: (-PRIORITY_ORDER[item["priority"]], item["line"], item["column"], item["rule_id"]),
    )


def scan(text: str, rules: list[dict[str, Any]], platform: str, context: int) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for rule in rules:
        if not rule_applies(rule["platforms"], platform):
            continue
        for match in re.finditer(rule["pattern"], text, re.IGNORECASE):
            line, column = line_and_column(text, match.start())
            hits.append(
                {
                    "rule_id": rule["id"],
                    "category": rule["category"],
                    "priority": rule["priority"],
                    "match": match.group(0),
                    "start": match.start(),
                    "end": match.end(),
                    "line": line,
                    "column": column,
                    "context": compact_context(text, match.start(), match.end(), context),
                    "review": rule["review"],
                    "action": rule["action"],
                }
            )
    return deduplicate(hits)


def result_payload(text: str, platform: str, hits: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(hit["priority"] for hit in hits)
    return {
        "tool": "media-publish-check/preflight",
        "platform": platform,
        "characters_scanned": len(text),
        "candidate_count": len(hits),
        "counts_by_priority": {
            priority: counts.get(priority, 0)
            for priority in sorted(PRIORITY_ORDER, key=PRIORITY_ORDER.get, reverse=True)
        },
        "disclaimer": (
            "Candidate priorities are triage order, not R0-R4 risk or a publishing verdict. "
            "Review context, sources, rights, qualifications, visuals, audio, labels, and current rules."
        ),
        "hits": hits,
    }


def md_escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(payload: dict[str, Any]) -> str:
    counts = payload["counts_by_priority"]
    lines = [
        "# 文本预检复核候选",
        "",
        f"- 平台：`{payload['platform']}`",
        f"- 扫描字符：{payload['characters_scanned']}",
        f"- 候选命中：{payload['candidate_count']}",
        "- 复核优先级：" + "，".join(f"{key}={value}" for key, value in counts.items()),
        "- 说明：优先级只用于排序，不是 R0-R4 风险结论；词语命中不等于违规。",
        "",
    ]
    if not payload["hits"]:
        lines.append("未发现词表候选命中；这不代表内容已通过完整审核。")
        return "\n".join(lines)
    lines.extend([
        "| 优先级 | 类别 | 命中 | 位置 | 上下文 | 人工复核 | 建议动作 |",
        "|---|---|---|---|---|---|---|",
    ])
    for hit in payload["hits"]:
        values = {key: md_escape(value) for key, value in hit.items()}
        lines.append(
            "| {priority} | {category} | `{match}` | L{line}:C{column} | {context} | {review} | {action} |".format(**values)
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    text_value = load_text(args)
    rules = load_rules(args.rules)
    payload = result_payload(text_value, args.platform, scan(text_value, rules, args.platform, max(0, args.context)))
    if args.format == "json":
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_markdown(payload) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
