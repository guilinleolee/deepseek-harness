"""
天龙引擎 V1.0 · gpt-image-2-gallery-explorer query.py
====================================================
检索 awesome-gpt-image-2 案例库（518 案例，12 类目）。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# UTF-8 stdout
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

SKILL_DIR = Path(__file__).parent.parent
GALLERY_DIR = SKILL_DIR / "references" / "gallery"

CATEGORIES = [
    "UI & Interfaces",
    "Charts & Infographics",
    "Posters & Typography",
    "Products & E-commerce",
    "Brand & Logos",
    "Architecture & Spaces",
    "Photography & Realism",
    "Illustration & Art",
    "Characters & People",
    "Scenes & Storytelling",
    "History & Classical",
    "Document & Publication",
]


def parse_gallery_file(path: Path) -> list:
    """解析 gallery markdown 文件，提取案例。

    上游格式示例：
      <a name="case-17"></a>
      ### 例 17：<标题>
      ![image](../data/images/case17.jpg)
      **来源：** ...
      **提示词：**
      ```text
      <prompt>
      ```
    """
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    cases = []

    # 用 anchor + heading 双锚定分割
    pattern = re.compile(
        r'<a name="case-?(\d+)"\s*></a>\s*\n+\s*###\s*例\s*\1[：:]\s*(.+?)(?=\n)',
        re.MULTILINE,
    )

    for match in pattern.finditer(text):
        num = match.group(1)
        title = match.group(2).strip()
        start = match.end()
        next_anchor = re.search(r'<a name="case-?\d+"\s*></a>', text[start:])
        body = text[start:start + next_anchor.start()] if next_anchor else text[start:]

        case = {"id": f"case-{num}", "num": int(num), "title": title}

        # 图片
        img = re.search(r'!\[.*?\]\(\.\./data/images/(case\d+\.\w+)\)', body)
        if img:
            case["image_url"] = f"/images/{img.group(1)}"

        # 来源
        src = re.search(r'\*\*来源[：:]\*\*\s*(.+?)(?=\n)', body)
        if src:
            case["source"] = src.group(1).strip()

        # 提示词（在 ```text 代码块中）
        prompt_m = re.search(r'\*\*提示词[：:]\*\*\s*```text\s*\n(.*?)\n```', body, re.DOTALL)
        if prompt_m:
            case["prompt"] = prompt_m.group(1).strip()
            pt = case["prompt"].lower()
            if any(kw in pt for kw in ["app screenshot", "ui ", "dashboard", "界面", "mockup"]):
                case["category"] = "UI & Interfaces"
            elif any(kw in pt for kw in ["infographic", "信息图", "chart", "diagram", "图解"]):
                case["category"] = "Charts & Infographics"
            elif any(kw in pt for kw in ["poster", "海报", "campaign", "typography"]):
                case["category"] = "Posters & Typography"
            elif any(kw in pt for kw in ["product", "电商", "商品", "e-commerce", "shopping"]):
                case["category"] = "Products & E-commerce"
            elif any(kw in pt for kw in ["logo", "brand", "品牌", "标志"]):
                case["category"] = "Brand & Logos"
            elif any(kw in pt for kw in ["architecture", "建筑", "interior", "室内"]):
                case["category"] = "Architecture & Spaces"
            elif any(kw in pt for kw in ["portrait", "photography", "fujifilm", "肖像", "摄影"]):
                case["category"] = "Photography & Realism"
            elif any(kw in pt for kw in ["illustration", "插画", "art style"]):
                case["category"] = "Illustration & Art"
            elif any(kw in pt for kw in ["character", "anime", "角色", "二次元", "toy"]):
                case["category"] = "Characters & People"
            elif any(kw in pt for kw in ["scene", "story", "场景", "直播"]):
                case["category"] = "Scenes & Storytelling"
            elif any(kw in pt for kw in ["history", "classical", "古风", "历史"]):
                case["category"] = "History & Classical"
            elif any(kw in pt for kw in ["document", "ocr", "文档", "publication"]):
                case["category"] = "Document & Publication"

        cases.append(case)
    return cases


def load_all_cases() -> list:
    """加载所有 gallery 文件的案例。"""
    all_cases = []
    for fname in ("gallery.md", "gallery-part-1.md", "gallery-part-2.md"):
        path = GALLERY_DIR / fname
        all_cases.extend(parse_gallery_file(path))
    return all_cases


def search(cases, category=None, keyword=None, style=None, scene=None, case_id=None, limit=10, random_mode=False):
    """多维检索"""
    import random as _r

    results = cases
    if case_id:
        results = [c for c in results if c["id"] == case_id or c["id"] == f"case-{case_id}"]
    if category:
        results = [c for c in results if c.get("category", "").lower() == category.lower()]
    if style:
        results = [c for c in results if any(style.lower() in s.lower() for s in c.get("styles", []))]
    if scene:
        results = [c for c in results if any(scene.lower() in s.lower() for s in c.get("scenes", []))]
    if keyword:
        kw = keyword.lower()
        results = [
            c for c in results
            if kw in c.get("title", "").lower()
            or kw in c.get("prompt", "").lower()
            or kw in c.get("category", "").lower()
            or any(kw in t.lower() for t in c.get("tags", []))
        ]
    if random_mode:
        _r.shuffle(results)
    return results[:limit]


def main():
    parser = argparse.ArgumentParser(description="检索 awesome-gpt-image-2 案例库")
    parser.add_argument("--category", help="类目（模糊匹配）")
    parser.add_argument("--keyword", help="关键词搜索")
    parser.add_argument("--style", help="风格标签")
    parser.add_argument("--scene", help="场景标签")
    parser.add_argument("--case", help="按案例 ID 查")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--random", type=int, help="随机 N 条")
    parser.add_argument("--stats", action="store_true", help="类目统计")
    parser.add_argument("--export", choices=["json", "md"], help="导出格式")
    parser.add_argument("--output", help="输出文件")

    args = parser.parse_args()

    cases = load_all_cases()

    if args.stats:
        from collections import Counter
        cats = Counter(c.get("category", "Unknown") for c in cases)
        print(f"📊 总计 {len(cases)} 个案例\n")
        for cat, n in cats.most_common():
            bar = "█" * min(50, n)
            print(f"  {cat:<30} {n:>4} {bar}")
        return

    results = search(
        cases,
        category=args.category,
        keyword=args.keyword,
        style=args.style,
        scene=args.scene,
        case_id=args.case,
        limit=args.limit,
        random_mode=bool(args.random),
    )

    if args.export == "json":
        import json as _json
        output = _json.dumps(results, ensure_ascii=False, indent=2)
    elif args.export == "md":
        lines = [f"# GPT-Image-2 案例库（{len(results)} 条）\n"]
        for c in results:
            lines.append(f"## {c['id']} — {c.get('title', '')}")
            lines.append(f"- **类目**: {c.get('category', '-')}")
            lines.append(f"- **风格**: {', '.join(c.get('styles', []))}")
            lines.append(f"- **场景**: {', '.join(c.get('scenes', []))}")
            lines.append(f"- **图片**: {c.get('image_url', '-')}")
            lines.append(f"\n```\n{c.get('prompt', '-')[:500]}\n```\n")
        output = "\n".join(lines)
    else:
        lines = [f"🔍 案例库检索（{len(results)} 条匹配）\n"]
        for c in results:
            lines.append(f"\n📌 **{c['id']}** — {c.get('title', '(无标题)')}")
            lines.append(f"   类目: {c.get('category', '-')} | 风格: {', '.join(c.get('styles', []))} | 场景: {', '.join(c.get('scenes', []))}")
            lines.append(f"   图片: {c.get('image_url', '-')}")
        output = "\n".join(lines)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"✅ 已导出到 {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()