#!/usr/bin/env python3
"""Quant research kernel (phase 1): one NDJSON request per process.

The TS plugin spawns ``python main.py`` per request, writes one request line
on stdin, and reads one response line on stdout. The kernel is a pure
calculator over its inputs — ``get_kline`` (synthetic deterministic walk or
akshare with an on-disk cache) and ``backtest`` (daily SMA-cross simulator
over caller-supplied bars). Stderr carries diagnostics only; the protocol
never writes anything but the single response line on stdout.

Usage: ``echo '<request>' | python main.py``
"""

import json
import sys
from pathlib import Path

# Allow running both as a module and as a plain script from any cwd.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pdat.datasource import ConfigError, fetch_kline  # noqa: E402
from pcpt.backtest import run_backtest  # noqa: E402
from utils.python_logger import log_debug, log_error  # noqa: E402

PROTOCOL_VERSION = 1


def _fail(request_id: str, code: str, message: str) -> dict:
    """Build one failure response line."""
    return {"id": request_id, "ok": False, "error": {"code": code, "message": message}}


def _handle_ping(params: dict) -> dict:
    """Liveness probe: no I/O, no dependencies."""
    del params
    return {"protocol": PROTOCOL_VERSION, "python": sys.version.split()[0]}


def _handle_get_kline(params: dict) -> dict:
    """Fetch one daily kline series through the pdat layer."""
    for field in ("source", "symbol", "bars"):
        if field not in params:
            raise ValueError(f"get_kline 缺少参数 {field}")
    return fetch_kline(
        source=params["source"],
        symbol=params["symbol"],
        period=params.get("period", "daily"),
        bars=params["bars"],
        max_retries=params.get("max_retries", 0),
        cache_dir=params.get("cache_dir"),
    )


def _handle_backtest(params: dict) -> dict:
    """Run the daily SMA-cross simulator over caller-supplied bars."""
    for field in ("bars", "fast", "slow", "initial_cash", "fee_rate"):
        if field not in params:
            raise ValueError(f"backtest 缺少参数 {field}")
    return run_backtest(
        bars=params["bars"],
        fast=params["fast"],
        slow=params["slow"],
        initial_cash=params["initial_cash"],
        fee_rate=params["fee_rate"],
        symbol=params.get("symbol", ""),
    )


HANDLERS = {
    "ping": _handle_ping,
    "get_kline": _handle_get_kline,
    "backtest": _handle_backtest,
}


def _error_code(exc: Exception) -> str:
    """Map one handler failure onto the wire error codes."""
    if isinstance(exc, ConfigError):
        return "CONFIG_ERROR"
    if isinstance(exc, ValueError):
        return "BAD_REQUEST"
    if isinstance(exc, ConnectionError):
        return "NETWORK_ERROR"
    return "DATA_ERROR"


def main() -> int:
    """Read one request line, answer one response line."""
    line = sys.stdin.readline()
    if not line.strip():
        log_error("空请求：未收到任何输入行")
        return 1
    try:
        request = json.loads(line)
    except json.JSONDecodeError as exc:
        log_error(f"请求不是合法 JSON：{exc}")
        return 1
    request_id = request.get("id", "")
    op = request.get("op", "")
    if request.get("protocol") != PROTOCOL_VERSION:
        response = _fail(request_id, "BAD_REQUEST", f"协议版本不支持：{request.get('protocol')}")
    elif op not in HANDLERS:
        response = _fail(request_id, "BAD_REQUEST", f"未知操作：{op}")
    else:
        try:
            response = {"id": request_id, "ok": True, "result": HANDLERS[op](request.get("params") or {})}
            log_debug(f"{op} 完成")
        except Exception as exc:  # noqa: BLE001 — the wire boundary reports every failure class
            log_error(f"{op} 失败：{exc}")
            response = _fail(request_id, _error_code(exc), str(exc))
    sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
