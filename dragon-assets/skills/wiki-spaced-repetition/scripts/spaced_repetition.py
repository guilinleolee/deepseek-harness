#!/usr/bin/env python3
"""
Wiki 间隔重复复习引擎
基于 SM-2 算法自动追踪 Wiki 笔记复习周期

Usage:
    python3 spaced_repetition.py --due
    python3 spaced_repetition.py --review "note_id" --quality 4
    python3 spaced_repetition.py --queue
    python3 spaced_repetition.py --note "note_id"
    python3 spaced_repetition.py --stats
"""

import argparse
import json
import yaml
import time
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Optional


WIKI_DIR = Path.home() / ".claude" / "wiki"
QUEUE_DIR = Path.home() / ".claude" / "wiki_review_queue"
QUEUE_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class ReviewRecord:
    """复习记录"""
    date: str
    quality: int  # 0-5
    interval: int   # 天数
    ef: float      # 简易度因子
    next_review: str


@dataclass
class NoteReview:
    """笔记复习信息"""
    note_id: str
    title: str
    added_at: str
    reviews: list = field(default_factory=list)
    due_reviews: int = 0
    total_reviews: int = 0
    streak: int = 0
    ef: float = 2.5
    interval: int = 1
    next_review: str = ""
    tags: list = field(default_factory=list)
    archive_count: int = 0
    reference_count: int = 0


class SpacedRepetition:
    """SM-2 间隔重复引擎"""

    # SM-2 算法参数
    INITIAL_INTERVAL = 1    # 首次复习间隔（天）
    SECOND_INTERVAL = 6     # 第二次复习间隔（天）
    INITIAL_EF = 2.5        # 初始简易度因子
    MIN_EF = 1.3            # EF 下限

    # 复利因子参数
    ARCHIVE_WEIGHT = 0.05   # 归档次数权重
    REFERENCE_WEIGHT = 0.1   # 引用次数权重

    def __init__(self, queue_dir: Optional[Path] = None):
        self.queue_dir = queue_dir or QUEUE_DIR
        self.queue_dir.mkdir(parents=True, exist_ok=True)

    def _note_path(self, note_id: str) -> Path:
        return self.queue_dir / f"{note_id}.yaml"

    def _load_note(self, note_id: str) -> Optional[NoteReview]:
        """加载笔记复习信息"""
        path = self._note_path(note_id)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not data:
                return None
            reviews = [ReviewRecord(**r) for r in data.get("reviews", [])]
            return NoteReview(
                note_id=data["note_id"],
                title=data["title"],
                added_at=data["added_at"],
                reviews=reviews,
                due_reviews=data.get("due_reviews", 0),
                total_reviews=data.get("total_reviews", 0),
                streak=data.get("streak", 0),
                ef=data.get("ef", self.INITIAL_EF),
                interval=data.get("interval", self.INITIAL_INTERVAL),
                next_review=data.get("next_review", ""),
                tags=data.get("tags", []),
                archive_count=data.get("archive_count", 0),
                reference_count=data.get("reference_count", 0),
            )
        except Exception:
            return None

    def _save_note(self, note: NoteReview):
        """保存笔记复习信息"""
        path = self._note_path(note.note_id)
        data = {
            "note_id": note.note_id,
            "title": note.title,
            "added_at": note.added_at,
            "reviews": [asdict(r) for r in note.reviews],
            "due_reviews": note.due_reviews,
            "total_reviews": note.total_reviews,
            "streak": note.streak,
            "ef": note.ef,
            "interval": note.interval,
            "next_review": note.next_review,
            "tags": note.tags,
            "archive_count": note.archive_count,
            "reference_count": note.reference_count,
        }
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, default_flow_style=False)

    def _calculate_ef(self, current_ef: float, quality: int) -> float:
        """根据质量评分调整 EF"""
        # SM-2 EF 调整公式
        # q=0: EF-0.8, q=1: EF-0.18, q=2: EF-0.08, q=3: EF不变, q=4: EF+0.1, q=5: EF+0.15
        adjustments = {
            0: -0.8,
            1: -0.18,
            2: -0.08,
            3: 0.0,
            4: 0.1,
            5: 0.15,
        }
        new_ef = current_ef + adjustments.get(quality, 0.0)
        return max(self.MIN_EF, new_ef)

    def _calculate_interval(self, review_num: int, ef: float, base_interval: int) -> int:
        """计算下次复习间隔"""
        if review_num == 0:
            return self.INITIAL_INTERVAL
        elif review_num == 1:
            return self.SECOND_INTERVAL
        else:
            # I(n) = I(n-1) × EF
            return int(base_interval * ef)

    def _calculate_compound_factor(self, note: NoteReview) -> float:
        """计算复利因子"""
        return 1.0 + (note.archive_count * self.ARCHIVE_WEIGHT) + (note.reference_count * self.REFERENCE_WEIGHT)

    def _is_due(self, note: NoteReview) -> bool:
        """检查笔记是否到期需要复习"""
        if not note.next_review:
            return True
        try:
            next_date = date.fromisoformat(note.next_review)
            return date.today() >= next_date
        except ValueError:
            return True

    def add_note(self, note_id: str, title: str, tags: list = None, archive_count: int = 0, reference_count: int = 0):
        """添加笔记到复习队列"""
        if self._load_note(note_id):
            return False  # 已存在

        today = date.today().isoformat()
        note = NoteReview(
            note_id=note_id,
            title=title,
            added_at=today,
            tags=tags or [],
            archive_count=archive_count,
            reference_count=reference_count,
            next_review=today,  # 新笔记立即可复习
        )
        self._save_note(note)
        return True

    def increment_reference(self, note_id: str):
        """笔记被引用时调用，增加复利因子"""
        note = self._load_note(note_id)
        if note:
            note.reference_count += 1
            self._save_note(note)

    def increment_archive(self, note_id: str):
        """笔记被归档时调用，增加复利因子"""
        note = self._load_note(note_id)
        if note:
            note.archive_count += 1
            self._save_note(note)

    def record_review(self, note_id: str, quality: int) -> Optional[NoteReview]:
        """记录一次复习结果"""
        note = self._load_note(note_id)
        if not note:
            return None

        if quality < 0 or quality > 5:
            quality = 3

        today = date.today().isoformat()
        review_count = len(note.reviews)

        # 更新 EF
        new_ef = self._calculate_ef(note.ef, quality)
        note.ef = new_ef

        # 计算复利因子
        compound_factor = self._calculate_compound_factor(note)

        # 计算新间隔
        base_interval = self._calculate_interval(review_count, new_ef, note.interval)
        adjusted_interval = int(base_interval * compound_factor)

        # 极差回忆(0-1)时缩短间隔
        if quality <= 1:
            adjusted_interval = max(1, adjusted_interval // 2)
        # 完美回忆(5)时略微延长
        elif quality == 5:
            adjusted_interval = int(adjusted_interval * 1.1)

        # 记录复习
        review = ReviewRecord(
            date=today,
            quality=quality,
            interval=adjusted_interval,
            ef=new_ef,
            next_review=(date.today() + timedelta(days=adjusted_interval)).isoformat(),
        )
        note.reviews.append(review)

        # 更新状态
        note.interval = adjusted_interval
        note.next_review = review.next_review
        note.total_reviews += 1
        note.due_reviews = 0

        # 更新连续复习天数
        if quality >= 3:
            note.streak += 1
        else:
            note.streak = 0

        self._save_note(note)
        return note

    def get_note(self, note_id: str) -> Optional[NoteReview]:
        """获取笔记复习信息"""
        return self._load_note(note_id)

    def get_due_reviews(self) -> list[NoteReview]:
        """获取所有到期的复习笔记"""
        notes = []
        for path in self.queue_dir.glob("*.yaml"):
            note = self._load_note(path.stem)
            if note and self._is_due(note):
                notes.append(note)
        return notes

    def get_queue(self) -> list[NoteReview]:
        """获取所有复习队列笔记（按优先级排序）"""
        notes = []
        for path in self.queue_dir.glob("*.yaml"):
            note = self._load_note(path.stem)
            if note:
                notes.append(note)

        def priority_key(n: NoteReview):
            today = date.today()
            try:
                days_until = (date.fromisoformat(n.next_review) - today).days if n.next_review else 0
            except ValueError:
                days_until = 0

            # 优先级：遗忘临界 > 高引用 > 新归档 > 陈旧
            if days_until < 0:
                score = -1000 - days_until  # 逾期越久越优先
            elif days_until == 0:
                score = 100
            elif days_until <= 1:
                score = 90
            else:
                score = 80 - days_until

            # 引用越多越优先
            score += n.reference_count * 0.5
            # 归档越多越优先
            score += n.archive_count * 0.3

            return score

        return sorted(notes, key=priority_key, reverse=True)

    def get_stats(self) -> dict:
        """获取复习统计"""
        notes = list(self.queue_dir.glob("*.yaml"))
        total = len(notes)

        due = 0
        total_reviews = 0
        total_streak = 0
        by_quality = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        for path in notes:
            note = self._load_note(path.stem)
            if note:
                if self._is_due(note):
                    due += 1
                total_reviews += note.total_reviews
                total_streak += note.streak
                if note.reviews:
                    last_q = note.reviews[-1].quality
                    by_quality[last_q] = by_quality.get(last_q, 0) + 1

        return {
            "total_notes": total,
            "due_reviews": due,
            "total_reviews": total_reviews,
            "avg_streak": total_streak / total if total else 0,
            "avg_quality": sum(k * v for k, v in by_quality.items()) / sum(by_quality.values()) if by_quality.values() else 0,
            "by_last_quality": by_quality,
        }

    def get_forgetting_curve_data(self, note_id: str) -> dict:
        """生成遗忘曲线数据"""
        note = self._load_note(note_id)
        if not note:
            return {}

        reviews = note.reviews
        if not reviews:
            return {"intervals": [1, 3, 7, 14, 30, 60], "retention": [100, 80, 60, 40, 25, 15]}

        # 基于实际复习数据计算
        retention_data = []
        days = [1, 3, 7, 14, 30, 60]
        for d in days:
            if d == 1:
                r = 100
            else:
                # 简化遗忘曲线模型
                r = max(5, int(100 * (0.9 ** (d / reviews[-1].interval if reviews[-1].interval else 1)))
            retention_data.append(r)

        return {
            "note_id": note_id,
            "title": note.title,
            "intervals": days,
            "retention": retention_data,
            "current_ef": note.ef,
            "current_interval": note.interval,
        }


def main():
    parser = argparse.ArgumentParser(description="Wiki 间隔重复复习引擎")
    parser.add_argument("--due", action="store_true", help="获取到期的复习笔记")
    parser.add_argument("--queue", action="store_true", help="获取复习队列")
    parser.add_argument("--note", help="获取指定笔记信息")
    parser.add_argument("--review", help="记录复习结果")
    parser.add_argument("--quality", type=int, help="复习质量评分 (0-5)")
    parser.add_argument("--add", nargs=2, metavar=("ID", "TITLE"), help="添加笔记到复习队列")
    parser.add_argument("--stats", action="store_true", help="获取复习统计")
    parser.add_argument("--curve", help="获取遗忘曲线数据")

    args = parser.parse_args()
    sr = SpacedRepetition()

    if args.due:
        due = sr.get_due_reviews()
        print(f"📚 待复习笔记 ({len(due)} 条):")
        for note in due[:20]:
            print(f"  [{note.note_id}] {note.title}")
            print(f"    上次复习: {note.reviews[-1].next_review if note.reviews else '从未复习'}")
            print(f"    连续天数: {note.streak}")

    elif args.queue:
        queue = sr.get_queue()
        stats = sr.get_stats()
        print(f"📊 复习队列概览:")
        print(f"  总笔记数: {stats['total_notes']}")
        print(f"  到期复习: {stats['due_reviews']}")
        print(f"  总复习次数: {stats['total_reviews']}")
        print(f"  平均连续天数: {stats['avg_streak']:.1f}")
        print(f"  平均质量: {stats['avg_quality']:.2f}")
        print()
        print(f"📋 复习队列 (优先级排序):")
        for note in queue[:20]:
            marker = "🔴" if sr._is_due(note) else "  "
            print(f"  {marker} [{note.note_id}] {note.title}")
            print(f"     下次复习: {note.next_review} | 间隔: {note.interval}天 | EF: {note.ef:.2f}")

    elif args.note:
        note = sr.get_note(args.note)
        if note:
            print(f"📄 笔记: {note.title}")
            print(f"   添加日期: {note.added_at}")
            print(f"   总复习次数: {note.total_reviews}")
            print(f"   连续复习天数: {note.streak}")
            print(f"   当前间隔: {note.interval} 天")
            print(f"   EF: {note.ef:.2f}")
            print(f"   下次复习: {note.next_review}")
            print(f"   归档次数: {note.archive_count}")
            print(f"   引用次数: {note.reference_count}")
            if note.reviews:
                print(f"   最近复习:")
                for r in note.reviews[-3:]:
                    print(f"     - {r.date}: q={r.quality}, 间隔={r.interval}天")
        else:
            print(f"笔记 {args.note} 不在复习队列中")

    elif args.review:
        if args.quality is None:
            print("错误: --review 需要配合 --quality 参数")
            return
        result = sr.record_review(args.review, args.quality)
        if result:
            print(f"✅ 复习记录已保存")
            print(f"   笔记: {result.title}")
            print(f"   质量评分: {args.quality}")
            print(f"   新间隔: {result.interval} 天")
            print(f"   EF: {result.ef:.2f}")
            print(f"   下次复习: {result.next_review}")
        else:
            print(f"笔记 {args.review} 不在复习队列中")

    elif args.add:
        note_id, title = args.add
        if sr.add_note(note_id, title):
            print(f"✅ 笔记 '{title}' 已添加到复习队列")
        else:
            print(f"笔记 {note_id} 已在复习队列中")

    elif args.stats:
        stats = sr.get_stats()
        print(f"📊 复习统计:")
        print(f"  总笔记数: {stats['total_notes']}")
        print(f"  到期复习: {stats['due_reviews']}")
        print(f"  总复习次数: {stats['total_reviews']}")
        print(f"  平均连续天数: {stats['avg_streak']:.1f}")
        print(f"  平均质量评分: {stats['avg_quality']:.2f}")
        print(f"  最近质量分布: {stats['by_last_quality']}")

    elif args.curve:
        data = sr.get_forgetting_curve_data(args.curve)
        if data:
            print(f"📈 遗忘曲线数据 [{data['title']}]:")
            print(f"  当前EF: {data['current_ef']:.2f}")
            print(f"  当前间隔: {data['current_interval']} 天")
            print(f"  预估保留率:")
            for d, r in zip(data['intervals'], data['retention']):
                print(f"    {d}天: {r}%")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
