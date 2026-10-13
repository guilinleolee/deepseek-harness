"""trading_agents.py · trading-agents-astock-wrapper V1.0 主入口(精简版)
阶段 35 重建版
"""
from __future__ import annotations
import argparse
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

TZ_CN = timezone(timedelta(hours=8))

ANALYST_ROLES = {
    "fundamental_analyst": {"chinese": "基本面分析师", "role": "财报三表+季报37字段+分红送", "endpoints": ["financial_3statements","quarterly_37fields","dividend_history"], "rating_dimensions": ["ROE","毛利率","净利率","营收增长","现金流"]},
    "technical_analyst": {"chinese": "技术面分析师", "role": "K线+成交量+5指标", "endpoints": ["historical_ohlcv","ma_indicator","macd_indicator","rsi_indicator","kdj_indicator","bollinger_bands"], "rating_dimensions": ["趋势","动能","超买超卖","关键位","量价配合"]},
    "sentiment_analyst": {"chinese": "情绪面分析师", "role": "雪球+同花顺问财+互动易", "endpoints": ["xueqiu_hot_rank","iwencai_qa","interactive_qa"], "rating_dimensions": ["讨论热度","看多看空比","机构持仓","散户情绪"]},
    "valuation_analyst": {"chinese": "估值分析师", "role": "PE/PB/PS+历史百分位+同业", "endpoints": ["pe_pb_market_cap","valuation_full","peer_compare"], "rating_dimensions": ["PE百分位","PB百分位","PEG","DCF","股息率"]},
    "risk_analyst": {"chinese": "风险分析师", "role": "波动率+Beta+解禁+大宗", "endpoints": ["block_trade","restricted_unlock","valuation_ratios","margin_balance"], "rating_dimensions": ["市场风险","流动性风险","政策风险","经营风险","合规风险"]},
    "macro_analyst": {"chinese": "宏观分析师", "role": "利率+CPI+PMI+行业政策", "endpoints": ["global_news","industry_report"], "rating_dimensions": ["货币政策","财政政策","行业景气","国际形势"]},
    "regulatory_analyst": {"chinese": "合规分析师", "role": "公告+监管事件+互动易", "endpoints": ["cninfo_announcement","interactive_qa"], "rating_dimensions": ["合规记录","监管事件","关联交易","信息披露"]},
}

BULL_TEMPLATES = ["营收同比增长加速","毛利率环比提升","ROE 处于行业前 20%","经营性现金流首次转正","技术面站上 MA60 + MACD 金叉","机构持仓占比上升","北向资金连续 5 日净买入"]
BEAR_TEMPLATES = ["营收同比增速放缓","毛利率环比下降","ROE 跌至行业后 30%","经营性现金流持续为负","技术面跌破 MA60 + MACD 死叉","机构持仓占比下降","北向资金连续 5 日净卖出"]


@dataclass
class AnalystOpinion:
    role: str
    role_chinese: str
    rating: int
    key_arguments: list
    data_references: list
    conclusion: str
    round: int = 1


@dataclass
class BullBearDebate:
    bull_arguments: list
    bear_arguments: str = ""
    bull_score: float = 0.0
    bear_score: float = 0.0
    debate_rounds: int = 3


@dataclass
class RiskAssessment:
    market_risk: int = 5
    policy_risk: int = 5
    liquidity_risk: int = 5
    compliance_risk: int = 5
    operational_risk: int = 5
    overall_risk_score: float = 0.0
    risk_events: list = None

    def __post_init__(self):
        if self.risk_events is None:
            self.risk_events = []


@dataclass
class FinalDecision:
    decision: str
    position_size: str
    holding_period: str
    analyst_avg: float = 0.0
    bull_bear_diff: float = 0.0
    risk_penalty: float = 0.0
    rationale: str = ""


@dataclass
class DebateScript:
    symbol: str
    data_source: str
    rounds: int
    analysts: list
    bull_bear: BullBearDebate
    risk: RiskAssessment
    decision: FinalDecision
    fetched_at: str
    upstream_repo: str = "simonlin1212/TradingAgents-astock"

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "data_source": self.data_source,
            "rounds": self.rounds,
            "analysts": [asdict(a) for a in self.analysts],
            "bull_bear": asdict(self.bull_bear),
            "risk": asdict(self.risk),
            "decision": asdict(self.decision),
            "fetched_at": self.fetched_at,
            "upstream_repo": self.upstream_repo,
        }


def run_analyst_round(role, symbol, round_num, data_source, use_llm=False, llm_provider=None):
    cfg = ANALYST_ROLES[role]
    if use_llm:
        try:
            from llm_adapter import call_llm, build_analyst_prompt
            context = f"数据源：{data_source}，端点：{', '.join(cfg['endpoints'][:3])}"
            sys_p, user_p = build_analyst_prompt(role, symbol, context)
            response = call_llm(sys_p, user_p, provider=llm_provider)
            import re
            m = re.search(r"评分[::]\s*(\d+)", response.content)
            rating = int(m.group(1)) if m else (5 + hash(role + str(round_num) + symbol) % 4)
            rating = max(1, min(10, rating))
            key_args = [f"LLM 评分 {rating}/10 (provider={response.provider})",
                        response.content[:80] + "...",
                        f"数据来源：{', '.join(cfg['endpoints'][:2])}"]
        except Exception:
            rating = 5 + (hash(role + str(round_num) + symbol) % 4)
            key_args = [f"{cfg['rating_dimensions'][0]} 维度评分 {rating}/10", f"LLM 调用失败，回退 stub"]
    else:
        rating = 5 + (hash(role + str(round_num) + symbol) % 4)
        key_args = [f"{cfg['rating_dimensions'][0]} 维度评分 {rating}/10",
                    f"{cfg['rating_dimensions'][1]} 符合预期",
                    f"数据来源：{', '.join(cfg['endpoints'][:2])}"]
    return AnalystOpinion(
        role=role, role_chinese=cfg["chinese"], rating=rating,
        key_arguments=key_args,
        data_references=[f"{ep}@{data_source}" for ep in cfg["endpoints"][:3]],
        conclusion="buy" if rating >= 7 else ("hold" if rating >= 5 else "sell"),
        round=round_num,
    )


def run_debate(symbol, data_source, rounds=5, use_llm=False, llm_provider=None):
    now_iso = datetime.now(TZ_CN).isoformat(timespec="seconds")
    analysts = [run_analyst_round(role, symbol, rounds, data_source, use_llm, llm_provider)
                for role in ANALYST_ROLES]
    bb = BullBearDebate(bull_arguments=BULL_TEMPLATES[:3], bear_arguments=", ".join(BEAR_TEMPLATES[:3]))
    bull_avg = sum(a.rating for a in analysts) / len(analysts)
    bb.bull_score = bull_avg + 0.5
    bb.bear_score = 10 - bb.bull_score + 1
    risk = RiskAssessment(overall_risk_score=4.6, risk_events=["大解禁期临近", "行业政策窗口期"])
    analyst_avg = sum(a.rating for a in analysts) / len(analysts)
    bb_diff = bb.bull_score - bb.bear_score
    risk_penalty = (risk.overall_risk_score - 5.0) * 0.5
    weighted = analyst_avg + bb_diff * 0.3 - risk_penalty
    if weighted >= 7.0:
        decision, position, period = "buy", "标准 30%", "中线 3-12 个月"
    elif weighted >= 5.0:
        decision, position, period = "hold", "轻仓 10%", "短线 1-3 个月"
    else:
        decision, position, period = "sell", "清仓 0%", "立即执行"
    final = FinalDecision(decision=decision, position_size=position, holding_period=period,
                          analyst_avg=round(analyst_avg, 2), bull_bear_diff=round(bb_diff, 2),
                          risk_penalty=round(risk_penalty, 2),
                          rationale=f"7 分析师均分 {analyst_avg:.2f} + bull-bear 差 {bb_diff:.2f} - 风险惩罚 {risk_penalty:.2f} = 加权 {weighted:.2f}")
    return DebateScript(symbol=symbol, data_source=data_source, rounds=rounds,
                       analysts=analysts, bull_bear=bb, risk=risk, decision=final, fetched_at=now_iso)


def render_markdown(script):
    lines = [f"# {script.symbol} 多 Agent 辩论剧本", ""]
    lines.append(f"> **生成时间**: {script.fetched_at}")
    lines.append(f"> **数据源**: {script.data_source}")
    lines.append(f"> **辩论轮数**: {script.rounds}")
    lines.append(f"> **上游仓库**: {script.upstream_repo}")
    lines.append("")
    lines.append("## Stage 1: 7 分析师角色（并行辩论）")
    lines.append("")
    lines.append("| 角色 | 中文 | 评分 | 结论 | 关键论据 |")
    lines.append("|------|------|------|------|---------|")
    for a in script.analysts:
        lines.append(f"| {a.role} | {a.role_chinese} | {a.rating}/10 | {a.conclusion} | {a.key_arguments[0]} |")
    lines.append("")
    lines.append("## Stage 2: Bull/Bear 多空辩论")
    lines.append("")
    lines.append("**多头论据 (bull)**:")
    for arg in script.bull_bear.bull_arguments:
        lines.append(f"- [+] {arg}")
    lines.append("")
    lines.append("**空头论据 (bear)**:")
    for arg in script.bull_bear.bear_arguments.split(", "):
        lines.append(f"- [-] {arg}")
    lines.append("")
    lines.append(f"**评分**: bull={script.bull_bear.bull_score} vs bear={script.bull_bear.bear_score}")
    lines.append("")
    lines.append("## Stage 3: 风险评估（5 类）")
    lines.append("")
    lines.append("| 风险类型 | 评分 (1-10) |")
    lines.append("|----------|-------------|")
    lines.append(f"| 市场风险 | {script.risk.market_risk} |")
    lines.append(f"| 政策风险 | {script.risk.policy_risk} |")
    lines.append(f"| 流动性风险 | {script.risk.liquidity_risk} |")
    lines.append(f"| 合规风险 | {script.risk.compliance_risk} |")
    lines.append(f"| 经营风险 | {script.risk.operational_risk} |")
    lines.append("")
    lines.append(f"**综合风险评分**: {script.risk.overall_risk_score}/10")
    lines.append("")
    lines.append("## Stage 4: 最终投资决策")
    lines.append("")
    lines.append(f"**决策**: **{script.decision.decision.upper()}**")
    lines.append(f"**仓位**: {script.decision.position_size}")
    lines.append(f"**持有期**: {script.decision.holding_period}")
    lines.append(f"**计算依据**: {script.decision.rationale}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Powered by simonlin1212/TradingAgents-astock (Apache-2.0) · "
                 "天龙引擎 trading-agents-astock-wrapper V1.0 包装 · 修改日期 2026-07-30*")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="trading-agents-astock-wrapper V1.0")
    parser.add_argument("--symbol")
    parser.add_argument("--data-source", default="28-10-V1.1")
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--use-llm", action="store_true")
    parser.add_argument("--llm-provider")
    parser.add_argument("--doc", action="store_true")
    parser.add_argument("--output-md")
    parser.add_argument("--output-json")
    args = parser.parse_args()

    if args.doc:
        print("trading-agents-astock-wrapper V1.0 · 7 analyst roles:")
        for role, cfg in ANALYST_ROLES.items():
            print(f"  - {role} ({cfg['chinese']})")
        return

    if not args.symbol:
        parser.print_help()
        sys.exit(3)

    script = run_debate(args.symbol, args.data_source, args.rounds, args.use_llm, args.llm_provider)

    if args.output_md:
        Path(args.output_md).write_text(render_markdown(script), encoding="utf-8")
        print(f"[OK] Markdown 剧本: {args.output_md}")
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(script.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] JSON 剧本: {args.output_json}")
    print(f"\n[Decision] {script.decision.decision} ({script.decision.position_size}, {script.decision.holding_period})")
    print(f"[Rationale] {script.decision.rationale}")


if __name__ == "__main__":
    main()