#!/usr/bin/env python3
"""
Wiki-MemPalace 矛盾同步器
检测并同步Wiki笔记与MemPalace实体间的知识矛盾

Usage:
    python3 contradiction_sync.py --scan
    python3 contradiction_sync.py --resolve --contradiction-id "cnt_001"
    python3 contradiction_sync.py --status
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import yaml
import re

WIKI_DIR = Path.home() / ".claude" / "wiki"
MEMPALACE_DIR = Path.home() / ".claude" / "mempalace"
CONTRADICTION_DB = Path.home() / ".claude" / "mempalace" / "contradictions.json"


class ContradictionDetector:
    """矛盾检测器"""

    def __init__(self):
        self.contradictions: List[dict] = []
        self._load_contradictions()

    def _load_contradictions(self):
        """加载已有矛盾记录"""
        if CONTRADICTION_DB.exists():
            try:
                data = json.loads(CONTRADICTION_DB.read_text(encoding="utf-8"))
                self.contradictions = data.get("contradictions", [])
            except:
                self.contradictions = []

    def _save_contradictions(self):
        """保存矛盾记录"""
        CONTRADICTION_DB.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "contradictions": self.contradictions,
            "last_scan": datetime.now().isoformat()
        }
        CONTRADICTION_DB.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def detect_claim_contradiction(self, entity_a: dict, entity_b: dict) -> Optional[dict]:
        """检测两个实体间的claim矛盾"""
        claims_a = entity_a.get("claims", [])
        claims_b = entity_b.get("claims", [])

        for claim_a in claims_a:
            for claim_b in claims_b:
                if self._is_contradictory(claim_a, claim_b):
                    return {
                        "type": "claim_conflict",
                        "entity_a": entity_a.get("entity_id"),
                        "entity_b": entity_b.get("entity_id"),
                        "claim_a": claim_a,
                        "claim_b": claim_b,
                        "reason": self._explain_contradiction(claim_a, claim_b),
                        "detected_at": datetime.now().isoformat(),
                        "status": "pending"
                    }
        return None

    def _is_contradictory(self, claim_a: dict, claim_b: dict) -> bool:
        """判断两个claim是否矛盾"""
        if claim_a.get("predicate") != claim_b.get("predicate"):
            return False

        val_a = str(claim_a.get("value", "")).lower()
        val_b = str(claim_b.get("value", "")).lower()

        negations = ["不", "非", "无", "不是", "no", "not", "false", "never", "none"]
        for neg in negations:
            if neg in val_a and neg in val_b:
                if val_a != val_b:
                    return True

        if val_a != val_b:
            numeric_a = self._extract_number(val_a)
            numeric_b = self._extract_number(val_b)
            if numeric_a is not None and numeric_b is not None:
                if abs(numeric_a - numeric_b) > 0.5 * max(numeric_a, numeric_b):
                    return True

        return False

    def _extract_number(self, text: str) -> Optional[float]:
        """从文本提取数字"""
        match = re.search(r'[-+]?\d*\.?\d+', text)
        if match:
            return float(match.group())
        return None

    def _explain_contradiction(self, claim_a: dict, claim_b: dict) -> str:
        """解释矛盾原因"""
        return f"'{claim_a.get('value')}' vs '{claim_b.get('value')}' on '{claim_a.get('predicate')}'"

    def detect_tag_contradiction(self, note_a: dict, note_b: dict) -> Optional[dict]:
        """检测标签分类矛盾"""
        tags_a = set(str(t).lower() for t in note_a.get("tags", []))
        tags_b = set(str(t).lower() for t in note_b.get("tags", []))

        conflict_pairs = [
            ({"tech", "技术"}, {"biz", "商业"}),
            ({"architecture"}, {"design"}),
            ({"database"}, {"cache"}),
            ({"frontend"}, {"backend"}),
        ]

        for pair in conflict_pairs:
            if pair[0].intersection(tags_a) and pair[1].intersection(tags_b):
                return {
                    "type": "tag_conflict",
                    "note_a": note_a.get("path", note_a.get("title", "unknown")),
                    "note_b": note_b.get("path", note_b.get("title", "unknown")),
                    "tags_a": list(tags_a),
                    "tags_b": list(tags_b),
                    "reason": f"矛盾分类: {list(tags_a)} vs {list(tags_b)}",
                    "detected_at": datetime.now().isoformat(),
                    "status": "pending"
                }

        return None

    def detect_link_contradiction(self, note_a: dict, note_b: dict) -> Optional[dict]:
        """检测链接方向矛盾"""
        links_a = set(re.findall(r'\[\[([^\]]+)\]\]', note_a.get("content", "")))
        links_b = set(re.findall(r'\[\[([^\]]+)\]\]', note_b.get("content", "")))

        for link in links_a:
            if link in links_b:
                link_target = link
                if self._has_reverse_link(note_b.get("content", ""), note_a.get("path", "")):
                    continue
                if self._claims_opposite_relation(note_a, note_b, link_target):
                    return {
                        "type": "link_conflict",
                        "note_a": note_a.get("path", note_a.get("title", "unknown")),
                        "note_b": note_b.get("path", note_b.get("title", "unknown")),
                        "link": link_target,
                        "reason": f"链接'{link}'的方向或含义存在矛盾",
                        "detected_at": datetime.now().isoformat(),
                        "status": "pending"
                    }

        return None

    def _has_reverse_link(self, content: str, note_path: str) -> bool:
        """检查是否存在反向链接"""
        note_name = Path(note_path).stem
        return f"[[{note_name}]]" in content

    def _claims_opposite_relation(self, note_a: dict, note_b: dict, link: str) -> bool:
        """检查是否存在相反的关系主张"""
        claims = ["依赖", "包含", "继承", "基于", "先于",
                   "depends", "contains", "inherits", "based", "before"]
        neg_claims = ["独立于", "不包含", "独立于", "无关于",
                       "independent", "excludes", "unrelated"]

        content_a = note_a.get("content", "").lower()
        content_b = note_b.get("content", "").lower()

        a_has_positive = any(c in content_a for c in claims)
        b_has_negative = any(c in content_b for c in neg_claims)
        a_has_negative = any(c in content_a for c in neg_claims)
        b_has_positive = any(c in content_b for c in claims)

        return (a_has_positive and b_has_negative) or (a_has_negative and b_has_positive)

    def scan_all(self) -> dict:
        """扫描所有笔记和实体检测矛盾"""
        results = {"claim_conflicts": [], "tag_conflicts": [], "link_conflicts": []}

        if not MEMPALACE_DIR.exists():
            return {"error": "MemPalace目录不存在"}

        entities = []
        for f in MEMPALACE_DIR.glob("*.json"):
            try:
                entities.append(json.loads(f.read_text(encoding="utf-8")))
            except:
                pass

        for i, entity_a in enumerate(entities):
            for entity_b in entities[i+1:]:
                contradiction = self.detect_claim_contradiction(entity_a, entity_b)
                if contradiction:
                    results["claim_conflicts"].append(contradiction)
                    self._register_contradiction(contradiction)

        if WIKI_DIR.exists():
            notes = []
            for f in WIKI_DIR.glob("*.md"):
                try:
                    notes.append(self._parse_wiki_note(f))
                except:
                    pass

            for i, note_a in enumerate(notes):
                for note_b in notes[i+1:]:
                    tag_contradiction = self.detect_tag_contradiction(note_a, note_b)
                    if tag_contradiction:
                        results["tag_conflicts"].append(tag_contradiction)
                        self._register_contradiction(tag_contradiction)

                    link_contradiction = self.detect_link_contradiction(note_a, note_b)
                    if link_contradiction:
                        results["link_conflicts"].append(link_contradiction)
                        self._register_contradiction(link_contradiction)

        self._save_contradictions()
        return results

    def _parse_wiki_note(self, note_path: Path) -> dict:
        """解析Wiki笔记"""
        content = note_path.read_text(encoding="utf-8")
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1])
                    return {"path": note_path, "content": parts[2], "tags": fm.get("tags", [])}
                except:
                    pass
        return {"path": note_path, "content": content, "tags": []}

    def _register_contradiction(self, contradiction: dict):
        """注册矛盾"""
        existing_ids = [c.get("id") for c in self.contradictions]
        contradiction["id"] = f"cnt_{len(self.contradictions):04d}"
        if contradiction["id"] not in existing_ids:
            self.contradictions.append(contradiction)

    def resolve_contradiction(self, contradiction_id: str, resolution: str) -> dict:
        """解决矛盾"""
        for c in self.contradictions:
            if c.get("id") == contradiction_id:
                c["status"] = "resolved"
                c["resolution"] = resolution
                c["resolved_at"] = datetime.now().isoformat()
                self._save_contradictions()

                self._update_wiki_mempalace(c, resolution)
                return {"success": True, "contradiction": c}

        return {"error": f"矛盾未找到: {contradiction_id}"}

    def _update_wiki_mempalace(self, contradiction: dict, resolution: str):
        """更新Wiki和MemPalace标记"""
        ctype = contradiction.get("type")

        if ctype == "claim_conflict":
            entity_ids = [contradiction.get("entity_a"), contradiction.get("entity_b")]
            for eid in entity_ids:
                if eid:
                    entity_file = MEMPALACE_DIR / f"{eid}.json"
                    if entity_file.exists():
                        try:
                            entity = json.loads(entity_file.read_text(encoding="utf-8"))
                            entity["last_contradiction"] = datetime.now().isoformat()
                            entity["contradiction_count"] = entity.get("contradiction_count", 0) + 1
                            entity["resolution"] = resolution
                            entity_file.write_text(
                                json.dumps(entity, ensure_ascii=False, indent=2),
                                encoding="utf-8"
                            )
                        except:
                            pass

        elif ctype in ("tag_conflict", "link_conflict"):
            note_paths = [contradiction.get("note_a"), contradiction.get("note_b")]
            for note_path_str in note_paths:
                if note_path_str:
                    note_path = Path(note_path_str) if isinstance(note_path_str, str) else note_path_str
                    if note_path.exists():
                        self._update_note_contradiction(note_path, contradiction, resolution)

    def _update_note_contradiction(self, note_path: Path, contradiction: dict, resolution: str):
        """更新笔记的矛盾标记"""
        content = note_path.read_text(encoding="utf-8")

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    fm = yaml.safe_load(parts[1])
                    content = parts[2]
                except:
                    fm = {}
            else:
                fm = {}
        else:
            fm = {}

        compound = fm.get("compound", {})
        compound["disputed"] = True
        compound["dispute_reason"] = contradiction.get("reason", "")
        compound["resolution_status"] = "resolved"
        compound["resolution"] = resolution
        fm["compound"] = compound

        fm_text = yaml.dump(fm, allow_unicode=True, default_flow_style=False)
        full_content = f"---\n{fm_text}---{content}"
        note_path.write_text(full_content, encoding="utf-8")

    def get_status(self) -> dict:
        """获取矛盾状态"""
        pending = [c for c in self.contradictions if c.get("status") == "pending"]
        resolved = [c for c in self.contradictions if c.get("status") == "resolved"]

        return {
            "total": len(self.contradictions),
            "pending": len(pending),
            "resolved": len(resolved),
            "pending_list": pending[:10],
            "last_scan": self._get_last_scan()
        }

    def _get_last_scan(self) -> Optional[str]:
        """获取最后扫描时间"""
        if CONTRADICTION_DB.exists():
            try:
                data = json.loads(CONTRADICTION_DB.read_text(encoding="utf-8"))
                return data.get("last_scan")
            except:
                pass
        return None


def format_status_report(status: dict) -> str:
    """格式化状态报告"""
    lines = [
        "╔══════════════════════════════════════════════════════════════════╗",
        "║         矛盾检测状态                                    ║",
        "╠══════════════════════════════════════════════════════════════════╣"
    ]

    lines.append(f"║  总矛盾数: {status['total']:<6}  待解决: {status['pending']:<6}  已解决: {status['resolved']:<6}        ║")
    if status.get("last_scan"):
        lines.append(f"║  最后扫描: {status['last_scan'][:19]:<32}        ║")

    lines.append("╠══════════════════════════════════════════════════════════════════╣")

    if status.get("pending_list"):
        lines.append("║  待解决矛盾:                                                 ║")
        for c in status["pending_list"][:5]:
            ctype = c.get("type", "unknown")
            reason = c.get("reason", "")[:40]
            lines.append(f"║  [{c.get('id')}] {ctype:<15} {reason:<30} ║")

    lines.append("╚══════════════════════════════════════════════════════════════════╝")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Wiki-MemPalace 矛盾同步器")
    parser.add_argument("--scan", action="store_true", help="扫描所有矛盾")
    parser.add_argument("--resolve", action="store_true", help="解决矛盾")
    parser.add_argument("--contradiction-id", help="矛盾ID")
    parser.add_argument("--resolution", help="解决方案")
    parser.add_argument("--status", action="store_true", help="显示矛盾状态")
    parser.add_argument("--format", choices=["json", "table"], default="table", help="输出格式")
    parser.add_argument("--list", action="store_true", help="列出所有矛盾")

    args = parser.parse_args()

    detector = ContradictionDetector()

    if args.status:
        status = detector.get_status()
        if args.format == "json":
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print(format_status_report(status))

    elif args.list:
        all_c = detector.contradictions
        if args.format == "json":
            print(json.dumps(all_c, ensure_ascii=False, indent=2))
        else:
            print(f"\n共 {len(all_c)} 个矛盾记录:\n")
            for c in all_c:
                print(f"  [{c.get('id')}] {c.get('type')} - {c.get('status')}")
                print(f"    {c.get('reason', '')[:60]}")
                print()

    elif args.scan:
        results = detector.scan_all()
        total = (len(results.get("claim_conflicts", [])) +
                 len(results.get("tag_conflicts", [])) +
                 len(results.get("link_conflicts", [])))

        if args.format == "json":
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(f"\n✓ 矛盾扫描完成")
            print(f"  Claim矛盾: {len(results.get('claim_conflicts', []))} 个")
            print(f"  标签矛盾: {len(results.get('tag_conflicts', []))} 个")
            print(f"  链接矛盾: {len(results.get('link_conflicts', []))} 个")
            print(f"  总计新增: {total} 个")

    elif args.resolve:
        if not args.contradiction_id or not args.resolution:
            print("Error: --contradiction-id 和 --resolution 必需")
            sys.exit(1)

        result = detector.resolve_contradiction(args.contradiction_id, args.resolution)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"✓ 矛盾已解决: {args.contradiction_id}")
            print(f"  解决方案: {args.resolution}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
