"""test_47_13_api · 6 个 univer_api 场景 + 1 个 db integrity"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from api_lookup import (
    UniverApiService,
    SYMBOL_DATABASE,
    test_find_by_keyword,
    test_find_with_category_filter,
    test_show_exact_symbol,
    test_find_returns_multiple,
    test_kinds_filter,
    test_cross_category_symbols,
)


def test_47_13_api():
    # 场景 1: find setValue → FWorkbook.setValue
    r1 = test_find_by_keyword()
    assert r1["ok"]
    assert r1["top_result"] == "FWorkbook.setValue"
    # score: 完全匹配 label +10; substring 匹配 +5
    # 因为我们 label 含父类前缀（如 FWorkbook.setValue），substring 只能拿到 5
    assert r1["score"] >= 5
    print(f"[PASS] find_by_keyword: top={r1['top_result']} score={r1['score']}")

    # 场景 2: find + category 过滤
    r2 = test_find_with_category_filter()
    assert r2["ok"]
    assert r2["sheet_count"] > 0
    assert r2["cross_count"] >= 3
    print(f"[PASS] find_category: sheet={r2['sheet_count']}, cross={r2['cross_count']}")

    # 场景 3: show 精确符号
    r3 = test_show_exact_symbol()
    assert r3["ok"]
    assert r3["setValue_returns"] == "boolean"
    assert r3["params_count"] == 1
    print(f"[PASS] show_exact: setValue → {r3['setValue_returns']}, {r3['params_count']} params")

    # 场景 4: find 返回多个
    r4 = test_find_returns_multiple()
    assert r4["ok"]
    assert r4["total_matches"] >= 3
    print(f"[PASS] find_multiple: {r4['total_matches']} matches, top3={r4['top3']}")

    # 场景 5: kinds 过滤
    r5 = test_kinds_filter()
    assert r5["ok"]
    assert r5["classes_count"] >= 5  # FWorkbook / FDocument / FPresentation / FBase / FUniver
    assert r5["methods_count"] >= 3  # set 系列至少 3 个 method（FRange.setFormula / FWorkbook.setValue / 等）
    print(f"[PASS] kinds_filter: classes={r5['classes_count']}, methods={r5['methods_count']}")

    # 聚合测试通过

    # 场景 6: cross-category symbols
    r6 = test_cross_category_symbols()
    assert r6["ok"]
    assert r6["FFormula_count"] >= 3
    print(f"[PASS] cross_category: {r6['FFormula_count']} FFormula.* methods")


# 独立 test function 让 pytest 单测收集
test_find_by_keyword.__test__ = True
test_find_with_category_filter.__test__ = True
test_show_exact_symbol.__test__ = True
test_find_returns_multiple.__test__ = True
test_kinds_filter.__test__ = True
test_cross_category_symbols.__test__ = True


def test_database_integrity():
    """数据库完整性：每个 label 唯一 + 至少 18 个 symbol + 6 category 覆盖"""
    db = SYMBOL_DATABASE

    # label 唯一
    labels = [s.label for s in db]
    duplicates = [l for l in labels if labels.count(l) > 1]
    assert not duplicates, f"[FAIL] 有重复 label: {duplicates}"

    # >= 18 个 symbol
    assert len(db) >= 18, f"[FAIL] symbol 数量 {len(db)} < 18"

    # 6 category 覆盖（sheet / doc / slide / base / cross / embed）
    categories = {s.category for s in db}
    expected = {"sheet", "doc", "slide", "base", "cross", "embed"}
    assert categories >= expected, f"[FAIL] category 覆盖不全: 差 {expected - categories}"

    # 每 category ≥ 2
    from collections import Counter
    cat_count = Counter(s.category for s in db)
    for cat, count in cat_count.items():
        assert count >= 2, f"[FAIL] category {cat} 仅 {count} 个"

    # 每 kind 分布合理
    kind_count = Counter(s.kind for s in db)
    assert kind_count.get("class", 0) >= 5, f"[FAIL] class 不足: {kind_count}"

    print(f"[PASS] db_integrity: {len(db)} symbols · 6 categories · all unique labels")
