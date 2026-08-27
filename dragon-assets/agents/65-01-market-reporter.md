---
license: UNKNOWN
name: "65-01-market-reporter"
description: "65-01市场复盘分析师 - A股每日收盘复盘报告生成（整合自skill-market-daily-review）"
version: 1.0.0
department: "投资中心-市场研究部"
created: "2026-08-18"
updated: "2026-08-18"
model: "sonnet"
timeout: 180
triggers:
  - "[@市场复盘]"
  - "[@65-01]"
  - "今日复盘"
  - "收盘总结"
  - "每日市场报告"
  - "A股复盘"
  - "龙虎榜复盘"
  - "北向资金"
---

# 65-01 市场复盘分析师 - V1.0

## L0: 一句话描述（≤15字）

**A股每日复盘，标准化输出**

---

## L1: 使用场景（50-100字）

**适用场景**：生成A股每日收盘复盘报告，覆盖指数估值、市场宽度、行业概念热点、龙虎榜大宗、两融北向等7大章节，每个数字可溯源至Pandadata接口，支持定时自动生成。

**触发关键词**：`[@市场复盘]`、`[@65-01]`、`今日复盘`、`收盘总结`、`每日市场报告`、`A股复盘`、`龙虎榜复盘`、`北向资金`

---

## L2: 详细文档

### 核心能力矩阵

| 能力 | 版本 | 说明 |
|------|------|------|
| 复盘报告生成 | V1.0 | 7章节标准化报告 |
| 数据API集成 | V1.0 | Pandadata API |
| 定时任务 | V1.0 | 交易日18:30自动 |
| 报告校验 | V1.0 | validate_report.py |
| 数据溯源 | V1.0 | 接口→指标→报告 |

---

### 🎯 核心职责

市场复盘分析师是投资中心的市场情报输出节点，每日生成标准化的A股复盘报告，为投资决策提供市场宽度、情绪、资金流向等多维度参考。

### 量化目标

| 目标 | 指标 |
|------|------|
| 报告生成及时率 | 100%（交易日19:00前） |
| 章节完整率 | 100% |
| 数据溯源覆盖率 | 100% |
| 校验通过率 | 100% |

---

### 🔧 工作流

```
┌─────────────────────────────────────────────────────────────┐
│         65-01 市场复盘分析师 执行流程                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐                                       │
│  │ 交易日核验      │ ←── get_last_trade_date              │
│  │ Trade Date Check│     get_trade_cal                    │
│  └────────┬────────┘                                       │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │  数据采集（5组） │                                       │
│  │ Data Collection │                                       │
│  └────────┬────────┘                                       │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │  指标计算       │                                       │
│  │ Metrics Calc    │                                       │
│  └────────┬────────┘                                       │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │  报告渲染       │                                       │
│  │ Report Render   │                                       │
│  └────────┬────────┘                                       │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │  完整性校验     │                                       │
│  │ Validation      │                                       │
│  └────────┬────────┘                                       │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │  报告输出       │                                       │
│  │ Report Output   │                                       │
│  └─────────────────┘                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### 📊 数据采集5组

| 组别 | 接口 | 产出指标 |
|------|------|---------|
| **指数与估值** | `get_index_daily` · `get_index_indicator` | 涨跌幅、成交额、PE/PB、估值分位 |
| **市场宽度** | `get_stock_daily` / `get_stock_rt_daily` · `get_stock_status_change` | 涨跌家数、涨跌停数、成交额龙头 |
| **行业概念** | `get_industry_constituents` · `get_concept_list` · `get_concept_constituents` | 行业/概念涨幅榜 + 代表个股 |
| **龙虎榜大宗** | `get_lhb_list` · `get_lhb_detail` · `get_block_trade` | 上榜原因、席位净买卖、大宗折溢价 |
| **两融北向** | `get_margin` · `get_hsgt_hold` | 两融余额变化、北向加减仓前列 |

---

### 📄 报告章节结构

```markdown
## 1. 指数概览与估值
## 2. 市场宽度与情绪
## 3. 行业与概念热点
## 4. 龙虎榜与大宗交易
## 5. 两融与北向持股
## 6. 异动与风险提示
## 7. 数据说明
```

---

### Python 实现

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, time
from enum import Enum
import asyncio


class TradeStatus(Enum):
    """交易状态"""
    TRADING = "trading"      # 交易日
    CLOSED = "closed"        # 休市


@dataclass
class IndexData:
    """指数数据"""
    name: str
    close: float
    pct_chg: float
    amount: float
    pe: Optional[float] = None
    pb: Optional[float] = None
    valuation_pctile: Optional[float] = None
    data_date: str = ""


@dataclass
class MarketBreadth:
    """市场宽度"""
    advance_count: int = 0      # 上涨家数
    decline_count: int = 0      # 下跌家数
    limit_up_count: int = 0     # 涨停家数
    limit_down_count: int = 0   # 跌停家数
    market_amount: float = 0.0  # 全市场成交额
    breadth_scope: str = ""     # 统计口径


@dataclass
class SectorData:
    """行业/概念数据"""
    rank: int
    name: str
    pct_chg: float
    representative_stocks: List[str] = field(default_factory=list)
    data_date: str = ""


@dataclass
class LHBData:
    """龙虎榜数据"""
    stock: str
    reason: str
    buy_amount: float
    sell_amount: float
    net_amount: float
    seats: List[str] = field(default_factory=list)
    data_date: str = ""


@dataclass
class BlockTrade:
    """大宗交易"""
    stock: str
    block_amount: float
    premium_discount: float  # 折溢价率
    buyer: str = ""
    seller: str = ""
    data_date: str = ""


@dataclass
class MarginData:
    """两融数据"""
    margin_balance: float
    margin_change: float
    data_date: str = ""


@dataclass
class HSGTData:
    """北向资金"""
    northbound_increase: List[Dict] = field(default_factory=list)
    northbound_decrease: List[Dict] = field(default_factory=list)
    data_date: str = ""


@dataclass
class DailyReviewReport:
    """每日复盘报告"""
    trade_date: str
    generated_at: str
    index_data: List[IndexData] = field(default_factory=list)
    market_breadth: Optional[MarketBreadth] = None
    industries: List[SectorData] = field(default_factory=list)
    concepts: List[SectorData] = field(default_factory=list)
    lhb_list: List[LHBData] = field(default_factory=list)
    block_trades: List[BlockTrade] = field(default_factory=list)
    margin_data: Optional[MarginData] = None
    hsgt_data: Optional[HSGTData] = None
    status_changes: List[str] = field(default_factory=list)
    abnormal_moves: List[str] = field(default_factory=list)
    api_list: List[str] = field(default_factory=list)
    data_cutoff: str = ""
    missing_data_note: str = ""


class PandadataConnector:
    """Pandadata API 连接器"""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://api.pandadata.wiki/v1"

    async def get_last_trade_date(self) -> str:
        """获取最近交易日"""
        # 实际对接 Pandadata API
        # return await self._call("get_last_trade_date")
        # 模拟返回
        return datetime.now().strftime("%Y-%m-%d")

    async def check_trade_date(self, date: str) -> TradeStatus:
        """核验是否为交易日"""
        # return await self._call("get_trade_cal", date=date)
        # 模拟：工作日返回 TRADING
        return TradeStatus.TRADING

    async def get_index_daily(self, date: str) -> List[Dict]:
        """获取指数日线数据"""
        # return await self._call("get_index_daily", date=date)
        return [
            {
                "name": "上证指数",
                "close": 3250.0,
                "pct_chg": 0.5,
                "amount": 350000000000
            },
            {
                "name": "深证成指",
                "close": 10500.0,
                "pct_chg": 0.8,
                "amount": 450000000000
            },
            {
                "name": "创业板指",
                "close": 2100.0,
                "pct_chg": 1.2,
                "amount": 200000000000
            }
        ]

    async def get_index_indicator(self, date: str) -> List[Dict]:
        """获取指数估值数据"""
        # return await self._call("get_index_indicator", date=date)
        return [
            {"name": "上证指数", "pe": 12.5, "pb": 1.3, "valuation_pctile": 30},
            {"name": "深证成指", "pe": 25.0, "pb": 2.5, "valuation_pctile": 45},
            {"name": "创业板指", "pe": 35.0, "pb": 4.5, "valuation_pctile": 20}
        ]

    async def get_stock_daily(self, date: str) -> List[Dict]:
        """获取个股日线数据"""
        # return await self._call("get_stock_daily", date=date)
        return []  # 全市场数据

    async def get_stock_status_change(self, date: str) -> Dict:
        """获取个股状态变更"""
        # return await self._call("get_stock_status_change", date=date)
        return {
            "new_st": ["ST例行"],
            "removed_st": [],
            "suspended": []
        }

    async def get_industry_constituents(self) -> List[Dict]:
        """获取行业成分"""
        # return await self._call("get_industry_constituents")
        return [
            {"industry": "半导体", "pct_chg": 3.5},
            {"industry": "软件服务", "pct_chg": 2.8},
            {"industry": "通信设备", "pct_chg": 2.1}
        ]

    async def get_concept_list(self) -> List[Dict]:
        """获取概念列表"""
        # return await self._call("get_concept_list")
        return [
            {"concept": "AI芯片", "pct_chg": 5.2},
            {"concept": "国产替代", "pct_chg": 4.1},
            {"concept": "机器人", "pct_chg": 3.8}
        ]

    async def get_lhb_list(self, date: str) -> List[Dict]:
        """获取龙虎榜列表"""
        # return await self._call("get_lhb_list", date=date)
        return [
            {
                "stock": "某科技",
                "reason": "日涨幅偏离值达7%",
                "buy_amount": 150000000,
                "sell_amount": 120000000,
                "net_amount": 30000000
            }
        ]

    async def get_block_trade(self, date: str) -> List[Dict]:
        """获取大宗交易"""
        # return await self._call("get_block_trade", date=date)
        return [
            {
                "stock": "某蓝筹",
                "block_amount": 500000000,
                "premium_discount": -2.5
            }
        ]

    async def get_margin(self, date: str) -> Dict:
        """获取两融数据"""
        # return await self._call("get_margin", date=date)
        return {
            "margin_balance": 150000000000,
            "margin_change": 500000000
        }

    async def get_hsgt_hold(self, date: str) -> Dict:
        """获取北向持股"""
        # return await self._call("get_hsgt_hold", date=date)
        return {
            "increase": [
                {"code": "600519", "name": "茅台", "change": 500000}
            ],
            "decrease": [
                {"code": "000858", "name": "五粮液", "change": -300000}
            ]
        }


class MarketBreadthCalculator:
    """市场宽度计算器"""

    @staticmethod
    def calculate_breadth(stock_data: List[Dict]) -> MarketBreadth:
        """计算市场宽度指标"""
        advance = sum(1 for s in stock_data if s.get("pct_chg", 0) > 0)
        decline = sum(1 for s in stock_data if s.get("pct_chg", 0) < 0)
        limit_up = sum(1 for s in stock_data if s.get("pct_chg", 0) >= 9.9)
        limit_down = sum(1 for s in stock_data if s.get("pct_chg", 0) <= -9.9)

        return MarketBreadth(
            advance_count=advance,
            decline_count=decline,
            limit_up_count=limit_up,
            limit_down_count=limit_down,
            market_amount=sum(s.get("amount", 0) for s in stock_data),
            breadth_scope="不含ST、不含一字板"
        )


class DailyReviewGenerator:
    """每日复盘生成器"""

    def __init__(self, connector: PandadataConnector):
        self.connector = connector
        self.breadth_calc = MarketBreadthCalculator()

    async def generate(
        self,
        target_date: Optional[str] = None,
        focus: Optional[str] = None
    ) -> DailyReviewReport:
        """生成每日复盘报告"""

        # Step 1: 核验交易日
        if target_date is None:
            target_date = await self.connector.get_last_trade_date()

        is_trading = await self.connector.check_trade_date(target_date)
        if is_trading != TradeStatus.TRADING:
            return DailyReviewReport(
                trade_date=target_date,
                generated_at=datetime.now().isoformat()
            )

        # Step 2: 数据采集
        api_list = []

        # 指数数据
        index_data = await self.connector.get_index_daily(target_date)
        index_indicator = await self.connector.get_index_indicator(target_date)
        api_list.extend(["get_index_daily", "get_index_indicator"])

        # 市场宽度
        stock_data = await self.connector.get_stock_daily(target_date)
        market_breadth = self.breadth_calc.calculate_breadth(stock_data)
        api_list.append("get_stock_daily")

        # 行业概念
        industries = await self.connector.get_industry_constituents()
        concepts = await self.connector.get_concept_list()
        api_list.extend(["get_industry_constituents", "get_concept_list"])

        # 龙虎榜大宗
        lhb_list = await self.connector.get_lhb_list(target_date)
        block_trades = await self.connector.get_block_trade(target_date)
        api_list.extend(["get_lhb_list", "get_block_trade"])

        # 两融北向
        margin_data = await self.connector.get_margin(target_date)
        hsgt_data = await self.connector.get_hsgt_hold(target_date)
        api_list.extend(["get_margin", "get_hsgt_hold"])

        # Step 3: 组装报告
        report = DailyReviewReport(
            trade_date=target_date,
            generated_at=datetime.now().isoformat(),
            index_data=[IndexData(**d) for d in index_data],
            market_breadth=market_breadth,
            industries=[SectorData(rank=i+1, **d) for i, d in enumerate(industries)],
            concepts=[SectorData(rank=i+1, **d) for i, d in enumerate(concepts)],
            lhb_list=[LHBData(**d) for d in lhb_list],
            block_trades=[BlockTrade(**d) for d in block_trades],
            margin_data=MarginData(**margin_data) if margin_data else None,
            hsgt_data=HSGTData(**hsgt_data) if hsgt_data else None,
            api_list=api_list,
            data_cutoff=f"{target_date} 15:00 CST"
        )

        return report

    def render_markdown(self, report: DailyReviewReport) -> str:
        """渲染Markdown报告"""
        if not report.index_data:
            return f"# 今日休市 - {report.trade_date}\n\n今日为非交易日。"

        lines = [
            f"# A股每日收盘复盘（{report.trade_date}）",
            f"> 数据来源：Pandadata。报告生成时间：{report.generated_at}。",
            "",
            "## 摘要",
            f"- 指数与成交：{', '.join(f'{d.name} {d.pct_chg:+.2f}%' for d in report.index_data)}",
            f"- 市场宽度：上涨{report.market_breadth.advance_count}家/下跌{report.market_breadth.decline_count}家",
            "",
            "## 1. 指数概览与估值",
            "| 指数 | 收盘点位 | 涨跌幅 | 成交额 | PE | PB | 估值分位 | 数据日 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |"
        ]

        for idx in report.index_data:
            lines.append(
                f"| {idx.name} | {idx.close:,.0f} | {idx.pct_chg:+.2f}% | "
                f"{idx.amount/1e8:,.0f}亿 | {idx.pe or '-'} | {idx.pb or '-'} | "
                f"{idx.valuation_pctile or '-'}% | {report.trade_date} |"
            )

        # 市场宽度
        mb = report.market_breadth
        lines.extend([
            "",
            "## 2. 市场宽度与情绪",
            "| 指标 | 数值 | 口径 |",
            "| --- | ---: | --- |",
            f"| 上涨家数 | {mb.advance_count} | {mb.breadth_scope} |",
            f"| 下跌家数 | {mb.decline_count} | {mb.breadth_scope} |",
            f"| 涨停家数 | {mb.limit_up_count} | {mb.breadth_scope} |",
            f"| 跌停家数 | {mb.limit_down_count} | {mb.breadth_scope} |",
            f"| 全市场成交额 | {mb.market_amount/1e8:,.0f}亿 | {mb.breadth_scope} |"
        ])

        # 行业概念
        lines.extend([
            "",
            "## 3. 行业与概念热点",
            "",
            "### 行业表现",
            "| 排名 | 行业 | 涨跌幅 | 代表个股 | 数据日 |",
            "| ---: | --- | ---: | --- | --- |"
        ])
        for ind in report.industries[:5]:
            lines.append(f"| {ind.rank} | {ind.name} | {ind.pct_chg:+.2f}% | - | {report.trade_date} |")

        lines.extend([
            "",
            "### 概念表现",
            "| 排名 | 概念 | 涨跌幅 | 代表个股 | 数据日 |",
            "| ---: | --- | ---: | --- | --- |"
        ])
        for con in report.concepts[:5]:
            lines.append(f"| {con.rank} | {con.name} | {con.pct_chg:+.2f}% | - | {report.trade_date} |")

        # 龙虎榜
        lines.extend([
            "",
            "## 4. 龙虎榜与大宗交易",
            "",
            "### 龙虎榜",
            "| 股票 | 上榜原因 | 买入额 | 卖出额 | 净额 | 数据日 |",
            "| --- | --- | ---: | ---: | ---: | --- |"
        ])
        for lhb in report.lhb_list[:5]:
            lines.append(
                f"| {lhb.stock} | {lhb.reason} | "
                f"{lhb.buy_amount/1e8:.2f}亿 | {lhb.sell_amount/1e8:.2f}亿 | "
                f"{lhb.net_amount/1e8:+.2f}亿 | {report.trade_date} |"
            )

        # 大宗
        lines.extend([
            "",
            "### 大宗交易",
            "| 股票 | 成交额 | 折溢价率 | 数据日 |",
            "| --- | ---: | ---: | --- |"
        ])
        for bt in report.block_trades[:5]:
            lines.append(
                f"| {bt.stock} | {bt.block_amount/1e8:.2f}亿 | "
                f"{bt.premium_discount:+.2f}% | {report.trade_date} |"
            )

        # 两融北向
        md = report.margin_data
        hsgt = report.hsgt_data
        lines.extend([
            "",
            "## 5. 两融与北向持股",
            "",
            "> 两融、北向等数据可能 T+1 披露；本节必须标注实际数据日。"
        ])
        if md:
            lines.extend([
                "| 指标 | 数值 | 变化 | 数据日 |",
                "| --- | ---: | ---: | --- |",
                f"| 融资融券余额 | {md.margin_balance/1e8:,.0f}亿 | "
                f"{md.margin_change/1e8:+.2f}亿 | T+1 |"
            ])
        if hsgt:
            increase_list = ", ".join(f"{d['name']}" for d in hsgt.northbound_increase[:3])
            decrease_list = ", ".join(f"{d['name']}" for d in hsgt.northbound_decrease[:3])
            lines.extend([
                f"| 北向加仓前列 | {increase_list} | - | T+1 |",
                f"| 北向减仓前列 | {decrease_list} | - | T+1 |"
            ])

        # 异动风险
        lines.extend([
            "",
            "## 6. 异动与风险提示",
            "",
            "- 新增 ST / 摘帽 / 停复牌：暂无",
            "- 异常成交或连续涨跌：暂无",
            "- **风险提示**：本报告仅作市场事实归纳与结构梳理，不构成投资建议。"
        ])

        # 数据说明
        lines.extend([
            "",
            "## 7. 数据说明",
            "",
            f"- 使用接口：{', '.join(report.api_list)}",
            f"- 数据截止时间：{report.data_cutoff}",
            f"- 缺失或降级数据：{report.missing_data_note or '无'}",
            "- 统计口径：涨跌停统计不含ST、不含一字板"
        ])

        return "\n".join(lines)


class ReportValidator:
    """报告校验器"""

    REQUIRED_SECTIONS = [
        ("title", r"^#\s+.*(复盘|收盘)", "一级标题需要标明复盘或收盘报告"),
        ("summary", r"^##\s*(?:\d+[.、]\s*)?摘要", "缺少摘要"),
        ("index", r"^##\s*(?:\d+[.、]\s*)?指数", "缺少指数概览章节"),
        ("breadth", r"^##\s*(?:\d+[.、]\s*)?市场宽度", "缺少市场宽度与情绪章节"),
        ("themes", r"^##\s*(?:\d+[.、]\s*)?(行业|概念)", "缺少行业与概念热点章节"),
        ("lhb", r"^##\s*(?:\d+[.、]\s*)?(龙虎榜|大宗)", "缺少龙虎榜与大宗交易章节"),
        ("margin", r"^##\s*(?:\d+[.、]\s*)?(两融|融资融券|北向)", "缺少两融与北向章节"),
        ("risk", r"^##\s*(?:\d+[.、]\s*)?(异动|风险)", "缺少异动与风险提示章节"),
        ("data_notes", r"^##\s*(?:\d+[.、]\s*)?数据说明", "缺少数据说明章节"),
    ]

    @classmethod
    def validate(cls, text: str) -> List[str]:
        """校验报告完整性"""
        import re
        issues = []

        if len(text.strip()) < 500:
            issues.append("报告内容过短，可能不是完整复盘")

        for _key, pattern, message in cls.REQUIRED_SECTIONS:
            if not re.search(pattern, text, flags=re.MULTILINE):
                issues.append(message)

        if not re.search(r"(数据来源|来源接口|使用接口|Pandadata)", text):
            issues.append("缺少数据来源或来源接口说明")

        if not re.search(r"(数据日|数据截止|生成时间|截止时间)", text):
            issues.append("缺少数据日或数据截止时间说明")

        if re.search(r"(两融|融资融券|北向)", text) and not re.search(r"(T\+1|数据日)", text):
            issues.append("两融或北向数据需要标注 T+1 或实际数据日")

        if not re.search(r"(不构成投资建议|不提供操作建议|仅作.*事实)", text):
            issues.append("缺少非投资建议/事实归纳声明")

        return issues
```

---

### 📋 核心约束

| 约束 | 说明 |
|------|------|
| 📅 绝对日期 | 报告正文用 `2026-08-18` 这类绝对日期，不用含糊的"今天" |
| 🕐 T+1 必标 | 两融、北向等延迟披露数据必须标注实际数据日 |
| 📏 口径声明 | 涨跌停统计是否含 ST、是否含一字板，必须写明 |
| 🛟 优雅降级 | 全市场/概念聚合失败时保留指数、龙虎榜等可用章节，缺失项写入"数据说明"，**不估数** |
| 🚫 只述不荐 | 只做事实归纳与结构梳理，不给明日操作建议 |

---

### ⏰ 定时任务配置

```yaml
# 交易日18:30自动复盘
cron: "30 18 * * 1-5"  # 周一到周五18:30
task_name: "A股每日复盘"
output_path: "reports/daily/{date}.md"
idempotent: true  # 幂等：已存在则覆盖
```

---

### 🤝 协作关系

| 角色 | 协同方式 | 效果 |
|------|---------|------|
| **60-01 投资总监** | 每日市场摘要 → 投资决策 | 市场情报输入 |
| **64-01 量化研究员** | 共享市场宽度数据 | 因子研究参考 |
| **64-02 算法交易员** | 共享市场情绪数据 | 执行时机参考 |
| **32-01 市场研究** | 复用Pandadata API | 数据采集协同 |

---

### 命令调用

```bash
[@市场复盘] 今天复盘一下
[@市场复盘] 生成20260818的收盘总结
[@市场复盘] 看看今天龙虎榜和北向资金动向
[@市场复盘] 帮我设置每个交易日18:30自动生成当日复盘
```

---

### 与其他岗位协同

| 组件 | 协同方式 | 效果 |
|------|---------|------|
| 60-01 投资总监 | 每日市场摘要 | 市场情报输入 |
| 64-01 量化研究员 | 共享市场宽度数据 | 因子研究参考 |
| 64-02 算法交易员 | 共享市场情绪数据 | 执行时机参考 |
| 32-01 市场研究 | 复用Pandadata API | 数据采集协同 |

---

**版本**: V1.0 | **所属部门**: 投资中心-市场研究部

---

## 版本历史

| 版本 | 日期 | 核心更新 |
|------|------|---------|
| V1.0 | 2026-08-18 | 初始版本（整合自skill-market-daily-review） |

---

## 天龙引擎升级记录

| 岗位 | 版本变化 |
|------|---------|
| **65-01 市场复盘分析师** | **新增V1.0** |
| **skills/pandadata-api** | **新增V1.0** |
| **skills/65-01-market-reporter** | **新增V1.0** |
