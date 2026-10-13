#!/usr/bin/env python3
"""
LLM Wiki Self-Healing - 自愈管道
Phase 4: LINT & MAINTAIN
LLM扫描wiki → 发现不一致/过期/断裂链接 → 主动修复
"""
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set
from scripts.compile import WikiCompiler


class WikiHealer:
    """
    Wiki自愈管道 - 让知识库自我修复
    检查项：断裂链接、孤立笔记、过时、矛盾、缺失链接
    """

    STALE_DAYS = 90

    def __init__(self, wiki_dir: Path):
        self.wiki_dir = wiki_dir
        self.meta_dir = wiki_dir / "_meta"
        self._all_notes: Dict[Path, Dict] = {}
        self._link_map: Dict[str, Set[Path]] = {}
        self._title_map: Dict[str, Path] = {}
        self._broken_links: List[Dict] = []
        self._stale_notes: List[Path] = []
        self._orphan_paths: Set[Path] = set()

    def health_check(self) -> Dict:
        """健康度检查"""
        self._scan_all_notes()

        total = len(self._all_notes)
        orphans = self._find_orphans()
        broken = self._find_broken_links()
        stale = self._find_stale_notes()
        disputed = self._find_disputed()

        # 健康分计算
        health = 100
        if total > 0:
            health -= min(30, (orphans / total) * 30)
            health -= min(30, (broken / total) * 30)
            health -= min(20, (stale / total) * 20)
            health -= min(10, (disputed / total) * 10)

        return {
            "total": total,
            "orphans": orphans,
            "broken_links": broken,
            "stale": stale,
            "disputed": disputed,
            "active": total - orphans - stale,
            "health_score": max(health, 0),
        }

    def self_heal(self) -> Dict:
        """自愈管道"""
        self._scan_all_notes()

        fixes = {
            "links_fixed": 0,
            "marked_stale": 0,
            "conflicts_resolved": 0,
            "links_suggested": 0,
            "errors": 0,
        }

        try:
            # 1. 修复断裂链接
            fixes["links_fixed"] = self._heal_broken_links()

            # 2. 标记过时笔记
            fixes["marked_stale"] = self._mark_stale()

            # 3. 更新孤立笔记列表
            fixes["links_suggested"] = self._suggest_orphan_links()

            # 4. 生成健康报告
            self._write_health_report()
        except Exception as e:
            print(f"自愈错误: {e}")
            fixes["errors"] = 1

        return fixes

    # ── 扫描 ────────────────────────────────────────────────

    def _scan_all_notes(self):
        """扫描所有笔记"""
        self._all_notes = {}
        self._link_map = {}
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

                # 提取链接
                for link in re.findall(r'"\[\[(.+?)\]\]"', content):
                    if link not in self._link_map:
                        self._link_map[link] = set()
                    self._link_map[link].add(fpath)
            except Exception:
                pass

    def _parse_fm(self, content: str) -> Dict:
        """解析frontmatter，YAML值去掉引号包裹"""
        fm = {}
        m = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        if m:
            for line in m.group(1).split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    v = v.strip()
                    # 去掉YAML引号包裹 "value" 或 'value'
                    if len(v) >= 2 and ((v[0] == '"' and v[-1] == '"') or (v[0] == "'" and v[-1] == "'")):
                        v = v[1:-1]
                    fm[k.strip()] = v
        return fm

    # ── 自愈核心 ───────────────────────────────────────────

    def _find_orphans(self) -> int:
        """查找孤立笔记（无反向链接）"""
        # 有反向链接的笔记 = 链接目标存在 的笔记
        # 注意：只有有效链接（目标在title_map中）的引用者才脱离孤立状态
        linked = set()
        for link, refs in self._link_map.items():
            if link in self._title_map:
                # 链接目标笔记不是孤立笔记
                linked.add(self._title_map[link])
                # 引用者也只有在链接有效时才脱离孤立状态
                for ref in refs:
                    linked.add(ref)

        orphan_paths = set(self._all_notes.keys()) - linked
        self._orphan_paths = orphan_paths
        return len(orphan_paths)

    def _find_broken_links(self) -> int:
        """查找断裂链接"""
        broken = 0
        self._broken_links: List[Dict] = []

        for link, refs in self._link_map.items():
            if link not in self._title_map:
                for ref in refs:
                    broken += 1
                    self._broken_links.append({"link": link, "ref": ref})

        return broken

    def _find_stale_notes(self) -> int:
        """查找过时笔记"""
        stale = 0
        self._stale_notes: List[Path] = []
        cutoff = datetime.now() - timedelta(days=self.STALE_DAYS)

        for fpath, fm in self._all_notes.items():
            updated_str = fm.get("updated", "")
            try:
                updated = datetime.strptime(updated_str, "%Y-%m-%d")
                if updated < cutoff:
                    stale += 1
                    self._stale_notes.append(fpath)
            except Exception:
                pass
        return stale

    def _find_disputed(self) -> int:
        """查找争议笔记"""
        disputed = 0
        for fm in self._all_notes.values():
            if fm.get("status") == "disputed":
                disputed += 1
        return disputed

    def _heal_broken_links(self) -> int:
        """修复断裂链接"""
        fixed = 0
        for item in self._broken_links:
            link = item["link"]
            ref_path = item["ref"]

            # 尝试模糊匹配
            matched_title = None
            for title in self._title_map.keys():
                if link.lower() in title.lower() or title.lower() in link.lower():
                    matched_title = title
                    break

            if matched_title:
                # 替换链接（链接格式为"[[Title]]"，需保留双引号）
                content = ref_path.read_text(encoding="utf-8")
                new_content = content.replace(f'"[[{link}]]"', f'"[[{matched_title}]]"')
                ref_path.write_text(new_content, encoding="utf-8")
                fixed += 1
                print(f"  修复链接: {ref_path.name} ({link} -> {matched_title})")
            else:
                # 标记为stale并添加TODO
                content = ref_path.read_text(encoding="utf-8")
                if "## 待验证" not in content:
                    content += "\n\n## 待验证\n\n"
                content += f"- [ ] 断裂链接: [[{link}]]\n"
                ref_path.write_text(content, encoding="utf-8")

        return fixed

    def _mark_stale(self) -> int:
        """标记过时笔记"""
        marked = 0
        for fpath in self._stale_notes:
            content = fpath.read_text(encoding="utf-8")
            # 更新frontmatter的status
            if "status: active" in content:
                content = content.replace("status: active", "status: stale")
                fpath.write_text(content, encoding="utf-8")
                marked += 1
                print(f"  标记陈旧: {fpath.name}")
        return marked

    def _suggest_orphan_links(self) -> int:
        """为孤立笔记建议链接"""
        suggested = 0
        suggestions = []

        for orphan_path in self._orphan_paths:
            orphan_fm = self._all_notes.get(orphan_path, {})
            orphan_title = orphan_fm.get("title", orphan_path.stem)
            orphan_keywords = orphan_fm.get("tags", "").split(",")

            # 查找潜在相关笔记
            for other_path, other_fm in self._all_notes.items():
                if other_path == orphan_path:
                    continue
                other_title = other_fm.get("title", other_path.stem)
                other_keywords = other_fm.get("tags", "").split(",")

                # 标签重叠
                overlap = set(t.strip().lower() for t in orphan_keywords) & \
                          set(t.strip().lower() for t in other_keywords)
                if len(overlap) >= 1:
                    suggestions.append(f"- [[{orphan_title}]] 可能与 [[{other_title}]] 相关 (共享标签: {', '.join(overlap)})")
                    suggested += 1

        # 写入孤立笔记建议
        if suggestions:
            orphan_file = self.meta_dir / "orphan-notes.md"
            existing = orphan_file.read_text(encoding="utf-8") if orphan_file.exists() else ""
            new_suggestions = "# 孤立笔记\n\n> 无反向链接的笔记\n\n## 链接建议\n\n" + "\n".join(suggestions[:20])
            orphan_file.write_text(new_suggestions, encoding="utf-8")
            print(f"  生成孤立笔记链接建议: {len(suggestions)} 条")

        return suggested

    def _write_health_report(self):
        """写入健康度报告"""
        report = self.health_check()
        content = f"""# Wiki健康报告

生成: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 概览

| 指标 | 数值 |
|------|------|
| 总笔记 | {report['total']} |
| 活跃笔记 | {report['active']} |
| 陈旧笔记 | {report['stale']} |
| 孤立笔记 | {report['orphans']} |
| 断裂链接 | {report['broken_links']} |
| 争议笔记 | {report['disputed']} |
| **健康分** | **{report['health_score']:.1f}/100** |

## 状态分布

"""
        for status in ["active", "stale", "disputed"]:
            count = sum(1 for fm in self._all_notes.values() if fm.get("status") == status)
            bar = "█" * (count // 5) + "░" * (20 - count // 5)
            content += f"- [{status}] {bar} {count}\n"

        content += "\n<!-- 自动生成 -->\n"
        (self.meta_dir / "health-report.md").write_text(content, encoding="utf-8")
