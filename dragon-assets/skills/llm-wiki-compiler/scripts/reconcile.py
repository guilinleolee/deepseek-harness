#!/usr/bin/env python3
"""
LLM Wiki Temporal Reconciler - 时间有效性调和
Phase 4: LINT & MAINTAIN
扫描所有笔记 → 根据valid_from/valid_until调和状态
状态流转: pending → active → expired
"""
import re
import json
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Set, Optional
from scripts.compile import WikiCompiler


class WikiReconciler:
    """
    Wiki时间有效性调和器
    检查项: valid_from(生效时间)/valid_until(失效时间)
    状态流转: pending → active → expired
    """

    def __init__(self, wiki_dir: Path):
        self.wiki_dir = wiki_dir
        self.meta_dir = wiki_dir / "_meta"
        self._all_notes: Dict[Path, Dict] = {}
        self._title_map: Dict[str, Path] = {}

    def reconcile_temporal(self) -> Dict:
        """调和所有笔记的时间有效性"""
        self._scan_all_notes()

        stats = {
            "expired": 0,
            "pending": 0,
            "active": 0,
            "fixed": 0,
            "errors": 0,
        }

        today = date.today()
        report_lines = []
        report_lines.append(f"# 时间有效性调和报告")
        report_lines.append(f"生成: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report_lines.append(f"\n## 概览\n")

        for fpath, fm in self._all_notes.items():
            old_status = fm.get("status", "active")
            new_status = old_status

            valid_from_str = fm.get("valid_from", "")
            valid_until_str = fm.get("valid_until", "")

            try:
                # 检查 valid_from
                if valid_from_str and valid_from_str not in ("null", ""):
                    valid_from = date.fromisoformat(valid_from_str)
                    if today < valid_from:
                        new_status = "pending"

                # 检查 valid_until
                if new_status != "pending" and valid_until_str and valid_until_str not in ("null", ""):
                    valid_until = date.fromisoformat(valid_until_str)
                    if today > valid_until:
                        new_status = "expired"
                    elif today <= valid_until:
                        new_status = "active"

                # 统计
                if old_status == "expired" or new_status == "expired":
                    stats["expired"] += 1
                elif old_status == "pending" or new_status == "pending":
                    stats["pending"] += 1
                else:
                    stats["active"] += 1

                # 写入状态变更
                if old_status != new_status:
                    content = fpath.read_text(encoding="utf-8")
                    content = self._update_status(content, old_status, new_status)
                    fpath.write_text(content, encoding="utf-8")
                    stats["fixed"] += 1
                    report_lines.append(f"- `{fpath.stem}`: {old_status} → **{new_status}**")

            except Exception as e:
                stats["errors"] += 1
                report_lines.append(f"- `{fpath.stem}`: 解析错误 - {e}")

        # 写入报告
        report_lines.append(f"\n总计: {sum(stats.values()) - stats['errors']} 笔记")
        report_lines.append(f"激活: {stats['active']} | 待生效: {stats['pending']} | 已过期: {stats['expired']}")
        report_lines.append(f"修复: {stats['fixed']} | 错误: {stats['errors']}")
        report_lines.append("\n<!-- 自动生成 -->")

        (self.meta_dir / "temporal-report.md").write_text(
            "\n".join(report_lines), encoding="utf-8"
        )
        return stats

    def health_check(self) -> Dict:
        """健康度检查（时间维度）"""
        self._scan_all_notes()
        today = date.today()
        expired = pending = active = 0

        for fm in self._all_notes.values():
            status = fm.get("status", "active")
            valid_until_str = fm.get("valid_until", "")
            valid_from_str = fm.get("valid_from", "")

            if status == "expired":
                expired += 1
            elif status == "pending":
                pending += 1
            elif valid_until_str and valid_until_str not in ("null", ""):
                try:
                    valid_until = date.fromisoformat(valid_until_str)
                    if today > valid_until:
                        expired += 1
                    else:
                        active += 1
                except Exception:
                    active += 1
            else:
                active += 1

        total = expired + pending + active
        health = 100
        if total > 0:
            health -= min(40, (expired / total) * 40)
            health -= min(30, (pending / total) * 30)

        return {
            "total": total,
            "active": active,
            "pending": pending,
            "expired": expired,
            "health_score": max(health, 0),
        }

    # ── 扫描 ────────────────────────────────────────────────

    def _scan_all_notes(self):
        """扫描所有笔记"""
        self._all_notes = {}
        self._title_map = {}

        for fpath in self.wiki_dir.glob("**/*.md"):
            if "_" in fpath.parts[0] or fpath.name.startswith("_"):
                continue
            try:
                content = fpath.read_text(encoding="utf-8")
                fm = self._parse_fm(content)
                title = fm.get("title", fpath.stem)
                self._title_map[title] = fpath
                self._all_notes[fpath] = fm
            except Exception:
                pass

    def _parse_fm(self, content: str) -> Dict:
        """解析frontmatter"""
        fm = {}
        m = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if m:
            for line in m.group(1).split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    v = v.strip()
                    if len(v) >= 2 and ((v[0] == '"' and v[-1] == '"') or (v[0] == "'" and v[-1] == "'")):
                        v = v[1:-1]
                    fm[k.strip()] = v
        return fm

    def _update_status(self, content: str, old: str, new: str) -> str:
        """更新frontmatter中的status字段"""
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith("status:"):
                lines[i] = line.replace(f"status: {old}", f"status: {new}")
                break
        return "\n".join(lines)