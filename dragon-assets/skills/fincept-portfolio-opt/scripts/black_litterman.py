"""Black-Litterman asset allocation model."""

from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
import yfinance as yf


class BlackLittermanOptimizer:
    """Black-Litterman Bayesian portfolio optimization."""

    def __init__(self, risk_free_rate: float = 0.04, tau: float = 0.05):
        """
        Initialize Black-Litterman optimizer.

        Args:
            risk_free_rate: Risk-free rate for Sharpe calculation
            tau: Uncertainty parameter for views (default 5%)
        """
        self.risk_free_rate = risk_free_rate
        self.tau = tau
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

    def black_litterman(
        self,
        tickers: List[str],
        market_cap: Optional[List[float]] = None,
        views: Optional[Dict[str, float]] = None,
        view_confidence: float = 0.7,
        start_date: str = "2019-01-01",
        end_date: Optional[str] = None,
    ) -> Dict[str, Union[float, Dict[str, float]]]:
        """
        Calculate Black-Litterman optimal weights.

        Args:
            tickers: List of stock tickers
            market_cap: Market capitalizations in trillions (for equilibrium returns)
            views: Dict of ticker -> expected return from views
            view_confidence: Confidence level for views (0 to 1)
            start_date: Start date for historical data
            end_date: End date for historical data

        Returns:
            Dict with expected_return, volatility, sharpe_ratio, weights
        """
        prices = self._fetch_prices(tickers, start_date, end_date)
        returns = prices.pct_change().dropna()

        if market_cap is None:
            market_cap = np.ones(len(tickers)) / len(tickers)
        mcap_weights = np.array(market_cap) / np.sum(market_cap)

        cov_matrix = returns.cov() * 252
        risk_aversion = (returns.mean().mean() - self.risk_free_rate) / (returns.std().mean() ** 2 * 252)

        equilibrium_returns = risk_aversion * cov_matrix.values @ mcap_weights

        if views is None:
            views = {}
        if not views:
            mu = equilibrium_returns
            cov_adjusted = cov_matrix.values
        else:
            view_returns = np.array([views.get(t, equilibrium_returns[i]) for i, t in enumerate(tickers)])
            view_scores = np.array([views.get(t, 0) for t in tickers])
            has_view = np.abs(view_scores) > 1e-9

            confidence = view_confidence * np.ones(len(tickers))
            omega = np.diag(np.diag(cov_matrix.values) * (1 - has_view) + np.diag(np.diag(cov_matrix.values)) * (1 - confidence) * self.tau)

            view_vector = view_returns - equilibrium_returns
            P = np.eye(len(tickers))[has_view]
            Q = view_vector[has_view]

            if P.shape[0] > 0:
                M = np.linalg.inv(np.linalg.inv(self.tau * cov_matrix.values) + P.T @ np.linalg.inv(omega) @ P)
                mu_bl = M @ (np.linalg.inv(self.tau * cov_matrix.values) @ equilibrium_returns + P.T @ np.linalg.inv(omega) @ Q)
            else:
                mu_bl = equilibrium_returns

            mu = mu_bl
            cov_adjusted = cov_matrix.values + self.tau * cov_matrix.values

        weights = np.linalg.inv(risk_aversion * cov_adjusted) @ mu / np.sum(np.linalg.inv(risk_aversion * cov_adjusted) @ mu)
        weights = np.maximum(weights, 0.01)
        weights = weights / np.sum(weights)

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
            "equilibrium_returns": {t: round(float(r), 4) for t, r in zip(tickers, equilibrium_returns)},
            "posterior_returns": {t: round(float(r), 4) for t, r in zip(tickers, mu)},
        }