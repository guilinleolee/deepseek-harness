#!/usr/bin/env python3
"""
LLM Wiki Compiler - 增量编译管道
基于Karpathy LLM Wiki Pattern
核心：LLM作为编译器，不是检索器
"""
import re
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

FRONTMATTER_TEMPLATE = """---
title: "{title}"
summary: "{summary}"
tags: [{tags}]
created: {created}
updated: {updated}
compilations: {compilations}
sources: [{sources}]
related: [{related}]
confidence: {confidence}
status: {status}

<!-- V2.0 新增字段 -->
context: "{context}"
focus: "{focus}"
temporal:
  learned: {learned}
  valid_from: "{valid_from}"
  valid_until: "{valid_until}"
---

## 核心内容

{content}

## 关键要点

{key_points}

## 与其他笔记的关联

{relationships}

## 待验证/待补充

{pending}

## 元注释 (For Future Claude)

{metadata}

"""


class WikiCompiler:
    """
    LLM Wiki增量编译器
    Phase 1: INGEST → Phase 2: COMPILE → Phase 3: QUERY → Phase 4: LINT
    """

    TOPIC_DIRS = {
        "analysis": "00-analysis",
        "analyst": "00-analysis",
        "research": "01-research",
        "investigator": "01-research",
        "调研": "01-research",
        "architecture": "02-architecture",
        "architect": "02-architecture",
        "架构": "02-architecture",
        "builder": "03-builder",
        "构建": "03-builder",
        "code": "03-builder",
        "validation": "04-validation",
        "validator": "04-validation",
        "验证": "04-validation",
        "test": "04-validation",
        "security": "05-security",
        "安全": "05-security",
        "review": "06-review",
        "审查": "06-review",
        "scribe": "07-scribe",
        "记录": "07-scribe",
        "publisher": "08-publisher",
        "发布": "08-publisher",
        "orchestration": "09-orchestration",
        "编排": "09-orchestration",
        "ai": "10-ai",
        "llm": "10-ai",
        "agent": "10-ai",
        "planning": "20-planning",
        "企划": "20-planning",
        "marketing": "30-marketing",
        "营销": "30-marketing",
        "operations": "40-operations",
        "运营": "40-operations",
        "investment": "60-investment",
        "投资": "60-investment",
        "general": "00-analysis",
    }

    def __init__(self, wiki_dir: Path):
        self.wiki_dir = wiki_dir
        self.raw_dir = wiki_dir / "raw"
        self.meta_dir = wiki_dir / "_meta"
        self.inbox_dir = wiki_dir / "_inbox"
        self.state_file = wiki_dir / "_meta" / "_compile_state.json"
        self._state = self._load_state()

    # ── 目录初始化 ───────────────────────────────────────────────

    def init_structure(self):
        """初始化完整的wiki目录结构"""
        self.wiki_dir.mkdir(parents=True, exist_ok=True)

        dirs = [
            "_templates",
            "_inbox",
            "_outbox",
            "_meta",
            "_logs",
            "00-analysis",
            "01-research",
            "02-architecture",
            "03-builder",
            "04-validation",
            "05-security",
            "06-review",
            "07-scribe",
            "08-publisher",
            "09-orchestration",
            "10-ai",
            "20-planning",
            "30-marketing",
            "40-operations",
            "60-investment",
            "raw",
        ]
        for d in dirs:
            (self.wiki_dir / d).mkdir(parents=True, exist_ok=True)

        # 创建全局索引
        index = self.meta_dir / "global-index.md"
        if not index.exists():
            index.write_text("# 全局主题索引\n\n## 按主题分类\n\n<!-- 由LLM编译器自动维护 -->\n", encoding="utf-8")

        # 创建孤立笔记列表
        orphan = self.meta_dir / "orphan-notes.md"
        if not orphan.exists():
            orphan.write_text("# 孤立笔记\n\n> 无反向链接的笔记\n\n", encoding="utf-8")

        # 创建断裂链接报告
        broken = self.meta_dir / "broken-links.md"
        if not broken.exists():
            broken.write_text("# 断裂链接报告\n\n> 被引用但不存在的笔记\n\n", encoding="utf-8")

        # 创建健康报告
        health = self.meta_dir / "health-report.md"
        if not health.exists():
            health.write_text("# Wiki健康报告\n\n> 由self-heal管道生成\n\n", encoding="utf-8")

        # 创建笔记模板
        template = self.wiki_dir / "_templates" / "note-template.md"
        if not template.exists():
            template.write_text(FRONTMATTER_TEMPLATE.format(
                title="笔记标题",
                summary="一句话描述",
                tags="",
                created=datetime.now().date(),
                updated=datetime.now().date(),
                compilations=1,
                sources="",
                related="",
                confidence=0.5,
                status="active",
                content="笔记正文内容",
                key_points="- 要点1\n- 要点2",
                relationships="",
                pending="- [ ] 待验证项1"
            ), encoding="utf-8")

        # 创建raw目录（输入源）
        self.raw_dir.mkdir(parents=True, exist_ok=True)

    # ── 增量编译 ───────────────────────────────────────────────

    def compile_changed(self) -> Dict[str, int]:
        """增量编译：只处理有变更的文件"""
        stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}

        if not self.raw_dir.exists():
            return stats

        for fpath in self.raw_dir.glob("**/*.md"):
            try:
                stat = self._check_change(fpath)
                if stat == "new":
                    self._compile_note(fpath)
                    stats["created"] += 1
                elif stat == "updated":
                    self._compile_note(fpath, update=True)
                    stats["updated"] += 1
                else:
                    stats["skipped"] += 1
            except Exception as e:
                print(f"  错误 {fpath.name}: {e}")
                stats["errors"] += 1

        self._update_global_index()
        self._save_state()
        return stats

    def _check_change(self, fpath: Path) -> str:
        """检查文件是否新增或变更"""
        rel = fpath.relative_to(self.raw_dir)
        key = str(rel)
        mtime = fpath.stat().st_mtime
        if key not in self._state:
            return "new"
        if self._state[key]["mtime"] != mtime:
            return "updated"
        return "unchanged"

    def _compile_note(self, fpath: Path, update: bool = False):
        """编译单个笔记文件到wiki"""
        rel = fpath.relative_to(self.raw_dir)
        content = fpath.read_text(encoding="utf-8")

        # 从路径推断topic目录
        topic = self._infer_topic(fpath)
        topic_dir = self.wiki_dir / topic
        topic_dir.mkdir(parents=True, exist_ok=True)

        # 生成目标文件名
        date = datetime.now().strftime("%Y-%m-%d")
        title = self._extract_title(content, fpath.stem)
        safe_title = re.sub(r"[^\w\s-]", "", title)[:60]
        out_name = f"{date}-{safe_title}.md"
        out_path = topic_dir / out_name

        # 增量更新frontmatter
        if update and out_path.exists():
            existing = self._parse_frontmatter(out_path.read_text(encoding="utf-8"))
            compilations = existing.get("compilations", 0) + 1
            sources = self._merge_sources(existing.get("sources", []), [str(fpath)])
        else:
            compilations = 1
            sources = [str(fpath)]

        # 提取标签
        tags = self._extract_tags(content, topic)

        # 生成结构化内容
        structured = self._structure_content(content)

        fm = {
            "title": title,
            "summary": structured["summary"],
            "tags": ", ".join(tags),
            "created": datetime.now().strftime("%Y-%m-%d") if not update else self._get_created(out_path),
            "updated": datetime.now().strftime("%Y-%m-%d"),
            "compilations": compilations,
            "sources": ", ".join(f'"{s}"' for s in sources),
            "related": ", ".join(str(r) for r in self._find_related_notes(structured["keywords"], topic)),
            "confidence": self._assess_confidence(content),
            "status": "active",
            "content": structured["body"],
            "key_points": structured["key_points"],
            "relationships": structured["relationships"],
            "pending": structured["pending"],
            # V2.0 新增字段
            "context": structured.get("context", ""),
            "focus": structured.get("focus", ""),
            "learned": datetime.now().strftime("%Y-%m-%d"),
            "valid_from": datetime.now().strftime("%Y-%m-%d"),
            "valid_until": "",
            "metadata": structured.get("metadata", ""),
        }

        out_path.write_text(FRONTMATTER_TEMPLATE.format(**fm), encoding="utf-8")

        # 更新编译状态
        self._state[str(rel)] = {
            "mtime": fpath.stat().st_mtime,
            "out_path": str(out_path),
        }

        print(f"  {'更新' if update else '新建'}: {out_path.relative_to(self.wiki_dir)}")

    def _infer_topic(self, fpath: Path) -> str:
        """从路径推断topic目录"""
        parts = fpath.parts
        if len(parts) > 1:
            first = parts[0].lower()
            if first in self.TOPIC_DIRS:
                return self.TOPIC_DIRS[first]
        # 从文件名推断
        stem = fpath.stem.lower()
        for key, val in self.TOPIC_DIRS.items():
            if key in stem:
                return val
        return "00-analysis"

    def _extract_title(self, content: str, default: str) -> str:
        """提取标题"""
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
            if line.startswith("**Title:**", 0) or re.match(r"^##?\s+\w", line):
                return re.sub(r"^#+\s+", "", line).strip()
        return default.replace("-", " ").replace("_", " ").title()

    def _extract_tags(self, content: str, topic: str) -> List[str]:
        """提取标签"""
        tags = [f"#{topic.replace('-', '/')}"]
        # 从frontmatter提取
        fm_match = re.search(r"tags:\s*\[(.*?)\]", content, re.DOTALL)
        if fm_match:
            existing = [t.strip() for t in fm_match.group(1).split(",")]
            tags.extend([t for t in existing if t.startswith("#")])
        # 从内容提取关键词
        keywords = self._extract_keywords(content)
        for kw in keywords[:3]:
            tag = f"#{kw.lower().replace(' ', '-')}"
            if tag not in tags:
                tags.append(tag)
        return tags

    def _extract_keywords(self, content: str) -> List[str]:
        """简单关键词提取（去掉停用词）"""
        stop = {"的", "是", "在", "了", "和", "与", "或", "以及", "以及", "this", "that", "the", "and", "or", "is", "are", "was", "were", "a", "an", "in", "on", "at", "to", "for", "of", "with", "by"}
        words = re.findall(r"[\w]{2,20}", content.lower())
        freq = {}
        for w in words:
            if w not in stop and len(w) > 2:
                freq[w] = freq.get(w, 0) + 1
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w for w, _ in sorted_words[:10]]

    def _structure_content(self, content: str) -> Dict:
        """将原始内容结构化，提取V2.0元字段"""
        # 去掉frontmatter
        body = re.sub(r"^---\n.*?\n---", "", content, flags=re.DOTALL).strip()

        # 生成摘要（第一段或前200字）
        paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
        summary = paragraphs[0][:200] if paragraphs else ""
        if len(summary) < 50 and len(paragraphs) > 1:
            summary = paragraphs[1][:200]

        # 提取要点
        key_points = []
        for para in paragraphs:
            if para.startswith("- ") or para.startswith("* "):
                key_points.append(para)
        if not key_points:
            key_points = [f"- {p[:100]}" for p in paragraphs[:3] if len(p) > 20]

        # 提取待验证项
        pending = []
        for line in body.split("\n"):
            if "?" in line or "待" in line or "TODO" in line or "[ ]" in line:
                pending.append(line.strip())

        # 关键词
        keywords = self._extract_keywords(body)

        # V2.0 新增：提取上下文(## 上下文 / ## Context)
        context = ""
        ctx_match = re.search(r"(?:^|\n)## ?(?:上下文|Context)[^\n]*\n+(.*?)(?=\n## |$)", body, re.DOTALL | re.IGNORECASE)
        if ctx_match:
            context = ctx_match.group(1).strip()[:300]

        # V2.0 新增：提取专注点(## 专注点 / ## Focus)
        focus = ""
        focus_match = re.search(r"(?:^|\n)## ?(?:专注点|Focus)[^\n]*\n+(.*?)(?=\n## |$)", body, re.DOTALL | re.IGNORECASE)
        if focus_match:
            focus = focus_match.group(1).strip()[:200]

        # V2.0 新增：提取元注释(## 元注释 / For Future Claude / ## Metadata)
        metadata = ""
        meta_patterns = [
            r"(?:^|\n)## ?(?:元注释|For Future Claude|Metadata)[^\n]*\n+(.*?)(?=\n## |$)",
            r"<!-- ?For Future Claude[^\n]*\n+(.*?)-->",
        ]
        for pattern in meta_patterns:
            meta_match = re.search(pattern, body, re.DOTALL | re.IGNORECASE)
            if meta_match:
                metadata = meta_match.group(1).strip()[:500]
                break

        return {
            "summary": summary.replace('"', "'"),
            "body": body,
            "key_points": "\n".join(key_points[:5]),
            "relationships": "",
            "pending": "\n".join(f"- [ ] {p}" for p in pending[:5]),
            "keywords": keywords,
            # V2.0 新增字段
            "context": context,
            "focus": focus,
            "metadata": metadata,
        }

    def _assess_confidence(self, content: str) -> float:
        """评估置信度"""
        score = 0.5
        if len(content) > 500:
            score += 0.1
        if "[[" in content:  # 有链接
            score += 0.1
        if re.search(r"\d{4}-\d{2}-\d{2}", content):  # 有日期
            score += 0.05
        if "来源" in content or "source" in content.lower():  # 有引用
            score += 0.1
        if "?" not in content and "TODO" not in content:  # 无待办
            score += 0.05
        return min(score, 0.99)

    def _find_related_notes(self, keywords: List[str], topic: str) -> List[str]:
        """查找相关笔记"""
        topic_dir = self.wiki_dir / topic
        if not topic_dir.exists():
            return []

        related = []
        for fpath in topic_dir.glob("*.md"):
            content = fpath.read_text(encoding="utf-8")
            title = self._parse_frontmatter(content).get("title", fpath.stem)
            for kw in keywords[:3]:
                if kw.lower() in content.lower() and title not in related:
                    related.append(title)
                    break
            if len(related) >= 5:
                break
        return related[:5]

    def _merge_sources(self, existing: List, new: List) -> List:
        """合并sources列表"""
        seen = set(existing)
        merged = list(existing)
        for s in new:
            if s not in seen:
                merged.append(s)
                seen.add(s)
        return merged[:10]  # 最多10个来源

    def _get_created(self, path: Path) -> str:
        """获取笔记创建日期"""
        if path.exists():
            fm = self._parse_frontmatter(path.read_text(encoding="utf-8"))
            return fm.get("created", datetime.now().strftime("%Y-%m-%d"))
        return datetime.now().strftime("%Y-%m-%d")

    def _parse_frontmatter(self, content: str) -> Dict:
        """解析frontmatter，自动类型转换"""
        fm = {}
        m = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if m:
            for line in m.group(1).split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip()
                    # 类型强制转换
                    if v.lstrip("-").isdigit():
                        fm[k] = int(v)
                    elif v.lstrip("-").replace(".", "", 1).isdigit():
                        fm[k] = float(v)
                    elif v == "true":
                        fm[k] = True
                    elif v == "false":
                        fm[k] = False
                    elif v.startswith("[") and v.endswith("]"):
                        # 简单列表解析: [a, b, c] → ['a', 'b', 'c']
                        inner = v[1:-1].strip()
                        if inner:
                            fm[k] = [x.strip().strip('"').strip("'") for x in inner.split(",")]
                        else:
                            fm[k] = []
                    else:
                        fm[k] = v.strip('"').strip("'")
        return fm

    # ── 索引更新 ───────────────────────────────────────────────

    def _update_global_index(self):
        """更新全局主题索引"""
        index_path = self.meta_dir / "global-index.md"
        sections = {}
        for topic_dir in sorted(self.wiki_dir.glob("[0-9][0-9]-*")):
            if topic_dir.is_dir() and topic_dir.name not in ("_meta", "_inbox", "_outbox", "_logs", "raw"):
                topic_name = topic_dir.name
                notes = []
                for fpath in sorted(topic_dir.glob("*.md")):
                    fm = self._parse_frontmatter(fpath.read_text(encoding="utf-8"))
                    title = fm.get("title", fpath.stem)
                    updated = fm.get("updated", "?")
                    notes.append(f"  - {title} ({updated})")
                if notes:
                    sections[topic_name] = f"## {topic_name}\n" + "\n".join(notes) + "\n"

        content = "# 全局主题索引\n\n"
        content += f"更新: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        content += "\n".join(sections.values())
        content += "\n\n<!-- 自动生成，请勿手动编辑 -->\n"
        index_path.write_text(content, encoding="utf-8")

    # ── 状态管理 ───────────────────────────────────────────────

    def _load_state(self) -> Dict:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save_state(self):
        self.meta_dir.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self._state, indent=2, ensure_ascii=False), encoding="utf-8")

    # ── 写入接口 ───────────────────────────────────────────────

    def write_from_output(self, topic: str, content: str) -> Path:
        """将Claude输出直接写入wiki（Phase 3核心）"""
        # 推送到inbox
        date = datetime.now().strftime("%Y-%m-%d")
        inbox_name = f"{date}-inbox-{datetime.now().strftime('%H%M%S')}.md"
        inbox_path = self.inbox_dir / inbox_name
        inbox_path.write_text(content, encoding="utf-8")
        print(f"  写入inbox: {inbox_path.relative_to(self.wiki_dir)}")

        # 同步编译到对应目录
        topic_key = topic.lower()
        if topic_key in self.TOPIC_DIRS:
            topic_dir = self.TOPIC_DIRS[topic_key]
        else:
            topic_dir = self._infer_topic(Path(topic))

        topic_wiki = self.wiki_dir / topic_dir
        title = self._extract_title(content, topic)
        safe_title = re.sub(r"[^\w\s-]", "", title)[:60]
        out_name = f"{date}-{safe_title}.md"
        out_path = topic_wiki / out_name

        structured = self._structure_content(content)
        tags = [f"#{topic.lower().replace(' ', '-')}"]
        fm = {
            "title": title,
            "summary": structured["summary"],
            "tags": ", ".join(tags),
            "created": date,
            "updated": date,
            "compilations": 1,
            "sources": f'"inbox:{inbox_name}"',
            "related": "",
            "confidence": self._assess_confidence(content),
            "status": "active",
            "content": structured["body"],
            "key_points": structured["key_points"],
            "relationships": "",
            "pending": structured["pending"],
            # V2.0 新增字段
            "context": structured.get("context", ""),
            "focus": structured.get("focus", ""),
            "metadata": structured.get("metadata", ""),
            "learned": "",          # 待填充：是否从经验学习
            "valid_from": date,     # 默认当天生效
            "valid_until": "",      # 空=永久有效
        }
        out_path.write_text(FRONTMATTER_TEMPLATE.format(**fm), encoding="utf-8")
        self._update_global_index()
        return out_path
