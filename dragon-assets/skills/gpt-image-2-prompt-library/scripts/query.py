#!/usr/bin/env python3
"""
GPT-Image-2 Prompt Library Query Script
数据来源: EvoLinkAI/awesome-gpt-image-2-prompts
"""

import json
import os
import random
import argparse
from pathlib import Path

# 默认数据路径
DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "gpt_image2_prompts.json")


class PromptLibrary:
    """GPT-Image-2提示词库"""

    def __init__(self, data_path: str = None):
        self.data_path = data_path or DEFAULT_DATA_PATH
        self._load_data()

    def _load_data(self):
        """加载提示词数据"""
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            # 如果本地数据不存在，使用内置的示例数据
            self.data = self._get_builtin_data()

    def _get_builtin_data(self):
        """内置示例数据（从awesome-gpt-image-2-prompts精选）"""
        return {
            "prompts": [
                # Portrait Categories
                {
                    "id": "p001",
                    "category": "portrait",
                    "style": "korean",
                    "prompt": "Korean idol aesthetic portrait, clean retouched skin, bright eye highlights, soft gradient pastel background, ethereal lighting from above, pastel wardrobe styling, dreamy atmosphere, editorial quality, 8K resolution",
                    "engagement": {"likes": 2847, "retweets": 892, "views": 45600},
                    "author": "@BubbleBrain",
                    "image_url": "https://x.com/BubbleBrain/status/example"
                },
                {
                    "id": "p002",
                    "category": "portrait",
                    "style": "fujifilm",
                    "prompt": "Fujifilm Provia 100F simulation portrait, vibrant yet pastel colors, soft contrast, natural skin tones, cinematic framing, golden hour lighting, film grain texture, editorial fashion photography",
                    "engagement": {"likes": 3156, "retweets": 1203, "views": 67800},
                    "author": "@FilmGrain",
                    "image_url": "https://x.com/FilmGrain/status/example"
                },
                {
                    "id": "p003",
                    "category": "portrait",
                    "style": "ccd",
                    "prompt": "CCD sensor aesthetic portrait, organic colors, slight color bleeding, nostalgic mood, analog warmth, rich blacks, purple and green color casts, early 2000s digital camera look, intimate framing",
                    "engagement": {"likes": 2456, "retweets": 934, "views": 52300},
                    "author": "@AnalogDreams",
                    "image_url": "https://x.com/AnalogDreams/status/example"
                },
                {
                    "id": "p004",
                    "category": "portrait",
                    "style": "35mm",
                    "prompt": "35mm film portrait, Kodak Portra 400, natural grain, warm color temperature, soft highlights, muted shadows, documentary style, intimate close-up, authentic emotion, analog aesthetic",
                    "engagement": {"likes": 1987, "retweets": 567, "views": 38900},
                    "author": "@FilmNeverDies",
                    "image_url": "https://x.com/FilmNeverDies/status/example"
                },
                {
                    "id": "p005",
                    "category": "portrait",
                    "style": "neon",
                    "prompt": "Neon-lit convenience store portrait, late night atmosphere, rain reflections on wet pavement, warm interior glow from fluorescent lights, cinematic portrait, shallow depth of field, moody lighting, urban夜色",
                    "engagement": {"likes": 3421, "retweets": 1456, "views": 89000},
                    "author": "@NeonDreams",
                    "image_url": "https://x.com/NeonDreams/status/example"
                },
                {
                    "id": "p006",
                    "category": "portrait",
                    "style": "japanese_onsen",
                    "prompt": "Japanese onsen ryokan portrait, traditional Japanese inn interior, steam rising, wooden bathhouse architecture, soft natural light through shoji screens, warm amber tones, serene contemplative mood, zen aesthetic",
                    "engagement": {"likes": 2890, "retweets": 1023, "views": 61200},
                    "author": "@JapanVisions",
                    "image_url": "https://x.com/JapanVisions/status/example"
                },

                # Poster Categories
                {
                    "id": "poster001",
                    "category": "poster",
                    "style": "vintage_newspaper",
                    "prompt": "Vintage newspaper design, aged yellow paper texture, letterpress typography, black and white with selective color, classic editorial layout, 1920s aesthetic, historical news aesthetic",
                    "engagement": {"likes": 1987, "retweets": 567, "views": 42300},
                    "author": "@RetroDesign",
                    "image_url": "https://x.com/RetroDesign/status/example"
                },
                {
                    "id": "poster002",
                    "category": "poster",
                    "style": "cyberpunk",
                    "prompt": "Cyberpunk movie poster, neon cityscape background, rain-soaked streets, glowing holographic advertisements, futuristic typography, dramatic lighting, cinematic composition, blade runner aesthetic",
                    "engagement": {"likes": 4123, "retweets": 1876, "views": 98000},
                    "author": "@CyberPunkArt",
                    "image_url": "https://x.com/CyberPunkArt/status/example"
                },
                {
                    "id": "poster003",
                    "category": "poster",
                    "style": "japanese_poster",
                    "prompt": "Japanese movie poster style, dramatic composition, ink wash painting elements, bold typography, cinematic lighting, samurai or geisha subject, traditional meets modern aesthetic, Takeshi Kitano style",
                    "engagement": {"likes": 2345, "retweets": 876, "views": 56700},
                    "author": "@JPPosterArt",
                    "image_url": "https://x.com/JPPosterArt/status/example"
                },

                # Character Design
                {
                    "id": "char001",
                    "category": "character",
                    "style": "anime_snapshot",
                    "prompt": "Anime screenshot style, cel shading, vibrant colors, detailed character design, expressive eyes, flowing hair with physics, dynamic pose, studio quality, frame from anime production",
                    "engagement": {"likes": 5678, "retweets": 2345, "views": 134000},
                    "author": "@AnimeMaster",
                    "image_url": "https://x.com/AnimeMaster/status/example"
                },
                {
                    "id": "char002",
                    "category": "character",
                    "style": "persona5",
                    "prompt": "Persona 5 UI aesthetic, bold typography, dynamic composition, character portrait in stylized frame, vibrant gradients, justice and rebellion theme, shadow forms in background, video game aesthetic",
                    "engagement": {"likes": 4567, "retweets": 1987, "views": 112000},
                    "author": "@P5Style",
                    "image_url": "https://x.com/P5Style/status/example"
                },
                {
                    "id": "char003",
                    "category": "character",
                    "style": "gal_game",
                    "prompt": "Visual novel character design, anime art style, sprite illustration, character introduction card, route selection UI elements, soft pastel colors, romantic atmosphere, dating sim aesthetic",
                    "engagement": {"likes": 3456, "retweets": 1234, "views": 89000},
                    "author": "@GalGameArt",
                    "image_url": "https://x.com/GalGameArt/status/example"
                },

                # UI Mockup
                {
                    "id": "ui001",
                    "category": "ui",
                    "style": "keynote_snapshot",
                    "prompt": "Keynote presentation slide screenshot, modern design, clean typography, gradient background, corporate presentation aesthetic, blur background, slide deck style, Apple keynote quality",
                    "engagement": {"likes": 1567, "retweets": 456, "views": 34500},
                    "author": "@DesignMockups",
                    "image_url": "https://x.com/DesignMockups/status/example"
                },
                {
                    "id": "ui002",
                    "category": "ui",
                    "style": "iphone_screenshot",
                    "prompt": "iPhone 15 Pro screenshot, iOS 17 interface, rounded corners, dynamic island, app interface mockup, glass morphism design, modern iOS aesthetic, realistic device frame",
                    "engagement": {"likes": 2345, "retweets": 678, "views": 56700},
                    "author": "@UIMockupPro",
                    "image_url": "https://x.com/UIMockupPro/status/example"
                },
                {
                    "id": "ui003",
                    "category": "ui",
                    "style": "handwritten_notebook",
                    "prompt": "Handwritten notebook photo, fountain pen on cream paper, ink bleeding effect, grid lines visible, personal notes, coffee stain decoration, authentic handwriting, study aesthetic",
                    "engagement": {"likes": 2890, "retweets": 890, "views": 67800},
                    "author": "@StudyVibes",
                    "image_url": "https://x.com/StudyVibes/status/example"
                },
                {
                    "id": "ui004",
                    "category": "ui",
                    "style": "chinese_social_media",
                    "prompt": "Chinese social media feed, Chinese characters, traditional ink painting border, water color wash aesthetic, 小红书style, modern meets classical, calligraphy elements, elegant design",
                    "engagement": {"likes": 3456, "retweets": 1234, "views": 89000},
                    "author": "@CNDesign",
                    "image_url": "https://x.com/CNDesign/status/example"
                },

                # Social Media
                {
                    "id": "social001",
                    "category": "social",
                    "style": "x_twitter_post",
                    "prompt": "Twitter/X post design, modern social media graphic, bold typography, gradient background, viral content aesthetic, engagement metrics display, platform mockup",
                    "engagement": {"likes": 1234, "retweets": 345, "views": 28900},
                    "author": "@SocialDesign",
                    "image_url": "https://x.com/SocialDesign/status/example"
                },
                {
                    "id": "social002",
                    "category": "social",
                    "style": "instagram_post",
                    "prompt": "Instagram square post, aesthetic lifestyle photo, warm lighting, minimalist composition, branded content style, influencer aesthetic, engagement focused design",
                    "engagement": {"likes": 2678, "retweets": 567, "views": 45600},
                    "author": "@InstaAesthetic",
                    "image_url": "https://x.com/InstaAesthetic/status/example"
                }
            ]
        }

    def search(self, category: str = None, style: str = None,
                sort: str = "engagement", limit: int = 10) -> list:
        """
        搜索提示词

        Args:
            category: 分类 (portrait/poster/character/ui/social)
            style: 风格 (korean/fujifilm/ccd/35mm/neon等)
            sort: 排序方式 (engagement/time/random)
            limit: 返回数量
        """
        results = self.data.get("prompts", [])

        # 按分类过滤
        if category:
            results = [p for p in results if p.get("category") == category]

        # 按风格过滤
        if style:
            results = [p for p in results if style.lower() in p.get("style", "").lower()]

        # 排序
        if sort == "engagement":
            results.sort(key=lambda x: sum(x.get("engagement", {}).values()), reverse=True)
        elif sort == "random":
            random.shuffle(results)

        return results[:limit]

    def recommend(self, use_case: str) -> list:
        """
        根据用例推荐提示词

        Args:
            use_case: 用例 (social_media_cover/portrait_design/poster_design等)
        """
        use_case_map = {
            "social_media_cover": {"category": "social", "styles": ["instagram_post", "chinese_social_media"]},
            "portrait_design": {"category": "portrait", "styles": ["korean", "fujifilm", "35mm"]},
            "poster_design": {"category": "poster", "styles": ["vintage_newspaper", "cyberpunk", "japanese_poster"]},
            "character_design": {"category": "character", "styles": ["anime_snapshot", "persona5"]},
            "ui_design": {"category": "ui", "styles": ["iphone_screenshot", "keynote_snapshot"]}
        }

        config = use_case_map.get(use_case, use_case_map["social_media_cover"])
        results = []

        for style in config["styles"]:
            results.extend(self.search(category=config["category"], style=style, limit=3))

        return results[:5]


def main():
    parser = argparse.ArgumentParser(description="GPT-Image-2 Prompt Library Query")
    parser.add_argument("--category", choices=["portrait", "poster", "character", "ui", "social"])
    parser.add_argument("--style", help="风格关键词")
    parser.add_argument("--sort", choices=["engagement", "random", "time"], default="engagement")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--random", action="store_true")
    parser.add_argument("--export", choices=["json", "markdown"])
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--recommend", help="用例推荐 (social_media_cover/portrait_design/...)")

    args = parser.parse_args()

    lib = PromptLibrary()

    if args.recommend:
        results = lib.recommend(args.recommend)
        sort = "random"
    elif args.random:
        results = lib.search(category=args.category, sort="random", limit=args.limit)
        sort = "random"
    else:
        results = lib.search(category=args.category, style=args.style,
                             sort=args.sort, limit=args.limit)
        sort = args.sort

    # 输出格式
    if args.export == "json":
        output = json.dumps(results, ensure_ascii=False, indent=2)
    elif args.export == "markdown":
        lines = ["# GPT-Image-2 提示词库\n"]
        for i, p in enumerate(results, 1):
            lines.append(f"## {i}. [{p['style']}] {p['category']}")
            lines.append(f"**Author**: {p['author']}")
            lines.append(f"**互动**: ❤️{p['engagement']['likes']} 🔄{p['engagement']['retweets']} 👁️{p['engagement']['views']}")
            lines.append(f"\n```\n{p['prompt']}\n```\n")
        output = "\n".join(lines)
    else:
        lines = [f"📚 GPT-Image-2 提示词库 (排序: {sort}, 显示: {len(results)})\n"]
        for i, p in enumerate(results, 1):
            eng = p["engagement"]
            lines.append(f"\n{i}. [{p['style']}] {p['category']}")
            lines.append(f"   {p['prompt'][:80]}...")
            lines.append(f"   📊 ❤️{eng['likes']} 🔄{eng['retweets']} | @{p['author'].lstrip('@')}")
        output = "\n".join(lines)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"✅ 已导出到 {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()