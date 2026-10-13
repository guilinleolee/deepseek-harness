#!/usr/bin/env python3
"""
UI/Social Media Mockup Prompt Query Script
UI界面+社媒配图提示词库查询
"""

import json
import os
import random
import argparse

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ui_social_prompts.json")


class UISocialPromptLibrary:
    """UI界面+社媒配图提示词库"""

    def __init__(self, data_path: str = None):
        self.data_path = data_path or DEFAULT_DATA_PATH
        self._load_data()

    def _load_data(self):
        """加载提示词数据"""
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = self._get_builtin_data()

    def _get_builtin_data(self):
        """内置示例数据"""
        return {
            "prompts": [
                # UI Mockup Categories
                {
                    "id": "ui001",
                    "category": "ui",
                    "style": "keynote",
                    "prompt": "Apple keynote snapshot style app UI mockup, modern design, blur background, floating UI elements, clean typography, San Francisco font, subtle shadows, product presentation aesthetic, white and gray color scheme, 16:9 aspect ratio",
                    "engagement": {"likes": 2345, "retweets": 876, "views": 56700},
                    "author": "@DesignMockups"
                },
                {
                    "id": "ui002",
                    "category": "ui",
                    "style": "keynote",
                    "prompt": "iPhone 15 Pro keynote presentation mockup, Dynamic Island, iOS 17 glass morphism, floating notification cards, App Store screenshot style, Apple product photography lighting, minimalist UI, soft gradient backgrounds, realistic device bezels",
                    "engagement": {"likes": 3456, "retweets": 1234, "views": 78900},
                    "author": "@AppleUI"
                },
                {
                    "id": "ui003",
                    "category": "ui",
                    "style": "iphone",
                    "prompt": "iOS app screenshot mockup, iPhone 15 Pro Max display, realistic shadow and reflections, App Store hero image style, dynamic island visible, iPhone 15 titanium frame, Mediterranean blue background, sleek product presentation",
                    "engagement": {"likes": 4123, "retweets": 1567, "views": 92300},
                    "author": "@iOSDesign"
                },
                {
                    "id": "ui004",
                    "category": "ui",
                    "style": "iphone",
                    "prompt": "iOS 17 control center mockup, Dynamic Island expanded view, glass morphism panels, Live Activities, iPhone 15 Pro titanium device frame, dark mode interface, notification bubbles, widget stack, realistic screen curvature",
                    "engagement": {"likes": 2890, "retweets": 987, "views": 45600},
                    "author": "@AppleMockups"
                },
                {
                    "id": "ui005",
                    "category": "ui",
                    "style": "handwritten",
                    "prompt": "Handwritten notebook UI wireframe, fountain pen style, cream colored paper texture, ink bleeding effect, architectural sketch aesthetic, cross-hatching shadows, sepia tones, hand-drawn UI components, wireframe annotations in pencil",
                    "engagement": {"likes": 1876, "retweets": 654, "views": 34500},
                    "author": "@SketchUX"
                },
                {
                    "id": "ui006",
                    "category": "ui",
                    "style": "handwritten",
                    "prompt": "Sketch-style app wireframe on paper, fountain pen ink, Leuchtturm1917 notebook, dot grid paper texture, hand-drawn rectangles representing UI elements, annotations with pencil, coffee ring stain, warm lighting",
                    "engagement": {"likes": 1567, "retweets": 543, "views": 28900},
                    "author": "@WireframeArt"
                },
                {
                    "id": "ui007",
                    "category": "ui",
                    "style": "android",
                    "prompt": "Android 14 Material You app screenshot, Pixel 8 Pro display, dynamic color theming, rounded corners, pill-shaped buttons, bottom sheet navigation, Google Sans typography, playful yet minimal interface, vibrant wallpaper-based colors",
                    "engagement": {"likes": 2134, "retweets": 765, "views": 41200},
                    "author": "@AndroidUI"
                },
                {
                    "id": "ui008",
                    "category": "ui",
                    "style": "android",
                    "prompt": "Android Material Design 3 mockup, Pixel Launcher home screen, At a Glance widget, dynamic color extraction from wallpaper, notification badges, app icon grid, gesture navigation hints, modern Google hardware aesthetic",
                    "engagement": {"likes": 1987, "retweets": 698, "views": 38700},
                    "author": "@MaterialYou"
                },

                # Chinese Social Media Categories
                {
                    "id": "xhs001",
                    "category": "chinese_social",
                    "style": "xhs",
                    "prompt": "小红书封面风格配图, 文艺小清新设计, 莫兰迪色调, 手写字体点缀, 绿植/咖啡杯/书本元素, 温暖自然光, 9:16竖版构图, 文艺博主风格, 留白设计, 质感生活氛围",
                    "engagement": {"likes": 8765, "retweets": 2345, "views": 156000},
                    "author": "@小红书设计"
                },
                {
                    "id": "xhs002",
                    "category": "chinese_social",
                    "style": "xhs",
                    "prompt": "小红书穿搭分享配图, 韩系风格, 奶油色背景, 人物穿搭展示, 精致配饰, 柔和打光, 时尚杂志排版, 9:16竖版构图, ins风滤镜质感, 高级感配色",
                    "engagement": {"likes": 7654, "retweets": 1987, "views": 134000},
                    "author": "@时尚穿搭"
                },
                {
                    "id": "xhs003",
                    "category": "chinese_social",
                    "style": "xhs",
                    "prompt": "小红书探店打卡配图, 国潮风格, 故宫红/金色元素, 传统建筑纹样, 书法字体, 新中式设计, 9:16竖版构图, 中国风滤镜, 高级感传统美学",
                    "engagement": {"likes": 6543, "retweets": 1678, "views": 112000},
                    "author": "@国潮美学"
                },
                {
                    "id": "xhs004",
                    "category": "chinese_social",
                    "style": "xhs",
                    "prompt": "小红书美食摄影配图, 日系治愈风格, 暖色调, 木质桌面背景, 食物特写, 散落的水果/面包, 自然光入镜, 9:16竖版构图, 生活方式博主风格",
                    "engagement": {"likes": 9876, "retweets": 2567, "views": 178000},
                    "author": "@美食摄影"
                },
                {
                    "id": "weibo001",
                    "category": "chinese_social",
                    "style": "weibo",
                    "prompt": "微博配图, 中国风海报设计, 水墨画元素, 传统祥云纹, 书法字体标题, 黑白红色调, 现代与传统结合, 16:9横版构图, 品牌传播视觉, 高端质感",
                    "engagement": {"likes": 4321, "retweets": 1234, "views": 89000},
                    "author": "@东方设计"
                },
                {
                    "id": "weibo002",
                    "category": "chinese_social",
                    "style": "weibo",
                    "prompt": "微博热搜配图, 抖音风格大字报设计, 渐变背景, 粗体中文字体, emoji装饰, 话题标签样式, 年轻化视觉, 社交媒体爆款风格, 高饱和度配色",
                    "engagement": {"likes": 5678, "retweets": 1678, "views": 123000},
                    "author": "@社交媒体"
                },
                {
                    "id": "wechat001",
                    "category": "chinese_social",
                    "style": "wechat",
                    "prompt": "微信公众号封面配图, 简约杂志风设计, 大标题+副标题排版, 莫兰迪色调, 留白美学, 文艺气质, 9:16竖版构图, 知识干货风格, 高端感配色",
                    "engagement": {"likes": 3456, "retweets": 987, "views": 67000},
                    "author": "@公众号设计"
                },

                # Western Social Media Categories
                {
                    "id": "instagram001",
                    "category": "western_social",
                    "style": "instagram",
                    "prompt": "Instagram aesthetic lifestyle post, warm golden hour lighting, minimalist composition, terracotta and sage color palette, linen textures, Mediterranean vibes, lifestyle flat lay, coffee and book, soft shadows, editorial quality photography",
                    "engagement": {"likes": 12340, "retweets": 3456, "views": 234000},
                    "author": "@AestheticFeed"
                },
                {
                    "id": "instagram002",
                    "category": "western_social",
                    "style": "instagram",
                    "prompt": "Instagram flat lay composition, modern interior design, neutral tones, marble and wood textures, luxury lifestyle aesthetic, carefully curated objects, natural lighting from window, soft morning light, clean minimal background",
                    "engagement": {"likes": 15670, "retweets": 4123, "views": 289000},
                    "author": "@InteriorGoals"
                },
                {
                    "id": "instagram003",
                    "category": "western_social",
                    "style": "instagram",
                    "prompt": "Instagram skincare flat lay, K-beauty aesthetic, pastel pink and white color scheme, glass bottles, minimalist branding, soft diffused lighting, clean marble surface, beauty editorial style, luxury skincare vibes",
                    "engagement": {"likes": 11230, "retweets": 2987, "views": 201000},
                    "author": "@SkincareAddict"
                },
                {
                    "id": "twitter001",
                    "category": "western_social",
                    "style": "twitter",
                    "prompt": "Twitter/X bold typography post, gradient background purple to blue, large bold text, modern tech aesthetic, startup vibes, dark mode friendly, social media viral style, bold statement design",
                    "engagement": {"likes": 8765, "retweets": 4567, "views": 178000},
                    "author": "@TechDesign"
                },
                {
                    "id": "twitter002",
                    "category": "western_social",
                    "style": "twitter",
                    "prompt": "Twitter/X thread cover image, dark theme design, neon accent colors, tech infographic style, data visualization elements, coding aesthetic, terminal window elements, developer community vibes, dark background with glowing highlights",
                    "engagement": {"likes": 7654, "retweets": 3876, "views": 145000},
                    "author": "@DevCommunity"
                },
                {
                    "id": "youtube001",
                    "category": "western_social",
                    "style": "youtube",
                    "prompt": "YouTube thumbnail design, bold face with text overlay, bright saturated colors, high contrast, attention-grabbing design, gaming/tech aesthetic, emoji elements, cinematic quality, 16:9 aspect ratio, viral thumbnail style",
                    "engagement": {"likes": 15670, "retweets": 5234, "views": 312000},
                    "author": "@ThumbnailKing"
                },
                {
                    "id": "youtube002",
                    "category": "western_social",
                    "style": "youtube",
                    "prompt": "YouTube channel art, minimalist design, gradient background blue to purple, subtle geometric patterns, clean typography, professional aesthetic, brand colors, 2560x1440 cinematic banner style",
                    "engagement": {"likes": 9876, "retweets": 3124, "views": 189000},
                    "author": "@ChannelArt"
                },
                {
                    "id": "tiktok001",
                    "category": "western_social",
                    "style": "tiktok",
                    "prompt": "TikTok video thumbnail, bold text with shadow, bright neon colors, Gen Z aesthetic, dynamic composition, trendy design elements, holographic effects, viral social media style, 9:16 vertical format",
                    "engagement": {"likes": 18760, "retweets": 6789, "views": 345000},
                    "author": "@GenZDesign"
                },
                {
                    "id": "linkedin001",
                    "category": "western_social",
                    "style": "linkedin",
                    "prompt": "LinkedIn professional post design, clean corporate aesthetic, blue and white color scheme, professional typography, subtle gradient background, business networking style, modern corporate design, trustworthy and authoritative",
                    "engagement": {"likes": 5432, "retweets": 1876, "views": 98000},
                    "author": "@BizDesign"
                }
            ]
        }

    def search(self, category: str = None, style: str = None,
               sort: str = "engagement", limit: int = 10) -> list:
        """
        搜索UI/社媒提示词

        Args:
            category: 分类 (ui/chinese_social/western_social)
            style: 风格 (keynote/iphone/handwritten/xhs/instagram/twitter等)
            sort: 排序方式 (engagement/random)
            limit: 返回数量
        """
        results = self.data.get("prompts", [])

        if category:
            results = [p for p in results if p.get("category") == category]

        if style:
            results = [p for p in results if style.lower() in p.get("style", "").lower()]

        if sort == "engagement":
            results.sort(key=lambda x: sum(x.get("engagement", {}).values()), reverse=True)
        elif sort == "random":
            random.shuffle(results)

        return results[:limit]

    def recommend(self, use_case: str) -> list:
        """
        根据用例推荐提示词

        Args:
            use_case: 用例 (product_screenshot/app_preview/social_media/brand_content等)
        """
        use_case_map = {
            "product_screenshot": {"category": "ui", "styles": ["keynote", "iphone"]},
            "app_preview": {"category": "ui", "styles": ["iphone", "android"]},
            "social_media": {"category": "western_social", "styles": ["instagram", "twitter"]},
            "chinese_social": {"category": "chinese_social", "styles": ["xhs", "weibo"]},
            "brand_content": {"category": "western_social", "styles": ["instagram", "youtube"]},
            "lifestyle": {"category": "chinese_social", "styles": ["xhs"]},
        }

        config = use_case_map.get(use_case, use_case_map["product_screenshot"])
        results = []

        for style in config["styles"]:
            results.extend(self.search(category=config["category"], style=style, limit=3))

        return results[:5]


def main():
    parser = argparse.ArgumentParser(description="UI/Social Media Mockup Prompts Query")
    parser.add_argument("--category", choices=["ui", "chinese_social", "western_social"],
                        help="分类 (ui/chinese_social/western_social)")
    parser.add_argument("--style", help="风格关键词 (keynote/iphone/xhs/instagram等)")
    parser.add_argument("--sort", choices=["engagement", "random"], default="engagement")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--random", action="store_true")
    parser.add_argument("--export", choices=["json", "markdown"])
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--recommend", help="用例推荐")

    args = parser.parse_args()

    lib = UISocialPromptLibrary()

    if args.recommend:
        results = lib.recommend(args.recommend)
        sort = "random"
    elif args.random:
        results = lib.search(category=args.category, style=args.style, sort="random", limit=args.limit)
        sort = "random"
    else:
        results = lib.search(category=args.category, style=args.style,
                             sort=args.sort, limit=args.limit)
        sort = args.sort

    if args.export == "json":
        output = json.dumps(results, ensure_ascii=False, indent=2)
    elif args.export == "markdown":
        lines = ["# UI/Social Media Mockup Prompts\n"]
        for i, p in enumerate(results, 1):
            lines.append(f"## {i}. [{p['style']}] {p['category']}")
            lines.append(f"**Author**: {p['author']}")
            lines.append(f"**互动**: ❤️{p['engagement']['likes']} 🔄{p['engagement']['retweets']} 👁️{p['engagement']['views']}")
            lines.append(f"\n```\n{p['prompt']}\n```\n")
        output = "\n".join(lines)
    else:
        lines = [f"UI/Social Media Mockup Prompts (Sort: {sort}, Showing: {len(results)})\n"]
        for i, p in enumerate(results, 1):
            eng = p["engagement"]
            lines.append(f"\n{i}. [{p['style']}] {p['category']}")
            lines.append(f"   {p['prompt'][:80]}...")
            lines.append(f"   📊 ❤️{eng['likes']} 🔄{eng['retweets']} | @{p['author'].lstrip('@')}")
        output = "\n".join(lines)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Exported to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
