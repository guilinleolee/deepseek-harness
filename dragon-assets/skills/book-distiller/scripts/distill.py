#!/usr/bin/env python3
"""
book-distiller V9.12 · 主蒸馏脚本
================================

天龙自研书籍蒸馏器 V9.12 的核心入口。

功能:
- 输入:章节列表 + 原文段落(或 cangjie 蒸馏产物目录)
- 输出:章节摘要 / 概念卡 / 案例库 / 知识图谱
- 4 层自检(在 quality_check.py 中)

约束:
- 不依赖任何 LLM API(可纯规则运行)
- 与 cangjie-skill 互导非依赖(共享数据格式,无代码耦合)

CLI:
    python distill.py --input-dir <DIR> --out-dir <DIR> [--lang zh|en|ja]
"""

from __future__ import annotations
import argparse
import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple


# ============================================================
# 1. 章节摘要(轻量 LLM-free 实现)
# ============================================================

def summarize_chapter(chapter_text: str, max_sentences: int = 5) -> str:
    """对一个章节做极简摘要:取前 max_sentences 句。

    真实场景应调 LLM,这里用纯规则演示。
    """
    # 简单按 。.!?!?;。分句
    sentences = re.split(r'(?<=[。!?;])\s*', chapter_text.strip())
    sentences = [s for s in sentences if len(s) > 5]
    return " ".join(sentences[:max_sentences])


# ============================================================
# 2. 概念卡(基于关键词密度 + 候选词库)
# ============================================================

# 中英日 3 语种概念候选词
CONCEPT_PATTERNS = {
    "zh": [
        r"^[^,。]{2,12}是指", r"^[^,。]{2,12}是(一种|一个|一项)",
        r"^所谓[^,。]{2,12}", r"^[^,。]{2,12}的(定义|概念|含义)是",
    ],
    "en": [
        r"^([A-Z][a-z]+\s+){0,3}is a", r"^([A-Z][a-z]+\s+){0,3}refers to",
        r"^([A-Z][a-z]+\s+){0,3}is defined as",
    ],
    "ja": [
        r"^([^。]{2,12})とは", r"^([^。]{2,12})とは[、,]\s*([^。]+)",
    ],
}


def extract_concepts(text: str, lang: str = "zh") -> List[str]:
    """从文本中抽取候选概念。

    真实场景应调 LLM,这里用正则 + 关键术语列表演示。
    """
    patterns = CONCEPT_PATTERNS.get(lang, CONCEPT_PATTERNS["zh"])
    concepts = []
    for line in text.splitlines():
        line = line.strip()
        if len(line) < 5 or len(line) > 200:
            continue
        for pat in patterns:
            if re.search(pat, line):
                concepts.append(line[:120])
                break

    # fallback:从章节标题 / 关键词提取(中文 2-4 字 + 英文 3+ 字母)
    if len(concepts) < 3:
        keywords = re.findall(r"[一-鿿]{2,6}|[A-Za-z]{4,}", text)
        for kw in keywords:
            if kw not in concepts and len(kw) >= 2:
                concepts.append(kw)
            if len(concepts) >= 10:
                break

    return list(dict.fromkeys(concepts))[:20]  # 去重 + 限 20


# ============================================================
# 3. 案例库(基于段落模式)
# ============================================================

CASE_MARKERS = {
    "zh": ["案例", "故事", "对话", "实例", "比如", "举例", "当时"],
    "en": ["case", "example", "instance", "story", "scenario"],
    "ja": ["事例", "ケース", "実例", "具体例"],
}


def extract_cases(text: str, lang: str = "zh") -> List[str]:
    """从文本中抽取案例段落。"""
    markers = CASE_MARKERS.get(lang, CASE_MARKERS["zh"])
    cases = []
    for para in text.split("\n\n"):
        para = para.strip()
        if len(para) < 30 or len(para) > 1000:
            continue
        if any(m in para for m in markers):
            cases.append(para[:300])
    return cases[:15]


# ============================================================
# 4. 知识图谱(实体关系抽取,简化版)
# ============================================================

def extract_kg(text: str) -> List[Tuple[str, str, str]]:
    """抽取 (head, relation, tail) 三元组(简化版)。

    真实场景应调 LLM,这里用「概念 A 包括 B」「A 影响 B」等模式演示。
    """
    triples = []
    patterns = [
        (r"([^。]{2,12})包括([^。]{2,30})", "包括"),
        (r"([^。]{2,12})影响([^。]{2,30})", "影响"),
        (r"([^。]{2,12})导致([^。]{2,30})", "导致"),
        (r"([^。]{2,12})是([^。]{2,30})的基础", "基础"),
    ]
    for pat, rel in patterns:
        for m in re.finditer(pat, text):
            head = m.group(1).strip()
            tail = m.group(2).strip()
            if head and tail and head != tail:
                triples.append((head, rel, tail))
    return list(dict.fromkeys(triples))[:30]


# ============================================================
# 5. 主入口
# ============================================================

def distill(input_dir: Path, out_dir: Path, lang: str = "zh") -> Dict:
    """运行 V9.12 蒸馏流程。

    优先识别 cangjie 蒸馏产物(有 BOOK_OVERVIEW.md),否则按章节处理。
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {"input_dir": str(input_dir), "lang": lang, "outputs": {}}

    # 检测 cangjie 模式
    is_cangjie = (input_dir / "BOOK_OVERVIEW.md").exists()

    if is_cangjie:
        # 读 BOOK_OVERVIEW.md 作为"原文"
        book_text = (input_dir / "BOOK_OVERVIEW.md").read_text(encoding="utf-8")
        book_title = "cangjie-book"
        # 收集所有 SKILL.md
        skill_files = list(input_dir.glob("*/SKILL.md"))
        summary["cangjie_mode"] = True
        summary["skill_count"] = len(skill_files)
    else:
        # 通用模式:从目录里读所有 .md
        book_text = ""
        for md in sorted(input_dir.glob("*.md")):
            book_text += f"\n\n# {md.stem}\n" + md.read_text(encoding="utf-8", errors="ignore")
        book_title = input_dir.name

    # 1. 章节摘要
    chapters = [c.strip() for c in book_text.split("\n## ") if c.strip()]
    chapter_summaries = []
    for ch in chapters[:20]:  # 限 20 章节
        lines = ch.split("\n")
        title = lines[0][:50]
        body = "\n".join(lines[1:]).strip()
        # 跳过只有标题没有正文的"章节"
        if len(body) < 10:
            continue
        summary_text = summarize_chapter(body, max_sentences=3)
        if summary_text:
            chapter_summaries.append({"title": title, "summary": summary_text})

    # cangjie 模式:复制 BOOK_OVERVIEW.md + DIGEST.md 到 out-dir
    # 让 V9.12 自包含(quality_check.py 直接读 out-dir)
    if is_cangjie:
        for f in ["BOOK_OVERVIEW.md", "DIGEST.md"]:
            src = input_dir / f
            if src.exists():
                (out_dir / f).write_text(src.read_text(encoding="utf-8", errors="ignore"),
                                          encoding="utf-8")
    summary["outputs"]["chapter_summaries"] = len(chapter_summaries)

    # 2. 概念卡
    concepts = extract_concepts(book_text, lang=lang)
    summary["outputs"]["concepts"] = len(concepts)

    # 3. 案例库
    cases = extract_cases(book_text, lang=lang)
    summary["outputs"]["cases"] = len(cases)

    # 4. 知识图谱
    triples = extract_kg(book_text)
    summary["outputs"]["kg_triples"] = len(triples)

    # 落盘
    (out_dir / "chapter_summaries.json").write_text(
        json.dumps(chapter_summaries, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "concepts.json").write_text(
        json.dumps(concepts, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "cases.json").write_text(
        json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "kg.json").write_text(
        json.dumps([{"h": h, "r": r, "t": t} for h, r, t in triples],
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary["book_title"] = book_title
    summary["status"] = "OK"

    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description="book-distiller V9.12")
    ap.add_argument("--input-dir", required=True, help="输入目录")
    ap.add_argument("--out-dir", required=True, help="输出目录")
    ap.add_argument("--lang", default="zh", choices=["zh", "en", "ja"])
    args = ap.parse_args()

    input_dir = Path(args.input_dir).resolve()
    out_dir = Path(args.out_dir).resolve()

    if not input_dir.exists():
        print(f"ERROR: input dir not found: {input_dir}", file=sys.stderr)
        return 3

    summary = distill(input_dir, out_dir, lang=args.lang)
    print(f"[OK] book-distiller V9.12 distill complete")
    print(f"  input:  {summary['input_dir']}")
    print(f"  lang:   {summary['lang']}")
    print(f"  outputs: {json.dumps(summary['outputs'], ensure_ascii=False)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())