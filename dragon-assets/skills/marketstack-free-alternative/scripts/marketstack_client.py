#!/usr/bin/env python3
"""
Marketstack Free API Client - Alpha Vantage + Finnhub 双冗余客户端
来源: 天龙引擎 V11.13 免费API替代方案
文档: skills/marketstack-free-alternative/SKILL.md
"""

import os
import json
import time
from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("请安装 requests: pip install requests")
    exit(1)


@dataclass
class StockQuote:
    """股票报价数据结构"""
    symbol: str
    price: float
    volume: int
    timestamp: str
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    previous_close: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "volume": self.volume,
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "previous_close": self.previous_close,
            "change": self.change,
            "change_percent": self.change_percent
        }


@dataclass
class DailyOHLCV:
    """日线OHLCV数据"""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }


@dataclass
class TechnicalIndicator:
    """技术指标数据"""
    date: str
    value: float
    indicator_type: str

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "value": self.value,
            "indicator_type": self.indicator_type
        }


@dataclass
class MarketNews:
    """市场新闻数据结构"""
    datetime: str
    headline: str
    source: str
    url: str
    summary: str
    category: str
    symbols: list[str]

    def to_dict(self) -> dict:
        return {
            "datetime": self.datetime,
            "headline": self.headline,
            "source": self.source,
            "url": self.url,
            "summary": self.summary,
            "category": self.category,
            "symbols": self.symbols
        }


class MarketAPIError(Exception):
    """市场API异常"""
    pass


class MarketStackClient:
    """
    双冗余市场数据客户端 - Alpha Vantage + Finnhub

    使用方式:
        client = MarketStackClient()  # 自动使用环境变量
        client = MarketStackClient(alpha_key="xxx", finnhub_key="xxx")  # 显式指定

    环境变量:
        ALPHA_VANTAGE_API_KEY: Alpha Vantage API密钥 (https://www.alphavantage.co)
        FINNHUB_API_KEY: Finnhub API密钥 (https://finnhub.io)

    免费额度:
        Alpha Vantage: 5请求/分钟, 500请求/天, 股票/外汇/数字货币
        Finnhub: 60请求/分钟, 股票数据+新闻
    """

    BASE_URL_ALPHA = "https://www.alphavantage.co/query"
    BASE_URL_FINNHUB = "https://finnhub.io/api/v1"

    def __init__(
        self,
        alpha_key: Optional[str] = None,
        finnhub_key: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: int = 300
    ):
        self.alpha_key = alpha_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        self.finnhub_key = finnhub_key or os.getenv("FINNHUB_API_KEY")
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        self._cache = {}

        if not self.alpha_key and not self.finnhub_key:
            raise MarketAPIError(
                "需要设置ALPHA_VANTAGE_API_KEY或FINNHUB_API_KEY环境变量\n"
                "获取地址:\n"
                "  Alpha Vantage: https://www.alphavantage.co/support/#api-key\n"
                "  Finnhub: https://finnhub.io/register\n"
                "推荐Alpha Vantage: 支持股票、外汇、数字货币，技术指标更丰富"
            )

    def _check_cache(self, key: str) -> Optional[list]:
        """检查缓存"""
        if not self.use_cache:
            return None
        if key in self._cache:
            cached, timestamp = self._cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return cached
        return None

    def _set_cache(self, key: str, data: list):
        """设置缓存"""
        if self.use_cache:
            self._cache[key] = (data, time.time())

    def _parse_alpha_quote(self, data: dict) -> StockQuote:
        """解析Alpha Vantage Global Quote"""
        global_quote = data.get("Global Quote", {})
        return StockQuote(
            symbol=global_quote.get("01. symbol", ""),
            price=float(global_quote.get("05. price", 0)),
            volume=int(global_quote.get("06. volume", 0)),
            timestamp=global_quote.get("07. latest trading day", ""),
            open=float(global_quote.get("02. open", 0)) if global_quote.get("02. open") else None,
            high=float(global_quote.get("03. high", 0)) if global_quote.get("03. high") else None,
            low=float(global_quote.get("04. low", 0)) if global_quote.get("04. low") else None,
            close=float(global_quote.get("05. price", 0)),
            previous_close=float(global_quote.get("08. previous close", 0)) if global_quote.get("08. previous close") else None,
            change=float(global_quote.get("09. change", 0)) if global_quote.get("09. change") else None,
            change_percent=global_quote.get("10. change percent", "").replace("%", "")
        )

    def _parse_alpha_daily(self, data: dict) -> list[DailyOHLCV]:
        """解析Alpha Vantage Time Series Daily"""
        time_series = data.get("Time Series (Daily)", {})
        result = []
        for date, values in time_series.items():
            result.append(DailyOHLCV(
                date=date,
                open=float(values.get("1. open", 0)),
                high=float(values.get("2. high", 0)),
                low=float(values.get("3. low", 0)),
                close=float(values.get("4. close", 0)),
                volume=int(values.get("5. volume", 0))
            ))
        return result

    def _parse_finnhub_quote(self, data: dict, symbol: str) -> StockQuote:
        """解析Finnhub Quote"""
        return StockQuote(
            symbol=symbol,
            price=data.get("c", 0),
            volume=data.get("volume", 0),
            timestamp=datetime.fromtimestamp(data.get("t", 0)).strftime("%Y-%m-%d") if data.get("t") else "",
            open=data.get("o"),
            high=data.get("h"),
            low=data.get("l"),
            close=data.get("c"),
            previous_close=data.get("pc"),
            change=data.get("d"),
            change_percent=str(data.get("dp", 0)) if data.get("dp") is not None else None
        )

    def get_quote(self, symbol: str, use_finnhub_fallback: bool = True) -> StockQuote:
        """
        获取实时股票报价

        参数:
            symbol: 股票代码 (如 AAPL, MSFT)
            use_finnhub_fallback: Alpha Vantage失败时是否使用Finnhub

        返回:
            StockQuote对象
        """
        cache_key = f"quote_{symbol}"
        cached = self._check_cache(cache_key)
        if cached:
            return StockQuote(**cached[0])

        # 优先使用Alpha Vantage
        if self.alpha_key:
            try:
                params = {
                    "function": "GLOBAL_QUOTE",
                    "symbol": symbol,
                    "apikey": self.alpha_key
                }
                resp = requests.get(self.BASE_URL_ALPHA, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()

                if "Global Quote" in data and data["Global Quote"]:
                    quote = self._parse_alpha_quote(data)
                    self._set_cache(cache_key, [quote.to_dict()])
                    return quote

            except requests.RequestException as e:
                if not use_finnhub_fallback:
                    raise MarketAPIError(f"Alpha Vantage请求失败: {e}")

        # Finnhub回退
        if self.finnhub_key:
            try:
                params = {"symbol": symbol, "token": self.finnhub_key}
                resp = requests.get(f"{self.BASE_URL_FINNHUB}/quote", params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()

                if data.get("c") and data.get("c") != 0:
                    quote = self._parse_finnhub_quote(data, symbol)
                    self._set_cache(cache_key, [quote.to_dict()])
                    return quote

            except requests.RequestException as e:
                raise MarketAPIError(f"Finnhub请求失败: {e}")

        raise MarketAPIError(f"无法获取 {symbol} 报价")

    def get_daily(
        self,
        symbol: str,
        output_size: str = "compact",
        use_finnhub_fallback: bool = False
    ) -> list[DailyOHLCV]:
        """
        获取日线OHLCV数据

        参数:
            symbol: 股票代码
            output_size: compact(最近100天) 或 full(20年+)
            use_finnhub_fallback: 是否使用Finnhub(有限支持)

        返回:
            DailyOHLCV列表
        """
        cache_key = f"daily_{symbol}_{output_size}"
        cached = self._check_cache(cache_key)
        if cached:
            return [DailyOHLCV(**item) for item in cached]

        if not self.alpha_key:
            raise MarketAPIError("需要ALPHA_VANTAGE_API_KEY来获取日线数据")

        try:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": output_size,
                "apikey": self.alpha_key
            }
            resp = requests.get(self.BASE_URL_ALPHA, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if "Time Series (Daily)" in data:
                daily = self._parse_alpha_daily(data)
                self._set_cache(cache_key, [d.to_dict() for d in daily])
                return daily

            raise MarketAPIError(f"Alpha Vantage错误: {data.get('Note', '未知错误')}")

        except requests.RequestException as e:
            raise MarketAPIError(f"Alpha Vantage请求失败: {e}")

    def get_indicator(
        self,
        symbol: str,
        indicator: str = "SMA",
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close"
    ) -> list[TechnicalIndicator]:
        """
        获取技术指标

        参数:
            symbol: 股票代码
            indicator: 指标类型 (SMA, EMA, RSI, MACD, BBANDS, etc.)
            interval: 时间间隔 (1min, 5min, 15min, 30min, 60min, daily, weekly, monthly)
            time_period: 周期数
            series_type: 数据类型 (close, open, high, low)

        返回:
            TechnicalIndicator列表
        """
        cache_key = f"indicator_{symbol}_{indicator}_{interval}_{time_period}"
        cached = self._check_cache(cache_key)
        if cached:
            return [TechnicalIndicator(**item) for item in cached]

        if not self.alpha_key:
            raise MarketAPIError("需要ALPHA_VANTAGE_API_KEY来获取技术指标")

        func_map = {
            "SMA": "SMA",
            "EMA": "EMA",
            "RSI": "RSI",
            "MACD": "MACD",
            "BBANDS": "BBANDS",
            "STOCH": "STOCH",
            "ADX": "ADX",
            "CCI": "CCI",
            "OBV": "OBV"
        }

        func = func_map.get(indicator.upper(), "SMA")

        try:
            params = {
                "function": func,
                "symbol": symbol,
                "interval": interval,
                "time_period": time_period,
                "series_type": series_type,
                "apikey": self.alpha_key
            }
            resp = requests.get(self.BASE_URL_ALPHA, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            # 解析不同指标格式
            result = []
            indicator_key = None

            for key in data:
                if "Technical Analysis" in key or key.startswith("Technical Analysis"):
                    indicator_key = key
                    break

            if indicator_key:
                for date, values in data[indicator_key].items():
                    if isinstance(values, dict):
                        for val_key, val in values.items():
                            result.append(TechnicalIndicator(
                                date=date,
                                value=float(val),
                                indicator_type=indicator
                            ))
                            break

            if not result:
                raise MarketAPIError(f"无法解析指标数据: {data}")

            self._set_cache(cache_key, [r.to_dict() for r in result])
            return result

        except requests.RequestException as e:
            raise MarketAPIError(f"Alpha Vantage请求失败: {e}")

    def get_news(
        self,
        category: str = "general",
        symbols: Optional[list[str]] = None,
        use_alpha_vantage: bool = False
    ) -> list[MarketNews]:
        """
        获取市场新闻

        参数:
            category: 新闻类别 (general, forex, crypto, merger)
            symbols: 股票代码列表过滤
            use_alpha_vantage: 是否使用Alpha Vantage(有限新闻)

        返回:
            MarketNews列表
        """
        cache_key = f"news_{category}_{'-'.join(symbols or [])}"
        cached = self._check_cache(cache_key)
        if cached:
            return [MarketNews(**item) for item in cached]

        # 优先使用Finnhub(新闻更丰富)
        if self.finnhub_key:
            try:
                params = {
                    "category": category,
                    "token": self.finnhub_key
                }
                if symbols:
                    params["symbol"] = ",".join(symbols[:5])  # Finnhub限制

                resp = requests.get(f"{self.BASE_URL_FINNHUB}/news", params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()

                result = []
                for item in data:
                    result.append(MarketNews(
                        datetime=datetime.fromtimestamp(item.get("datetime", 0)).strftime("%Y-%m-%d %H:%M")
                            if item.get("datetime") else "",
                        headline=item.get("headline", ""),
                        source=item.get("source", ""),
                        url=item.get("url", ""),
                        summary=item.get("summary", ""),
                        category=item.get("category", category),
                        symbols=item.get("related", "").split(",")[:10]
                    ))

                self._set_cache(cache_key, [n.to_dict() for n in result])
                return result

            except requests.RequestException as e:
                if not use_alpha_vantage:
                    raise MarketAPIError(f"Finnhub请求失败: {e}")

        # Alpha Vantage回退
        if self.alpha_key and use_alpha_vantage:
            try:
                params = {
                    "function": "NEWS_SENTIMENT",
                    "apikey": self.alpha_key
                }
                resp = requests.get(self.BASE_URL_ALPHA, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()

                if "feed" in data:
                    result = []
                    for item in data["feed"][:20]:
                        result.append(MarketNews(
                            datetime=item.get("time_published", ""),
                            headline=item.get("title", ""),
                            source=item.get("source", ""),
                            url=item.get("url", ""),
                            summary=item.get("summary", ""),
                            category=item.get("categories", ""),
                            symbols=item.get("tickers", [])[:10]
                        ))
                    self._set_cache(cache_key, [n.to_dict() for n in result])
                    return result

            except requests.RequestException as e:
                raise MarketAPIError(f"Alpha Vantage请求失败: {e}")

        raise MarketAPIError("需要FINNHUB_API_KEY来获取市场新闻")

    def search_symbol(self, query: str) -> list[dict]:
        """
        搜索股票代码

        参数:
            query: 搜索关键词

        返回:
            股票信息列表
        """
        if not self.finnhub_key:
            raise MarketAPIError("需要FINNHUB_API_KEY来搜索股票")

        cache_key = f"search_{query}"
        cached = self._check_cache(cache_key)
        if cached:
            return cached

        try:
            params = {"query": query, "token": self.finnhub_key}
            resp = requests.get(f"{self.BASE_URL_FINNHUB}/search", params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            result = data.get("result", [])[:10]
            self._set_cache(cache_key, result)
            return result

        except requests.RequestException as e:
            raise MarketAPIError(f"Finnhub搜索失败: {e}")

    def to_json(self, data: list) -> str:
        """转换为JSON格式"""
        if isinstance(data, list) and len(data) > 0:
            if hasattr(data[0], "to_dict"):
                return json.dumps([item.to_dict() for item in data], ensure_ascii=False, indent=2)
        return json.dumps(data, ensure_ascii=False, indent=2)


def main():
    """CLI入口"""
    import argparse

    parser = argparse.ArgumentParser(description="市场数据API客户端 - Alpha Vantage + Finnhub")
    parser.add_argument("--symbol", "-s", help="股票代码")
    parser.add_argument("--quote", "-q", action="store_true", help="获取实时报价")
    parser.add_argument("--daily", "-d", action="store_true", help="获取日线数据")
    parser.add_argument("--indicator", "-i", help="技术指标 (SMA, EMA, RSI, MACD, BBANDS)")
    parser.add_argument("--period", type=int, default=20, help="指标周期 (默认: 20)")
    parser.add_argument("--news", "-n", action="store_true", help="获取市场新闻")
    parser.add_argument("--search", help="搜索股票代码")
    parser.add_argument("--category", default="general", help="新闻类别 (默认: general)")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text", help="输出格式")
    parser.add_argument("--no-cache", action="store_true", help="禁用缓存")

    args = parser.parse_args()

    try:
        client = MarketStackClient(use_cache=not args.no_cache)

        if args.search:
            results = client.search_symbol(args.search)
            if args.format == "json":
                print(client.to_json(results))
            else:
                print(f"🔍 搜索结果: {args.search}")
                for item in results:
                    print(f"  {item.get('symbol', 'N/A')} | {item.get('description', 'N/A')}")
            return

        if not args.symbol:
            parser.print_help()
            return

        if args.quote:
            quote = client.get_quote(args.symbol)
            if args.format == "json":
                print(client.to_json([quote.to_dict()]))
            else:
                print(f"📈 {args.symbol} 报价")
                print(f"   当前价格: ${quote.price}")
                if quote.change is not None:
                    print(f"   涨跌: ${quote.change} ({quote.change_percent}%)")
                print(f"   成交量: {quote.volume:,}")
                print(f"   高/低: ${quote.high or 'N/A'}/${quote.low or 'N/A'}")

        elif args.daily:
            daily = client.get_daily(args.symbol)
            if args.format == "json":
                print(client.to_json(daily))
            else:
                print(f"📊 {args.symbol} 日线数据")
                for item in daily[:10]:
                    print(f"   {item.date}: O={item.open:.2f} H={item.high:.2f} L={item.low:.2f} C={item.close:.2f} V={item.volume:,}")

        elif args.indicator:
            indicator = args.indicator.upper()
            data = client.get_indicator(args.symbol, indicator, time_period=args.period)
            if args.format == "json":
                print(client.to_json(data))
            else:
                print(f"📉 {args.symbol} {indicator} (周期: {args.period})")
                for item in data[:10]:
                    print(f"   {item.date}: {item.value:.2f}")

        elif args.news:
            news = client.get_news(args.category)
            if args.format == "json":
                print(client.to_json(news))
            else:
                print(f"📰 市场新闻 ({args.category})")
                for i, item in enumerate(news[:10], 1):
                    print(f"\n{i}. {item.headline}")
                    print(f"   来源: {item.source} | 时间: {item.datetime}")
                    if item.symbols:
                        print(f"   相关: {', '.join(item.symbols[:3])}")

        else:
            parser.print_help()

    except MarketAPIError as e:
        print(f"❌ 错误: {e}")
        exit(1)


if __name__ == "__main__":
    main()