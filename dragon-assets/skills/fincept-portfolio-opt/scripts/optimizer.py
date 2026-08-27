"""Portfolio optimization core module using PyPortfolioOpt."""

import warnings
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import yfinance as yf
from pypfopt import (
    EfficientFrontier,
    HRPOpt,
    risk_models,
    expected_returns,
    objective_functions,
)
from pypfopt.risk_models import CovarianceShrinkage


class PortfolioOptimizer:
    """Institutional-grade portfolio optimization wrapper."""

    def __init__(self, risk_free_rate: float = 0.04):
        """
        Initialize optimizer.

        Args:
            risk_free_rate: Risk-free rate for Sharpe ratio calculation (default 4%)
        """
        self.risk_free_rate = risk_free_rate
        self._prices_cache: Dict[str, pd.DataFrame] = {}

    def _fetch_prices(
        self, tickers: List[str], start_date: str = "2019-01-01", end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch adjusted closing prices from Yahoo Finance."""
        cache_key = ",".join(tickers)
        if cache_key in self._prices_cache:
            return self._prices_cache[cache_key]

        prices = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True)["Close"]
        if prices.isnull().all().any():
            tickers_with_nan = prices.columns[prices.isnull().all()].tolist()
            raise ValueError(f"Failed to fetch data for: {tickers_with_nan}")
        self._prices_cache[cache_key] = prices.dropna()
        return self._prices_cache[cache_key]

    def _get_cov_matrix(self, prices: pd.DataFrame, method: str = "shrunk") -> pd.DataFrame:
        """Calculate covariance matrix with shrinkage."""
        if method == "shrunk":
            return CovarianceShrinkage(prices).ledoit_wolf()
        return risk_models.sample_cov(prices)

    def _get_expected_returns(self, prices: pd.DataFrame, method: str = "capm") -> pd.Series:
        """Calculate expected returns."""
        if method == "capm":
            return expected_returns.capm_return(prices)
        return expected_returns.mean_historical_return(prices)

    def optimize(
        self,
        tickers: List[str],
        objective: str = "max_sharpe",
        constraints: Optional[Dict[str, float]] = None,
        start_date: str = "2019-01-01",
        end_date: Optional[str] = None,
        market_ticker: str = "^SPX",
    ) -> Dict[str, Union[float, Dict[str, float]]]:
        """
        Optimize portfolio weights.

        Args:
            tickers: List of stock tickers
            objective: Optimization objective (max_sharpe, min_volatility, max_return)
            constraints: Dict with max_weight, min_weight, etc.
            start_date: Start date for historical data
            end_date: End date for historical data
            market_ticker: Market ticker for CAPM model

        Returns:
            Dict with expected_return, volatility, sharpe_ratio, weights
        """
        constraints = constraints or {}
        max_weight = constraints.get("max_weight", 0.3)
        min_weight = constraints.get("min_weight", 0.05)
        max_leverage = constraints.get("max_leverage", 1.0)

        prices = self._fetch_prices(tickers, start_date, end_date)
        n = len(tickers)

        mu = self._get_expected_returns(prices, method="capm")
        S = self._get_cov_matrix(prices, method="shrunk")

        ef = EfficientFrontier(mu, S, weight_bounds=(min_weight, max_weight), gamma=0)

        if objective == "max_sharpe":
            ef.maximize_sharpe(risk_free_rate=self.risk_free_rate)
        elif objective == "min_volatility":
            ef.minimize_volatility()
        elif objective == "max_return":
            ef.maximize_return()
        else:
            raise ValueError(f"Unknown objective: {objective}")

        weights = ef.clean_weights()
        portfolio_return = ef.portfolio_return()
        volatility = ef.portfolio_volatility()
        sharpe = ef.portfolio_sharpe(risk_free_rate=self.risk_free_rate)

        return {
            "expected_return": portfolio_return,
            "volatility": volatility,
            "sharpe_ratio": sharpe,
            "weights": {k: round(v, 4) for k, v in weights.items() if abs(v) > 1e-4},
        }

    def efficient_frontier(
        self,
        tickers: List[str],
        points: int = 50,
        start_date: str = "2019-01-01",
        end_date: Optional[str] = None,
    ) -> List[Tuple[float, float, Dict[str, float]]]:
        """
        Calculate efficient frontier.

        Args:
            tickers: List of stock tickers
            points: Number of points on frontier
            start_date: Start date for historical data
            end_date: End date for historical data

        Returns:
            List of (return, volatility, weights) tuples
        """
        prices = self._fetch_prices(tickers, start_date, end_date)
        n = len(tickers)

        mu = self._get_expected_returns(prices)
        S = self._get_cov_matrix(prices)

        ef = EfficientFrontier(mu, S, weight_bounds=(0.05, 0.3))

        ret_range = ef.efficient_return(target_return=min(mu) * 1.5, full_output=False)
        vol_range = ef.efficient_frontier(
            points=points, show_values=False, ax=None, ci=60, method="linprog"
        )

        mu_min = min(mu)
        mu_max = max(mu) * 1.2

        results = []
        target_returns = np.linspace(mu_min, mu_max, points)
        for target_ret in target_returns:
            try:
                ef_i = EfficientFrontier(mu, S, weight_bounds=(0.05, 0.3))
                ef_i.efficient_return(target_return=target_ret)
                weights = ef_i.clean_weights()
                ret = ef_i.portfolio_return()
                vol = ef_i.portfolio_volatility()
                results.append((ret, vol, {k: round(v, 4) for k, v in weights.items() if abs(v) > 1e-4}))
            except Exception:
                continue

        return results

    def hrp_portfolio(
        self,
        tickers: List[str],
        start_date: str = "2019-01-01",
        end_date: Optional[str] = None,
    ) -> Dict[str, Union[float, Dict[str, float]]]:
        """
        Hierarchical Risk Parity portfolio.
        """
        prices = self._fetch_prices(tickers, start_date, end_date)
        returns = prices.pct_change().dropna()

        cov_matrix = risk_models.sample_cov(returns)
        hrp = HRPOpt(returns, cov_matrix)
        hrp.optimize()

        weights = hrp.clean_weights()
        returns_portfolio = (returns * pd.Series(weights)).sum(axis=1)
        expected_return = returns_portfolio.mean() * 252
        volatility = returns_portfolio.std() * np.sqrt(252)
        sharpe = (expected_return - self.risk_free_rate) / volatility

        return {
            "expected_return": expected_return,
            "volatility": volatility,
            "sharpe_ratio": sharpe,
            "weights": {k: round(v, 4) for k, v in weights.items() if abs(v) > 1e-4},
        }