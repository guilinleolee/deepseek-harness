---
license: UNKNOWN
triggers: ["options strategy advisor", "期权策略顾问 (Options Strategy Advisor)"]
---
# 期权策略顾问 (Options Strategy Advisor)

## L0: 一句话描述 (≤15字)
期权希腊字母风控+Black-Scholes定价+隐波曲面分析。

## L1: 使用场景 (50-100字)
当需要构建期权组合、对冲现有持仓风险、或进行收益增强时使用，包含期权定价、希腊字母风控、隐含波动率分析、策略推荐。适用于天龙引擎60-01投资总监和64-02算法交易员的收益增强和风控对冲决策。

## L2: 详细文档

### 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ 期权策略顾问 — 四维分析体系                                 │
├─────────────────────────────────────────────────────────────┤
│  Dimension 1: 期权定价                                      │
│    → Black-Scholes公式计算理论价格                         │
│    → 历史波动率(HV) vs 隐含波动率(IV)                     │
│    → Put-Call Parity验证                                  │
│                                                              │
│  Dimension 2: 希腊字母                                     │
│    → Delta: 价格敏感度 (对冲比率)                          │
│    → Gamma: Delta变化率 (凸性)                             │
│    → Theta: 时间衰减 (每日消耗)                            │
│    → Vega: 波动率敏感度 (VIX影响)                         │
│                                                              │
│  Dimension 3: 隐含波动率曲面                               │
│    → 期限结构 (Contango/Backwardation)                    │
│    → Strike Skew (偏斜程度)                               │
│    → IV Rank / IV Percentile                              │
│                                                              │
│  Dimension 4: 策略推荐                                     │
│    → 根据市场格局和持仓状况智能推荐                         │
│    → 收益增强 / 风险对冲 / 套利机会                        │
└─────────────────────────────────────────────────────────────┘
```

### 期权定价与希腊字母代码实现

```python
import math
from dataclasses import dataclass
from scipy.stats import norm


@dataclass
class Option:
    """期权"""
    S: float          # 标的价格
    K: float          # 行权价
    T: float          # 剩余期限 (年)
    r: float          # 无风险利率
    sigma: float      # 波动率
    is_call: bool     # True=Call, False=Put


def black_scholes_price(option: Option) -> dict:
    """
    Black-Scholes期权定价 + 希腊字母
    """
    S, K, T, r, sigma = option.S, option.K, option.T, option.r, option.sigma

    if T <= 0:
        # 到期期权
        if option.is_call:
            price = max(S - K, 0)
            return {"price": price, "delta": 1.0 if S > K else 0.0,
                    "gamma": 0, "theta": 0, "vega": 0}
        else:
            price = max(K - S, 0)
            return {"price": price, "delta": -1.0 if S < K else 0.0,
                    "gamma": 0, "theta": 0, "vega": 0}

    d1 = (math.log(S / K) + (r + sigma ** 2 / 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    if option.is_call:
        price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
    else:
        price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = norm.cdf(d1) - 1

    # 希腊字母
    gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
    theta_call = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T))
    theta_put = theta_call
    if option.is_call:
        theta = (theta_call - r * K * math.exp(-r * T) * norm.cdf(d2)) / 365
    else:
        theta = (theta_put + r * K * math.exp(-r * T) * norm.cdf(-d2)) / 365

    vega = S * norm.pdf(d1) * math.sqrt(T) / 100  # 每1%IV变化

    return {
        "price": round(price, 4),
        "delta": round(delta, 4),
        "gamma": round(gamma, 6),
        "theta": round(theta, 4),
        "vega": round(vega, 4),
        "d1": round(d1, 4),
        "d2": round(d2, 4),
        "intrinsic": max(S - K, 0) if option.is_call else max(K - S, 0),
        "time_value": price - (max(S - K, 0) if option.is_call else max(K - S, 0))
    }


def calculate_implied_vol(
    option_price: float,
    option: Option,
    tolerance: float = 0.0001,
    max_iterations: int = 100
) -> float:
    """
    二分法计算隐含波动率 (IV)
    """
    low = 0.01
    high = 3.0

    for _ in range(max_iterations):
        mid = (low + high) / 2
        test_option = Option(option.S, option.K, option.T, option.r, mid, option.is_call)
        price = black_scholes_price(test_option)["price"]

        if abs(price - option_price) < tolerance:
            return round(mid, 4)

        if price < option_price:
            low = mid
        else:
            high = mid

    return round(mid, 4)


class OptionsStrategyAdvisor:
    """期权策略顾问"""

    def __init__(self):
        self.risk_free_rate = 0.03  # 无风险利率

    def recommend_strategy(
        self,
        market_regime: str,           # strong_uptrend/uptrend/neutral/downtrend/panic_bottom
        portfolio_delta: float,        # 组合Delta (-100 to 100)
        portfolio_gamma: float,        # 组合Gamma
        iv_rank: float,              # IV百分位 (0-100)
        outlook_days: int = 30        # 展望天数
    ) -> dict:
        """
        根据市场格局和持仓状况推荐期权策略
        """
        recommendations = []

        # === 收益增强策略 ===
        if market_regime in ["uptrend", "neutral"]:
            # 卖出备兑Call (Covered Call)
            recommendations.append({
                "strategy": "备兑开仓 (Covered Call)",
                "action": "sell_call",
                "description": "持有正股+卖出虚值Call，收取权利金增强收益",
                "target_dte": 30,
                "strike_pct": 5,  # 虚值5%
                "expected_premium": "2-4% annualized",
                "delta_hedge": -0.3,  # 降低正股Delta暴露
                "risk": "上涨空间有限"
            })

        if market_regime == "neutral" and iv_rank > 60:
            # 卖出跨式 (Short Straddle) — 高IV环境
            recommendations.append({
                "strategy": "卖出跨式 (Short Straddle)",
                "action": "sell_straddle",
                "description": "同时卖出平值Call和Put，收取双边权利金",
                "target_dte": 30,
                "iv_edge": f"IV Rank={iv_rank}% > 60%",
                "expected_premium": "5-10% annualized",
                "delta_hedge": 0,
                "risk": "大幅波动会亏损，需要严格止损"
            })

        # === 风控对冲策略 ===
        if market_regime == "downtrend":
            # 买入Put保护 (Protective Put)
            recommendations.append({
                "strategy": "保护性Put",
                "action": "buy_put",
                "description": "持有正股+买入Put，对冲下行风险",
                "target_dte": 60,
                "strike_pct": -5,  # 虚值5%保护
                "cost": "1-3% 权利金",
                "delta_hedge": -portfolio_delta * 0.5,
                "max_loss": "Put行权价 - 当前价 - 权利金"
            })

        if market_regime in ["neutral", "downtrend"] and portfolio_delta > 50:
            # 买入Put保护高Delta组合
            recommendations.append({
                "strategy": "熊市价差 (Bear Put Spread)",
                "action": "buy_put_spread",
                "description": "买入高行权Put + 卖出低行权Put，降低成本",
                "target_dte": 30,
                "strike_width": 10,  # 价差宽度
                "cost_reduction": "40-60% vs 单独买Put",
                "max_profit": "strike_width - 净权利金",
                "risk": "最大亏损为净权利金"
            })

        # === 方向性策略 ===
        if market_regime == "strong_uptrend" and portfolio_delta < 30:
            # 买入Call杠杆
            recommendations.append({
                "strategy": "牛市价差 (Bull Call Spread)",
                "action": "buy_call_spread",
                "description": "买入低行权Call + 卖出高行权Call，降低成本",
                "target_dte": 30,
                "delta_leverage": "+30-40 Delta",
                "cost_reduction": "50-70% vs 买平值Call",
                "max_loss": "净权利金",
                "breakeven": "低行权价 + 净权利金"
            })

        if market_regime == "panic_bottom" and iv_rank > 80:
            # 买入跨式价差 (Long Strangle) — 低IV买入机会
            recommendations.append({
                "strategy": "买入跨式价差 (Long Strangle)",
                "action": "buy_strangle",
                "description": "买入虚值Call + 买入虚值Put，赌大幅波动",
                "target_dte": 60,
                "strike_otm": 10,  # 10%虚值
                "cost": "IV极高→权利金便宜",
                "max_loss": "总权利金",
                "profit_target": "strike_width - 权利金"
            })

        return {
            "market_regime": market_regime,
            "iv_rank": iv_rank,
            "portfolio_delta": portfolio_delta,
            "recommendations": recommendations,
            "selected": recommendations[0] if recommendations else None
        }

    def hedge_portfolio(
        self,
        portfolio_value: float,
        portfolio_beta: float,
        spot_price: float,
        target_delta: float = 0,
        atm_strike: float = None
    ) -> dict:
        """
        计算期权对冲方案
        """
        if atm_strike is None:
            atm_strike = spot_price

        # 计算需要的期权数量
        # 每份ETF期权的合约乘数通常为100
        contract_multiplier = 100

        # 需要的Delta总量
        target_delta_value = portfolio_value * (target_delta / 100)
        current_position_delta = portfolio_value * (0.5 / 100)  # 假设组合Delta=50%
        needed_delta = target_delta_value - current_position_delta

        # ATM Put的Delta ≈ -0.5
        put_delta = -0.5
        contracts_needed = abs(needed_delta / (put_delta * atm_strike * contract_multiplier))

        return {
            "needed_delta": round(needed_delta, 0),
            "contracts": int(contracts_needed),
            "estimated_cost": round(contracts_needed * atm_strike * 0.03 * contract_multiplier, 2),
            "hedge_ratio": round(contracts_needed * contract_multiplier * atm_strike / portfolio_value * 100, 1),
            "action": "buy_put" if needed_delta < 0 else "sell_call"
        }
```

### 天龙引擎协同命令

```bash
# 策略推荐
[@60-01] 根据当前市场格局推荐合适的期权策略

# 对冲计算
[@64-02] 计算期权对冲方案，目标组合Delta中性

# 隐含波动率分析
[@64-02] 分析沪深300期权隐含波动率曲面，寻找套利机会

# 完整工作流
[@64-02] market-regime → options-strategy-advisor → position-sizer-pro → trader-memory
```

### 市场格局与策略匹配矩阵

| 市场格局 | IV Rank | 推荐策略 | 核心逻辑 |
|----------|---------|---------|---------|
| 强势上升 | 任意 | 备兑Call / Bull Call Spread | 收益增强+有限风险 |
| 上升格局 | <50% | 保护性Put (低IV便宜) | 下行保险 |
| 上升格局 | >60% | 卖出Put | 卖出高IV赚权利金 |
| 中性震荡 | <40% | Long Straddle | 低IV买入赌波动 |
| 中性震荡 | >60% | Short Straddle | 高IV卖出收权利金 |
| 弱势下降 | 任意 | 熊市价差 / Protective Put | 对冲下行+降低成本 |
| 恐慌筑底 | >80% | Long Strangle | IV极高→买入低成本 |

### 与现有技能协同

| 天龙技能 | 协同方式 | 效果 |
|---------|---------|------|
| **market-regime-analyzer** | 格局→策略匹配 | 智能策略推荐 |
| **position-sizer-pro** | 权利金→仓位成本 | 整体风险预算控制 |
| **trader-memory-system** | 期权交易→历史记忆 | 策略效果追踪 |

### 局限与注意事项

1. **模型假设**：Black-Scholes假设股价服从对数正态分布，极端行情会偏离
2. **波动率微笑**：实际期权市场存在Skew，简单的BS定价可能低估虚值期权
3. **流动性风险**：深度虚值期权可能流动性差，买卖价差大
4. **保证金风险**：卖出期权需要保证金账户支撑

### 参考来源

- McMillan: Options as a Strategic Investment
- Sheldon Natenberg: Option Pricing and Volatility
- John Hull: Options, Futures, and Other Derivatives
