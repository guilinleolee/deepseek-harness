---
license: UNKNOWN
triggers: ["market regime analyzer", "市场格局分析器 (Market Regime Analyzer)"]
---
# 市场格局分析器 (Market Regime Analyzer)

## L0: 一句话描述 (≤15字)
多维度市场格局识别与趋势判断。

## L1: 使用场景 (50-100字)
当需要对A股/港股/美股进行宏观市场格局判断时使用，包含6大广度指标计算、趋势分类（上升/下降/震荡/筑底）、板块轮动分析。适用于天龙引擎60-01投资总监和64-01量化研究员的买入时机判断和仓位调整决策。

## L2: 详细文档

### 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ 市场格局分析器 — 6大广度指标体系                            │
├─────────────────────────────────────────────────────────────┤
│  指标1: 均线多头排列率 (MA Bull %)
│    → 计算规则: 收盘价 > 5/20/60/120日均线的股票占比
│    → 权重: 25% (最重要)
│
│  指标2: MACD强度扩散率 (MACD Breadth)
│    → 计算规则: MACD柱状图扩张的股票占比
│    → 权重: 20%
│
│  指标3: 价格动量加速率 (Momentum Acceleration)
│    → 计算规则: 20日动量 > 60日动量的股票占比
│    → 权重: 20%
│
│  指标4: 新高新低扩散率 (NH-NL Breadth)
│    → 计算规则: 创52周新高的股票数 - 创52周新低的股票数
│    → 权重: 15%
│
│  指标5: 成交量分布健康度 (Volume Distribution)
│    → 计算规则: 上涨日成交量均值 / 下跌日成交量均值
│    → 权重: 10%
│
│  指标6: 相对强弱广度 (RS Breadth)
│    → 计算规则: 与大盘相比走强的股票占比
│    → 权重: 10%
└─────────────────────────────────────────────────────────────┘
```

### 格局评分公式

```
市场格局得分 = Σ(指标值 × 权重) × 100

分级标准:
- 80-100: 🟢 强势上升格局 — 持仓为主，积极做多
- 60-79:  🟡 上升格局 — 持仓，逢回调加仓
- 40-59:  🟠 中性震荡格局 — 区间操作，降低仓位
- 20-39:  🔴 弱势下降格局 — 空仓或轻仓，等待信号
- 0-19:   ⚫ 恐慌筑底格局 — 逐步建仓，等待反转
```

### 广度评分代码实现

```python
def calculate_market_regime(price_data: dict, lookback: int = 60) -> dict:
    """
    计算市场格局评分
    price_data: {symbol: [收盘价列表]}
    """
    results = {
        "ma_bull_pct": 0.0,      # 均线多头排列率
        "macd_breadth": 0.0,     # MACD强度扩散率
        "momentum_accel": 0.0,    # 动量加速率
        "nh_nl_diff": 0,          # 新高新低差值
        "volume_ratio": 1.0,       # 量能健康度
        "rs_breadth": 0.0,         # 相对强弱广度
        "overall_score": 0.0,       # 综合得分
        "regime": "neutral"         # 格局分类
    }

    n = len(price_data)
    ma_bull_count = 0
    macd_breadth_count = 0
    momentum_accel_count = 0
    new_highs = 0
    new_lows = 0
    up_volume_sum = 0
    down_volume_sum = 0
    rs_strong_count = 0

    for symbol, data in price_data.items():
        closes = data["closes"]
        volumes = data["volumes"]

        if len(closes) < 120:
            continue

        # 指标1: 均线多头排列
        ma5 = sum(closes[-5:]) / 5
        ma20 = sum(closes[-20:]) / 20
        ma60 = sum(closes[-60:]) / 60
        ma120 = sum(closes[-120:]) / 120

        if closes[-1] > ma5 and closes[-1] > ma20 and \
           closes[-1] > ma60 and closes[-1] > ma120:
            ma_bull_count += 1

        # 指标2: MACD强度
        macd, signal = calculate_macd(closes)
        if macd[-1] > macd[-2] > macd[-3]:
            macd_breadth_count += 1

        # 指标3: 动量加速
        mom20 = closes[-1] - closes[-21]
        mom60 = closes[-21] - closes[-61]
        if mom20 > mom60:
            momentum_accel_count += 1

        # 指标4: 新高新低
        high_52w = max(closes[-252:])
        low_52w = min(closes[-252:])
        if closes[-1] >= high_52w * 0.98:
            new_highs += 1
        if closes[-1] <= low_52w * 1.02:
            new_lows += 1

        # 指标5: 量能分布
        for i in range(len(closes)-1):
            if closes[i+1] > closes[i]:
                up_volume_sum += volumes[i]
            else:
                down_volume_sum += volumes[i]

        # 指标6: 相对强弱
        # (与基准指数对比，简化处理)

    # 汇总计算
    results["ma_bull_pct"] = ma_bull_count / n
    results["macd_breadth"] = macd_breadth_count / n
    results["momentum_accel"] = momentum_accel_count / n
    results["nh_nl_diff"] = new_highs - new_lows
    results["volume_ratio"] = up_volume_sum / (down_volume_sum + 0.001)

    # 综合评分
    results["overall_score"] = (
        results["ma_bull_pct"] * 0.25 +
        results["macd_breadth"] * 0.20 +
        results["momentum_accel"] * 0.20 +
        min(results["nh_nl_diff"] / 100, 1.0) * 0.15 +
        min(results["volume_ratio"], 2) / 2 * 0.10 +
        results["rs_breadth"] * 0.10
    ) * 100

    # 格局分类
    score = results["overall_score"]
    if score >= 80:
        results["regime"] = "strong_uptrend"
    elif score >= 60:
        results["regime"] = "uptrend"
    elif score >= 40:
        results["regime"] = "neutral"
    elif score >= 20:
        results["regime"] = "downtrend"
    else:
        results["regime"] = "panic_bottom"

    return results


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """计算MACD"""
    ema_fast = ema(prices, fast)
    ema_slow = ema(prices, slow)
    macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
    signal_line = ema(macd_line, signal)
    macd_histogram = [m - s for m, s in zip(macd_line, signal_line)]
    return macd_histogram, signal_line
```

### 天龙引擎协同命令

```bash
# 启动市场格局分析
[@60-01] 分析当前市场格局，输出6大指标和综合评分

# 量化研究场景
[@64-01] 使用market-regime-analyzer判断当前是否适合建仓

# 买入时机判断
[@64-01] 分析茅20成分股的市场格局

# 与其他技能协同
[@64-01] market-regime-analyzer → position-sizer-pro → trader-memory-system
```

### 与现有天龙技能协同

| 天龙技能 | 协同方式 | 效果 |
|---------|---------|------|
| **position-sizer-pro** | 格局强→加重仓，格局弱→轻仓 | 仓位动态调整 |
| **vcp-canslim-screener** | 格局上升→筛选严格，格局震荡→筛选宽松 | 筛选参数动态 |
| **trader-memory-system** | 格局判断→存入交易记忆→下次参考 | 历史判断追溯 |

### 适用市场

| 市场 | 股票池 | 指标适配 |
|------|--------|---------|
| **A股** | 茅20/沪深300成分股 | 均线参数适配 |
| **港股** | 恒生科技/恒生指数 | 均线参数适配 |
| **美股** | ~2800只主要股票 | 原始CANSLIM参数 |

### 局限与注意事项

1. **数据延迟**: 广度数据通常滞后1-2天，不要用于短期择时
2. **参数敏感性**: 均线参数(5/20/60/120)需根据市场特性调整
3. **极端行情**: 股灾期间广度指标会持续低位，不适合抄底
4. **与基本面结合**: 格局分析是择时工具，不能替代基本面分析

### 参考来源

- CANSLIM (William O'Neil): 广度确认原则
- Stan Weinstein: 走势图分析中的板块广度验证
- IBD (Investor's Business Daily): 广度指标体系
