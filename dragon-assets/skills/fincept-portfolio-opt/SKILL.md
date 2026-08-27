---
license: UNKNOWN
---

# Fincept Portfolio Optimizer Skill

## L0: 一句话描述
机构级组合优化工具，封装最大夏普/风险平价/Black-Litterman/因子归因能力。

## L1: 使用场景

### 组合优化场景
- **最大夏普组合**: 风险调整收益最优配置
- **最小波动组合**: 波动率最低的分散化组合
- **目标收益组合**: 给定期望收益下的最小方差组合

### 风险平价场景
- 对冲基金常用风险平价策略
- 基于波动率/CVaR/最大回撤的风险分配
- 适用于多资产类别配置

### Black-Litterman场景
- 融合主动投资观点的贝叶斯配置
- 利用市值作为先验分布
- 适合机构投资者结合宏观观点

### 因子归因场景
- Brinson模型分解配置/选股/交互效应
- Fama-French五因子模型分析Alpha和Beta
- 业绩归因和风险归因

## L2: 详细文档

### 核心API

#### PortfolioOptimizer
```python
from fincept_portfolio import PortfolioOptimizer

optimizer = PortfolioOptimizer()

# 基础优化
result = optimizer.optimize(
    tickers=["AAPL", "MSFT", "GOOGL", "AMZN", "META"],
    objective="max_sharpe",
    constraints={"max_weight": 0.3, "min_weight": 0.05}
)
```

#### 有效前沿
```python
frontier = optimizer.efficient_frontier(
    tickers=["AAPL", "MSFT", "GOOGL", "AMZN", "META"],
    points=50
)
```

#### 风险平价
```python
result = optimizer.risk_parity(
    tickers=["AAPL", "MSFT", "GOOGL", "BND"],
    risk_measure="volatility"
)
```

#### Black-Litterman
```python
result = optimizer.black_litterman(
    tickers=["AAPL", "MSFT", "GOOGL"],
    market_cap=[3.0, 2.5, 1.8],
    views={"AAPL": 0.12, "MSFT": 0.10},
    view_confidence=0.7
)
```

#### 因子模型
```python
result = optimizer.factor_model(
    returns=portfolio_returns,
    factors="ff5"
)
```

#### Brinson归因
```python
attribution = optimizer.brinson(
    portfolio_weights=weights,
    benchmark_weights=b_weights,
    portfolio_returns=pret,
    benchmark_returns=bret
)
```

### CLI用法
```bash
# 优化组合
python ~/.claude/skills/fincept-portfolio-opt/scripts/cli.py optimize \
  --tickers AAPL,MSFT,GOOGL,AMZN,META \
  --objective max_sharpe \
  --max-weight 0.3

# 风险平价
python ~/.claude/skills/fincept-portfolio-opt/scripts/cli.py risk-parity \
  --tickers AAPL,MSFT,GOOGL,BND

# Black-Litterman
python ~/.claude/skills/fincept-portfolio-opt/scripts/cli.py bl \
  --tickers AAPL,MSFT,GOOGL \
  --views '{"AAPL": 0.12}'

# 有效前沿
python ~/.claude/skills/fincept-portfolio-opt/scripts/cli.py frontier \
  --tickers AAPL,MSFT,GOOGL,AMZN,META \
  --points 50

# 因子模型
python ~/.claude/skills/fincept-portfolio-opt/scripts/cli.py factor \
  --factor-type ff5

# Brinson归因
python ~/.claude/skills/fincept-portfolio-opt/scripts/cli.py attribution \
  --portfolio-weights weights.json \
  --benchmark-weights benchmark.json
```

### 依赖
- pyportfolioopt>=1.5.0
- riskfolio-lib>=4.0.0
- pandas>=1.5.0
- numpy>=1.21.0
- scikit-learn>=1.0.0

### 约束条件
- `max_weight`: 单资产最大权重 (默认0.3)
- `min_weight`: 单资产最小权重 (默认0.05)
- `max_leverage`: 最大杠杆 (默认1.0)
- `min_return`: 目标最低收益 (可选)

### 返回值结构
```python
{
    "expected_return": float,   # 预期年化收益
    "volatility": float,       # 年化波动率
    "sharpe_ratio": float,     # 夏普比率
    "weights": {ticker: weight},  # 权重字典
    "optimal_returns": list,   # 有效前沿收益序列
    "optimal_volatility": list  # 有效前沿波动序列
}
```