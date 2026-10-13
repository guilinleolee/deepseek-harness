#!/usr/bin/env python3
"""
Fincept Market Data CLI
命令行接口
"""

import argparse
import json
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fincept_market_data import MarketDataClient


def format_json(data):
    """格式化JSON输出"""
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def cmd_quote(args):
    """获取单只股票行情"""
    client = MarketDataClient()
    result = client.quote(args.symbol)
    print(format_json(result))


def cmd_quotes(args):
    """批量获取股票行情"""
    client = MarketDataClient()
    symbols = [s.strip() for s in args.symbols.split(",")]
    results = client.quotes(symbols)
    print(format_json(results))


def cmd_historical(args):
    """获取历史数据"""
    client = MarketDataClient()
    results = client.historical(
        args.symbol,
        start=args.start,
        end=args.end,
        interval=args.interval
    )
    print(format_json(results))


def cmd_crypto(args):
    """获取加密货币价格"""
    client = MarketDataClient()
    result = client.crypto(args.symbol)
    print(format_json(result))


def cmd_crypto_historical(args):
    """获取加密货币历史数据"""
    client = MarketDataClient()
    results = client.crypto_historical(
        args.symbol,
        start=args.start,
        end=args.end,
        interval=args.interval
    )
    print(format_json(results))


def cmd_financials(args):
    """获取财务报表"""
    client = MarketDataClient()
    result = client.financials(args.symbol)
    print(format_json(result))


def cmd_earnings(args):
    """获取盈利数据"""
    client = MarketDataClient()
    result = client.earnings(args.symbol)
    print(format_json(result))


def cmd_options(args):
    """获取期权链"""
    client = MarketDataClient()
    result = client.option_chain(args.symbol, args.expiration)
    print(format_json(result))


def cmd_option_expirations(args):
    """获取期权到期日"""
    client = MarketDataClient()
    result = client.option_expirations(args.symbol)
    print(format_json(result))


def cmd_batch(args):
    """批量获取历史数据"""
    client = MarketDataClient()
    symbols = [s.strip() for s in args.symbols.split(",")]
    results = client.batch_historical(
        symbols,
        start=args.start,
        end=args.end,
        interval=args.interval,
        parallel=not args.no_parallel
    )
    print(format_json(results))


def cmd_search(args):
    """搜索股票代码"""
    client = MarketDataClient()
    results = client.search_symbols(args.query)
    print(format_json(results))


def cmd_cache_stats(args):
    """查看缓存统计"""
    client = MarketDataClient()
    if client.cache:
        stats = client.cache.stats()
        print(format_json(stats))
    else:
        print("Cache is disabled")


def cmd_cache_clear(args):
    """清除缓存"""
    client = MarketDataClient()
    if client.cache:
        client.cache.clear()
        print("Cache cleared")
    else:
        print("Cache is disabled")


def main():
    parser = argparse.ArgumentParser(
        description="Fincept Market Data CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Quote
    p_quote = subparsers.add_parser("quote", help="Get single stock quote")
    p_quote.add_argument("symbol", help="Stock symbol (e.g., AAPL)")
    p_quote.set_defaults(func=cmd_quote)

    # Quotes
    p_quotes = subparsers.add_parser("quotes", help="Get multiple stock quotes")
    p_quotes.add_argument("symbols", help="Comma-separated symbols (e.g., AAPL,MSFT)")
    p_quotes.set_defaults(func=cmd_quotes)

    # Historical
    p_hist = subparsers.add_parser("hist", help="Get historical data")
    p_hist.add_argument("symbol", help="Stock symbol")
    p_hist.add_argument("--start", default="2024-01-01", help="Start date YYYY-MM-DD")
    p_hist.add_argument("--end", default="2024-12-31", help="End date YYYY-MM-DD")
    p_hist.add_argument("--interval", "-i", default="1d", help="Interval: 1m,5m,15m,1h,4h,1d,1wk")
    p_hist.set_defaults(func=cmd_historical)

    # Crypto
    p_crypto = subparsers.add_parser("crypto", help="Get crypto price")
    p_crypto.add_argument("symbol", help="Crypto pair (e.g., BTC-USD)")
    p_crypto.set_defaults(func=cmd_crypto)

    # Crypto Historical
    p_crypto_hist = subparsers.add_parser("crypto-hist", help="Get crypto historical data")
    p_crypto_hist.add_argument("symbol", help="Crypto pair")
    p_crypto_hist.add_argument("--start", help="Start date YYYY-MM-DD")
    p_crypto_hist.add_argument("--end", help="End date YYYY-MM-DD")
    p_crypto_hist.add_argument("--interval", "-i", default="1h", help="Interval")
    p_crypto_hist.set_defaults(func=cmd_crypto_historical)

    # Financials
    p_fin = subparsers.add_parser("financials", help="Get financial statements")
    p_fin.add_argument("symbol", help="Stock symbol")
    p_fin.set_defaults(func=cmd_financials)

    # Earnings
    p_earn = subparsers.add_parser("earnings", help="Get earnings data")
    p_earn.add_argument("symbol", help="Stock symbol")
    p_earn.set_defaults(func=cmd_earnings)

    # Options
    p_opt = subparsers.add_parser("options", help="Get option chain")
    p_opt.add_argument("symbol", help="Stock symbol")
    p_opt.add_argument("--expiration", "-e", help="Expiration date YYYY-MM-DD")
    p_opt.set_defaults(func=cmd_options)

    # Option Expirations
    p_opt_exp = subparsers.add_parser("expirations", help="Get option expiration dates")
    p_opt_exp.add_argument("symbol", help="Stock symbol")
    p_opt_exp.set_defaults(func=cmd_option_expirations)

    # Batch
    p_batch = subparsers.add_parser("batch", help="Batch historical data")
    p_batch.add_argument("symbols", help="Comma-separated symbols")
    p_batch.add_argument("--start", default="2024-01-01", help="Start date")
    p_batch.add_argument("--end", default="2024-12-31", help="End date")
    p_batch.add_argument("--interval", "-i", default="1d", help="Interval")
    p_batch.add_argument("--no-parallel", action="store_true", help="Disable parallel fetching")
    p_batch.set_defaults(func=cmd_batch)

    # Search
    p_search = subparsers.add_parser("search", help="Search symbols")
    p_search.add_argument("query", help="Search query")
    p_search.set_defaults(func=cmd_search)

    # Cache
    p_cache = subparsers.add_parser("cache-stats", help="Show cache statistics")
    p_cache.set_defaults(func=cmd_cache_stats)

    p_cache_clear = subparsers.add_parser("cache-clear", help="Clear cache")
    p_cache_clear.set_defaults(func=cmd_cache_clear)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
