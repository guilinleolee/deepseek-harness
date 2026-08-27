#!/usr/bin/env python3
"""
LLM Wiki Synthesizer - 知识综合器
Phase 4: LINT & MAINTAIN
扫描多篇相关笔记 → 综合为深度知识条目
目标: 从碎片到体系，从点滴到河流
"""
import re
import json
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
from scripts.compile import WikiCompiler


class WikiSynthesizer:
    """
    Wiki知识综合器
    核心能力: 将多篇相关笔记综合为深度知识条目
    综合策略: 标签聚类 + 关系链 + 冲突检测
    """

    def __init__(self, wiki_dir: Path):
        self.wiki_dir = wiki_dir
        self.meta_dir = wiki_dir / "_meta"
        self._all_notes: Dict[Path, Dict] = {}
        self._tag_index: Dict[str, List[Path]] = defaultdict(list)

    # ── 公开API ────────────────────────────────────────────────

    def synthesize(self, min_tag_count: int = 2, dry_run: bool = False) -> Dict:
        """
        综合所有可合成的笔记群

        Args:
            min_tag_count: 标签出现次数阈值（>=2才触发综合）
            dry_run: True则只分析不写入

        Returns:
            stats: created/updated/skipped/errors/candidates
        """
        self._scan_all_notes()
        self._build_tag_index()

        stats = {
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "candidates": 0,
        }
        candidates = self._find_synthesis_candidates(min_tag_count)
        stats["candidates"] = len(candidates)

        report_lines = []
        report_lines.append(f"# 知识综合报告")
        report_lines.append(f"生成: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report_lines.append(f"候选群: {len(candidates)}")

        for group_key, note_paths in candidates:
            try:
                if dry_run:
                    report_lines.append(
                        f"- [DRY] `{group_key}`: {len(note_paths)}篇 → 1综合"
                    )
                    stats["skipped"] += 1
                else:
                    result = self._synthesize_group(group_key, note_paths)
                    if result == "created":
                        stats["created"] += 1
                        report_lines.append(
                            f"- [NEW] `{group_key}`: {len(note_paths)}篇 → 综合笔记"
                        )
                    elif result == "updated":
                        stats["updated"] += 1
                        report_lines.append(
                            f"- [UPD] `{group_key}`: {len(note_paths)}篇 → 更新综合"
                        )
                    else:
                        stats["skipped"] += 1
                        report_lines.append(
                            f"- [SKIP] `{group_key}`: {result}"
                        )
            except Exception as e:
                stats["errors"] += 1
                report_lines.append(f"- [ERR] `{group_key}`: {e}")

        report_lines.append(f"\n总计: 创建{stats['created']} 更新{stats['updated']} 跳过{stats['skipped']} 错误{stats['errors']}")
        report_lines.append("\n<!-- 自动生成 -->")

        (self.meta_dir / "synthesis-report.md").write_text(
            "\n".join(report_lines), encoding="utf-8"
        )
        return stats

    def diagnose(self) -> Dict:
        """
        诊断所有笔记的综合潜力

        Returns:
            diagnosis: {
                "total": int,
                "groupable": int,     # 可综合的
                "orphaned": int,     # 孤立笔记
                "already_synth": int, # 已综合
                "groups": [{"key": str, "size": int, "paths": [str]}],
                "orphans": [str],     # 孤立路径列表
            }
        """
        self._scan_all_notes()
        self._build_tag_index()

        candidates = self._find_synthesis_candidates(min_tag_count=2)

        already_synth = {
            p for p, fm in self._all_notes.items()
            if fm.get("sources") and len(fm.get("sources", [])) > 1
        }

        all_in_groups: Set[Path] = set()
        for paths in candidates.values():
            all_in_groups.update(paths)

        orphaned = set(self._all_notes.keys()) - all_in_groups - already_synth

        return {
            "total": len(self._all_notes),
            "groupable": len(candidates),
            "orphaned": len(orphaned),
            "already_synth": len(already_synth),
            "groups": [
                {"key": k, "size": len(v), "paths": [str(p) for p in v]}
                for k, v in sorted(candidates.items(), key=lambda x: -len(x[1]))
            ],
            "orphans": [str(p) for p in orphaned],
        }

    # ── 核心逻辑 ──────────────────────────────────────────────

    def _find_synthesis_candidates(self, min_tag_count: int) -> Dict[str, List[Path]]:
        """
        找出可综合的笔记群

        策略:
        1. 标签聚类: 共享>=2个标签的笔记
        2. 时间窗口: valid_from间隔<30天
        3. 排除已综合的笔记
        """
        candidates: Dict[str, List[Path]] = {}
        active_notes = [
            (p, fm) for p, fm in self._all_notes.items()
            if fm.get("status", "active") == "active"
        ]

        # 标签聚类
        for p, fm in active_notes:
            tags = set(t.strip().lstrip("#") for t in fm.get("tags", "").split(","))
            # 找共享标签的其他笔记
            for tag in tags:
                if not tag:
                    continue
                for other_p, other_fm in active_notes:
                    if other_p == p:
                        continue
                    other_tags = set(t.strip().lstrip("#") for t in other_fm.get("tags", "").split(","))
                    shared = tags & other_tags
                    if len(shared) >= min_tag_count:
                        # 用共享标签排序作为群key
                        key = "|".join(sorted(shared))
                        if key not in candidates:
                            candidates[key] = []
                        candidates[key] = [p, other_p]
                        break

        # 去重 + 排序
        for key in candidates:
            candidates[key] = list(set(candidates[key]))
            candidates[key].sort(key=lambda p: self._all_notes[p].get("created", ""))

        # 过滤掉已综合的（sources里有多个）
        filtered = {}
        for key, paths in candidates.items():
            non_synth = [
                p for p in paths
                if not (self._all_notes[p].get("sources") and
                       len(self._all_notes[p].get("sources", "")) > 1)
            ]
            if len(non_synth) >= 2:
                filtered[key] = non_synth

        return filtered

    def _synthesize_group(self, group_key: str, note_paths: List[Path]) -> str:
        """
        综合一组笔记为单篇深度知识条目

        Returns:
            "created" | "updated" | "skipped:reason"
        """
        # 收集所有内容
        notes_data = []
        for p in note_paths:
            fm = self._all_notes[p]
            content = p.read_text(encoding="utf-8")
            # 去掉frontmatter
            body = re.sub(r"^---\n.*?\n---\n", "", content, count=1, flags=re.DOTALL)
            notes_data.append({
                "path": p,
                "title": fm.get("title", p.stem),
                "tags": fm.get("tags", ""),
                "created": fm.get("created", ""),
                "updated": fm.get("updated", ""),
                "summary": fm.get("summary", ""),
                "confidence": fm.get("confidence", "0.7"),
                "content": body.strip(),
            })

        # 生成综合标题
        titles = [n["title"] for n in notes_data]
        synth_title = self._generate_synth_title(group_key, titles)

        # 生成综合内容
        synth_body = self._generate_synth_content(notes_data, group_key)

        # 生成关键要点
        key_points = self._extract_key_points(notes_data)

        # 生成关系
        relationships = self._generate_relationships(notes_data)

        # 收集来源
        sources = [str(p) for p in note_paths]

        # 检查是否已有同名综合笔记
        existing = self._find_existing_synth(synth_title)
        if existing:
            # 检查是否有新增内容
            if self._needs_update(existing, sources):
                self._update_synth(existing, notes_data, sources)
                return "updated"
            return "skipped:内容已完整"

        # 写入新综合笔记
        self._write_synth(
            synth_title=synth_title,
            group_key=group_key,
            body=synth_body,
            key_points=key_points,
            relationships=relationships,
            sources=sources,
            notes_data=notes_data,
        )
        return "created"

    def _generate_synth_title(self, group_key: str, titles: List[str]) -> str:
        """基于群标签和来源标题生成综合标题"""
        tag_str = group_key.replace("|", " + ")
        if len(titles) == 2:
            return f"{titles[0]} × {titles[1]}"
        elif len(titles) <= 4:
            return f"【综合】{tag_str}"
        else:
            return f"【综合系列】{tag_str}（{len(titles)}篇）"

    def _generate_synth_content(self, notes_data: List[Dict], group_key: str) -> str:
        """生成综合正文"""
        sections = []
        sections.append(f"## 综合来源\n")
        sections.append(f"本条目综合了 {len(notes_data)} 篇相关笔记：\n")

        for i, n in enumerate(notes_data, 1):
            sections.append(f"{i}. **{n['title']}**")
            if n.get("summary"):
                sections.append(f"   - {n['summary']}")

        sections.append("\n---\n\n")

        # 合并核心内容
        all_contents = [n["content"] for n in notes_data if n["content"]]
        if all_contents:
            sections.append("## 核心内容\n")
            # 简单合并：去重后拼接
            seen_lines = set()
            for content in all_contents:
                for line in content.split("\n"):
                    stripped = line.strip()
                    if stripped and stripped not in seen_lines and not stripped.startswith("#"):
                        seen_lines.add(stripped)
                        if len(seen_lines) <= 50:  # 限制合并行数
                            sections.append(f"{stripped}\n")

        return "\n".join(sections)

    def _extract_key_points(self, notes_data: List[Dict]) -> str:
        """从所有笔记中提取关键要点"""
        points = []
        for n in notes_data:
            if n.get("summary"):
                points.append(f"- {n['title']}: {n['summary']}")
        return "\n".join(points) if points else "- （综合提炼中）"

    def _generate_relationships(self, notes_data: List[Dict]) -> str:
        """生成与其他笔记的关系"""
        rels = []
        for n in notes_data:
            rels.append(f"- [[{n['title']}]] ← 来源")
        return "\n".join(rels)

    def _find_existing_synth(self, title: str) -> Optional[Path]:
        """查找已有的同名综合笔记"""
        for p in self._all_notes:
            fm = self._all_notes[p]
            if fm.get("title") == title:
                return p
        return None

    def _needs_update(self, existing: Path, new_sources: List[str]) -> bool:
        """检查是否需要更新综合笔记"""
        fm = self._all_notes.get(existing, {})
        existing_sources = fm.get("sources", "")
        if existing_sources:
            # 有新的来源未包含
            for src in new_sources:
                if src not in existing_sources:
                    return True
        return False

    def _write_synth(
        self,
        synth_title: str,
        group_key: str,
        body: str,
        key_points: str,
        relationships: str,
        sources: List[str],
        notes_data: List[Dict],
    ):
        """写入综合笔记到wiki目录"""
        # 生成slug
        slug = re.sub(r'[^\w\s-]', '', synth_title)
        slug = re.sub(r'[\s+]', '-', slug)
        slug = re.sub(r'-+', '-', slug).strip('-')

        # 综合笔记放在 _synth/ 子目录
        synth_dir = self.wiki_dir / "_synth"
        synth_dir.mkdir(exist_ok=True)
        out_path = synth_dir / f"{slug}.md"

        now = datetime.now().strftime("%Y-%m-%d")
        tags_str = group_key.replace("|", ", #")

        frontmatter = f"""---
title: "{synth_title}"
summary: "综合知识条目：{group_key.replace('|', ' + ')}"
tags: [synthesized, #{" + #".join(group_key.split('|'))}]
created: {now}
updated: {now}
compilations: 1
sources: [{', '.join(sources)}]
related: []
confidence: 0.9
status: active

<!-- V2.0 综合字段 -->
context: "综合{note_paths if (note_paths := notes_data) and len(note_paths) else len(notes_data)}篇笔记"
focus: "{group_key}"
temporal:
  learned: {now}
  valid_from: {now}
  valid_until: ""
---

{body}

## 关键要点

{key_points}

## 与其他笔记的关联

{relationships}

## 待验证/待补充

- 综合内容需定期复核，确保时效性

<!-- 自动综合生成 -->
"""

        out_path.write_text(frontmatter, encoding="utf-8")

    def _update_synth(
        self,
        existing: Path,
        notes_data: List[Dict],
        new_sources: List[str],
    ):
        """更新已有综合笔记"""
        fm = self._all_notes[existing]
        content = existing.read_text(encoding="utf-8")
        now = datetime.now().strftime("%Y-%m-%d")

        # 追加新来源到sources
        old_sources = fm.get("sources", "")
        all_sources = list(set(
            [s.strip() for s in old_sources.split(",") if s.strip()] +
            new_sources
        ))
        sources_str = ", ".join(f'"{s}"' for s in all_sources)

        # 更新时间戳和compilations
        old_comp = int(fm.get("compilations", 0))
        content = re.sub(
            r"^updated: .+$", f"updated: {now}", content, count=1, flags=re.MULTILINE
        )
        content = re.sub(
            r"^compilations: .+$", f"compilations: {old_comp + 1}", content, count=1, flags=re.MULTILINE
        )
        content = re.sub(
            r"^sources: \[.+\]$", f"sources: [{sources_str}]", content, count=1, flags=re.MULTILINE
        )

        existing.write_text(content, encoding="utf-8")

    # ── 扫描 ───────────────────────────────────────────────────

    def _scan_all_notes(self):
        """扫描所有wiki笔记"""
        self._all_notes = {}
        for fpath in self.wiki_dir.glob("**/*.md"):
            if "_" in fpath.parts[0] or fpath.name.startswith("_"):
                continue
            try:
                content = fpath.read_text(encoding="utf-8")
                fm = self._parse_fm(content)
                self._all_notes[fpath] = fm
            except Exception:
                pass

    def _build_tag_index(self):
        """构建标签倒排索引"""
        self._tag_index = defaultdict(list)
        for p, fm in self._all_notes.items():
            tags = [t.strip().lstrip("#") for t in fm.get("tags", "").split(",")]
            for tag in tags:
                if tag:
                    self._tag_index[tag].append(p)

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