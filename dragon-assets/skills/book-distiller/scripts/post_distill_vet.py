#!/usr/bin/env python3
"""
book-distiller V9.12 · post_distill_vet 联动(post_distill_vet.py)
===============================================================

V9.12 联动 github-to-skills V1.1:
蒸馏产物写入 skills/ 或 agents/ 时自动跑 vet,确保不混入危险模式。

CLI:
    python post_distill_vet.py --distill-out <DIR>
"""

from __future__ import annotations
import argparse
import json
import sys
import re
from pathlib import Path
from typing import Tuple


# ============================================================
# 危险模式扫描
# ============================================================

DANGER_PATTERNS = {
    "exfiltrate": [r"curl\s+.*-d\s+@", r"curl.*\|\s*sh", r"wget.*\|\s*sh", r"\$\(.*base64.*-d"],
    "secret_leak": [r"sk-[a-zA-Z0-9]{20,}", r"AKIA[0-9A-Z]{16}", r"ghp_[a-zA-Z0-9]{36}"],
    "rm_rf": [r"rm\s+-rf\s+/"],
    "reverse_shell": [r"bash\s+-i\s+>&?\s*/dev/tcp", r"nc\s+-e\s+/bin"],
}


def vet(out_dir: Path) -> Tuple[bool, dict]:
    """对蒸馏产物做危险模式扫描。"""
    findings = []

    if not out_dir.exists():
        return False, {"error": f"out_dir {out_dir} 不存在"}

    for f in out_dir.rglob("*.md"):
        text = f.read_text(encoding="utf-8", errors="ignore")
        for category, patterns in DANGER_PATTERNS.items():
            for pat in patterns:
                matches = re.findall(pat, text)
                if matches:
                    findings.append({
                        "file": str(f.relative_to(out_dir)),
                        "category": category,
                        "pattern": pat,
                        "count": len(matches),
                    })

    report = {
        "out_dir": str(out_dir),
        "scanned_files": len(list(out_dir.rglob("*.md"))),
        "findings": findings,
        "vet_pass": len(findings) == 0,
    }
    return report["vet_pass"], report


def main() -> int:
    ap = argparse.ArgumentParser(description="post_distill_vet")
    ap.add_argument("--distill-out", required=True)
    args = ap.parse_args()

    out_dir = Path(args.distill_out).resolve()
    ok, report = vet(out_dir)

    print("=" * 60)
    print(f"post_distill_vet · 扫描 {out_dir}")
    print(f"  扫描文件数: {report.get('scanned_files', 0)}")
    print(f"  发现危险模式: {len(report.get('findings', []))}")
    if not ok:
        for f in report["findings"]:
            print(f"    [X] {f['file']} - {f['category']} ({f['count']} 处匹配)")
    print("=" * 60)
    if ok:
        print("[OK] post_distill_vet PASS")
    else:
        print("[X] post_distill_vet FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())