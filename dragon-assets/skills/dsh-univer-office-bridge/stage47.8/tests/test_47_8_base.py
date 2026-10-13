"""test_47_8_base · 5 个 univer_base 场景全部 PASS"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from base_demo import (
    test_base_structure,
    test_ooxml_formula_refs,
    test_external_reference_binding,
    test_view_filters,
    test_export_xlsx,
    build_customer_tracking_base,
    validate_formula_ref,
    build_table_ref,
)


def test_47_8_base():
    # 场景 1: Base 结构
    r1 = test_base_structure()
    assert r1["ok"]
    assert r1["tables"] == 2
    print(f"[PASS] base_structure: 2 tables + {r1['total_fields']} fields")

    # 场景 2: OOXML 公式引用
    r2 = test_ooxml_formula_refs()
    assert r2["ok"]
    assert r2["valid_refs"] == 5
    print(f"[PASS] ooxml_formula_refs: {r2['valid_refs']} 合法引用全部通过")

    # 场景 3: 跨表 External Reference
    r3 = test_external_reference_binding()
    assert r3["ok"]
    assert r3["qualifier"] == "Sales Source"
    print(f"[PASS] external_reference_binding: qualifier={r3['qualifier']}, source={r3['source_unit_type']}")

    # 场景 4: View filters/sort/group_by
    r4 = test_view_filters()
    assert r4["ok"]
    assert r4["all_view_fields"] == 5
    assert r4["pending_view_filters"] == 1
    print(f"[PASS] view_filters: grid(5 fields) + kanban(1 filter)")

    # 场景 5: 导出 xlsx
    r5 = test_export_xlsx()
    assert r5["ok"]
    assert r5["result"]["sheets_written"] == 2
    assert r5["result"]["total_records"] == 6
    print(f"[PASS] export_xlsx: {r5['result']['sheets_written']} sheets, {r5['result']['total_records']} records, {r5['result']['size_bytes']} B")


# 独立 test function 让 pytest 单独收集
test_base_structure.__test__ = True
test_ooxml_formula_refs.__test__ = True
test_external_reference_binding.__test__ = True
test_view_filters.__test__ = True
test_export_xlsx.__test__ = True
