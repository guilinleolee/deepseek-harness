"""Risk Parity portfolio optimization using Riskfolio-Lib."""

from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
import yfinance as yf


class RiskParityOptimizer:
    """Risk Parity / Risk Budgeting portfolio optimizer."""

    def __init__(self, risk_free_rate: float = 0.04):
        """
        Initialize Risk Parity optimizer.

        Args:
            risk_free_rate: Risk-free rate for Sharpe calculation
        """
        self.risk_free_rate = risk_free_rate
        self._prices_cache: Dict[str, pd.DataFrame] = {}

    def _fetch_prices(
        self, tickers: List[str], start_date: str = "2019-01-01", end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch adjusted closing prices."""
        cache_key = ",".join(tickers)
        if cache_key in self._prices_cache:
            return self._prices_cache[cache_key]

        prices = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True)["Close"]
        self._prices_cache[cache_key] = prices.dropna()
        return self._prices_cache[cache_key]

    def risk_parity(
        self,
        tickers: List[str],
        risk_measure: str = "volatility",
        start_date: str = "2019-01-01",
        end_date: Optional[str] = None,
        target_risk: Optional[List[float]] = None,
    ) -> Dict[str, Union[float, Dict[str, float]]]:
        """
        Calculate risk parity weights.

        Args:
            tickers: List of stock tickers
            risk_measure: Risk measure (volatility, cvar, drawdown)
            start_date: Start date for historical data
            end_date: End date for historical data
            target_risk: Target risk contributions (equal if None)

        Returns:
            Dict with expected_return, volatility, sharpe_ratio, weights
        """
        prices = self._fetch_prices(tickers, start_date, end_date)
        returns = prices.pct_change().dropna()

        cov_matrix = returns.cov() * 252
        vols = np.sqrt(np.diag(cov_matrix))

        if target_risk is None:
            target_risk = np.ones(len(tickers)) / len(tickers)
        target_risk = np.array(target_risk) / np.sum(target_risk)

        cov_inv = np.linalg.pinv(cov_matrix.values)
        ones = np.ones(len(tickers))
        denominator = ones @ cov_inv @ ones
        risk_budget_weights = cov_inv @ ones / denominator

        if target_risk is not None:
            scale = (cov_matrix.values @ risk_budget_weights) / (vols * target_risk)
            risk_budget_weights = risk_budget_weights / np.sqrt(scale @ cov_matrix.values @ scale)

        weights = risk_budget_weights / risk_budget_weights.sum()

        w_series = pd.Series(weights, index=tickers)
        port_returns = (returns * w_series).sum(axis=1)
        expected_return = port_returns.mean() * 252
        volatility = port_returns.std() * np.sqrt(252)
        sharpe = (expected_return - self.risk_free_rate) / volatility if volatility > 0 else 0

        return {
            "expected_return": float(expected_return),
            "volatility": float(volatility),
            "sharpe_ratio": float(sharpe),
            "weights": {t: round(float(w), 4) for t, w in zip(tickers, weights) if abs(w) > 1e-4},
        }

    def risk_budget(
        self,
        tickers: List[str],
        risk_budget: Dict[str, float],
        start_date: str = "2019-01-01",
        end_date: Optional[str] = None,
    ) -> Dict[str, Union[float, Dict[str, float]]]:
        """
        Allocate risk budget to each asset.

        Args:
            tickers: List of stock tickers
            risk_budget: Dict mapping ticker to target risk contribution (e.g., {"AAPL": 0.3})
            start_date: Start date for historical data
            end_date: End date for historical data

        Returns:
            Dict with portfolio metrics and weights
        """
        prices = self._fetch_prices(tickers, start_date, end_date)
        returns = prices.pct_change().dropna()

        cov_matrix = returns.cov() * 252
        vols = np.sqrt(np.diag(cov_matrix))

        total_risk = np.sum(list(risk_budget.values()))
        target_risk = np.array([risk_budget.get(t, 0.0) for t in tickers]) / total_risk

        cov_inv = np.linalg.pinv(cov_matrix.values)
        ones = np.ones(len(tickers))
        base_weights = cov_inv @ ones / (ones @ cov_inv @ ones)

        scale = (cov_matrix.values @ base_weights) / (vols * target_risk + 1e-10)
        risk_parity_w = base_weights / np.sqrt(scale @ cov_matrix.values @ scale + 1e-10)
        weights = risk_parity_w / risk_parity_w.sum()

        w_series = pd.Series(weights, index=tickers)
        port_returns = (returns * w_series).sum(axis=1)
        expected_return = port_returns.mean() * 252
        volatility = port_returns.std() * np.sqrt(252)
        sharpe = (expected_return - self.risk_free_rate) / volatility if volatility > 0 else 0

        return {
            "expected_return": float(expected_return),
            "volatility": float(volatility),
            "sharpe_ratio": float(sharpe),
            "weights": {t: round(float(w), 4) for t, w in zip(tickers, weights) if abs(w) > 1e-4},
        }