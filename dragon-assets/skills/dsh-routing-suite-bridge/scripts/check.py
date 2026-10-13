"""check.py · dsh-routing-suite-bridge 健康检查 · V1.0

6 项 PASS：
  1. SKILL.md 存在 + YAML frontmatter
  2. LICENSE (MIT) 存在 + SPDX
  3. NOTICE 含 "Modified by dragon-engine" 段
  4. 4-mode 路由常量定义
  5. dev_* 工具接口完整
  6. 上游关键词命中（spec/react/weak/mixed）

退出码契约：
  0 = 全部 PASS
  1 = 至少 1 项 FAIL
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
SKILL_MD = SKILL_ROOT / "SKILL.md"
LICENSE = SKILL_ROOT / "LICENSE"
NOTICE = SKILL_ROOT / "NOTICE"
ROUTER_PY = SKILL_ROOT / "scripts" / "router.py"
DEV_TOOLS_PY = SKILL_ROOT / "scripts" / "dev_tools.py"


def check_01_skill_md_exists() -> tuple[bool, str]:
    """1. SKILL.md 存在 + YAML frontmatter"""
    if not SKILL_MD.exists():
        return False, f"[FAIL] SKILL.md 不存在: {SKILL_MD}"
    text = SKILL_MD.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False, "[FAIL] 缺 YAML frontmatter"
    if "name:" not in text[:500] or "description:" not in text[:1000]:
        return False, "[FAIL] frontmatter 缺 name/description"
    return True, "[PASS] SKILL.md 存在 + YAML frontmatter"


def check_02_mit_license() -> tuple[bool, str]:
    """2. LICENSE (MIT) 存在 + SPDX 标识"""
    if not LICENSE.exists():
        return False, "[FAIL] LICENSE 不存在"
    text = LICENSE.read_text(encoding="utf-8")
    if "MIT License" not in text:
        return False, "[FAIL] LICENSE 不是 MIT"
    if "Copyright (c) 2026 yjh051108" not in text:
        return False, "[FAIL] LICENSE 缺上游版权"
    return True, "[PASS] LICENSE (MIT) + 上游版权完整"


def check_03_modified_by_notice() -> tuple[bool, str]:
    """3. NOTICE 含 Modified 段"""
    if not NOTICE.exists():
        return False, "[FAIL] NOTICE 不存在"
    text = NOTICE.read_text(encoding="utf-8")
    if "Modified by dragon-engine" not in text and "Adapted by dragon-engine" not in text:
        return False, "[FAIL] NOTICE 缺 Modified by dragon-engine 段"
    if "yjh051108" not in text:
        return False, "[FAIL] NOTICE 缺上游版权声明"
    return True, "[PASS] NOTICE 含 Modified/Adapted + 上游版权"


def check_04_router_modes() -> tuple[bool, str]:
    """4. 4-mode 路由常量定义"""
    if not ROUTER_PY.exists():
        return False, f"[FAIL] router.py 不存在: {ROUTER_PY}"
    text = ROUTER_PY.read_text(encoding="utf-8")
    modes = ["MODE_SPEC", "MODE_REACT", "MODE_MIXED", "MODE_WEAK"]
    missing = [m for m in modes if m not in text]
    if missing:
        return False, f"[FAIL] router.py 缺 mode 常量: {missing}"
    if "def classify" not in text:
        return False, "[FAIL] router.py 缺 classify 函数"
    if "def adapt" not in text:
        return False, "[FAIL] router.py 缺 adapt 函数"
    return True, "[PASS] 4-mode 路由常量 + classify/adapt 函数"


def check_05_dev_tools() -> tuple[bool, str]:
    """5. dev_* 工具接口完整"""
    if not DEV_TOOLS_PY.exists():
        return False, f"[FAIL] dev_tools.py 不存在: {DEV_TOOLS_PY}"
    text = DEV_TOOLS_PY.read_text(encoding="utf-8")
    tools = ["dev_router_status", "dev_router_mode", "dev_mode_subagent"]
    missing = [t for t in tools if f"def {t}" not in text]
    if missing:
        return False, f"[FAIL] dev_tools.py 缺工具函数: {missing}"
    return True, "[PASS] 3 个 dev_* 工具函数完整"


def check_06_upstream_keywords() -> tuple[bool, str]:
    """6. 上游关键词命中（spec/react/weak/mixed 全出现）"""
    text = SKILL_MD.read_text(encoding="utf-8")
    keywords = ["spec", "react", "mixed", "weak"]
    # 大小写不敏感
    text_lower = text.lower()
    missing = [k for k in keywords if k not in text_lower]
    if missing:
        return False, f"[FAIL] SKILL.md 缺关键词: {missing}"
    # 上游版本 + 协议引用
    if "v0.3.0" not in text and "MIT" not in text:
        return False, "[FAIL] SKILL.md 缺上游版本或协议引用"
    return True, "[PASS] 上游 4 模式关键词 + 版本/协议引用完整"


# ─── 主入口 ────────────────────────────────────────────────────────────────

CHECKS = [
    ("check_01_skill_md_exists", "1. SKILL.md + frontmatter"),
    ("check_02_mit_license", "2. LICENSE MIT"),
    ("check_03_modified_by_notice", "3. NOTICE 含 Modified 段"),
    ("check_04_router_modes", "4. router.py 4-mode 常量"),
    ("check_05_dev_tools", "5. dev_tools.py 3 工具"),
    ("check_06_upstream_keywords", "6. SKILL.md 关键词 + 协议"),
]


def run_all() -> dict:
    return {fn: {"label": lbl, **(lambda: (lambda ok, msg: {"pass": ok, "msg": msg})(*globals()[fn]()))()}
            for fn, lbl in CHECKS}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", help="单测名")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.check:
        fn = globals().get(args.check)
        if not fn:
            print(f"[FAIL] 未知检查: {args.check}", file=sys.stderr)
            return 1
        ok, msg = fn()
        print(msg)
        return 0 if ok else 1

    results = run_all()
    passed = sum(1 for r in results.values() if r["pass"])
    total = len(results)

    if args.json:
        print(json.dumps({"passed": passed, "total": total, "results": results}, ensure_ascii=False, indent=2))
    else:
        print("=" * 70)
        print("dsh-routing-suite-bridge Health Check · Stage 52")
        print("=" * 70)
        for info in results.values():
            print(f"  {info['msg']}")
        print("=" * 70)
        print(f"  PASSED: {passed} / {total}")
        print("=" * 70)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
