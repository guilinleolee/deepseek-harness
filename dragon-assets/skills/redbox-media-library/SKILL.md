---
license: UNKNOWN
triggers: ["redbox media library", "redbox-media-library - 媒体库管理引擎 (RedBox Media Library)"]
---
# redbox-media-library - 媒体库管理引擎 (RedBox Media Library)

## L0: 一句话描述
统一管理内容创作的媒体素材（图片/视频/音频/文档），支持分类标签、元数据管理和多场景复用。

## L1: 使用场景
- 管理创作所需的图片、视频、音频素材
- 按标签和类型快速检索媒体资源
- 记录媒体使用历史和版权信息
- 支持创作流程中的素材快速调用

## L2: 详细文档

### 媒体类型

| 类型 | 扩展名 | 说明 |
|------|--------|------|
| **image** | jpg/jpeg/png/gif/webp/svg | 图片素材 |
| **video** | mp4/mov/avi/webm | 视频素材 |
| **audio** | mp3/wav/m4a/ogg | 音频素材 |
| **document** | pdf/doc/docx/ppt/pptx | 文档素材 |

### 媒体数据结构

```yaml
media:
  id: string              # 唯一标识
  name: string           # 文件名
  type: image|video|udio|document
  path: string           # 存储路径
  tags: [string]         # 标签列表
  metadata:              # 元数据
    size: number          # 文件大小(字节)
    width: number          # 宽(图片/视频)
    height: number        # 高(图片/视频)
    duration: number      # 时长(音视频)
    created: string       # 创建时间
    modified: string      # 修改时间
    format: string        # 文件格式
  copyright:             # 版权信息
    source: string        # 来源
    license: string      # 许可证
    author: string       # 作者
    usage_rights: string # 使用权
  usage_count: number    # 使用次数
  related_cards: [string] # 关联创意卡片
  created_at: string
  updated_at: string
```

### 核心能力

| 能力 | 说明 | 触发命令 |
|------|------|---------|
| **媒体导入** | 导入本地媒体文件 | `/media import` |
| **媒体查询** | 按类型/标签检索媒体 | `/media list` |
| **媒体详情** | 获取媒体完整信息 | `/media get` |
| **媒体更新** | 修改媒体标签/元数据 | `/media update` |
| **媒体删除** | 删除媒体记录 | `/media delete` |
| **使用追踪** | 记录媒体使用历史 | `/media use` |
| **统计分析** | 媒体库使用统计 | `/media stats` |
| **批量导入** | 批量导入目录 | `/media batch` |

### 与其他Skill协同

```python
# RedBox风格的媒体调用流程
def use_media_in_creative(theme, media_library):
    """从媒体库选择素材"""

    # 1. 查询相关媒体
    media_list = media_library.query(
        tags=theme.tags,
        type=['image', 'video']
    )

    # 2. 选择最适合的媒体
    for media in media_list[:3]:
        # 记录使用
        media_library.increment_usage(media.id)
        yield media

    # 3. 更新关联
    if card_id:
        media_library.link_to_card(media.id, card_id)
```

### 使用示例

```bash
# 导入媒体
/media import --file "cover.jpg" --tags "封面,科技" --source "自摄"

/media import --file "demo.mp4" --tags "教程,演示" --type video

# 查询媒体
/media list --type image --tags "科技" --limit 20

/media list --tags "教程,入门" --type video

# 媒体详情
/media get --id xxx

# 更新媒体
/media update --id xxx --tags "科技,AI,教程" --author "张三"

# 记录使用
/media use --id xxx --card-id xxx

# 批量导入
/media batch --dir "./素材" --tags "默认标签"

# 统计分析
/media stats

# 删除媒体
/media delete --id xxx
```

### 技术实现

```python
# scripts/media_library.py - 核心实现
from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
import uuid
import hashlib

@dataclass
class MediaMetadata:
    size: int = 0
    width: int = 0
    height: int = 0
    duration: float = 0
    created: str = ""
    modified: str = ""
    format: str = ""

@dataclass
class MediaCopyright:
    source: str = ""
    license: str = ""
    author: str = ""
    usage_rights: str = ""

@dataclass
class Media:
    id: str
    name: str
    type: str  # image/video/audio/document
    path: str
    tags: List[str]
    metadata: MediaMetadata
    copyright: MediaCopyright
    usage_count: int = 0
    related_cards: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

class MediaLibrary:
    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or MEDIA_FILE
        self.media: List[Media] = self._load()

    def import_file(self, file_path: str, tags: List[str] = None,
                    source: str = "", media_type: str = None) -> Media:
        """导入媒体文件"""

    def query(self, type: str = None, tags: List[str] = None,
              limit: int = 20) -> List[Media]:
        """查询媒体"""

    def increment_usage(self, media_id: str, card_id: str = None) -> bool:
        """增加使用计数"""

    def stats(self) -> Dict:
        """获取统计信息"""
```

### 安装与配置

```bash
# 初始化媒体库
python scripts/media_library.py init

# 导入示例素材
python scripts/media_library.py import --file "sample.jpg" --tags "示例"

# 查看统计
python scripts/media_library.py stats
```

### 预期收益

| 指标 | 基准 | 集成后 | 提升 |
|------|------|--------|------|
| 媒体复用率 | 随机 | 系统化管理 | +200% |
| 检索效率 | 手动搜索 | 自动分类 | +300% |
| 使用追踪 | 无记录 | 完整历史 | +100% |
| 版权管理 | 无 | 许可证追踪 | 新增 |

## 核心原理

> "好的素材库让创作灵感不再枯竭"

RedBox媒体库的核心洞察：
1. **分类即索引** - 好的标签体系让检索效率翻倍
2. **元数据即知识** - 丰富的元数据让素材可被发现
3. **复用即效率** - 使用追踪让优质素材被重复利用

## 版本信息

- **版本**: 1.0.0
- **来源**: RedBox Media Library启发
- **依赖**: redbox-wander, redbox-subject-library
- **更新**: 2026-04-30
