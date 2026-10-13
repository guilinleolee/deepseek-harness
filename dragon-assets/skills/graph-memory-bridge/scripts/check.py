"""check.py · graph-memory-bridge 健康检查 · V1.0"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = SKILL_ROOT / "SKILL.md"
LICENSE = SKILL_ROOT / "LICENSE"
NOTICE = SKILL_ROOT / "NOTICE"
SCRIPT = SKILL_ROOT / "scripts" / "extractor.py"


def check_01_skill_md() -> tuple[bool, str]:
    if not SKILL_MD.exists():
        return False, f"[FAIL] SKILL.md 不存在: {SKILL_MD}"
    text = SKILL_MD.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False, "[FAIL] 缺 YAML frontmatter"
    if "name:" not in text[:500] or "description:" not in text[:1000]:
        return False, "[FAIL] frontmatter 缺 name/description"
    return True, "[PASS] SKILL.md 存在 + YAML frontmatter"


def check_02_mit_license() -> tuple[bool, str]:
    if not LICENSE.exists():
        return False, "[FAIL] LICENSE 不存在"
    text = LICENSE.read_text(encoding="utf-8")
    if "MIT License" not in text:
        return False, "[FAIL] LICENSE 不是 MIT"
    if "Copyright (c) 2026 adoresever" not in text:
        return False, "[FAIL] LICENSE 缺上游版权"
    return True, "[PASS] LICENSE (MIT) + 上游版权完整"


def check_03_modified_by_notice() -> tuple[bool, str]:
    if not NOTICE.exists():
        return False, "[FAIL] NOTICE 不存在"
    text = NOTICE.read_text(encoding="utf-8")
    if "Modified by dragon-engine" not in text:
        return False, "[FAIL] NOTICE 缺 Modified 段"
    if "adoresever" not in text:
        return False, "[FAIL] NOTICE 缺上游版权声明"
    return True, "[PASS] NOTICE 含 Modified 段 + 上游版权"


def check_04_three_node_types() -> tuple[bool, str]:
    text = SCRIPT.read_text(encoding="utf-8")
    for nt in ["TASK", "SKILL", "EVENT"]:
        if f'"{nt}"' not in text and f'NodeType.{nt}' not in text and f'= "{nt}"' not in text:
            return False, f"[FAIL] 缺 NodeType.{nt}"
    return True, "[PASS] 3 类节点 (TASK/SKILL/EVENT) 完整"


def check_05_five_edge_types() -> tuple[bool, str]:
    text = SCRIPT.read_text(encoding="utf-8")
    for et in ["USED_SKILL", "SOLVED_BY", "REQUIRES", "PATCHES", "CONFLICTS_WITH"]:
        if et not in text:
            return False, f"[FAIL] 缺 EdgeType.{et}"
    return True, "[PASS] 5 类边 (USED_SKILL/SOLVED_BY/REQUIRES/PATCHES/CONFLICTS_WITH) 完整"


def check_06_four_gm_tools() -> tuple[bool, str]:
    text = SCRIPT.read_text(encoding="utf-8")
    tools = ["gm_status", "gm_search", "gm_record", "gm_stats"]
    missing = [t for t in tools if f"def {t}" not in text]
    if missing:
        return False, f"[FAIL] 缺 gm_* 工具: {missing}"
    return True, "[PASS] 4 个 gm_* 工具 (status/search/record/stats) 完整"


def check_07_ppr_recall_token_budget() -> tuple[bool, str]:
    text = SCRIPT.read_text(encoding="utf-8")
    required = ["personalized_pagerank", "recall", "recallTokenBudget", "4096",
                "autoRecallMinScore"]
    missing = [r for r in required if r not in text]
    if missing:
        return False, f"[FAIL] 缺核心: {missing}"
    return True, "[PASS] PPR + recall + tokenBudget (4096) + autoRecallMinScore 完整"


def check_08_rolling_checkpoint() -> tuple[bool, str]:
    text = SCRIPT.read_text(encoding="utf-8")
    if "rolling_checkpoint" not in text or "freshTurnCount" not in text:
        return False, "[FAIL] 缺 rolling_checkpoint 或 freshTurnCount"
    return True, "[PASS] rolling_checkpoint + freshTurnCount 完整"


def check_09_upstream_keywords() -> tuple[bool, str]:
    text = SKILL_MD.read_text(encoding="utf-8")
    keywords = ["Knowledge Graph", "TASK", "SKILL", "EVENT", "USED_SKILL",
                "Personalized PageRank", "75%", "autoRecallMinScore",
                "gm_search", "gm_record", "freshTurnCount"]
    text_lower = text.lower()
    missing = [k for k in keywords if k.lower() not in text_lower]
    if len(missing) > 3:
        return False, f"[FAIL] SKILL.md 缺关键词: {missing[:5]}"
    return True, "[PASS] 上游 ≥ 8 关键词覆盖"


CHECKS = [
    ("check_01_skill_md", "1. SKILL.md + frontmatter"),
    ("check_02_mit_license", "2. LICENSE MIT"),
    ("check_03_modified_by_notice", "3. NOTICE 含 Modified"),
    ("check_04_three_node_types", "4. 3 类节点 (TASK/SKILL/EVENT)"),
    ("check_05_five_edge_types", "5. 5 类边"),
    ("check_06_four_gm_tools", "6. 4 个 gm_* 工具"),
    ("check_07_ppr_recall_token_budget", "7. PPR + recall + tokenBudget"),
    ("check_08_rolling_checkpoint", "8. rolling_checkpoint"),
    ("check_09_upstream_keywords", "9. 上游 11 关键词"),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", help="单测名")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.check:
        fn = globals().get(args.check)
        if not fn:
            print(f"[FAIL] 未知: {args.check}", file=sys.stderr)
            return 1
        ok, msg = fn()
        print(msg)
        return 0 if ok else 1

    results = {}
    for fn, lbl in CHECKS:
        ok, msg = globals()[fn]()
        results[fn] = {"label": lbl, "pass": ok, "msg": msg}

    passed = sum(1 for r in results.values() if r["pass"])
    total = len(results)

    if args.json:
        print(json.dumps({"passed": passed, "total": total, "results": results}, ensure_ascii=False, indent=2))
    else:
        print("=" * 70)
        print("graph-memory-bridge Health Check · Stage 55.1")
        print("=" * 70)
        for info in results.values():
            print(f"  {info['msg']}")
        print("=" * 70)
        print(f"  PASSED: {passed} / {total}")
        print("=" * 70)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
