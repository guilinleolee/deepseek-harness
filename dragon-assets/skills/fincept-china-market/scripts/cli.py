#!/usr/bin/env python3
"""
Fincept China Market CLI
命令行接口
用法: fincept-china <command> [args]
"""

import sys
import argparse
import json
from typing import Optional

# 添加父目录到路径
sys.path.insert(0, __file__.rsplit("/", 2)[0])

from fincept_china_market.scripts.client import ChinaMarketClient, FinceptError


def format_output(df, format_type: str = "table") -> str:
    """
    格式化输出

    Args:
        df: DataFrame 数据
        format_type: 输出格式 (table/json/csv)

    Returns:
        str: 格式化后的字符串
    """
    if df is None or df.empty:
        return "无数据"

    if format_type == "json":
        return df.to_json(orient="records", force_ascii=False, indent=2)
    elif format_type == "csv":
        return df.to_csv(index=False)
    else:  # table
        # 限制显示行数
        if len(df) > 20:
            return df.head(20).to_string(index=False) + f"\n... 共 {len(df)} 行"
        return df.to_string(index=False)


def cmd_realtime(args):
    """实时行情命令"""
    client = ChinaMarketClient()
    symbols = args.symbols.split(",")

    if len(symbols) == 1:
        df = client.realtime(symbols[0])
    else:
        df = client.realtime(symbols)

    print(format_output(df, args.format))


def cmd_kline(args):
    """K线命令"""
    client = ChinaMarketClient()

    df = client.kline(
        symbol=args.symbol,
        period=args.period,
        start_date=args.start,
        end_date=args.end
    )

    print(format_output(df, args.format))


def cmd_financial(args):
    """财务数据命令"""
    client = ChinaMarketClient()
    result = client.financial(args.symbol)

    for key, df in result.items():
        print(f"\n=== {key.upper()} ===")
        print(format_output(df, args.format))


def cmd_indicator(args):
    """财务指标命令"""
    client = ChinaMarketClient()
    df = client.indicator(args.symbol)
    print(format_output(df, args.format))


def cmd_futures(args):
    """期货命令"""
    client = ChinaMarketClient()

    if args.spot:
        df = client.futures_spot()
    elif args.positions:
        df = client.futures_positions(args.symbol)
    else:
        df = client.futures(args.symbol)

    print(format_output(df, args.format))


def cmd_options(args):
    """期权命令"""
    client = ChinaMarketClient()

    if args.type == "50etf":
        df = client.options_50etf()
    else:
        df = client.options_300()

    print(format_output(df, args.format))


def cmd_bond(args):
    """债券命令"""
    client = ChinaMarketClient()

    if args.corporate:
        df = client.corporate_bond()
    else:
        df = client.bond()

    print(format_output(df, args.format))


def cmd_fund(args):
    """基金命令"""
    client = ChinaMarketClient()

    if args.nav:
        df = client.fund_nav(args.symbol)
    else:
        df = client.fund(args.symbol, period=args.period)
        if args.start:
            df = client.fund(args.symbol, period=args.period,
                           start_date=args.start, end_date=args.end)

    print(format_output(df, args.format))


def cmd_macro(args):
    """宏观数据命令"""
    client = ChinaMarketClient()

    if args.cpi:
        df = client.macro_cpi()
    elif args.gdp:
        df = client.macro_gdp()
    elif args.ppi:
        df = client.macro_ppi()
    elif args.money:
        df = client.money_supply()
    else:
        print("请指定数据类型: --cpi, --gdp, --ppi, --money")
        return

    print(format_output(df, args.format))


def cmd_crypto(args):
    """加密货币命令"""
    client = ChinaMarketClient()
    df = client.crypto_cn(args.symbol.upper())
    print(format_output(df, args.format))


def main():
    parser = argparse.ArgumentParser(
        description="Fincept China Market - 中国市场数据 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 实时行情
    p_realtime = subparsers.add_parser("realtime", help="实时行情")
    p_realtime.add_argument("symbols", help="股票代码 (逗号分隔)")
    p_realtime.add_argument("--format", "-f", choices=["table", "json", "csv"],
                           default="table", help="输出格式")

    # K线
    p_kline = subparsers.add_parser("kline", help="历史K线")
    p_kline.add_argument("symbol", help="股票代码")
    p_kline.add_argument("--period", "-p", default="daily",
                        choices=["daily", "weekly", "monthly"], help="K线周期")
    p_kline.add_argument("--start", "-s", help="开始日期 YYYYMMDD")
    p_kline.add_argument("--end", "-e", help="结束日期 YYYYMMDD")
    p_kline.add_argument("--format", "-f", choices=["table", "json", "csv"],
                        default="table", help="输出格式")

    # 财务
    p_financial = subparsers.add_parser("financial", help="财务报表")
    p_financial.add_argument("symbol", help="股票代码")
    p_financial.add_argument("--format", "-f", choices=["table", "json", "csv"],
                            default="table", help="输出格式")

    # 指标
    p_indicator = subparsers.add_parser("indicator", help="财务指标")
    p_indicator.add_argument("symbol", help="股票代码")
    p_indicator.add_argument("--format", "-f", choices=["table", "json", "csv"],
                           default="table", help="输出格式")

    # 期货
    p_futures = subparsers.add_parser("futures", help="期货数据")
    p_futures.add_argument("symbol", nargs="?", help="期货品种")
    p_futures.add_argument("--spot", action="store_true", help="商品期货实时")
    p_futures.add_argument("--positions", action="store_true", help="持仓排名")
    p_futures.add_argument("--format", "-f", choices=["table", "json", "csv"],
                          default="table", help="输出格式")

    # 期权
    p_options = subparsers.add_parser("options", help="期权数据")
    p_options.add_argument("--type", "-t", choices=["50etf", "300"],
                          default="50etf", help="期权类型")

    # 债券
    p_bond = subparsers.add_parser("bond", help="债券数据")
    p_bond.add_argument("--corporate", "-c", action="store_true", help="企业债")
    p_bond.add_argument("--format", "-f", choices=["table", "json", "csv"],
                       default="table", help="输出格式")

    # 基金
    p_fund = subparsers.add_parser("fund", help="基金数据")
    p_fund.add_argument("symbol", help="基金代码")
    p_fund.add_argument("--nav", "-n", action="store_true", help="净值数据")
    p_fund.add_argument("--period", "-p", default="daily",
                       choices=["daily", "weekly", "monthly"], help="周期")
    p_fund.add_argument("--start", "-s", help="开始日期")
    p_fund.add_argument("--end", "-e", help="结束日期")
    p_fund.add_argument("--format", "-f", choices=["table", "json", "csv"],
                       default="table", help="输出格式")

    # 宏观
    p_macro = subparsers.add_parser("macro", help="宏观数据")
    p_macro.add_argument("--cpi", action="store_true", help="CPI数据")
    p_macro.add_argument("--gdp", action="store_true", help="GDP数据")
    p_macro.add_argument("--ppi", action="store_true", help="PPI数据")
    p_macro.add_argument("--money", action="store_true", help="货币供应量")
    p_macro.add_argument("--format", "-f", choices=["table", "json", "csv"],
                        default="table", help="输出格式")

    # 加密货币
    p_crypto = subparsers.add_parser("crypto", help="加密货币")
    p_crypto.add_argument("symbol", help="币种 (BTC/ETH/USDT)")
    p_crypto.add_argument("--format", "-f", choices=["table", "json", "csv"],
                         default="table", help="输出格式")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # 执行命令
    try:
        if args.command == "realtime":
            cmd_realtime(args)
        elif args.command == "kline":
            cmd_kline(args)
        elif args.command == "financial":
            cmd_financial(args)
        elif args.command == "indicator":
            cmd_indicator(args)
        elif args.command == "futures":
            cmd_futures(args)
        elif args.command == "options":
            cmd_options(args)
        elif args.command == "bond":
            cmd_bond(args)
        elif args.command == "fund":
            cmd_fund(args)
        elif args.command == "macro":
            cmd_macro(args)
        elif args.command == "crypto":
            cmd_crypto(args)
        else:
            print(f"未知命令: {args.command}")
    except FinceptError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"未知错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
