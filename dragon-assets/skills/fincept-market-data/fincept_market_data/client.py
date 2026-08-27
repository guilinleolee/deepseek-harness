"""
Fincept Market Data Client
主客户端，封装所有数据源
"""

import os
import json
import sqlite3
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Union, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from .providers.base_provider import BaseProvider, ProviderPriority
from .providers.yfinance_provider import YFinanceProvider
from .providers.polygon_provider import PolygonProvider
from .providers.crypto_provider import CryptoProvider

logger = logging.getLogger(__name__)


class Cache:
    """SQLite缓存"""

    def __init__(self, cache_dir: str = "~/.fincept_cache", ttl: int = 300):
        self.cache_dir = Path(os.path.expanduser(cache_dir))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / "market_data.db"
        self.ttl = ttl
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    ttl INTEGER NOT NULL
                )
            """)

    def _make_key(self, symbol: str, data_type: str) -> str:
        return f"{symbol}:{data_type}"

    def get(self, symbol: str, data_type: str) -> Optional[Dict]:
        key = self._make_key(symbol, data_type)
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT data, timestamp, ttl FROM cache WHERE key = ?",
                (key,)
            ).fetchone()

        if row is None:
            return None

        data, timestamp, ttl = row
        if time.time() - timestamp > ttl:
            return None

        return json.loads(data)

    def set(self, symbol: str, data_type: str, data: Dict, ttl: Optional[int] = None):
        key = self._make_key(symbol, data_type)
        ttl = ttl or self.ttl
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, data, timestamp, ttl) VALUES (?, ?, ?, ?)",
                (key, json.dumps(data), time.time(), ttl)
            )

    def clear(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache")

    def stats(self) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]
            oldest = conn.execute(
                "SELECT MIN(timestamp) FROM cache"
            ).fetchone()[0]
        return {
            "total_entries": total,
            "oldest_entry": datetime.fromtimestamp(oldest).isoformat() if oldest else None,
            "cache_dir": str(self.cache_dir)
        }


class MarketDataClient:
    """
    金融市场数据客户端

    支持30+数据源，统一API获取股票、ETF、期货、加密货币等行情数据
    """

    def __init__(
        self,
        cache_enabled: bool = True,
        cache_dir: str = "~/.fincept_cache",
        timeout: int = 30,
        max_retries: int = 3,
        provider_priority: Optional[List[str]] = None,
        api_keys: Optional[Dict[str, str]] = None
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.provider_priority = provider_priority or ["yfinance", "polygon", "crypto"]
        self.api_keys = api_keys or {}

        self.cache = Cache(cache_dir) if cache_enabled else None

        self.providers: Dict[str, BaseProvider] = {
            "yfinance": YFinanceProvider(timeout, max_retries),
            "polygon": PolygonProvider(
                timeout, max_retries,
                api_key=self.api_keys.get("polygon")
            ),
            "crypto": CryptoProvider(timeout, max_retries),
        }

    def _get_provider(self, data_type: str) -> BaseProvider:
        """根据数据类型选择最优Provider"""
        for name in self.provider_priority:
            provider = self.providers.get(name)
            if provider and provider.supports(data_type):
                return provider
        return self.providers["yfinance"]

    def _with_cache(self, symbol: str, data_type: str, fetch_func, ttl: int = 300):
        """带缓存的获取逻辑"""
        if self.cache:
            cached = self.cache.get(symbol, data_type)
            if cached:
                logger.debug(f"Cache hit: {symbol}:{data_type}")
                return cached

        result = fetch_func()

        if self.cache and result:
            self.cache.set(symbol, data_type, result, ttl)

        return result

    def quote(self, symbol: str, use_cache: bool = True) -> Dict:
        """
        获取单只股票实时行情

        Args:
            symbol: 股票代码，如 "AAPL"
            use_cache: 是否使用缓存

        Returns:
            dict: 行情数据
        """
        def fetch():
            provider = self._get_provider("quote")
            return provider.quote(symbol)

        if use_cache:
            return self._with_cache(symbol.upper(), "quote", fetch, ttl=60)
        return fetch()

    def quotes(self, symbols: List[str], use_cache: bool = True) -> List[Dict]:
        """
        批量获取股票实时行情

        Args:
            symbols: 股票代码列表
            use_cache: 是否使用缓存

        Returns:
            list: 行情数据列表
        """
        results = []
        for symbol in symbols:
            results.append(self.quote(symbol, use_cache))
        return results

    def historical(
        self,
        symbol: str,
        start: str,
        end: str,
        interval: str = "1d",
        use_cache: bool = True
    ) -> List[Dict]:
        """
        获取历史K线数据

        Args:
            symbol: 股票代码
            start: 开始日期 "YYYY-MM-DD"
            end: 结束日期 "YYYY-MM-DD"
            interval: K线周期 "1d", "60m", "1h", "1wk"
            use_cache: 是否使用缓存

        Returns:
            list: K线数据列表
        """
        cache_key = f"historical:{interval}"

        def fetch():
            provider = self._get_provider("historical")
            return provider.historical(symbol, start, end, interval)

        if use_cache:
            return self._with_cache(symbol.upper(), cache_key, fetch, ttl=3600)
        return fetch()

    def crypto(
        self,
        symbol: str,
        use_cache: bool = True
    ) -> Dict:
        """
        获取加密货币实时价格

        Args:
            symbol: 交易对，如 "BTC-USD", "ETH-USD"
            use_cache: 是否使用缓存

        Returns:
            dict: 实时价格数据
        """
        def fetch():
            provider = self.providers["crypto"]
            return provider.quote(symbol)

        if use_cache:
            return self._with_cache(symbol.upper(), "crypto", fetch, ttl=30)
        return fetch()

    def crypto_historical(
        self,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        interval: str = "1h"
    ) -> List[Dict]:
        """
        获取加密货币历史数据

        Args:
            symbol: 交易对
            start: 开始日期
            end: 结束日期
            interval: 周期 "1m", "5m", "15m", "1h", "4h", "1d"

        Returns:
            list: 历史数据列表
        """
        if end is None:
            end = datetime.now().strftime("%Y-%m-%d")
        if start is None:
            start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        provider = self.providers["crypto"]
        return provider.historical(symbol, start, end, interval)

    def financials(self, symbol: str, use_cache: bool = True) -> Dict:
        """
        获取财务报表

        Args:
            symbol: 股票代码
            use_cache: 是否使用缓存

        Returns:
            dict: 包含 income_statement, balance_sheet, cash_flow
        """
        def fetch():
            provider = self._get_provider("financials")
            return provider.financials(symbol)

        if use_cache:
            return self._with_cache(symbol.upper(), "financials", fetch, ttl=86400)
        return fetch()

    def earnings(self, symbol: str, use_cache: bool = True) -> List[Dict]:
        """
        获取盈利数据

        Args:
            symbol: 股票代码
            use_cache: 是否使用缓存

        Returns:
            list: 盈利数据列表
        """
        def fetch():
            provider = self._get_provider("earnings")
            return provider.earnings(symbol)

        if use_cache:
            return self._with_cache(symbol.upper(), "earnings", fetch, ttl=86400)
        return fetch()

    def option_chain(self, symbol: str, expiration: Optional[str] = None) -> Dict:
        """
        获取期权链

        Args:
            symbol: 股票代码
            expiration: 到期日 "YYYY-MM-DD"，默认获取最近到期

        Returns:
            dict: 包含 calls 和 puts 列表
        """
        provider = self._get_provider("option_chain")
        return provider.option_chain(symbol, expiration)

    def option_expirations(self, symbol: str) -> List[str]:
        """获取期权到期日列表"""
        provider = self._get_provider("option_chain")
        return provider.option_expirations(symbol)

    def batch_historical(
        self,
        symbols: List[str],
        start: str,
        end: str,
        interval: str = "1d",
        parallel: bool = True,
        max_workers: int = 5
    ) -> Dict[str, List[Dict]]:
        """
        批量获取历史数据

        Args:
            symbols: 股票代码列表
            start: 开始日期
            end: 结束日期
            interval: K线周期
            parallel: 是否并行获取
            max_workers: 最大并行数

        Returns:
            dict: {symbol: [kline_data, ...]}
        """
        results = {}

        if parallel:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(
                        self.historical, s, start, end, interval, False
                    ): s for s in symbols
                }
                for future in as_completed(futures):
                    symbol = futures[future]
                    try:
                        results[symbol] = future.result()
                    except Exception as e:
                        logger.error(f"Error fetching {symbol}: {e}")
                        results[symbol] = []
        else:
            for symbol in symbols:
                try:
                    results[symbol] = self.historical(symbol, start, end, interval, False)
                except Exception as e:
                    logger.error(f"Error fetching {symbol}: {e}")
                    results[symbol] = []

        return results

    def search_symbols(self, query: str) -> List[Dict]:
        """
        搜索股票代码

        Args:
            query: 搜索关键词

        Returns:
            list: 匹配的股票列表
        """
        provider = self._get_provider("search")
        return provider.search(query)


class RateLimitError(Exception):
    """Rate limit exceeded"""
    pass


class DataNotFoundError(Exception):
    """Data not found for symbol"""
    pass


class ProviderError(Exception):
    """Generic provider error"""
    pass
