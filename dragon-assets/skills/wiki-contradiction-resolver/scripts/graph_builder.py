#!/usr/bin/env python3
"""
Wiki 矛盾图谱构建器
将矛盾检测结果可视化为图结构，支持多种输出格式

Usage:
    python3 graph_builder.py --build
    python3 graph_builder.py --visualize
    python3 graph_builder.py --stats
"""

import argparse
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

WIKI_DIR = Path.home() / ".claude" / "wiki"
GRAPH_DIR = Path.home() / ".claude" / "wiki_contradiction_cache"
GRAPH_FILE = GRAPH_DIR / "contradiction_graph.json"
CACHE_FILE = GRAPH_DIR / "contradictions.json"


@dataclass
class GraphNode:
    """图谱节点"""
    id: str
    title: str
    path: Path
    type: str  # normal, disputed, contradictory, resolved
    contradiction_count: int = 0
    linked_notes: list = field(default_factory=list)
    tags: list = field(default_factory=list)
    last_updated: str = ""


@dataclass
class GraphEdge:
    """图谱边（矛盾关系）"""
    source: str
    target: str
    type: str  # entity_relation, temporal, causal, semantic
    confidence: float
    severity: str  # high, medium, low
    resolved: bool = False


@dataclass
class ContradictionGraph:
    """完整矛盾图谱"""
    nodes: dict = field(default_factory=dict)
    edges: list = field(default_factory=list)
    stats: dict = field(default_factory=dict)
    generated_at: str = ""


class GraphBuilder:
    """矛盾图谱构建器"""

    # 节点颜色映射
    NODE_COLORS = {
        "normal": "#22c55e",       # green
        "disputed": "#eab308",    # yellow
        "contradictory": "#ef4444", # red
        "resolved": "#3b82f6",    # blue
    }

    # 边类型颜色
    EDGE_COLORS = {
        "entity_relation": "#8b5cf6",  # purple
        "temporal": "#f97316",         # orange
        "causal": "#06b6d4",           # cyan
        "semantic": "#ec4899",          # pink
    }

    # 严重程度阈值
    SEVERITY_THRESHOLDS = {
        "high": 0.8,
        "medium": 0.5,
        "low": 0.4,
    }

    def __init__(self, wiki_dir: Optional[Path] = None):
        self.wiki_dir = wiki_dir or WIKI_DIR
        self.graph_dir = GRAPH_DIR
        self.graph_dir.mkdir(parents=True, exist_ok=True)

    def _load_notes(self) -> list[dict]:
        """加载所有笔记"""
        if not self.wiki_dir.exists():
            return []

        notes = []
        for md_file in self.wiki_dir.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                title = self._extract_title(content, md_file.stem)
                notes.append({
                    "id": md_file.stem,
                    "title": title,
                    "path": md_file,
                    "content": content,
                })
            except Exception:
                continue
        return notes

    def _extract_title(self, content: str, filename: str) -> str:
        """提取笔记标题"""
        if content.startswith("# "):
            return content.split("\n")[0][2:].strip()
        return filename.replace("-", " ").replace("_", " ").title()

    def _load_contradictions(self) -> list[dict]:
        """加载矛盾数据"""
        if CACHE_FILE.exists():
            try:
                data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
                return data.get("contradictions", [])
            except Exception:
                pass
        return []

    def _determine_severity(self, confidence: float) -> str:
        """根据置信度确定严重程度"""
        if confidence >= self.SEVERITY_THRESHOLDS["high"]:
            return "high"
        elif confidence >= self.SEVERITY_THRESHOLDS["medium"]:
            return "medium"
        return "low"

    def _determine_node_type(self, contradiction_count: int, avg_confidence: float) -> str:
        """根据矛盾数量和平均置信度确定节点类型"""
        if contradiction_count == 0:
            return "normal"
        if avg_confidence >= 0.8:
            return "contradictory"
        elif avg_confidence >= 0.5:
            return "disputed"
        return "disputed"

    def build_graph(self, contradictions: Optional[list] = None) -> ContradictionGraph:
        """构建矛盾图谱"""
        # 加载笔记
        notes = self._load_notes()
        note_map = {note["id"]: note for note in notes}

        # 加载矛盾
        if contradictions is None:
            contradictions = self._load_contradictions()

        # 统计每个笔记的矛盾数
        note_contradictions: dict[str, list] = {note["id"]: [] for note in notes}
        edges = []

        for c in contradictions:
            if isinstance(c, dict):
                node_a = c.get("node_a", "")
                node_b = c.get("node_b", "")
                confidence = c.get("confidence", 0.5)
            else:
                node_a = c.node_a
                node_b = c.node_b
                confidence = c.confidence

            if node_a in note_contradictions:
                note_contradictions[node_a].append(c)
            if node_b in note_contradictions:
                note_contradictions[node_b].append(c)

            # 创建边
            edge_type = c.get("type", "entity_relation") if isinstance(c, dict) else c.type
            severity = self._determine_severity(confidence)

            edges.append(GraphEdge(
                source=node_a,
                target=node_b,
                type=edge_type,
                confidence=confidence,
                severity=severity,
            ))

        # 构建节点
        nodes = {}
        for note in notes:
            note_id = note["id"]
            note_cons = note_contradictions.get(note_id, [])

            if note_cons:
                avg_conf = sum(
                    (c.get("confidence", 0.5) if isinstance(c, dict) else c.confidence
                    for c in note_cons
                ) / len(note_cons)
            else:
                avg_conf = 0.0

            node_type = self._determine_node_type(len(note_cons), avg_conf)

            # 获取关联笔记
            linked = []
            for edge in edges:
                if edge.source == note_id:
                    linked.append(edge.target)
                elif edge.target == note_id:
                    linked.append(edge.source)
            linked = list(set(linked))

            nodes[note_id] = GraphNode(
                id=note_id,
                title=note["title"],
                path=note["path"],
                type=node_type,
                contradiction_count=len(note_cons),
                linked_notes=linked,
                last_updated=datetime.now().isoformat(),
            )

        # 计算统计
        by_type = {}
        by_severity = {"high": 0, "medium": 0, "low": 0}
        by_node_type = {"normal": 0, "disputed": 0, "contradictory": 0, "resolved": 0}

        for edge in edges:
            by_type[edge.type] = by_type.get(edge.type, 0) + 1
            by_severity[edge.severity] += 1

        for node in nodes.values():
            by_node_type[node.type] += 1

        stats = {
            "total_notes": len(notes),
            "notes_with_contradictions": len([n for n in nodes.values() if n.contradiction_count > 0]),
            "total_contradictions": len(edges),
            "by_type": by_type,
            "by_severity": by_severity,
            "by_node_type": by_node_type,
        }

        return ContradictionGraph(
            nodes=nodes,
            edges=edges,
            stats=stats,
            generated_at=datetime.now().isoformat(),
        )

    def export_json(self, graph: ContradictionGraph) -> dict:
        """导出JSON格式"""
        return {
            "generated_at": graph.generated_at,
            "stats": graph.stats,
            "nodes": {
                node_id: {
                    "id": node.id,
                    "title": node.title,
                    "path": str(node.path),
                    "type": node.type,
                    "color": self.NODE_COLORS[node.type],
                    "contradiction_count": node.contradiction_count,
                    "linked_notes": node.linked_notes,
                    "last_updated": node.last_updated,
                }
                for node_id, node in graph.nodes.items()
            },
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "type": edge.type,
                    "color": self.EDGE_COLORS[edge.type],
                    "confidence": edge.confidence,
                    "severity": edge.severity,
                }
                for edge in graph.edges
            ],
        }

    def export_cytoscape(self, graph: ContradictionGraph) -> dict:
        """导出Cytoscape.js格式"""
        elements = {"nodes": [], "edges": []}

        for node in graph.nodes.values():
            elements["nodes"].append({
                "data": {
                    "id": node.id,
                    "label": node.title,
                    "color": self.NODE_COLORS[node.type],
                    "type": node.type,
                    "contradictions": node.contradiction_count,
                }
            })

        for edge in graph.edges:
            elements["edges"].append({
                "data": {
                    "id": f"{edge.source}-{edge.target}",
                    "source": edge.source,
                    "target": edge.target,
                    "label": edge.type,
                    "color": self.EDGE_COLORS[edge.type],
                    "confidence": edge.confidence,
                }
            })

        return elements

    def export_d3_force(self, graph: ContradictionGraph) -> dict:
        """导出D3.js力导向图格式"""
        nodes = []
        for node in graph.nodes.values():
            nodes.append({
                "id": node.id,
                "name": node.title,
                "group": node.type,
                "count": node.contradiction_count,
                "color": self.NODE_COLORS[node.type],
            })

        links = []
        for edge in graph.edges:
            links.append({
                "source": edge.source,
                "target": edge.target,
                "type": edge.type,
                "value": edge.confidence,
                "color": self.EDGE_COLORS[edge.type],
            })

        return {"nodes": nodes, "links": links}

    def export_graphml(self, graph: ContradictionGraph) -> str:
        """导出GraphML格式"""
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
            '  <key id="label" for="node" attr.name="label" attr.type="string"/>',
            '  <key id="color" for="node" attr.name="color" attr.type="string"/>',
            '  <key id="type" for="node" attr.name="nodeType" attr.type="string"/>',
            '  <key id="contradictions" for="node" attr.name="contradictionCount" attr.type="int"/>',
            '  <key id="edge_color" for="edge" attr.name="color" attr.type="string"/>',
            '  <key id="confidence" for="edge" attr.name="confidence" attr.type="double"/>',
            '  <graph edgedefault="undirected">',
        ]

        for node in graph.nodes.values():
            lines.append(
                f'    <node id="{node.id}">'
            )
            lines.append(f'      <data key="label">{node.title}</data>')
            lines.append(f'      <data key="color">{self.NODE_COLORS[node.type]}</data>')
            lines.append(f'      <data key="type">{node.type}</data>')
            lines.append(f'      <data key="contradictions">{node.contradiction_count}</data>')
            lines.append('    </node>')

        for edge in graph.edges:
            lines.append(
                f'    <edge source="{edge.source}" target="{edge.target}">'
            )
            lines.append(f'      <data key="edge_color">{self.EDGE_COLORS[edge.type]}</data>')
            lines.append(f'      <data key="confidence">{edge.confidence}</data>')
            lines.append('    </edge>')

        lines.extend(['  </graph>', '</graphml>'])
        return '\n'.join(lines)

    def export_html_visualization(self, graph: ContradictionGraph, output_path: Optional[Path] = None) -> Path:
        """导出交互式HTML可视化"""
        if output_path is None:
            output_path = self.graph_dir / "contradiction_graph.html"

        d3_data = self.export_d3_force(graph)

        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wiki 矛盾图谱</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        #container {{
            display: flex;
            height: 100vh;
        }}
        #sidebar {{
            width: 280px;
            background: #f8fafc;
            border-right: 1px solid #e2e8f0;
            overflow-y: auto;
            padding: 16px;
        }}
        #graph {{
            flex: 1;
            background: #1e293b;
        }}
        .stat-card {{
            background: white;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .stat-label {{ color: #64748b; font-size: 12px; margin-bottom: 4px; }}
        .stat-value {{ font-size: 24px; font-weight: 600; color: #1e293b; }}
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 12px;
            color: #475569;
        }}
        .legend-color {{
            width: 12px;
            height: 12px;
            border-radius: 3px;
        }}
        #stats {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-top: 16px;
        }}
        .mini-stat {{
            background: white;
            padding: 8px;
            border-radius: 6px;
            text-align: center;
        }}
        .mini-stat-value {{ font-size: 18px; font-weight: 600; }}
        .mini-stat-label {{ font-size: 10px; color: #64748b; }}
        .node-info {{
            position: absolute;
            background: white;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: none;
            z-index: 100;
            max-width: 280px;
        }}
        .node-info h4 {{ margin-bottom: 8px; color: #1e293b; }}
        .node-info p {{ font-size: 13px; color: #64748b; margin: 4px 0; }}
        .node-info .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            margin-right: 4px;
        }}
        .node-info .badge.high {{ background: #fef2f2; color: #dc2626; }}
        .node-info .badge.medium {{ background: #fefce8; color: #ca8a04; }}
        .node-info .badge.low {{ background: #f0fdf4; color: #16a34a; }}
    </style>
</head>
<body>
    <div id="container">
        <div id="sidebar">
            <h2 style="font-size: 16px; margin-bottom: 16px;">Wiki 矛盾图谱</h2>

            <div class="stat-card">
                <div class="stat-label">总笔记数</div>
                <div class="stat-value">{graph.stats.get("total_notes", 0)}</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">矛盾数量</div>
                <div class="stat-value">{graph.stats.get("total_contradictions", 0)}</div>
            </div>

            <div id="stats">
                <div class="mini-stat">
                    <div class="mini-stat-value" style="color: #ef4444;">{graph.stats.get("by_node_type", {{}}).get("contradictory", 0)}</div>
                    <div class="mini-stat-label">矛盾节点</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-stat-value" style="color: #eab308;">{graph.stats.get("by_node_type", {{}}).get("disputed", 0)}</div>
                    <div class="mini-stat-label">争议节点</div>
                </div>
            </div>

            <h3 style="font-size: 13px; margin: 16px 0 8px; color: #475569;">节点类型</h3>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: {self.NODE_COLORS["normal"]};"></div>
                    <span>正常</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: {self.NODE_COLORS["disputed"]};"></div>
                    <span>争议</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: {self.NODE_COLORS["contradictory"]};"></div>
                    <span>矛盾</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: {self.NODE_COLORS["resolved"]};"></div>
                    <span>已解决</span>
                </div>
            </div>

            <h3 style="font-size: 13px; margin: 16px 0 8px; color: #475569;">矛盾类型</h3>
            <div class="legend">
                <div class="legend-item">
                    <div class="legend-color" style="background: {self.EDGE_COLORS["entity_relation"]};"></div>
                    <span>实体</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: {self.EDGE_COLORS["temporal"]};"></div>
                    <span>时序</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: {self.EDGE_COLORS["causal"]};"></div>
                    <span>因果</span>
                </div>
                <div class="legend-item">
                    <div class="legend-color" style="background: {self.EDGE_COLORS["semantic"]};"></div>
                    <span>语义</span>
                </div>
            </div>

            <p style="font-size: 11px; color: #94a3b8; margin-top: 24px;">
                生成时间: {graph.generated_at[:19].replace("T", " ")}
            </p>
        </div>
        <div id="graph"></div>
    </div>

    <div class="node-info" id="nodeInfo"></div>

    <script>
        const data = {json.dumps(d3_data)};

        const width = document.getElementById("graph").clientWidth;
        const height = document.getElementById("graph").clientHeight;

        const svg = d3.select("#graph")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        // Zoom behavior
        const g = svg.append("g");
        svg.call(d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => g.attr("transform", event.transform)));

        // Arrow marker
        svg.append("defs").selectAll("marker")
            .data(["arrow"])
            .join("marker")
            .attr("id", d => d)
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 20)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("fill", "#999")
            .attr("d", "M0,-5L10,0L0,5");

        // Simulation
        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(30));

        // Links
        const link = g.append("g")
            .selectAll("line")
            .data(data.links)
            .join("line")
            .attr("stroke", d => d.color)
            .attr("stroke-opacity", 0.6)
            .attr("stroke-width", d => d.value * 2);

        // Nodes
        const node = g.append("g")
            .selectAll("g")
            .data(data.nodes)
            .join("g")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        node.append("circle")
            .attr("r", d => 8 + d.count * 2)
            .attr("fill", d => d.color)
            .attr("stroke", "#fff")
            .attr("stroke-width", 2)
            .on("mouseover", showNodeInfo)
            .on("mouseout", hideNodeInfo);

        node.append("text")
            .text(d => d.name.substring(0, 20))
            .attr("x", 12)
            .attr("y", 4)
            .attr("fill", "#e2e8f0")
            .attr("font-size", "11px");

        // Simulation update
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});

        function dragstarted(event) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }}

        function dragged(event) {{
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }}

        function dragended(event) {{
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }}

        function showNodeInfo(event, d) {{
            const info = document.getElementById("nodeInfo");
            const typeLabels = {{"normal": "正常", "disputed": "争议", "contradictory": "矛盾", "resolved": "已解决"}};
            const typeColors = {{"normal": "green", "disputed": "yellow", "contradictory": "red", "resolved": "blue"}};

            info.innerHTML = `
                <h4>${{d.name}}</h4>
                <p>ID: ${{d.id}}</p>
                <p>类型: <span class="badge ${{typeColors[d.group]}}">${{typeLabels[d.group]}}</span></p>
                <p>矛盾数: ${{d.count}}</p>
            `;
            info.style.display = "block";
            info.style.left = (event.pageX + 10) + "px";
            info.style.top = (event.pageY + 10) + "px";
        }}

        function hideNodeInfo() {{
            document.getElementById("nodeInfo").style.display = "none";
        }}
    </script>
</body>
</html>'''

        output_path.write_text(html, encoding="utf-8")
        return output_path

    def save_graph(self, graph: ContradictionGraph):
        """保存图谱数据"""
        data = self.export_json(graph)
        GRAPH_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def get_stats(self, graph: ContradictionGraph) -> str:
        """生成统计报告"""
        stats = graph.stats
        by_type = stats.get("by_type", {})
        by_node = stats.get("by_node_type", {})

        lines = [
            "=" * 50,
            " Wiki 矛盾图谱统计报告",
            "=" * 50,
            "",
            f"生成时间: {graph.generated_at[:19].replace('T', ' ')}",
            "",
            f"📊 整体统计:",
            f"   笔记总数: {stats.get('total_notes', 0)}",
            f"   有矛盾的笔记: {stats.get('notes_with_contradictions', 0)}",
            f"   矛盾总数: {stats.get('total_contradictions', 0)}",
            "",
            f"🔴 按节点类型:",
            f"   矛盾节点: {by_node.get('contradictory', 0)}",
            f"   争议节点: {by_node.get('disputed', 0)}",
            f"   正常节点: {by_node.get('normal', 0)}",
            f"   已解决: {by_node.get('resolved', 0)}",
            "",
            f"🔗 按矛盾类型:",
        ]

        type_names = {
            "entity_relation": "实体关系",
            "temporal": "时序",
            "causal": "因果",
            "semantic": "语义",
        }
        for t, count in by_type.items():
            name = type_names.get(t, t)
            lines.append(f"   {name}: {count}")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Wiki 矛盾图谱构建")
    parser.add_argument("--build", action="store_true", help="构建图谱")
    parser.add_argument("--visualize", action="store_true", help="生成HTML可视化")
    parser.add_argument("--stats", action="store_true", help="显示统计")
    parser.add_argument("--format", choices=["json", "cytoscape", "graphml", "d3"],
                       default="json", help="导出格式")

    args = parser.parse_args()

    builder = GraphBuilder()

    if args.build or args.visualize or args.stats or not any([args.build, args.visualize, args.stats]):
        graph = builder.build_graph()
        builder.save_graph(graph)

        if args.stats:
            print(builder.get_stats(graph))

        if args.visualize or not any([args.build, args.visualize, args.stats]):
            output_path = builder.export_html_visualization(graph)
            print(f"\n可视化已保存: {output_path}")

        if args.format and args.format != "json":
            if args.format == "cytoscape":
                data = builder.export_cytoscape(graph)
            elif args.format == "graphml":
                data = builder.export_graphml(graph)
            elif args.format == "d3":
                data = builder.export_d3_force(graph)

            if isinstance(data, dict):
                print(json.dumps(data, ensure_ascii=False, indent=2))
            else:
                print(data)

        if args.build:
            print(builder.get_stats(graph))

    parser.print_help()


if __name__ == "__main__":
    main()
