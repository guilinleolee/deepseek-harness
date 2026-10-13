"""
fincept-news-intel - 新闻智能分析客户端

提供新闻抓取、情感分析、主题聚类、实体关联和 SEC 公告追踪能力。
"""

import os
import json
import time
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta

import requests

try:
    from .sentiment import SentimentAnalyzer
    from .clustering import NewsClustering
    from .correlation import EntityCorrelator
    from .sec_filings import SECFilingsTracker
except ImportError:
    # Standalone mode
    from sentiment import SentimentAnalyzer
    from clustering import NewsClustering
    from correlation import EntityCorrelator
    from sec_filings import SECFilingsTracker


class NewsIntelError(Exception):
    """新闻智能分析错误"""
    pass


class NewsIntelligence:
    """
    新闻智能分析主类

    提供新闻抓取、情感分析、主题聚类、实体关联和 SEC 公告追踪能力。
    """

    def __init__(
        self,
        newsapi_key: Optional[str] = None,
        finnhub_key: Optional[str] = None,
        polygon_key: Optional[str] = None,
        alpha_key: Optional[str] = None,
        cache_dir: Optional[str] = None
    ):
        """
        初始化新闻智能分析客户端。

        Args:
            newsapi_key: NewsAPI API Key
            finnhub_key: FinnHub API Key
            polygon_key: Polygon.io API Key
            alpha_key: Alpha Vantage API Key
            cache_dir: 缓存目录路径
        """
        self.newsapi_key = newsapi_key or os.getenv("NEWS_API_KEY")
        self.finnhub_key = finnhub_key or os.getenv("FINNHUB_API_KEY")
        self.polygon_key = polygon_key or os.getenv("POLYGON_API_KEY")
        self.alpha_key = alpha_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/fincept-news-intel")

        # 初始化子模块
        self._sentiment = SentimentAnalyzer()
        self._clustering = NewsClustering()
        self._correlation = EntityCorrelator()
        self._sec = SECFilingsTracker()

        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)

    def search(
        self,
        query: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        source: str = "all",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        搜索新闻。

        Args:
            query: 搜索关键词
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            source: 新闻源 (bloomberg/reuters/wsj/sec/all)
            limit: 返回数量上限

        Returns:
            新闻列表

        Raises:
            NewsIntelError: API 调用失败
        """
        if not query:
            raise NewsIntelError("搜索关键词不能为空")

        # 优先使用 FinnHub（更稳定）
        if self.finnhub_key:
            return self._search_finnhub(query, limit)

        # 备用 NewsAPI
        if self.newsapi_key:
            return self._search_newsapi(query, start_date, end_date, limit)

        # 离线模式（返回模拟数据）
        return self._mock_news(query, limit)

    def _search_finnhub(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """使用 FinnHub 搜索新闻"""
        try:
            import finnhub

            client = finnhub.Client(api_key=self.finnhub_key)
            news = client.company_news(query.upper(), _from="2024-01-01", to="2024-12-31")

            results = []
            for item in news[:limit]:
                results.append({
                    "title": item.get("headline", ""),
                    "source": item.get("source", ""),
                    "date": item.get("datetime", ""),
                    "url": item.get("url", ""),
                    "summary": item.get("summary", ""),
                    "content": item.get("body", ""),
                    "entities": self._extract_entities(item.get("headline", "") + " " + item.get("summary", ""))
                })

            return results

        except Exception as e:
            raise NewsIntelError(f"FinnHub API 调用失败: {str(e)}") from e

    def _search_newsapi(
        self,
        query: str,
        start_date: Optional[str],
        end_date: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """使用 NewsAPI 搜索新闻"""
        try:
            from newsapi import NewsApiClient

            client = NewsApiClient(api_key=self.newsapi_key)

            # 处理日期
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

            response = client.get_everything(
                q=query,
                from_param=start_date,
                to=end_date,
                language="en",
                sort_by="relevancy",
                page_size=min(limit, 100)
            )

            results = []
            for article in response.get("articles", [])[:limit]:
                results.append({
                    "title": article.get("title", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "date": article.get("publishedAt", "")[:10],
                    "url": article.get("url", ""),
                    "summary": article.get("description", ""),
                    "content": article.get("content", ""),
                    "entities": self._extract_entities(
                        article.get("title", "") + " " + article.get("description", "")
                    )
                })

            return results

        except Exception as e:
            raise NewsIntelError(f"NewsAPI 调用失败: {str(e)}") from e

    def _mock_news(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """离线模式返回模拟数据"""
        return [
            {
                "title": f"Mock Article about {query} #1",
                "source": "MockSource",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "url": "https://example.com/1",
                "summary": f"This is a mock article about {query} for testing purposes.",
                "content": f"Full content of mock article about {query}...",
                "entities": [query]
            }
        ]

    def _extract_entities(self, text: str) -> List[str]:
        """简单实体提取（基于大写字母模式）"""
        import re
        # 简单匹配大写字母开头的单词
        entities = re.findall(r'\b[A-Z][A-Z0-9]{1,}\b', text)
        return list(set(entities))[:10]  # 去重，最多10个

    def sentiment(self, text: str) -> Dict[str, Any]:
        """
        单条文本情感分析。

        Args:
            text: 待分析文本

        Returns:
            情感分析结果 {
                "label": str,      # positive/negative/neutral
                "score": float,    # -1 to 1
                "confidence": float  # 0 to 1
            }

        Raises:
            NewsIntelError: 分析失败
        """
        if not text:
            raise NewsIntelError("分析文本不能为空")

        try:
            return self._sentiment.analyze(text)
        except Exception as e:
            raise NewsIntelError(f"情感分析失败: {str(e)}") from e

    def batch_sentiment(
        self,
        news: List[Dict[str, Any]],
        batch_size: int = 32
    ) -> List[Dict[str, Any]]:
        """
        批量情感分析。

        Args:
            news: 新闻列表（需要包含 summary 或 content 字段）
            batch_size: 批大小

        Returns:
            情感分析结果列表

        Raises:
            NewsIntelError: 分析失败
        """
        if not news:
            return []

        texts = []
        for item in news:
            text = item.get("summary") or item.get("content") or item.get("title", "")
            texts.append(text)

        try:
            return self._sentiment.batch_analyze(texts, batch_size)
        except Exception as e:
            raise NewsIntelError(f"批量情感分析失败: {str(e)}") from e

    def cluster(
        self,
        news: List[Dict[str, Any]],
        n_clusters: int = 5,
        method: str = "hdbscan"
    ) -> List[Dict[str, Any]]:
        """
        新闻主题聚类。

        Args:
            news: 新闻列表
            n_clusters: 目标聚类数量
            method: 聚类方法 (hdbscan/kmeans)

        Returns:
            聚类结果列表 [{
                "topic": str,           # 主题描述
                "size": int,            # 文章数量
                "keywords": List[str], # 核心关键词
                "articles": List[Dict]  # 文章列表
            }]

        Raises:
            NewsIntelError: 聚类失败
        """
        if not news:
            raise NewsIntelError("聚类新闻列表不能为空")

        try:
            return self._clustering.cluster(news, n_clusters, method)
        except Exception as e:
            raise NewsIntelError(f"主题聚类失败: {str(e)}") from e

    def correlate(
        self,
        entity: str,
        date_range: Optional[Tuple[str, str]] = None
    ) -> Dict[str, Any]:
        """
        实体关联分析。

        Args:
            entity: 实体名称（公司/人物/事件）
            date_range: 日期范围 (start_date, end_date)

        Returns:
            关联分析结果 {
                "entity": str,
                "entities": List[str],  # 相关实体
                "timeline": List[Dict]  # 事件时间线
            }

        Raises:
            NewsIntelError: 分析失败
        """
        if not entity:
            raise NewsIntelError("实体名称不能为空")

        try:
            return self._correlation.correlate(entity, date_range)
        except Exception as e:
            raise NewsIntelError(f"关联分析失败: {str(e)}") from e

    def sec_filings(
        self,
        ticker: str,
        form_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        SEC 公告追踪。

        Args:
            ticker: 股票代码
            form_type: 公告类型 (8-K/10-K/10-Q/4)
            limit: 返回数量上限

        Returns:
            SEC 公告列表 [{
                "form_type": str,       # 公告类型
                "filing_date": str,     # 提交日期
                "description": str,      # 描述
                "url": str              # EDGAR 链接
            }]

        Raises:
            NewsIntelError: 查询失败
        """
        if not ticker:
            raise NewsIntelError("股票代码不能为空")

        try:
            return self._sec.get_filings(ticker.upper(), form_type, limit)
        except Exception as e:
            raise NewsIntelError(f"SEC 公告查询失败: {str(e)}") from e

    def earnings_call(
        self,
        ticker: str,
        quarter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        财报电话会分析。

        Args:
            ticker: 股票代码
            quarter: 季度 (Q1-2024)

        Returns:
            财报电话会结果 {
                "date": str,
                "ticker": str,
                "quarter": str,
                "mgmt_sentiment": str,  # positive/negative/neutral
                "highlights": List[Dict]  # 关键指标
            }

        Raises:
            NewsIntelError: 查询失败
        """
        if not ticker:
            raise NewsIntelError("股票代码不能为空")

        # 模拟财报电话会数据
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "ticker": ticker.upper(),
            "quarter": quarter or "Q1-2024",
            "mgmt_sentiment": "positive",
            "highlights": [
                {"name": "Revenue", "value": "Mock Revenue"},
                {"name": "EPS", "value": "Mock EPS"}
            ]
        }


# 便捷函数
def create_client(**kwargs) -> NewsIntelligence:
    """创建新闻智能分析客户端"""
    return NewsIntelligence(**kwargs)
