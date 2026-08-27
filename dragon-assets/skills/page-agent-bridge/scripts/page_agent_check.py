#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
page_agent_check.py · page-agent-bridge 健康检查器
退出码契约:
  0 = 全部健康
  1 = 工具不可用
  2 = 限流 / 平台不支持
  3 = schema 不匹配
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_CONF = ROOT / "runtime.conf"
LICENSE = ROOT / "LICENSE"
SKILL_MD = ROOT / "SKILL.md"

EXIT_OK = 0
EXIT_TOOL_DOWN = 1
EXIT_RATE_LIMITED = 2
EXIT_SCHEMA_MISMATCH = 3


def check_skill_md_exists() -> bool:
    return SKILL_MD.exists() and SKILL_MD.stat().st_size > 1000


def check_license_verbatim() -> bool:
    if not LICENSE.exists():
        return False
    text = LICENSE.read_text(encoding="utf-8")
    return (
        "MIT License" in text
        and "Copyright (c) 2025 Alibaba" in text
        and "Modified by dragon-engine" in text
        and "browser-use" in text  # upstream attribution
    )


def check_cdn_runtime_paths() -> bool:
    if not RUNTIME_CONF.exists():
        return False
    text = RUNTIME_CONF.read_text(encoding="utf-8")
    return (
        "cdn.jsdelivr.net" in text
        and "page-agent@1.12.2" in text
        and "qwen3.5-plus" in text
        and "dragon-engine/skills/page-agent-bridge" in text
    )


def check_no_demo_cdn_bundled() -> bool:
    """Verify mirror does NOT bundle demo CDN (per user decision 2026-08-26)."""
    if not RUNTIME_CONF.exists():
        return False
    text = RUNTIME_CONF.read_text(encoding="utf-8")
    return "demo" not in text or "does NOT bundle demo" in text


def main() -> int:
    results = []

    r1 = check_skill_md_exists()
    results.append(("skill_md_exists", "PASS" if r1 else "FAIL"))

    r2 = check_license_verbatim()
    results.append(("license_verbatim", "PASS" if r2 else "FAIL"))

    r3 = check_cdn_runtime_paths()
    results.append(("cdn_runtime_paths", "PASS" if r3 else "FAIL"))

    expected_pass = sum(1 for _, s in results if s == "PASS")
    if expected_pass == 3:
        final_exit = EXIT_OK
    else:
        critical_fail = any(r[1] == "FAIL" for r in results if r[0] in ("skill_md_exists", "license_verbatim"))
        final_exit = EXIT_SCHEMA_MISMATCH if critical_fail else EXIT_TOOL_DOWN

    output = {
        "page_agent_bridge_health": {
            "total": len(results),
            "passed": expected_pass,
            "failed": 3 - expected_pass,
            "results": [{"name": n, "status": s} for n, s in results],
            "exit_code": final_exit,
            "exit_meaning": {
                0: "all healthy",
                1: "tool down",
                2: "rate limited / platform unsupported",
                3: "schema mismatch",
            }.get(final_exit, "unknown"),
        }
    }

    if "--json" in sys.argv:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("page-agent-bridge health check")
        print("=" * 60)
        for name, status in results:
            marker = "[OK]  " if status == "PASS" else "[FAIL]"
            print(f"{marker} {name:<30} {status}")
        print("-" * 60)
        print(f"Total: {expected_pass}/3 PASS · exit {final_exit} ({output['page_agent_bridge_health']['exit_meaning']})")
        print("=" * 60)

    return final_exit


if __name__ == "__main__":
    sys.exit(main())