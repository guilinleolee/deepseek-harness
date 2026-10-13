"""
Polygon.io Provider
专业级市场数据，需要API Key
"""

import logging
from typing import Optional, List, Dict, Any

from .base_provider import BaseProvider, DataType

logger = logging.getLogger(__name__)


class PolygonProvider(BaseProvider):
    """
    Polygon.io数据Provider

    需要API Key，支持股票、ETF、期权、加密货币
    免费tier有限制，付费tier支持完整数据
    """

    def __init__(self, timeout: int = 30, max_retries: int = 3, api_key: Optional[str] = None):
        super().__init__(timeout, max_retries)
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"

    def supports(self, data_type: str) -> bool:
        if not self.api_key:
            return False
        return data_type in [
            "quote", "historical", "financials",
            "earnings", "option_chain"
        ]

    def quote(self, symbol: str) -> Dict[str, Any]:
        symbol = self._validate_symbol(symbol)

        if not self.api_key:
            raise ValueError("Polygon API key required")

        import requests
        url = f"{self.base_url}/v2/aggs/ticker/{symbol}/prev"
        params = {"apiKey": self.api_key}

        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()
        if data.get("status") != "OK" or not data.get("results"):
            return {"symbol": symbol, "price": 0, "error": "No data"}

        result = data["results"][0]

        return {
            "symbol": symbol,
            "price": result.get("c", 0),
            "open": result.get("o", 0),
            "high": result.get("h", 0),
            "low": result.get("l", 0),
            "close": result.get("c", 0),
            "volume": result.get("v", 0),
            "timestamp": data.get("ticker"),
            "change": result.get("c", 0) - result.get("o", 0),
            "change_pct": ((result.get("c", 0) - result.get("o", 0)) / result.get("o", 1)) * 100
        }

    def historical(
        self,
        symbol: str,
        start: str,
        end: str,
        interval: str = "1d"
    ) -> List[Dict[str, Any]]:
        symbol = self._validate_symbol(symbol)

        if not self.api_key:
            raise ValueError("Polygon API key required")

        import requests

        multiplier, timespan = self._parse_interval(interval)
        url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range"
        params = {
            "apiKey": self.api_key,
            "from": start,
            "to": end,
            "multiplier": multiplier,
            "timespan": timespan,
            "adjusted": "true"
        }

        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()
        if data.get("status") != "OK":
            return []

        results = []
        for bar in data.get("results", []):
            results.append({
                "datetime": self._format_timestamp(bar.get("t")),
                "open": bar.get("o", 0),
                "high": bar.get("h", 0),
                "low": bar.get("l", 0),
                "close": bar.get("c", 0),
                "volume": bar.get("v", 0)
            })

        return results

    def financials(self, symbol: str) -> Dict[str, List[Dict]]:
        symbol = self._validate_symbol(symbol)

        if not self.api_key:
            raise ValueError("Polygon API key required")

        import requests
        url = f"{self.base_url}/vX/reference/financials"
        params = {"apiKey": self.api_key, "ticker": symbol}

        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        income_statement = []
        balance_sheet = []
        cash_flow = []

        for r in results:
            fin_type = r.get("financials_type", "")
            if "income" in fin_type:
                income_statement.append(r)
            elif "balance" in fin_type:
                balance_sheet.append(r)
            elif "cash_flow" in fin_type:
                cash_flow.append(r)

        return {
            "income_statement": income_statement,
            "balance_sheet": balance_sheet,
            "cash_flow": cash_flow
        }

    def earnings(self, symbol: str) -> List[Dict[str, Any]]:
        symbol = self._validate_symbol(symbol)

        if not self.api_key:
            raise ValueError("Polygon API key required")

        import requests
        url = f"{self.base_url}/vX/reference/financials"
        params = {"apiKey": self.api_key, "ticker": symbol, "type": "EARNINGS"}

        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()
        return data.get("results", [])

    def option_chain(
        self,
        symbol: str,
        expiration: Optional[str] = None
    ) -> Dict[str, Any]:
        symbol = self._validate_symbol(symbol)

        if not self.api_key:
            raise ValueError("Polygon API key required")

        import requests

        if expiration:
            expiration_str = expiration.replace("-", "")
            url = f"{self.base_url}/v3/reference/options/contracts"
            params = {
                "apiKey": self.api_key,
                "underlying_ticker": symbol,
                "expiration_date": expiration
            }
        else:
            url = f"{self.base_url}/v3/reference/options/contracts"
            params = {
                "apiKey": self.api_key,
                "underlying_ticker": symbol,
                "expires.gte": "true"
            }

        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()
        contracts = data.get("results", [])

        calls = [c for c in contracts if c.get("contract_type") == "call"]
        puts = [c for c in contracts if c.get("contract_type") == "put"]

        return {
            "calls": calls,
            "puts": puts,
            "expiration": expiration
        }

    def option_expirations(self, symbol: str) -> List[str]:
        symbol = self._validate_symbol(symbol)

        if not self.api_key:
            raise ValueError("Polygon API key required")

        import requests
        url = f"{self.base_url}/v3/reference/options/contracts"
        params = {
            "apiKey": self.api_key,
            "underlying_ticker": symbol,
            "expires.gte": "true",
            "fields": "expiration_date"
        }

        response = requests.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()
        expirations = set()
        for c in data.get("results", []):
            if "expiration_date" in c:
                expirations.add(c["expiration_date"])

        return sorted(list(expirations))

    def _parse_interval(self, interval: str) -> tuple:
        """解析interval为multiplier和timespan"""
        interval_map = {
            "1m": (1, "minute"),
            "5m": (5, "minute"),
            "15m": (15, "minute"),
            "30m": (30, "minute"),
            "1h": (1, "hour"),
            "4h": (4, "hour"),
            "1d": (1, "day"),
            "1wk": (1, "week")
        }
        return interval_map.get(interval, (1, "day"))

    def _format_timestamp(self, timestamp: int) -> str:
        """格式化Unix时间戳"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp / 1000).isoformat()
