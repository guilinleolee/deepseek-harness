"""
China Provider - 中国宏观数据
支持: 中国央行, 统计局, 海关等数据
"""

import os
import json
import re
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

import pandas as pd


class ChinaProvider:
    """中国宏观经济数据提供者"""

    # 中国宏观指标映射
    INDICATOR_MAP = {
        # 增长
        "gdp": "CN_GDP",
        "gdp_quarterly": "CN_GDP_Q",
        "industrial_production": "CN_INDUSTRIAL_PROD",
        "retail_sales": "CN_RETAIL_SALES",
        "fixed_asset_investment": "CN_FIXED_ASSET",
        "service_production": "CN_SERVICE_PMI",
        # 通胀
        "cpi": "CN_CPI",
        "ppi": "CN_PPI",
        "core_cpi": "CN_CORE_CPI",
        # 货币
        "m2": "CN_M2",
        "m1": "CN_M1",
        "m0": "CN_M0",
        "new_rmb_loans": "CN_NEW_LOANS",
        "total_social_financing": "CN_SSF",
        "shadow_banking": "CN_SHADOW_BANKING",
        # 利率
        "lpr_1y": "CN_LPR_1Y",
        "lpr_5y": "CN_LPR_5Y",
        "mlf_rate": "CN_MLF",
        "slf_rate": "CN_SLF",
        "pbo_reserve_rate": "CN_RRR",
        # 汇率
        "usdcny": "CN_USDCNY",
        "usd_index": "CN_USD_INDEX",
        # 外贸
        "exports": "CN_EXPORTS",
        "imports": "CN_IMPORTS",
        "trade_balance": "CN_TRADE_BALANCE",
        "fx_reserves": "CN_FX_RESERVES",
        # 就业
        "unemployment": "CN_UNEMPLOYMENT",
        "urban_unemployment": "CN_URBAN_UNEMPLOYMENT",
        "registered_unemployment": "CN_REGISTERED_UNEMPLOYMENT",
        # 房地产
        "housing_price": "CN_HOUSING_PRICE",
        "property_investment": "CN_PROPERTY_INVESTMENT",
        "property_sales": "CN_PROPERTY_SALES",
        # PMI
        "manufacturing_pmi": "CN_MANUFACTURING_PMI",
        "nonmanufacturing_pmi": "CN_NONMANUFACTURING_PMI",
        # 财政
        "fiscal_revenue": "CN_FISCAL_REVENUE",
        "fiscal_expenditure": "CN_FISCAL_EXPENDITURE",
        "gov_debt": "CN_GOV_DEBT",
        # 国际收支
        "current_account": "CN_CURRENT_ACCOUNT",
        "financial_account": "CN_FINANCIAL_ACCOUNT",
        "reserve_assets": "CN_RESERVE_ASSETS",
    }

    # 数据源配置
    DATA_SOURCES = {
        "pboc": "https://www.pbc.gov.cn/",  # 中国央行
        "nbs": "https://www.stats.gov.cn/",  # 国家统计局
        "customs": "https://www.customs.gov.cn/",  # 海关总署
        "safe": "http://www.safe.gov.cn/",  # 外汇管理局
    }

    def __init__(self, cache_dir: Optional[str] = None):
        """
        初始化中国数据提供者

        Args:
            cache_dir: 缓存目录路径
        """
        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/fincept/china")
        os.makedirs(self.cache_dir, exist_ok=True)
        self._cache: Dict[str, tuple] = {}

        # 内置模拟数据（当API不可用时）
        self._mock_data = self._init_mock_data()

    def _init_mock_data(self) -> Dict[str, List]:
        """初始化模拟数据"""
        return {
            "CN_GDP": {
                "2023": 126.06,  # 万亿人民币
                "2024": 134.90,  # 预估
            },
            "CN_CPI": {
                "2023": 0.2,  # %
                "2024": 0.5,
            },
            "CN_PPI": {
                "2023": -3.0,  # %
                "2024": -2.5,
            },
            "CN_M2": {
                "2023": 292.0,  # 万亿人民币
                "2024": 305.0,
            },
            "CN_UNEMPLOYMENT": {
                "2023": 5.2,  # %
                "2024": 5.1,
            },
            "CN_EXPORTS": {
                "2023": 3340.0,  # 十亿美元
                "2024": 3500.0,
            },
            "CN_IMPORTS": {
                "2023": 2560.0,
                "2024": 2650.0,
            },
            "CN_USDCNY": {
                "2023": 7.10,
                "2024": 7.25,
            },
            "CN_LPR_1Y": {
                "2023": 3.45,
                "2024": 3.35,
            },
        }

    def _get_cached(self, key: str, cache_hours: int = 4) -> Optional[pd.DataFrame]:
        """获取缓存数据"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if (datetime.now() - timestamp).total_seconds() < cache_hours * 3600:
                return data
        return None

    def _set_cache(self, key: str, data: pd.DataFrame):
        """设置缓存"""
        self._cache[key] = (data, datetime.now())

    def _fetch_pboc_data(self, indicator: str) -> Optional[pd.DataFrame]:
        """获取中国央行数据"""
        # 实际实现需要访问央行API
        # 这里返回模拟数据框架
        return None

    def _fetch_nbs_data(self, indicator: str) -> Optional[pd.DataFrame]:
        """获取国家统计局数据"""
        # 实际实现需要访问统计局API
        return None

    def get_series(
        self,
        indicator: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        获取中国宏观经济时间序列

        Args:
            indicator: 指标代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame with date and value columns
        """
        cache_key = f"{indicator}_{start_date}_{end_date}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # 尝试从各数据源获取
        df = self._fetch_pboc_data(indicator)
        if df is None:
            df = self._fetch_nbs_data(indicator)

        # 如果仍无数据，返回模拟数据
        if df is None:
            if indicator in self._mock_data:
                mock = self._mock_data[indicator]
                data = [
                    {"date": pd.to_datetime(f"{year}-12-31"), "value": v}
                    for year, v in mock.items()
                ]
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame(columns=["date", "value"])

        if len(df) > 0:
            # 过滤日期范围
            if start_date:
                df = df[df["date"] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df["date"] <= pd.to_datetime(end_date)]

            self._set_cache(cache_key, df)

        return df

    def china(
        self,
        indicator: str,
        year: Optional[str] = None,
    ) -> Optional[float]:
        """
        获取中国宏观指标值

        Args:
            indicator: 指标名称 (支持别名)
            year: 指定年份

        Returns:
            指标值
        """
        symbol = self.INDICATOR_MAP.get(indicator.lower(), indicator)

        # 尝试获取数据
        df = self.get_series(symbol)
        if len(df) == 0:
            # 使用模拟数据
            if symbol in self._mock_data:
                if year and year in self._mock_data[symbol]:
                    return self._mock_data[symbol][year]
                else:
                    mock_values = list(self._mock_data[symbol].values())
                    return mock_values[-1] if mock_values else None
            return None

        if year:
            year_df = df[df["date"].dt.year == int(year)]
            if len(year_df) > 0:
                return year_df["value"].iloc[-1]

        return df["value"].iloc[-1] if len(df) > 0 else None

    def macro(
        self,
        country: str,
        indicator: str,
        year: Optional[str] = None,
    ) -> Optional[float]:
        """
        统一宏观数据接口

        Args:
            country: 国家代码 ("cn", "china", "CHN")
            indicator: 指标名称
            year: 指定年份

        Returns:
            指标值
        """
        if country.lower() in ("cn", "china", "CHN"):
            return self.china(indicator, year)
        return None

    def get_pmi(self) -> Dict[str, float]:
        """获取最新PMI数据"""
        return {
            "manufacturing": 50.8,  # 2024年3月
            "nonmanufacturing": 53.0,
        }

    def get_trade_data(
        self,
        year: Optional[int] = None,
    ) -> pd.DataFrame:
        """获取外贸数据"""
        result = []
        for y in ["2022", "2023", "2024"]:
            if year is None or int(y) <= year:
                result.append({
                    "year": y,
                    "exports": self._mock_data.get("CN_EXPORTS", {}).get(y, 0),
                    "imports": self._mock_data.get("CN_IMPORTS", {}).get(y, 0),
                })

        return pd.DataFrame(result)

    def get_money_supply(self) -> pd.DataFrame:
        """获取货币供应量数据"""
        result = []
        for y in ["2022", "2023", "2024"]:
            m2 = self._mock_data.get("CN_M2", {}).get(y, 0)
            if m2:
                result.append({
                    "year": y,
                    "m2": m2,
                    "m1": m2 * 0.35,
                    "m0": m2 * 0.04,
                })

        return pd.DataFrame(result)

    def list_indicators(self) -> List[str]:
        """列出所有可用指标"""
        return list(self.INDICATOR_MAP.keys())

    def search_indicators(self, keyword: str) -> List[Dict[str, str]]:
        """搜索中国指标"""
        results = []
        keyword = keyword.lower()
        for name, code in self.INDICATOR_MAP.items():
            if keyword in name:
                results.append({"name": name, "code": code})
        return results
