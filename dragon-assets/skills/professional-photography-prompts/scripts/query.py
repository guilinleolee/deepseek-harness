#!/usr/bin/env python3
"""
Professional Photography Prompts Query Script
专业摄影风格提示词库查询
"""

import json
import os
import random
import argparse

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "photography_prompts.json")


class PhotographyPromptLibrary:
    """专业摄影提示词库"""

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
                # Portrait Categories
                {
                    "id": "ph001",
                    "category": "portrait",
                    "style": "35mm",
                    "prompt": "35mm film portrait, Kodak Portra 400, natural grain, warm color temperature, soft highlights, muted shadows, documentary style, intimate close-up, authentic emotion, analog aesthetic, shallow depth of field",
                    "engagement": {"likes": 1987, "retweets": 567, "views": 38900},
                    "author": "@FilmNeverDies"
                },
                {
                    "id": "ph002",
                    "category": "portrait",
                    "style": "fujifilm",
                    "prompt": "Fujifilm Provia 100F simulation portrait, vibrant yet pastel colors, soft contrast, natural skin tones, cinematic framing, golden hour lighting, film grain texture, editorial fashion photography, professional retouch",
                    "engagement": {"likes": 3156, "retweets": 1203, "views": 67800},
                    "author": "@FilmGrain"
                },
                {
                    "id": "ph003",
                    "category": "portrait",
                    "style": "ccd",
                    "prompt": "CCD sensor aesthetic portrait, organic colors, slight color bleeding, nostalgic mood, analog warmth, rich blacks, purple and green color casts, early 2000s digital camera look, intimate framing, dreamy atmosphere",
                    "engagement": {"likes": 2456, "retweets": 934, "views": 52300},
                    "author": "@AnalogDreams"
                },
                {
                    "id": "ph004",
                    "category": "portrait",
                    "style": "korean",
                    "prompt": "Korean idol aesthetic portrait, clean retouched skin, bright eye highlights, soft gradient pastel background, ethereal lighting from above, pastel wardrobe styling, dreamy atmosphere, editorial quality, glossy magazine look, 8K resolution",
                    "engagement": {"likes": 2847, "retweets": 892, "views": 45600},
                    "author": "@BubbleBrain"
                },
                {
                    "id": "ph005",
                    "category": "portrait",
                    "style": "neon",
                    "prompt": "Neon-lit convenience store portrait, late night atmosphere, rain reflections on wet pavement, warm interior glow from fluorescent lights, cinematic portrait, shallow depth of field, moody lighting, urban夜色, bokeh city lights in background",
                    "engagement": {"likes": 3421, "retweets": 1456, "views": 89000},
                    "author": "@NeonDreams"
                },
                {
                    "id": "ph006",
                    "category": "portrait",
                    "style": "japanese_onsen",
                    "prompt": "Japanese onsen ryokan portrait, traditional Japanese inn interior, steam rising, wooden bathhouse architecture, soft natural light through shoji screens, warm amber tones, serene contemplative mood, zen aesthetic, intimate close-up",
                    "engagement": {"likes": 2890, "retweets": 1023, "views": 61200},
                    "author": "@JapanVisions"
                },
                {
                    "id": "ph007",
                    "category": "portrait",
                    "style": "cinematic",
                    "prompt": "Cinematic portrait photography, anamorphic lens look, shallow depth of field, dramatic side lighting, film still quality, Roger Deakins inspired, rich color grading, film grain, 2.39:1 aspect ratio composition",
                    "engagement": {"likes": 4123, "retweets": 1876, "views": 98000},
                    "author": "@CinematicStill"
                },
                {
                    "id": "ph008",
                    "category": "portrait",
                    "style": "moody",
                    "prompt": "Moody fine art portrait, dark moody aesthetic, Rembrandt lighting, deep shadows, desaturated tones, fog atmosphere, editorial photography, high contrast black and white conversion potential, mysterious atmosphere",
                    "engagement": {"likes": 3567, "retweets": 1234, "views": 72300},
                    "author": "@FineArtMood"
                },

                # Street Categories
                {
                    "id": "st001",
                    "category": "street",
                    "style": "documentary",
                    "prompt": "Street photography documentary style, candid moment, natural light, urban environment, decisive moment Henri Cartier-Bresson, 35mm film look, environmental portrait, authentic scene, journalistic aesthetic",
                    "engagement": {"likes": 2345, "retweets": 876, "views": 45600},
                    "author": "@StreetDoc"
                },
                {
                    "id": "st002",
                    "category": "street",
                    "style": "tokyo_night",
                    "prompt": "Tokyo street photography at night, neon lights reflection on wet streets, crowd silhouettes, Japanese signage, cinematic color grading, Street photography aesthetic, Daido Moriyama inspired, high contrast black and white option",
                    "engagement": {"likes": 4567, "retweets": 1987, "views": 89000},
                    "author": "@TokyoNight"
                },
                {
                    "id": "st003",
                    "category": "street",
                    "style": "urban_ decay",
                    "prompt": "Urban decay photography, abandoned building interior, golden hour light through broken windows, dust particles in light beam, melancholic atmosphere, film photography aesthetic, expired Kodak film look, rich texture",
                    "engagement": {"likes": 2876, "retweets": 987, "views": 56700},
                    "author": "@UrbanDecay"
                },

                # Product Categories
                {
                    "id": "pr001",
                    "category": "product",
                    "style": "minimal",
                    "prompt": "Minimalist product photography, white background, single product centered, soft shadows, clean lighting, Apple-style product shot, studio lighting setup, high-end commercial aesthetic, 8K resolution",
                    "engagement": {"likes": 3456, "retweets": 1234, "views": 67800},
                    "author": "@ProductMinimal"
                },
                {
                    "id": "pr002",
                    "category": "product",
                    "style": "lifestyle",
                    "prompt": "Lifestyle product photography, coffee shop setting, warm natural light, wooden table surface, flat lay arrangement, lifestyle context, editorial style, inviting atmosphere, shallow depth of field",
                    "engagement": {"likes": 4123, "retweets": 1567, "views": 78900},
                    "author": "@LifestyleShot"
                },
                {
                    "id": "pr003",
                    "category": "product",
                    "style": "dark_moody",
                    "prompt": "Dark moody product photography, dark background, dramatic rim lighting, single product highlight, luxury aesthetic, high-end commercial, rich shadows, selective focus, perfume bottle or jewelry style",
                    "engagement": {"likes": 2890, "retweets": 1023, "views": 56700},
                    "author": "@DarkProduct"
                },

                # Landscape Categories
                {
                    "id": "ls001",
                    "category": "landscape",
                    "style": "golden_hour",
                    "prompt": "Golden hour landscape photography, dramatic sky, warm orange and purple tones, silhouette foreground, sweeping vista, Ansel Adams inspired, rich detail in highlights and shadows, 4x5 large format look, epic scale",
                    "engagement": {"likes": 5678, "retweets": 2345, "views": 134000},
                    "author": "@LandscapeMaster"
                },
                {
                    "id": "ls002",
                    "category": "landscape",
                    "style": "japanese_garden",
                    "prompt": "Japanese garden landscape, koi pond, autumn colors, red maple leaves reflection, stone lantern, traditional architecture, serene atmosphere, zen aesthetic, soft diffused light, travel photography style",
                    "engagement": {"likes": 4567, "retweets": 1876, "views": 98000},
                    "author": "@JapanGarden"
                },
                {
                    "id": "ls003",
                    "category": "landscape",
                    "style": "astrophotography",
                    "prompt": "Astrophotography style landscape, Milky Way galaxy arch over mountain silhouette, star trails, long exposure look, dark sky preserve aesthetic, awe-inspiring scale, deep blue and purple tones, commercial quality",
                    "engagement": {"likes": 6789, "retweets": 2987, "views": 156000},
                    "author": "@AstroLandscape"
                },

                # Editorial Categories
                {
                    "id": "ed001",
                    "category": "editorial",
                    "style": "vogue",
                    "prompt": "Vogue editorial portrait, high fashion, dramatic makeup, bold styling, studio lighting setup, fashion magazine quality, editorial composition, Helmut Newton inspired, confident powerful pose, luxury fashion aesthetic",
                    "engagement": {"likes": 7890, "retweets": 3456, "views": 178000},
                    "author": "@FashionEditorial"
                },
                {
                    "id": "ed002",
                    "category": "editorial",
                    "style": "teen_vogue",
                    "prompt": "Teen Vogue style editorial, fresh natural makeup, effortless cool styling, natural light, candid moments, Gen Z aesthetic, diverse representation, street style mixed with editorial, social media ready",
                    "engagement": {"likes": 6789, "retweets": 2876, "views": 145000},
                    "author": "@TeenEditorial"
                },
                {
                    "id": "ed003",
                    "category": "editorial",
                    "style": "commercial",
                    "prompt": "Commercial editorial photography, clean aesthetic, lifestyle brand style, aspirational imagery, soft colors, natural settings, Gap or Uniqlo campaign aesthetic, approachable yet polished, warm inviting tones",
                    "engagement": {"likes": 4567, "retweets": 1876, "views": 89000},
                    "author": "@CommercialEdit"
                }
            ]
        }

    def search(self, category: str = None, style: str = None,
               sort: str = "engagement", limit: int = 10) -> list:
        """
        搜索摄影提示词

        Args:
            category: 分类 (portrait/street/product/landscape/editorial)
            style: 风格 (35mm/fujifilm/ccd/korean/neon等)
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
            use_case: 用例 (social_media/social_media_portrait/product_shot/landscape/editorial)
        """
        use_case_map = {
            "social_media_portrait": {"category": "portrait", "styles": ["korean", "35mm", "fujifilm"]},
            "product_shot": {"category": "product", "styles": ["minimal", "lifestyle", "dark_moody"]},
            "landscape": {"category": "landscape", "styles": ["golden_hour", "japanese_garden", "astrophotography"]},
            "editorial": {"category": "editorial", "styles": ["vogue", "teen_vogue", "commercial"]},
            "street": {"category": "street", "styles": ["documentary", "tokyo_night", "urban_decay"]},
        }

        config = use_case_map.get(use_case, use_case_map["social_media_portrait"])
        results = []

        for style in config["styles"]:
            results.extend(self.search(category=config["category"], style=style, limit=3))

        return results[:5]


def main():
    parser = argparse.ArgumentParser(description="Professional Photography Prompts Query")
    parser.add_argument("--category", choices=["portrait", "street", "product", "landscape", "editorial"])
    parser.add_argument("--style", help="风格关键词")
    parser.add_argument("--sort", choices=["engagement", "random"], default="engagement")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--random", action="store_true")
    parser.add_argument("--export", choices=["json", "markdown"])
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--recommend", help="用例推荐")

    args = parser.parse_args()

    lib = PhotographyPromptLibrary()

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

    if args.export == "json":
        output = json.dumps(results, ensure_ascii=False, indent=2)
    elif args.export == "markdown":
        lines = ["# Professional Photography Prompts\n"]
        for i, p in enumerate(results, 1):
            lines.append(f"## {i}. [{p['style']}] {p['category']}")
            lines.append(f"**Author**: {p['author']}")
            lines.append(f"**互动**: ❤️{p['engagement']['likes']} 🔄{p['engagement']['retweets']} 👁️{p['engagement']['views']}")
            lines.append(f"\n```\n{p['prompt']}\n```\n")
        output = "\n".join(lines)
    else:
        lines = [f"Professional Photography Prompts (Sort: {sort}, Showing: {len(results)})\n"]
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
