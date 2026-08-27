#!/usr/bin/env python3
"""
Baostock Runtime - 统一的 baostock API 调用封装

支持：
- 自动登录/登出
- 方法调用封装
- 数据自动转换为 DataFrame
- 错误处理

Usage:
    from baostock_runtime import BaostockRuntime
    runtime = BaostockRuntime()
    df = runtime.get_stock_daily("600519", days=30)
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    import baostock as bs
    HAS_BAOSTOCK = True
except ImportError:
    HAS_BAOSTOCK = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class BaostockError(Exception):
    """Baostock API 错误"""
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


@dataclass
class StockCode:
    """股票代码"""
    code: str       # 原始代码
    market: str      # sh/sz/bj
    bs_code: str    # Baostock格式


def to_baostock_code(code: str) -> StockCode:
    """转换为 Baostock 格式代码"""
    code = code.strip().upper()

    # 已经是 baostock 格式
    if '.' in code:
        market, num = code.split('.', 1)
        return StockCode(code=code, market=market, bs_code=code)

    # 去掉后缀
    code = code.replace('.SH', '').replace('.SZ', '').replace('.HK', '')

    # 根据代码判断市场
    if code.startswith('6'):
        market = 'sh'
    elif code.startswith(('0', '3')):
        market = 'sz'
    elif code.startswith(('4', '8')):
        market = 'bj'
    else:
        market = 'sh'

    bs_code = f"{market}.{code}"
    return StockCode(code=code, market=market, bs_code=bs_code)


class BaostockRuntime:
    """Baostock API 运行时"""

    def __init__(self):
        if not HAS_BAOSTOCK:
            raise ImportError("请安装 baostock: pip install baostock")
        if not HAS_PANDAS:
            raise ImportError("请安装 pandas: pip install pandas")

        self._logged_in = False
        self.login()

    def login(self):
        """登录 Baostock"""
        if self._logged_in:
            return

        result = bs.login()
        if result.error_code != '0':
            raise BaostockError(result.error_code, result.error_msg)
        self._logged_in = True

    def logout(self):
        """登出 Baostock"""
        if self._logged_in:
            bs.logout()
            self._logged_in = False

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def _query(self, query_func, *args, **kwargs) -> List[Dict]:
        """执行查询并返回结果列表"""
        self.login()

        rs = query_func(*args, **kwargs)
        if rs.error_code != '0':
            raise BaostockError(rs.error_code, rs.error_msg)

        data_list = []
        while rs.next():
            data_list.append(rs.get_row_data())

        return data_list

    def _query_to_df(self, query_func, columns: List[str], *args, **kwargs) -> pd.DataFrame:
        """执行查询并返回 DataFrame"""
        data_list = self._query(query_func, *args, **kwargs)
        if not data_list:
            return pd.DataFrame(columns=columns)

        df = pd.DataFrame(data_list, columns=columns)
        return df

    def get_stock_daily(
        self,
        code: str,
        days: int = 30,
        start_date: str = None,
        end_date: str = None,
        adjustflag: str = "2"
    ) -> pd.DataFrame:
        """
        获取股票日线数据

        Args:
            code: 股票代码，如 '600519' 或 'sh.600519'
            days: 获取天数
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            adjustflag: 复权方式 1=不复权 2=前复权 3=后复权

        Returns:
            DataFrame: 包含 date, open, high, low, close, volume 列
        """
        bs_code = to_baostock_code(code)

        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=days + 30)).strftime('%Y-%m-%d')

        columns = ["date", "open", "high", "low", "close", "volume", "amount"]

        df = self._query_to_df(
            bs.query_history_k_data_plus,
            columns,
            bs_code.bs_code,
            "date,open,high,low,close,volume,amount",
            start_date=start_date,
            end_date=end_date,
            frequency="d",
            adjustflag=adjustflag
        )

        if df.empty:
            return df

        # 类型转换
        for col in ["open", "high", "low", "close", "volume", "amount"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()

        return df.tail(days)

    def get_index_daily(
        self,
        code: str,
        days: int = 60
    ) -> pd.DataFrame:
        """
        获取指数日线数据

        Args:
            code: 指数代码，如 '000001' (上证指数)
            days: 获取天数

        Returns:
            DataFrame: 包含 date, open, high, low, close, volume 列
        """
        # 转换为 baostock 格式
        bs_code = to_baostock_code(code)

        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days + 30)).strftime('%Y-%m-%d')

        columns = ["date", "open", "high", "low", "close", "volume"]

        df = self._query_to_df(
            bs.query_history_k_data_plus,
            columns,
            bs_code.bs_code,
            "date,open,high,low,close,volume",
            start_date=start_date,
            end_date=end_date,
            frequency="d"
        )

        if df.empty:
            return df

        # 类型转换
        for col in ["open", "high", "low", "close", "volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index()

        return df.tail(days)

    def get_fina_indicator(
        self,
        code: str,
        start_date: str = None,
        end_date: str = None
    ) -> pd.DataFrame:
        """
        获取财务指标

        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame: 包含财务指标列
        """
        bs_code = to_baostock_code(code)

        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')

        rs = bs.query_fina_indicator(
            bs_code.bs_code,
            start_date=start_date,
            end_date=end_date
        )

        data_list = []
        while rs.error_code == '0' and rs.next():
            data_list.append(rs.get_row_data())

        if not data_list:
            return pd.DataFrame()

        df = pd.DataFrame(data_list, columns=rs.fields)
        return df

    def get_stock_basic(self, code: str = None) -> pd.DataFrame:
        """
        获取股票基本信息

        Args:
            code: 股票代码，如 'sh.600519'，None 则获取全部

        Returns:
            DataFrame: 包含股票基本信息
        """
        if code:
            bs_code = to_baostock_code(code)
            rs = bs.query_stock_basic(code=bs_code.bs_code)
        else:
            rs = bs.query_stock_basic(code=None)

        data_list = []
        while rs.error_code == '0' and rs.next():
            data_list.append(rs.get_row_data())

        if not data_list:
            return pd.DataFrame()

        df = pd.DataFrame(data_list, columns=rs.fields)
        return df

    def get_dividend(self, code: str, year: str = None) -> pd.DataFrame:
        """
        获取分红数据

        Args:
            code: 股票代码
            year: 年份，如 '2025'

        Returns:
            DataFrame: 包含分红数据
        """
        bs_code = to_baostock_code(code)

        if year is None:
            year = datetime.now().strftime('%Y')

        rs = bs.query_dividend_data(bs_code.bs_code, year=year)

        data_list = []
        while rs.error_code == '0' and rs.next():
            data_list.append(rs.get_row_data())

        if not data_list:
            return pd.DataFrame()

        df = pd.DataFrame(data_list, columns=rs.fields)
        return df


# 全局默认运行时实例
_default_runtime: Optional[BaostockRuntime] = None


def get_runtime() -> BaostockRuntime:
    """获取默认运行时实例"""
    global _default_runtime
    if _default_runtime is None:
        _default_runtime = BaostockRuntime()
    return _default_runtime


def get_stock_daily(code: str, days: int = 30, **kwargs) -> pd.DataFrame:
    """便捷调用函数"""
    return get_runtime().get_stock_daily(code, days, **kwargs)


def get_index_daily(code: str, days: int = 60) -> pd.DataFrame:
    """便捷调用函数"""
    return get_runtime().get_index_daily(code, days)


# CLI 入口
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Baostock Runtime CLI")
    parser.add_argument("action", choices=["stock", "index", "basic"], help="操作类型")
    parser.add_argument("--code", required=True, help="股票/指数代码")
    parser.add_argument("--days", type=int, default=30, help="获取天数")

    args = parser.parse_args()

    try:
        runtime = BaostockRuntime()

        if args.action == "stock":
            df = runtime.get_stock_daily(args.code, days=args.days)
            print(df.to_string())
        elif args.action == "index":
            df = runtime.get_index_daily(args.code, days=args.days)
            print(df.to_string())
        elif args.action == "basic":
            df = runtime.get_stock_basic(args.code)
            print(df.to_string())

        runtime.logout()

    except BaostockError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
