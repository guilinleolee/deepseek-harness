#!/usr/bin/env python3
"""
知识图谱管理器 - 构建和维护实体关系图谱
支持查询、更新、导出等功能
"""

import os
import sys
import json
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from collections import defaultdict

# 图谱数据库路径
GRAPH_DB = Path.home() / '.claude' / 'memory-graph.db'


class KnowledgeGraphManager:
    """知识图谱管理器"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or GRAPH_DB
        self._init_db()

    def _init_db(self):
        """初始化图谱数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 节点表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                type TEXT,
                content TEXT,
                metadata TEXT,
                created_at INTEGER,
                updated_at INTEGER
            )
        """)

        # 边表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                metadata TEXT,
                created_at INTEGER,
                FOREIGN KEY (source_id) REFERENCES nodes(id),
                FOREIGN KEY (target_id) REFERENCES nodes(id)
            )
        """)

        # 索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_label ON nodes(label)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id)")

        conn.commit()
        conn.close()

    def add_node(self, label: str, node_type: str = "entity",
                 content: str = "", metadata: Optional[Dict] = None) -> str:
        """添加节点"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        node_id = f"node-{datetime.now().strftime('%Y%m%d%H%M%S')}-{label[:20]}"
        now = int(datetime.now().timestamp())

        cursor.execute("""
            INSERT INTO nodes (id, label, type, content, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (node_id, label, node_type, content,
              json.dumps(metadata or {}, ensure_ascii=False), now, now))

        conn.commit()
        conn.close()

        print(f"✓ 节点已添加: {label} ({node_id})")
        return node_id

    def add_edge(self, source_id: str, target_id: str, relation: str,
                 weight: float = 1.0, metadata: Optional[Dict] = None) -> str:
        """添加边"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        edge_id = f"edge-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        now = int(datetime.now().timestamp())

        cursor.execute("""
            INSERT INTO edges (id, source_id, target_id, relation, weight, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (edge_id, source_id, target_id, relation, weight,
              json.dumps(metadata or {}, ensure_ascii=False), now))

        conn.commit()
        conn.close()

        print(f"✓ 边已添加: {source_id} --[{relation}]--> {target_id}")
        return edge_id

    def query(self, keyword: str, max_results: int = 20) -> List[Dict]:
        """查询相关节点"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, label, type, content, metadata
            FROM nodes
            WHERE label LIKE ? OR content LIKE ?
            ORDER BY updated_at DESC
            LIMIT ?
        """, (f"%{keyword}%", f"%{keyword}%", max_results))

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'label': row[1],
                'type': row[2],
                'content': row[3],
                'metadata': row[4]
            })

        conn.close()
        return results

    def get_relations(self, node_id: str) -> List[Dict]:
        """获取节点的所有关系"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 出去的边
        cursor.execute("""
            SELECT e.id, n.label, e.relation, e.weight
            FROM edges e
            JOIN nodes n ON e.target_id = n.id
            WHERE e.source_id = ?
        """, (node_id,))
        outgoing = [{'id': r[0], 'target': r[1], 'relation': r[2], 'weight': r[3]}
                     for r in cursor.fetchall()]

        # 进入的边
        cursor.execute("""
            SELECT e.id, n.label, e.relation, e.weight
            FROM edges e
            JOIN nodes n ON e.source_id = n.id
            WHERE e.target_id = ?
        """, (node_id,))
        incoming = [{'id': r[0], 'source': r[1], 'relation': r[2], 'weight': r[3]}
                     for r in cursor.fetchall()]

        conn.close()
        return {'outgoing': outgoing, 'incoming': incoming}

    def export_json(self, output_path: Optional[Path] = None) -> Dict:
        """导出图谱为JSON"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("SELECT id, label, type, content, metadata FROM nodes")
        nodes = [{'id': r[0], 'label': r[1], 'type': r[2],
                  'content': r[3], 'metadata': r[4]} for r in cursor.fetchall()]

        cursor.execute("SELECT id, source_id, target_id, relation, weight FROM edges")
        edges = [{'id': r[0], 'source': r[1], 'target': r[2],
                  'relation': r[3], 'weight': r[4]} for r in cursor.fetchall()]

        conn.close()

        graph = {
            'nodes': nodes,
            'edges': edges,
            'stats': {
                'node_count': len(nodes),
                'edge_count': len(edges),
                'updated': datetime.now().isoformat()
            }
        }

        if output_path:
            output_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f"✓ 图谱已导出: {output_path}")

        return graph

    def export_html(self, output_path: Path) -> bool:
        """导出为交互式HTML可视化"""
        graph = self.export_json()

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>知识图谱可视化</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: #eee; }}
        h1 {{ text-align: center; color: #00d4ff; }}
        #graph {{ width: 100%; height: 600px; border: 1px solid #333; border-radius: 8px; }}
        .node {{ cursor: pointer; }}
        .link {{ stroke: #555; stroke-opacity: 0.6; }}
        .label {{ font-size: 12px; fill: #fff; }}
        .stats {{ text-align: center; margin: 20px 0; color: #888; }}
    </style>
</head>
<body>
    <h1>知识图谱</h1>
    <div class="stats">
        节点: {graph['stats']['node_count']} | 边: {graph['stats']['edge_count']} | 更新: {graph['stats']['updated']}
    </div>
    <div id="graph"></div>
    <script>
        const data = {json.dumps(graph, ensure_ascii=False)};

        const width = document.getElementById('graph').clientWidth;
        const height = 600;

        const svg = d3.select('#graph')
            .append('svg')
            .attr('width', width)
            .attr('height', height);

        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.edges).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width/2, height/2));

        const link = svg.append('g')
            .selectAll('line')
            .data(data.edges)
            .join('line')
            .attr('class', 'link')
            .attr('stroke-width', d => Math.sqrt(d.weight || 1) * 2);

        const node = svg.append('g')
            .selectAll('circle')
            .data(data.nodes)
            .join('circle')
            .attr('class', 'node')
            .attr('r', 10)
            .attr('fill', d => d.type === 'insight' ? '#ff6b6b' :
                             d.type === 'knowledge' ? '#4ecdc4' : '#45b7d1')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended));

        const label = svg.append('g')
            .selectAll('text')
            .data(data.nodes)
            .join('text')
            .attr('class', 'label')
            .text(d => d.label.substring(0, 15));

        simulation.on('tick', () => {{
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);
            node
                .attr('cx', d => d.x)
                .attr('cy', d => d.y);
            label
                .attr('x', d => d.x + 15)
                .attr('y', d => d.y + 5);
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
    </script>
</body>
</html>"""

        output_path.write_text(html, encoding='utf-8')
        print(f"✓ HTML可视化已生成: {output_path}")
        return True

    def stats(self) -> Dict:
        """获取图谱统计"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM nodes")
        node_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM edges")
        edge_count = cursor.fetchone()[0]

        cursor.execute("SELECT type, COUNT(*) FROM nodes GROUP BY type")
        type_dist = {r[0]: r[1] for r in cursor.fetchall()}

        cursor.execute("""
            SELECT relation, COUNT(*) as cnt
            FROM edges
            GROUP BY relation
            ORDER BY cnt DESC
            LIMIT 5
        """)
        top_relations = [{'relation': r[0], 'count': r[1]} for r in cursor.fetchall()]

        conn.close()

        return {
            'node_count': node_count,
            'edge_count': edge_count,
            'type_distribution': type_dist,
            'top_relations': top_relations
        }

    def update_from_memories(self, db_path: Path = None) -> int:
        """从记忆数据库更新图谱"""
        mem_db = db_path or Path.home() / '.claude' / 'memory.db'

        if not mem_db.exists():
            print(f"⚠ 记忆数据库不存在: {mem_db}")
            return 0

        conn = sqlite3.connect(str(mem_db))
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, content, layer, metadata
                FROM memories
                WHERE layer IN ('L3', 'L2', 3, 2)
            """)
            memories = cursor.fetchall()
        except:
            print("⚠ 无法从记忆数据库读取")
            conn.close()
            return 0

        added = 0
        for mem in memories:
            metadata = {}
            try:
                if mem[3]:
                    metadata = json.loads(mem[3])
            except:
                pass

            node_type = 'insight' if mem[2] in ('L3', 3) else 'knowledge'
            node_id = self.add_node(
                label=metadata.get('topic', mem[0][:30]),
                node_type=node_type,
                content=mem[1][:200] if mem[1] else '',
                metadata=metadata
            )
            added += 1

            # 建立与已有节点的关联
            if metadata.get('topic'):
                related = self.query(metadata['topic'], max_results=1)
                if related and related[0]['id'] != node_id:
                    self.add_edge(related[0]['id'], node_id, '包含')

        conn.close()
        print(f"✓ 从记忆更新了 {added} 个节点")
        return added


def main():
    parser = argparse.ArgumentParser(description='知识图谱管理器')
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # update命令
    update_parser = subparsers.add_parser('update', help='更新图谱')
    update_parser.add_argument('--type', choices=['research', 'all'], default='all',
                             help='更新类型')

    # query命令
    query_parser = subparsers.add_parser('query', help='查询节点')
    query_parser.add_argument('keyword', help='查询关键词')
    query_parser.add_argument('--limit', type=int, default=20, help='最大结果数')

    # export命令
    export_parser = subparsers.add_parser('export', help='导出图谱')
    export_parser.add_argument('--format', choices=['json', 'html'], default='json',
                             help='导出格式')
    export_parser.add_argument('--output', help='输出路径')

    # stats命令
    subparsers.add_parser('stats', help='查看统计')

    # add-node命令
    node_parser = subparsers.add_parser('add-node', help='添加节点')
    node_parser.add_argument('label', help='节点标签')
    node_parser.add_argument('--type', default='entity', help='节点类型')
    node_parser.add_argument('--content', default='', help='节点内容')

    args = parser.parse_args()

    manager = KnowledgeGraphManager()

    if args.command == 'update':
        count = manager.update_from_memories()
        print(f"✓ 图谱更新完成: {count} 个节点")

    elif args.command == 'query':
        results = manager.query(args.keyword, args.limit)
        print(f"\n=== 查询结果: '{args.keyword}' ===")
        print(f"找到 {len(results)} 个节点:\n")
        for i, node in enumerate(results, 1):
            print(f"{i}. [{node['type']}] {node['label']}")
            if node['content']:
                print(f"   {node['content'][:100]}...")

    elif args.command == 'export':
        if args.format == 'html':
            output = Path(args.output) if args.output else \
                Path.home() / '.claude' / 'knowledge-graph.html'
            manager.export_html(output)
        else:
            output = Path(args.output) if args.output else \
                Path.home() / '.claude' / 'knowledge-graph.json'
            manager.export_json(output)

    elif args.command == 'stats':
        stats = manager.stats()
        print("\n=== 图谱统计 ===")
        print(f"节点数: {stats['node_count']}")
        print(f"边数: {stats['edge_count']}")
        print(f"\n类型分布: {stats['type_distribution']}")
        print(f"\n热门关系: {stats['top_relations']}")

    elif args.command == 'add-node':
        manager.add_node(args.label, args.type, args.content)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
