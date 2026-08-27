"""
FRED Provider - 美联储经济数据
文档: https://fred.stlouisfed.org/docs/api/fred/
"""

import os
import time
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

try:
    from fredapi import Fred
    FRED_AVAILABLE = True
except ImportError:
    FRED_AVAILABLE = False

import pandas as pd


class FredProvider:
    """FRED 美联储经济数据提供者"""

    # FRED常用指标映射
    INDICATOR_MAP = {
        # 增长指标
        "gdp": "GDP",
        "gnp": "GNP",
        "gni": "GNI",
        "ngdp": "NGDPD",
        "current_account": "NETCIV",
        # 通胀指标
        "cpi": "CPIAUCSL",
        "ppi": "PPIFGS",
        "pce": "PCEPI",
        "core_pce": "CORESTICKM037S",
        "core_cpi": "CPILFESL",
        # 就业指标
        "unemployment": "UNRATE",
        "payrolls": "PAYEMS",
        "labor_participation": "CIVPART",
        "job_openings": "JTSJOL",
        "initial_claims": "ICSA",
        # 利率指标
        "fed_funds": "FEDFUNDS",
        "prime_rate": "PRIME",
        "libor_3m": "USD3MTD156N",
        "yield_2y": "DGS2",
        "yield_5y": "DGS5",
        "yield_10y": "DGS10",
        "yield_30y": "DGS30",
        # 货币指标
        "m1": "M1SL",
        "m2": "M2SL",
        "m2_velocity": "M2V",
        "total_credit": "TCREDIT",
        "commercial_loans": "BUSLOANS",
        # 贸易指标
        "exports": "EXPGSC1",
        "imports": "IMPGSC1",
        "trade_balance": "BOPGSTB",
        "current_account": "CURRENTACCOUNT",
        # 消费者指标
        "consumer_sentiment": "UMCSENT",
        "retail_sales": "RSXFS",
        "pce_consumer": "PCECTPI",
        # 房地产指标
        "housing_starts": "HOUST",
        "home_price": "CSUSHPINSA",
        "mortgage_rate_30y": "MORTGAGE30US",
        # 股票市场
        "sp500": "SP500",
        "vix": "VIXCLS",
        # 工业指标
        "ism_manufacturing": "MANEMP",
        "industrial_production": "INDPRO",
        "capacity_utilization": "CAPUTIL",
        "durables_orders": "DGORDER",
    }

    def __init__(self, api_key: Optional[str] = None, cache_dir: Optional[str] = None):
        """
        初始化FRED提供者

        Args:
            api_key: FRED API密钥，默认从环境变量FRED_API_KEY读取
            cache_dir: 缓存目录路径
        """
        if not FRED_AVAILABLE:
            raise ImportError("fredapi not installed. Run: pip install fredapi")

        self.api_key = api_key or os.environ.get("FRED_API_KEY")
        if not self.api_key:
            raise ValueError("FRED API key required. Set FRED_API_KEY environment variable.")

        self.fred = Fred(api_key=self.api_key)
        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/fincept/fred")
        os.makedirs(self.cache_dir, exist_ok=True)
        self._cache: Dict[str, tuple] = {}  # symbol -> (data, timestamp)

    def _get_cached(self, symbol: str, cache_hours: int = 1) -> Optional[pd.DataFrame]:
        """获取缓存数据"""
        if symbol in self._cache:
            data, timestamp = self._cache[symbol]
            if (datetime.now() - timestamp).total_seconds() < cache_hours * 3600:
                return data
        return None

    def _set_cache(self, symbol: str, data: pd.DataFrame):
        """设置缓存"""
        self._cache[symbol] = (data, datetime.now())

    def get_series(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: Optional[str] = None,
        aggregation_method: Optional[str] = "Average",
        units: Optional[str] = "lin",
    ) -> pd.DataFrame:
        """
        获取FRED时间序列数据

        Args:
            symbol: FRED指标代码 (如 "GDP", "UNRATE")
            start_date: 开始日期 (如 "2020-01-01")
            end_date: 结束日期
            frequency: 数据频率 (a=年, q=季度, m=月, w=周, d=日)
            aggregation_method: 聚合方法 (Average, Sum, End of Period)
            units: 单位 (lin=水平值, chg=变化, ch1=百分比变化, etc.)

        Returns:
            DataFrame with columns: date, value
        """
        # 检查缓存
        cache_key = f"{symbol}_{start_date}_{end_date}_{frequency}_{units}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            # 获取数据
            obs = self.fred.get_series(
                symbol,
                observation_start=start_date,
                observation_end=end_date,
                frequency=frequency,
                aggregation_method=aggregation_method,
                units=units,
            )

            if obs is None or len(obs) == 0:
                return pd.DataFrame(columns=["date", "value"])

            # 转换为DataFrame
            df = pd.DataFrame({
                "date": pd.to_datetime(obs.index),
                "value": obs.values
            })
            df = df.dropna()

            self._set_cache(cache_key, df)
            return df

        except Exception as e:
            print(f"Error fetching FRED series {symbol}: {e}")
            return pd.DataFrame(columns=["date", "value"])

    def search(self, text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        搜索FRED指标

        Args:
            text: 搜索关键词
            limit: 返回结果数量

        Returns:
            指标列表，每项包含id, title, units, frequency
        """
        try:
            results = self.fred.search(text, limit=limit)
            return results.to_dict("records")
        except Exception as e:
            print(f"Error searching FRED: {e}")
            return []

    def get_category(self, category_id: int) -> List[str]:
        """获取分类下的所有指标"""
        try:
            return self.fred.get_category(category_id)
        except Exception as e:
            print(f"Error fetching FRED category {category_id}: {e}")
            return []

    def get_releases(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近发布的经济数据"""
        try:
            releases = self.fred.get_releases(limit=limit)
            return releases.to_dict("records")
        except Exception as e:
            print(f"Error fetching FRED releases: {e}")
            return []

    def get_series_nowcast(self, symbol: str) -> Optional[float]:
        """获取最新值"""
        try:
            return self.fred.get_series_latest_release(symbol)
        except Exception:
            return None

    def fred(
        self,
        indicator: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[float]:
        """
        获取最新经济指标值

        Args:
            indicator: 指标名称 (支持别名映射)
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            最新值或时间序列DataFrame
        """
        # 映射指标别名
        symbol = self.INDICATOR_MAP.get(indicator.lower(), indicator)

        if start_date is None and end_date is None:
            # 返回最新值
            return self.get_series_nowcast(symbol)
        else:
            # 返回时间序列
            return self.get_series(symbol, start_date=start_date, end_date=end_date)

    def fred_series(
        self,
        indicators: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        批量获取多个指标

        Args:
            indicators: 指标列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame with date index and indicator columns
        """
        result = None
        for indicator in indicators:
            symbol = self.INDICATOR_MAP.get(indicator.lower(), indicator)
            df = self.get_series(symbol, start_date=start_date, end_date=end_date)
            if len(df) > 0:
                df = df.rename(columns={"value": symbol})
                if result is None:
                    result = df
                else:
                    result = result.merge(df, on="date", how="outer")

        return result if result is not None else pd.DataFrame()

    def interest_rates(self, country: str = "us") -> Optional[float]:
        """
        获取央行利率

        Args:
            country: 国家代码 (us, eu, cn, jp, uk)

        Returns:
            当前利率
        """
        rate_map = {
            "us": "FEDFUNDS",
            "fed": "FEDFUNDS",
            "eu": "ECBDFR",
            "ecb": "ECBDFR",
            "cn": "ChinaIntRate",
            "pbc": "ChinaIntRate",
            "jp": "JapanPolicyRate",
            "boj": "JapanPolicyRate",
            "uk": "UKBaseRate",
            "boe": "UKBaseRate",
        }
        symbol = rate_map.get(country.lower())
        if symbol:
            return self.get_series_nowcast(symbol)
        return None

    def yield_curve(
        self,
        country: str = "us",
        date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        获取国债收益率曲线

        Args:
            country: 国家代码
            date: 指定日期

        Returns:
            DataFrame with tenor and yield columns
        """
        if country.lower() in ("us", "united_states"):
            tenors = {
                "1M": "DGS1MO",
                "3M": "DGS3MO",
                "6M": "DGS6MO",
                "1Y": "DGS1",
                "2Y": "DGS2",
                "3Y": "DGS3",
                "5Y": "DGS5",
                "7Y": "DGS7",
                "10Y": "DGS10",
                "20Y": "DGS20",
                "30Y": "DGS30",
            }
        else:
            return pd.DataFrame()

        result = []
        end_date = date or datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        for tenor, symbol in tenors.items():
            df = self.get_series(symbol, start_date=start_date, end_date=end_date)
            if len(df) > 0:
                result.append({
                    "tenor": tenor,
                    "yield": df["value"].iloc[-1]
                })

        return pd.DataFrame(result)

    def economic_calendar(self) -> List[Dict[str, Any]]:
        """获取FRED经济日历（即将发布的数据）"""
        try:
            return self.fred.get_series_updates(limit=20)
        except Exception:
            return []
