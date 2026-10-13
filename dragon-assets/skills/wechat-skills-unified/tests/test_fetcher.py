"""
fetcher模块单元测试
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from core.fetcher import UnifiedFetcher
from models.article import Article
from core.cache import ArticleCache


class TestUnifiedFetcher:
    """统一获取器测试"""

    def setup_method(self):
        """每个测试前创建临时缓存"""
        import tempfile
        import os
        from core.config import Config, get_default_config

        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # 创建使用临时数据库的配置
        self.config = Config(
            cache_path=self.db_path,
            cache_enabled=True,
            l1_cache_size=5,
            cache_ttl_days=30
        )

        # 创建fetcher（使用config参数）
        self.fetcher = UnifiedFetcher(config=self.config)

    def teardown_method(self):
        """每个测试后清理临时文件"""
        import os

        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_init(self):
        """测试初始化"""
        assert self.fetcher.cache is not None
        assert self.fetcher.config is not None

    def test_fetch_from_cache(self):
        """测试从缓存获取"""
        # 使用有效的微信公众号URL
        test_url = "https://mp.weixin.qq.com/s/test123"

        # 先写入缓存
        article = Article(
            url=test_url,
            url_hash="",
            title="Test Article",
            author="Author",
            account_name="Account",
            source="cache"
        )
        self.fetcher.cache.set(article)

        # 从缓存获取
        result = self.fetcher.fetch_article(test_url)

        assert result is not None
        assert result.title == "Test Article"
        assert result.source == "cache"

    def test_cache_miss(self):
        """测试缓存未命中"""
        test_url = "https://mp.weixin.qq.com/s/test456"

        # Mock DirectFetchStrategy.fetch
        with patch('core.fallback.DirectFetchStrategy.fetch') as mock_fetch:
            mock_fetch.return_value = Article(
                url=test_url,
                url_hash="",
                title="Network Article",
                author="Author",
                account_name="Account",
                source="direct"
            )

            result = self.fetcher.fetch_article(test_url)

            assert result is not None
            assert result.title == "Network Article"
            mock_fetch.assert_called_once()

    def test_fetch_batch(self):
        """测试批量获取"""
        # Mock DirectFetchStrategy.fetch
        with patch('core.fallback.DirectFetchStrategy.fetch') as mock_fetch:
            def create_article(url):
                return Article(
                    url=url,
                    url_hash="",
                    title=f"Article {url}",
                    author="Author",
                    account_name="Account",
                    source="direct"
                )

            mock_fetch.side_effect = lambda url: create_article(url)

            urls = [
                "https://mp.weixin.qq.com/s/test1",
                "https://mp.weixin.qq.com/s/test2",
                "https://mp.weixin.qq.com/s/test3"
            ]

            results = self.fetcher.fetch_batch(urls, concurrent=2)

            assert len(results) == 3
            # 所有结果都应该成功
            assert all(r is not None for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
