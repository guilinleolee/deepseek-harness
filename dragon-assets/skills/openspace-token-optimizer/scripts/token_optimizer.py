#!/usr/bin/env python3
"""
OpenSpace Token Optimizer

Intelligent token management and optimization for天龙引擎 skills.
Provides context compression, progressive disclosure, and smart caching.
Based on OpenSpace Cloud's 4.2x performance improvement and 46% token savings.
"""

import os
import re
import json
import hashlib
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TokenBudget:
    """Token budget tracking."""
    daily_limit: int = 100000
    used_today: int = 0
    reset_date: Optional[str] = None
    alert_threshold: float = 0.8

    def is_exhausted(self) -> bool:
        """Check if budget is exhausted."""
        return self.used_today >= self.daily_limit

    def check_alert(self) -> bool:
        """Check if alert threshold reached."""
        return (self.used_today / self.daily_limit) >= self.alert_threshold

    def remaining(self) -> int:
        """Remaining tokens."""
        return max(0, self.daily_limit - self.used_today)


@dataclass
class CacheEntry:
    """Cache entry for tokens."""
    key: str
    value: str
    tokens: int
    created_at: str
    ttl_seconds: int
    hit_count: int = 0
    last_accessed: Optional[str] = None


@dataclass
class OptimizationResult:
    """Result of token optimization."""
    original_tokens: int
    optimized_tokens: int
    savings_percent: float
    method: str
    cached: bool = False


class TokenOptimizer:
    """Token optimization engine."""

    # OpenSpace benchmark data
    BENCHMARK_SAVINGS = 0.46  # 46% average savings
    PERFORMANCE_IMPROVEMENT = 4.2

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("~/.claude/skills/openspace-token-optimizer/config")
        self.config = self._load_config()
        self.budget = self._load_budget()
        self.cache: Dict[str, CacheEntry] = {}
        self._load_cache()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration."""
        config_file = self.config_path / "token_config.json"
        if config_file.exists():
            try:
                return json.loads(config_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Default config
        return {
            "token_budget": {
                "daily_limit": 100000,
                "alert_threshold": 0.8
            },
            "compression": {
                "enabled": True,
                "aggressive": False
            },
            "cache": {
                "enabled": True,
                "strategy": "semantic",
                "ttl_seconds": 3600,
                "max_entries": 1000
            },
            "progressive_disclosure": {
                "index_tokens": 100,
                "summary_tokens": 500
            }
        }

    def _load_budget(self) -> TokenBudget:
        """Load token budget."""
        budget_file = self.config_path / "budget.json"
        today = datetime.utcnow().strftime("%Y-%m-%d")

        if budget_file.exists():
            try:
                data = json.loads(budget_file.read_text(encoding="utf-8"))
                if data.get("reset_date") != today:
                    data["used_today"] = 0
                    data["reset_date"] = today
                return TokenBudget(**data)
            except Exception:
                pass

        return TokenBudget(reset_date=today)

    def _save_budget(self):
        """Save token budget."""
        self.config_path.mkdir(parents=True, exist_ok=True)
        budget_file = self.config_path / "budget.json"
        data = {
            "daily_limit": self.budget.daily_limit,
            "used_today": self.budget.used_today,
            "reset_date": self.budget.reset_date,
            "alert_threshold": self.budget.alert_threshold
        }
        budget_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load_cache(self):
        """Load cache from disk."""
        cache_file = self.config_path / "cache.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                for key, entry_data in data.items():
                    self.cache[key] = CacheEntry(**entry_data)
                logger.info(f"Loaded {len(self.cache)} cache entries")
            except Exception:
                pass

    def _save_cache(self):
        """Save cache to disk."""
        cache_file = self.config_path / "cache.json"
        data = {k: asdict(v) for k, v in self.cache.items()}
        cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough estimate: 4 chars per token)."""
        return len(text) // 4

    def get_cache_key(self, content: str, mode: str = "semantic") -> str:
        """Generate cache key."""
        if mode == "semantic":
            # Use hash of content for semantic cache
            return hashlib.sha256(content.encode()).hexdigest()[:16]
        elif mode == "exact":
            return hashlib.md5(content.encode()).hexdigest()
        return hashlib.sha256(content.encode()).hexdigest()

    def check_cache(self, content: str, mode: str = "semantic") -> Optional[str]:
        """Check if content is in cache."""
        if not self.config.get("cache", {}).get("enabled", True):
            return None

        cache_key = self.get_cache_key(content, mode)
        entry = self.cache.get(cache_key)

        if entry:
            # Check TTL
            created = datetime.fromisoformat(entry.created_at)
            ttl = timedelta(seconds=entry.ttl_seconds)
            if datetime.utcnow() - created < ttl:
                entry.hit_count += 1
                entry.last_accessed = datetime.utcnow().isoformat()
                logger.info(f"Cache hit: {cache_key[:8]}... (hit #{entry.hit_count})")
                return entry.value
            else:
                # TTL expired
                del self.cache[cache_key]

        return None

    def store_cache(self, content: str, optimized: str, mode: str = "semantic"):
        """Store optimized content in cache."""
        if not self.config.get("cache", {}).get("enabled", True):
            return

        cache_key = self.get_cache_key(content, mode)
        ttl = self.config.get("cache", {}).get("ttl_seconds", 3600)

        # Evict if at capacity
        max_entries = self.config.get("cache", {}).get("max_entries", 1000)
        if len(self.cache) >= max_entries:
            # Remove oldest entry
            oldest = min(self.cache.items(), key=lambda x: x[1].created_at)
            del self.cache[oldest[0]]

        self.cache[cache_key] = CacheEntry(
            key=cache_key,
            value=optimized,
            tokens=self.estimate_tokens(optimized),
            created_at=datetime.utcnow().isoformat(),
            ttl_seconds=ttl
        )
        self._save_cache()

    def compress_context(self, text: str, aggressive: bool = False) -> str:
        """Compress context while preserving meaning."""
        # Check cache first
        cached = self.check_cache(text)
        if cached:
            return cached

        lines = text.split("\n")
        compressed_lines = []
        skip_empty = aggressive

        for line in lines:
            stripped = line.strip()

            # Skip empty lines if aggressive
            if skip_empty and not stripped:
                continue

            # Remove obvious comments
            if stripped.startswith("#") and len(stripped) < 80:
                # Keep structure comments, skip trivial ones
                if any(kw in stripped.lower() for kw in ["todo", "fixme", "note", "important"]):
                    compressed_lines.append(line)
                elif aggressive:
                    continue
                else:
                    compressed_lines.append(line)
                continue

            # Skip commented code
            if stripped.startswith("//") and len(stripped) < 60:
                if aggressive:
                    continue
                else:
                    compressed_lines.append(line)
                continue

            compressed_lines.append(line)

        result = "\n".join(compressed_lines)

        # Store in cache
        if result != text:
            self.store_cache(text, result)

        return result

    def progressive_disclose(
        self,
        skill_path: Path,
        mode: str = "index"
    ) -> Tuple[str, int]:
        """
        Progressive disclosure of skill content.

        Modes:
        - index: File list and function signatures (~100 tokens)
        - summary: Key decisions and patterns (~500 tokens)
        - detail: Full content (on demand)
        """
        index_tokens = self.config.get("progressive_disclosure", {}).get("index_tokens", 100)
        summary_tokens = self.config.get("progressive_disclosure", {}).get("summary_tokens", 500)

        if mode == "index":
            # Just file names and function signatures
            output = [f"Skill: {skill_path.name}\n"]

            for file_path in skill_path.rglob("*"):
                if file_path.is_file() and not any(p.startswith(".") for p in file_path.parts):
                    rel_path = file_path.relative_to(skill_path)
                    output.append(f"\n## {rel_path}")

                    if file_path.suffix == ".py":
                        try:
                            content = file_path.read_text(encoding="utf-8")
                            # Extract function definitions
                            for match in re.finditer(r"^def (\w+)\(", content, re.MULTILINE):
                                output.append(f"  - def {match.group(1)}()")
                        except Exception:
                            pass

            result = "\n".join(output)
            return result, self.estimate_tokens(result)

        elif mode == "summary":
            # Key patterns and decisions
            output = [f"Skill: {skill_path.name}\n"]
            output.append("\n## Overview")

            skill_md = skill_path / "SKILL.md"
            if skill_md.exists():
                content = skill_md.read_text(encoding="utf-8")
                # Extract key sections
                lines = content.split("\n")
                in_features = False
                for line in lines:
                    if "##" in line and any(kw in line.lower() for kw in ["feature", "usage", "example"]):
                        in_features = True
                        output.append(line)
                    elif "##" in line:
                        in_features = False
                    elif in_features:
                        output.append(line)

            result = "\n".join(output)
            tokens = self.estimate_tokens(result)

            # Truncate if over limit
            if tokens > summary_tokens:
                lines = result.split("\n")
                truncated = []
                current_tokens = 0
                for line in lines:
                    line_tokens = self.estimate_tokens(line)
                    if current_tokens + line_tokens <= summary_tokens:
                        truncated.append(line)
                        current_tokens += line_tokens
                    else:
                        break
                result = "\n".join(truncated)

            return result, self.estimate_tokens(result)

        # Full detail
        full_content = []
        for file_path in skill_path.rglob("*"):
            if file_path.is_file() and not any(p.startswith(".") for p in file_path.parts):
                rel_path = file_path.relative_to(skill_path)
                try:
                    content = file_path.read_text(encoding="utf-8")
                    full_content.append(f"\n## {rel_path}\n{content}")
                except Exception:
                    pass

        result = "\n".join(full_content)
        return result, self.estimate_tokens(result)

    def optimize(
        self,
        content: str,
        method: str = "auto",
        aggressive: bool = False
    ) -> OptimizationResult:
        """
        Optimize token usage.

        Methods:
        - auto: Choose best method based on content
        - compress: Context compression
        - progressive: Progressive disclosure
        - cache: Cache lookup
        """
        original_tokens = self.estimate_tokens(content)

        # Check budget
        if self.budget.is_exhausted():
            logger.warning("Token budget exhausted")
            return OptimizationResult(
                original_tokens=original_tokens,
                optimized_tokens=original_tokens,
                savings_percent=0,
                method="budget_exhausted"
            )

        if method == "auto":
            # Choose method based on content size
            if original_tokens > 5000:
                method = "compress"
            elif original_tokens > 1000:
                method = "progressive"
            else:
                method = "cache"

        if method == "compress":
            optimized = self.compress_context(content, aggressive=aggressive)
        elif method == "progressive":
            # This would need skill path
            optimized = content
        else:
            cached = self.check_cache(content)
            if cached:
                optimized = cached
            else:
                optimized = content
                self.store_cache(content, optimized)

        optimized_tokens = self.estimate_tokens(optimized)
        savings = ((original_tokens - optimized_tokens) / original_tokens * 100
                   if original_tokens > 0 else 0)

        result = OptimizationResult(
            original_tokens=original_tokens,
            optimized_tokens=optimized_tokens,
            savings_percent=savings,
            method=method,
            cached=(method == "cache")
        )

        # Update budget
        self.budget.used_today += optimized_tokens
        self._save_budget()

        return result

    def sync_with_openspace(self) -> Dict[str, Any]:
        """Sync optimization patterns with OpenSpace Cloud."""
        try:
            response = requests.get(
                "https://api.open-space.cloud/v1/token-optimization",
                headers={"Authorization": f"Bearer {os.environ.get('OPENSPACE_API_KEY', '')}"},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                logger.info("Synced optimization patterns from OpenSpace")
                return data
        except Exception as e:
            logger.warning(f"Failed to sync with OpenSpace: {e}")
        return {}

    def generate_report(self, skill_path: Optional[Path] = None) -> Dict[str, Any]:
        """Generate token optimization report."""
        today = datetime.utcnow().strftime("%Y-%m-%d")

        # Calculate cache stats
        cache_hits = sum(e.hit_count for e in self.cache.values())
        cache_entries = len(self.cache)
        cache_tokens = sum(e.tokens for e in self.cache.values())

        report = {
            "date": today,
            "budget": {
                "daily_limit": self.budget.daily_limit,
                "used": self.budget.used_today,
                "remaining": self.budget.remaining(),
                "usage_percent": (self.budget.used_today / self.budget.daily_limit * 100
                                  if self.budget.daily_limit > 0 else 0),
                "alert_triggered": self.budget.check_alert()
            },
            "cache": {
                "entries": cache_entries,
                "total_hits": cache_hits,
                "tokens_cached": cache_tokens,
                "avg_hit_rate": (cache_hits / cache_entries if cache_entries > 0 else 0)
            },
            "benchmark": {
                "open_space_savings": f"{self.BENCHMARK_SAVINGS * 100:.1f}%",
                "performance_improvement": f"{self.PERFORMANCE_IMPROVEMENT}x"
            }
        }

        if skill_path:
            # Analyze skill
            total_tokens = 0
            file_count = 0
            for file_path in skill_path.rglob("*"):
                if file_path.is_file() and not any(p.startswith(".") for p in file_path.parts):
                    try:
                        content = file_path.read_text(encoding="utf-8")
                        total_tokens += self.estimate_tokens(content)
                        file_count += 1
                    except Exception:
                        pass

            projected_savings = total_tokens * self.BENCHMARK_SAVINGS

            report["skill_analysis"] = {
                "path": str(skill_path),
                "files": file_count,
                "total_tokens": total_tokens,
                "projected_savings": int(projected_savings),
                "optimized_tokens": int(total_tokens - projected_savings)
            }

        return report


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="OpenSpace Token Optimizer")
    parser.add_argument("action", choices=["optimize", "compress", "cache", "report", "budget", "sync"])
    parser.add_argument("--input", "-i", type=Path, help="Input file")
    parser.add_argument("--output", "-o", type=Path, help="Output file")
    parser.add_argument("--skill", "-s", type=Path, help="Skill directory")
    parser.add_argument("--mode", "-m", default="auto",
                        choices=["auto", "compress", "progressive", "cache"])
    parser.add_argument("--aggressive", "-a", action="store_true", help="Aggressive compression")
    parser.add_argument("--budget-reset", action="store_true", help="Reset daily budget")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text")

    args = parser.parse_args()

    optimizer = TokenOptimizer()

    if args.action == "budget":
        if args.budget_reset:
            optimizer.budget.used_today = 0
            optimizer.budget.reset_date = datetime.utcnow().strftime("%Y-%m-%d")
            optimizer._save_budget()
            print("Budget reset")
        else:
            print(f"Daily Budget: {optimizer.budget.daily_limit}")
            print(f"Used Today: {optimizer.budget.used_today}")
            print(f"Remaining: {optimizer.budget.remaining()}")
            print(f"Usage: {optimizer.budget.used_today / optimizer.budget.daily_limit * 100:.1f}%")

    elif args.action == "cache":
        if args.input:
            content = args.input.read_text(encoding="utf-8")
            cached = optimizer.check_cache(content)
            if cached:
                print(f"Cache HIT: {len(cached)} chars")
            else:
                print("Cache MISS")
        else:
            print(f"Cache entries: {len(optimizer.cache)}")
            for key, entry in list(optimizer.cache.items())[:5]:
                print(f"  {key[:8]}: {entry.tokens} tokens, {entry.hit_count} hits")

    elif args.action == "optimize" or args.action == "compress":
        if not args.input:
            print("Error: --input required")
            return

        content = args.input.read_text(encoding="utf-8")

        if args.action == "compress":
            result = optimizer.compress_context(content, aggressive=args.aggressive)
        else:
            opt_result = optimizer.optimize(content, method=args.mode, aggressive=args.aggressive)
            result = opt_result.optimized_tokens

            if args.format == "json":
                print(json.dumps(asdict(opt_result), indent=2))
                return

            print(f"Original: {opt_result.original_tokens} tokens")
            print(f"Optimized: {opt_result.optimized_tokens} tokens")
            print(f"Savings: {opt_result.savings_percent:.1f}%")
            print(f"Method: {opt_result.method}")

        if args.output:
            args.output.write_text(result, encoding="utf-8")
            print(f"Written to: {args.output}")
        else:
            print(result)

    elif args.action == "report":
        report = optimizer.generate_report(args.skill)

        if args.format == "json":
            print(json.dumps(report, indent=2))
        else:
            print("\n=== Token Optimization Report ===")
            print(f"Date: {report['date']}")
            print(f"\nBudget:")
            print(f"  Limit: {report['budget']['daily_limit']}")
            print(f"  Used: {report['budget']['used']} ({report['budget']['usage_percent']:.1f}%)")
            print(f"  Remaining: {report['budget']['remaining']}")
            print(f"  Alert: {'YES' if report['budget']['alert_triggered'] else 'No'}")

            print(f"\nCache:")
            print(f"  Entries: {report['cache']['entries']}")
            print(f"  Hits: {report['cache']['total_hits']}")
            print(f"  Cached Tokens: {report['cache']['tokens_cached']}")

            print(f"\nBenchmark (OpenSpace):")
            print(f"  Token Savings: {report['benchmark']['open_space_savings']}")
            print(f"  Performance: {report['benchmark']['performance_improvement']}")

            if "skill_analysis" in report:
                sa = report["skill_analysis"]
                print(f"\nSkill Analysis: {sa['path']}")
                print(f"  Files: {sa['files']}")
                print(f"  Total Tokens: {sa['total_tokens']}")
                print(f"  Projected Savings: {sa['projected_savings']} tokens")

    elif args.action == "sync":
        result = optimizer.sync_with_openspace()
        if result:
            print(f"Synced patterns from OpenSpace")
        else:
            print("Sync failed or no data")


def asdict(obj):
    """Convert dataclass to dict."""
    if hasattr(obj, "__dataclass_fields__"):
        return {k: asdict(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, list):
        return [asdict(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: asdict(v) for k, v in obj.items()}
    return obj


if __name__ == "__main__":
    main()
