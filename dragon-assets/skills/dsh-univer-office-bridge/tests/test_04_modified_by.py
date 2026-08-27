"""test_04_modified_by — NOTICE 含 'Modified by dragon-engine' + 上游版权 + 商标

对应阶段 26 累计 PASS 第 4 项。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from check import check_04_modified_by_notice  # noqa: E402


def test_04_modified_by():
    ok, msg = check_04_modified_by_notice()
    assert ok, msg
    print(f"[PASS] {msg}")


if __name__ == "__main__":
    test_04_modified_by()
