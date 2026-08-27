#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys

# 设置标准输出编码为 UTF-8 (只在非测试环境)
try:
    if hasattr(sys.stdout, 'buffer') and not sys.stdout.closed:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass
"""
session-distiller - 语义检索模块

基于 SQLite FTS5 的智能记忆检索
支持语义相似度和类型筛选
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# ============ 配置 ============
DEFAULT_DB_PATH = Path.home() / ".claude" / "session-distiller" / "memory.db"


class SemanticSearch:
    """语义检索器"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.conn = None

    def connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(str(self.db_path))

    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()

    def search(
        self,
        query: str,
        mode: str = "hybrid",  # exact, semantic, hybrid
        filter_type: Optional[str] = None,
        limit: int = 10,
        context_lines: int = 3
    ) -> List[dict]:
        """
        搜索记忆

        Args:
            query: 搜索关键词
            mode: 搜索模式
                - exact: 精确匹配
                - semantic: 语义相似度
                - hybrid: 混合模式
            filter_type: 筛选类型 (decision, todo, info)
            limit: 返回结果数量
            context_lines: 上下文行数

        Returns:
            搜索结果列表
        """
        self.connect()

        results = []

        if mode == "exact":
            results = self._exact_search(query, filter_type, limit)
        elif mode == "semantic":
            results = self._semantic_search(query, filter_type, limit)
        else:  # hybrid
            # 先尝试精确匹配，再补充语义结果
            exact_results = self._exact_search(query, filter_type, limit // 2)
            semantic_results = self._semantic_search(query, filter_type, limit // 2)

            # 合并并去重
            seen_ids = set()
            for r in exact_results + semantic_results:
                if r['id'] not in seen_ids:
                    seen_ids.add(r['id'])
                    results.append(r)

        # 添加上下文
        for r in results:
            r['context'] = self._get_context(r['content'], query, context_lines)

        self.close()
        return results

    def _exact_search(
        self,
        query: str,
        filter_type: Optional[str],
        limit: int
    ) -> List[dict]:
        """精确搜索 (FTS5)"""
        cursor = self.conn.cursor()

        # 搜索会话 (sessions_fts 的列是 content 和 session_id)
        cursor.execute(
            """SELECT session_id, content FROM sessions_fts
               WHERE sessions_fts MATCH ?
               LIMIT ?""",
            (query, limit)
        )

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'content': row[1],
                'source': 'fts',
                'created_at': '',
                'type': 'session',
                'score': 1.0
            })

        # 如果有类型筛选，搜索关键点
        if filter_type:
            cursor.execute(
                """SELECT id, content, session_id, created_at FROM keypoints
                   WHERE content LIKE ? AND category = ?
                   LIMIT ?""",
                (f"%{query}%", filter_type, limit)
            )

            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'content': row[1],
                    'session_id': row[2],
                    'created_at': row[3],
                    'type': 'keypoint',
                    'category': filter_type,
                    'score': 0.9
                })

        return results

    def _semantic_search(
        self,
        query: str,
        filter_type: Optional[str],
        limit: int
    ) -> List[dict]:
        """
        语义搜索

        简化实现：使用关键词权重计算相似度
        完整实现应使用嵌入向量和余弦相似度
        """
        cursor = self.conn.cursor()

        # 获取所有会话
        cursor.execute(
            "SELECT id, content, source, created_at FROM sessions LIMIT 100"
        )

        # 简单相似度计算 (演示用)
        query_terms = set(query.lower().split())
        results = []

        for row in cursor.fetchall():
            content_terms = set(row[1].lower().split())

            # Jaccard 相似度
            if query_terms and content_terms:
                intersection = query_terms & content_terms
                union = query_terms | content_terms
                score = len(intersection) / len(union)

                if score > 0.1:  # 阈值
                    results.append({
                        'id': row[0],
                        'content': row[1],
                        'source': row[2],
                        'created_at': row[3],
                        'type': 'session',
                        'score': score
                    })

        # 按分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]

    def _get_context(self, content: str, query: str, lines: int) -> str:
        """获取搜索词的上下文"""
        content_lines = content.split('\n')

        for i, line in enumerate(content_lines):
            if query.lower() in line.lower():
                start = max(0, i - lines)
                end = min(len(content_lines), i + lines + 1)
                return '\n'.join(content_lines[start:end])

        return content[:200] + '...'

    def search_by_entity(self, entity: str) -> List[dict]:
        """按实体搜索 (知识图谱)"""
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute(
            """SELECT id, title, content, tags FROM knowledge_cards
               WHERE content LIKE ?""",
            (f"%{entity}%",)
        )

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'tags': json.loads(row[3]) if row[3] else []
            })

        self.close()
        return results

    def get_related(self, card_id: str) -> List[dict]:
        """获取相关知识卡片"""
        self.connect()
        cursor = self.conn.cursor()

        # 获取目标卡片
        cursor.execute(
            "SELECT tags FROM knowledge_cards WHERE id = ?",
            (card_id,)
        )
        row = cursor.fetchone()

        if not row or not row[0]:
            self.close()
            return []

        tags = json.loads(row[0])

        # 搜索具有相似标签的卡片
        results = []
        for tag in tags:
            cursor.execute(
                """SELECT id, title, content, tags FROM knowledge_cards
                   WHERE tags LIKE ? AND id != ?
                   LIMIT 5""",
                (f"%{tag}%", card_id)
            )

            for r in cursor.fetchall():
                results.append({
                    'id': r[0],
                    'title': r[1],
                    'content': r[2],
                    'tags': json.loads(r[3]) if r[3] else []
                })

        self.close()
        return results

    def get_timeline(self, entity: str = None) -> List[dict]:
        """获取时间线"""
        self.connect()
        cursor = self.conn.cursor()

        if entity:
            cursor.execute(
                """SELECT id, content, created_at FROM sessions
                   WHERE content LIKE ?
                   ORDER BY created_at DESC
                   LIMIT 50""",
                (f"%{entity}%",)
            )
        else:
            cursor.execute(
                """SELECT id, content, created_at FROM sessions
                   ORDER BY created_at DESC
                   LIMIT 50"""
            )

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'content': row[1][:100] + '...',
                'created_at': row[2]
            })

        self.close()
        return results

    def get_network(self) -> dict:
        """获取知识网络"""
        self.connect()
        cursor = self.conn.cursor()

        # 统计标签
        cursor.execute("SELECT tags FROM knowledge_cards")
        tag_counts = {}

        for row in cursor.fetchall():
            if row[0]:
                tags = json.loads(row[0])
                for tag in tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # 统计类型
        cursor.execute(
            "SELECT category, COUNT(*) FROM keypoints GROUP BY category"
        )
        category_counts = {row[0]: row[1] for row in cursor.fetchall()}

        self.close()

        return {
            'tags': sorted(tag_counts.items(), key=lambda x: x[1], reverse=True),
            'categories': category_counts,
            'total_cards': sum(tag_counts.values())
        }


def main():
    parser = argparse.ArgumentParser(
        description="Semantic Search - 语义检索"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="搜索关键词"
    )
    parser.add_argument(
        "--mode",
        choices=["exact", "semantic", "hybrid"],
        default="hybrid",
        help="搜索模式"
    )
    parser.add_argument(
        "--type",
        help="筛选类型: decision, todo, info"
    )
    parser.add_argument(
        "--context",
        type=int,
        default=3,
        help="上下文行数"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="结果数量"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="显示统计信息"
    )
    parser.add_argument(
        "--network",
        action="store_true",
        help="显示知识网络"
    )
    parser.add_argument(
        "--timeline",
        action="store_true",
        help="显示时间线"
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="数据库路径"
    )

    args = parser.parse_args()

    searcher = SemanticSearch(args.db_path)

    if args.stats:
        stats = searcher.get_network()
        print("📊 知识网络统计:")
        print(f"\n🏷️ 标签热度:")
        for tag, count in stats['tags'][:10]:
            print(f"   {tag}: {count}")
        print(f"\n📂 内容类型:")
        for cat, count in stats['categories'].items():
            print(f"   {cat}: {count}")
        return

    if args.network:
        network = searcher.get_network()
        print("🔗 知识网络:")
        print(f"\n节点数: {network['total_cards']}")
        print(f"标签数: {len(network['tags'])}")
        return

    if args.timeline:
        timeline = searcher.get_timeline()
        print("📅 记忆时间线:")
        for item in timeline[:20]:
            print(f"\n   [{item['created_at']}] {item['content']}")
        return

    if not args.query:
        parser.print_help()
        return

    results = searcher.search(
        args.query,
        mode=args.mode,
        filter_type=args.type,
        limit=args.limit,
        context_lines=args.context
    )

    print(f"🔍 搜索 '{args.query}' 的结果 ({len(results)} 条):\n")

    for i, r in enumerate(results, 1):
        print(f"{'='*60}")
        print(f"📌 #{i} [{r['type']}] {r.get('category', '')} (置信度: {r.get('score', 0):.2f})")
        print(f"   ID: {r['id']}")
        print(f"   时间: {r['created_at']}")
        print(f"\n   📄 内容片段:")
        for line in r['context'].split('\n')[:10]:
            if line.strip():
                print(f"      {line[:80]}")
        print()


if __name__ == "__main__":
    main()
