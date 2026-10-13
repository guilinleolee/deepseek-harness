"""
Fincept China Market - 主客户端
封装 AkShare 的中国市场数据能力
"""

import time
import os
import json
from datetime import datetime
from typing import Union, List, Optional, Dict, Any
import pandas as pd

# AkShare 封装
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("警告: akshare 未安装，请运行: pip install akshare>=1.14.0")


class FinceptError(Exception):
    """Fincept 数据获取错误"""
    pass


class ChinaMarketClient:
    """
    中国市场数据客户端

    支持: A股、期货、期权、债券、基金、宏观、加密货币
    """

    def __init__(self, cache: bool = True, cache_dir: str = "/tmp/fincept_cache",
                 request_delay: float = 0.5):
        """
        初始化客户端

        Args:
            cache: 是否启用缓存
            cache_dir: 缓存目录
            request_delay: 请求间隔(秒)，避免高频被封
        """
        self.cache = cache
        self.cache_dir = cache_dir
        self.request_delay = request_delay
        self._cache: Dict[str, Any] = {}

        if cache and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)

        if not AKSHARE_AVAILABLE:
            raise FinceptError("akshare 未安装，请运行: pip install akshare>=1.14.0")

    def _request(self, key: str, fetch_func, *args, **kwargs) -> pd.DataFrame:
        """
        统一的请求方法，支持缓存和延迟

        Args:
            key: 缓存键
            fetch_func: 数据获取函数
            *args, **kwargs: 传递给 fetch_func 的参数

        Returns:
            pd.DataFrame: 数据结果
        """
        # 检查缓存
        if self.cache and key in self._cache:
            cache_time, data = self._cache[key]
            if time.time() - cache_time < 300:  # 5分钟缓存
                return data

        # 获取数据
        try:
            time.sleep(self.request_delay)  # 请求延迟
            result = fetch_func(*args, **kwargs)

            if isinstance(result, pd.DataFrame):
                # 缓存结果
                if self.cache:
                    self._cache[key] = (time.time(), result)
                return result
            else:
                raise FinceptError(f"数据类型错误: {type(result)}")

        except Exception as e:
            raise FinceptError(f"数据获取失败 [{key}]: {str(e)}")

    # ==================== A股市场 ====================

    def realtime(self, symbol: Union[str, List[str]]) -> pd.DataFrame:
        """
        获取 A 股实时行情

        Args:
            symbol: 股票代码或代码列表 (如 "000001" 或 ["000001", "600000"])

        Returns:
            pd.DataFrame: 实时行情数据
        """
        if isinstance(symbol, list):
            symbol = ",".join(symbol)

        cache_key = f"realtime_{symbol}"
        return self._request(cache_key, ak.stock_zh_a_spot_em, symbol=symbol)

    def kline(self, symbol: str, period: str = "daily",
              start_date: Optional[str] = None, end_date: Optional[str] = None,
              adjust: str = "") -> pd.DataFrame:
        """
        获取 A 股历史 K 线

        Args:
            symbol: 股票代码 (如 "000001")
            period: K线周期 (daily/weekly/monthly)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            adjust: 复权类型 ("qfq"/"hfq"/"")

        Returns:
            pd.DataFrame: K线数据
        """
        # 转换周期
        period_map = {"daily": "日", "weekly": "周", "monthly": "月"}
        period_cn = period_map.get(period, "日")

        cache_key = f"kline_{symbol}_{period}_{start_date}_{end_date}_{adjust}"
        return self._request(cache_key, ak.stock_zh_a_hist,
                            symbol=symbol, period=period_cn,
                            start_date=start_date, end_date=end_date,
                            adjust=adjust)

    def financial(self, symbol: str) -> Dict[str, pd.DataFrame]:
        """
        获取 A 股财务报表

        Args:
            symbol: 股票代码

        Returns:
            Dict: 包含利润表、资产负债表、现金流量表
        """
        result = {}

        # 利润表
        cache_key = f"financial_profit_{symbol}"
        result["profit"] = self._request(cache_key,
            ak.stock_profit_sheet_by_report_em, symbol=symbol)

        # 资产负债表
        cache_key = f"financial_balance_{symbol}"
        result["balance"] = self._request(cache_key,
            ak.stock_balance_sheet_by_report_em, symbol=symbol)

        # 现金流量表
        cache_key = f"financial_cashflow_{symbol}"
        result["cashflow"] = self._request(cache_key,
            ak.stock_cash_flow_sheet_by_report_em, symbol=symbol)

        return result

    def indicator(self, symbol: str) -> pd.DataFrame:
        """
        获取 A 股财务指标

        Args:
            symbol: 股票代码

        Returns:
            pd.DataFrame: 财务指标 (PE、PB、ROE 等)
        """
        cache_key = f"indicator_{symbol}"
        return self._request(cache_key,
            ak.stock_financial_analysis_indicator, symbol=symbol)

    def balance(self, symbol: str) -> pd.DataFrame:
        """获取资产负债表"""
        cache_key = f"balance_{symbol}"
        return self._request(cache_key,
            ak.stock_balance_sheet_by_report_em, symbol=symbol)

    def cashflow(self, symbol: str) -> pd.DataFrame:
        """获取现金流量表"""
        cache_key = f"cashflow_{symbol}"
        return self._request(cache_key,
            ak.stock_cash_flow_sheet_by_report_em, symbol=symbol)

    def profit(self, symbol: str) -> pd.DataFrame:
        """获取利润表"""
        cache_key = f"profit_{symbol}"
        return self._request(cache_key,
            ak.stock_profit_sheet_by_report_em, symbol=symbol)

    # ==================== 期货市场 ====================

    def futures(self, symbol: str) -> pd.DataFrame:
        """
        获取期货行情

        Args:
            symbol: 期货品种 (如 "IF", "IC", "IH", "IM", "CU", "AL")

        Returns:
            pd.DataFrame: 期货行情
        """
        cache_key = f"futures_{symbol}"
        return self._request(cache_key,
            ak.futures_zh_daily_sina, symbol=symbol)

    def futures_spot(self) -> pd.DataFrame:
        """获取商品期货实时行情"""
        cache_key = "futures_spot_all"
        return self._request(cache_key, ak.futures_zh_spot)

    def futures_positions(self, symbol: str) -> pd.DataFrame:
        """
        获取期货持仓排名

        Args:
            symbol: 期货品种

        Returns:
            pd.DataFrame: 持仓排名
        """
        cache_key = f"futures_positions_{symbol}"
        return self._request(cache_key,
            ak.futures_zh_position_sina, symbol=symbol)

    # ==================== 期权市场 ====================

    def options_50etf(self) -> pd.DataFrame:
        """获取 50ETF 期权数据"""
        cache_key = "options_50etf"
        return self._request(cache_key, ak.option_50etf_spot)

    def options_300(self) -> pd.DataFrame:
        """获取沪深 300 期权数据"""
        cache_key = "options_300"
        return self._request(cache_key, ak.option_300_spot)

    # ==================== 债券市场 ====================

    def bond(self) -> pd.DataFrame:
        """获取国债实时行情"""
        cache_key = "bond_zh_spot"
        return self._request(cache_key, ak.bond_zh_cibm_spot)

    def corporate_bond(self) -> pd.DataFrame:
        """获取企业债数据"""
        cache_key = "corporate_bond"
        return self._request(cache_key, ak.bond_zh_em_spot)

    # ==================== 基金市场 ====================

    def fund(self, symbol: str, period: str = "daily",
             start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取基金历史数据

        Args:
            symbol: 基金代码 (如 "510300" 沪深300ETF)
            period: K线周期
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            pd.DataFrame: 基金历史数据
        """
        cache_key = f"fund_{symbol}_{period}_{start_date}_{end_date}"
        return self._request(cache_key,
            ak.fund_etf_hist_sina, symbol=symbol, period=period,
            start_date=start_date, end_date=end_date)

    def fund_nav(self, symbol: str) -> pd.DataFrame:
        """
        获取基金净值数据

        Args:
            symbol: 基金代码

        Returns:
            pd.DataFrame: 基金净值
        """
        cache_key = f"fund_nav_{symbol}"
        return self._request(cache_key, ak.fund_open_fund_info, fund=symbol)

    def fund_list(self) -> pd.DataFrame:
        """获取公募基金列表"""
        cache_key = "fund_list_all"
        return self._request(cache_key, ak.fund_open_fund_info_em)

    # ==================== 宏观数据 ====================

    def macro_cpi(self) -> pd.DataFrame:
        """获取中国 CPI 月度数据"""
        cache_key = "macro_cpi"
        return self._request(cache_key, ak.macro_china_cpi)

    def macro_gdp(self) -> pd.DataFrame:
        """获取中国 GDP 季度数据"""
        cache_key = "macro_gdp"
        return self._request(cache_key, ak.macro_china_gdp)

    def macro_ppi(self) -> pd.DataFrame:
        """获取中国 PPI 月度数据"""
        cache_key = "macro_ppi"
        return self._request(cache_key, ak.macro_china_ppi)

    def money_supply(self) -> pd.DataFrame:
        """获取货币供应量 M0/M1/M2"""
        cache_key = "money_supply"
        return self._request(cache_key, ak.macro_china_money_supply)

    def social_financing(self) -> pd.DataFrame:
        """获取社会融资规模"""
        cache_key = "social_financing"
        return self._request(cache_key, ak.macro_china_shibor)

    # ==================== 加密货币 ====================

    def crypto_cn(self, symbol: str = "BTC") -> pd.DataFrame:
        """
        获取加密货币实时行情 (CNY)

        Args:
            symbol: 币种 (BTC/ETH/USDT)

        Returns:
            pd.DataFrame: 实时行情
        """
        symbol_upper = symbol.upper()
        cache_key = f"crypto_{symbol_upper}_cn"

        if symbol_upper == "BTC":
            return self._request(cache_key, ak.crypto_js_spot, symbol="BTC")
        elif symbol_upper == "ETH":
            return self._request(cache_key, ak.crypto_js_spot, symbol="ETH")
        elif symbol_upper == "USDT":
            return self._request(cache_key, ak.crypto_js_spot, symbol="USDT")
        else:
            return self._request(cache_key, ak.crypto_js_spot, symbol=symbol_upper)

    # ==================== 工具方法 ====================

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        if os.path.exists(self.cache_dir):
            for f in os.listdir(self.cache_dir):
                if f.endswith(".pkl"):
                    os.remove(os.path.join(self.cache_dir, f))

    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        return {
            "enabled": self.cache,
            "dir": self.cache_dir,
            "items": len(self._cache),
            "cache_keys": list(self._cache.keys())
        }
