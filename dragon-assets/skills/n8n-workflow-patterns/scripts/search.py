#!/usr/bin/env python3
"""
n8n Workflow Pattern Search
搜索4,343个n8n工作流模板
"""

import sys
import json
import sqlite3
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.parent
DB_PATH = SCRIPT_DIR / "index.db"


def search_workflows(keyword, category=None, trigger=None, limit=10):
    """搜索n8n工作流模板"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 构建SQL查询
    sql = """
    SELECT name, description, category, integration, nodes_count, trigger_type, complexity
    FROM workflows
    WHERE name LIKE ? OR description LIKE ?
    """
    params = [f"%{keyword}%", f"%{keyword}%"]

    if category:
        sql += " AND category = ?"
        params.append(category)

    if trigger:
        sql += " AND trigger_type = ?"
        params.append(trigger)

    sql += f" LIMIT {limit}"

    cursor.execute(sql, params)
    results = cursor.fetchall()
    conn.close()

    return [dict(row) for row in results]


def format_result(workflow, rank):
    """格式化搜索结果"""
    integrations = workflow.get('integration', '').split(',')[:3]
    return f"""#{rank} {workflow['name']}
   分类: {workflow['category']} | 节点: {workflow['nodes_count']}
   触发: {workflow['trigger_type']} | 复杂度: {workflow['complexity']}
   集成: {', '.join(integrations)}
   描述: {workflow['description'][:100]}..."""


def main():
    if len(sys.argv) < 2:
        print("用法: n8n-search <keyword> [--category <分类>] [--trigger <触发器>] [--limit <数量>]")
        sys.exit(1)

    keyword = sys.argv[1]
    category = None
    trigger = None
    limit = 10

    # 解析参数
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == '--category' and i + 1 < len(args):
            category = args[i + 1]
            i += 2
        elif args[i] == '--trigger' and i + 1 < len(args):
            trigger = args[i + 1]
            i += 2
        elif args[i] == '--limit' and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 2
        else:
            i += 1

    results = search_workflows(keyword, category, trigger, limit)

    if not results:
        print(f"未找到匹配 '{keyword}' 的工作流")
        return

    print(f"\n找到 {len(results)} 个匹配的工作流模板:\n")
    for i, workflow in enumerate(results, 1):
        print(format_result(workflow, i))
        print()


if __name__ == "__main__":
    main()