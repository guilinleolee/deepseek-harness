"""em_base.py · a-stock-data-bridge V1.0 主入口

天龙自研包装层 · Apache-2.0
用法：
  python em_base.py --type stock --symbol "600519.SH" --layers L1,L3,L4,L6,L7
  python em_base.py --doc --endpoint kline_with_ma
  python em_base.py --doc                          # 列出全部 43 端点 schema
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
    """加载 fallback.yaml → 43 端点兜底链"""
    with open(BASE_DIR / "fallback.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_priority() -> dict:
    """加载 source_priority.json → 15 数据源优先级"""
    with open(BASE_DIR / "source_priority.json", "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────
# 43 端点 schema（1:1 映射上游 V3.4.0）
# ─────────────────────────────────────────────
ENDPOINTS: dict[str, dict[str, Any]] = {
    # L1 行情层 5 端点
    "kline_with_ma":     {"layer": "L1", "params": ["symbol", "period", "limit"], "returns": "OHLCV + MA5/10/20"},
    "five_level_quote":  {"layer": "L1", "params": ["symbol"], "returns": "5档盘口价格/量"},
    "pe_pb_market_cap":  {"layer": "L1", "params": ["symbol"], "returns": "PE/PB/市值/流通市值"},
    "index_etf_quote":   {"layer": "L1", "params": ["code"], "returns": "指数/ETF 实时行情"},
    "minute_kline":      {"layer": "L1", "params": ["symbol", "date"], "returns": "分钟 K 线"},
    # L2 研报层 5 端点
    "research_report_list":   {"layer": "L2", "params": ["symbol", "since"], "returns": "研报列表"},
    "research_report_pdf":    {"layer": "L2", "params": ["report_id"], "returns": "PDF 下载"},
    "consensus_eps":          {"layer": "L2", "params": ["symbol"], "returns": "一致预期 EPS/营收"},
    "iwencai_nl_search":      {"layer": "L2", "params": ["query"], "returns": "NL 搜索结果"},
    "industry_report":        {"layer": "L2", "params": ["industry"], "returns": "行业研报列表"},
    # L3 信号层 9 端点
    "strong_stock_signal":    {"layer": "L3", "params": ["date"], "returns": "强势股榜单"},
    "theme_attribution":      {"layer": "L3", "params": ["symbol"], "returns": "题材归因"},
    "north_bound_flow":       {"layer": "L3", "params": ["date"], "returns": "北向资金净流入"},
    "concept_sector_flow":    {"layer": "L3", "params": ["date"], "returns": "概念板块资金流"},
    "money_flow_rank":        {"layer": "L3", "params": ["date"], "returns": "资金流排名"},
    "dragon_tiger_list":      {"layer": "L3", "params": ["date"], "returns": "龙虎榜"},
    "restricted_unlock":      {"layer": "L3", "params": ["since"], "returns": "解禁清单"},
    "north_top10":            {"layer": "L3", "params": ["date"], "returns": "北向 TOP10"},
    "south_bound_flow":       {"layer": "L3", "params": ["date"], "returns": "南向资金净流入"},
    # L4 资金面 5 端点
    "margin_balance":         {"layer": "L4", "params": ["symbol"], "returns": "融资融券余额"},
    "block_trade":            {"layer": "L4", "params": ["date"], "returns": "大宗交易"},
    "shareholder_count":      {"layer": "L4", "params": ["symbol"], "returns": "股东户数"},
    "dividend_history":       {"layer": "L4", "params": ["symbol"], "returns": "分红送转历史"},
    "minute_money_flow":      {"layer": "L4", "params": ["symbol", "date"], "returns": "分钟级资金流"},
    # L5 新闻层 2 端点
    "stock_news":             {"layer": "L5", "params": ["symbol", "limit"], "returns": "个股新闻"},
    "global_news":            {"layer": "L5", "params": ["limit"], "returns": "全球资讯"},
    # L6 基础数据 3 端点
    "quarterly_report_37fields": {"layer": "L6", "params": ["symbol", "year", "quarter"], "returns": "季报 37 字段"},
    "f10_nine_categories":    {"layer": "L6", "params": ["symbol"], "returns": "F10 九大类"},
    "financial_3statements":  {"layer": "L6", "params": ["symbol", "year", "quarter"], "returns": "财报三表"},
    # L7 公告层 2 端点
    "cninfo_announcement":    {"layer": "L7", "params": ["symbol", "since"], "returns": "巨潮公告列表"},
    "cninfo_pdf":             {"layer": "L7", "params": ["announcement_id"], "returns": "公告 PDF 字节流"},
    # L8 打板层 4 端点
    "limit_up_board":         {"layer": "L8", "params": ["date"], "returns": "涨停板榜单"},
    "limit_up_leader":        {"layer": "L8", "params": ["date"], "returns": "龙头识别"},
    "sector_linkage":         {"layer": "L8", "params": ["date"], "returns": "板块联动"},
    "tickflow_auction":       {"layer": "L8", "params": ["date"], "returns": "集合竞价数据"},
    # L9 ETF期权 4 端点
    "etf_nav":                {"layer": "L9", "params": ["code"], "returns": "ETF 净值"},
    "etf_holdings":           {"layer": "L9", "params": ["code"], "returns": "ETF 持仓明细"},
    "option_chain":           {"layer": "L9", "params": ["underlying", "date"], "returns": "期权链"},
    "option_greeks":          {"layer": "L9", "params": ["option_code"], "returns": "Greeks/隐含波动率"},
    # L10 舆情互动 3 端点
    "xueqiu_hot_rank":        {"layer": "L10", "params": ["limit"], "returns": "雪球热榜(cookie 态)"},
    "iwencai_qa":             {"layer": "L10", "params": ["query"], "returns": "问财 QA"},
    "interactive_qa":         {"layer": "L10", "params": ["symbol"], "returns": "互动易问答"},
    # 补充 L1/L6 2 端点(累计 43)
    "valuation_full":         {"layer": "L6", "params": ["symbol"], "returns": "完整估值数据"},
}


# 各底稿类型默认端点组合
BASE_TEMPLATES = {
    "stock":         ["kline_with_ma", "five_level_quote", "pe_pb_market_cap", "north_bound_flow",
                      "dragon_tiger_list", "margin_balance", "cninfo_announcement", "quarterly_report_37fields"],
    "industry":      ["industry_report", "valuation_full", "etf_nav", "etf_holdings", "interactive_qa"],
    "event":         ["north_bound_flow", "dragon_tiger_list", "limit_up_board", "limit_up_leader",
                      "minute_money_flow"],
    "announcement":  ["cninfo_announcement", "financial_3statements", "quarterly_report_37fields"],
}


def build_plan(args: argparse.Namespace) -> list[str]:
    if args.layers:
        wanted_layers = set(layer.strip() for layer in args.layers.split(","))
        return [name for name, meta in ENDPOINTS.items() if meta["layer"] in wanted_layers]
    if args.type in BASE_TEMPLATES:
        return BASE_TEMPLATES[args.type]
    return list(ENDPOINTS.keys())


def render_markdown(base_type: str, symbol: str, results: list[dict]) -> str:
    lines: list[str] = []
    title_map = {
        "stock": f"# {symbol} 个股深度底稿",
        "industry": "# 行业横评底稿",
        "event": "# 资金流事件底稿",
        "announcement": f"# {symbol} 公告事件底稿",
    }
    lines.append(title_map.get(base_type, "# a-stock-data-bridge 底稿"))
    lines.append("")
    lines.append(f"> **生成时间**: {results[0].get('fetched_at', '?') if results else '?'}")
    lines.append(f"> **底稿类型**: {base_type}")
    lines.append(f"> **调用端点数**: {len(results)}")
    fallback_count = sum(1 for r in results if r.get("fallback_used"))
    lines.append(f"> **备胎使用**: {fallback_count}")
    lines.append(f"> **真源行数合计**: {sum(r.get('rows', 0) for r in results)}")
    lines.append("")
    lines.append("## 端点列表")
    lines.append("")
    lines.append("| 端点名 | 层 | 溯源 | 备胎 | rows | 数据 |")
    lines.append("|--------|----|------|------|------|------|")
    for r in results:
        ep = r.get("endpoint", "?")
        layer = ENDPOINTS.get(ep, {}).get("layer", "?")
        rows = r.get("rows", 0)
        if r.get("error"):
            data_summary = f"ERR: {r['error'][:40]}"
        else:
            data_summary = r.get("data_summary", "?")[:50]
        lines.append(f"| {ep} | {layer} | {r.get('source','?')} | "
                     f"{'是' if r.get('fallback_used') else '否'} | {rows} | {data_summary} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Powered by simonlin1212/a-stock-data V3.4.0 (Apache-2.0) · "
                 "天龙引擎 a-stock-data-bridge V1.0 包装 · 修改日期 2026-07-21*")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="a-stock-data-bridge V1.0 CLI")
    parser.add_argument("--type", choices=["stock", "industry", "event", "announcement"])
    parser.add_argument("--symbol")
    parser.add_argument("--industry")
    parser.add_argument("--event")
    parser.add_argument("--since")
    parser.add_argument("--date")
    parser.add_argument("--layers")
    parser.add_argument("--force-fallback", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--doc", action="store_true")
    parser.add_argument("--endpoint")
    parser.add_argument("--output-md")
    parser.add_argument("--output-json")
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
            print(f"a-stock-data-bridge V1.0 · 43 endpoints · {len(ENDPOINTS)} 已注册")
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
        print(f"[dry-run] 底稿类型: {args.type}")
        print(f"[dry-run] 计划调用端点 ({len(plan)} 个):")
        for ep in plan:
            meta = ENDPOINTS[ep]
            sources = fallback_cfg["endpoints"].get(ep, [])
            print(f"  - {ep} ({meta['layer']})  sources={sources}")
        return

    # 延迟导入避免 collection 问题
    from em_get import get_session
    from live_fetch import dispatch as live_dispatch

    session = get_session()
    results = []
    for ep in plan:
        sources = fallback_cfg["endpoints"].get(ep, [ep])
        primary = sources[0]
        fallbacks = sources[1:] if len(sources) > 1 else []

        # 真源：调 live_fetch 上游 V3.4.0 函数
        sym = args.symbol or ""
        kwargs = {
            "symbol": sym,
            "industry": args.industry,
            "event": args.event,
            "date": args.date,
            "since": args.since,
        }

        def primary_call(_p=primary):
            data, ret_type, src = live_dispatch(ep, **kwargs)
            try:
                import pandas as pd
                rows = len(data) if hasattr(data, "__len__") else 0
            except ImportError:
                rows = 0
            if ret_type == "error":
                return {"endpoint": ep, "source": _p, "rows": 0, "error": src, "note": "fetch-error"}
            return {
                "endpoint": ep,
                "source": _p,
                "rows": rows,
                "data_summary": f"ret_type={ret_type} src={src}",
                "fetched_at": __import__("datetime").datetime.now().isoformat(),
                "fallback_used": False,
            }

        def fallback_call(_fb):
            return {
                "endpoint": ep,
                "source": _fb,
                "rows": 0,
                "data_summary": f"fallback:{_fb}",
                "fetched_at": __import__("datetime").datetime.now().isoformat(),
                "fallback_used": True,
            }

        result = session.em_get(
            endpoint_name=ep,
            primary_source=primary_call,
            fallback_sources=[lambda _fb=fb: fallback_call(_fb) for fb in fallbacks],
        )
        rd = result.to_dict() if hasattr(result, "to_dict") else result.__dict__
        # primary 返回的 payload 在 rd["data"] 里
        payload = rd.get("data") if isinstance(rd.get("data"), dict) else {}
        results.append({
            "endpoint": ep,
            "source": rd.get("source", primary),
            "rows": payload.get("rows", 0),
            "data_summary": payload.get("data_summary", ""),
            "fetched_at": rd.get("fetched_at", ""),
            "fallback_used": rd.get("fallback_used", False),
            "error": payload.get("error", ""),
        })

    md = render_markdown(args.type, args.symbol or "?", results)
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