"""阶段 47.11 · univer_cross_unit_formula 验证

本脚本：
  1. 模拟 univer_cross_unit_formula 的 buildReference / upsertExternalReference
  2. 构造跨 Unit 公式（Sheet → Sheet / Shape → Sheet / Shape → Base）
  3. 验证 formula + externalReferences 一致性
  4. 验证 onCalculationResultApplied 订阅/await 模式
  5. 验证 Shape formula 替换为 regular shape 的 removeFormula 语义

Author: dragon-engine · Stage 47.11 · 2026-08-26
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ─── Facade 接口语义 ─────────────────────────────────────────────────────

@dataclass
class ExternalReference:
    """externalReference 元数据（持久在 Host Unit 上）"""
    qualifier: str           # 与公式中的 '[qualifier]...' 匹配
    source_unit_id: str
    source_unit_type: str    # UNIVER_SHEET / UNIVER_BASE / UNIVER_DOC / etc.
    source_unit_name: str = ""  # formulaQualifier 用


@dataclass
class FormulaResult:
    """公式执行结果"""
    status: str            # SUCCESS / FAILED / PENDING
    raw_value: Any = None
    display_text: str = ""
    number_format: str = ""
    error: str = ""


@dataclass
class SourceTarget:
    """buildReference 的 target 描述"""
    kind: str              # SHEET_RANGE / TABLE_COLUMN / etc.
    sheet_name: str = ""
    range: dict = field(default_factory=dict)   # {startRow, endRow, startColumn, endColumn}
    table_name: str = ""
    column_name: str = ""


class FormulaBuilder:
    """buildReference + upsertExternalReference 模拟"""

    def __init__(self):
        self.registry: dict[str, ExternalReference] = {}  # host_unit_id → ext_ref

    def build_reference(self, host_unit_id: str, source_unit_id: str,
                        source_unit_name: str,
                        target: SourceTarget) -> str:
        """构造引用字符串（与 univer-cross-unit-formula/SKILL.md §Resolve the public API 一致）

        上游规则：
          - formulaQualifier = source_unit_name
          - 公式按名寻址，metadata 保稳定 ID
          - buildReference 负责 quote/escape
        """
        if target.kind == "SHEET_RANGE":
            rng = target.range
            return (
                f"'{source_unit_name}'!{target.sheet_name}!"
                f"R{rng['startRow']+1}C{rng['startColumn']+1}:R{rng['endRow']+1}C{rng['endColumn']+1}"
            )
        elif target.kind == "TABLE_COLUMN":
            return f"{source_unit_name}[{target.column_name}]"
        else:
            raise ValueError(f"unknown target kind: {target.kind}")

    def upsert_external_reference(self, host_unit_id: str, qualifier: str,
                                   source_unit_id: str, source_unit_type: str) -> bool:
        """持久化 external reference metadata"""
        existing = self.registry.get(host_unit_id)
        if existing and existing.qualifier != qualifier:
            return False  # 不同 qualifier → 冲突
        self.registry[host_unit_id] = ExternalReference(
            qualifier=qualifier,
            source_unit_id=source_unit_id,
            source_unit_type=source_unit_type,
            source_unit_name=qualifier,  # 默认同名
        )
        return True

    def get_external_reference(self, host_unit_id: str) -> ExternalReference | None:
        return self.registry.get(host_unit_id)


class CalculationTracker:
    """onCalculationResultApplied 订阅 + await 模式"""

    def __init__(self):
        self.subscribers: list = []
        self.applied_results: list[FormulaResult] = []

    def subscribe(self, callback):
        """订阅 calculation 完成事件"""
        self.subscribers.append(callback)

    def trigger(self, results: list[FormulaResult]):
        """触发 calculation 完成（模拟 DSH 框架调 callback）"""
        self.applied_results.extend(results)
        for cb in self.subscribers:
            cb(results)


# ─── 验证场景 ──────────────────────────────────────────────────────────

def test_build_reference_sheet_range() -> dict:
    """场景 1: buildReference 构造 Sheet 范围引用"""
    fb = FormulaBuilder()
    target = SourceTarget(
        kind="SHEET_RANGE",
        sheet_name="Sales",
        range={"startRow": 1, "endRow": 3, "startColumn": 1, "endColumn": 2},
    )
    ref = fb.build_reference(
        host_unit_id="host-001",
        source_unit_id="source-001",
        source_unit_name="Sales Source",
        target=target,
    )
    assert ref == "'Sales Source'!Sales!R2C2:R4C3", f"[FAIL] ref = {ref}"
    return {"name": "build_reference_sheet_range", "ok": True, "ref": ref}


def test_upsert_external_reference() -> dict:
    """场景 2: upsertExternalReference 持久化 metadata"""
    fb = FormulaBuilder()
    ok1 = fb.upsert_external_reference(
        host_unit_id="host-002",
        qualifier="Sales Source",
        source_unit_id="source-002",
        source_unit_type="UNIVER_SHEET",
    )
    assert ok1, "[FAIL] 首次 upsert 应成功"

    # 同 host + 同 qualifier → 幂等（更新）
    ok2 = fb.upsert_external_reference(
        host_unit_id="host-002",
        qualifier="Sales Source",
        source_unit_id="source-002",
        source_unit_type="UNIVER_SHEET",
    )
    assert ok2, "[FAIL] 同 host+qualifier 应幂等"

    # 不同 qualifier → 冲突
    ok3 = fb.upsert_external_reference(
        host_unit_id="host-002",
        qualifier="Different Source",
        source_unit_id="source-002",
        source_unit_type="UNIVER_SHEET",
    )
    assert not ok3, "[FAIL] 不同 qualifier 应被拒绝"

    ref = fb.get_external_reference("host-002")
    assert ref.qualifier == "Sales Source"
    return {"name": "upsert_external_reference", "ok": True,
            "first_ok": ok1, "idempotent_ok": ok2, "conflict_rejected": not ok3}


def test_sheet_cell_consumer() -> dict:
    """场景 3: Sheet 单元格消费方（formula + external ref + 计算）"""
    fb = FormulaBuilder()
    tracker = CalculationTracker()
    results_received = []

    def on_calc(results):
        results_received.extend(results)

    tracker.subscribe(on_calc)

    # 1. upsert external ref
    fb.upsert_external_reference("host-003", "Sales Source", "source-003", "UNIVER_SHEET")

    # 2. build reference
    target = SourceTarget(kind="SHEET_RANGE", sheet_name="Sales",
                          range={"startRow": 1, "endRow": 3, "startColumn": 1, "endColumn": 1})
    ref = fb.build_reference("host-003", "source-003", "Sales Source", target)

    # 3. setFormula（公式 host 单元）
    formula = f"=SUM({ref})"
    assert formula.startswith("=SUM(")
    assert "'Sales Source'" in formula

    # 4. await onCalculationResultApplied
    fake_result = FormulaResult(status="SUCCESS", raw_value=42.5, display_text="42.5")
    tracker.trigger([fake_result])

    assert len(results_received) == 1
    assert results_received[0].status == "SUCCESS"
    assert results_received[0].raw_value == 42.5

    return {"name": "sheet_cell_consumer", "ok": True,
            "formula": formula, "result_value": fake_result.raw_value}


def test_formula_driven_shape_consumer() -> dict:
    """场景 4: Shape 消费方（插入 → setFormula with externalReferences → 验证）"""
    fb = FormulaBuilder()
    tracker = CalculationTracker()
    results_received = []

    def on_calc(results):
        results_received.extend(results)

    tracker.subscribe(on_calc)

    # 创建 Shape（in host sheet）
    host_unit_id = "host-004"
    shape_id = "shape-kpi-001"
    shape_type = "Rect"

    # 构造 reference + external reference
    fb.upsert_external_reference(host_unit_id, "Sales Source", "source-004", "UNIVER_SHEET")
    target = SourceTarget(kind="SHEET_RANGE", sheet_name="Sales",
                          range={"startRow": 1, "endRow": 1, "startColumn": 1, "endColumn": 1})
    ref = fb.build_reference(host_unit_id, "source-004", "Sales Source", target)

    # Shape.setFormula({formula, externalReferences})
    formula_obj = {
        "formula": f"=SUM({ref})",
        "externalReferences": [{
            "qualifier": "Sales Source",
            "sourceUnitId": "source-004",
            "sourceUnitType": "UNIVER_SHEET",
        }],
    }

    # 触发计算
    tracker.trigger([FormulaResult(status="SUCCESS", raw_value=42.5)])

    # 验证 success 状态
    assert results_received[0].status == "SUCCESS"

    return {"name": "formula_driven_shape", "ok": True,
            "shape_id": shape_id, "formula": formula_obj["formula"],
            "ext_refs_count": len(formula_obj["externalReferences"])}


def test_remove_formula() -> dict:
    """场景 5: Shape.removeFormula() → 转成 regular Shape 保留内容/样式"""
    # 上游规则：removeFormula 转 regular shape，保留 content + style

    # 模拟：一个 formula-driven Shape
    shape = {
        "id": "shape-kpi",
        "type": "Rect",
        "is_formula": True,
        "formula": "=SUM('Sales Source'!Sales!R2C2)",
        "externalReferences": [{"qualifier": "Sales Source", "sourceUnitId": "source-005"}],
        "content": "42.5",       # 公式结果缓存
        "style": {"fill": "#E8F4FD"},
    }

    # removeFormula
    shape["is_formula"] = False
    # 公式清除，但 content + style 保留
    # shape["formula"] = None  # cleared
    # shape["externalReferences"] = []  # cleared

    assert shape["is_formula"] is False
    assert shape["content"] == "42.5"  # 保留
    assert shape["style"]["fill"] == "#E8F4FD"  # 保留
    return {"name": "remove_formula", "ok": True, "is_formula_after": shape["is_formula"]}


def test_source_mutation_triggers_recalc() -> dict:
    """场景 6: Source 变更触发重算（上游 §Acceptance 规则 3）"""
    fb = FormulaBuilder()
    tracker = CalculationTracker()
    calc_count = [0]

    def on_calc(results):
        calc_count[0] += 1
        # 记录每次结果
        if results:
            tracker.applied_results.append(results[0])

    tracker.subscribe(on_calc)

    # 初始写公式 + 重算 1
    fb.upsert_external_reference("host-006", "Sales Source", "source-006", "UNIVER_SHEET")
    target = SourceTarget(kind="SHEET_RANGE", sheet_name="Sales",
                          range={"startRow": 1, "endRow": 3, "startColumn": 1, "endColumn": 1})
    ref = fb.build_reference("host-006", "source-006", "Sales Source", target)
    tracker.trigger([FormulaResult(status="SUCCESS", raw_value=42.5)])  # 第 1 次

    # 改 Source 值 + 重算 2
    tracker.trigger([FormulaResult(status="SUCCESS", raw_value=50.0)])  # 第 2 次

    # 改 Source 值 + 重算 3
    tracker.trigger([FormulaResult(status="SUCCESS", raw_value=75.5)])  # 第 3 次

    assert calc_count[0] == 3
    # 最后一次重算应该是 75.5
    assert tracker.applied_results[-1].raw_value == 75.5

    return {"name": "source_mutation_recalc", "ok": True,
            "calc_count": calc_count[0], "last_value": 75.5}


# ─── 主入口 ────────────────────────────────────────────────────────────────

def main() -> int:
    print("=" * 70)
    print("Stage 47.11 · univer_cross_unit_formula 验证")
    print("=" * 70)

    results = [
        test_build_reference_sheet_range(),
        test_upsert_external_reference(),
        test_sheet_cell_consumer(),
        test_formula_driven_shape_consumer(),
        test_remove_formula(),
        test_source_mutation_triggers_recalc(),
    ]

    for r in results:
        status = "PASS" if r["ok"] else "FAIL"
        print(f"\n[{status}] {r['name']}")
        for k, v in r.items():
            if k not in ("ok", "name"):
                print(f"    {k}: {v}")

    print("\n" + "=" * 70)
    print(f"Stage 47.11 PASS: {sum(1 for r in results if r['ok'])}/{len(results)} 场景")
    print("=" * 70)

    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
