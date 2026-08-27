"""
Yahoo Finance Provider
使用yfinance获取股票、ETF、加密货币数据
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

from .base_provider import BaseProvider, DataType

logger = logging.getLogger(__name__)


class YFinanceProvider(BaseProvider):
    """
    Yahoo Finance数据Provider

    支持: 股票、ETF、期货、指数、加密货币
    """

    def supports(self, data_type: str) -> bool:
        if not YFINANCE_AVAILABLE:
            return False
        return data_type in [
            "quote", "historical", "financials",
            "earnings", "option_chain", "crypto", "search"
        ]

    def quote(self, symbol: str) -> Dict[str, Any]:
        symbol = self._validate_symbol(symbol)

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
                "volume": int(info.get("volume", 0)),
                "timestamp": datetime.now().isoformat(),
                "market_cap": info.get("market_cap"),
                "currency": info.get("currency", "USD")
            }
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return {
                "symbol": symbol,
                "price": 0,
                "change": 0,
                "change_pct": 0,
                "volume": 0,
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
        symbol = self._validate_symbol(symbol)

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

    def financials(self, symbol: str) -> Dict[str, List[Dict]]:
        symbol = self._validate_symbol(symbol)
        ticker = yf.Ticker(symbol)

        def parse_financials(financials_df, fin_type: str) -> List[Dict]:
            if financials_df is None or financials_df.empty:
                return []
            records = []
            for date_col in financials_df.columns:
                record = {"date": str(date_col), "type": fin_type}
                for idx in financials_df.index:
                    record[idx.lower().replace(" ", "_")] = financials_df.loc[idx, date_col]
                records.append(record)
            return records

        try:
            income = ticker.income_stmt
            balance = ticker.balance_sheet
            cashflow = ticker.cashflow

            return {
                "income_statement": parse_financials(income, "income"),
                "balance_sheet": parse_financials(balance, "balance"),
                "cash_flow": parse_financials(cashflow, "cashflow")
            }
        except Exception as e:
            logger.error(f"Error fetching financials for {symbol}: {e}")
            return {
                "income_statement": [],
                "balance_sheet": [],
                "cash_flow": []
            }

    def earnings(self, symbol: str) -> List[Dict[str, Any]]:
        symbol = self._validate_symbol(symbol)
        ticker = yf.Ticker(symbol)

        try:
            earnings_df = ticker.earnings
            if earnings_df is None or earnings_df.empty:
                return []

            results = []
            for date, row in earnings_df.iterrows():
                results.append({
                    "date": str(date),
                    "eps": float(row.get("Earnings", 0)),
                    "revenue": float(row.get("Revenue", 0)) if "Revenue" in row else None,
                    "surprise": float(row.get("Surprise", 0)) if "Surprise" in row else None
                })

            return results
        except Exception as e:
            logger.error(f"Error fetching earnings for {symbol}: {e}")
            return []

    def option_chain(
        self,
        symbol: str,
        expiration: Optional[str] = None
    ) -> Dict[str, Any]:
        symbol = self._validate_symbol(symbol)
        ticker = yf.Ticker(symbol)

        try:
            if expiration:
                opts = ticker.option_chain(expiration)
            else:
                dates = ticker.options
                if not dates:
                    return {"calls": [], "puts": [], "expiration": None}
                opts = ticker.option_chain(dates[0])

            calls = []
            for _, row in opts.calls.iterrows():
                calls.append({
                    "strike": float(row["Strike"]),
                    "bid": float(row["Bid"]),
                    "ask": float(row["Ask"]),
                    "volume": int(row["Volume"]) if "Volume" in row else 0,
                    "open_interest": int(row["Open Interest"]) if "Open Interest" in row else 0,
                    "implied_volatility": float(row["Implied Volatility"]) if "Implied Volatility" in row else 0
                })

            puts = []
            for _, row in opts.puts.iterrows():
                puts.append({
                    "strike": float(row["Strike"]),
                    "bid": float(row["Bid"]),
                    "ask": float(row["Ask"]),
                    "volume": int(row["Volume"]) if "Volume" in row else 0,
                    "open_interest": int(row["Open Interest"]) if "Open Interest" in row else 0,
                    "implied_volatility": float(row["Implied Volatility"]) if "Implied Volatility" in row else 0
                })

            return {
                "calls": calls,
                "puts": puts,
                "expiration": expiration or (dates[0] if dates else None)
            }
        except Exception as e:
            logger.error(f"Error fetching options for {symbol}: {e}")
            return {"calls": [], "puts": [], "expiration": None}

    def option_expirations(self, symbol: str) -> List[str]:
        symbol = self._validate_symbol(symbol)
        ticker = yf.Ticker(symbol)

        try:
            return list(ticker.options) if ticker.options else []
        except Exception as e:
            logger.error(f"Error fetching option expirations for {symbol}: {e}")
            return []

    def search(self, query: str) -> List[Dict[str, Any]]:
        try:
            import yfinance as yf
            search_results = yf.Search(query)
            return [
                {
                    "symbol": r.get("symbol"),
                    "name": r.get("longname") or r.get("shortname"),
                    "type": r.get("type"),
                    "exchange": r.get("exchange")
                }
                for r in search_results.get("quotes", [])
                if r.get("symbol")
            ]
        except Exception as e:
            logger.error(f"Error searching {query}: {e}")
            return []
