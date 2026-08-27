#!/usr/bin/env python3
"""
RedBox Media Library - 媒体库管理引擎
统一管理内容创作的媒体素材（图片/视频/音频/文档），支持分类标签、元数据管理和多场景复用。

核心能力:
1. 媒体导入 - 导入本地媒体文件
2. 媒体查询 - 按类型/标签检索媒体
3. 媒体详情 - 获取媒体完整信息
4. 媒体更新 - 修改媒体标签/元数据
5. 媒体删除 - 删除媒体记录
6. 使用追踪 - 记录媒体使用历史
7. 统计分析 - 媒体库使用统计
8. 批量导入 - 批量导入目录
"""

import json
import uuid
import os
import hashlib
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from enum import Enum

# 配置路径
CONFIG_DIR = Path.home() / ".claude" / "skills" / "redbox-media-library"
DATA_DIR = CONFIG_DIR / "data"
MEDIA_FILE = DATA_DIR / "media.json"
STATS_FILE = DATA_DIR / "stats.json"

# 支持的媒体类型
MEDIA_TYPES = ["image", "video", "audio", "document"]

# 扩展名映射
EXTENSION_MAP = {
    "image": ["jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "ico"],
    "video": ["mp4", "mov", "avi", "webm", "mkv", "flv", "wmv"],
    "audio": ["mp3", "wav", "m4a", "ogg", "flac", "aac", "wma"],
    "document": ["pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx", "txt", "md"]
}


class MediaType(Enum):
    """媒体类型枚举"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


def get_media_type_by_extension(filename: str) -> Optional[str]:
    """根据文件扩展名判断媒体类型"""
    ext = filename.lower().split('.')[-1]
    for media_type, extensions in EXTENSION_MAP.items():
        if ext in extensions:
            return media_type
    return None


def get_file_hash(filepath: Path) -> str:
    """计算文件MD5哈希"""
    md5 = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()
    except Exception:
        return ""


@dataclass
class MediaMetadata:
    """媒体元数据结构"""
    size: int = 0  # 文件大小(字节)
    width: int = 0  # 宽(图片/视频)
    height: int = 0  # 高(图片/视频)
    duration: float = 0  # 时长(音视频) 秒
    created: str = ""  # 创建时间
    modified: str = ""  # 修改时间
    format: str = ""  # 文件格式

    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'MediaMetadata':
        """从字典创建"""
        return cls(**data) if data else cls()


@dataclass
class MediaCopyright:
    """版权信息结构"""
    source: str = ""  # 来源
    license: str = ""  # 许可证
    author: str = ""  # 作者
    usage_rights: str = ""  # 使用权

    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'MediaCopyright':
        """从字典创建"""
        return cls(**data) if data else cls()


@dataclass
class Media:
    """媒体数据结构"""
    id: str
    name: str
    type: str  # image/video/audio/document
    path: str  # 存储路径
    tags: List[str]
    metadata: MediaMetadata
    copyright: MediaCopyright
    usage_count: int = 0
    related_cards: List[str] = field(default_factory=list)
    file_hash: str = ""  # 文件哈希，用于去重
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "path": self.path,
            "tags": self.tags,
            "metadata": self.metadata.to_dict() if isinstance(self.metadata, MediaMetadata) else self.metadata,
            "copyright": self.copyright.to_dict() if isinstance(self.copyright, MediaCopyright) else self.copyright,
            "usage_count": self.usage_count,
            "related_cards": self.related_cards,
            "file_hash": self.file_hash,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Media':
        """从字典创建"""
        metadata = MediaMetadata.from_dict(data.get("metadata", {}))
        copyright = MediaCopyright.from_dict(data.get("copyright", {}))
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            path=data["path"],
            tags=data.get("tags", []),
            metadata=metadata,
            copyright=copyright,
            usage_count=data.get("usage_count", 0),
            related_cards=data.get("related_cards", []),
            file_hash=data.get("file_hash", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", "")
        )


class MediaLibrary:
    """媒体库管理器"""

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or MEDIA_FILE
        self.media: List[Media] = self._load()

    def _load(self) -> List[Media]:
        """加载媒体数据"""
        if self.data_path.exists():
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [Media.from_dict(m) for m in data]
            except (json.JSONDecodeError, KeyError):
                return []
        return []

    def _save(self):
        """保存媒体数据"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump([m.to_dict() for m in self.media], f,
                      ensure_ascii=False, indent=2)

    def import_file(self, file_path: str, tags: List[str] = None,
                    source: str = "", media_type: str = None,
                    author: str = "", license: str = "") -> Media:
        """
        导入媒体文件

        Args:
            file_path: 文件路径
            tags: 标签列表
            source: 来源
            media_type: 媒体类型(默认自动检测)
            author: 作者
            license: 许可证

        Returns:
            创建的媒体记录
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 自动检测类型
        if not media_type:
            media_type = get_media_type_by_extension(path.name)
            if not media_type:
                raise ValueError(f"不支持的文件类型: {path.name}")

        # 计算文件哈希(用于去重)
        file_hash = get_file_hash(path)

        # 检查是否已存在
        for existing in self.media:
            if existing.file_hash == file_hash:
                print(f"⚠️  文件已存在，跳过: {path.name}")
                return existing

        # 获取文件元数据
        stat = path.stat()
        metadata = MediaMetadata(
            size=stat.st_size,
            created=datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            modified=datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            format=path.suffix[1:].lower()
        )

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        media = Media(
            id=str(uuid.uuid4()),
            name=path.name,
            type=media_type,
            path=str(path.absolute()),
            tags=tags or [],
            metadata=metadata,
            copyright=MediaCopyright(
                source=source,
                author=author,
                license=license
            ),
            usage_count=0,
            related_cards=[],
            file_hash=file_hash,
            created_at=now,
            updated_at=now
        )

        self.media.append(media)
        self._save()
        return media

    def query(self, type: str = None, tags: List[str] = None,
              limit: int = 20) -> List[Media]:
        """
        查询媒体

        Args:
            type: 媒体类型
            tags: 标签列表
            limit: 返回数量限制

        Returns:
            匹配的媒体列表，按使用次数降序
        """
        results = self.media

        # 按类型过滤
        if type:
            results = [m for m in results if m.type == type]

        # 按标签过滤
        if tags:
            results = [m for m in results
                      if any(t in m.tags for t in tags)]

        # 按使用次数降序
        return sorted(results, key=lambda x: x.usage_count,
                      reverse=True)[:limit]

    def get(self, media_id: str) -> Optional[Media]:
        """获取媒体详情"""
        for m in self.media:
            if m.id == media_id:
                return m
        return None

    def update(self, media_id: str, **kwargs) -> Optional[Media]:
        """
        更新媒体信息

        Args:
            media_id: 媒体ID
            **kwargs: 要更新的字段

        Returns:
            更新后的媒体，失败返回None
        """
        for m in self.media:
            if m.id == media_id:
                # 更新标签
                if "tags" in kwargs:
                    m.tags = kwargs["tags"]

                # 更新版权信息
                if "source" in kwargs:
                    m.copyright.source = kwargs["source"]
                if "author" in kwargs:
                    m.copyright.author = kwargs["author"]
                if "license" in kwargs:
                    m.copyright.license = kwargs["license"]
                if "usage_rights" in kwargs:
                    m.copyright.usage_rights = kwargs["usage_rights"]

                # 更新元数据
                if "width" in kwargs:
                    m.metadata.width = kwargs["width"]
                if "height" in kwargs:
                    m.metadata.height = kwargs["height"]
                if "duration" in kwargs:
                    m.metadata.duration = kwargs["duration"]

                # 更新关联卡片
                if "related_cards" in kwargs:
                    m.related_cards = kwargs["related_cards"]

                m.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save()
                return m
        return None

    def delete(self, media_id: str) -> bool:
        """删除媒体记录"""
        for i, m in enumerate(self.media):
            if m.id == media_id:
                del self.media[i]
                self._save()
                return True
        return False

    def increment_usage(self, media_id: str, card_id: str = None) -> bool:
        """
        增加使用计数

        Args:
            media_id: 媒体ID
            card_id: 关联的创意卡片ID

        Returns:
            是否成功
        """
        for m in self.media:
            if m.id == media_id:
                m.usage_count += 1
                m.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if card_id and card_id not in m.related_cards:
                    m.related_cards.append(card_id)
                self._save()
                return True
        return False

    def link_to_card(self, media_id: str, card_id: str) -> bool:
        """关联媒体到创意卡片"""
        for m in self.media:
            if m.id == media_id:
                if card_id not in m.related_cards:
                    m.related_cards.append(card_id)
                    m.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self._save()
                return True
        return False

    def stats(self) -> Dict:
        """获取统计信息"""
        total = len(self.media)
        by_type = {}
        by_tag = {}
        total_size = 0

        for m in self.media:
            # 按类型统计
            by_type[m.type] = by_type.get(m.type, 0) + 1

            # 按标签统计
            for tag in m.tags:
                by_tag[tag] = by_tag.get(tag, 0) + 1

            # 累计大小
            total_size += m.metadata.size

        # 使用次数前10
        top_used = sorted(self.media,
                          key=lambda x: x.usage_count,
                          reverse=True)[:10]

        return {
            "total": total,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "by_type": by_type,
            "by_tag": by_tag,
            "top_used": [
                {"id": m.id, "name": m.name, "type": m.type,
                 "usage_count": m.usage_count}
                for m in top_used
            ]
        }

    def batch_import(self, dir_path: str, tags: List[str] = None,
                     recursive: bool = True) -> Dict:
        """
        批量导入目录

        Args:
            dir_path: 目录路径
            tags: 默认标签列表
            recursive: 是否递归子目录

        Returns:
            导入统计
        """
        path = Path(dir_path)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"目录不存在: {dir_path}")

        imported = 0
        skipped = 0
        errors = []

        pattern = "**/*" if recursive else "*"
        for file_path in path.glob(pattern):
            if file_path.is_file():
                media_type = get_media_type_by_extension(file_path.name)
                if media_type:
                    try:
                        self.import_file(
                            str(file_path),
                            tags=tags,
                            media_type=media_type
                        )
                        imported += 1
                    except FileNotFoundError:
                        skipped += 1
                    except ValueError as e:
                        errors.append(str(e))
                    except Exception as e:
                        errors.append(f"{file_path.name}: {e}")

        return {
            "imported": imported,
            "skipped": skipped,
            "errors": errors,
            "total": imported + skipped
        }

    def export_json(self, filepath: Path = None) -> str:
        """导出为JSON"""
        path = filepath or DATA_DIR / "media_export.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump([m.to_dict() for m in self.media],
                      f, ensure_ascii=False, indent=2)
        return str(path)

    def import_json(self, filepath: Path) -> int:
        """从JSON导入"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for item in data:
            # 检查是否已存在
            existing = any(m.id == item.get("id") for m in self.media)
            if not existing:
                self.media.append(Media.from_dict(item))
                count += 1
        if count > 0:
            self._save()
        return count


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="RedBox Media Library - 媒体库管理引擎")
    parser.add_argument("command", choices=[
        "init", "import", "list", "get", "update", "delete",
        "use", "link", "batch", "stats", "export", "import-json"
    ], help="命令")
    parser.add_argument("--id", help="媒体ID")
    parser.add_argument("--file", help="文件路径")
    parser.add_argument("--path", help="目录路径")
    parser.add_argument("--type", choices=MEDIA_TYPES, help="媒体类型")
    parser.add_argument("--tags", help="标签列表，逗号分隔")
    parser.add_argument("--source", help="来源")
    parser.add_argument("--author", help="作者")
    parser.add_argument("--license", help="许可证")
    parser.add_argument("--card-id", help="创意卡片ID")
    parser.add_argument("--limit", type=int, default=20, help="返回数量")
    parser.add_argument("--recursive", action="store_true", help="递归子目录")

    args = parser.parse_args()
    library = MediaLibrary()

    if args.command == "init":
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not MEDIA_FILE.exists():
            with open(MEDIA_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
            print("✅ 初始化完成")
            print(f"   数据目录: {DATA_DIR}")
            print(f"   媒体文件: {MEDIA_FILE}")
        else:
            print("✅ 媒体库已存在，无需初始化")

    elif args.command == "import":
        if not args.file:
            print("❌ 需要提供 --file")
            return
        tags = args.tags.split(",") if args.tags else []
        try:
            media = library.import_file(
                args.file,
                tags=tags,
                source=args.source or "",
                media_type=args.type,
                author=args.author or "",
                license=args.license or ""
            )
            print(f"✅ 导入成功: {media.name}")
            print(f"   ID: {media.id}")
            print(f"   类型: {media.type}")
        except Exception as e:
            print(f"❌ 导入失败: {e}")

    elif args.command == "list":
        type_filter = args.type
        tags_filter = args.tags.split(",") if args.tags else None
        media_list = library.query(type=type_filter, tags=tags_filter,
                                    limit=args.limit)
        print(f"\n📁 媒体库 (共 {len(media_list)} 个)")
        print("=" * 60)
        for m in media_list:
            tags_str = ", ".join(m.tags) if m.tags else "无"
            size_mb = round(m.metadata.size / (1024 * 1024), 2)
            print(f"\n  [{m.id[:8]}] {m.name} ({m.type})")
            print(f"      标签: {tags_str}")
            print(f"      大小: {size_mb}MB | 使用: {m.usage_count}次")

    elif args.command == "get":
        if not args.id:
            print("❌ 需要提供 --id")
            return
        media = library.get(args.id)
        if media:
            print(f"\n📝 媒体详情: {media.name}")
            print("=" * 60)
            print(f"  ID: {media.id}")
            print(f"  类型: {media.type}")
            print(f"  路径: {media.path}")
            print(f"  标签: {', '.join(media.tags) if media.tags else '无'}")
            print(f"  大小: {round(media.metadata.size / (1024 * 1024), 2)}MB")
            print(f"  格式: {media.metadata.format}")
            if media.metadata.width and media.metadata.height:
                print(f"  分辨率: {media.metadata.width}x{media.metadata.height}")
            if media.metadata.duration:
                print(f"  时长: {media.metadata.duration}秒")
            print(f"  版权来源: {media.copyright.source or '未设置'}")
            print(f"  版权作者: {media.copyright.author or '未设置'}")
            print(f"  使用次数: {media.usage_count}")
            print(f"  关联卡片: {len(media.related_cards)}个")
            print(f"  创建: {media.created_at}")
            print(f"  更新: {media.updated_at}")
        else:
            print(f"❌ 未找到媒体: {args.id}")

    elif args.command == "update":
        if not args.id:
            print("❌ 需要提供 --id")
            return
        kwargs = {}
        if args.tags:
            kwargs["tags"] = args.tags.split(",")
        if args.source:
            kwargs["source"] = args.source
        if args.author:
            kwargs["author"] = args.author
        if args.license:
            kwargs["license"] = args.license
        if kwargs:
            result = library.update(args.id, **kwargs)
            if result:
                print(f"✅ 更新成功: {result.name}")
            else:
                print(f"❌ 未找到媒体: {args.id}")
        else:
            print("❌ 需要提供更新字段")

    elif args.command == "delete":
        if not args.id:
            print("❌ 需要提供 --id")
            return
        if library.delete(args.id):
            print("✅ 删除成功")
        else:
            print(f"❌ 未找到媒体: {args.id}")

    elif args.command == "use":
        if not args.id:
            print("❌ 需要提供 --id")
            return
        if library.increment_usage(args.id, args.card_id):
            print("✅ 使用记录已更新")
        else:
            print(f"❌ 未找到媒体: {args.id}")

    elif args.command == "link":
        if not args.id or not args.card_id:
            print("❌ 需要提供 --id 和 --card-id")
            return
        if library.link_to_card(args.id, args.card_id):
            print("✅ 关联成功")
        else:
            print(f"❌ 未找到媒体: {args.id}")

    elif args.command == "batch":
        if not args.path:
            print("❌ 需要提供 --path")
            return
        tags = args.tags.split(",") if args.tags else []
        try:
            result = library.batch_import(
                args.path,
                tags=tags,
                recursive=args.recursive
            )
            print(f"\n📊 批量导入结果:")
            print(f"   导入成功: {result['imported']}")
            print(f"   跳过: {result['skipped']}")
            if result['errors']:
                print(f"   错误: {len(result['errors'])}")
                for err in result['errors'][:5]:
                    print(f"     - {err}")
        except Exception as e:
            print(f"❌ 批量导入失败: {e}")

    elif args.command == "stats":
        stats = library.stats()
        print("\n📊 媒体库统计:")
        print("=" * 60)
        print(f"  总媒体数: {stats['total']}")
        print(f"  总大小: {stats['total_size_mb']}MB")
        print(f"\n  按类型分布:")
        for t, count in stats["by_type"].items():
            print(f"    - {t}: {count}")
        print(f"\n  热门标签:")
        top_tags = sorted(stats["by_tag"].items(),
                          key=lambda x: x[1], reverse=True)[:5]
        for tag, count in top_tags:
            print(f"    - {tag}: {count}")
        print(f"\n  使用次数TOP10:")
        for m in stats["top_used"]:
            print(f"    - {m['name']}: {m['usage_count']}次")

    elif args.command == "export":
        path = library.export_json(Path(args.file) if args.file else None)
        print(f"✅ 导出成功: {path}")

    elif args.command == "import-json":
        if not args.file:
            print("❌ 需要提供 --file")
            return
        count = library.import_json(Path(args.file))
        print(f"✅ 导入成功: 新增 {count} 个媒体")


if __name__ == "__main__":
    main()
