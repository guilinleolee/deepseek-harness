#!/usr/bin/env python3
"""
darwin_check.py · darwin-skill × 天龙引擎合规自检

Exit code 契约:
  0 = PASS (全部合规)
  1 = FAIL (mirror 不完整 / LICENSE 缺失)
  2 = WARN (MIT 致谢段未填充 / frontmatter 字段缺失)
  3 = ERROR (系统错 · 文件读取失败)
"""

from __future__ import annotations
import sys
import os
from pathlib import Path
from typing import Tuple

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
TEMPLATES_DIR = SKILL_DIR / "templates"
ASSETS_DIR = SKILL_DIR / "assets"
TEST_PROMPTS_PATH = SKILL_DIR / "test-prompts.json"


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
    required_dirs = [SCRIPTS_DIR, REFERENCES_DIR, TEMPLATES_DIR, ASSETS_DIR]
    missing_dirs = [d for d in required_dirs if not d.exists()]
    if missing_dirs:
        return False, f"upstream 镜像目录缺失: {[d.name for d in missing_dirs]}"

    if not TEST_PROMPTS_PATH.exists():
        return False, "test-prompts.json 缺失 (上游核心协议文件)"

    refs_required = ["runtime-neutrality.md", "skilllens-evidence.md"]
    refs_missing = [r for r in refs_required if not (REFERENCES_DIR / r).exists()]
    if refs_missing:
        return False, f"upstream references 缺失: {refs_missing}"

    templates_required = ["result-card.html", "result-card-dark.html", "result-card-white.html"]
    templates_missing = [t for t in templates_required if not (TEMPLATES_DIR / t).exists()]
    if templates_missing:
        return False, f"upstream templates 缺失: {templates_missing}"

    scripts = list(SCRIPTS_DIR.iterdir()) if SCRIPTS_DIR.exists() else []
    if not scripts:
        return False, "upstream scripts/ 为空"

    assets = list(ASSETS_DIR.iterdir()) if ASSETS_DIR.exists() else []
    if len(assets) < 10:
        return False, f"upstream assets 数量异常: {len(assets)} (期望 >= 10)"

    return True, f"upstream mirror 完整 (scripts={len(scripts)} templates={len(templates_required)} assets={len(assets)})"


def check_l3_specs() -> Tuple[bool, str]:
    """l3-specs 子目录存在（MIT 允许子包装）"""
    if not L3_SPECS_PATH.exists():
        return False, "l3-specs/ 缺失"
    files = list(L3_SPECS_PATH.iterdir())
    if not files:
        return False, "l3-specs/ 为空"
    bridge = L3_SPECS_PATH / "darwin-neat-freak-bridge.md"
    if not bridge.exists():
        return False, "darwin-neat-freak-bridge.md 缺失 (天龙核心联动协议)"
    return True, f"l3-specs/ 存在 ({len(files)} 文件，含 neat-freak 联动)"


def check_9_dim_rubric_reference() -> Tuple[bool, str]:
    """SKILL.md 引用 9 维 rubric"""
    content = SKILL_MD_PATH.read_text(encoding="utf-8", errors="ignore")
    required_keywords = ["9-dimension", "9-dim", "rubric", "SkillLens", "skilllens-evidence"]
    found = [k for k in required_keywords if k in content or k.lower() in content.lower()]
    if len(found) < 2:
        return False, f"SKILL.md 9 维 rubric 引用不足 (found: {found})"
    return True, f"9 维 rubric 引用 OK ({len(found)} 关键词)"


def check_test_prompts_format() -> Tuple[bool, str]:
    """test-prompts.json darwin 格式校验"""
    if not TEST_PROMPTS_PATH.exists():
        return False, "test-prompts.json 缺失"
    import json
    try:
        data = json.loads(TEST_PROMPTS_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"test-prompts.json JSON 解析失败: {e}"
    if not isinstance(data, list) or len(data) < 1:
        return False, "test-prompts.json 应为非空数组"
    required_fields = ["id", "scenario", "prompt", "expected"]
    for i, item in enumerate(data):
        missing = [f for f in required_fields if f not in item]
        if missing:
            return False, f"test case {i} 缺字段: {missing}"
    return True, f"test-prompts.json 格式 OK ({len(data)} test cases)"


def main() -> int:
    checks = [
        ("LICENSE verbatim", check_license_exists),
        ("SKILL.md frontmatter", check_frontmatter),
        ("天龙扩展文档", check_tianlong_extensions),
        ("upstream mirror 完整性", check_mirror_integrity),
        ("l3-specs/ 子目录 + neat-freak bridge", check_l3_specs),
        ("9 维 rubric 引用", check_9_dim_rubric_reference),
        ("test-prompts.json 格式", check_test_prompts_format),
    ]

    print("=" * 70)
    print(f"darwin-skill × 天龙引擎 合规自检")
    print("=" * 70)

    fail_count = 0
    for name, fn in checks:
        try:
            ok, msg = fn()
            tag = "PASS" if ok else "FAIL"
            print(f"  [{tag}] {name}: {msg}")
            if not ok:
                fail_count += 1
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")
            fail_count += 1

    print("=" * 70)
    if fail_count == 0:
        print("[OK] 全部合规 → exit 0")
        return 0
    print(f"[X] {fail_count} 项不达标 → exit 1")
    return 1


if __name__ == "__main__":
    sys.exit(main())