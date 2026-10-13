"""
文章数据模型
化学视角：Article是系统的分子，包含所有原子属性
"""

import json
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path


@dataclass
class Article:
    """微信公众号文章数据模型

    设计原则：
    - 不可变性：创建后不修改（除了内部状态）
    - 完整性：包含所有必要信息
    - 可序列化：支持JSON导出
    - 类型安全：使用类型注解
    """

    # 标识（不可变）
    url: str                              # 原文URL
    url_hash: str                         # URL的SHA256哈希（用于缓存键）

    # 元数据
    title: str                            # 标题
    author: str                           # 作者
    account_name: str                     # 公众号名称
    publish_time: Optional[datetime] = None  # 发布时间

    # 内容
    content_html: str = ""                # HTML格式内容
    content_markdown: str = ""            # Markdown格式内容
    content_text: str = ""                # 纯文本内容

    # 媒体
    images: List[str] = field(default_factory=list)  # 图片URL列表
    cover_image: Optional[str] = None     # 封面图URL

    # 元信息
    fetch_time: datetime = field(default_factory=datetime.now)  # 获取时间
    source: str = "unknown"               # 来源: 'cache'/'direct'/'api'
    word_count: int = 0                   # 字数

    def __post_init__(self):
        """初始化后处理"""
        # 如果没有提供url_hash，自动生成
        if not self.url_hash:
            self.url_hash = self._hash_url(self.url)

        # 计算字数
        if not self.word_count and self.content_text:
            self.word_count = len(self.content_text)

    @staticmethod
    def _hash_url(url: str) -> str:
        """计算URL的SHA256哈希

        Args:
            url: 文章URL

        Returns:
            SHA256哈希值（十六进制）
        """
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """序列化为字典

        Returns:
            包含所有字段的可序列化字典
        """
        data = asdict(self)

        # 处理datetime字段
        if self.publish_time:
            data['publish_time'] = self.publish_time.isoformat()
        if self.fetch_time:
            data['fetch_time'] = self.fetch_time.isoformat()

        return data

    def to_json(self, indent: int = 2, ensure_ascii: bool = False) -> str:
        """序列化为JSON字符串

        Args:
            indent: 缩进空格数
            ensure_ascii: 是否确保ASCII编码

        Returns:
            JSON字符串
        """
        return json.dumps(
            self.to_dict(),
            indent=indent,
            ensure_ascii=ensure_ascii
        )

    def save_json(self, path: str) -> None:
        """保存为JSON文件

        Args:
            path: 文件路径（.json）
        """
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(path_obj, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    def save_markdown(self, path: str) -> None:
        """保存为Markdown文件

        Args:
            path: 文件路径（.md）
        """
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(path_obj, 'w', encoding='utf-8') as f:
            # 写入元数据
            f.write(f"# {self.title}\n\n")
            f.write(f"**作者**: {self.author}  \n")
            f.write(f"**公众号**: {self.account_name}  \n")
            if self.publish_time:
                f.write(f"**发布时间**: {self.publish_time.strftime('%Y-%m-%d %H:%M')}  \n")
            f.write(f"**原文链接**: {self.url}  \n\n")
            f.write("---\n\n")

            # 写入正文
            f.write(self.content_markdown)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Article':
        """从字典反序列化

        Args:
            data: 包含文章数据的字典

        Returns:
            Article对象
        """
        # 处理datetime字段
        if 'publish_time' in data and isinstance(data['publish_time'], str):
            data['publish_time'] = datetime.fromisoformat(data['publish_time'])
        if 'fetch_time' in data and isinstance(data['fetch_time'], str):
            data['fetch_time'] = datetime.fromisoformat(data['fetch_time'])

        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'Article':
        """从JSON字符串反序列化

        Args:
            json_str: JSON字符串

        Returns:
            Article对象
        """
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_json_file(cls, path: str) -> 'Article':
        """从JSON文件加载

        Args:
            path: JSON文件路径

        Returns:
            Article对象
        """
        with open(path, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())

    def is_expired(self, ttl_days: int = 30) -> bool:
        """检查文章是否过期

        Args:
            ttl_days: 生存时间（天）

        Returns:
            True if expired, False otherwise
        """
        from datetime import timedelta
        expiry = self.fetch_time + timedelta(days=ttl_days)
        return datetime.now() > expiry

    def get_summary(self, max_length: int = 200) -> str:
        """获取文章摘要

        Args:
            max_length: 最大长度

        Returns:
            摘要文本
        """
        text = self.content_text.strip()
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

    def __repr__(self) -> str:
        """字符串表示"""
        return f"Article(title='{self.title}', author='{self.author}', words={self.word_count})"


# 类型别名
ArticleList = List[Article]
OptionalArticle = Optional[Article]
