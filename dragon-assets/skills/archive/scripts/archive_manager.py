#!/usr/bin/env python3
"""
archive_manager.py - 跨会话知识归档管理器

功能：
- session归档（自动捕获关键输出）
- 知识索引（按主题/日期/项目组织）
- 搜索（跨会话语义搜索）
- 摘要生成（自动总结归档内容）
- 与天龙引擎claude-mem、lessons.md协同
"""

import os
import sys
import json
import uuid
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_ARCHIVE_PATH = os.path.expanduser('~/.claude/archive')
DEFAULT_DB_PATH = os.path.expanduser('~/.claude/archive.db')


class ArchiveType(Enum):
    """归档类型枚举"""
    DECISION = "decision"
    PATTERN = "pattern"
    DISCOVERY = "discovery"
    PROJECT = "project"


@dataclass
class ArchiveEntry:
    """归档条目"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = "decision"
    title: str = ""
    content: str = ""
    project: str = "default"
    category: str = ""
    tags: List[str] = field(default_factory=list)
    created: str = field(default_factory=lambda: datetime.now().isoformat())
    updated: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0
    last_accessed: Optional[str] = None
    related: List[str] = field(default_factory=list)
    confidence: float = 0.8
    status: str = "active"

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'ArchiveEntry':
        return cls(**data)


class ArchiveManager:
    """跨会话知识归档管理器"""

    def __init__(
        self,
        archive_path: Optional[str] = None,
        db_path: Optional[str] = None
    ):
        self.archive_path = Path(archive_path or DEFAULT_ARCHIVE_PATH)
        self.db_path = Path(db_path or DEFAULT_DB_PATH)
        self._ensure_directories()

    def _ensure_directories(self):
        """确保归档目录结构存在"""
        directories = [
            'decisions',
            'patterns',
            'discoveries',
            'projects',
            'sessions',
        ]

        self.archive_path.mkdir(parents=True, exist_ok=True)

        for dir_name in directories:
            (self.archive_path / dir_name).mkdir(exist_ok=True)

        # 创建索引文件
        self._ensure_index('decisions')
        self._ensure_index('patterns')
        self._ensure_index('discoveries')
        self._ensure_index('projects')

        # 创建元数据
        meta_path = self.archive_path / '.archive_meta.json'
        if not meta_path.exists():
            meta = {
                'version': '1.0.0',
                'created': datetime.now().isoformat(),
                'total_entries': 0,
                'by_type': {
                    'decision': 0,
                    'pattern': 0,
                    'discovery': 0,
                    'project': 0
                }
            }
            meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8')

        logger.info(f"归档管理器初始化完成: {self.archive_path}")

    def _ensure_index(self, category: str):
        """确保索引文件存在"""
        index_path = self.archive_path / category / 'index.json'
        if not index_path.exists():
            index_path.write_text(json.dumps({'entries': []}, indent=2, ensure_ascii=False), encoding='utf-8')

    def _get_index_path(self, archive_type: str) -> Path:
        """获取指定类型的索引文件路径"""
        type_map = {
            'decision': 'decisions',
            'pattern': 'patterns',
            'discovery': 'discoveries',
            'project': 'projects'
        }
        category = type_map.get(archive_type, archive_type)
        return self.archive_path / category / 'index.json'

    def _load_index(self, archive_type: str) -> Dict:
        """加载索引"""
        index_path = self._get_index_path(archive_type)
        try:
            return json.loads(index_path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, FileNotFoundError):
            return {'entries': []}

    def _save_index(self, archive_type: str, index: Dict):
        """保存索引"""
        index_path = self._get_index_path(archive_type)
        index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding='utf-8')

    def _update_meta(self, entry: ArchiveEntry, is_add: bool = True):
        """更新元数据"""
        meta_path = self.archive_path / '.archive_meta.json'
        try:
            meta = json.loads(meta_path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, FileNotFoundError):
            meta = {'version': '1.0.0', 'total_entries': 0, 'by_type': {}}

        if is_add:
            meta['total_entries'] = meta.get('total_entries', 0) + 1
            meta['by_type'][entry.type] = meta['by_type'].get(entry.type, 0) + 1
        else:
            meta['total_entries'] = max(0, meta.get('total_entries', 0) - 1)
            meta['by_type'][entry.type] = max(0, meta['by_type'].get(entry.type, 0) - 1)

        meta['last_updated'] = datetime.now().isoformat()
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8')

    def save(
        self,
        title: str,
        content: str,
        archive_type: str = "decision",
        project: str = "default",
        category: str = "",
        tags: Optional[List[str]] = None,
        related: Optional[List[str]] = None,
        confidence: float = 0.8
    ) -> ArchiveEntry:
        """保存归档条目"""
        entry = ArchiveEntry(
            type=archive_type,
            title=title,
            content=content,
            project=project,
            category=category,
            tags=tags or [],
            related=related or [],
            confidence=confidence
        )

        # 确定存储路径
        type_map = {
            'decision': 'decisions',
            'pattern': 'patterns',
            'discovery': 'discoveries',
            'project': 'projects'
        }
        category_dir = type_map.get(archive_type, 'decisions')

        # 生成文件名
        date_str = datetime.now().strftime('%Y-%m-%d')
        slug = self._slugify(title)[:50]
        filename = f"{date_str}-{slug}.md"
        file_path = self.archive_path / category_dir / filename

        # 写入内容
        md_content = self._generate_markdown(entry)
        file_path.write_text(md_content, encoding='utf-8')

        # 更新索引
        index = self._load_index(archive_type)
        index['entries'].append({
            'id': entry.id,
            'title': entry.title,
            'file': filename,
            'created': entry.created,
            'tags': entry.tags,
            'project': entry.project
        })
        self._save_index(archive_type, index)

        # 更新元数据
        self._update_meta(entry, is_add=True)

        logger.info(f"归档已保存: [{entry.type}] {entry.title}")
        return entry

    def _slugify(self, text: str) -> str:
        """将文本转换为URL友好slug"""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')

    def _generate_markdown(self, entry: ArchiveEntry) -> str:
        """生成Markdown格式的归档内容"""
        lines = [
            f"# {entry.title}",
            "",
            f"**类型**: {entry.type}",
            f"**项目**: {entry.project}",
            f"**分类**: {entry.category}",
            f"**创建时间**: {entry.created}",
            f"**置信度**: {entry.confidence}",
            "",
            "## 内容",
            "",
            entry.content,
            "",
            "## 标签",
            "",
        ]

        if entry.tags:
            lines.append(", ".join(f"`{tag}`" for tag in entry.tags))
        else:
            lines.append("_无标签_")

        lines.extend([
            "",
            "## 关联归档",
            "",
        ])

        if entry.related:
            for related_id in entry.related:
                lines.append(f"- 见 #{related_id}")
        else:
            lines.append("_无关联_")

        lines.extend([
            "",
            "---",
            f"*归档ID: {entry.id}*",
        ])

        return "\n".join(lines)

    def search(
        self,
        query: str,
        archive_type: Optional[str] = None,
        project: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[ArchiveEntry]:
        """搜索归档"""
        results = []
        types_to_search = [archive_type] if archive_type else ['decision', 'pattern', 'discovery', 'project']

        query_lower = query.lower()

        for atype in types_to_search:
            index = self._load_index(atype)

            for entry_meta in index.get('entries', []):
                # 项目过滤
                if project and entry_meta.get('project') != project:
                    continue

                # 标签过滤
                if tags:
                    entry_tags = set(entry_meta.get('tags', []))
                    if not entry_tags.intersection(set(tags)):
                        continue

                # 读取完整内容进行搜索
                filename = entry_meta.get('file', '')
                if not filename:
                    continue

                type_map = {
                    'decision': 'decisions',
                    'pattern': 'patterns',
                    'discovery': 'discoveries',
                    'project': 'projects'
                }
                category_dir = type_map.get(atype, atype)
                file_path = self.archive_path / category_dir / filename

                if not file_path.exists():
                    continue

                content = file_path.read_text(encoding='utf-8').lower()

                # 简单关键词匹配
                if query_lower in content or query_lower in entry_meta.get('title', '').lower():
                    # 构建Entry对象
                    entry = ArchiveEntry(
                        id=entry_meta['id'],
                        type=atype,
                        title=entry_meta['title'],
                        created=entry_meta['created'],
                        tags=entry_meta.get('tags', []),
                        project=entry_meta.get('project', 'default')
                    )
                    results.append(entry)

                    if len(results) >= limit:
                        return results

        # 按置信度和访问次数排序
        results.sort(key=lambda x: (x.confidence, x.access_count), reverse=True)
        return results[:limit]

    def list(
        self,
        archive_type: Optional[str] = None,
        project: Optional[str] = None,
        limit: int = 20
    ) -> List[ArchiveEntry]:
        """列出归档"""
        results = []
        types_to_list = [archive_type] if archive_type else ['decision', 'pattern', 'discovery', 'project']

        for atype in types_to_list:
            index = self._load_index(atype)

            for entry_meta in index.get('entries', []):
                if project and entry_meta.get('project') != project:
                    continue

                entry = ArchiveEntry(
                    id=entry_meta['id'],
                    type=atype,
                    title=entry_meta['title'],
                    created=entry_meta['created'],
                    tags=entry_meta.get('tags', []),
                    project=entry_meta.get('project', 'default')
                )
                results.append(entry)

        # 按时间倒序
        results.sort(key=lambda x: x.created, reverse=True)
        return results[:limit]

    def get(self, entry_id: str) -> Optional[ArchiveEntry]:
        """获取单个归档"""
        types_to_search = ['decision', 'pattern', 'discovery', 'project']

        for atype in types_to_search:
            index = self._load_index(atype)

            for entry_meta in index.get('entries', []):
                if entry_meta['id'] == entry_id:
                    # 读取完整内容
                    filename = entry_meta.get('file', '')
                    if not filename:
                        continue

                    type_map = {
                        'decision': 'decisions',
                        'pattern': 'patterns',
                        'discovery': 'discoveries',
                        'project': 'projects'
                    }
                    category_dir = type_map.get(atype, atype)
                    file_path = self.archive_path / category_dir / filename

                    if not file_path.exists():
                        continue

                    content = file_path.read_text(encoding='utf-8')

                    # 解析内容
                    entry = ArchiveEntry(
                        id=entry_meta['id'],
                        type=atype,
                        title=entry_meta['title'],
                        content=content,
                        created=entry_meta['created'],
                        tags=entry_meta.get('tags', []),
                        project=entry_meta.get('project', 'default'),
                        access_count=entry_meta.get('access_count', 0)
                    )

                    # 更新访问计数
                    entry_meta['access_count'] = entry_meta.get('access_count', 0) + 1
                    entry_meta['last_accessed'] = datetime.now().isoformat()
                    self._save_index(atype, index)

                    return entry

        return None

    def delete(self, entry_id: str) -> bool:
        """删除归档"""
        types_to_search = ['decision', 'pattern', 'discovery', 'project']

        for atype in types_to_search:
            index = self._load_index(atype)
            entries = index.get('entries', [])

            for i, entry_meta in enumerate(entries):
                if entry_meta['id'] == entry_id:
                    # 删除文件
                    filename = entry_meta.get('file', '')
                    if filename:
                        type_map = {
                            'decision': 'decisions',
                            'pattern': 'patterns',
                            'discovery': 'discoveries',
                            'project': 'projects'
                        }
                        category_dir = type_map.get(atype, atype)
                        file_path = self.archive_path / category_dir / filename
                        if file_path.exists():
                            file_path.unlink()

                    # 从索引移除
                    entries.pop(i)
                    index['entries'] = entries
                    self._save_index(atype, index)

                    # 更新元数据
                    self._update_meta(ArchiveEntry(type=atype), is_add=False)

                    logger.info(f"归档已删除: {entry_id}")
                    return True

        return False

    def summarize(
        self,
        project: Optional[str] = None,
        days: int = 30
    ) -> Dict:
        """生成归档摘要"""
        cutoff_date = datetime.now() - timedelta(days=days)

        summary = {
            'generated_at': datetime.now().isoformat(),
            'period_days': days,
            'project': project or 'all',
            'total_entries': 0,
            'by_type': {
                'decision': [],
                'pattern': [],
                'discovery': [],
                'project': []
            },
            'recent_entries': [],
            'top_tags': {}
        }

        types_to_summarize = ['decision', 'pattern', 'discovery', 'project']

        for atype in types_to_summarize:
            index = self._load_index(atype)

            for entry_meta in index.get('entries', []):
                if project and entry_meta.get('project') != project:
                    continue

                created_str = entry_meta.get('created', '')
                try:
                    created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                    if created < cutoff_date:
                        continue
                except (ValueError, AttributeError):
                    pass

                summary['total_entries'] += 1
                summary['by_type'][atype].append({
                    'id': entry_meta['id'],
                    'title': entry_meta['title'],
                    'created': entry_meta['created'],
                    'tags': entry_meta.get('tags', [])
                })

                # 更新标签统计
                for tag in entry_meta.get('tags', []):
                    summary['top_tags'][tag] = summary['top_tags'].get(tag, 0) + 1

        # 最近条目
        all_recent = []
        for atype, entries in summary['by_type'].items():
            for entry in entries[:5]:
                entry['type'] = atype
                all_recent.append(entry)

        all_recent.sort(key=lambda x: x['created'], reverse=True)
        summary['recent_entries'] = all_recent[:10]

        # 排序标签
        summary['top_tags'] = dict(
            sorted(summary['top_tags'].items(), key=lambda x: x[1], reverse=True)[:20]
        )

        return summary

    def clean(self, before_date: Optional[str] = None, keep_count: int = 10) -> int:
        """清理过期归档"""
        cleaned = 0

        if before_date:
            try:
                cutoff = datetime.fromisoformat(before_date)
            except ValueError:
                cutoff = datetime.now() - timedelta(days=365)

        types_to_clean = ['decision', 'pattern', 'discovery', 'project']

        for atype in types_to_clean:
            index = self._load_index(atype)
            entries = index.get('entries', [])

            # 按日期排序
            sorted_entries = sorted(
                entries,
                key=lambda x: x.get('created', ''),
                reverse=True
            )

            # 保留最近的keep_count条
            to_keep = sorted_entries[:keep_count]
            to_delete = sorted_entries[keep_count:]

            if before_date:
                to_delete = [
                    e for e in to_delete
                    if datetime.fromisoformat(e.get('created', '2000-01-01')) < cutoff
                ]

            # 删除文件
            for entry_meta in to_delete:
                filename = entry_meta.get('file', '')
                if filename:
                    type_map = {
                        'decision': 'decisions',
                        'pattern': 'patterns',
                        'discovery': 'discoveries',
                        'project': 'projects'
                    }
                    category_dir = type_map.get(atype, atype)
                    file_path = self.archive_path / category_dir / filename
                    if file_path.exists():
                        file_path.unlink()
                        cleaned += 1

            # 更新索引
            index['entries'] = to_keep
            self._save_index(atype, index)

        logger.info(f"清理完成，删除 {cleaned} 个归档")
        return cleaned

    def check(self, task_description: str) -> List[Dict]:
        """检查是否有相关归档"""
        query_lower = task_description.lower()

        # 提取关键词
        keywords = []
        important_words = ['数据库', '架构', '设计', '模式', '选择', '使用', '依赖', '项目', '代码']
        for word in important_words:
            if word in query_lower:
                keywords.append(word)

        results = []
        if keywords:
            for keyword in keywords[:3]:
                matches = self.search(keyword, limit=3)
                for match in matches:
                    results.append({
                        'type': match.type,
                        'title': match.title,
                        'project': match.project,
                        'relevance': 'high' if keyword in match.title.lower() else 'medium'
                    })

        return results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='archive - 跨会话知识归档管理器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  archive_manager.py save "选择PostgreSQL" --type decision --project myapp
  archive_manager.py search "数据库"
  archive_manager.py list --project myapp --type decision
  archive_manager.py summarize --project myapp --days 30
  archive_manager.py check "我应该使用什么数据库"
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # save命令
    save_parser = subparsers.add_parser('save', help='保存归档')
    save_parser.add_argument('title', help='归档标题')
    save_parser.add_argument('--content', '-c', default='', help='归档内容')
    save_parser.add_argument('--type', '-t', default='decision',
                            choices=['decision', 'pattern', 'discovery', 'project'],
                            help='归档类型')
    save_parser.add_argument('--project', '-p', default='default', help='项目名称')
    save_parser.add_argument('--category', '-g', default='', help='分类')
    save_parser.add_argument('--tags', nargs='+', default=[], help='标签')
    save_parser.add_argument('--confidence', '-cf', type=float, default=0.8, help='置信度')

    # search命令
    search_parser = subparsers.add_parser('search', help='搜索归档')
    search_parser.add_argument('query', help='搜索关键词')
    search_parser.add_argument('--type', '-t', help='归档类型')
    search_parser.add_argument('--project', '-p', help='项目名称')
    search_parser.add_argument('--limit', '-l', type=int, default=10, help='结果数量')

    # list命令
    list_parser = subparsers.add_parser('list', help='列出归档')
    list_parser.add_argument('--type', '-t', help='归档类型')
    list_parser.add_argument('--project', '-p', help='项目名称')
    list_parser.add_argument('--limit', '-l', type=int, default=20, help='结果数量')

    # get命令
    get_parser = subparsers.add_parser('get', help='获取单个归档')
    get_parser.add_argument('id', help='归档ID')

    # delete命令
    delete_parser = subparsers.add_parser('delete', help='删除归档')
    delete_parser.add_argument('id', help='归档ID')

    # summarize命令
    summarize_parser = subparsers.add_parser('summarize', help='生成摘要')
    summarize_parser.add_argument('--project', '-p', help='项目名称')
    summarize_parser.add_argument('--days', '-d', type=int, default=30, help='统计天数')

    # clean命令
    clean_parser = subparsers.add_parser('clean', help='清理归档')
    clean_parser.add_argument('--before', '-b', help='清理此日期之前的归档')
    clean_parser.add_argument('--keep', '-k', type=int, default=10, help='每个类型保留数量')

    # check命令
    check_parser = subparsers.add_parser('check', help='检查相关归档')
    check_parser.add_argument('task', help='当前任务描述')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = ArchiveManager()

    if args.command == 'save':
        entry = manager.save(
            title=args.title,
            content=args.content,
            archive_type=args.type,
            project=args.project,
            category=args.category,
            tags=args.tags,
            confidence=args.confidence
        )
        print(f"归档已保存: {entry.id}")

    elif args.command == 'search':
        results = manager.search(
            query=args.query,
            archive_type=args.type,
            project=args.project,
            limit=args.limit
        )
        if results:
            print(f"找到 {len(results)} 条结果:\n")
            for r in results:
                print(f"[{r.type}] {r.title} ({r.project}) - {r.created[:10]}")
        else:
            print("未找到结果")

    elif args.command == 'list':
        results = manager.list(
            archive_type=args.type,
            project=args.project,
            limit=args.limit
        )
        if results:
            print(f"共 {len(results)} 条归档:\n")
            for r in results:
                print(f"[{r.type}] {r.title} ({r.project}) - {r.created[:10]}")
        else:
            print("暂无归档")

    elif args.command == 'get':
        entry = manager.get(args.id)
        if entry:
            print(f"# {entry.title}\n")
            print(f"类型: {entry.type}")
            print(f"项目: {entry.project}")
            print(f"创建: {entry.created}")
            print(f"标签: {', '.join(entry.tags) if entry.tags else '无'}\n")
            print("## 内容\n")
            print(entry.content)
        else:
            print("未找到归档")

    elif args.command == 'delete':
        if manager.delete(args.id):
            print("归档已删除")
        else:
            print("未找到归档")

    elif args.command == 'summarize':
        summary = manager.summarize(project=args.project, days=args.days)
        print(f"\n{'='*50}")
        print(f"归档摘要 - {summary['period_days']}天")
        print(f"{'='*50}")
        print(f"总条目: {summary['total_entries']}")
        print(f"项目: {summary['project']}\n")
        print("按类型统计:")
        for atype, entries in summary['by_type'].items():
            print(f"  {atype}: {len(entries)}")
        print("\n最近条目:")
        for entry in summary['recent_entries'][:5]:
            print(f"  [{entry['type']}] {entry['title']}")
        print("\n热门标签:")
        for tag, count in list(summary['top_tags'].items())[:10]:
            print(f"  {tag}: {count}")

    elif args.command == 'clean':
        cleaned = manager.clean(before_date=args.before, keep_count=args.keep)
        print(f"已清理 {cleaned} 个归档")

    elif args.command == 'check':
        results = manager.check(args.task)
        if results:
            print(f"发现 {len(results)} 条相关归档:\n")
            for r in results:
                print(f"[{r['type']}] {r['title']} ({r['project']}) - 相关度: {r['relevance']}")
        else:
            print("未发现相关归档")


if __name__ == '__main__':
    main()
