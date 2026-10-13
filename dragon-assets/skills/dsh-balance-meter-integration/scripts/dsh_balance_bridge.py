"""
dsh-balance-meter-bridge V1.0 · DSH 余额读取 + cost 估算天龙桥

================================================================================
  Stage 45.1 · 2026-08-24

设计：
  - 借鉴 stage 44 trajectory-debug-bridge 模式（unified-api-client 风格）
  - 不调用上游 lib/（避免 DSH 主仓 peer 依赖）；纯 Python wrapper
  - 暴露 4 RPC：balance.get / session.cost / pricing.refresh / ledger.snapshot
  - sklearn-free / 仅 urllib（stage 44 bridge.py 同款）
  - 退出码契约：0=OK / 1=BALANCE_FETCH_FAIL / 2=PARSE_ERR / 3=CONFIG_ERR
================================================================================
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

# 配置常量
DEFAULT_DSH_BASE = os.environ.get("DSH_BASE_URL", "http://127.0.0.1:3080")
DEFAULT_API_BASE = "https://api.deepseek.com"
DEFAULT_BALANCE_PATH = "/user/balance"

EXIT_OK = 0
EXIT_BALANCE_FETCH_FAIL = 1
EXIT_PARSE_ERR = 2
EXIT_CONFIG_ERR = 3


# ==============================================================================
# 1. pricing 模型（参考 stage 44 paperclip-cost-control V2.0 + DeepSeek peak/off-peak）
# ==============================================================================

# DeepSeek 2026-08-17 后的 peak/off-peak 双价（CNY per 1M tokens）
# Built-in preset fallback
DEFAULT_PRICING = {
    "deepseek-v4-flash": {
        "off_peak": {"input": 0.02, "cache_read": 0.02, "cache_write": 0.0, "output": 1.00},
        "peak":     {"input": 0.04, "cache_read": 0.04, "cache_write": 0.0, "output": 2.00},
    },
    "deepseek-v4-pro": {
        "off_peak": {"input": 0.20, "cache_read": 0.20, "cache_write": 0.0, "output": 4.00},
        "peak":     {"input": 0.40, "cache_read": 0.40, "cache_write": 0.0, "output": 8.00},
    },
    # 旧名 fallback 同 flash
    "deepseek-chat": {
        "off_peak": {"input": 0.02, "cache_read": 0.02, "cache_write": 0.0, "output": 1.00},
        "peak":     {"input": 0.04, "cache_read": 0.04, "cache_write": 0.0, "output": 2.00},
    },
}


def is_peak_hour(beijing_dt: Optional[datetime] = None) -> bool:
    """北京时 09:00-12:00 / 14:00-18:00 为 peak"""
    dt = beijing_dt or datetime.now(timezone(timedelta(hours=8)))
    h = dt.hour
    return (9 <= h < 12) or (14 <= h < 18)


def get_pricing(model: str, band: Optional[str] = None) -> Dict[str, float]:
    """返回指定 model 当前应使用的价格（CNY per 1M tokens）"""
    band = band or ("peak" if is_peak_hour() else "off_peak")
    m = DEFAULT_PRICING.get(model, DEFAULT_PRICING["deepseek-v4-flash"])
    return m[band]


# ==============================================================================
# 2. 余额读取（3 source 借鉴 dsh-balance-meter README）
# ==============================================================================

def read_balance_official(api_key: str, api_base: str = DEFAULT_API_BASE) -> Dict[str, Any]:
    """official source · DeepSeek /user/balance"""
    url = f"{api_base}{DEFAULT_BALANCE_PATH}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"ok": False, "source": "official", "error": {"code": e.code, "message": e.reason}}
    except (TimeoutError, json.JSONDecodeError, urllib.error.URLError) as e:
        return {"ok": False, "source": "official", "error": {"code": "conn_or_parse", "message": str(e)}}

    # DeepSeek balance_infos schema: list of {currency, total_balance, granted, topped_up}
    balance_infos = payload.get("balance_infos", [])
    if not balance_infos:
        return {"ok": False, "source": "official", "error": {"code": "empty", "message": "no balance_infos"}}

    # return first non-zero currency
    for info in balance_infos:
        currency = info.get("currency", "CNY")
        total = float(info.get("total_balance", 0))
        if total > 0:
            return {
                "ok": True,
                "source": "official",
                "currency": currency,
                "total_balance": total,
                "granted": float(info.get("granted_balance", 0)),
                "topped_up": float(info.get("topped_up_balance", 0)),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

    return {"ok": False, "source": "official", "error": {"code": "all_zero", "message": "all balance_infos zero"}}


def read_balance_proxy(api_key: str, endpoint: str, currency_path: str = "data.balance", proxy_currency: str = "CNY") -> Dict[str, Any]:
    """proxy source · custom endpoint + Bearer + 数字路径"""
    req = urllib.request.Request(endpoint, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"ok": False, "source": "proxy", "error": {"code": "conn_or_parse", "message": str(e)}}

    # dot-path 解析
    parts = currency_path.split(".")
    val = payload
    for p in parts:
        if isinstance(val, dict):
            val = val.get(p)
        else:
            return {"ok": False, "source": "proxy", "error": {"code": "bad_path", "message": currency_path}}
    try:
        amount = float(val)
    except (TypeError, ValueError):
        return {"ok": False, "source": "proxy", "error": {"code": "non_numeric", "message": str(val)}}

    return {
        "ok": True,
        "source": "proxy",
        "currency": proxy_currency,
        "total_balance": amount,
        "granted": amount,
        "topped_up": 0.0,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def read_balance_manual(manual_balance: float, manual_currency: str = "CNY") -> Dict[str, Any]:
    """manual source · 本地 ledger 基线"""
    return {
        "ok": True,
        "source": "manual",
        "currency": manual_currency,
        "total_balance": float(manual_balance),
        "granted": float(manual_balance),
        "topped_up": 0.0,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


# ==============================================================================
# 3. 单 session cost 估算（4 buckets + per-model pricing）
# ==============================================================================

def estimate_session_cost(
    *,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_read_tokens: int = 0,
    cache_write_tokens: int = 0,
    model: str = "deepseek-v4-flash",
    band: Optional[str] = None,
) -> Dict[str, float]:
    """单 session cost 估算（CNY）"""
    pricing = get_pricing(model, band)
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    cache_r_cost = (cache_read_tokens / 1_000_000) * pricing["cache_read"]
    cache_w_cost = (cache_write_tokens / 1_000_000) * pricing["cache_write"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    total = input_cost + cache_r_cost + cache_w_cost + output_cost

    return {
        "model": model,
        "band": band or ("peak" if is_peak_hour() else "off_peak"),
        "input_cost_cny": round(input_cost, 4),
        "cache_read_cost_cny": round(cache_r_cost, 4),
        "cache_write_cost_cny": round(cache_w_cost, 4),
        "output_cost_cny": round(output_cost, 4),
        "total_cost_cny": round(total, 4),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_read_tokens": cache_read_tokens,
        "cache_write_tokens": cache_write_tokens,
    }


# ==============================================================================
# 4. local ledger snapshot（manual 模式持久化）
# ==============================================================================

@dataclass
class LedgerSnapshot:
    """manual 模式本地 ledger 快照"""
    baseline: float
    remaining: float
    spent: float
    currency: str = "CNY"
    sessions: List[Dict[str, Any]] = field(default_factory=list)
    updated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def load_ledger(ledger_path: str) -> LedgerSnapshot:
    """从 DSH settings namespace 加载 ledger JSON"""
    try:
        with open(ledger_path, encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return LedgerSnapshot(baseline=0, remaining=0, spent=0)
    return LedgerSnapshot(
        baseline=float(data.get("baseline", 0)),
        remaining=float(data.get("remaining", 0)),
        spent=float(data.get("spent", 0)),
        currency=data.get("currency", "CNY"),
        sessions=data.get("sessions", []),
        updated_at=data.get("updated_at", ""),
    )


# ==============================================================================
# CLI
# ==============================================================================

def cmd_balance(args: argparse.Namespace) -> int:
    api_key = args.api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key and args.source != "manual":
        print("[ERROR] DEEPSEEK_API_KEY not set", file=sys.stderr)
        return EXIT_CONFIG_ERR

    if args.source == "official":
        result = read_balance_official(api_key, args.api_base)
    elif args.source == "proxy":
        result = read_balance_proxy(api_key, args.endpoint, args.currency_path, args.proxy_currency)
    elif args.source == "manual":
        result = read_balance_manual(args.manual_balance, args.manual_currency)
    else:
        print(f"[ERROR] unknown source: {args.source}", file=sys.stderr)
        return EXIT_CONFIG_ERR

    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result.get("ok"):
        return EXIT_BALANCE_FETCH_FAIL
    return EXIT_OK


def cmd_session_cost(args: argparse.Namespace) -> int:
    """单 session cost 估算"""
    result = estimate_session_cost(
        input_tokens=args.input,
        output_tokens=args.output,
        cache_read_tokens=args.cache_read,
        cache_write_tokens=args.cache_write,
        model=args.model,
        band=args.band,  # 修正 bug：之前缺这行导致 --band 参数丢失
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_pricing_demo(args: argparse.Namespace) -> int:
    """当前 peak/off-peak 价格 demo"""
    pricing = get_pricing(args.model)
    band = "peak" if is_peak_hour() else "off_peak"
    print(json.dumps({
        "model": args.model,
        "band_now": band,
        "pricing_cny_per_1M": pricing,
        "is_peak_now": is_peak_hour(),
    }, indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_ledger_demo(args: argparse.Namespace) -> int:
    snap = load_ledger(args.ledger_path)
    print(json.dumps(snap.to_dict(), indent=2, ensure_ascii=False))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dsh_balance_bridge",
        description="Stage 45.1 dsh-balance-meter-bridge V1.0 · BSD-3-Clause",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp_balance = sub.add_parser("balance", help="读余额（3 source）")
    sp_balance.add_argument("--source", choices=["official", "proxy", "manual"], required=True)
    sp_balance.add_argument("--api-key", help="DeepSeek API key (or env DEEPSEEK_API_KEY)")
    sp_balance.add_argument("--api-base", default=DEFAULT_API_BASE)
    sp_balance.add_argument("--endpoint", help="proxy source URL")
    sp_balance.add_argument("--currency-path", default="data.balance")
    sp_balance.add_argument("--proxy-currency", default="CNY")
    sp_balance.add_argument("--manual-balance", type=float, default=0)
    sp_balance.add_argument("--manual-currency", default="CNY")
    sp_balance.set_defaults(func=cmd_balance)

    sp_cost = sub.add_parser("session-cost", help="单 session cost 估算")
    sp_cost.add_argument("--input", type=int, default=0)
    sp_cost.add_argument("--output", type=int, default=0)
    sp_cost.add_argument("--cache-read", type=int, default=0)
    sp_cost.add_argument("--cache-write", type=int, default=0)
    sp_cost.add_argument("--model", default="deepseek-v4-flash")
    sp_cost.add_argument("--band", choices=["off_peak", "peak"], help="(可选) 强制 band，否则按当前 Beijing 时间自动判断")
    sp_cost.set_defaults(func=cmd_session_cost)

    sp_pricing = sub.add_parser("pricing-demo", help="peak/off-peak 价格 demo")
    sp_pricing.add_argument("--model", default="deepseek-v4-flash")
    sp_pricing.set_defaults(func=cmd_pricing_demo)

    sp_ledger = sub.add_parser("ledger-demo", help="local ledger 快照")
    sp_ledger.add_argument("--ledger-path", required=True)
    sp_ledger.set_defaults(func=cmd_ledger_demo)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
