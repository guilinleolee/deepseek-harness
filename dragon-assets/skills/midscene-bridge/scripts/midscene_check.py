#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
midscene_check.py · midscene-bridge 健康检查器
退出码契约:
  0 = 全部健康
  1 = 工具不可用
  2 = 限流 / 模型未配
  3 = schema 不匹配
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_CONF = ROOT / "runtime.conf"
LICENSE = ROOT / "LICENSE"
SKILL_MD = ROOT / "SKILL.md"

CORE_APIS = ["aiAct", "aiQuery", "aiAssert"]
PLATFORMS = ["web", "ios", "android", "harmonyos", "desktop"]
MODELS = ["qwen3.5-plus", "doubao-seed-2.1-pro", "glm-4.6v", "gemini-3.5-flash", "UI-TARS"]

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
    return "MIT License" in text and "Copyright (c) 2025 Midscene.js" in text and "Modified by dragon-engine" in text


def check_3_api_wrappers() -> bool:
    """Verify aiAct/aiQuery/aiAssert in SKILL.md and runtime.conf."""
    if not SKILL_MD.exists() or not RUNTIME_CONF.exists():
        return False
    skill_text = SKILL_MD.read_text(encoding="utf-8")
    conf_text = RUNTIME_CONF.read_text(encoding="utf-8")
    return all(api in skill_text and api in conf_text for api in CORE_APIS)


def check_subcommand_dryrun() -> int:
    """Try midscene --version; absence is expected on Windows host."""
    import subprocess
    try:
        result = subprocess.run(
            ["midscene", "--version"],
            capture_output=True,
            timeout=5,
            text=True,
        )
        if result.returncode == 0:
            return EXIT_OK
        return EXIT_TOOL_DOWN
    except FileNotFoundError:
        return EXIT_RATE_LIMITED
    except subprocess.TimeoutExpired:
        return EXIT_TOOL_DOWN
    except Exception:
        return EXIT_SCHEMA_MISMATCH


def main() -> int:
    results = []

    r1 = check_skill_md_exists()
    results.append(("skill_md_exists", "PASS" if r1 else "FAIL"))

    r2 = check_license_verbatim()
    results.append(("license_verbatim", "PASS" if r2 else "FAIL"))

    r3 = check_3_api_wrappers()
    results.append(("3_api_wrappers", "PASS" if r3 else "FAIL"))

    r4_sub = check_subcommand_dryrun()
    r4 = r4_sub in (EXIT_OK, EXIT_RATE_LIMITED)
    results.append(("midscene_subcommand", "PASS" if r4 else "FAIL"))

    expected_pass = sum(1 for _, s in results if s == "PASS")
    if expected_pass == 4:
        final_exit = EXIT_OK
    else:
        critical_fail = any(r[1] == "FAIL" for r in results if r[0] in ("skill_md_exists", "license_verbatim", "3_api_wrappers"))
        final_exit = EXIT_SCHEMA_MISMATCH if critical_fail else EXIT_TOOL_DOWN

    output = {
        "midscene_bridge_health": {
            "total": len(results),
            "passed": expected_pass,
            "failed": 4 - expected_pass,
            "results": [{"name": n, "status": s} for n, s in results],
            "exit_code": final_exit,
            "exit_meaning": {
                0: "all healthy",
                1: "tool down",
                2: "rate limited / model not configured",
                3: "schema mismatch",
            }.get(final_exit, "unknown"),
        }
    }

    if "--json" in sys.argv:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("midscene-bridge health check")
        print("=" * 60)
        for name, status in results:
            marker = "[OK]  " if status == "PASS" else "[FAIL]"
            print(f"{marker} {name:<30} {status}")
        print("-" * 60)
        print(f"Total: {expected_pass}/4 PASS · exit {final_exit} ({output['midscene_bridge_health']['exit_meaning']})")
        print("=" * 60)

    return final_exit


if __name__ == "__main__":
    sys.exit(main())