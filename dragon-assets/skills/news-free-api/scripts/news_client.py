#!/usr/bin/env python3
"""
News Free API Client - NewsAPI + CurrentsAPI 双冗余客户端
来源: 天龙引擎 V11.13 免费API替代方案
文档: skills/news-free-api/SKILL.md
"""

import os
import json
import time
from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("请安装 requests: pip install requests")
    exit(1)


@dataclass
class NewsArticle:
    """新闻文章数据结构"""
    title: str
    description: Optional[str]
    url: str
    source: str
    published_at: str
    author: Optional[str] = None
    image_url: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "source": self.source,
            "published_at": self.published_at,
            "author": self.author,
            "image_url": self.image_url,
            "content": self.content,
            "category": self.category
        }


class NewsAPIError(Exception):
    """新闻API异常"""
    pass


class NewsClient:
    """
    双冗余新闻客户端 - NewsAPI + CurrentsAPI

    使用方式:
        client = NewsClient()  # 自动使用环境变量
        client = NewsClient(newsapi_key="xxx", currents_key="xxx")  # 显式指定

    环境变量:
        NEWS_API_KEY: NewsAPI.com API密钥 (https://newsapi.org)
        CURRENTS_API_KEY: Currents API密钥 (https://currentsapi.services)

    免费额度:
        NewsAPI: 100请求/天, 仅支持英文
        CurrentsAPI: 300请求/天, 支持多语言
    """

    BASE_URL_NEWSAPI = "https://newsapi.org/v2"
    BASE_URL_CURRENTS = "https://api.currentsapi.services/v1"

    def __init__(
        self,
        newsapi_key: Optional[str] = None,
        currents_key: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: int = 300
    ):
        self.newsapi_key = newsapi_key or os.getenv("NEWS_API_KEY")
        self.currents_key = currents_key or os.getenv("CURRENTS_API_KEY")
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self._cache = {}

        if not self.newsapi_key and not self.currents_key:
            raise NewsAPIError(
                "需要设置NEWS_API_KEY或CURRENTS_API_KEY环境变量\n"
                "获取地址:\n"
                "  NewsAPI: https://newsapi.org/register\n"
                "  CurrentsAPI: https://currentsapi.services/en/signup"
            )

    def _check_cache(self, key: str) -> Optional[list]:
        """检查缓存"""
        if not self.use_cache:
            return None
        if key in self._cache:
            cached, timestamp = self._cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return cached
        return None

    def _set_cache(self, key: str, data: list):
        """设置缓存"""
        if self.use_cache:
            self._cache[key] = (data, time.time())

    def _parse_newsapi_article(self, article: dict) -> NewsArticle:
        """解析NewsAPI文章格式"""
        return NewsArticle(
            title=article.get("title", ""),
            description=article.get("description"),
            url=article.get("url", ""),
            source=article.get("source", {}).get("name", ""),
            published_at=article.get("publishedAt", ""),
            author=article.get("author"),
            image_url=article.get("urlToImage"),
            content=article.get("content"),
            category=None
        )

    def _parse_currents_article(self, article: dict) -> NewsArticle:
        """解析CurrentsAPI文章格式"""
        return NewsArticle(
            title=article.get("title", ""),
            description=article.get("description"),
            url=article.get("url", ""),
            source=article.get("author", ""),
            published_at=article.get("published", ""),
            author=article.get("author"),
            image_url=article.get("image", ""),
            content=article.get("content", ""),
            category=article.get("category", [None])[0] if article.get("category") else None
        )

    def top_headlines(
        self,
        country: str = "us",
        category: Optional[str] = None,
        page_size: int = 20
    ) -> list[NewsArticle]:
        """
        获取头条新闻 (NewsAPI)

        参数:
            country: 国家代码 (us, gb, cn, jp, de, fr, etc.)
            category: 类别 (business, entertainment, general, health, science, sports, technology)
            page_size: 返回数量 (最大100)

        返回:
            NewsArticle列表
        """
        cache_key = f"headlines_{country}_{category}_{page_size}"
        cached = self._check_cache(cache_key)
        if cached:
            return [NewsArticle(**a) if isinstance(a, dict) else a for a in cached]

        if not self.newsapi_key:
            raise NewsAPIError("需要NEWS_API_KEY来获取头条新闻")

        params = {
            "country": country,
            "pageSize": min(page_size, 100),
            "apiKey": self.newsapi_key
        }
        if category:
            params["category"] = category

        try:
            resp = requests.get(
                f"{self.BASE_URL_NEWSAPI}/top-headlines",
                params=params,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") != "ok":
                raise NewsAPIError(f"NewsAPI错误: {data.get('message', '未知错误')}")

            articles = [self._parse_newsapi_article(a) for a in data.get("articles", [])]
            self._set_cache(cache_key, [a.to_dict() for a in articles])
            return articles

        except requests.RequestException as e:
            raise NewsAPIError(f"NewsAPI请求失败: {e}")

    def search(
        self,
        query: str,
        language: str = "en",
        sort_by: str = "publishedAt",
        page_size: int = 20
    ) -> list[NewsArticle]:
        """
        搜索新闻 (NewsAPI)

        参数:
            query: 搜索关键词
            language: 语言 (en, ar, de, es, fr, he, it, nl, no, pt, ru, sv, ud, zh)
            sort_by: 排序 (relevancy, popularity, publishedAt)
            page_size: 返回数量

        返回:
            NewsArticle列表
        """
        cache_key = f"search_{query}_{language}_{sort_by}_{page_size}"
        cached = self._check_cache(cache_key)
        if cached:
            return [NewsArticle(**a) if isinstance(a, dict) else a for a in cached]

        if not self.newsapi_key:
            raise NewsAPIError("需要NEWS_API_KEY来搜索新闻")

        params = {
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "pageSize": min(page_size, 100),
            "apiKey": self.newsapi_key
        }

        try:
            resp = requests.get(
                f"{self.BASE_URL_NEWSAPI}/everything",
                params=params,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") != "ok":
                raise NewsAPIError(f"NewsAPI错误: {data.get('message', '未知错误')}")

            articles = [self._parse_newsapi_article(a) for a in data.get("articles", [])]
            self._set_cache(cache_key, [a.to_dict() for a in articles])
            return articles

        except requests.RequestException as e:
            raise NewsAPIError(f"NewsAPI搜索失败: {e}")

    def get_sources(self, category: Optional[str] = None, language: str = "en") -> list[dict]:
        """
        获取新闻源列表 (NewsAPI)

        参数:
            category: 类别筛选
            language: 语言筛选

        返回:
            新闻源列表
        """
        if not self.newsapi_key:
            raise NewsAPIError("需要NEWS_API_KEY来获取新闻源")

        params = {
            "apiKey": self.newsapi_key,
            "language": language
        }
        if category:
            params["category"] = category

        try:
            resp = requests.get(
                f"{self.BASE_URL_NEWSAPI}/sources",
                params=params,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            if data.get("status") != "ok":
                raise NewsAPIError(f"NewsAPI错误: {data.get('message', '未知错误')}")

            return data.get("sources", [])

        except requests.RequestException as e:
            raise NewsAPIError(f"NewsAPI请求失败: {e}")

    def multi_lang_search(
        self,
        query: str,
        languages: list[str] = None
    ) -> list[NewsArticle]:
        """
        多语言搜索 (CurrentsAPI) - NewsAPI的免费版本不支持中文

        参数:
            query: 搜索关键词
            languages: 语言列表 (en, zh, es, fr, de, etc.)

        返回:
            NewsArticle列表
        """
        if languages is None:
            languages = ["en", "zh"]

        cache_key = f"multilang_{query}_{'-'.join(languages)}"
        cached = self._check_cache(cache_key)
        if cached:
            return [NewsArticle(**a) if isinstance(a, dict) else a for a in cached]

        if not self.currents_key:
            raise NewsAPIError("需要CURRENTS_API_KEY来使用多语言搜索")

        results = []
        for lang in languages:
            params = {
                "keywords": query,
                "language": lang,
                "apiKey": self.currents_key
            }

            try:
                resp = requests.get(
                    f"{self.BASE_URL_CURRENTS}/search",
                    params=params,
                    timeout=10
                )
                resp.raise_for_status()
                data = resp.json()

                for article in data.get("news", []):
                    results.append(self._parse_currents_article(article))

            except requests.RequestException as e:
                print(f" CurrentsAPI {lang}请求失败: {e}")
                continue

        # 去重
        seen = set()
        unique_results = []
        for article in results:
            if article.url not in seen:
                seen.add(article.url)
                unique_results.append(article)

        self._set_cache(cache_key, [a.to_dict() for a in unique_results])
        return unique_results

    def latest_news(
        self,
        category: Optional[str] = None,
        count: int = 20
    ) -> list[NewsArticle]:
        """
        获取最新新闻 (CurrentsAPI) - 多语言支持

        参数:
            category: 类别 (science, technology, sports, etc.)
            count: 返回数量

        返回:
            NewsArticle列表
        """
        cache_key = f"latest_{category}_{count}"
        cached = self._check_cache(cache_key)
        if cached:
            return [NewsArticle(**a) if isinstance(a, dict) else a for a in cached]

        if not self.currents_key:
            # 回退到NewsAPI
            return self.top_headlines(page_size=count)

        params = {
            "apiKey": self.currents_key,
            "page_size": count
        }
        if category:
            params["category"] = category

        try:
            resp = requests.get(
                f"{self.BASE_URL_CURRENTS}/latest-news",
                params=params,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()

            articles = [self._parse_currents_article(a) for a in data.get("news", [])]
            self._set_cache(cache_key, [a.to_dict() for a in articles])
            return articles

        except requests.RequestException as e:
            raise NewsAPIError(f"CurrentsAPI请求失败: {e}")

    def to_json(self, articles: list[NewsArticle]) -> str:
        """转换为JSON格式"""
        return json.dumps([a.to_dict() for a in articles], ensure_ascii=False, indent=2)


def main():
    """CLI入口"""
    import argparse

    parser = argparse.ArgumentParser(description="新闻API客户端 - NewsAPI + CurrentsAPI")
    parser.add_argument("--query", "-q", help="搜索关键词")
    parser.add_argument("--headlines", action="store_true", help="获取头条新闻")
    parser.add_argument("--country", default="us", help="国家代码 (默认: us)")
    parser.add_argument("--category", "-c", help="新闻类别")
    parser.add_argument("--latest", action="store_true", help="获取最新新闻")
    parser.add_argument("--sources", action="store_true", help="获取新闻源列表")
    parser.add_argument("--lang", default="en", help="语言 (默认: en)")
    parser.add_argument("--count", type=int, default=10, help="返回数量 (默认: 10)")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text", help="输出格式")
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存")

    args = parser.parse_args()

    try:
        client = NewsClient(use_cache=not args.no_cache)

        articles = []

        if args.headlines:
            articles = client.top_headlines(
                country=args.country,
                category=args.category,
                page_size=args.count
            )
            print(f"📰 头条新闻 ({args.country.upper()})")

        elif args.query:
            if args.lang != "en":
                articles = client.multi_lang_search(args.query, languages=[args.lang, "en"])
            else:
                articles = client.search(args.query, language=args.lang, page_size=args.count)
            print(f"🔍 搜索结果: {args.query}")

        elif args.latest:
            articles = client.latest_news(category=args.category, count=args.count)
            print("📰 最新新闻")

        elif args.sources:
            sources = client.get_sources(category=args.category, language=args.lang)
            if args.format == "json":
                print(json.dumps(sources, ensure_ascii=False, indent=2))
            else:
                for src in sources:
                    print(f"  [{src.get('category', 'N/A')}] {src.get('name', 'N/A')}")
                    print(f"    ID: {src.get('id', 'N/A')}")
                    print(f"    描述: {src.get('description', 'N/A')[:80]}...")
                    print()
            return

        else:
            parser.print_help()
            return

        if args.format == "json":
            print(client.to_json(articles))
        else:
            for i, article in enumerate(articles, 1):
                print(f"\n{i}. {article.title}")
                print(f"   来源: {article.source} | 时间: {article.published_at[:10] if article.published_at else 'N/A'}")
                if article.description:
                    print(f"   {article.description[:120]}...")
                print(f"   链接: {article.url}")

    except NewsAPIError as e:
        print(f"❌ 错误: {e}")
        exit(1)


if __name__ == "__main__":
    main()
