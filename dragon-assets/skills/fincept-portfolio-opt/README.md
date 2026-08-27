# Fincept Portfolio Optimizer

Institution-grade portfolio optimization tools.

## Quick Start

```python
from fincept_portfolio import PortfolioOptimizer

optimizer = PortfolioOptimizer()

# Max Sharpe portfolio
result = optimizer.optimize(
    tickers=["AAPL", "MSFT", "GOOGL", "AMZN", "META"],
    objective="max_sharpe"
)
```

## CLI Usage

```bash
# Max Sharpe optimization
python scripts/cli.py optimize --tickers AAPL,MSFT,GOOGL,AMZN,META --objective max_sharpe

# Risk parity
python scripts/cli.py risk-parity --tickers AAPL,MSFT,GOOGL,BND

# Black-Litterman
python scripts/cli.py bl --tickers AAPL,MSFT,GOOGL --views '{"AAPL": 0.12}'

# Efficient frontier
python scripts/cli.py frontier --tickers AAPL,MSFT,GOOGL,AMZN,META --points 50

# Factor model
python scripts/cli.py factor --tickers AAPL,MSFT,GOOGL --factor-type ff5

# Brinson attribution
python scripts/cli.py attribution --portfolio-weights weights.json --benchmark-weights benchmark.json
```

## Features

| Feature | Description |
|---------|-------------|
| **Portfolio Optimization** | Max Sharpe, Min Volatility, Max Return |
| **Efficient Frontier** | N-point frontier calculation |
| **Hierarchical Risk Parity** | HRP without covariance inversion |
| **Risk Parity** | Volatility/CVaR/Drawdown based |
| **Black-Litterman** | Bayesian view integration |
| **Fama-French** | FF3/FF5/Carhart factor models |
| **Brinson Attribution** | Allocation/Selection/Interaction effects |

## Installation

```bash
pip install -r requirements.txt
```