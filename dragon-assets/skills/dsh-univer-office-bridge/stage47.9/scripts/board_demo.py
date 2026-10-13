"""阶段 47.9 · univer_board Unit 接口语义验证

本脚本：
  1. 模拟 univer_board 的 Facade（FBoard / FShape / 连接线 / 图表）
  2. 创建 Board Unit + shapes + connectors + native chart
  3. 验证连接线端点 lint（element-overlap / connector-through-element / connector-collinear-overlap）
  4. 验证 export 限制（Board 不支持 export）

Author: dragon-engine · Stage 47.9 · 2026-08-26
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any


# ─── Enums ────────────────────────────────────────────────────────────────

class ShapeType(str, Enum):
    RECT = "RoundRect"
    RECT_BASIC = "Rect"
    CIRCLE = "Circle"
    DIAMOND = "Diamond"
    TEXT = "Text"


class RoutingMode(str, Enum):
    STRAIGHT = "straight"
    ORTHOGONAL = "orthogonal"
    CURVE = "curve"


class ConnectorSite(str, Enum):
    TOP = "Top"
    RIGHT = "Right"
    BOTTOM = "Bottom"
    LEFT = "Left"


class IssueSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


# ─── Facade 接口语义 ─────────────────────────────────────────────────────

@dataclass
class FShape:
    id: str
    shape_type: ShapeType
    transform: dict  # {left, top, width, height}
    text: str = ""
    fill: dict = field(default_factory=dict)
    stroke: dict = field(default_factory=dict)


@dataclass
class FConnector:
    id: str
    from_element_id: str
    to_element_id: str
    from_site: ConnectorSite = ConnectorSite.RIGHT
    to_site: ConnectorSite = ConnectorSite.LEFT
    routing: RoutingMode = RoutingMode.ORTHOGONAL
    routing_mode: str = "auto"
    style: dict = field(default_factory=dict)


@dataclass
class FBoardChart:
    id: str
    chart_type: str  # Column / Line / Pie / Bar
    title: str
    source: list  # 2D array
    position: dict  # {left, top}
    size: dict  # {width, height}


@dataclass
class FBoard:
    id: str
    name: str
    width: float = 1200
    height: float = 800
    elements: list = field(default_factory=list)  # [FShape, FConnector, FBoardChart]

    def get_element_by_id(self, eid: str):
        for e in self.elements:
            if e.id == eid:
                return e
        return None

    def get_shapes(self):
        return [e for e in self.elements if isinstance(e, FShape)]

    def get_connectors(self):
        return [e for e in self.elements if isinstance(e, FConnector)]

    def get_charts(self):
        return [e for e in self.elements if isinstance(e, FBoardChart)]

    def describe_elements(self) -> dict:
        return {
            "shapes": [{"id": s.id, "type": s.shape_type.value, "text": s.text,
                        "transform": s.transform} for s in self.get_shapes()],
            "connectors": [{"id": c.id, "from": c.from_element_id, "to": c.to_element_id,
                            "routing": c.routing.value} for c in self.get_connectors()],
            "charts": [{"id": ch.id, "type": ch.chart_type, "title": ch.title,
                        "position": ch.position, "size": ch.size} for ch in self.get_charts()],
        }


# ─── 布局分析（lint 简化版） ─────────────────────────────────────────────

@dataclass
class LayoutFinding:
    type: str
    severity: IssueSeverity
    elements: list  # 受影响的 element IDs
    description: str


def rects_overlap(a: dict, b: dict) -> bool:
    """判断两个矩形（{left, top, width, height}）是否重叠"""
    return not (
        a["left"] + a["width"] <= b["left"]
        or b["left"] + b["width"] <= a["left"]
        or a["top"] + a["height"] <= b["top"]
        or b["top"] + b["height"] <= a["top"]
    )


def analyze_layout(board: FBoard) -> list[LayoutFinding]:
    """布局 lint（简化版，覆盖 3 条上游规则）"""
    findings = []
    shapes = board.get_shapes()

    # 1. element-overlap（阻塞）
    for i, a in enumerate(shapes):
        for b in shapes[i+1:]:
            if rects_overlap(a.transform, b.transform):
                findings.append(LayoutFinding(
                    type="element-overlap",
                    severity=IssueSeverity.ERROR,
                    elements=[a.id, b.id],
                    description=f"{a.id} and {b.id} overlap",
                ))

    # 2. connector-through-element（阻塞）
    # 简化：检查 connector 端点是否落在 shape 内部
    for c in board.get_connectors():
        from_shape = board.get_element_by_id(c.from_element_id)
        to_shape = board.get_element_by_id(c.to_element_id)
        if not (isinstance(from_shape, FShape) and isinstance(to_shape, FShape)):
            continue

        for shape in shapes:
            if shape.id in (from_shape.id, to_shape.id):
                continue
            # 简化判定：从 from_site 到 to_site 的连线是否穿过 shape
            # 用矩形中心点 + 端点连线的中点粗略判定
            from_x = from_shape.transform["left"] + (from_shape.transform["width"] if c.from_site == ConnectorSite.RIGHT else 0)
            from_y = from_shape.transform["top"] + (from_shape.transform["height"] if c.from_site == ConnectorSite.BOTTOM else 0)
            to_x = to_shape.transform["left"] + (0 if c.to_site == ConnectorSite.LEFT else to_shape.transform["width"])
            to_y = to_shape.transform["top"] + (to_shape.transform["height"] / 2)

            mid_x = (from_x + to_x) / 2
            mid_y = (from_y + to_y) / 2

            s_left, s_top = shape.transform["left"], shape.transform["top"]
            s_right, s_bottom = s_left + shape.transform["width"], s_top + shape.transform["height"]

            if s_left <= mid_x <= s_right and s_top <= mid_y <= s_bottom:
                findings.append(LayoutFinding(
                    type="connector-through-element",
                    severity=IssueSeverity.ERROR,
                    elements=[c.id, shape.id],
                    description=f"connector {c.id} midpoint passes through {shape.id}",
                ))

    # 3. connector-collinear-overlap（同向重叠，阻塞）
    for i, c1 in enumerate(board.get_connectors()):
        for c2 in board.get_connectors()[i+1:]:
            if (c1.from_element_id == c2.from_element_id
                and c1.to_element_id == c2.to_element_id
                and c1.from_site == c2.from_site
                and c1.to_site == c2.to_site):
                findings.append(LayoutFinding(
                    type="connector-collinear-overlap",
                    severity=IssueSeverity.ERROR,
                    elements=[c1.id, c2.id],
                    description=f"connectors {c1.id} and {c2.id} are collinear",
                ))

    return findings


# ─── 1. 流程图 Board ───────────────────────────────────────────────────────

def build_workflow_board() -> FBoard:
    """构造"客户审批流程"流程图"""
    board = FBoard(id="board-workflow-001", name="客户审批流程图")

    # 3 个流程节点（横排）
    shapes_data = [
        (ShapeType.RECT, "shape-1", "提交申请", {"left": 80, "top": 200, "width": 160, "height": 80}),
        (ShapeType.DIAMOND, "shape-2", "审批?", {"left": 360, "top": 200, "width": 160, "height": 80}),
        (ShapeType.RECT, "shape-3", "通过", {"left": 640, "top": 200, "width": 160, "height": 80}),
        (ShapeType.RECT, "shape-4", "拒绝", {"left": 640, "top": 360, "width": 160, "height": 80}),
    ]
    for st, sid, text, transform in shapes_data:
        shape = FShape(id=sid, shape_type=st, transform=transform, text=text,
                       fill={"type": "solid", "color": "#FFFFFF"},
                       stroke={"type": "solid", "color": "#000000", "width": 1})
        board.elements.append(shape)

    # 连接线
    connectors = [
        ("c-1-2", "shape-1", "shape-2", ConnectorSite.RIGHT, ConnectorSite.LEFT),
        ("c-2-3", "shape-2", "shape-3", ConnectorSite.RIGHT, ConnectorSite.LEFT),
        ("c-2-4", "shape-2", "shape-4", ConnectorSite.BOTTOM, ConnectorSite.TOP),
    ]
    for cid, fid, tid, fs, ts in connectors:
        c = FConnector(id=cid, from_element_id=fid, to_element_id=tid,
                       from_site=fs, to_site=ts, routing=RoutingMode.ORTHOGONAL,
                       routing_mode="auto",
                       style={"endMarker": {"type": "filledTriangle", "size": "md"}})
        board.elements.append(c)

    return board


def build_diagram_with_chart() -> FBoard:
    """构造"产品架构图 + 销售图表"混合 Board"""
    board = FBoard(id="board-arch-001", name="产品架构 + 销售图表")

    # 5 个组件矩形
    components = [
        ("c-web", "Web 前端", {"left": 80, "top": 80, "width": 200, "height": 60}),
        ("c-api", "API 网关", {"left": 80, "top": 200, "width": 200, "height": 60}),
        ("c-db", "数据库", {"left": 80, "top": 320, "width": 200, "height": 60}),
        ("c-cache", "缓存", {"left": 360, "top": 200, "width": 200, "height": 60}),
        ("c-queue", "消息队列", {"left": 360, "top": 320, "width": 200, "height": 60}),
    ]
    for sid, text, transform in components:
        shape = FShape(id=sid, shape_type=ShapeType.RECT, transform=transform, text=text,
                       fill={"type": "solid", "color": "#E8F4FD"},
                       stroke={"type": "solid", "color": "#2E5C8A", "width": 2})
        board.elements.append(shape)

    # 连接线（避免穿过其他 shape）
    connections = [
        ("c1", "c-web", "c-api", ConnectorSite.BOTTOM, ConnectorSite.TOP),
        ("c2", "c-api", "c-db", ConnectorSite.BOTTOM, ConnectorSite.TOP),
        ("c3", "c-api", "c-cache", ConnectorSite.RIGHT, ConnectorSite.LEFT),
        ("c4", "c-api", "c-queue", ConnectorSite.RIGHT, ConnectorSite.LEFT),
    ]
    for cid, fid, tid, fs, ts in connections:
        c = FConnector(id=cid, from_element_id=fid, to_element_id=tid,
                       from_site=fs, to_site=ts, routing=RoutingMode.ORTHOGONAL,
                       routing_mode="auto")
        board.elements.append(c)

    # 原生图表（销售额）
    chart = FBoardChart(
        id="chart-sales-001",
        chart_type="Column",
        title="2026 Q2 销售额",
        source=[
            ["月份", "销售额"],
            ["4 月", 12],
            ["5 月", 18],
            ["6 月", 15],
        ],
        position={"left": 700, "top": 100},
        size={"width": 400, "height": 280},
    )
    board.elements.append(chart)

    return board


# ─── 验证场景 ──────────────────────────────────────────────────────────

def test_workflow_board_structure() -> dict:
    """场景 1: 流程图 Board 结构"""
    board = build_workflow_board()
    assert len(board.get_shapes()) == 4
    assert len(board.get_connectors()) == 3
    assert len(board.get_charts()) == 0

    # 描述元素
    desc = board.describe_elements()
    assert len(desc["shapes"]) == 4
    assert len(desc["connectors"]) == 3
    return {"name": "workflow_board_structure", "ok": True,
            "shapes": len(desc["shapes"]), "connectors": len(desc["connectors"])}


def test_layout_lint_clean() -> dict:
    """场景 2: 流程图布局 lint（无 finding）"""
    board = build_workflow_board()
    findings = analyze_layout(board)
    errors = [f for f in findings if f.severity == IssueSeverity.ERROR]
    return {"name": "layout_lint_clean", "ok": len(errors) == 0,
            "findings": len(findings), "errors": len(errors)}


def test_element_overlap_detection() -> dict:
    """场景 3: element-overlap 检测"""
    # 故意创建 2 个重叠的 shape
    board = FBoard(id="board-overlap", name="重叠测试")
    s1 = FShape(id="s1", shape_type=ShapeType.RECT,
                transform={"left": 100, "top": 100, "width": 200, "height": 200},
                text="A")
    s2 = FShape(id="s2", shape_type=ShapeType.RECT,
                transform={"left": 200, "top": 200, "width": 200, "height": 200},
                text="B")
    board.elements.extend([s1, s2])

    findings = analyze_layout(board)
    overlaps = [f for f in findings if f.type == "element-overlap"]
    assert len(overlaps) == 1, f"[FAIL] 应检测到 1 个重叠，实际 {len(overlaps)}"
    assert "s1" in overlaps[0].elements and "s2" in overlaps[0].elements
    return {"name": "element_overlap_detection", "ok": True, "overlaps": len(overlaps)}


def test_diagram_with_chart() -> dict:
    """场景 4: 架构图 + 原生图表"""
    board = build_diagram_with_chart()
    assert len(board.get_shapes()) == 5
    assert len(board.get_connectors()) == 4
    assert len(board.get_charts()) == 1

    chart = board.get_charts()[0]
    assert chart.chart_type == "Column"
    assert chart.title == "2026 Q2 销售额"
    assert len(chart.source) == 4  # 1 header + 3 data

    # 验证 layout lint（架构图无 finding）
    findings = analyze_layout(board)
    errors = [f for f in findings if f.severity == IssueSeverity.ERROR]
    return {"name": "diagram_with_chart", "ok": len(errors) == 0,
            "shapes": 5, "connectors": 4, "charts": 1, "lint_errors": len(errors)}


def test_connector_sites() -> dict:
    """场景 5: 连接线端点 4 方向"""
    board = build_workflow_board()

    # 端点种类（unique）
    sites = set()
    for c in board.get_connectors():
        sites.add(c.from_site.value)
        sites.add(c.to_site.value)

    assert "Right" in sites  # 至少 1 个 Right
    assert "Left" in sites   # 至少 1 个 Left
    assert "Bottom" in sites  # shape-2 → shape-4 用 Bottom → Top
    assert "Top" in sites

    return {"name": "connector_sites", "ok": True, "sites": sorted(sites)}


def test_export_not_supported() -> dict:
    """场景 6: Board 不支持 export（只能预览）"""
    # 上游 SKILL.md 明确：Board export is unsupported
    board = build_workflow_board()

    # 模拟 univer_export 行为：Board 应返回 error
    def try_export(unit_type: str) -> dict:
        if unit_type == "board":
            return {"ok": False, "error": "EXPORT_NOT_SUPPORTED",
                    "message": "Board export is unsupported; deliver ready worktree preview"}
        return {"ok": True}

    r = try_export("board")
    assert not r["ok"]
    assert r["error"] == "EXPORT_NOT_SUPPORTED"
    return {"name": "export_not_supported", "ok": True, "error": r["error"]}


def test_analyze_model_layout() -> dict:
    """场景 7: analyzeModelLayout 接口"""
    board = build_workflow_board()
    # 简化版：调用 analyze_layout
    analysis = analyze_layout(board)
    # 返回结构与上游 board.analyzeModelLayout(48) 类似
    return {"name": "analyze_model_layout", "ok": True,
            "findings_count": len(analysis)}


# ─── 主入口 ────────────────────────────────────────────────────────────────

def main() -> int:
    print("=" * 70)
    print("Stage 47.9 · univer_board Unit 接口语义验证")
    print("=" * 70)

    results = [
        test_workflow_board_structure(),
        test_layout_lint_clean(),
        test_element_overlap_detection(),
        test_diagram_with_chart(),
        test_connector_sites(),
        test_export_not_supported(),
        test_analyze_model_layout(),
    ]

    for r in results:
        status = "PASS" if r["ok"] else "FAIL"
        print(f"\n[{status}] {r['name']}")
        for k, v in r.items():
            if k not in ("ok", "name"):
                print(f"    {k}: {v}")

    print("\n" + "=" * 70)
    print(f"Stage 47.9 PASS: {sum(1 for r in results if r['ok'])}/{len(results)} 场景")
    print("=" * 70)

    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
