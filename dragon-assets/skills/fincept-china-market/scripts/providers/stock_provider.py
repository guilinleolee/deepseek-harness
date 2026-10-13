"""
股票数据提供者
封装 AkShare 股票相关数据接口
"""

import pandas as pd
from typing import Optional, List

try:
    import akshare as ak
except ImportError:
    raise ImportError("akshare 未安装，请运行: pip install akshare>=1.14.0")


class StockProvider:
    """股票数据提供者"""

    @staticmethod
    def get_realtime(symbol: str) -> pd.DataFrame:
        """
        获取 A 股实时行情

        Args:
            symbol: 股票代码

        Returns:
            pd.DataFrame: 实时行情
        """
        return ak.stock_zh_a_spot_em(symbol=symbol)

    @staticmethod
    def get_realtime_batch(symbols: List[str]) -> pd.DataFrame:
        """
        批量获取 A 股实时行情

        Args:
            symbols: 股票代码列表

        Returns:
            pd.DataFrame: 实时行情
        """
        symbols_str = ",".join(symbols)
        return ak.stock_zh_a_spot_em(symbol=symbols_str)

    @staticmethod
    def get_kline(symbol: str, period: str = "日",
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None,
                   adjust: str = "") -> pd.DataFrame:
        """
        获取 A 股历史 K 线

        Args:
            symbol: 股票代码
            period: 周期 (日/周/月)
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
            adjust: 复权类型 (qfq/hfq/空)

        Returns:
            pd.DataFrame: K线数据
        """
        return ak.stock_zh_a_hist(
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )

    @staticmethod
    def get_indicator(symbol: str) -> pd.DataFrame:
        """
        获取财务指标

        Args:
            symbol: 股票代码

        Returns:
            pd.DataFrame: 财务指标
        """
        return ak.stock_financial_analysis_indicator(symbol=symbol)

    @staticmethod
    def get_profit(symbol: str) -> pd.DataFrame:
        """获取利润表"""
        return ak.stock_profit_sheet_by_report_em(symbol=symbol)

    @staticmethod
    def get_balance(symbol: str) -> pd.DataFrame:
        """获取资产负债表"""
        return ak.stock_balance_sheet_by_report_em(symbol=symbol)

    @staticmethod
    def get_cashflow(symbol: str) -> pd.DataFrame:
        """获取现金流量表"""
        return ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)

    @staticmethod
    def get_info(symbol: str) -> pd.DataFrame:
        """获取股票基本信息"""
        return ak.stock_individual_info_em(symbol=symbol)

    @staticmethod
    def get_history_fhpx(symbol: str) -> pd.DataFrame:
        """获取分红配股数据"""
        return ak.stock_history_dividend_detail(symbol=symbol, indicator="分红")
