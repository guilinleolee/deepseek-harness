"""
Options Analysis Analyzer
CFA级别期权定价与Greeks分析
"""

import numpy as np
from scipy.stats import norm
from typing import Optional


class OptionsAnalyzer:
    """
    期权分析器

    支持：
    - Black-Scholes期权定价
    - Greeks计算 (Delta, Gamma, Theta, Vega, Rho)
    - 期权链分析
    - 隐含波动率计算
    - 策略分析 (Straddle, Strangle, Butterfly)
    """

    def __init__(self):
        self.defaults = {
            "risk_free_rate": 0.05,
            "default_sigma": 0.25,
        }

    def black_scholes(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str = "call",
    ) -> float:
        """
        Black-Scholes期权定价

        Args:
            S: 标的资产当前价格
            K: 行权价
            T: 到期时间（年）
            r: 无风险利率
            sigma: 波动率
            option_type: 'call' 或 'put'

        Returns:
            float: 期权价格
        """
        if T <= 0:
            if option_type == "call":
                return max(S - K, 0)
            else:
                return max(K - S, 0)

        d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if option_type == "call":
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

        return round(price, 4)

    def greeks(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: str = "call",
    ) -> dict:
        """
        计算期权Greeks

        Args:
            S: 标的资产当前价格
            K: 行权价
            T: 到期时间（年）
            r: 无风险利率
            sigma: 波动率
            option_type: 'call' 或 'put'

        Returns:
            dict: 包含delta, gamma, theta, vega, rho
        """
        if T <= 0:
            return {
                "delta": 1.0 if option_type == "call" and S > K else (-1.0 if option_type == "put" and S < K else 0),
                "gamma": 0.0,
                "theta": 0.0,
                "vega": 0.0,
                "rho": 0.0,
            }

        d1 = (np.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        sqrt_T = np.sqrt(T)

        # Delta
        if option_type == "call":
            delta = norm.cdf(d1)
        else:
            delta = norm.cdf(d1) - 1

        # Gamma (call和put相同)
        gamma = norm.pdf(d1) / (S * sigma * sqrt_T)

        # Theta
        term1 = -S * norm.pdf(d1) * sigma / (2 * sqrt_T)
        if option_type == "call":
            term2 = r * K * np.exp(-r * T) * norm.cdf(d2)
            theta = (term1 - term2) / 365
        else:
            term2 = r * K * np.exp(-r * T) * norm.cdf(-d2)
            theta = (term1 + term2) / 365

        # Vega (call和put相同)
        vega = S * sqrt_T * norm.pdf(d1) / 100

        # Rho
        if option_type == "call":
            rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
        else:
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100

        return {
            "delta": round(delta, 4),
            "gamma": round(gamma, 6),
            "theta": round(theta, 4),
            "vega": round(vega, 4),
            "rho": round(rho, 4),
            "d1": round(d1, 4),
            "d2": round(d2, 4),
        }

    def implied_volatility(
        self,
        market_price: float,
        S: float,
        K: float,
        T: float,
        r: float,
        option_type: str = "call",
        precision: float = 0.0001,
        max_iterations: int = 100,
    ) -> float:
        """
        计算隐含波动率 (Newton-Raphson方法)

        Args:
            market_price: 市场价格
            S: 标的资产当前价格
            K: 行权价
            T: 到期时间（年）
            r: 无风险利率
            option_type: 'call' 或 'put'
            precision: 收敛精度
            max_iterations: 最大迭代次数

        Returns:
            float: 隐含波动率
        """
        sigma = 0.3  # 初始猜测

        for _ in range(max_iterations):
            bs_price = self.black_scholes(S, K, T, r, sigma, option_type)
            vega = self.greeks(S, K, T, r, sigma, option_type)["vega"] * 100

            if vega == 0:
                break

            diff = market_price - bs_price
            if abs(diff) < precision:
                break

            sigma = sigma + diff / vega

            if sigma <= 0 or sigma > 2:
                sigma = 0.3
                break

        return round(sigma, 4)

    def option_chain(
        self,
        ticker: str,
        S: float,
        expiration: str,
        strikes: Optional[list] = None,
        risk_free: float = 0.05,
        sigma: float = 0.25,
    ) -> dict:
        """
        生成期权链

        Args:
            ticker: 股票代码
            S: 当前股价
            expiration: 到期日 (YYYY-MM-DD)
            strikes: 行权价列表（可选，自动生成）
            risk_free: 无风险利率
            sigma: 波动率

        Returns:
            dict: 期权链数据
        """
        if strikes is None:
            # 自动生成ATM附近的行权价
            strike_step = S * 0.05
            strikes = [
                S - 3 * strike_step,
                S - 2 * strike_step,
                S - strike_step,
                S,
                S + strike_step,
                S + 2 * strike_step,
                S + 3 * strike_step,
            ]

        chain = {"ticker": ticker, "expiration": expiration, "underlying_price": S}

        calls = []
        puts = []

        for K in strikes:
            call_price = self.black_scholes(S, K, 0.1, risk_free, sigma, "call")
            put_price = self.black_scholes(S, K, 0.1, risk_free, sigma, "put")

            call_greeks = self.greeks(S, K, 0.1, risk_free, sigma, "call")
            put_greeks = self.greeks(S, K, 0.1, risk_free, sigma, "put")

            calls.append({
                "strike": K,
                "bid": round(call_price * 0.95, 2),
                "ask": round(call_price * 1.05, 2),
                "mid": round(call_price, 2),
                "intrinsic": round(max(S - K, 0), 2),
                "delta": call_greeks["delta"],
                "gamma": call_greeks["gamma"],
                "theta": call_greeks["theta"],
                "vega": call_greeks["vega"],
            })

            puts.append({
                "strike": K,
                "bid": round(put_price * 0.95, 2),
                "ask": round(put_price * 1.05, 2),
                "mid": round(put_price, 2),
                "intrinsic": round(max(K - S, 0), 2),
                "delta": put_greeks["delta"],
                "gamma": put_greeks["gamma"],
                "theta": put_greeks["theta"],
                "vega": put_greeks["vega"],
            })

        chain["calls"] = calls
        chain["puts"] = puts

        return chain

    def strategy_payoff(
        self,
        strategy: str,
        S: float,
        strikes: list,
        premiums: list,
        option_type: str = "call",
    ) -> dict:
        """
        计算期权策略收益

        Args:
            strategy: 策略名称 (straddle, strangle, butterfly, iron_condor)
            S: 当前标的价格
            strikes: 行权价列表
            premiums: 权利金列表
            option_type: 'call' 或 'put'

        Returns:
            dict: 策略收益分析
        """
        if strategy == "straddle":
            # 跨式策略：同价买入call和put
            K = strikes[0]
            payoff_at_K = premiums[0] + premiums[1]

            # 计算不同标的价格下的收益
            prices = np.linspace(S * 0.5, S * 1.5, 100)
            payoffs = []

            for price in prices:
                call_payoff = max(price - K, 0) - premiums[0]
                put_payoff = max(K - price, 0) - premiums[1]
                payoffs.append(call_payoff + put_payoff)

            breakeven = S + payoff_at_K

            return {
                "strategy": "straddle",
                "max_profit": "unlimited" if option_type == "call" else K - sum(premiums),
                "max_loss": sum(premiums),
                "breakeven": round(breakeven, 2),
                "prices": prices.tolist()[:10],
                "payoffs": [round(p, 2) for p in payoffs[:10]],
            }

        elif strategy == "strangle":
            # 宽跨式策略
            K_call, K_put = strikes[0], strikes[1]
            total_premium = sum(premiums)

            prices = np.linspace(S * 0.5, S * 1.5, 100)
            payoffs = []

            for price in prices:
                call_payoff = max(price - K_call, 0) - premiums[0]
                put_payoff = max(K_put - price, 0) - premiums[1]
                payoffs.append(call_payoff + put_payoff)

            return {
                "strategy": "strangle",
                "max_loss": total_premium,
                "breakeven_up": S + total_premium,
                "breakeven_down": S - total_premium,
                "prices": prices.tolist()[:10],
                "payoffs": [round(p, 2) for p in payoffs[:10]],
            }

        elif strategy == "butterfly":
            # 蝶式策略
            K1, K2, K3 = strikes
            premium1, premium2, premium3 = premiums

            max_profit = K2 - K1 - premium1 + premium2 - premium3
            max_loss = premium1 - premium2 + premium3

            return {
                "strategy": "butterfly",
                "max_profit": round(max_profit, 2),
                "max_loss": round(max_loss, 2),
                "breakeven": [K1 + max_loss, K3 - max_loss],
            }

        return {"strategy": strategy, "error": "unknown strategy"}


if __name__ == "__main__":
    # 测试期权分析
    analyzer = OptionsAnalyzer()

    # Black-Scholes定价
    price = analyzer.black_scholes(S=185, K=180, T=0.1, r=0.05, sigma=0.25)
    print(f"Call Option Price: ${price:.2f}")

    # Greeks
    greeks = analyzer.greeks(S=185, K=180, T=0.1, r=0.05, sigma=0.25)
    print(f"\nGreeks:")
    print(f"  Delta: {greeks['delta']:.4f}")
    print(f"  Gamma: {greeks['gamma']:.6f}")
    print(f"  Theta: {greeks['theta']:.4f}")
    print(f"  Vega: {greeks['vega']:.4f}")
    print(f"  Rho: {greeks['rho']:.4f}")

    # 隐含波动率
    iv = analyzer.implied_volatility(market_price=8.5, S=185, K=180, T=0.1, r=0.05)
    print(f"\nImplied Volatility: {iv:.2%}")

    # 期权链
    chain = analyzer.option_chain("AAPL", S=185, expiration="2026-05-16")
    print(f"\nOption Chain for {chain['ticker']}:")
    print(f"  Underlying Price: ${chain['underlying_price']}")
    print(f"  Calls: {len(chain['calls'])} strikes")
    print(f"  Puts: {len(chain['puts'])} strikes")