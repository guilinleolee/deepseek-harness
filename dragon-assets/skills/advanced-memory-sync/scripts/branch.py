#!/usr/bin/env python3
"""
分支管理器 - Git-like对话分支管理
支持创建分支、切换分支、合并分支等操作
"""

import os
import sys
import json
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# 分支数据库路径
BRANCH_DB = Path.home() / '.claude' / 'memory-branches.db'


class BranchManager:
    """分支管理器"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or BRANCH_DB
        self._init_db()

    def _init_db(self):
        """初始化分支数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 分支表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS branches (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                parent_id TEXT,
                created_at INTEGER NOT NULL,
                metadata TEXT,
                is_active INTEGER DEFAULT 0
            )
        """)

        # 分支记忆表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS branch_memories (
                id TEXT PRIMARY KEY,
                branch_id TEXT NOT NULL,
                conversation_id TEXT,
                content TEXT,
                layer TEXT,
                created_at INTEGER,
                FOREIGN KEY (branch_id) REFERENCES branches(id)
            )
        """)

        conn.commit()
        conn.close()

    def create_branch(self, name: str, parent_id: Optional[str] = None,
                     metadata: Optional[Dict] = None) -> str:
        """创建新分支"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        branch_id = f"branch-{datetime.now().strftime('%Y%m%d%H%M%S')}-{name}"
        created_at = int(datetime.now().timestamp())

        cursor.execute("""
            INSERT INTO branches (id, name, parent_id, created_at, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (branch_id, name, parent_id, created_at,
              json.dumps(metadata or {}, ensure_ascii=False)))

        conn.commit()
        conn.close()

        print(f"✓ 分支已创建: {name} ({branch_id})")
        return branch_id

    def checkout(self, branch_id: str) -> bool:
        """切换到指定分支"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 检查分支是否存在
        cursor.execute("SELECT id, name FROM branches WHERE id = ?", (branch_id,))
        branch = cursor.fetchone()

        if not branch:
            print(f"✗ 分支不存在: {branch_id}")
            return False

        # 取消当前活跃分支
        cursor.execute("UPDATE branches SET is_active = 0 WHERE is_active = 1")

        # 设置新分支为活跃
        cursor.execute("UPDATE branches SET is_active = 1 WHERE id = ?", (branch_id,))

        conn.commit()
        conn.close()

        print(f"✓ 已切换到分支: {branch[1]} ({branch_id})")
        return True

    def merge(self, source_id: str, target_id: str,
              resolve_conflicts: bool = False) -> bool:
        """合并分支"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 检查源分支和目标分支
        cursor.execute("SELECT id, name FROM branches WHERE id = ?", (source_id,))
        source = cursor.fetchone()

        cursor.execute("SELECT id, name FROM branches WHERE id = ?", (target_id,))
        target = cursor.fetchone()

        if not source or not target:
            print("✗ 源分支或目标分支不存在")
            return False

        # 获取源分支的记忆
        cursor.execute("""
            SELECT id, conversation_id, content, layer, created_at
            FROM branch_memories
            WHERE branch_id = ?
        """, (source_id,))

        source_memories = cursor.fetchall()

        # 合并记忆到目标分支
        merge_id = f"merge-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        for memory in source_memories:
            # 检查冲突
            cursor.execute("""
                SELECT id FROM branch_memories
                WHERE branch_id = ? AND conversation_id = ?
            """, (target_id, memory[1]))

            if cursor.fetchone():
                if resolve_conflicts:
                    # 解决冲突：保留两个版本
                    new_id = f"{memory[0]}-merged-{merge_id}"
                    cursor.execute("""
                        INSERT INTO branch_memories
                        (id, branch_id, conversation_id, content, layer, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (new_id, target_id, memory[1],
                         f"[MERGED from {source[1]}] {memory[2]}",
                         memory[3], memory[4]))
                # 如果不解决冲突，跳过
            else:
                cursor.execute("""
                    INSERT INTO branch_memories
                    (id, branch_id, conversation_id, content, layer, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (f"{memory[0]}-migrated", target_id, memory[1],
                     memory[2], memory[3], memory[4]))

        # 记录合并
        cursor.execute("""
            INSERT INTO branch_memories
            (id, branch_id, conversation_id, content, layer, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (f"merge-record-{merge_id}", target_id, None,
              json.dumps({
                  'type': 'merge',
                  'source': source[1],
                  'timestamp': datetime.now().isoformat(),
                  'conflicts_resolved': resolve_conflicts
              }, ensure_ascii=False),
              'META', int(datetime.now().timestamp())))

        conn.commit()
        conn.close()

        print(f"✓ 已将 {source[1]} 合并到 {target[1]}")
        print(f"  合并了 {len(source_memories)} 条记忆")
        return True

    def list_branches(self, show_active: bool = True) -> List[Dict]:
        """列出所有分支"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, parent_id, created_at, is_active, metadata
            FROM branches
            ORDER BY created_at DESC
        """)

        branches = []
        for row in cursor.fetchall():
            metadata = {}
            try:
                if row[5]:
                    metadata = json.loads(row[5])
            except:
                pass

            branches.append({
                'id': row[0],
                'name': row[1],
                'parent': row[2],
                'created': datetime.fromtimestamp(row[3]).strftime('%Y-%m-%d %H:%M:%S'),
                'active': bool(row[4]),
                'metadata': metadata
            })

        conn.close()

        if show_active:
            print("\n=== 分支列表 ===")
            for i, b in enumerate(branches, 1):
                active_mark = " ✓" if b['active'] else ""
                parent_info = f" <- {b['parent']}" if b['parent'] else ""
                print(f"  {i}. {b['name']}{active_mark} ({b['id']}){parent_info}")
                print(f"     创建于: {b['created']}")

        return branches

    def diff(self, branch_a_id: str, branch_b_id: str) -> bool:
        """对比两个分支的差异"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 获取分支A的记忆
        cursor.execute("""
            SELECT conversation_id, content, layer
            FROM branch_memories
            WHERE branch_id = ?
        """, (branch_a_id,))
        mem_a = {m[0]: m for m in cursor.fetchall()}

        # 获取分支B的记忆
        cursor.execute("""
            SELECT conversation_id, content, layer
            FROM branch_memories
            WHERE branch_id = ?
        """, (branch_b_id,))
        mem_b = {m[0]: m for m in cursor.fetchall()}

        # 计算差异
        only_a = set(mem_a.keys()) - set(mem_b.keys())
        only_b = set(mem_b.keys()) - set(mem_a.keys())
        common = set(mem_a.keys()) & set(mem_b.keys())

        print("\n=== 分支对比 ===")
        print(f"\n仅在分支A ({branch_a_id}):")
        for cid in only_a:
            print(f"  - {cid[:30]}...")

        print(f"\n仅在分支B ({branch_b_id}):")
        for cid in only_b:
            print(f"  - {cid[:30]}...")

        print(f"\n共同记忆数: {len(common)}")

        conn.close()
        return True

    def get_current_branch(self) -> Optional[Dict]:
        """获取当前活跃分支"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, parent_id, created_at, metadata
            FROM branches
            WHERE is_active = 1
        """)

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'name': row[1],
                'parent': row[2],
                'created': datetime.fromtimestamp(row[3]).strftime('%Y-%m-%d %H:%M:%S'),
                'metadata': json.loads(row[4]) if row[4] else {}
            }

        return None

    def delete_branch(self, branch_id: str, force: bool = False) -> bool:
        """删除分支"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 检查是否为活跃分支
        cursor.execute("SELECT is_active FROM branches WHERE id = ?", (branch_id,))
        row = cursor.fetchone()

        if not row:
            print(f"✗ 分支不存在: {branch_id}")
            return False

        if row[0] and not force:
            print("✗ 无法删除活跃分支，请先切换到其他分支")
            return False

        # 删除分支记忆
        cursor.execute("DELETE FROM branch_memories WHERE branch_id = ?", (branch_id,))

        # 删除分支
        cursor.execute("DELETE FROM branches WHERE id = ?", (branch_id,))

        conn.commit()
        conn.close()

        print(f"✓ 分支已删除: {branch_id}")
        return True


def main():
    parser = argparse.ArgumentParser(description='分支管理器')
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # create命令
    create_parser = subparsers.add_parser('create', help='创建新分支')
    create_parser.add_argument('name', help='分支名称')
    create_parser.add_argument('--parent', help='父分支ID')

    # checkout命令
    checkout_parser = subparsers.add_parser('checkout', help='切换分支')
    checkout_parser.add_argument('branch_id', help='分支ID')

    # merge命令
    merge_parser = subparsers.add_parser('merge', help='合并分支')
    merge_parser.add_argument('source', help='源分支ID')
    merge_parser.add_argument('--into', '--target', dest='target', required=True,
                             help='目标分支ID')
    merge_parser.add_argument('--resolve', action='store_true',
                             help='自动解决冲突')

    # list命令
    subparsers.add_parser('list', help='列出分支')

    # current命令
    subparsers.add_parser('current', help='显示当前分支')

    # diff命令
    diff_parser = subparsers.add_parser('diff', help='对比分支')
    diff_parser.add_argument('branch_a', help='分支A')
    diff_parser.add_argument('branch_b', help='分支B')

    # delete命令
    delete_parser = subparsers.add_parser('delete', help='删除分支')
    delete_parser.add_argument('branch_id', help='分支ID')
    delete_parser.add_argument('--force', action='store_true', help='强制删除')

    args = parser.parse_args()

    manager = BranchManager()

    if args.command == 'create':
        manager.create_branch(args.name, args.parent)

    elif args.command == 'checkout':
        manager.checkout(args.checkout)

    elif args.command == 'merge':
        manager.merge(args.source, args.target, args.resolve)

    elif args.command == 'list':
        manager.list_branches()

    elif args.command == 'current':
        current = manager.get_current_branch()
        if current:
            print(f"\n当前分支: {current['name']} ({current['id']})")
            print(f"创建于: {current['created']}")
        else:
            print("\n当前无活跃分支")

    elif args.command == 'diff':
        manager.diff(args.branch_a, args.branch_b)

    elif args.command == 'delete':
        manager.delete_branch(args.branch_id, args.force)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
