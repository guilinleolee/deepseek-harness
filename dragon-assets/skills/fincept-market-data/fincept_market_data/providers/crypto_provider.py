"""
Crypto Provider
加密货币数据，支持Binance, Coinbase, Kraken等
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

from .base_provider import BaseProvider, DataType

logger = logging.getLogger(__name__)


class CryptoProvider(BaseProvider):
    """
    加密货币数据Provider

    使用yfinance作为主要数据源（支持Kraken等交易所）
    """

    CRYPTO_SYMBOLS = {
        "BTC-USD": "BTC-USD",  # Kraken
        "ETH-USD": "ETH-USD",
        "BTC-GBP": "BTC-GBP",
        "ETH-EUR": "ETH-EUR",
    }

    def supports(self, data_type: str) -> bool:
        return data_type in ["quote", "historical", "crypto"]

    def quote(self, symbol: str) -> Dict[str, Any]:
        """获取加密货币实时价格"""
        symbol = self._validate_crypto_symbol(symbol)

        ticker = yf.Ticker(symbol)
        info = ticker.fast_info

        try:
            price = info.get("price") or info.get("lastPrice")
            previous_close = info.get("previous_close") or info.get("regularMarketPreviousClose")
            change = price - previous_close if price and previous_close else 0
            change_pct = (change / previous_close * 100) if previous_close else 0

            return {
                "symbol": symbol,
                "price": float(price) if price else 0,
                "change": float(change) if change else 0,
                "change_pct": float(change_pct) if change_pct else 0,
                "volume_24h": info.get("volume", 0),
                "bid": price * 0.9999,  # 估算
                "ask": price * 1.0001,  # 估算
                "timestamp": datetime.now().isoformat(),
                "exchange": "Kraken",
                "currency": symbol.split("-")[-1]
            }
        except Exception as e:
            logger.error(f"Error fetching crypto quote for {symbol}: {e}")
            return {
                "symbol": symbol,
                "price": 0,
                "change": 0,
                "change_pct": 0,
                "volume_24h": 0,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def historical(
        self,
        symbol: str,
        start: str,
        end: str,
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        """获取加密货币历史数据"""
        symbol = self._validate_crypto_symbol(symbol)

        interval_map = {
            "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
            "1h": "60m", "4h": "4h", "1d": "1d", "1wk": "1wk"
        }
        yf_interval = interval_map.get(interval, "1d")

        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start, end=end, interval=yf_interval)

        if hist.empty:
            return []

        results = []
        for dt, row in hist.iterrows():
            results.append({
                "datetime": dt.isoformat(),
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"])
            })

        return results

    def _validate_crypto_symbol(self, symbol: str) -> str:
        """验证并标准化加密货币符号"""
        symbol = symbol.upper().strip()
        if "-" not in symbol:
            if symbol.endswith("USD"):
                symbol = symbol.replace("USD", "-USD")
            elif symbol.endswith("USDT"):
                symbol = symbol.replace("USDT", "-USD")
            else:
                symbol = f"{symbol}-USD"
        return symbol

    def batch_quotes(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """批量获取加密货币报价"""
        results = []
        for symbol in symbols:
            results.append(self.quote(symbol))
        return results

    def get_exchange_rates(self, base_currency: str = "BTC") -> Dict[str, float]:
        """
        获取加密货币汇率

        Args:
            base_currency: 基础货币，如 "BTC"

        Returns:
            dict: {currency: rate}
        """
        rates = {}
        currency_symbols = ["USD", "EUR", "GBP", "JPY", "CNY"]

        for curr in currency_symbols:
            symbol = f"{base_currency}-{curr}"
            try:
                ticker = yf.Ticker(symbol)
                price = ticker.fast_info.get("price")
                if price:
                    rates[curr] = float(price)
            except Exception as e:
                logger.warning(f"Error fetching {symbol}: {e}")

        return rates

    def get_market_summary(self, symbol: str) -> Dict[str, Any]:
        """获取市场概要"""
        symbol = self._validate_crypto_symbol(symbol)
        ticker = yf.Ticker(symbol)

        try:
            info = ticker.info
            return {
                "symbol": symbol,
                "name": info.get("name", symbol),
                "price": info.get("current_price", 0),
                "market_cap": info.get("market_cap", 0),
                "market_cap_rank": info.get("market_cap_rank", 0),
                "total_volume": info.get("total_volume", 0),
                "high_24h": info.get("high_24h", 0),
                "low_24h": info.get("low_24h", 0),
                "price_change_24h": info.get("price_change_24h", 0),
                "price_change_percentage_24h": info.get("price_change_percentage_24h", 0),
                "circulating_supply": info.get("circulating_supply", 0),
                "total_supply": info.get("total_supply", 0),
                "max_supply": info.get("max_supply", 0),
                "ath": info.get("ath", 0),
                "atl": info.get("atl", 0),
                "last_updated": info.get("last_updated", datetime.now().isoformat())
            }
        except Exception as e:
            logger.error(f"Error fetching market summary for {symbol}: {e}")
            return {"symbol": symbol, "error": str(e)}
