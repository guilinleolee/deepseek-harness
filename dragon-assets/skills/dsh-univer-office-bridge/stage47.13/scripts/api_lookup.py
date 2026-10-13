"""阶段 47.13 · univer_api 验证（Facade symbol 查找）

本脚本：
  1. 模拟 univer_api 的 find / show 接口
  2. 验证按关键词查找（不解释 intent）
  3. 验证 show 精确返回 class/member/type/field/enum
  4. 验证 curated symbol database（模拟 univer-cli/api-reference）

Author: dragon-engine · Stage 47.13 · 2026-08-26
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from typing import Any


# ─── Symbol Database（模拟 univer-cli/api-reference 索引） ───────────────

@dataclass
class SymbolDoc:
    """univer-api show 返回的精确引用"""
    label: str                       # "FWorkbook.setValue"
    kind: str                        # class / method / field / enum / type
    parent: str = ""                 # "FWorkbook"
    signature: str = ""              # "setValue(cell: FCellData | ICellData): boolean"
    params: list = field(default_factory=list)  # [{name, type, desc}]
    returns: str = ""                # "boolean"
    description: str = ""
    since: str = "1.0.0"
    example: str = ""
    category: str = ""               # sheet / doc / slide / base / board / cross

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v not in (None, "", [])}


# 内置 symbol 数据库（按 univer Facade 精选）
SYMBOL_DATABASE: list[SymbolDoc] = [
    # ─── Sheet Facade ───
    SymbolDoc(
        label="FWorkbook", kind="class", category="sheet",
        description="Sheet Unit 的主 facade",
        since="1.0.0",
        example="const workbook = univerAPI.getWorkbook(unitId);",
    ),
    SymbolDoc(
        label="FWorkbook.setValue", kind="method", parent="FWorkbook", category="sheet",
        signature="setValue(value: ICellData | ICellData[][]): boolean",
        params=[
            {"name": "value", "type": "ICellData | ICellData[][]",
             "desc": "单元格数据（单格或二维数组）"},
        ],
        returns="boolean",
        description="设置单元格值（自动覆盖）",
        since="1.0.0",
        example="sheet.getActiveSheet().getRange('A1').setValue({v: 'hello', t: 1})",
    ),
    SymbolDoc(
        label="FWorkbook.getActiveSheet", kind="method", parent="FWorkbook", category="sheet",
        signature="getActiveSheet(): FWorksheet",
        returns="FWorksheet",
        description="获取当前激活的工作表",
        since="1.0.0",
    ),
    SymbolDoc(
        label="FWorksheet.getRange", kind="method", parent="FWorksheet", category="sheet",
        signature="getRange(range: string | number, number, number?, number?): FRange",
        params=[
            {"name": "range", "type": "string | number",
             "desc": "'A1' 或 row, col（0-based）"},
        ],
        returns="FRange",
        description="获取范围（支持 A1 字符串或 0-based 坐标）",
        since="1.0.0",
        example="sheet.getRange('A1:C9') 或 sheet.getRange(0, 0, 3, 9)",
    ),
    SymbolDoc(
        label="FRange.setFormula", kind="method", parent="FRange", category="sheet",
        signature="setFormula(formula: string): boolean",
        params=[{"name": "formula", "type": "string", "desc": "公式（如 =SUM(A1:A10)）"}],
        returns="boolean",
        description="设置单元格公式",
        since="1.0.0",
    ),
    SymbolDoc(
        label="FRange.getValue", kind="method", parent="FRange", category="sheet",
        signature="getValue(): any",
        returns="any",
        description="获取单元格 stored value",
        since="1.0.0",
    ),

    # ─── Doc Facade ───
    SymbolDoc(
        label="FDocument", kind="class", category="doc",
        description="Doc Unit 的主 facade",
        since="1.0.0",
    ),
    SymbolDoc(
        label="FDocument.appendParagraph", kind="method", parent="FDocument", category="doc",
        signature="appendParagraph(text?: string): FDocumentParagraph",
        params=[{"name": "text", "type": "string", "desc": "段落文本"}],
        returns="FDocumentParagraph",
        description="追加段落",
        since="1.0.0",
    ),
    SymbolDoc(
        label="FDocument.insertImage", kind="method", parent="FDocument", category="doc",
        signature="insertImage(params: IFDocumentInsertImageParams): Promise<IFImage>",
        params=[{"name": "params", "type": "IFDocumentInsertImageParams"}],
        returns="Promise<IFImage>",
        description="插入图片（headless 必须 width+height）",
        since="1.0.0",
    ),

    # ─── Slide Facade ───
    SymbolDoc(
        label="FPresentation", kind="class", category="slide",
        description="Slide Unit 的主 facade",
        since="1.0.0",
    ),
    SymbolDoc(
        label="FPresentation.getSlides", kind="method", parent="FPresentation", category="slide",
        signature="getSlides(): FSlide[]",
        returns="FSlide[]",
        description="获取所有幻灯片（0-based 索引）",
        since="1.0.0",
    ),
    SymbolDoc(
        label="FSlide.insertShape", kind="method", parent="FSlide", category="slide",
        signature="insertShape(input: IShapeCreateInput): IShape | null",
        params=[{"name": "input", "type": "IShapeCreateInput"}],
        returns="IShape | null",
        description="插入形状（null 表示失败）",
        since="1.0.0",
    ),

    # ─── Base Facade ───
    SymbolDoc(
        label="FBase", kind="class", category="base",
        description="Base Unit 的主 facade（univerAPI.getBase）",
        since="1.0.0",
    ),
    SymbolDoc(
        label="FBase.getTableById", kind="method", parent="FBase", category="base",
        signature="getTableById(tableId: string): FTable | null",
        params=[{"name": "tableId", "type": "string"}],
        returns="FTable | null",
        description="按 ID 查表",
        since="1.0.0",
    ),
    SymbolDoc(
        label="FTable.addField", kind="method", parent="FTable", category="base",
        signature="addField(name: string, type: BaseFieldType, config?: IBaseFieldConfig): boolean",
        params=[{"name": "name", "type": "string"},
                {"name": "type", "type": "BaseFieldType"},
                {"name": "config", "type": "IBaseFieldConfig", "optional": True}],
        returns="boolean",
        description="添加字段（含 Formula 类型 + externalReferences）",
        since="1.0.0",
    ),

    # ─── Cross-Unit Formula ───
    SymbolDoc(
        label="FFormula.buildReference", kind="method", parent="FFormula", category="cross",
        signature="buildReference(params: IBuildReferenceParams): string",
        params=[{"name": "params", "type": "IBuildReferenceParams"}],
        returns="string",
        description="构造跨 Unit 引用字符串（自动 quote/escape）",
        since="1.0.0",
    ),
    SymbolDoc(
        label="FFormula.upsertExternalReference", kind="method", parent="FFormula", category="cross",
        signature="upsertExternalReference(params: IUpsertExternalReferenceParams): boolean",
        params=[{"name": "params", "type": "IUpsertExternalReferenceParams"}],
        returns="boolean",
        description="持久化 external reference metadata（重复 qualifier 失败）",
        since="1.0.0",
    ),
    SymbolDoc(
        label="FFormula.onCalculationResultApplied", kind="method", parent="FFormula", category="cross",
        signature="onCalculationResultApplied(timeout?: number): Promise<unknown>",
        params=[{"name": "timeout", "type": "number", "optional": True}],
        returns="Promise<unknown>",
        description="订阅 calculation 完成事件（先订阅再 setFormula）",
        since="1.0.0",
    ),

    # ─── Embed ───
    SymbolDoc(
        label="FUniver", kind="class", category="embed",
        description="顶级 facade（univerAPI 本身）",
        since="1.0.0",
    ),
    SymbolDoc(
        label="FUniver.createEmbed", kind="method", parent="FUniver", category="embed",
        signature="createEmbed(params: ICreateEmbedParams): FEmbed",
        params=[{"name": "params", "type": "ICreateEmbedParams"}],
        returns="FEmbed",
        description="创建 embed（host + child + surface + interaction）",
        since="1.0.0",
    ),
]


# ─── API 服务 ──────────────────────────────────────────────────────────

class UniverApiService:
    """univer_api 服务（find + show）"""

    def __init__(self, db: list[SymbolDoc] = None):
        self.db = db or SYMBOL_DATABASE

    def find(self, queries: list[str], category: str = "",
            kind: str = "") -> list[dict]:
        """按关键词查找（不解释 task intent）

        规则：
          - 关键词匹配 symbol.label / symbol.description / symbol.parent
          - 可选 category 过滤
          - 可选 kind 过滤
          - 按相关度排序（label 命中 > parent 命中 > description 命中）
        """
        results = []
        for sym in self.db:
            if category and sym.category != category:
                continue
            if kind and sym.kind != kind:
                continue
            # 计算 score
            score = 0
            for q in queries:
                q_lower = q.lower()
                if q_lower == sym.label.lower():
                    score += 10
                elif q_lower in sym.label.lower():
                    score += 5
                if sym.parent and q_lower == sym.parent.lower():
                    score += 3
                if sym.parent and q_lower in sym.parent.lower():
                    score += 2
                if q_lower in sym.description.lower():
                    score += 1
            if score > 0:
                results.append((score, sym))
        results.sort(key=lambda x: (-x[0], x[1].label))
        return [
            {
                "label": sym.label,
                "kind": sym.kind,
                "category": sym.category,
                "score": score,
            }
            for score, sym in results
        ]

    def show(self, label: str) -> dict:
        """精确显示单个 symbol 完整定义"""
        for sym in self.db:
            if sym.label == label:
                return {"ok": True, "symbol": sym.to_dict()}
        return {"ok": False, "error": "SYMBOL_NOT_FOUND", "label": label}


# ─── 验证场景 ──────────────────────────────────────────────────────────

def test_find_by_keyword() -> dict:
    """场景 1: find 按关键词查找（不解释 intent）"""
    api = UniverApiService()

    # 查询 "setValue" → 应返回 FWorkbook.setValue
    results = api.find(["setValue"])
    assert len(results) > 0
    assert results[0]["label"] == "FWorkbook.setValue"
    # score: 完全匹配 label +10; substring 匹配 +5
    # 因为我们 label 含父类前缀（如 FWorkbook.setValue），substring 只能拿到 5
    assert results[0]["score"] >= 5

    return {"name": "find_by_keyword", "ok": True,
            "top_result": results[0]["label"], "score": results[0]["score"]}


def test_find_with_category_filter() -> dict:
    """场景 2: find + category 过滤"""
    api = UniverApiService()

    # "get" 类方法在所有 category 都有 → sheet 内应只返回 sheet 方法
    sheet_results = api.find(["get"], category="sheet")
    assert all(r["category"] == "sheet" for r in sheet_results)

    # cross category 查 FFormula.*  → 用 "FFormula" keyword 命中 3 个
    cross_results = api.find(["FFormula"], category="cross")
    assert any(r["label"] == "FFormula.upsertExternalReference" for r in cross_results)
    assert len(cross_results) >= 3
    return {"name": "find_with_category", "ok": True,
            "sheet_count": len(sheet_results), "cross_count": len(cross_results)}


def test_show_exact_symbol() -> dict:
    """场景 3: show 精确显示"""
    api = UniverApiService()

    # show "FWorkbook.setValue" → 完整定义
    result = api.show("FWorkbook.setValue")
    assert result["ok"]
    sym = result["symbol"]
    assert sym["kind"] == "method"
    assert sym["parent"] == "FWorkbook"
    assert sym["signature"] == "setValue(value: ICellData | ICellData[][]): boolean"
    assert sym["returns"] == "boolean"
    assert len(sym["params"]) == 1
    assert sym["params"][0]["name"] == "value"
    assert "example" in sym

    # show 不存在的 symbol
    result_404 = api.show("NonExistent.method")
    assert not result_404["ok"]
    assert result_404["error"] == "SYMBOL_NOT_FOUND"

    return {"name": "show_exact", "ok": True,
            "setValue_returns": sym["returns"], "params_count": len(sym["params"])}


def test_find_returns_multiple() -> dict:
    """场景 4: find 返回多个相关结果（按相关度排序）"""
    api = UniverApiService()

    # "get" → FWorkbook.getActiveSheet + FBase.getTableById + ...
    results = api.find(["get"])
    assert len(results) >= 3
    # 第一个应该是 "get" 开头的（FWorkbook.getActiveSheet）
    assert "get" in results[0]["label"].lower()
    return {"name": "find_multiple", "ok": True,
            "total_matches": len(results), "top3": [r["label"] for r in results[:3]]}


def test_kinds_filter() -> dict:
    """场景 5: find + kind 过滤（只查 class / method 等）"""
    api = UniverApiService()

    # 只查 class
    classes = api.find(["F"], kind="class")
    assert all(r["kind"] == "class" for r in classes)

    # 只查 method
    methods = api.find(["set"], kind="method")
    assert all(r["kind"] == "method" for r in methods)

    return {"name": "kinds_filter", "ok": True,
            "classes_count": len(classes), "methods_count": len(methods)}


def test_cross_category_symbols() -> dict:
    """场景 6: 跨 category symbols（cross Unit 公式）"""
    api = UniverApiService()

    # 找 FFormula.* 相关
    cross_results = api.find(["FFormula"])
    assert all(r["label"].startswith("FFormula.") for r in cross_results)
    assert any(r["label"] == "FFormula.buildReference" for r in cross_results)
    assert any(r["label"] == "FFormula.upsertExternalReference" for r in cross_results)
    assert any(r["label"] == "FFormula.onCalculationResultApplied" for r in cross_results)

    return {"name": "cross_category", "ok": True,
            "FFormula_count": len(cross_results),
            "methods_found": [r["label"] for r in cross_results]}


# ─── 主入口 ────────────────────────────────────────────────────────────────

def main() -> int:
    print("=" * 70)
    print("Stage 47.13 · univer_api 验证（Facade symbol 查找）")
    print("=" * 70)

    # 先打印数据库大小
    api = UniverApiService()
    print(f"\nSymbol Database: {len(SYMBOL_DATABASE)} 个 curated symbol")
    categories = {}
    for s in SYMBOL_DATABASE:
        categories[s.category] = categories.get(s.category, 0) + 1
    print(f"按 category 分布: {dict(sorted(categories.items()))}")

    results = [
        test_find_by_keyword(),
        test_find_with_category_filter(),
        test_show_exact_symbol(),
        test_find_returns_multiple(),
        test_kinds_filter(),
        test_cross_category_symbols(),
    ]

    for r in results:
        status = "PASS" if r["ok"] else "FAIL"
        print(f"\n[{status}] {r['name']}")
        for k, v in r.items():
            if k not in ("ok", "name"):
                print(f"    {k}: {v}")

    print("\n" + "=" * 70)
    print(f"Stage 47.13 PASS: {sum(1 for r in results if r['ok'])}/{len(results)} 场景")
    print("=" * 70)

    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
