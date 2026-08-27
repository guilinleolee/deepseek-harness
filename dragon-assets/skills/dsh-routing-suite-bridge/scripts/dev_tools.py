"""dev_tools.py · dsh-routing-suite-bridge dev_* 工具族 · V1.0

天龙自研模块 · MIT
借鉴 yjh051108/dsh-super-injector v0.3.3 的 3 个 dev_* 工具接口：
  - dev_router_status：查询当前路由状态
  - dev_router_mode：切换路由模式
  - dev_mode_subagent：下放任务给 sub-agent

接口语义与上游 dsh-super-injector v0.3.3 对齐（dev_* 工具族的 contract）。
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from threading import Lock
from typing import Any

from router import (
    RouteResult,
    VALID_MODES,
    MODE_SPEC,
    MODE_REACT,
    MODE_MIXED,
    MODE_WEAK,
    is_valid_mode,
)


TZ_CN = timezone(timedelta(hours=8))


@dataclass
class RouterState:
    """全局路由状态（runtime injector 维护）"""
    current_mode: str = MODE_REACT
    current_model: str = "unknown"
    history: list[dict] = field(default_factory=list)
    cache_hits: int = 0
    cache_misses: int = 0
    total_routes: int = 0
    locked_at: str = ""

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v not in (None, [], "", 0)}


# 全局 state（线程安全）
_state = RouterState()
_lock = Lock()


def dev_router_status() -> dict:
    """查询当前路由状态（dev_router_status）

    返回：当前 mode / model / 命中率 / 总路由数
    """
    with _lock:
        total = _state.total_routes
        hit_rate = (_state.cache_hits / total) if total > 0 else 0.0
        result = {
            "ok": True,
            "tool": "dev_router_status",
            "current_mode": _state.current_mode,
            "current_model": _state.current_model,
            "total_routes": total,
            "cache_hits": _state.cache_hits,
            "cache_misses": _state.cache_misses,
            "hit_rate": round(hit_rate, 4),
            "history_size": len(_state.history),
            "last_route_at": _state.locked_at,
        }
        return result


def dev_router_mode(mode: str, model: str | None = None) -> dict:
    """切换路由模式（dev_router_mode）

    输入：
      mode: spec / react / mixed / weak
      model: 可选，更新当前模型

    约束：
      - mixed 模式仅用于 trap detection，不推荐长期使用
      - 切换后 history 保留
    """
    if not is_valid_mode(mode):
        return {
            "ok": False,
            "tool": "dev_router_mode",
            "error": "INVALID_MODE",
            "valid_modes": sorted(VALID_MODES),
        }

    with _lock:
        old_mode = _state.current_mode
        _state.current_mode = mode
        if model:
            _state.current_model = model
        _state.history.append({
            "action": "mode_change",
            "from": old_mode,
            "to": mode,
            "model": model or _state.current_model,
            "at": datetime.now(TZ_CN).isoformat(),
        })
        _state.locked_at = datetime.now(TZ_CN).isoformat()
        result = {
            "ok": True,
            "tool": "dev_router_mode",
            "old_mode": old_mode,
            "new_mode": mode,
            "model": _state.current_model,
            "at": _state.locked_at,
            "warning": "mixed mode is for trap detection only" if mode == MODE_MIXED else None,
        }
    return result


def dev_mode_subagent(task: str, mode: str = "", preserve_persona: bool = True) -> dict:
    """下放任务给 sub-agent（dev_mode_subagent）

    输入：
      task: 任务描述
      mode: 指定的路由模式（空 = 用当前 mode）
      preserve_persona: 是否保留 persona 三锚（spec 模式专属）

    返回：sub-agent 配置（可被 DSH agent-teams 消费）
    """
    use_mode = mode or _state.current_mode
    if not is_valid_mode(use_mode):
        return {
            "ok": False,
            "tool": "dev_mode_subagent",
            "error": "INVALID_MODE",
            "valid_modes": sorted(VALID_MODES),
        }

    # persona 配置
    persona = []
    if use_mode == MODE_SPEC and preserve_persona:
        persona = ["review", "converge", "anti_drift"]  # 三锚
    elif use_mode == MODE_REACT:
        persona = ["execute", "iterate"]
    elif use_mode == MODE_WEAK:
        persona = ["neutral", "classify"]

    with _lock:
        _state.total_routes += 1
        _state.history.append({
            "action": "subagent_spawn",
            "mode": use_mode,
            "task_preview": task[:80],
            "at": datetime.now(TZ_CN).isoformat(),
        })

    return {
        "ok": True,
        "tool": "dev_mode_subagent",
        "mode": use_mode,
        "persona": persona,
        "task": task,
        "preserve_persona": preserve_persona and use_mode == MODE_SPEC,
        "sub_agent_id": f"sub-{_state.total_routes:04d}",
        "at": datetime.now(TZ_CN).isoformat(),
    }


def record_route(hit: bool) -> None:
    """内部：记录一次路由 + 缓存命中"""
    with _lock:
        _state.total_routes += 1
        if hit:
            _state.cache_hits += 1
        else:
            _state.cache_misses += 1


def reset_state() -> None:
    """测试用：重置 state"""
    global _state
    _state = RouterState()


# ─── 主入口 ────────────────────────────────────────────────────────────────

def main() -> int:
    """演示：3 个 dev_* 工具调用"""
    print("=" * 70)
    print("Stage 52 · dsh-routing-suite-bridge · dev_* 工具族演示")
    print("=" * 70)

    # 1. 状态查询
    r1 = dev_router_status()
    print(f"\n[1] dev_router_status:")
    print(f"  → mode={r1['current_mode']}  total={r1['total_routes']}  hit_rate={r1.get('hit_rate', 0)}")

    # 2. 切换模式
    r2 = dev_router_mode("spec", model="pro")
    print(f"\n[2] dev_router_mode: {r2['old_mode']} → {r2['new_mode']}  (model={r2['model']})")

    # 3. sub-agent 下放
    r3 = dev_mode_subagent("调研 2026 年 AI 编程工具趋势", mode="spec")
    print(f"\n[3] dev_mode_subagent:")
    print(f"  → sub_agent_id={r3['sub_agent_id']}  mode={r3['mode']}  persona={r3['persona']}")

    # 4. 状态查询（看更新）
    r4 = dev_router_status()
    print(f"\n[4] dev_router_status (after 3 calls):")
    print(f"  → mode={r4['current_mode']}  total={r4['total_routes']}  history={r4['history_size']}")

    print("\n" + "=" * 70)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
