"""test_05_triggers_coverage — 触发词 ≥30 + 5 类 Unit 路由齐全

对应阶段 26 累计 PASS 第 5 项。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from check import check_05_triggers_coverage  # noqa: E402


def test_05_triggers_coverage():
    ok, msg = check_05_triggers_coverage()
    assert ok, msg
    print(f"[PASS] {msg}")


if __name__ == "__main__":
    test_05_triggers_coverage()
