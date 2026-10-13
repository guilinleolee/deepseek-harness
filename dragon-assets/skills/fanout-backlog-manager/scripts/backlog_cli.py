#!/usr/bin/env python3
"""
Fanout Backlog Manager CLI
GEO内容生产任务队列管理工具
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 配置路径
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
BACKLOG_FILE = DATA_DIR / "backlog.json"
ARCHIVE_DIR = DATA_DIR / "archive"

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


def load_backlog() -> dict:
    """加载backlog数据"""
    if BACKLOG_FILE.exists():
        with open(BACKLOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tasks": [], "version": "1.0", "updated_at": datetime.now().isoformat()}


def save_backlog(data: dict) -> None:
    """保存backlog数据"""
    data["updated_at"] = datetime.now().isoformat()
    with open(BACKLOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_task_id() -> str:
    """生成唯一任务ID"""
    import uuid
    return f"GEO-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def add_task(brief_id: str, priority: str = "P2", title: str = "", targets: list = None) -> dict:
    """创建新任务"""
    backlog = load_backlog()

    task = {
        "task_id": generate_task_id(),
        "brief_id": brief_id,
        "title": title,
        "priority": priority,
        "status": "drafting",
        "gates": {
            "L1": {"status": "pending", "passed": False, "notes": ""},
            "L2": {"status": "pending", "passed": False, "notes": ""},
            "L3": {"status": "pending", "passed": False, "notes": ""},
            "L4": {"status": "pending", "passed": False, "notes": ""},
            "L5": {"status": "pending", "passed": False, "notes": ""},
        },
        "fanout_targets": targets or ["wordpress"],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    backlog["tasks"].append(task)
    save_backlog(backlog)

    return task


def list_tasks(status: Optional[str] = None, priority: Optional[str] = None) -> list:
    """列出任务"""
    backlog = load_backlog()
    tasks = backlog["tasks"]

    if status:
        tasks = [t for t in tasks if t["status"] == status]
    if priority:
        priorities = priority.split(",")
        tasks = [t for t in tasks if t["priority"] in priorities]

    # 按优先级和创建时间排序
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    tasks.sort(key=lambda x: (priority_order.get(x["priority"], 4), x["created_at"]))

    return tasks


def update_task(task_id: str, status: Optional[str] = None, gate: Optional[str] = None,
                gate_status: Optional[str] = None, notes: Optional[str] = None) -> Optional[dict]:
    """更新任务状态"""
    backlog = load_backlog()

    for task in backlog["tasks"]:
        if task["task_id"] == task_id:
            if status:
                task["status"] = status

            if gate and gate_status:
                if gate in task["gates"]:
                    task["gates"][gate]["status"] = gate_status
                    if gate_status == "passed":
                        task["gates"][gate]["passed"] = True
                    if notes:
                        task["gates"][gate]["notes"] = notes

            task["updated_at"] = datetime.now().isoformat()
            save_backlog(backlog)
            return task

    return None


def archive_task(task_id: str) -> bool:
    """归档任务"""
    backlog = load_backlog()

    for i, task in enumerate(backlog["tasks"]):
        if task["task_id"] == task_id:
            # 移动到归档
            task["archived_at"] = datetime.now().isoformat()
            archived_file = ARCHIVE_DIR / f"{task_id}.json"
            with open(archived_file, "w", encoding="utf-8") as f:
                json.dump(task, f, ensure_ascii=False, indent=2)

            # 从backlog移除
            backlog["tasks"].pop(i)
            save_backlog(backlog)
            return True

    return False


def print_task(task: dict, verbose: bool = False) -> None:
    """打印任务信息"""
    priority_icon = {"P0": "🔴", "P1": "🟠", "P2": "🟡", "P3": "🟢"}.get(task["priority"], "⚪")
    status_icon = {
        "drafting": "📝",
        "reviewing": "🔍",
        "published": "✅",
        "archived": "📦"
    }.get(task["status"], "❓")

    print(f"\n{priority_icon} {task['task_id']} {status_icon} {task['status']}")
    print(f"   Brief: {task['brief_id']}")
    if task.get("title"):
        print(f"   Title: {task['title']}")

    if verbose:
        print(f"   Priority: {task['priority']}")
        print(f"   Created: {task['created_at']}")
        print(f"   Updated: {task['updated_at']}")
        print(f"   Fanout Targets: {', '.join(task['fanout_targets'])}")

        print("   Quality Gates:")
        for gate, info in task["gates"].items():
            icon = "✅" if info["passed"] else "⬜"
            print(f"      {icon} {gate}: {info['status']}")


def main():
    parser = argparse.ArgumentParser(description="Fanout Backlog Manager CLI")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # add命令
    add_parser = subparsers.add_parser("add", help="创建新任务")
    add_parser.add_argument("--brief", required=True, help="Editorial Brief ID")
    add_parser.add_argument("--priority", default="P2", choices=["P0", "P1", "P2", "P3"], help="优先级")
    add_parser.add_argument("--title", default="", help="任务标题")
    add_parser.add_argument("--targets", nargs="+", default=["wordpress"], help="发布目标")

    # list命令
    list_parser = subparsers.add_parser("list", help="列出任务")
    list_parser.add_argument("--status", help="按状态筛选")
    list_parser.add_argument("--priority", help="按优先级筛选(逗号分隔)")
    list_parser.add_argument("-v", "--verbose", action="store_true", help="详细信息")

    # update命令
    update_parser = subparsers.add_parser("update", help="更新任务")
    update_parser.add_argument("task_id", help="任务ID")
    update_parser.add_argument("--status", help="新状态")
    update_parser.add_argument("--gate", help="质量门控层(L1-L5)")
    update_parser.add_argument("--gate-status", choices=["pending", "passed", "failed"], help="门控状态")
    update_parser.add_argument("--notes", help="备注")

    # archive命令
    archive_parser = subparsers.add_parser("archive", help="归档任务")
    archive_parser.add_argument("task_id", help="任务ID")

    args = parser.parse_args()

    if args.command == "add":
        task = add_task(args.brief, args.priority, args.title, args.targets)
        print(f"✅ 创建任务: {task['task_id']}")
        print_task(task)

    elif args.command == "list":
        tasks = list_tasks(args.status, args.priority)
        print(f"\n📋 任务列表 (共 {len(tasks)} 个)")
        print("=" * 60)
        for task in tasks:
            print_task(task, args.verbose)

    elif args.command == "update":
        task = update_task(args.task_id, args.status, args.gate, args.gate_status, args.notes)
        if task:
            print(f"✅ 更新任务: {task['task_id']}")
            print_task(task)
        else:
            print(f"❌ 未找到任务: {args.task_id}")
            sys.exit(1)

    elif args.command == "archive":
        if archive_task(args.task_id):
            print(f"✅ 归档任务: {args.task_id}")
        else:
            print(f"❌ 未找到任务: {args.task_id}")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
