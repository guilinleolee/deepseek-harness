#!/usr/bin/env python3
"""
Wiki 自适应检索路由核心
基于 Karpathy LLM Wiki Pattern，根据知识库规模自动选择最优检索策略

Usage:
    python3 router.py query "微服务架构"
    python3 router.py query "微服务" --strategy full-scan
    python3 router.py query "微服务" --budget 2000
    python3 router.py batch queries.txt
"""

import argparse
import json
import re
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

WIKI_DIR = Path.home() / ".claude" / "wiki"
CACHE_DIR = Path.home() / ".claude" / "wiki_router_cache"
CACHE_FILE = CACHE_DIR / "query_cache.json"


class Strategy(Enum):
    FULL_SCAN = "full-scan"
    GREP_SCAN = "grep-scan"
    VECTOR_SEARCH = "vector-search"
    AUTO = "auto"


@dataclass
class RetrievalResult:
    """检索结果"""
    note_id: str
    title: str
    path: Path
    content: str
    relevance_score: float
    strategy_used: str
    query_time_ms: float
    snippet: str = ""


@dataclass
class RoutingDecision:
    """路由决策"""
    strategy: Strategy
    corpus_size: int
    estimated_time_ms: float
    reasoning: str
    cache_hit: bool = False


@dataclass
class RetrievalStats:
    """检索统计"""
    total_results: int
    total_time_ms: float
    strategies_used: dict
    cache_hits: int
    budget_used_ms: float


class AdaptiveRouter:
    """自适应检索路由器"""

    # 阈值配置
    FULL_SCAN_MAX = 100
    GREP_SCAN_MAX = 1000

    # 性能预算
    BUDGET_MS = 3000
    TOP_K = 10

    def __init__(self, wiki_dir: Optional[Path] = None):
        self.wiki_dir = wiki_dir or WIKI_DIR
        self.cache = self._load_cache()
        self.corpus_size = self._count_notes()

    def _load_cache(self) -> dict:
        """加载查询缓存"""
        if CACHE_FILE.exists():
            try:
                return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            except:
                pass
        return {}

    def _save_cache(self):
        """保存查询缓存"""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(
            json.dumps(self.cache, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def _count_notes(self) -> int:
        """统计笔记数量"""
        if not self.wiki_dir.exists():
            return 0
        return len(list(self.wiki_dir.glob("*.md")))

    def _select_strategy(self, query: str, force_strategy: Optional[Strategy] = None) -> RoutingDecision:
        """选择检索策略"""
        if force_strategy and force_strategy != Strategy.AUTO:
            return RoutingDecision(
                strategy=force_strategy,
                corpus_size=self.corpus_size,
                estimated_time_ms=self._estimate_time(force_strategy),
                reasoning=f"强制使用 {force_strategy.value}"
            )

        # 缓存命中
        cache_key = query.lower().strip()
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            return RoutingDecision(
                strategy=Strategy(cached["strategy"]),
                corpus_size=self.corpus_size,
                estimated_time_ms=0,
                reasoning="缓存命中",
                cache_hit=True
            )

        # 规模感知策略选择
        if self.corpus_size < self.FULL_SCAN_MAX:
            strategy = Strategy.FULL_SCAN
            reasoning = f"个人级规模 ({self.corpus_size} 篇 < {self.FULL_SCAN_MAX})"
        elif self.corpus_size < self.GREP_SCAN_MAX:
            strategy = Strategy.GREP_SCAN
            reasoning = f"团队级规模 ({self.corpus_size} 篇, {self.FULL_SCAN_MAX}-{self.GREP_SCAN_MAX})"
        else:
            strategy = Strategy.VECTOR_SEARCH
            reasoning = f"企业级规模 ({self.corpus_size} 篇 > {self.GREP_SCAN_MAX})"

        return RoutingDecision(
            strategy=strategy,
            corpus_size=self.corpus_size,
            estimated_time_ms=self._estimate_time(strategy),
            reasoning=reasoning
        )

    def _estimate_time(self, strategy: Strategy) -> float:
        """估算检索时间(ms)"""
        estimates = {
            Strategy.FULL_SCAN: 5 * (self.corpus_size / 50),  # ~5ms per 50 notes
            Strategy.GREP_SCAN: 50 + 10 * (self.corpus_size / 200),  # ~50ms base
            Strategy.VECTOR_SEARCH: 200,  # ~200ms for vector search
        }
        return estimates.get(strategy, 100)

    def _extract_title(self, content: str, filename: str) -> str:
        """提取笔记标题"""
        if content.startswith("# "):
            return content.split("\n")[0][2:].strip()
        elif content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                for line in parts[1].split("\n"):
                    if line.startswith("title:"):
                        return line.split(":", 1)[1].strip()
        return filename.replace("-", " ").replace("_", " ").title()

    def _calculate_relevance(self, content: str, query: str) -> float:
        """计算相关性分数"""
        query_lower = query.lower()
        content_lower = content.lower()

        score = 0.0

        # 标题匹配 (高权重)
        lines = content.split("\n")
        title = self._extract_title(content, "")
        if query_lower in title.lower():
            score += 0.5

        # 关键词出现次数
        words = query_lower.split()
        for word in words:
            count = content_lower.count(word)
            score += min(count * 0.1, 0.3)

        # 第一次出现位置 (早出现更好)
        first_pos = content_lower.find(query_lower)
        if first_pos >= 0:
            score += max(0, 0.2 - first_pos / len(content) * 0.2)

        return min(score, 1.0)

    def _get_snippet(self, content: str, query: str, max_len: int = 200) -> str:
        """获取匹配片段"""
        query_lower = query.lower()
        content_lower = content.lower()
        pos = content_lower.find(query_lower)

        if pos < 0:
            return content[:max_len] + "..."

        start = max(0, pos - 50)
        end = min(len(content), pos + len(query) + 150)
        snippet = content[start:end].strip()

        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def full_scan(self, query: str, budget_ms: float = BUDGET_MS) -> list[RetrievalResult]:
        """Full-Scan 个人级检索 (<100笔记)"""
        start_time = time.time()
        results = []

        if not self.wiki_dir.exists():
            return results

        for md_file in self.wiki_dir.glob("*.md"):
            if time.time() - start_time > budget_ms / 1000:
                break

            try:
                content = md_file.read_text(encoding="utf-8")
                if query.lower() in content.lower():
                    title = self._extract_title(content, md_file.stem)
                    relevance = self._calculate_relevance(content, query)

                    results.append(RetrievalResult(
                        note_id=md_file.stem,
                        title=title,
                        path=md_file,
                        content=content,
                        relevance_score=relevance,
                        strategy_used="full-scan",
                        query_time_ms=(time.time() - start_time) * 1000,
                        snippet=self._get_snippet(content, query)
                    ))
            except Exception as e:
                continue

        # 按相关性排序
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:self.TOP_K]

    def grep_scan(self, query: str, budget_ms: float = BUDGET_MS) -> list[RetrievalResult]:
        """Grep-Scan 团队级检索 (100-1000笔记)"""
        start_time = time.time()
        results = []

        if not self.wiki_dir.exists():
            return results

        # 阶段1: 标题索引匹配
        candidates = []
        for md_file in self.wiki_dir.glob("*.md"):
            title = md_file.stem.replace("-", " ").replace("_", " ").lower()
            if query.lower() in title:
                candidates.append(md_file)

        # 阶段2: 内容grep验证
        for md_file in candidates:
            if time.time() - start_time > budget_ms / 1000:
                break

            try:
                content = md_file.read_text(encoding="utf-8")
                if query.lower() in content.lower():
                    title = self._extract_title(content, md_file.stem)
                    relevance = self._calculate_relevance(content, query)

                    results.append(RetrievalResult(
                        note_id=md_file.stem,
                        title=title,
                        path=md_file,
                        content=content,
                        relevance_score=relevance,
                        strategy_used="grep-scan",
                        query_time_ms=(time.time() - start_time) * 1000,
                        snippet=self._get_snippet(content, query)
                    ))
            except Exception as e:
                continue

        # 未匹配标题的笔记也扫描
        title_matched = {r.note_id for r in results}
        for md_file in self.wiki_dir.glob("*.md"):
            if md_file.stem in title_matched:
                continue
            if time.time() - start_time > budget_ms / 1000:
                break

            try:
                content = md_file.read_text(encoding="utf-8")
                if query.lower() in content.lower():
                    title = self._extract_title(content, md_file.stem)
                    relevance = self._calculate_relevance(content, query)

                    results.append(RetrievalResult(
                        note_id=md_file.stem,
                        title=title,
                        path=md_file,
                        content=content,
                        relevance_score=relevance,
                        strategy_used="grep-scan",
                        query_time_ms=(time.time() - start_time) * 1000,
                        snippet=self._get_snippet(content, query)
                    ))
            except Exception as e:
                continue

        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:self.TOP_K]

    def vector_search(self, query: str, budget_ms: float = BUDGET_MS) -> list[RetrievalResult]:
        """Vector-Search 企业级检索 (>1000笔记)"""
        start_time = time.time()

        # 尝试使用 LightRAG
        try:
            from lightrag import LightRAG
            rag = LightRAG(working_dir=str(CACHE_DIR / "lightrag_cache"))
            rag.insert_dir(str(self.wiki_dir))
            response = rag.query(query, mode="hybrid")

            # 解析响应并生成结果
            results = [
                RetrievalResult(
                    note_id="vector-1",
                    title="LightRAG 检索结果",
                    path=self.wiki_dir,
                    content=response,
                    relevance_score=0.9,
                    strategy_used="vector-search",
                    query_time_ms=(time.time() - start_time) * 1000,
                    snippet=response[:300] + "..."
                )
            ]
            return results

        except ImportError:
            # LightRAG 未安装，回退到 grep-scan
            return self.grep_scan(query, budget_ms)
        except Exception as e:
            # 出错时回退
            return self.grep_scan(query, budget_ms)

    def query(self, query: str, strategy: Optional[Strategy] = None,
              budget_ms: float = BUDGET_MS, top_k: int = TOP_K) -> list[RetrievalResult]:
        """执行检索"""
        self.TOP_K = top_k
        self.BUDGET_MS = budget_ms

        # 路由决策
        decision = self._select_strategy(query, strategy)

        # 缓存命中
        if decision.cache_hit:
            cached_results = self.cache.get(query.lower().strip(), {}).get("results", [])
            return [RetrievalResult(
                note_id=r["note_id"],
                title=r["title"],
                path=Path(r.get("path", "")),
                content=r.get("content", ""),
                relevance_score=r.get("relevance", 0.5),
                strategy_used=r.get("strategy", "cache"),
                query_time_ms=0,
                snippet=r.get("snippet", "")
            ) for r in cached_results]

        # 执行检索
        start_time = time.time()
        if decision.strategy == Strategy.FULL_SCAN:
            results = self.full_scan(query, budget_ms)
        elif decision.strategy == Strategy.GREP_SCAN:
            results = self.grep_scan(query, budget_ms)
        else:
            results = self.vector_search(query, budget_ms)

        total_time = (time.time() - start_time) * 1000

        # 更新缓存
        self.cache[query.lower().strip()] = {
            "strategy": decision.strategy.value,
            "results": [
                {
                    "note_id": r.note_id,
                    "title": r.title,
                    "path": str(r.path),
                    "snippet": r.snippet,
                    "relevance": r.relevance_score
                }
                for r in results
            ],
            "timestamp": time.time()
        }
        self._save_cache()

        # 打印路由信息
        print(f"\n📊 路由决策:")
        print(f"   策略: {decision.strategy.value}")
        print(f"   规模: {decision.corpus_size} 篇笔记")
        print(f"   推理: {decision.reasoning}")
        print(f"   耗时: {total_time:.1f}ms")
        print(f"   结果: {len(results)} 条")

        return results

    def get_stats(self) -> dict:
        """获取路由器统计"""
        return {
            "corpus_size": self.corpus_size,
            "strategy": self._select_strategy("").strategy.value,
            "cache_size": len(self.cache),
            "wiki_dir": str(self.wiki_dir),
            "thresholds": {
                "full_scan_max": self.FULL_SCAN_MAX,
                "grep_scan_max": self.GREP_SCAN_MAX
            }
        }


def format_results(results: list[RetrievalResult]) -> str:
    """格式化检索结果"""
    if not results:
        return "\n❌ 未找到匹配结果\n"

    lines = [
        f"\n{'='*60}",
        f"检索结果 ({len(results)} 条)",
        f"{'='*60}\n"
    ]

    for i, r in enumerate(results, 1):
        score_bar = "█" * int(r.relevance_score * 10) + "░" * (10 - int(r.relevance_score * 10))
        lines.append(f"{i}. {r.title}")
        lines.append(f"   📊 相关性: {score_bar} {r.relevance_score:.1%}")
        lines.append(f"   ⏱️ 耗时: {r.query_time_ms:.0f}ms")
        lines.append(f"   📁 路径: {r.path.name}")
        lines.append(f"   💡 片段: {r.snippet[:100]}...")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Wiki 自适应检索路由")
    parser.add_argument("action", choices=["query", "stats"], help="操作类型")
    parser.add_argument("query", nargs="?", help="检索查询")
    parser.add_argument("--strategy", "-s", choices=["full-scan", "grep-scan", "vector-search", "auto"],
                       default="auto", help="检索策略")
    parser.add_argument("--budget", "-b", type=int, default=3000, help="时间预算(ms)")
    parser.add_argument("--top-k", "-k", type=int, default=10, help="返回结果数")
    parser.add_argument("--json", "-j", action="store_true", help="JSON格式输出")
    parser.add_argument("--batch", help="批量查询文件")

    args = parser.parse_args()

    router = AdaptiveRouter()

    if args.action == "stats":
        stats = router.get_stats()
        if args.json:
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        else:
            print(f"\n📊 路由器统计:")
            print(f"   笔记总数: {stats['corpus_size']}")
            print(f"   推荐策略: {stats['strategy']}")
            print(f"   缓存条目: {stats['cache_size']}")
            print(f"   阈值配置:")
            print(f"     - Full-Scan: < {stats['thresholds']['full_scan_max']} 篇")
            print(f"     - Grep-Scan: {stats['thresholds']['full_scan_max']}-{stats['thresholds']['grep_scan_max']} 篇")
            print(f"     - Vector-Search: > {stats['thresholds']['grep_scan_max']} 篇")
        return

    if args.action == "query":
        if not args.query:
            parser.print_help()
            return

        strategy = Strategy(args.strategy) if args.strategy != "auto" else None
        results = router.query(
            args.query,
            strategy=strategy,
            budget_ms=args.budget,
            top_k=args.top_k
        )

        if args.json:
            output = [
                {
                    "note_id": r.note_id,
                    "title": r.title,
                    "path": str(r.path),
                    "relevance_score": r.relevance_score,
                    "strategy_used": r.strategy_used,
                    "query_time_ms": r.query_time_ms,
                    "snippet": r.snippet
                }
                for r in results
            ]
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            print(format_results(results))


if __name__ == "__main__":
    main()
