#!/usr/bin/env python3
"""
LLM Wiki Router - Scale-Aware 检索路由
个人规模 (<100笔记) → 直接读取
团队规模 (100-1000笔记) → 标题索引+grep
企业规模 (>1000笔记) → LightRAG双层检索
"""
import re
import subprocess
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class WikiRouter:
    """
    Scale-Aware路由策略 - Karpathy模式的核心洞察：
    个人规模不需要向量检索，直接读取文件即可
    """

    PERSONAL_THRESHOLD = 100
    TEAM_THRESHOLD = 1000

    def __init__(self, wiki_dir: Path):
        self.wiki_dir = wiki_dir

    def query(self, query: str, limit: int = 10) -> List[Dict]:
        """查询wiki - 根据规模自动选择策略"""
        note_count = self._count_notes()

        if note_count <= self.PERSONAL_THRESHOLD:
            # 个人规模：直接读取所有笔记
            return self._personal_query(query, limit)
        elif note_count <= self.TEAM_THRESHOLD:
            # 团队规模：标题索引 + grep
            return self._team_query(query, limit)
        else:
            # 企业规模：委托给LightRAG
            return self._enterprise_query(query, limit)

    def _personal_query(self, query: str, limit: int) -> List[Dict]:
        """个人规模：直接读取 + LLM筛选"""
        results = []
        keywords = self._extract_keywords(query)

        for fpath in self.wiki_dir.glob("**/*.md"):
            if "_" in fpath.parts[0]:
                continue
            try:
                content = fpath.read_text(encoding="utf-8")
                fm = self._parse_fm(content)
                title = fm.get("title", fpath.stem)
                summary = fm.get("summary", "")
                tags = fm.get("tags", "").split(",")

                # 关键词匹配
                score = self._match_score(content, keywords, title, tags)
                if score > 0:
                    results.append({
                        "title": title,
                        "summary": summary,
                        "tags": [t.strip() for t in tags if t.strip()],
                        "updated": fm.get("updated", ""),
                        "path": str(fpath),
                        "score": score,
                        "content_preview": content[:300],
                    })
            except Exception:
                pass

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def _team_query(self, query: str, limit: int) -> List[Dict]:
        """团队规模：grep标题 + 快速筛选"""
        results = []
        keywords = self._extract_keywords(query)

        # grep标题匹配
        for fpath in self.wiki_dir.glob("**/*.md"):
            if "_" in fpath.parts[0]:
                continue
            try:
                content = fpath.read_text(encoding="utf-8")
                fm = self._parse_fm(content)
                title = fm.get("title", fpath.stem)
                summary = fm.get("summary", "")
                tags = fm.get("tags", "").split(",")

                score = 0
                for kw in keywords:
                    if kw.lower() in title.lower():
                        score += 3
                    if kw.lower() in summary.lower():
                        score += 1
                    if any(kw.lower() in t.lower() for t in tags):
                        score += 2

                if score > 0:
                    results.append({
                        "title": title,
                        "summary": summary,
                        "tags": [t.strip() for t in tags if t.strip()],
                        "updated": fm.get("updated", ""),
                        "path": str(fpath),
                        "score": score,
                        "content_preview": content[:300],
                    })
            except Exception:
                pass

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def _enterprise_query(self, query: str, limit: int) -> List[Dict]:
        """企业规模：委托给LightRAG（如果已集成）"""
        # 尝试调用LightRAG
        try:
            from skills.lightrag_hku_wrapper import LightRAGWrapper
            rag = LightRAGWrapper()
            return rag.query(query, limit)
        except ImportError:
            # 回退到团队策略
            print("LightRAG未集成，回退到grep策略")
            return self._team_query(query, limit)

    def _count_notes(self) -> int:
        """计算笔记总数"""
        count = 0
        for fpath in self.wiki_dir.glob("**/*.md"):
            if "_" in fpath.parts[0]:
                continue
            count += 1
        return count

    def _extract_keywords(self, query: str) -> List[str]:
        """提取查询关键词"""
        words = re.findall(r"[\w]{2,20}", query.lower())
        stop = {"的", "是", "在", "了", "和", "与", "the", "a", "an", "of", "in", "for", "to", "what", "how", "why", "when", "where", "about", "有关", "关于"}
        return [w for w in words if w not in stop and len(w) > 1]

    def _match_score(self, content: str, keywords: List[str], title: str, tags: List[str]) -> float:
        """计算匹配分数"""
        score = 0.0
        content_lower = content.lower()
        for kw in keywords:
            # 标题命中权重最高
            if kw.lower() in title.lower():
                score += 5.0
            # 标签命中
            if any(kw.lower() in t.lower() for t in tags):
                score += 3.0
            # 内容命中
            count = content_lower.count(kw.lower())
            score += min(count * 0.5, 3.0)
        return score

    def _parse_fm(self, content: str) -> Dict:
        """解析frontmatter"""
        fm = {}
        m = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if m:
            for line in m.group(1).split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip()
        return fm
