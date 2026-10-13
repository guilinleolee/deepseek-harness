#!/usr/bin/env python3
"""
Social Media Content Generator - 社媒内容自动生成
YouTube视频章节 → 小红书/抖音/公众号文案
"""

import sys
from pathlib import Path
from typing import Optional, TypedDict
from dataclasses import dataclass, field


class SocialContent(TypedDict):
    xiaohongshu: str
    douyin: str
    wechat: str


@dataclass
class Chapter:
    title: str
    start: str
    end: str
    summary: str
    keywords: list[str] = field(default_factory=list)


class SocialMediaGenerator:
    """
    社媒内容生成器

    根据视频章节内容，自动生成适合各平台的文案:
    - 小红书: 封面标题 + 正文 + 标签
    - 抖音: 爆款标题 + 前3秒脚本 + CTA
    - 公众号: 标题 + 引言 + 正文结构
    """

    def generate(
        self,
        chapter: Chapter,
        platforms: list[str] = None,
        api_key: Optional[str] = None
    ) -> SocialContent:
        """
        生成社媒内容

        Args:
            chapter: 视频章节信息
            platforms: 目标平台列表
            api_key: LLM API密钥

        Returns:
            各平台文案
        """
        if platforms is None:
            platforms = ["xiaohongshu", "douyin", "wechat"]

        content = {}

        for platform in platforms:
            if platform == "xiaohongshu":
                content["xiaohongshu"] = self._generate_xiaohongshu(chapter, api_key)
            elif platform == "douyin":
                content["douyin"] = self._generate_douyin(chapter, api_key)
            elif platform == "wechat":
                content["wechat"] = self._generate_wechat(chapter, api_key)

        return SocialContent(**content)

    def _generate_xiaohongshu(self, chapter: Chapter, api_key: Optional[str]) -> str:
        """生成小红书文案"""
        prompt = f"""Generate a 小红书 (Xiaohongshu) post based on this video chapter.

Chapter Title: {chapter.title}
Summary: {chapter.summary}
Keywords: {', '.join(chapter.keywords)}

Generate content in this format:
---
[Title - catchy and engaging]

[Body - conversational, personal, use emojis]

#标签1 #标签2 #标签3 #标签4 #标签5
---

Requirements:
- Title: 15-25 characters, attention-grabbing
- Body: 150-300 characters, story-style
- Use 3-5 relevant hashtags
- Include a hook in the first line"""

        if api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a 小红书 content expert."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content.strip()
            except Exception:
                pass

        # Fallback模板
        return f"""{chapter.title}

{chapter.summary}

#getchapter.keywords[0] #getchapter.keywords[1] #AI教程 #学习方法 #知识分享"""

    def _generate_douyin(self, chapter: Chapter, api_key: Optional[str]) -> str:
        """生成抖音文案"""
        prompt = f"""Generate a 抖音 (Douyin/TikTok) script based on this video chapter.

Chapter Title: {chapter.title}
Summary: {chapter.summary}
Keywords: {', '.join(chapter.keywords)}

Generate content in this format:
---
[Title - viral-style, under 30 characters]

[Hook (first 3 seconds) - 立即抓住注意力]

[Body - fast-paced, engaging script]

[CTA - 点赞/关注/评论]
---

Requirements:
- Title: Attention-grabbing, under 30 chars
- Hook: Immediate attention in first 3 seconds
- Body: 30-60 seconds script
- Include trending audio suggestions"""

        if api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a 抖音 content expert."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content.strip()
            except Exception:
                pass

        # Fallback模板
        return f"""{chapter.title}

🔥 戳开看！{chapter.summary}

内容超有料！

#getchapter.keywords[0] #getchapter.keywords[1] #抖音
@好友 #douyin"""

    def _generate_wechat(self, chapter: Chapter, api_key: Optional[str]) -> str:
        """生成公众号文案"""
        prompt = f"""Generate a 微信公众号 article based on this video chapter.

Chapter Title: {chapter.title}
Summary: {chapter.summary}
Keywords: {', '.join(chapter.keywords)}

Generate content in this format:
---
[Title - professional, click-worthy]

[Lead - hook the reader in first 50 words]

[Body - structured with ### headings]

[Conclusion with CTA]
---

Requirements:
- Title: 20-40 characters, professional tone
- Lead: Hook reader immediately
- Body: Use ### for sections
- Include relevant emojis for engagement
- End with a question to encourage comments"""

        if api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a 微信公众号 writer."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content.strip()
            except Exception:
                pass

        # Fallback模板
        return f"""# {chapter.title}

{chapter.summary}

## 核心要点

{chr(10).join([f'- {kw}' for kw in chapter.keywords[:3]])}

## 总结

今天分享的内容希望能给你带来启发！

---

你觉得这个话题怎么样？欢迎在评论区留言讨论！"""


def main():
    if len(sys.argv) < 3:
        print("Usage: python social_media_generator.py <title> <summary> [keywords] [api_key]")
        print("Example: python social_media_generator.py 'Claude Code入门' '介绍基本概念' 'AI,Claude,教程' [key]")
        sys.exit(1)

    title = sys.argv[1]
    summary = sys.argv[2]
    keywords = sys.argv[3].split(',') if len(sys.argv) > 3 else []
    api_key = sys.argv[4] if len(sys.argv) > 4 else None

    chapter = Chapter(
        title=title,
        start="00:00:00",
        end="00:05:00",
        summary=summary,
        keywords=keywords
    )

    generator = SocialMediaGenerator()
    content = generator.generate(chapter, api_key=api_key)

    print("=" * 50)
    print("小红书:")
    print("-" * 50)
    print(content["xiaohongshu"])
    print("\n" + "=" * 50)
    print("抖音:")
    print("-" * 50)
    print(content["douyin"])
    print("\n" + "=" * 50)
    print("公众号:")
    print("-" * 50)
    print(content["wechat"])


if __name__ == "__main__":
    main()
