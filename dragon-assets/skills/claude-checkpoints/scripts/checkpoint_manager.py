#!/usr/bin/env python3
"""
Claude Checkpoints Manager
会话快照与回滚管理系统

功能:
- checkpoint_save: 保存当前会话状态
- checkpoint_list: 列出所有快照
- checkpoint_restore: 恢复到指定快照
- checkpoint_diff: 对比两个快照
- checkpoint_delete: 删除快照
"""

import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
import argparse

# 检查点目录
CHECKPOINTS_DIR = Path.home() / ".claude" / "checkpoints"
INDEX_FILE = CHECKPOINTS_DIR / "index.json"


def ensure_dir():
    """确保检查点目录存在"""
    CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)


def load_index() -> dict:
    """加载索引文件"""
    ensure_dir()
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"checkpoints": [], "version": "1.0"}


def save_index(index: dict):
    """保存索引文件"""
    ensure_dir()
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


def checkpoint_save(name: str, description: str = "") -> str:
    """
    保存当前会话状态为快照

    Args:
        name: 快照名称
        description: 快照描述

    Returns:
        快照ID
    """
    ensure_dir()

    checkpoint_id = f"checkpoint-{uuid.uuid4().hex[:8]}"
    checkpoint_dir = CHECKPOINTS_DIR / checkpoint_id
    checkpoint_dir.mkdir(exist_ok=True)

    # 会话状态
    session_state = {
        "timestamp": datetime.now().isoformat(),
        "name": name,
        "description": description,
        "cwd": os.getcwd(),
    }

    # Git状态
    git_state = {"has_git": False}
    try:
        import subprocess
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5
        )
        git_state = {
            "has_git": True,
            "status": result.stdout,
            "branch": subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True
            ).stdout.strip()
        }
    except:
        pass

    # 保存文件
    files = {
        "session.json": session_state,
        "git-state.json": git_state,
    }

    for filename, data in files.items():
        with open(checkpoint_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # 更新索引
    index = load_index()
    index["checkpoints"].append({
        "id": checkpoint_id,
        "name": name,
        "description": description,
        "timestamp": datetime.now().isoformat(),
        "path": str(checkpoint_dir)
    })
    save_index(index)

    return checkpoint_id


def checkpoint_list() -> list:
    """列出所有快照"""
    index = load_index()
    return sorted(index["checkpoints"],
                  key=lambda x: x["timestamp"],
                  reverse=True)


def checkpoint_restore(checkpoint_id: str) -> bool:
    """
    恢复到指定快照

    Args:
        checkpoint_id: 快照ID

    Returns:
        是否成功
    """
    checkpoint_dir = CHECKPOINTS_DIR / checkpoint_id
    if not checkpoint_dir.exists():
        print(f"❌ 快照不存在: {checkpoint_id}")
        return False

    # 读取会话状态
    session_file = checkpoint_dir / "session.json"
    if session_file.exists():
        with open(session_file, 'r', encoding='utf-8') as f:
            session = json.load(f)
            print(f"📍 恢复目标目录: {session.get('cwd', 'unknown')}")

    print(f"✅ 已加载快照: {checkpoint_id}")
    print(f"💡 请使用以下命令恢复会话:")
    print(f"   claude --resume --checkpoint {checkpoint_id}")
    return True


def checkpoint_diff(id1: str, id2: str) -> dict:
    """对比两个快照"""
    diff_result = {
        "checkpoint1": id1,
        "checkpoint2": id2,
        "differences": []
    }

    for cp_id in [id1, id2]:
        cp_dir = CHECKPOINTS_DIR / cp_id
        if cp_dir.exists():
            git_file = cp_dir / "git-state.json"
            if git_file.exists():
                with open(git_file, 'r', encoding='utf-8') as f:
                    diff_result["differences"].append({
                        "id": cp_id,
                        "git_state": json.load(f)
                    })

    return diff_result


def checkpoint_delete(checkpoint_id: str) -> bool:
    """删除指定快照"""
    import shutil

    checkpoint_dir = CHECKPOINTS_DIR / checkpoint_id
    if not checkpoint_dir.exists():
        print(f"❌ 快照不存在: {checkpoint_id}")
        return False

    # 删除目录
    shutil.rmtree(checkpoint_dir)

    # 更新索引
    index = load_index()
    index["checkpoints"] = [
        cp for cp in index["checkpoints"]
        if cp["id"] != checkpoint_id
    ]
    save_index(index)

    print(f"✅ 已删除快照: {checkpoint_id}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Claude Checkpoints Manager")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # save 命令
    save_parser = subparsers.add_parser("save", help="保存快照")
    save_parser.add_argument("name", help="快照名称")
    save_parser.add_argument("--desc", "-d", default="", help="快照描述")

    # list 命令
    subparsers.add_parser("list", help="列出快照")

    # restore 命令
    restore_parser = subparsers.add_parser("restore", help="恢复快照")
    restore_parser.add_argument("id", help="快照ID")

    # diff 命令
    diff_parser = subparsers.add_parser("diff", help="对比快照")
    diff_parser.add_argument("id1", help="快照ID1")
    diff_parser.add_argument("id2", help="快照ID2")

    # delete 命令
    delete_parser = subparsers.add_parser("delete", help="删除快照")
    delete_parser.add_argument("id", help="快照ID")

    args = parser.parse_args()

    if args.command == "save":
        checkpoint_id = checkpoint_save(args.name, args.desc)
        print(f"✅ 已保存快照: {checkpoint_id}")

    elif args.command == "list":
        checkpoints = checkpoint_list()
        print(f"\n📋 检查点列表 ({len(checkpoints)} 个)\n")
        print(f"{'ID':<20} {'名称':<25} {'时间':<25}")
        print("-" * 70)
        for cp in checkpoints:
            ts = cp["timestamp"][:19].replace("T", " ")
            print(f"{cp['id']:<20} {cp['name']:<25} {ts:<25}")

    elif args.command == "restore":
        checkpoint_restore(args.id)

    elif args.command == "diff":
        result = checkpoint_diff(args.id1, args.id2)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "delete":
        checkpoint_delete(args.id)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
