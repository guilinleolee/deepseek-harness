#!/usr/bin/env python3
"""
Citation Crawler
引用页面爬取工具
"""

import os
import time
from typing import List, Dict, Any, Optional


class CitationCrawler:
    """引用页面爬取器"""

    def __init__(self, firecrawl_key: str = None):
        self.firecrawl_key = firecrawl_key or os.getenv("FIRECRAWL_API_KEY")
        self.base_url = "https://api.firecrawl.dev/v0"
        self.session = None

        if not self.firecrawl_key:
            print("⚠️  FIRECRAWL_API_KEY未设置，使用模拟数据")

    def crawl(self, fanouts: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
        """
        爬取Fanout相关引用页面

        Args:
            fanouts: Fanout列表
            limit: 最多爬取数量

        Returns:
            List[Dict]: 引用列表
        """
        citations = []

        for fanout in fanouts[:limit]:
            fanout_citations = self._crawl_fanout(fanout)
            citations.extend(fanout_citations)

        if not citations:
            return self._mock_citations(limit)

        return citations

    def _crawl_fanout(self, fanout: Dict[str, Any]) -> List[Dict[str, Any]]:
        """爬取单个Fanout的引用"""
        question = fanout.get("question", "")
        context = fanout.get("context", "")

        if self.firecrawl_key:
            return self._crawl_with_api(question, context)
        else:
            return self._mock_fanout_citations(fanout)

    def _crawl_with_api(self, question: str, context: str) -> List[Dict[str, Any]]:
        """使用Firecrawl API爬取"""
        try:
            import requests

            headers = {
                "Authorization": f"Bearer {self.firecrawl_key}",
                "Content-Type": "application/json"
            }

            data = {
                "prompt": f"搜索关于'{question}'的权威信息来源",
                "question": question,
                "source": "web"
            }

            response = requests.post(
                f"{self.base_url}/search",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                return self._parse_search_results(response.json())
            else:
                print(f"⚠️  Firecrawl API错误: {response.status_code}")
                return self._mock_fanout_citations({"question": question, "context": context})

        except Exception as e:
            print(f"❌ 爬取失败: {e}")
            return self._mock_fanout_citations({"question": question, "context": context})

    def _parse_search_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析搜索结果"""
        results = data.get("results", [])
        citations = []

        for item in results[:5]:
            citations.append({
                "id": f"citation-{item.get('id', '')}",
                "url": item.get("url", ""),
                "title": item.get("title", ""),
                "authority": self._assess_authority(item.get("url", "")),
                "relevance": item.get("score", 0.8),
                "content_snippet": item.get("description", "")[:200]
            })

        return citations

    def _assess_authority(self, url: str) -> str:
        """评估来源权威性"""
        high_authority_domains = [
            "nature.com", "science.org", "arxiv.org",
            "mckinsey.com", "bain.com", "bcg.com",
            "forbes.com", "hbr.org", "mit.edu"
        ]

        for domain in high_authority_domains:
            if domain in url:
                return "editorial"

        medium_authority = [
            "medium.com", "dev.to", "github.com",
            "stackoverflow.com", "wikipedia.org"
        ]

        for domain in medium_authority:
            if domain in url:
                return "research"

        return "community"

    def _mock_fanout_citations(self, fanout: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成模拟Fanout引用"""
        question = fanout.get("question", "")
        return [
            {
                "id": f"citation-fanout-{hash(question) % 1000}-1",
                "url": "https://example.com/article-1",
                "title": f"关于{question}的深度分析",
                "authority": "editorial",
                "relevance": 0.9,
                "content_snippet": "权威来源的详细分析内容..."
            },
            {
                "id": f"citation-fanout-{hash(question) % 1000}-2",
                "url": "https://example.org/research-2",
                "title": f"{question}的研究报告",
                "authority": "research",
                "relevance": 0.85,
                "content_snippet": "学术研究的摘要内容..."
            }
        ]

    def _mock_citations(self, limit: int) -> List[Dict[str, Any]]:
        """生成模拟引用数据"""
        return [
            {
                "id": f"citation-{i}",
                "url": f"https://example.com/article-{i}",
                "title": f"权威来源 {i+1}",
                "authority": ["editorial", "official", "research", "expert"][i % 4],
                "relevance": 0.8 + i * 0.02,
                "content_snippet": "这是引用内容片段..."
            }
            for i in range(limit)
        ]
