"""
dsh-univer-office-bridge · 健康检查 + 累计 PASS 验证 · V1.0

5 项 PASS：
  1. dragon-engine/skills/dsh-univer-office-bridge/SKILL.md 存在且含 frontmatter
  2. 上游 7 个 SKILL.md 镜像全部存在（univer / univer-sheet / univer-doc / univer-slide / univer-base / univer-board / univer-embed / univer-cross-unit-formula）
  3. LICENSE + NOTICE 双件套存在且 Apache-2.0
  4. NOTICE 含 "Modified by dragon-engine" 段
  5. 触发词命中 — references/triggers.md 含 ≥30 个触发词 + 5 类 Unit 路由齐全

退出码契约：
  0 = 全部 PASS
  1 = 至少 1 项 FAIL
  2 = 部分 PASS（warning 但不阻断）

支持 CLI 参数：
  python check.py            # 跑全部
  python check.py --check X  # 单测
  python check.py --json     # JSON 输出

Author: dragon-engine · Stage 26 · 2026-08-26
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ─── 路径常量 ────────────────────────────────────────────────────────────────
SKILL_ROOT = Path(__file__).resolve().parent.parent
DRAGON_ENGINE_ROOT = SKILL_ROOT.parent.parent  # dragon-engine/skills/dsh-univer-office-bridge → dragon-engine
SKILL_MD = SKILL_ROOT / "SKILL.md"
LICENSE = SKILL_ROOT / "LICENSE"
NOTICE = SKILL_ROOT / "NOTICE"
TRIGGERS = SKILL_ROOT / "references" / "triggers.md"

UPSTREAM_SKILLS = [
    "univer",
    "univer-sheet",
    "univer-doc",
    "univer-slide",
    "univer-base",
    "univer-board",
    "univer-embed",
    "univer-cross-unit-formula",
]

UPSTREAM_SKILL_ROOT = DRAGON_ENGINE_ROOT / "skills"


# ─── 检查项 ────────────────────────────────────────────────────────────────

def check_01_skill_md_exists() -> tuple[bool, str]:
    """1. dragon-engine/skills/dsh-univer-office-bridge/SKILL.md 存在 + frontmatter 完整"""
    if not SKILL_MD.exists():
        return False, f"[FAIL] SKILL.md 不存在: {SKILL_MD}"
    text = SKILL_MD.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False, "[FAIL] 缺 YAML frontmatter（应以 --- 开头）"
    if "name:" not in text[:500]:
        return False, "[FAIL] frontmatter 缺 name 字段"
    if "description:" not in text[:1000]:
        return False, "[FAIL] frontmatter 缺 description 字段"
    return True, "[PASS] SKILL.md 存在 + YAML frontmatter 完整"


def check_02_upstream_skill_mirrors() -> tuple[bool, str]:
    """2. 上游 7+ 个 SKILL.md 镜像全部存在（实际 8 个：univer + 5 Unit + embed + cross-unit-formula）"""
    missing = []
    for slug in UPSTREAM_SKILLS:
        path = UPSTREAM_SKILL_ROOT / slug / "SKILL.md"
        if not path.exists():
            missing.append(slug)
    if missing:
        return False, f"[FAIL] 缺镜像: {missing}"
    return True, f"[PASS] 上游 {len(UPSTREAM_SKILLS)} 个 SKILL.md 全部镜像: {', '.join(UPSTREAM_SKILLS)}"


def check_03_license_notice_pair() -> tuple[bool, str]:
    """3. LICENSE + NOTICE 双件套存在 + Apache-2.0"""
    if not LICENSE.exists():
        return False, "[FAIL] LICENSE 不存在"
    if not NOTICE.exists():
        return False, "[FAIL] NOTICE 不存在"
    license_text = LICENSE.read_text(encoding="utf-8")
    if "Apache License" not in license_text or "Version 2.0" not in license_text:
        return False, "[FAIL] LICENSE 不是 Apache-2.0"
    notice_text = NOTICE.read_text(encoding="utf-8")
    if "Apache License 2.0" not in notice_text and "Apache-2.0" not in notice_text:
        return False, "[FAIL] NOTICE 未声明 Apache-2.0"
    return True, "[PASS] LICENSE + NOTICE 双件套存在 + Apache-2.0"


def check_04_modified_by_notice() -> tuple[bool, str]:
    """4. NOTICE 含 'Modified by dragon-engine' 段"""
    if not NOTICE.exists():
        return False, "[FAIL] NOTICE 不存在"
    text = NOTICE.read_text(encoding="utf-8")
    if "Modified by dragon-engine" not in text:
        return False, "[FAIL] NOTICE 缺 'Modified by dragon-engine' 段（Apache-2.0 §4(d) 红线）"
    if "DreamNum" not in text:
        return False, "[FAIL] NOTICE 缺上游版权声明 DreamNum Co., Ltd."
    if "Section 3" not in text or "Trademark" not in text:
        return False, "[FAIL] NOTICE 缺第 6 条商标声明段"
    return True, "[PASS] NOTICE 含 'Modified by dragon-engine' + 上游版权 + 商标声明"


def check_05_triggers_coverage() -> tuple[bool, str]:
    """5. 触发词命中 — triggers.md ≥30 个触发词 + 5 类 Unit 路由齐全"""
    if not TRIGGERS.exists():
        return False, f"[FAIL] triggers.md 不存在: {TRIGGERS}"
    text = TRIGGERS.read_text(encoding="utf-8")
    # 统计行内出现的触发词（每行一个 | xxx | yyy |）
    pipe_rows = re.findall(r"^\|[^|]+\|[^|]+\|\s*$", text, re.MULTILINE)
    # 提取每行的左侧（中文）和右侧（英文）
    zh_triggers = []
    en_triggers = []
    for row in pipe_rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        if len(cells) >= 2:
            zh_triggers.append(cells[0])
            en_triggers.append(cells[1])
    total = len(zh_triggers) + len(en_triggers)
    if total < 30:
        return False, f"[FAIL] 触发词总数 {total} < 30"
    # 检查 5 类 Unit 路由齐全
    required_sections = ["Sheet", "Doc", "Slide", "Base", "Board"]
    missing = [s for s in required_sections if s not in text]
    if missing:
        return False, f"[FAIL] 触发词 5 类 Unit 路由不全，缺: {missing}"
    return True, f"[PASS] 触发词 {total} 个（{len(zh_triggers)} 中文 + {len(en_triggers)} 英文）+ 5 类 Unit 路由齐全"


# ─── 主入口 ────────────────────────────────────────────────────────────────

CHECKS = [
    ("check_01_skill_md_exists", "1. SKILL.md 存在 + frontmatter"),
    ("check_02_upstream_skill_mirrors", "2. 上游 8 个 SKILL.md 镜像齐全"),
    ("check_03_license_notice_pair", "3. LICENSE + NOTICE Apache-2.0"),
    ("check_04_modified_by_notice", "4. NOTICE 含 Modified by dragon-engine"),
    ("check_05_triggers_coverage", "5. 触发词 ≥30 + 5 类 Unit 路由"),
]


def run_all() -> dict:
    results = {}
    for fn_name, label in CHECKS:
        fn = globals()[fn_name]
        ok, msg = fn()
        results[fn_name] = {"label": label, "pass": ok, "msg": msg}
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="dsh-univer-office-bridge 健康检查")
    parser.add_argument("--check", help="单测名（如 check_01_skill_md_exists）")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    args = parser.parse_args()

    if args.check:
        fn = globals().get(args.check)
        if not fn:
            print(f"❌ 未知检查项: {args.check}", file=sys.stderr)
            return 1
        ok, msg = fn()
        if args.json:
            print(json.dumps({"check": args.check, "pass": ok, "msg": msg}, ensure_ascii=False))
        else:
            print(msg)
        return 0 if ok else 1

    results = run_all()
    passed = sum(1 for r in results.values() if r["pass"])
    total = len(results)

    if args.json:
        print(json.dumps({"passed": passed, "total": total, "results": results}, ensure_ascii=False, indent=2))
    else:
        print("=" * 70)
        print("dsh-univer-office-bridge Health Check · Stage 26")
        print("=" * 70)
        for fn_name, info in results.items():
            print(f"  {info['msg']}")
        print("=" * 70)
        print(f"  PASSED: {passed} / {total}")
        print("=" * 70)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
