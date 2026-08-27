#!/usr/bin/env python3
"""
Character Design Prompts Query Script
角色设计提示词库查询
"""

import json
import os
import random
import argparse

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "character_design_prompts.json")


class CharacterDesignPromptLibrary:
    """角色设计提示词库"""

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
                # Anime Category
                {
                    "id": "cd001",
                    "category": "anime",
                    "style": "anime",
                    "prompt": "Japanese anime character design, cel shading, vibrant colors, Studio Ghibli inspired, soft lighting, detailed hair strands, expressive eyes, dynamic pose, traditional anime art style, 4K resolution",
                    "engagement": {"likes": 4567, "retweets": 1234, "views": 89000},
                    "author": "@AnimeArtDesign"
                },
                {
                    "id": "cd002",
                    "category": "anime",
                    "style": "anime",
                    "prompt": "Anime protagonist design, spiky blue hair, determined expression, school uniform with custom details, cape flowing in wind, studio ufotable quality, cinematic composition, warm sunset lighting, detailed background environment",
                    "engagement": {"likes": 5678, "retweets": 1567, "views": 112000},
                    "author": "@AnimeCreator"
                },
                {
                    "id": "cd003",
                    "category": "anime",
                    "style": "anime",
                    "prompt": "Mecha anime character, sleek robot suit design, glowing energy core, pilot cockpit view, detailed mechanical joints, anti-beam coating texture, dynamic action pose, Evangelion inspired, clean vector lines",
                    "engagement": {"likes": 3456, "retweets": 987, "views": 67000},
                    "author": "@MechaDesign"
                },

                # Manga Category
                {
                    "id": "cd004",
                    "category": "manga",
                    "style": "manga",
                    "prompt": "Black and white manga character, halftone dot patterns, speed lines, dramatic action pose, traditional manga art style, thick outline strokes, detailed screen tones, comic panel composition, Akira Toriyama inspired",
                    "engagement": {"likes": 2345, "retweets": 678, "views": 45000},
                    "author": "@MangaArtist"
                },
                {
                    "id": "cd005",
                    "category": "manga",
                    "style": "manga",
                    "prompt": "Shoujo manga character design, sparkles, rose petals, big sparkling eyes, flowing hair with ribbons, elegant dress, soft pink color palette, Love Live style, spark effects, dreamy atmosphere",
                    "engagement": {"likes": 6789, "retweets": 2345, "views": 134000},
                    "author": "@ShoujoManga"
                },

                # Chibi Category
                {
                    "id": "cd006",
                    "category": "chibi",
                    "style": "chibi",
                    "prompt": "Super deformed chibi character, big head small body ratio 1:1, cute round face, tiny limbs, adorable expression, pastel colors, kawaii style, transparent shadow, enamel pin design aesthetic, simple clean lines",
                    "engagement": {"likes": 7890, "retweets": 2876, "views": 156000},
                    "author": "@ChibiArt"
                },
                {
                    "id": "cd007",
                    "category": "chibi",
                    "style": "chibi",
                    "prompt": "Chibi anime mascot character, happy expression, peace sign pose, circular badge design, limited color palette, bold black outlines, sticker sheet composition, Sanrio inspired, fluffy cheeks",
                    "engagement": {"likes": 8901, "retweets": 3124, "views": 178000},
                    "author": "@KawaiiDesign"
                },

                # Pixar/Disney 3D Character
                {
                    "id": "cd008",
                    "category": "3d_character",
                    "style": "pixar",
                    "prompt": "Pixar style 3D character design, toon shader rendering, stylized proportions, warm lighting, subsurface scattering on skin, expressive face, detailed clothing with fabric simulation, toy story aesthetic, 3D render quality",
                    "engagement": {"likes": 9123, "retweets": 3456, "views": 201000},
                    "author": "@3DCharacterArt"
                },
                {
                    "id": "cd009",
                    "category": "3d_character",
                    "style": "pixar",
                    "prompt": "Pixar style action hero character, muscular yet stylized build, dynamic heroic pose, costume design with cape and emblem, dramatic rim lighting, volumetric fog atmosphere, movie poster composition, Incredibles inspired",
                    "engagement": {"likes": 7654, "retweets": 2345, "views": 145000},
                    "author": "@PixarHero"
                },

                # Disney Category
                {
                    "id": "cd010",
                    "category": "3d_character",
                    "style": "disney",
                    "prompt": "Disney princess character design, elegant ball gown, flowing hair with flowers, tiara crown, fairy godmother magic sparkles, Renaissance painting aesthetic, Disney Frozen inspired, ice blue color scheme, magical atmosphere",
                    "engagement": {"likes": 11234, "retweets": 4567, "views": 234000},
                    "author": "@DisneyPrincess"
                },
                {
                    "id": "cd011",
                    "category": "3d_character",
                    "style": "disney",
                    "prompt": "Disney villain design, theatrical costume with cape, dramatic silhouette, sinister smile, dark purple and black color palette, Maleficent inspired, magical fire effects, theatrical stage lighting, character turnaround sheet",
                    "engagement": {"likes": 8907, "retweets": 3234, "views": 167000},
                    "author": "@DisneyVillain"
                },

                # Dreamworks Category
                {
                    "id": "cd012",
                    "category": "3d_character",
                    "style": "dreamworks",
                    "prompt": "Dreamworks style character, exaggerated expressions, How to Train Your Dragon inspired, Viking warrior design, leather armor with fur trim, battle scars, heroic pose with weapon, dramatic sky background, bold character design",
                    "engagement": {"likes": 5678, "retweets": 1876, "views": 112000},
                    "author": "@DreamworksArt"
                },

                # Vintage Cartoon Style
                {
                    "id": "cd013",
                    "category": "cartoon",
                    "style": "vintage_cartoon",
                    "prompt": "1950s rubber hose animation style character, round head, bendy limbs, limited animation poses, warm vintage color palette, cream and brown tones, Betty Boop inspired, film grain texture overlay, nostalgic cartoon aesthetic",
                    "engagement": {"likes": 3456, "retweets": 987, "views": 67000},
                    "author": "@VintageCartoon"
                },
                {
                    "id": "cd014",
                    "category": "cartoon",
                    "style": "vintage_cartoon",
                    "prompt": "Looney Tunes inspired character, exaggerated squash and stretch, cel animation style, bright primary colors, black outlines, Bugs Bunny aesthetic, running pose, desert background, classic cartoon energy",
                    "engagement": {"likes": 4567, "retweets": 1234, "views": 89000},
                    "author": "@ClassicCartoon"
                },

                # Doodle/Sketch Style
                {
                    "id": "cd015",
                    "category": "style",
                    "style": "doodle",
                    "prompt": "Hand-drawn doodle style character, wobbly lines, marker pen aesthetic, notebook paper background, loose sketchy strokes, colorful markers, South Park inspired, simple but expressive, character sheet with multiple poses",
                    "engagement": {"likes": 5432, "retweets": 1567, "views": 98000},
                    "author": "@DoodleArt"
                },
                {
                    "id": "cd016",
                    "category": "style",
                    "style": "sketch",
                    "prompt": "Detailed pencil sketch character design, graphite on paper texture, cross-hatching shading, anatomical accuracy, fashion illustration style, high-end editorial sketch, loose flowing hair strands, Valentino inspired, runway model proportions",
                    "engagement": {"likes": 4321, "retweets": 1234, "views": 78000},
                    "author": "@SketchArtist"
                },

                # Vector Style
                {
                    "id": "cd017",
                    "category": "style",
                    "style": "vector",
                    "prompt": "Clean vector art character design, flat design aesthetic, limited color palette, bold shapes, Adobe Illustrator style, flat color with subtle gradients, minimal shadows, tech company mascot design, scalable to any size",
                    "engagement": {"likes": 3456, "retweets": 876, "views": 56000},
                    "author": "@VectorDesign"
                },
                {
                    "id": "cd018",
                    "category": "style",
                    "style": "vector",
                    "prompt": "Vector illustration character, flat vector art with depth, isometric view, tech startup mascot design, pastel colors, simple geometric shapes, modern corporate art style, Slack/Discord mascot inspired, character turnaround",
                    "engagement": {"likes": 4567, "retweets": 1098, "views": 78000},
                    "author": "@FlatVector"
                },

                # IP Design
                {
                    "id": "cd019",
                    "category": "anime",
                    "style": "anime",
                    "prompt": "Original IP character design, mascot design for brand, friendly design, memorable silhouette, simple shapes, strong color identity, toy-friendly design, multiple expression sheets, cohesive design language, Sanrio inspired mascot, commercial quality",
                    "engagement": {"likes": 6789, "retweets": 2134, "views": 123000},
                    "author": "@IPDesigner"
                },
                {
                    "id": "cd020",
                    "category": "anime",
                    "style": "anime",
                    "prompt": "Game character design for RPG, knight warrior with sword and shield, detailed armor plates, fantasy aesthetic, Guild Wars inspired, character creation sheet with stats, front back side view, weapon detail close-ups, RPG game ready",
                    "engagement": {"likes": 5432, "retweets": 1654, "views": 102000},
                    "author": "@GameCharacter"
                }
            ]
        }

    def search(self, category: str = None, style: str = None,
               sort: str = "engagement", limit: int = 10) -> list:
        """
        搜索角色设计提示词

        Args:
            category: 分类 (anime/manga/chibi/3d_character/cartoon/style)
            style: 风格 (anime/manga/chibi/pixar/disney/dreamworks/vintage_cartoon/doodle/sketch/vector)
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
            use_case: 用例 (anime_character/manga_style/chibi_cute/3d_animation/disney_character/game_character/ip_design)
        """
        use_case_map = {
            "anime_character": {"category": "anime", "styles": ["anime"]},
            "manga_style": {"category": "manga", "styles": ["manga"]},
            "chibi_cute": {"category": "chibi", "styles": ["chibi"]},
            "3d_animation": {"category": "3d_character", "styles": ["pixar", "disney", "dreamworks"]},
            "disney_character": {"category": "3d_character", "styles": ["disney"]},
            "pixar_style": {"category": "3d_character", "styles": ["pixar"]},
            "game_character": {"category": "anime", "styles": ["anime"]},
            "ip_design": {"category": "anime", "styles": ["anime", "chibi"]},
            "vintage_cartoon": {"category": "cartoon", "styles": ["vintage_cartoon"]},
            "doodle_sketch": {"category": "style", "styles": ["doodle", "sketch"]},
            "vector_art": {"category": "style", "styles": ["vector"]},
        }

        config = use_case_map.get(use_case, use_case_map["anime_character"])
        results = []

        for style in config["styles"]:
            results.extend(self.search(category=config["category"], style=style, limit=3))

        return results[:5]


def main():
    parser = argparse.ArgumentParser(description="Character Design Prompts Query")
    parser.add_argument("--category", choices=["anime", "manga", "chibi", "3d_character", "cartoon", "style"],
                        help="分类 (anime/manga/chibi/3d_character/cartoon/style)")
    parser.add_argument("--style", help="风格关键词 (anime/manga/chibi/pixar/disney/doodle等)")
    parser.add_argument("--sort", choices=["engagement", "random"], default="engagement")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--random", action="store_true")
    parser.add_argument("--export", choices=["json", "markdown"])
    parser.add_argument("--output", help="输出文件路径")
    parser.add_argument("--recommend", help="用例推荐")

    args = parser.parse_args()

    lib = CharacterDesignPromptLibrary()

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
        lines = ["# Character Design Prompts\n"]
        for i, p in enumerate(results, 1):
            lines.append(f"## {i}. [{p['style']}] {p['category']}")
            lines.append(f"**Author**: {p['author']}")
            lines.append(f"**互动**: ❤️{p['engagement']['likes']} 🔄{p['engagement']['retweets']} 👁️{p['engagement']['views']}")
            lines.append(f"\n```\n{p['prompt']}\n```\n")
        output = "\n".join(lines)
    else:
        lines = [f"Character Design Prompts (Sort: {sort}, Showing: {len(results)})\n"]
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
