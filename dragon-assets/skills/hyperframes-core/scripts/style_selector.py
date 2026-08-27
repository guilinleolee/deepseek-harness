#!/usr/bin/env python3
"""
Hyperframes Visual Style Selector
Recommends the most appropriate visual style based on content characteristics.

Usage:
    from style_selector import StyleSelector
    selector = StyleSelector()
    result = selector.recommend(content_type="data_presentation", industry="saas")
    print(result.style)       # VisualStyle.SWISS_PULSE
    print(result.reason)      # Human-readable reason

    # Quick function
    from style_selector import quick_recommend
    style = quick_recommend("科技发布会")
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any


class VisualStyle(Enum):
    """8 Hyperframes visual styles"""
    SWISS_PULSE = "swiss-pulse"
    VELVET_STANDARD = "velvet-standard"
    DECONSTRUCTED = "deconstructed"
    MAXIMALIST_TYPE = "maximalist-type"
    DATA_DRIFT = "data-drift"
    SOFT_SIGNAL = "soft-signal"
    FOLK_FREQUENCY = "folk-frequency"
    SHADOW_CUT = "shadow-cut"


@dataclass
class StyleRecommendation:
    """Result of style recommendation"""
    style: VisualStyle
    confidence: float  # 0.0-1.0
    reason: str
    alternatives: List[VisualStyle]
    shader_transition: str
    easing: str
    keywords: List[str]


@dataclass
class ContentProfile:
    """Content profile for style matching"""
    content_type: str
    industry: str
    mood: str
    target_audience: str
    keywords: List[str]


class StyleSelector:
    """
    Recommends visual styles based on content characteristics.

    Decision Tree:
        内容类型 → 推荐风格
        ├── 数据/开发工具 → Swiss Pulse
        ├── 高端/奢侈品 → Velvet Standard
        ├── 科技/安全 → Deconstructed
        ├── 大事件/促销 → Maximalist Type
        ├── AI/未来 → Data Drift
        ├── 健康/个人 → Soft Signal
        ├── 消费/美食 → Folk Frequency
        └── 戏剧/神秘 → Shadow Cut
    """

    # Content type → style mapping
    CONTENT_STYLE_MAP: Dict[str, VisualStyle] = {
        # Data & Development
        "data_presentation": VisualStyle.SWISS_PULSE,
        "dashboard": VisualStyle.SWISS_PULSE,
        "analytics": VisualStyle.SWISS_PULSE,
        "developer_tools": VisualStyle.SWISS_PULSE,
        "saas": VisualStyle.SWISS_PULSE,
        "fintech": VisualStyle.SWISS_PULSE,
        "b2b": VisualStyle.SWISS_PULSE,
        "technical": VisualStyle.SWISS_PULSE,
        "api_docs": VisualStyle.SWISS_PULSE,
        "metrics": VisualStyle.SWISS_PULSE,
        "reports": VisualStyle.SWISS_PULSE,

        # Luxury & Premium
        "luxury": VisualStyle.VELVET_STANDARD,
        "fashion": VisualStyle.VELVET_STANDARD,
        "jewelry": VisualStyle.VELVET_STANDARD,
        "automotive": VisualStyle.VELVET_STANDARD,
        "high_end": VisualStyle.VELVET_STANDARD,
        "watches": VisualStyle.VELVET_STANDARD,
        "perfume": VisualStyle.VELVET_STANDARD,
        "real_estate": VisualStyle.VELVET_STANDARD,
        "premium": VisualStyle.VELVET_STANDARD,

        # Tech & Security
        "tech": VisualStyle.DECONSTRUCTED,
        "cybersecurity": VisualStyle.DECONSTRUCTED,
        "developer": VisualStyle.DECONSTRUCTED,
        "blockchain": VisualStyle.DECONSTRUCTED,
        "ai_security": VisualStyle.DECONSTRUCTED,
        "open_source": VisualStyle.DECONSTRUCTED,
        "hacking": VisualStyle.DECONSTRUCTED,

        # Big Events & Promotions
        "promotion": VisualStyle.MAXIMALIST_TYPE,
        "flash_sale": VisualStyle.MAXIMALIST_TYPE,
        "black_friday": VisualStyle.MAXIMALIST_TYPE,
        "concert": VisualStyle.MAXIMALIST_TYPE,
        "sports": VisualStyle.MAXIMALIST_TYPE,
        "festival": VisualStyle.MAXIMALIST_TYPE,
        "big_event": VisualStyle.MAXIMALIST_TYPE,
        "holiday": VisualStyle.MAXIMALIST_TYPE,
        "announcement": VisualStyle.MAXIMALIST_TYPE,

        # AI & Future
        "ai": VisualStyle.DATA_DRIFT,
        "futuristic": VisualStyle.DATA_DRIFT,
        "ml": VisualStyle.DATA_DRIFT,
        "robotics": VisualStyle.DATA_DRIFT,
        "space": VisualStyle.DATA_DRIFT,
        "metaverse": VisualStyle.DATA_DRIFT,
        "gaming": VisualStyle.DATA_DRIFT,
        "esports": VisualStyle.DATA_DRIFT,
        "deep_tech": VisualStyle.DATA_DRIFT,

        # Health & Personal
        "health": VisualStyle.SOFT_SIGNAL,
        "wellness": VisualStyle.SOFT_SIGNAL,
        "fitness": VisualStyle.SOFT_SIGNAL,
        "beauty": VisualStyle.SOFT_SIGNAL,
        "skincare": VisualStyle.SOFT_SIGNAL,
        "meditation": VisualStyle.SOFT_SIGNAL,
        "mental_health": VisualStyle.SOFT_SIGNAL,
        "personal": VisualStyle.SOFT_SIGNAL,
        "lifestyle": VisualStyle.SOFT_SIGNAL,

        # Consumer & Food
        "food": VisualStyle.FOLK_FREQUENCY,
        "restaurant": VisualStyle.FOLK_FREQUENCY,
        "recipe": VisualStyle.FOLK_FREQUENCY,
        "coffee": VisualStyle.FOLK_FREQUENCY,
        "consumer": VisualStyle.FOLK_FREQUENCY,
        "retail": VisualStyle.FOLK_FREQUENCY,
        "fashion_casual": VisualStyle.FOLK_FREQUENCY,
        "craft": VisualStyle.FOLK_FREQUENCY,
        "handmade": VisualStyle.FOLK_FREQUENCY,

        # Dramatic & Mystery
        "dramatic": VisualStyle.SHADOW_CUT,
        "movie": VisualStyle.SHADOW_CUT,
        "series": VisualStyle.SHADOW_CUT,
        "mystery": VisualStyle.SHADOW_CUT,
        "thriller": VisualStyle.SHADOW_CUT,
        "horror": VisualStyle.SHADOW_CUT,
        "documentary": VisualStyle.SHADOW_CUT,
        "story": VisualStyle.SHADOW_CUT,
        "narrative": VisualStyle.SHADOW_CUT,
    }

    # Style metadata
    STYLE_METADATA: Dict[VisualStyle, Dict[str, Any]] = {
        VisualStyle.SWISS_PULSE: {
            "shader": "cinematic-zoom",
            "easing": "expo.out",
            "keywords": ["clean", "minimal", "professional", "data", "modern"],
            "description": "Clean geometry, high contrast, perfect for data/dev tools",
        },
        VisualStyle.VELVET_STANDARD: {
            "shader": "cross-warp-morph",
            "easing": "sine.inOut",
            "keywords": ["luxury", "elegant", "premium", "gold", "serif"],
            "description": "Dark backgrounds with gold accents, serif typography",
        },
        VisualStyle.DECONSTRUCTED: {
            "shader": "glitch",
            "easing": "back.out(2.5)",
            "keywords": ["glitch", "tech", "security", "pixelated", "futuristic"],
            "description": "Glitch art, deconstructed elements, tech aesthetic",
        },
        VisualStyle.MAXIMALIST_TYPE: {
            "shader": "ridged-burn",
            "easing": "expo.out",
            "keywords": ["bold", "loud", "impact", "big", "vivid"],
            "description": "200px+ fonts, vivid colors, maximum impact",
        },
        VisualStyle.DATA_DRIFT: {
            "shader": "gravitational-lens",
            "easing": "sine.inOut",
            "keywords": ["dark", "neon", "cyber", "ai", "futuristic", "grid"],
            "description": "Dark backgrounds with neon cyan, grid/particle effects",
        },
        VisualStyle.SOFT_SIGNAL: {
            "shader": "thermal-distortion",
            "easing": "sine.inOut",
            "keywords": ["soft", "pastel", "rounded", "gentle", "calm"],
            "description": "Soft pastels, rounded shapes, wellness aesthetic",
        },
        VisualStyle.FOLK_FREQUENCY: {
            "shader": "swirl-vortex",
            "easing": "back.out(1.6)",
            "keywords": ["folk", "craft", "warm", "earthy", "authentic"],
            "description": "Folk colors, hand-drawn aesthetic, authentic warmth",
        },
        VisualStyle.SHADOW_CUT: {
            "shader": "domain-warp",
            "easing": "power4.in",
            "keywords": ["dramatic", "dark", "spotlight", "theatrical", "mystery"],
            "description": "Deep black, dramatic spotlight, theatrical lighting",
        },
    }

    # Industry style preferences (overrides for specific industries)
    INDUSTRY_OVERRIDES: Dict[str, VisualStyle] = {
        "luxury_fashion": VisualStyle.VELVET_STANDARD,
        "watch_jewelry": VisualStyle.VELVET_STANDARD,
        "automotive": VisualStyle.VELVET_STANDARD,
        "real_estate": VisualStyle.VELVET_STANDARD,
        "saas": VisualStyle.SWISS_PULSE,
        "fintech": VisualStyle.SWISS_PULSE,
        "healthcare": VisualStyle.SOFT_SIGNAL,
        "fitness": VisualStyle.SOFT_SIGNAL,
        "food_beverage": VisualStyle.FOLK_FREQUENCY,
        "restaurant": VisualStyle.FOLK_FREQUENCY,
        "ai_tech": VisualStyle.DATA_DRIFT,
        "cybersecurity": VisualStyle.DECONSTRUCTED,
        "gaming": VisualStyle.DATA_DRIFT,
        "entertainment": VisualStyle.MAXIMALIST_TYPE,
        "retail": VisualStyle.FOLK_FREQUENCY,
    }

    def recommend(
        self,
        content_type: Optional[str] = None,
        industry: Optional[str] = None,
        mood: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        platform: Optional[str] = None,
    ) -> StyleRecommendation:
        """
        Recommend a visual style based on content characteristics.

        Args:
            content_type: Type of content (e.g., "data_presentation", "luxury", "tech")
            industry: Industry vertical (e.g., "saas", "healthcare", "food")
            mood: Desired mood (e.g., "professional", "playful", "dramatic")
            keywords: List of content keywords
            platform: Target platform (e.g., "tiktok", "youtube", "linkedin")

        Returns:
            StyleRecommendation with style, confidence, and metadata
        """
        keywords = keywords or []
        all_text = " ".join([
            content_type or "",
            industry or "",
            mood or "",
            " ".join(keywords),
        ]).lower()

        # Step 1: Check for industry-specific overrides
        if industry:
            industry_lower = industry.lower().replace(" ", "_")
            for key, style in self.INDUSTRY_OVERRIDES.items():
                if key in industry_lower or industry_lower in key:
                    return self._build_recommendation(
                        style=style,
                        confidence=0.95,
                        reason=f"Industry override: {industry} → {style.value}",
                        keywords=keywords,
                    )

        # Step 2: Match content type
        if content_type:
            content_lower = content_type.lower().replace(" ", "_")
            for key, style in self.CONTENT_STYLE_MAP.items():
                if key in content_lower or content_lower in key:
                    return self._build_recommendation(
                        style=style,
                        confidence=0.85,
                        reason=f"Content type match: {content_type} → {style.value}",
                        keywords=keywords,
                    )

        # Step 3: Keyword matching
        style_scores = {style: 0 for style in VisualStyle}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            for style, meta in self.STYLE_METADATA.items():
                for kw in meta["keywords"]:
                    if kw in keyword_lower or keyword_lower in kw:
                        style_scores[style] += 1

        # Check for mood keywords
        mood_patterns = {
            "dramatic": VisualStyle.SHADOW_CUT,
            "futuristic": VisualStyle.DATA_DRIFT,
            "luxurious": VisualStyle.VELVET_STANDARD,
            "playful": VisualStyle.FOLK_FREQUENCY,
            "minimal": VisualStyle.SWISS_PULSE,
            "bold": VisualStyle.MAXIMALIST_TYPE,
            "tech": VisualStyle.DECONSTRUCTED,
            "soft": VisualStyle.SOFT_SIGNAL,
            "clean": VisualStyle.SWISS_PULSE,
        }
        for mood_word, style in mood_patterns.items():
            if mood_word in all_text:
                style_scores[style] += 2

        # Find best match
        if max(style_scores.values()) > 0:
            best_style = max(style_scores, key=style_scores.get)
            best_score = style_scores[best_style]
            confidence = min(0.7 + (best_score * 0.05), 0.85)
            return self._build_recommendation(
                style=best_style,
                confidence=confidence,
                reason=f"Keyword analysis: matched {best_style.value}",
                keywords=keywords,
            )

        # Step 4: Platform-based defaults
        if platform:
            platform_defaults = {
                "tiktok": VisualStyle.DATA_DRIFT,
                "douyin": VisualStyle.MAXIMALIST_TYPE,
                "youtube": VisualStyle.SWISS_PULSE,
                "linkedin": VisualStyle.SWISS_PULSE,
                "instagram": VisualStyle.VELVET_STANDARD,
                "wechat": VisualStyle.SWISS_PULSE,
            }
            for pf, style in platform_defaults.items():
                if pf in platform.lower():
                    return self._build_recommendation(
                        style=style,
                        confidence=0.6,
                        reason=f"Platform default: {platform} → {style.value}",
                        keywords=keywords,
                    )

        # Default: Swiss Pulse
        return self._build_recommendation(
            style=VisualStyle.SWISS_PULSE,
            confidence=0.5,
            reason="Default: no specific match found, using Swiss Pulse",
            keywords=keywords,
        )

    def _build_recommendation(
        self,
        style: VisualStyle,
        confidence: float,
        reason: str,
        keywords: List[str],
    ) -> StyleRecommendation:
        """Build a StyleRecommendation with alternatives"""
        meta = self.STYLE_METADATA[style]

        # Generate alternatives (styles with different characteristics)
        alternatives = [s for s in VisualStyle if s != style][:2]

        return StyleRecommendation(
            style=style,
            confidence=confidence,
            reason=reason,
            alternatives=alternatives,
            shader_transition=meta["shader"],
            easing=meta["easing"],
            keywords=keywords + meta["keywords"],
        )

    def list_styles(self) -> List[str]:
        """List all available visual styles"""
        return [s.value for s in VisualStyle]

    def get_style_info(self, style: VisualStyle) -> Dict[str, Any]:
        """Get detailed information about a style"""
        meta = self.STYLE_METADATA.get(style, {})
        return {
            "name": style.value,
            "shader_transition": meta.get("shader", "unknown"),
            "easing": meta.get("easing", "unknown"),
            "keywords": meta.get("keywords", []),
            "description": meta.get("description", ""),
        }

    def compare_styles(
        self,
        styles: List[VisualStyle],
    ) -> Dict[VisualStyle, Dict[str, Any]]:
        """Compare multiple styles and return their metadata"""
        return {style: self.get_style_info(style) for style in styles}


def quick_recommend(content_description: str) -> VisualStyle:
    """
    Quick one-liner style recommendation.

    Usage:
        style = quick_recommend("数据仪表盘SaaS产品")
        style = quick_recommend("AI科技发布会")
        style = quick_recommend("高级腕表品牌")
    """
    selector = StyleSelector()

    # Parse common Chinese patterns
    chinese_patterns = {
        "数据": VisualStyle.SWISS_PULSE,
        "开发": VisualStyle.SWISS_PULSE,
        "工具": VisualStyle.SWISS_PULSE,
        "科技": VisualStyle.DATA_DRIFT,
        "AI": VisualStyle.DATA_DRIFT,
        "未来": VisualStyle.DATA_DRIFT,
        "奢侈": VisualStyle.VELVET_STANDARD,
        "高端": VisualStyle.VELVET_STANDARD,
        "时尚": VisualStyle.VELVET_STANDARD,
        "美食": VisualStyle.FOLK_FREQUENCY,
        "餐饮": VisualStyle.FOLK_FREQUENCY,
        "咖啡": VisualStyle.FOLK_FREQUENCY,
        "健康": VisualStyle.SOFT_SIGNAL,
        "健身": VisualStyle.SOFT_SIGNAL,
        "美妆": VisualStyle.SOFT_SIGNAL,
        "促销": VisualStyle.MAXIMALIST_TYPE,
        "大促": VisualStyle.MAXIMALIST_TYPE,
        "节日": VisualStyle.MAXIMALIST_TYPE,
        "发布": VisualStyle.DECONSTRUCTED,
        "安全": VisualStyle.DECONSTRUCTED,
        "悬疑": VisualStyle.SHADOW_CUT,
        "戏剧": VisualStyle.SHADOW_CUT,
        "电影": VisualStyle.SHADOW_CUT,
    }

    content_lower = content_description.lower()
    for pattern, style in chinese_patterns.items():
        if pattern in content_lower:
            return style

    # Fallback to English keyword parsing
    result = selector.recommend(keywords=content_description.split())
    return result.style


def get_style_presets() -> Dict[str, Dict[str, Any]]:
    """
    Get preset configurations for common use cases.

    Returns:
        Dictionary of preset name → {style, props, transitions}
    """
    presets = {
        "social_media_quick": {
            "style": VisualStyle.DATA_DRIFT,
            "fps": 30,
            "duration": 15,
            "platform": "tiktok",
        },
        "product_showcase": {
            "style": VisualStyle.VELVET_STANDARD,
            "fps": 24,
            "duration": 30,
            "platform": "instagram",
        },
        "data_dashboard": {
            "style": VisualStyle.SWISS_PULSE,
            "fps": 30,
            "duration": 20,
            "platform": "youtube",
        },
        "flash_sale": {
            "style": VisualStyle.MAXIMALIST_TYPE,
            "fps": 30,
            "duration": 10,
            "platform": "tiktok",
        },
        "tech_demo": {
            "style": VisualStyle.DECONSTRUCTED,
            "fps": 30,
            "duration": 45,
            "platform": "youtube",
        },
        "health_wellness": {
            "style": VisualStyle.SOFT_SIGNAL,
            "fps": 24,
            "duration": 30,
            "platform": "instagram",
        },
        "food_content": {
            "style": VisualStyle.FOLK_FREQUENCY,
            "fps": 24,
            "duration": 20,
            "platform": "tiktok",
        },
        "dramatic_story": {
            "style": VisualStyle.SHADOW_CUT,
            "fps": 24,
            "duration": 60,
            "platform": "youtube",
        },
    }
    return presets


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Hyperframes Visual Style Selector")
    subparsers = parser.add_subparsers(dest="command")

    # Recommend command
    rec_parser = subparsers.add_parser("recommend", help="Recommend a style")
    rec_parser.add_argument("--content", "-c", help="Content type")
    rec_parser.add_argument("--industry", "-i", help="Industry")
    rec_parser.add_argument("--mood", "-m", help="Desired mood")
    rec_parser.add_argument("--keywords", "-k", nargs="+", help="Keywords")
    rec_parser.add_argument("--platform", "-p", help="Target platform")
    rec_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # List styles command
    subparsers.add_parser("list", help="List all available styles")

    # Style info command
    info_parser = subparsers.add_parser("info", help="Get style information")
    info_parser.add_argument("style", help="Style name (e.g., swiss-pulse)")

    # Quick command
    quick_parser = subparsers.add_parser("quick", help="Quick recommendation")
    quick_parser.add_argument("description", help="Content description")

    # Presets command
    subparsers.add_parser("presets", help="List style presets")

    args = parser.parse_args()

    selector = StyleSelector()

    if args.command == "recommend":
        result = selector.recommend(
            content_type=args.content,
            industry=args.industry,
            mood=args.mood,
            keywords=args.keywords,
            platform=args.platform,
        )

        if args.json:
            print(json.dumps({
                "style": result.style.value,
                "confidence": result.confidence,
                "reason": result.reason,
                "alternatives": [s.value for s in result.alternatives],
                "shader_transition": result.shader_transition,
                "easing": result.easing,
            }, indent=2))
        else:
            print(f"Recommended Style: {result.style.value}")
            print(f"Confidence: {result.confidence:.0%}")
            print(f"Reason: {result.reason}")
            print(f"Shader Transition: {result.shader_transition}")
            print(f"Easing: {result.easing}")
            if result.alternatives:
                print(f"Alternatives: {', '.join(s.value for s in result.alternatives)}")

    elif args.command == "list":
        print("Available Visual Styles:")
        for style in VisualStyle:
            info = selector.get_style_info(style)
            print(f"  - {style.value}")
            print(f"    {info['description']}")

    elif args.command == "info":
        try:
            style = VisualStyle(args.style)
            info = selector.get_style_info(style)
            print(f"Style: {info['name']}")
            print(f"Description: {info['description']}")
            print(f"Shader Transition: {info['shader_transition']}")
            print(f"Easing: {info['easing']}")
            print(f"Keywords: {', '.join(info['keywords'])}")
        except ValueError:
            print(f"Unknown style: {args.style}")
            print(f"Available: {', '.join(s.value for s in VisualStyle)}")

    elif args.command == "quick":
        style = quick_recommend(args.description)
        print(f"Style: {style.value}")

    elif args.command == "presets":
        print("Style Presets:")
        for name, preset in get_style_presets().items():
            print(f"  - {name}")
            print(f"    Style: {preset['style'].value}")
            print(f"    Platform: {preset['platform']}, {preset['fps']}fps, {preset['duration']}s")

    else:
        parser.print_help()
