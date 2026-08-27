#!/usr/bin/env python3
"""
Backlog Manager
Fanout Backlog管理系统
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class BacklogManager:
    """Fanout Backlog管理器"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data", "backlog.json"
            )
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_db()

    def _ensure_db(self):
        """确保数据库存在"""
        if not self.db_path.exists():
            self.db_path.write_text(
                json.dumps({"items": [], "last_updated": datetime.now().isoformat()}),
                encoding="utf-8"
            )

    def _read_db(self) -> Dict[str, Any]:
        """读取数据库"""
        return json.loads(self.db_path.read_text(encoding="utf-8"))

    def _write_db(self, data: Dict[str, Any]):
        """写入数据库"""
        data["last_updated"] = datetime.now().isoformat()
        self.db_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, topic: str, priority: str = "P1", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        添加Backlog项

        Args:
            topic: 主题
            priority: 优先级 (P0/P1/P2/P3)
            metadata: 元数据

        Returns:
            Dict: 添加的项
        """
        data = self._read_db()
        item_id = f"fanout-{len(data['items'])+1:04d}"

        item = {
            "id": item_id,
            "topic": topic,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "depth": metadata.get("depth", "full") if metadata else "full",
            "metadata": metadata or {}
        }

        data["items"].insert(0, item)
        self._write_db(data)

        return item

    def list_all(self) -> List[Dict[str, Any]]:
        """列出所有Backlog项"""
        data = self._read_db()
        items = data.get("items", [])

        priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        status_order = {"pending": 0, "running": 1, "completed": 2, "failed": 3}

        items.sort(key=lambda x: (
            priority_order.get(x.get("priority", "P2"), 1),
            status_order.get(x.get("status", "pending"), 1),
            x.get("created_at", "")
        ))

        return items

    def select_next(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        选择下一个要处理的项

        Args:
            limit: 最多选择数量

        Returns:
            List[Dict]: 待处理的项列表
        """
        pending = [item for item in self.list_all() if item.get("status") == "pending"]
        return pending[:limit]

    def mark_running(self, item_id: str) -> Optional[Dict[str, Any]]:
        """标记为运行中"""
        data = self._read_db()
        for item in data["items"]:
            if item["id"] == item_id:
                item["status"] = "running"
                item["updated_at"] = datetime.now().isoformat()
                self._write_db(data)
                return item
        return None

    def mark_completed(self, item_id: str) -> Optional[Dict[str, Any]]:
        """标记为已完成"""
        data = self._read_db()
        for item in data["items"]:
            if item["id"] == item_id:
                item["status"] = "completed"
                item["completed_at"] = datetime.now().isoformat()
                item["updated_at"] = datetime.now().isoformat()
                self._write_db(data)
                return item
        return None

    def mark_failed(self, item_id: str, error: str = None) -> Optional[Dict[str, Any]]:
        """标记为失败"""
        data = self._read_db()
        for item in data["items"]:
            if item["id"] == item_id:
                item["status"] = "failed"
                item["error"] = error
                item["updated_at"] = datetime.now().isoformat()
                self._write_db(data)
                return item
        return None

    def retry(self, item_id: str) -> Optional[Dict[str, Any]]:
        """重试失败的项"""
        data = self._read_db()
        for item in data["items"]:
            if item["id"] == item_id and item.get("status") == "failed":
                item["status"] = "pending"
                item["retry_count"] = item.get("retry_count", 0) + 1
                item["updated_at"] = datetime.now().isoformat()
                self._write_db(data)
                return item
        return None

    def delete(self, item_id: str) -> bool:
        """删除项"""
        data = self._read_db()
        original_count = len(data["items"])
        data["items"] = [item for item in data["items"] if item["id"] != item_id]

        if len(data["items"]) < original_count:
            self._write_db(data)
            return True
        return False

    def update_priority(self, item_id: str, priority: str) -> Optional[Dict[str, Any]]:
        """更新优先级"""
        data = self._read_db()
        for item in data["items"]:
            if item["id"] == item_id:
                item["priority"] = priority
                item["updated_at"] = datetime.now().isoformat()
                self._write_db(data)
                return item
        return None

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        items = self.list_all()

        stats = {
            "total": len(items),
            "by_status": {},
            "by_priority": {},
            "recent_failures": []
        }

        for item in items:
            status = item.get("status", "unknown")
            priority = item.get("priority", "unknown")

            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1

            if status == "failed":
                stats["recent_failures"].append({
                    "id": item["id"],
                    "topic": item["topic"],
                    "error": item.get("error", ""),
                    "failed_at": item.get("updated_at", "")
                })

        stats["recent_failures"] = stats["recent_failures"][:5]
        return stats

    def export_to_csv(self, filepath: str):
        """导出为CSV"""
        import csv

        items = self.list_all()
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "topic", "priority", "status", "created_at"])
            writer.writeheader()
            for item in items:
                writer.writerow({
                    "id": item["id"],
                    "topic": item["topic"],
                    "priority": item["priority"],
                    "status": item["status"],
                    "created_at": item["created_at"]
                })

    def import_from_csv(self, filepath: str) -> int:
        """从CSV导入"""
        import csv

        count = 0
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.add(
                    topic=row["topic"],
                    priority=row.get("priority", "P1"),
                    metadata={"imported": True}
                )
                count += 1

        return count
