"""
Fincept Quant Analytics CLI

命令行接口，提供以下命令：
- dcf: DCF估值分析
- tech: 技术指标计算
- greeks: 期权Greeks计算
- risk: 风险指标计算
"""

import argparse
import sys
import json

# 添加scripts目录到路径
sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")

from fincept_quant import DCFAnalyzer, TechnicalAnalyzer, OptionsAnalyzer, RiskAnalyzer


def cmd_dcf(args):
    """DCF估值命令"""
    analyzer = DCFAnalyzer()

    result = analyzer.dcf(
        ticker=args.ticker,
        revenue=args.revenue,
        revenue_growth=args.growth,
        operating_margin=args.margin,
        discount_rate=args.discount,
        terminal_growth=args.terminal_growth,
        years=args.years,
        shares_outstanding=args.shares,
        net_debt=args.net_debt or 0,
        current_price=args.price,
    )

    print(f"\n{'='*50}")
    print(f"DCF Valuation for {result['ticker']}")
    print(f"{'='*50}")
    print(f"Intrinsic Value: ${result['intrinsic_value']:.2f}")

    if result['current_price']:
        print(f"Current Price: ${result['current_price']:.2f}")
        if result['margin_of_safety'] is not None:
            print(f"Margin of Safety: {result['margin_of_safety']:.1%}")

    print(f"\nEnterprise Value: ${result['enterprise_value']:.2f}M")
    print(f"Terminal Value: ${result['terminal_value']:.2f}M")
    print(f"PV of FCF: ${result['pv_fcf']:.2f}M")

    if args.json:
        print(json.dumps(result, indent=2))


def cmd_tech(args):
    """技术指标命令"""
    analyzer = TechnicalAnalyzer()

    indicators = args.indicators.split(",") if args.indicators else ["sma", "ema", "rsi", "macd"]

    # 如果没有提供价格数据，生成模拟数据
    if args.prices:
        prices = [float(p) for p in args.prices.split(",")]
    else:
        import numpy as np
        np.random.seed(42)
        prices = list(100 + np.cumsum(np.random.randn(50) * 2))

    result = analyzer.calculate(prices, indicators)
    signals = analyzer.signals(args.ticker or "UNKNOWN", result)

    print(f"\n{'='*50}")
    print(f"Technical Analysis for {signals['ticker']}")
    print(f"{'='*50}")
    print(f"Combined Signal: {signals['combined'].upper()}")

    print(f"\nIndicator Details:")
    for name, data in result.items():
        if isinstance(data, dict):
            if "value" in data:
                print(f"  {name.upper()}: {data['value']} ({data.get('signal', 'neutral')})")
            elif "macd" in data:
                print(f"  {name.upper()}: MACD={data['macd']}, Signal={data['signal_line']}, Hist={data['histogram']}")

    print(f"\nSignal Count: Bullish={signals['bullish_count']}, Bearish={signals['bearish_count']}, Neutral={signals['neutral_count']}")

    if args.json:
        print(json.dumps({"indicators": result, "signals": signals}, indent=2))


def cmd_greeks(args):
    """Greeks计算命令"""
    analyzer = OptionsAnalyzer()

    if args.chain:
        # 生成期权链
        chain = analyzer.option_chain(
            ticker=args.ticker or "UNKNOWN",
            S=args.S,
            expiration=args.expiration or "2026-05-16",
            risk_free=args.r or 0.05,
            sigma=args.sigma or 0.25,
        )

        print(f"\n{'='*50}")
        print(f"Option Chain for {chain['ticker']}")
        print(f"{'='*50}")
        print(f"Underlying Price: ${chain['underlying_price']}")
        print(f"Expiration: {chain['expiration']}")

        print(f"\nCalls:")
        for c in chain["calls"]:
            print(f"  K=${c['strike']:.0f}: Bid=${c['bid']:.2f}, Ask=${c['ask']:.2f}, Delta={c['delta']:.3f}")

        print(f"\nPuts:")
        for p in chain["puts"]:
            print(f"  K=${p['strike']:.0f}: Bid=${p['bid']:.2f}, Ask=${p['ask']:.2f}, Delta={p['delta']:.3f}")

        if args.json:
            print(json.dumps(chain, indent=2))

    else:
        # 计算Greeks
        greeks = analyzer.greeks(
            S=args.S,
            K=args.K,
            T=args.T,
            r=args.r or 0.05,
            sigma=args.sigma or 0.25,
        )

        bs_price = analyzer.black_scholes(args.S, args.K, args.T, args.r or 0.05, args.sigma or 0.25)

        print(f"\n{'='*50}")
        print(f"Option Greeks")
        print(f"{'='*50}")
        print(f"Spot: ${args.S}, Strike: ${args.K}, Maturity: {args.T}y, Vol: {args.sigma or 0.25:.0%}")
        print(f"\nBlack-Scholes Price: ${bs_price:.4f}")
        print(f"\nGreeks:")
        print(f"  Delta: {greeks['delta']:.4f}")
        print(f"  Gamma: {greeks['gamma']:.6f}")
        print(f"  Theta: {greeks['theta']:.4f}/day")
        print(f"  Vega: {greeks['vega']:.4f}/vol")
        print(f"  Rho: {greeks['rho']:.4f}")

        if args.json:
            print(json.dumps({"greeks": greeks, "black_scholes": bs_price}, indent=2))


def cmd_risk(args):
    """风险指标命令"""
    analyzer = RiskAnalyzer()

    # 解析收益率
    if args.returns:
        returns = [float(r) for r in args.returns.split(",")]
    else:
        import numpy as np
        np.random.seed(42)
        returns = list(np.random.normal(0.001, 0.02, 252))

    print(f"\n{'='*50}")
    print(f"Risk Analysis")
    print(f"{'='*50}")

    # VaR
    var_95 = analyzer.value_at_risk(returns, confidence=0.95)
    var_99 = analyzer.value_at_risk(returns, confidence=0.99)
    print(f"\nValue at Risk:")
    print(f"  95% VaR: {var_95:.4%}")
    print(f"  99% VaR: {var_99:.4%}")

    # CVaR
    cvar_95 = analyzer.cvar(returns, confidence=0.95)
    print(f"\nConditional VaR:")
    print(f"  95% CVaR: {cvar_95:.4%}")

    # 夏普比率
    sharpe = analyzer.sharpe_ratio(returns, risk_free=args.rf or 0.04)
    sortino = analyzer.sortino_ratio(returns, risk_free=args.rf or 0.04)
    print(f"\nReturn Metrics:")
    print(f"  Sharpe Ratio: {sharpe:.4f}")
    print(f"  Sortino Ratio: {sortino:.4f}")

    # 最大回撤
    max_dd = analyzer.max_drawdown(returns)
    calmar = analyzer.calmar_ratio(returns)
    print(f"\nDrawdown Metrics:")
    print(f"  Max Drawdown: {max_dd:.4%}")
    print(f"  Calmar Ratio: {calmar:.4f}")

    # 统计检验
    if len(returns) >= 20:
        jb = analyzer.jarque_bera(returns)
        lb = analyzer.ljung_box(returns, lags=args.lags or 10)

        print(f"\nStatistical Tests:")
        print(f"  Jarque-Bera: stat={jb['jb_stat']:.4f}, p={jb['p_value']:.4f} -> {jb['conclusion']}")
        print(f"  Ljung-Box: stat={lb['lb_stat']:.4f}, p={lb['p_value']:.4f} -> {lb['conclusion']}")

    if args.json:
        result = {
            "var_95": var_95,
            "var_99": var_99,
            "cvar_95": cvar_95,
            "sharpe": sharpe,
            "sortino": sortino,
            "max_drawdown": max_dd,
            "calmar": calmar,
        }
        print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Fincept Quant Analytics CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # DCF command
    dcf_parser = subparsers.add_parser("dcf", help="DCF valuation analysis")
    dcf_parser.add_argument("ticker", help="Stock ticker")
    dcf_parser.add_argument("--revenue", type=float, default=100.0, help="Current annual revenue (millions)")
    dcf_parser.add_argument("--growth", type=float, default=0.08, help="Revenue growth rate")
    dcf_parser.add_argument("--margin", type=float, default=0.20, help="Operating margin")
    dcf_parser.add_argument("--discount", type=float, default=0.10, help="Discount rate (WACC)")
    dcf_parser.add_argument("--terminal", type=float, default=0.03, help="Terminal growth rate")
    dcf_parser.add_argument("--years", type=int, default=5, help="Projection years")
    dcf_parser.add_argument("--shares", type=float, default=1.0, help="Shares outstanding (millions)")
    dcf_parser.add_argument("--net-debt", type=float, help="Net debt (millions)")
    dcf_parser.add_argument("--price", type=float, help="Current stock price")
    dcf_parser.add_argument("--json", action="store_true", help="Output as JSON")
    dcf_parser.set_defaults(func=cmd_dcf)

    # Tech command
    tech_parser = subparsers.add_parser("tech", help="Technical analysis")
    tech_parser.add_argument("ticker", nargs="?", help="Stock ticker")
    tech_parser.add_argument("--prices", help="Comma-separated price list")
    tech_parser.add_argument("--indicators", help="Comma-separated indicator list (sma,ema,rsi,macd,bbands,atr)")
    tech_parser.add_argument("--json", action="store_true", help="Output as JSON")
    tech_parser.set_defaults(func=cmd_tech)

    # Greeks command
    greeks_parser = subparsers.add_parser("greeks", help="Option Greeks calculation")
    greeks_parser.add_argument("--ticker", help="Stock ticker")
    greeks_parser.add_argument("--S", type=float, required=True, help="Spot price")
    greeks_parser.add_argument("--K", type=float, required=True, help="Strike price")
    greeks_parser.add_argument("--T", type=float, required=True, help="Time to expiration (years)")
    greeks_parser.add_argument("--r", type=float, default=0.05, help="Risk-free rate")
    greeks_parser.add_argument("--sigma", type=float, default=0.25, help="Volatility")
    greeks_parser.add_argument("--chain", action="store_true", help="Generate option chain")
    greeks_parser.add_argument("--expiration", help="Expiration date (YYYY-MM-DD)")
    greeks_parser.add_argument("--json", action="store_true", help="Output as JSON")
    greeks_parser.set_defaults(func=cmd_greeks)

    # Risk command
    risk_parser = subparsers.add_parser("risk", help="Risk metrics calculation")
    risk_parser.add_argument("--returns", help="Comma-separated return list")
    risk_parser.add_argument("--rf", type=float, default=0.04, help="Risk-free rate")
    risk_parser.add_argument("--lags", type=int, default=10, help="Ljung-Box lags")
    risk_parser.add_argument("--json", action="store_true", help="Output as JSON")
    risk_parser.set_defaults(func=cmd_risk)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()