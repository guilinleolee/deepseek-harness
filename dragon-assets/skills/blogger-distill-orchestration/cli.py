# -*- coding: utf-8 -*-
"""
CLI Entry Point — blogger-distill orchestrate / dlq / verify
来源: blogger-distill-orchestration SKILL.md (lines 443-474)
"""

import argparse
import json
import sys
import os
from pathlib import Path

# 添加包根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import PipelineOrchestrator, parallel_collect
from steps.step2_verifier import Step2Verifier


# ── 辅助 ──────────────────────────────────────────────────────────────


def _resolve_blogger_name(blogger_id: str, output_dir: str) -> str:
    """从已有的 pipeline state 文件推断 blogger_name"""
    path = os.path.join(output_dir, f"pipeline_{blogger_id}.json")
    if os.path.exists(path):
        try:
            state = json.load(open(path, encoding="utf-8"))
            return state.get("blogger_name", blogger_id)
        except Exception:
            pass
    return blogger_id


def _resolve_output_dir(args) -> str:
    """从 --output 参数或默认值推断 output_dir"""
    if args.output:
        return args.output
    return getattr(args, "output_dir", "./output")


# ── orchestrate ──────────────────────────────────────────────────────────


def cmd_orchestrate(args):
    blogger_ids = [b.strip() for b in args.blogger_ids.split(",") if b.strip()]
    output_dir = args.output or "./output"

    if len(blogger_ids) > 1:
        # 并行多Blogger
        configs = []
        for bid in blogger_ids:
            bname = args.blogger_names.get(bid, bid) if args.blogger_names else bid
            configs.append({
                "blogger_id": bid,
                "blogger_name": bname,
                "output_dir": output_dir,
                "steps": args.steps or "all",
                "mode": args.mode,
                "api_token": args.api_token,
                "notes_count": args.notes,
            })

        results = parallel_collect(configs, max_workers=args.parallel or 3)

        total = len(results)
        ok = sum(1 for r in results.values() if "error" not in r)
        print(f"\n[完成] 成功 {ok}/{total} 个Blogger")

        if args.export_summary:
            for bid, result in results.items():
                if "error" not in result:
                    summary = json.dumps(result, ensure_ascii=False, indent=2)
                    out = os.path.join(output_dir, f"{bid}_summary.json")
                    with open(out, "w", encoding="utf-8") as f:
                        f.write(summary)
                    print(f"[导出] {out}")
        return

    # 单Blogger
    blogger_id = blogger_ids[0]
    blogger_name = args.blogger_name or blogger_id

    orch = PipelineOrchestrator(
        blogger_id=blogger_id,
        blogger_name=blogger_name,
        output_dir=output_dir,
        steps=args.steps or "all",
        mode=args.mode or "learn",
        resume=args.resume,
        resume_from_step=args.from_step,
        api_token=args.api_token,
        notes_count=args.notes or 100,
    )

    if args.dry_run:
        status = orch.status()
        print(f"[Dry Run] blogger={status['blogger_name']}, "
              f"completed={status['completed']}, failed={status['failed']}")
        return

    result = orch.run()

    if args.export_summary:
        md = orch.export_summary(format=args.export_format or "markdown")
        out = os.path.join(output_dir, f"{blogger_name}_pipeline_summary.md")
        with open(out, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"[导出摘要] {out}")

    # 打印摘要
    elapsed = result.get("elapsed_seconds", 0)
    done = len(result.get("completed_steps", []))
    failed = len(result.get("failed_steps", []))
    print(f"\n[完成] 步骤 {done}/6 完成, {failed} 失败, 耗时 {elapsed:.1f}s")


# ── dlq ────────────────────────────────────────────────────────────────


def cmd_dlq(args):
    blogger_name = args.blogger_id or "unknown"
    output_dir = args.output or "./output"
    dlq_path = os.path.join(output_dir, f"dlq_{blogger_name}.json")

    if not os.path.exists(dlq_path):
        print(f"[DLQ] 无待处理项: {dlq_path}")
        return

    try:
        dlq_data = json.load(open(dlq_path, encoding="utf-8"))
    except Exception as e:
        print(f"[DLQ] 读取失败: {e}")
        return

    items = dlq_data.get("items", [])

    if args.subcmd == "list":
        if not items:
            print(f"[DLQ] 无待处理项")
            return
        print(f"[DLQ] 待处理项 ({len(items)} 条):")
        for i, item in enumerate(items):
            print(f"  [{i}] step={item.get('step')} id={item.get('item_id')} "
                  f"reason={str(item.get('reason', ''))[:60]}")
        return

    idx = args.idx
    if idx < 0 or idx >= len(items):
        print(f"[DLQ] 无效索引 {idx} (有效范围: 0-{len(items)-1})")
        return

    if args.subcmd == "retry":
        # 重试: 从 dlq 中移除并从失败步骤恢复
        item = items.pop(idx)
        dlq_data["items"] = items
        with open(dlq_path, "w", encoding="utf-8") as f:
            json.dump(dlq_data, f, ensure_ascii=False, indent=2)
        step = int(item.get("step", "1").replace("step", ""))
        print(f"[DLQ] 重试项 {idx}: {item.get('step')} / {item.get('item_id')}")
        print(f"[DLQ] 从 Step {step} 恢复执行...")

        orch = PipelineOrchestrator(
            blogger_id=item.get("item_id", blogger_name),
            blogger_name=item.get("item_id", blogger_name),
            output_dir=output_dir,
            resume_from_step=step,
        )
        orch.run()
        return

    if args.subcmd == "abandon":
        item = items.pop(idx)
        dlq_data["items"] = items
        dlq_data.setdefault("abandoned", []).append(item)
        with open(dlq_path, "w", encoding="utf-8") as f:
            json.dump(dlq_data, f, ensure_ascii=False, indent=2)
        print(f"[DLQ] 放弃项 {idx}: {item.get('step')} / {item.get('item_id')}")


# ── verify ─────────────────────────────────────────────────────────────


def cmd_verify(args):
    verifier = Step2Verifier(
        output_dir=args.output or "./output",
        threshold_v1=args.threshold,
        blocking=args.blocking,
    )

    notes_raw = json.load(open(args.notes_file, encoding="utf-8"))
    result = verifier.run(notes_raw)

    passed = result.get("passed", 0)
    failed = result.get("failed", 0)
    complete = result.get("complete", 0)
    partial = result.get("partial", 0)

    print(f"\n[验证] 通过 {passed}/{passed+failed} 条 "
          f"(complete={complete}, partial={partial})")

    if result.get("verified_path"):
        print(f"[验证] 产出: {result['verified_path']}")


# ── CLI 入口 ──────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        prog="blogger-distill",
        description="博主笔记蒸馏 6 步编排引擎 CLI",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # ── orchestrate ──────────────────────────────────────────────
    orch = sub.add_parser("orchestrate", help="执行采集→验证→补全→分析→蒸馏→归档 pipeline")
    orch.add_argument("--blogger-id", dest="blogger_ids", required=True,
                      help="博主 ID (多 blogger 用逗号分隔)")
    orch.add_argument("--blogger-name", dest="blogger_name",
                      help="博主名称 (单 blogger 时使用)")
    orch.add_argument("--blogger-names", dest="blogger_names", default="",
                      help="多 blogger 名称映射 (bid:name,bid:name 格式)")
    orch.add_argument("--notes", type=int, default=100,
                      help="目标采集笔记数量 (默认 100)")
    orch.add_argument("--mode", default="learn",
                      choices=["learn", "publish", "analyze"],
                      help="执行模式 (默认 learn)")
    orch.add_argument("--steps", help="步骤范围 (如 1-3 或 all, 默认 all)")
    orch.add_argument("--resume", action="store_true",
                      help="从上次中断处恢复")
    orch.add_argument("--from-step", type=int, dest="from_step",
                      help="从指定步骤恢复 (如 3)")
    orch.add_argument("--resume-from-step", dest="resume_from_step", type=int,
                      help="从指定步骤恢复 (别名 --from-step)")
    orch.add_argument("--output", help="输出目录 (默认 ./output)")
    orch.add_argument("--dry-run", action="store_true",
                      help="仅打印状态，不执行")
    orch.add_argument("--export-summary", action="store_true",
                      help="导出 pipeline 执行摘要")
    orch.add_argument("--export-format", dest="export_format",
                      choices=["markdown", "json"], default="markdown",
                      help="摘要格式 (默认 markdown)")
    orch.add_argument("--parallel", type=int,
                      help="多 blogger 并行数 (默认 3)")
    orch.add_argument("--api-token", dest="api_token",
                      help="API 认证令牌")
    orch.set_defaults(func=cmd_orchestrate)

    # ── dlq ─────────────────────────────────────────────────
    dlq = sub.add_parser("dlq", help="死信队列管理")
    dlq.add_argument("subcmd", choices=["list", "retry", "abandon"],
                     help="子命令: list 列表 / retry 重试 / abandon 放弃")
    dlq.add_argument("--blogger-id", dest="blogger_id",
                      help="博主 ID (用于定位 dlq 文件)")
    dlq.add_argument("--idx", type=int, default=0,
                      help="队列索引 (默认 0)")
    dlq.add_argument("--output", help="输出目录 (默认 ./output)")
    dlq.set_defaults(func=cmd_dlq)

    # ── verify ────────────────────────────────────────────────
    verify = sub.add_parser("verify", help="质量门控验证 (Step2)")
    verify.add_argument("notes_file", help="笔记 JSON 文件路径 (Step1 产出)")
    verify.add_argument("--threshold", type=float, default=0.5,
                        help="V1 正文完整度阈值 (默认 0.5)")
    verify.add_argument("--blocking", action="store_true", default=True,
                      help="启用阻断门控 (默认 True)")
    verify.add_argument("--no-blocking", dest="blocking", action="store_false",
                      help="禁用阻断门控")
    verify.add_argument("--output", help="输出目录 (默认 ./output)")
    verify.set_defaults(func=cmd_verify)

    args = parser.parse_args()

    # 统一 --from-step 别名
    if hasattr(args, "from_step") and args.from_step:
        args.resume_from_step = args.from_step

    try:
        args.func(args)
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
