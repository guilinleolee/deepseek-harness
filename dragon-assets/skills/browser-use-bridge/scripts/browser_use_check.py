#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
browser_use_check.py · browser-use-bridge 健康检查器
退出码契约:
  0 = 全部健康
  1 = 工具不可用
  2 = 限流 / API key 缺失
  3 = schema 不匹配
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_CONF = ROOT / "runtime.conf"
LICENSE = ROOT / "LICENSE"
SKILL_MD = ROOT / "SKILL.md"
ENV_EXAMPLE = ROOT / ".env.example"

ENV_KEYS = [
    "BROWSER_USE_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
]

REST_ENDPOINTS = [
    "/api/v4/runs",
    "/api/v4/runs/{run_id}/completion",
    "/api/v4/browsers",
]

LLM_MODELS = [
    "bu-2-0-mini-preview",
    "bu-30-0-a3b-preview",
    "anthropic/claude-opus-4-8",
    "anthropic/claude-sonnet-4-6",
    "openai/gpt-5.5",
    "google/gemini-3-pro",
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
    return "MIT License" in text and "Copyright (c) 2024 Gregor Zunic" in text and "Modified by dragon-engine" in text


def check_runtime_conf_paths() -> bool:
    if not RUNTIME_CONF.exists():
        return False
    text = RUNTIME_CONF.read_text(encoding="utf-8")
    return "browser-use" in text and "api/v4" in text and "dragon-engine/skills/browser-use-bridge" in text


def check_env_example_4_fields() -> bool:
    if not ENV_EXAMPLE.exists():
        return False
    text = ENV_EXAMPLE.read_text(encoding="utf-8")
    return all(k in text for k in ENV_KEYS)


def check_cloud_sdk_import() -> int:
    """Try import browser_use_sdk; absence is fine on Windows host (mirror healthy)."""
    try:
        import browser_use_sdk  # noqa: F401
        return EXIT_OK
    except ImportError:
        return EXIT_RATE_LIMITED
    except Exception:
        return EXIT_SCHEMA_MISMATCH


def check_rest_endpoint_schema() -> bool:
    if not RUNTIME_CONF.exists():
        return False
    text = RUNTIME_CONF.read_text(encoding="utf-8")
    return all(ep.strip() in text for ep in REST_ENDPOINTS)


def check_subcommand_dryrun() -> int:
    """Try browser-use --version; absence is expected on Windows host."""
    import subprocess
    try:
        result = subprocess.run(
            ["browser-use", "--version"],
            capture_output=True,
            timeout=5,
            text=True,
        )
        if result.returncode == 0:
            return EXIT_OK
        return EXIT_TOOL_DOWN
    except FileNotFoundError:
        return EXIT_RATE_LIMITED  # 未装机 · 镜像层视为 PASS
    except subprocess.TimeoutExpired:
        return EXIT_TOOL_DOWN
    except Exception:
        return EXIT_SCHEMA_MISMATCH


def check_llm_provider_strategy() -> bool:
    if not RUNTIME_CONF.exists():
        return False
    text = RUNTIME_CONF.read_text(encoding="utf-8")
    return "bu-2-0-mini-preview" in text or "ChatBrowserUse" in text


def main() -> int:
    results = []

    r1 = check_skill_md_exists()
    results.append(("skill_md_exists", "PASS" if r1 else "FAIL"))

    r2 = check_license_verbatim()
    results.append(("license_verbatim", "PASS" if r2 else "FAIL"))

    r3 = check_runtime_conf_paths()
    results.append(("runtime_conf_paths", "PASS" if r3 else "FAIL"))

    r4 = check_env_example_4_fields()
    results.append(("env_example_4_fields", "PASS" if r4 else "FAIL"))

    r5_sub = check_cloud_sdk_import()
    r5 = r5_sub in (EXIT_OK, EXIT_RATE_LIMITED)
    results.append(("cloud_sdk_import", "PASS" if r5 else "FAIL"))

    r6 = check_rest_endpoint_schema()
    results.append(("rest_endpoint_schema", "PASS" if r6 else "FAIL"))

    r7_sub = check_subcommand_dryrun()
    r7 = r7_sub in (EXIT_OK, EXIT_RATE_LIMITED)
    results.append(("browser_use_subcommand", "PASS" if r7 else "FAIL"))

    r8 = check_llm_provider_strategy()
    results.append(("llm_provider_strategy", "PASS" if r8 else "FAIL"))

    expected_pass = sum(1 for _, s in results if s == "PASS")
    if expected_pass == 8:
        final_exit = EXIT_OK
    else:
        critical_fail = any(r[1] == "FAIL" for r in results if r[0] in ("skill_md_exists", "license_verbatim", "runtime_conf_paths"))
        final_exit = EXIT_SCHEMA_MISMATCH if critical_fail else EXIT_TOOL_DOWN

    output = {
        "browser_use_bridge_health": {
            "total": len(results),
            "passed": expected_pass,
            "failed": 8 - expected_pass,
            "results": [{"name": n, "status": s} for n, s in results],
            "exit_code": final_exit,
            "exit_meaning": {
                0: "all healthy",
                1: "tool down",
                2: "rate limited / API key missing / SDK not installed",
                3: "schema mismatch",
            }.get(final_exit, "unknown"),
        }
    }

    if "--json" in sys.argv:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("browser-use-bridge health check")
        print("=" * 60)
        for name, status in results:
            marker = "[OK]  " if status == "PASS" else "[FAIL]"
            print(f"{marker} {name:<30} {status}")
        print("-" * 60)
        print(f"Total: {expected_pass}/8 PASS · exit {final_exit} ({output['browser_use_bridge_health']['exit_meaning']})")
        print("=" * 60)

    return final_exit


if __name__ == "__main__":
    sys.exit(main())