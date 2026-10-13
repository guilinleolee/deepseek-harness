"""
统一文章获取器
化学视角：Fetcher是核心反应器，协调缓存、降级、解析等所有反应

设计原则：
- 统一入口：所有获取通过此模块
- 缓存优先：先查缓存，再查网络
- 自动降级：主策略失败自动降级
- 向后兼容：兼容旧版API
"""

import logging
from typing import Optional, List
from datetime import datetime

from core.config import Config, get_default_config
from core.cache import ArticleCache
from core.fallback import FallbackController, DirectFetchStrategy, APIFetchStrategy
from core.parser import HTMLParser
from core.ratelimit import get_global_limiter, RateLimitedError
from utils.http import HTTPClient
from models.article import Article
from utils.security import sanitize_url, sanitize_exception


logger = logging.getLogger(__name__)


class UnifiedFetcher:
    """统一文章获取器

    核心流程：
    1. 验证URL
    2. 查询缓存（L1 -> L2）
    3. 缓存未命中，执行降级获取
    4. 写入缓存
    5. 返回Article对象
    """

    def __init__(self, config: Optional[Config] = None):
        """初始化统一获取器

        Args:
            config: 配置对象，None则使用默认配置
        """
        self.config = config or get_default_config()

        # 初始化缓存
        if self.config.cache_enabled:
            self.cache = ArticleCache(
                db_path=self.config.cache_path,
                l1_size=self.config.l1_cache_size,
                ttl_days=self.config.cache_ttl_days
            )
        else:
            self.cache = None

        # 初始化HTTP客户端
        self.http_client = HTTPClient(
            user_agents=self.config.user_agents,
            timeout=self.config.timeout,
            retry_times=self.config.retry_times,
            retry_delay=self.config.retry_delay,
            request_interval=self.config.request_interval
        )

        # 初始化HTML解析器
        self.parser = HTMLParser()

        # 初始化降级控制器
        strategies = [
            DirectFetchStrategy(self.http_client, self.parser)
        ]

        # 如果配置了API Key，添加API降级策略
        if self.config.enable_fallback and self.config.api_key:
            strategies.append(
                APIFetchStrategy(
                    api_key=self.config.api_key,
                    api_endpoint=self.config.api_endpoint
                )
            )

        self.fallback = FallbackController(strategies)

    def fetch_article(
        self,
        url: str,
        use_cache: bool = True
    ) -> Optional[Article]:
        """获取单篇文章

        Args:
            url: 文章URL
            use_cache: 是否使用缓存

        Returns:
            Article对象，失败返回None

        Raises:
            URLValidationError: URL格式错误
            AllStrategiesFailedError: 所有策略失败
            RateLimitedError: 超过速率限制
        """
        # 验证URL
        from utils.http import validate_url
        if not validate_url(url):
            logger.error(f"URL格式错误: {sanitize_url(url)}")
            return None

        # 获取速率限制许可
        limiter = get_global_limiter()
        if not limiter.acquire(tokens=1, timeout=30):
            logger.warning(f"速率限制：请求被拒绝")
            raise RateLimitedError("超过速率限制，请稍后重试")

        try:
            # 1. 查询缓存
            if use_cache and self.cache:
                article = self.cache.get(url)
                if article:
                    logger.info(f"缓存命中: {sanitize_url(url)}")
                    return article

            # 2. 降级获取
            try:
                logger.info(f"开始获取: {sanitize_url(url)}")
                article = self.fallback.fetch(url)

                # 3. 写入缓存
                if use_cache and self.cache:
                    self.cache.set(article)
                    logger.info("已写入缓存")

                return article

            except Exception as e:
                logger.error(f"获取失败: {sanitize_url(url)}, 错误: {sanitize_exception(e)}")
                return None
        finally:
            # 释放速率限制许可
            limiter.release()

    def fetch_batch(
        self,
        urls: List[str],
        use_cache: bool = True,
        concurrent: int = 3
    ) -> List[Optional[Article]]:
        """批量获取文章

        Args:
            urls: 文章URL列表
            use_cache: 是否使用缓存
            concurrent: 并发数（1-10）

        Returns:
            Article列表（失败位置为None）

        Raises:
            RateLimitedError: 批量数量超过限制
        """
        # 限制并发数
        concurrent = max(1, min(concurrent, 10))

        # 预检查：是否超过速率限制
        if len(urls) > 100:
            logger.warning(f"批量获取数量过大: {len(urls)}")
            raise RateLimitedError(f"单次最多100个URL，当前: {len(urls)}")

        results = []

        # 分批处理（避免并发过多）
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def fetch_single(url: str) -> tuple:
            """获取单篇文章（返回索引和结果）"""
            return urls.index(url), self.fetch_article(url, use_cache)

        with ThreadPoolExecutor(max_workers=concurrent) as executor:
            futures = {executor.submit(fetch_single, url): url for url in urls}

            for future in as_completed(futures):
                try:
                    idx, article = future.result()
                    results.append((idx, article))
                except RateLimitedError as e:
                    logger.error(f"速率限制: {sanitize_exception(e)}")
                    idx = urls.index(futures[future])
                    results.append((idx, None))
                except Exception as e:
                    url = futures[future]
                    logger.error(f"批量获取失败: {sanitize_url(url)}, 错误: {sanitize_exception(e)}")
                    idx = urls.index(url)
                    results.append((idx, None))

        # 按原始顺序排序
        results.sort(key=lambda x: x[0])
        return [article for _, article in results]

    def clear_cache(
        self,
        before_date: Optional[datetime] = None
    ) -> int:
        """清理缓存

        Args:
            before_date: 清除此日期前的缓存

        Returns:
            清理的条目数
        """
        if not self.cache:
            return 0

        l1_cleared, l2_cleared = self.cache.clear(before_date)
        return l1_cleared + l2_cleared

    def get_cache_stats(self) -> dict:
        """获取缓存统计信息

        Returns:
            统计信息字典
        """
        if not self.cache:
            return {}

        return self.cache.get_stats()

    def get_health_status(self) -> dict:
        """获取降级策略健康状态

        Returns:
            健康状态字典
        """
        return self.fallback.get_health_status()


# 全局默认实例
_default_fetcher: Optional[UnifiedFetcher] = None


def get_default_fetcher() -> UnifiedFetcher:
    """获取全局默认获取器（单例）

    Returns:
        UnifiedFetcher实例
    """
    global _default_fetcher
    if _default_fetcher is None:
        _default_fetcher = UnifiedFetcher()
    return _default_fetcher


def fetch_article(
    url: str,
    use_cache: bool = True,
    config: Optional[Config] = None
) -> Optional[Article]:
    """获取单篇文章（便捷函数）

    Args:
        url: 文章URL
        use_cache: 是否使用缓存
        config: 配置对象

    Returns:
        Article对象，失败返回None

    示例:
        >>> article = fetch_article("https://mp.weixin.qq.com/s/xxxxx")
        >>> print(article.title)
    """
    if config:
        fetcher = UnifiedFetcher(config)
    else:
        fetcher = get_default_fetcher()

    return fetcher.fetch_article(url, use_cache)


def fetch_batch(
    urls: List[str],
    use_cache: bool = True,
    concurrent: int = 3,
    config: Optional[Config] = None
) -> List[Optional[Article]]:
    """批量获取文章（便捷函数）

    Args:
        urls: 文章URL列表
        use_cache: 是否使用缓存
        concurrent: 并发数
        config: 配置对象

    Returns:
        Article列表

    示例:
        >>> urls = ["url1", "url2", "url3"]
        >>> articles = fetch_batch(urls)
        >>> for article in articles:
        ...     if article:
        ...         print(article.title)
    """
    if config:
        fetcher = UnifiedFetcher(config)
    else:
        fetcher = get_default_fetcher()

    return fetcher.fetch_batch(urls, use_cache, concurrent)


def clear_cache(
    before_date: Optional[datetime] = None,
    config: Optional[Config] = None
) -> int:
    """清理缓存（便捷函数）

    Args:
        before_date: 清除此日期前的缓存
        config: 配置对象

    Returns:
        清理的条目数
    """
    if config:
        fetcher = UnifiedFetcher(config)
    else:
        fetcher = get_default_fetcher()

    return fetcher.clear_cache(before_date)
