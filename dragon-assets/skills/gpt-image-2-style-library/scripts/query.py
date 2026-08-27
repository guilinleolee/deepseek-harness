"""
天龙引擎 V2.0 · gpt-image-2-style-library query.py
==================================================
查询 awesome-gpt-image-2 的 21 套工业模板。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# UTF-8 stdout
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

DEFAULT_REF = Path(__file__).parent.parent / "references" / "style-library.md"


def parse_reference(ref_path: Path) -> List[Dict]:
    """从 references/style-library.md 解析模板"""
    if not ref_path.exists():
        print(f"❌ Reference 不存在: {ref_path}")
        return []

    text = ref_path.read_text(encoding="utf-8", errors="replace")
    templates: List[Dict] = []
    current: Optional[Dict] = None

    for line in text.splitlines():
        if line.startswith("### "):
            if current:
                templates.append(current)
            current = {
                "name": line[4:].strip(),
                "id": "",
                "category": "",
                "styles": [],
                "scenes": [],
                "tags": [],
                "use_when": [],
                "guidance": [],
                "pitfalls": [],
                "example_cases": [],
            }
        elif current is not None:
            line_s = line.strip()
            if line_s.startswith("- ID:"):
                current["id"] = line_s.split(":", 1)[1].strip().strip("`")
            elif line_s.startswith("- Category:"):
                current["category"] = line_s.split(":", 1)[1].strip()
            elif line_s.startswith("- Styles:"):
                current["styles"] = [s.strip() for s in line_s.split(":", 1)[1].split(",")]
            elif line_s.startswith("- Scenes:"):
                current["scenes"] = [s.strip() for s in line_s.split(":", 1)[1].split(",")]
            elif line_s.startswith("- Tags:"):
                current["tags"] = [s.strip() for s in line_s.split(":", 1)[1].split(",")]
            elif line_s.startswith("- Example cases:"):
                ids = re.findall(r"\d+", line_s)
                current["example_cases"] = [int(i) for i in ids]
            elif line_s.startswith("- "):
                current["use_when"].append(line_s[2:])
            elif line_s.startswith("  - "):
                current["guidance" if "Guidance" in str(current.get("_section", "")) else "pitfalls"].append(line_s[4:])

    if current:
        templates.append(current)
    return templates


def search_templates(
    templates: List[Dict],
    category: Optional[str] = None,
    style: Optional[str] = None,
    scene: Optional[str] = None,
    keyword: Optional[str] = None,
) -> List[Dict]:
    results = []
    for t in templates:
        if category and category.lower() not in t["category"].lower():
            continue
        if style and not any(style.lower() in s.lower() for s in t["styles"]):
            continue
        if scene and not any(scene.lower() in s.lower() for s in t["scenes"]):
            continue
        if keyword and keyword.lower() not in t["name"].lower():
            continue
        results.append(t)
    return results


def main():
    parser = argparse.ArgumentParser(description="查询 GPT-Image2 工业模板")
    parser.add_argument("--category", help="类目过滤 (UI / Poster / Infographic / Brand / Character ...)")
    parser.add_argument("--style", help="风格标签 (UI / Realistic / Illustration ...)")
    parser.add_argument("--scene", help="场景标签 (Social / Commerce / Education ...)")
    parser.add_argument("--keyword", "-k", help="关键词搜索")
    parser.add_argument("--list", action="store_true", help="列出所有模板")
    parser.add_argument("--case", type=int, help="按案例 ID 查找")
    parser.add_argument("--export", choices=["json", "md"], help="导出格式")
    parser.add_argument("--output", "-o", help="输出文件")
    parser.add_argument("--limit", type=int, default=20, help="最大返回数")
    parser.add_argument("--ref", default=str(DEFAULT_REF), help="Reference 文件路径")

    args = parser.parse_args()

    templates = parse_reference(Path(args.ref))
    if not templates:
        sys.exit(1)

    if args.list:
        results = templates
    elif args.case:
        results = [t for t in templates if args.case in t["example_cases"]]
    else:
        results = search_templates(
            templates,
            category=args.category,
            style=args.style,
            scene=args.scene,
            keyword=args.keyword,
        )

    results = results[:args.limit]

    if args.export == "json":
        output = json.dumps(results, ensure_ascii=False, indent=2)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            print(f"✅ 已导出 {len(results)} 个模板到 {args.output}")
        else:
            print(output)
    else:
        print(f"=== {len(results)} 个匹配模板 ===\n")
        for i, t in enumerate(results, 1):
            print(f"{i}. **{t['name']}** (`{t['id']}`)")
            print(f"   类目: {t['category']} | 风格: {', '.join(t['styles'])} | 场景: {', '.join(t['scenes'])}")
            if t["example_cases"]:
                print(f"   案例: {', '.join(f'case {c}' for c in t['example_cases'][:5])}")
            print()


if __name__ == "__main__":
    main()