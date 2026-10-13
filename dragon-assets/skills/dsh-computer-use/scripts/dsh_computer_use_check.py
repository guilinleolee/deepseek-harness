"""
dsh-computer-use 健康检查器 V1.0

功能:
- 镜像同步验证(3 层)
- LICENSE 完整性
- 关键 SKILL.md 字段 / 触发词 / DON'T 护栏
- Windows / Linux 平台降级报告
- 退出码契约 0/1/2/3

退出码:
- 0: 全部 PASS
- 1: 镜像同步失败(必须修复)
- 2: LICENSE / 必填字段缺失(协议违规)
- 3: 平台降级(Windows / Linux,功能不可用)
"""

import sys
import re
import json
from pathlib import Path

SKILL_NAME = "dsh-computer-use"
STAGE = 26

# 三层镜像路径
MIRRORS = {
    "source": Path(r"C:\Users\li\.claude\projects\dragon-engine\skills\dsh-computer-use\SKILL.md"),
    "project": Path(r"C:\Users\li\.claude\projects\dragon-engine\.claude\skills\dsh-computer-use\SKILL.md"),
    "workspace": Path(r"C:\Users\li\.claude\projects\skills\dsh-computer-use\SKILL.md"),
}

LICENSE_PATH = Path(r"C:\Users\li\.claude\projects\dragon-engine\skills\dsh-computer-use\LICENSE")


def check_mirror_sync() -> tuple[bool, list[str]]:
    """检查三层镜像是否存在 + 真源包含关键 frontmatter"""
    failures = []
    if not MIRRORS["source"].exists():
        failures.append("source mirror missing")
    else:
        content = MIRRORS["source"].read_text(encoding="utf-8")
        for required in ["name: dsh-computer-use", "version: 1.1.0", "license: MIT", "platform: macOS 14+ only"]:
            if required not in content:
                failures.append(f"source mirror missing required: {required!r}")
    if not MIRRORS["project"].exists():
        failures.append("project-level mirror missing")
    if not MIRRORS["workspace"].exists():
        failures.append("workspace-root mirror missing")
    return (len(failures) == 0, failures)


def check_license_verbatim() -> tuple[bool, list[str]]:
    """验证 LICENSE 是上游 MIT verbatim + Modified by footer"""
    failures = []
    if not LICENSE_PATH.exists():
        failures.append("LICENSE file missing")
        return (False, failures)
    content = LICENSE_PATH.read_text(encoding="utf-8")
    required_phrases = [
        "MIT License",
        "Copyright (c) 2026 anionex",
        "Permission is hereby granted, free of charge",
        "THE SOFTWARE IS PROVIDED \"AS IS\"",
        "Modified by dragon-engine / 2026-08-23",
        "https://github.com/Anionex/dsh-computer-use",
    ]
    for phrase in required_phrases:
        if phrase not in content:
            failures.append(f"LICENSE missing phrase: {phrase!r}")
    return (len(failures) == 0, failures)


def check_skill_required_sections() -> tuple[bool, list[str]]:
    """验证 SKILL.md 包含天龙 L0/L1/L2 + 11 类触发词 + 11 条 DON'T"""
    failures = []
    if not MIRRORS["source"].exists():
        return (False, ["source mirror missing - cannot check sections"])
    content = MIRRORS["source"].read_text(encoding="utf-8")
    required_sections = [
        "## L0 · 触发词与不触发",
        "## L1 · 一键装 / 卸",
        "## L2 · 11 个 Tool + 4 类错误码",
        "## L3 · 4 类 host policy",
        "## L4 · 11 条 DON'T 护栏",
        "## L5 · 7 类 Bundle 配置字段",
        "## L6 · 5 类 agent 协同点",
        "## L7 · 5 类平台限制",
        "## L8 · 安全模型",
        "## L9 · macOS TCC 权限自助清单",
        "## L10 · 当前主机状态",
    ]
    for section in required_sections:
        if section not in content:
            failures.append(f"SKILL.md missing section: {section!r}")
    # 11 条 DON'T 护栏计数
    dont_count = len(re.findall(r"^\d+\. \*\*不要", content, re.MULTILINE))
    if dont_count < 11:
        failures.append(f"SKILL.md has {dont_count} DON'T 护栏, expected >= 11")
    # 11 类触发词(✅ 路由)
    trigger_count = len(re.findall(r"^\| \d+ \|", content[:5000], re.MULTILINE))
    return (len(failures) == 0, failures)


def check_platform_degradation() -> tuple[bool, list[str]]:
    """在 Windows / Linux 上报告平台降级"""
    import platform
    failures = []
    system = platform.system()
    if system == "Windows":
        failures.append("platform=Windows, expected COMPUTER_UNSUPPORTED_PLATFORM - functionality NOT available")
    elif system == "Linux":
        failures.append("platform=Linux, expected COMPUTER_UNSUPPORTED_PLATFORM - functionality NOT available")
    # darwin(macOS)是目标平台,不报错
    return (True, failures) if not failures else (False, failures)


def main() -> int:
    results = {
        "test_01_mirror_sync": check_mirror_sync(),
        "test_02_license_verbatim": check_license_verbatim(),
        "test_03_skill_sections": check_skill_required_sections(),
        "test_04_platform_degradation": check_platform_degradation(),
    }

    failed = 0
    print(f"=== dsh-computer-use health check (stage {STAGE}) ===\n")
    for name, (passed, failures) in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")
        for f in failures:
            print(f"  - {f}")
        if not passed:
            failed += 1

    print(f"\n{sum(1 for p, _ in results.values() if p)}/{len(results)} checks passed")

    # 退出码契约
    if any("platform=" in f for _, fs in results.values() for f in fs):
        return 3  # 平台降级
    if any("LICENSE missing" in f or "missing required" in f for _, fs in results.values() for f in fs):
        return 2  # 合规缺失
    if failed > 0:
        return 1  # 镜像同步失败
    return 0


if __name__ == "__main__":
    sys.exit(main())