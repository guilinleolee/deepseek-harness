#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
free-llm-tier-router Provider 健康检查
Usage: python provider_check.py [--verbose]
===============================================================================
"""

import argparse
import json
import httpx
import sys
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProviderStatus:
    name: str
    endpoint: str
    online: bool
    latency_ms: Optional[float]
    error: Optional[str]
    details: dict

LOCAL_PROVIDERS = [
    ("ollama", "http://localhost:11434"),
    ("lmstudio", "http://localhost:1234/v1"),
    ("llamacpp", "http://localhost:8080/v1"),
]

CLOUD_PROVIDERS = [
    ("openrouter", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    ("deepseek", "https://api.deepseek.com", "DEEPSEEK_API_KEY"),
    ("nvidia", "https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY"),
]

def check_endpoint(name: str, url: str, timeout: float = 5.0) -> ProviderStatus:
    """检查单个端点是否在线"""
    import time
    start = time.time()
    try:
        if name == "ollama":
            resp = httpx.get(f"{url}/api/tags", timeout=timeout)
        elif name in ("lmstudio", "llamacpp"):
            resp = httpx.get(f"{url}/models", timeout=timeout)
        elif name == "openrouter":
            resp = httpx.get(
                f"{url}/models",
                headers={"Authorization": f"Bearer {get_api_key('OPENROUTER_API_KEY')}"},
                timeout=timeout
            )
        elif name == "deepseek":
            resp = httpx.get(
                f"{url}/models",
                headers={"Authorization": f"Bearer {get_api_key('DEEPSEEK_API_KEY')}"},
                timeout=timeout
            )
        elif name == "nvidia":
            resp = httpx.get(
                f"{url}/models",
                headers={"Authorization": f"Bearer {get_api_key('NVIDIA_API_KEY')}"},
                timeout=timeout
            )
        else:
            resp = httpx.get(url, timeout=timeout)

        latency = (time.time() - start) * 1000
        if resp.status_code == 200:
            return ProviderStatus(name, url, True, round(latency, 1), None, resp.json() if resp.text else {})
        else:
            return ProviderStatus(name, url, False, round(latency, 1),
                                f"HTTP {resp.status_code}", {})
    except Exception as e:
        latency = (time.time() - start) * 1000
        return ProviderStatus(name, url, False, round(latency, 1), str(e), {})

def get_api_key(var: str) -> str:
    import os
    return os.getenv(var, "")

def check_provider(name: str, url: str, api_key_var: str, verbose: bool = False) -> ProviderStatus:
    """检查云端 Provider（需要 API Key）"""
    api_key = get_api_key(api_key_var)
    if not api_key:
        return ProviderStatus(name, url, False, None, "API Key 未配置", {})

    status = check_endpoint(name, url)
    if verbose:
        status.details = {"api_key_prefix": api_key[:8] + "..."}
    return status

def run_checks(providers: list, verbose: bool = False) -> list[ProviderStatus]:
    """运行所有检查"""
    results = []
    for name, url in providers:
        status = check_endpoint(name, url, timeout=5.0)
        results.append(status)
        if verbose:
            print(f"  [{name}] {url} -> {'✅' if status.online else '❌'} "
                  f"{status.latency_ms}ms" + (f" ({status.error})" if status.error else ""))
    return results

def print_summary(results: list[ProviderStatus], title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

    online = sum(1 for r in results if r.online)
    print(f"  在线: {online}/{len(results)}")
    print(f"")

    for r in results:
        icon = "✅" if r.online else "❌"
        latency_str = f"{r.latency_ms}ms" if r.latency_ms else "-"
        print(f"  {icon} {r.name:12s}  {r.endpoint}")
        if r.latency_ms:
            print(f"      延迟: {latency_str}")
        if r.error:
            print(f"      错误: {r.error}")
        if r.details and "api_key_prefix" in r.details:
            print(f"      Key: {r.details['api_key_prefix']}")

    print(f"{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(description="free-llm-tier-router Provider 健康检查")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--local", "-l", action="store_true", help="仅检查本地 Provider")
    parser.add_argument("--cloud", "-c", action="store_true", help="仅检查云端 Provider")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    verbose = args.verbose
    results = []

    if args.local:
        results.extend(run_checks(LOCAL_PROVIDERS, verbose))
    elif args.cloud:
        for name, url, key_var in CLOUD_PROVIDERS:
            status = check_provider(name, url, key_var, verbose)
            results.append(status)
            if verbose:
                print(f"  [{name}] {'✅' if status.online else '❌'} "
                      f"{status.latency_ms}ms" + (f" ({status.error})" if status.error else ""))
    else:
        results.extend(run_checks(LOCAL_PROVIDERS, verbose))
        for name, url, key_var in CLOUD_PROVIDERS:
            status = check_provider(name, url, key_var, verbose)
            results.append(status)
            if verbose:
                print(f"  [{name}] {'✅' if status.online else '❌'} "
                      f"{status.latency_ms}ms" + (f" ({status.error})" if status.error else ""))

    if args.json:
        print(json.dumps([{"name": r.name, "online": r.online,
                          "latency_ms": r.latency_ms, "error": r.error}
                         for r in results], ensure_ascii=False, indent=2))
    else:
        print_summary(results, "Provider 健康检查结果")

        # 汇总
        total_online = sum(1 for r in results if r.online)
        if total_online == 0:
            print("  ⚠️  没有可用的 Provider!")
            print("  → 启动本地 Provider 或配置云端 API Key")
            return 1
        elif total_online == len(results):
            print("  ✅ 所有 Provider 均在线")
        else:
            print(f"  ⚠️  {len(results) - total_online} 个 Provider 不可用")
        return 0

if __name__ == "__main__":
    sys.exit(main())
