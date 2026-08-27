"""test_03_license_notice — LICENSE + NOTICE 双件套 + Apache-2.0

对应阶段 26 累计 PASS 第 3 项。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from check import check_03_license_notice_pair  # noqa: E402


def test_03_license_notice():
    ok, msg = check_03_license_notice_pair()
    assert ok, msg
    print(f"[PASS] {msg}")


if __name__ == "__main__":
    test_03_license_notice()
