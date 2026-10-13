"""
dsh-trajectory-bridge · Python 入口（天龙风格的 unified-api-client wrapper）

================================================================================
  Stage 40 · 2026-08-24

设计：
  - 不破坏上游 MIT 协议；纯 client，wrapper 厚度 ≈ 80 行
  - 不依赖 @deepseek-ai/dsh Host runtime；通过 dsh webserver 公开的
    POST /api/trajectory-debug/rpc 调用
  - 输出统一 JSON / Python dict，喂给 session-distiller / meta-prism / paperclip
  - 与 anysearch V1.0 风格一致：
        dsh_trajectory_bridge.py <command> [args]
        退出码契约：0=OK / 1=DSH 连接失败 / 2=方法错误 / 3=参数错误 / 4=5xx
================================================================================
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

DEFAULT_DSH_BASE = "http://127.0.0.1:3080"
RPC_PATH = "/api/trajectory-debug/rpc"
EXIT_OK = 0
EXIT_CONN = 1
EXIT_METHOD = 2
EXIT_ARGS = 3
EXIT_5XX = 4


# ==============================================================================
# 1. 7 大 RPC 方法（与上游 CHANGELOG v0.2.0 / transport.spec.ts 完全对齐）
# ==============================================================================

RPC_METHODS = {
    # ─── 查询类 ───
    "trajectory.list": "List all sessions with trajectory",
    "step.context": "Get the step context (model view + action) at step <seq>",
    "perf": "Performance dashboard: success / percentile / token / TTFT / cost",

    # ─── 回放类 ───
    "replay.start": "Start a deterministic replay session from step 0",
    "replay.step": "Advance the replay cursor by 1 step",
    "replay.seek": "Seek to a specific step",

    # ─── 断点类 ───
    "breakpoint.set": "Set a breakpoint at <agent>/<pre-step>",
    "breakpoint.remove": "Remove a breakpoint by id",
    "breakpoint.list": "List active breakpoints",
    "breakpoint.resume": "Resume a paused breakpoint",

    # ─── 干预类 ───
    "intervention.rerunTool": "Re-run a tool with new params (strategy: record|sandbox|ask)",

    # ─── 分叉类 ───
    "variant.fork": "Fork a new variant from a base + head",
    "variant.list": "List variants of a session",
    "variant.compare": "Compare two variants (diff + summary)",

    # ─── 导出类 ───
    "export": "Export trace in OTel GenAI format (default) or JSON",
}


# ==============================================================================
# 2. RPC 客户端
# ==============================================================================

class DshTrajectoryRPC:
    """轻量 HTTP RPC 客户端，对应 webserver 自定义路由 POST /api/trajectory-debug/rpc"""

    def __init__(self, base_url: str = DEFAULT_DSH_BASE, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def call(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if method not in RPC_METHODS:
            return {"ok": False, "error": {"code": "unknown_method", "method": method}}

        url = f"{self.base_url}{RPC_PATH}"
        body = json.dumps({"method": method, "params": params or {}}).encode("utf-8")
        req = urllib.request.Request(
            url, data=body, method="POST",
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = resp.read().decode("utf-8")
                data = json.loads(payload)
        except urllib.error.HTTPError as e:
            return {"ok": False, "error": {"code": e.code, "message": e.reason}}
        except urllib.error.URLError as e:
            return {"ok": False, "error": {"code": "conn_refused", "message": str(e.reason)}}
        except (TimeoutError, json.JSONDecodeError) as e:
            return {"ok": False, "error": {"code": "parse_error", "message": str(e)}}

        # 上游返回 {ok, value|error}
        if not data.get("ok"):
            err = data.get("error", {})
            return {"ok": False, "error": err}
        return {"ok": True, "value": data.get("value")}


# ==============================================================================
# 3. CLI 命令树
# ==============================================================================

def cmd_list_methods(_: argparse.Namespace) -> int:
    """列出所有 RPC 方法 + 简介"""
    print("== dsh-trajectory-bridge · 14 RPC methods ==")
    for m, desc in RPC_METHODS.items():
        print(f"  {m:<28} {desc}")
    return EXIT_OK


def cmd_call(args: argparse.Namespace) -> int:
    """通用 RPC 调用：dsh-trajectory-bridge call <method> --json '<params>'"""
    params = {}
    if args.json:
        try:
            params = json.loads(args.json)
        except json.JSONDecodeError as e:
            print(f"[args] JSON parse error: {e}", file=sys.stderr)
            return EXIT_ARGS
    rpc = DshTrajectoryRPC(args.base_url)
    result = rpc.call(args.method, params)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return EXIT_OK if result.get("ok") else EXIT_METHOD


def cmd_trajectory_list(args: argparse.Namespace) -> int:
    """alias: trajectory.list"""
    rpc = DshTrajectoryRPC(args.base_url)
    result = rpc.call("trajectory.list", {"limit": args.limit})
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return EXIT_OK if result.get("ok") else EXIT_METHOD


def cmd_perf(args: argparse.Namespace) -> int:
    """alias: perf（支持价格表 → cost 估算）"""
    price = {}
    if args.price:
        try:
            price = json.loads(args.price)
        except json.JSONDecodeError as e:
            print(f"[price] JSON parse error: {e}", file=sys.stderr)
            return EXIT_ARGS
    rpc = DshTrajectoryRPC(args.base_url)
    result = rpc.call("perf", {"sessionId": args.session, "tokenPriceTable": price})
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return EXIT_OK if result.get("ok") else EXIT_METHOD


def cmd_replay_step(args: argparse.Namespace) -> int:
    """alias: replay.step（确定性回放下一步）"""
    rpc = DshTrajectoryRPC(args.base_url)
    result = rpc.call("replay.step", {"replayId": args.replay_id, "delta": 1})
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return EXIT_OK if result.get("ok") else EXIT_METHOD


def cmd_export(args: argparse.Namespace) -> int:
    """alias: export（OTel GenAI trace）"""
    rpc = DshTrajectoryRPC(args.base_url)
    result = rpc.call("export", {"sessionId": args.session, "format": "trace"})
    if result.get("ok"):
        out = args.output or "trace.jsonl"
        with open(out, "w", encoding="utf-8") as f:
            payload = result["value"]
            if isinstance(payload, list):
                for span in payload:
                    f.write(json.dumps(span, ensure_ascii=False) + "\n")
            else:
                f.write(json.dumps(payload, ensure_ascii=False))
        print(f"[export] wrote {out}")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    return EXIT_OK if result.get("ok") else EXIT_METHOD


def cmd_healthcheck(args: argparse.Namespace) -> int:
    """Health check：探测 DSH webserver 是否跑 trajectory-debug RPC"""
    import socket
    try:
        from urllib.parse import urlparse
        u = urlparse(args.base_url)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect((u.hostname or "127.0.0.1", u.port or 3080))
        sock.close()
    except Exception as e:
        print(f"[FAIL] cannot reach {args.base_url}: {e}", file=sys.stderr)
        return EXIT_CONN

    # ping 一个轻量 RPC 方法
    rpc = DshTrajectoryRPC(args.base_url)
    result = rpc.call("trajectory.list", {"limit": 1})
    if result.get("ok"):
        print(f"[OK] DSH trajectory-debug RPC responds at {args.base_url}")
        return EXIT_OK
    elif result.get("error", {}).get("code") == "conn_refused":
        print(f"[FAIL] DSH up but trajectory-debug RPC not registered", file=sys.stderr)
        return EXIT_METHOD
    else:
        print(f"[FAIL] unexpected: {result}", file=sys.stderr)
        return EXIT_5XX


# ==============================================================================
# 4. 主程序
# ==============================================================================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dsh_trajectory_bridge",
        description="天龙 dsh-trajectory-bridge · 14 RPC methods · MIT",
    )
    p.add_argument("--base-url", default=DEFAULT_DSH_BASE,
                   help=f"DSH webserver URL (default: {DEFAULT_DSH_BASE})")

    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("list-methods", help="列出所有 RPC 方法")
    sp.set_defaults(func=cmd_list_methods)

    sp = sub.add_parser("call", help="通用 RPC 调用")
    sp.add_argument("method", help=f"RPC 方法名（可用 list-methods 查）")
    sp.add_argument("--json", help="参数字符串，例: '{\"sessionId\":\"abc\",\"limit\":10}'")
    sp.set_defaults(func=cmd_call)

    sp = sub.add_parser("list", help="列出全部 trajectory 会话（alias trajectory.list）")
    sp.add_argument("--limit", type=int, default=20, help="最多 N 条")
    sp.set_defaults(func=cmd_trajectory_list)

    sp = sub.add_parser("perf", help="性能 dashboard（带 cost 估算）")
    sp.add_argument("--session", required=True, help="会话 ID")
    sp.add_argument("--price", help="价格表 JSON，例: '{\"openai\":{\"input\":2.5,\"output\":10}}'")
    sp.set_defaults(func=cmd_perf)

    sp = sub.add_parser("replay-step", help="回放 +1 步")
    sp.add_argument("--replay-id", required=True, help="replay session id")
    sp.set_defaults(func=cmd_replay_step)

    sp = sub.add_parser("export", help="导出 OTel GenAI trace")
    sp.add_argument("--session", required=True, help="会话 ID")
    sp.add_argument("--output", help="输出文件（默认 trace.jsonl）")
    sp.set_defaults(func=cmd_export)

    sp = sub.add_parser("healthcheck", help="健康检查")
    sp.set_defaults(func=cmd_healthcheck)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
