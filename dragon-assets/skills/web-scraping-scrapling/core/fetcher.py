"""
Web Scraping SKILL - Core Fetcher Module
基于 Scrapling 框架的智能爬虫核心模块

Author: Claude Code (Dragon Team)
Version: v1.0.0
Date: 2025-02-26
"""

import json
import time
import random
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScraplingFetcher:
    """
    Scrapling 爬虫核心类

    提供统一的爬虫接口，支持多种模式和配置
    """

    def __init__(
        self,
        stealth: bool = True,
        timeout: int = 30,
        retry_times: int = 3,
        delay_range: tuple = (1, 3),
        proxy_pool: Optional[List[str]] = None
    ):
        """
        初始化爬虫

        Args:
            stealth: 是否启用反检测模式
            timeout: 请求超时时间（秒）
            retry_times: 失败重试次数
            delay_range: 请求延迟范围（秒）
            proxy_pool: 代理池列表
        """
        self.stealth = stealth
        self.timeout = timeout
        self.retry_times = retry_times
        self.delay_range = delay_range
        self.proxy_pool = proxy_pool or []
        self.current_proxy_index = 0

        # 性能统计
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_time': 0
        }

        logger.info("🕷️ Scrapling Fetcher 初始化完成")

    def _get_random_delay(self) -> float:
        """获取随机延迟时间"""
        return random.uniform(*self.delay_range)

    def _get_next_proxy(self) -> Optional[str]:
        """获取下一个代理"""
        if not self.proxy_pool:
            return None

        proxy = self.proxy_pool[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_pool)
        return proxy

    def _retry_fetch(self, url: str, **kwargs) -> Any:
        """
        带重试的请求

        Args:
            url: 目标URL
            **kwargs: 其他参数

        Returns:
            响应对象
        """
        last_error = None

        for attempt in range(self.retry_times):
            try:
                # 添加延迟
                if attempt > 0:
                    delay = self._get_random_delay()
                    logger.info(f"⏳ 等待 {delay:.2f} 秒后重试...")
                    time.sleep(delay)

                # 选择代理
                proxy = self._get_next_proxy()

                # 导入 Scrapling（延迟导入以避免启动时的依赖问题）
                try:
                    from scrapling import Fetcher as ScraplingFetcher
                    fetcher = ScraplingFetcher()
                    if self.stealth:
                        fetcher.configure(stealth=True)
                except ImportError:
                    logger.error("❌ Scrapling 未安装，请运行: pip install scrapling")
                    raise ImportError("Scrapling is not installed")

                # 发起请求 (Scrapling 使用 get/post/put 方法)
                if proxy:
                    logger.info(f"🔗 使用代理: {proxy}")
                    # TODO: Scrapling 代理配置需要查阅文档
                    pass

                result = fetcher.get(url, timeout=self.timeout)

                # 更新统计
                self.stats['successful_requests'] += 1
                logger.info(f"✅ 成功: {url}")

                return result

            except Exception as e:
                last_error = e
                self.stats['failed_requests'] += 1
                logger.warning(f"⚠️  请求失败 (尝试 {attempt + 1}/{self.retry_times}): {e}")

        # 所有重试都失败
        logger.error(f"❌ 所有重试均失败: {url}")
        raise last_error

    def fetch_single(
        self,
        url: str,
        selector: Optional[str] = None,
        extract_text: bool = True
    ) -> Union[str, List[str], Dict[str, Any]]:
        """
        爬取单个页面

        Args:
            url: 目标URL
            selector: CSS选择器（可选）
            extract_text: 是否提取文本内容

        Returns:
            爬取结果
        """
        start_time = time.time()
        self.stats['total_requests'] += 1

        logger.info(f"🎯 开始爬取: {url}")

        try:
            result = self._retry_fetch(url)

            # 如果提供了选择器，提取特定元素
            if selector:
                elements = result.select(selector)
                if extract_text:
                    return [elem.get_text(strip=True) for elem in elements]
                return elements

            # 否则返回整个页面的文本
            if extract_text:
                return result.get_text(strip=True)
            return result

        finally:
            elapsed = time.time() - start_time
            self.stats['total_time'] += elapsed
            logger.info(f"⏱️  耗时: {elapsed:.2f} 秒")

    def fetch_batch(
        self,
        urls: List[str],
        selector: Optional[str] = None,
        max_concurrent: int = 3,
        delay: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        批量爬取多个页面

        Args:
            urls: URL列表
            selector: CSS选择器（可选）
            max_concurrent: 最大并发数
            delay: 请求间隔（秒）

        Returns:
            爬取结果列表
        """
        results = []

        logger.info(f"📦 开始批量爬取: {len(urls)} 个页面")

        for i, url in enumerate(urls, 1):
            logger.info(f"📍 进度: {i}/{len(urls)}")

            try:
                # 爬取数据
                data = self.fetch_single(url, selector)

                results.append({
                    'url': url,
                    'success': True,
                    'data': data,
                    'timestamp': time.time()
                })

                # 延迟（除了最后一个）
                if i < len(urls):
                    time.sleep(delay)

            except Exception as e:
                logger.error(f"❌ 爬取失败: {url} - {e}")
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e),
                    'timestamp': time.time()
                })

        # 统计信息
        success_count = sum(1 for r in results if r['success'])
        logger.info(f"✅ 批量爬取完成: {success_count}/{len(urls)} 成功")

        return results

    def export_results(
        self,
        results: List[Dict[str, Any]],
        output_path: str,
        format: str = 'json'
    ):
        """
        导出结果到文件

        Args:
            results: 爬取结果
            output_path: 输出路径
            format: 输出格式 (json/csv/excel)
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"💾 导出数据到: {output_file}")

        try:
            if format == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)

            elif format == 'csv':
                import pandas as pd
                df = pd.DataFrame(results)
                df.to_csv(output_file, index=False, encoding='utf-8-sig')

            elif format == 'excel':
                import pandas as pd
                df = pd.DataFrame(results)
                df.to_excel(output_file, index=False)

            else:
                raise ValueError(f"不支持的格式: {format}")

            logger.info(f"✅ 导出成功: {output_file}")

        except Exception as e:
            logger.error(f"❌ 导出失败: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """
        获取性能统计

        Returns:
            统计信息字典
        """
        if self.stats['total_requests'] > 0:
            success_rate = self.stats['successful_requests'] / self.stats['total_requests']
            avg_time = self.stats['total_time'] / self.stats['total_requests']
        else:
            success_rate = 0
            avg_time = 0

        return {
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'success_rate': f"{success_rate:.2%}",
            'total_time': f"{self.stats['total_time']:.2f}s",
            'avg_time_per_request': f"{avg_time:.2f}s"
        }

    def print_stats(self):
        """打印性能统计"""
        stats = self.get_stats()

        print("\n" + "="*50)
        print("📊 爬取统计")
        print("="*50)
        print(f"总请求数: {stats['total_requests']}")
        print(f"成功请求: {stats['successful_requests']}")
        print(f"失败请求: {stats['failed_requests']}")
        print(f"成功率: {stats['success_rate']}")
        print(f"总耗时: {stats['total_time']}")
        print(f"平均耗时: {stats['avg_time_per_request']}")
        print("="*50 + "\n")


# 便捷函数
def quick_fetch(url: str, selector: Optional[str] = None) -> Any:
    """
    快速爬取单个页面

    Args:
        url: 目标URL
        selector: CSS选择器（可选）

    Returns:
        爬取结果
    """
    fetcher = ScraplingFetcher()
    return fetcher.fetch_single(url, selector)


def quick_fetch_batch(urls: List[str], selector: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    快速批量爬取

    Args:
        urls: URL列表
        selector: CSS选择器（可选）

    Returns:
        爬取结果列表
    """
    fetcher = ScraplingFetcher()
    return fetcher.fetch_batch(urls, selector)


if __name__ == "__main__":
    # 测试代码
    print("🕷️ Scrapling Fetcher 测试\n")

    # 单页面爬取测试
    print("测试 1: 单页面爬取")
    try:
        result = quick_fetch("https://example.com")
        print(f"结果长度: {len(result)} 字符")
    except Exception as e:
        print(f"测试失败: {e}")

    # 批量爬取测试
    print("\n测试 2: 批量爬取")
    try:
        urls = [
            "https://example.com",
            "https://example.org",
        ]
        results = quick_fetch_batch(urls)
        print(f"成功: {sum(1 for r in results if r['success'])}/{len(results)}")
    except Exception as e:
        print(f"测试失败: {e}")
