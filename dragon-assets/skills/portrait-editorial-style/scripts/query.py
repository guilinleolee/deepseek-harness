#!/usr/bin/env python3
"""
Portrait + Editorial Style Prompts Query Script
肖像摄影+时尚编辑提示词库查询
"""

import json
import os
import random
import argparse

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "portrait_editorial_prompts.json")


class PortraitEditorialPromptLibrary:
    """肖像摄影+时尚编辑提示词库"""

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
                # Portrait Categories - 肖像摄影
                {
                    "id": "pe001",
                    "category": "portrait",
                    "style": "35mm",
                    "prompt": "35mm film portrait, Kodak Portra 400, natural grain, warm color temperature, soft highlights, muted shadows, documentary style, intimate close-up, authentic emotion, analog aesthetic, shallow depth of field",
                    "engagement": {"likes": 1987, "retweets": 567, "views": 38900},
                    "author": "@FilmNeverDies"
                },
                {
                    "id": "pe002",
                    "category": "portrait",
                    "style": "fujifilm",
                    "prompt": "Fujifilm Provia 100F simulation portrait, vibrant yet pastel colors, soft contrast, natural skin tones, cinematic framing, golden hour lighting, film grain texture, editorial fashion photography, professional retouch",
                    "engagement": {"likes": 3156, "retweets": 1203, "views": 67800},
                    "author": "@FilmGrain"
                },
                {
                    "id": "pe003",
                    "category": "portrait",
                    "style": "ccd",
                    "prompt": "CCD sensor aesthetic portrait, organic colors, slight color bleeding, nostalgic mood, analog warmth, rich blacks, purple and green color casts, early 2000s digital camera look, intimate framing, dreamy atmosphere",
                    "engagement": {"likes": 2456, "retweets": 934, "views": 52300},
                    "author": "@AnalogDreams"
                },
                {
                    "id": "pe004",
                    "category": "portrait",
                    "style": "korean",
                    "prompt": "Korean idol aesthetic portrait, clean retouched skin, bright eye highlights, soft gradient pastel background, ethereal lighting from above, pastel wardrobe styling, dreamy atmosphere, editorial quality, glossy magazine look, 8K resolution",
                    "engagement": {"likes": 2847, "retweets": 892, "views": 45600},
                    "author": "@BubbleBrain"
                },
                {
                    "id": "pe005",
                    "category": "portrait",
                    "style": "neon",
                    "prompt": "Neon-lit convenience store portrait, late night atmosphere, rain reflections on wet pavement, warm interior glow from fluorescent lights, cinematic portrait, shallow depth of field, moody lighting, urban夜色, bokeh city lights in background",
                    "engagement": {"likes": 3421, "retweets": 1456, "views": 89000},
                    "author": "@NeonDreams"
                },
                {
                    "id": "pe006",
                    "category": "portrait",
                    "style": "cinematic",
                    "prompt": "Cinematic portrait photography, anamorphic lens look, shallow depth of field, dramatic side lighting, film still quality, Roger Deakins inspired, rich color grading, film grain, 2.39:1 aspect ratio composition",
                    "engagement": {"likes": 4123, "retweets": 1876, "views": 98000},
                    "author": "@CinematicStill"
                },
                {
                    "id": "pe007",
                    "category": "portrait",
                    "style": "moody",
                    "prompt": "Moody fine art portrait, dark moody aesthetic, Rembrandt lighting, deep shadows, desaturated tones, fog atmosphere, editorial photography, high contrast black and white conversion potential, mysterious atmosphere",
                    "engagement": {"likes": 3567, "retweets": 1234, "views": 72300},
                    "author": "@FineArtMood"
                },

                # Editorial Categories - 时尚编辑
                {
                    "id": "pe008",
                    "category": "editorial",
                    "style": "vogue",
                    "prompt": "Vogue editorial portrait, high fashion, dramatic makeup, bold styling, studio lighting setup, fashion magazine quality, editorial composition, Helmut Newton inspired, confident powerful pose, luxury fashion aesthetic, 85mm f/1.4",
                    "engagement": {"likes": 7890, "retweets": 3456, "views": 178000},
                    "author": "@FashionEditorial"
                },
                {
                    "id": "pe009",
                    "category": "editorial",
                    "style": "teen_vogue",
                    "prompt": "Teen Vogue style editorial, fresh natural makeup, effortless cool styling, natural light, candid moments, Gen Z aesthetic, diverse representation, street style mixed with editorial, social media ready, authentic youth culture",
                    "engagement": {"likes": 6789, "retweets": 2876, "views": 145000},
                    "author": "@TeenEditorial"
                },
                {
                    "id": "pe010",
                    "category": "editorial",
                    "style": "commercial",
                    "prompt": "Commercial editorial photography, clean aesthetic, lifestyle brand style, aspirational imagery, soft colors, natural settings, Gap or Uniqlo campaign aesthetic, approachable yet polished, warm inviting tones, commercial print quality",
                    "engagement": {"likes": 4567, "retweets": 1876, "views": 89000},
                    "author": "@CommercialEdit"
                },

                # Additional Portrait Styles
                {
                    "id": "pe011",
                    "category": "portrait",
                    "style": "portrait",
                    "prompt": "Clean beauty portrait photography, minimal retouching, natural skin texture, soft diffused lighting, neutral background, product focus, beauty editorial quality, glass bottle reflections, high-end cosmetics aesthetic",
                    "engagement": {"likes": 2890, "retweets": 1023, "views": 56700},
                    "author": "@CleanBeauty"
                },
                {
                    "id": "pe012",
                    "category": "portrait",
                    "style": "portrait",
                    "prompt": "Environmental portrait, subject in their natural setting, documentary approach, available light, authentic context, editorial storytelling, National Geographic style, intimate connection between subject and environment",
                    "engagement": {"likes": 3245, "retweets": 1187, "views": 65400},
                    "author": "@EnvironmentalPortraits"
                },
                {
                    "id": "pe013",
                    "category": "portrait",
                    "style": "portrait",
                    "prompt": "High contrast black and white portrait, strong directional lighting, detailed texture in skin, Ansel Adams influenced, Zone System exposure, artistic interpretation, fine art gallery quality, silver gelatin print aesthetic",
                    "engagement": {"likes": 2156, "retweets": 876, "views": 43200},
                    "author": "@BWMaster"
                },
                {
                    "id": "pe014",
                    "category": "portrait",
                    "style": "portrait",
                    "prompt": "Double exposure portrait, silhouette combined with landscape, surreal artistic effect, creative composite, fine art photography, conceptual portrait, gallery exhibition quality, limited color palette",
                    "engagement": {"likes": 3567, "retweets": 1456, "views": 72300},
                    "author": "@ConceptualPortraits"
                },
                {
                    "id": "pe015",
                    "category": "portrait",
                    "style": "portrait",
                    "prompt": "Golden hour portrait, warm sunset light, lens flare, rim lighting, romantic atmosphere, outdoor setting, soft bokeh background, editorial travel style, National Geographic meets fashion, cinematic color grading",
                    "engagement": {"likes": 4234, "retweets": 1678, "views": 87600},
                    "author": "@GoldenHourPortraits"
                },

                # Additional Editorial Styles
                {
                    "id": "pe016",
                    "category": "editorial",
                    "style": "editorial",
                    "prompt": "Harper's Bazaar editorial, sophisticated elegance, timeless beauty, dramatic lighting, couture fashion, museum quality, editorial composition, classic photography aesthetic, fine art meets fashion",
                    "engagement": {"likes": 5678, "retweets": 2345, "views": 112000},
                    "author": "@BazaarEditorial"
                },
                {
                    "id": "pe017",
                    "category": "editorial",
                    "style": "editorial",
                    "prompt": "ELLE magazine editorial, fresh modern beauty, natural makeup, effortless styling, rooftop or urban setting, candid moments, lifestyle fashion, social media crossover, approachable luxury",
                    "engagement": {"likes": 4890, "retweets": 1987, "views": 98000},
                    "author": "@ELLEditorial"
                },
                {
                    "id": "pe018",
                    "category": "editorial",
                    "style": "editorial",
                    "prompt": "Vogue Italia style editorial, avant-garde fashion, artistic composition, dramatic makeup, conceptual styling, museum exhibition quality, fashion as art, editorial innovation, boundary-pushing creativity",
                    "engagement": {"likes": 6789, "retweets": 2876, "views": 145000},
                    "author": "@VogueItalia"
                }
            ]
        }

    def search(self, category: str = None, style: str = None,
               sort: str = "engagement", limit: int = 10) -> list:
        """
        搜索肖像/时尚编辑提示词

        Args:
            category: 分类 (portrait/editorial)
            style: 风格 (35mm/fujifilm/ccd/korean/neon/cinematic/moody/vogue/teen_vogue/commercial)
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
            use_case: 用例 (social_media_portrait/editorial_magazine/product_portrait/artistic_portrait)
        """
        use_case_map = {
            "social_media_portrait": {"category": "portrait", "styles": ["korean", "35mm", "ccd"]},
            "editorial_magazine": {"category": "editorial", "styles": ["vogue", "teen_vogue", "editorial"]},
            "product_portrait": {"category": "portrait", "styles": ["cinematic", "moody", "neon"]},
            "artistic_portrait": {"category": "portrait", "styles": ["moody", "cinematic", "fujifilm"]},
        }

        config = use_case_map.get(use_case, use_case_map["social_media_portrait"])
        results = []

        for style in config["styles"]:
            results.extend(self.search(category=config["category"], style=style, limit=3))

        return results[:5]


def main():
    parser = argparse.ArgumentParser(description="Portrait + Editorial Style Prompts Query")
    parser.add_argument("--category", choices=["portrait", "editorial"],
                        help="分类 (portrait/editorial)")
    parser.add_argument("--style", help="风格关键词 (35mm/fujifilm/ccd/korean/vogue等)")
    parser.add_argument("--sort", choices=["engagement", "random"], default="engagement")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--random", action="store_true")
    parser.add_argument("--export", choices=["json", "markdown"])
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--recommend", help="用例推荐")

    args = parser.parse_args()

    lib = PortraitEditorialPromptLibrary()

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
        lines = ["# Portrait + Editorial Style Prompts\n"]
        for i, p in enumerate(results, 1):
            lines.append(f"## {i}. [{p['style']}] {p['category']}")
            lines.append(f"**Author**: {p['author']}")
            lines.append(f"**互动**: ❤️{p['engagement']['likes']} 🔄{p['engagement']['retweets']} 👁️{p['engagement']['views']}")
            lines.append(f"\n```\n{p['prompt']}\n```\n")
        output = "\n".join(lines)
    else:
        lines = [f"Portrait + Editorial Style Prompts (Sort: {sort}, Showing: {len(results)})\n"]
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
