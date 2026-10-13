#!/usr/bin/env python3
"""
evalite-benchmark CLI 运行器
支持 run/leaderboard/regression 命令
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

import click
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

# 导入统计模块
from statistical import (
    t_test,
    chi_square,
    wilcoxon_test,
    bootstrap_ci,
    compare_models
)


console = Console()


class BenchmarkConfig:
    """Benchmark 配置管理"""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """加载 YAML 配置"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_models(self) -> List[Dict]:
        """获取模型配置"""
        return self.config.get("models", [])

    def get_dataset_path(self) -> str:
        """获取数据集路径"""
        return self.config.get("dataset", {}).get("source", "")

    def get_trials(self) -> int:
        """获取试验次数"""
        return self.config.get("evaluation", {}).get("trials", 5)

    def get_alpha(self) -> float:
        """获取显著性水平"""
        return self.config.get("statistical", {}).get("alpha", 0.05)


class Model:
    """模型定义"""

    def __init__(self, name: str, provider: str, model_id: str, **kwargs):
        self.name = name
        self.provider = provider
        self.model_id = model_id
        self.api_key_env = kwargs.get("api_key_env")
        self.base_url = kwargs.get("base_url")
        self.extra_params = kwargs.get("extra_params", {})

    def __repr__(self):
        return f"Model({self.name}, {self.provider}/{self.model_id})"


class Dataset:
    """数据集定义"""

    def __init__(self, path: str):
        self.path = path
        self.tasks = self._load_tasks()

    def _load_tasks(self) -> List[Dict]:
        """加载任务数据"""
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("tasks", [])

    def __len__(self):
        return len(self.tasks)


class BenchmarkResult:
    """评估结果"""

    def __init__(
        self,
        model: Model,
        task_results: List[Dict],
        metrics: Dict[str, float],
        timestamp: str
    ):
        self.model = model
        self.task_results = task_results
        self.metrics = metrics
        self.timestamp = timestamp

    def to_dict(self) -> dict:
        return {
            "model": {
                "name": self.model.name,
                "provider": self.model.provider,
                "model_id": self.model.model_id
            },
            "metrics": self.metrics,
            "timestamp": self.timestamp
        }


def load_results(results_dir: Path) -> List[BenchmarkResult]:
    """加载已有结果"""
    results = []

    for json_file in results_dir.glob("*.json"):
        if json_file.name == "baseline.json":
            continue

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        model_data = data.get("model", {})
        model = Model(
            name=model_data.get("name", ""),
            provider=model_data.get("provider", ""),
            model_id=model_data.get("model_id", "")
        )

        result = BenchmarkResult(
            model=model,
            task_results=data.get("task_results", []),
            metrics=data.get("metrics", {}),
            timestamp=data.get("timestamp", "")
        )
        results.append(result)

    return results


def simulate_evaluation(model: Model, dataset: Dataset, trials: int) -> BenchmarkResult:
    """
    模拟评估（实际实现需要调用 LLM API）
    这里用随机结果模拟
    """
    import random
    import time

    task_results = []
    scores = []

    for task in dataset.tasks:
        # 模拟 API 调用延迟
        time.sleep(0.1)

        # 模拟评分（实际应该调用 LLM）
        score = random.uniform(0.7, 0.95)
        scores.append(score)

        task_results.append({
            "task_id": task.get("id", ""),
            "score": score,
            "latency_ms": random.randint(500, 2000),
            "cost": random.uniform(0.001, 0.01)
        })

    metrics = {
        "accuracy": sum(scores) / len(scores),
        "avg_latency_ms": sum(r.get("latency_ms", 0) for r in task_results) / len(task_results),
        "avg_cost": sum(r.get("cost", 0) for r in task_results) / len(task_results),
        "total_cost": sum(r.get("cost", 0) for r in task_results)
    }

    return BenchmarkResult(
        model=model,
        task_results=task_results,
        metrics=metrics,
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
    )


def run_benchmark(config: BenchmarkConfig, models: List[Model], dataset: Dataset) -> List[BenchmarkResult]:
    """运行 benchmark 评估"""
    console.print(Panel.fit("[bold cyan]LLM Benchmark 评估系统[/bold cyan]"))

    results = []
    trials = config.get_trials()

    for model in models:
        console.print(f"\n[yellow]评估模型: {model.name}[/yellow]")

        model_results = []
        for trial in range(trials):
            console.print(f"  Trial {trial + 1}/{trials}...")
            result = simulate_evaluation(model, dataset, trials)
            model_results.append(result)

        # 汇总多次试验结果
        avg_metrics = {
            "accuracy": sum(r.metrics["accuracy"] for r in model_results) / trials,
            "avg_latency_ms": sum(r.metrics["avg_latency_ms"] for r in model_results) / trials,
            "avg_cost": sum(r.metrics["avg_cost"] for r in model_results) / trials
        }

        # 创建汇总结果
        all_task_results = []
        for r in model_results:
            all_task_results.extend(r.task_results)

        summary_result = BenchmarkResult(
            model=model,
            task_results=all_task_results,
            metrics=avg_metrics,
            timestamp=model_results[-1].timestamp
        )
        results.append(summary_result)

        console.print(f"  ✓ 准确率: {avg_metrics['accuracy']:.2%}")

    return results


def save_results(results: List[BenchmarkResult], output_dir: Path) -> None:
    """保存结果到文件"""
    output_dir.mkdir(parents=True, exist_ok=True)

    for result in results:
        filename = f"{result.model.name.replace(' ', '_').lower()}_results.json"
        filepath = output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

    console.print(f"\n✓ 结果已保存到: {output_dir}")


def display_leaderboard(results: List[BenchmarkResult]) -> None:
    """显示排行榜"""
    # 按准确率排序
    sorted_results = sorted(results, key=lambda r: r.metrics["accuracy"], reverse=True)

    table = Table(title="📊 LLM Benchmark 排行榜", show_header=True, header_style="bold cyan")
    table.add_column("排名", justify="center", style="bold")
    table.add_column("模型", style="cyan")
    table.add_column("准确率", justify="right")
    table.add_column("延迟(ms)", justify="right")
    table.add_column("成本($/1K)", justify="right")
    table.add_column("综合得分", justify="right")

    # 计算综合得分
    # 公式: 0.5×准确率 + 0.3×(1/延迟标准化) + 0.2×(1/成本标准化)
    max_latency = max(r.metrics["avg_latency_ms"] for r in sorted_results)
    max_cost = max(r.metrics["avg_cost"] for r in sorted_results)

    for i, result in enumerate(sorted_results, 1):
        latency_score = 1 - (result.metrics["avg_latency_ms"] / max_latency) if max_latency > 0 else 0
        cost_score = 1 - (result.metrics["avg_cost"] / max_cost) if max_cost > 0 else 0
        composite = 0.5 * result.metrics["accuracy"] + 0.3 * latency_score + 0.2 * cost_score

        table.add_row(
            f"#{i}",
            result.model.name,
            f"{result.metrics['accuracy']:.1%}",
            f"{result.metrics['avg_latency_ms']:.0f}",
            f"${result.metrics['avg_cost']:.4f}",
            f"{composite:.2f}"
        )

    console.print(table)

    # 统计显著性检验
    if len(sorted_results) >= 2:
        console.print("\n[bold]统计显著性检验 (α=0.05)[/bold]")
        compare_models(sorted_results, console)


def display_regression(current_results: List[BenchmarkResult], baseline_file: Path) -> None:
    """显示回归检测结果"""
    if not baseline_file.exists():
        console.print(f"[red]基准文件不存在: {baseline_file}[/red]")
        return

    with open(baseline_file, "r", encoding="utf-8") as f:
        baseline_data = json.load(f)

    console.print(Panel.fit("[bold red]回归检测报告[/bold red]"))

    for current in current_results:
        baseline_metrics = baseline_data.get(current.model.name, {}).get("metrics", {})
        baseline_accuracy = baseline_metrics.get("accuracy", 0)
        current_accuracy = current.metrics["accuracy"]

        change = (current_accuracy - baseline_accuracy) / baseline_accuracy if baseline_accuracy > 0 else 0
        threshold = 0.05

        if change < -threshold:
            status = "[red]🔴 回归[/red]"
        elif change > threshold:
            status = "[green]🟢 提升[/green]"
        else:
            status = "[yellow]🟡 稳定[/yellow]"

        console.print(f"{status} {current.model.name}: {baseline_accuracy:.1%} → {current_accuracy:.1%} ({(change*100):+.1f}%)")


@click.group()
def cli():
    """evalite-benchmark CLI"""
    pass


@cli.command()
@click.option("--config", "-c", required=True, type=Path, help="配置文件路径")
@click.option("--models", "-m", multiple=True, help="指定模型名称")
@click.option("--output", "-o", type=Path, default=Path("./results"), help="输出目录")
def run(config: Path, models: List[str], output: Path):
    """运行 benchmark 评估"""
    cfg = BenchmarkConfig(config)

    # 加载数据集
    dataset_path = cfg.get_dataset_path()
    dataset = Dataset(dataset_path)
    console.print(f"📦 加载数据集: {len(dataset)} 个任务")

    # 加载模型
    model_configs = cfg.get_models()
    model_list = [
        Model(
            name=m.get("name", ""),
            provider=m.get("provider", ""),
            model_id=m.get("model_id", ""),
            api_key_env=m.get("api_key_env"),
            base_url=m.get("base_url")
        )
        for m in model_configs
        if not models or m.get("name") in models
    ]

    console.print(f"🤖 模型数量: {len(model_list)}")

    # 运行评估
    results = run_benchmark(cfg, model_list, dataset)

    # 保存结果
    save_results(results, output)

    # 显示排行榜
    display_leaderboard(results)


@cli.command()
@click.option("--results", "-r", type=Path, default=Path("./results"), help="结果目录")
@click.option("--format", "-f", type=click.Choice(["table", "json", "markdown"]), default="table")
def leaderboard(results: Path, format: str):
    """显示排行榜"""
    loaded_results = load_results(results)

    if not loaded_results:
        console.print("[yellow]没有找到评估结果[/yellow]")
        return

    if format == "table":
        display_leaderboard(loaded_results)
    elif format == "json":
        console.print_json(data=[r.to_dict() for r in loaded_results])
    elif format == "markdown":
        for r in sorted(loaded_results, key=lambda x: x.metrics["accuracy"], reverse=True):
            console.print(f"- **{r.model.name}**: {r.metrics['accuracy']:.1%}")


@cli.command()
@click.option("--baseline", "-b", type=Path, required=True, help="基准结果文件")
@click.option("--current", "-c", type=Path, required=True, help="当前结果目录")
def regression(baseline: Path, current: Path):
    """检测性能回归"""
    current_results = load_results(current)
    display_regression(current_results, baseline)


if __name__ == "__main__":
    cli()