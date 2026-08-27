---
license: UNKNOWN
triggers: ["trader memory system", "交易员记忆系统 (Trader Memory System)"]
---
# 交易员记忆系统 (Trader Memory System)

## L0: 一句话描述 (≤15字)
交易历史持久化+策略复盘+AI驱动的交易记忆检索。

## L1: 使用场景 (50-100字)
当需要进行交易历史追溯、策略复盘分析或基于历史表现优化交易决策时使用，包含交易日志自动记录、盈亏归因分析、策略表现追踪。适用于天龙引擎64-01量化研究员和64-02算法交易员的策略迭代和风控优化。

## L2: 详细文档

### 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ 交易员记忆系统 — 四层记忆架构                              │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: 交易日志 (Trade Log)                            │
│    → 每笔交易自动记录：时间、价格、数量、理由、结果         │
│    → 必填字段：symbol/entry/exit/quantity/stop/rationale │
│                                                              │
│  Layer 2: 盈亏归因 (P&L Attribution)                      │
│    → 分解为：选股/择时/仓位/执行四维度                     │
│    → 计算各维度对总盈亏的贡献                              │
│                                                              │
│  Layer 3: 策略评分 (Strategy Scoring)                      │
│    → 每笔交易后自动评分：形态/基本面/择时/风控            │
│    → 追踪评分与结果的长期相关性                             │
│                                                              │
│  Layer 4: AI复盘 (AI Post-Mortem)                        │
│    → 亏损交易自动触发深度复盘分析                          │
│    → 识别重复错误模式                                      │
│    → 生成改进建议                                          │
└─────────────────────────────────────────────────────────────┘
```

### 交易记忆数据模型

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json


@dataclass
class TradeRecord:
    """交易记录"""
    trade_id: str
    symbol: str
    market: str                          # A股/港股/美股
    direction: str                       # long/short

    # 入场信息
    entry_date: datetime
    entry_price: float
    quantity: int

    # 出场信息
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None

    # 风控参数
    stop_loss: float
    initial_stop: float
    atr_at_entry: float

    # 交易理由
    rationale: str                        # VCP/CANSLIM/突破等
    signals: list = field(default_factory=list)

    # 评分 (1-10)
    formation_score: int = 0             # 形态评分
    fundamental_score: int = 0            # 基本面评分
    timing_score: int = 0                 # 择时评分
    risk_score: int = 0                  # 风控评分
    overall_score: int = 0               # 综合评分

    # 归因分析
    attribution: dict = field(default_factory=dict)

    # 复盘结论
    post_mortem: Optional[str] = None
    lessons: list = field(default_factory=list)

    @property
    def pnl(self) -> float:
        if self.exit_price is None:
            return 0.0
        return (self.exit_price - self.entry_price) * self.quantity

    @property
    def pnl_pct(self) -> float:
        if self.exit_price is None:
            return 0.0
        return (self.exit_price - self.entry_price) / self.entry_price * 100

    @property
    def holding_days(self) -> int:
        if self.exit_date is None:
            return (datetime.now() - self.entry_date).days
        return (self.exit_date - self.entry_date).days

    @property
    def max_adverse_excursion(self) -> float:
        """最大不利偏移（需要实时数据，计算简化版）"""
        return (self.entry_price - self.stop_loss) / self.entry_price * 100


class TraderMemorySystem:
    """交易员记忆系统"""

    def __init__(self, storage_path: str = "./trader_memory/"):
        self.storage_path = storage_path
        self.trades: list[TradeRecord] = []
        self.strategy_stats: dict = {}
        self.load_trades()

    def log_trade(self, trade: TradeRecord) -> str:
        """记录新交易"""
        self.trades.append(trade)
        self.save_trade(trade)
        return trade.trade_id

    def calculate_attribution(self, trade: TradeRecord) -> dict:
        """
        盈亏归因分析
        将总盈亏分解为各维度贡献
        """
        pnl = trade.pnl

        attribution = {
            "total_pnl": pnl,
            "selection_pnl": 0.0,     # 选股贡献
            "timing_pnl": 0.0,        # 择时贡献
            "position_pnl": 0.0,       # 仓位贡献
            "execution_pnl": 0.0       # 执行贡献
        }

        # 简化归因：基于评分权重分配
        total_score = (
            trade.formation_score +
            trade.fundamental_score +
            trade.timing_score +
            trade.risk_score
        )
        if total_score == 0:
            return attribution

        # 选股贡献 (形态+基本面)
        selection_weight = (trade.formation_score + trade.fundamental_score) / total_score
        attribution["selection_pnl"] = pnl * selection_weight

        # 择时贡献
        timing_weight = trade.timing_score / total_score
        attribution["timing_pnl"] = pnl * timing_weight

        # 风控贡献（亏损时为正贡献，因为风控限制了亏损）
        risk_weight = trade.risk_score / total_score
        if pnl < 0:
            attribution["position_pnl"] = pnl * risk_weight * 0.5
        else:
            attribution["position_pnl"] = pnl * risk_weight

        trade.attribution = attribution
        return attribution

    def generate_post_mortem(self, trade: TradeRecord) -> str:
        """
        AI驱动的交易复盘
        基于交易记录生成深度分析
        """
        if trade.pnl >= 0:
            return self._generate_winning_post_mortem(trade)
        else:
            return self._generate_losing_post_mortem(trade)

    def _generate_losing_post_mortem(self, trade: TradeRecord) -> str:
        """亏损交易复盘"""
        lessons = []

        # 形态评分低 → 检查VCP形态
        if trade.formation_score < 7:
            lessons.append("VCP形态不完整，应等待更明确的形态确认")

        # 基本面评分低 → 检查基本面
        if trade.fundamental_score < 7:
            lessons.append("基本面支撑不足，选股标准需要提高")

        # 择时评分低 → 检查市场环境
        if trade.timing_score < 7:
            lessons.append("市场格局不支持，应减少仓位或观望")

        # 持仓时间过长
        if trade.holding_days > 30:
            lessons.append(f"持仓{trade.holding_days}天过长，应执行时间止损")

        # 回顾相似历史交易
        similar = self.find_similar_trades(trade.symbol, trade.rationale)
        if similar:
            avg_pnl = sum(t.pnl_pct for t in similar) / len(similar)
            lessons.append(f"同类型交易历史平均表现: {avg_pnl:.1f}%")

        trade.lessons = lessons
        trade.post_mortem = "\n".join(f"- {l}" for l in lessons)
        return trade.post_mortem

    def _generate_winning_post_mortem(self, trade: TradeRecord) -> str:
        """盈利交易复盘"""
        lessons = []

        if trade.formation_score >= 8:
            lessons.append("VCP形态完整，继续坚持高形态标准")
        if trade.fundamental_score >= 8:
            lessons.append("基本面支撑强劲，可适当提高此类仓位")
        if trade.timing_score >= 8:
            lessons.append("择时准确，观察当时的市场格局信号")

        # 检查是否卖得太早
        if trade.pnl_pct < 10 and trade.holding_days < 10:
            lessons.append("盈利但幅度小，可能卖得太早，应设置移动止盈")

        trade.lessons = lessons
        trade.post_mortem = "\n".join(f"- {l}" for l in lessons)
        return trade.post_mortem

    def find_similar_trades(self, symbol: str, rationale: str) -> list[TradeRecord]:
        """查找相似历史交易"""
        return [
            t for t in self.trades
            if t.symbol == symbol or t.rationale == rationale
        ]

    def get_strategy_performance(self) -> dict:
        """策略整体表现统计"""
        closed_trades = [t for t in self.trades if t.exit_price is not None]
        if not closed_trades:
            return {}

        wins = [t for t in closed_trades if t.pnl > 0]
        losses = [t for t in closed_trades if t.pnl <= 0]

        return {
            "total_trades": len(closed_trades),
            "win_rate": len(wins) / len(closed_trades) * 100,
            "avg_win_pct": sum(t.pnl_pct for t in wins) / len(wins) if wins else 0,
            "avg_loss_pct": sum(t.pnl_pct for t in losses) / len(losses) if losses else 0,
            "profit_factor": (
                abs(sum(t.pnl for t in wins) / sum(t.pnl for t in losses))
                if losses and sum(t.pnl for t in losses) != 0 else 0
            ),
            "avg_holding_days": sum(t.holding_days for t in closed_trades) / len(closed_trades),
            "best_trade": max(t.pnl_pct for t in closed_trades),
            "worst_trade": min(t.pnl_pct for t in closed_trades),
            "avg_overall_score": sum(t.overall_score for t in closed_trades) / len(closed_trades)
        }

    def save_trade(self, trade: TradeRecord):
        """持久化保存交易记录"""
        filename = f"{self.storage_path}{trade.trade_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(trade.__dict__, f, default=str, ensure_ascii=False, indent=2)

    def load_trades(self):
        """加载所有交易记录"""
        import os
        os.makedirs(self.storage_path, exist_ok=True)
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                with open(os.path.join(self.storage_path, filename), encoding="utf-8") as f:
                    data = json.load(f)
                    self.trades.append(TradeRecord(**data))
```

### 天龙引擎协同命令

```bash
# 记录交易
[@64-02] 记录一笔新交易：买入XYZ，入口价100，数量500，止损98

# 查看策略表现
[@64-02] 生成交易记忆报告，分析最近30笔交易的表现

# 亏损交易复盘
[@64-02] 对亏损超过5%的交易进行深度复盘

# 完整工作流
[@64-02] market-regime → vcp-screener → position-sizer → [log_trade] → trader-memory
```

### 交易记忆报告模板

```markdown
## 交易记忆月报 — {年月}

### 整体表现
- 总交易数: {n}笔
- 胜率: {win_rate}%
- 盈亏比: {profit_factor}
- 平均持仓: {avg_days}天

### 归因分析
- 选股贡献: {selection_pnl}%
- 择时贡献: {timing_pnl}%
- 仓位贡献: {position_pnl}%

### 高频教训 (Top 3)
{lessons}

### 下月改进计划
{improvements}
```

### 与现有技能协同

| 天龙技能 | 协同方式 | 效果 |
|---------|---------|------|
| **vcp-canslim-screener** | 选股理由存入记忆 | 历史验证选股标准 |
| **position-sizer-pro** | 仓位参数存入记忆 | 持续优化仓位公式 |
| **market-regime-analyzer** | 市场格局记录 | 格局判断准确度追踪 |

### 局限与注意事项

1. **数据完整性**：记忆系统的价值取决于记录完整性，需要强制养成记录习惯
2. **归因简化**：简化归因模型可能无法完全反映真实因果关系
3. **过度拟合风险**：基于历史表现优化可能产生过度拟合
4. **心理因素**：记忆系统无法捕捉交易时的心理状态

### 参考来源

- Mark Douglas: 交易心理分析中的交易日志重要性
- Van Tharp: 交易员心理账户概念
- Brett Steenbarger: 交易员改善 (Enhancing Trader Performance)
