#!/usr/bin/env python3
"""
RedBox Subject Library - 主体库管理引擎
统一管理内容创作的主体库（人物/产品/场景），为组合创新提供结构化素材支持。

核心能力:
1. 主体查询 - 按类型/标签查询主体
2. 主体详情 - 获取主体完整信息
3. 主体创建 - 添加新主体
4. 主体更新 - 修改主体信息
5. 组合推荐 - 基于主题推荐主体组合
6. 统计分析 - 主体使用统计
"""

import json
import uuid
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Set
from datetime import datetime
from pathlib import Path

# 配置路径
CONFIG_DIR = Path.home() / ".claude" / "skills" / "redbox-subject-library"
DATA_DIR = CONFIG_DIR / "data"
SUBJECTS_FILE = DATA_DIR / "subjects.json"
STATS_FILE = DATA_DIR / "stats.json"


@dataclass
class Subject:
    """主体数据结构"""
    id: str
    name: str
    type: str  # character/product/scene
    tags: List[str]
    description: str
    attributes: Dict
    created_at: str
    updated_at: str
    usage_count: int = 0

    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Subject':
        """从字典创建"""
        return cls(**data)


class SubjectLibrary:
    """主体库管理器"""

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or SUBJECTS_FILE
        self.subjects: List[Subject] = self._load()

    def _load(self) -> List[Subject]:
        """加载主体数据"""
        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Subject.from_dict(s) for s in data]
        return []

    def _save(self):
        """保存主体数据"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in self.subjects], f,
                      ensure_ascii=False, indent=2)

    def query(self, type: str = None, tags: List[str] = None,
              limit: int = 10) -> List[Subject]:
        """
        查询主体

        Args:
            type: 主体类型 (character/product/scene)
            tags: 标签列表
            limit: 返回数量限制

        Returns:
            匹配的主体列表，按使用次数降序
        """
        results = self.subjects

        # 按类型过滤
        if type:
            results = [s for s in results if s.type == type]

        # 按标签过滤
        if tags:
            results = [s for s in results
                      if any(t in s.tags for t in tags)]

        # 按使用次数降序
        return sorted(results, key=lambda x: x.usage_count,
                      reverse=True)[:limit]

    def get(self, subject_id: str) -> Optional[Subject]:
        """获取主体详情"""
        for s in self.subjects:
            if s.id == subject_id:
                return s
        return None

    def add(self, name: str, type: str, tags: List[str],
            description: str = "", attributes: Dict = None) -> Subject:
        """
        创建新主体

        Args:
            name: 主体名称
            type: 主体类型
            tags: 标签列表
            description: 描述
            attributes: 类型特定属性

        Returns:
            创建的主体
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = Subject(
            id=str(uuid.uuid4()),
            name=name,
            type=type,
            tags=tags,
            description=description,
            attributes=attributes or {},
            created_at=now,
            updated_at=now,
            usage_count=0
        )
        self.subjects.append(subject)
        self._save()
        return subject

    def update(self, subject_id: str, **kwargs) -> Optional[Subject]:
        """
        更新主体信息

        Args:
            subject_id: 主体ID
            **kwargs: 要更新的字段

        Returns:
            更新后的主体，失败返回None
        """
        for s in self.subjects:
            if s.id == subject_id:
                for key, value in kwargs.items():
                    if hasattr(s, key):
                        setattr(s, key, value)
                s.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save()
                return s
        return None

    def delete(self, subject_id: str) -> bool:
        """删除主体"""
        for i, s in enumerate(self.subjects):
            if s.id == subject_id:
                del self.subjects[i]
                self._save()
                return True
        return False

    def recommend(self, theme: str, num: int = 3) -> List[Subject]:
        """
        基于主题推荐主体

        Args:
            theme: 主题关键词
            num: 推荐数量

        Returns:
            推荐的主体列表
        """
        theme_tags = theme.split()

        # 计算每个主体的匹配分数
        scored = []
        for s in self.subjects:
            score = len(set(theme_tags) & set(s.tags))
            if score > 0:
                scored.append((s, score))

        # 按分数降序，返回前num个
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _ in scored[:num]]

    def increment_usage(self, subject_id: str) -> bool:
        """增加使用计数"""
        for s in self.subjects:
            if s.id == subject_id:
                s.usage_count += 1
                self._save()
                return True
        return False

    def stats(self) -> Dict:
        """获取统计信息"""
        total = len(self.subjects)
        by_type = {}
        by_tag = {}

        for s in self.subjects:
            # 按类型统计
            by_type[s.type] = by_type.get(s.type, 0) + 1

            # 按标签统计
            for tag in s.tags:
                by_tag[tag] = by_tag.get(tag, 0) + 1

        # 使用次数前10
        top_used = sorted(self.subjects,
                          key=lambda x: x.usage_count,
                          reverse=True)[:10]

        return {
            "total": total,
            "by_type": by_type,
            "by_tag": by_tag,
            "top_used": [
                {"id": s.id, "name": s.name, "type": s.type,
                 "usage_count": s.usage_count}
                for s in top_used
            ]
        }

    def export_json(self, filepath: Path = None) -> str:
        """导出为JSON"""
        path = filepath or DATA_DIR / "subjects_export.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in self.subjects],
                      f, ensure_ascii=False, indent=2)
        return str(path)

    def import_json(self, filepath: Path) -> int:
        """从JSON导入"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for item in data:
            # 检查是否已存在
            existing = any(s.id == item.get("id") for s in self.subjects)
            if not existing:
                self.subjects.append(Subject.from_dict(item))
                count += 1
        if count > 0:
            self._save()
        return count


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="RedBox Subject Library - 主体库管理引擎")
    parser.add_argument("command", choices=[
        "list", "get", "add", "update", "delete",
        "recommend", "stats", "init", "export", "import"
    ], help="命令")
    parser.add_argument("--id", help="主体ID")
    parser.add_argument("--name", help="主体名称")
    parser.add_argument("--type", choices=["character", "product", "scene"],
                        help="主体类型")
    parser.add_argument("--tags", help="标签列表，逗号分隔")
    parser.add_argument("--description", help="主体描述")
    parser.add_argument("--attributes", help="类型特定属性(JSON)")
    parser.add_argument("--limit", type=int, default=10, help="返回数量")
    parser.add_argument("--theme", help="推荐主题")
    parser.add_argument("--file", help="导入/导出文件路径")

    args = parser.parse_args()
    library = SubjectLibrary()

    if args.command == "init":
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not SUBJECTS_FILE.exists():
            # 创建示例主体
            sample_subjects = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "职场博主",
                    "type": "character",
                    "tags": ["职场", "成长", "分享"],
                    "description": "分享职场经验和成长心得的博主",
                    "attributes": {
                        "personality": ["积极", "务实"],
                        "viewpoint": "职场成长需要持续学习和主动争取机会",
                        "speaking_style": "真诚分享，干货满满"
                    },
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "usage_count": 0
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "00后",
                    "type": "character",
                    "tags": ["年轻", "反差", "职场"],
                    "description": "新生代职场人，代表年轻视角",
                    "attributes": {
                        "personality": ["开放", "敢言"],
                        "viewpoint": "拒绝职场PUA，追求工作生活平衡",
                        "speaking_style": "直接幽默，有态度"
                    },
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "usage_count": 0
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "程序员",
                    "type": "character",
                    "tags": ["技术", "逻辑", "解决问题"],
                    "description": "技术从业者视角",
                    "attributes": {
                        "personality": ["理性", "好奇"],
                        "viewpoint": "用技术思维解决一切问题",
                        "speaking_style": "逻辑清晰，喜欢用数据和案例说话"
                    },
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "usage_count": 0
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "精致生活",
                    "type": "scene",
                    "tags": ["生活", "品质", "仪式感"],
                    "description": "追求生活品质的场景",
                    "attributes": {
                        "environment": "温馨舒适，布置有格调",
                        "atmosphere": "轻松愉悦，注重细节",
                        "suitable_topics": ["生活方式", "好物推荐", "家居"]
                    },
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "usage_count": 0
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "办公室",
                    "type": "scene",
                    "tags": ["工作", "日常", "职场"],
                    "description": "日常办公场景",
                    "attributes": {
                        "environment": "格子间或开放式办公区",
                        "atmosphere": "忙碌但有节奏感",
                        "suitable_topics": ["职场", "效率", "同事关系"]
                    },
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "usage_count": 0
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "AI助手",
                    "type": "product",
                    "tags": ["科技", "效率", "智能"],
                    "description": "AI工具和产品",
                    "attributes": {
                        "features": ["自动化", "智能推荐", "24小时服务"],
                        "target_users": ["职场人", "创作者", "学生"],
                        "price_range": "免费到订阅制",
                        "competitors": ["ChatGPT", "Claude", "Gemini"]
                    },
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "usage_count": 0
                }
            ]
            with open(SUBJECTS_FILE, "w", encoding="utf-8") as f:
                json.dump(sample_subjects, f, ensure_ascii=False, indent=2)
            print("✅ 初始化完成")
            print(f"   数据目录: {DATA_DIR}")
            print(f"   主体文件: {SUBJECTS_FILE}")
        else:
            print("✅ 主体库已存在，无需初始化")

    elif args.command == "list":
        type_filter = args.type
        tags_filter = args.tags.split(",") if args.tags else None
        subjects = library.query(type=type_filter, tags=tags_filter,
                                  limit=args.limit)
        print(f"\n📚 主体库 (共 {len(subjects)} 个)")
        print("=" * 60)
        for s in subjects:
            tags_str = ", ".join(s.tags)
            print(f"\n  [{s.id[:8]}] {s.name} ({s.type})")
            print(f"      标签: {tags_str}")
            print(f"      使用: {s.usage_count}次")

    elif args.command == "get":
        if not args.id:
            print("❌ 需要提供 --id")
            return
        subject = library.get(args.id)
        if subject:
            print(f"\n📝 主体详情: {subject.name}")
            print("=" * 60)
            print(f"  ID: {subject.id}")
            print(f"  类型: {subject.type}")
            print(f"  标签: {', '.join(subject.tags)}")
            print(f"  描述: {subject.description}")
            print(f"  属性: {json.dumps(subject.attributes, ensure_ascii=False, indent=2)}")
            print(f"  使用次数: {subject.usage_count}")
            print(f"  创建: {subject.created_at}")
            print(f"  更新: {subject.updated_at}")
        else:
            print(f"❌ 未找到主体: {args.id}")

    elif args.command == "add":
        if not args.name or not args.type:
            print("❌ 需要提供 --name 和 --type")
            return
        tags = args.tags.split(",") if args.tags else []
        attrs = json.loads(args.attributes) if args.attributes else {}
        subject = library.add(args.name, args.type, tags,
                              args.description or "", attrs)
        print(f"✅ 创建主体成功: {subject.name}")
        print(f"   ID: {subject.id}")

    elif args.command == "update":
        if not args.id:
            print("❌ 需要提供 --id")
            return
        kwargs = {}
        if args.name:
            kwargs["name"] = args.name
        if args.tags:
            kwargs["tags"] = args.tags.split(",")
        if args.description:
            kwargs["description"] = args.description
        if args.attributes:
            kwargs["attributes"] = json.loads(args.attributes)
        subject = library.update(args.id, **kwargs)
        if subject:
            print(f"✅ 更新主体成功: {subject.name}")
        else:
            print(f"❌ 未找到主体: {args.id}")

    elif args.command == "delete":
        if not args.id:
            print("❌ 需要提供 --id")
            return
        if library.delete(args.id):
            print("✅ 删除主体成功")
        else:
            print(f"❌ 未找到主体: {args.id}")

    elif args.command == "recommend":
        if not args.theme:
            print("❌ 需要提供 --theme")
            return
        subjects = library.recommend(args.theme, args.limit)
        print(f"\n🎯 基于「{args.theme}」推荐主体:")
        print("=" * 60)
        for i, s in enumerate(subjects, 1):
            tags_str = ", ".join(s.tags)
            print(f"\n  [{i}] {s.name} ({s.type})")
            print(f"      标签: {tags_str}")
            print(f"      描述: {s.description[:50]}...")

    elif args.command == "stats":
        stats = library.stats()
        print("\n📊 主体库统计:")
        print("=" * 60)
        print(f"  总主体数: {stats['total']}")
        print(f"\n  按类型分布:")
        for t, count in stats["by_type"].items():
            print(f"    - {t}: {count}")
        print(f"\n  热门标签:")
        top_tags = sorted(stats["by_tag"].items(),
                          key=lambda x: x[1], reverse=True)[:5]
        for tag, count in top_tags:
            print(f"    - {tag}: {count}")
        print(f"\n  使用次数TOP10:")
        for s in stats["top_used"]:
            print(f"    - {s['name']}: {s['usage_count']}次")

    elif args.command == "export":
        path = library.export_json(Path(args.file) if args.file else None)
        print(f"✅ 导出成功: {path}")

    elif args.command == "import":
        if not args.file:
            print("❌ 需要提供 --file")
            return
        count = library.import_json(Path(args.file))
        print(f"✅ 导入成功: 新增 {count} 个主体")


if __name__ == "__main__":
    main()
