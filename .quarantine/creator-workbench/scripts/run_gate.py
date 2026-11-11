#!/usr/bin/env python3
"""Run one quality gate over a draft.

Usage:
    python scripts/run_gate.py <gate> --draft <path> [--research <path>] \
        [--platform <p>] [--style <s>] [--style-dna <path>] [--output <path>]

Gates:
    grammar     mechanical typo / punctuation / repetition check (deterministic)
    structure   mechanical title / paragraph / word-count check (deterministic)
    compliance  mechanical banned-word scan (deterministic)
    factual     placeholder — model-driven, this script just extracts claims
    tone        placeholder — model-driven, this script just summarizes style

Deterministic gates exit 0 with the gate result JSON on stdout (and to
`--output` when given). Model-driven gates exit 2 with a partial result JSON
on stdout so the calling agent can decide. Per the gate SOPs, the agent owns
the final verdict; this script only surfaces the data.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


# Default banned-words — extend via prompts/style/banned-words.json when needed.
DEFAULT_BANNED_WORDS = [
    "震惊", "必看", "99%", "你一定要", "史上最", "惊呆了",
    "刷屏", "炸裂", "逆天", "改写命运",
    "稳赚不赔", "保本", "根治", "100% 有效",
]


def _load_banned_words(extra_path: Path | None) -> list[str]:
    words = list(DEFAULT_BANNED_WORDS)
    if extra_path and extra_path.exists():
        try:
            data = json.loads(extra_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                words.extend(str(w) for w in data)
        except json.JSONDecodeError:
            pass
    return words


def gate_grammar(draft: str) -> dict:
    issues: list[dict] = []
    lines = draft.splitlines()

    for idx, line in enumerate(lines, start=1):
        # very crude repetition: 3+ identical consecutive non-empty lines
        if idx >= 3 and line.strip() and lines[idx - 2].strip() == line.strip() == lines[idx - 3].strip():
            issues.append({
                "line": idx,
                "type": "repetition",
                "text": line.strip()[:60],
                "fix": "合并重复段落",
            })

        # very crude typo / punctuation mix: ASCII comma in CJK run
        if re.search(r"[\u4e00-\u9fff],", line):
            issues.append({
                "line": idx,
                "type": "punctuation",
                "text": line[:60],
                "fix": "中文逗号应为 ，",
            })
        if re.search(r"[\u4e00-\u9fff]\.", line):
            issues.append({
                "line": idx,
                "type": "punctuation",
                "text": line[:60],
                "fix": "中文句号应为 。",
            })

    return {
        "gate": "grammar",
        "passed": len(issues) == 0,
        "issues": issues,
        "iterations": 1,
        "checker": "scripts/run_gate.py grammar",
        "checked_at": _now_iso(),
    }


def gate_structure(draft: str, platform: str) -> dict:
    title_match = re.search(r"^#\s+(.+)$", draft, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else ""
    h2_count = len(re.findall(r"^##\s+", draft, re.MULTILINE))
    image_placeholders = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", draft)) + draft.count("<插入点")
    word_count = len(re.findall(r"[\u4e00-\u9fff]", draft))

    ranges = {
        "wechat":        {"title_min": 14, "title_max": 22, "h2_min": 3, "img_min": 2,  "words_min": 1500, "words_max": 3000},
        "xiaohongshu":   {"title_min": 0,  "title_max": 21, "h2_min": 0, "img_min": 6,  "words_min": 300,  "words_max": 800},
        "douyin":        {"title_min": 15, "title_max": 25, "h2_min": 4, "img_min": 5,  "words_min": 180,  "words_max": 280},
        "toutiao":       {"title_min": 0,  "title_max": 20, "h2_min": 0, "img_min": 0,  "words_min": 200,  "words_max": 500},
        "zhihu":         {"title_min": 0,  "title_max": 30, "h2_min": 3, "img_min": 0,  "words_min": 500,  "words_max": 4000},
        "bilibili":      {"title_min": 20, "title_max": 30, "h2_min": 4, "img_min": 0,  "words_min": 1500, "words_max": 4500},
    }
    spec = ranges.get(platform, ranges["wechat"])
    issues: list[dict] = []

    title_len = len(title)
    if not (spec["title_min"] <= title_len <= spec["title_max"]):
        issues.append({
            "line": 1,
            "type": "title_length",
            "text": title,
            "fix": f"标题应在 {spec['title_min']}-{spec['title_max']} 字之间",
        })
    if h2_count < spec["h2_min"]:
        issues.append({
            "line": 0,
            "type": "h2_count",
            "text": f"h2_count={h2_count}",
            "fix": f"应至少有 {spec['h2_min']} 个 H2 章节",
        })
    if image_placeholders < spec["img_min"]:
        issues.append({
            "line": 0,
            "type": "image_placeholders",
            "text": f"images={image_placeholders}",
            "fix": f"应至少有 {spec['img_min']} 个图片位",
        })
    if not (spec["words_min"] <= word_count <= spec["words_max"]):
        issues.append({
            "line": 0,
            "type": "word_count",
            "text": f"words={word_count}",
            "fix": f"字数应在 {spec['words_min']}-{spec['words_max']} 之间",
        })

    return {
        "gate": "structure",
        "passed": len(issues) == 0,
        "issues": issues,
        "metrics": {
            "title_chars": title_len,
            "h2_count": h2_count,
            "image_placeholders": image_placeholders,
            "word_count": word_count,
        },
        "iterations": 1,
        "checker": "scripts/run_gate.py structure",
        "checked_at": _now_iso(),
    }


def gate_compliance(draft: str, banned_words: list[str]) -> dict:
    issues: list[dict] = []
    lines = draft.splitlines()
    for idx, line in enumerate(lines, start=1):
        for word in banned_words:
            if word in line:
                issues.append({
                    "line": idx,
                    "phrase": word,
                    "category": "banned_word",
                    "fix": f"删除或改写\"{word}\"",
                })
    return {
        "gate": "compliance",
        "passed": len(issues) == 0,
        "issues": issues,
        "iterations": 1,
        "checker": "scripts/run_gate.py compliance",
        "checked_at": _now_iso(),
    }


def gate_factual_placeholder(draft: str, research_path: Path | None) -> dict:
    """Model-driven gate. This script just extracts candidate claims and
    leaves the final verdict to the agent. Per `sop/gate-factual.md`, the
    agent checks each claim against `research.json`.
    """
    claims: list[dict] = []
    for idx, line in enumerate(draft.splitlines(), start=1):
        # crude extractor: numeric + percentage / amount / date / tool name patterns
        for match in re.finditer(
            r"\d+(?:\.\d+)?\s*(?:%|元|块|w|W|万|倍|岁|年|月|日)|"
            r"\d{4}\s*年|\d{1,2}\s*月\d{1,2}\s*日",
            line,
        ):
            claims.append({
                "line": idx,
                "claim": match.group(0),
                "context": line.strip()[:120],
            })
    return {
        "gate": "factual",
        "passed": None,  # agent must decide
        "issues": [],
        "candidate_claims": claims[:50],
        "iterations": 1,
        "checker": "scripts/run_gate.py factual (placeholder)",
        "checked_at": _now_iso(),
        "research_path": str(research_path) if research_path else None,
    }


def gate_tone_placeholder(draft: str, style: str, style_dna_path: Path | None) -> dict:
    """Model-driven gate. The script emits a summary the agent uses to decide.
    """
    style_dna = _read_text(style_dna_path) if style_dna_path else ""
    return {
        "gate": "tone",
        "passed": None,  # agent must decide
        "issues": [],
        "style_requested": style,
        "style_dna_loaded_chars": len(style_dna),
        "draft_chars": len(draft),
        "iterations": 1,
        "checker": "scripts/run_gate.py tone (placeholder)",
        "checked_at": _now_iso(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("gate", choices=["grammar", "structure", "compliance", "factual", "tone"])
    parser.add_argument("--draft", required=True, type=Path)
    parser.add_argument("--platform", default="wechat")
    parser.add_argument("--style", default="professional")
    parser.add_argument("--style-dna", type=Path, default=Path("prompts/style/style-dna.md"))
    parser.add_argument("--research", type=Path)
    parser.add_argument("--banned-words", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    draft = _read_text(args.draft)
    if not draft:
        print(json.dumps({
            "gate": args.gate,
            "passed": False,
            "issues": [{"line": 0, "type": "missing_draft", "text": str(args.draft)}],
            "checked_at": _now_iso(),
        }, ensure_ascii=False))
        return 1

    if args.gate == "grammar":
        result = gate_grammar(draft)
        rc = 0 if result["passed"] else 1
    elif args.gate == "structure":
        result = gate_structure(draft, args.platform)
        rc = 0 if result["passed"] else 1
    elif args.gate == "compliance":
        banned = _load_banned_words(args.banned_words)
        result = gate_compliance(draft, banned)
        rc = 0 if result["passed"] else 1
    elif args.gate == "factual":
        result = gate_factual_placeholder(draft, args.research)
        rc = 2  # placeholder; agent decides
    elif args.gate == "tone":
        result = gate_tone_placeholder(draft, args.style, args.style_dna)
        rc = 2  # placeholder; agent decides
    else:  # pragma: no cover
        raise SystemExit(f"unknown gate: {args.gate}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(json.dumps(result, ensure_ascii=False))
    return rc


if __name__ == "__main__":
    sys.exit(main())