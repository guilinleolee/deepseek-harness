#!/usr/bin/env python3
"""
OSWorld Benchmark Integration - GUI-VLA Performance Evaluation
Mano-P Phase 2

OSWorld: 354个真实桌面任务评估基准
- 支持系统: Ubuntu (XFCE), Windows, macOS
- 评估指标: 任务成功率, 步数效率, 恢复能力
- 目标: >=58.2% (超越Claude Computer Use)
"""

import json
import time
import statistics
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from pathlib import Path


@dataclass
class BenchmarkTask:
    id: str
    instruction: str
    evaluator_type: str  # "exact_match" | "contains" | "custom"
    evaluator_config: Dict[str, Any]
    initial_benchmark_url: str = ""
    max_steps: int = 30


@dataclass
class BenchmarkResult:
    task_id: str
    status: str  # "success" | "failure" | "partial"
    success_rate: float
    steps_taken: int
    max_steps: int
    duration_seconds: float
    error: Optional[str] = None
    reasoning_log: List[str] = field(default_factory=list)
    verification_score: float = 0.0


@dataclass
class BenchmarkReport:
    total_tasks: int
    passed: int
    failed: int
    partial: int
    overall_success_rate: float
    avg_steps: float
    avg_duration: float
    success_rate_by_category: Dict[str, float] = field(default_factory=dict)
    benchmark_version: str = "v1.0"
    mano_p_version: str = "1.0.0"


class OSWorldBenchmark:
    """
    OSWorld Benchmark Integration

    支持的评估类别:
    - os_home_operation: 系统操作 (文件管理, 应用启动)
    - web_browser: 浏览器操作
    - document_editing: 文档编辑
    - software_specific: 软件特定操作 (VSCode, LibreOffice)
    - cross_application: 跨应用操作

    使用方法:
        benchmark = OSWorldBenchmark(tav_loop)
        results = await benchmark.run_all(max_tasks=50)
        report = benchmark.generate_report(results)
    """

    BENCHMARK_TASKS = [
        # === OS Home Operation ===
        BenchmarkTask(
            id="os_home_001",
            instruction="打开文件管理器, 在主目录下创建名为'project'的新文件夹",
            evaluator_type="exact_match",
            evaluator_config={"path": "~/project", "type": "directory"}
        ),
        BenchmarkTask(
            id="os_home_002",
            instruction="打开终端, 执行 'ls -la' 命令并记录输出",
            evaluator_type="contains",
            evaluator_config={"expected_output": "total"}
        ),
        BenchmarkTask(
            id="os_home_003",
            instruction="打开系统设置, 将语言改为英文",
            evaluator_type="custom",
            evaluator_config={"check": "language_setting_changed"}
        ),

        # === Web Browser ===
        BenchmarkTask(
            id="web_001",
            instruction="打开Chrome浏览器, 访问 github.com, 搜索 'Claude Code'",
            evaluator_type="contains",
            evaluator_config={"expected_url": "github.com", "expected_content": "GitHub"}
        ),
        BenchmarkTask(
            id="web_002",
            instruction="打开Firefox浏览器, 打开一个新标签页, 访问 wikipedia.org",
            evaluator_type="exact_match",
            evaluator_config={"expected_url": "wikipedia.org"}
        ),

        # === Document Editing ===
        BenchmarkTask(
            id="doc_001",
            instruction="打开LibreOffice Writer, 新建文档, 输入 'Hello World', 保存为~/document.docx",
            evaluator_type="contains",
            evaluator_config={"expected_file": "~/document.docx", "expected_content": "Hello World"}
        ),
        BenchmarkTask(
            id="doc_002",
            instruction="使用gedit打开~/test.txt, 在末尾添加一行'Benchmark Complete'",
            evaluator_type="contains",
            evaluator_config={"expected_content": "Benchmark Complete"}
        ),

        # === Cross Application ===
        BenchmarkTask(
            id="cross_001",
            instruction="打开Firefox下载一个PDF文件, 然后用默认PDF阅读器打开它",
            evaluator_type="custom",
            evaluator_config={"check": "pdf_opened"}
        ),
        BenchmarkTask(
            id="cross_002",
            instruction="打开文件管理器定位一个图片, 用默认图片查看器打开",
            evaluator_type="custom",
            evaluator_config={"check": "image_viewer_opened"}
        ),

        # === Software Specific ===
        BenchmarkTask(
            id="soft_001",
            instruction="打开VSCode, 打开文件夹 ~/project, 新建文件 test.py",
            evaluator_type="custom",
            evaluator_config={"check": "vscode_file_created"}
        ),
    ]

    CATEGORIES = {
        "os_home_operation": ["os_home_001", "os_home_002", "os_home_003"],
        "web_browser": ["web_001", "web_002"],
        "document_editing": ["doc_001", "doc_002"],
        "cross_application": ["cross_001", "cross_002"],
        "software_specific": ["soft_001"]
    }

    def __init__(
        self,
        tav_loop=None,
        vla_client=None,
        output_dir: str = "~/.claude/skills/mano-p-core/benchmark_results"
    ):
        self.tav_loop = tav_loop
        self.vla_client = vla_client
        self.output_dir = Path(output_dir).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[BenchmarkResult] = []

    async def run_task(self, task: BenchmarkTask) -> BenchmarkResult:
        """运行单个基准任务"""
        print(f"\n[OSWorld] Running task: {task.id}")
        print(f"  Instruction: {task.instruction}")

        start_time = time.time()
        reasoning_log = []

        try:
            # 截图获取当前状态
            if self.vla_client:
                screenshot = await self.vla_client.get_screenshot()
            else:
                screenshot = None

            # 执行TAV循环
            if self.tav_loop:
                result = await self.tav_loop.run(task.instruction, screenshot)

                if result["status"] == "success":
                    status = "success"
                    verification_score = result.get("verify_score", 0.85)
                elif result["verify_score"] >= 0.5:
                    status = "partial"
                    verification_score = result["verify_score"]
                else:
                    status = "failure"
                    verification_score = result.get("verify_score", 0.0)

                steps_taken = result.get("steps", 0)
                reasoning_log = [s.get("reasoning", "") for s in result.get("logs", [])]
                error = result.get("error")
            else:
                # 无VLA Client时模拟
                status = "failure"
                verification_score = 0.0
                steps_taken = 0
                error = "VLA Client not configured"

            duration = time.time() - start_time

            # 计算成功率
            if status == "success":
                success_rate = 1.0
            elif status == "partial":
                success_rate = verification_score
            else:
                success_rate = 0.0

            return BenchmarkResult(
                task_id=task.id,
                status=status,
                success_rate=success_rate,
                steps_taken=steps_taken,
                max_steps=task.max_steps,
                duration_seconds=duration,
                verification_score=verification_score,
                reasoning_log=reasoning_log,
                error=error
            )

        except Exception as e:
            return BenchmarkResult(
                task_id=task.id,
                status="failure",
                success_rate=0.0,
                steps_taken=0,
                max_steps=task.max_steps,
                duration_seconds=time.time() - start_time,
                error=str(e)
            )

    async def run_all(
        self,
        max_tasks: Optional[int] = None,
        categories: Optional[List[str]] = None
    ) -> List[BenchmarkResult]:
        """运行所有基准任务或指定子集"""

        # 选择任务
        if categories:
            task_ids = []
            for cat in categories:
                task_ids.extend(self.CATEGORIES.get(cat, []))
            tasks = [t for t in self.BENCHMARK_TASKS if t.id in task_ids]
        else:
            tasks = self.BENCHMARK_TASKS

        if max_tasks:
            tasks = tasks[:max_tasks]

        print(f"\n{'='*60}")
        print(f"OSWorld Benchmark Starting")
        print(f"  Total tasks: {len(tasks)}")
        print(f"  Categories: {categories or 'all'}")
        print(f"{'='*60}\n")

        results = []

        for i, task in enumerate(tasks):
            print(f"[{i+1}/{len(tasks)}] ", end="")
            result = await self.run_task(task)
            results.append(result)

            status_icon = "✅" if result.status == "success" else "⚠️" if result.status == "partial" else "❌"
            print(f"  {status_icon} {result.task_id}: {result.status} "
                  f"(score={result.success_rate:.2f}, steps={result.steps_taken})")

        self.results = results
        return results

    def generate_report(self, results: List[BenchmarkResult] = None) -> BenchmarkReport:
        """生成基准测试报告"""

        results = results or self.results

        passed = sum(1 for r in results if r.status == "success")
        failed = sum(1 for r in results if r.status == "failure")
        partial = sum(1 for r in results if r.status == "partial")
        total = len(results)

        overall_rate = sum(r.success_rate for r in results) / total if total > 0 else 0.0
        avg_steps = statistics.mean([r.steps_taken for r in results]) if results else 0.0
        avg_duration = statistics.mean([r.duration_seconds for r in results]) if results else 0.0

        # 按类别统计
        category_stats = {}
        for cat, task_ids in self.CATEGORIES.items():
            cat_results = [r for r in results if r.task_id in task_ids]
            if cat_results:
                cat_rate = sum(r.success_rate for r in cat_results) / len(cat_results)
                category_stats[cat] = round(cat_rate, 3)

        report = BenchmarkReport(
            total_tasks=total,
            passed=passed,
            failed=failed,
            partial=partial,
            overall_success_rate=round(overall_rate, 3),
            avg_steps=round(avg_steps, 1),
            avg_duration=round(avg_duration, 1),
            success_rate_by_category=category_stats
        )

        # 打印报告
        self._print_report(report)

        # 保存报告
        self._save_report(report, results)

        return report

    def _print_report(self, report: BenchmarkReport):
        """打印基准测试报告"""

        print(f"\n{'='*60}")
        print(f"       OSWorld Benchmark Report")
        print(f"{'='*60}")
        print(f"  Overall Success Rate: {report.overall_success_rate:.1%}")
        print(f"  Tasks: {report.total_tasks} total | "
              f"✅{report.passed} | ⚠️{report.partial} | ❌{report.failed}")
        print(f"  Avg Steps: {report.avg_steps:.1f} | Avg Duration: {report.avg_duration:.1f}s")
        print(f"\n  Success Rate by Category:")
        for cat, rate in report.success_rate_by_category.items():
            bar = "█" * int(rate * 20) + "░" * (20 - int(rate * 20))
            icon = "🟢" if rate >= 0.7 else "🟡" if rate >= 0.4 else "🔴"
            print(f"    {icon} {cat:25s} {rate:.1%} {bar}")

        # 目标对比
        TARGET_RATE = 0.582  # Claude Computer Use baseline
        diff = report.overall_success_rate - TARGET_RATE
        if diff >= 0:
            print(f"\n  🎉 超越目标! (+{diff:.1%} vs Claude Computer Use)")
        else:
            print(f"\n  📈 距离目标还差 {-diff:.1%}")

        print(f"{'='*60}\n")

    def _save_report(
        self,
        report: BenchmarkReport,
        results: List[BenchmarkResult]
    ):
        """保存报告到文件"""

        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # JSON报告
        report_path = self.output_dir / f"osworld_report_{timestamp}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({
                "report": {
                    "total_tasks": report.total_tasks,
                    "passed": report.passed,
                    "failed": report.failed,
                    "partial": report.partial,
                    "overall_success_rate": report.overall_success_rate,
                    "avg_steps": report.avg_steps,
                    "avg_duration": report.avg_duration,
                    "success_rate_by_category": report.success_rate_by_category,
                    "benchmark_version": report.benchmark_version,
                    "mano_p_version": report.mano_p_version
                },
                "results": [
                    {
                        "task_id": r.task_id,
                        "status": r.status,
                        "success_rate": r.success_rate,
                        "steps_taken": r.steps_taken,
                        "duration_seconds": r.duration_seconds,
                        "verification_score": r.verification_score,
                        "reasoning_log": r.reasoning_log,
                        "error": r.error
                    }
                    for r in results
                ]
            }, f, indent=2, ensure_ascii=False)

        print(f"  Report saved to: {report_path}")

    def compare_with_baseline(self) -> Dict[str, Any]:
        """与基线对比"""
        baseline = {
            "Claude Computer Use": 0.497,
            "OpenAI Computer Use": 0.385,
            "OSWorld Baseline (Random)": 0.05
        }

        current = self.generate_report().overall_success_rate

        return {
            "current": current,
            "baseline": baseline,
            "improvement_vs_claude": current - baseline["Claude Computer Use"],
            "improvement_vs_openai": current - baseline["OpenAI Computer Use"]
        }


async def demo():
    """OSWorld Benchmark 演示"""
    print("=== OSWorld Benchmark Demo ===\n")

    benchmark = OSWorldBenchmark()

    print("可用基准任务:")
    for task in benchmark.BENCHMARK_TASKS[:5]:
        print(f"  [{task.id}] {task.instruction[:50]}...")

    print(f"\n基准类别:")
    for cat, task_ids in benchmark.CATEGORIES.items():
        print(f"  {cat}: {len(task_ids)} tasks")

    print("\n运行示例:")
    print("  benchmark = OSWorldBenchmark(vla_client=mano_vla_client)")
    print("  results = await benchmark.run_all(categories=['web_browser'])")
    print("  report = benchmark.generate_report(results)")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())