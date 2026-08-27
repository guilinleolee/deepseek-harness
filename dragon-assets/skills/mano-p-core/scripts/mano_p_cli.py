#!/usr/bin/env python3
"""
Mano-P CLI - 命令行工具封装
天龙引擎 Phase 2

用法:
  python mano_p_cli.py execute "任务描述"
  python mano_p_cli.py tav "任务描述"
  python mano_p_cli.py benchmark --category web_browser --limit 5
  python mano_p_cli.py route "任务描述"
"""

import argparse
import asyncio
import json
import sys
import os
from pathlib import Path

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from mano_vla_client import ManoPVLAClient
from dual_engine_client import DualEngineOrchestrator, TaskAnalyzer, OrchestrationMode
from tav_loop import ThinkActVerifyLoop, TAVConfig
from osworld_benchmark import OSWorldBenchmark


def setup_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Mano-P CLI - GUI-VLA命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python mano_p_cli.py execute "打开Chrome访问GitHub"
  python mano_p_cli.py tav "从SAP提取数据到Excel"
  python mano_p_cli.py benchmark --category web_browser --limit 5
  python mano_p_cli.py route "在桌面上创建新文件夹"
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # execute命令
    exec_parser = subparsers.add_parser("execute", help="执行单个任务")
    exec_parser.add_argument("task", help="任务描述")
    exec_parser.add_argument("--mode", choices=["turix", "mano", "dual"],
                             default="dual", help="编排模式")

    # tav命令
    tav_parser = subparsers.add_parser("tav", help="Think-Act-Verify循环")
    tav_parser.add_argument("task", help="任务描述")
    tav_parser.add_argument("--max-loops", type=int, default=3, help="最大循环次数")
    tav_parser.add_argument("--max-steps", type=int, default=100, help="最大步数")

    # benchmark命令
    bench_parser = subparsers.add_parser("benchmark", help="运行OSWorld基准测试")
    bench_parser.add_argument("--category", help="指定类别")
    bench_parser.add_argument("--limit", type=int, default=10, help="限制任务数")

    # route命令
    route_parser = subparsers.add_parser("route", help="分析任务路由")
    route_parser.add_argument("task", help="任务描述")

    return parser


async def cmd_execute(args):
    """执行命令"""
    print(f"\n[Execute] Task: {args.task}")
    print(f"[Execute] Mode: {args.mode}\n")

    orchestrator = DualEngineOrchestrator()

    mode_map = {
        "turix": OrchestrationMode.TURIX_FIRST,
        "mano": OrchestrationMode.MANO_P_INFERENCE,
        "dual": OrchestrationMode.DUAL_ORCHESTRATION
    }

    result = await orchestrator.execute(
        args.task,
        mode=mode_map[args.mode],
        force_mode=True
    )

    print(f"\n{'='*50}")
    print(f"Result: {result.status}")
    print(f"Engine: {result.engine_used}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    print(f"Score: {result.verification_score:.2f}")
    print(f"{'='*50}\n")

    if result.error:
        print(f"Error: {result.error}\n")

    return 0 if result.status == "success" else 1


async def cmd_tav(args):
    """TAV循环命令"""
    print(f"\n[TAV Loop] Task: {args.task}")
    print(f"[TAV] Max Loops: {args.max_loops}, Max Steps: {args.max_steps}\n")

    config = TAVConfig(
        max_loops=args.max_loops,
        max_steps=args.max_steps,
        verify_interval=5
    )

    tav_loop = ThinkActVerifyLoop(config=config)

    # 注意：实际执行需要VLA Server
    print("Note: 需要实际VLA Server运行才能执行")
    print("启动VLA Server后:")
    print("  mano_vla = ManoPVLAClient()")
    print("  tav_loop = ThinkActVerifyLoop(config=config, vla_client=mano_vla)")
    print("  result = await tav_loop.run(task, screenshot)")

    return 0


async def cmd_benchmark(args):
    """基准测试命令"""
    print(f"\n[Benchmark] Category: {args.category or 'all'}, Limit: {args.limit}\n")

    benchmark = OSWorldBenchmark()

    categories = [args.category] if args.category else None

    print("运行OSWorld基准测试...\n")

    # 注意：实际测试需要VLA Server
    print("Note: 需要实际VLA Server运行才能执行基准测试")
    print("启动VLA Server后:")
    print("  mano_vla = ManoPVLAClient()")
    print("  tav_loop = ThinkActVerifyLoop(vla_client=mano_vla)")
    print("  benchmark = OSWorldBenchmark(tav_loop=tav_loop, vla_client=mano_vla)")
    print("  results = await benchmark.run_all(categories=categories, max_tasks=args.limit)")
    print("  report = benchmark.generate_report(results)")

    # 模拟运行演示
    print("\n模拟基准测试结果:")
    demo_report = benchmark.generate_report()

    return 0


async def cmd_route(args):
    """路由分析命令"""
    print(f"\n[Route] Task: {args.task}\n")

    analyzer = TaskAnalyzer()
    decision = analyzer.analyze(args.task)

    mode_icons = {
        "turix_first": "⚡ TURIX_FIRST",
        "mano_p_inference": "🧠 MANO_P_INFERENCE",
        "dual_orchestration": "🔄 DUAL_ORCHESTRATION"
    }

    print(f"{'='*50}")
    print(f"推荐模式: {mode_icons[decision.mode.value]}")
    print(f"推理: {decision.reasoning}")
    print(f"置信度: {decision.confidence:.2f}")
    print(f"预估时间: {decision.estimated_time:.1f}s")
    print(f"推荐引擎: {', '.join(decision.recommended_engines)}")
    print(f"{'='*50}\n")

    return 0


def main():
    parser = setup_argparse()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # 命令路由
    if args.command == "execute":
        return asyncio.run(cmd_execute(args))
    elif args.command == "tav":
        return asyncio.run(cmd_tav(args))
    elif args.command == "benchmark":
        return asyncio.run(cmd_benchmark(args))
    elif args.command == "route":
        return asyncio.run(cmd_route(args))
    else:
        print(f"未知命令: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
