"""
宏观数据提供者
封装 AkShare 宏观数据接口
"""

import pandas as pd

try:
    import akshare as ak
except ImportError:
    raise ImportError("akshare 未安装，请运行: pip install akshare>=1.14.0")


class MacroProvider:
    """宏观数据提供者"""

    @staticmethod
    def get_cpi() -> pd.DataFrame:
        """
        获取中国 CPI 月度数据

        Returns:
            pd.DataFrame: CPI 数据
        """
        return ak.macro_china_cpi()

    @staticmethod
    def get_gdp() -> pd.DataFrame:
        """
        获取中国 GDP 季度数据

        Returns:
            pd.DataFrame: GDP 数据
        """
        return ak.macro_china_gdp()

    @staticmethod
    def get_ppi() -> pd.DataFrame:
        """
        获取中国 PPI 月度数据

        Returns:
            pd.DataFrame: PPI 数据
        """
        return ak.macro_china_ppi()

    @staticmethod
    def get_money_supply() -> pd.DataFrame:
        """
        获取货币供应量 M0/M1/M2

        Returns:
            pd.DataFrame: 货币供应量数据
        """
        return ak.macro_china_money_supply()

    @staticmethod
    def get_shibor() -> pd.DataFrame:
        """获取上海银行间同业拆借利率"""
        return ak.macro_china_shibor()

    @staticmethod
    def get_loan_rate() -> pd.DataFrame:
        """获取贷款市场报价利率 LPR"""
        return ak.macro_china_loan_rate()

    @staticmethod
    def get_fx_reserves() -> pd.DataFrame:
        """获取外汇储备"""
        return ak.macro_china_fx_reserves()

    @staticmethod
    def get_trade_balance() -> pd.DataFrame:
        """获取贸易顺差数据"""
        return ak.macro_china_trade_balance()
