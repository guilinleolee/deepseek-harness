"""
Risk Analysis Analyzer
CFA级别风险指标计算
"""

import numpy as np
from scipy import stats
from typing import List, Union, Optional


class RiskAnalyzer:
    """
    风险分析器

    支持：
    - VaR / CVaR (Value at Risk / Conditional VaR)
    - 夏普比率 / 索提诺比率
    - 最大回撤 / 卡尔马比率
    - 统计检验 (Jarque-Bera, Ljung-Box, ADF)
    - 蒙特卡洛模拟
    """

    def __init__(self):
        self.defaults = {
            "risk_free_rate": 0.04,
            "confidence_levels": [0.95, 0.99],
        }

    def returns(self, prices: List[float]) -> np.ndarray:
        """
        计算收益率序列

        Args:
            prices: 价格序列

        Returns:
            np.ndarray: 收益率数组
        """
        prices = np.array(prices)
        returns = np.diff(prices) / prices[:-1]
        return returns

    def value_at_risk(
        self,
        returns: Union[List[float], np.ndarray],
        confidence: float = 0.95,
        portfolio_value: float = 1.0,
    ) -> float:
        """
        计算VaR (Value at Risk)

        Args:
            returns: 收益率序列
            confidence: 置信水平 (如0.95)
            portfolio_value: 组合价值（用于计算金额VaR）

        Returns:
            float: VaR值（负数表示损失）
        """
        returns = np.array(returns)

        var = np.percentile(returns, (1 - confidence) * 100)

        return var * portfolio_value

    def cvar(
        self,
        returns: Union[List[float], np.ndarray],
        confidence: float = 0.95,
        portfolio_value: float = 1.0,
    ) -> float:
        """
        计算CVaR (Conditional VaR / Expected Shortfall)

        Args:
            returns: 收益率序列
            confidence: 置信水平
            portfolio_value: 组合价值

        Returns:
            float: CVaR值
        """
        returns = np.array(returns)
        var = np.percentile(returns, (1 - confidence) * 100)

        cvar = returns[returns <= var].mean()

        return cvar * portfolio_value

    def sharpe_ratio(
        self,
        returns: Union[List[float], np.ndarray],
        risk_free: float = 0.04,
        periods_per_year: int = 252,
    ) -> float:
        """
        计算夏普比率

        Args:
            returns: 收益率序列
            risk_free: 年化无风险利率
            periods_per_year: 年化周期数（股票用252）

        Returns:
            float: 夏普比率
        """
        returns = np.array(returns)

        excess_returns = returns - risk_free / periods_per_year

        if np.std(returns) == 0:
            return 0.0

        sharpe = np.mean(excess_returns) / np.std(returns) * np.sqrt(periods_per_year)

        return round(sharpe, 4)

    def sortino_ratio(
        self,
        returns: Union[List[float], np.ndarray],
        risk_free: float = 0.04,
        periods_per_year: int = 252,
        target_return: float = 0.0,
    ) -> float:
        """
        计算索提诺比率（只考虑下行风险）

        Args:
            returns: 收益率序列
            risk_free: 年化无风险利率
            periods_per_year: 年化周期数
            target_return: 目标收益率

        Returns:
            float: 索提诺比率
        """
        returns = np.array(returns)

        excess_returns = returns - risk_free / periods_per_year
        downside_returns = returns[returns < target_return]

        if len(downside_returns) == 0 or np.std(downside_returns) == 0:
            return 0.0

        sortino = (np.mean(excess_returns) - target_return) / np.std(downside_returns) * np.sqrt(periods_per_year)

        return round(sortino, 4)

    def max_drawdown(self, returns: Union[List[float], np.ndarray]) -> float:
        """
        计算最大回撤

        Args:
            returns: 收益率序列

        Returns:
            float: 最大回撤（负数）
        """
        returns = np.array(returns)

        # 计算累积净值
        wealth_index = (1 + returns).cumprod()

        # 计算历史最高点
        previous_peaks = np.maximum.accumulate(wealth_index)

        # 计算回撤
        drawdowns = (wealth_index - previous_peaks) / previous_peaks

        max_drawdown = drawdowns.min()

        return round(max_drawdown, 6)

    def calmar_ratio(
        self,
        returns: Union[List[float], np.ndarray],
        periods_per_year: int = 252,
    ) -> float:
        """
        计算卡尔马比率 (年化收益 / 最大回撤)

        Args:
            returns: 收益率序列
            periods_per_year: 年化周期数

        Returns:
            float: 卡尔马比率
        """
        returns = np.array(returns)

        max_dd = abs(self.max_drawdown(returns))

        if max_dd == 0:
            return 0.0

        annual_return = np.mean(returns) * periods_per_year

        calmar = annual_return / max_dd

        return round(calmar, 4)

    def beta(
        self,
        asset_returns: Union[List[float], np.ndarray],
        market_returns: Union[List[float], np.ndarray],
    ) -> float:
        """
        计算Beta (资产对市场的敏感性)

        Args:
            asset_returns: 资产收益率序列
            market_returns: 市场收益率序列

        Returns:
            float: Beta值
        """
        asset_returns = np.array(asset_returns)
        market_returns = np.array(market_returns)

        # 对齐长度
        min_len = min(len(asset_returns), len(market_returns))
        asset_returns = asset_returns[:min_len]
        market_returns = market_returns[:min_len]

        covariance = np.cov(asset_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)

        if market_variance == 0:
            return 1.0

        beta = covariance / market_variance

        return round(beta, 4)

    def treynor_ratio(
        self,
        asset_returns: Union[List[float], np.ndarray],
        market_returns: Union[List[float], np.ndarray],
        risk_free: float = 0.04,
        periods_per_year: int = 252,
    ) -> float:
        """
        计算特雷诺比率

        Args:
            asset_returns: 资产收益率序列
            market_returns: 市场收益率序列
            risk_free: 年化无风险利率
            periods_per_year: 年化周期数

        Returns:
            float: 特雷诺比率
        """
        asset_returns = np.array(asset_returns)
        market_returns = np.array(market_returns)

        beta = self.beta(asset_returns, market_returns)

        if beta == 0:
            return 0.0

        annual_return = np.mean(asset_returns) * periods_per_year
        excess_return = annual_return - risk_free

        treynor = excess_return / beta

        return round(treynor, 4)

    def information_ratio(
        self,
        asset_returns: Union[List[float], np.ndarray],
        benchmark_returns: Union[List[float], np.ndarray],
        periods_per_year: int = 252,
    ) -> float:
        """
        计算信息比率 (超额收益 / 跟踪误差)

        Args:
            asset_returns: 资产收益率序列
            benchmark_returns: 基准收益率序列
            periods_per_year: 年化周期数

        Returns:
            float: 信息比率
        """
        asset_returns = np.array(asset_returns)
        benchmark_returns = np.array(benchmark_returns)

        # 对齐长度
        min_len = min(len(asset_returns), len(benchmark_returns))
        asset_returns = asset_returns[:min_len]
        benchmark_returns = benchmark_returns[:min_len]

        excess_returns = asset_returns - benchmark_returns

        if np.std(excess_returns) == 0:
            return 0.0

        ir = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(periods_per_year)

        return round(ir, 4)

    def jarque_bera(self, returns: Union[List[float], np.ndarray]) -> dict:
        """
        Jarque-Bera正态性检验

        H0: 收益率服从正态分布

        Args:
            returns: 收益率序列

        Returns:
            dict: 包含jb_stat, p_value, conclusion
        """
        returns = np.array(returns)

        n = len(returns)

        if n < 20:
            return {
                "jb_stat": None,
                "p_value": None,
                "conclusion": "insufficient_data",
                "message": "样本量不足，需要至少20个观测值",
            }

        # 计算偏度和峰度
        mean = np.mean(returns)
        std = np.std(returns)

        if std == 0:
            return {
                "jb_stat": None,
                "p_value": None,
                "conclusion": "undefined",
                "message": "标准差为0，无法进行检验",
            }

        skewness = np.mean(((returns - mean) / std) ** 3)
        kurtosis = np.mean(((returns - mean) / std) ** 4)

        # JB统计量
        jb_stat = (n / 6) * (skewness**2 + (1/4) * (kurtosis - 3)**2)

        # p值（卡方分布，df=2）
        p_value = 1 - stats.chi2.cdf(jb_stat, df=2)

        # 结论
        if p_value < 0.05:
            conclusion = "reject_normality"
            message = "拒绝正态分布假设 (p < 0.05)"
        else:
            conclusion = "accept_normality"
            message = "不能拒绝正态分布假设 (p >= 0.05)"

        return {
            "jb_stat": round(jb_stat, 4),
            "p_value": round(p_value, 4),
            "skewness": round(skewness, 4),
            "kurtosis": round(kurtosis, 4),
            "conclusion": conclusion,
            "message": message,
        }

    def ljung_box(
        self,
        returns: Union[List[float], np.ndarray],
        lags: int = 10,
    ) -> dict:
        """
        Ljung-Box自相关检验

        H0: 不存在自相关

        Args:
            returns: 收益率序列
            lags: 检验的滞后期数

        Returns:
            dict: 包含lb_stat, p_value, conclusion
        """
        returns = np.array(returns)
        n = len(returns)

        if n < lags + 1:
            return {
                "lb_stat": None,
                "p_value": None,
                "conclusion": "insufficient_data",
                "message": f"样本量不足，需要至少{lags + 1}个观测值",
            }

        # 计算自相关
        acf = np.correlate(returns - np.mean(returns), returns - np.mean(returns), mode='full')
        acf = acf / acf[len(acf) // 2]
        acf = acf[len(acf) // 2 + 1:]

        # Ljung-Box统计量
        lb_stat = 0
        for k in range(1, lags + 1):
            lb_stat += acf[k - 1] ** 2 / (n - k)

        lb_stat = n * (n + 2) * lb_stat

        # p值（卡方分布，df=lags）
        p_value = 1 - stats.chi2.cdf(lb_stat, df=lags)

        # 结论
        if p_value < 0.05:
            conclusion = "reject_independence"
            message = "拒绝独立假设，存在自相关 (p < 0.05)"
        else:
            conclusion = "accept_independence"
            message = "不能拒绝独立假设 (p >= 0.05)"

        return {
            "lb_stat": round(lb_stat, 4),
            "p_value": round(p_value, 4),
            "lags": lags,
            "acf": [round(a, 4) for a in acf[:lags]],
            "conclusion": conclusion,
            "message": message,
        }

    def autocorrelation(self, returns: Union[List[float], np.ndarray], max_lag: int = 20) -> dict:
        """
        计算自相关函数

        Args:
            returns: 收益率序列
            max_lag: 最大滞后期

        Returns:
            dict: 自相关系数
        """
        returns = np.array(returns)
        n = len(returns)

        acf_values = []
        mean = np.mean(returns)
        variance = np.sum((returns - mean) ** 2)

        for lag in range(1, max_lag + 1):
            if lag >= n:
                break

            covariance = np.sum((returns[:-lag] - mean) * (returns[lag:] - mean))
            acf = covariance / variance
            acf_values.append(round(acf, 4))

        return {
            "acf": acf_values,
            "lags": len(acf_values),
            "significant_95": [i + 1 for i, acf in enumerate(acf_values) if abs(acf) > 1.96 / np.sqrt(n)],
        }

    def monte_carlo_var(
        self,
        returns: Union[List[float], np.ndarray],
        confidence: float = 0.95,
        simulations: int = 10000,
        portfolio_value: float = 1.0,
    ) -> float:
        """
        蒙特卡洛模拟计算VaR

        Args:
            returns: 历史收益率序列
            confidence: 置信水平
            simulations: 模拟次数
            portfolio_value: 组合价值

        Returns:
            float: VaR值
        """
        returns = np.array(returns)

        mean = np.mean(returns)
        std = np.std(returns)

        # 模拟未来收益
        simulated_returns = np.random.normal(mean, std, simulations)

        # 计算VaR
        var = np.percentile(simulated_returns, (1 - confidence) * 100)

        return var * portfolio_value

    def rolling_sharpe(
        self,
        returns: Union[List[float], np.ndarray],
        window: int = 60,
        risk_free: float = 0.04,
    ) -> dict:
        """
        计算滚动夏普比率

        Args:
            returns: 收益率序列
            window: 滚动窗口大小
            risk_free: 年化无风险利率

        Returns:
            dict: 滚动夏普比率序列
        """
        returns = np.array(returns)
        n = len(returns)

        if n < window:
            return {"sharpe": [], "dates": []}

        sharpe_values = []
        daily_rf = risk_free / 252

        for i in range(window, n):
            window_returns = returns[i - window:i]
            excess = window_returns - daily_rf
            sharpe = np.mean(excess) / np.std(window_returns) * np.sqrt(252)
            sharpe_values.append(round(sharpe, 4))

        return {
            "sharpe": sharpe_values,
            "mean": round(np.mean(sharpe_values), 4),
            "min": round(np.min(sharpe_values), 4),
            "max": round(np.max(sharpe_values), 4),
            "current": sharpe_values[-1] if sharpe_values else None,
        }


if __name__ == "__main__":
    # 测试风险分析
    analyzer = RiskAnalyzer()

    # 模拟收益率
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, 252)

    # VaR
    var_95 = analyzer.value_at_risk(returns, confidence=0.95)
    var_99 = analyzer.value_at_risk(returns, confidence=0.99)
    print(f"95% VaR: {var_95:.4%}")
    print(f"99% VaR: {var_99:.4%}")

    # CVaR
    cvar_95 = analyzer.cvar(returns, confidence=0.95)
    print(f"95% CVaR: {cvar_95:.4%}")

    # 夏普比率
    sharpe = analyzer.sharpe_ratio(returns, risk_free=0.04)
    print(f"Sharpe Ratio: {sharpe:.4f}")

    # 最大回撤
    max_dd = analyzer.max_drawdown(returns)
    print(f"Max Drawdown: {max_dd:.4%}")

    # Jarque-Bera检验
    jb = analyzer.jarque_bera(returns)
    print(f"\nJarque-Bera Test:")
    print(f"  JB Stat: {jb['jb_stat']:.4f}")
    print(f"  p-value: {jb['p_value']:.4f}")
    print(f"  Conclusion: {jb['conclusion']}")

    # Ljung-Box检验
    lb = analyzer.ljung_box(returns, lags=10)
    print(f"\nLjung-Box Test:")
    print(f"  LB Stat: {lb['lb_stat']:.4f}")
    print(f"  p-value: {lb['p_value']:.4f}")
    print(f"  Conclusion: {lb['conclusion']}")