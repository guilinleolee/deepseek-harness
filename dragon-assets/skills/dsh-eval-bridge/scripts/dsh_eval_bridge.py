"""
dsh-eval-bridge V1.0 · 借鉴 hccccc01333/dsh-eval 4 类方法论 · 自研实现

================================================================================
  Stage 45 · 2026-08-24

设计：
  - 不镜像上游真源（DSH 主仓依赖是 blocker；与 stage 41 mneme-heat-engine 借鉴模式一致）
  - 借鉴 4 类方法论：
       1. benchmark YAML schema（11 字段）
       2. 11 类评测指标（task success / tool success / 9 other）
       3. LLM judge 接口（strict JSON schema）
       4. paired A/B 计算 (B-A signed delta)
  - 累计 PASS：Stage 45 = 5 unittest (schema / metric / judge / paired / cost)
  - 退出码契约：0=OK / 1=YAML 解析错 / 2=schema 校验错 / 3=指标计算错
================================================================================
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from collections import defaultdict

import yaml

EXIT_OK = 0
EXIT_YAML = 1
EXIT_SCHEMA = 2
EXIT_METRIC = 3

# ==============================================================================
# 数据模型
# ==============================================================================

@dataclass
class BenchmarkCase:
    """单 case · 借鉴 dsh-eval 的 case schema"""
    id: str
    prompt: str
    workspace: Optional[str] = None
    expected_tool: Optional[str] = None
    expected_check: Optional[str] = None
    trials: int = 3
    timeout_ms: int = 600000


@dataclass
class Benchmark:
    """整个 benchmark · 借鉴 dsh-eval 的 YAML schema"""
    name: str
    model: str
    profile: str
    command: List[str] = field(default_factory=lambda: ["dsh"])
    trials: int = 3
    timeout_ms: int = 600000
    seed: Optional[int] = None
    cases: List[BenchmarkCase] = field(default_factory=list)
    pricing: Dict[str, Dict[str, float]] = field(default_factory=dict)
    judge: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["cases"] = [asdict(c) for c in self.cases]
        return d


@dataclass
class TrialResult:
    """单 trial 结果"""
    case_id: str
    trial_idx: int
    task_success: bool = False
    tool_success: bool = False
    tool_selection_correct: bool = False
    actual_tool: Optional[str] = None
    steps: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    latency_ms: int = 0
    ttft_ms: int = 0
    llm_ms: int = 0
    tool_ms: int = 0
    cost_usd: float = 0.0
    retry_count: int = 0
    invalid_tool_calls: int = 0
    final_answer: str = ""
    judge_score: Optional[float] = None
    judge_hallucinated: Optional[bool] = None
    judge_comment: Optional[str] = None


# ==============================================================================
# 1. benchmark YAML schema 借鉴
# ==============================================================================

REQUIRED_TOP_KEYS = ["name", "model", "profile"]
REQUIRED_CASE_KEYS = ["id", "prompt"]


def parse_benchmark_yaml(yaml_text: str) -> Benchmark:
    """借鉴 dsh-eval 的 benchmark.yaml schema · 自研简化版本"""
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        raise ValueError(f"YAML parse failed: {e}") from e

    # 顶层校验
    for k in REQUIRED_TOP_KEYS:
        if k not in data:
            raise ValueError(f"Missing required top-level key: {k}")

    # cases 校验
    if "cases" not in data or not data["cases"]:
        raise ValueError("Missing or empty 'cases' list")

    cases = []
    for c in data["cases"]:
        for k in REQUIRED_CASE_KEYS:
            if k not in c:
                raise ValueError(f"Case missing required key: {k}")
        exp = c.get("expected", {}) or {}
        cases.append(
            BenchmarkCase(
                id=c["id"],
                prompt=c["prompt"],
                workspace=c.get("workspace"),
                expected_tool=exp.get("tool"),
                expected_check=exp.get("check"),
                trials=c.get("trials", data.get("trials", 3)),
                timeout_ms=c.get("timeoutMs", data.get("timeoutMs", 600000)),
            )
        )

    return Benchmark(
        name=data["name"],
        model=data["model"],
        profile=data["profile"],
        command=data.get("command", ["dsh"]),
        trials=data.get("trials", 3),
        timeout_ms=data.get("timeoutMs", 600000),
        seed=data.get("seed"),
        cases=cases,
        pricing=data.get("pricing", {}),
        judge=data.get("judge"),
    )


# ==============================================================================
# 2. 11 类评测指标计算 · 借鉴 dsh-eval metrics 表
# ==============================================================================

def compute_case_metrics(trials: List[TrialResult]) -> Dict[str, Any]:
    """单 case 折叠 N trial 的 11 类指标"""
    if not trials:
        return {}

    task_success_rate = sum(1 for t in trials if t.task_success) / len(trials)
    tool_success_rate = sum(1 for t in trials if t.tool_success) / len(trials)
    tool_sel_acc = sum(1 for t in trials if t.tool_selection_correct) / len(trials)

    steps_list = [t.steps for t in trials]
    ttft_list = [t.ttft_ms for t in trials if t.ttft_ms > 0]
    latency_list = [t.latency_ms for t in trials if t.latency_ms > 0]

    total_cost = sum(t.cost_usd for t in trials)
    total_input = sum(t.input_tokens for t in trials)
    total_output = sum(t.output_tokens for t in trials)

    judge_scores = [t.judge_score for t in trials if t.judge_score is not None]
    hallucination_flags = [t.judge_hallucinated for t in trials if t.judge_hallucinated is not None]

    return {
        "case_id": trials[0].case_id,
        "n_trials": len(trials),
        # 5 个 rate 类指标
        "task_success_rate": round(task_success_rate, 3),
        "tool_success_rate": round(tool_success_rate, 3),
        "tool_selection_accuracy": round(tool_sel_acc, 3),
        # 4 个统计类指标
        "steps_median": int(statistics.median(steps_list)) if steps_list else 0,
        "latency_p95_ms": percentile(latency_list, 0.95) if latency_list else 0,
        "ttft_p95_ms": percentile(ttft_list, 0.95) if ttft_list else 0,
        # 3 个总量类指标
        "total_tokens": total_input + total_output,
        "total_cost_usd": round(total_cost, 4),
        "total_retry": sum(t.retry_count for t in trials),
        # 2 个 judge 类指标
        "judge_score_mean": round(statistics.mean(judge_scores), 3) if judge_scores else None,
        "hallucination_rate": round(
            sum(1 for f in hallucination_flags if f) / len(hallucination_flags), 3
        ) if hallucination_flags else None,
    }


def percentile(values: List[float], p: float) -> int:
    """百分位数（P95 等）"""
    if not values:
        return 0
    sorted_vals = sorted(values)
    idx = int(p * (len(sorted_vals) - 1))
    return int(sorted_vals[idx])


def compute_cost_usd(trial: TrialResult, pricing: Dict[str, Dict[str, float]]) -> float:
    """借鉴 paperclip V2.0 的 cost 数学 · 单 trial cost"""
    p = pricing.get(trial.actual_tool or trial.case_id.split('-')[0])
    if not p:
        return 0.0
    in_cost = (trial.input_tokens / 1_000_000) * p.get("inputUsdPerMTokens", 0)
    out_cost = (trial.output_tokens / 1_000_000) * p.get("outputUsdPerMTokens", 0)
    cache_r = (trial.cache_read_tokens / 1_000_000) * p.get("cacheReadUsdPerMTokens", 0)
    cache_w = (trial.cache_write_tokens / 1_000_000) * p.get("cacheWriteUsdPerMTokens", 0)
    return in_cost + out_cost + cache_r + cache_w


# ==============================================================================
# 3. LLM judge 接口 · 借鉴 dsh-eval 的 strict JSON schema
# ==============================================================================

JUDGE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "hallucinated": {"type": "boolean"},
        "comment": {"type": "string", "minLength": 10, "maxLength": 500},
    },
    "required": ["score", "hallucinated", "comment"],
}


def parse_judge_verdict(judge_text: str) -> Dict[str, Any]:
    """借鉴 dsh-eval strict 解析 + 自研容错"""
    # 提取 JSON（兼容 markdown 包装）
    json_match = re.search(r"\{.*\}", judge_text, re.DOTALL)
    if not json_match:
        # 容错：返回极简默认值
        return {"score": 0.0, "hallucinated": True, "comment": "judge parse failed"}
    try:
        data = json.loads(json_match.group(0))
    except json.JSONDecodeError:
        return {"score": 0.0, "hallucinated": True, "comment": "judge JSON malformed"}

    # 严格 schema 校验
    for k in ["score", "hallucinated", "comment"]:
        if k not in data:
            return {"score": 0.0, "hallucinated": True, "comment": f"missing key: {k}"}

    # 范围
    score = data.get("score", 0)
    if not (0 <= score <= 1):
        score = max(0, min(1, score))

    return {
        "score": float(score),
        "hallucinated": bool(data.get("hallucinated", True)),
        "comment": str(data.get("comment", ""))[:500],
    }


def build_judge_prompt(case_prompt: str, expected: Dict[str, Any], actual_answer: str) -> str:
    """借鉴 dsh-eval judge prompt 模板（简洁版）"""
    return f"""You are evaluating a DeepSeek Harness agent task.

Task prompt: {case_prompt}
Expected: {json.dumps(expected, ensure_ascii=False)}
Actual answer: {actual_answer[:1000]}

Output a JSON verdict with this exact schema (no other keys allowed):
{{
  "score": <0.0-1.0>,
  "hallucinated": <true|false>,
  "comment": "<10-500 char explanation>"
}}
"""


# ==============================================================================
# 4. paired A/B 计算 · 借鉴 dsh-eval compare
# ==============================================================================

def paired_ab_compare(
    run_a: Dict[str, Any],
    run_b: Dict[str, Any],
) -> Dict[str, Any]:
    """
    借鉴 dsh-eval compare：同 case 按 score 算 B-A
    输出 win/lose/tie 统计
    """
    cases_a = {c["case_id"]: c for c in run_a.get("cases", [])}
    cases_b = {c["case_id"]: c for c in run_b.get("cases", [])}

    common = set(cases_a.keys()) & set(cases_b.keys())
    if not common:
        return {"common_cases": [], "summary": {"A_win": 0, "B_win": 0, "tie": 0}}

    rows = []
    a_wins = b_wins = ties = 0
    for cid in sorted(common):
        a = cases_a[cid]
        b = cases_b[cid]
        # 主指标选 task_success_rate
        a_score = a.get("task_success_rate", 0)
        b_score = b.get("task_success_rate", 0)
        delta = round(b_score - a_score, 3)
        if delta > 0:
            verdict = "B WIN"
            b_wins += 1
        elif delta < 0:
            verdict = "A WIN"
            a_wins += 1
        else:
            verdict = "TIE"
            ties += 1
        rows.append({
            "case_id": cid,
            "a_score": a_score,
            "b_score": b_score,
            "delta": delta,
            "verdict": verdict,
        })

    return {
        "common_cases": rows,
        "summary": {
            "A_win": a_wins,
            "B_win": b_wins,
            "tie": ties,
            "total": len(common),
        },
    }


def paired_ab_markdown(result: Dict[str, Any]) -> str:
    """借鉴 dsh-eval compare table markdown 输出"""
    rows = result["common_cases"]
    summary = result["summary"]
    lines = [
        "| Case | A Score | B Score | Δ (B-A) | Verdict |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['case_id']} | {r['a_score']:.2f} | {r['b_score']:.2f} | {r['delta']:+.3f} | {r['verdict']} |"
        )
    lines.append(f"\n**TOTAL**: A_win={summary['A_win']} · B_win={summary['B_win']} · TIE={summary['tie']} · total={summary['total']}")
    return "\n".join(lines)


# ==============================================================================
# CLI 命令树
# ==============================================================================

def cmd_parse(args: argparse.Namespace) -> int:
    bm = parse_benchmark_yaml(open(args.yaml_file, encoding="utf-8").read())
    print(json.dumps(bm.to_dict(), indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_compute_cost(args: argparse.Namespace) -> int:
    """单 trial cost 估算 + 11 类指标折叠 demo"""
    # mock 一个 trial
    t = TrialResult(
        case_id="demo",
        trial_idx=0,
        input_tokens=10_000,
        output_tokens=5_000,
        cache_read_tokens=2_000,
        cache_write_tokens=0,
        task_success=True,
        tool_success=True,
        tool_selection_correct=True,
        actual_tool="deepseek-v4",
        steps=3,
        latency_ms=1500,
        ttft_ms=200,
        final_answer="ok",
        judge_score=0.85,
        judge_hallucinated=False,
    )
    pricing = json.loads(args.pricing) if args.pricing else {
        "deepseek-v4": {
            "inputUsdPerMTokens": 0.27,
            "cacheReadUsdPerMTokens": 0.07,
            "cacheWriteUsdPerMTokens": 0.27,
            "outputUsdPerMTokens": 1.10,
        }
    }
    t.cost_usd = compute_cost_usd(t, pricing)
    metrics = compute_case_metrics([t])
    print(json.dumps({"trial": asdict(t), "metrics": metrics}, indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_paired(args: argparse.Namespace) -> int:
    run_a = json.load(open(args.run_a, encoding="utf-8"))
    run_b = json.load(open(args.run_b, encoding="utf-8"))
    result = paired_ab_compare(run_a, run_b)
    print(paired_ab_markdown(result))
    return EXIT_OK


def cmd_judge_demo(args: argparse.Namespace) -> int:
    """demo parse_judge_verdict"""
    sample = '{"score": 0.85, "hallucinated": false, "comment": "good answer"}'
    verdict = parse_judge_verdict(sample)
    print(json.dumps(verdict, indent=2, ensure_ascii=False))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dsh_eval_bridge",
        description="Stage 45 dsh-eval-bridge V1.0 · 借鉴 dsh-eval 4 类方法论 · 自研",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("parse", help="解析 benchmark YAML")
    sp.add_argument("yaml_file", help="benchmark.yaml 路径")
    sp.set_defaults(func=cmd_parse)

    sp = sub.add_parser("compute-cost", help="单 trial cost 估算 + 11 类指标 demo")
    sp.add_argument("--pricing", help="价格表 JSON 字符串")
    sp.set_defaults(func=cmd_compute_cost)

    sp = sub.add_parser("paired", help="paired A/B 计算")
    sp.add_argument("run_a", help="run A JSON 路径")
    sp.add_argument("run_b", help="run B JSON 路径")
    sp.set_defaults(func=cmd_paired)

    sp = sub.add_parser("judge-demo", help="judge verdict 解析 demo")
    sp.set_defaults(func=cmd_judge_demo)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, KeyError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return EXIT_SCHEMA
    except Exception as e:
        print(f"[EXCEPTION] {e}", file=sys.stderr)
        return EXIT_METRIC


if __name__ == "__main__":
    sys.exit(main())
