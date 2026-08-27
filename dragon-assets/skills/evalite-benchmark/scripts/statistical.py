#!/usr/bin/env python3
"""
evalite-benchmark 统计检验模块
支持 t-test, chi-square, Wilcoxon, Bootstrap CI
"""

from typing import List, Dict, Tuple, Optional
import math

import numpy as np
from scipy import stats
from rich.console import Console


console = Console()


def t_test(
    scores_a: List[float],
    scores_b: List[float],
    alpha: float = 0.05
) -> Dict:
    """
    独立样本 t 检验，比较两个模型的准确率

    Args:
        scores_a: 模型A的分数列表
        scores_b: 模型B的分数列表
        alpha: 显著性水平

    Returns:
        包含统计结果的字典
    """
    if len(scores_a) < 2 or len(scores_b) < 2:
        return {"error": "样本量不足，需要至少2个样本"}

    t_stat, p_value = stats.ttest_ind(scores_a, scores_b)

    mean_a = np.mean(scores_a)
    mean_b = np.mean(scores_b)
    diff = mean_a - mean_b

    # 计算置信区间
    n_a, n_b = len(scores_a), len(scores_b)
    se = np.sqrt(np.var(scores_a)/n_a + np.var(scores_b)/n_b)
    df = ((np.var(scores_a)/n_a + np.var(scores_b)/n_b)**2) / \
         ((np.var(scores_a)/n_a)**2/(n_a-1) + (np.var(scores_b)/n_b)**2/(n_b-1))
    t_crit = stats.t.ppf(1 - alpha/2, df)
    ci_lower = diff - t_crit * se
    ci_upper = diff + t_crit * se

    return {
        "significant": p_value < alpha,
        "p_value": p_value,
        "t_stat": t_stat,
        "mean_a": mean_a,
        "mean_b": mean_b,
        "difference": diff,
        "ci_95": (ci_lower, ci_upper),
        "alpha": alpha
    }


def chi_square(
    passes_a: int,
    total_a: int,
    passes_b: int,
    total_b: int,
    alpha: float = 0.05
) -> Dict:
    """
    卡方检验，比较两个模型的通过率

    Args:
        passes_a: 模型A通过数
        total_a: 模型A总数
        passes_b: 模型B通过数
        total_b: 模型B总数
        alpha: 显著性水平

    Returns:
        包含统计结果的字典
    """
    # 构建列联表
    contingency = [
        [passes_a, total_a - passes_a],
        [passes_b, total_b - passes_b]
    ]

    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

    rate_a = passes_a / total_a if total_a > 0 else 0
    rate_b = passes_b / total_b if total_b > 0 else 0

    return {
        "significant": p_value < alpha,
        "p_value": p_value,
        "chi2_stat": chi2,
        "dof": dof,
        "pass_rate_a": rate_a,
        "pass_rate_b": rate_b,
        "difference": rate_a - rate_b,
        "alpha": alpha
    }


def wilcoxon_test(
    scores_a: List[float],
    scores_b: List[float],
    alpha: float = 0.05
) -> Dict:
    """
    Wilcoxon 符号秩检验，配对样本比较（非正态分布数据）

    Args:
        scores_a: 模型A的分数列表（与scores_b一一对应）
        scores_b: 模型B的分数列表
        alpha: 显著性水平

    Returns:
        包含统计结果的字典
    """
    if len(scores_a) != len(scores_b):
        return {"error": "样本数量不匹配"}

    if len(scores_a) < 5:
        return {"error": "样本量不足，需要至少5个配对样本"}

    # 计算差值
    diffs = np.array(scores_a) - np.array(scores_b)

    # Wilcoxon 符号秩检验
    statistic, p_value = stats.wilcoxon(diffs)

    mean_a = np.mean(scores_a)
    mean_b = np.mean(scores_b)

    return {
        "significant": p_value < alpha,
        "p_value": p_value,
        "statistic": statistic,
        "mean_a": mean_a,
        "mean_b": mean_b,
        "difference": mean_a - mean_b,
        "alpha": alpha
    }


def bootstrap_ci(
    scores: List[float],
    confidence: float = 0.95,
    n_iterations: int = 10000,
    seed: Optional[int] = None
) -> Tuple[float, float]:
    """
    Bootstrap 置信区间估计

    Args:
        scores: 分数列表
        confidence: 置信水平（默认95%）
        n_iterations: 迭代次数
        seed: 随机种子

    Returns:
        置信区间 (lower, upper)
    """
    if seed is not None:
        np.random.seed(seed)

    scores_arr = np.array(scores)
    n = len(scores_arr)

    bootstrap_means = []
    for _ in range(n_iterations):
        # 有放回抽样
        sample = np.random.choice(scores_arr, size=n, replace=True)
        bootstrap_means.append(np.mean(sample))

    # 计算置信区间
    alpha = 1 - confidence
    lower = np.percentile(bootstrap_means, alpha/2 * 100)
    upper = np.percentile(bootstrap_means, (1 - alpha/2) * 100)

    return (lower, upper)


def bootstrap_difference_ci(
    scores_a: List[float],
    scores_b: List[float],
    confidence: float = 0.95,
    n_iterations: int = 10000,
    seed: Optional[int] = None
) -> Tuple[float, float]:
    """
    Bootstrap 差值置信区间

    Args:
        scores_a: 模型A分数
        scores_b: 模型B分数
        confidence: 置信水平
        n_iterations: 迭代次数
        seed: 随机种子

    Returns:
        差值置信区间 (lower, upper)
    """
    if seed is not None:
        np.random.seed(seed)

    scores_a_arr = np.array(scores_a)
    scores_b_arr = np.array(scores_b)

    n_a, n_b = len(scores_a_arr), len(scores_b_arr)

    bootstrap_diffs = []
    for _ in range(n_iterations):
        sample_a = np.random.choice(scores_a_arr, size=n_a, replace=True)
        sample_b = np.random.choice(scores_b_arr, size=n_b, replace=True)
        bootstrap_diffs.append(np.mean(sample_a) - np.mean(sample_b))

    alpha = 1 - confidence
    lower = np.percentile(bootstrap_diffs, alpha/2 * 100)
    upper = np.percentile(bootstrap_diffs, (1 - alpha/2) * 100)

    return (lower, upper)


def compare_models(results: List, console: Optional[Console] = None) -> Dict:
    """
    比较多个模型的性能

    Args:
        results: BenchmarkResult 列表
        console: Rich console 用于输出

    Returns:
        比较结果字典
    """
    if not console:
        console = Console()

    if len(results) < 2:
        return {"error": "需要至少2个模型进行比较"}

    # 按准确率排序
    sorted_results = sorted(results, key=lambda r: r.metrics["accuracy"], reverse=True)

    comparisons = []

    for i in range(len(sorted_results)):
        for j in range(i + 1, len(sorted_results)):
            model_a = sorted_results[i]
            model_b = sorted_results[j]

            # 提取分数（这里用准确率作为分数）
            scores_a = [r.metrics["accuracy"] for r in [model_a]]
            scores_b = [r.metrics["accuracy"] for r in [model_b]]

            # 获取每个任务的分数
            task_scores_a = [tr["score"] for tr in model_a.task_results]
            task_scores_b = [tr["score"] for tr in model_b.task_results]

            # t-test
            t_result = t_test(task_scores_a, task_scores_b)

            # Bootstrap CI for difference
            diff_ci = bootstrap_difference_ci(task_scores_a, task_scores_b)

            winner = model_a.model.name if t_result["significant"] and t_result["mean_a"] > t_result["mean_b"] else None

            comparison = {
                "model_a": model_a.model.name,
                "model_b": model_b.model.name,
                "accuracy_a": model_a.metrics["accuracy"],
                "accuracy_b": model_b.metrics["accuracy"],
                "p_value": t_result["p_value"],
                "significant": t_result["significant"],
                "ci_95_diff": diff_ci,
                "winner": winner
            }
            comparisons.append(comparison)

            # 输出结果
            sig_mark = "✓" if t_result["significant"] else "✗"
            console.print(
                f"  {sig_mark} {model_a.model.name} vs {model_b.model.name}: "
                f"p={t_result['p_value']:.4f}, "
                f"差异={t_result['difference']:.2%}, "
                f"CI=[{diff_ci[0]:.2%}, {diff_ci[1]:.2%}]"
            )

    return {
        "comparisons": comparisons,
        "sorted_models": [r.model.name for r in sorted_results]
    }


def effect_sizeCohen(scores_a: List[float], scores_b: List[float]) -> float:
    """
    计算 Cohen's d 效应量

    Args:
        scores_a: 组A分数
        scores_b: 组B分数

    Returns:
        Cohen's d 值
    """
    mean_a = np.mean(scores_a)
    mean_b = np.mean(scores_b)

    # 合并标准差
    n_a, n_b = len(scores_a), len(scores_b)
    var_a = np.var(scores_a, ddof=1)
    var_b = np.var(scores_b, ddof=1)

    pooled_std = np.sqrt(((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2))

    if pooled_std == 0:
        return 0.0

    return (mean_a - mean_b) / pooled_std


def interpret_effect_size(d: float) -> str:
    """
    解释 Cohen's d 效应量

    Args:
        d: Cohen's d 值

    Returns:
        效应量描述
    """
    abs_d = abs(d)
    if abs_d < 0.2:
        return "可忽略"
    elif abs_d < 0.5:
        return "小效应"
    elif abs_d < 0.8:
        return "中等效应"
    else:
        return "大效应"


def generate_report(results: List, alpha: float = 0.05) -> str:
    """
    生成统计报告

    Args:
        results: BenchmarkResult 列表
        alpha: 显著性水平

    Returns:
        Markdown 格式报告
    """
    sorted_results = sorted(results, key=lambda r: r.metrics["accuracy"], reverse=True)

    lines = [
        "# LLM Benchmark 统计报告",
        "",
        f"**显著性水平**: α = {alpha}",
        "",
        "## 模型排名",
        "",
        "| 排名 | 模型 | 准确率 | 延迟(ms) | 成本($/1K) |",
        "|------|------|--------|----------|-----------|"
    ]

    for i, r in enumerate(sorted_results, 1):
        lines.append(
            f"| {i} | {r.model.name} | {r.metrics['accuracy']:.1%} | "
            f"{r.metrics['avg_latency_ms']:.0f} | ${r.metrics['avg_cost']:.4f} |"
        )

    lines.append("")

    if len(sorted_results) >= 2:
        lines.append("## 统计显著性检验")
        lines.append("")

        task_scores = {}
        for r in sorted_results:
            task_scores[r.model.name] = [tr["score"] for tr in r.task_results]

        for i in range(len(sorted_results)):
            for j in range(i + 1, len(sorted_results)):
                name_a = sorted_results[i].model.name
                name_b = sorted_results[j].model.name

                scores_a = task_scores[name_a]
                scores_b = task_scores[name_b]

                t_result = t_test(scores_a, scores_b, alpha)
                diff_ci = bootstrap_difference_ci(scores_a, scores_b)

                effect = effect_sizeCohen(scores_a, scores_b)
                effect_interp = interpret_effect_size(effect)

                winner = "无显著差异" if not t_result["significant"] else (
                    name_a if t_result["mean_a"] > t_result["mean_b"] else name_b
                )

                lines.append(f"### {name_a} vs {name_b}")
                lines.append("")
                lines.append(f"- **t检验**: t = {t_result['t_stat']:.3f}, p = {t_result['p_value']:.4f}")
                lines.append(f"- **显著性**: {'是' if t_result['significant'] else '否'} (α = {alpha})")
                lines.append(f"- **差异**: {t_result['difference']:.2%}")
                lines.append(f"- **95% CI**: [{diff_ci[0]:.2%}, {diff_ci[1]:.2%}]")
                lines.append(f"- **效应量**: Cohen's d = {effect:.3f} ({effect_interp})")
                lines.append(f"- **胜者**: {winner}")
                lines.append("")

    return "\n".join(lines)


# 导出主要函数
__all__ = [
    "t_test",
    "chi_square",
    "wilcoxon_test",
    "bootstrap_ci",
    "bootstrap_difference_ci",
    "compare_models",
    "effect_sizeCohen",
    "interpret_effect_size",
    "generate_report"
]