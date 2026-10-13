"""CLI for Fincept Portfolio Optimizer."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.optimizer import PortfolioOptimizer
from scripts.risk_parity import RiskParityOptimizer
from scripts.black_litterman import BlackLittermanOptimizer
from scripts.factor_model import FactorModelOptimizer
from scripts.attribution import BrinsonAttribution


def cmd_optimize(args):
    """Run portfolio optimization."""
    tickers = args.tickers.split(",")
    optimizer = PortfolioOptimizer(risk_free_rate=args.risk_free_rate)

    constraints = {
        "max_weight": args.max_weight,
        "min_weight": args.min_weight,
        "max_leverage": 1.0,
    }

    result = optimizer.optimize(
        tickers=tickers,
        objective=args.objective,
        constraints=constraints,
    )

    print(f"\n{'='*60}")
    print(f"  Portfolio Optimization Results")
    print(f"{'='*60}")
    print(f"  Objective: {args.objective}")
    print(f"  Expected Return: {result['expected_return']:.2%}")
    print(f"  Volatility:     {result['volatility']:.2%}")
    print(f"  Sharpe Ratio:    {result['sharpe_ratio']:.4f}")
    print(f"\n  Weights:")
    for ticker, weight in sorted(result["weights"].items(), key=lambda x: -x[1]):
        bar = "#" * int(weight * 100)
        print(f"    {ticker:<8} {weight:>7.2%}  {bar}")
    print(f"{'='*60}\n")


def cmd_frontier(args):
    """Calculate efficient frontier."""
    tickers = args.tickers.split(",")
    optimizer = PortfolioOptimizer(risk_free_rate=args.risk_free_rate)

    frontier = optimizer.efficient_frontier(tickers=tickers, points=args.points)

    print(f"\n{'='*60}")
    print(f"  Efficient Frontier ({len(frontier)} points)")
    print(f"{'='*60}")
    print(f"  {'Return':<12} {'Volatility':<12} {'Sharpe':<10}")
    print(f"  {'-'*34}")
    for ret, vol, _ in frontier:
        sharpe = (ret - args.risk_free_rate) / vol if vol > 0 else 0
        print(f"  {ret:>10.2%}  {vol:>10.2%}  {sharpe:>8.4f}")
    print(f"{'='*60}\n")


def cmd_risk_parity(args):
    """Calculate risk parity portfolio."""
    tickers = args.tickers.split(",")
    optimizer = RiskParityOptimizer(risk_free_rate=args.risk_free_rate)

    result = optimizer.risk_parity(tickers=tickers, risk_measure=args.risk_measure)

    print(f"\n{'='*60}")
    print(f"  Risk Parity Portfolio")
    print(f"{'='*60}")
    print(f"  Risk Measure: {args.risk_measure}")
    print(f"  Expected Return: {result['expected_return']:.2%}")
    print(f"  Volatility:     {result['volatility']:.2%}")
    print(f"  Sharpe Ratio:    {result['sharpe_ratio']:.4f}")
    print(f"\n  Weights:")
    for ticker, weight in sorted(result["weights"].items(), key=lambda x: -x[1]):
        bar = "#" * int(weight * 100)
        print(f"    {ticker:<8} {weight:>7.2%}  {bar}")
    print(f"{'='*60}\n")


def cmd_bl(args):
    """Run Black-Litterman optimization."""
    tickers = args.tickers.split(",")
    optimizer = BlackLittermanOptimizer(risk_free_rate=args.risk_free_rate)

    views = json.loads(args.views) if args.views else None

    result = optimizer.black_litterman(
        tickers=tickers,
        market_cap=args.market_cap,
        views=views,
        view_confidence=args.confidence,
    )

    print(f"\n{'='*60}")
    print(f"  Black-Litterman Portfolio")
    print(f"{'='*60}")
    if views:
        print(f"  Views: {views}")
        print(f"  Confidence: {args.confidence:.0%}")
    print(f"  Expected Return: {result['expected_return']:.2%}")
    print(f"  Volatility:     {result['volatility']:.2%}")
    print(f"  Sharpe Ratio:    {result['sharpe_ratio']:.4f}")
    print(f"\n  Equilibrium vs Posterior Returns:")
    for ticker in tickers:
        eq = result["equilibrium_returns"].get(ticker, 0)
        po = result["posterior_returns"].get(ticker, 0)
        print(f"    {ticker:<8} Eq: {eq:>7.2%}  Po: {po:>7.2%}")
    print(f"\n  Weights:")
    for ticker, weight in sorted(result["weights"].items(), key=lambda x: -x[1]):
        bar = "#" * int(weight * 100)
        print(f"    {ticker:<8} {weight:>7.2%}  {bar}")
    print(f"{'='*60}\n")


def cmd_factor(args):
    """Run factor model analysis."""
    optimizer = FactorModelOptimizer(risk_free_rate=args.risk_free_rate)

    result = optimizer.factor_model(
        returns=None,
        tickers=args.tickers.split(",") if args.tickers else None,
        factor_type=args.factor_type,
    )

    print(f"\n{'='*60}")
    print(f"  Factor Model ({args.factor_type.upper()})")
    print(f"{'='*60}")
    print(f"  Alpha:     {result['alpha']:.4f}")
    print(f"  R-squared: {result['r_squared']:.4f}")
    print(f"  Idiosyncratic Vol: {result['idiosyncratic_vol']:.2%}")
    print(f"\n  Factor Betas:")
    for factor, beta in result["betas"].items():
        sign = "+" if beta >= 0 else ""
        print(f"    {factor:<12} {sign}{beta:.4f}")
    print(f"\n  Factor Returns (Annual):")
    for factor, ret in result["factor_returns"].items():
        print(f"    {factor:<12} {ret:>8.2%}")
    print(f"{'='*60}\n")


def cmd_attribution(args):
    """Run Brinson attribution."""
    with open(args.portfolio_weights) as f:
        pw = json.load(f)
    with open(args.benchmark_weights) as f:
        bw = json.load(f)

    if args.periods:
        with open(args.portfolio_returns) as f:
            pr = json.load(f)
        with open(args.benchmark_returns) as f:
            br = json.load(f)

        optimizer = BrinsonAttribution()
        result = optimizer.multi_period_brinson(pw, bw, pr, br)
    else:
        pr_list = list(pw.values()) if isinstance(pw, dict) else pw
        br_list = list(bw.values()) if isinstance(bw, dict) else bw

        optimizer = BrinsonAttribution()
        result = optimizer.brinson(pw, bw, pr_list, br_list)

    print(f"\n{'='*60}")
    print(f"  Brinson Attribution")
    print(f"{'='*60}")
    print(f"  Allocation Effect:   {result['allocation']:>10.4%}")
    print(f"  Selection Effect:    {result['selection']:>10.4%}")
    print(f"  Interaction Effect:  {result['interaction']:>10.4%}")
    print(f"  Total Active Return: {result['total_active_return']:>10.4%}")
    print(f"  Portfolio Return:    {result['portfolio_return']:>10.4%}")
    print(f"  Benchmark Return:    {result['benchmark_return']:>10.4%}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Fincept Portfolio Optimizer CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # optimize
    p_optimize = subparsers.add_parser("optimize", help="Optimize portfolio")
    p_optimize.add_argument("--tickers", required=True, help="Comma-separated tickers")
    p_optimize.add_argument("--objective", default="max_sharpe", choices=["max_sharpe", "min_volatility", "max_return"])
    p_optimize.add_argument("--max-weight", type=float, default=0.3)
    p_optimize.add_argument("--min-weight", type=float, default=0.05)
    p_optimize.add_argument("--risk-free-rate", type=float, default=0.04)
    p_optimize.set_defaults(func=cmd_optimize)

    # frontier
    p_frontier = subparsers.add_parser("frontier", help="Calculate efficient frontier")
    p_frontier.add_argument("--tickers", required=True, help="Comma-separated tickers")
    p_frontier.add_argument("--points", type=int, default=50)
    p_frontier.add_argument("--risk-free-rate", type=float, default=0.04)
    p_frontier.set_defaults(func=cmd_frontier)

    # risk-parity
    p_rp = subparsers.add_parser("risk-parity", help="Calculate risk parity portfolio")
    p_rp.add_argument("--tickers", required=True, help="Comma-separated tickers")
    p_rp.add_argument("--risk-measure", default="volatility", choices=["volatility", "cvar", "drawdown"])
    p_rp.add_argument("--risk-free-rate", type=float, default=0.04)
    p_rp.set_defaults(func=cmd_risk_parity)

    # bl
    p_bl = subparsers.add_parser("bl", help="Black-Litterman optimization")
    p_bl.add_argument("--tickers", required=True, help="Comma-separated tickers")
    p_bl.add_argument("--market-cap", type=float, nargs="+", help="Market caps in trillions")
    p_bl.add_argument("--views", help="JSON string of views")
    p_bl.add_argument("--confidence", type=float, default=0.7)
    p_bl.add_argument("--risk-free-rate", type=float, default=0.04)
    p_bl.set_defaults(func=cmd_bl)

    # factor
    p_factor = subparsers.add_parser("factor", help="Factor model analysis")
    p_factor.add_argument("--tickers", help="Comma-separated tickers")
    p_factor.add_argument("--factor-type", default="ff5", choices=["ff3", "ff5", "carhart"])
    p_factor.add_argument("--risk-free-rate", type=float, default=0.04)
    p_factor.set_defaults(func=cmd_factor)

    # attribution
    p_attr = subparsers.add_parser("attribution", help="Brinson attribution")
    p_attr.add_argument("--portfolio-weights", required=True, help="JSON file for portfolio weights")
    p_attr.add_argument("--benchmark-weights", required=True, help="JSON file for benchmark weights")
    p_attr.add_argument("--portfolio-returns", help="JSON file for portfolio returns (multi-period)")
    p_attr.add_argument("--benchmark-returns", help="JSON file for benchmark returns (multi-period)")
    p_attr.add_argument("--periods", action="store_true", help="Multi-period attribution")
    p_attr.set_defaults(func=cmd_attribution)

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()