"""em_debate_check.py · 阶段 35 重建精简版"""
import argparse
import re
import sys
from pathlib import Path

ANALYST_KEYWORDS = ["fundamental_analyst", "technical_analyst", "sentiment_analyst",
                    "valuation_analyst", "risk_analyst", "macro_analyst", "regulatory_analyst"]
RISK_KEYWORDS = ["市场风险", "政策风险", "流动性风险", "合规风险", "经营风险"]


def check_all_7_analysts(md):
    present = [k for k in ANALYST_KEYWORDS if k in md]
    missing = [k for k in ANALYST_KEYWORDS if k not in md]
    return len(missing) == 0, f"present={len(present)}/7 missing={missing}"


def check_rating_with_rationale(md):
    found = 0
    for role in ANALYST_KEYWORDS:
        if role in md:
            if re.search(rf"{role}[^\n]*\n[^\n]*评分[^\n]*", md):
                found += 1
    return found >= 5, f"analysts_with_rationale={found}/7"


def check_bull_bear_debate(md):
    bull = len(re.findall(r"- \[\+\]", md))
    bear = len(re.findall(r"- \[-\]", md))
    return bull >= 3 and bear >= 3, f"bull={bull} bear={bear}"


def check_risk_5_categories(md):
    present = [k for k in RISK_KEYWORDS if k in md]
    missing = [k for k in RISK_KEYWORDS if k not in md]
    return len(missing) == 0, f"present={len(present)}/5 missing={missing}"


def check_apache_attribution(md):
    has_upstream = "simonlin1212" in md
    has_apache = "Apache-2.0" in md or "Apache License" in md
    has_modified = "Modified" in md or "天龙引擎" in md or "天蟒引擎" in md
    return has_upstream and has_apache and has_modified, f"upstream={has_upstream} apache={has_apache} modified={has_modified}"


def check_decision_complete(md):
    has_d = bool(re.search(r"\*\*决策\*\*:", md))
    has_p = bool(re.search(r"\*\*仓位\*\*:", md))
    has_h = bool(re.search(r"\*\*持有期\*\*:", md))
    return has_d and has_p and has_h, f"d={has_d} p={has_p} h={has_h}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("md_file")
    args = parser.parse_args()
    path = Path(args.md_file)
    if not path.exists():
        print(f"[ERROR] {path}")
        sys.exit(3)
    md = path.read_text(encoding="utf-8")
    checks = [
        ("W1 7 分析师", check_all_7_analysts),
        ("W2 评分依据", check_rating_with_rationale),
        ("W3 辩论完整", check_bull_bear_debate),
        ("W4 5 类风险", check_risk_5_categories),
        ("W5 Apache", check_apache_attribution),
    ]
    recommended = [("R2 决策完整", check_decision_complete)]
    failed = []
    warned = []
    print(f"[Check] {path}")
    for label, fn in checks:
        ok, note = fn(md)
        print(f"  {'[OK]' if ok else '[FAIL]'} {label}  ({note})")
        if not ok:
            failed.append(label)
    for label, fn in recommended:
        ok, note = fn(md)
        print(f"  {'[OK]' if ok else '[WARN]'} {label}  ({note})")
        if not ok:
            warned.append(label)
    print()
    if failed:
        print(f"[FAIL] {len(failed)}")
        sys.exit(1)
    if warned:
        print(f"[WARN] {len(warned)}")
        sys.exit(2)
    print("[PASS]")
    sys.exit(0)


if __name__ == "__main__":
    main()