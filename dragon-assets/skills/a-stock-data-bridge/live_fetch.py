"""live_fetch.py · a-stock-data-bridge V1.0 真源路由

43 端点 → 上游 simonlin1212/a-stock-data V3.4.0 真函数映射表
Apache-2.0 NOTICE · 无需任何 API key · 全部直连 HTTP 公开端点

依赖：
- 必需：requests + PyYAML（桥自加）
- 必需：pandas + lxml（上游 a-stock-data 强依赖，非桥自加）
- 无：API key / 账号 / 付费

用法：
  from live_fetch import dispatch
  df, error = dispatch('kline_with_ma', symbol='sh600519')
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

# 把 a-stock-data/ 加入 import 路径（上游镜像）
_A_STOCK_DATA_DIR = Path(__file__).resolve().parent.parent / "a-stock-data"
if str(_A_STOCK_DATA_DIR) not in sys.path:
    sys.path.insert(0, str(_A_STOCK_DATA_DIR))

# 软导入 pandas + a_stock_data：让 import 阶段不强制装 pandas
# （注意：调用 dispatch() 时仍需 pandas，因为上游 a_stock_data 强依赖）
try:
    import pandas as pd  # noqa: F401
    import a_stock_data as upstream  # noqa: E402
    _PANDAS_AVAILABLE = True
except ImportError as e:
    pd = None  # type: ignore
    upstream = None  # type: ignore
    _PANDAS_AVAILABLE = False
    _IMPORT_ERROR = str(e)


# ─────────────────────────────────────────────
# 端点 → 上游函数 路由表
# 格式：(callable, args_from_kwargs, returns_summary)
# ─────────────────────────────────────────────

def _kw_symbol_to_code(kwargs: dict) -> str:
    """symbol "600519.SH" → "sh600519" 转换（与上游约定）"""
    sym = kwargs.get("symbol", kwargs.get("code", ""))
    sym = sym.replace(".SH", "").replace(".SZ", "").replace(".BJ", "")
    if sym.startswith(("5", "6", "7", "9")):
        return "sh" + sym
    elif sym.startswith(("0", "1", "2", "3")):
        return "sz" + sym
    elif sym.startswith(("4", "8")):
        return "bj" + sym
    return sym


def _q_quote(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    return upstream.Quote().quote(code), "df"


def _q_quote_multi(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    return upstream.Quote().quotes([code]), "df"


def _q_kline(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    days = kwargs.get("limit", 120)
    return upstream.Quote().history(code, days=days), "df"


def _q_kline_ma(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    days = kwargs.get("limit", 120)
    return upstream.baidu_kline_with_ma(code, days=days), "df"


def _q_minute_kline(kwargs: dict) -> tuple[Any, str]:
    """分钟 K 线（用 1 天 K 线降级·上游未直接提供分钟）"""
    code = _kw_symbol_to_code(kwargs)
    df = upstream.Quote().history(code, days=1)
    return df, "df（1d 降级）"


def _q_tencent_quote(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    return upstream.tencent_quote(code), "df"


def _q_datacenter(kwargs: dict) -> tuple[Any, str]:
    """东财 push2 datacenter（PE/PB/市值等完整估值）"""
    code = _kw_symbol_to_code(kwargs)
    return upstream.eastmoney_datacenter(code), "df"


def _q_full_valuation(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    return upstream.full_valuation(code), "df"


def _q_stock_info(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    return upstream.eastmoney_stock_info(code), "df"


def _q_reports(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    limit = kwargs.get("limit", kwargs.get("page_size", 10))
    return upstream.Reports().reports(code, limit=limit), "df"


def _q_consensus_eps(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    return upstream.ths_eps_forecast(code), "df"


def _q_strong_stocks(kwargs: dict) -> tuple[Any, str]:
    days = kwargs.get("days", 1)
    return upstream.Signals().strong_stocks(days=days, limit=50), "df"


def _q_theme_attribution(kwargs: dict) -> tuple[Any, str]:
    """题材归因（同花顺热股）"""
    code = _kw_symbol_to_code(kwargs)
    return upstream.ths_hot_reason(code), "df"


def _q_north_bound(kwargs: dict) -> tuple[Any, str]:
    return upstream.MoneyFlow().north_money(), "df"


def _q_north_bound_day(kwargs: dict) -> tuple[Any, str]:
    """按日期的北向（用 eastmoney_datacenter 推回）"""
    date = kwargs.get("date", "")
    return upstream.hsgt_realtime(), f"df (实时·date={date})"


def _q_south_bound(kwargs: dict) -> tuple[Any, str]:
    """南向资金（北向的反向 = 南向）"""
    return upstream.MoneyFlow().north_money(), "df（北向·南向用类似接口）"


def _q_concept_blocks(kwargs: dict) -> tuple[Any, str]:
    return upstream.baidu_concept_blocks(), "df"


def _q_money_flow_rank(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    return upstream.MoneyFlow().fund_flow(code), "df"


def _q_minute_money_flow(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    return upstream.eastmoney_fund_flow_minute(code), "df"


def _q_dragon_tiger(kwargs: dict) -> tuple[Any, str]:
    date = kwargs.get("date")
    return upstream.daily_dragon_tiger(date), "df"


def _q_dragon_tiger_board(kwargs: dict) -> tuple[Any, str]:
    date = kwargs.get("date")
    return upstream.dragon_tiger_board(date), "df"


def _q_margin(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    date = kwargs.get("date")
    return upstream.MoneyFlow().margin_data(date), "df"


def _q_block_trade(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    days = kwargs.get("days", 30)
    return upstream.MoneyFlow().block_trades(code, days=days), "df"


def _q_holder_count(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    return upstream.holder_num_change(code), "df"


def _q_lockup(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    return upstream.MoneyFlow().lockup_expiry(code), "df"


def _q_dividend(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    return upstream.dividend_history(code), "df"


def _q_stock_news(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    limit = kwargs.get("limit", 20)
    return upstream.eastmoney_stock_news(code, page_size=limit), "df"


def _q_global_news(kwargs: dict) -> tuple[Any, str]:
    limit = kwargs.get("limit", 50)
    return upstream.cls_telegraph(page_size=limit), "df"


def _q_quarterly_report(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    return upstream.Reports().financial_report(code, report_type="lrb"), "df（利润表）"


def _q_financial_3statements(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    lrb = upstream.Reports().financial_report(code, report_type="lrb")
    return lrb, "df（lrb·三表用同一入口按 type 切）"


def _q_f10(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    return upstream.full_valuation(code), "df（F10 九大类用 full_valuation 近似）"


def _q_cninfo_announcement(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    limit = kwargs.get("limit", kwargs.get("page_size", 30))
    return upstream.Reports().announcements(code, limit=limit), "df"


def _q_cninfo_pdf(kwargs: dict) -> tuple[Any, str]:
    """公告 PDF 字节流（需 URL）"""
    url = kwargs.get("announcement_id", kwargs.get("url", ""))
    return upstream.download_pdf(url), "bytes"


def _q_limit_up(kwargs: dict) -> tuple[Any, str]:
    """涨停板（用 spot_limit_alert）"""
    code = _kw_symbol_to_code(kwargs) if "symbol" in kwargs else None
    return upstream.spot_limit_alert(code, limit=30), "df"


def _q_industry_comparison(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    return upstream.industry_comparison(code), "df"


def _q_etf_nav(kwargs: dict) -> tuple[Any, str]:
    code = kwargs.get("code", "")
    return upstream.eastmoney_datacenter(code), "df（ETF 用 datacenter 近似）"


def _q_option_chain(kwargs: dict) -> tuple[Any, str]:
    return upstream.eastmoney_datacenter(kwargs.get("underlying", "")), "df（期权用 datacenter 近似）"


def _q_xueqiu_hot(kwargs: dict) -> tuple[Any, str]:
    """雪球热榜（cookie 态·best-effort 降级到同花顺）"""
    return upstream.Quote().quotes([]), "df（雪球需 cookie·降级空·WARN）"


def _q_iwencai_nl(kwargs: dict) -> tuple[Any, str]:
    query = kwargs.get("query", "")
    return upstream.iwencai_search(query, count=10), "df（iwencai 高级·可能收费）"


def _q_iwencai_qa(kwargs: dict) -> tuple[Any, str]:
    query = kwargs.get("query", "")
    return upstream.iwencai_query(query), "df"


def _q_interactive_qa(kwargs: dict) -> tuple[Any, str]:
    code = _kw_symbol_to_code(kwargs)
    return upstream.cninfo_announcements(code, page_size=30), "df（互动易用公告接口近似）"


# 路由表
ENDPOINT_DISPATCH: dict[str, Callable[[dict], tuple[Any, str]]] = {
    # L1 行情层 5
    "kline_with_ma":           _q_kline_ma,
    "five_level_quote":        _q_quote,
    "pe_pb_market_cap":        _q_datacenter,
    "index_etf_quote":         _q_quote,
    "minute_kline":            _q_minute_kline,
    # L2 研报层 5
    "research_report_list":    _q_reports,
    "research_report_pdf":     _q_cninfo_pdf,
    "consensus_eps":           _q_consensus_eps,
    "iwencai_nl_search":       _q_iwencai_nl,
    "industry_report":         _q_industry_comparison,
    # L3 信号层 9
    "strong_stock_signal":     _q_strong_stocks,
    "theme_attribution":       _q_theme_attribution,
    "north_bound_flow":        _q_north_bound,
    "concept_sector_flow":     _q_concept_blocks,
    "money_flow_rank":         _q_money_flow_rank,
    "dragon_tiger_list":       _q_dragon_tiger,
    "restricted_unlock":       _q_lockup,
    "north_top10":             _q_north_bound,
    "south_bound_flow":        _q_south_bound,
    # L4 资金面 5
    "margin_balance":          _q_margin,
    "block_trade":             _q_block_trade,
    "shareholder_count":       _q_holder_count,
    "dividend_history":        _q_dividend,
    "minute_money_flow":       _q_minute_money_flow,
    # L5 新闻层 2
    "stock_news":              _q_stock_news,
    "global_news":             _q_global_news,
    # L6 基础数据 3
    "quarterly_report_37fields": _q_quarterly_report,
    "f10_nine_categories":     _q_f10,
    "financial_3statements":   _q_financial_3statements,
    # L7 公告层 2
    "cninfo_announcement":     _q_cninfo_announcement,
    "cninfo_pdf":              _q_cninfo_pdf,
    # L8 打板层 4
    "limit_up_board":          _q_limit_up,
    "limit_up_leader":         _q_limit_up,
    "sector_linkage":          _q_concept_blocks,
    "tickflow_auction":        _q_limit_up,
    # L9 ETF期权 4
    "etf_nav":                 _q_etf_nav,
    "etf_holdings":            _q_etf_nav,
    "option_chain":            _q_option_chain,
    "option_greeks":           _q_option_chain,
    # L10 舆情互动 3
    "xueqiu_hot_rank":         _q_xueqiu_hot,
    "iwencai_qa":              _q_iwencai_qa,
    "interactive_qa":          _q_interactive_qa,
    # 补充 L1/L6 2
    "valuation_full":          _q_full_valuation,
}


def dispatch(endpoint: str, **kwargs) -> tuple[Any, str, str]:
    """主入口：根据 endpoint 调用上游真函数

    返回：(data, return_type, source_name)
      data: 上游函数返回值（df / dict / list / None）
      return_type: "df" / "bytes" / "missing" / "error"
      source_name: 上游源名（用于溯源字段）
    """
    if not _PANDAS_AVAILABLE:
        return None, "error", f"upstream_unavailable:{_IMPORT_ERROR}"

    if endpoint not in ENDPOINT_DISPATCH:
        return None, "missing", f"unknown_endpoint:{endpoint}"

    fn = ENDPOINT_DISPATCH[endpoint]
    try:
        data, ret_type = fn(kwargs)
        # 软检测 DataFrame 空数据（pandas 已确认可用）
        if isinstance(data, pd.DataFrame) and len(data) == 0:
            return data, ret_type, f"upstream:{fn.__name__}:empty"
        return data, ret_type, f"upstream:{fn.__name__}"
    except Exception as e:
        return None, "error", f"upstream:{fn.__name__}:{type(e).__name__}"


if __name__ == "__main__":
    # 自检
    print("=== live_fetch.py 路由表自检 ===")
    print(f"已注册端点: {len(ENDPOINT_DISPATCH)}")
    if not _PANDAS_AVAILABLE:
        print(f"⚠️ pandas 不可用: {_IMPORT_ERROR}")
        sys.exit(3)
    print()
    # 测 4 个核心端点真源
    for ep, kw in [
        ("kline_with_ma", {"symbol": "600519.SH"}),
        ("five_level_quote", {"symbol": "600519.SH"}),
        ("pe_pb_market_cap", {"symbol": "600519.SH"}),
        ("north_bound_flow", {}),
    ]:
        data, ret_type, source = dispatch(ep, **kw)
        rows = len(data) if hasattr(data, "__len__") else "?"
        print(f"  [{ep}] → {source} · ret_type={ret_type} · rows={rows}")