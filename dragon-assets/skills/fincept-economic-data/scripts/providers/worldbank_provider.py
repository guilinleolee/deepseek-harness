"""
World Bank Provider - 世界银行数据
支持: 发展指标, GDP, 人口, 贸易等
"""

import os
from typing import Optional, List, Dict, Any

try:
    import wbdata
    import wbven
    WB_AVAILABLE = True
except ImportError:
    WB_AVAILABLE = False

import pandas as pd


class WorldBankProvider:
    """World Bank 世界银行数据提供者"""

    # 常用指标代码
    INDICATOR_MAP = {
        # GDP相关
        "gdp_usd": "NY.GDP.MKTP.CD",           # GDP (当前美元)
        "gdp_growth": "NY.GDP.MKTP.KD.ZG",    # GDP增长率
        "gdp_ppp": "NY.GDP.MKTP.PP.CD",        # GDP (PPP)
        "gdp_per_capita": "NY.GDP.PCAP.CD",    # 人均GDP
        "gdp_per_capita_ppp": "NY.GDP.PCAP.PP.CD",  # 人均GDP (PPP)
        "gni": "NY.GNP.MKTP.CD",              # GNI
        "gni_per_capita": "NY.GNP.PCAP.CD",    # 人均GNI
        # 人口
        "population": "SP.POP.TOTL",           # 总人口
        "population_growth": "SP.POP.GROW",    # 人口增长率
        "urban_population": "SP.URB.TOTL.IN.ZS",  # 城市人口占比
        # 贸易
        "exports": "NE.EXP.GNFS.ZS",          # 出口占GDP比例
        "imports": "NE.IMP.GNFS.ZS",          # 进口占GDP比例
        "trade": "TG.VAL.TOTL.GD.ZS",         # 贸易占GDP比例
        # 通胀
        "inflation": "FP.CPI.TOTL.ZG",        # 通胀率
        "core_inflation": "FP.CPI.TOTL.ZG",    # 核心通胀
        # 利率
        "real_interest": "FR.INR.RINR",       # 实际利率
        "lending_rate": "FR.INR.LEND",         # 贷款利率
        # 就业
        "unemployment": "SL.UEM.TOTL.ZS",      # 失业率
        "labor_force": "SL.TLF.TOTL.IN",       # 劳动力
        "employment": "SL.EMP.TOTL.SE.ZS",     # 就业率
        # 财政
        "government_debt": "GC.DOD.TOTL.GD.ZS",  # 政府债务
        "government_revenue": "GC.REV.XGTD.ZS",  # 政府收入
        "government_expenditure": "GC.XPN.TOTL.GD.ZS",  # 政府支出
        # 货币
        "money_supply": "FM.LBL.BMNY.GD.ZS",  # 广义货币占GDP
        # 外汇
        "foreign_exchange": "FI.RES.TOTL.CD",   # 外汇储备
        "external_debt": "DT.DOD.DECT.CD",     # 外债
        # 发展指标
        "life_expectancy": "SP.DYN.LE00.IN",  # 预期寿命
        "fertility_rate": "SP.DYN.TFRT.IN",    # 生育率
        "mortality_rate": "SP.DYN.IMRT.IN",    # 婴儿死亡率
        "poverty_rate": "SI.POV.DDAY",         # 极端贫困率
        "gini": "SI.POV.GINI",                # 基尼系数
        # 教育
        "school_enrollment": "SE.TEN.ENRR",    # 入学率
        "public_spending_education": "SE.XPD.TOTL.GD.ZS",  # 教育支出
        # 健康
        "health_spending": "SH.XPD.TOTL.ZS",  # 健康支出
        # 投资
        "gross_capital": "NE.GDI.TOTL.ZS",    # 总资本形成
        "foreign_direct_investment": "BX.KLT.DINV.CD.WD",  # FDI流入
        # 科技创新
        "patent_applications": "IP.PAT.NRES",  # 专利申请
        "research_spending": "GB.XPD.RSDV.ZS",  # 研发支出
    }

    def __init__(self, cache_dir: Optional[str] = None):
        """
        初始化World Bank提供者

        Args:
            cache_dir: 缓存目录路径
        """
        if not WB_AVAILABLE:
            raise ImportError("wbdata not installed. Run: pip install wbdata")

        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/fincept/worldbank")
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
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        获取World Bank时间序列数据

        Args:
            country: 国家代码 (如 "USA", "CHN", "WLD")
            indicator: 指标代码 (如 "NY.GDP.MKTP.CD")
            start_date: 开始年份
            end_date: 结束年份

        Returns:
            DataFrame with date and value columns
        """
        cache_key = f"{country}_{indicator}_{start_date}_{end_date}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            # 设置时间范围
            if start_date is None:
                start_date = 2000
            if end_date is None:
                end_date = 2024

            # 转换国家代码
            if country.upper() == "CN":
                country = "CHN"
            elif country.upper() == "UK":
                country = "GBR"
            elif country.upper() == "EU":
                country = "EUU"

            # 获取数据
            data_date = wbdata.dataframe(
                {indicator: indicator},
                country=country,
                data_date=range(start_date, end_date + 1),
            )

            if data_date is None or len(data_date) == 0:
                return pd.DataFrame(columns=["date", "value"])

            # 重置索引
            df = data_date.reset_index()
            df["date"] = pd.to_datetime(df["date"], format="%Y")
            df["value"] = df[indicator].astype(float)
            df = df[["date", "value"]]
            df = df.dropna()

            self._set_cache(cache_key, df)
            return df

        except Exception as e:
            print(f"Error fetching World Bank series {country}/{indicator}: {e}")
            return pd.DataFrame(columns=["date", "value"])

    def get_multiple_series(
        self,
        countries: List[str],
        indicator: str,
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        获取多个国家的同一指标

        Args:
            countries: 国家代码列表
            indicator: 指标代码
            start_date: 开始年份
            end_date: 结束年份

        Returns:
            DataFrame with date, country, value columns
        """
        result = None
        for country in countries:
            df = self.get_series(country, indicator, start_date, end_date)
            if len(df) > 0:
                df["country"] = country
                if result is None:
                    result = df
                else:
                    result = pd.concat([result, df])

        return result if result is not None else pd.DataFrame()

    def worldbank(
        self,
        country: str,
        indicator: str,
        year: Optional[int] = None,
    ) -> Optional[float]:
        """
        获取World Bank指标值

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
            year_df = df[df["date"].dt.year == year]
            if len(year_df) > 0:
                return year_df["value"].iloc[-1]

        return df["value"].iloc[-1] if len(df) > 0 else None

    def worldbank_series(
        self,
        country: str,
        indicators: List[str],
        start_date: Optional[int] = None,
        end_date: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        批量获取World Bank指标

        Args:
            country: 国家代码
            indicators: 指标列表
            start_date: 开始年份
            end_date: 结束年份

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

    def search_indicators(self, keyword: str) -> List[Dict[str, str]]:
        """
        搜索World Bank指标

        Args:
            keyword: 搜索关键词

        Returns:
            匹配指标列表
        """
        try:
            results = wbdata.get_indicatorsource(keyword)
            return [
                {"id": r["id"], "name": r.get("name", r["id"])}
                for r in results[:20]
            ]
        except Exception:
            # 简单本地搜索
            results = []
            keyword = keyword.lower()
            for name, code in self.INDICATOR_MAP.items():
                if keyword in name:
                    results.append({"id": code, "name": name})
            return results

    def get_country_list(self, income_level: Optional[str] = None) -> List[str]:
        """
        获取国家列表

        Args:
            income_level: 收入级别 (HIC=高收入, LIC=低收入, MIC=中等收入, LMC=中低收入, UMC=中高收入)

        Returns:
            国家代码列表
        """
        try:
            if income_level:
                countries = wbdata.get_income_level(income_level)
            else:
                countries = wbdata.get_country()
            return [c["id"] for c in countries]
        except Exception:
            return []

    def list_indicators(self) -> List[str]:
        """列出所有常用指标名称"""
        return list(self.INDICATOR_MAP.keys())
