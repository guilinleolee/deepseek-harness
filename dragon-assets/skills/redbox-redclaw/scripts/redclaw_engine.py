#!/usr/bin/env python3
"""
RedBox RedClaw Creative Engine - 创作自动化引擎
基于RedBox启发，自动化内容创作全流程——从创意捕捉到多平台分发的创作加速引擎。

核心能力:
1. 创意捕捉 - 快速记录灵感，自动打标签
2. 内容生成 - 基于模板生成多平台内容
3. 多平台分发 - 一键分发到多个平台
4. 版本管理 - 内容版本迭代管理
5. 效果追踪 - 创作数据分析
"""

import json
import uuid
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Set
from datetime import datetime
from pathlib import Path

# 配置路径
CONFIG_DIR = Path.home() / ".claude" / "skills" / "redbox-redclaw"
DATA_DIR = CONFIG_DIR / "data"
CARDS_FILE = DATA_DIR / "creative_cards.json"
STATS_FILE = DATA_DIR / "stats.json"
INSPIRATION_LOG = DATA_DIR / "inspiration_log.md"


@dataclass
class Subject:
    """创作素材关联"""
    name: str
    type: str  # character/product/scene
    tags: List[str] = field(default_factory=list)


@dataclass
class Version:
    """内容版本"""
    version: str
    content: str
    platform: str
    created_at: str
    tags: List[str] = field(default_factory=list)
    note: str = ""


@dataclass
class CreativeCard:
    """创意卡片数据结构"""
    id: str
    seed: str  # 原始灵感
    theme: str
    tags: List[str]
    keywords: List[str]
    source: str  # manual/wander/manuscript/import
    materials: Dict[str, List[Subject]]  # characters/products/scenes
    status: str  # draft/processing/published/archived
    created_at: str
    updated_at: str
    versions: List[Version] = field(default_factory=list)
    platform_contents: Dict[str, str] = field(default_factory=dict)  # platform -> content

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'CreativeCard':
        # 反序列化时转换 Subject 对象
        if 'materials' in data:
            for key in data['materials']:
                data['materials'][key] = [
                    Subject(**s) if isinstance(s, dict) else s
                    for s in data['materials'][key]
                ]
        if 'versions' in data:
            data['versions'] = [
                Version(**v) if isinstance(v, dict) else v
                for v in data['versions']
            ]
        return cls(**data)


@dataclass
class PlatformContent:
    """平台适配内容"""
    platform: str
    title: str
    content: str
    tags: List[str]
    word_count: int
    format_notes: str


@dataclass
class PublishResult:
    """发布结果"""
    platform: str
    card_id: str
    success: bool
    url: str = ""
    error: str = ""
    published_at: str = ""


class RedClawEngine:
    """RedClaw创作自动化引擎"""

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or CARDS_FILE
        self.cards: List[CreativeCard] = self._load()

    def _load(self) -> List[CreativeCard]:
        """加载创意卡片数据"""
        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [CreativeCard.from_dict(c) for c in data]
        return []

    def _save(self):
        """保存创意卡片数据"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump([c.to_dict() for c in self.cards], f,
                      ensure_ascii=False, indent=2)

    # ==================== 创意捕捉 ====================

    def capture(self, seed: str, theme: str = "", tags: List[str] = None,
                keywords: List[str] = None, source: str = "manual",
                materials: Dict[str, List[Subject]] = None) -> CreativeCard:
        """
        捕捉创意

        Args:
            seed: 原始灵感/种子
            theme: 主题
            tags: 标签列表
            keywords: 关键词列表
            source: 来源 (manual/wander/manuscript/import)
            materials: 素材配置

        Returns:
            创建的创意卡片
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 解析主题
        if not theme:
            theme = seed[:50] if len(seed) > 50 else seed

        # 自动标签
        if tags is None:
            tags = self._extract_tags(seed)
        if keywords is None:
            keywords = self._extract_keywords(seed)

        card = CreativeCard(
            id=str(uuid.uuid4()),
            seed=seed,
            theme=theme,
            tags=tags,
            keywords=keywords,
            source=source,
            materials=materials or {"characters": [], "products": [], "scenes": []},
            status="draft",
            created_at=now,
            updated_at=now,
            versions=[],
            platform_contents={}
        )

        self.cards.append(card)
        self._save()

        # 记录到灵感日志
        self._log_inspiration(card)

        return card

    def _extract_tags(self, text: str) -> List[str]:
        """从文本提取标签"""
        # 简单关键词提取
        common_tags = [
            "AI", "科技", "创业", "职场", "成长", "生活",
            "学习", "投资", "营销", "产品", "设计", "运营"
        ]
        found = [tag for tag in common_tags if tag in text]
        return found[:5] if found else ["未分类"]

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本提取关键词"""
        # 简单分词（实际应用中可用jieba等）
        words = text.replace(",", " ").replace("，", " ").replace("。", " ").split()
        return list(set(words))[:10]

    def _log_inspiration(self, card: CreativeCard):
        """记录灵感到日志"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(INSPIRATION_LOG, "a", encoding="utf-8") as f:
            f.write(f"\n## 灵感卡片 {card.created_at}\n")
            f.write(f"- **ID**: {card.id}\n")
            f.write(f"- **种子**: {card.seed}\n")
            f.write(f"- **主题**: {card.theme}\n")
            f.write(f"- **标签**: {', '.join(card.tags)}\n")
            f.write(f"- **来源**: {card.source}\n")

    # ==================== 内容生成 ====================

    def generate(self, card_id: str, platform: str,
                 template: str = None) -> PlatformContent:
        """
        生成平台适配内容

        Args:
            card_id: 创意卡片ID
            platform: 目标平台 (xiaohongshu/wechat/weibo/bilibili/zhihu)
            template: 可选模板名称

        Returns:
            平台适配内容
        """
        card = self.get(card_id)
        if not card:
            raise ValueError(f"未找到创意卡片: {card_id}")

        # 获取平台模板
        plat_template = self._get_platform_template(platform, template)

        # 生成标题
        title = self._generate_title(card, platform)

        # 生成正文
        content = self._generate_body(card, platform, plat_template)

        # 生成标签
        tags = self._generate_tags(card, platform)

        # 记录版本
        version = Version(
            version=f"v{len(card.versions) + 1}",
            content=content,
            platform=platform,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            tags=tags
        )
        card.versions.append(version)
        card.platform_contents[platform] = content
        card.status = "processing"
        card.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save()

        return PlatformContent(
            platform=platform,
            title=title,
            content=content,
            tags=tags,
            word_count=len(content),
            format_notes=plat_template.get("format_notes", "")
        )

    def _get_platform_template(self, platform: str, template: str = None) -> Dict:
        """获取平台模板配置"""
        templates = {
            "xiaohongshu": {
                "title_format": "悬念/数字/痛点型",
                "body_format": "开头Hook + 干货 + 结尾CTA",
                "max_length": 1000,
                "requires_tags": True,
                "requires_images": True,
                "format_notes": "Emoji点缀，话题标签#XX#，正文分段"
            },
            "wechat": {
                "title_format": "深度/故事型",
                "body_format": "引言 + 核心观点 + 案例 + 总结",
                "max_length": 0,  # 无限制
                "requires_cover": True,
                "requires_meta": True,
                "format_notes": "引用块、正文分段、图文并茂"
            },
            "weibo": {
                "title_format": "热点/争议型",
                "body_format": "观点 + 补充",
                "max_length": 2000,
                "supports_thread": True,
                "supports_poll": True,
                "format_notes": "@提及、#话题#、短句子"
            },
            "bilibili": {
                "title_format": "好奇/揭秘型",
                "body_format": "悬念开场 + 干货内容 + 互动引导",
                "max_length": 500,
                "requires_cover": True,
                "format_notes": "分P标注，时效性提示"
            },
            "zhihu": {
                "title_format": "专业/深度型",
                "body_format": "问题 + 分析 + 结论 + 建议",
                "max_length": 0,
                "requires_meta": True,
                "format_notes": "专业排版，引用数据，小标题"
            }
        }
        return templates.get(platform, templates["xiaohongshu"])

    def _generate_title(self, card: CreativeCard, platform: str) -> str:
        """生成平台适配标题"""
        title_patterns = {
            "xiaohongshu": [
                f"救命！{card.theme}竟然这么简单",
                f"关于{card.theme}，我想说...",
                f"{card.theme}的真相（建议收藏）",
                f"答应我，一定要看{card.theme}这篇",
            ],
            "wechat": [
                f"深度解析：{card.theme}",
                f"关于{card.theme}的思考",
                f"{card.theme}：我的观察与判断",
            ],
            "weibo": [
                f"聊聊{card.theme}",
                f"关于{card.theme}的几点看法",
                f"突然想说说{card.theme}",
            ],
            "bilibili": [
                f"【必看】{card.theme}完全指南",
                f"关于{card.theme}，你可能不知道的",
                f"{card.theme}入门到精通",
            ],
            "zhihu": [
                f"如何看待{card.theme}？",
                f"深度分析：{card.theme}",
                f"{card.theme}的底层逻辑是什么？",
            ]
        }
        import random
        patterns = title_patterns.get(platform, title_patterns["xiaohongshu"])
        return random.choice(patterns)

    def _generate_body(self, card: CreativeCard, platform: str,
                       template: Dict) -> str:
        """生成平台适配正文"""
        # 根据平台格式生成正文
        body_templates = {
            "xiaohongshu": """💡 {hook}

{intro}

{content}

{cta}

{hashtags}""",
            "wechat": """{intro}

{content}

{conclusion}""",
            "weibo": """{content}

#话题#{hashtags}""",
            "bilibili": """{hook}

{content}

有收获的话记得一键三连~""",
            "zhihu": """## 问题背景
{intro}

## 深度分析
{content}

## 结论
{conclusion}"""
        }

        template_str = body_templates.get(platform, body_templates["xiaohongshu"])

        import random

        # 生成各部分内容
        hooks = [
            f"最近被问最多的就是{card.theme}",
            f"我发现了一个关于{card.theme}的秘密",
            f"关于{card.theme}，90%的人都搞错了",
        ]
        intros = [
            f"今天想和大家聊聊{card.theme}这个话题",
            f"在研究{card.theme}的过程中，我发现了一些有趣的现象",
        ]
        contents = [
            f"核心观点：{card.seed}\n\n",
            f"首先，我们需要理解{card.theme}的本质。\n\n",
            f"结合我的实践经验，{card.theme}的关键在于...\n\n",
        ]
        ctas = [
            "觉得有用的点个赞~",
            "有任何问题评论区见",
            "收藏起来慢慢看",
        ]
        conclusions = [
            f"总结：{card.theme}的核心是{card.seed[:50]}",
            f"以上是我关于{card.theme}的一些思考",
        ]
        hashtags = " ".join([f"#{t}#" for t in card.tags[:5]])

        body = template_str.format(
            hook=random.choice(hooks),
            intro=random.choice(intros),
            content=random.choice(contents) + card.seed,
            cta=random.choice(ctas),
            conclusion=random.choice(conclusions),
            hashtags=hashtags
        )

        # 截断到平台限制
        max_len = template.get("max_length", 0)
        if max_len > 0 and len(body) > max_len:
            body = body[:max_len - 20] + "..."

        return body

    def _generate_tags(self, card: CreativeCard, platform: str) -> List[str]:
        """生成平台标签"""
        base_tags = card.tags.copy()
        platform_suffixes = {
            "xiaohongshu": ["种草", "干货", "分享"],
            "wechat": ["原创", "深度", "推荐"],
            "weibo": ["分享", "感悟", "思考"],
            "bilibili": ["教程", "科普", "必看"],
            "zhihu": ["专栏", "原创", "深度"]
        }
        return base_tags + platform_suffixes.get(platform, [])[:2]

    # ==================== 多平台分发 ====================

    def publish(self, card_id: str, platforms: List[str]) -> List[PublishResult]:
        """
        多平台分发

        Args:
            card_id: 创意卡片ID
            platforms: 目标平台列表

        Returns:
            发布结果列表
        """
        card = self.get(card_id)
        if not card:
            raise ValueError(f"未找到创意卡片: {card_id}")

        results = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for platform in platforms:
            # 确保有内容
            if platform not in card.platform_contents:
                # 先生成内容
                try:
                    self.generate(card_id, platform)
                except Exception as e:
                    results.append(PublishResult(
                        platform=platform,
                        card_id=card_id,
                        success=False,
                        error=str(e),
                        published_at=now
                    ))
                    continue

            # 模拟发布（实际实现需接入各平台API）
            result = self._post_to_platform(card, platform)
            results.append(result)

            if result.success:
                card.status = "published"

        card.updated_at = now
        self._save()
        return results

    def _post_to_platform(self, card: CreativeCard,
                          platform: str) -> PublishResult:
        """
        发布到指定平台（模拟实现）

        实际应用中需要接入各平台API：
        - 小红书: xiaohongshu-mcp
        - 公众号: baoyu-post-to-wechat
        - 微博: baoyu-post-to-weibo
        - B站: bilibili-cli
        - 知乎: zhihu-api
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 模拟发布成功
        # 实际场景中这里会调用平台API
        return PublishResult(
            platform=platform,
            card_id=card.id,
            success=True,
            url=f"https://{platform}.com/post/{card.id[:8]}",
            published_at=now
        )

    # ==================== 版本管理 ====================

    def list_versions(self, card_id: str) -> List[Version]:
        """列出所有版本"""
        card = self.get(card_id)
        if not card:
            return []
        return card.versions

    def get_version(self, card_id: str, version: str) -> Optional[Version]:
        """获取指定版本"""
        card = self.get(card_id)
        if not card:
            return None
        for v in card.versions:
            if v.version == version:
                return v
        return None

    def diff_versions(self, card_id: str, v1: str, v2: str) -> Dict:
        """对比两个版本的差异"""
        version1 = self.get_version(card_id, v1)
        version2 = self.get_version(card_id, v2)

        if not version1 or not version2:
            return {"error": "版本不存在"}

        # 简单差异计算
        lines1 = version1.content.split("\n")
        lines2 = version2.content.split("\n")

        added = len(lines2) - len(lines1)
        common = sum(1 for a, b in zip(lines1, lines2) if a == b)

        return {
            "v1": v1,
            "v2": v2,
            "v1_words": len(version1.content),
            "v2_words": len(version2.content),
            "lines_added": added,
            "common_lines": common,
            "v1_platform": version1.platform,
            "v2_platform": version2.platform
        }

    # ==================== 效果追踪 ====================

    def analytics(self, period: str = "30d") -> Dict:
        """
        创作数据分析

        Args:
            period: 时间范围 (7d/30d/90d/all)

        Returns:
            统计数据
        """
        # 按状态统计
        by_status = {}
        by_platform = {}
        by_source = {}
        total_tags = {}

        for card in self.cards:
            # 状态统计
            by_status[card.status] = by_status.get(card.status, 0) + 1

            # 平台统计
            for platform in card.platform_contents.keys():
                by_platform[platform] = by_platform.get(platform, 0) + 1

            # 来源统计
            by_source[card.source] = by_source.get(card.source, 0) + 1

            # 标签统计
            for tag in card.tags:
                total_tags[tag] = total_tags.get(tag, 0) + 1

        # 热门标签TOP10
        top_tags = sorted(total_tags.items(),
                           key=lambda x: x[1], reverse=True)[:10]

        # 活跃卡片（最近更新）
        active_cards = sorted(
            self.cards,
            key=lambda c: c.updated_at,
            reverse=True
        )[:10]

        return {
            "total_cards": len(self.cards),
            "by_status": by_status,
            "by_platform": by_platform,
            "by_source": by_source,
            "top_tags": [{"tag": t, "count": c} for t, c in top_tags],
            "active_cards": [
                {
                    "id": c.id[:8],
                    "theme": c.theme,
                    "status": c.status,
                    "updated": c.updated_at
                }
                for c in active_cards
            ]
        }

    # ==================== 基础CRUD ====================

    def get(self, card_id: str) -> Optional[CreativeCard]:
        """获取创意卡片"""
        for card in self.cards:
            if card.id == card_id:
                return card
        return None

    def list(self, status: str = None, limit: int = 20) -> List[CreativeCard]:
        """列出创意卡片"""
        cards = self.cards
        if status:
            cards = [c for c in cards if c.status == status]
        return sorted(cards, key=lambda c: c.updated_at, reverse=True)[:limit]

    def update(self, card_id: str, **kwargs) -> Optional[CreativeCard]:
        """更新创意卡片"""
        for card in self.cards:
            if card.id == card_id:
                for key, value in kwargs.items():
                    if hasattr(card, key):
                        setattr(card, key, value)
                card.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save()
                return card
        return None

    def delete(self, card_id: str) -> bool:
        """删除创意卡片"""
        for i, card in enumerate(self.cards):
            if card.id == card_id:
                del self.cards[i]
                self._save()
                return True
        return False

    def update_content(self, card_id: str, platform: str,
                       content: str) -> Optional[CreativeCard]:
        """更新平台内容"""
        card = self.get(card_id)
        if not card:
            return None

        # 记录版本
        version = Version(
            version=f"v{len(card.versions) + 1}",
            content=content,
            platform=platform,
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            tags=card.tags.copy()
        )
        card.versions.append(version)
        card.platform_contents[platform] = content
        card.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save()
        return card

    def archive(self, card_id: str) -> Optional[CreativeCard]:
        """归档创意卡片"""
        return self.update(card_id, status="archived")

    # ==================== 导入导出 ====================

    def export_json(self, card_id: str, filepath: Path = None) -> str:
        """导出卡片为JSON"""
        card = self.get(card_id)
        if not card:
            raise ValueError(f"未找到创意卡片: {card_id}")

        path = filepath or DATA_DIR / f"card_{card_id[:8]}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(card.to_dict(), f, ensure_ascii=False, indent=2)
        return str(path)

    def import_json(self, filepath: Path) -> Optional[CreativeCard]:
        """从JSON导入卡片"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 检查是否已存在
        for card in self.cards:
            if card.id == data.get("id"):
                return None

        card = CreativeCard.from_dict(data)
        self.cards.append(card)
        self._save()
        return card

    def init(self) -> None:
        """初始化数据目录"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # 创建灵感日志
        if not INSPIRATION_LOG.exists():
            with open(INSPIRATION_LOG, "w", encoding="utf-8") as f:
                f.write("# 灵感库\n\n记录所有创作灵感\n")


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="RedBox RedClaw Creative Engine - 创作自动化引擎")
    parser.add_argument("command", choices=[
        "init", "capture", "generate", "publish",
        "list", "get", "versions", "diff",
        "analytics", "export", "delete", "archive"
    ], help="命令")
    parser.add_argument("--card-id", help="创意卡片ID")
    parser.add_argument("--seed", help="原始灵感")
    parser.add_argument("--theme", help="主题")
    parser.add_argument("--tags", help="标签列表，逗号分隔")
    parser.add_argument("--keywords", help="关键词列表，逗号分隔")
    parser.add_argument("--source", default="manual",
                        choices=["manual", "wander", "manuscript", "import"],
                        help="来源")
    parser.add_argument("--platform", help="目标平台")
    parser.add_argument("--platforms", help="平台列表，逗号分隔")
    parser.add_argument("--limit", type=int, default=20, help="返回数量")
    parser.add_argument("--period", default="30d", help="统计周期")
    parser.add_argument("--file", help="文件路径")
    parser.add_argument("--v1", help="版本1")
    parser.add_argument("--v2", help="版本2")

    args = parser.parse_args()
    engine = RedClawEngine()

    if args.command == "init":
        engine.init()
        print("✅ 初始化完成")
        print(f"   数据目录: {DATA_DIR}")
        print(f"   卡片文件: {CARDS_FILE}")
        print(f"   灵感日志: {INSPIRATION_LOG}")

    elif args.command == "capture":
        if not args.seed:
            print("❌ 需要提供 --seed")
            return
        tags = args.tags.split(",") if args.tags else None
        keywords = args.keywords.split(",") if args.keywords else None
        card = engine.capture(
            seed=args.seed,
            theme=args.theme or "",
            tags=tags,
            keywords=keywords,
            source=args.source
        )
        print(f"✅ 创意捕捉成功: {card.id}")
        print(f"   种子: {card.seed}")
        print(f"   主题: {card.theme}")
        print(f"   标签: {', '.join(card.tags)}")

    elif args.command == "generate":
        if not args.card_id or not args.platform:
            print("❌ 需要提供 --card-id 和 --platform")
            return
        content = engine.generate(args.card_id, args.platform)
        print(f"\n📝 生成内容: {args.platform}")
        print("=" * 60)
        print(f"\n【标题】{content.title}")
        print(f"\n【正文】\n{content.content}")
        print(f"\n【标签】{', '.join(content.tags)}")
        print(f"\n【字数】{content.word_count}")

    elif args.command == "publish":
        if not args.card_id:
            print("❌ 需要提供 --card-id")
            return
        platforms = args.platforms.split(",") if args.platforms else ["xiaohongshu"]
        results = engine.publish(args.card_id, platforms)
        print(f"\n📤 发布结果:")
        print("=" * 60)
        for r in results:
            status = "✅" if r.success else "❌"
            print(f"  {status} {r.platform}: {r.url or r.error}")

    elif args.command == "list":
        cards = engine.list(limit=args.limit)
        print(f"\n📚 创意卡片 (共 {len(cards)} 个)")
        print("=" * 60)
        for c in cards:
            print(f"\n  [{c.id[:8]}] {c.theme}")
            print(f"      状态: {c.status} | 来源: {c.source}")
            print(f"      标签: {', '.join(c.tags[:3])}")
            print(f"      更新: {c.updated_at}")

    elif args.command == "get":
        if not args.card_id:
            print("❌ 需要提供 --card-id")
            return
        card = engine.get(args.card_id)
        if card:
            print(f"\n📝 创意卡片详情: {card.theme}")
            print("=" * 60)
            print(f"  ID: {card.id}")
            print(f"  种子: {card.seed}")
            print(f"  主题: {card.theme}")
            print(f"  标签: {', '.join(card.tags)}")
            print(f"  关键词: {', '.join(card.keywords)}")
            print(f"  来源: {card.source}")
            print(f"  状态: {card.status}")
            print(f"  版本数: {len(card.versions)}")
            print(f"  平台内容: {', '.join(card.platform_contents.keys())}")
            print(f"  创建: {card.created_at}")
            print(f"  更新: {card.updated_at}")
        else:
            print(f"❌ 未找到卡片: {args.card_id}")

    elif args.command == "versions":
        if not args.card_id:
            print("❌ 需要提供 --card-id")
            return
        versions = engine.list_versions(args.card_id)
        print(f"\n📜 版本历史 (共 {len(versions)} 个)")
        print("=" * 60)
        for v in versions:
            print(f"\n  [{v.version}] {v.platform}")
            print(f"      {v.created_at}")
            print(f"      字数: {len(v.content)}")

    elif args.command == "diff":
        if not args.card_id or not args.v1 or not args.v2:
            print("❌ 需要提供 --card-id, --v1, --v2")
            return
        diff = engine.diff_versions(args.card_id, args.v1, args.v2)
        print(f"\n📊 版本对比: {args.v1} vs {args.v2}")
        print("=" * 60)
        for k, v in diff.items():
            print(f"  {k}: {v}")

    elif args.command == "analytics":
        stats = engine.analytics(args.period)
        print(f"\n📊 创作数据统计 (最近 {args.period})")
        print("=" * 60)
        print(f"  总卡片数: {stats['total_cards']}")
        print(f"\n  按状态:")
        for status, count in stats['by_status'].items():
            print(f"    - {status}: {count}")
        print(f"\n  按平台:")
        for platform, count in stats['by_platform'].items():
            print(f"    - {platform}: {count}")
        print(f"\n  TOP标签:")
        for t in stats['top_tags'][:5]:
            print(f"    - #{t['tag']}: {t['count']}")

    elif args.command == "export":
        if not args.card_id:
            print("❌ 需要提供 --card-id")
            return
        path = engine.export_json(args.card_id, Path(args.file) if args.file else None)
        print(f"✅ 导出成功: {path}")

    elif args.command == "delete":
        if not args.card_id:
            print("❌ 需要提供 --card-id")
            return
        if engine.delete(args.card_id):
            print("✅ 删除成功")
        else:
            print(f"❌ 未找到卡片: {args.card_id}")

    elif args.command == "archive":
        if not args.card_id:
            print("❌ 需要提供 --card-id")
            return
        card = engine.archive(args.card_id)
        if card:
            print(f"✅ 归档成功: {card.theme}")
        else:
            print(f"❌ 未找到卡片: {args.card_id}")


if __name__ == "__main__":
    main()
