# Options Analysis Skill

## L0: 一句话描述
期权链分析 + IV Rank计算 + Options Score多因子评分

## L1: 使用场景
期权交易决策、IV Crush风险识别、期权组合评分排序

## L2: 详细文档

### 核心功能

#### 1. 期权链解析
```python
from options_analyzer import OptionsChain

chain = OptionsChain("AAPL")
puts = chain.get_puts(strike_low=170, strike_high=190)
calls = chain.get_calls(expiry="2024-12-20")
```

#### 2. IV Rank计算
```
IV Rank = (当前IV - 52周最低IV) / (52周最高IV - 52周最低IV) × 100%

判断:
- IV Rank > 70: IV偏高，适合卖期权
- IV Rank < 30: IV偏低，适合买期权
```

#### 3. Earnings IV Crush分析
```
事件驱动分析:
- 财报前IV飙升
- 财报后IV急剧下降 (IV Crush)
- 历史IV变化模式识别
```

#### 4. Options Score多因子模型
```
Score = Σ(因子权重 × 因子值)

因子:
- IV Rank权重: 0.25
- Volume/OI比值: 0.20
- Price Momentum: 0.20
- Earnings Factor: 0.15
- Gamma Exposure: 0.20
```

### CLI命令

```bash
# 期权链分析
options-analysis AAPL --expiry 2024-12-20

# IV Rank计算
options-analysis AAPL --iv-rank

# Earnings IV Crush
options-analysis AAPL --earnings-crush --earnings-date 2025-01-28

# Options Score排序
options-analysis AAPL MSFT GOOGL --score --top 5

# 完整分析报告
options-analysis AAPL --full-report --output report.json
```

### 与天龙岗位协同

| 天龙岗位 | 使用场景 |
|---------|---------|
| **60-01 投资总监** | 期权组合IV Rank配置 |
| **64-02 算法交易员** | Options Score自动交易 |
| **66-01 风控经理** | IV Crush风险监控 |
