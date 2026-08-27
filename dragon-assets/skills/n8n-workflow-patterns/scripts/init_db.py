#!/usr/bin/env python3
"""
n8n-workflow-patterns SQLite 数据库初始化脚本
从 samples.json 导入示例工作流数据
"""
import sqlite3
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DB_PATH = SCRIPT_DIR.parent / "index.db"
SAMPLES_PATH = SCRIPT_DIR.parent / "workflows" / "samples.json"


def init_db():
    """初始化数据库并导入样本数据"""
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 创建 workflows 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflows (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            complexity TEXT,
            integrations TEXT,
            nodes_count INTEGER,
            trigger_type TEXT,
            use_cases TEXT,
           天龙适配 TEXT
        )
    """)

    # 创建 FTS5 虚拟表用于全文搜索
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS workflows_fts USING fts5(
            name,
            description,
            category,
            integrations,
            trigger_type,
            use_cases,
            content='workflows',
            content_rowid='rowid'
        )
    """)

    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON workflows(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trigger ON workflows(trigger_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_complexity ON workflows(complexity)")

    # 读取样本数据
    if SAMPLES_PATH.exists():
        with open(SAMPLES_PATH, "r", encoding="utf-8") as f:
            samples = json.load(f)

        # 导入数据
        for workflow in samples:
            cursor.execute("""
                INSERT OR REPLACE INTO workflows
                (id, name, description, category, complexity, integrations,
                 nodes_count, trigger_type, use_cases,天龙适配)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                workflow["id"],
                workflow["name"],
                "",  # description 字段为空
                workflow.get("category", ""),
                workflow.get("complexity", ""),
                ",".join(workflow.get("integrations", [])),
                workflow.get("nodes_count", 0),
                workflow.get("trigger_type", ""),
                ",".join(workflow.get("use_cases", [])),
                json.dumps(workflow.get("天龙适配", {}), ensure_ascii=False)
            ))

        # 重建 FTS 索引
        cursor.execute("INSERT INTO workflows_fts(workflows_fts) VALUES('rebuild')")

    conn.commit()

    # 验证数据
    cursor.execute("SELECT COUNT(*) FROM workflows")
    count = cursor.fetchone()[0]
    print(f"✓ 数据库初始化完成，共 {count} 条工作流记录")
    print(f"  数据库路径: {DB_PATH}")

    conn.close()
    return count


def search_db(keyword: str, category: str = None, trigger: str = None, limit: int = 10):
    """搜索工作流"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = "SELECT name, category, trigger_type, integrations, nodes_count FROM workflows WHERE 1=1"
    params = []

    if keyword:
        query += " AND (name LIKE ? OR integrations LIKE ? OR use_cases LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])

    if category:
        query += " AND category = ?"
        params.append(category)

    if trigger:
        query += " AND trigger_type = ?"
        params.append(trigger)

    query += f" LIMIT {limit}"

    cursor.execute(query, params)
    results = cursor.fetchall()

    print(f"\n🔍 搜索结果: '{keyword}'")
    print("-" * 70)
    for i, row in enumerate(results, 1):
        name, cat, trig, integ, nodes = row
        print(f"{i}. {name}")
        print(f"   分类: {cat} | 触发器: {trig} | 节点数: {nodes}")
        print(f"   集成: {integ}")
        print()

    conn.close()
    return results


def list_all():
    """列出所有工作流"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name, category, trigger_type, complexity, nodes_count FROM workflows")
    results = cursor.fetchall()

    print(f"\n📋 全部工作流 ({len(results)} 条)")
    print("-" * 70)
    for row in results:
        name, cat, trig, comp, nodes = row
        print(f"  • {name} [{comp}] {trig} {nodes}节点")

    conn.close()
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "search":
            keyword = sys.argv[2] if len(sys.argv) > 2 else ""
            category = None
            trigger = None
            for i, arg in enumerate(sys.argv):
                if arg == "--category" and i + 1 < len(sys.argv):
                    category = sys.argv[i + 1]
                if arg == "--trigger" and i + 1 < len(sys.argv):
                    trigger = sys.argv[i + 1]
            search_db(keyword, category, trigger)
        elif sys.argv[1] == "list":
            list_all()
        else:
            init_db()
    else:
        init_db()
