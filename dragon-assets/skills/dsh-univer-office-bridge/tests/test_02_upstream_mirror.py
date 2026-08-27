"""test_02_upstream_mirror — 上游 8 个 SKILL.md 镜像齐全

对应阶段 26 累计 PASS 第 2 项。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from check import check_02_upstream_skill_mirrors  # noqa: E402


def test_02_upstream_mirror():
    ok, msg = check_02_upstream_skill_mirrors()
    assert ok, msg
    print(f"[PASS] {msg}")


if __name__ == "__main__":
    test_02_upstream_mirror()
