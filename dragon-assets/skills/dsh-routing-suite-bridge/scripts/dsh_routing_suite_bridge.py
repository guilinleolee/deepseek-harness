"""
dsh-routing-suite-bridge V1.0 · Stage 51.1 借鉴档 · yjh051108/dsh-routing-suite MIT 借鉴

================================================================================
  Stage 51.1 · 2026-08-26

设计：
  - 借鉴档模式（与 stage 41/45/46/48/49.1/49.2/49.4/50.1/50.2 同）
  - 5 类借鉴：runtime injector / task-aware reasoning-mode router /
    measured P1-P23 evaluation / 4 类路由行为带 / install.ps1 一键安装
  - 上游无 package.json（PowerShell 脚本安装）· 借鉴档不实跑 git clone
  - 自研 14+ unittest PASS
  - 退出码契约：0=OK / 1=PARSE_ERR / 2=CONFIG_ERR / 3=VALIDATION_ERR
================================================================================
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

EXIT_OK = 0
EXIT_PARSE = 1
EXIT_CONFIG = 2
EXIT_VALIDATION = 3


# ==============================================================================
# 1. Runtime Injector 配置（借鉴 inject/dev_* 工具）
# ==============================================================================

@dataclass
class RuntimeInjectorConfig:
    """runtime injector 配置（借鉴 dsh-super-injector）"""
    version: str = "0.3.3"
    dev_tools: List[str] = field(default_factory=lambda: [
        "dev_inject",      # 注入工具
        "dev_reload",      # 热重载
        "dev_promote",     # 侧挂转正
        "dev_unload",      # 卸载
        "dev_router_status",  # 路由状态查询
        "dev_router_mode",  # 路由模式切换
        "dev_mode_subagent",  # subagent 模式
    ])
    reload_strategy: str = "hot"   # hot / soft / restart
    auto_recover: bool = True


# ==============================================================================
# 2. Reasoning-Mode Router 预设（借鉴 router-standard / router-spec）
# ==============================================================================

REASONING_MODES = ["spec", "react", "mixed", "weak"]


@dataclass
class ReasoningMode:
    """reasoning-mode router preset"""
    name: str                           # spec / react / mixed / weak
    description: str = ""
    persona: Optional[str] = None       # 分类 persona 静态内容
    sections: List[str] = field(default_factory=list)
    suitable_models: List[str] = field(default_factory=list)
    expected_gain_pct: float = 0.0


# 标准 4 类路由行为带（借鉴 README §router-standard 预设能力）
DEFAULT_MODES = [
    ReasoningMode(
        name="spec",
        description="计划-集体 · 深度思考优先",
        persona="分类 persona + few-shot examples",
        sections=["回顾", "收敛", "反跑题"],
        suitable_models=["Pro"],
        expected_gain_pct=5.0,
    ),
    ReasoningMode(
        name="react",
        description="执行者 · 行为模式切换",
        persona="neutral + classify",
        sections=["回顾", "收敛", "反跑题"],
        suitable_models=["Flash"],
        expected_gain_pct=5.7,
    ),
    ReasoningMode(
        name="mixed",
        description="陷阱模式 · 应回避（避免注入）",
        persona=None,
        sections=[],
        suitable_models=[],
        expected_gain_pct=0.0,
    ),
    ReasoningMode(
        name="weak",
        description="模型自分类 · fallback 默认",
        persona=None,
        sections=[],
        suitable_models=["Pro", "Flash"],
        expected_gain_pct=0.0,
    ),
]


# ==============================================================================
# 3. P1-P23 评测框架（借鉴 measured 框架）
# ==============================================================================

@dataclass
class EvalResult:
    """P1-P23 单项评测结果"""
    p_id: str                  # P1, P2, ..., P23
    task: str
    mode: str                  # router mode
    success: bool
    gain_pct: float
    notes: str = ""


def parse_p_id(p_id: str) -> int:
    """解析 'P1' → 1"""
    m = re.match(r"P(\d+)", p_id)
    return int(m.group(1)) if m else 0


def filter_eval_by_model(results: List[EvalResult], model: str) -> List[EvalResult]:
    """按 model 过滤 P1-P23 结果"""
    return [r for r in results if model in r.mode or model.lower() in r.notes.lower()]


# ==============================================================================
# 4. 4 类路由行为带校验（借鉴 README §router-standard 4 类型）
# ==============================================================================

VALID_BEHAVIORS = ["spec", "react", "mixed", "weak"]


def validate_behavior(behavior: str) -> bool:
    """校验行为带是否在 4 类标准之内"""
    return behavior in VALID_BEHAVIORS


# ==============================================================================
# 5. install.ps1 一键安装脚本模板（借鉴 install.ps1 3 步）
# ==============================================================================

INSTALL_STEPS = [
    "1. 拉套装 (git clone https://github.com/yjh051108/dsh-routing-suite.git)",
    "2. 一键安装 (./install.ps1) 或手动 (dsh plugin add + Copy-Item preset)",
    "3. 重启 DSH → 新会话选择 Router Standard / Router Spec (experimental)",
]


# ==============================================================================
# CLI
# ==============================================================================

def cmd_list_modes(args: argparse.Namespace) -> int:
    """列出 4 类 reasoning-mode router preset"""
    print("=== router-standard 4 类路由行为带 ===")
    for mode in DEFAULT_MODES:
        gain = f"+{mode.expected_gain_pct:.1f}%" if mode.expected_gain_pct else "neutral"
        print(f"  [{mode.name:<6}] {mode.description:<30} models={mode.suitable_models} gain={gain}")
    return EXIT_OK


def cmd_validate_config(args: argparse.Namespace) -> int:
    """校验 injector 配置（4 类行为带）"""
    behaviors = args.behaviors.split(",") if args.behaviors else []
    invalid = [b for b in behaviors if not validate_behavior(b)]
    if invalid:
        print(f"[error] invalid behaviors: {invalid} (allowed: {VALID_BEHAVIORS})", file=sys.stderr)
        return EXIT_VALIDATION
    print(json.dumps({"behaviors": behaviors, "all_valid": True}, indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_parse_p_id(args: argparse.Namespace) -> int:
    """解析 P1-P23 ID"""
    try:
        n = parse_p_id(args.p_id)
        print(json.dumps({"p_id": args.p_id, "numeric": n}, indent=2))
        return EXIT_OK
    except ValueError as e:
        print(f"[parse error] {e}", file=sys.stderr)
        return EXIT_PARSE


def cmd_filter_eval(args: argparse.Namespace) -> int:
    """按 model 过滤 P1-P23 评测（mock）"""
    # mock 23 项评测结果
    mock_results = []
    for i in range(1, 24):
        model = "Pro" if i % 2 == 0 else "Flash"
        mock_results.append(EvalResult(
            p_id=f"P{i}",
            task=f"task-{i}",
            mode=model.lower(),
            success=i % 3 != 0,
            gain_pct=5.0 + (i % 5),
            notes=f"{model} model",
        ))
    filtered = filter_eval_by_model(mock_results, args.model)
    print(json.dumps([asdict(r) for r in filtered], indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_install_steps(args: argparse.Namespace) -> int:
    """列出 install.ps1 3 步"""
    print("=== install.ps1 三步 ===")
    for step in INSTALL_STEPS:
        print(f"  {step}")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dsh_routing_suite_bridge",
        description="Stage 51.1 dsh-routing-suite-bridge V1.0 · yjh051108/dsh-routing-suite MIT 借鉴档",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("list-modes", help="列出 4 类 reasoning-mode router preset")
    sp.set_defaults(func=cmd_list_modes)

    sp = sub.add_parser("validate-config", help="校验 injector 配置（4 类行为带）")
    sp.add_argument("--behaviors", required=True, help="comma-separated behaviors")
    sp.set_defaults(func=cmd_validate_config)

    sp = sub.add_parser("parse-p-id", help="解析 P1-P23 ID")
    sp.add_argument("--p-id", required=True, help="如 P5")
    sp.set_defaults(func=cmd_parse_p_id)

    sp = sub.add_parser("filter-eval", help="按 model 过滤 P1-P23 评测")
    sp.add_argument("--model", required=True, choices=["pro", "flash"], help="filter model")
    sp.set_defaults(func=cmd_filter_eval)

    sp = sub.add_parser("install-steps", help="列出 install.ps1 3 步")
    sp.set_defaults(func=cmd_install_steps)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
