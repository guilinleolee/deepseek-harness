---
license: UNKNOWN
triggers: ["fincept quant analytics", "Fincept Quant Analytics — CFA级别量化分析Skill"]
---
# Fincept Quant Analytics — CFA级别量化分析Skill

## 版本历史

| 版本 | 日期 | 描述 |
|------|------|------|
| V1.0 | 2026-04-27 | 初始版本，CFA级别量化分析能力 |

## 概述

Fincept Quant Analytics封装了CFA级别的量化分析能力，提供DCF估值、技术指标、期权分析、风险指标等核心功能。

## 核心能力

### 1. DCF估值模型

```python
from fincept_quant import DCFAnalyzer

analyzer = DCFAnalyzer()

result = analyzer.dcf(
    ticker="AAPL",
    revenue_growth=0.08,
    operating_margin=0.28,
    discount_rate=0.10,
    terminal_growth=0.03,
    years=5
)

print(f"内在价值: ${result['intrinsic_value']:.2f}")
print(f"当前价格: ${result['current_price']:.2f}")
print(f"安全边际: {result['margin_of_safety']:.1%}")
```

### 2. 技术指标分析

```python
from fincept_quant import TechnicalAnalyzer

analyzer = TechnicalAnalyzer()

indicators = analyzer.calculate(
    prices=[100, 102, 101, 105, 107, 106, 110, 112],
    indicators=["sma", "ema", "rsi", "macd", "bbands", "atr"]
)

signals = analyzer.signals(ticker="AAPL", indicators=indicators)
print(f"综合信号: {signals['combined']}")  # bullish/bearish/neutral
```

### 3. 期权分析

```python
from fincept_quant import OptionsAnalyzer

analyzer = OptionsAnalyzer()

# Greeks计算
greeks = analyzer.greeks(S=185, K=180, T=0.1, r=0.05, sigma=0.25)
print(f"Delta: {greeks['delta']:.3f}")
print(f"Gamma: {greeks['gamma']:.4f}")
print(f"Theta: {greeks['theta']:.4f}")
print(f"Vega: {greeks['vega']:.4f}")

# Black-Scholes定价
price = analyzer.black_scholes(S=185, K=180, T=0.1, r=0.05, sigma=0.25)
print(f"期权价格: ${price:.2f}")
```

### 4. 风险指标

```python
from fincept_quant import RiskAnalyzer

analyzer = RiskAnalyzer()

returns = [0.01, -0.02, 0.03, 0.015, -0.01, 0.02]

# VaR计算
var = analyzer.value_at_risk(returns, confidence=0.95)
print(f"95% VaR: {var:.2%}")

# 夏普比率
sharpe = analyzer.sharpe_ratio(returns, risk_free=0.04)
print(f"夏普比率: {sharpe:.2f}")

# 最大回撤
max_dd = analyzer.max_drawdown(returns)
print(f"最大回撤: {max_dd:.2%}")
```

### 5. 统计检验

```python
# 收益率正态性检验
normality = analyzer.jarque_bera(returns)
print(f"JB统计量: {normality['jb_stat']:.4f}")
print(f"p值: {normality['p_value']:.4f}")

# 自相关检验
autocorr = analyzer.ljung_box(returns, lags=10)
```

## 命令行接口

```bash
# DCF估值
python -m fincept_quant.cli dcf AAPL --growth 0.08 --margin 0.28 --discount 0.10

# 技术指标
python -m fincept_quant.cli tech AAPL --indicators sma,ema,rsi

# 期权Greeks
python -m fincept_quant.cli greeks --S 185 --K 180 --T 0.1 --sigma 0.25

# 风险指标
python -m fincept_quant.cli risk --returns 0.01,-0.02,0.03,0.015
```

## 安装依赖

```bash
pip install numpy pandas scipy ta-lib pandas-ta quantlib
```

## 与天龙引擎集成

本Skill为以下天龙岗位提供量化分析能力：

| 天龙岗位 | 能力映射 |
|---------|---------|
| 64-01 量化研究员 | DCF、风险指标、统计检验 |
| 60-01 投资总监 | 绝对估值、风险指标 |
| 62-02 行业研究员 | 技术分析、相对估值 |
| 17-01 数据分析师 | 统计检验、风险指标 |

## 文件结构

```
fincept-quant-analytics/
├── SKILL.md                    # 本文件
├── scripts/
│   ├── __init__.py            # 包入口
│   ├── dcf_analyzer.py        # DCF估值模型
│   ├── technical_analyzer.py # 技术指标分析
│   ├── options_analyzer.py    # 期权分析
│   ├── risk_analyzer.py      # 风险指标
│   └── cli.py                # 命令行接口
├── requirements.txt           # 依赖列表
└── README.md                  # 使用说明
```