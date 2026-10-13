"""
Fincept Economic Data Skill - CLI入口
宏观经济数据命令行工具
"""

import os
import sys
import argparse
import json
from typing import Optional

import pandas as pd

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client import EconomicDataClient


def main():
    parser = argparse.ArgumentParser(
        description="Fincept Economic Data CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # FRED指标查询
  python cli.py fred GDP
  python cli.py fred-series GDP,UNRATE,CPIAUCSL

  # 宏观经济查询
  python cli.py macro us gdp
  python cli.py macro cn gdp

  # 利率查询
  python cli.py rates fed
  python cli.py yield-curve us

  # IMF数据
  python cli.py imf USA bop

  # World Bank
  python cli.py worldbank CHN ny.gdp.mktp.cd

  # 搜索指标
  python cli.py search "inflation"

  # 仪表板数据
  python cli.py dashboard

  # 设置API Key
  export FRED_API_KEY=your_key
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # FRED命令
    fred_parser = subparsers.add_parser("fred", help="Query FRED indicator")
    fred_parser.add_argument("indicator", help="Indicator code or name")
    fred_parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    fred_parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    fred_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # FRED批量查询
    fred_series_parser = subparsers.add_parser("fred-series", help="Query multiple FRED indicators")
    fred_series_parser.add_argument("indicators", help="Comma-separated indicator list")
    fred_series_parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    fred_series_parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    fred_series_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # 宏观经济查询
    macro_parser = subparsers.add_parser("macro", help="Query macroeconomic data")
    macro_parser.add_argument("country", help="Country code (us, cn, eu, etc.)")
    macro_parser.add_argument("indicator", help="Indicator name")
    macro_parser.add_argument("--year", help="Specific year")
    macro_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # 利率查询
    rates_parser = subparsers.add_parser("rates", help="Query central bank interest rates")
    rates_parser.add_argument("country", nargs="?", default="us", help="Country code")
    rates_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # 收益率曲线
    yield_parser = subparsers.add_parser("yield-curve", help="Query yield curve")
    yield_parser.add_argument("country", nargs="?", default="us", help="Country code")
    yield_parser.add_argument("--date", help="Specific date (YYYY-MM-DD)")
    yield_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # IMF数据
    imf_parser = subparsers.add_parser("imf", help="Query IMF data")
    imf_parser.add_argument("country", help="Country code (USA, CHN, etc.)")
    imf_parser.add_argument("indicator", help="Indicator name")
    imf_parser.add_argument("--year", help="Specific year")
    imf_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # World Bank数据
    wb_parser = subparsers.add_parser("worldbank", help="Query World Bank data")
    wb_parser.add_argument("country", help="Country code (USA, CHN, etc.)")
    wb_parser.add_argument("indicator", help="Indicator code")
    wb_parser.add_argument("--year", type=int, help="Specific year")
    wb_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # 搜索指标
    search_parser = subparsers.add_parser("search", help="Search economic indicators")
    search_parser.add_argument("keyword", help="Search keyword")
    search_parser.add_argument("--source", choices=["fred", "imf", "worldbank", "china", "all"],
                                default="all", help="Data source filter")
    search_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # 仪表板数据
    dash_parser = subparsers.add_parser("dashboard", help="Get key economic indicators")
    dash_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # 列出指标
    list_parser = subparsers.add_parser("list", help="List available indicators")
    list_parser.add_argument("--source", choices=["fred", "imf", "worldbank", "china"],
                              help="Filter by source")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 创建客户端
    client = EconomicDataClient()

    try:
        if args.command == "fred":
            result = client.fred(args.indicator, start_date=args.start, end_date=args.end)
            if isinstance(result, pd.DataFrame):
                if args.json:
                    print(result.to_json(orient="records"))
                else:
                    print(result.to_string())
            else:
                if args.json:
                    print(json.dumps({"indicator": args.indicator, "value": result}))
                else:
                    print(f"{args.indicator}: {result}")

        elif args.command == "fred-series":
            indicators = [i.strip() for i in args.indicators.split(",")]
            result = client.fred_series(indicators, start_date=args.start, end_date=args.end)
            if args.json:
                print(result.to_json(orient="records"))
            else:
                print(result.to_string())

        elif args.command == "macro":
            result = client.macro(args.country, args.indicator, year=args.year)
            if args.json:
                print(json.dumps({"country": args.country, "indicator": args.indicator, "value": result}))
            else:
                print(f"{args.country} {args.indicator}: {result}")

        elif args.command == "rates":
            result = client.interest_rates(args.country)
            if args.json:
                print(json.dumps({"country": args.country, "rate": result}))
            else:
                print(f"{args.country} interest rate: {result}%")

        elif args.command == "yield-curve":
            result = client.yield_curve(args.country, date=args.date)
            if args.json:
                print(result.to_json(orient="records"))
            else:
                print(f"\n{args.country.upper()} Yield Curve:")
                print(result.to_string(index=False))

        elif args.command == "imf":
            result = client.imf(args.country, args.indicator, year=args.year)
            if args.json:
                print(json.dumps({"country": args.country, "indicator": args.indicator, "value": result}))
            else:
                print(f"IMF {args.country} {args.indicator}: {result}")

        elif args.command == "worldbank":
            result = client.worldbank(args.country, args.indicator, year=args.year)
            if args.json:
                print(json.dumps({"country": args.country, "indicator": args.indicator, "value": result}))
            else:
                print(f"World Bank {args.country} {args.indicator}: {result}")

        elif args.command == "search":
            results = client.search_indicators(source=args.source, keyword=args.keyword)
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(f"\nSearch results for '{args.keyword}' ({args.source}):")
                for r in results:
                    print(f"  [{r['source']}] {r['id']}: {r['title']}")

        elif args.command == "dashboard":
            result = client.get_dashboard_data()
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                print("\n=== Economic Dashboard ===")
                for country, indicators in result.items():
                    print(f"\n{country.upper()}:")
                    for name, value in indicators.items():
                        if value is not None:
                            print(f"  {name}: {value:,.2f}" if isinstance(value, (int, float)) else f"  {name}: {value}")

        elif args.command == "list":
            if args.source == "fred":
                from providers.fred_provider import FredProvider
                provider = FredProvider()
                print("\nFRED Indicators:")
                for name in list(FredProvider.INDICATOR_MAP.keys())[:20]:
                    print(f"  {name}")
            elif args.source == "worldbank":
                from providers.worldbank_provider import WorldBankProvider
                provider = WorldBankProvider()
                print("\nWorld Bank Indicators:")
                for name in list(WorldBankProvider.INDICATOR_MAP.keys())[:20]:
                    print(f"  {name}")
            elif args.source == "china":
                from providers.china_provider import ChinaProvider
                provider = ChinaProvider()
                print("\nChina Indicators:")
                for name in list(ChinaProvider.INDICATOR_MAP.keys())[:20]:
                    print(f"  {name}")
            else:
                print("Use --source to specify fred, worldbank, or china")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
