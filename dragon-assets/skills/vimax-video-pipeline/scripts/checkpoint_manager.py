#!/usr/bin/env python3
"""
ViMax Checkpoint Manager - 检查点管理器
支持流水线暂停/恢复、状态保存、JSON格式检查点
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class CheckpointManager:
    """ViMax检查点管理器"""

    def __init__(self, checkpoint_dir: str = "./vimax_checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def save(self, phase_name: str, phase_data: dict, metadata: Optional[dict] = None) -> str:
        """保存检查点"""
        checkpoint = {
            "phase": phase_name,
            "data": phase_data,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        }

        checkpoint_file = self.checkpoint_dir / f"{phase_name}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, ensure_ascii=False, indent=2)

        print(f"[Checkpoint] 已保存: {phase_name}")
        return str(checkpoint_file)

    def load(self, phase_name: str) -> Optional[dict]:
        """加载检查点"""
        checkpoint_file = self.checkpoint_dir / f"{phase_name}.json"

        if not checkpoint_file.exists():
            print(f"[Checkpoint] 未找到: {phase_name}")
            return None

        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)

        print(f"[Checkpoint] 已加载: {phase_name}")
        return checkpoint

    def list_checkpoints(self) -> list:
        """列出所有检查点"""
        checkpoints = []
        for f in self.checkpoint_dir.glob("*.json"):
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                checkpoints.append({
                    "phase": data["phase"],
                    "timestamp": data["timestamp"],
                    "file": str(f)
                })
        return sorted(checkpoints, key=lambda x: x["timestamp"])

    def delete(self, phase_name: str) -> bool:
        """删除检查点"""
        checkpoint_file = self.checkpoint_dir / f"{phase_name}.json"
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            print(f"[Checkpoint] 已删除: {phase_name}")
            return True
        return False

    def clear_all(self):
        """清除所有检查点"""
        for f in self.checkpoint_dir.glob("*.json"):
            f.unlink()
        print(f"[Checkpoint] 已清除所有检查点")


def main():
    parser = argparse.ArgumentParser(description="ViMax Checkpoint Manager")
    parser.add_argument("--save", metavar="PHASE", help="保存检查点")
    parser.add_argument("--load", metavar="PHASE", help="加载检查点")
    parser.add_argument("--list", action="store_true", help="列出所有检查点")
    parser.add_argument("--delete", metavar="PHASE", help="删除检查点")
    parser.add_argument("--clear", action="store_true", help="清除所有检查点")
    parser.add_argument("--dir", default="./vimax_checkpoints", help="检查点目录")
    parser.add_argument("--data", help="保存的数据(JSON格式)")

    args = parser.parse_args()
    manager = CheckpointManager(args.dir)

    if args.save:
        data = json.loads(args.data) if args.data else {}
        manager.save(args.save, data)

    elif args.load:
        checkpoint = manager.load(args.load)
        if checkpoint:
            print(json.dumps(checkpoint, ensure_ascii=False, indent=2))

    elif args.list:
        checkpoints = manager.list_checkpoints()
        print(f"[Checkpoint] 共 {len(checkpoints)} 个检查点:")
        for cp in checkpoints:
            print(f"  - {cp['phase']}: {cp['timestamp']}")

    elif args.delete:
        manager.delete(args.delete)

    elif args.clear:
        manager.clear_all()


if __name__ == "__main__":
    main()
