#!/usr/bin/env python3
"""
free-claude-remote-session - 会话管理器
管理 Claude Code 会话的生命周期
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

SKILL_DIR = Path(__file__).parent.parent
DB_PATH = SKILL_DIR / "logs" / "sessions.db"


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """确保数据库和sessions表存在"""
    LOG_DIR = SKILL_DIR / "logs"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            im_platform TEXT NOT NULL,
            im_user_id TEXT NOT NULL,
            im_chat_id TEXT NOT NULL,
            status TEXT DEFAULT 'created',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            task_summary TEXT DEFAULT ''
        )
    """)
    conn.commit()
    conn.close()


def cmd_list(platform: Optional[str], status: Optional[str]) -> bool:
    """列出所有会话"""
    init_db()
    conn = get_db()
    c = conn.cursor()

    query = "SELECT * FROM sessions"
    conditions = []
    params = []

    if platform:
        conditions.append("im_platform = ?")
        params.append(platform)
    if status:
        conditions.append("status = ?")
        params.append(status)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY updated_at DESC"

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("  无会话记录")
        return True

    print(f"\n  {'ID':20s} {'平台':10s} {'状态':12s} {'创建时间':19s} {'摘要':30s}")
    print("  " + "-" * 95)

    status_icon = {
        "created": "🆕", "running": "🟢", "paused": "⏸️",
        "waiting_input": "💬", "completed": "✅", "failed": "❌", "cancelled": "🚫"
    }

    for row in rows:
        sid = row["session_id"][:20]
        plat = row["im_platform"][:10]
        st = row["status"][:12]
        icon = status_icon.get(row["status"], "❓")
        created = row["created_at"][:19]
        summary = row["task_summary"][:28] if row["task_summary"] else ""

        print(f"  {sid:20s} {plat:10s} {icon} {st:10s} {created:19s} {summary:30s}")

    print(f"\n  共 {len(rows)} 个会话\n")
    return True


def cmd_resume(session_id: str) -> bool:
    """恢复指定会话"""
    init_db()
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        print(f"  🔴 会话不存在: {session_id}")
        return False

    status = row["status"]
    if status in ["completed", "failed", "cancelled"]:
        print(f"  🔴 会话状态为 {status}，无法恢复")
        return False

    print(f"\n  恢复会话: {session_id}")
    print(f"  平台: {row['im_platform']}")
    print(f"  用户: {row['im_user_id']}")
    print(f"  状态: {row['status']}")
    print(f"  创建: {row['created_at']}")
    if row["task_summary"]:
        print(f"  摘要: {row['task_summary']}")

    # TODO: 实现与 Dragon Gateway 的实际恢复通信
    # 目前仅更新状态
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        UPDATE sessions
        SET status = 'running', updated_at = ?
        WHERE session_id = ?
    """, (datetime.now().isoformat(), session_id))
    conn.commit()
    conn.close()

    print(f"  ✅ 会话已恢复")
    return True


def cmd_export(session_id: str, format: str) -> bool:
    """导出会话"""
    init_db()
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        print(f"  🔴 会话不存在: {session_id}")
        return False

    data = dict(row)

    if format == "json":
        output = json.dumps(data, indent=2, ensure_ascii=False)
        print(output)
    elif format == "csv":
        if not data:
            print("  无数据")
            return True
        headers = list(data.keys())
        values = [str(v) for v in data.values()]
        print(",".join(headers))
        print(",".join(f'"{v}"' for v in values))
    else:
        print(f"  🔴 不支持的格式: {format}")
        return False

    return True


def cmd_cancel(session_id: str) -> bool:
    """取消会话"""
    init_db()
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT status FROM sessions WHERE session_id = ?", (session_id,))
    row = c.fetchone()

    if not row:
        print(f"  🔴 会话不存在: {session_id}")
        conn.close()
        return False

    if row["status"] in ["completed", "failed", "cancelled"]:
        print(f"  🔴 会话状态已是 {row['status']}")
        conn.close()
        return False

    c.execute("""
        UPDATE sessions
        SET status = 'cancelled', updated_at = ?
        WHERE session_id = ?
    """, (datetime.now().isoformat(), session_id))
    conn.commit()
    conn.close()

    print(f"  ✅ 会话已取消: {session_id}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Session Manager")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # list
    p_list = subparsers.add_parser("list", help="列出所有会话")
    p_list.add_argument("--platform", choices=["telegram", "discord", "feishu", "qq"],
                        help="按平台筛选")
    p_list.add_argument("--status", choices=["created", "running", "paused",
                            "waiting_input", "completed", "failed", "cancelled"],
                        help="按状态筛选")

    # resume
    p_resume = subparsers.add_parser("resume", help="恢复会话")
    p_resume.add_argument("session_id", help="会话ID")

    # export
    p_export = subparsers.add_parser("export", help="导出会话")
    p_export.add_argument("session_id", help="会话ID")
    p_export.add_argument("--format", choices=["json", "csv"], default="json",
                          help="导出格式")

    # cancel
    p_cancel = subparsers.add_parser("cancel", help="取消会话")
    p_cancel.add_argument("session_id", help="会话ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "list":
        sys.exit(0 if cmd_list(
            getattr(args, "platform", None),
            getattr(args, "status", None)
        ) else 1)
    elif args.command == "resume":
        sys.exit(0 if cmd_resume(args.session_id) else 1)
    elif args.command == "export":
        sys.exit(0 if cmd_export(args.session_id, args.format) else 1)
    elif args.command == "cancel":
        sys.exit(0 if cmd_cancel(args.session_id) else 1)


if __name__ == "__main__":
    main()
