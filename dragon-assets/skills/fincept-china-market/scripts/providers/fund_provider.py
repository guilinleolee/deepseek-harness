"""
基金数据提供者
封装 AkShare 基金相关数据接口
"""

import pandas as pd
from typing import Optional

try:
    import akshare as ak
except ImportError:
    raise ImportError("akshare 未安装，请运行: pip install akshare>=1.14.0")


class FundProvider:
    """基金数据提供者"""

    @staticmethod
    def get_etf_hist(symbol: str, period: str = "daily",
                      start_date: Optional[str] = None,
                      end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取 ETF 历史数据

        Args:
            symbol: ETF 代码
            period: 周期 (daily/weekly/monthly)
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: ETF 历史数据
        """
        return ak.fund_etf_hist_sina(
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date
        )

    @staticmethod
    def get_open_fund_info(fund: str) -> pd.DataFrame:
        """
        获取公募基金信息

        Args:
            fund: 基金代码

        Returns:
            pd.DataFrame: 基金信息
        """
        return ak.fund_open_fund_info(fund=fund)

    @staticmethod
    def get_open_fund_list() -> pd.DataFrame:
        """获取公募基金列表"""
        return ak.fund_open_fund_info_em()

    @staticmethod
    def get_etf_fund_info() -> pd.DataFrame:
        """获取 ETF 基金列表"""
        return ak.fund_etf_info_sina()

    @staticmethod
    def get_lof_fund_list() -> pd.DataFrame:
        """获取 LOF 基金列表"""
        return ak.fund_lof_info_sina()

    @staticmethod
    def get_financial_fund() -> pd.DataFrame:
        """获取理财基金列表"""
        return ak.fund_financial_fund_info()

    @staticmethod
    def get_rank() -> pd.DataFrame:
        """获取基金排行榜"""
        return ak.fund_em_rank()
