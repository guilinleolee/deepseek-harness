# -*- coding: utf-8 -*-
"""
Step6Archiver — 知识持久化归档管道
来源: blogger-distill-orchestration SKILL.md (lines 208-221)

WikiArchiver + PipelineSummary + FollowupScheduler
输出: wiki/{blogger_name}/ + pipeline_summary.json + followup_reminder.json
"""

import json
import os
import shutil
from datetime import datetime
from typing import Any, Optional


# ── Wiki归档 ────────────────────────────────────────────────────────────────

class WikiArchiver:
    """
    Wiki知识库归档器
    将pipeline全部产出归档到 wiki/{blogger_name}/ 目录
    """

    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def archive(self, blogger_name: str, step_results: dict) -> dict:
        """
        执行Wiki归档

        Args:
            blogger_name: 博主名称（作为归档目录名）
            step_results: pipeline执行结果（含pipeline/results/errors/dlq_stats）

        Returns:
            dict: 归档结果摘要
        """
        wiki_dir = os.path.join(self.output_dir, "wiki", blogger_name)
        os.makedirs(wiki_dir, exist_ok=True)

        pipeline_data = step_results.get("pipeline", {})
        results = step_results.get("results", {})
        errors = step_results.get("errors", {})
        dlq_stats = step_results.get("dlq_stats", {})

        # 1. 写入Wiki首页 README.md
        readme_path = os.path.join(wiki_dir, "README.md")
        self._write_readme(readme_path, blogger_name, step_results)

        # 2. 归档pipeline状态
        pipeline_dir = os.path.join(wiki_dir, "pipeline")
        os.makedirs(pipeline_dir, exist_ok=True)
        self._write_pipeline_state(pipeline_dir, blogger_name, pipeline_data)

        # 3. 归档各步骤产物
        for step_num, result in results.items():
            step_dir = os.path.join(wiki_dir, f"step{step_num}")
            os.makedirs(step_dir, exist_ok=True)
            self._archive_step_output(step_dir, blogger_name, step_num, result)

        # 4. 归档失败记录
        if errors:
            failed_dir = os.path.join(wiki_dir, "failed")
            os.makedirs(failed_dir, exist_ok=True)
            self._archive_errors(failed_dir, blogger_name, errors)

        # 5. 归档DLQ记录
        dlq_dir = os.path.join(wiki_dir, "dlq")
        os.makedirs(dlq_dir, exist_ok=True)
        self._archive_dlq(dlq_dir, blogger_name, step_results)

        # 6. 归档原始JSON产物（快照）
        snapshot_dir = os.path.join(wiki_dir, "snapshots")
        os.makedirs(snapshot_dir, exist_ok=True)
        self._create_snapshots(snapshot_dir, blogger_name, results)

        print(f"[WikiArchiver] 归档完成: {wiki_dir}")
        return {"wiki_dir": wiki_dir, "file_count": self._count_files(wiki_dir)}

    def _write_readme(self, path: str, blogger_name: str, step_results: dict) -> None:
        """写入Wiki首页"""
        pipeline = step_results.get("pipeline", {})
        completed = pipeline.get("completed_steps", [])
        results = step_results.get("results", {})
        errors = step_results.get("errors", {})
        dlq_stats = step_results.get("dlq_stats", {})

        started_at = pipeline.get("started_at", "未知")
        completed_at = pipeline.get("completed_at", datetime.now().isoformat())

        total_steps = len(results) + len(errors)
        success_rate = (
            f"{len(results)}/{total_steps}" if total_steps > 0 else "0/0"
        )

        lines = [
            f"# {blogger_name} — Pipeline归档",
            "",
            f"**归档时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**执行时间**: {started_at} → {completed_at}",
            f"**完成步骤**: {len(completed)}步",
            f"**成功率**: {success_rate}",
            f"**DLQ待处理**: {dlq_stats.get('pending', 0)}条",
            "",
            "## 目录结构",
            "",
            "```",
            "wiki/{blogger_name}/",
            "├── README.md              # 本文件",
            "├── pipeline/              # Pipeline状态快照",
            "├── step1-6/             # 各步骤产物",
            "├── failed/               # 失败记录",
            "├── dlq/                 # 死信队列",
            "└── snapshots/           # JSON产物快照",
            "```",
            "",
            "## 步骤产物",
            "",
        ]

        for step_num in sorted(results.keys(), key=lambda x: int(x)):
            label = self._step_label(int(step_num))
            lines.append(f"- **Step {step_num} {label}**: `./step{step_num}/`")

        if errors:
            lines.append("")
            lines.append("## 失败记录")
            for step_num, err in errors.items():
                label = self._step_label(int(step_num))
                lines.append(f"- Step {step_num} {label}: `{err[:100]}...`")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _write_pipeline_state(
        self, pipeline_dir: str, blogger_name: str, pipeline_data: dict
    ) -> None:
        """归档pipeline状态JSON"""
        path = os.path.join(pipeline_dir, "state.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "blogger_name": blogger_name,
                    "captured_at": datetime.now().isoformat(),
                    "pipeline": pipeline_data,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        # 写入markdown摘要
        md_path = os.path.join(pipeline_dir, "state.md")
        completed = pipeline_data.get("completed_steps", [])
        errors = pipeline_data.get("step_errors", {})
        lines = [
            f"# Pipeline状态 — {blogger_name}",
            "",
            f"**Blogger ID**: {pipeline_data.get('blogger_id', '')}",
            f"**开始时间**: {pipeline_data.get('started_at', '未知')}",
            f"**已完成步骤**: {', '.join(str(s) for s in completed) or '无'}",
            "",
            "## 步骤结果",
            "",
        ]
        for step_num in range(1, 7):
            if step_num in completed:
                lines.append(f"- Step {step_num}: ✅ 完成")
            elif str(step_num) in errors:
                err_msg = errors[str(step_num)]
                lines.append(f"- Step {step_num}: ❌ 失败 — {err_msg[:80]}")
            else:
                lines.append(f"- Step {step_num}: ⏭️ 跳过")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _archive_step_output(
        self, step_dir: str, blogger_name: str, step_num: int, result: Any
    ) -> None:
        """归档单步骤产物"""
        # 写入JSON快照
        json_path = os.path.join(step_dir, "output.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"step": step_num, "blogger_name": blogger_name, "result": result}, f, ensure_ascii=False, indent=2, default=str)

        # 写入摘要markdown
        md_path = os.path.join(step_dir, "summary.md")
        label = self._step_label(step_num)
        lines = [f"# Step {step_num} {label} — {blogger_name}", ""]

        if isinstance(result, dict):
            for key, value in result.items():
                if key not in ("notes", "passed_notes", "failed_notes", "details"):
                    lines.append(f"- **{key}**: {value}")
        else:
            lines.append(f"- 结果: `{result}`")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _archive_errors(self, failed_dir: str, blogger_name: str, errors: dict) -> None:
        """归档失败记录"""
        path = os.path.join(failed_dir, "errors.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "blogger_name": blogger_name,
                    "archived_at": datetime.now().isoformat(),
                    "errors": errors,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        # markdown摘要
        md_path = os.path.join(failed_dir, "errors.md")
        lines = [f"# 失败记录 — {blogger_name}", ""]
        for step_num, err in errors.items():
            label = self._step_label(int(step_num))
            lines.append(f"## Step {step_num} {label}")
            lines.append(f"```\n{err}\n```")
            lines.append("")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _archive_dlq(self, dlq_dir: str, blogger_name: str, step_results: dict) -> None:
        """归档DLQ记录"""
        dlq_stats = step_results.get("dlq_stats", {})
        path = os.path.join(dlq_dir, "stats.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "blogger_name": blogger_name,
                    "archived_at": datetime.now().isoformat(),
                    "stats": dlq_stats,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        # DLQ markdown摘要
        md_path = os.path.join(dlq_dir, "summary.md")
        pending = dlq_stats.get("pending", 0)
        resolved = dlq_stats.get("resolved", 0)
        lines = [
            f"# 死信队列 — {blogger_name}",
            "",
            f"**待处理**: {pending}条",
            f"**已解决**: {resolved}条",
            "",
            "> 请定期检查 `./dlq/` 目录，手动处理挂起的条目",
        ]
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _create_snapshots(
        self, snapshot_dir: str, blogger_name: str, results: dict
    ) -> None:
        """为各步骤产物创建快照"""
        snapshot_files = [
            (f"{blogger_name}_raw.json", "step1"),
            (f"{blogger_name}_verified.json", "step2"),
            (f"{blogger_name}_repaired.json", "step3"),
            (f"{blogger_name}_analysis.json", "step4"),
            (f"{blogger_name}_stats.json", "step4"),
            (f"{blogger_name}_distill_guide.md", "step5"),
            (f"{blogger_name}_self_analysis.md", "step5"),
        ]

        for fname, step_name in snapshot_files:
            src = os.path.join(self.output_dir, fname)
            if os.path.exists(src):
                dst = os.path.join(snapshot_dir, fname)
                shutil.copy2(src, dst)

    def _step_label(self, step_num: int) -> str:
        labels = {1: "采集", 2: "验证", 3: "补全", 4: "分析", 5: "蒸馏", 6: "归档"}
        return labels.get(step_num, f"Step{step_num}")

    def _count_files(self, directory: str) -> int:
        """统计目录文件数"""
        count = 0
        for _, _, files in os.walk(directory):
            count += len(files)
        return count


# ── Pipeline摘要 ────────────────────────────────────────────────────────────

class PipelineSummary:
    """
    Pipeline执行摘要生成器
    生成 pipeline_summary.json（含各步骤耗时/成功率）
    """

    STEP_LABELS = {
        1: "采集",
        2: "验证",
        3: "补全",
        4: "分析",
        5: "蒸馏",
        6: "归档",
    }

    def generate(self, blogger_name: str, step_results: dict) -> dict:
        """
        生成Pipeline执行摘要

        Args:
            blogger_name: 博主名称
            step_results: pipeline执行结果

        Returns:
            dict: 摘要数据
        """
        pipeline = step_results.get("pipeline", {})
        results = step_results.get("results", {})
        errors = step_results.get("errors", {})
        dlq_stats = step_results.get("dlq_stats", {})

        started_at = pipeline.get("started_at", "未知")
        completed_at = datetime.now().isoformat()

        # 计算各步骤耗时（从结果中提取）
        step_timings = self._extract_timings(results)

        # 汇总各步骤数据
        step_summaries = []
        for step_num in range(1, 7):
            label = self.STEP_LABELS.get(step_num, f"Step{step_num}")
            step_result = results.get(str(step_num), results.get(step_num))
            error = errors.get(str(step_num), errors.get(step_num_num))

            summary = {
                "step": step_num,
                "label": label,
                "status": "success" if step_result is not None else ("failed" if error else "skipped"),
                "error": error,
                "timing_seconds": step_timings.get(step_num),
            }

            # 提取关键指标
            if isinstance(step_result, dict):
                summary.update(self._extract_key_metrics(step_num, step_result))

            step_summaries.append(summary)

        # 计算整体指标
        total_steps = len(step_summaries)
        success_count = sum(1 for s in step_summaries if s["status"] == "success")
        failed_count = sum(1 for s in step_summaries if s["status"] == "failed")
        success_rate = success_count / total_steps if total_steps > 0 else 0.0
        total_time = sum(
            t for t in step_timings.values() if t is not None
        )

        # 质量门控摘要
        quality_summary = self._build_quality_summary(results, errors)

        summary = {
            "blogger_name": blogger_name,
            "generated_at": datetime.now().isoformat(),
            "started_at": started_at,
            "completed_at": completed_at,
            "total_steps": total_steps,
            "success_count": success_count,
            "failed_count": failed_count,
            "success_rate": round(success_rate * 100, 1),
            "total_timing_seconds": round(total_time, 1),
            "step_summaries": step_summaries,
            "quality_summary": quality_summary,
            "dlq_stats": dlq_stats,
            "blocking_error": pipeline.get("_blocking_error", False),
        }

        # 写入文件
        summary_path = os.path.join(self.output_dir, f"{blogger_name}_pipeline_summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

        print(f"[PipelineSummary] 生成摘要: {summary_path}")
        return summary

    def _extract_timings(self, results: dict) -> dict:
        """从结果中提取各步骤耗时"""
        timings = {}
        timing_keys = {
            1: ["timing_seconds", "collected", "total_list", "failed"],
            2: ["timing_seconds", "total_input", "passed", "failed"],
            3: ["timing_seconds", "total", "repaired_count", "skipped_count"],
            4: ["timing_seconds", "total_notes", "analyzed_count"],
            5: ["timing_seconds", "notes_analyzed"],
            6: ["timing_seconds"],
        }

        for step_num, result in results.items():
            if isinstance(result, dict):
                # 尝试从结果中提取timing_seconds（如果orchestrator注入了elapsed字段）
                timing = result.get("elapsed_seconds") or result.get("timing_seconds")
                # 或者从文件名推断（通过collected/passed等字段的数值估算）
                if timing is None:
                    collected = result.get("collected", 0)
                    passed = result.get("passed", 0)
                    repaired = result.get("repaired_count", 0)
                    if collected > 0:
                        timing = collected * 0.05  # 估算每条0.05s
                    elif passed > 0:
                        timing = passed * 0.03
                    elif repaired > 0:
                        timing = repaired * 0.02
                    else:
                        timing = None
                timings[int(step_num)] = round(timing, 1) if timing else None

        return timings

    def _extract_key_metrics(self, step_num: int, result: dict) -> dict:
        """从步骤结果中提取关键指标"""
        metrics = {}

        if step_num == 1:
            metrics["collected"] = result.get("collected", 0)
            metrics["total_list"] = result.get("total_list", 0)
            metrics["failed"] = result.get("failed", 0)

        elif step_num == 2:
            metrics["total_input"] = result.get("total_input", 0)
            metrics["passed"] = result.get("passed", 0)
            metrics["failed"] = result.get("failed", 0)
            metrics["complete"] = result.get("complete", 0)
            metrics["partial"] = result.get("partial", 0)

        elif step_num == 3:
            metrics["total"] = result.get("total", 0)
            metrics["repaired_count"] = result.get("repaired_count", 0)
            metrics["skipped_count"] = result.get("skipped_count", 0)

        elif step_num == 4:
            metrics["total_notes"] = result.get("total_notes", 0)
            metrics["analyzed_count"] = result.get("analyzed_count", result.get("total_notes", 0))

        elif step_num == 5:
            metrics["notes_analyzed"] = result.get("notes_analyzed", 0)
            if "guide_path" in result:
                metrics["guide_path"] = result["guide_path"]
            if "skill_files_dir" in result:
                metrics["skill_files_dir"] = result["skill_files_dir"]

        return metrics

    def _build_quality_summary(self, results: dict, errors: dict) -> dict:
        """构建质量门控摘要"""
        quality = {
            "v1_blocked": False,
            "v6_blocked": False,
            "warning_count": 0,
            "passed_notes": 0,
            "failed_notes": 0,
        }

        # Step2验证结果
        step2 = results.get("2") or results.get(2)
        if isinstance(step2, dict):
            quality["passed_notes"] = step2.get("passed", 0)
            quality["failed_notes"] = step2.get("failed", 0)

        # Step3补全结果
        step3 = results.get("3") or results.get(3)
        if isinstance(step3, dict):
            quality["repaired_count"] = step3.get("repaired_count", 0)

        # 检查阻断错误
        if "1" in errors or 1 in errors:
            quality["v1_blocked"] = True
        if "6" in errors or 6 in errors:
            quality["v6_blocked"] = True

        return quality


# ── 后续调度 ────────────────────────────────────────────────────────────────

class FollowupScheduler:
    """
    后续调度器
    生成定期复采建议
    """

    # 复采周期建议（天）
    RECOLLECT_INTERVALS = {
        "high_frequency": 7,   # 高频博主（>3篇/周）→ 每周复采
        "medium_frequency": 14, # 中频博主（1-3篇/周）→ 两周复采
        "low_frequency": 30,    # 低频博主（<1篇/周）→ 每月复采
    }

    def schedule(self, blogger_name: str, step_results: dict) -> dict:
        """
        生成后续调度建议

        Args:
            blogger_name: 博主名称
            step_results: pipeline执行结果

        Returns:
            dict: 调度建议
        """
        results = step_results.get("results", {})
        pipeline = step_results.get("pipeline", {})

        # 分析发布频率
        frequency = self._analyze_frequency(results)

        # 计算下次复采时间
        next_collect_date = self._calc_next_collect(frequency)

        # 生成调度建议
        schedule = {
            "blogger_name": blogger_name,
            "scheduled_at": datetime.now().isoformat(),
            "frequency_analysis": frequency,
            "next_collect_date": next_collect_date,
            "interval_days": self.RECOLLECT_INTERVALS[frequency["tier"]],
            "tier": frequency["tier"],
            "recommendations": self._build_recommendations(frequency),
            "dlq_warning": self._check_dlq_warning(step_results),
        }

        # 写入文件
        schedule_path = os.path.join(
            self.output_dir, f"{blogger_name}_followup_reminder.json"
        )
        with open(schedule_path, "w", encoding="utf-8") as f:
            json.dump(schedule, f, ensure_ascii=False, indent=2)

        print(f"[FollowupScheduler] 生成调度: {schedule_path}")
        return schedule

    def _analyze_frequency(self, results: dict) -> dict:
        """分析博主发布频率"""
        # 从Step1结果中提取笔记数量和时间范围
        step1 = results.get("1") or results.get(1)
        collected = 0
        date_range_days = 90  # 默认90天

        if isinstance(step1, dict):
            collected = step1.get("collected", 0)
            total_list = step1.get("total_list", 0)
            # 估算时间范围（假设每批100条）
            if total_list > 0:
                date_range_days = 90  # 简化：统一按90天估算

        # 计算周均发布量
        weeks = max(1, date_range_days / 7)
        weekly_avg = collected / weeks if weeks > 0 else 0

        # 判断频率等级
        if weekly_avg >= 3:
            tier = "high_frequency"
        elif weekly_avg >= 1:
            tier = "medium_frequency"
        else:
            tier = "low_frequency"

        return {
            "total_notes": collected,
            "date_range_days": date_range_days,
            "weekly_avg": round(weekly_avg, 1),
            "tier": tier,
            "interval_days": self.RECOLLECT_INTERVALS[tier],
        }

    def _calc_next_collect(self, frequency: dict) -> str:
        """计算下次复采日期"""
        from datetime import timedelta

        interval = frequency["interval_days"]
        next_date = datetime.now() + timedelta(days=interval)
        return next_date.strftime("%Y-%m-%d")

    def _build_recommendations(self, frequency: dict) -> list[str]:
        """生成调度建议"""
        tier = frequency["tier"]
        weekly_avg = frequency["weekly_avg"]

        recommendations = []

        if tier == "high_frequency":
            recommendations.append(
                f"高频博主（周均{weekly_avg}篇），建议每周复采一次"
            )
            recommendations.append("关注近期热门笔记和趋势变化")
            recommendations.append("对比内容风格是否有调整")
        elif tier == "medium_frequency":
            recommendations.append(
                f"中频博主（周均{weekly_avg}篇），建议每两周复采一次"
            )
            recommendations.append("关注内容主题是否有新方向")
            recommendations.append("跟踪粉丝互动趋势变化")
        else:
            recommendations.append(
                f"低频博主（周均{weekly_avg}篇），建议每月复采一次"
            )
            recommendations.append("博主可能处于转型期，关注内容变化")
            recommendations.append("评估是否继续跟踪该博主")

        return recommendations

    def _check_dlq_warning(self, step_results: dict) -> Optional[str]:
        """检查DLQ警告"""
        dlq_stats = step_results.get("dlq_stats", {})
        pending = dlq_stats.get("pending", 0)
        if pending > 0:
            return f"⚠️ 有{pending}条失败记录待处理，建议先解决DLQ再安排下次复采"
        return None


# ── Step6主类 ─────────────────────────────────────────────────────────────

class Step6Archiver:
    """
    Step 6 归档/知识持久化管道

    依赖:
      - WikiArchiver
      - PipelineSummary
      - FollowupScheduler

    输入:
      - step_results: pipeline._build_step_results() 产出
        包含 {pipeline, results, errors, dlq_stats}

    处理:
      1. WikiArchiver.archive() → wiki/{blogger_name}/ 目录归档
      2. PipelineSummary.generate() → pipeline_summary.json（含各步骤耗时/成功率）
      3. FollowupScheduler.schedule() → followup_reminder.json（定期复采建议）

    输出:
      - wiki/{blogger_name}/ — Wiki归档目录
      - {blogger_name}_pipeline_summary.json — Pipeline执行摘要
      - {blogger_name}_followup_reminder.json — 后续调度建议
    """

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def archive(self, step_results: dict) -> dict:
        """
        执行归档流程

        Args:
            step_results: pipeline._build_step_results() 产出
                    {
                        "pipeline": {...},
                        "results": {1: {...}, 2: {...}, ...},
                        "errors": {1: "...", ...},
                        "dlq_stats": {...}
                    }

        Returns:
            dict: 归档结果摘要
        """
        pipeline = step_results.get("pipeline", {})
        blogger_name = pipeline.get("blogger_name", "unknown")
        print(f"[Step6Archiver] 开始归档 blogger={blogger_name}")

        # 1. Wiki归档
        wiki_archiver = WikiArchiver(self.output_dir)
        wiki_result = wiki_archiver.archive(blogger_name, step_results)

        # 2. Pipeline摘要
        summary_gen = PipelineSummary()
        summary_gen.output_dir = self.output_dir
        pipeline_summary = summary_gen.generate(blogger_name, step_results)

        # 3. 后续调度
        scheduler = FollowupScheduler()
        scheduler.output_dir = self.output_dir
        followup = scheduler.schedule(blogger_name, step_results)

        # 汇总输出路径
        blogger_name_out = blogger_name
        wiki_dir = wiki_result["wiki_dir"]
        summary_path = os.path.join(self.output_dir, f"{blogger_name_out}_pipeline_summary.json")
        followup_path = os.path.join(self.output_dir, f"{blogger_name_out}_followup_reminder.json")

        print(f"[Step6Archiver] 完成归档")
        print(f"[Step6Archiver] Wiki归档: {wiki_dir}")
        print(f"[Step6Archiver] 摘要: {summary_path}")
        print(f"[Step6Archiver] 调度: {followup_path}")

        return {
            "blogger_name": blogger_name,
            "wiki_dir": wiki_dir,
            "wiki_file_count": wiki_result["file_count"],
            "pipeline_summary_path": summary_path,
            "followup_reminder_path": followup_path,
            "success_rate": pipeline_summary["success_rate"],
            "total_timing_seconds": pipeline_summary["total_timing_seconds"],
            "next_collect_date": followup["next_collect_date"],
            "dlq_pending": pipeline_summary["dlq_stats"].get("pending", 0),
        }
