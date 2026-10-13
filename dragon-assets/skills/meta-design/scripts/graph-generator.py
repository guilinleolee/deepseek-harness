#!/usr/bin/env python3
"""
Meta关系图生成器 (Meta Relationship Graph Generator)

基于元的身份定义和依赖关系，生成可视化的依赖图谱。
支持多种格式输出：Mermaid、Graphviz DOT、JSON结构化数据。

用法:
    python graph-generator.py <meta_id> [--input input.json] [--output graph.md]
    python graph-generator.py <meta_id> --format mermaid --full
    python graph-generator.py <meta_id> --format dot --output graph.dot
"""

import json
import sys
import argparse
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Set
from datetime import datetime
from enum import Enum


class OutputFormat(Enum):
    """输出格式枚举"""
    MERMAID = "mermaid"
    DOT = "dot"
    JSON = "json"
    MARKDOWN = "markdown"
    PLANTUML = "plantuml"


@dataclass
class MetaNode:
    """元节点定义"""
    meta_id: str
    meta_name: str
    meta_type: str  # 编排元/执行元/基础设施元
    layer: int  # 层级 (0-3)
    responsibilities: List[str] = field(default_factory=list)
    nac_domains: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # 依赖的元ID列表
    dependents: List[str] = field(default_factory=list)  # 依赖此元的元ID列表
    description: str = ""
    version: str = "1.0.0"

    def add_dependency(self, dep_id: str):
        """添加依赖"""
        if dep_id not in self.dependencies:
            self.dependencies.append(dep_id)

    def add_dependent(self, dep_id: str):
        """添加被依赖"""
        if dep_id not in self.dependents:
            self.dependents.append(dep_id)


@dataclass
class Relationship:
    """关系定义"""
    source_id: str
    target_id: str
    rel_type: str  # depends_on/delegates_to/validates/reviews/contains
    description: str = ""
    bidirectional: bool = False


@dataclass
class GraphResult:
    """图谱生成结果"""
    meta_id: str
    meta_name: str
    generation_date: str

    nodes: List[MetaNode] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)

    # 统计信息
    total_nodes: int = 0
    total_edges: int = 0
    max_depth: int = 0
    critical_path: List[str] = field(default_factory=list)
    isolated_nodes: List[str] = field(default_factory=list)

    # 分析结果
    circular_dependencies: List[List[str]] = field(default_factory=list)
    high_coupling: List[str] = field(default_factory=list)  # 依赖数>5的节点
    bottlenecks: List[str] = field(default_factory=list)  # 被依赖数>3的节点

    def to_dict(self) -> dict:
        return {
            'meta_id': self.meta_id,
            'meta_name': self.meta_name,
            'generation_date': self.generation_date,
            'nodes': [asdict(n) for n in self.nodes],
            'relationships': [asdict(r) for r in self.relationships],
            'statistics': {
                'total_nodes': self.total_nodes,
                'total_edges': self.total_edges,
                'max_depth': self.max_depth,
                'critical_path': self.critical_path,
                'isolated_nodes': self.isolated_nodes,
                'circular_dependencies': self.circular_dependencies,
                'high_coupling': self.high_coupling,
                'bottlenecks': self.bottlenecks
            }
        }


class MetaGraphGenerator:
    """Meta关系图生成器"""

    # 元类型定义
    META_TYPES = {
        'orchestration': {'name': '编排元', 'color': '#FF6B6B', 'layer': 2},
        'execution': {'name': '执行元', 'color': '#4ECDC4', 'layer': 1},
        'infrastructure': {'name': '基础设施元', 'color': '#45B7D1', 'layer': 0},
        'meta_layer': {'name': '元治理层', 'color': '#96CEB4', 'layer': 3}
    }

    # 关系类型定义
    RELATIONSHIP_TYPES = {
        'depends_on': {'name': '依赖', 'style': 'solid', 'arrow': '-->'},
        'delegates_to': {'name': '委托', 'style': 'dashed', 'arrow': '-.->'},
        'validates': {'name': '验证', 'style': 'dotted', 'arrow': '--|>'},
        'reviews': {'name': '审查', 'style': 'dotted', 'arrow': '-->>'},
        'contains': {'name': '包含', 'style': 'solid', 'arrow': '--+'},
        'escalates_to': {'name': '升级', 'style': 'dashed', 'arrow': '-->'}
    }

    def __init__(self, meta_id: str):
        self.meta_id = meta_id
        self.nodes: Dict[str, MetaNode] = {}
        self.relationships: List[Relationship] = []

    def add_node(self, node: MetaNode):
        """添加节点"""
        self.nodes[node.meta_id] = node

    def add_relationship(self, rel: Relationship):
        """添加关系"""
        self.relationships.append(rel)
        # 更新节点的依赖关系
        if rel.source_id in self.nodes:
            self.nodes[rel.source_id].add_dependency(rel.target_id)
        if rel.target_id in self.nodes:
            self.nodes[rel.target_id].add_dependent(rel.source_id)

    def add_meta(self, meta_id: str, meta_name: str, meta_type: str = 'execution',
                 layer: int = 1, responsibilities: List[str] = None,
                 nac_domains: List[str] = None, description: str = ""):
        """便捷方法：添加元定义"""
        node = MetaNode(
            meta_id=meta_id,
            meta_name=meta_name,
            meta_type=meta_type,
            layer=layer,
            responsibilities=responsibilities or [],
            nac_domains=nac_domains or [],
            description=description
        )
        self.add_node(node)
        return node

    def link_metas(self, source_id: str, target_id: str, rel_type: str = 'depends_on',
                  description: str = ""):
        """便捷方法：链接两个元"""
        rel = Relationship(
            source_id=source_id,
            target_id=target_id,
            rel_type=rel_type,
            description=description
        )
        self.add_relationship(rel)
        return rel

    def build_from_data(self, data: dict):
        """从数据构建图谱"""
        # 添加所有节点
        for node_data in data.get('nodes', []):
            self.add_meta(
                meta_id=node_data['meta_id'],
                meta_name=node_data.get('meta_name', node_data['meta_id']),
                meta_type=node_data.get('meta_type', 'execution'),
                layer=node_data.get('layer', 1),
                responsibilities=node_data.get('responsibilities', []),
                nac_domains=node_data.get('nac_domains', []),
                description=node_data.get('description', '')
            )

        # 添加所有关系
        for rel_data in data.get('relationships', []):
            self.link_metas(
                source_id=rel_data['source_id'],
                target_id=rel_data['target_id'],
                rel_type=rel_data.get('rel_type', 'depends_on'),
                description=rel_data.get('description', '')
            )

    def analyze(self) -> GraphResult:
        """分析图谱"""
        result = GraphResult(
            meta_id=self.meta_id,
            meta_name=self.nodes.get(self.meta_id, MetaNode(self.meta_id, self.meta_id, 'execution', 1)).meta_name,
            generation_date=datetime.now().isoformat(),
            nodes=list(self.nodes.values()),
            relationships=self.relationships
        )

        # 统计节点和边
        result.total_nodes = len(self.nodes)
        result.total_edges = len(self.relationships)

        # 检测孤立节点
        result.isolated_nodes = [
            node_id for node_id, node in self.nodes.items()
            if not node.dependencies and not node.dependents
        ]

        # 检测高度耦合节点（依赖数>5）
        result.high_coupling = [
            node_id for node_id, node in self.nodes.items()
            if len(node.dependencies) > 5
        ]

        # 检测瓶颈节点（被依赖数>3）
        result.bottlenecks = [
            node_id for node_id, node in self.nodes.items()
            if len(node.dependents) > 3
        ]

        # 检测循环依赖
        result.circular_dependencies = self._detect_circular_dependencies()

        # 计算最大深度
        result.max_depth = self._calculate_max_depth()

        # 找出关键路径
        result.critical_path = self._find_critical_path()

        return result

    def _detect_circular_dependencies(self) -> List[List[str]]:
        """检测循环依赖（DFS）"""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            node = self.nodes.get(node_id)
            if node:
                for dep in node.dependencies:
                    if dep not in self.nodes:
                        continue
                    if dep not in visited:
                        if dfs(dep):
                            return True
                    elif dep in rec_stack:
                        # 发现循环
                        cycle_start = path.index(dep)
                        cycle = path[cycle_start:] + [dep]
                        cycles.append(cycle)
                        return True

            path.pop()
            rec_stack.remove(node_id)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)

        return cycles

    def _calculate_max_depth(self) -> int:
        """计算最大深度（BFS）"""
        if not self.nodes:
            return 0

        # 找到没有依赖的根节点
        root_nodes = [
            node_id for node_id, node in self.nodes.items()
            if not node.dependencies
        ]

        if not root_nodes:
            return 1

        max_depth = 0
        depths = {node_id: 1 for node_id in root_nodes}
        queue = list(root_nodes)

        while queue:
            current = queue.pop(0)
            current_depth = depths[current]

            node = self.nodes.get(current)
            if node:
                for dep in node.dependents:
                    if dep in depths:
                        depths[dep] = max(depths[dep], current_depth + 1)
                    else:
                        depths[dep] = current_depth + 1
                        queue.append(dep)

            max_depth = max(max_depth, current_depth)

        return max_depth

    def _find_critical_path(self) -> List[str]:
        """找出关键路径（最长路径）"""
        if not self.nodes:
            return []

        # 找到入度为0的节点
        root_nodes = [
            node_id for node_id, node in self.nodes.items()
            if not node.dependencies
        ]

        if not root_nodes:
            root_nodes = list(self.nodes.keys())[:1]

        # DAG最长路径（动态规划）
        longest = {node_id: ([node_id], 1) for node_id in self.nodes}

        def dfs(node_id: str, visited: Set[str]) -> tuple:
            if node_id in visited:
                return [node_id], 1

            visited.add(node_id)
            node = self.nodes.get(node_id)
            if not node or not node.dependents:
                return [node_id], 1

            best_path = [node_id]
            best_len = 1

            for dep in node.dependents:
                if dep in self.nodes:
                    path, length = dfs(dep, visited.copy())
                    if length + 1 > best_len:
                        best_len = length + 1
                        best_path = [node_id] + path

            return best_path, best_len

        best_overall = []
        for root in root_nodes:
            path, _ = dfs(root, set())
            if len(path) > len(best_overall):
                best_overall = path

        return best_overall

    def generate_mermaid(self, result: GraphResult) -> str:
        """生成Mermaid格式图谱"""
        lines = ["```mermaid", "flowchart TD"]

        # 添加节点定义
        node_ids = list(self.nodes.keys())
        for node_id in node_ids:
            node = self.nodes[node_id]
            meta_type_info = self.META_TYPES.get(node.meta_type, {})
            color = meta_type_info.get('color', '#CCCCCC')
            type_name = meta_type_info.get('name', '未知')
            lines.append(f'    {node_id}["{node.meta_name}<br/><small>({type_name})</small>"]:::{node.meta_type}')

        # 添加样式类
        for meta_type, info in self.META_TYPES.items():
            lines.append(f'    classDef {meta_type} fill:{info["color"]},stroke:#333,stroke-width:2px')

        # 添加关系
        for rel in self.relationships:
            rel_info = self.RELATIONSHIP_TYPES.get(rel.rel_type, {})
            arrow = rel_info.get('arrow', '-->')
            lines.append(f'    {rel.source_id} {arrow} {rel.target_id}')

        # 添加标注
        if result.circular_dependencies:
            lines.append("")
            lines.append("    %% ⚠️ 警告：检测到循环依赖")
            for i, cycle in enumerate(result.circular_dependencies):
                lines.append(f'    %% 循环{i+1}: {" -> ".join(cycle)}')

        lines.append("```")
        return "\n".join(lines)

    def generate_dot(self, result: GraphResult) -> str:
        """生成Graphviz DOT格式"""
        lines = [
            "digraph meta_graph {",
            "    rankdir=TB;",
            "    node [shape=box, style=rounded];",
            "    edge [fontsize=10];"
        ]

        # 添加节点
        for node_id, node in self.nodes.items():
            meta_type_info = self.META_TYPES.get(node.meta_type, {})
            color = meta_type_info.get('color', '#EEEEEE')
            label = f'{node.meta_name}\\n({node.meta_type})'
            lines.append(f'    "{node_id}" [label="{label}", fillcolor="{color}", style=filled];')

        # 添加关系
        for rel in self.relationships:
            rel_info = self.RELATIONSHIP_TYPES.get(rel.rel_type, {})
            style = rel_info.get('style', 'solid')
            label = rel_info.get('name', rel.rel_type)
            lines.append(f'    "{rel.source_id}" -> "{rel.target_id}" [label="{label}", style={style}];')

        # 警告
        if result.circular_dependencies:
            lines.append("")
            lines.append("    // ⚠️ 警告：检测到循环依赖")
            for cycle in result.circular_dependencies:
                lines.append(f"    // {' -> '.join(cycle)}")

        lines.append("}")
        return "\n".join(lines)

    def generate_json(self, result: GraphResult) -> str:
        """生成JSON格式"""
        return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)

    def generate_markdown(self, result: GraphResult) -> str:
        """生成Markdown格式报告"""
        report = f"""# Meta关系图谱报告

## 基本信息

| 项目 | 内容 |
|------|------|
| 根元ID | {result.meta_id} |
| 根元名称 | {result.meta_name} |
| 生成日期 | {result.generation_date} |

## 图谱统计

| 指标 | 数值 |
|------|------|
| 总节点数 | {result.total_nodes} |
| 总边数 | {result.total_edges} |
| 最大深度 | {result.max_depth} |
| 孤立节点数 | {len(result.isolated_nodes)} |
| 循环依赖数 | {len(result.circular_dependencies)} |
| 高耦合节点数 | {len(result.high_coupling)} |
| 瓶颈节点数 | {len(result.bottlenecks)} |

## 节点清单

| 元ID | 名称 | 类型 | 层级 | 依赖数 | 被依赖数 |
|------|------|------|------|--------|----------|
"""

        for node_id, node in self.nodes.items():
            meta_type_info = self.META_TYPES.get(node.meta_type, {})
            type_name = meta_type_info.get('name', '未知')
            report += f"| {node.meta_id} | {node.meta_name} | {type_name} | {node.layer} | {len(node.dependencies)} | {len(node.dependents)} |\n"

        # 关系清单
        report += """
## 关系清单

| 源元 | 目标元 | 关系类型 | 说明 |
|------|--------|----------|------|
"""
        for rel in self.relationships:
            rel_info = self.RELATIONSHIP_TYPES.get(rel.rel_type, {})
            rel_name = rel_info.get('name', rel.rel_type)
            report += f"| {rel.source_id} | {rel.target_id} | {rel_name} | {rel.description} |\n"

        # 警告信息
        if result.circular_dependencies:
            report += """
## ⚠️ 警告信息

### 循环依赖
检测到以下循环依赖，请优先解决：
"""
            for i, cycle in enumerate(result.circular_dependencies):
                report += f"- 循环{i+1}: {' → '.join(cycle)}\n"

        if result.isolated_nodes:
            report += f"""
### 孤立节点
以下节点没有依赖关系，可能是孤立节点：
{', '.join(result.isolated_nodes)}
"""

        if result.high_coupling:
            report += f"""
### 高耦合节点
以下节点依赖数过多（>5），建议拆分：
{', '.join(result.high_coupling)}
"""

        if result.bottlenecks:
            report += f"""
### 瓶颈节点
以下节点被多个节点依赖，是潜在的单点故障：
{', '.join(result.bottlenecks)}
"""

        # 关键路径
        if result.critical_path:
            report += """
## 关键路径

```
"""
            for i, node_id in enumerate(result.critical_path):
                prefix = "→ " if i > 0 else "  "
                node = self.nodes.get(node_id)
                if node:
                    report += f"{prefix}{node.meta_name} ({node_id})\n"
            report += "```\n"

        # Mermaid图
        report += """
## 可视化图谱

"""
        report += self.generate_mermaid(result)
        report += f"""

---

*本报告由 Meta Graph Generator 自动生成*
"""
        return report

    def generate_report(self, result: GraphResult, fmt: OutputFormat = OutputFormat.MARKDOWN) -> str:
        """生成指定格式的报告"""
        if fmt == OutputFormat.MERMAID:
            return self.generate_mermaid(result)
        elif fmt == OutputFormat.DOT:
            return self.generate_dot(result)
        elif fmt == OutputFormat.JSON:
            return self.generate_json(result)
        elif fmt == OutputFormat.PLANTUML:
            return self._generate_plantuml(result)
        else:
            return self.generate_markdown(result)

    def _generate_plantuml(self, result: GraphResult) -> str:
        """生成PlantUML格式"""
        lines = ["@startuml", "!theme plain"]

        for node_id, node in self.nodes.items():
            meta_type_info = self.META_TYPES.get(node.meta_type, {})
            type_name = meta_type_info.get('name', '未知')
            lines.append(f'node "{node.meta_name}\\n({type_name})" as {node_id}')

        for rel in self.relationships:
            rel_info = self.RELATIONSHIP_TYPES.get(rel.rel_type, {})
            arrow = "->" if rel.rel_type == "depends_on" else "-->"
            lines.append(f"{rel.source_id} {arrow} {rel.target_id} : {rel_info.get('name', rel.rel_type)}")

        lines.append("@enduml")
        return "\n".join(lines)


def interactive_build() -> MetaGraphGenerator:
    """交互式构建图谱"""
    print("\n" + "="*60)
    print("📊 Meta关系图构建")
    print("="*60 + "\n")

    # 输入根元信息
    root_id = input("请输入根元ID: ").strip() or "root-meta"
    root_name = input("请输入根元名称: ").strip() or "根元"

    generator = MetaGraphGenerator(root_id)
    generator.add_meta(root_id, root_name, 'orchestration', layer=2)

    # 添加其他元
    print("\n添加元节点（输入空行结束）:")
    while True:
        meta_id = input("\n  元ID: ").strip()
        if not meta_id:
            break

        meta_name = input("  元名称: ").strip() or meta_id

        print("  元类型:")
        print("    1. 编排元 (orchestration)")
        print("    2. 执行元 (execution)")
        print("    3. 基础设施元 (infrastructure)")
        print("    4. 元治理层 (meta_layer)")

        type_choice = input("  选择类型 (1-4): ").strip()
        type_map = {'1': 'orchestration', '2': 'execution', '3': 'infrastructure', '4': 'meta_layer'}
        meta_type = type_map.get(type_choice, 'execution')

        layer = int(input("  层级 (0-3): ").strip() or "1")

        print("  添加依赖关系（输入空行结束）:")
        while True:
            dep = input("    依赖的元ID: ").strip()
            if not dep:
                break
            rel_type = input("    关系类型 (1.依赖 2.委托 3.验证 4.审查): ").strip()
            rel_map = {'1': 'depends_on', '2': 'delegates_to', '3': 'validates', '4': 'reviews'}
            rel_type = rel_map.get(rel_type, 'depends_on')

            generator.add_meta(dep, dep, 'execution', layer=1)
            generator.link_metas(meta_id, dep, rel_type)

        generator.add_meta(meta_id, meta_name, meta_type, layer=layer)

    return generator


def main():
    parser = argparse.ArgumentParser(description='Meta关系图生成器')
    parser.add_argument('meta_id', help='根元ID')
    parser.add_argument('--input', '-i', help='输入JSON文件')
    parser.add_argument('--output', '-o', help='输出文件')
    parser.add_argument('--format', '-f', choices=['mermaid', 'dot', 'json', 'markdown', 'plantuml'],
                        default='markdown', help='输出格式')
    parser.add_argument('--interactive', '-I', action='store_true', help='交互式构建')

    args = parser.parse_args()

    generator = MetaGraphGenerator(args.meta_id)

    if args.interactive:
        generator = interactive_build()
    elif args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        generator.build_from_data(data)
    else:
        # 简单示例数据
        generator.add_meta('orchestrator', '编排协调师', 'orchestration', layer=2)
        generator.add_meta('00-analyst', '分析师', 'execution', layer=1)
        generator.add_meta('01-investigator', '调研师', 'execution', layer=1)
        generator.add_meta('02-architect', '架构师', 'execution', layer=1)
        generator.add_meta('03-builder', '构建师', 'execution', layer=1)
        generator.add_meta('04-validator', '验证师', 'execution', layer=1)
        generator.add_meta('05-security', '安全师', 'execution', layer=1)
        generator.add_meta('06-reviewer', '审查师', 'execution', layer=1)
        generator.add_meta('07-scribe', '记录师', 'execution', layer=1)
        generator.add_meta('08-publisher', '发布师', 'execution', layer=1)

        # 添加关系
        generator.link_metas('orchestrator', '00-analyst', 'delegates_to')
        generator.link_metas('orchestrator', '01-investigator', 'delegates_to')
        generator.link_metas('orchestrator', '02-architect', 'delegates_to')
        generator.link_metas('00-analyst', '02-architect', 'depends_on')
        generator.link_metas('02-architect', '03-builder', 'depends_on')
        generator.link_metas('03-builder', '04-validator', 'depends_on')
        generator.link_metas('04-validator', '05-security', 'validates')
        generator.link_metas('05-security', '06-reviewer', 'reviews')
        generator.link_metas('06-reviewer', '07-scribe', 'depends_on')
        generator.link_metas('07-scribe', '08-publisher', 'depends_on')

    # 分析并生成报告
    result = generator.analyze()
    fmt_map = {
        'mermaid': OutputFormat.MERMAID,
        'dot': OutputFormat.DOT,
        'json': OutputFormat.JSON,
        'markdown': OutputFormat.MARKDOWN,
        'plantuml': OutputFormat.PLANTUML
    }
    report = generator.generate_report(result, fmt_map)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)

        # 同时保存JSON结果
        json_output = args.output.replace('.md', '.json').replace('.dot', '.json')
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)

        print(f"\n✅ 图谱已保存到: {args.output}")
        print(f"✅ JSON结果已保存到: {json_output}")
    else:
        print(report)

    # 打印警告信息
    if result.circular_dependencies:
        print("\n⚠️ 警告：检测到循环依赖")
        for cycle in result.circular_dependencies:
            print(f"  - {' → '.join(cycle)}")

    if result.high_coupling:
        print(f"\n⚠️ 高耦合节点: {', '.join(result.high_coupling)}")

    if result.bottlenecks:
        print(f"\n⚠️ 瓶颈节点: {', '.join(result.bottlenecks)}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
