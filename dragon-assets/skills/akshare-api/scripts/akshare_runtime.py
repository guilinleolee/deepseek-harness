#!/usr/bin/env python3
"""
AKShare Runtime - 统一的 akshare API 调用封装

支持：
- 港股/美股/期货数据获取
- 数据自动转换为 DataFrame
- 错误处理

Usage:
    from akshare_runtime import AKShareRuntime
    runtime = AKShareRuntime()
    df = runtime.get_hk_daily("00700")
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    import akshare as ak
    HAS_AKSHARE = True
except ImportError:
    HAS_AKSHARE = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class AKShareError(Exception):
    """AKShare API 错误"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class AKShareRuntime:
    """AKShare API 运行时"""

    def __init__(self):
        if not HAS_AKSHARE:
            raise ImportError("请安装 akshare: pip install akshare")
        if not HAS_PANDAS:
            raise ImportError("请安装 pandas: pip install pandas")

    def _safe_call(self, func, *args, **kwargs) -> pd.DataFrame:
        """安全的 API 调用"""
        try:
            result = func(*args, **kwargs)
            if result is None or (isinstance(result, pd.DataFrame) and result.empty):
                return pd.DataFrame()
            return result
        except Exception as e:
            raise AKShareError(f"{func.__name__} 失败: {e}")

    def get_hk_daily(
        self,
        symbol: str,
        adjust: str = "qfq",
        days: int = 30
    ) -> pd.DataFrame:
        """
        获取港股日线数据

        Args:
            symbol: 港股代码，如 '00700'
            adjust: 复权方式 'qfq' 前复权
            days: 获取天数

        Returns:
            DataFrame
        """
        df = self._safe_call(ak.stock_hk_daily, symbol=symbol, adjust=adjust)

        if df.empty:
            return df

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date').sort_index()
            df = df.tail(days)

        return df

    def get_us_daily(
        self,
        symbol: str,
        adjust: str = "qfq",
        days: int = 30
    ) -> pd.DataFrame:
        """
        获取美股日线数据

        Args:
            symbol: 美股代码，如 'AAPL'
            adjust: 复权方式 'qfq' 前复权
            days: 获取天数

        Returns:
            DataFrame
        """
        df = self._safe_call(ak.stock_us_daily, symbol=symbol, adjust=adjust)

        if df.empty:
            return df

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date').sort_index()
            df = df.tail(days)

        return df

    def get_futures_daily(
        self,
        symbol: str,
        days: int = 30
    ) -> pd.DataFrame:
        """
        获取期货日线数据

        Args:
            symbol: 期货代码，如 'rb2501'
            days: 获取天数

        Returns:
            DataFrame
        """
        df = self._safe_call(ak.futures_zh_daily_sina, symbol=symbol)

        if df.empty:
            return df

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date').sort_index()
            df = df.tail(days)

        return df

    def get_etf_hist(
        self,
        symbol: str,
        days: int = 30
    ) -> pd.DataFrame:
        """
        获取ETF历史数据

        Args:
            symbol: ETF代码，如 '518880' (黄金ETF)
            days: 获取天数

        Returns:
            DataFrame
        """
        df = self._safe_call(ak.fund_etf_hist_sina, symbol=symbol)

        if df.empty:
            return df

        if '日期' in df.columns:
            df['日期'] = pd.to_datetime(df['日期'])
            df = df.set_index('日期').sort_index()
            df = df.tail(days)

        return df

    def get_forex_rate(
        self,
        symbol: str = "USD/CNY"
    ) -> float:
        """
        获取汇率

        Args:
            symbol: 货币对，如 'USD/CNY'

        Returns:
            汇率
        """
        df = self._safe_call(ak.forex_hist, symbol=symbol)

        if df.empty:
            return None

        return float(df.iloc[-1]['close'])

    def get_stock_spot(
        self,
        market: str = "hk",
        symbol: str = None
    ) -> pd.DataFrame:
        """
        获取实时行情

        Args:
            market: 市场 'hk' 港股, 'us' 美股
            symbol: 股票代码

        Returns:
            DataFrame
        """
        if market == "hk":
            return self._safe_call(ak.stock_hk_spot_em, symbol=symbol)
        elif market == "us":
            return self._safe_call(ak.stock_us_spot_em, symbol=symbol)
        else:
            raise AKShareError(f"不支持的市场: {market}")


# 全局默认运行时实例
_default_runtime: Optional[AKShareRuntime] = None


def get_runtime() -> AKShareRuntime:
    """获取默认运行时实例"""
    global _default_runtime
    if _default_runtime is None:
        _default_runtime = AKShareRuntime()
    return _default_runtime


def get_hk_daily(symbol: str, **kwargs) -> pd.DataFrame:
    """便捷调用函数"""
    return get_runtime().get_hk_daily(symbol, **kwargs)


def get_us_daily(symbol: str, **kwargs) -> pd.DataFrame:
    """便捷调用函数"""
    return get_runtime().get_us_daily(symbol, **kwargs)


def get_futures_daily(symbol: str, **kwargs) -> pd.DataFrame:
    """便捷调用函数"""
    return get_runtime().get_futures_daily(symbol, **kwargs)


# CLI 入口
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="AKShare Runtime CLI")
    parser.add_argument("action", choices=["hk", "us", "futures", "etf"], help="操作类型")
    parser.add_argument("--code", required=True, help="代码")
    parser.add_argument("--days", type=int, default=30, help="获取天数")

    args = parser.parse_args()

    try:
        runtime = AKShareRuntime()

        if args.action == "hk":
            df = runtime.get_hk_daily(args.code, days=args.days)
            print(df.to_string())
        elif args.action == "us":
            df = runtime.get_us_daily(args.code, days=args.days)
            print(df.to_string())
        elif args.action == "futures":
            df = runtime.get_futures_daily(args.code, days=args.days)
            print(df.to_string())
        elif args.action == "etf":
            df = runtime.get_etf_hist(args.code, days=args.days)
            print(df.to_string())

    except AKShareError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
