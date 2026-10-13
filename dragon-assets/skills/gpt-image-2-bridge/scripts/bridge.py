"""天龙引擎 V1.0 · gpt-image-2-bridge/scripts/bridge.py
====================================================

把 gpt-image-2 工业模板 + 544 真实案例自动编排到 4 个下游:
  1. cover_mondo     — qiaomu-mondo-poster-design (海报)
  2. cover_baoyu     — baoyu-cover-image (公众号封面)
  3. illustrations   — smart-illustrator (配图)
  4. storyboard      — seedance2-skill (短视频剧本)

输入（按优先级）:
  --category <name>    按 12 类目之一筛选
  --keyword <text>     按关键词搜索
  --case <id>...       按案例 ID 列表
  --auto-sample        按类目统计 + 抽样

用法:
    python bridge.py --category "Posters & Typography" --count 5 --dry-run
    python bridge.py --keyword "futuristic dashboard" --only cover_baoyu
    python bridge.py --case 17 --case 45
    python bridge.py --auto-sample --per-category 2
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# UTF-8 stdout
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BRIDGE_DIR = Path(__file__).parent.parent
GALLERY_QUERY = BRIDGE_DIR.parent / "gpt-image-2-gallery-explorer" / "scripts" / "query.py"
TEMPLATES_MD = BRIDGE_DIR.parent / "gpt-image-2-style-library" / "references" / "templates.md"

# 12 类目
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

# 类目 → Adapter 路由矩阵（score 0-3）
ROUTING_MATRIX = {
    "UI & Interfaces":            {"cover_mondo": 2, "cover_baoyu": 3, "illustrations": 3, "storyboard": 1},
    "Charts & Infographics":      {"cover_mondo": 1, "cover_baoyu": 2, "illustrations": 3, "storyboard": 1},
    "Posters & Typography":       {"cover_mondo": 3, "cover_baoyu": 3, "illustrations": 2, "storyboard": 2},
    "Products & E-commerce":      {"cover_mondo": 2, "cover_baoyu": 2, "illustrations": 3, "storyboard": 1},
    "Brand & Logos":              {"cover_mondo": 3, "cover_baoyu": 2, "illustrations": 2, "storyboard": 1},
    "Architecture & Spaces":      {"cover_mondo": 2, "cover_baoyu": 1, "illustrations": 3, "storyboard": 2},
    "Photography & Realism":      {"cover_mondo": 2, "cover_baoyu": 2, "illustrations": 3, "storyboard": 2},
    "Illustration & Art":         {"cover_mondo": 3, "cover_baoyu": 2, "illustrations": 3, "storyboard": 2},
    "Characters & People":        {"cover_mondo": 2, "cover_baoyu": 1, "illustrations": 3, "storyboard": 3},
    "Scenes & Storytelling":      {"cover_mondo": 1, "cover_baoyu": 1, "illustrations": 2, "storyboard": 3},
    "History & Classical":        {"cover_mondo": 2, "cover_baoyu": 1, "illustrations": 3, "storyboard": 2},
    "Document & Publication":     {"cover_mondo": 1, "cover_baoyu": 1, "illustrations": 2, "storyboard": 1},
}


# ---------------------------------------------------------------------------
# 上游 1：调用 gallery-explorer query.py 筛选案例
# ---------------------------------------------------------------------------

def fetch_cases(category: Optional[str] = None,
                keyword: Optional[str] = None,
                case_ids: Optional[List[str]] = None,
                limit: int = 50) -> List[Dict]:
    """调 gallery-explorer query.py 拿 JSON 结果。"""
    if not GALLERY_QUERY.exists():
        print(f"⚠️  gallery-explorer 未找到: {GALLERY_QUERY}")
        return []

    cmd = [sys.executable, str(GALLERY_QUERY), "--export", "json", "--limit", str(limit)]
    if category:
        cmd.extend(["--category", category])
    if keyword:
        cmd.extend(["--keyword", keyword])
    if case_ids:
        for cid in case_ids:
            cmd.extend(["--case", cid])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if result.returncode != 0:
            print(f"⚠️  query.py 失败: {result.stderr[:200]}")
            return []
        return json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        print("⚠️  query.py 超时")
        return []
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON 解析失败: {e}")
        return []


def fetch_category_stats() -> Dict[str, int]:
    """拉类目统计。"""
    if not GALLERY_QUERY.exists():
        return {}
    try:
        result = subprocess.run(
            [sys.executable, str(GALLERY_QUERY), "--stats"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        stats = {}
        for line in result.stdout.splitlines():
            line = line.strip()
            # 格式: "UI & Interfaces          73 ███████"
            m_match = line.split()
            if len(m_match) >= 2:
                try:
                    n = int(m_match[-1].split("█")[0].strip())
                    cat = " ".join(m_match[:-1]).strip()
                    if cat and cat in CATEGORIES:
                        stats[cat] = n
                except (ValueError, IndexError):
                    pass
        return stats
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# 上游 2：读取 templates.md 中的类目定义（用于补充 prompt 结构）
# ---------------------------------------------------------------------------

def parse_template_definitions() -> Dict[str, Dict]:
    """从 templates.md 提取 12 类目的模板定义 + 避坑指南。"""
    if not TEMPLATES_MD.exists():
        return {}
    text = TEMPLATES_MD.read_text(encoding="utf-8", errors="replace")
    defs = {}
    # 单次扫描: 找出所有 <a name="tpl-..."> 锚点的位置
    # vet-safe: 标准库正则 finditer
    pattern = r'<a name="tpl-(\w+[-\w]*)"></a>\s*\n+###\s*(.+?)\n'
    matches = list(re.finditer(pattern, text, re.MULTILINE))

    for i, match in enumerate(matches):
        slug = match.group(1)
        title = match.group(2).strip()
        start = match.end()
        # 下一段起点 = 下一个 match 的起点, 末尾 = 文本结尾
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end]

        # 提取常规模板（text code block 第一个）
        tmpl_m = re.search(r"```text\s*\n(.*?)\n```", body, re.DOTALL)
        template_text = tmpl_m.group(1).strip() if tmpl_m else ""

        # 提取避坑指南（**避坑指南** 后的列表）
        pitfall_m = re.search(r"\*\*避坑指南\*\*\s*\n(.+?)(?=\n###|\n<a|\Z)", body, re.DOTALL)
        pitfalls = pitfall_m.group(1).strip() if pitfall_m else ""

        defs[slug] = {"title": title, "template": template_text, "pitfalls": pitfalls[:300]}
    return defs


# ---------------------------------------------------------------------------
# 下游 4 个 adapter（与 book-distiller-bridge schema 同构）
# ---------------------------------------------------------------------------

def adapter_cover_mondo(case: Dict, lang: str = "auto",
                        style: str = "vintage") -> Dict:
    """Mondo 海报 prompt（基于 gpt-image-2 案例 prompt 二次构造）。"""
    case_id = case.get("id", "unknown")
    title = case.get("title", "")
    src_prompt = case.get("prompt", "")[:300]
    category = case.get("category", "Unknown")

    if lang == "en":
        prompt = (
            f"A {style} poster inspired by gpt-image-2 case '{case_id}' - '{title}'. "
            f"Category: {category}. "
            f"Source prompt essence: {src_prompt[:200]}. "
            f"Typography: bold serif title, minimalist composition. "
            f"Color palette: warm muted tones, strong contrast. "
            f"Aspect ratio: 1:1, high quality poster design."
        )
    else:
        prompt = (
            f"一张{style}风格的海报, 灵感来自 gpt-image-2 案例 '{case_id}' - '{title}'. "
            f"类目: {category}. "
            f"原 prompt 精髓: {src_prompt[:150]}. "
            f"排版: 粗体衬线标题, 极简构图. "
            f"色彩: 暖色调低饱和, 高对比. 1:1 高品质海报."
        )
    return {
        "adapter": "cover_mondo",
        "downstream_skill": "qiaomu-mondo-poster-design",
        "prompt": prompt,
        "output_format": "PNG 1024x1024",
        "filename": f"cover_mondo_{case_id}.png",
        "source_case_id": case_id,
        "source_category": category,
    }


def adapter_cover_baoyu(case: Dict, lang: str = "auto") -> Dict:
    """Baoyu 公众号封面 prompt。"""
    case_id = case.get("id", "unknown")
    title = case.get("title", "")
    src_prompt = case.get("prompt", "")[:200]
    category = case.get("category", "Unknown")

    if lang == "en":
        prompt = (
            f"WeChat article cover inspired by gpt-image-2 case '{case_id}'. "
            f"Title concept: '{title}'. "
            f"Key visual: {src_prompt[:120]}. "
            f"Style: clean editorial, 16:9, text-friendly, high readability."
        )
    else:
        prompt = (
            f"公众号文章封面, 灵感来自 gpt-image-2 案例 '{case_id}'. "
            f"标题概念: '{title}'. "
            f"核心视觉: {src_prompt[:80]}. "
            f"风格: 简洁编辑风, 16:9, 文字友好, 高可读性."
        )
    return {
        "adapter": "cover_baoyu",
        "downstream_skill": "baoyu-cover-image",
        "prompt": prompt,
        "output_format": "PNG 900x383 (16:9)",
        "filename": f"cover_baoyu_{case_id}.png",
        "source_case_id": case_id,
        "source_category": category,
    }


def adapter_illustration(case: Dict, lang: str = "auto",
                         style_prefix: str = "") -> Dict:
    """单图配图 prompt。"""
    case_id = case.get("id", "unknown")
    title = case.get("title", "")
    src_prompt = case.get("prompt", "")[:250]
    category = case.get("category", "Unknown")

    if lang == "en":
        prompt = (
            f"{style_prefix} Illustration inspired by gpt-image-2 case '{case_id}' - '{title}'. "
            f"Category: {category}. "
            f"Scene: {src_prompt[:150]}. "
            f"Style: clean editorial illustration, 16:9, warm tones, high quality."
        )
    else:
        prompt = (
            f"{style_prefix} 配图, 灵感来自 gpt-image-2 案例 '{case_id}' - '{title}'. "
            f"类目: {category}. "
            f"场景: {src_prompt[:100]}. "
            f"风格: 简洁编辑插画, 16:9, 暖色调, 高品质."
        )
    return {
        "adapter": "illustrations_smart",
        "downstream_skill": "smart-illustrator",
        "prompt": prompt,
        "output_format": "PNG 16:9 (1920x1080)",
        "filename": f"illustrations/{case_id}.png",
        "source_case_id": case_id,
        "source_category": category,
    }


def adapter_storyboard(cases: List[Dict], title: str = "",
                        duration: int = 30, lang: str = "auto") -> Dict:
    """Seedance 短视频剧本（基于 N 个 Scenes 案例）。"""
    n_shots = max(3, min(6, duration // 5))
    shots = []
    for i in range(n_shots):
        if i < len(cases):
            c = cases[i]
            scene_name = c.get("title", f"Scene {i+1}")[:30]
            kw_str = c.get("prompt", "")[:80]
        else:
            scene_name = "Outro"
            kw_str = "结尾"
        shot = {
            "shot_id": i + 1,
            "duration_sec": duration // n_shots,
            "scene": scene_name,
            "source_case_id": cases[i].get("id") if i < len(cases) else None,
            "camera": ["establishing wide", "medium close-up", "over-shoulder",
                       "close-up", "pan", "pull-back"][i % 6],
            "prompt_zh": f"镜头{i+1} ({duration//n_shots}秒): 场景 - {scene_name}, 元素: {kw_str}",
            "prompt_en": f"Shot {i+1} ({duration//n_shots}s): scene - {scene_name}, elements: {kw_str}",
        }
        shots.append(shot)
    return {
        "adapter": "storyboard_seedance",
        "downstream_skill": "seedance2-skill",
        "title": title or f"gpt-image-2 Scenes Compilation",
        "duration_sec": duration,
        "shots": shots,
        "output_format": "Markdown script + N prompts",
        "filename": "storyboard_seedance.md",
        "source_cases": [c.get("id") for c in cases],
    }


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def bridge(category: Optional[str] = None,
           keyword: Optional[str] = None,
           case_ids: Optional[List[str]] = None,
           auto_sample: bool = False,
           per_category: int = 2,
           only: Optional[str] = None,
           count: int = 6,
           dry_run: bool = False,
           output_dir: Optional[Path] = None,
           lang: str = "auto",
           mondo_style: str = "vintage",
           seedance_duration: int = 30) -> Dict:
    """主入口: 解析 + 编排 4 个 adapter。"""
    output_dir = (output_dir or BRIDGE_DIR / "bridge_output").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "illustrations").mkdir(exist_ok=True)

    # Step 1: 取案例
    cases: List[Dict] = []
    if auto_sample:
        print("🎲 自动抽样模式（按类目）...")
        stats = fetch_category_stats()
        for cat in CATEGORIES:
            if cat in stats and stats[cat] > 0:
                n = min(per_category, stats[cat])
                cat_cases = fetch_cases(category=cat, limit=n)
                # 随机抽样
                random.shuffle(cat_cases)
                cases.extend(cat_cases[:n])
    else:
        cases = fetch_cases(
            category=category,
            keyword=keyword,
            case_ids=case_ids,
            limit=count * 3 if only in (None, "illustrations_smart") else max(20, count),
        )

    # 按类目分组
    by_category: Dict[str, List[Dict]] = {cat: [] for cat in CATEGORIES}
    by_category["Unknown"] = []
    for c in cases:
        cat = c.get("category", "Unknown")
        if cat in by_category:
            by_category[cat].append(c)
        else:
            by_category["Unknown"].append(c)

    print(f"\n📊 检索结果: {len(cases)} 个案例")
    for cat, lst in by_category.items():
        if lst:
            print(f"   {cat}: {len(lst)}")

    if not cases:
        return {"ok": False, "error": "未检索到案例", "cases": []}

    # Step 2: 风格前缀
    style_prefix = f"Style: clean editorial, warm muted colors, 16:9. Source: gpt-image-2 gallery (518 cases)."

    prompts_used: List[Dict] = []
    manifest = {
        "ok": True,
        "input": {"category": category, "keyword": keyword, "case_ids": case_ids,
                  "auto_sample": auto_sample, "per_category": per_category},
        "lang": lang,
        "dry_run": dry_run,
        "adapters_run": [],
        "routing_matrix_used": ROUTING_MATRIX,
    }

    # 1. cover_mondo — 选 Posters/Brand/Illustration 类目
    if only in (None, "cover_mondo"):
        print("\n🎨 [1/4] cover_mondo...")
        # 优先 Posters > Brand > Illustration
        target = (by_category["Posters & Typography"] or
                  by_category["Brand & Logos"] or
                  by_category["Illustration & Art"] or
                  cases[:1])
        if target:
            p = adapter_cover_mondo(target[0], lang=lang, style=mondo_style)
            prompts_used.append(p)
            manifest["adapters_run"].append("cover_mondo")
            print(f"   case: {p['source_case_id']} ({p['source_category']})")
            if not dry_run:
                print(f"   [dry-run] → {p['downstream_skill']}")

    # 2. cover_baoyu — 选 UI/Posters 类目
    if only in (None, "cover_baoyu"):
        print("\n📰 [2/4] cover_baoyu...")
        target = (by_category["UI & Interfaces"] or
                  by_category["Posters & Typography"] or
                  cases[:1])
        if target:
            p = adapter_cover_baoyu(target[0], lang=lang)
            prompts_used.append(p)
            manifest["adapters_run"].append("cover_baoyu")
            print(f"   case: {p['source_case_id']} ({p['source_category']})")
            if not dry_run:
                print(f"   [dry-run] → {p['downstream_skill']}")

    # 3. illustrations — 按路由矩阵选 N 个
    if only in (None, "illustrations_smart"):
        print(f"\n🖼️  [3/4] illustrations (最多 {count} 张)...")
        # 按路由评分排序选 case
        scored = []
        for c in cases:
            cat = c.get("category", "Unknown")
            score = ROUTING_MATRIX.get(cat, {}).get("illustrations", 0)
            scored.append((score, c))
        scored.sort(key=lambda x: -x[0])
        selected = [c for s, c in scored if s > 0][:count]
        for i, c in enumerate(selected, 1):
            p = adapter_illustration(c, lang=lang, style_prefix=style_prefix)
            prompts_used.append(p)
            print(f"   [{i}/{len(selected)}] {p['source_case_id']} ({p['source_category']}) → {p['filename']}")
        manifest["adapters_run"].append(f"illustrations_smart x {len(selected)}")
        if not dry_run:
            print(f"   [dry-run] → smart-illustrator")

    # 4. storyboard — 选 Scenes/Characters 类目
    if only in (None, "storyboard_seedance"):
        print(f"\n🎬 [4/4] storyboard ({seedance_duration}s)...")
        target = (by_category["Scenes & Storytelling"] or
                  by_category["Characters & People"] or
                  cases[:3])
        if target:
            p = adapter_storyboard(target, lang=lang, duration=seedance_duration)
            prompts_used.append(p)
            manifest["adapters_run"].append("storyboard_seedance")
            print(f"   {len(p['shots'])} 镜头, 总时长 {p['duration_sec']}s, source cases: {p['source_cases']}")
            if not dry_run:
                md_path = output_dir / "storyboard_seedance.md"
                lines = [f"# {p['title']} · Seedance 短视频剧本",
                         f"\n> 来源: gpt-image-2 gallery ({len(p['source_cases'])} cases)",
                         f"\n> 时长: {p['duration_sec']}s | 镜头数: {len(p['shots'])}",
                         "\n## 镜头清单\n"]
                for s in p["shots"]:
                    lines.append(f"### Shot {s['shot_id']} · {s['scene']} ({s['duration_sec']}s)")
                    lines.append(f"- **运镜**: {s['camera']}")
                    lines.append(f"- **Source Case**: {s.get('source_case_id', '-')}")
                    lines.append(f"- **Prompt (ZH)**: {s['prompt_zh']}")
                    lines.append(f"- **Prompt (EN)**: {s['prompt_en']}\n")
                md_path.write_text("\n".join(lines), encoding="utf-8")
                print(f"   剧本已写入: {md_path.relative_to(output_dir)}")

    # 写产物
    (output_dir / "prompts_used.json").write_text(
        json.dumps(prompts_used, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n✅ bridge 完成, 产物在 {output_dir}/")
    try:
        rel = output_dir.relative_to(BRIDGE_DIR.parent)
        print(f"   (相对: {rel})")
    except ValueError:
        pass
    print(f"   - prompts_used.json ({len(prompts_used)} prompts)")
    print(f"   - manifest.json")

    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="天龙引擎 V1.0 · gpt-image-2-bridge 编排器"
    )
    # 输入
    parser.add_argument("--category", choices=CATEGORIES, help="按类目筛选 (12 类目之一)")
    parser.add_argument("--keyword", help="按关键词搜索 (prompt/title)")
    parser.add_argument("--case", action="append", dest="case_ids", help="按案例 ID (可多次)")
    parser.add_argument("--auto-sample", action="store_true", help="自动按类目统计 + 抽样")
    parser.add_argument("--per-category", type=int, default=2, help="auto-sample 时每类目抽样数")
    # 输出
    parser.add_argument("--only", choices=["cover_mondo", "cover_baoyu",
                        "illustrations_smart", "storyboard_seedance"],
                        help="只跑某 adapter")
    parser.add_argument("--count", type=int, default=6, help="illustrations 数量上限")
    parser.add_argument("--mondo-style", default="vintage",
                        choices=["vintage", "modern", "minimal"])
    parser.add_argument("--seedance-duration", type=int, default=30,
                        help="短视频总时长 15/30/60")
    parser.add_argument("--lang", choices=["auto", "zh", "en"], default="auto")
    parser.add_argument("--dry-run", action="store_true", help="只生成 prompt 不调 API")
    parser.add_argument("--output-dir", help="输出目录")

    args = parser.parse_args()
    r = bridge(
        category=args.category,
        keyword=args.keyword,
        case_ids=args.case_ids,
        auto_sample=args.auto_sample,
        per_category=args.per_category,
        only=args.only,
        count=args.count,
        dry_run=args.dry_run,
        output_dir=Path(args.output_dir) if args.output_dir else None,
        lang=args.lang,
        mondo_style=args.mondo_style,
        seedance_duration=args.seedance_duration,
    )
    print("\n📊 manifest:")
    print(json.dumps(r, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()