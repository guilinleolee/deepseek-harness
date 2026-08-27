#!/usr/bin/env python3
"""
E-commerce Image Generator Query Script
电商场景专用提示词查询
数据来源: EvoLinkAI/awesome-gpt-image-2-prompts - E-commerce分类
"""

import json
import os
import random
import argparse
from pathlib import Path

DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "ecommerce_prompts.json")


class EcommercePromptLibrary:
    """电商场景提示词库"""

    CATEGORIES = {
        "product_main": "商品主图",
        "ad_banner": "广告Banner",
        "detail_page": "详情页",
        "seeding": "种草图文",
        "comparison": "对比图",
        "price_tag": "价格标签"
    }

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
        """内置电商提示词示例"""
        return {
            "prompts": [
                # 商品主图
                {
                    "id": "ec_p001",
                    "category": "product_main",
                    "name": "白底主图",
                    "prompt": "clean white background product photography, {product_name}, studio lighting, high resolution, detailed texture, {angle} view, minimalist composition, 4K, white seamless backdrop",
                    "platform": "淘宝/京东/亚马逊",
                    "conversion": 4.2
                },
                {
                    "id": "ec_p002",
                    "category": "product_main",
                    "name": "透明背景",
                    "prompt": "transparent PNG product shot, {product_name}, pure white background, studio lighting, professional photography, alpha channel, clean edge cutting, 4K resolution",
                    "platform": "亚马逊/eBay",
                    "conversion": 3.8
                },
                {
                    "id": "ec_p003",
                    "category": "product_main",
                    "name": "场景代入",
                    "prompt": "{product_name} in lifestyle setting, {scene}, warm natural lighting, {mood} atmosphere, professional e-commerce photography, high conversion, cinematic composition",
                    "platform": "天猫/京东",
                    "conversion": 4.5
                },
                # 广告Banner
                {
                    "id": "ec_b001",
                    "category": "ad_banner",
                    "name": "直通车爆款",
                    "prompt": "{product_name} explosive sales banner, vibrant colors, bold typography '{headline}', flash sale countdown style, dynamic composition, high energy, mobile-first design",
                    "platform": "淘宝直通车",
                    "conversion": 4.1
                },
                {
                    "id": "ec_b002",
                    "category": "ad_banner",
                    "name": "品牌旗舰店",
                    "prompt": "{product_name} luxury brand banner, elegant design, minimalist composition, premium feel, {brand} aesthetic, sophisticated typography, soft gradient background",
                    "platform": "天猫旗舰店",
                    "conversion": 4.3
                },
                {
                    "id": "ec_b003",
                    "category": "ad_banner",
                    "name": "促销秒杀",
                    "prompt": "{product_name} flash sale poster, urgent atmosphere, countdown timer graphic, bold discount price tag, {headline}, high contrast colors, attention-grabbing design",
                    "platform": "京东秒杀",
                    "conversion": 3.9
                },
                # 详情页
                {
                    "id": "ec_d001",
                    "category": "detail_page",
                    "name": "场景故事",
                    "prompt": "{product_name} in {scene} lifestyle, emotional storytelling photography, warm lighting, relatable atmosphere, lifestyle integration, aspirational mood, natural expression",
                    "platform": "详情页主图",
                    "conversion": 4.4
                },
                {
                    "id": "ec_d002",
                    "category": "detail_page",
                    "name": "功能展示",
                    "prompt": "{product_name} product detail shot, showcasing {feature}, clean studio lighting, professional product photography, feature highlight, annotation-ready design, white background",
                    "platform": "详情页功能区",
                    "conversion": 3.7
                },
                {
                    "id": "ec_d003",
                    "category": "detail_page",
                    "name": "对比说明",
                    "prompt": "{product_name} before and after comparison, split screen layout, dramatic transformation visual, professional photography, evidence-based marketing, trust-building imagery",
                    "platform": "详情页对比区",
                    "conversion": 4.0
                },
                # 种草图文
                {
                    "id": "ec_s001",
                    "category": "seeding",
                    "name": "小红书种草",
                    "prompt": "aesthetic flat lay of {product_name}, {style} photography, styled with {props}, natural daylight, {color_palette} palette, minimalist composition, instagram-worthy, lifestyle content",
                    "platform": "小红书/抖音",
                    "conversion": 4.6
                },
                {
                    "id": "ec_s002",
                    "category": "seeding",
                    "name": "开箱测评",
                    "prompt": "{product_name} unboxing photography, excited reveal moment, premium packaging visible, lifestyle setting, natural expression of surprise, user-generated content style, authentic feel",
                    "platform": "小红书/微博",
                    "conversion": 4.3
                },
                {
                    "id": "ec_s003",
                    "category": "seeding",
                    "name": "使用场景",
                    "prompt": "{product_name} in daily use, {scene} setting, relatable lifestyle, warm lighting, {mood} atmosphere, authentic moment captured, UGC aesthetic, aspirational but real",
                    "platform": "小红书/抖音",
                    "conversion": 4.5
                },
                # 对比图
                {
                    "id": "ec_c001",
                    "category": "comparison",
                    "name": "竞品对比",
                    "prompt": "left right comparison: our {product_name} vs competitors product, same scene same angle, quality difference clearly visible, professional comparison layout, evidence-based selling",
                    "platform": "详情页/知乎",
                    "conversion": 3.6
                },
                {
                    "id": "ec_c002",
                    "category": "comparison",
                    "name": "规格对比",
                    "prompt": "{product_name} size comparison chart, household items for scale, clear measurement annotations, professional product photography, educational layout, informative design",
                    "platform": "详情页/京东",
                    "conversion": 3.8
                },
                # 价格标签
                {
                    "id": "ec_t001",
                    "category": "price_tag",
                    "name": "促销标签",
                    "prompt": "{discount}% off price tag design, bold red color scheme, urgent countdown timer, {product_name}, attention-grabbing graphic, promotional sticker style, mobile-ready",
                    "platform": "淘宝/拼多多",
                    "conversion": 4.0
                },
                {
                    "id": "ec_t002",
                    "category": "price_tag",
                    "name": "会员专享",
                    "prompt": "VIP member exclusive price tag, premium gold design, {product_name}, exclusive badge graphic, sophisticated typography, loyalty program visual, elegant styling",
                    "platform": "天猫/京东",
                    "conversion": 3.9
                },
                {
                    "id": "ec_t003",
                    "category": "price_tag",
                    "name": "限时特惠",
                    "prompt": "limited time special offer design, {product_name}, countdown urgency element, flash sale graphic, high contrast colors, mobile-optimized, conversion-focused typography",
                    "platform": "各平台通用",
                    "conversion": 4.2
                }
            ]
        }

    def search(self, category: str = None, keyword: str = None,
               sort: str = "conversion", limit: int = 10) -> list:
        """
        搜索电商提示词

        Args:
            category: 分类 (product_main/ad_banner/detail_page/seeding/comparison/price_tag)
            keyword: 关键词搜索
            sort: 排序方式 (conversion/random)
            limit: 返回数量
        """
        results = self.data.get("prompts", [])

        if category:
            results = [p for p in results if p.get("category") == category]

        if keyword:
            keyword_lower = keyword.lower()
            results = [p for p in results
                       if keyword_lower in p.get("name", "").lower()
                       or keyword_lower in p.get("prompt", "").lower()]

        if sort == "conversion":
            results.sort(key=lambda x: x.get("conversion", 0), reverse=True)
        elif sort == "random":
            random.shuffle(results)

        return results[:limit]

    def recommend(self, platform: str = None, purpose: str = None) -> list:
        """
        根据平台和用途推荐提示词

        Args:
            platform: 平台 (淘宝/天猫/京东/小红书/抖音/亚马逊)
            purpose: 用途 (销售/品牌/种草/促销)
        """
        mapping = {
            "淘宝": {"categories": ["product_main", "ad_banner", "price_tag"], "sort": "conversion"},
            "天猫": {"categories": ["product_main", "ad_banner", "detail_page"], "sort": "conversion"},
            "京东": {"categories": ["product_main", "detail_page", "comparison"], "sort": "conversion"},
            "小红书": {"categories": ["seeding", "detail_page"], "sort": "conversion"},
            "抖音": {"categories": ["seeding", "ad_banner", "price_tag"], "sort": "conversion"},
            "亚马逊": {"categories": ["product_main", "comparison", "detail_page"], "sort": "conversion"}
        }

        config = mapping.get(platform, mapping["天猫"])
        results = []
        for cat in config["categories"]:
            results.extend(self.search(category=cat, sort=config["sort"], limit=3))

        return results[:6] if purpose else results[:3]


# 提示词模板变量说明
TEMPLATE_VARS = """
📝 模板变量说明:
- {product_name} - 产品名称
- {scene} - 使用场景 (厨房/卧室/办公室/户外等)
- {mood} - 氛围 (温馨/活力/简约/奢华)
- {angle} - 视角 (front/side/45度)
- {feature} - 产品特性
- {headline} - 广告语
- {props} - 搭配道具
- {color_palette} - 配色方案
- {brand} - 品牌调性
- {discount} - 折扣力度
"""


def main():
    parser = argparse.ArgumentParser(description="电商场景GPT-Image-2提示词查询")
    parser.add_argument("--category", "-c",
                        choices=list(EcommercePromptLibrary.CATEGORIES.keys()),
                        help="分类筛选")
    parser.add_argument("--keyword", "-k", help="关键词搜索")
    parser.add_argument("--platform", "-p",
                        help="平台推荐 (淘宝/天猫/京东/小红书/抖音/亚马逊)")
    parser.add_argument("--purpose", help="用途 (销售/品牌/种草/促销)")
    parser.add_argument("--sort", choices=["conversion", "random"], default="conversion")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--export", choices=["json", "markdown"])
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--vars", action="store_true", help="显示模板变量说明")

    args = parser.parse_args()

    lib = EcommercePromptLibrary()

    if args.vars:
        print(TEMPLATE_VARS)
        return

    if args.platform:
        results = lib.recommend(platform=args.platform, purpose=args.purpose)
    else:
        results = lib.search(category=args.category, keyword=args.keyword,
                             sort=args.sort, limit=args.limit)

    # 输出格式
    if args.export == "json":
        output = json.dumps(results, ensure_ascii=False, indent=2)
    elif args.export == "markdown":
        lines = ["# 电商场景GPT-Image-2提示词库\n"]
        for i, p in enumerate(results, 1):
            cat_name = EcommercePromptLibrary.CATEGORIES.get(p["category"], p["category"])
            lines.append(f"## {i}. [{cat_name}] {p['name']}")
            lines.append(f"**平台**: {p['platform']} | **转化率评分**: {p['conversion']}/5.0")
            lines.append(f"\n```\n{p['prompt']}\n```\n")
        output = "\n".join(lines)
    else:
        lines = [f"🛒 电商场景提示词库 (找到{len(results)}条)\n"]
        if args.platform:
            lines[0] = f"🛒 {args.platform}平台推荐提示词 (找到{len(results)}条)\n"
        lines.append("-" * 50)
        for i, p in enumerate(results, 1):
            cat_name = EcommercePromptLibrary.CATEGORIES.get(p["category"], p["category"])
            lines.append(f"\n{i}. [{cat_name}] {p['name']}")
            lines.append(f"   📊 转化率: {p['conversion']}/5.0 | 平台: {p['platform']}")
            lines.append(f"   💬 {p['prompt'][:60]}...")
        lines.append("\n" + "-" * 50)
        lines.append(TEMPLATE_VARS)
        output = "\n".join(lines)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"✅ 已导出到 {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
