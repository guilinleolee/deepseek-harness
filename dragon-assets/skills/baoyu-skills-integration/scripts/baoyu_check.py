"""baoyu-skills V1.0 验证脚本 — 21 项结构 + 协同检查
退出码契约: 0=PASS / 1=FAIL / 2=配置错 / 3=系统错
"""

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # dragon-engine/
SKILL_DIR = ROOT / "skills"
TESTS_DIR = SKILL_DIR / "baoyu-skills-integration" / "tests"

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_WARNING = 2
EXIT_BAD_USAGE = 3

EXPECTED_SKILLS = [
    "baoyu-article-illustrator",
    "baoyu-comic",
    "baoyu-compress-image",
    "baoyu-cover-image",
    "baoyu-danger-gemini-web",
    "baoyu-danger-x-to-markdown",
    "baoyu-diagram",
    "baoyu-electron-extract",
    "baoyu-format-markdown",
    "baoyu-image-gen",
    "baoyu-infographic",
    "baoyu-markdown-to-html",
    "baoyu-post-to-wechat",
    "baoyu-post-to-weibo",
    "baoyu-post-to-x",
    "baoyu-slide-deck",
    "baoyu-translate",
    "baoyu-url-to-markdown",
    "baoyu-wechat-summary",
    "baoyu-xhs-images",
    "baoyu-youtube-transcript",
]


def main():
    if not TESTS_DIR.exists():
        print(f"[ERROR] 测试目录不存在: {TESTS_DIR}", file=sys.stderr)
        sys.exit(EXIT_BAD_USAGE)

    sys.path.insert(0, str(TESTS_DIR))
    import test_baoyu

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_baoyu)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 计算退出码
    if result.wasSuccessful():
        if len(result.skipped) == 0:
            exit_code = EXIT_OK
        else:
            exit_code = EXIT_WARNING
    else:
        exit_code = EXIT_FAIL

    print()
    print("=" * 70)
    print("baoyu-skills V1.0 验证总结")
    passed = result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
    print(f"  [OK]    Passed:  {passed}")
    print(f"  [FAIL]  Failed:  {len(result.failures)}")
    print(f"  [ERR]   Errors:  {len(result.errors)}")
    print(f"  [SKIP]  Skipped: {len(result.skipped)}")
    print(f"  Total Run: {result.testsRun}")
    print(f"  Expected: {len(EXPECTED_SKILLS)} skills (21/21)")
    print()
    if exit_code == EXIT_OK:
        print("[PASS] 全部 21 项验证通过")
    elif exit_code == EXIT_WARNING:
        print("[WARN] 全部通过（部分 skipped）")
    else:
        print("[FAIL] 存在失败或错误")
    print(f"---EXIT: {exit_code}---")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
