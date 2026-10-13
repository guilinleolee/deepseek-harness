"""
dsh-computer-use 集成测试 V1.1.0 (阶段 42.3 升级)

5 PASS 用例:
- test_01_mirror_sync: 3 层镜像存在 + frontmatter 完整 (version: 1.1.0)
- test_02_license_verbatim: MIT verbatim + Modified by footer
- test_03_skill_sections: L0/L1/L2...L12 完整 + 11 类触发词 + 11 条 DON'T
- test_04_platform_degradation: Windows / Linux 优雅降级报告
- test_05_npm_package_name: 包名是 @anionex/dsh-computer-use(旧名应被禁用)

阶段 42.3 升级新增测试 (V1.1.0):
- test_06_ecosystem_comparison: 3 个新增 references 文件存在
- test_07_L11_L12_sections: SKILL.md L11/L12 章节存在
"""

import sys
import re
import platform
from pathlib import Path

# 复用 scripts/dsh_computer_use_check.py
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from dsh_computer_use_check import (
    check_mirror_sync,
    check_license_verbatim,
    check_skill_required_sections,
    check_platform_degradation,
    MIRRORS,
    LICENSE_PATH,
)


def test_01_mirror_sync():
    """三层镜像存在 + 真源包含关键 frontmatter 字段"""
    passed, failures = check_mirror_sync()
    assert passed, f"Mirror sync failed: {failures}"


def test_02_license_verbatim():
    """LICENSE 是上游 MIT verbatim + Modified by dragon-engine footer"""
    passed, failures = check_license_verbatim()
    assert passed, f"LICENSE check failed: {failures}"


def test_03_skill_sections():
    """SKILL.md 包含天龙 L0...L10 + 11 类触发词 + 11 条 DON'T"""
    passed, failures = check_skill_required_sections()
    assert passed, f"SKILL.md sections check failed: {failures}"


def test_04_platform_degradation():
    """在 Windows / Linux 上报告平台降级(应失败,提示降级)"""
    system = platform.system()
    if system in ("Windows", "Linux"):
        passed, failures = check_platform_degradation()
        # Windows / Linux 上应返回 (False, [...platform info...])
        assert not passed, f"Platform degradation should be reported on {system}"
        assert any("platform=" in f for f in failures), "Should mention platform in failure"
    else:
        # macOS 上不报错(本测试 pass)
        assert True


def test_05_npm_package_name():
    """SKILL.md frontmatter 记录正确包名 + README 不引用旧名"""
    content = MIRRORS["source"].read_text(encoding="utf-8")
    # frontmatter 应该是 @anionex/dsh-computer-use
    assert 'npm_package: "@anionex/dsh-computer-use"' in content, "frontmatter npm_package should be @anionex/dsh-computer-use"
    # 旧名 @dsh-external/dsh-computer-use 只在注释禁用提示中允许出现
    # 不能作为 install 命令使用
    bad_pattern = re.search(r"dsh plugin.*@dsh-external/dsh-computer-use", content)
    assert not bad_pattern, "Should not use old package name @dsh-external/dsh-computer-use as install command"


def test_06_ecosystem_comparison(V1_1_0_NEW=True):
    """V1.1.0 阶段 42.3 升级新增:3 个新 references 文件存在"""
    base = MIRRORS["source"].parent
    new_files = [
        base / "references" / "ecosystem-comparison.md",
        base / "references" / "cross-platform-decision-matrix.md",
        base / "references" / "tianlong-ecosystem-fit.md",
        base / "docs" / "announce-stage-42-3-upgrade.md",
    ]
    missing = [str(f.relative_to(base)) for f in new_files if not f.exists()]
    assert not missing, f"V1.1.0 新增文件缺失: {missing}"


def test_07_L11_L12_sections(V1_1_0_NEW=True):
    """V1.1.0 阶段 42.3 升级新增:SKILL.md L11/L12 章节存在"""
    content = MIRRORS["source"].read_text(encoding="utf-8")
    required_sections = [
        "## L11 · 生态位对比",
        "## L12 · 升级路线图",
    ]
    missing = [s for s in required_sections if s not in content]
    assert not missing, f"V1.1.0 升级 SKILL.md 缺失章节: {missing}"


def main():
    tests = [
        test_01_mirror_sync,
        test_02_license_verbatim,
        test_03_skill_sections,
        test_04_platform_degradation,
        test_05_npm_package_name,
        test_06_ecosystem_comparison,
        test_07_L11_L12_sections,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"[PASS] {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(main())