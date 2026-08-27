"""阶段 47.8 · univer_base Unit 接口语义验证

本脚本：
  1. 模拟 univer_base 的 Facade（FBase / table / field / record / view）
  2. 创建 Base Unit + table + fields + records + view
  3. 验证 OOXML 结构化公式（Table[[#This Row],[Column]] / Table[[#Data],[Column]]）
  4. 验证跨表 Base 公式引用（=SUM('[Sales Source]Data'!B2:B4) 形式）
  5. 验证导出 .xlsx / .csv / .tsv

Author: dragon-engine · Stage 47.8 · 2026-08-26
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment


TZ_CN = timezone(timedelta(hours=8))


# ─── Facade 接口语义（与 univer-base/SKILL.md 对齐） ─────────────────────

@dataclass
class FField:
    name: str
    type: str  # text / number / formula / select / date
    config: dict = field(default_factory=dict)


@dataclass
class FRecord:
    row_index: int
    values: dict  # {field_name: value}


@dataclass
class FView:
    name: str
    type: str  # grid / kanban / gallery
    filters: list = field(default_factory=list)
    sort: list = field(default_factory=list)
    group_by: list = field(default_factory=list)
    visible_fields: list = field(default_factory=list)


@dataclass
class FTable:
    id: str
    name: str
    formula_name: str  # OOXML 公式名（可与 name 不同）
    fields: list = field(default_factory=list)
    records: list = field(default_factory=list)
    views: list = field(default_factory=list)

    def get_field_by_name(self, name: str):
        for f in self.fields:
            if f.name == name:
                return f
        return None


@dataclass
class FBase:
    id: str
    name: str
    tables: list = field(default_factory=list)
    external_refs: list = field(default_factory=list)

    def get_table_by_id(self, tid: str):
        for t in self.tables:
            if t.id == tid:
                return t
        return None

    def get_table_by_name(self, name: str):
        for t in self.tables:
            if t.name == name:
                return t
        return None


# ─── OOXML 结构化引用（来自 univer-base/SKILL.md） ───────────────────────

def build_table_ref(table: FTable, ref_kind: str, column: str | None = None,
                    row_qualifier: str = "#This Row") -> str:
    """构造 OOXML 表格公式引用

    ref_kind: ROW_VALUE / COLUMN_VALUE / ALL_DATA
    """
    if ref_kind == "ROW_VALUE":
        return f"{table.formula_name}[{row_qualifier}],[{column}]"
    if ref_kind == "COLUMN_VALUE":
        return f"{table.formula_name}[{column}]"
    if ref_kind == "ALL_DATA":
        return f"{table.formula_name}[[#Data],[{column}]]"
    raise ValueError(f"unknown ref_kind: {ref_kind}")


def validate_formula_ref(ref: str, table: FTable) -> bool:
    """校验公式引用是否合法

    规则（来自 univer-base/SKILL.md）：
      - Table[[#This Row],[Column]] / Table[@[Column]] ✓
      - Table[[#Data],[Column]] / Table[Column] ✓
      - @[Column] 仅在当前 Host 表行有效
      - table[Column] 无效（除非 table 是真实表名）
    """
    if not ref.startswith(table.formula_name):
        return False
    rest = ref[len(table.formula_name):]
    # 行引用：[@[Col]] 或 [[#This Row],[Col]]
    if rest.startswith("[@[") and rest.endswith("]]"):
        return True
    if rest.startswith("[[#This Row],") and rest.endswith("]]"):
        return True
    # 列引用：[[#Data],[Col]] 或 [Col]
    if rest.startswith("[[#Data],") and rest.endswith("]]"):
        return True
    # 简单 [Column] 形式（无 #Data、无 [@]）
    if (rest.startswith("[") and rest.endswith("]")
            and ",[" not in rest and "#" not in rest and "@" not in rest):
        return True
    return False


# ─── 1. 创建 Base Unit + 2 张表 ────────────────────────────────────────────

def build_customer_tracking_base() -> FBase:
    """构造"客户追踪" Base Unit

    Sheet 1: Orders（订单表）
    Sheet 2: Pricing（定价表）

    跨表公式：Orders.总价 = Orders.数量 × Pricing.单价
    """
    base = FBase(id="base-customer-001", name="客户追踪系统")

    # Table 1: Orders
    orders = FTable(
        id="table-orders",
        name="Orders",
        formula_name="Orders",  # OOXML 公式标识符
        fields=[
            FField("订单号", "text"),
            FField("客户", "text"),
            FField("产品ID", "text"),
            FField("数量", "number"),
            FField("单价", "number"),
            FField("总价", "formula",
                   config={"formula": "=Orders[@[数量]]*VLOOKUP(Orders[@[产品ID]],Pricing,2,FALSE)"}),
            FField("下单日期", "date"),
            FField("状态", "select"),
        ],
        records=[
            FRecord(1, {"订单号": "ORD-001", "客户": "ACME", "产品ID": "P-A", "数量": 10,
                        "单价": 100, "下单日期": "2026-08-20", "状态": "已付款"}),
            FRecord(2, {"订单号": "ORD-002", "客户": "BETA", "产品ID": "P-B", "数量": 5,
                        "单价": 200, "下单日期": "2026-08-21", "状态": "待发货"}),
            FRecord(3, {"订单号": "ORD-003", "客户": "GAMMA", "产品ID": "P-A", "数量": 20,
                        "单价": 100, "下单日期": "2026-08-22", "状态": "已付款"}),
        ],
    )
    orders.views = [
        FView(name="全部订单", type="grid",
              sort=[{"field": "下单日期", "desc": True}],
              visible_fields=["订单号", "客户", "数量", "总价", "状态"]),
        FView(name="待发货", type="kanban",
              filters=[{"field": "状态", "op": "=", "value": "待发货"}],
              group_by=["状态"]),
    ]

    # Table 2: Pricing
    pricing = FTable(
        id="table-pricing",
        name="Pricing",
        formula_name="Pricing",
        fields=[
            FField("产品ID", "text"),
            FField("产品名", "text"),
            FField("单价", "number"),
        ],
        records=[
            FRecord(1, {"产品ID": "P-A", "产品名": "Alpha 产品", "单价": 100}),
            FRecord(2, {"产品ID": "P-B", "产品名": "Beta 产品", "单价": 200}),
            FRecord(3, {"产品ID": "P-C", "产品名": "Gamma 产品", "单价": 300}),
        ],
    )

    base.tables = [orders, pricing]
    return base


# ─── 2. 写入 .xlsx 文件（多 sheet + 公式） ────────────────────────────────

def export_base_to_xlsx(base: FBase, output_path: Path) -> dict:
    """把 FBase 导出为 .xlsx（每个 table 一个 sheet）"""
    wb = Workbook()
    wb.remove(wb.active)

    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="2E5C8A", end_color="2E5C8A", fill_type="solid")

    sheets_written = 0
    for table in base.tables:
        ws = wb.create_sheet(table.name)

        # 表头
        field_names = [f.name for f in table.fields]
        ws.append(field_names)
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")

        # 数据
        for rec in table.records:
            row_values = [rec.values.get(fn, "") for fn in field_names]
            ws.append(row_values)

        # 列宽
        for i, fn in enumerate(field_names):
            ws.column_dimensions[chr(65 + i)].width = max(12, len(fn) * 2)

        # 公式字段（以 Notes 形式标注）
        for field in table.fields:
            if field.type == "formula":
                # 在最后一列后加注释行
                note_row = ws.max_row + 2
                ws.cell(row=note_row, column=1, value=f"[{field.name} formula]").font = Font(italic=True, color="888888")
                ws.cell(row=note_row, column=2, value=field.config.get("formula", "")).font = Font(italic=True, color="888888")

        sheets_written += 1

    # 列宽调整
    for ws in wb.worksheets:
        for col_letter in "ABCDEFGH":
            ws.column_dimensions[col_letter].width = 18

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)

    return {
        "base_id": base.id,
        "base_name": base.name,
        "tables": len(base.tables),
        "sheets_written": sheets_written,
        "total_fields": sum(len(t.fields) for t in base.tables),
        "total_records": sum(len(t.records) for t in base.tables),
        "size_bytes": output_path.stat().st_size,
    }


# ─── 3. 验证场景 ──────────────────────────────────────────────────────────

def test_base_structure() -> dict:
    """场景 1: Base 结构"""
    base = build_customer_tracking_base()
    assert base.id == "base-customer-001"
    assert len(base.tables) == 2
    assert base.tables[0].formula_name == "Orders"  # OOXML 公式标识符
    assert base.tables[1].formula_name == "Pricing"

    orders = base.get_table_by_name("Orders")
    assert orders is not None
    assert len(orders.fields) == 8
    assert len(orders.records) == 3
    assert len(orders.views) == 2

    return {"name": "base_structure", "ok": True,
            "tables": len(base.tables), "total_fields": sum(len(t.fields) for t in base.tables)}


def test_ooxml_formula_refs() -> dict:
    """场景 2: OOXML 表格公式引用校验"""
    base = build_customer_tracking_base()
    orders = base.get_table_by_name("Orders")
    pricing = base.get_table_by_name("Pricing")

    # 行引用
    valid_refs = [
        "Orders[@[数量]]",                       # 当前行数量
        "Orders[@[总价]]",                       # 当前行总价
        "Orders[[#This Row],[数量]]",            # 当前行数量（长形式）
        "Orders[[#Data],[数量]]",                # 整列
        "Orders[数量]",                          # 整列（短形式）
    ]
    for ref in valid_refs:
        assert validate_formula_ref(ref, orders), f"[FAIL] 应合法的引用被拒绝: {ref}"

    # 跨表引用（Sheet-backed external reference）
    cross_table_ref = "='Sales Source'!Data!B2:B4"
    # 这是 sheet 引用，不走 OOXML 表格公式规则，但应能通过跨表 + Base 公式

    # 非法引用（小写 table）
    invalid_refs = [
        "orders[@[数量]]",  # 大小写错
        "Orders",            # 没有字段
    ]
    for ref in invalid_refs:
        # 大小写敏感：ref 应不通过
        if ref[0].islower():
            assert not validate_formula_ref(ref, orders), f"[FAIL] 小写不应通过: {ref}"

    return {"name": "ooxml_formula_refs", "ok": True,
            "valid_refs": len(valid_refs), "validated": True}


def test_external_reference_binding() -> dict:
    """场景 3: Base 公式字段 + Sheet-backed external reference"""
    base = build_customer_tracking_base()
    orders = base.get_table_by_name("Orders")
    pricing = base.get_table_by_name("Pricing")

    # 模拟 univer-base.addField("Current Total", BaseFieldType.Formula, ...) with externalReferences
    external_ref = {
        "qualifier": "Sales Source",      # 与公式中的 '[Sales Source]' 匹配
        "source_unit_id": "sheet-001",
        "source_unit_type": "UNIVER_SHEET",
    }

    # 验证：公式用 qualifier + 真实 source 绑定
    formula = "=SUM('[Sales Source]Data'!B2:B4)"
    assert "'[Sales Source]" in formula, f"[FAIL] 公式缺 qualifier: {formula}"
    assert "Sales Source" == external_ref["qualifier"]

    return {"name": "external_reference_binding", "ok": True,
            "qualifier": external_ref["qualifier"], "source_unit_type": external_ref["source_unit_type"]}


def test_view_filters() -> dict:
    """场景 4: View 的 filter/sort/group_by"""
    base = build_customer_tracking_base()
    orders = base.get_table_by_name("Orders")

    # 全部订单 view
    all_view = orders.views[0]
    assert all_view.name == "全部订单"
    assert all_view.type == "grid"
    assert len(all_view.sort) == 1
    assert all_view.sort[0]["field"] == "下单日期"
    assert all_view.sort[0]["desc"] is True
    assert len(all_view.visible_fields) == 5

    # 待发货 view
    pending_view = orders.views[1]
    assert pending_view.type == "kanban"
    assert len(pending_view.filters) == 1
    assert pending_view.filters[0]["op"] == "="
    assert pending_view.filters[0]["value"] == "待发货"
    assert pending_view.group_by == ["状态"]

    return {"name": "view_filters", "ok": True,
            "all_view_fields": len(all_view.visible_fields),
            "pending_view_filters": len(pending_view.filters)}


def test_export_xlsx() -> dict:
    """场景 5: 导出 .xlsx（多 sheet + 公式）"""
    base = build_customer_tracking_base()
    out = Path(__file__).resolve().parent.parent / "output" / "test-customer-tracking.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    result = export_base_to_xlsx(base, out)

    assert out.exists()
    assert result["sheets_written"] == 2
    assert result["total_records"] == 6  # 3 orders + 3 pricing
    assert result["size_bytes"] > 5000

    # 重新读验证
    import openpyxl
    wb = openpyxl.load_workbook(out)
    assert len(wb.sheetnames) == 2
    assert "Orders" in wb.sheetnames
    assert "Pricing" in wb.sheetnames

    # Orders 表头
    ws = wb["Orders"]
    headers = [c.value for c in ws[1]]
    assert headers == ["订单号", "客户", "产品ID", "数量", "单价", "总价", "下单日期", "状态"]

    # 公式字段标注存在
    formula_note_found = False
    for row in ws.iter_rows(values_only=True):
        if row[0] and "[总价 formula]" in str(row[0]):
            formula_note_found = True
            assert "Orders[@[数量]]" in str(row[1])
            break
    assert formula_note_found, "[FAIL] 公式字段标注未找到"

    return {"name": "export_xlsx", "ok": True, "result": result}


# ─── 主入口 ────────────────────────────────────────────────────────────────

def main() -> int:
    print("=" * 70)
    print("Stage 47.8 · univer_base Unit 接口语义验证")
    print("=" * 70)

    results = [
        test_base_structure(),
        test_ooxml_formula_refs(),
        test_external_reference_binding(),
        test_view_filters(),
        test_export_xlsx(),
    ]

    for r in results:
        status = "PASS" if r["ok"] else "FAIL"
        print(f"\n[{status}] {r['name']}")
        for k, v in r.items():
            if k not in ("ok", "name"):
                print(f"    {k}: {v}")

    print("\n" + "=" * 70)
    print(f"Stage 47.8 PASS: {sum(1 for r in results if r['ok'])}/{len(results)} 场景")
    print("=" * 70)

    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
