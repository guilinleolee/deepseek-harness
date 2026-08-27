#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
free-claude-code 模型性能基准测试脚本
Usage: python model-benchmark.py [--provider ollama|lmstudio|llamacpp] [--model MODEL]
===============================================================================
"""

import argparse
import json
import time
import statistics
import requests
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class BenchmarkResult:
    provider: str
    model: str
    total_tokens: int
    tokens_per_second: float
    time_to_first_token: float
    total_time: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    error_rate: float
    success_count: int
    total_runs: int
    timestamp: str


class ModelBenchmark:
    """模型性能基准测试器"""

    PROVIDER_ENDPOINTS = {
        "ollama": "http://localhost:11434",
        "lmstudio": "http://localhost:1234/v1",
        "llamacpp": "http://localhost:8080/v1",
    }

    DEFAULT_MODELS = {
        "ollama": "llama3.1:8b",
        "lmstudio": "meta-llama-3.1-8b-instruct",
        "llamacpp": "llama-3.1-8b-instruct",
    }

    # 测试提示词
    TEST_PROMPTS = [
        "What is the capital of France?",
        "Explain quantum computing in one sentence.",
        "Write a haiku about artificial intelligence.",
        "What are the three primary colors?",
        "Who wrote Romeo and Juliet?",
    ]

    def __init__(self, provider: str, model: Optional[str] = None):
        self.provider = provider.lower()
        self.base_url = self.PROVIDER_ENDPOINTS.get(self.provider)
        if not self.base_url:
            raise ValueError(f"Unknown provider: {provider}")

        self.model = model or self.DEFAULT_MODELS.get(self.provider)
        self.results: list[dict] = []

    def check_health(self) -> bool:
        """检查Provider服务是否可用"""
        try:
            if self.provider == "ollama":
                resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            else:
                resp = requests.get(f"{self.base_url}/models", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def build_payload(self, prompt: str) -> dict:
        """根据Provider构建请求负载"""
        if self.provider == "ollama":
            return {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": 128},
            }
        else:  # lmstudio, llamacpp
            return {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 128,
                "stream": False,
            }

    def run_single_test(self, prompt: str) -> Optional[dict]:
        """执行单次测试"""
        try:
            start = time.time()
            ttf_start = start
            time_to_first = None
            content = ""
            total_tokens = 0

            if self.provider == "ollama":
                endpoint = f"{self.base_url}/api/generate"
            else:
                endpoint = f"{self.base_url}/chat/completions"

            resp = requests.post(
                endpoint,
                json=self.build_payload(prompt),
                timeout=120,
            )
            end = time.time()
            total_time = end - start

            if resp.status_code != 200:
                return None

            data = resp.json()

            if self.provider == "ollama":
                content = data.get("response", "")
                eval_count = data.get("eval_count", 0)
                prompt_eval_count = data.get("prompt_eval_count", 0)
                total_tokens = eval_count + prompt_eval_count
                time_to_first = data.get("eval_duration", 0) / 1e9  # ns to s
            else:
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "")
                usage = data.get("usage", {})
                total_tokens = usage.get("total_tokens", len(content) // 4)

            if time_to_first is None:
                time_to_first = total_time * 0.1  # 估算10%

            tokens_per_second = total_tokens / total_time if total_time > 0 else 0

            return {
                "prompt": prompt,
                "total_time": total_time,
                "time_to_first_token": time_to_first,
                "total_tokens": total_tokens,
                "tokens_per_second": tokens_per_second,
                "content_length": len(content),
                "success": True,
            }
        except Exception as e:
            return {"prompt": prompt, "success": False, "error": str(e)}

    def run_benchmark(self, num_runs: int = 3) -> BenchmarkResult:
        """运行完整基准测试"""
        print(f"\n{'='*60}")
        print(f"  {self.provider.upper()} 模型基准测试")
        print(f"  Model: {self.model}")
        print(f"{'='*60}\n")

        if not self.check_health():
            print(f"[ERROR] {self.provider} service not available")
            return self._empty_result()

        latencies = []
        ttft_list = []
        tps_list = []
        success = 0
        total = 0

        for run in range(num_runs):
            print(f"[Run {run + 1}/{num_runs}]")
            for i, prompt in enumerate(self.TEST_PROMPTS):
                total += 1
                result = self.run_single_test(prompt)

                if result and result.get("success"):
                    success += 1
                    latencies.append(result["total_time"] * 1000)  # ms
                    ttft_list.append(result["time_to_first_token"] * 1000)
                    tps_list.append(result["tokens_per_second"])
                    print(
                        f"  [{i + 1}/{len(self.TEST_PROMPTS)}] "
                        f"OK | {result['total_time']:.2f}s | "
                        f"{result['tokens_per_second']:.1f} tok/s | "
                        f"{len(result['content'])} chars"
                    )
                else:
                    print(f"  [{i + 1}/{len(self.TEST_PROMPTS)}] FAIL")

                time.sleep(0.5)  # 避免过载

        if not latencies:
            return self._empty_result()

        error_rate = (total - success) / total * 100
        avg_tps = statistics.mean(tps_list)
        avg_ttft = statistics.mean(ttft_list)
        p50 = statistics.median(latencies)
        p95 = statistics.quantiles(latencies, n=20)[9] if len(latencies) >= 20 else max(latencies)
        p99 = max(latencies) * 0.99

        result = BenchmarkResult(
            provider=self.provider,
            model=self.model,
            total_tokens=sum(r.get("total_tokens", 0) for r in self.results if r.get("success")),
            tokens_per_second=avg_tps,
            time_to_first_token=avg_ttft,
            total_time=sum(r.get("total_time", 0) for r in self.results if r.get("success")),
            latency_p50_ms=p50,
            latency_p95_ms=p95,
            latency_p99_ms=p99,
            error_rate=error_rate,
            success_count=success,
            total_runs=total,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        self._print_summary(result)
        return result

    def _empty_result(self) -> BenchmarkResult:
        return BenchmarkResult(
            provider=self.provider,
            model=self.model,
            total_tokens=0,
            tokens_per_second=0,
            time_to_first_token=0,
            total_time=0,
            latency_p50_ms=0,
            latency_p95_ms=0,
            latency_p99_ms=0,
            error_rate=100,
            success_count=0,
            total_runs=0,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        )

    def _print_summary(self, result: BenchmarkResult):
        """打印基准测试汇总"""
        print(f"\n{'='*60}")
        print(f"  基准测试汇总")
        print(f"{'='*60}")
        print(f"  Provider:        {result.provider}")
        print(f"  Model:           {result.model}")
        print(f"  成功率:          {result.success_count}/{result.total_runs} ({100 - result.error_rate:.1f}%)")
        print(f"  平均速度:         {result.tokens_per_second:.1f} tok/s")
        print(f"  首Token延迟:      {result.time_to_first_token:.0f} ms")
        print(f"  P50 延迟:        {result.latency_p50_ms:.0f} ms")
        print(f"  P95 延迟:        {result.latency_p95_ms:.0f} ms")
        print(f"  P99 延迟:        {result.latency_p99_ms:.0f} ms")
        print(f"{'='*60}\n")

        # 性能评级
        tps = result.tokens_per_second
        if tps >= 80:
            grade = "S (卓越)"
        elif tps >= 50:
            grade = "A (优秀)"
        elif tps >= 30:
            grade = "B (良好)"
        elif tps >= 15:
            grade = "C (一般)"
        else:
            grade = "D (待优化)"

        print(f"  性能评级: {grade}")
        print(f"  基准时间: {result.timestamp}\n")

    def save_results(self, result: BenchmarkResult, filepath: str = "benchmark-results.jsonl"):
        """保存结果到JSONL文件"""
        try:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(result), ensure_ascii=False) + "\n")
            print(f"[INFO] 结果已保存: {filepath}")
        except Exception as e:
            print(f"[ERROR] 保存失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="free-claude-code 模型基准测试")
    parser.add_argument(
        "--provider", "-p",
        choices=["ollama", "lmstudio", "llamacpp"],
        default="ollama",
        help="本地LLM Provider (默认: ollama)",
    )
    parser.add_argument(
        "--model", "-m",
        help="指定模型名称 (默认: 根据provider自动选择)",
    )
    parser.add_argument(
        "--runs", "-r",
        type=int,
        default=3,
        help="每个提示词的测试次数 (默认: 3)",
    )
    parser.add_argument(
        "--save", "-s",
        default="benchmark-results.jsonl",
        help="结果保存路径 (默认: benchmark-results.jsonl)",
    )
    args = parser.parse_args()

    benchmark = ModelBenchmark(args.provider, args.model)
    result = benchmark.run_benchmark(args.runs)
    benchmark.save_results(result, args.save)


if __name__ == "__main__":
    main()
