# Stock Scorer Skill

## L0: 一句话描述
股票G=B+M评分系统，Basics+Momentum双因子量化评分

## L1: 使用场景
股票筛选排序、多空组合构建、基本面动量因子选股

## L2: 详细文档

### G = B + M 模型

```
总分 G = Basics分数 × 权重B + Momentum分数 × 权重M

权重配置:
- 保守型: B=0.7, M=0.3
- 平衡型: B=0.5, M=0.5
- 进取型: B=0.3, M=0.7
```

### Basics评分 (B) - 基本面

```
五个维度:

1. 估值 (Valuation) - 权重25%
   - PE Ratio: 行业对比百分位
   - PB Ratio: 账面价值比
   - PS Ratio: 销售额比
   - EV/EBITDA: 企业价值比

2. 盈利 (Earnings) - 权重25%
   - EPS增长: YoY增长率
   - 盈利质量: 经营现金流/净利润
   - 盈利稳定性: EPS标准差

3. 成长 (Growth) - 权重20%
   - 收入增长: YoY增长率
   - 利润增长: YoY增长率
   - 预期增长: Forward EPS vs Current

4. 财务健康 (Financial Health) - 权重15%
   - 负债率: D/E比率
   - 流动性: Current Ratio
   - 利息覆盖: Interest Coverage

5. 股息 (Dividend) - 权重15%
   - 股息率: Yield
   - 派息率: Payout Ratio
   - 股息增长: 5年CAGR
```

### Momentum评分 (M) - 动量

```
五个维度:

1. 价格趋势 (Price Trend) - 权重30%
   - 20日均线位置
   - 50日均线位置
   - 200日均线位置

2. 动量强度 (Momentum Strength) - 权重25%
   - ROC(20): 20日变化率
   - ROC(60): 60日变化率
   - ROC(120): 120日变化率

3. 相对强弱 (RSI) - 权重15%
   - RSI(14): 14日RSI
   - RSI偏离: 当前 vs 20日均值

4. 成交量 (Volume) - 权重15%
   - Volume Ratio: 当前量/平均量
   - Volume Trend: 量价配合度

5. 波动率 (Volatility) - 权重15%
   - 历史波动率
   - IV vs HV利差
```

### CLI命令

```bash
# 单股评分
stock-scorer AAPL --weight balanced

# 多股评分排序
stock-scorer AAPL MSFT GOOGL AMZN TSLA --top 5 --weight aggressive

# 行业扫描
stock-scorer --sector tech --top 20 --weight balanced

# 完整报告
stock-scorer AAPL --full-report --output score_report.json

# 多空组合
stock-scorer --long-short --top 10 --bottom 10
```

### 评分输出示例

```json
{
  "symbol": "AAPL",
  "total_score": 78.5,
  "basics": {
    "score": 82.3,
    "valuation": 85.0,
    "earnings": 80.0,
    "growth": 88.0,
    "financial_health": 78.0,
    "dividend": 80.0
  },
  "momentum": {
    "score": 74.7,
    "price_trend": 72.0,
    "momentum_strength": 78.0,
    "rsi": 70.0,
    "volume": 80.0,
    "volatility": 75.0
  },
  "percentile": {
    "sector": 85,
    "market": 78
  }
}
```

### 与天龙岗位协同

| 天龙岗位 | 使用场景 |
|---------|---------|
| **60-01 投资总监** | 投资组合评分 |
| **62-03 公司研究员** | 股票基本面评分 |
| **62-02 行业研究员** | 行业股票横向对比 |
