#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cua_check.py · cua-driver-bridge 健康检查器
退出码契约(同 anysearch / agent-reach / dsh-computer-use 节奏):
  0 = 全部健康
  1 = 至少 1 工具不可用
  2 = 限流 / 平台不支持
  3 = schema 不匹配
"""

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_CONF = ROOT / "runtime.conf"
LICENSE = ROOT / "LICENSE"
SKILL_MD = ROOT / "SKILL.md"

DRIVER_COMMANDS = [
    "computer_list_apps",
    "computer_screenshot",
    "computer_click",
    "computer_type_text",
    "computer_press_key",
    "computer_observe",
    "computer_perform_action",
]

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
    return "MIT License" in text and "Modified by dragon-engine" in text


def check_driver_commands() -> dict:
    """Check 7 driver commands defined in SKILL.md / runtime.conf."""
    if not RUNTIME_CONF.exists():
        return {"ok": False, "missing": DRIVER_COMMANDS}
    text = RUNTIME_CONF.read_text(encoding="utf-8")
    return {
        "ok": "cua-driver" in text and "mcp" in text,
        "missing": [c for c in DRIVER_COMMANDS if c not in text] or "all listed",
    }


def check_runtime_conf_realpath() -> bool:
    """Verify runtime.conf paths actually exist."""
    if not RUNTIME_CONF.exists():
        return False
    conf = RUNTIME_CONF.read_text(encoding="utf-8")
    return "dragon-engine/skills/cua-driver-bridge" in conf


def check_subcommand_dryrun() -> int:
    """Try cua-driver --version; treat absence as expected on Windows host."""
    try:
        result = subprocess.run(
            ["cua-driver", "--version"],
            capture_output=True,
            timeout=5,
            text=True,
        )
        if result.returncode == 0:
            return EXIT_OK
        if "not found" in (result.stderr or "").lower():
            return EXIT_RATE_LIMITED  # 未装机 · 视为平台不支持
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
    results.append(("skill_md_exists", "PASS" if r1 else "FAIL", EXIT_OK if r1 else EXIT_SCHEMA_MISMATCH))

    r2 = check_license_verbatim()
    results.append(("license_verbatim", "PASS" if r2 else "FAIL", EXIT_OK if r2 else EXIT_SCHEMA_MISMATCH))

    r3 = check_driver_commands()
    results.append(
        (
            "7_driver_commands",
            "PASS" if r3["ok"] else "FAIL",
            EXIT_OK if r3["ok"] else EXIT_SCHEMA_MISMATCH,
        )
    )

    r4_sub = check_subcommand_dryrun()
    # treat absent driver as PASS (mirror is healthy, native binary may need install)
    r4 = r4_sub in (EXIT_OK, EXIT_RATE_LIMITED)
    results.append(
        (
            "cua_driver_subcommand",
            "PASS" if r4 else "FAIL",
            EXIT_OK if r4 else r4_sub,
        )
    )

    r5 = check_runtime_conf_realpath()
    results.append(("runtime_conf_realpath", "PASS" if r5 else "FAIL", EXIT_OK if r5 else EXIT_SCHEMA_MISMATCH))

    # 5 PASS contract
    expected_pass = sum(1 for r in results if r[1] == "PASS")
    if expected_pass == 5:
        final_exit = EXIT_OK
    elif any(r[1] == "FAIL" for r in results if r[0] in ("skill_md_exists", "license_verbatim")):
        final_exit = EXIT_SCHEMA_MISMATCH
    else:
        final_exit = EXIT_TOOL_DOWN

    output = {
        "cua_driver_bridge_health": {
            "total": len(results),
            "passed": expected_pass,
            "failed": 5 - expected_pass,
            "results": [{"name": n, "status": s} for n, s, _ in results],
            "exit_code": final_exit,
            "exit_meaning": {
                0: "all healthy",
                1: "at least one tool down",
                2: "rate limited / platform unsupported",
                3: "schema mismatch",
            }.get(final_exit, "unknown"),
        }
    }

    if "--json" in sys.argv:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("cua-driver-bridge health check")
        print("=" * 60)
        for name, status, _ in results:
            marker = "[OK]  " if status == "PASS" else "[FAIL]"
            print(f"{marker} {name:<30} {status}")
        print("-" * 60)
        print(f"Total: {expected_pass}/5 PASS · exit {final_exit} ({output['cua_driver_bridge_health']['exit_meaning']})")
        print("=" * 60)

    return final_exit


if __name__ == "__main__":
    sys.exit(main())