#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
free-llm-tier-router 核心路由引擎
Usage:
    python tier_router.py route "任务描述"
    python tier_router.py route --tier opus "任务描述"
    python tier_router.py status
    python tier_router.py direct --provider openrouter --model claude-3.5-sonnet "Hello"
    python tier_router.py stats
===============================================================================
"""

import argparse
import json
import sys
import time
import statistics
import os
from dataclasses import dataclass, asdict, field
from typing import Literal, Optional
from datetime import datetime

try:
    import httpx
except ImportError:
    print("[错误] 请先安装依赖: pip install httpx pydantic python-dotenv")
    sys.exit(1)

Tier = Literal["local", "haiku", "sonnet", "opus"]

# ============================================================
# 配置
# ============================================================

@dataclass
class RouteConfig:
    provider: str
    model: str
    base_url: str
    cost_per_1k_input: float
    cost_per_1k_output: float
    latency_ms: int
    capabilities: list[str]

TIER_CONFIGS: dict[Tier, list[RouteConfig]] = {
    "local": [
        RouteConfig("ollama", "llama3.1:8b", "http://localhost:11434", 0, 0, 50, ["chat", "code"]),
        RouteConfig("lmstudio", "meta-llama-3.1-8b-instruct", "http://localhost:1234/v1", 0, 0, 80, ["chat", "code"]),
        RouteConfig("llamacpp", "llama-3.1-8b-instruct", "http://localhost:8080/v1", 0, 0, 100, ["chat"]),
    ],
    "haiku": [
        RouteConfig("deepseek", "deepseek-chat-v3-0324", "https://api.deepseek.com", 0.001, 0.001, 500, ["chat", "fast"]),
        RouteConfig("openrouter", "anthropic/claude-3-haiku", "https://openrouter.ai/api/v1", 0.001, 0.001, 800, ["chat", "fast"]),
    ],
    "sonnet": [
        RouteConfig("openrouter", "anthropic/claude-3.5-sonnet", "https://openrouter.ai/api/v1", 0.003, 0.015, 1200, ["chat", "code", "analysis"]),
        RouteConfig("deepseek", "deepseek-reasoner", "https://api.deepseek.com", 0.002, 0.008, 1000, ["reasoning", "analysis"]),
    ],
    "opus": [
        RouteConfig("openrouter", "anthropic/claude-3-opus", "https://openrouter.ai/api/v1", 0.015, 0.075, 2000, ["reasoning", "analysis", "code", "security"]),
        RouteConfig("nvidia", "claude-3-opus", "https://integrate.api.nvidia.com/v1", 0.01, 0.05, 1500, ["reasoning", "analysis", "code", "security"]),
    ],
}

TIER_KEYWORDS: dict[Tier, list[str]] = {
    "local": ["离线", "内网", "本地", "快速", "简单", "免费", "成本", "预算", "测试", "原型"],
    "haiku": ["分类", "标签", "摘要", "总结", "概要", "快速回答", "简单问答", "翻译"],
    "sonnet": ["代码", "编程", "实现", "文档", "报告", "创意", "头脑风暴", "分析", "图表", "代码审查"],
    "opus": ["架构", "系统设计", "安全审计", "风险评估", "复杂推理", "深度推理", "跨领域", "复杂分析"],
}

TIER_LABELS: dict[Tier, str] = {
    "local": "LOCAL",
    "haiku": "HAIKU",
    "sonnet": "SONNET",
    "opus": "OPUS",
}

# ============================================================
# 路由算法
# ============================================================

class TierRouter:
    def __init__(self, available_providers: Optional[list[str]] = None):
        self.available_providers = available_providers or self._detect_available()
        self.stats = {
            "total_requests": 0,
            "by_tier": {t: 0 for t in TIER_CONFIGS},
            "by_provider": {},
            "total_cost": 0.0,
        }

    def _detect_available(self) -> list[str]:
        """自动检测可用的 Provider"""
        available = []
        checks = [
            ("ollama", "http://localhost:11434"),
            ("lmstudio", "http://localhost:1234/v1"),
            ("llamacpp", "http://localhost:8080/v1"),
        ]
        for name, url in checks:
            try:
                resp = httpx.get(url.replace("/v1", "/api/tags") if "llama" not in name else url + "/models",
                                timeout=3)
                if resp.status_code == 200:
                    available.append(name)
            except Exception:
                pass
        # 云端 Provider 需要 API Key 检查
        if os.getenv("OPENROUTER_API_KEY"):
            available.append("openrouter")
        if os.getenv("DEEPSEEK_API_KEY"):
            available.append("deepseek")
        if os.getenv("NVIDIA_API_KEY"):
            available.append("nvidia")
        return available

    def classify_tier(self, prompt: str) -> Tier:
        """根据 prompt 内容分类到对应 Tier"""
        prompt_lower = prompt.lower()
        for tier in ["opus", "sonnet", "haiku", "local"]:
            if any(kw in prompt_lower for kw in TIER_KEYWORDS[tier]):
                return tier
        return "sonnet"  # 默认

    def select_provider(self, tier: Tier) -> RouteConfig:
        """从可用 Provider 中选择最优配置"""
        configs = TIER_CONFIGS[tier]
        for config in configs:
            if config.provider in self.available_providers:
                return config
        # 降级策略
        fallback_tiers = ["sonnet", "haiku", "local"]
        for ftier in fallback_tiers:
            if ftier == tier:
                continue
            for config in TIER_CONFIGS[ftier]:
                if config.provider in self.available_providers:
                    return config
        raise ValueError(f"No available provider for tier {tier} (fallback exhausted)")

    def route(self, prompt: str, forced_tier: Optional[Tier] = None) -> dict:
        """执行路由决策"""
        tier = forced_tier or self.classify_tier(prompt)
        config = self.select_provider(tier)

        # 统计
        self.stats["total_requests"] += 1
        self.stats["by_tier"][tier] += 1
        self.stats["by_provider"][config.provider] = self.stats["by_provider"].get(config.provider, 0) + 1

        return {
            "tier": tier,
            "tier_label": TIER_LABELS[tier],
            "provider": config.provider,
            "model": config.model,
            "base_url": config.base_url,
            "estimated_latency_ms": config.latency_ms,
            "estimated_cost_per_1k": config.cost_per_1k_input + config.cost_per_1k_output,
            "capabilities": config.capabilities,
        }

    def chat(self, prompt: str, forced_tier: Optional[Tier] = None, fallback: bool = True) -> dict:
        """执行路由并调用 LLM"""
        route_info = self.route(prompt, forced_tier)
        start = time.time()
        try:
            result = self._call_llm(route_info, prompt)
            elapsed = time.time() - start
            return {
                **route_info,
                "response": result.get("content", ""),
                "input_tokens": result.get("input_tokens", 0),
                "output_tokens": result.get("output_tokens", 0),
                "elapsed_ms": round(elapsed * 1000),
                "success": True,
                "error": None,
            }
        except Exception as e:
            elapsed = time.time() - start
            return {
                **route_info,
                "response": "",
                "input_tokens": 0,
                "output_tokens": 0,
                "elapsed_ms": round(elapsed * 1000),
                "success": False,
                "error": str(e),
            }

    def _call_llm(self, route_info: dict, prompt: str) -> dict:
        """调用 LLM Provider"""
        provider = route_info["provider"]
        base_url = route_info["base_url"]
        model = route_info["model"]

        headers = {"Content-Type": "application/json"}
        if provider == "openrouter":
            headers["Authorization"] = f"Bearer {os.getenv('OPENROUTER_API_KEY')}"
        elif provider == "deepseek":
            headers["Authorization"] = f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"
        elif provider == "nvidia":
            headers["Authorization"] = f"Bearer {os.getenv('NVIDIA_API_KEY')}"
        elif provider == "ollama":
            return self._call_ollama(base_url, model, prompt)
        elif provider in ("lmstudio", "llamacpp"):
            return self._call_openai_compatible(base_url, model, prompt)

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
        }
        resp = httpx.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return {
            "content": content,
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
        }

    def _call_ollama(self, base_url: str, model: str, prompt: str) -> dict:
        payload = {"model": model, "prompt": prompt, "stream": False, "options": {"num_predict": 256}}
        resp = httpx.post(f"{base_url}/api/generate", json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return {
            "content": data.get("response", ""),
            "input_tokens": data.get("prompt_eval_count", 0),
            "output_tokens": data.get("eval_count", 0),
        }

    def _call_openai_compatible(self, base_url: str, model: str, prompt: str) -> dict:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 256,
            "stream": False,
        }
        resp = httpx.post(f"{base_url}/chat/completions", json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return {
            "content": content,
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
        }

    def get_stats(self) -> dict:
        return self.stats

# ============================================================
# CLI
# ============================================================

def print_route_info(route: dict):
    tier_colors = {
        "local": "\033[92m",   # 绿色
        "haiku": "\033[93m",   # 黄色
        "sonnet": "\033[94m",   # 蓝色
        "opus": "\033[95m",     # 紫色
    }
    reset = "\033[0m"
    color = tier_colors.get(route["tier"], "")

    print(f"\n{'='*60}")
    print(f"  路由决策")
    print(f"{'='*60}")
    print(f"  Tier:        {color}{route['tier_label']}{reset}")
    print(f"  Provider:    {route['provider']}")
    print(f"  Model:      {route['model']}")
    print(f"  Endpoint:    {route['base_url']}")
    print(f"  延迟估算:    ~{route['estimated_latency_ms']}ms")
    cost = route['estimated_cost_per_1k']
    print(f"  成本估算:    ${cost:.4f}/1K tokens" if cost > 0 else f"  成本估算:    免费")
    print(f"  能力:       {', '.join(route['capabilities'])}")
    print(f"{'='*60}\n")

def print_stats(stats: dict):
    total = stats["total_requests"]
    print(f"\n{'='*60}")
    print(f"  Tier Router 统计")
    print(f"{'='*60}")
    print(f"  总请求数:    {total}")
    print(f"")
    print(f"  By Tier:")
    for tier, count in stats["by_tier"].items():
        pct = (count / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"    {TIER_LABELS.get(tier, tier):6s}:  {count:4d} ({pct:5.1f}%) {bar}")
    print(f"")
    print(f"  By Provider:")
    for provider, count in sorted(stats["by_provider"].items(), key=lambda x: -x[1]):
        pct = (count / total * 100) if total > 0 else 0
        print(f"    {provider:12s}:  {count:4d} ({pct:5.1f}%)")
    print(f"{'='*60}\n")

def cmd_route(args):
    router = TierRouter()
    route = router.route(args.prompt, args.tier)
    print_route_info(route)

    if args.execute:
        print("[执行] 正在调用 LLM...")
        result = router.chat(args.prompt, args.tier)
        if result["success"]:
            print(f"[响应] {result['response'][:500]}")
            print(f"[统计] 耗时: {result['elapsed_ms']}ms, "
                  f"Token: {result['input_tokens']} in + {result['output_tokens']} out")
        else:
            print(f"[错误] {result['error']}")
    elif args.stats:
        print_stats(router.get_stats())

def cmd_direct(args):
    router = TierRouter()
    route = {
        "provider": args.provider,
        "model": args.model,
        "base_url": args.base_url or "",
        "tier": "direct",
        "tier_label": "DIRECT",
        "estimated_latency_ms": 1000,
        "estimated_cost_per_1k": 0.01,
        "capabilities": ["chat"],
    }
    print(f"\n[直接调用] {args.provider}/{args.model}")
    result = router.chat(args.prompt, None)
    if result["success"]:
        print(f"[响应]\n{result['response'][:500]}")
        print(f"[统计] 耗时: {result['elapsed_ms']}ms")
    else:
        print(f"[错误] {result['error']}")

def cmd_status(args):
    router = TierRouter()
    print(f"\n{'='*60}")
    print(f"  Provider 状态")
    print(f"{'='*60}")
    print(f"  已配置 Provider:")
    for provider in router.available_providers:
        print(f"    ✅ {provider}")
    not_available = [p for p in ["ollama","lmstudio","llamacpp","openrouter","deepseek","nvidia"]
                      if p not in router.available_providers]
    if not_available:
        print(f"  不可用 Provider:")
        for provider in not_available:
            print(f"    ❌ {provider}")
    print(f"{'='*60}\n")

def cmd_stats(args):
    router = TierRouter()
    print_stats(router.get_stats())

def main():
    parser = argparse.ArgumentParser(description="free-llm-tier-router 核心路由引擎")
    sub = parser.add_subparsers(dest="cmd")

    # route 命令
    route_p = sub.add_parser("route", help="路由任务")
    route_p.add_argument("prompt", help="任务描述")
    route_p.add_argument("--tier", "-t", choices=["local", "haiku", "sonnet", "opus"],
                        help="强制指定 Tier")
    route_p.add_argument("--execute", "-e", action="store_true", help="执行路由并调用 LLM")
    route_p.add_argument("--stats", "-s", action="store_true", help="显示统计信息")
    route_p.set_defaults(func=cmd_route)

    # direct 命令
    direct_p = sub.add_parser("direct", help="直接调用指定 Provider")
    direct_p.add_argument("prompt", help="任务描述")
    direct_p.add_argument("--provider", "-p", required=True,
                          choices=["ollama", "lmstudio", "llamacpp", "openrouter", "deepseek", "nvidia"],
                          help="指定 Provider")
    direct_p.add_argument("--model", "-m", required=True, help="指定模型")
    direct_p.add_argument("--base-url", help="自定义端点 URL")
    direct_p.set_defaults(func=cmd_direct)

    # status 命令
    status_p = sub.add_parser("status", help="查看 Provider 状态")
    status_p.set_defaults(func=cmd_status)

    # stats 命令
    stats_p = sub.add_parser("stats", help="查看路由统计")
    stats_p.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
