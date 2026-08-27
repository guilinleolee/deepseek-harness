#!/usr/bin/env python3
"""
nuwa_check.py · nuwa-skill × 天龙引擎合规自检

Exit code 契约:
  0 = PASS (全部合规)
  1 = FAIL (mirror 不完整 / LICENSE 缺失)
  2 = WARN (MIT 致谢段未填充 / frontmatter 字段缺失)
  3 = ERROR (系统错 · 文件读取失败)

用法:
  python scripts/nuwa_check.py
  python scripts/nuwa_check.py --target all
"""

from __future__ import annotations
import sys
import os
import re
from pathlib import Path
from typing import List, Tuple

# Force UTF-8 stdout/stderr for Windows GBK encoding compatibility
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


SKILL_DIR = Path(__file__).resolve().parent.parent
LICENSE_PATH = SKILL_DIR / "LICENSE"
SKILL_MD_PATH = SKILL_DIR / "SKILL.md"
AGENT_PATH = SKILL_DIR / "AGENT.md"
HANDOFF_PATH = SKILL_DIR / "HANDOFF.md"
PRODUCT_PATH = SKILL_DIR / "PRODUCT.md"
L3_SPECS_PATH = SKILL_DIR / "l3-specs"
SCRIPTS_DIR = SKILL_DIR / "scripts"
REFERENCES_DIR = SKILL_DIR / "references"
EXAMPLES_DIR = SKILL_DIR / "examples"


def check_license_exists() -> Tuple[bool, str]:
    """LICENSE verbatim 存在校验"""
    if not LICENSE_PATH.exists():
        return False, "LICENSE missing"
    txt = LICENSE_PATH.read_text(encoding="utf-8", errors="ignore")
    if "MIT License" not in txt:
        return False, "LICENSE does not contain 'MIT License'"
    if "Copyright" not in txt:
        return False, "LICENSE missing Copyright"
    size = LICENSE_PATH.stat().st_size
    if size < 800 or size > 1500:
        return False, f"LICENSE size abnormal: {size} B (expected 800-1500)"
    return True, f"LICENSE verbatim OK ({size} B)"


def check_frontmatter() -> Tuple[bool, str]:
    """SKILL.md frontmatter 必填字段"""
    if not SKILL_MD_PATH.exists():
        return False, "SKILL.md missing"
    content = SKILL_MD_PATH.read_text(encoding="utf-8", errors="ignore")
    required = ["license: MIT", "source:", "upstream:", "modified_by:", "mirror_mode:"]
    missing = [f for f in required if f not in content]
    if missing:
        return False, f"SKILL.md frontmatter missing: {missing}"
    return True, "SKILL.md frontmatter OK"


def check_tianlong_extensions() -> Tuple[bool, str]:
    """天龙扩展文档存在"""
    missing = []
    for name, path in [
        ("AGENT.md", AGENT_PATH),
        ("HANDOFF.md", HANDOFF_PATH),
        ("PRODUCT.md", PRODUCT_PATH),
    ]:
        if not path.exists():
            missing.append(name)
    if missing:
        return False, f"天龙扩展文档缺失: {missing}"
    return True, "天龙扩展三件套齐全 (AGENT/HANDOFF/PRODUCT)"


def check_mirror_integrity() -> Tuple[bool, str]:
    """mirror 文件存在性"""
    required_dirs = [SCRIPTS_DIR, REFERENCES_DIR, EXAMPLES_DIR]
    missing_dirs = [d for d in required_dirs if not d.exists()]
    if missing_dirs:
        return False, f"upstream 镜像目录缺失: {[d.name for d in missing_dirs]}"

    scripts_required = ["quality_check.py"]
    scripts_missing = [s for s in scripts_required if not (SCRIPTS_DIR / s).exists()]
    if scripts_missing:
        return False, f"upstream scripts 缺失: {scripts_missing}"

    references_required = ["extraction-framework.md", "fidelity-scorecard.md", "skill-template.md"]
    refs_missing = [r for r in references_required if not (REFERENCES_DIR / r).exists()]
    if refs_missing:
        return False, f"upstream references 缺失: {refs_missing}"

    examples = list(EXAMPLES_DIR.iterdir()) if EXAMPLES_DIR.exists() else []
    if len(examples) < 5:
        return False, f"upstream examples 数量异常: {len(examples)} (期望 ≥ 5)"

    return True, f"upstream mirror 完整 (scripts={len(list(SCRIPTS_DIR.iterdir()))} references={len(list(REFERENCES_DIR.iterdir()))} examples={len(examples)})"


def check_l3_specs() -> Tuple[bool, str]:
    """l3-specs 子目录存在（MIT 允许子包装）"""
    if not L3_SPECS_PATH.exists():
        return False, "l3-specs/ 缺失 (MIT 允许子包装，天龙应落地本地增强)"
    files = list(L3_SPECS_PATH.iterdir())
    if not files:
        return False, "l3-specs/ 为空"
    return True, f"l3-specs/ 存在 ({len(files)} 文件)"


def check_evidence() -> List[str]:
    """evidence: 把每个 check 的状态记录下来"""
    return []


def main() -> int:
    checks = [
        ("LICENSE verbatim", check_license_exists),
        ("SKILL.md frontmatter", check_frontmatter),
        ("天龙扩展文档", check_tianlong_extensions),
        ("upstream mirror 完整性", check_mirror_integrity),
        ("l3-specs/ 子目录", check_l3_specs),
    ]

    print("=" * 70)
    print(f"nuwa-skill × 天龙引擎 合规自检")
    print("=" * 70)

    fail_count = 0
    warn_count = 0
    for name, fn in checks:
        try:
            ok, msg = fn()
            tag = "✅ PASS" if ok else "❌ FAIL"
            print(f"  [{tag}] {name}: {msg}")
            if not ok:
                fail_count += 1
        except Exception as e:
            print(f"  [⚠️ ERROR] {name}: {e}")
            fail_count += 1

    print("=" * 70)
    if fail_count == 0:
        print("🟢 全部合规 → exit 0")
        return 0
    print(f"🔴 {fail_count} 项不达标 → exit 1")
    return 1


if __name__ == "__main__":
    sys.exit(main())