"""
Web Scraping SKILL - Core Package
"""

from .fetcher import ScraplingFetcher, quick_fetch, quick_fetch_batch
from .data_cleaner import DataValidator, DataCleaner
from .async_fetcher import AsyncScraper, run_async_scraper
from .proxy_pool import ProxyPool, ProxyInfo
from .monitoring import PerformanceMonitor, ErrorTracker

__all__ = [
    'ScraplingFetcher',
    'quick_fetch',
    'quick_fetch_batch',
    'DataValidator',
    'DataCleaner',
    'AsyncScraper',
    'run_async_scraper',
    'ProxyPool',
    'ProxyInfo',
    'PerformanceMonitor',
    'ErrorTracker',
]

__version__ = '1.1.0'
__author__ = 'Claude Code (Dragon Team)'
