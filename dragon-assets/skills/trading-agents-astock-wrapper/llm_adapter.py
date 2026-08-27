"""llm_adapter.py · trading-agents-astock-wrapper LLM Adapter (阶段 28 重建)"""
from __future__ import annotations
import os, random
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import Any
TZ_CN = timezone(timedelta(hours=8))


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    tokens_used: int = 0
    fetched_at: str = ""

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v}


class LLMProvider:
    name = "abstract"
    default_model = ""


class StubProvider(LLMProvider):
    name = "stub"
    default_model = "stub-v1"
    def call(self, system_prompt, user_prompt, **kwargs):
        return LLMResponse(content=f"[STUB] sys={len(system_prompt)} user={len(user_prompt)}", provider=self.name, model=self.default_model,
                           tokens_used=len(system_prompt)+len(user_prompt), fetched_at=datetime.now(TZ_CN).isoformat(timespec="seconds"))


class OpenAIProvider(LLMProvider):
    name = "openai"
    default_model = "gpt-4-turbo"
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.model = self.default_model
    def call(self, system_prompt, user_prompt, **kwargs):
        if not self.api_key:
            return LLMResponse(content="[OPENAI-STUB] 需 OPENAI_API_KEY", provider=self.name, model=self.model, fetched_at=datetime.now(TZ_CN).isoformat(timespec="seconds"))
        return LLMResponse(content=f"[OPENAI-REAL-STUB] {self.model}", provider=self.name, model=self.model, fetched_at=datetime.now(TZ_CN).isoformat(timespec="seconds"))


class AnthropicProvider(LLMProvider):
    name = "anthropic"
    default_model = "claude-opus-4-8-1m"
    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    def call(self, system_prompt, user_prompt, **kwargs):
        if not self.api_key:
            return LLMResponse(content="[ANTHROPIC-STUB] 需 ANTHROPIC_API_KEY", provider=self.name, model=self.default_model, fetched_at=datetime.now(TZ_CN).isoformat(timespec="seconds"))
        return LLMResponse(content="[ANTHROPIC-REAL-STUB]", provider=self.name, model=self.default_model, fetched_at=datetime.now(TZ_CN).isoformat(timespec="seconds"))


class QwenProvider(LLMProvider):
    name = "qwen"
    default_model = "qwen-turbo"
    def __init__(self):
        self.api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    def call(self, system_prompt, user_prompt, **kwargs):
        if not self.api_key:
            return LLMResponse(content="[QWEN-STUB] 需 DASHSCOPE_API_KEY", provider=self.name, model=self.default_model, fetched_at=datetime.now(TZ_CN).isoformat(timespec="seconds"))
        return LLMResponse(content="[QWEN-REAL-STUB]", provider=self.name, model=self.default_model, fetched_at=datetime.now(TZ_CN).isoformat(timespec="seconds"))


class DeepSeekProvider(LLMProvider):
    name = "deepseek"
    default_model = "deepseek-chat"
    def __init__(self):
        self.api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    def call(self, system_prompt, user_prompt, **kwargs):
        if not self.api_key:
            return LLMResponse(content="[DEEPSEEK-STUB] 需 DEEPSEEK_API_KEY", provider=self.name, model=self.default_model, fetched_at=datetime.now(TZ_CN).isoformat(timespec="seconds"))
        return LLMResponse(content="[DEEPSEEK-REAL-STUB]", provider=self.name, model=self.default_model, fetched_at=datetime.now(TZ_CN).isoformat(timespec="seconds"))


PROVIDERS = {"stub": StubProvider, "openai": OpenAIProvider, "anthropic": AnthropicProvider, "qwen": QwenProvider, "deepseek": DeepSeekProvider}


def get_provider(name=None):
    name = name or os.environ.get("LLM_PROVIDER", "stub")
    cls = PROVIDERS.get(name.lower())
    if not cls:
        raise ValueError(f"未知 LLM Provider: {name}")
    return cls()


def call_llm(system_prompt, user_prompt, provider=None, **kwargs):
    p = get_provider(provider)
    return p.call(system_prompt, user_prompt, **kwargs)


ANALYST_SYSTEM_PROMPTS = {
    "fundamental_analyst": "你是一个 A 股基本面分析师。基于提供的财报三表/季报 37 字段/分红送数据，给出 ROE/毛利率/净利率/营收增长/现金流评分。输出 1-10 评分 + 关键论据 + 结论（buy/hold/sell）。",
    "technical_analyst": "你是一个 A 股技术面分析师。基于 K 线/成交量/MA/MACD/RSI/KDJ/布林带 5 指标，给出趋势/动能/超买超卖/关键位/量价配合评分。",
    "sentiment_analyst": "你是一个 A 股情绪面分析师。基于雪球/同花顺问财/互动易数据，给出讨论热度/看多看空比/机构持仓/散户情绪评分。",
    "valuation_analyst": "你是一个 A 股估值分析师。基于 PE/PB/PS/历史百分位/同业对比，给出估值合理性评分。",
    "risk_analyst": "你是一个 A 股风险评估师。基于波动率/Beta/解禁/大宗交易/融资融券数据，识别市场/政策/流动性/合规/经营 5 类风险。",
    "macro_analyst": "你是一个 A 股宏观分析师。基于利率/CPI/PMI/行业政策数据，给出货币政策/财政政策/行业景气/国际形势评分。",
    "regulatory_analyst": "你是一个 A 股合规分析师。基于公告/监管事件/互动易问答，识别合规记录/监管事件/关联交易/信息披露风险。",
}


def build_analyst_prompt(role, symbol, context=""):
    sys_p = ANALYST_SYSTEM_PROMPTS.get(role, "你是一个 A 股分析师。")
    user_p = f"""请分析 {symbol}：
{context if context else "(无额外数据)"}

输出格式：
- 评分（1-10）
- 关键论据（3 条）
- 结论（buy/hold/sell）
"""
    return sys_p, user_p