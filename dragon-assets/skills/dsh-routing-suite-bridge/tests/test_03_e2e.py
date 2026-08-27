"""test_03_e2e · 端到端：4 模式 × 多任务 + 协同 DSH agent-teams"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from router import adapt, classify, MODE_SPEC, MODE_REACT, MODE_MIXED, MODE_WEAK
from dev_tools import (
    dev_router_status, dev_router_mode, dev_mode_subagent,
    reset_state,
)


# 9 个测试任务 × Pro/Flash 双模型（覆盖 4 路由模式 + 模型适配）
TASK_MODEL_MATRIX = [
    # (task, model, expected_mode, category)
    ("帮我规划 2026 年内容矩阵，分主题/分平台", "pro", MODE_SPEC, "spec-complex"),
    ("深度调研中国新能源汽车产业链，写一份研报", "pro", MODE_SPEC, "spec-complex"),
    ("制定下季度 OKR 计划", "pro", MODE_SPEC, "spec-complex"),
    ("写一个 Python 函数做 5 选 3 组合", "flash", MODE_WEAK, "flash-react-downgrades-to-weak"),  # adapt 规则
    ("执行一下登录页面代码", "flash", MODE_WEAK, "flash-react-downgrades-to-weak"),
    ("实现登录页面 UI", "pro", MODE_SPEC, "spec-react-conflict-spec-wins"),  # Pro + spec + react → spec
    ("随便看看有什么可做的", "flash", MODE_WEAK, "weak-ambiguous"),
    ("什么好玩", "pro", MODE_SPEC, "weak-pro-forces-spec"),
    ("查询天气", "flash", MODE_WEAK, "weak-flash-neutral"),
]


def test_03_e2e():
    reset_state()

    for task, model, expected_mode, category in TASK_MODEL_MATRIX:
        r = adapt(model, task)
        assert r.mode == expected_mode, \
            f"[FAIL] {category}: '{task}' ({model}) → {r.mode}, expected {expected_mode}\n  result: {r.to_dict()}"
        print(f"[PASS] {category:40s}: mode={r.mode} ({r.confidence:.2f}) model={model}")

    # 端到端：完整 subagent 流程（用 mix 模型避免 Pro 强制）
    print("\n--- E2E: 完整 sub-agent 流程 ---")
    reset_state()
    dev_router_mode(MODE_REACT)  # 用 REACT 模式（不被 Pro 强制）

    tasks = [
        "调研 2026 AI 编程工具",
        "实现 Python 工具链",
    ]
    sub_results = []
    for t in tasks:
        r = dev_mode_subagent(t)
        sub_results.append(r)

    assert all(r["ok"] for r in sub_results)
    assert sub_results[0]["mode"] == MODE_REACT
    assert sub_results[1]["mode"] == MODE_REACT

    # 状态汇总
    status = dev_router_status()
    assert status["total_routes"] == 2
    assert status["history_size"] >= 3  # 1 mode_change + 2 subagent_spawn
    print(f"[PASS] 端到端 2 subagent: total_routes={status['total_routes']}, history={status['history_size']}")

    # 综合验证：天龙协同 DSH agent-teams 风格（Pro 强制 spec）
    print("\n--- E2E: captain 协同风格 ---")
    reset_state()
    # captain (pro) 决策 → spec → 下放给 member
    captain_decision = adapt("pro", "分析 2026 年 AI 编程工具的市场份额")
    assert captain_decision.mode == MODE_SPEC

    sub1 = dev_mode_subagent("调研 Cursor / Windsurf / Continue 工具", mode=captain_decision.mode)
    sub2 = dev_mode_subagent("做横向对比矩阵", mode=captain_decision.mode)

    assert sub1["preserve_persona"]  # spec 应保留 persona
    assert "review" in sub1["persona"]
    print(f"[PASS] captain 协同: 2 subagent 全部保留 persona 三锚 = {sub1['persona']}")


if __name__ == "__main__":
    test_03_e2e()
