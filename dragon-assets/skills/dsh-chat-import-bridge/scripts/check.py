"""check.py · dsh-chat-import-bridge 健康检查 · V1.0

8 项 PASS：
  1. SKILL.md 存在 + frontmatter
  2. LICENSE (MIT)
  3. NOTICE 含 Modified 段
  4. 18 format 路由完整
  5. detect_format 函数
  6. bundle 双指纹机制
  7. 5 大核心类（Session/Message/Bundle/Import/Export）
  8. 上游关键词命中
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
SCRIPT = SKILL_ROOT / "scripts" / "chat_import.py"

REQUIRED_FORMATS = {
    "claude", "codex", "chatgpt", "cursor", "gemini", "reasonix",
    "opencode", "mimo", "zcode", "grok", "openclaw", "pi",
    "hermes", "kimi", "qoder", "workbuddy",
    "dsh", "local-jsonl",
}


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
    if "Copyright (c) 2026 Nwflower" not in text:
        return False, "[FAIL] LICENSE 缺上游版权"
    return True, "[PASS] LICENSE (MIT) + 上游版权完整"


def check_03_modified_by_notice() -> tuple[bool, str]:
    if not NOTICE.exists():
        return False, "[FAIL] NOTICE 不存在"
    text = NOTICE.read_text(encoding="utf-8")
    if "Modified by dragon-engine" not in text and "Adapted by dragon-engine" not in text:
        return False, "[FAIL] NOTICE 缺 Modified 段"
    if "Nwflower" not in text:
        return False, "[FAIL] NOTICE 缺上游版权声明"
    return True, "[PASS] NOTICE 含 Modified 段 + 上游版权"


def check_04_format_router() -> tuple[bool, str]:
    if not SCRIPT.exists():
        return False, f"[FAIL] chat_import.py 不存在: {SCRIPT}"
    text = SCRIPT.read_text(encoding="utf-8")
    missing = [f for f in REQUIRED_FORMATS if f'"{f}"' not in text]
    if missing:
        return False, f"[FAIL] 缺 format 路由: {missing}"
    return True, f"[PASS] 18 format 路由完整"


def check_05_detect_format() -> tuple[bool, str]:
    text = SCRIPT.read_text(encoding="utf-8")
    if "def detect_format" not in text:
        return False, "[FAIL] 缺 detect_format 函数"
    if "FORMAT_SIGNATURES" not in text:
        return False, "[FAIL] 缺 FORMAT_SIGNATURES 字典"
    return True, "[PASS] detect_format + FORMAT_SIGNATURES 完整"


def check_06_bundle_fingerprint() -> tuple[bool, str]:
    text = SCRIPT.read_text(encoding="utf-8")
    if "ChatBundle" not in text:
        return False, "[FAIL] 缺 ChatBundle 类"
    if "fingerprint_source" not in text or "fingerprint_content" not in text:
        return False, "[FAIL] 缺 SHA-256 双指纹"
    if "def export_bundle" not in text or "def restore_bundle" not in text:
        return False, "[FAIL] 缺 export_bundle / restore_bundle"
    return True, "[PASS] Bundle SHA-256 双指纹机制完整"


def check_07_core_classes() -> tuple[bool, str]:
    text = SCRIPT.read_text(encoding="utf-8")
    required = ["ChatMessage", "ChatSession", "ChatBundle", "import_chat", "export_chat", "scan_discover"]
    missing = [r for r in required if r not in text]
    if missing:
        return False, f"[FAIL] 缺核心: {missing}"
    return True, f"[PASS] 6 个核心 API 完整"


def check_08_upstream_keywords() -> tuple[bool, str]:
    text = SKILL_MD.read_text(encoding="utf-8")
    keywords = ["import_chat", "scan_discover", "export_bundle", "restore_bundle",
                "sync_to_claude", "Claude Code", "Codex", "ChatGPT", "DSH"]
    text_lower = text.lower()
    missing = [k for k in keywords if k.lower() not in text_lower]
    if len(missing) > 3:
        return False, f"[FAIL] SKILL.md 缺关键词: {missing[:5]}"
    return True, "[PASS] 上游 9 关键词覆盖 ≥ 6"


CHECKS = [
    ("check_01_skill_md", "1. SKILL.md + frontmatter"),
    ("check_02_mit_license", "2. LICENSE MIT"),
    ("check_03_modified_by_notice", "3. NOTICE 含 Modified"),
    ("check_04_format_router", "4. 18 format 路由"),
    ("check_05_detect_format", "5. detect_format"),
    ("check_06_bundle_fingerprint", "6. Bundle 双指纹"),
    ("check_07_core_classes", "7. 6 核心 API"),
    ("check_08_upstream_keywords", "8. 上游 9 关键词"),
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

    results = {fn: {"label": lbl, **({"pass": ok, "msg": msg} if (ok := globals()[fn]() and (msg := globals()[fn]()[1])) else {"pass": False, "msg": "fail"})}
                for fn, lbl in CHECKS}
    # 上面 lambda 太复杂，简化：
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
        print("dsh-chat-import-bridge Health Check · Stage 55")
        print("=" * 70)
        for info in results.values():
            print(f"  {info['msg']}")
        print("=" * 70)
        print(f"  PASSED: {passed} / {total}")
        print("=" * 70)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
