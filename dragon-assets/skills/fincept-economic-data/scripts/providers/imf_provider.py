"""
IMF Provider - 国际货币基金组织数据
支持: 国际收支, 外汇储备, 金融账户, 汇率等
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    import pandas_datareader as pdr
    from pandas_datareader import data as web
    IMF_AVAILABLE = True
except ImportError:
    IMF_AVAILABLE = False

import pandas as pd


class IMFProvider:
    """IMF 国际货币基金组织数据提供者"""

    # IMF数据库代码
    DATABASE_CODES = {
        "bop": "BOP",      # 国际收支
        "fs": "FS",        # 金融统计
        "dot": "DOT",      # 贸易方向
        "cof": "COF",      # 投资头寸
        "css": "CSS",      # 证券统计
        " IES": "IES",      # 国际收支服务
        "bdp": "BDP",      # 国际存款利率
    }

    # 常用指标
    INDICATOR_MAP = {
        # 国际收支 (BOP)
        "current_account": "BNCABFGA",
        "goods_export": "TXGFGA",
        "goods_import": "TMGFGA",
        "services_export": "TXSFGA",
        "services_import": "TMSFGA",
        "primary_income": "PYGFGA",
        "secondary_income": "ISYRFGA",
        # 金融账户 (Financial Account)
        "direct_investment": "DIAGFGA",
        "portfolio_investment": "PIGGFGA",
        "other_investment": "OIGGFGA",
        "reserve_assets": "RAGGFGA",
        # 外汇储备
        "total_reserves": "TRESVA",
        "foreign_exchange": "FXRESVA",
        "gold": "GOLDAMNA",
        "special_drawing": "SDRGAMNA",
    }

    def __init__(self, cache_dir: Optional[str] = None):
        """
        初始化IMF提供者

        Args:
            cache_dir: 缓存目录路径
        """
        if not IMF_AVAILABLE:
            raise ImportError("pandas-datareader not installed. Run: pip install pandas-datareader")

        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/fincept/imf")
        os.makedirs(self.cache_dir, exist_ok=True)
        self._cache: Dict[str, tuple] = {}

    def _get_cached(self, key: str, cache_hours: int = 24) -> Optional[pd.DataFrame]:
        """获取缓存数据"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if (datetime.now() - timestamp).total_seconds() < cache_hours * 3600:
                return data
        return None

    def _set_cache(self, key: str, data: pd.DataFrame):
        """设置缓存"""
        self._cache[key] = (data, datetime.now())

    def get_series(
        self,
        country: str,
        indicator: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        freq: str = "Q",
    ) -> pd.DataFrame:
        """
        获取IMF时间序列数据

        Args:
            country: 国家代码 (ISO 3-letter, 如 "USA", "CHN")
            indicator: 指标代码 (如 "BNCABFGA" 经常账户)
            start_date: 开始日期
            end_date: 结束日期
            freq: 数据频率 (A=年, Q=季度, M=月)

        Returns:
            DataFrame with date and value columns
        """
        cache_key = f"{country}_{indicator}_{freq}_{start_date}_{end_date}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            # 构建FRED数据源格式
            # IMF数据通过FRED API访问
            symbol = f"{country}_{indicator}"

            start = pd.to_datetime(start_date) if start_date else pd.Timestamp("2010-01-01")
            end = pd.to_datetime(end_date) if end_date else pd.Timestamp.now()

            df = web.DataReader(
                symbol,
                "fred",
                start,
                end,
            )

            df = df.reset_index()
            df.columns = ["date", "value"]
            df = df.dropna()

            self._set_cache(cache_key, df)
            return df

        except Exception as e:
            print(f"Error fetching IMF series {country}/{indicator}: {e}")
            return pd.DataFrame(columns=["date", "value"])

    def get_bop(
        self,
        country: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        获取国际收支数据

        Args:
            country: 国家代码 (USA, CHN, JPN, DEU, etc.)
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            包含经常账户、资本账户、金融账户的DataFrame
        """
        indicators = [
            "BNCABFGA",  # 经常账户余额
            "BGNFABFGA", # 资本账户
            "BNFAGFGA",  # 金融账户
            "DIAGFGA",   # 直接投资
            "PIGGFGA",   # 证券投资
            "OIGGFGA",   # 其他投资
            "RAGGFGA",   # 储备资产
        ]

        result = None
        for ind in indicators:
            df = self.get_series(country, ind, start_date, end_date)
            if len(df) > 0:
                df = df.rename(columns={"value": ind})
                if result is None:
                    result = df
                else:
                    result = result.merge(df, on="date", how="outer")

        return result if result is not None else pd.DataFrame()

    def get_reserves(
        self,
        country: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        获取外汇储备数据

        Returns:
            DataFrame with total reserves, gold, FX, SDR
        """
        indicators = {
            "total_reserves": "TRESVA",
            "gold": "GOLDAMNA",
            "special_drawing": "SDRGAMNA",
        }

        result = None
        for name, ind in indicators.items():
            df = self.get_series(country, ind, start_date, end_date)
            if len(df) > 0:
                df = df.rename(columns={"value": name})
                if result is None:
                    result = df
                else:
                    result = result.merge(df, on="date", how="outer")

        return result if result is not None else pd.DataFrame()

    def imf(
        self,
        country: str,
        indicator: str,
        year: Optional[str] = None,
    ) -> Optional[float]:
        """
        获取IMF指标最新值

        Args:
            country: 国家代码
            indicator: 指标名称 (支持别名)
            year: 指定年份

        Returns:
            最新值或指定年份值
        """
        symbol = self.INDICATOR_MAP.get(indicator.lower(), indicator)

        df = self.get_series(country, symbol)
        if len(df) == 0:
            return None

        if year:
            year_df = df[df["date"].dt.year == int(year)]
            if len(year_df) > 0:
                return year_df["value"].iloc[-1]

        return df["value"].iloc[-1] if len(df) > 0 else None

    def imf_series(
        self,
        country: str,
        indicators: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        批量获取IMF指标

        Args:
            country: 国家代码
            indicators: 指标列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame with date index and indicator columns
        """
        result = None
        for indicator in indicators:
            symbol = self.INDICATOR_MAP.get(indicator.lower(), indicator)
            df = self.get_series(country, symbol, start_date, end_date)
            if len(df) > 0:
                df = df.rename(columns={"value": indicator})
                if result is None:
                    result = df
                else:
                    result = result.merge(df, on="date", how="outer")

        return result if result is not None else pd.DataFrame()

    def list_indicators(self, database: str = "bop") -> List[str]:
        """列出指定数据库的可用指标"""
        return list(self.INDICATOR_MAP.keys())

    def search_indicators(self, keyword: str) -> List[Dict[str, str]]:
        """搜索IMF指标"""
        results = []
        keyword = keyword.lower()
        for name, code in self.INDICATOR_MAP.items():
            if keyword in name:
                results.append({"name": name, "code": code})
        return results
