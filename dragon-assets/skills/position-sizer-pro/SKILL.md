---
license: UNKNOWN
triggers: ["position sizer pro", "仓位管理器 (Position Sizer Pro)"]
---
# 仓位管理器 (Position Sizer Pro)

## L0: 一句话描述 (≤15字)
ATR动态仓位+凯利公式+风险预算管理系统。

## L1: 使用场景 (50-100字)
当需要对单笔交易进行仓位计算和风险预算管理时使用，包含ATR波动率适配、凯利公式最优仓位、风险预算分配。适用于天龙引擎60-01投资总监和64-02算法交易员的买入时机判断和仓位调整决策。

## L2: 详细文档

### 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ 仓位管理器 — 四层风险控制体系                              │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: 单笔风险预算                                     │
│    → 单笔最大亏损 ≤ 总账户1-2%                           │
│    → 止损距离 = 入口价 × ATR倍数                         │
│                                                              │
│  Layer 2: 波动率适配                                       │
│    → 高波动股：止损距离宽 → 仓位轻                        │
│    → 低波动股：止损距离窄 → 仓位重                        │
│    → ATR(14)作为波动率基准                                │
│                                                              │
│  Layer 3: 凯利公式优化                                     │
│    → f* = (bp - q) / b                                   │
│    → 实际仓位 = 凯利比例 × 风险系数(0.2-0.5)            │
│                                                              │
│  Layer 4: 总仓位控制                                       │
│    → 总风险敞口 ≤ 账户总值6%                              │
│    → 单市场 ≤ 25%                                        │
│    → 相关标的分散                                          │
└─────────────────────────────────────────────────────────────┘
```

### 仓位计算公式

```
┌─────────────────────────────────────────────────────────────┐
│ 单笔仓位计算                                                │
├─────────────────────────────────────────────────────────────┤
│  1. 止损距离 = ATR(14) × N                               │
│     N值: VCP标的=1.5, 趋势跟踪=2.0, 突破=2.5           │
│                                                              │
│  2. 单笔风险金额 = 账户总值 × 风险比例(1-2%)             │
│                                                              │
│  3. 仓位股数 = 单笔风险金额 / 止损距离                    │
│                                                              │
│  4. 凯利修正:                                             │
│     实际仓位 = 仓位股数 × min(凯利f* × 0.3, 1.0)        │
│                                                              │
│  5. 总仓位校验:                                           │
│     总仓位 ≤ 账户 × 最大仓位比例(60-80%)                   │
└─────────────────────────────────────────────────────────────┘
```

### 仓位管理代码实现

```python
def calculate_position_size(
    account_value: float,
    entry_price: float,
    atr: float,
    stop_distance_atr: float,
    win_rate: float = 0.5,
    avg_win_loss_ratio: float = 2.0,
    risk_per_trade: float = 0.02,
    max_total_risk: float = 0.06
) -> dict:
    """
    智能仓位计算
    account_value: 账户总值
    entry_price: 入口价格
    atr: ATR(14)波动率
    stop_distance_atr: ATR倍数止损距离
    win_rate: 历史胜率
    avg_win_loss_ratio: 平均盈利/平均亏损
    risk_per_trade: 单笔风险比例 (默认2%)
    max_total_risk: 总风险敞口 (默认6%)
    """
    results = {
        "stop_loss_price": 0.0,          # 止损价格
        "position_size": 0,            # 仓位股数
        "position_value": 0.0,         # 仓位市值
        "risk_amount": 0.0,             # 风险金额
        "kelly_fraction": 0.0,           # 凯利比例
        "actual_fraction": 0.0,          # 实际仓位比例
        "risk_per_trade_pct": 0.0,     # 单笔风险%
        "total_risk_check": False,       # 总风险校验
        "recommendation": "neutral"      # 建议
    }

    # Layer 1: 计算止损价格
    stop_loss_price = entry_price - (atr * stop_distance_atr)
    results["stop_loss_price"] = round(stop_loss_price, 2)

    # Layer 2: 单笔风险金额
    risk_amount = account_value * risk_per_trade
    results["risk_amount"] = risk_amount

    # Layer 3: 基础仓位股数
    stop_distance = entry_price - stop_loss_price
    if stop_distance <= 0:
        results["recommendation"] = "invalid_entry"
        return results

    raw_position = risk_amount / stop_distance
    results["position_size"] = int(raw_position)

    # Layer 4: 凯利公式优化
    # f* = (bp - q) / b
    # b = avg_win_loss_ratio, p = win_rate, q = 1 - win_rate
    b = avg_win_loss_ratio
    p = win_rate
    q = 1 - p

    kelly_f = max(0, (b * p - q) / b)
    results["kelly_fraction"] = kelly_f

    # 实际仓位 = 凯利比例 × 风险系数(0.3)
    # 凯利比例通常需要打折使用（全额凯利风险过大）
    kelly_adjusted = kelly_f * 0.3
    results["actual_fraction"] = kelly_adjusted

    # 应用凯利修正
    adjusted_position = int(raw_position * min(kelly_adjusted * 3, 1.5))
    results["position_size"] = adjusted_position

    # Layer 5: 仓位市值
    position_value = results["position_size"] * entry_price
    results["position_value"] = round(position_value, 2)
    results["risk_per_trade_pct"] = (
        (results["position_size"] * stop_distance) / account_value * 100
    )

    # Layer 6: 总仓位校验
    total_risk = results["risk_per_trade_pct"] / 100
    results["total_risk_check"] = total_risk <= max_total_risk

    # Layer 7: 推荐建议
    if results["risk_per_trade_pct"] > 2.0:
        results["recommendation"] = "reduce_position"
    elif results["risk_per_trade_pct"] <= 1.0 and kelly_f > 0.1:
        results["recommendation"] = "increase_position"
    elif not results["total_risk_check"]:
        results["recommendation"] = "total_risk_limit_reached"
    else:
        results["recommendation"] = "acceptable"

    return results


def calculate_portfolio_risk(positions: list, account_value: float) -> dict:
    """
    组合整体风险评估
    positions: [{symbol, shares, stop_loss, entry_price}, ...]
    """
    total_exposure = 0.0
    total_risk = 0.0
    market_exposure = {}

    for pos in positions:
        pos_value = pos["shares"] * pos["entry_price"]
        risk_per_pos = pos["shares"] * (pos["entry_price"] - pos["stop_loss"])

        total_exposure += pos_value
        total_risk += risk_per_pos
        market = pos.get("market", "default")
        market_exposure[market] = market_exposure.get(market, 0) + pos_value

    results = {
        "total_exposure_pct": total_exposure / account_value * 100,
        "total_risk_pct": total_risk / account_value * 100,
        "market_exposure": {
            k: v / account_value * 100 for k, v in market_exposure.items()
        },
        "leverage": total_exposure / account_value,
        "warnings": []
    }

    # 风险警告
    if results["total_exposure_pct"] > 80:
        results["warnings"].append("总仓位过高，建议减仓")
    if results["total_risk_pct"] > 6:
        results["warnings"].append("总风险敞口超6%")
    for market, pct in results["market_exposure"].items():
        if pct > 25:
            results["warnings"].append(f"{market}市场敞口超25%")

    return results
```

### 天龙引擎协同命令

```bash
# 启动仓位计算
[@60-01] 计算当前账户的最佳仓位，标的XYZ，入口价100，ATR=2.5

# 量化研究场景
[@64-02] 使用position-sizer-pro计算凯利最优仓位

# 完整工作流
[@64-02] market-regime-analyzer → vcp-canslim-screener → position-sizer-pro → trader-memory-system
```

### 仓位管理矩阵

| 市场环境 | 单笔风险 | 总仓位上限 | ATR倍数 | 凯利系数 |
|----------|----------|-----------|---------|-----------|
| **强势上升** | 2.0% | 80% | 1.5 | 0.3 |
| **上升格局** | 1.5% | 60% | 2.0 | 0.25 |
| **中性震荡** | 1.0% | 40% | 2.5 | 0.2 |
| **弱势下降** | 0.5% | 20% | 3.0 | 0.15 |

### 与现有技能协同

| 天龙技能 | 协同方式 | 效果 |
|---------|---------|------|
| **market-regime-analyzer** | 格局强→仓位重，格局弱→仓位轻 | 动态风险调整 |
| **vcp-canslim-screener** | 评分高→允许更高仓位 | 标的质量加权 |
| **trader-memory-system** | 历史仓位表现→优化参数 | 策略持续迭代 |

### 局限与注意事项

1. **凯利公式假设**：需要准确的胜率和盈亏比估计
2. **ATR滞后性**：极端波动时ATR反应滞后
3. **不能替代止损**：任何仓位管理都不能替代硬止损
4. **相关性风险**：分散仓位降低 idiosyncratic 风险，但不能消除系统性风险

### 参考来源

- Edward Thorp: 凯利公式在21点和投资中的应用
- Van Tharp: 资金管理公式 (Super Traders)
- Mark Douglas: 交易心理分析 (The Disciplined Trader)
- William O'Neil: CANSLIM中的仓位管理原则
