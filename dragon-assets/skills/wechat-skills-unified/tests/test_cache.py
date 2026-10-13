"""
三层缓存系统单元测试
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path

from core.cache import LRUCache, SQLiteCache, ArticleCache
from models.article import Article


class TestLRUCache:
    """LRU内存缓存测试"""

    def test_basic_get_set(self):
        """测试基本读写"""
        cache = LRUCache(capacity=10)

        article = Article(
            url="https://example.com/test1",
            url_hash="hash1",
            title="Test Article",
            author="Author",
            account_name="Account"
        )

        # 设置
        cache.set("hash1", article)

        # 获取
        result = cache.get("hash1")

        assert result is not None
        assert result.title == "Test Article"

    def test_lru_eviction(self):
        """测试LRU驱逐机制"""
        cache = LRUCache(capacity=3)

        # 添加3个元素
        for i in range(3):
            article = Article(
                url=f"https://example.com/test{i}",
                url_hash=f"hash{i}",
                title=f"Article {i}",
                author="Author",
                account_name="Account"
            )
            cache.set(f"hash{i}", article)

        # 添加第4个元素，应该驱逐hash0
        article4 = Article(
            url="https://example.com/test4",
            url_hash="hash4",
            title="Article 4",
            author="Author",
            account_name="Account"
        )
        cache.set("hash4", article4)

        assert cache.get("hash0") is None
        assert cache.get("hash4") is not None

    def test_hit_rate(self):
        """测试缓存命中率"""
        cache = LRUCache(capacity=10)

        article = Article(
            url="https://example.com/test",
            url_hash="hash",
            title="Test",
            author="Author",
            account_name="Account"
        )
        cache.set("hash", article)

        # 命中
        cache.get("hash")
        # 未命中
        cache.get("notexist")

        assert cache.hits == 1
        assert cache.misses == 1
        assert cache.hit_rate == 0.5


class TestSQLiteCache:
    """SQLite持久化缓存测试"""

    def setup_method(self):
        """每个测试前创建临时数据库"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name

    def teardown_method(self):
        """每个测试后删除临时数据库"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_basic_get_set(self):
        """测试基本读写"""
        cache = SQLiteCache(db_path=self.db_path, ttl_days=30)

        article = Article(
            url="https://example.com/test1",
            url_hash="hash1",
            title="Test Article",
            author="Author",
            account_name="Account",
            fetch_time=datetime.now()
        )

        # 设置
        cache.set(article)

        # 获取
        result = cache.get("hash1")

        assert result is not None
        assert result.title == "Test Article"
        assert result.url == "https://example.com/test1"

    def test_ttl_expiry(self):
        """测试TTL过期"""
        cache = SQLiteCache(db_path=self.db_path, ttl_days=1)

        # 创建过期的文章
        old_time = datetime.now() - timedelta(days=2)
        article = Article(
            url="https://example.com/old",
            url_hash="old_hash",
            title="Old Article",
            author="Author",
            account_name="Account",
            fetch_time=old_time
        )

        cache.set(article)

        # 应该返回None（已过期）
        result = cache.get("old_hash")
        assert result is None

    def test_delete(self):
        """测试删除"""
        cache = SQLiteCache(db_path=self.db_path, ttl_days=30)

        article = Article(
            url="https://example.com/test",
            url_hash="hash",
            title="Test",
            author="Author",
            account_name="Account"
        )

        cache.set(article)
        assert cache.get("hash") is not None

        # 删除
        assert cache.delete("hash") is True
        assert cache.get("hash") is None


class TestArticleCache:
    """三层缓存控制器测试"""

    def setup_method(self):
        """每个测试前创建临时缓存"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")

    def teardown_method(self):
        """每个测试后清理临时文件"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_l1_l2_interaction(self):
        """测试L1和L2交互"""
        cache = ArticleCache(db_path=self.db_path, l1_size=5, ttl_days=30)

        # 创建Article（不提供url_hash，让系统自动生成）
        article = Article(
            url="https://example.com/test",
            url_hash="",  # 空字符串会触发自动生成
            title="Test",
            author="Author",
            account_name="Account"
        )

        # 写入缓存
        cache.set(article)

        # 第一次获取：应该命中L2，回填L1
        result1 = cache.get("https://example.com/test")
        assert result1 is not None
        assert result1.title == "Test"

        # 第二次获取：应该命中L1
        result2 = cache.get("https://example.com/test")
        assert result2 is not None

        # L1应该有数据
        assert cache.l1.size == 1

    def test_cache_miss(self):
        """测试缓存未命中"""
        cache = ArticleCache(db_path=self.db_path, l1_size=5, ttl_days=30)

        # 获取不存在的文章
        result = cache.get("https://example.com/notexist")

        assert result is None

    def test_clear_cache(self):
        """测试清理缓存"""
        cache = ArticleCache(db_path=self.db_path, l1_size=5, ttl_days=30)

        # 添加一些文章
        for i in range(3):
            article = Article(
                url=f"https://example.com/test{i}",
                url_hash=f"hash{i}",
                title=f"Article {i}",
                author="Author",
                account_name="Account"
            )
            cache.set(article)

        # 清理所有缓存
        l1_cleared, l2_cleared = cache.clear()

        assert l1_cleared == 3
        assert l2_cleared == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
