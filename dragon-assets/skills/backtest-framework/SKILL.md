---
license: UNKNOWN
triggers: ["backtest framework", "回测框架 (Backtest Framework)"]
---
# 回测框架 (Backtest Framework)

## L0: 一句话描述 (≤15字)
事件驱动回测引擎+滑点建模+统计分析报告。

## L1: 使用场景 (50-100字)
当需要验证交易策略的历史表现时使用，包含事件驱动回测、交易成本建模、统计显著性分析。适用于天龙引擎64-01量化研究员的新策略验证和参数优化决策。

## L2: 详细文档

### 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ 回测框架 — 五模块架构                                       │
├─────────────────────────────────────────────────────────────┤
│  Module 1: 事件驱动引擎                                    │
│    → OHLCV数据流 → 信号生成 → 订单执行 → 持仓更新          │
│    → 逐根(K线)运行，保证信号不偷看未来                     │
│                                                              │
│  Module 2: 交易成本建模                                    │
│    → 滑点: 0.05-0.2% (根据流动性调整)                    │
│    → 佣金: 0.03-0.1%                                     │
│    → 冲击成本: 基于成交量占比                               │
│                                                              │
│  Module 3: 风险指标                                        │
│    → Sharpe/Max Drawdown/Calmar/Win Rate                  │
│    → 蒙特卡洛模拟                                          │
│    → 最大单日亏损/MDD持续时间                               │
│                                                              │
│  Module 4: 统计显著性                                      │
│    → 样本量检验 (n≥30)                                    │
│    → t检验策略vs基准                                       │
│    → 序列相关性检验                                        │
│                                                              │
│  Module 5: 参数优化                                         │
│    → 网格搜索 (Grid Search)                                 │
│    → Walk-Forward Analysis                                 │
│    → 参数敏感性分析                                        │
└─────────────────────────────────────────────────────────────┘
```

### 回测代码实现

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import numpy as np


@dataclass
class BacktestConfig:
    """回测配置"""
    initial_capital: float = 1000000.0    # 初始资金
    commission: float = 0.001             # 佣金 (0.1%)
    slippage: float = 0.0005              # 滑点 (0.05%)
    impact_factor: float = 0.1            # 市场冲击系数
    benchmark: str = "000300"              # 对比基准 (沪深300)


@dataclass
class Trade:
    """回测交易"""
    entry_date: datetime
    entry_price: float
    quantity: int
    stop_loss: float
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    pnl: float = 0.0
    pnl_pct: float = 0.0
    holding_bars: int = 0
    exit_reason: str = ""                  # stop/target/manual


@dataclass
class BacktestResult:
    """回测结果"""
    total_return: float = 0.0             # 总收益率
    annualized_return: float = 0.0          # 年化收益率
    sharpe_ratio: float = 0.0             # 夏普比率
    max_drawdown: float = 0.0             # 最大回撤
    max_drawdown_duration: int = 0         # 最大回撤持续时间
    win_rate: float = 0.0                 # 胜率
    profit_factor: float = 0.0             # 盈亏比
    calmar_ratio: float = 0.0              # 卡玛比率
    trade_count: int = 0                  # 交易次数
    avg_holding_days: float = 0.0          # 平均持仓天数

    equity_curve: list = field(default_factory=list)
    trades: list = field(default_factory=list)

    # 统计显著性
    t_statistic: float = 0.0
    p_value: float = 1.0
    sample_size: int = 0

    # 参数
    params: dict = field(default_factory=dict)


class BacktestEngine:
    """事件驱动回测引擎"""

    def __init__(self, config: BacktestConfig):
        self.config = config
        self.trades: list[Trade] = []
        self.equity_curve: list = []
        self.current_position: Optional[Trade] = None

    def run(
        self,
        data: dict,          # {date: {symbol: OHLCV}}
        signals: list,        # [{date, symbol, signal: buy/sell/short, params}]
        benchmark_data: list  # [{date, close}]
    ) -> BacktestResult:
        """
        运行回测
        data: {date: {symbol: {"open":, "high":, "low":, "close":, "volume":}}}
        signals: 信号列表
        """
        capital = self.config.initial_capital
        position = None
        equity_timeline = []

        for date, day_data in sorted(data.items()):
            # 检查信号
            signal = self._get_signal(date, signals)
            if signal:
                if signal["action"] == "buy" and position is None:
                    position = self._open_position(
                        date, signal, day_data, capital
                    )
                elif signal["action"] == "sell" and position is not None:
                    position = self._close_position(
                        date, position, day_data, "signal"
                    )

            # 检查止损
            if position:
                symbol = position.get("symbol", "")
                if symbol in day_data:
                    low = day_data[symbol]["low"]
                    if low <= position["stop_loss"]:
                        position = self._close_position(
                            date, position, day_data, "stop"
                        )

            # 更新权益曲线
            equity = capital
            if position:
                symbol = position["symbol"]
                if symbol in day_data:
                    current_price = day_data[symbol]["close"]
                    equity += (current_price - position["entry_price"]) * position["quantity"]

            equity_timeline.append({"date": date, "equity": equity})

        # 计算结果
        result = self._calculate_metrics(equity_timeline, self.trades)
        result.equity_curve = equity_timeline
        result.trades = self.trades
        return result

    def _open_position(
        self, date, signal, day_data, capital
    ) -> dict:
        """开仓"""
        symbol = signal["symbol"]
        price = day_data[symbol]["close"] * (1 + self.config.slippage)

        # 仓位计算
        risk_amount = capital * 0.02  # 2%风险
        stop_loss = signal.get("stop_loss", price * 0.95)
        stop_distance = price - stop_loss
        quantity = int(risk_amount / stop_distance)

        position_value = price * quantity
        commission = position_value * self.config.commission

        return {
            "symbol": symbol,
            "entry_date": date,
            "entry_price": price,
            "quantity": quantity,
            "stop_loss": stop_loss,
            "atr": signal.get("atr", 0)
        }

    def _close_position(
        self, date, position, day_data, reason
    ) -> dict:
        """平仓"""
        symbol = position["symbol"]
        price = day_data[symbol]["close"] * (1 - self.config.slippage)

        pnl = (price - position["entry_price"]) * position["quantity"]
        pnl_pct = (price - position["entry_price"]) / position["entry_price"] * 100

        trade = Trade(
            entry_date=position["entry_date"],
            entry_price=position["entry_price"],
            quantity=position["quantity"],
            stop_loss=position["stop_loss"],
            exit_date=date,
            exit_price=price,
            pnl=pnl,
            pnl_pct=pnl_pct,
            exit_reason=reason
        )
        self.trades.append(trade)
        return None  # 清空持仓

    def _get_signal(self, date, signals) -> Optional[dict]:
        """获取当日信号"""
        for sig in signals:
            if sig["date"] == date:
                return sig
        return None

    def _calculate_metrics(
        self, equity_curve: list, trades: list
    ) -> BacktestResult:
        """计算回测指标"""
        if not equity_curve:
            return BacktestResult()

        equity = [e["equity"] for e in equity_curve]
        returns = np.diff(equity) / equity[:-1]

        # 基础收益
        total_return = (equity[-1] - equity[0]) / equity[0] * 100

        # 年化收益 (假设250交易日)
        n_years = len(equity_curve) / 250
        annualized = ((1 + total_return / 100) ** (1 / n_years) - 1) * 100 if n_years > 0 else 0

        # 夏普比率
        if len(returns) > 1 and np.std(returns) > 0:
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(250)
        else:
            sharpe = 0.0

        # 最大回撤
        peak = equity[0]
        max_dd = 0.0
        max_dd_duration = 0
        current_dd_duration = 0
        dd_start = 0

        for i, eq in enumerate(equity):
            if eq > peak:
                peak = eq
                current_dd_duration = 0
            else:
                current_dd_duration += 1
                dd = (peak - eq) / peak * 100
                if dd > max_dd:
                    max_dd = dd
                    max_dd_duration = current_dd_duration

        # 交易统计
        wins = [t for t in trades if t.pnl > 0]
        losses = [t for t in trades if t.pnl <= 0]

        win_rate = len(wins) / len(trades) * 100 if trades else 0
        profit_factor = (
            abs(sum(t.pnl for t in wins) / sum(t.pnl for t in losses))
            if losses and sum(t.pnl for t in losses) != 0 else 0
        )

        # 卡玛比率
        calmar = annualized / max_dd if max_dd > 0 else 0

        return BacktestResult(
            total_return=total_return,
            annualized_return=annualized,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            max_drawdown_duration=max_dd_duration,
            win_rate=win_rate,
            profit_factor=profit_factor,
            calmar_ratio=calmar,
            trade_count=len(trades),
            sample_size=len(trades)
        )


def walk_forward_analysis(
    engine: BacktestEngine,
    data: dict,
    signals: list,
    train_window: int = 252,    # 训练窗口 (交易日)
    test_window: int = 63,       # 测试窗口 (63交易日≈1季度)
    step: int = 21               # 滚动步长
) -> list[BacktestResult]:
    """
    Walk-Forward Analysis
    滚动窗口前向分析，避免过拟合
    """
    dates = sorted(data.keys())
    results = []

    for i in range(0, len(dates) - train_window, step):
        train_end = i + train_window
        test_end = min(train_end + test_window, len(dates))

        train_data = {d: data[d] for d in dates[i:train_end]}
        test_data = {d: data[d] for d in dates[train_end:test_end]}

        train_signals = [s for s in signals if dates[i] <= s["date"] < dates[train_end]]
        test_signals = [s for s in signals if dates[train_end] <= s["date"] < dates[test_end]]

        # 训练阶段找最优参数
        train_result = engine.run(train_data, train_signals, [])

        # 测试阶段用最优参数
        test_result = engine.run(test_data, test_signals, [])

        results.append({
            "train_period": (dates[i], dates[train_end]),
            "test_period": (dates[train_end], dates[test_end]),
            "train_sharpe": train_result.sharpe_ratio,
            "test_sharpe": test_result.sharpe_ratio,
            "test_return": test_result.total_return,
            "degradation": train_result.sharpe_ratio - test_result.sharpe_ratio
        })

    return results
```

### 天龙引擎协同命令

```bash
# 启动回测
[@64-01] 回测VCP-CANSLIM策略，过去3年数据

# Walk-Forward分析
[@64-01] 对该策略进行Walk-Forward分析，评估过拟合风险

# 参数优化
[@64-01] 优化ATR止损倍数参数，找到最优区间

# 完整工作流
[@64-01] market-regime → vcp-screener → backtest-framework → position-sizer-pro
```

### 回测质量检查清单

| 检查项 | 标准 | 阈值 |
|--------|------|------|
| 样本量 | 交易数≥30 | n<30不可信 |
| 夏普比率 | ≥1.0优秀 | <0.5差 |
| 最大回撤 | <20%可接受 | >40%危险 |
| 胜率 | >40%配合盈亏比>1.5 | 单看胜率不够 |
| 盈亏比 | ≥1.5 | <1.0差 |
| Walk-Forward | 训练/测试Sharpe差异<30% | 差异大=过拟合 |
| 序列相关 | 自相关系数<0.2 | >0.5=不独立 |

### 与现有技能协同

| 天龙技能 | 协同方式 | 效果 |
|---------|---------|------|
| **vcp-canslim-screener** | 筛选标准→回测验证 | 策略参数优化 |
| **market-regime-analyzer** | 格局过滤→不同市场表现 | 择时策略验证 |
| **position-sizer-pro** | 仓位参数→回测效果对比 | 最优仓位方案 |

### 局限与注意事项

1. **过拟合风险**：过度优化参数可能导致虚高回测表现
2. **市场变化**：历史表现不代表未来，回测需要结合Walk-Forward
3. **流动性假设**：回测假设100%成交，实际可能有滑点
4. **幸存者偏差**：如果使用当前成分股回测历史，会高估收益

### 参考来源

- Ernest Chan: Quantitative Trading / Algorithmic Trading
- Marcos López de Prado: Advances in Financial Machine Learning (Walk-Forward)
- Robert Carver: Systematic Trading (不回测不等于不可信)
