# -*- coding: utf-8 -*-
"""
DeadLetterQueue - 失败条目死信队列，支持人工介入
来源: blogger-distill-orchestration SKILL.md (lines 279-313)
"""

import json
import os
from datetime import datetime
from typing import Optional


class DeadLetterQueue:
    """失败条目死信队列，支持人工介入"""

    def __init__(self, path: str):
        self.path = path
        self.queue = self._load()

    # ── Persistence ──────────────────────────────────────────────────────────────

    def _load(self) -> list:
        if os.path.exists(self.path):
            try:
                return json.load(open(self.path, encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.queue, f, ensure_ascii=False, indent=2)

    # ── Core Operations ───────────────────────────────────────────────────────────

    def add(self, step: str, item_id: str, reason: str, traceback: str,
            extra: Optional[dict] = None):
        """添加失败条目到死信队列"""
        entry = {
            "step": step,
            "item_id": item_id,
            "reason": reason,
            "traceback": traceback,
            "timestamp": datetime.now().isoformat(),
            "retries": 0,
            "status": "pending",  # pending / resolved / abandoned
        }
        if extra:
            entry.update(extra)
        self.queue.append(entry)
        self._save()

    def retry(self, idx: int, max_retries: int = 3) -> bool:
        """重试指定条目（最多max_retries次）"""
        if 0 <= idx < len(self.queue):
            entry = self.queue[idx]
            if entry["retries"] < max_retries:
                entry["retries"] += 1
                entry["status"] = "pending"
                entry["last_retry"] = datetime.now().isoformat()
                self._save()
                return True
        return False

    def resolve(self, idx: int, resolution: str = ""):
        """标记条目为已解决"""
        if 0 <= idx < len(self.queue):
            self.queue[idx]["status"] = "resolved"
            self.queue[idx]["resolution"] = resolution
            self.queue[idx]["resolved_at"] = datetime.now().isoformat()
            self._save()

    def abandon(self, idx: int, reason: str = ""):
        """放弃条目"""
        if 0 <= idx < len(self.queue):
            self.queue[idx]["status"] = "abandoned"
            self.queue[idx]["abandon_reason"] = reason
            self.queue[idx]["abandoned_at"] = datetime.now().isoformat()
            self._save()

    # ── Reporting ────────────────────────────────────────────────────────────────

    def report(self, verbose: bool = False):
        """生成死信队列报告"""
        pending = [e for e in self.queue if e["status"] == "pending"]
        resolved = [e for e in self.queue if e["status"] == "resolved"]
        abandoned = [e for e in self.queue if e["status"] == "abandoned"]

        total = len(self.queue)
        print(f"\n{'='*60}")
        print(f"Dead Letter Queue Report — {self.path}")
        print(f"{'='*60}")
        print(f"Total: {total} | Pending: {len(pending)} | "
              f"Resolved: {len(resolved)} | Abandoned: {len(abandoned)}")

        if pending:
            print(f"\n{'─'*60}")
            print(f"Pending ({len(pending)}):")
            for i, e in enumerate(pending):
                print(f"  [{i}] [{e['step']}] {e['item_id']}")
                print(f"      Reason: {e['reason']}")
                print(f"      Retries: {e['retries']} | Since: {e['timestamp']}")
                if verbose and e.get("traceback"):
                    print(f"      Traceback:\n{e['traceback']}")

        if verbose and abandoned:
            print(f"\n{'─'*60}")
            print(f"Abandoned ({len(abandoned)}):")
            for e in abandoned:
                print(f"  [{e['step']}] {e['item_id']}: {e.get('abandon_reason', '')}")

        if verbose and resolved:
            print(f"\n{'─'*60}")
            print(f"Recently Resolved ({len(resolved)}):")
            for e in resolved[-5:]:
                print(f"  [{e['step']}] {e['item_id']} -> {e.get('resolution', '')}")

        print(f"{'='*60}\n")
        return {"total": total, "pending": len(pending),
                "resolved": len(resolved), "abandoned": len(abandoned)}

    # ── Utilities ────────────────────────────────────────────────────────────────

    def get(self, idx: int) -> Optional[dict]:
        """获取指定条目"""
        if 0 <= idx < len(self.queue):
            return self.queue[idx]
        return None

    def stats(self) -> dict:
        """返回统计摘要"""
        return {
            "total": len(self.queue),
            "pending": sum(1 for e in self.queue if e["status"] == "pending"),
            "resolved": sum(1 for e in self.queue if e["status"] == "resolved"),
            "abandoned": sum(1 for e in self.queue if e["status"] == "abandoned"),
            "by_step": self._by_step(),
        }

    def _by_step(self) -> dict:
        counts = {}
        for e in self.queue:
            step = e["step"]
            counts[step] = counts.get(step, 0) + 1
        return counts

    def clear(self, which: str = "resolved"):
        """清理已解决/已放弃的条目"""
        before = len(self.queue)
        if which == "resolved":
            self.queue = [e for e in self.queue if e["status"] != "resolved"]
        elif which == "abandoned":
            self.queue = [e for e in self.queue if e["status"] != "abandoned"]
        elif which == "all":
            self.queue = [e for e in self.queue if e["status"] == "pending"]
        self._save()
        print(f"Cleared {before - len(self.queue)} entries (kept {len(self.queue)})")

    def __len__(self):
        return len(self.queue)

    def __iter__(self):
        return iter(self.queue)

    def __repr__(self):
        pending = sum(1 for e in self.queue if e["status"] == "pending")
        return f"<DeadLetterQueue pending={pending} total={len(self.queue)}>"
