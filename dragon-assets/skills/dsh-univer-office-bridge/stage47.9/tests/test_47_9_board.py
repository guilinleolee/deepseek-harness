"""test_47_9_board · 7 个 univer_board 场景全部 PASS"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from board_demo import (
    test_workflow_board_structure,
    test_layout_lint_clean,
    test_element_overlap_detection,
    test_diagram_with_chart,
    test_connector_sites,
    test_export_not_supported,
    test_analyze_model_layout,
    build_workflow_board,
    build_diagram_with_chart,
    analyze_layout,
    IssueSeverity,
)


def test_47_9_board():
    # 场景 1: 流程图结构
    r1 = test_workflow_board_structure()
    assert r1["ok"]
    assert r1["shapes"] == 4
    assert r1["connectors"] == 3
    print(f"[PASS] workflow_board: 4 shapes + 3 connectors")

    # 场景 2: 流程图 lint 干净
    r2 = test_layout_lint_clean()
    assert r2["ok"]
    assert r2["errors"] == 0
    print(f"[PASS] layout_lint: 流程图 0 errors")

    # 场景 3: element-overlap 检测
    r3 = test_element_overlap_detection()
    assert r3["ok"]
    assert r3["overlaps"] == 1
    print(f"[PASS] element_overlap: 检测 1 个重叠")

    # 场景 4: 架构图 + 图表
    r4 = test_diagram_with_chart()
    assert r4["ok"]
    assert r4["shapes"] == 5 and r4["connectors"] == 4 and r4["charts"] == 1
    assert r4["lint_errors"] == 0
    print(f"[PASS] diagram_with_chart: 5+4+1 = {r4['shapes']+r4['connectors']+r4['charts']} elements, 0 lint errors")

    # 场景 5: 连接线端点 4 方向
    r5 = test_connector_sites()
    assert r5["ok"]
    assert set(r5["sites"]) == {"Right", "Left", "Bottom", "Top"}
    print(f"[PASS] connector_sites: 4 方向全覆盖 {r5['sites']}")

    # 场景 6: Board 不支持 export
    r6 = test_export_not_supported()
    assert r6["ok"]
    assert r6["error"] == "EXPORT_NOT_SUPPORTED"
    print(f"[PASS] export_not_supported: Board 禁止 export")

    # 场景 7: analyzeModelLayout
    r7 = test_analyze_model_layout()
    assert r7["ok"]
    print(f"[PASS] analyze_model_layout: 返回 {r7['findings_count']} findings")

    # 边界 case：复杂多 shape 场景
    print("\n--- 边界 case ---")
    # 创建 1 个 shape + 1 个 connector（同源同宿）
    board = build_workflow_board()
    from board_demo import FConnector, ConnectorSite, RoutingMode
    duplicate = FConnector(id="c-dup", from_element_id="shape-1",
                          to_element_id="shape-2", from_site=ConnectorSite.RIGHT,
                          to_site=ConnectorSite.LEFT, routing=RoutingMode.ORTHOGONAL)
    board.elements.append(duplicate)

    findings = analyze_layout(board)
    collinear = [f for f in findings if f.type == "connector-collinear-overlap"]
    assert len(collinear) >= 1, f"[FAIL] 应检测到 collinear-overlap，实际 {len(collinear)}"
    print(f"[PASS] collinear-overlap: 检测到 {len(collinear)} 个重复连接线")


# 独立 test function
test_workflow_board_structure.__test__ = True
test_layout_lint_clean.__test__ = True
test_element_overlap_detection.__test__ = True
test_diagram_with_chart.__test__ = True
test_connector_sites.__test__ = True
test_export_not_supported.__test__ = True
test_analyze_model_layout.__test__ = True
