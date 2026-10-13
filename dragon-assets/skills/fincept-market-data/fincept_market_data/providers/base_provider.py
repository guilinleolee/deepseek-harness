"""
Base Data Provider
Provider基类，定义统一接口
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, List, Dict, Any


class DataType(Enum):
    """支持的数据类型"""
    QUOTE = "quote"
    HISTORICAL = "historical"
    FINANCIALS = "financials"
    EARNINGS = "earnings"
    OPTION_CHAIN = "option_chain"
    CRYPTO = "crypto"
    SEARCH = "search"


class ProviderPriority(Enum):
    """Provider优先级"""
    PRIMARY = 1
    SECONDARY = 2
    FALLBACK = 3


class BaseProvider(ABC):
    """
    数据Provider基类

    所有数据源Provider必须继承此类并实现抽象方法
    """

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries

    @abstractmethod
    def supports(self, data_type: str) -> bool:
        """
        检查是否支持该数据类型

        Args:
            data_type: 数据类型字符串

        Returns:
            bool: 是否支持
        """
        pass

    def quote(self, symbol: str) -> Dict[str, Any]:
        """
        获取实时行情

        Args:
            symbol: 股票代码

        Returns:
            dict: 行情数据
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support quotes")

    def historical(
        self,
        symbol: str,
        start: str,
        end: str,
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """
        获取历史K线

        Args:
            symbol: 股票代码
            start: 开始日期
            end: 结束日期
            interval: K线周期

        Returns:
            list: K线数据列表
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support historical data")

    def financials(self, symbol: str) -> Dict[str, List[Dict]]:
        """
        获取财务报表

        Args:
            symbol: 股票代码

        Returns:
            dict: 财务报表
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support financials")

    def earnings(self, symbol: str) -> List[Dict[str, Any]]:
        """
        获取盈利数据

        Args:
            symbol: 股票代码

        Returns:
            list: 盈利数据列表
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support earnings")

    def option_chain(
        self,
        symbol: str,
        expiration: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取期权链

        Args:
            symbol: 股票代码
            expiration: 到期日

        Returns:
            dict: 期权链数据
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support options")

    def option_expirations(self, symbol: str) -> List[str]:
        """
        获取期权到期日列表

        Args:
            symbol: 股票代码

        Returns:
            list: 到期日列表
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support option expirations")

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        搜索股票代码

        Args:
            query: 搜索关键词

        Returns:
            list: 匹配的股票列表
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support search")

    def _retry_with_backoff(self, func, *args, **kwargs):
        """
        指数退避重试

        Args:
            func: 要执行的函数
            *args, **kwargs: 函数参数

        Returns:
            函数返回值
        """
        import time
        import logging

        logger = logging.getLogger(__name__)

        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise

                wait_time = 2 ** attempt
                logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s..."
                )
                time.sleep(wait_time)

        return None

    def _validate_symbol(self, symbol: str) -> str:
        """验证并标准化股票代码"""
        return symbol.upper().strip()
