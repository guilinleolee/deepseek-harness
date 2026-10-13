"""
期货数据提供者
封装 AkShare 期货相关数据接口
"""

import pandas as pd
from typing import Optional

try:
    import akshare as ak
except ImportError:
    raise ImportError("akshare 未安装，请运行: pip install akshare>=1.14.0")


class FuturesProvider:
    """期货数据提供者"""

    @staticmethod
    def get_spot() -> pd.DataFrame:
        """
        获取商品期货实时行情

        Returns:
            pd.DataFrame: 期货实时行情
        """
        return ak.futures_zh_spot()

    @staticmethod
    def get_daily(symbol: str) -> pd.DataFrame:
        """
        获取期货日线数据

        Args:
            symbol: 期货品种代码

        Returns:
            pd.DataFrame: 日线数据
        """
        return ak.futures_zh_daily_sina(symbol=symbol)

    @staticmethod
    def get_positions(symbol: str) -> pd.DataFrame:
        """
        获取期货持仓排名

        Args:
            symbol: 期货品种

        Returns:
            pd.DataFrame: 持仓排名
        """
        return ak.futures_zh_position_sina(symbol=symbol)

    @staticmethod
    def get_continuous(symbol: str, contract: str = "当月") -> pd.DataFrame:
        """
        获取期货连续合约

        Args:
            symbol: 期货品种
            contract: 合约类型 (当月/下月/下季/隔季)

        Returns:
            pd.DataFrame: 连续合约数据
        """
        return ak.futures_zh_kline_sina(
            symbol=symbol,
            contract=contract
        )

    @staticmethod
    def get_receipt() -> pd.DataFrame:
        """获取期货仓单数据"""
        return ak.futures_zh_receipt()

    @staticmethod
    def get_financial_futures() -> pd.DataFrame:
        """获取金融期货行情 (IF/IC/IH/IM)"""
        return ak.futures_zh_spot(symbol="IF")
