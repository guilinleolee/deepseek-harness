"""test_01_skill_md_exists — SKILL.md 存在 + YAML frontmatter 完整

对应阶段 26 累计 PASS 第 1 项。
"""
import sys
from pathlib import Path

# 把 scripts/ 加入 path 便于直接 import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from check import check_01_skill_md_exists  # noqa: E402


def test_01_skill_md_exists():
    ok, msg = check_01_skill_md_exists()
    assert ok, msg
    print(f"[PASS] {msg}")


if __name__ == "__main__":
    test_01_skill_md_exists()
