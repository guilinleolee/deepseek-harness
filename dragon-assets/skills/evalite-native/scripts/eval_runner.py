#!/usr/bin/env python3
"""
Evalite Native 评估运行器
Python 封装脚本，支持 Dragon SQLite 持久化
"""

import argparse
import asyncio
import json
import os
import subprocess
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Dragon SQLite 数据库路径
DRAGON_DB = Path.home() / ".claude" / "dragon_evals.db"


def init_dragon_db():
    """初始化 Dragon SQLite 数据库"""
    DRAGON_DB.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DRAGON_DB)
    cursor = conn.cursor()

    # 创建 dragon_runs 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dragon_runs (
            id TEXT PRIMARY KEY,
            started_at INTEGER NOT NULL,
            completed_at INTEGER,
            eval_name TEXT NOT NULL,
            status TEXT NOT NULL,
            total_evals INTEGER DEFAULT 0,
            passed_evals INTEGER DEFAULT 0,
            avg_score REAL DEFAULT 0.0
        )
    """)

    # 创建 dragon_evals 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dragon_evals (
            id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            input TEXT NOT NULL,
            expected TEXT,
            actual TEXT,
            score REAL,
            status TEXT DEFAULT 'pending',
            error TEXT,
            created_at INTEGER DEFAULT (strftime('%s', 'now')),
            FOREIGN KEY (run_id) REFERENCES dragon_runs(id)
        )
    """)

    # 创建 dragon_traces 表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dragon_traces (
            id TEXT PRIMARY KEY,
            eval_id TEXT NOT NULL,
            trace_json TEXT NOT NULL,
            created_at INTEGER DEFAULT (strftime('%s', 'now')),
            FOREIGN KEY (eval_id) REFERENCES dragon_evals(id)
        )
    """)

    # 创建索引
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_evals_run_id
        ON dragon_evals(run_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_traces_eval_id
        ON dragon_traces(eval_id)
    """)

    conn.commit()
    conn.close()
    print(f"✅ Dragon SQLite 数据库已初始化: {DRAGON_DB}")


def save_run(run_id: str, eval_name: str, status: str = "running"):
    """保存运行记录"""
    conn = sqlite3.connect(DRAGON_DB)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO dragon_runs (id, started_at, eval_name, status)
        VALUES (?, ?, ?, ?)
    """, (run_id, int(datetime.now().timestamp()), eval_name, status))

    conn.commit()
    conn.close()


def update_run(run_id: str, status: str, total: int = 0,
                passed: int = 0, avg_score: float = 0.0):
    """更新运行记录"""
    conn = sqlite3.connect(DRAGON_DB)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE dragon_runs
        SET completed_at = ?,
            status = ?,
            total_evals = ?,
            passed_evals = ?,
            avg_score = ?
        WHERE id = ?
    """, (int(datetime.now().timestamp()), status, total, passed, avg_score, run_id))

    conn.commit()
    conn.close()


def save_eval(eval_id: str, run_id: str, input_data: str,
              expected: Optional[str] = None,
              actual: Optional[str] = None,
              score: Optional[float] = None,
              status: str = "pending",
              error: Optional[str] = None):
    """保存评估记录"""
    conn = sqlite3.connect(DRAGON_DB)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO dragon_evals
        (id, run_id, input, expected, actual, score, status, error)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (eval_id, run_id, input_data, expected, actual, score, status, error))

    conn.commit()
    conn.close()


def save_trace(trace_id: str, eval_id: str, trace_json: str):
    """保存追踪记录"""
    conn = sqlite3.connect(DRAGON_DB)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO dragon_traces (id, eval_id, trace_json)
        VALUES (?, ?, ?)
    """, (trace_id, eval_id, trace_json))

    conn.commit()
    conn.close()


def parse_evalite_output(output: str) -> dict:
    """解析 Evalite 输出"""
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "evals": []
    }

    for line in output.split("\n"):
        if "✓" in line or "PASS" in line:
            results["passed"] += 1
        elif "✗" in line or "FAIL" in line:
            results["failed"] += 1

    results["total"] = results["passed"] + results["failed"]
    return results


def run_eval(args):
    """运行评估"""
    import uuid

    run_id = str(uuid.uuid4())
    eval_name = args.eval_name or "default"

    print(f"🚀 开始评估: {eval_name}")
    print(f"   Run ID: {run_id}")

    # 保存运行记录
    save_run(run_id, eval_name)

    # 构建命令
    cmd = ["npx", "evalite"]

    if args.watch:
        cmd.append("--watch")
    if args.output:
        cmd.extend(["--output", args.output])

    # 执行评估
    try:
        result = subprocess.run(
            cmd,
            cwd=args.project_dir or ".",
            capture_output=True,
            text=True,
            timeout=args.timeout or 300
        )

        # 解析输出
        output = result.stdout + result.stderr
        results = parse_evalite_output(output)

        # 更新运行记录
        avg_score = results["passed"] / results["total"] if results["total"] > 0 else 0.0
        update_run(
            run_id,
            status="completed" if result.returncode == 0 else "failed",
            total=results["total"],
            passed=results["passed"],
            avg_score=avg_score
        )

        # 输出结果
        print(f"\n📊 评估结果:")
        print(f"   总数: {results['total']}")
        print(f"   通过: {results['passed']} ✓")
        print(f"   失败: {results['failed']} ✗")
        print(f"   平均分: {avg_score:.2f}")
        print(f"\n💾 已保存到 Dragon SQLite: {DRAGON_DB}")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        update_run(run_id, status="timeout")
        print(f"❌ 评估超时 (>{args.timeout or 300}s)")
        return False
    except Exception as e:
        update_run(run_id, status="error")
        print(f"❌ 评估失败: {e}")
        return False


def show_history(args):
    """显示评估历史"""
    conn = sqlite3.connect(DRAGON_DB)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, eval_name, status, total_evals, passed_evals,
               avg_score, started_at, completed_at
        FROM dragon_runs
        ORDER BY started_at DESC
        LIMIT ?
    """, (args.limit or 20,))

    runs = cursor.fetchall()

    if not runs:
        print("📭 暂无评估历史")
        return

    print(f"\n📜 评估历史 (最近 {len(runs)} 条):\n")
    print(f"{'Run ID':<38} {'评估名':<20} {'状态':<10} {'分数':<8}")
    print("-" * 80)

    for run in runs:
        run_id, eval_name, status, total, passed, score, started, completed = run
        started_dt = datetime.fromtimestamp(started).strftime("%Y-%m-%d %H:%M")

        score_str = f"{score:.2f}" if score else "-"
        status_icon = "✓" if status == "completed" else "✗" if status == "failed" else "⏳"

        print(f"{run_id[:36]:<38} {eval_name:<20} {status_icon} {status:<8} {score_str:<8}")

    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Evalite Native 评估运行器")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # init 命令
    init_parser = subparsers.add_parser("init", help="初始化 Dragon SQLite 数据库")

    # run 命令
    run_parser = subparsers.add_parser("run", help="运行评估")
    run_parser.add_argument("eval_name", nargs="?", help="评估名称")
    run_parser.add_argument("--watch", action="store_true", help="观看模式")
    run_parser.add_argument("--output", choices=["table", "json"], help="输出格式")
    run_parser.add_argument("--project-dir", help="项目目录")
    run_parser.add_argument("--timeout", type=int, default=300, help="超时时间(秒)")

    # history 命令
    history_parser = subparsers.add_parser("history", help="显示评估历史")
    history_parser.add_argument("--limit", type=int, default=20, help="显示条数")

    args = parser.parse_args()

    if args.command == "init":
        init_dragon_db()
    elif args.command == "run":
        run_eval(args)
    elif args.command == "history":
        show_history(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
