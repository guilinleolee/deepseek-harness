"""
VoxCPM2 能力查询 · 30 语种 + 9 方言 + 5 维音色设计 + 6 部署栈
天龙引擎集成版 V1.0

用法:
    from query import query_capabilities, get_language_matrix
"""

import json
from pathlib import Path
from voxcpm import (
    LANGUAGES, DIALECTS, MODES, BACKENDS,
    VOICE_DESIGN_DIMENSIONS, VOICE_DESIGN_TEMPLATES,
    get_language_name, get_dialect_name
)


def query_capabilities(category: str = None, lang: str = None) -> dict:
    """
    查询能力

    category: languages | dialects | modes | backends | voice_design | all
    lang: 语言代码（用于返回音色模板）
    """
    if category == "languages" or category == "all":
        result = {
            "category": "languages",
            "count": len(LANGUAGES),
            "languages": [
                {"code": code, "name": get_language_name(code)}
                for code in LANGUAGES
            ],
        }
        if category == "languages":
            return result

    if category == "dialects" or category == "all":
        result = {
            "category": "dialects",
            "count": len(DIALECTS),
            "dialects": [
                {"code": code, "name": get_dialect_name(code)}
                for code in DIALECTS
            ],
        }
        if category == "dialects":
            return result

    if category == "modes" or category == "all":
        result = {
            "category": "modes",
            "count": len(MODES),
            "modes": MODES,
        }
        if category == "modes":
            return result

    if category == "backends" or category == "all":
        result = {
            "category": "backends",
            "count": len(BACKENDS),
            "backends": BACKENDS,
        }
        if category == "backends":
            return result

    if category == "voice_design" or category == "all":
        result = {
            "category": "voice_design",
            "dimensions": VOICE_DESIGN_DIMENSIONS,
            "templates": VOICE_DESIGN_TEMPLATES,
        }
        if category == "voice_design":
            return result

    if category == "all":
        return {
            "languages": {
                "count": len(LANGUAGES),
                "languages": [
                    {"code": code, "name": get_language_name(code)}
                    for code in LANGUAGES
                ],
            },
            "dialects": {
                "count": len(DIALECTS),
                "dialects": [
                    {"code": code, "name": get_dialect_name(code)}
                    for code in DIALECTS
                ],
            },
            "modes": MODES,
            "backends": BACKENDS,
            "voice_design": {
                "dimensions": VOICE_DESIGN_DIMENSIONS,
                "templates": VOICE_DESIGN_TEMPLATES,
            },
        }

    # 默认返回 summary
    return {
        "summary": {
            "languages": len(LANGUAGES),
            "dialects": len(DIALECTS),
            "modes": len(MODES),
            "backends": len(BACKENDS),
            "voice_design_dimensions": len(VOICE_DESIGN_DIMENSIONS),
            "voice_design_templates": len(VOICE_DESIGN_TEMPLATES),
        }
    }


def get_language_matrix() -> dict:
    """返回 30 语言 × 9 方言矩阵"""
    return {
        "languages": [
            {"code": code, "name": get_language_name(code)}
            for code in LANGUAGES
        ],
        "dialects": [
            {"code": code, "name": get_dialect_name(code)}
            for code in DIALECTS
        ],
        "total_locales": len(LANGUAGES) + len(DIALECTS),
    }


def get_voice_design_template(emotion: str = None, gender: str = None) -> list:
    """根据情绪/性别筛选音色设计模板"""
    results = []
    for template in VOICE_DESIGN_TEMPLATES:
        if emotion and emotion not in template:
            continue
        if gender and gender not in template:
            continue
        results.append(template)
    return results


def main():
    """CLI 入口"""
    import argparse
    parser = argparse.ArgumentParser(description="VoxCPM2 能力查询")
    parser.add_argument(
        "--category",
        default="all",
        choices=["all", "languages", "dialects", "modes", "backends", "voice_design"],
        help="查询类别",
    )
    parser.add_argument("--emotion", help="按情绪筛选音色模板")
    parser.add_argument("--gender", help="按性别筛选音色模板")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    if args.emotion or args.gender:
        templates = get_voice_design_template(args.emotion, args.gender)
        if args.json:
            print(json.dumps({"templates": templates}, ensure_ascii=False, indent=2))
        else:
            print(f"\n🎨 音色模板（emotion={args.emotion}, gender={args.gender}）:")
            for t in templates:
                print(f"  - {t}")
        return

    result = query_capabilities(args.category)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n📊 VoxCPM2 能力 ({args.category}):")
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()