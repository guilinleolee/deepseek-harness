#!/usr/bin/env python3
"""
Wiki 矛盾检测核心
检测笔记中的内容矛盾，支持四种类型：实体关系、时序、因果、语义矛盾

Usage:
    python3 resolver.py --scan
    python3 resolver.py --note "note_id"
    python3 resolver.py --report --json
"""

import argparse
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

WIKI_DIR = Path.home() / ".claude" / "wiki"
CACHE_DIR = Path.home() / ".claude" / "wiki_contradiction_cache"
CACHE_FILE = CACHE_DIR / "contradictions.json"


@dataclass
class Contradiction:
    """矛盾记录"""
    type: str  # entity_relation, temporal, causal, semantic
    node_a: str
    node_b: str
    entity: str = ""
    statement_a: str = ""
    statement_b: str = ""
    event: str = ""
    time_a: str = ""
    time_b: str = ""
    cause: str = ""
    counter: str = ""
    confidence: float = 0.0
    detected_at: float = 0.0


@dataclass
class DetectionStats:
    """检测统计"""
    total_notes: int
    notes_scanned: int
    contradictions_found: int
    high_confidence: int
    medium_confidence: int
    low_confidence: int
    scan_time_ms: float
    by_type: dict = field(default_factory=dict)


class ContradictionResolver:
    """矛盾检测器"""

    # 矛盾类型
    TYPE_ENTITY = "entity_relation"
    TYPE_TEMPORAL = "temporal"
    TYPE_CAUSAL = "causal"
    TYPE_SEMANTIC = "semantic"

    # 置信度阈值
    CONFIDENCE_HIGH = 0.8
    CONFIDENCE_MEDIUM = 0.5
    CONFIDENCE_LOW = 0.4
    CONFIDENCE_FILTER = 0.4  # 自动过滤阈值

    def __init__(self, wiki_dir: Optional[Path] = None):
        self.wiki_dir = wiki_dir or WIKI_DIR
        self.cache = self._load_cache()
        self.contradictions = []

    def _load_cache(self) -> dict:
        """加载矛盾缓存"""
        if CACHE_FILE.exists():
            try:
                return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            except:
                pass
        return {"contradictions": [], "last_scan": 0}

    def _save_cache(self):
        """保存矛盾缓存"""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.cache["contradictions"] = [
            {
                "type": c.type,
                "node_a": c.node_a,
                "node_b": c.node_b,
                "entity": c.entity,
                "statement_a": c.statement_a,
                "statement_b": c.statement_b,
                "event": c.event,
                "time_a": c.time_a,
                "time_b": c.time_b,
                "cause": c.cause,
                "counter": c.counter,
                "confidence": c.confidence,
                "detected_at": c.detected_at,
            }
            for c in self.contradictions
        ]
        self.cache["last_scan"] = time.time()
        CACHE_FILE.write_text(
            json.dumps(self.cache, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def _count_notes(self) -> int:
        """统计笔记数量"""
        if not self.wiki_dir.exists():
            return 0
        return len(list(self.wiki_dir.glob("*.md")))

    def _extract_title(self, content: str, filename: str) -> str:
        """提取笔记标题"""
        if content.startswith("# "):
            return content.split("\n")[0][2:].strip()
        return filename.replace("-", " ").replace("_", " ").title()

    def _extract_entities(self, content: str) -> set:
        """提取实体（简化版：提取首字母大写的词组）"""
        # 匹配中文实体（连续的中文字符）
        chinese = set(re.findall(r'[\u4e00-\u9fff]{2,}', content))
        # 匹配英文实体（首字母大写的词）
        english = set(re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content))
        return chinese | english

    def _extract_dates(self, content: str) -> list:
        """提取日期"""
        patterns = [
            r'(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})',
            r'(\d{4})[年\-/](\d{1,2})',
            r'(\d{4})年',
        ]
        dates = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            dates.extend(['-'.join(m) if isinstance(m, tuple) else m for m in matches])
        return dates

    def _extract_causal_keywords(self, content: str) -> list:
        """提取因果关键词"""
        cause_keywords = ['导致', '引起', '造成', '致使', '因为', '由于',
                          'causes', 'leads to', 'results in', 'because', 'due to']
        effect_keywords = ['因此', '所以', '从而', '导致', 'result', 'therefore',
                          'consequently', 'thus', 'hence']
        content_lower = content.lower()
        found = []
        for kw in cause_keywords + effect_keywords:
            if kw.lower() in content_lower:
                found.append(kw)
        return found

    def _detect_entity_relation(self, note_a: dict, note_b: dict) -> Optional[Contradiction]:
        """检测实体关系矛盾"""
        entities_a = self._extract_entities(note_a["content"])
        entities_b = self._extract_entities(note_b["content"])
        common_entities = entities_a & entities_b

        if not common_entities:
            return None

        # 检查是否存在 X 是 Y 和 X 不是 Y 的矛盾
        for entity in common_entities:
            content_a = note_a["content"]
            content_b = note_b["content"]

            # 简化检测：检查是否同时包含"是"和"不是"
            patterns_same = [
                (f"{entity}.*是.*", f"{entity}.*不是.*"),
                (f"是.*{entity}", f"不是.*{entity}"),
            ]

            for pat_a, pat_b in patterns_same:
                match_a = re.search(pat_a, content_a)
                match_b = re.search(pat_b, content_b)
                if match_a and match_b:
                    return Contradiction(
                        type=self.TYPE_ENTITY,
                        node_a=note_a["id"],
                        node_b=note_b["id"],
                        entity=entity,
                        statement_a=match_a.group(0)[:100],
                        statement_b=match_b.group(0)[:100],
                        confidence=0.75
                    )

        return None

    def _detect_temporal(self, note_a: dict, note_b: dict) -> Optional[Contradiction]:
        """检测时序矛盾"""
        dates_a = self._extract_dates(note_a["content"])
        dates_b = self._extract_dates(note_b["content"])

        if not dates_a or not dates_b:
            return None

        # 检查是否有共同事件但时间不同
        content_a = note_a["content"]
        content_b = note_b["content"]

        # 提取可能的事件描述
        events_a = re.findall(r'[\u4e00-\u9fff]{4,}.*?(?:发生|开始|结束|成立|创建|发布)', content_a)
        events_b = re.findall(r'[\u4e00-\u9fff]{4,}.*?(?:发生|开始|结束|成立|创建|发布)', content_b)

        for event_a in events_a:
            for event_b in events_b:
                if event_a[:10] == event_b[:10]:  # 相似事件
                    # 找到对应的日期
                    for date_a in dates_a:
                        for date_b in dates_b:
                            if date_a != date_b:
                                return Contradiction(
                                    type=self.TYPE_TEMPORAL,
                                    node_a=note_a["id"],
                                    node_b=note_b["id"],
                                    event=event_a[:20],
                                    time_a=date_a,
                                    time_b=date_b,
                                    confidence=0.85
                                )

        return None

    def _detect_causal(self, note_a: dict, note_b: dict) -> Optional[Contradiction]:
        """检测因果矛盾"""
        causal_a = self._extract_causal_keywords(note_a["content"])
        causal_b = self._extract_causal_keywords(note_b["content"])

        if not causal_a or not causal_b:
            return None

        # 检查因果方向是否相反
        cause_kw = {'导致', '引起', '造成', 'causes', 'leads to', 'results in'}
        effect_kw = {'因此', '所以', 'result', 'therefore', 'consequently'}

        has_cause_a = bool(cause_kw & set(causal_a))
        has_effect_a = bool(effect_kw & set(causal_a))
        has_cause_b = bool(cause_kw & set(causal_b))
        has_effect_b = bool(effect_kw & set(causal_b))

        # A说是原因，B说是结果
        if has_cause_a and has_effect_b:
            # 进一步检查是否讨论相同主题
            entities_a = self._extract_entities(note_a["content"])
            entities_b = self._extract_entities(note_b["content"])
            if entities_a & entities_b:
                return Contradiction(
                    type=self.TYPE_CAUSAL,
                    node_a=note_a["id"],
                    node_b=note_b["id"],
                    cause="A认为是原因",
                    counter="B认为是结果",
                    confidence=0.7
                )

        return None

    def _detect_semantic(self, note_a: dict, note_b: dict) -> Optional[Contradiction]:
        """检测语义矛盾"""
        content_a = note_a["content"].lower()
        content_b = note_b["content"].lower()

        # 检测反义关键词
        antonym_pairs = [
            (['好', '优秀', '棒', '赞'], ['坏', '差', '烂', '糟']),
            (['重要', '关键', '核心'], ['次要', '无关', '边缘']),
            (['支持', '赞成', '同意'], ['反对', '否定', '拒绝']),
            (['应该', '必须', '需要'], ['不应', '禁止', '不能']),
            (['有效', '可行'], ['无效', '不可行']),
        ]

        for pos_words, neg_words in antonym_pairs:
            has_pos_a = any(w in content_a for w in pos_words)
            has_neg_a = any(w in content_a for w in neg_words)
            has_pos_b = any(w in content_b for w in pos_words)
            has_neg_b = any(w in content_b for w in neg_words)

            # A正面，B负面
            if has_pos_a and has_neg_b:
                return Contradiction(
                    type=self.TYPE_SEMANTIC,
                    node_a=note_a["id"],
                    node_b=note_b["id"],
                    statement_a="正面评价",
                    statement_b="负面评价",
                    confidence=0.65
                )
            # A负面，B正面
            if has_neg_a and has_pos_b:
                return Contradiction(
                    type=self.TYPE_SEMANTIC,
                    node_a=note_a["id"],
                    node_b=note_b["id"],
                    statement_a="负面评价",
                    statement_b="正面评价",
                    confidence=0.65
                )

        return None

    def _detect_between(self, note_a: dict, note_b: dict) -> list[Contradiction]:
        """检测两条笔记之间的所有矛盾"""
        contradictions = []

        # 实体关系矛盾
        result = self._detect_entity_relation(note_a, note_b)
        if result:
            contradictions.append(result)

        # 时序矛盾
        result = self._detect_temporal(note_a, note_b)
        if result:
            contradictions.append(result)

        # 因果矛盾
        result = self._detect_causal(note_a, note_b)
        if result:
            contradictions.append(result)

        # 语义矛盾
        result = self._detect_semantic(note_a, note_b)
        if result:
            contradictions.append(result)

        return contradictions

    def detect_note(self, note_id: str) -> list[Contradiction]:
        """检测单条笔记与其他笔记的矛盾"""
        if not self.wiki_dir.exists():
            return []

        target_file = self.wiki_dir / f"{note_id}.md"
        if not target_file.exists():
            return []

        contradictions = []
        try:
            target_content = target_file.read_text(encoding="utf-8")
        except:
            return []

        target_note = {"id": note_id, "content": target_content}

        # 与所有其他笔记比较
        for md_file in self.wiki_dir.glob("*.md"):
            if md_file.stem == note_id:
                continue

            try:
                other_content = md_file.read_text(encoding="utf-8")
            except:
                continue

            other_note = {"id": md_file.stem, "content": other_content}

            # 检测矛盾
            results = self._detect_between(target_note, other_note)
            for c in results:
                c.detected_at = time.time()
                if c.confidence >= self.CONFIDENCE_FILTER:
                    contradictions.append(c)

        return contradictions

    def scan_all(self) -> list[Contradiction]:
        """扫描所有笔记检测矛盾"""
        start_time = time.time()

        if not self.wiki_dir.exists():
            return []

        notes = []
        for md_file in self.wiki_dir.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                notes.append({"id": md_file.stem, "content": content})
            except:
                continue

        self.contradictions = []

        # 两两比较笔记
        total_pairs = len(notes) * (len(notes) - 1) // 2
        checked = 0

        for i in range(len(notes)):
            for j in range(i + 1, len(notes)):
                checked += 1
                if checked % 100 == 0:
                    # 避免超时，大规模时限制
                    if time.time() - start_time > 30:
                        break

                results = self._detect_between(notes[i], notes[j])
                for c in results:
                    c.detected_at = time.time()
                    if c.confidence >= self.CONFIDENCE_FILTER:
                        self.contradictions.append(c)

        self._save_cache()
        return self.contradictions

    def get_stats(self) -> DetectionStats:
        """获取检测统计"""
        high = sum(1 for c in self.contradictions if c.confidence >= self.CONFIDENCE_HIGH)
        medium = sum(1 for c in self.contradictions
                     if self.CONFIDENCE_MEDIUM <= c.confidence < self.CONFIDENCE_HIGH)
        low = sum(1 for c in self.contradictions
                  if self.CONFIDENCE_LOW <= c.confidence < self.CONFIDENCE_MEDIUM)

        by_type = {}
        for c in self.contradictions:
            by_type[c.type] = by_type.get(c.type, 0) + 1

        return DetectionStats(
            total_notes=self._count_notes(),
            notes_scanned=len(list(self.wiki_dir.glob("*.md"))) if self.wiki_dir.exists() else 0,
            contradictions_found=len(self.contradictions),
            high_confidence=high,
            medium_confidence=medium,
            low_confidence=low,
            scan_time_ms=0,
            by_type=by_type
        )

    def get_report(self) -> str:
        """生成矛盾报告"""
        stats = self.get_stats()

        lines = [
            "=" * 60,
            " Wiki 矛盾检测报告",
            "=" * 60,
            "",
            f"📊 统计概览:",
            f"   笔记总数: {stats.total_notes}",
            f"   矛盾数量: {stats.contradictions_found}",
            f"   高置信度 (>0.8): {stats.high_confidence}",
            f"   中置信度 (0.5-0.8): {stats.medium_confidence}",
            f"   低置信度 (0.4-0.5): {stats.low_confidence}",
            "",
            f"📈 按类型分布:",
        ]

        for type_name, count in stats.by_type.items():
            type_label = {
                "entity_relation": "实体关系",
                "temporal": "时序",
                "causal": "因果",
                "semantic": "语义",
            }.get(type_name, type_name)
            lines.append(f"   {type_label}: {count}")

        lines.append("")
        lines.append("=" * 60)

        # 列出高置信度矛盾
        high_conf = [c for c in self.contradictions if c.confidence >= self.CONFIDENCE_HIGH]
        if high_conf:
            lines.append("")
            lines.append("🔴 高置信度矛盾 (需人工确认):")
            for c in high_conf[:10]:
                type_label = {
                    "entity_relation": "实体关系",
                    "temporal": "时序",
                    "causal": "因果",
                    "semantic": "语义",
                }.get(c.type, c.type)
                lines.append(f"   [{type_label}] {c.node_a} ↔ {c.node_b}")
                lines.append(f"   置信度: {c.confidence:.2f}")

        # 列出中置信度矛盾
        medium_conf = [c for c in self.contradictions
                      if self.CONFIDENCE_MEDIUM <= c.confidence < self.CONFIDENCE_HIGH]
        if medium_conf:
            lines.append("")
            lines.append("🟡 中置信度矛盾 (生成解决建议):")
            for c in medium_conf[:10]:
                type_label = {
                    "entity_relation": "实体关系",
                    "temporal": "时序",
                    "causal": "因果",
                    "semantic": "语义",
                }.get(c.type, c.type)
                lines.append(f"   [{type_label}] {c.node_a} ↔ {c.node_b}")

        return "\n".join(lines)

    def export_json(self) -> dict:
        """导出JSON格式报告"""
        return {
            "stats": {
                "total_notes": self._count_notes(),
                "contradictions_found": len(self.contradictions),
                "high_confidence": sum(1 for c in self.contradictions if c.confidence >= self.CONFIDENCE_HIGH),
                "medium_confidence": sum(1 for c in self.contradictions
                                         if self.CONFIDENCE_MEDIUM <= c.confidence < self.CONFIDENCE_HIGH),
                "low_confidence": sum(1 for c in self.contradictions
                                      if self.CONFIDENCE_LOW <= c.confidence < self.CONFIDENCE_MEDIUM),
                "by_type": {
                    k: sum(1 for c in self.contradictions if c.type == k)
                    for k in set(c.type for c in self.contradictions)
                }
            },
            "contradictions": [
                {
                    "type": c.type,
                    "node_a": c.node_a,
                    "node_b": c.node_b,
                    "entity": c.entity,
                    "statement_a": c.statement_a,
                    "statement_b": c.statement_b,
                    "event": c.event,
                    "time_a": c.time_a,
                    "time_b": c.time_b,
                    "cause": c.cause,
                    "counter": c.counter,
                    "confidence": c.confidence,
                    "resolution_priority": "P0" if c.confidence >= self.CONFIDENCE_HIGH
                                          else "P1" if c.confidence >= self.CONFIDENCE_MEDIUM
                                          else "P2"
                }
                for c in self.contradictions
            ]
        }


def main():
    parser = argparse.ArgumentParser(description="Wiki 矛盾检测器")
    parser.add_argument("--scan", action="store_true", help="扫描所有笔记")
    parser.add_argument("--note", help="检测单条笔记")
    parser.add_argument("--report", action="store_true", help="生成矛盾报告")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    parser.add_argument("--cache", action="store_true", help="从缓存加载")

    args = parser.parse_args()

    resolver = ContradictionResolver()

    if args.cache:
        # 从缓存加载
        if resolver.cache.get("contradictions"):
            resolver.contradictions = [
                Contradiction(**c) for c in resolver.cache["contradictions"]
            ]

    if args.scan:
        print("开始扫描笔记...")
        resolver.scan_all()
        print(f"扫描完成，发现 {len(resolver.contradictions)} 个矛盾")

    if args.note:
        print(f"检测笔记: {args.note}")
        contradictions = resolver.detect_note(args.note)
        print(f"发现 {len(contradictions)} 个矛盾")

    if args.report:
        if not resolver.contradictions:
            resolver.scan_all()
        if args.json:
            print(json.dumps(resolver.export_json(), ensure_ascii=False, indent=2))
        else:
            print(resolver.get_report())

    if not any([args.scan, args.note, args.report]):
        parser.print_help()


if __name__ == "__main__":
    main()
