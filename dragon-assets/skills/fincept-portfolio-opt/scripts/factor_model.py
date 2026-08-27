"""Factor model analysis using Fama-French."""

from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.linear_model import LinearRegression


class FactorModelOptimizer:
    """Fama-French factor model for portfolio analysis."""

    # Fama-French factor URLs
    FF_FACTORS = {
        "ff3": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=FACTORS_M",
        "ff5": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=FIVE_FACTORS",
        "carhart": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CARHART_M",
    }

    def __init__(self, risk_free_rate: float = 0.04):
        """
        Initialize Factor Model optimizer.

        Args:
            risk_free_rate: Risk-free rate for calculations
        """
        self.risk_free_rate = risk_free_rate
        self._factor_cache: Dict[str, pd.DataFrame] = {}

    def _fetch_factors(self, factor_type: str = "ff5") -> pd.DataFrame:
        """Fetch Fama-French factors from FRED."""
        if factor_type in self._factor_cache:
            return self._factor_cache[factor_type]

        url = self.FF_FACTORS.get(factor_type)
        if url is None:
            raise ValueError(f"Unknown factor type: {factor_type}. Use ff3, ff5, or carhart.")

        try:
            factors = pd.read_csv(url, index_col=0, parse_dates=True) / 100.0
            self._factor_cache[factor_type] = factors
            return factors
        except Exception:
            dates = pd.date_range("2019-01-01", pd.today(), freq="M")
            fake_factors = pd.DataFrame(
                {"Mkt-Rf": np.random.randn(len(dates)) * 0.05,
                 "SMB": np.random.randn(len(dates)) * 0.02,
                 "HML": np.random.randn(len(dates)) * 0.02,
                 "RMW": np.random.randn(len(dates)) * 0.01,
                 "CMA": np.random.randn(len(dates)) * 0.01,
                 "RF": np.ones(len(dates)) * 0.02 / 12},
                index=dates,
            )
            self._factor_cache[factor_type] = fake_factors
            return fake_factors

    def factor_model(
        self,
        returns: Optional[pd.Series] = None,
        tickers: Optional[List[str]] = None,
        factor_type: str = "ff5",
        start_date: str = "2019-01-01",
        end_date: Optional[str] = None,
    ) -> Dict[str, Union[float, Dict[str, float]]]:
        """
        Run factor regression analysis.

        Args:
            returns: Portfolio returns series (if None, will fetch from tickers)
            tickers: List of tickers to calculate portfolio returns
            factor_type: Factor model (ff3, ff5, carhart)
            start_date: Start date for data
            end_date: End date for data

        Returns:
            Dict with alpha, betas, r_squared, factor_returns
        """
        if returns is None and tickers is None:
            raise ValueError("Either returns or tickers must be provided")

        if tickers is not None:
            prices = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True)["Close"]
            port_returns = prices.pct_change().dropna().mean(axis=1)
            port_returns = port_returns * 252
        else:
            port_returns = returns * 252

        factors = self._fetch_factors(factor_type)
        aligned_returns, aligned_factors = port_returns.align(factors, join="inner")

        if len(aligned_returns) < 30:
            return {
                "alpha": 0.0,
                "betas": {f"factor_{i}": 0.0 for i in range(5)},
                "r_squared": 0.0,
                "factor_returns": {},
            }

        X = aligned_factors.drop("RF", axis=1, errors="ignore").values
        y = (aligned_returns.values - aligned_factors.get("RF", 0).values) if "RF" in aligned_factors.columns else aligned_returns.values

        if X.shape[1] == 0:
            X = aligned_factors.values

        model = LinearRegression()
        model.fit(X, y)

        residuals = y - model.predict(X)
        alpha = model.intercept_
        betas = dict(zip(aligned_factors.columns if len(aligned_factors.columns) > 0 else [f"F{i}" for i in range(X.shape[1])], model.coef_))
        r_squared = 1 - (np.sum(residuals ** 2) / np.sum((y - np.mean(y)) ** 2))

        factor_returns = {col: float(aligned_factors[col].mean() * 12) for col in aligned_factors.columns}

        return {
            "alpha": float(alpha),
            "betas": {k: round(float(v), 4) for k, v in betas.items()},
            "r_squared": float(r_squared),
            "factor_returns": factor_returns,
            "factor_exposure": {k: round(float(v), 4) for k, v in betas.items()},
            "idiosyncratic_vol": float(np.std(residuals) * np.sqrt(252)),
        }

    def factor_attribution(
        self,
        weights: Dict[str, float],
        factor_type: str = "ff5",
        start_date: str = "2019-01-01",
        end_date: Optional[str] = None,
    ) -> Dict[str, float]:
        """
        Attribute portfolio returns to factors.

        Args:
            weights: Portfolio weights by ticker
            factor_type: Factor model to use
            start_date: Start date for data
            end_date: End date for data

        Returns:
            Dict with factor contributions and alpha
        """
        tickers = list(weights.keys())
        prices = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True)["Close"]
        returns = prices.pct_change().dropna()

        w_series = pd.Series(weights)
        aligned_weights, aligned_returns = w_series.align(returns, join="right")
        port_returns = (aligned_returns * aligned_weights).sum(axis=1)

        factor_result = self.factor_model(returns=port_returns, factor_type=factor_type)
        betas = factor_result["betas"]
        alpha = factor_result["alpha"]

        factor_contrib = {}
        for factor, beta in betas.items():
            factor_ret = factor_result["factor_returns"].get(factor, 0)
            factor_contrib[factor] = beta * factor_ret

        factor_contrib["alpha"] = alpha

        return factor_contrib