"""test_47_14 · univer_* 13 工具 一次性 e2e"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from e2e_all_tools import full_13_tool_e2e, test_47_14_all_13_tools


def test_47_14_e2e():
    # 完整 13 工具链路
    r = full_13_tool_e2e()
    assert r["ok"], f"[FAIL] 端到端失败: {r}"
    assert r["trace_count"] >= 14
    failed = [(name, ok) for name, ok in r["trace"] if not ok]
    assert not failed, f"[FAIL] trace 失败: {failed}"
    print(f"\n[PASS] 47.14 e2e: {r['trace_count']} 步全成功 (13 tools + worktree.ready)")


if __name__ == "__main__":
    test_47_14_e2e()
