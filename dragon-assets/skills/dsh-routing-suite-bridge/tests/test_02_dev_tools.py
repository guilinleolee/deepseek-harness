"""test_02_dev_tools · 3 个 dev_* 工具接口"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from dev_tools import (
    dev_router_status, dev_router_mode, dev_mode_subagent,
    reset_state, record_route,
    MODE_SPEC, MODE_REACT, MODE_MIXED, MODE_WEAK,
)


def test_02_dev_tools():
    reset_state()

    # 1. dev_router_status 初态
    r = dev_router_status()
    assert r["ok"]
    assert r["tool"] == "dev_router_status"
    assert r["current_mode"] == MODE_REACT  # 默认
    assert r["total_routes"] == 0
    assert r["hit_rate"] == 0.0
    print(f"[PASS] dev_router_status: 初态 current_mode={r['current_mode']}, total={r['total_routes']}")

    # 2. dev_router_mode 切换
    r = dev_router_mode("spec", model="pro")
    assert r["ok"]
    assert r["old_mode"] == MODE_REACT
    assert r["new_mode"] == MODE_SPEC
    assert r["model"] == "pro"
    print(f"[PASS] dev_router_mode: react → spec (model=pro)")

    # 3. 状态查询（应已更新）
    r = dev_router_status()
    assert r["current_mode"] == MODE_SPEC
    assert r["current_model"] == "pro"
    assert r["history_size"] == 1
    print(f"[PASS] dev_router_status: 切换后 current_mode=spec, history_size=1")

    # 4. dev_router_mode 错误模式
    r = dev_router_mode("invalid_mode")
    assert not r["ok"]
    assert r["error"] == "INVALID_MODE"
    assert "valid_modes" in r
    print(f"[PASS] dev_router_mode: 无效模式被拒绝 (valid_modes={r['valid_modes']})")

    # 5. dev_router_mode mixed 模式（警告）
    r = dev_router_mode(MODE_MIXED)
    assert r["ok"]
    assert r["warning"] is not None, f"[FAIL] mixed 应有警告: {r}"
    assert "trap" in r["warning"].lower() or "trap detection" in r["warning"]
    print(f"[PASS] dev_router_mode mixed: 警告 '{r['warning']}'")

    # 6. dev_mode_subagent spec + preserve_persona
    reset_state()
    r = dev_mode_subagent("调研 2026 AI 编程工具", mode=MODE_SPEC, preserve_persona=True)
    assert r["ok"]
    assert r["mode"] == MODE_SPEC
    assert r["preserve_persona"] is True
    assert "review" in r["persona"]
    assert "converge" in r["persona"]
    assert "anti_drift" in r["persona"]  # 三锚
    assert r["sub_agent_id"].startswith("sub-")
    print(f"[PASS] dev_mode_subagent spec: persona 三锚 = {r['persona']}")

    # 7. dev_mode_subagent react
    r = dev_mode_subagent("写代码", mode=MODE_REACT)
    assert r["ok"]
    assert r["persona"] == ["execute", "iterate"]
    print(f"[PASS] dev_mode_subagent react: persona = {r['persona']}")

    # 8. dev_mode_subagent weak
    r = dev_mode_subagent("查询天气", mode=MODE_WEAK)
    assert r["ok"]
    assert r["persona"] == ["neutral", "classify"]
    print(f"[PASS] dev_mode_subagent weak: persona = {r['persona']}")

    # 9. dev_mode_subagent 不带 mode → 用 current
    dev_router_mode(MODE_SPEC, model="pro")
    r = dev_mode_subagent("test")
    assert r["mode"] == MODE_SPEC
    print(f"[PASS] dev_mode_subagent (无 mode 参数) → 用 current_mode=spec")

    # 10. record_route + cache hit rate
    reset_state()
    record_route(True)
    record_route(True)
    record_route(False)
    r = dev_router_status()
    assert r["total_routes"] == 3
    assert r["cache_hits"] == 2
    assert r["cache_misses"] == 1
    assert abs(r["hit_rate"] - 2/3) < 0.01
    print(f"[PASS] record_route: hit_rate={r['hit_rate']:.4f} (2 hits / 3 total)")


if __name__ == "__main__":
    test_02_dev_tools()
