# -*- coding: utf-8 -*-
"""
PipelineOrchestrator — 6步编排引擎状态机
来源: blogger-distill-orchestration SKILL.md (lines 386-411)
"""

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Optional, Union

from .dlq import DeadLetterQueue
from .steps import (
    Step1Collector,
    Step2Verifier,
    Step3Repairer,
    Step4Analyzer,
    Step5Distiller,
    Step6Archiver,
)


class PipelineOrchestrator:
    """6步编排引擎状态机 — 采集→验证→补全→分析→蒸馏→归档"""

    # ── 常量 ──────────────────────────────────────────────────────────────

    STEP_NAMES = {
        1: "Step1Collector",
        2: "Step2Verifier",
        3: "Step3Repairer",
        4: "Step4Analyzer",
        5: "Step5Distiller",
        6: "Step6Archiver",
    }

    STEP_LABELS = {
        1: "采集",
        2: "验证",
        3: "补全",
        4: "分析",
        5: "蒸馏",
        6: "归档",
    }

    # ── 初始化 ────────────────────────────────────────────────────────

    def __init__(
        self,
        blogger_id: str,
        blogger_name: Optional[str] = None,
        output_dir: str = "./output",
        steps: Union[str, list, int] = "all",
        mode: str = "learn",
        max_workers: int = 3,
        resume: bool = False,
        resume_from_step: Optional[int] = None,
        api_token: Optional[str] = None,
        checkpoint_interval: int = 10,
        notes_count: int = 100,
    ):
        self.blogger_id = blogger_id
        self.blogger_name = blogger_name or blogger_id
        self.output_dir = output_dir
        self.steps = steps
        self.mode = mode
        self.max_workers = max_workers
        self.resume = resume
        self.resume_from_step = resume_from_step
        self.api_token = api_token
        self.checkpoint_interval = checkpoint_interval
        self.notes_count = notes_count

        # 运行时状态
        self._running = False
        self._aborted = False
        self._results: dict[int, Any] = {}
        self._errors: dict[int, str] = {}
        self._start_time: Optional[float] = None
        self._step_start: Optional[float] = None

        # 初始化输出目录
        os.makedirs(self.output_dir, exist_ok=True)

        # 初始化死信队列
        self._dlq = DeadLetterQueue(
            os.path.join(self.output_dir, f"dlq_{self.blogger_name}.json")
        )

        # 初始化检查点
        self._pipeline_state = self._load_pipeline_state()

        # 解析步骤范围
        self._step_range = self._parse_steps(steps)

        # 解析恢复起始步骤
        if resume_from_step:
            self._effective_start = resume_from_step
        elif resume:
            self._effective_start = self._pipeline_state.get("last_completed_step", 0) + 1
        else:
            self._effective_start = self._step_range[0]

    # ── 步骤解析 ────────────────────────────────────────────────────

    def _parse_steps(self, steps) -> list[int]:
        if steps == "all":
            return list(range(1, 7))
        if isinstance(steps, int):
            return [steps]
        if isinstance(steps, str) and "-" in steps:
            start, end = steps.split("-")
            return list(range(int(start), int(end) + 1))
        if isinstance(steps, list):
            return steps
        return list(range(1, 7))

    # ── Pipeline State ───────────────────────────────────────────────

    def _load_pipeline_state(self) -> dict:
        path = os.path.join(self.output_dir, f"pipeline_{self.blogger_name}.json")
        if os.path.exists(path):
            try:
                return json.load(open(path, encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                pass
        return {
            "blogger_id": self.blogger_id,
            "blogger_name": self.blogger_name,
            "started_at": None,
            "completed_steps": [],
            "last_completed_step": 0,
            "step_results": {},
            "step_errors": {},
            "aborted": False,
        }

    def _save_pipeline_state(self):
        path = os.path.join(self.output_dir, f"pipeline_{self.blogger_name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._pipeline_state, f, ensure_ascii=False, indent=2)

    # ── 核心运行 ────────────────────────────────────────────────────

    def run(self) -> dict:
        """执行 pipeline，返回各步骤结果摘要"""
        self._running = True
        self._start_time = time.time()
        self._pipeline_state["started_at"] = datetime.now().isoformat()

        print(f"\n{'='*60}")
        print(f"PipelineOrchestrator — {self.blogger_name}")
        print(f"步骤范围: {self._step_range}  |  模式: {self.mode}")
        print(f"{'='*60}\n")

        try:
            for step_num in self._step_range:
                if step_num < self._effective_start:
                    print(f"[跳过] Step {step_num} ({self.STEP_LABELS[step_num]}) — 已在之前完成")
                    continue

                if self._aborted:
                    print(f"\n[中断] Pipeline 在 Step {step_num} 被中止")
                    break

                self._step_start = time.time()
                self._run_step(step_num)

                if step_num in self._errors and self._pipeline_state.get("_blocking_error"):
                    break

            self._pipeline_state["completed_steps"] = [
                s for s in self._pipeline_state["completed_steps"]
                if s in self._step_range
            ]

        finally:
            self._running = False
            self._save_pipeline_state()

        return self._build_summary()

    def _run_step(self, step_num: int):
        """执行单个步骤"""
        step_name = self.STEP_NAMES[step_num]
        step_label = self.STEP_LABELS[step_num]
        print(f"[开始] Step {step_num}/6 — {step_label} ({step_name})")

        try:
            result = self._execute_step(step_num)
            self._results[step_num] = result
            self._pipeline_state["step_results"][str(step_num)] = result
            self._pipeline_state["completed_steps"].append(step_num)
            self._pipeline_state["last_completed_step"] = step_num

            elapsed = time.time() - self._step_start
            print(f"[完成] Step {step_num}/6 — {step_label}  ({elapsed:.1f}s)")

        except Exception as e:
            tb = self._format_traceback(e)
            self._errors[step_num] = str(e)
            self._pipeline_state["step_errors"][str(step_num)] = str(e)

            # V1/V6 阻断错误
            if step_num in (1, 6):
                self._pipeline_state["_blocking_error"] = True
                print(f"\n[阻断错误] Step {step_num} — {step_label}: {e}")
                self._dlq.add(
                    step=f"step{step_num}",
                    item_id=self.blogger_id,
                    reason=str(e),
                    traceback=tb,
                    extra={"step_label": step_label},
                )
                self._save_pipeline_state()
                sys.exit(1)

            # 其他步骤警告
            print(f"[警告] Step {step_num} — {step_label}: {e}")
            self._dlq.add(
                step=f"step{step_num}",
                item_id=self.blogger_id,
                reason=str(e),
                traceback=tb,
                extra={"step_label": step_label},
            )

        self._save_pipeline_state()

    def _execute_step(self, step_num: int) -> Any:
        """实例化并执行步骤"""
        if step_num == 1:
            collector = Step1Collector(self.api_token, self.output_dir)
            return collector.run(self.blogger_id, notes_count=self.notes_count)

        elif step_num == 2:
            verifier = Step2Verifier(self.output_dir)
            # 从上一步加载
            raw_path = os.path.join(
                self.output_dir, f"{self.blogger_name}_raw.json"
            )
            notes_raw = json.load(open(raw_path, encoding="utf-8"))
            return verifier.run(notes_raw)

        elif step_num == 3:
            repairer = Step3Repairer(self.api_token, self.output_dir)
            verified_path = os.path.join(
                self.output_dir, f"{self.blogger_name}_verified.json"
            )
            verified = json.load(open(verified_path, encoding="utf-8"))
            return repairer.run(verified)

        elif step_num == 4:
            analyzer = Step4Analyzer(self.output_dir)
            repaired_path = os.path.join(
                self.output_dir, f"{self.blogger_name}_repaired.json"
            )
            repaired = json.load(open(repaired_path, encoding="utf-8"))
            return analyzer.run(repaired)

        elif step_num == 5:
            distiller = Step5Distiller(mode=self.mode, output_dir=self.output_dir)
            report_path = os.path.join(
                self.output_dir, f"{self.blogger_name}_analysis.json"
            )
            stats_path = os.path.join(
                self.output_dir, f"{self.blogger_name}_stats.json"
            )
            report = json.load(open(report_path, encoding="utf-8"))
            stats = json.load(open(stats_path, encoding="utf-8"))
            return distiller.run(report, stats)

        elif step_num == 6:
            archiver = Step6Archiver(self.output_dir)
            return archiver.archive(self._build_step_results())

        return None

    # ── 状态查询 ────────────────────────────────────────────────────

    def status(self) -> dict:
        """返回 pipeline 状态（各步骤完成度/失败数）"""
        completed = set(self._pipeline_state["completed_steps"])
        failed = set(int(k) for k in self._pipeline_state["step_errors"])
        blocking = self._pipeline_state.get("_blocking_error", False)

        return {
            "blogger_id": self.blogger_id,
            "blogger_name": self.blogger_name,
            "step_range": self._step_range,
            "effective_start": self._effective_start,
            "completed": sorted(completed),
            "failed": sorted(failed),
            "blocking_error": blocking,
            "running": self._running,
            "aborted": self._aborted,
            "dlq_stats": self._dlq.stats(),
        }

    def resume(self, from_step: Optional[int] = None):
        """从指定步骤恢复执行"""
        if from_step:
            self.resume_from_step = from_step
            self._effective_start = from_step
        else:
            self._effective_start = self._pipeline_state.get("last_completed_step", 0) + 1
        print(f"[恢复] 从 Step {self._effective_start} 继续执行")
        return self.run()

    def abort(self):
        """中止 pipeline，保存当前状态"""
        self._aborted = True
        self._pipeline_state["aborted"] = True
        self._save_pipeline_state()
        print("[中止] Pipeline 已标记为中止状态")

    def get_dlq(self) -> DeadLetterQueue:
        """获取死信队列"""
        return self._dlq

    def export_summary(self, format: str = "markdown") -> str:
        """导出 pipeline 执行摘要"""
        summary = self._build_summary()

        if format == "json":
            return json.dumps(summary, ensure_ascii=False, indent=2)

        # Markdown 格式
        elapsed = time.time() - self._start_time if self._start_time else 0
        lines = [
            f"# Pipeline 执行摘要 — {self.blogger_name}",
            "",
            f"**Blogger ID**: {self.blogger_id}",
            f"**模式**: {self.mode}",
            f"**步骤范围**: {self._step_range}",
            f"**执行时间**: {elapsed:.1f}s",
            f"**完成时间**: {datetime.now().isoformat()}",
            "",
            "## 步骤结果",
            "",
            "| 步骤 | 状态 | 耗时 |",
            "|------|------|------|",
        ]

        for step_num in self._step_range:
            label = self.STEP_LABELS[step_num]
            if step_num in self._results:
                lines.append(f"| {step_num}. {label} | ✅ 完成 | — |")
            elif step_num in self._errors:
                lines.append(f"| {step_num}. {label} | ❌ 失败 | — |")
            else:
                lines.append(f"| {step_num}. {label} | ⏭️ 跳过 | — |")

        lines += [
            "",
            "## 质量门控",
            "",
            f"- **V1 阻断**: {'是' if 1 in self._errors else '否'}",
            f"- **DLQ 待处理**: {self._dlq.stats()['pending']}",
            "",
            "## 输出文件",
            "",
        ]

        for fname in [
            f"{self.blogger_name}_raw.json",
            f"{self.blogger_name}_verified.json",
            f"{self.blogger_name}_repaired.json",
            f"{self.blogger_name}_analysis.json",
            f"{self.blogger_name}_stats.json",
            f"pipeline_{self.blogger_name}.json",
        ]:
            fpath = os.path.join(self.output_dir, fname)
            marker = "✅" if os.path.exists(fpath) else "❌"
            lines.append(f"- {marker} `{fname}`")

        return "\n".join(lines)

    # ── 辅助方法 ────────────────────────────────────────────────────

    def _build_summary(self) -> dict:
        elapsed = time.time() - self._start_time if self._start_time else 0
        return {
            "blogger_id": self.blogger_id,
            "blogger_name": self.blogger_name,
            "mode": self.mode,
            "step_range": self._step_range,
            "completed_steps": self._pipeline_state["completed_steps"],
            "failed_steps": [int(k) for k in self._pipeline_state["step_errors"]],
            "blocking_error": self._pipeline_state.get("_blocking_error", False),
            "results": {str(k): v for k, v in self._results.items()},
            "errors": self._pipeline_state["step_errors"],
            "dlq_stats": self._dlq.stats(),
            "elapsed_seconds": round(elapsed, 1),
            "completed_at": datetime.now().isoformat(),
        }

    def _build_step_results(self) -> dict:
        """构建包含所有步骤结果的字典（用于Step 6归档）"""
        return {
            "pipeline": self._pipeline_state,
            "results": self._results,
            "errors": self._pipeline_state["step_errors"],
            "dlq_stats": self._dlq.stats(),
        }

    @staticmethod
    def _format_traceback(exc: Exception) -> str:
        import traceback
        return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

    def __repr__(self):
        completed = len(self._pipeline_state["completed_steps"])
        failed = len(self._pipeline_state["step_errors"])
        return (
            f"<PipelineOrchestrator blogger={self.blogger_name} "
            f"steps={self._step_range} "
            f"completed={completed} failed={failed}>"
        )


# ── 多Blogger并行 ───────────────────────────────────────────────

def parallel_collect(
    blogger_configs: list[dict],
    max_workers: int = 3,
) -> dict:
    """多 Blogger 并行采集，互不干扰"""
    results = {}

    def run_one(cfg: dict) -> tuple[str, dict]:
        blogger_id = cfg["blogger_id"]
        blogger_name = cfg.get("blogger_name", blogger_id)
        output_dir = cfg.get("output_dir", "./output")
        steps = cfg.get("steps", "all")
        mode = cfg.get("mode", "learn")
        api_token = cfg.get("api_token")
        notes_count = cfg.get("notes_count", 100)

        orch = PipelineOrchestrator(
            blogger_id=blogger_id,
            blogger_name=blogger_name,
            output_dir=output_dir,
            steps=steps,
            mode=mode,
            api_token=api_token,
            notes_count=notes_count,
        )
        result = orch.run()
        return blogger_id, result

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(run_one, cfg): cfg["blogger_id"]
            for cfg in blogger_configs
        }

        for future in as_completed(futures):
            blogger_id = futures[future]
            try:
                _, result = future.result()
                results[blogger_id] = result
                print(f"✅ {blogger_id} 完成")
            except Exception as e:
                results[blogger_id] = {"error": str(e)}
                print(f"❌ {blogger_id} 失败: {e}")

    return results
