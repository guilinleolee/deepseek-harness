#!/usr/bin/env python3
"""
RSS Feed Manager - 订阅源管理+优先级调度
配合TrendRadar实现精准舆情监控
"""

import feedparser
import requests
import hashlib
import time
import os
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path


@dataclass
class FeedItem:
    """订阅条目"""
    title: str
    url: str
    published: str
    summary: str
    source: str
    category: str
    fetched_at: str = ""


@dataclass
class FeedSource:
    """订阅源"""
    url: str
    category: str
    priority: str  # P0/P1/P2
    refresh_interval: int  # 分钟
    status: str  # active/paused
    last_fetch: str = ""
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    error_count: int = 0
    last_error: str = ""


class RSSFeedManager:
    """RSS订阅源管理器"""

    def __init__(self, config_path: str = "config/feeds.txt"):
        self.config_path = config_path
        self.feeds: dict[str, FeedSource] = {}
        self.seen_hashes: set[str] = set()
        self.cache_dir = Path("cache/rss")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._load_feeds()
        self._load_seen_hashes()

    def _load_feeds(self):
        """加载订阅配置"""
        if not os.path.exists(self.config_path):
            return

        with open(self.config_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split("|")
                if len(parts) >= 5:
                    url, category, priority, refresh, status = parts[:5]
                    self.feeds[url] = FeedSource(
                        url=url,
                        category=category,
                        priority=priority,
                        refresh_interval=int(refresh),
                        status=status
                    )

    def _save_feeds(self):
        """保存订阅配置"""
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write("# RSS订阅配置: url|category|priority|refresh_interval|status\n")
            f.write("# 优先级: P0(核心30min)/P1(重要60min)/P2(一般180min)\n\n")

            for feed in self.feeds.values():
                line = f"{feed.url}|{feed.category}|{feed.priority}|{feed.refresh_interval}|{feed.status}\n"
                f.write(line)

    def _load_seen_hashes(self):
        """加载已见哈希"""
        hash_file = self.cache_dir / "seen_hashes.json"
        if hash_file.exists():
            with open(hash_file, "r", encoding="utf-8") as f:
                self.seen_hashes = set(json.load(f))

    def _save_seen_hashes(self):
        """保存已见哈希"""
        hash_file = self.cache_dir / "seen_hashes.json"
        # 只保留最近10000条
        hashes = list(self.seen_hashes)[-10000:]
        with open(hash_file, "w", encoding="utf-8") as f:
            json.dump(hashes, f)

    def _compute_hash(self, item: FeedItem) -> str:
        """计算内容哈希用于去重"""
        content = f"{item.url}|{item.title}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def add_feed(self, url: str, category: str, priority: str = "P1",
                 refresh_interval: int = 60, status: str = "active") -> bool:
        """添加订阅源"""
        if url in self.feeds:
            return False

        self.feeds[url] = FeedSource(
            url=url,
            category=category,
            priority=priority,
            refresh_interval=refresh_interval,
            status=status
        )
        self._save_feeds()
        return True

    def remove_feed(self, url: str) -> bool:
        """删除订阅源"""
        if url not in self.feeds:
            return False
        del self.feeds[url]
        self._save_feeds()
        return True

    def pause_feed(self, url: str) -> bool:
        """暂停订阅源"""
        if url in self.feeds:
            self.feeds[url].status = "paused"
            self._save_feeds()
            return True
        return False

    def resume_feed(self, url: str) -> bool:
        """恢复订阅源"""
        if url in self.feeds:
            self.feeds[url].status = "active"
            self._save_feeds()
            return True
        return False

    def get_pending_feeds(self) -> list[FeedSource]:
        """获取待更新订阅源（按优先级排序）"""
        pending = []
        now = datetime.now()

        for feed in self.feeds.values():
            if feed.status != "active":
                continue

            if feed.last_fetch:
                last = datetime.fromisoformat(feed.last_fetch)
                elapsed = (now - last).total_seconds() / 60
                if elapsed < feed.refresh_interval:
                    continue
            else:
                # 首次抓取总是待更新
                pass

            pending.append(feed)

        # 按优先级排序: P0 > P1 > P2
        priority_order = {"P0": 0, "P1": 1, "P2": 2}
        pending.sort(key=lambda f: priority_order.get(f.priority, 3))
        return pending

    def fetch_feed(self, url: str, timeout: int = 30) -> list[FeedItem]:
        """抓取单个订阅源"""
        if url not in self.feeds:
            return []

        feed_meta = self.feeds[url]
        headers = {"User-Agent": "RSSFeedManager/1.0"}

        # 增量更新
        if feed_meta.etag:
            headers["If-None-Match"] = feed_meta.etag
        if feed_meta.last_modified:
            headers["If-Modified-Since"] = feed_meta.last_modified

        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 304:
                # 未修改
                return []

            resp.raise_for_status()
            feed_meta.etag = resp.headers.get("ETag")
            feed_meta.last_modified = resp.headers.get("Last-Modified")

            parsed = feedparser.parse(resp.content)
            items = []

            for entry in parsed.entries[:50]:  # 最多50条
                item = FeedItem(
                    title=entry.get("title", ""),
                    url=entry.get("link", ""),
                    published=str(entry.get("published", "")),
                    summary=entry.get("summary", entry.get("description", "")),
                    source=url,
                    category=feed_meta.category,
                    fetched_at=datetime.now().isoformat()
                )

                # 去重检查
                item_hash = self._compute_hash(item)
                if item_hash in self.seen_hashes:
                    continue
                self.seen_hashes.add(item_hash)

                items.append(item)

            feed_meta.last_fetch = datetime.now().isoformat()
            feed_meta.error_count = 0
            self._save_seen_hashes()
            return items

        except Exception as e:
            feed_meta.error_count += 1
            feed_meta.last_error = str(e)[:200]
            return []

    def fetch_all_pending(self) -> list[FeedItem]:
        """抓取所有待更新订阅源"""
        all_items = []
        for feed in self.get_pending_feeds():
            items = self.fetch_feed(feed.url)
            all_items.extend(items)
            # 礼貌性延迟
            time.sleep(1)
        return all_items

    def get_stats(self) -> dict:
        """获取统计信息"""
        active = [f for f in self.feeds.values() if f.status == "active"]
        paused = [f for f in self.feeds.values() if f.status == "paused"]

        # 计算今日抓取数
        today = datetime.now().date()
        today_hashes = [
            h for h in self.seen_hashes
            if int(h, 16) % 1000 == today.day  # 粗略估计
        ]

        return {
            "total_count": len(self.feeds),
            "active_count": len(active),
            "paused_count": len(paused),
            "today_fetches": len(self.seen_hashes) % 1000,
            "by_priority": {
                "P0": len([f for f in active if f.priority == "P0"]),
                "P1": len([f for f in active if f.priority == "P1"]),
                "P2": len([f for f in active if f.priority == "P2"]),
            }
        }

    def list_feeds(self) -> list[dict]:
        """列出所有订阅源"""
        return [
            {
                "url": f.url,
                "category": f.category,
                "priority": f.priority,
                "refresh_interval": f.refresh_interval,
                "status": f.status,
                "last_fetch": f.last_fetch,
                "error_count": f.error_count
            }
            for f in self.feeds.values()
        ]


# ============ 天龙引擎集成函数 ============

def get_news_from_feeds() -> list[dict]:
    """从所有订阅源获取新闻"""
    manager = RSSFeedManager()
    items = manager.fetch_all_pending()
    return [
        {
            "title": item.title,
            "content": item.summary[:500],
            "url": item.url,
            "source": item.source,
            "category": item.category,
            "published": item.published
        }
        for item in items
    ]


def add_rss_source(url: str, category: str, priority: str = "P1") -> str:
    """快速添加RSS源"""
    manager = RSSFeedManager()
    intervals = {"P0": 30, "P1": 60, "P2": 180}
    if manager.add_feed(url, category, priority, intervals.get(priority, 60)):
        return f"已添加: {url} ({priority})"
    return f"源已存在: {url}"


def show_feed_status() -> str:
    """显示订阅源状态"""
    manager = RSSFeedManager()
    stats = manager.get_stats()
    feeds = manager.list_feeds()

    lines = [f"📊 RSS订阅统计: 活跃{stats['active_count']}个/暂停{stats['paused_count']}个"]
    lines.append(f"   P0核心:{stats['by_priority']['P0']} P1重要:{stats['by_priority']['P1']} P2一般:{stats['by_priority']['P2']}")
    lines.append("\n📋 订阅源列表:")

    for f in feeds[:20]:
        status_icon = "✅" if f["status"] == "active" else "⏸️"
        lines.append(f"  {status_icon} [{f['priority']}] {f['category']} - {f['url'][:50]}")

    return "\n".join(lines)


if __name__ == "__main__":
    # 测试
    manager = RSSFeedManager()
    print(f"加载 {len(manager.feeds)} 个订阅源")
    print(f"待更新: {len(manager.get_pending_feeds())} 个")
    print(show_feed_status())
