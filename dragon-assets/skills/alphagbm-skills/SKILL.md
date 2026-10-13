---
license: UNKNOWN
triggers: ["alphagbm skills", "AlphaGBM Options Intelligence Skills"]
---
# AlphaGBM Options Intelligence Skills

## L0: 一句话描述 (≤15字)
期权智能分析，希腊字母计算，波动率风险溢价分析

## L1: 使用场景 (50-100字)
适用于投资总监、量化研究员、算法交易员进行期权分析、波动率交易、风控计算。当需要进行期权定价、Greeks计算、IV Crush分析、期权组合评分时调用。

## L2: 详细文档

### 来源项目
> [AlphaGBM/skills](https://github.com/AlphaGBM/skills) - 124 Stars, MIT License
> 26个期权与股票分析AI技能，涵盖Greeks计算、波动率分析、IV Rank评分系统

### 核心能力矩阵

| 技能 | 功能 | 命令 |
|------|------|------|
| options-analysis | 期权链分析，IV Rank计算 | `/options-analysis` |
| volatility-intelligence | 波动率微笑、期限结构、VRP分析 | `/volatility-intelligence` |
| greeks-calculator | Delta/Gamma/Theta/Vega/Rho计算 | `/greeks-calculator` |
| stock-scorer | 股票G=B+M评分系统 | `/stock-scorer` |
| risk-analyzer | 期权组合风控，Greeks风控指标 | `/risk-analyzer` |

### 数据覆盖

- **美股期权**: 200+标的
- **港股期权**: 35+标的
- **ETF期权**: 20+标的
- **商品期权**: 原油、黄金等

### 期权分析技能

#### 1. Options Analysis (options-analysis)
```
功能:
- 期权链解析 (Calls/Puts, Bid/Ask, Volume, OI)
- IV Rank计算 (252日历史比较)
- Earnings IV Crush分析
- Options Score多因子评分

使用方法:
/options-analysis AAPL --expiry 2024-12-20 --score
```

#### 2. Volatility Intelligence (volatility-intelligence)
```
功能:
- 隐含波动率 (IV) 计算
- 波动率微笑 (Vol Smile)
- 波动率期限结构 (Term Structure)
- 波动率风险溢价 (VRP)

使用方法:
/volatility-intelligence AAPL --vrp --term-structure
```

#### 3. Greeks Calculator (greeks-calculator)
```
功能:
- Delta: 价格敏感度
- Gamma: Delta变化率
- Theta: 时间衰减
- Vega: 波动率敏感度
- Rho: 利率敏感度

使用方法:
/greeks-calculator AAPL 180C --days 30 --iv 25
```

#### 4. Stock Scorer (stock-scorer)
```
功能:
- G = B + M 模型
- Basics评分 (估值、盈利、成长)
- Momentum评分 (趋势、动量)
- 综合评分排序

使用方法:
/stock-scorer AAPL MSFT GOOGL --top 10
```

#### 5. Risk Analyzer (risk-analyzer)
```
功能:
- 期权组合VaR
- Greeks风控 (Delta/Gamma中性检测)
- 保证金计算
- 压力测试

使用方法:
/risk-analyzer --portfolio positions.json --var 95 --days 1
```

### 天龙引擎协同

| 天龙岗位 | 协同方式 |
|---------|---------|
| **60-01 投资总监** | 期权组合分析 + IV评分 |
| **62-03 公司研究员** | 股票G=B+M评分 |
| **64-01 量化研究员** | Greeks计算 + 回测框架 |
| **64-02 算法交易员** | Options Score执行 |
| **66-01 风控经理** | Greeks风控 + VaR |

### 安装验证

```bash
# 克隆仓库
git clone https://github.com/AlphaGBM/skills.git ~/.claude/skills/alphagbm-skills

# 验证安装
python3 ~/.claude/skills/alphagbm-skills/scripts/verify_setup.py
```

### 版本信息

- **版本**: V1.0
- **日期**: 2026-05-19
- **来源**: AlphaGBM/skills
- **License**: MIT
