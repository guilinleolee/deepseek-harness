#!/usr/bin/env python3
"""
TrendRadar MCP Client - AI舆情过滤核心客户端
来源: sansan0/TrendRadar (56k Stars)
"""

import json
import httpx
from typing import Optional
from dataclasses import dataclass


@dataclass
class NewsItem:
    """新闻条目"""
    title: str
    content: str
    url: str
    source: str = ""
    published_at: str = ""


@dataclass
class FilterResult:
    """过滤结果"""
    primary_tag: str
    score: float
    all_tags: list
    confidence: float


@dataclass
class Alert:
    """告警"""
    id: str
    tag: str
    title: str
    url: str
    score: float
    created_at: str


class TrendRadarClient:
    """TrendRadar MCP客户端封装"""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = 30.0

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def get_ai_interests(self) -> list[dict]:
        """获取AI兴趣定义"""
        response = httpx.post(
            f"{self.base_url}/tools/call",
            headers=self._headers(),
            json={"tool": "get_ai_interests", "arguments": {}},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json().get("result", [])

    def search_news(self, query: str, limit: int = 20) -> list[dict]:
        """搜索新闻"""
        response = httpx.post(
            f"{self.base_url}/tools/call",
            headers=self._headers(),
            json={
                "tool": "search_news",
                "arguments": {"query": query, "limit": limit}
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json().get("result", [])

    def get_trending_news(self, limit: int = 20) -> list[dict]:
        """获取趋势新闻"""
        response = httpx.post(
            f"{self.base_url}/tools/call",
            headers=self._headers(),
            json={
                "tool": "get_trending_news",
                "arguments": {"limit": limit}
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json().get("result", [])

    def ai_filter_news(self, title: str, content: str, url: str = "") -> FilterResult:
        """AI过滤单条新闻"""
        response = httpx.post(
            f"{self.base_url}/tools/call",
            headers=self._headers(),
            json={
                "tool": "ai_filter_news",
                "arguments": {
                    "title": title,
                    "content": content,
                    "url": url
                }
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        result = response.json().get("result", {})
        return FilterResult(
            primary_tag=result.get("primary_tag", ""),
            score=result.get("score", 0.0),
            all_tags=result.get("all_tags", []),
            confidence=result.get("confidence", 0.0)
        )

    def batch_ai_filter_news(self, news_list: list[dict]) -> list[FilterResult]:
        """批量AI过滤新闻"""
        response = httpx.post(
            f"{self.base_url}/tools/call",
            headers=self._headers(),
            json={
                "tool": "batch_ai_filter_news",
                "arguments": {"news_list": news_list}
            },
            timeout=self.timeout * 2  # 批量操作增加超时
        )
        response.raise_for_status()
        results = response.json().get("result", [])
        return [
            FilterResult(
                primary_tag=r.get("primary_tag", ""),
                score=r.get("score", 0.0),
                all_tags=r.get("all_tags", []),
                confidence=r.get("confidence", 0.0)
            )
            for r in results
        ]

    def get_pending_alerts(self, limit: int = 50) -> list[Alert]:
        """获取待处理告警"""
        response = httpx.post(
            f"{self.base_url}/tools/call",
            headers=self._headers(),
            json={
                "tool": "get_pending_alerts",
                "arguments": {"limit": limit}
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        alerts = response.json().get("result", [])
        return [
            Alert(
                id=a.get("id", ""),
                tag=a.get("tag", ""),
                title=a.get("title", ""),
                url=a.get("url", ""),
                score=a.get("score", 0.0),
                created_at=a.get("created_at", "")
            )
            for a in alerts
        ]

    def dismiss_alert(self, alert_id: str) -> bool:
        """忽略告警"""
        response = httpx.post(
            f"{self.base_url}/tools/call",
            headers=self._headers(),
            json={
                "tool": "dismiss_alert",
                "arguments": {"alert_id": alert_id}
            },
            timeout=self.timeout
        )
        return response.status_code == 200

    def get_system_stats(self) -> dict:
        """获取系统状态"""
        response = httpx.post(
            f"{self.base_url}/tools/call",
            headers=self._headers(),
            json={
                "tool": "get_system_stats",
                "arguments": {}
            },
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json().get("result", {})


# ============ 天龙引擎集成函数 ============

def filter_news(title: str, content: str, url: str = "") -> str:
    """快速过滤单条新闻"""
    client = TrendRadarClient()
    result = client.ai_filter_news(title, content, url)
    return f"[{result.primary_tag}] 评分: {result.score:.2f}"


def batch_filter(news_items: list[dict]) -> list[dict]:
    """批量过滤新闻，返回高价值结果"""
    client = TrendRadarClient()
    results = client.batch_ai_filter_news(news_items)
    # 只返回评分>0.7的高价值新闻
    high_value = [
        {"item": item, "result": r}
        for item, r in zip(news_items, results)
        if r.score > 0.7
    ]
    return high_value


def get_top_alerts(limit: int = 10) -> str:
    """获取最新告警摘要"""
    client = TrendRadarClient()
    alerts = client.get_pending_alerts(limit)
    if not alerts:
        return "暂无告警"
    lines = [f"📢 [{a.tag}] {a.title} (评分:{a.score:.2f})" for a in alerts]
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    client = TrendRadarClient()
    try:
        stats = client.get_system_stats()
        print(f"✅ TrendRadar连接成功: {stats}")
    except Exception as e:
        print(f"⚠️ TrendRadar未连接或服务不可用: {e}")
        print("提示: 启动TrendRadar服务或配置正确的base_url")