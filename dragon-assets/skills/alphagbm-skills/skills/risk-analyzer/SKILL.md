# Risk Analyzer Skill

## L0: 一句话描述
期权组合VaR计算、Greeks风控指标、压力测试

## L1: 使用场景
期权组合风险评估、Greeks中性对冲、VaR风险限额管理

## L2: 详细文档

### 核心功能

#### 1. VaR (Value at Risk) 计算
```
方法: Historical Simulation / Parametric / Monte Carlo

95% VaR: 95%置信度下，最大单日损失
99% VaR: 99%置信度下，最大单日损失

输出:
- Dollar VaR: 金额损失
- Percent VaR: 百分比损失
- Component VaR: 各合约VaR贡献
```

#### 2. Greeks风控指标
```
核心指标:

1. Delta
   - 组合Delta: Σ(Delta × 数量 × 乘数)
   - Delta Dollar: Σ(Delta × 标的价格 × 数量)

2. Gamma
   - 组合Gamma: Σ(Gamma × 数量 × 乘数)
   - Gamma Risk: 高Gamma暴露

3. Theta
   - 日Theta消耗: Σ(Theta × 数量 × 乘数)
   - 时间损耗预警

4. Vega
   - 组合Vega: Σ(Vega × 数量 × 乘数)
   - IV敏感性暴露
```

#### 3. 保证金计算
```
SPAN保证金模型:
- 风险数组 (Risk Array)
- 扫描价格范围
- 跨月价差抵销

账户预警:
- 警告线: 保证金 × 1.3
- 追缴线: 保证金 × 1.1
- 强平线: 保证金 × 1.0
```

#### 4. 压力测试
```
场景测试:
- ±1σ 价格变动
- ±2σ 价格变动
- IV ±20% 变动
- 相关性崩溃
- 流动性枯竭

历史情景:
- 2020-03 COVID Crash
- 2022-11 FTX暴雷
- 2008-09 金融危机
```

### CLI命令

```bash
# 组合VaR计算
risk-analyzer --portfolio positions.json --var 95 --days 1

# Greeks汇总
risk-analyzer --portfolio positions.json --greeks-summary

# 保证金检查
risk-analyzer --portfolio positions.json --margin --account 123456

# 压力测试
risk-analyzer --portfolio positions.json --stress-test --scenarios covid,ftx,rate

# 完整风控报告
risk-analyzer --portfolio positions.json --full-report --output risk_report.json
```

### 风控阈值配置

```yaml
# 风险限额 (示例)
limits:
  daily_loss:
    warning: 10000    # $10,000
    critical: 25000   # $25,000

  greeks:
    delta:
      warning: ±500
      critical: ±1000
    gamma:
      warning: ±200
      critical: ±400
    theta:
      warning: -100    # 每日损耗
      critical: -250
    vega:
      warning: ±150
      critical: ±300

  margin:
    warning_ratio: 1.3
    margin_call: 1.1
    liquidation: 1.0
```

### 仓位格式

```json
{
  "positions": [
    {
      "symbol": "AAPL",
      "type": "call",
      "expiry": "2024-12-20",
      "strike": 180,
      "quantity": 10,
      "side": "long"
    },
    {
      "symbol": "AAPL",
      "type": "put",
      "expiry": "2024-12-20",
      "strike": 175,
      "quantity": 5,
      "side": "short"
    }
  ]
}
```

### 与天龙岗位协同

| 天龙岗位 | 使用场景 |
|---------|---------|
| **66-01 风控经理** | 日常风控监控 |
| **66-02 合规专员** | 限额合规检查 |
| **64-02 算法交易员** | 自动风控触发 |
| **60-01 投资总监** | 组合风险决策 |
