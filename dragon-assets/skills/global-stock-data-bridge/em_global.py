"""em_global.py · global-stock-data-bridge V1.0 主入口

天龙自研包装层 · Apache-2.0
用法：
  python em_global.py --type valuation --symbol AAPL --layers L1,L6,L7
  python em_global.py --doc --endpoint valuation_ratios
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


BASE_DIR = Path(__file__).resolve().parent


def load_fallback() -> dict:
    with open(BASE_DIR / "fallback.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_priority() -> dict:
    with open(BASE_DIR / "source_priority.json", "r", encoding="utf-8") as f:
        return json.load(f)


# 17 端点 schema
ENDPOINTS: dict[str, dict[str, Any]] = {
    # L1 行情层 4 端点
    "quote_realtime":      {"layer": "L1", "params": ["symbol"], "returns": "实时报价+盘前盘后",
                            "market": ["US", "HK"]},
    "historical_ohlcv":    {"layer": "L1", "params": ["symbol", "period", "range"],
                            "returns": "历史OHLCV(支持日/周/月)", "market": ["US", "HK"]},
    "intraday_ohlcv":      {"layer": "L1", "params": ["symbol", "interval"],
                            "returns": "分钟级OHLCV(1m/5m/15m/30m/60m)", "market": ["US"]},
    "adjusted_close":      {"layer": "L1", "params": ["symbol", "range"],
                            "returns": "复权收盘价(分红除权调整)", "market": ["US", "HK"]},
    # L2 财务层 3 端点
    "financial_3statements": {"layer": "L2", "params": ["symbol", "year", "quarter"],
                              "returns": "财报三表(资产负债/利润/现金流量)", "market": ["US", "HK"]},
    "quarterly_37fields":  {"layer": "L2", "params": ["symbol", "year", "quarter"],
                            "returns": "季报37字段", "market": ["US"]},
    "ttm_summary":         {"layer": "L2", "params": ["symbol"], "returns": "12个月滚动摘要",
                            "market": ["US", "HK"]},
    # L3 技术指标层 5 端点
    "ma_indicator":        {"layer": "L3", "params": ["symbol", "periods"],
                            "returns": "MA(默认5/10/20/60/120/250)", "compute": True},
    "macd_indicator":      {"layer": "L3", "params": ["symbol"], "returns": "MACD(12,26,9)",
                            "compute": True},
    "rsi_indicator":       {"layer": "L3", "params": ["symbol", "period"],
                            "returns": "RSI(默认14)", "compute": True},
    "kdj_indicator":       {"layer": "L3", "params": ["symbol"],
                            "returns": "KDJ(9,3,3)", "compute": True},
    "bollinger_bands":     {"layer": "L3", "params": ["symbol"],
                            "returns": "布林带(20,2)", "compute": True},
    # L4 新闻层 2 端点
    "global_news":         {"layer": "L4", "params": ["limit"], "returns": "全球财经新闻",
                            "market": ["GLOBAL"]},
    "stock_news":          {"layer": "L4", "params": ["symbol", "limit"], "returns": "个股新闻",
                            "market": ["US", "HK"]},
    # L5 公告层 1 端点
    "sec_filing":          {"layer": "L5", "params": ["symbol", "form_type", "since"],
                            "returns": "美股/港股公告检索(10-K/10-Q/8-K)",
                            "market": ["US", "HK"]},
    # L6 估值层 1 端点
    "valuation_ratios":    {"layer": "L6", "params": ["symbol"],
                            "returns": "PE/PB/PS/EV-EBITDA/股息率/Beta", "compute": True},
    # L7 同业对比 1 端点
    "peer_compare":        {"layer": "L7", "params": ["symbol", "industry"],
                            "returns": "同业PE对比+行业百分位", "market": ["US", "HK"]},
}


def _infer_market(symbol: str) -> str:
    """根据股票代码推断市场"""
    s = symbol.upper()
    if s.endswith(".HK") or (s.isdigit() and len(s) <= 5):
        return "HK"
    if s.endswith(".SH") or s.endswith(".SZ"):
        return "CN"
    return "US"


BASE_TEMPLATES = {
    "valuation":  ["quote_realtime", "adjusted_close", "valuation_ratios", "peer_compare"],
    "financials": ["financial_3statements", "quarterly_37fields", "ttm_summary"],
    "technical":  ["historical_ohlcv", "ma_indicator", "macd_indicator", "rsi_indicator",
                   "kdj_indicator", "bollinger_bands"],
    "hk_southbound": ["sec_filing", "stock_news"],
}


def build_plan(args: argparse.Namespace) -> list[str]:
    if args.layers:
        wanted_layers = set(layer.strip() for layer in args.layers.split(","))
        return [name for name, meta in ENDPOINTS.items() if meta["layer"] in wanted_layers]
    if args.type in BASE_TEMPLATES:
        return BASE_TEMPLATES[args.type]
    return list(ENDPOINTS.keys())


def render_markdown(base_type: str, symbol: str, results: list[dict], market: str) -> str:
    title_map = {
        "valuation": f"# {symbol} ({market}) 市值估值底稿",
        "financials": f"# {symbol} ({market}) 财报三表底稿",
        "technical": f"# {symbol} ({market}) 技术面底稿",
        "hk_southbound": f"# {symbol} ({market}) 港股南向资金底稿",
    }
    title = title_map.get(base_type, f"# {symbol} ({market}) 美港股底稿")
    lines: list[str] = [title, ""]
    lines.append(f"> **生成时间**: {results[0].get('fetched_at', '?') if results else '?'}")
    lines.append(f"> **市场**: {market}")
    lines.append(f"> **底稿类型**: {base_type}")
    lines.append(f"> **调用端点数**: {len(results)}")
    lines.append(f"> **备胎使用**: {sum(1 for r in results if r.get('fallback_used'))}")
    lines.append("")
    lines.append("## 端点列表")
    lines.append("")
    lines.append("| 端点名 | 层 | 市场 | 溯源 | 备胎 | 数据 |")
    lines.append("|--------|----|------|------|------|------|")
    for r in results:
        ep = r.get("endpoint", "?")
        layer = ENDPOINTS.get(ep, {}).get("layer", "?")
        m = r.get("market", "?")
        data_summary = "OK" if r.get("data") is not None else f"MISSING ({r.get('error', '?')[:40]})"
        lines.append(f"| {ep} | {layer} | {m} | {r.get('source','?')} | "
                     f"{'是' if r.get('fallback_used') else '否'} | {data_summary} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Powered by simonlin1212/global-stock-data V1.0.1 (Apache-2.0) · "
                 "天龙引擎 global-stock-data-bridge V1.0 包装 · 修改日期 2026-07-27*")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="global-stock-data-bridge V1.0 CLI")
    parser.add_argument("--type", choices=["valuation", "financials", "technical", "hk_southbound"],
                        help="底稿类型")
    parser.add_argument("--symbol", help="股票代码，如 AAPL / BABA / 0700.HK")
    parser.add_argument("--industry", help="行业名称（peer_compare 用）")
    parser.add_argument("--since", help="起始日期 YYYY-MM-DD")
    parser.add_argument("--layers", help="层级，如 L1,L3,L6,L7")
    parser.add_argument("--force-fallback", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--doc", action="store_true")
    parser.add_argument("--endpoint", help="配合 --doc")
    parser.add_argument("--output-md", help="Markdown 底稿输出")
    parser.add_argument("--output-json", help="JSON 底稿输出")
    args = parser.parse_args()

    fallback_cfg = load_fallback()

    if args.doc:
        if args.endpoint:
            meta = ENDPOINTS.get(args.endpoint)
            if not meta:
                print(f"[ERROR] 未知端点: {args.endpoint}")
                sys.exit(3)
            print(json.dumps({"name": args.endpoint, **meta}, ensure_ascii=False, indent=2))
        else:
            layers: dict[str, list[str]] = {}
            for name, meta in ENDPOINTS.items():
                layers.setdefault(meta["layer"], []).append(name)
            print(f"global-stock-data-bridge V1.0 · 17 endpoints · {len(ENDPOINTS)} 已注册")
            for layer in sorted(layers):
                print(f"\n## {layer} ({len(layers[layer])} 端点)")
                for name in layers[layer]:
                    print(f"  - {name}")
        return

    if not args.type:
        parser.print_help()
        sys.exit(3)

    plan = build_plan(args)
    if args.dry_run:
        market = _infer_market(args.symbol or "AAPL")
        print(f"[dry-run] 底稿类型: {args.type}")
        print(f"[dry-run] 标的: {args.symbol or '?'} ({market})")
        print(f"[dry-run] 计划调用端点 ({len(plan)} 个):")
        for ep in plan:
            meta = ENDPOINTS[ep]
            sources = fallback_cfg["endpoints"].get(ep, [])
            print(f"  - {ep} ({meta['layer']})  sources={sources}")
        return

    market = _infer_market(args.symbol or "AAPL")

    # 实际拉取
    def _get_session():
        from em_global_get import get_session
        return get_session()
    session = _get_session()
    results = []
    for ep in plan:
        sources = fallback_cfg["endpoints"].get(ep, [ep])
        primary = sources[0]
        fallbacks = sources[1:] if len(sources) > 1 else []

        def primary_call(_p=primary):
            return {"endpoint": ep, "source": _p, "rows": 0, "note": "stub"}

        def fallback_call(_fb):
            return {"endpoint": ep, "source": _fb, "rows": 0, "note": "stub-fallback"}

        result = session.em_global_get(
            endpoint_name=ep,
            market=market,
            primary_source=primary_call,
            fallback_sources=[lambda _fb=fb: fallback_call(_fb) for fb in fallbacks],
        )
        results.append(result.to_dict() if hasattr(result, "to_dict") else result.__dict__)

    md = render_markdown(args.type, args.symbol or "?", results, market)
    if args.output_md:
        Path(args.output_md).write_text(md, encoding="utf-8")
        print(f"[OK] Markdown 底稿: {args.output_md}")
    else:
        print(md)

    if args.output_json:
        Path(args.output_json).write_text(
            json.dumps(results, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[OK] JSON 底稿: {args.output_json}")

    print(f"\n[Stats] {session.stats()}")


if __name__ == "__main__":
    main()
