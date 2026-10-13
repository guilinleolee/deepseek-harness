"""
Fincept Economic Data Client
宏观经济数据统一客户端
"""

import os
import sys
from typing import Optional, List, Dict, Any, Union

import pandas as pd

# 处理相对导入（当作为包使用时）
if __package__:
    from .providers.fred_provider import FredProvider
    from .providers.imf_provider import IMFProvider
    from .providers.worldbank_provider import WorldBankProvider
    from .providers.china_provider import ChinaProvider
else:
    # 直接运行时使用绝对导入
    from providers.fred_provider import FredProvider
    from providers.imf_provider import IMFProvider
    from providers.worldbank_provider import WorldBankProvider
    from providers.china_provider import ChinaProvider


class EconomicDataClient:
    """
    宏观经济数据统一客户端

    支持数据源:
    - FRED (美联储经济数据)
    - IMF (国际货币基金组织)
    - World Bank (世界银行)
    - 中国宏观数据 (PBoC/NBS)
    """

    def __init__(
        self,
        fred_api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
    ):
        """
        初始化经济数据客户端

        Args:
            fred_api_key: FRED API密钥，默认从环境变量FRED_API_KEY读取
            cache_dir: 缓存目录路径
        """
        # 初始化各数据源提供者
        self.fred: Optional[FredProvider] = None
        self.imf: Optional[IMFProvider] = None
        self.worldbank: Optional[WorldBankProvider] = None
        self.china: Optional[ChinaProvider] = None

        # 延迟初始化（检查依赖）
        self._initialized = False

        self.fred_api_key = fred_api_key or os.environ.get("FRED_API_KEY")
        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/fincept")

    def _ensure_init(self):
        """延迟初始化所有数据源"""
        if self._initialized:
            return

        # 初始化FRED
        if self.fred_api_key:
            try:
                self.fred = FredProvider(
                    api_key=self.fred_api_key,
                    cache_dir=self.cache_dir,
                )
            except ImportError as e:
                print(f"FRED provider not available: {e}")
            except Exception as e:
                print(f"Failed to initialize FRED: {e}")

        # 初始化IMF
        try:
            self.imf = IMFProvider(cache_dir=self.cache_dir)
        except ImportError as e:
            print(f"IMF provider not available: {e}")
        except Exception as e:
            print(f"Failed to initialize IMF: {e}")

        # 初始化World Bank
        try:
            self.worldbank = WorldBankProvider(cache_dir=self.cache_dir)
        except ImportError as e:
            print(f"World Bank provider not available: {e}")
        except Exception as e:
            print(f"Failed to initialize World Bank: {e}")

        # 初始化中国数据
        try:
            self.china = ChinaProvider(cache_dir=self.cache_dir)
        except Exception as e:
            print(f"Failed to initialize China provider: {e}")

        self._initialized = True

    # ==================== FRED接口 ====================

    def fred(self, indicator: str, **kwargs) -> Optional[float]:
        """
        获取FRED经济指标

        Args:
            indicator: 指标名称/代码 (如 "GDP", "UNRATE", "CPIAUCSL")
            **kwargs: 传递给FredProvider的参数

        Returns:
            最新指标值或时间序列DataFrame

        Example:
            client.fred("GDP")                    # 最新GDP
            client.fred("GDP", start_date="2020") # 2020年至今GDP
        """
        self._ensure_init()
        if not self.fred:
            print("FRED provider not available")
            return None
        return self.fred.fred(indicator, **kwargs)

    def fred_series(
        self,
        indicators: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        批量获取FRED指标

        Args:
            indicators: 指标列表
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame with date index and indicator columns
        """
        self._ensure_init()
        if not self.fred:
            return pd.DataFrame()
        return self.fred.fred_series(indicators, start_date, end_date)

    def interest_rates(self, country: str = "us") -> Optional[float]:
        """
        获取央行利率

        Args:
            country: 国家 (us/fed, eu/ecb, cn/pbc, jp/boj, uk/boe)

        Returns:
            当前利率
        """
        self._ensure_init()
        if not self.fred:
            return None
        return self.fred.interest_rates(country)

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
        self._ensure_init()
        if not self.fred:
            return pd.DataFrame()
        return self.fred.yield_curve(country, date)

    # ==================== 宏观经济接口 ====================

    def macro(
        self,
        country: str,
        indicator: str,
        year: Optional[str] = None,
    ) -> Optional[float]:
        """
        获取宏观经济指标

        Args:
            country: 国家代码 (us, cn, eu, jp, uk, etc.)
            indicator: 指标名称 (gdp, inflation, unemployment, etc.)
            year: 指定年份

        Returns:
            指标值
        """
        self._ensure_init()

        country = country.lower()

        # 中国数据
        if country in ("cn", "china"):
            if not self.china:
                return None
            return self.china.macro(country, indicator, year)

        # 通过FRED获取
        if self.fred:
            return self.fred.fred(indicator)

        return None

    def macro_gdp(
        self,
        country: str = "us",
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        获取GDP时间序列

        Args:
            country: 国家代码
            start_year: 开始年份
            end_year: 结束年份

        Returns:
            GDP时间序列DataFrame
        """
        self._ensure_init()

        country = country.lower()

        if country in ("cn", "china"):
            if not self.china:
                return pd.DataFrame()
            return self.china.get_series("CN_GDP")

        # 使用World Bank
        if self.worldbank:
            return self.worldbank.get_series(
                country.upper(),
                "NY.GDP.MKTP.CD",
                start_year,
                end_year,
            )

        return pd.DataFrame()

    def macro_inflation(
        self,
        country: str = "us",
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        获取通胀数据

        Args:
            country: 国家代码
            start_year: 开始年份
            end_year: 结束年份

        Returns:
            通胀时间序列DataFrame
        """
        self._ensure_init()

        country = country.lower()

        if country in ("cn", "china"):
            if not self.china:
                return pd.DataFrame()
            return self.china.get_series("CN_CPI")

        # 使用World Bank
        if self.worldbank:
            return self.worldbank.get_series(
                country.upper(),
                "FP.CPI.TOTL.ZG",
                start_year,
                end_year,
            )

        return pd.DataFrame()

    # ==================== IMF接口 ====================

    def imf(
        self,
        country: str,
        indicator: str,
        year: Optional[str] = None,
    ) -> Optional[float]:
        """
        获取IMF指标

        Args:
            country: 国家代码 (USA, CHN, etc.)
            indicator: 指标名称
            year: 指定年份

        Returns:
            指标值
        """
        self._ensure_init()
        if not self.imf:
            return None
        return self.imf.imf(country, indicator, year)

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
            DataFrame with date and value columns
        """
        self._ensure_init()
        if not self.imf:
            return pd.DataFrame()
        return self.imf.imf_series(country, indicators, start_date, end_date)

    def imf_bop(self, country: str) -> pd.DataFrame:
        """
        获取国际收支数据

        Args:
            country: 国家代码

        Returns:
            包含经常账户、金融账户等的DataFrame
        """
        self._ensure_init()
        if not self.imf:
            return pd.DataFrame()
        return self.imf.get_bop(country)

    # ==================== World Bank接口 ====================

    def worldbank(
        self,
        country: str,
        indicator: str,
        year: Optional[int] = None,
    ) -> Optional[float]:
        """
        获取World Bank指标

        Args:
            country: 国家代码
            indicator: 指标名称
            year: 指定年份

        Returns:
            指标值
        """
        self._ensure_init()
        if not self.worldbank:
            return None
        return self.worldbank.worldbank(country, indicator, year)

    def worldbank_series(
        self,
        country: str,
        indicators: List[str],
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        批量获取World Bank指标

        Args:
            country: 国家代码
            indicators: 指标列表
            start_year: 开始年份
            end_year: 结束年份

        Returns:
            DataFrame with date and value columns
        """
        self._ensure_init()
        if not self.worldbank:
            return pd.DataFrame()
        return self.worldbank.worldbank_series(
            country, indicators, start_year, end_year
        )

    # ==================== 工具方法 ====================

    def search_indicators(
        self,
        source: Optional[str] = None,
        keyword: str = "",
    ) -> List[Dict[str, str]]:
        """
        搜索经济指标

        Args:
            source: 数据源 (fred, imf, worldbank, china, all)
            keyword: 搜索关键词

        Returns:
            匹配指标列表
        """
        self._ensure_init()
        results = []

        if source is None or source == "all":
            sources = ["fred", "imf", "worldbank", "china"]
        else:
            sources = [source]

        if "fred" in sources and self.fred:
            # FRED搜索通过web search
            try:
                fred_results = self.fred.search(keyword, limit=10)
                for r in fred_results:
                    results.append({
                        "source": "FRED",
                        "id": r.get("id", ""),
                        "title": r.get("title", ""),
                    })
            except Exception:
                pass

        if "imf" in sources and self.imf:
            imf_results = self.imf.search_indicators(keyword)
            for r in imf_results:
                results.append({
                    "source": "IMF",
                    "id": r.get("code", r.get("id", "")),
                    "title": r.get("name", r.get("title", "")),
                })

        if "worldbank" in sources and self.worldbank:
            wb_results = self.worldbank.search_indicators(keyword)
            for r in wb_results:
                results.append({
                    "source": "World Bank",
                    "id": r.get("id", ""),
                    "title": r.get("name", ""),
                })

        if "china" in sources and self.china:
            china_results = self.china.search_indicators(keyword)
            for r in china_results:
                results.append({
                    "source": "China",
                    "id": r.get("code", ""),
                    "title": r.get("name", ""),
                })

        return results

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        获取仪表板关键经济指标

        Returns:
            包含主要经济指标的字典
        """
        self._ensure_init()
        data = {}

        # 美国数据
        if self.fred:
            data["us"] = {
                "gdp": self.fred.get_series_nowcast("GDP"),
                "unemployment": self.fred.get_series_nowcast("UNRATE"),
                "cpi": self.fred.get_series_nowcast("CPIAUCSL"),
                "fed_funds": self.fred.get_series_nowcast("FEDFUNDS"),
                "yield_10y": self.fred.get_series_nowcast("DGS10"),
                "m2": self.fred.get_series_nowcast("M2SL"),
            }

        # 中国数据
        if self.china:
            data["china"] = {
                "gdp": self.china.china("gdp"),
                "cpi": self.china.china("cpi"),
                "ppi": self.china.china("ppi"),
                "m2": self.china.china("m2"),
                "usdcny": self.china.china("usdcny"),
                "lpr": self.china.china("lpr_1y"),
            }

        return data

    def refresh(self, indicator: str):
        """
        手动刷新指标缓存

        Args:
            indicator: 指标名称
        """
        self._ensure_init()
        # 清除缓存，下次请求将重新获取
        if self.fred:
            self.fred._cache.clear()
        if self.imf:
            self.imf._cache.clear()
        if self.worldbank:
            self.worldbank._cache.clear()
        if self.china:
            self.china._cache.clear()

    def clear_cache(self):
        """清除所有缓存"""
        if self.fred:
            self.fred._cache.clear()
        if self.imf:
            self.imf._cache.clear()
        if self.worldbank:
            self.worldbank._cache.clear()
        if self.china:
            self.china._cache.clear()


# 便捷函数
def create_client(**kwargs) -> EconomicDataClient:
    """创建经济数据客户端"""
    return EconomicDataClient(**kwargs)
