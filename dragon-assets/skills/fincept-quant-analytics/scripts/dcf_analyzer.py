"""
DCF (Discounted Cash Flow) 估值分析器
CFA级别绝对估值模型
"""

import numpy as np
from typing import Optional


class DCFAnalyzer:
    """
    DCF估值模型

    支持：
    - 自由现金流折现
    - 永续增长率计算
    - 安全边际分析
    - 敏感性分析
    """

    def __init__(self):
        self.defaults = {
            "discount_rate": 0.10,
            "terminal_growth": 0.03,
            "tax_rate": 0.21,
            "depreciation_rate": 0.05,
            "capex_rate": 0.05,
        }

    def dcf(
        self,
        ticker: str,
        revenue: float,
        revenue_growth: float = 0.08,
        operating_margin: float = 0.20,
        discount_rate: float = 0.10,
        terminal_growth: float = 0.03,
        years: int = 5,
        shares_outstanding: float = 1.0,
        net_debt: float = 0.0,
        current_price: Optional[float] = None,
    ) -> dict:
        """
        执行DCF估值

        Args:
            ticker: 股票代码
            revenue: 当前年收入（百万）
            revenue_growth: 收入增长率
            operating_margin: 营业利润率
            discount_rate: 折现率 (WACC)
            terminal_growth: 永续增长率
            years: 预测年数
            shares_outstanding: 流通股数（百万）
            net_debt: 净债务（百万）
            current_price: 当前股价（可选）

        Returns:
            dict: 包含内在价值、安全边际等
        """
        yearly_fcf = []
        current_revenue = revenue

        # 生成每年自由现金流
        for year in range(1, years + 1):
            future_revenue = current_revenue * (1 + revenue_growth)
            ebit = future_revenue * operating_margin
            taxes = ebit * self.defaults["tax_rate"]
            nopat = ebit * (1 - self.defaults["tax_rate"])
            d_and_a = future_revenue * self.defaults["depreciation_rate"]
            capex = future_revenue * self.defaults["capex_rate"]
            fcff = nopat + d_and_a - capex
            yearly_fcf.append(fcff)
            current_revenue = future_revenue

        # 计算终端价值
        terminal_fcf = yearly_fcf[-1] * (1 + terminal_growth)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth)

        # 折现所有现金流
        discount_factors = [(1 / (1 + discount_rate) ** t) for t in range(1, years + 1)]
        pv_fcf = sum(fcff * df for fcff, df in zip(yearly_fcf, discount_factors))
        pv_terminal = terminal_value * discount_factors[-1]

        # 企业价值 = PV(FCF) + PV(终端价值)
        enterprise_value = pv_fcf + pv_terminal

        # 股权价值 = EV - 净债务
        equity_value = enterprise_value - net_debt

        # 每股价值
        intrinsic_value = equity_value / shares_outstanding

        # 安全边际
        if current_price is not None:
            margin_of_safety = (intrinsic_value - current_price) / intrinsic_value
        else:
            margin_of_safety = None

        return {
            "ticker": ticker,
            "intrinsic_value": round(intrinsic_value, 2),
            "current_price": current_price,
            "margin_of_safety": margin_of_safety,
            "enterprise_value": round(enterprise_value, 2),
            "equity_value": round(equity_value, 2),
            "terminal_value": round(terminal_value, 2),
            "pv_fcf": round(pv_fcf, 2),
            "yearly_fcf": [round(fcff, 2) for fcff in yearly_fcf],
            "discount_rate": discount_rate,
            "terminal_growth": terminal_growth,
            "years": years,
        }

    def sensitivity(
        self,
        revenue: float,
        operating_margin: float = 0.20,
        discount_rate: float = 0.10,
        terminal_growth: float = 0.03,
        growth_range: tuple = (-0.02, 0.06),
        margin_range: tuple = (-0.05, 0.05),
    ) -> dict:
        """
        敏感性分析

        Args:
            revenue: 当前年收入
            operating_margin: 基准营业利润率
            discount_rate: 基准折现率
            terminal_growth: 永续增长率
            growth_range: 增长率变化范围
            margin_range: 利润率变化范围

        Returns:
            dict: 敏感性矩阵
        """
        results = {}
        growth_steps = np.linspace(growth_range[0], growth_range[1], 5)
        margin_steps = np.linspace(margin_range[0], margin_range[1], 5)

        matrix = []
        for g in growth_steps:
            row = []
            for m in margin_steps:
                result = self.dcf(
                    ticker="SENSITIVITY",
                    revenue=revenue,
                    revenue_growth=g,
                    operating_margin=operating_margin + m,
                    discount_rate=discount_rate,
                    terminal_growth=terminal_growth,
                    years=5,
                )
                row.append(round(result["intrinsic_value"], 2))
            matrix.append(row)

        return {
            "matrix": matrix,
            "growth_steps": [round(g, 4) for g in growth_steps],
            "margin_steps": [round(m, 4) for m in margin_steps],
            "base_value": self.dcf(
                ticker="BASE",
                revenue=revenue,
                revenue_growth=0.08,
                operating_margin=operating_margin,
                discount_rate=discount_rate,
                terminal_growth=terminal_growth,
                years=5,
            )["intrinsic_value"],
        }

    def ddm(
        self,
        ticker: str,
        dividend_per_share: float,
        dividend_growth: float = 0.08,
        discount_rate: float = 0.10,
        terminal_growth: float = 0.03,
        years: int = 5,
    ) -> dict:
        """
        DDM (Dividend Discount Model) 股价估值

        Args:
            ticker: 股票代码
            dividend_per_share: 当前每股股息
            dividend_growth: 股息增长率
            discount_rate: 折现率
            terminal_growth: 永续增长率
            years: 预测年数

        Returns:
            dict: DDM估值结果
        """
        dividends = []
        current_div = dividend_per_share

        for year in range(1, years + 1):
            future_div = current_div * (1 + dividend_growth)
            dividends.append(future_div)
            current_div = future_div

        # 终端价值
        terminal_div = dividends[-1] * (1 + terminal_growth)
        terminal_value = terminal_div / (discount_rate - terminal_growth)

        # 折现
        discount_factors = [(1 / (1 + discount_rate) ** t) for t in range(1, years + 1)]
        pv_dividends = sum(d * df for d, df in zip(dividends, discount_factors))
        pv_terminal = terminal_value * discount_factors[-1]

        intrinsic_value = pv_dividends + pv_terminal

        return {
            "ticker": ticker,
            "intrinsic_value": round(intrinsic_value, 2),
            "terminal_value": round(terminal_value, 2),
            "pv_dividends": round(pv_dividends, 2),
            "dividends": [round(d, 4) for d in dividends],
            "discount_rate": discount_rate,
            "terminal_growth": terminal_growth,
        }


if __name__ == "__main__":
    # 测试DCF
    analyzer = DCFAnalyzer()

    result = analyzer.dcf(
        ticker="AAPL",
        revenue=394.328,  # Apple FY2024 revenue in billions
        revenue_growth=0.08,
        operating_margin=0.28,
        discount_rate=0.10,
        terminal_growth=0.03,
        years=5,
        shares_outstanding=15.5,  # billions
        net_debt=0,
        current_price=175.0,
    )

    print(f"DCF Valuation for {result['ticker']}")
    print(f"Intrinsic Value: ${result['intrinsic_value']:.2f}")
    print(f"Current Price: ${result['current_price']:.2f}")
    if result['margin_of_safety'] is not None:
        print(f"Margin of Safety: {result['margin_of_safety']:.1%}")
    print(f"Enterprise Value: ${result['enterprise_value']:.2f}B")
    print(f"Terminal Value: ${result['terminal_value']:.2f}B")