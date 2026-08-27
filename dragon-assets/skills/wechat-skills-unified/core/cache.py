"""
三层缓存系统
化学视角：缓存是血液循环，L1=毛细血管（内存），L2=静脉（SQLite），L3=心脏（网络）

设计原则：
- L1内存缓存：最热数据，<1ms访问
- L2持久化缓存：历史数据，5-15ms访问
- L3网络获取：冷数据，500-2000ms访问
"""

import sqlite3
import hashlib
import logging
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from collections import OrderedDict
from contextlib import contextmanager

from models.article import Article
from utils.path_security import validate_cache_path
from utils.security import sanitize_exception


logger = logging.getLogger(__name__)


class LRUCache:
    """LRU内存缓存

    设计思路：
    - 使用OrderedDict实现O(1)访问和驱逐
    - 容量限制防止内存溢出
    - 线程不安全（单线程环境可接受）
    """

    def __init__(self, capacity: int = 100):
        """初始化LRU缓存

        Args:
            capacity: 最大容量
        """
        self.cache: OrderedDict[str, Article] = OrderedDict()
        self.capacity = capacity
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Article]:
        """获取缓存项

        Args:
            key: 缓存键

        Returns:
            Article对象或None
        """
        if key in self.cache:
            # 命中：移到末尾（最近使用）
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def set(self, key: str, value: Article) -> None:
        """设置缓存项

        Args:
            key: 缓存键
            value: Article对象
        """
        if key in self.cache:
            # 更新：移到末尾
            self.cache.move_to_end(key)
        self.cache[key] = value

        # 驱逐最久未使用的项
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def invalidate(self, key: str) -> bool:
        """使缓存失效

        Args:
            key: 缓存键

        Returns:
            是否成功失效
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()

    @property
    def size(self) -> int:
        """当前大小"""
        return len(self.cache)

    @property
    def hit_rate(self) -> float:
        """缓存命中率"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class SQLiteCache:
    """SQLite持久化缓存

    设计思路：
    - 使用WAL模式提高并发性能
    - 索引优化查询速度
    - TTL自动过期机制
    """

    # SQL语句
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS articles (
        url_hash TEXT PRIMARY KEY,
        url TEXT NOT NULL,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        account_name TEXT NOT NULL,
        publish_time TEXT,
        content_html TEXT,
        content_markdown TEXT,
        content_text TEXT,
        images TEXT,
        cover_image TEXT,
        fetch_time TEXT NOT NULL,
        source TEXT NOT NULL,
        word_count INTEGER DEFAULT 0
    )
    """

    # 索引SQL（拆分为多个语句，因为sqlite3.execute不支持一次执行多条语句）
    CREATE_INDEX_SQL_LIST = [
        "CREATE INDEX IF NOT EXISTS idx_fetch_time ON articles(fetch_time);",
        "CREATE INDEX IF NOT EXISTS idx_source ON articles(source);"
    ]

    def __init__(self, db_path: str, ttl_days: int = 30):
        """初始化SQLite缓存

        Args:
            db_path: 数据库文件路径
            ttl_days: 默认TTL（天）
        """
        # 验证路径安全性
        validated_path = validate_cache_path(db_path)
        self.db_path = str(validated_path)
        self.ttl = timedelta(days=ttl_days)
        self._init_db()

    def _init_db(self) -> None:
        """初始化数据库"""
        # 确保目录存在
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # 创建表和索引
        with self._get_conn() as conn:
            conn.execute(self.CREATE_TABLE_SQL)
            # 逐个执行索引创建语句
            for index_sql in self.CREATE_INDEX_SQL_LIST:
                conn.execute(index_sql)
            conn.commit()

    @contextmanager
    def _get_conn(self):
        """获取数据库连接（上下文管理器）

        Yields:
            sqlite3.Connection
        """
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row  # 支持字典访问
        try:
            yield conn
        finally:
            conn.close()

    def get(self, url_hash: str) -> Optional[Article]:
        """获取缓存项

        Args:
            url_hash: URL哈希值

        Returns:
            Article对象或None
        """
        try:
            with self._get_conn() as conn:
                cursor = conn.execute(
                    "SELECT * FROM articles WHERE url_hash = ?",
                    (url_hash,)
                )
                row = cursor.fetchone()

                if not row:
                    return None

                # 检查是否过期
                fetch_time = datetime.fromisoformat(row['fetch_time'])
                if datetime.now() - fetch_time > self.ttl:
                    # 过期，删除并返回None
                    self.delete(url_hash)
                    return None

                # 反序列化
                return self._row_to_article(row)

        except Exception as e:
            logger.error(f"SQLite缓存读取失败: {sanitize_exception(e)}")
            return None

    def set(self, article: Article) -> None:
        """设置缓存项

        Args:
            article: Article对象
        """
        try:
            with self._get_conn() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO articles
                    (url_hash, url, title, author, account_name, publish_time,
                     content_html, content_markdown, content_text, images,
                     cover_image, fetch_time, source, word_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        article.url_hash,
                        article.url,
                        article.title,
                        article.author,
                        article.account_name,
                        article.publish_time.isoformat() if article.publish_time else None,
                        article.content_html,
                        article.content_markdown,
                        article.content_text,
                        ",".join(article.images),
                        article.cover_image,
                        article.fetch_time.isoformat(),
                        article.source,
                        article.word_count
                    )
                )
                conn.commit()
        except Exception as e:
            logger.error(f"SQLite缓存写入失败: {sanitize_exception(e)}")

    def delete(self, url_hash: str) -> bool:
        """删除缓存项

        Args:
            url_hash: URL哈希值

        Returns:
            是否成功删除
        """
        try:
            with self._get_conn() as conn:
                cursor = conn.execute(
                    "DELETE FROM articles WHERE url_hash = ?",
                    (url_hash,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"SQLite缓存删除失败: {sanitize_exception(e)}")
            return False

    def clear(self, before_date: Optional[datetime] = None) -> int:
        """清理缓存

        Args:
            before_date: 清除此日期前的缓存，None表示全部

        Returns:
            清理的条目数
        """
        try:
            with self._get_conn() as conn:
                if before_date:
                    cursor = conn.execute(
                        "DELETE FROM articles WHERE fetch_time < ?",
                        (before_date.isoformat(),)
                    )
                else:
                    cursor = conn.execute("DELETE FROM articles")
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"SQLite缓存清理失败: {sanitize_exception(e)}")
            return 0

    def get_stats(self) -> Dict[str, int]:
        """获取缓存统计信息

        Returns:
            统计信息字典
        """
        try:
            with self._get_conn() as conn:
                # 总条目数
                total = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]

                # 按来源统计
                sources = conn.execute(
                    "SELECT source, COUNT(*) FROM articles GROUP BY source"
                ).fetchall()

                return {
                    'total': total,
                    'sources': dict(sources)
                }
        except Exception as e:
            logger.error(f"获取缓存统计失败: {sanitize_exception(e)}")
            return {'total': 0, 'sources': {}}

    @staticmethod
    def _row_to_article(row: sqlite3.Row) -> Article:
        """将数据库行转换为Article对象

        Args:
            row: sqlite3.Row对象

        Returns:
            Article对象
        """
        images = row['images'].split(',') if row['images'] else []

        return Article(
            url=row['url'],
            url_hash=row['url_hash'],
            title=row['title'],
            author=row['author'],
            account_name=row['account_name'],
            publish_time=datetime.fromisoformat(row['publish_time']) if row['publish_time'] else None,
            content_html=row['content_html'] or "",
            content_markdown=row['content_markdown'] or "",
            content_text=row['content_text'] or "",
            images=images,
            cover_image=row['cover_image'],
            fetch_time=datetime.fromisoformat(row['fetch_time']),
            source=row['source'],
            word_count=row['word_count']
        )


class ArticleCache:
    """三层缓存控制器

    设计思路：
    - L1: 内存缓存（最热数据，<1ms）
    - L2: SQLite缓存（历史数据，5-15ms）
    - L3: 网络获取（冷数据，500-2000ms）

    缓存策略：
    1. 查询L1，命中则返回
    2. L1未命中，查询L2，命中则回填L1
    3. L2未命中，返回None（触发L3网络获取）
    4. L3获取成功后，同时写入L1和L2
    """

    def __init__(
        self,
        db_path: str = "./cache/articles.db",
        l1_size: int = 100,
        ttl_days: int = 30
    ):
        """初始化三层缓存

        Args:
            db_path: SQLite数据库路径
            l1_size: L1缓存容量
            ttl_days: 缓存TTL（天）
        """
        self.l1 = LRUCache(capacity=l1_size)
        self.l2 = SQLiteCache(db_path=db_path, ttl_days=ttl_days)
        self.ttl = timedelta(days=ttl_days)

    def get(self, url: str) -> Optional[Article]:
        """获取文章（三层查找）

        Args:
            url: 文章URL

        Returns:
            Article对象或None
        """
        url_hash = Article._hash_url(url)

        # L1: 内存缓存
        article = self.l1.get(url_hash)
        if article:
            logger.debug(f"L1缓存命中: {url}")
            # 标记来源为缓存
            article.source = "cache"
            return article

        # L2: SQLite缓存
        article = self.l2.get(url_hash)
        if article:
            logger.debug(f"L2缓存命中: {url}")
            # 标记来源为缓存
            article.source = "cache"
            # 回填L1
            self.l1.set(url_hash, article)
            return article

        # L3: 未命中，需要网络获取
        logger.debug(f"缓存未命中: {url}")
        return None

    def set(self, article: Article) -> None:
        """写入缓存（同时写入L1和L2）

        Args:
            article: Article对象
        """
        url_hash = article.url_hash

        # 写入L1
        self.l1.set(url_hash, article)

        # 写入L2
        self.l2.set(article)

    def invalidate(self, url: str) -> bool:
        """使缓存失效

        Args:
            url: 文章URL

        Returns:
            是否成功
        """
        url_hash = Article._hash_url(url)

        # 失效L1
        self.l1.invalidate(url_hash)

        # 失效L2
        return self.l2.delete(url_hash)

    def clear(self, before_date: Optional[datetime] = None) -> Tuple[int, int]:
        """清理缓存

        Args:
            before_date: 清除此日期前的缓存

        Returns:
            (L1清理数, L2清理数)
        """
        l1_cleared = 0
        l2_cleared = 0

        if before_date is None:
            # 清理L1
            l1_size = self.l1.size
            self.l1.clear()
            l1_cleared = l1_size

        # 清理L2
        l2_cleared = self.l2.clear(before_date)

        return (l1_cleared, l2_cleared)

    def get_stats(self) -> Dict[str, any]:
        """获取缓存统计

        Returns:
            统计信息字典
        """
        return {
            'l1': {
                'size': self.l1.size,
                'capacity': self.l1.capacity,
                'hit_rate': self.l1.hit_rate,
                'hits': self.l1.hits,
                'misses': self.l1.misses
            },
            'l2': self.l2.get_stats()
        }
