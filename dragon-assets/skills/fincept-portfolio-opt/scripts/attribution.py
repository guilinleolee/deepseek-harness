"""Brinson performance attribution model."""

from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd


class BrinsonAttribution:
    """Brinson model for portfolio performance attribution."""

    def __init__(self, risk_free_rate: float = 0.04):
        """
        Initialize Brinson Attribution model.

        Args:
            risk_free_rate: Risk-free rate for calculations
        """
        self.risk_free_rate = risk_free_rate

    def brinson(
        self,
        portfolio_weights: Union[Dict[str, float], List[float]],
        benchmark_weights: Union[Dict[str, float], List[float]],
        portfolio_returns: Union[Dict[str, float], List[float], pd.Series],
        benchmark_returns: Union[Dict[str, float], List[float], pd.Series],
    ) -> Dict[str, float]:
        """
        Calculate Brinson attribution.

        Breaks down portfolio active return into:
        - Allocation effect: Benefits from over/under-weighting sectors
        - Selection effect: Benefits from picking winning stocks within sectors
        - Interaction effect: Combined effect of allocation and selection

        Args:
            portfolio_weights: Portfolio weights (dict or list)
            benchmark_weights: Benchmark weights (dict or list)
            portfolio_returns: Portfolio asset returns
            benchmark_returns: Benchmark asset returns

        Returns:
            Dict with allocation, selection, interaction, and total effect
        """
        if isinstance(portfolio_weights, dict):
            pw = pd.Series(portfolio_weights)
        else:
            pw = pd.Series(portfolio_weights)

        if isinstance(benchmark_weights, dict):
            bw = pd.Series(benchmark_weights)
        else:
            bw = pd.Series(benchmark_weights)

        if isinstance(portfolio_returns, (dict, list)):
            pr = pd.Series(portfolio_returns)
        else:
            pr = portfolio_returns

        if isinstance(benchmark_returns, (dict, list)):
            br = pd.Series(benchmark_returns)
        else:
            br = benchmark_returns

        aligned_pw, aligned_pr = pw.align(pr, join="inner")
        aligned_bw, aligned_br = bw.align(br, join="inner")
        aligned_pw, aligned_bw = aligned_pw.align(aligned_bw, join="outer")
        aligned_pr, aligned_br = aligned_pr.align(aligned_br, join="outer")

        aligned_pw = aligned_pw.fillna(0)
        aligned_bw = aligned_bw.fillna(1.0 / len(aligned_bw))
        aligned_pr = aligned_pr.fillna(0)
        aligned_br = aligned_br.fillna(0)

        total_active_return = float((aligned_pr - aligned_br).dot(aligned_pw))
        total_benchmark_return = float(aligned_br.dot(aligned_bw))

        allocation_effect = float((aligned_pw - aligned_bw).dot(aligned_br))
        selection_effect = float((aligned_pr - aligned_br).dot(aligned_bw))
        interaction_effect = total_active_return - allocation_effect - selection_effect

        return {
            "allocation": round(allocation_effect, 6),
            "selection": round(selection_effect, 6),
            "interaction": round(interaction_effect, 6),
            "total_active_return": round(total_active_return, 6),
            "portfolio_return": round(float(aligned_pr.dot(aligned_pw)), 6),
            "benchmark_return": round(float(aligned_br.dot(aligned_bw)), 6),
        }

    def multi_period_brinson(
        self,
        portfolio_weights: List[Dict[str, float]],
        benchmark_weights: List[Dict[str, float]],
        portfolio_returns: List[Dict[str, float]],
        benchmark_returns: List[Dict[str, float]],
    ) -> Dict[str, Union[float, Dict[str, float]]]:
        """
        Calculate multi-period Brinson attribution with compounding.

        Args:
            portfolio_weights: List of portfolio weight dicts over time
            benchmark_weights: List of benchmark weight dicts over time
            portfolio_returns: List of portfolio return dicts over time
            benchmark_returns: List of benchmark return dicts over time

        Returns:
            Dict with compounded attribution and period-by-period breakdown
        """
        if len(portfolio_weights) != len(benchmark_weights):
            raise ValueError("Portfolio and benchmark weight lists must have same length")
        if len(portfolio_returns) != len(benchmark_returns):
            raise ValueError("Portfolio and benchmark return lists must have same length")

        cumulative_allocation = 0.0
        cumulative_selection = 0.0
        cumulative_interaction = 0.0
        cumulative_portfolio = 1.0
        cumulative_benchmark = 1.0

        periods = []

        for i in range(len(portfolio_weights)):
            result = self.brinson(
                portfolio_weights[i],
                benchmark_weights[i],
                portfolio_returns[i],
                benchmark_returns[i],
            )

            cumulative_allocation += result["allocation"]
            cumulative_selection += result["selection"]
            cumulative_interaction += result["interaction"]
            cumulative_portfolio *= 1 + result["portfolio_return"]
            cumulative_benchmark *= 1 + result["benchmark_return"]

            periods.append({
                "period": i + 1,
                "allocation": result["allocation"],
                "selection": result["selection"],
                "interaction": result["interaction"],
                "portfolio_return": result["portfolio_return"],
                "benchmark_return": result["benchmark_return"],
            })

        return {
            "allocation": round(cumulative_allocation, 6),
            "selection": round(cumulative_selection, 6),
            "interaction": round(cumulative_interaction, 6),
            "total_return": round(cumulative_portfolio - 1, 6),
            "portfolio_total_return": round(cumulative_portfolio - 1, 6),
            "benchmark_total_return": round(cumulative_benchmark - 1, 6),
            "periods": periods,
        }