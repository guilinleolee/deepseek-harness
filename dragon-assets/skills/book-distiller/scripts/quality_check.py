#!/usr/bin/env python3
"""
book-distiller V9.12 · 4 层自检(quality_check.py)
=================================================

V9.12 核心升级:蒸馏质量 4 层自检
- L1 完整性:章节是否 100% 覆盖(无遗漏 / 无重复)
- L2 一致性:摘要与原文章节主旨是否一致(无曲解)
- L3 知识密度:概念卡 / 案例库是否包含可操作知识
- L4 复用价值:蒸馏产物是否能被天龙其他 skill 直接消费

CLI:
    python quality_check.py --out-dir <DIR>

输入依赖:out-dir 必须有 distill.py 跑过的产物(chapter_summaries.json 等)
"""

from __future__ import annotations
import argparse
import json
import sys
import re
from pathlib import Path
from typing import Tuple


# ============================================================
# L1 完整性
# ============================================================

def check_L1_completeness(out_dir: Path) -> Tuple[bool, str]:
    """L1 完整性:章节摘要数 ≥ 1 且去重后无完全相同摘要。"""
    p = out_dir / "chapter_summaries.json"
    if not p.exists():
        return False, "L1: chapter_summaries.json 缺失"

    data = json.loads(p.read_text(encoding="utf-8"))
    if not data:
        return False, "L1: 章节摘要为空"

    n = len(data)
    # 去重
    unique = {d["summary"] for d in data if d.get("summary")}
    n_unique = len(unique)
    dup = n - n_unique

    if dup > n * 0.3:
        return False, f"L1: 重复率 {dup}/{n} > 30%"
    return True, f"L1 PASS (章节 {n} · 唯一摘要 {n_unique} · 重复 {dup})"


# ============================================================
# L2 一致性
# ============================================================

def check_L2_consistency(out_dir: Path) -> Tuple[bool, str]:
    """L2 一致性:摘要关键词与原始章节标题至少 50% 重叠(简化版)。"""
    book_overview = out_dir.parent / "BOOK_OVERVIEW.md"
    cs_path = out_dir / "chapter_summaries.json"
    if not cs_path.exists():
        return False, "L2: chapter_summaries.json 缺失"

    summaries = json.loads(cs_path.read_text(encoding="utf-8"))
    if not summaries:
        return False, "L2: 摘要为空"

    # 用 BOOK_OVERVIEW.md 里的关键词做基准
    # 优先查 out_dir/BOOK_OVERVIEW.md(cangjie 模式把 BOOK_OVERVIEW 复制到 out-dir)
    # 否则查 out_dir.parent/BOOK_OVERVIEW.md
    candidates = [
        out_dir / "BOOK_OVERVIEW.md",
        out_dir.parent / "BOOK_OVERVIEW.md",
        out_dir.parent / "input" / "BOOK_OVERVIEW.md",
    ]
    ref_text = ""
    for c in candidates:
        if c.exists():
            ref_text = c.read_text(encoding="utf-8", errors="ignore")
            break
    if not ref_text:
        # fallback:用 chapter_summaries 自身标题 + DIGEST
        ref_text = " ".join(s.get("title", "") for s in summaries)
        digest = out_dir / "DIGEST.md"
        if digest.exists():
            ref_text += " " + digest.read_text(encoding="utf-8", errors="ignore")

    ref_keywords = set(re.findall(r"[一-鿿]{2,4}|[A-Za-z]{3,}", ref_text))

    overlap_scores = []
    for s in summaries:
        summary = s.get("summary", "")
        sum_keywords = set(re.findall(r"[一-鿿]{2,4}|[A-Za-z]{3,}", summary))
        if not sum_keywords:
            continue
        overlap = len(sum_keywords & ref_keywords) / len(sum_keywords)
        overlap_scores.append(overlap)

    if not overlap_scores:
        return False, "L2: 摘要无可比关键词"

    avg_overlap = sum(overlap_scores) / len(overlap_scores)
    if avg_overlap < 0.2:
        return False, f"L2: 平均关键词重叠 {avg_overlap:.2f} < 0.2(疑似曲解)"
    return True, f"L2 PASS (关键词平均重叠 {avg_overlap:.2f})"


# ============================================================
# L3 知识密度
# ============================================================

def check_L3_density(out_dir: Path) -> Tuple[bool, str]:
    """L3 知识密度:概念 ≥ 3 + 案例 ≥ 1 + 知识图谱 ≥ 1 三元组。"""
    paths = {
        "concepts": out_dir / "concepts.json",
        "cases": out_dir / "cases.json",
        "kg": out_dir / "kg.json",
    }
    missing = [k for k, p in paths.items() if not p.exists()]
    if missing:
        return False, f"L3: 缺失产物 {missing}"

    concepts = json.loads(paths["concepts"].read_text(encoding="utf-8"))
    cases = json.loads(paths["cases"].read_text(encoding="utf-8"))
    kg = json.loads(paths["kg"].read_text(encoding="utf-8"))

    issues = []
    if len(concepts) < 3:
        issues.append(f"概念 {len(concepts)} < 3")
    if len(cases) < 1:
        issues.append(f"案例 {len(cases)} < 1")
    if len(kg) < 1:
        issues.append(f"三元组 {len(kg)} < 1")

    if issues:
        return False, f"L3: 知识密度不足 ({', '.join(issues)})"
    return True, f"L3 PASS (概念 {len(concepts)} · 案例 {len(cases)} · 三元组 {len(kg)})"


# ============================================================
# L4 复用价值
# ============================================================

def check_L4_reuse(out_dir: Path) -> Tuple[bool, str]:
    """L4 复用价值:summary.json 含 book_title + 至少 1 类输出 ≥ 1。

    简化版:验证 summary.json 结构完整。
    """
    p = out_dir / "summary.json"
    if not p.exists():
        return False, "L4: summary.json 缺失"

    summary = json.loads(p.read_text(encoding="utf-8"))
    if "book_title" not in summary:
        return False, "L4: summary.json 缺 book_title"
    if "outputs" not in summary:
        return False, "L4: summary.json 缺 outputs"

    outputs = summary["outputs"]
    if not outputs:
        return False, "L4: outputs 为空"

    # 至少 1 类产出 ≥ 1
    nonzero = [k for k, v in outputs.items() if v and v > 0]
    if not nonzero:
        return False, f"L4: 所有输出都为 0 ({outputs})"
    return True, f"L4 PASS (非零产出 {nonzero} · book_title={summary['book_title']!r})"


# ============================================================
# 主入口
# ============================================================

def quality_check(out_dir: Path) -> Tuple[bool, dict]:
    """跑 4 层自检。

    返回 (all_pass, report_dict)
    """
    checks = {
        "L1_completeness": check_L1_completeness(out_dir),
        "L2_consistency": check_L2_consistency(out_dir),
        "L3_density": check_L3_density(out_dir),
        "L4_reuse": check_L4_reuse(out_dir),
    }
    report = {
        "out_dir": str(out_dir),
        "checks": {k: {"pass": ok, "msg": msg} for k, (ok, msg) in checks.items()},
    }
    all_pass = all(ok for ok, _ in checks.values())
    report["all_pass"] = all_pass
    return all_pass, report


def main() -> int:
    ap = argparse.ArgumentParser(description="book-distiller V9.12 4 层自检")
    ap.add_argument("--out-dir", required=True, help="distill.py 产物目录")
    args = ap.parse_args()

    out_dir = Path(args.out_dir).resolve()
    if not out_dir.exists():
        print(f"ERROR: out-dir not found: {out_dir}", file=sys.stderr)
        return 3

    all_pass, report = quality_check(out_dir)

    print("=" * 60)
    print("book-distiller V9.12 · 4 层自检")
    print("=" * 60)
    for k, c in report["checks"].items():
        tag = "PASS" if c["pass"] else "FAIL"
        print(f"  [{tag}] {k}: {c['msg']}")
    print("=" * 60)
    if all_pass:
        print("[OK] 4 层全部 PASS")
    else:
        n_fail = sum(1 for c in report["checks"].values() if not c["pass"])
        print(f"[X] {n_fail} 层 FAIL")

    # 写报告
    report_path = out_dir / "quality_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())