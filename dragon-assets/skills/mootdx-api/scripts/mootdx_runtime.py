#!/usr/bin/env python3
"""
Mootdx Runtime - 统一的 mootdx API 调用封装

支持：
- 实时行情/分时数据/盘口数据
- 自动选择数据源
- 错误处理

Usage:
    from mootdx_runtime import MootdxRuntime
    runtime = MootdxRuntime()
    df = runtime.get_daily("600519")
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from mootdx import Reader
    HAS_MOOTDX = True
except ImportError:
    HAS_MOOTDX = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class MootdxError(Exception):
    """Mootdx API 错误"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def to_mootdx_code(code: str) -> str:
    """转换为 Mootdx 格式代码"""
    code = code.strip().upper()

    # 已经是 mootdx 格式
    if code.startswith('sh') or code.startswith('sz'):
        return code

    # 去掉后缀
    code = code.replace('.SH', '').replace('.SZ', '').replace('.', '')

    # 根据代码判断市场
    if code.startswith('6'):
        return f"sh{code}"
    elif code.startswith(('0', '3')):
        return f"sz{code}"
    else:
        return f"sh{code}"


class MootdxRuntime:
    """Mootdx API 运行时"""

    def __init__(self, source: str = 'bestpay'):
        if not HAS_MOOTDX:
            raise ImportError("请安装 mootdx: pip install mootdx")
        if not HAS_PANDAS:
            raise ImportError("请安装 pandas: pip install pandas")

        self.source = source
        self._reader = None

    def _get_reader(self):
        """获取 Reader 实例"""
        if self._reader is None:
            self._reader = Reader(self.source)
        return self._reader

    def get_daily(
        self,
        code: str,
        start: str = None,
        end: str = None,
        days: int = 30
    ) -> pd.DataFrame:
        """
        获取日线数据

        Args:
            code: 股票代码，如 '600519' 或 'sh600519'
            start: 开始日期 (YYYYMMDD)
            end: 结束日期 (YYYYMMDD)
            days: 获取天数

        Returns:
            DataFrame
        """
        mootdx_code = to_mootdx_code(code)

        if end is None:
            end = datetime.now().strftime('%Y%m%d')
        if start is None:
            start = (datetime.now() - timedelta(days=days + 10)).strftime('%Y%m%d')

        try:
            reader = self._get_reader()
            df = reader.daily(code=mootdx_code, start=start, end=end)

            if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                return pd.DataFrame()

            # 处理日期列
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
                df = df.set_index('date').sort_index()
                df = df.tail(days)

            return df
        except Exception as e:
            raise MootdxError(f"获取日线失败: {e}")

    def get_minute(self, code: str) -> pd.DataFrame:
        """
        获取分时数据

        Args:
            code: 股票代码

        Returns:
            DataFrame
        """
        mootdx_code = to_mootdx_code(code)

        try:
            reader = self._get_reader()
            df = reader.minute(code=mootdx_code)

            if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                return pd.DataFrame()

            return df
        except Exception as e:
            raise MootdxError(f"获取分时数据失败: {e}")

    def get_bidask(self, code: str) -> pd.DataFrame:
        """
        获取盘口数据

        Args:
            code: 股票代码

        Returns:
            DataFrame
        """
        mootdx_code = to_mootdx_code(code)

        try:
            reader = self._get_reader()
            df = reader.bidAsk(code=mootdx_code)

            if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                return pd.DataFrame()

            return df
        except Exception as e:
            raise MootdxError(f"获取盘口数据失败: {e}")

    def get_realtime(self, codes: List[str]) -> pd.DataFrame:
        """
        获取实时行情

        Args:
            codes: 股票代码列表

        Returns:
            DataFrame
        """
        mootdx_codes = [to_mootdx_code(c) for c in codes]

        try:
            reader = self._get_reader()
            df = reader.realtime(symbols=mootdx_codes)

            if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                return pd.DataFrame()

            return df
        except Exception as e:
            raise MootdxError(f"获取实时行情失败: {e}")


# 全局默认运行时实例
_default_runtime: Optional[MootdxRuntime] = None


def get_runtime(source: str = 'bestpay') -> MootdxRuntime:
    """获取默认运行时实例"""
    global _default_runtime
    if _default_runtime is None:
        _default_runtime = MootdxRuntime(source)
    return _default_runtime


def get_daily(code: str, **kwargs) -> pd.DataFrame:
    """便捷调用函数"""
    return get_runtime().get_daily(code, **kwargs)


def get_minute(code: str) -> pd.DataFrame:
    """便捷调用函数"""
    return get_runtime().get_minute(code)


def get_bidask(code: str) -> pd.DataFrame:
    """便捷调用函数"""
    return get_runtime().get_bidask(code)


# CLI 入口
if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Mootdx Runtime CLI")
    parser.add_argument("action", choices=["daily", "minute", "bidask", "realtime"], help="操作类型")
    parser.add_argument("--code", help="股票代码")
    parser.add_argument("--codes", help="股票代码列表(逗号分隔)", default="")
    parser.add_argument("--days", type=int, default=30, help="获取天数")

    args = parser.parse_args()

    try:
        runtime = MootdxRuntime()

        if args.action == "daily":
            if not args.code:
                print("--code 参数必需", file=sys.stderr)
                sys.exit(1)
            df = runtime.get_daily(args.code, days=args.days)
            print(df.to_string())
        elif args.action == "minute":
            if not args.code:
                print("--code 参数必需", file=sys.stderr)
                sys.exit(1)
            df = runtime.get_minute(args.code)
            print(df.to_string())
        elif args.action == "bidask":
            if not args.code:
                print("--code 参数必需", file=sys.stderr)
                sys.exit(1)
            df = runtime.get_bidask(args.code)
            print(df.to_string())
        elif args.action == "realtime":
            codes = args.codes.split(',') if args.codes else []
            if not codes:
                print("--codes 参数必需", file=sys.stderr)
                sys.exit(1)
            df = runtime.get_realtime(codes)
            print(df.to_string())

    except MootdxError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
