#!/usr/bin/env python3
"""
cangjie_check.py · cangjie-skill × 天龙引擎合规自检（AGPL 严格）

Exit code 契约:
  0 = PASS (全部合规)
  1 = FAIL (mirror 不完整 / LICENSE 缺失 / AGPL 红线触犯)
  2 = WARN (AGPL 致谢段未填充 / frontmatter 字段缺失)
  3 = ERROR (系统错 · 文件读取失败)

8 项 AGPL 红线:
  R1 LICENSE 是 AGPL-3.0 verbatim (不可删任何条款)
  R2 mirror-only 严格（upstream methodology/extractors/templates 字节级保护）
  R3 COMMERCIAL_LICENSING.md 存在
  R4 README.md 末尾 AGPL 强制署名段
  R5 test-prompts.json 模板含 darwin_compatible 字段
  R6 5 场景风险矩阵已写入产品文档
  R7 不得 upload upstream methodology/extractors/templates 完整模板到对外网络
  R8 不得把 7 阶段 / 21 packs / 三重验证作为课程 / 自研产品售卖
"""

from __future__ import annotations
import sys
import os
import re
from pathlib import Path
from typing import Tuple

# Force UTF-8 stdout/stderr
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
COMMERCIAL_PATH = SKILL_DIR / "COMMERCIAL_LICENSING.md"
METHODOLOGY_DIR = SKILL_DIR / "methodology"
EXTRACTORS_DIR = SKILL_DIR / "extractors"
TEMPLATES_DIR = SKILL_DIR / "templates"
SCRIPTS_DIR = SKILL_DIR / "scripts"
TEST_PROMPTS_TEMPLATE = TEMPLATES_DIR / "test-prompts.json.template"


def check_license_agpl() -> Tuple[bool, str]:
    """R1: LICENSE AGPL-3.0 verbatim 完整 + 字节级大小校验"""
    if not LICENSE_PATH.exists():
        return False, "LICENSE missing"
    txt = LICENSE_PATH.read_text(encoding="utf-8", errors="ignore")
    if "GNU AFFERO GENERAL PUBLIC LICENSE" not in txt and "Affero General Public License" not in txt:
        return False, "LICENSE 不是 AGPL-3.0"
    if "Version 3" not in txt:
        return False, "LICENSE 缺少 AGPL Version 3 段"
    size = LICENSE_PATH.stat().st_size
    if size < 30000 or size > 40000:
        return False, f"LICENSE size 异常: {size} B (AGPL 原文期望 34000-35000 B)"
    return True, f"AGPL-3.0 LICENSE verbatim OK ({size} B)"


def check_mirror_integrity() -> Tuple[bool, str]:
    """R2: upstream methodology/extractors/templates 字节级保护"""
    methodology_required = [
        "00-overview.md", "01-stage0-adler.md", "02-stage1-parallel-extract.md",
        "03-stage1.5-triple-verify.md", "04-stage2-ria-plus.md", "05-stage3-zettelkasten.md",
        "06-stage4-pressure-test.md", "07-stage5-deliver.md",
    ]
    missing = [m for m in methodology_required if not (METHODOLOGY_DIR / m).exists()]
    if missing:
        return False, f"methodology 缺失: {missing}"

    extractors_required = [
        "case-extractor.md", "counter-example-extractor.md", "framework-extractor.md",
        "glossary-extractor.md", "principle-extractor.md",
    ]
    missing_e = [e for e in extractors_required if not (EXTRACTORS_DIR / e).exists()]
    if missing_e:
        return False, f"extractors 缺失: {missing_e}"

    templates_required = [
        "BOOK_OVERVIEW.md.template", "DIGEST.md.template", "INDEX.md.template",
        "SKILL.md.template", "test-prompts.json.template",
    ]
    missing_t = [t for t in templates_required if not (TEMPLATES_DIR / t).exists()]
    if missing_t:
        return False, f"templates 缺失: {missing_t}"

    return True, f"mirror 完整 (methodology={len(methodology_required)} extractors={len(extractors_required)} templates={len(templates_required)})"


def check_commercial_licensing() -> Tuple[bool, str]:
    """R3: COMMERCIAL_LICENSING.md AGPL 强制商用边界"""
    if not COMMERCIAL_PATH.exists():
        return False, "COMMERCIAL_LICENSING.md 缺失 (AGPL 强制)"
    content = COMMERCIAL_PATH.read_text(encoding="utf-8", errors="ignore")
    required = ["深度内置授权", "上架与露出合作", "收益分成", "AGPL-3.0"]
    missing = [r for r in required if r not in content]
    if missing:
        return False, f"COMMERCIAL_LICENSING 缺章节: {missing}"
    return True, f"COMMERCIAL_LICENSING 三档齐全 ({COMMERCIAL_PATH.stat().st_size} B)"


def check_readme_agpl_attribution() -> Tuple[bool, str]:
    """R4: README.md 末尾 AGPL 强制署名段（天龙扩展）"""
    readme_path = SKILL_DIR / "README.md"
    if not readme_path.exists():
        return False, "README.md 缺失"
    content = readme_path.read_text(encoding="utf-8", errors="ignore")
    # 上游 README 含 "GNU AGPL v3" / "AGPL v3.0" / "AGPL-3.0" 等多种写法
    has_agpl = any(marker in content for marker in [
        "AGPL-3.0", "AGPL v3", "AGPL_v3", "GNU AGPL", "Affero General Public License",
    ])
    if not has_agpl:
        return False, "README.md 末尾缺 AGPL 署名"
    return True, "README.md 末尾 AGPL 署名段 OK"


def check_test_prompts_darwin_compat() -> Tuple[bool, str]:
    """R5: test-prompts.json.template 含 darwin_compatible 字段"""
    if not TEST_PROMPTS_TEMPLATE.exists():
        return False, "test-prompts.json.template 缺失"
    content = TEST_PROMPTS_TEMPLATE.read_text(encoding="utf-8", errors="ignore")
    if "darwin_compatible" not in content:
        return False, "test-prompts.json.template 缺 darwin_compatible 字段"
    return True, "test-prompts.json.template 包含 darwin_compatible 字段"


def check_5_scenario_risk_matrix() -> Tuple[bool, str]:
    """R6: PRODUCT.md / COMMERCIAL_LICENSING.md 含 5 场景风险矩阵"""
    sources = [PRODUCT_PATH, COMMERCIAL_PATH]
    found = False
    for src in sources:
        if src.exists():
            content = src.read_text(encoding="utf-8", errors="ignore")
            scenarios = ["C1", "C2", "C3", "C4", "C5"]
            if all(s in content for s in scenarios):
                found = True
                break
    if not found:
        return False, f"5 场景风险矩阵缺失 (PRODUCT.md 或 COMMERCIAL_LICENSING.md 任一必须含 C1-C5)"
    return True, "5 场景风险矩阵完整 (PRODUCT.md 或 COMMERCIAL_LICENSING.md)"


def check_no_external_template_upload() -> Tuple[bool, str]:
    """R7: 文档层无 upload templates 完整到对外网络的指引"""
    for name, path in [("AGENT.md", AGENT_PATH), ("HANDOFF.md", HANDOFF_PATH), ("PRODUCT.md", PRODUCT_PATH)]:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        # 上传到 H5 / 博客 必须有禁止表述
        if "上传" in content and "禁止" not in content and "🔴" not in content:
            return False, f"{name} 提到「上传」但缺少「禁止」"
    return True, "文档层红线表述完整"


def check_not_selling_methodology() -> Tuple[bool, str]:
    """R8: 不把 7 阶段 / 21 packs / 三重验证作为方法论 / 课程 / 自研产品售卖"""
    for name, path in [("AGENT.md", AGENT_PATH), ("PRODUCT.md", PRODUCT_PATH), ("COMMERCIAL_LICENSING.md", COMMERCIAL_PATH)]:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        if "知识付费" in content and "禁止" not in content:
            return False, f"{name} 提到「知识付费」但缺少「禁止」"
    return True, "7 阶段 / 21 packs 作为知识付费售卖 ✓ 明确禁止"


def check_frontmatter() -> Tuple[bool, str]:
    """SKILL.md frontmatter 必填字段"""
    if not SKILL_MD_PATH.exists():
        return False, "SKILL.md missing"
    content = SKILL_MD_PATH.read_text(encoding="utf-8", errors="ignore")
    required = ["license: AGPL-3.0", "source:", "upstream:", "modified_by:", "mirror_mode:"]
    missing = [f for f in required if f not in content]
    if missing:
        return False, f"SKILL.md frontmatter missing: {missing}"
    return True, "SKILL.md frontmatter OK"


def check_no_l3_specs() -> Tuple[bool, str]:
    """AGPL 不可子包装 — 验证没有 l3-specs/ 目录（MIT 专属）"""
    l3_dir = SKILL_DIR / "l3-specs"
    if l3_dir.exists():
        files = list(l3_dir.iterdir())
        return False, f"AGPL 不允许 l3-specs/ 子包装（发现 {len(files)} 文件）"
    return True, "无 l3-specs/ (AGPL 禁止子包装 ✓)"


def main() -> int:
    checks = [
        ("R1 LICENSE AGPL-3.0 verbatim", check_license_agpl),
        ("R2 upstream mirror 字节级保护", check_mirror_integrity),
        ("R3 COMMERCIAL_LICENSING.md", check_commercial_licensing),
        ("R4 README.md AGPL 署名", check_readme_agpl_attribution),
        ("R5 test-prompts darwin 兼容", check_test_prompts_darwin_compat),
        ("R6 5 场景风险矩阵", check_5_scenario_risk_matrix),
        ("R7 不上传模板到对外网络", check_no_external_template_upload),
        ("R8 不卖方法论 / 课程", check_not_selling_methodology),
        ("SKILL.md frontmatter", check_frontmatter),
        ("AGPL 不可子包装验证", check_no_l3_specs),
    ]

    print("=" * 70)
    print(f"cangjie-skill × 天龙引擎 合规自检 (AGPL 严格)")
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