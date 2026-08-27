"""阶段 47.2 · Sheet + a-stock-data-bridge 跨 Unit 公式联动

本脚本：
  1. 调用 a-stock-data-bridge 的 FetchResult 接口语义（无需真实拉取，使用模拟数据，
     与 em_get.FetchResult 同构）
  2. 把 5 类端点结果写入 5 个 sheet
  3. 关键：跨 sheet 公式联动（用户改 D2 资产负债率 → 第 4 sheet 财务健康分自动重算）
  4. 输出 .xlsx 含 5 sheet + 10+ 公式 + 1 图表

Author: dragon-engine · Stage 47.2 · 2026-08-26
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill

# ─── 模拟 FetchResult（与 a-stock-data-bridge em_get.FetchResult 同构） ─────

TZ_CN = timezone(timedelta(hours=8))


@dataclass
class FetchResult:
    """与 em_get.FetchResult 同构 · a-stock-data-bridge 接口语义"""
    source: str
    endpoint: str
    data: Any
    fetched_at: str = field(default_factory=lambda: datetime.now(TZ_CN).isoformat())
    fallback_used: bool = False
    rows: int = 0

    def to_dict(self):
        return {
            "source": self.source,
            "endpoint": self.endpoint,
            "fetched_at": self.fetched_at,
            "fallback_used": self.fallback_used,
            "rows": self.rows,
        }


def mock_pe_pb(symbol: str = "600519.SH") -> FetchResult:
    """L1 端点：pe_pb_market_cap · 估值数据"""
    data = {
        "symbol": symbol,
        "name": "贵州茅台",
        "pe_ttm": 27.5,
        "pe_static": 28.3,
        "pb": 8.9,
        "market_cap": 1.65e12,
        "circulating_cap": 1.65e12,
        "total_shares": 1.256e9,
        "industry_pe": 32.1,
    }
    return FetchResult(source="eastmoney", endpoint="pe_pb_market_cap", data=data, rows=8)


def mock_financial_3statements(symbol: str = "600519.SH", year: int = 2025) -> FetchResult:
    """L6 端点：financial_3statements · 财报三表"""
    data = {
        "balance_sheet": {
            "total_assets": 2.85e11,
            "total_liabilities": 4.18e10,
            "shareholder_equity": 2.43e11,
            "current_assets": 2.10e11,
            "current_liabilities": 3.85e10,
            "cash_and_equivalents": 1.45e10,
            "inventory": 4.20e10,
            "accounts_receivable": 1.20e9,
        },
        "income_statement": {
            "revenue": 1.74e11,
            "operating_cost": 4.30e10,
            "gross_profit": 1.31e11,
            "operating_expense": 1.80e10,
            "operating_profit": 1.13e11,
            "net_profit": 6.48e10,
            "eps": 51.6,
        },
        "cash_flow_statement": {
            "operating_cash_flow": 6.85e10,
            "investing_cash_flow": -1.20e10,
            "financing_cash_flow": -3.95e10,
            "free_cash_flow": 5.65e10,
        },
    }
    return FetchResult(source="mootdx", endpoint="financial_3statements", data=data, rows=20)


def mock_quarterly(symbol: str = "600519.SH", year: int = 2025, quarter: int = 2) -> FetchResult:
    """L6 端点：quarterly_report_37fields · 季报 37 字段"""
    return FetchResult(
        source="mootdx",
        endpoint="quarterly_report_37fields",
        data={
            "revenue_yoy": 0.182,
            "net_profit_yoy": 0.247,
            "gross_margin": 0.753,
            "roe": 0.265,
            "roa": 0.227,
            "asset_liability_ratio": 0.147,
            "current_ratio": 5.45,
            "quick_ratio": 4.36,
            "inventory_turnover_days": 1240,
            "receivable_turnover_days": 5,
            "eps_basic": 12.90,
            "bvps": 193.50,
            "operating_cash_flow_per_share": 5.45,
        },
        rows=13,
    )


def mock_north_bound(symbol: str = "600519.SH") -> FetchResult:
    """L3 端点：north_top10 · 北向 TOP10"""
    return FetchResult(
        source="eastmoney",
        endpoint="north_top10",
        data={
            "net_buy_amount_5d": 1.20e9,
            "net_buy_amount_20d": 3.45e9,
            "holdings_shares": 9.85e7,
            "holdings_ratio": 0.0784,
            "rank_in_north": 5,
        },
        rows=5,
    )


def mock_consensus(symbol: str = "600519.SH") -> FetchResult:
    """L2 端点：consensus_eps · 一致预期"""
    return FetchResult(
        source="iwencai",
        endpoint="consensus_eps",
        data={
            "consensus_eps_2025E": 68.5,
            "consensus_revenue_2025E": 1.95e11,
            "buy_count": 28,
            "hold_count": 8,
            "sell_count": 1,
            "target_price_high": 2200,
            "target_price_low": 1500,
            "target_price_median": 1850,
        },
        rows=8,
    )


# ─── 主函数：拉取 → 写入多 sheet + 跨 sheet 公式联动 .xlsx ─────────────────

def build_finance_workbook(symbol: str, output_path: Path) -> dict:
    """把 5 个端点结果写入 5 个 sheet，并加入跨 sheet 公式联动

    Sheet 1: 估值快照（pe_pb + 一致预期）
    Sheet 2: 财报三表（balance + income + cash flow）
    Sheet 3: 季报关键指标（37 字段关键 + 同比公式）
    Sheet 4: 资金流与持仓（北向 + 财务健康度评分 ← 跨 sheet 公式）
    Sheet 5: 投资分析（综合评级 + 风险提示 ← 引用其他 4 sheet）
    """
    # 1. 拉取 5 类数据（实际部署时替换为 em_get.em_get() 真实调用）
    r_pe = mock_pe_pb(symbol)
    r_fin = mock_financial_3statements(symbol)
    r_q = mock_quarterly(symbol)
    r_nb = mock_north_bound(symbol)
    r_cons = mock_consensus(symbol)

    results = [r_pe, r_fin, r_q, r_nb, r_cons]

    wb = Workbook()
    # 删默认 sheet
    wb.remove(wb.active)

    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="2E5C8A", end_color="2E5C8A", fill_type="solid")
    label_font = Font(bold=True, size=10)

    # ─────── Sheet 1：估值快照 ───────
    ws1 = wb.create_sheet("1_估值快照")
    ws1.append(["指标", "数值", "来源", "备注"])
    for cell in ws1[1]:
        cell.font = header_font
        cell.fill = header_fill

    pe = r_pe.data
    cons = r_cons.data
    ws1.append(["股票代码", pe["symbol"], r_pe.source, ""])
    ws1.append(["股票名称", pe["name"], r_pe.source, ""])
    ws1.append(["PE(TTM)", pe["pe_ttm"], r_pe.source, "市盈率(滚动 12 月)"])
    ws1.append(["PE(静态)", pe["pe_static"], r_pe.source, "市盈率(去年)"])
    ws1.append(["PB", pe["pb"], r_pe.source, "市净率"])
    ws1.append(["市值(亿元)", pe["market_cap"] / 1e8, r_pe.source, ""])
    ws1.append(["行业 PE", pe["industry_pe"], r_pe.source, "对照基准"])
    ws1.append(["相对估值(PE_TTM/行业_PE)", f"=B4/B8", "公式", "本表内公式"])  # 行 8
    ws1.append(["一致预期 EPS 2025E", cons["consensus_eps_2025E"], r_cons.source, ""])
    ws1.append(["买入/持有/卖出", f"{cons['buy_count']}/{cons['hold_count']}/{cons['sell_count']}",
                r_cons.source, f"{cons['buy_count'] + cons['hold_count'] + cons['sell_count']} 家覆盖"])
    ws1.append(["目标价中位数", cons["target_price_median"], r_cons.source, ""])

    # ─────── Sheet 2：财报三表 ───────
    ws2 = wb.create_sheet("2_财报三表")
    ws2.append(["科目", "金额(元)", "占比", "来源"])
    for cell in ws2[1]:
        cell.font = header_font
        cell.fill = header_fill

    fin = r_fin.data
    bs = fin["balance_sheet"]
    inc = fin["income_statement"]
    cf = fin["cash_flow_statement"]

    bs_rows = [
        ("总资产", bs["total_assets"]),
        ("总负债", bs["total_liabilities"]),
        ("股东权益", bs["shareholder_equity"]),
        ("流动资产", bs["current_assets"]),
        ("流动负债", bs["current_liabilities"]),
        ("现金及等价物", bs["cash_and_equivalents"]),
        ("存货", bs["inventory"]),
        ("应收账款", bs["accounts_receivable"]),
    ]
    inc_rows = [
        ("营业收入", inc["revenue"]),
        ("营业成本", inc["operating_cost"]),
        ("毛利", inc["gross_profit"]),
        ("营业费用", inc["operating_expense"]),
        ("营业利润", inc["operating_profit"]),
        ("净利润", inc["net_profit"]),
    ]
    cf_rows = [
        ("经营性现金流", cf["operating_cash_flow"]),
        ("投资性现金流", cf["investing_cash_flow"]),
        ("筹资性现金流", cf["financing_cash_flow"]),
        ("自由现金流", cf["free_cash_flow"]),
    ]

    start_row = 2
    for i, (name, val) in enumerate(bs_rows + inc_rows + cf_rows):
        ws2.cell(row=start_row + i, column=1, value=name).font = label_font
        ws2.cell(row=start_row + i, column=2, value=val)
        ws2.cell(row=start_row + i, column=3, value=f"=B{start_row + i}/$B$2")  # 占总资产
        ws2.cell(row=start_row + i, column=3).number_format = "0.0%"
        ws2.cell(row=start_row + i, column=4, value=r_fin.source)

    # 关键比率（公式）
    ratio_row = start_row + len(bs_rows) + len(inc_rows) + len(cf_rows) + 1
    ws2.cell(row=ratio_row, column=1, value="=== 关键比率（自动算）===").font = Font(bold=True, color="C0392B")
    ws2.cell(row=ratio_row + 1, column=1, value="资产负债率").font = label_font
    ws2.cell(row=ratio_row + 1, column=2, value="=B3/B2")  # 总负债 / 总资产
    ws2.cell(row=ratio_row + 1, column=2).number_format = "0.00%"
    ws2.cell(row=ratio_row + 2, column=1, value="流动比率").font = label_font
    ws2.cell(row=ratio_row + 2, column=2, value="=B5/B6")  # 流动资产 / 流动负债
    ws2.cell(row=ratio_row + 2, column=2).number_format = "0.00"
    ws2.cell(row=ratio_row + 3, column=1, value="毛利率").font = label_font
    # 毛利在 row 12（=start_row + 8 + 2 = 12），营收在 row 10
    ws2.cell(row=ratio_row + 3, column=2, value="=B12/B10")
    ws2.cell(row=ratio_row + 3, column=2).number_format = "0.00%"
    ws2.cell(row=ratio_row + 4, column=1, value="净利率").font = label_font
    # 净利在 row 15
    ws2.cell(row=ratio_row + 4, column=2, value="=B15/B10")
    ws2.cell(row=ratio_row + 4, column=2).number_format = "0.00%"

    # ─────── Sheet 3：季报关键指标 + 同比公式 ───────
    ws3 = wb.create_sheet("3_季报关键指标")
    ws3.append(["指标", "数值", "同比", "来源"])
    for cell in ws3[1]:
        cell.font = header_font
        cell.fill = header_fill

    q = r_q.data
    q_rows = [
        ("营收同比", q["revenue_yoy"]),
        ("净利同比", q["net_profit_yoy"]),
        ("毛利率", q["gross_margin"]),
        ("ROE", q["roe"]),
        ("ROA", q["roa"]),
        ("资产负债率", q["asset_liability_ratio"]),
        ("流动比率", q["current_ratio"]),
        ("速动比率", q["quick_ratio"]),
        ("存货周转天数", q["inventory_turnover_days"]),
        ("应收周转天数", q["receivable_turnover_days"]),
        ("基本 EPS", q["eps_basic"]),
        ("每股净资产", q["bvps"]),
        ("每股经营性现金流", q["operating_cash_flow_per_share"]),
    ]
    for i, (name, val) in enumerate(q_rows):
        ws3.cell(row=i + 2, column=1, value=name).font = label_font
        ws3.cell(row=i + 2, column=2, value=val)
        if "%" in name or "率" in name or "ROE" in name or "ROA" in name:
            ws3.cell(row=i + 2, column=2).number_format = "0.00%"
        ws3.cell(row=i + 2, column=4, value=r_q.source)

    # 同比公式（与上季度对比，假设上季度在 G 列）
    ws3.cell(row=1, column=6, value="上季度对照（模拟）").font = Font(italic=True, color="888888")
    last_quarter = [0.150, 0.190, 0.740, 0.250, 0.215, 0.152, 5.20, 4.10, 1320, 6, 11.50, 185.0, 4.80]
    for i, v in enumerate(last_quarter):
        ws3.cell(row=i + 2, column=7, value=v)
        ws3.cell(row=i + 2, column=7).font = Font(color="BBBBBB")

    # 同比涨幅公式（B 列 - G 列）/ G 列
    for i in range(len(q_rows)):
        row = i + 2
        if q_rows[i][0] in ["营收同比", "净利同比", "毛利率", "ROE", "ROA", "资产负债率"]:
            ws3.cell(row=row, column=3, value=f"=B{row}-G{row}")
            ws3.cell(row=row, column=3).number_format = "0.0%"
        else:
            ws3.cell(row=row, column=3, value=f"=(B{row}-G{row})/G{row}")
            ws3.cell(row=row, column=3).number_format = "0.0%"

    # ─────── Sheet 4：资金流与持仓 + 跨 sheet 公式（财务健康度评分） ───────
    ws4 = wb.create_sheet("4_资金流与持仓")
    ws4.append(["指标", "数值", "来源"])
    for cell in ws4[1]:
        cell.font = header_font
        cell.fill = header_fill

    nb = r_nb.data
    ws4.append(["北向净买入(5 日, 亿元)", nb["net_buy_amount_5d"] / 1e8, r_nb.source])
    ws4.append(["北向净买入(20 日, 亿元)", nb["net_buy_amount_20d"] / 1e8, r_nb.source])
    ws4.append(["北向持股(万股)", nb["holdings_shares"] / 1e4, r_nb.source])
    ws4.append(["北向持股比例", nb["holdings_ratio"], r_nb.source])
    ws4.cell(row=5, column=2).number_format = "0.00%"

    # 跨 sheet 公式：从 sheet 2 拿 ROE / 资产负债率 / 毛利率；从 sheet 3 拿 ROE/资产负债率
    # 财务健康度评分 = 0.4*ROE + 0.3*(1-资产负债率) + 0.2*毛利率 + 0.1*流动比率
    ws4.cell(row=7, column=1, value="=== 财务健康度评分（跨 sheet）===").font = Font(bold=True, color="C0392B")
    ws4.cell(row=8, column=1, value="ROE 贡献（40%）").font = label_font
    ws4.cell(row=8, column=2, value="='3_季报关键指标'!B5*0.4")  # sheet3 ROE
    ws4.cell(row=8, column=2).number_format = "0.00%"
    ws4.cell(row=9, column=1, value="资产负债率反向贡献（30%）").font = label_font
    ws4.cell(row=9, column=2, value="=(1-'3_季报关键指标'!B7)*0.3")  # 1 - sheet3 资产负债率
    ws4.cell(row=9, column=2).number_format = "0.00%"
    ws4.cell(row=10, column=1, value="毛利率贡献（20%）").font = label_font
    ws4.cell(row=10, column=2, value="='3_季报关键指标'!B4*0.2")  # sheet3 毛利率
    ws4.cell(row=10, column=2).number_format = "0.00%"
    ws4.cell(row=11, column=1, value="流动比率归一贡献（10%）").font = label_font
    ws4.cell(row=11, column=2, value="=MIN('3_季报关键指标'!B8/10,1)*0.1")
    ws4.cell(row=11, column=2).number_format = "0.00%"
    ws4.cell(row=12, column=1, value="财务健康度总分").font = Font(bold=True, color="2E5C8A")
    ws4.cell(row=12, column=2, value="=SUM(B8:B11)")
    ws4.cell(row=12, column=2).number_format = "0.00%"
    ws4.cell(row=12, column=2).font = Font(bold=True, color="2E5C8A", size=12)

    # ─────── Sheet 5：投资分析（综合评级 · 跨 4 sheet 引用） ───────
    ws5 = wb.create_sheet("5_投资分析")
    ws5.append(["维度", "评分", "权重", "加权得分", "来源"])
    for cell in ws5[1]:
        cell.font = header_font
        cell.fill = header_fill

    ws5.append(["估值合理性", "='1_估值快照'!B9", 0.20, "=B2*C2", "PE/行业 PE"])
    ws5.cell(row=2, column=2).number_format = "0.00"
    ws5.append(["财务健康", "='4_资金流与持仓'!B12", 0.30, "=B3*C3", "Sheet 4 总分"])
    ws5.cell(row=3, column=2).number_format = "0.00%"
    ws5.append(["业绩同比", "='3_季报关键指标'!C2", 0.20, "=B4*C4", "Sheet 3 营收同比差"])
    ws5.cell(row=4, column=2).number_format = "0.00%"
    ws5.append(["资金面（北向）", "='4_资金流与持仓'!B5", 0.15, "=B5*C5", "Sheet 4 持股比例"])
    ws5.cell(row=5, column=2).number_format = "0.00%"
    ws5.append(["分析师一致预期", "='1_估值快照'!B11", 0.15, "=B6*C6", "目标价中位数 / 当前价"])
    ws5.cell(row=6, column=2).number_format = "0"

    ws5.cell(row=7, column=1, value="综合得分").font = Font(bold=True, color="C0392B", size=12)
    ws5.cell(row=7, column=2, value="=SUM(D2:D6)")
    ws5.cell(row=7, column=2).font = Font(bold=True, color="C0392B", size=12)
    ws5.cell(row=7, column=2).number_format = "0.000"

    ws5.cell(row=8, column=1, value="投资建议").font = Font(bold=True)
    ws5.cell(row=8, column=2, value='=IF(B7>0.6,"强烈推荐",IF(B7>0.4,"推荐",IF(B7>0.2,"中性","回避")))')
    ws5.cell(row=8, column=2).font = Font(bold=True, color="2E5C8A", size=14)

    # ─────── 列宽 ───────
    for ws in [ws1, ws2, ws3, ws4, ws5]:
        ws.column_dimensions["A"].width = 28
        ws.column_dimensions["B"].width = 18
        ws.column_dimensions["C"].width = 14
        ws.column_dimensions["D"].width = 14
        ws.column_dimensions["F"].width = 18
        ws.column_dimensions["G"].width = 16

    # ─────── 图表：Sheet 2 资产构成 ───────
    chart = BarChart()
    chart.title = "资产负债表构成（亿元）"
    chart.type = "bar"
    chart.style = 11
    data = Reference(ws2, min_col=2, min_row=1, max_row=9, max_col=2)
    cats = Reference(ws2, min_col=1, min_row=2, max_row=9)
    chart.add_data(data, titles_from_data=False)
    chart.set_categories(cats)
    chart.width = 16
    chart.height = 8
    ws2.add_chart(chart, "F2")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)

    return {
        "symbol": symbol,
        "path": str(output_path),
        "sheets": len(wb.sheetnames),
        "endpoints": [r.endpoint for r in results],
        "rows_total": sum(r.rows for r in results),
        "fetched_at": r_pe.fetched_at,
        "size_bytes": output_path.stat().st_size,
    }


# ─── 主入口 ────────────────────────────────────────────────────────────────

def main() -> int:
    out = Path(__file__).resolve().parent.parent / "output" / f"贵州茅台-财务模型-{datetime.now(TZ_CN).strftime('%Y-%m-%d')}.xlsx"
    r = build_finance_workbook("600519.SH", out)

    print("=" * 70)
    print("Stage 47.2 · Sheet + a-stock-data-bridge 跨 Unit 公式联动")
    print("=" * 70)
    print(f"  Symbol:    {r['symbol']}")
    print(f"  Path:      {r['path']}")
    print(f"  Sheets:    {r['sheets']}")
    print(f"  Endpoints: {', '.join(r['endpoints'])}")
    print(f"  Rows:      {r['rows_total']}")
    print(f"  Fetched:   {r['fetched_at']}")
    print(f"  Size:      {r['size_bytes']} B")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
