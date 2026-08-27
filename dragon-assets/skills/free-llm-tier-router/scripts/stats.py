#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
free-llm-tier-router 统计报告器
Usage: python stats.py [--json] [--save]
===============================================================================
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

STATS_FILE = os.path.join(os.path.dirname(__file__), "..", ".stats.jsonl")

@dataclass
class TierStat:
    count: int = 0
    total_latency_ms: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0
    errors: int = 0

@dataclass
class ProviderStat:
    count: int = 0
    total_latency_ms: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0
    errors: int = 0
    tiers_used: dict = None

    def __post_init__(self):
        if self.tiers_used is None:
            self.tiers_used = {}

@dataclass
class RouterStats:
    total_requests: int = 0
    by_tier: dict = None
    by_provider: dict = None
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0
    total_errors: int = 0
    start_time: str = ""
    last_updated: str = ""

    def __post_init__(self):
        if self.by_tier is None:
            self.by_tier = {}
        if self.by_provider is None:
            self.by_provider = {}

    @classmethod
    def from_file(cls, path: str) -> "RouterStats":
        if not os.path.exists(path):
            return cls(start_time=datetime.now().isoformat())
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if not lines:
                return cls(start_time=datetime.now().isoformat())

            stats = cls(start_time=datetime.now().isoformat())
            # 聚合最后一行的累计数据
            for line in lines:
                entry = json.loads(line)
                stats._merge_entry(entry)
            return stats
        except Exception:
            return cls(start_time=datetime.now().isoformat())

    def _merge_entry(self, entry: dict):
        self.total_requests += 1
        if entry.get("success"):
            self.total_input_tokens += entry.get("input_tokens", 0)
            self.total_output_tokens += entry.get("output_tokens", 0)
            self.total_cost += entry.get("estimated_cost", 0)
            tier = entry.get("tier", "unknown")
            self.by_tier[tier] = self.by_tier.get(tier, 0) + 1
            provider = entry.get("provider", "unknown")
            if provider not in self.by_provider:
                self.by_provider[provider] = {"count": 0, "tiers": set()}
            self.by_provider[provider]["count"] += 1
            self.by_provider[provider]["tiers"].add(tier)
        else:
            self.total_errors += 1
        self.last_updated = entry.get("timestamp", datetime.now().isoformat())

    def to_dict(self) -> dict:
        result = asdict(self)
        # 转换 set 为 list
        for pv in result.get("by_provider", {}).values():
            if "tiers" in pv and isinstance(pv["tiers"], set):
                pv["tiers"] = list(pv["tiers"])
        return result

def print_ascii_report(stats: RouterStats):
    total = stats.total_requests
    cost = stats.total_cost
    savings = cost * 20 if cost > 0 else 0  # 假设用 Claude Opus 的成本

    print(f"\n{'='*60}")
    print(f"  Tier Router 统计报告")
    print(f"{'='*60}")
    print(f"  生成时间:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  统计时段:   {stats.start_time[:19]} ~ {stats.last_updated[:19]}")
    print(f"")
    print(f"  📊 总览:")
    print(f"  总请求数:      {total}")
    print(f"  成功:         {total - stats.total_errors} ({100 if total == 0 else (total-stats.total_errors)*100/total:.1f}%)")
    print(f"  失败:         {stats.total_errors}")
    print(f"  Token消耗:    {stats.total_input_tokens:,} in / {stats.total_output_tokens:,} out")
    print(f"  总成本:        ${cost:.4f}")
    if savings > 0:
        print(f"  节省( vs Claude): ${savings:.2f} ({savings/(cost+savings)*100:.0f}%)")
    print(f"")

    print(f"  📈 By Tier:")
    tier_labels = {"local": "LOCAL  ", "haiku": "HAIKU ", "sonnet": "SONNET", "opus": "OPUS  "}
    tier_colors = {"local": "🟢", "haiku": "🟡", "sonnet": "🔵", "opus": "🟣"}
    for tier, count in sorted(stats.by_tier.items(), key=lambda x: -x[1]):
        pct = (count / total * 100) if total > 0 else 0
        bar_len = int(pct / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        icon = tier_colors.get(tier, "⚪")
        print(f"    {icon} {tier_labels.get(tier, tier)}: {count:4d} ({pct:5.1f}%) {bar}")
    print(f"")

    print(f"  📊 By Provider:")
    for provider, data in sorted(stats.by_provider.items(), key=lambda x: -x[1]["count"]):
        count = data["count"]
        pct = (count / total * 100) if total > 0 else 0
        tiers = ", ".join(sorted(data["tiers"]))
        print(f"    {provider:12s}: {count:4d} ({pct:5.1f}%)  [{tiers}]")

    print(f"")
    print(f"  💡 建议:")
    local_pct = stats.by_tier.get("local", 0) / total * 100 if total > 0 else 0
    if local_pct < 30:
        print(f"  → 本地模型使用率偏低 ({local_pct:.0f}%)，可增加简单任务路由到 LOCAL Tier")
    if stats.total_errors > 0:
        err_pct = stats.total_errors / total * 100
        print(f"  → 错误率 {err_pct:.1f}%，建议检查 Provider 健康状态")
    if total < 10:
        print(f"  → 统计数据较少，继续使用以获得更准确的优化建议")
    if total >= 10 and local_pct >= 50:
        print(f"  → 优秀! {local_pct:.0f}% 任务使用了免费本地模型")

    print(f"{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(description="Tier Router 统计报告")
    parser.add_argument("--json", "-j", action="store_true", help="JSON 格式输出")
    parser.add_argument("--save", "-s", action="store_true", help="保存当前会话统计")
    parser.add_argument("--file", "-f", default=STATS_FILE, help="统计文件路径")
    args = parser.parse_args()

    stats = RouterStats.from_file(args.file)

    if args.save:
        print(f"[保存] 统计已保存到: {args.file}")
        # 当前会话数据保存由 tier_router.py 在每次请求时追加

    if args.json:
        print(json.dumps(stats.to_dict(), ensure_ascii=False, indent=2))
    else:
        print_ascii_report(stats)

if __name__ == "__main__":
    main()
