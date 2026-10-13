# Volatility Intelligence Skill

## L0: 一句话描述
波动率微笑分析、期限结构、波动率风险溢价(VRP)计算

## L1: 使用场景
识别波动率交易机会、检测IV异常、波动率期限结构择时

## L2: 详细文档

### 核心功能

#### 1. 隐含波动率 (IV) 计算
```
方法: Black-Scholes反推
输入: 期权价格、标的价格、执行价、到期时间、无风险利率
输出: IV百分比

判断标准:
- IV > 50%: 高波动率环境
- IV < 20%: 低波动率环境
- IV > HV 30%+: IV相对偏高
```

#### 2. 波动率微笑 (Vol Smile)
```
现象: 同到期日期权，IV随执行价呈"微笑"形状
解读:
- 左偏(Skew): 下跌风险溢价
- 右偏: 上涨预期强烈
- 对称: 市场中性

分析方法:
- Strike vs IV散点图
- Skew指数计算
- 历史Skew追踪
```

#### 3. 波动率期限结构 (Term Structure)
```
结构类型:
- 正向(Contango): 远期IV > 近端IV → 正常市场
- 反向(Backwardation): 远期IV < 近端IV → 危机/冲击
- 平坦(Flat): IV跨期限接近 → 转折信号

交易应用:
- Contango: 卖出远期期权
- Backwardation: 买入近端期权
```

#### 4. 波动率风险溢价 (VRP)
```
VRP = IV - HV (历史波动率)

策略:
- VRP > 0: 卖出期权获IV溢价
- VRP < 0: 买入期权赌波动率回归

计算:
VRP_30d = IV_30d - HV_30d
VRP_60d = IV_60d - HV_60d
```

### CLI命令

```bash
# IV分析
volatility-intelligence AAPL --iv --chain

# 波动率微笑
volatility-intelligence AAPL --smile --expiry 2024-12-20

# 期限结构
volatility-intelligence AAPL --term-structure --expirations 30,60,90

# VRP分析
volatility-intelligence AAPL --vrp --hist-window 252

# 综合报告
volatility-intelligence AAPL --full-report --output vol_report.json
```

### 与天龙岗位协同

| 天龙岗位 | 使用场景 |
|---------|---------|
| **60-01 投资总监** | VRP择时决策 |
| **64-01 量化研究员** | 波动率因子研究 |
| **66-01 风控经理** | IV异常监控 |
