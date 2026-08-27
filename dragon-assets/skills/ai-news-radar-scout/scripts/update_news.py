#!/usr/bin/env python3
"""
AI News Radar - 新闻更新Pipeline
抓取 → 去重与归一化 → AI强相关过滤 → 源健康统计 → 输出JSON
"""

import argparse
import json
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import pytz

try:
    import feedparser
except ImportError:
    print("错误: 请先安装依赖 pip install feedparser")
    exit(1)


class NewsPipeline:
    """新闻更新Pipeline"""

    def __init__(self, window_hours: int = 24):
        self.window_hours = window_hours
        self.articles = []
        self.seen_urls = set()
        self.seen_hashes = set()

    def fetch_rss(self, url: str) -> List[dict]:
        """抓取RSS源"""
        articles = []
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                article = {
                    "title": entry.get("title", ""),
                    "url": entry.get("link") or entry.get("href", ""),
                    "source": feed.feed.get("title", url),
                    "published": entry.get("published") or entry.get("updated", ""),
                    "summary": entry.get("summary", "")[:500],
                }
                articles.append(article)
        except Exception as e:
            print(f"抓取失败 {url}: {e}")
        return articles

    def deduplicate(self, articles: List[dict]) -> List[dict]:
        """去重与归一化"""
        deduped = []
        for article in articles:
            url_hash = hashlib.md5(article["url"].encode()).hexdigest()
            if url_hash not in self.seen_hashes:
                self.seen_hashes.add(url_hash)
                article["url_hash"] = url_hash
                deduped.append(article)
        return deduped

    def filter_ai_relevant(self, article: dict) -> tuple:
        """
        AI强相关过滤
        返回: (is_relevant, score, reason)
        """
        ai_keywords = [
            "ai", "artificial intelligence", "machine learning", "deep learning",
            "llm", "large language model", "gpt", "claude", "gemini",
            "openai", "anthropic", "mistral", "perplexity", "groq",
            "neural network", "transformer", "nlp", "nlu",
            "chatbot", "generative", "rag", "agent", "copilot",
            "api", "model", "benchmark", "research", "paper"
        ]

        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
        matches = [kw for kw in ai_keywords if kw in text]
        score = len(matches) / len(ai_keywords)

        if score > 0.05:
            return True, score, f"命中关键词: {matches[:5]}"
        return False, score, "AI相关性不足"

    def is_within_window(self, article: dict) -> bool:
        """检查是否在时间窗口内"""
        if not article.get("published"):
            return True

        try:
            # 简单实现，实际需要更复杂的日期解析
            return True
        except:
            return True

    def process_source(self, url: str) -> int:
        """处理单个信息源"""
        articles = self.fetch_rss(url)
        count = 0

        for article in articles:
            if not self.is_within_window(article):
                continue

            article = self.deduplicate([article])[0]

            is_relevant, score, reason = self.filter_ai_relevant(article)
            article["ai_relevance_score"] = round(score, 3)
            article["ai_relevance_reason"] = reason

            if is_relevant:
                self.articles.append(article)
                count += 1

        return count

    def run(self, source_urls: List[str]) -> dict:
        """执行完整Pipeline"""
        healthy_count = 0
        unhealthy_count = 0

        for url in source_urls:
            try:
                count = self.process_source(url)
                if count > 0:
                    healthy_count += 1
                else:
                    unhealthy_count += 1
            except Exception as e:
                unhealthy_count += 1
                print(f"处理失败 {url}: {e}")

        # 按AI相关性排序
        self.articles.sort(key=lambda x: x.get("ai_relevance_score", 0), reverse=True)

        return {
            "timestamp": datetime.now(pytz.UTC).isoformat(),
            "window_hours": self.window_hours,
            "total_sources": len(source_urls),
            "healthy_sources": healthy_count,
            "unhealthy_sources": unhealthy_count,
            "total_articles": len(self.articles),
            "articles": self.articles
        }


def load_sources(config_path: str) -> List[str]:
    """从配置文件加载信息源"""
    config = Path(config_path)
    if config.exists():
        data = json.loads(config.read_text(encoding="utf-8"))
        return data.get("sources", [])
    return []


def main():
    parser = argparse.ArgumentParser(description="AI News Radar - 新闻更新Pipeline")
    parser.add_argument("--sources", help="信息源配置文件(JSON)")
    parser.add_argument("--source-list", nargs="+", help="信息源URL列表")
    parser.add_argument("--output-dir", default="data", help="输出目录")
    parser.add_argument("--window-hours", type=int, default=24, help="时间窗口(小时)")
    parser.add_argument("--format", choices=["json", "jsonl"], default="json", help="输出格式")

    args = parser.parse_args()

    # 加载信息源
    if args.sources:
        urls = load_sources(args.sources)
    elif args.source_list:
        urls = args.source_list
    else:
        # 默认信息源
        urls = [
            "https://openai.com/index/feed/",
            "https://www.anthropic.com/news/rss",
            "https://deepmind.google/blog/rss.xml",
            "https://ai.meta.com/blog/rss.xml",
        ]

    # 执行Pipeline
    pipeline = NewsPipeline(window_hours=args.window_hours)
    result = pipeline.run(urls)

    # 输出结果
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"news_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✅ 更新完成: {len(result['articles'])} 篇AI相关新闻")
    print(f"📁 输出文件: {output_file}")


if __name__ == "__main__":
    main()
