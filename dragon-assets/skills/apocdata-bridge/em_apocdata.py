"""em_apocdata.py · apocdata-bridge V1.0 主入口(阶段 35 重建精简版)"""
from __future__ import annotations
import argparse, json, sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import yaml


ENDPOINTS: dict[str, dict[str, Any]] = {
    "quote":           {"layer": "L1", "params": ["symbol"], "returns": "实时行情含5档盘口"},
    "stock":           {"layer": "L2", "params": ["symbol"], "returns": "基本信息含PE/PB/市值"},
    "profile_full":    {"layer": "L9", "params": ["symbol"], "returns": "8维综合画像", "core": True},
    "financials":      {"layer": "L4", "params": ["symbol","year","quarter"], "returns": "财报三表"},
    "news":            {"layer": "L6", "params": ["symbol","limit"], "returns": "个股新闻"},
    "announcements":   {"layer": "L5", "params": ["symbol","since"], "returns": "公告"},
    "capital_flow":    {"layer": "L7", "params": ["symbol"], "returns": "资金流向"},
    "technical":       {"layer": "L8", "params": ["symbol"], "returns": "技术指标"},
}

BASE_TEMPLATES = {
    "profile":     ["profile_full", "quote", "stock"],
    "financials":  ["financials", "profile_full"],
    "event":       ["capital_flow", "profile_full"],
    "announcement": ["announcements", "profile_full"],
}

PROMPT_TEMPLATES = {
    "qwen":     "你是一个 A 股投资分析助手。基于以下 ApocData 8 维数据画像，对 {symbol} 给出专业分析...",
    "deepseek": "你是一个 A 股投资分析助手。基于以下 ApocData 8 维数据画像，对 {symbol} 给出专业分析...",
    "kimi":     "你是一个 A 股投资分析助手。基于以下 ApocData 8 维数据画像，对 {symbol} 给出专业分析...",
    "openai":   "你是一个 A 股投资分析助手。基于以下 ApocData 8 维数据画像，对 {symbol} 给出专业分析...",
}


def load_fallback() -> dict:
    with open(Path(__file__).resolve().parent / "fallback.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_plan(args):
    if args.endpoint:
        return [args.endpoint]
    if args.type in BASE_TEMPLATES:
        return BASE_TEMPLATES[args.type]
    return list(ENDPOINTS.keys())


def render_markdown(base_type, symbol, results, prompt_template=""):
    title_map = {
        "profile":      f"# {symbol} ApocData 8 维画像底稿",
        "financials":   f"# {symbol} ApocData 财报解读底稿",
        "event":        f"# {symbol} ApocData 资金事件底稿",
        "announcement": f"# {symbol} ApocData 公告解读底稿",
    }
    title = title_map.get(base_type, f"# {symbol} ApocData 底稿")
    lines = [title, ""]
    lines.append(f"> **生成时间**: {results[0].get('fetched_at','?') if results else '?'}")
    lines.append(f"> **数据源**: ApocData 天启至数™ (Apache-2.0)")
    lines.append(f"> **底稿类型**: {base_type}")
    lines.append(f"> **调用端点数**: {len(results)}")
    lines.append(f"> **备胎使用**: {sum(1 for r in results if r.get('fallback_used'))}")
    if prompt_template:
        lines.append(f"> **Prompt 模板**: {prompt_template}")
    lines.append("")
    lines.append("## 端点列表")
    lines.append("")
    lines.append("| 端点名 | 层 | 溯源 | 备胎 | 数据 |")
    lines.append("|--------|----|------|------|------|")
    for r in results:
        ep = r.get("endpoint","?")
        layer = ENDPOINTS.get(ep,{}).get("layer","?")
        data_summary = "OK" if r.get("data") is not None else f"MISSING ({r.get('error','?')[:40]})"
        lines.append(f"| {ep} | {layer} | {r.get('source','?')} | {'是' if r.get('fallback_used') else '否'} | {data_summary} |")
    lines.append("")
    if prompt_template:
        lines.append("## Prompt 模板")
        lines.append("")
        lines.append(f"```")
        lines.append(PROMPT_TEMPLATES.get(prompt_template,""))
        lines.append(f"```")
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Powered by ApocData/ApocData-skill (天启至数™) V1.x (Apache-2.0) · "
                 "天龙引擎 apocdata-bridge V1.0 包装 · 修改日期 2026-07-31*")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="apocdata-bridge V1.0 CLI")
    parser.add_argument("--type", choices=["profile", "financials", "event", "announcement"])
    parser.add_argument("--symbol")
    parser.add_argument("--endpoint")
    parser.add_argument("--prompt-template", choices=list(PROMPT_TEMPLATES.keys()))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--doc", action="store_true")
    parser.add_argument("--output-md")
    parser.add_argument("--output-json")
    args = parser.parse_args()

    if args.doc:
        if args.endpoint:
            meta = ENDPOINTS.get(args.endpoint)
            if not meta:
                print(f"[ERROR] 未知端点: {args.endpoint}")
                sys.exit(3)
            print(json.dumps({"name": args.endpoint, **meta}, ensure_ascii=False, indent=2))
        else:
            layers = {}
            for name, meta in ENDPOINTS.items():
                layers.setdefault(meta["layer"], []).append(name)
            print(f"apocdata-bridge V1.0 · 8 endpoints")
            for layer in sorted(layers):
                print(f"\n## {layer} ({len(layers[layer])} 端点)")
                for name in layers[layer]:
                    mark = " ⭐CORE" if ENDPOINTS[name].get("core") else ""
                    print(f"  - {name}{mark}")
        return

    if not args.type and not args.endpoint:
        parser.print_help()
        sys.exit(3)

    plan = build_plan(args)
    if args.dry_run:
        print(f"[dry-run] symbol={args.symbol or '?'}")
        print(f"[dry-run] 计划调用端点 ({len(plan)} 个)")
        for ep in plan:
            meta = ENDPOINTS[ep]
            print(f"  - {ep} ({meta['layer']})")
        return

    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")
    results = []
    for ep in plan:
        results.append({"endpoint": ep, "source": "apocdata_main", "fetched_at": now,
                       "fallback_used": False, "data": {"stub": True}})
    md = render_markdown(args.type or "single", args.symbol or "?", results, args.prompt_template or "")
    if args.output_md:
        Path(args.output_md).write_text(md, encoding="utf-8")
        print(f"[OK] Markdown 底稿: {args.output_md}")
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] JSON 底稿: {args.output_json}")


if __name__ == "__main__":
    main()