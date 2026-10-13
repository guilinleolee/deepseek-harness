#!/usr/bin/env python3
"""
MCP Remote Servers - 第三方MCP服务客户端
支持 DataForSEO, Firecrawl, Exa, Tavily, Brave 等服务
"""

import json
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
import urllib.request
import urllib.error


@dataclass
class RemoteMCPResponse:
    """远程MCP响应"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    cached: bool = False
    duration_ms: float = 0


class DataForSEOMCP:
    """DataForSEO MCP服务 - 专业SEO数据API"""

    BASE_URL = "https://api.dataforseo.com/v3"

    def __init__(self, login: str = None, password: str = None):
        self.login = login or os.getenv("DATAFORSEO_LOGIN", "")
        self.password = password or os.getenv("DATAFORSEO_PASSWORD", "")
        self.auth_string = None
        if self.login and self.password:
            import base64
            self.auth_string = base64.b64encode(
                f"{self.login}:{self.password}".encode()
            ).decode()

    def _make_request(self, endpoint: str, data: Dict = None) -> Dict:
        """发送请求"""
        if not self.auth_string:
            return {"error": "DataForSEO credentials not configured"}

        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Basic {self.auth_string}",
            "Content-Type": "application/json"
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode() if data else None,
                headers=headers,
                method="POST" if data else "GET"
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {"error": str(e)}

    async def serp_search(self, keyword: str, location: str = "US", language: str = "en") -> RemoteMCPResponse:
        """SERP搜索"""
        data = {
            "keyword": keyword,
            "location_name": location,
            "language_code": language,
            "depth": 10
        }
        result = self._make_request("serp/google/organic/live/advanced", data)

        if "error" in result:
            return RemoteMCPResponse(success=False, error=result["error"])

        tasks = result.get("tasks", [])
        if tasks and tasks[0].get("result"):
            results = tasks[0]["result"][0].get("items", [])
            return RemoteMCPResponse(
                success=True,
                data={
                    "keyword": keyword,
                    "total_results": len(results),
                    "organic_results": [
                        {
                            "position": r.get("rank_position"),
                            "title": r.get("title"),
                            "url": r.get("url"),
                            "description": r.get("description"),
                            "domain": r.get("domain")
                        }
                        for r in results[:10]
                    ],
                    "ai_overview": None,
                    "featured_snippet": None
                }
            )

        return RemoteMCPResponse(success=False, error="No results")

    async def keyword_data(self, keywords: List[str], location: str = "US") -> RemoteMCPResponse:
        """关键词数据"""
        data = {
            "keywords": keywords,
            "location_name": location,
            "filters": ["Keyword stats"]
        }
        result = self._make_request("keywords_data/google/search_volume/live", data)

        if "error" in result:
            return RemoteMCPResponse(success=False, error=result["error"])

        return RemoteMCPResponse(success=True, data=result)

    async def domain_analytics(self, domain: str) -> RemoteMCPResponse:
        """域名分析"""
        data = {"target": domain}
        result = self._make_request("domain_analytics/summary/live", data)

        if "error" in result:
            return RemoteMCPResponse(success=False, error=result["error"])

        return RemoteMCPResponse(success=True, data=result)


class FirecrawlMCP:
    """Firecrawl MCP服务 - 网页抓取和内容提取"""

    BASE_URL = "https://api.firecrawl.dev"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY", "")

    def _make_request(self, endpoint: str, data: Dict = None) -> Dict:
        """发送请求"""
        if not self.api_key:
            return {"error": "Firecrawl API key not configured"}

        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode() if data else None,
                headers=headers,
                method="POST" if data else "GET"
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {"error": str(e)}

    async def scrape(self, url: str, formats: List[str] = None) -> RemoteMCPResponse:
        """抓取单个页面"""
        if formats is None:
            formats = ["markdown", "html"]

        data = {
            "url": url,
            "formats": formats,
            "onlyMainContent": True
        }

        result = self._make_request("v0/scrape", data)

        if "error" in result:
            return RemoteMCPResponse(success=False, error=result["error"])

        return RemoteMCPResponse(
            success=True,
            data={
                "url": url,
                "markdown": result.get("data", {}).get("markdown", ""),
                "html": result.get("data", {}).get("html", ""),
                "metadata": result.get("data", {}).get("metadata", {}),
                "links": result.get("data", {}).get("links", [])
            }
        )

    async def crawl(self, url: str, limit: int = 10) -> RemoteMCPResponse:
        """批量抓取"""
        data = {
            "url": url,
            "limit": limit,
            "scrapeOptions": {"formats": ["markdown"]}
        }

        result = self._make_request("v0/crawl", data)

        if "error" in result:
            return RemoteMCPResponse(success=False, error=result["error"])

        job_id = result.get("id")
        if job_id:
            return RemoteMCPResponse(
                success=True,
                data={
                    "job_id": job_id,
                    "status": result.get("status", "processing"),
                    "message": "Use job_id to poll for results"
                }
            )

        return RemoteMCPResponse(success=False, error="No job ID returned")

    async def batch_scrape(self, urls: List[str]) -> RemoteMCPResponse:
        """批量抓取多个页面"""
        data = {
            "urls": urls,
            "formats": ["markdown"],
            "onlyMainContent": True
        }

        result = self._make_request("v0/batch/scrape", data)

        if "error" in result:
            return RemoteMCPResponse(success=False, error=result["error"])

        return RemoteMCPResponse(
            success=True,
            data={
                "status": result.get("status", "processing"),
                "job_id": result.get("id")
            }
        )


class ExaMCP:
    """Exa MCP服务 - AI语义搜索"""

    BASE_URL = "https://api.exa.ai"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("EXA_API_KEY", "")

    def _make_request(self, endpoint: str, data: Dict = None) -> Dict:
        """发送请求"""
        if not self.api_key:
            return {"error": "Exa API key not configured"}

        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode() if data else None,
                headers=headers,
                method="POST" if data else "GET"
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {"error": str(e)}

    async def search(self, query: str, num_results: int = 10) -> RemoteMCPResponse:
        """语义搜索"""
        data = {
            "query": query,
            "numResults": num_results,
            "type": "article"
        }

        result = self._make_request("search", data)

        if "error" in result:
            return RemoteMCPResponse(success=False, error=result["error"])

        results = result.get("results", [])
        return RemoteMCPResponse(
            success=True,
            data={
                "query": query,
                "total_results": len(results),
                "results": [
                    {
                        "title": r.get("title"),
                        "url": r.get("url"),
                        "snippet": r.get("snippet"),
                        "score": r.get("score")
                    }
                    for r in results
                ]
            }
        )

    async def find_similar(self, url: str, num_results: int = 10) -> RemoteMCPResponse:
        """查找相似内容"""
        data = {"url": url, "numResults": num_results}

        result = self._make_request("findSimilar", data)

        if "error" in result:
            return RemoteMCPResponse(success=False, error=result["error"])

        results = result.get("results", [])
        return RemoteMCPResponse(
            success=True,
            data={
                "source_url": url,
                "total_results": len(results),
                "similar": [
                    {
                        "title": r.get("title"),
                        "url": r.get("url"),
                        "snippet": r.get("snippet"),
                        "score": r.get("score")
                    }
                    for r in results
                ]
            }
        )

    async def content(self, url: str) -> RemoteMCPResponse:
        """获取页面内容"""
        data = {"urls": [url]}

        result = self._make_request("contents", data)

        if "error" in result:
            return RemoteMCPResponse(success=False, error=result["error"])

        contents = result.get("contents", [])
        if contents:
            return RemoteMCPResponse(
                success=True,
                data={
                    "url": url,
                    "content": contents[0].get("text", ""),
                    "metadata": contents[0].get("metadata", {})
                }
            )

        return RemoteMCPResponse(success=False, error="No content returned")


class TavilyMCP:
    """Tavily MCP服务 - AI搜索API"""

    BASE_URL = "https://api.tavily.com"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY", "")

    def _make_request(self, endpoint: str, data: Dict = None) -> Dict:
        """发送请求"""
        if not self.api_key:
            return {"error": "Tavily API key not configured"}

        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode() if data else None,
                headers=headers,
                method="POST" if data else "GET"
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {"error": str(e)}

    async def search(self, query: str, depth: str = "basic") -> RemoteMCPResponse:
        """搜索"""
        data = {
            "query": query,
            "search_depth": depth,
            "max_results": 10
        }

        result = self._make_request("search", data)

        if "error" in result:
            return RemoteMCPResponse(success=False, error=result["error"])

        return RemoteMCPResponse(
            success=True,
            data={
                "query": query,
                "answer": result.get("answer"),
                "results": result.get("results", []),
                "images": result.get("images", [])
            }
        )

    async def deep_search(self, query: str) -> RemoteMCPResponse:
        """深度搜索"""
        return await self.search(query, depth="advanced")

    async def extract(self, urls: List[str]) -> RemoteMCPResponse:
        """提取页面内容"""
        data = {"urls": urls}

        result = self._make_request("extract", data)

        if "error" in result:
            return RemoteMCPResponse(success=False, error=result["error"])

        return RemoteMCPResponse(
            success=True,
            data={"results": result.get("results", [])}
        )


class BraveMCP:
    """Brave Search MCP服务 - 隐私搜索API"""

    BASE_URL = "https://api.search.brave.com/res/v1"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("BRAVE_API_KEY", "")

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """发送请求"""
        if not self.api_key:
            return {"error": "Brave API key not configured"}

        url = f"{self.BASE_URL}/{endpoint}"
        if params:
            url += "?" + urlencode(params)

        headers = {
            "X-Subscription-Token": self.api_key,
            "Accept": "application/json"
        }

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            return {"error": str(e)}

    async def web_search(self, query: str, count: int = 10) -> RemoteMCPResponse:
        """网页搜索"""
        params = {
            "q": query,
            "count": min(count, 20),
            "safesearch": "moderate"
        }

        result = self._make_request("web/search", params)

        if "error" in result:
            return RemoteMCPResponse(success=False, error=result["error"])

        results = result.get("web", {}).get("results", [])
        return RemoteMCPResponse(
            success=True,
            data={
                "query": query,
                "total_results": result.get("web", {}).get("total", 0),
                "results": [
                    {
                        "title": r.get("title"),
                        "url": r.get("url"),
                        "description": r.get("description"),
                        "age": r.get("age")
                    }
                    for r in results
                ]
            }
        )

    async def news_search(self, query: str, count: int = 10) -> RemoteMCPResponse:
        """新闻搜索"""
        params = {"q": query, "count": min(count, 20)}

        result = self._make_request("news/search", params)

        if "error" in result:
            return RemoteMCPResponse(success=False, error=result["error"])

        results = result.get("results", [])
        return RemoteMCPResponse(
            success=True,
            data={
                "query": query,
                "total_results": len(results),
                "results": [
                    {
                        "title": r.get("title"),
                        "url": r.get("url"),
                        "description": r.get("description"),
                        "page_age": r.get("page_age")
                    }
                    for r in results
                ]
            }
        )

    async def local_search(self, query: str, latitude: float = None, longitude: float = None) -> RemoteMCPResponse:
        """本地搜索"""
        params = {"q": query}
        if latitude and longitude:
            params["latitude"] = latitude
            params["longitude"] = longitude

        result = self._make_request("local/search", params)

        if "error" in result:
            return RemoteMCPResponse(success=False, error=result["error"])

        results = result.get("results", [])
        return RemoteMCPResponse(
            success=True,
            data={
                "query": query,
                "total_results": len(results),
                "results": [
                    {
                        "name": r.get("name"),
                        "address": r.get("address"),
                        "url": r.get("url"),
                        "rating": r.get("rating")
                    }
                    for r in results
                ]
            }
        )


class RemoteMCPServices:
    """远程MCP服务工厂"""

    def __init__(self):
        self._services = {}
        self._init_services()

    def _init_services(self):
        """初始化所有服务"""
        self._services = {
            "dataforseo": DataForSEOMCP(),
            "firecrawl": FirecrawlMCP(),
            "exa": ExaMCP(),
            "tavily": TavilyMCP(),
            "brave": BraveMCP(),
        }

    def get_service(self, name: str):
        """获取服务实例"""
        return self._services.get(name.lower())

    def list_services(self) -> List[Dict]:
        """列出所有服务"""
        services = []
        for name, service in self._services.items():
            # 检查是否配置（处理不同服务类型）
            if hasattr(service, 'api_key'):
                configured = bool(service.api_key)
            elif hasattr(service, 'auth_string'):
                configured = bool(service.auth_string)
            else:
                configured = False
            services.append({
                "name": name,
                "class": service.__class__.__name__,
                "configured": configured
            })
        return services


async def main():
    """CLI主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Remote MCP Services CLI")
    parser.add_argument("service", choices=["dataforseo", "firecrawl", "exa", "tavily", "brave", "list"], help="Service name")
    parser.add_argument("action", nargs="?", help="Action to perform")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--url", "-u", help="URL")
    parser.add_argument("--urls", nargs="+", help="URLs for batch")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.service == "list":
        factory = RemoteMCPServices()
        services = factory.list_services()
        print(json.dumps(services, indent=2))
        return

    factory = RemoteMCPServices()
    service = factory.get_service(args.service)

    if not service:
        print(f"Service {args.service} not found")
        return 1

    result = None

    if args.service == "dataforseo":
        if args.action == "serp" and args.query:
            result = await service.serp_search(args.query)
        elif args.action == "keywords" and args.query:
            result = await service.keyword_data([args.query])

    elif args.service == "firecrawl":
        if args.action == "scrape" and args.url:
            result = await service.scrape(args.url)
        elif args.action == "crawl" and args.url:
            result = await service.crawl(args.url)
        elif args.action == "batch" and args.urls:
            result = await service.batch_scrape(args.urls)

    elif args.service == "exa":
        if args.action == "search" and args.query:
            result = await service.search(args.query)
        elif args.action == "similar" and args.url:
            result = await service.find_similar(args.url)
        elif args.action == "content" and args.url:
            result = await service.content(args.url)

    elif args.service == "tavily":
        if args.action == "search" and args.query:
            result = await service.search(args.query)
        elif args.action == "deep" and args.query:
            result = await service.deep_search(args.query)
        elif args.action == "extract" and args.urls:
            result = await service.extract(args.urls)

    elif args.service == "brave":
        if args.action == "search" and args.query:
            result = await service.web_search(args.query)
        elif args.action == "news" and args.query:
            result = await service.news_search(args.query)
        elif args.action == "local" and args.query:
            result = await service.local_search(args.query)

    if result:
        if args.json:
            print(json.dumps(result.data or {"error": result.error}, indent=2, ensure_ascii=False))
        elif result.success:
            print(json.dumps(result.data, indent=2, ensure_ascii=False))
        else:
            print(f"Error: {result.error}")
            return 1
    else:
        print(f"Unknown action: {args.action}")
        return 1

    return 0


if __name__ == "__main__":
    import asyncio
    import sys
    sys.exit(asyncio.run(main()))
