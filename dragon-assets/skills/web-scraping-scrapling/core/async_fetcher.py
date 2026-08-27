"""
异步爬虫模块 - 提供高性能并发爬取能力
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Callable
import logging
from concurrent.futures import ThreadPoolExecutor
from .fetcher import ScraplingFetcher

logger = logging.getLogger(__name__)


class AsyncScraper:
    """异步爬虫类"""

    def __init__(
        self,
        max_concurrent: int = 5,
        delay_range: tuple = (1, 3),
        timeout: int = 30
    ):
        """
        初始化异步爬虫

        Args:
            max_concurrent: 最大并发数
            delay_range: 请求延迟范围
            timeout: 请求超时时间
        """
        self.max_concurrent = max_concurrent
        self.delay_range = delay_range
        self.timeout = timeout
        self.fetcher = ScraplingFetcher(delay_range=delay_range, timeout=timeout)
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_single_async(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        异步爬取单个页面

        Args:
            url: 目标URL
            **kwargs: 其他参数

        Returns:
            爬取结果
        """
        async with self.semaphore:
            try:
                # 在线程池中执行同步操作
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as pool:
                    result = await loop.run_in_executor(
                        pool,
                        lambda: self.fetcher.fetch_single(url, **kwargs)
                    )

                return {
                    'url': url,
                    'success': True,
                    'data': result,
                    'timestamp': time.time()
                }

            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                return {
                    'url': url,
                    'success': False,
                    'error': str(e),
                    'timestamp': time.time()
                }

    async def fetch_batch_async(
        self,
        urls: List[str],
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        异步批量爬取

        Args:
            urls: URL列表
            progress_callback: 进度回调函数

        Returns:
            爬取结果列表
        """
        tasks = []
        for url in urls:
            task = self.fetch_single_async(url)
            tasks.append(task)

        results = []
        for i, task in enumerate(asyncio.as_completed(tasks)):
            result = await task
            results.append(result)

            # 调用进度回调
            if progress_callback:
                progress_callback(i + 1, len(urls), result)

        return results

    async def fetch_with_retry(
        self,
        url: str,
        max_retries: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        带重试的异步爬取

        Args:
            url: 目标URL
            max_retries: 最大重试次数
            **kwargs: 其他参数

        Returns:
            爬取结果
        """
        for attempt in range(max_retries):
            result = await self.fetch_single_async(url, **kwargs)
            if result['success']:
                return result

            # 等待后重试
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 指数退避

        return result


def run_async_scraper(urls: List[str], max_concurrent: int = 5) -> List[Dict]:
    """
    运行异步爬虫（同步包装器）

    Args:
        urls: URL列表
        max_concurrent: 最大并发数

    Returns:
        爬取结果列表
    """
    async def _run():
        scraper = AsyncScraper(max_concurrent=max_concurrent)
        return await scraper.fetch_batch_async(urls)

    return asyncio.run(_run())
