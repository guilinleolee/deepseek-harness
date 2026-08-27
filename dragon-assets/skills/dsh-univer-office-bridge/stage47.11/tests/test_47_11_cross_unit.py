"""test_47_11_cross_unit · 6 个跨 Unit 公式场景"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from cross_unit import (
    FormulaBuilder,
    CalculationTracker,
    FormulaResult,
    SourceTarget,
    test_build_reference_sheet_range,
    test_upsert_external_reference,
    test_sheet_cell_consumer,
    test_formula_driven_shape_consumer,
    test_remove_formula,
    test_source_mutation_triggers_recalc,
)


def test_47_11_cross_unit():
    # 场景 1
    r1 = test_build_reference_sheet_range()
    assert r1["ok"]
    assert r1["ref"].startswith("'Sales Source'!")
    print(f"[PASS] build_reference: {r1['ref']}")

    # 场景 2
    r2 = test_upsert_external_reference()
    assert r2["ok"]
    assert r2["first_ok"] and r2["idempotent_ok"] and r2["conflict_rejected"]
    print(f"[PASS] upsert_external_reference: first_ok={r2['first_ok']}, idempotent_ok={r2['idempotent_ok']}")

    # 场景 3
    r3 = test_sheet_cell_consumer()
    assert r3["ok"]
    assert "SUM" in r3["formula"]
    print(f"[PASS] sheet_cell_consumer: formula={r3['formula'][:50]}..., result={r3['result_value']}")

    # 场景 4
    r4 = test_formula_driven_shape_consumer()
    assert r4["ok"]
    assert r4["ext_refs_count"] == 1
    print(f"[PASS] formula_driven_shape: ext_refs={r4['ext_refs_count']}")

    # 场景 5
    r5 = test_remove_formula()
    assert r5["ok"]
    assert r5["is_formula_after"] is False
    print(f"[PASS] remove_formula: 转 regular shape 保留 content + style")

    # 场景 6
    r6 = test_source_mutation_triggers_recalc()
    assert r6["ok"]
    assert r6["calc_count"] == 3
    assert r6["last_value"] == 75.5
    print(f"[PASS] source_mutation_triggers_recalc: {r6['calc_count']} 次重算, 最终值 {r6['last_value']}")


# 独立 test
test_build_reference_sheet_range.__test__ = True
test_upsert_external_reference.__test__ = True
test_sheet_cell_consumer.__test__ = True
test_formula_driven_shape_consumer.__test__ = True
test_remove_formula.__test__ = True
test_source_mutation_triggers_recalc.__test__ = True
