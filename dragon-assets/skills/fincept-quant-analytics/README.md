# Fincept Quant Analytics

CFA级别量化分析能力封装，为天龙引擎提供专业的金融量化分析功能。

## 核心能力

### 1. DCF估值模型
- 自由现金流折现
- 永续增长率计算
- 安全边际分析
- 敏感性矩阵分析
- DDM (股息贴现模型)

### 2. 技术指标分析
- 移动平均线 (SMA, EMA, WMA)
- 动量指标 (RSI, MACD, Stochastic)
- 波动率指标 (Bollinger Bands, ATR)
- 趋势指标 (ADX)
- 综合交易信号生成

### 3. 期权分析
- Black-Scholes定价
- Greeks计算 (Delta, Gamma, Theta, Vega, Rho)
- 隐含波动率计算
- 期权链生成
- 策略分析 (Straddle, Strangle, Butterfly)

### 4. 风险指标
- VaR / CVaR (Value at Risk)
- 夏普比率 / 索提诺比率
- 最大回撤 / 卡尔马比率
- Beta / 特雷诺比率 / 信息比率
- Jarque-Bera正态性检验
- Ljung-Box自相关检验

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### Python API

```python
from fincept_quant import DCFAnalyzer, TechnicalAnalyzer, OptionsAnalyzer, RiskAnalyzer

# DCF估值
dcf = DCFAnalyzer()
result = dcf.dcf(ticker="AAPL", revenue=394.328, revenue_growth=0.08, operating_margin=0.28)

# 技术分析
tech = TechnicalAnalyzer()
indicators = tech.calculate(prices=[...], indicators=["sma", "rsi", "macd"])

# 期权分析
options = OptionsAnalyzer()
greeks = options.greeks(S=185, K=180, T=0.1, r=0.05, sigma=0.25)

# 风险分析
risk = RiskAnalyzer()
var = risk.value_at_risk(returns=[...], confidence=0.95)
```

### 命令行接口

```bash
# DCF估值
python -m fincept_quant.cli dcf AAPL --revenue 394 --growth 0.08 --margin 0.28

# 技术指标
python -m fincept_quant.cli tech AAPL --indicators sma,ema,rsi

# 期权Greeks
python -m fincept_quant.cli greeks --S 185 --K 180 --T 0.1 --sigma 0.25

# 风险指标
python -m fincept_quant.cli risk --rf 0.04
```

## 天龙引擎集成

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
├── SKILL.md                    # 技能总览
├── README.md                   # 本文件
├── requirements.txt            # Python依赖
└── scripts/
    ├── __init__.py            # 包入口
    ├── dcf_analyzer.py        # DCF估值模型
    ├── technical_analyzer.py  # 技术指标分析
    ├── options_analyzer.py    # 期权分析
    ├── risk_analyzer.py      # 风险指标
    └── cli.py                # 命令行接口
```

## 版本

- V1.0 (2026-04-27): 初始版本