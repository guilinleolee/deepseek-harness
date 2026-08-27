# Greeks Calculator Skill

## L0: 一句话描述
期权希腊字母计算：Delta/Gamma/Theta/Vega/Rho

## L1: 使用场景
期权组合Greeks风控、Delta对冲、Gamma Scalping交易

## L2: 详细文档

### 五个希腊字母

#### 1. Delta (Δ) - 价格敏感度
```
定义: 标的价格变化1元，期权价格变化多少
范围:
- Call: 0 ~ 1
- Put: -1 ~ 0
- ATM: ≈ 0.5 (Call) / ≈ -0.5 (Put)

应用:
- Delta Hedge: 构建Delta中性组合
- 概率近似: Delta ≈ 到期概率
- 仓位规模: 100 shares / Delta = 期权数量
```

#### 2. Gamma (Γ) - Delta变化率
```
定义: 标的价格变化1元，Delta变化多少
特点:
- ATM期权Gamma最大
- 临近到期Gamma急剧增加
- 正值(多头期权总是正Gamma)

应用:
- Gamma Scalping: 利用Gamma赚取时间价值
- 风险控制: 高Gamma = 高风险
```

#### 3. Theta (Θ) - 时间衰减
```
定义: 每天期权时间价值损失多少
特点:
- 多头期权Theta为负(每天损耗)
- 空头期权Theta为正(每天收取)
- ATM期权Theta损耗最快

应用:
- 卖方策略: 收取Theta
- Theta Decay曲线: 临近到期加速衰减
```

#### 4. Vega (ν) - 波动率敏感度
```
定义: IV变化1%，期权价格变化多少
特点:
- ATM期权Vega最大
- 长期期权Vega > 短期期权
- 多头期权Vega为正

应用:
- IV预期: 买入Vega赌IV上涨
- IV溢价: 卖出Vega赚IV均值回归
```

#### 5. Rho (ρ) - 利率敏感度
```
定义: 利率变化1%，期权价格变化多少
特点:
- Call: Rho > 0 (利率↑ → Call↑)
- Put: Rho < 0 (利率↑ → Put↓)
- 短期期权对利率不敏感

应用:
- 利率变动预期交易
- 低利率环境: Put Rho影响小
```

### Black-Scholes计算公式

```python
from greeks_calculator import GreeksCalculator

calc = GreeksCalculator(
    S=180,      # 标的价格
    K=180,      # 执行价
    T=30/365,   # 到期时间(年)
    r=0.05,     # 无风险利率
    sigma=0.25  # 波动率
)

greeks = calc.compute()
# {'delta': 0.52, 'gamma': 0.032, 'theta': -0.012, 'vega': 0.18, 'rho': 0.08}
```

### CLI命令

```bash
# 基本计算
greeks-calculator AAPL 180C --spot 180 --days 30 --iv 25

# 完整Greeks报告
greeks-calculator AAPL 180C 175P --full-report

# Delta对冲建议
greeks-calculator AAPL --delta-hedge --position "180C x10"

# 组合Greeks汇总
greeks-calculator --portfolio positions.json --summary
```

### Greeks风控阈值

| 指标 | 警戒线 | 强制平仓 |
|------|--------|---------|
| Total Delta | ±500 | ±1000 |
| Total Gamma | ±200 | ±400 |
| Total Theta | < -50 | < -100 |
| Total Vega | ±150 | ±300 |

### 与天龙岗位协同

| 天龙岗位 | 使用场景 |
|---------|---------|
| **66-01 风控经理** | Greeks风险监控 |
| **64-01 量化研究员** | Greeks因子研究 |
| **64-02 算法交易员** | Delta对冲执行 |
