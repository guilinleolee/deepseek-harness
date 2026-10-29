#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-runtime.py · 运行时依赖体检
========================================================

在报价或交付之前，检查本机配置能否真正跑通各条能力路径。

每条路径给出四种结论之一：
  ok    — 配置正确且可达
  auth  — 凭据被拒（401/403）：key 无效或缺失
  quota — 余额或配额不足（402）：key 有效但账户没钱
  cfg   — 配置错误（404/400）：base URL 或端点不对
  net   — 网络不可达（连接失败）
  skip  — 该路径不适用（例如没有装某个可选后端）

当前默认工作后端是 MiniMax Code Plan：文本走本地代理
（ANTHROPIC_BASE_URL，默认 http://127.0.0.1:15721），出图走官方 API。
DeepSeek 一路只在用 DeepSeek 账户时需要。

用法：
    python check-runtime.py            # 检查全部
    python check-runtime.py --json     # 机器可读输出
    python check-runtime.py --only deepseek,mupapi

退出码：0 = 全部可用或跳过的路径均正常；1 = 有路径不可用。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Dict, List, Optional, Tuple

# DeepSeek Messages API 的正确 base（含 /anthropic 后缀）
DEEPSEEK_MESSAGES_BASE = "https://api.deepseek.com/anthropic"
# DeepSeek Search / Fetch API 的 base
DEEPSEEK_TOOLS_BASE = "https://api.deepseek.com/v1/tools"
# muapi 的生成入口
MUAPI_BASE = "https://api.muapi.ai/v1"


def probe(
    url: str,
    headers: Dict[str, str],
    payload: Optional[Dict[str, object]] = None,
    timeout: int = 45,
) -> Tuple[str, str]:
    """Probe one endpoint and classify the outcome.

    :returns: (verdict, detail) where verdict is ok, auth, quota, cfg, or net.
    """
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(url, data=data, headers=headers, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return "ok", f"HTTP {response.status}"
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")[:200]
        if error.code in (401, 403):
            return "auth", f"HTTP {error.code} {body}"
        if error.code == 402:
            return "quota", f"HTTP {error.code} {body}"
        if error.code in (400, 404):
            return "cfg", f"HTTP {error.code} {body}"
        return "cfg", f"HTTP {error.code} {body}"
    except urllib.error.URLError as error:
        return "net", str(error.reason)
    except Exception as error:  # noqa: BLE001 - diagnostic script
        return "net", f"{type(error).__name__}: {error}"


def check_deepseek() -> Dict[str, object]:
    """Check the DeepSeek model, search, and fetch paths.

    DeepSeek is optional when another backend (for example the MiniMax Code
    Plan proxy) serves the model. A missing key is therefore a skip, not a
    failure.
    """
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    base = os.environ.get("DEEPSEEK_BASE_URL", "").rstrip("/")
    result: Dict[str, object] = {"name": "deepseek", "verdict": "ok", "detail": "", "checks": []}

    if not key:
        result["verdict"] = "skip"
        result["detail"] = "未设置 DEEPSEEK_API_KEY；当前用其他后端（见 minimax 一项）"
        return result

    # A base URL set to the plain API root is the known misconfiguration: the
    # harness speaks the Anthropic-compatible Messages protocol.
    if base and not base.endswith("/anthropic"):
        result["verdict"] = "cfg"
        result["detail"] = (
            f"DEEPSEEK_BASE_URL={base} 缺少 /anthropic 后缀；"
            f"harness 需要 Anthropic 兼容端点（默认 {DEEPSEEK_MESSAGES_BASE}）"
        )
        return result

    # The harness calls the Anthropic-compatible Messages endpoint.
    messages_base = base or DEEPSEEK_MESSAGES_BASE
    if not messages_base.endswith("/anthropic"):
        result["verdict"] = "cfg"
        result["detail"] = (
            f"DEEPSEEK_BASE_URL={messages_base} 缺少 /anthropic 后缀；"
            f"harness 需要 Anthropic 兼容端点（默认 {DEEPSEEK_MESSAGES_BASE}）"
        )
        return result

    verdict, detail = probe(
        f"{messages_base}/v1/messages",
        {"Content-Type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01"},
        {"model": "deepseek-chat", "max_tokens": 8, "messages": [{"role": "user", "content": "hi"}]},
    )
    result["checks"].append({"endpoint": "messages", "verdict": verdict, "detail": detail})
    result["verdict"] = verdict
    result["detail"] = detail

    for name, path, payload in (
        ("search", "/search", {"query": "test", "count": 3}),
        ("fetch", "/fetch", {"url": "https://example.com"}),
    ):
        search_verdict, search_detail = probe(
            f"{DEEPSEEK_TOOLS_BASE}{path}",
            {"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
            payload,
        )
        result["checks"].append({"endpoint": name, "verdict": search_verdict, "detail": search_detail})

    return result


def check_mupapi() -> Dict[str, object]:
    """Check the muapi generation path."""
    key = os.environ.get("MUAPI_API_KEY", "")
    result: Dict[str, object] = {"name": "mupapi", "verdict": "ok", "detail": "", "checks": []}

    if not key:
        result["verdict"] = "auth"
        result["detail"] = "MUAPI_API_KEY 未设置"
        return result

    # The model list endpoint is public and does not authenticate, so it proves
    # nothing. Probe the generation endpoint instead.
    verdict, detail = probe(
        f"{MUAPI_BASE}/images/generations",
        {"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        {"model": "flux-schnell", "prompt": "a red circle", "n": 1, "size": "1024x1024"},
    )
    result["checks"].append({"endpoint": "images/generations", "verdict": verdict, "detail": detail})
    result["verdict"] = verdict
    result["detail"] = detail
    return result


def check_minimax() -> Dict[str, object]:
    """Check the MiniMax paths: the local Code Plan proxy for text, the official API for images."""
    key = os.environ.get("MINIMAX_API_KEY", "")
    result: Dict[str, object] = {"name": "minimax", "verdict": "ok", "detail": "", "checks": []}

    if not key:
        result["verdict"] = "auth"
        result["detail"] = "MINIMAX_API_KEY 未设置"
        return result

    # Text through the local Code Plan proxy (Anthropic-compatible Messages).
    proxy_base = os.environ.get("ANTHROPIC_BASE_URL", "http://127.0.0.1:15721").rstrip("/")
    proxy_verdict, proxy_detail = probe(
        f"{proxy_base}/v1/messages",
        {"Content-Type": "application/json", "anthropic-version": "2023-06-01"},
        {
            "model": "DeepSeek V4 Flash",
            "max_tokens": 16,
            "messages": [{"role": "user", "content": "hi"}],
        },
    )
    result["checks"].append({"endpoint": f"proxy{proxy_base}/v1/messages", "verdict": proxy_verdict, "detail": proxy_detail})

    # Images through the official MiniMax API.
    image_verdict, image_detail = probe(
        "https://api.minimax.chat/v1/image_generation",
        {"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        {"model": "image-01", "prompt": "a red circle", "aspect_ratio": "1:1", "n": 1},
    )
    result["checks"].append({"endpoint": "image_generation", "verdict": image_verdict, "detail": image_detail})

    # The image path is the one that matters for delivery, so it decides the verdict.
    result["verdict"] = image_verdict
    result["detail"] = image_detail
    return result


def check_browser() -> Dict[str, object]:
    """Check the headless Chrome path used by render-deck and the CDP publishers."""
    import shutil
    from pathlib import Path

    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
    ]
    found = next((path for path in candidates if Path(path).exists()), None)
    if found is None:
        found = shutil.which("google-chrome") or shutil.which("chromium")
    if found is None:
        return {"name": "browser", "verdict": "skip", "detail": "未找到 Chrome/Chromium", "checks": []}
    return {"name": "browser", "verdict": "ok", "detail": found, "checks": []}


def check_runner() -> Dict[str, object]:
    """Check the bun/npx runner used by the CDP publishers."""
    import shutil

    for name in ("bun", "npx"):
        found = shutil.which(name)
        if found:
            return {"name": "runner", "verdict": "ok", "detail": found, "checks": []}
    return {"name": "runner", "verdict": "skip", "detail": "bun 与 npx 均不在 PATH", "checks": []}


def check_anysearch() -> Dict[str, object]:
    """Check the anysearch CLI and its optional key."""
    import shutil

    key = os.environ.get("ANYSEARCH_API_KEY", "")
    verdict = "ok" if key else "skip"
    detail = "已配置 ANYSEARCH_API_KEY" if key else "未设置 ANYSEARCH_API_KEY，走匿名低配额"
    found = shutil.which("anysearch")
    if found:
        detail += f"（CLI: {found}）"
    return {"name": "anysearch", "verdict": verdict, "detail": detail, "checks": []}


CHECKS = {
    "deepseek": check_deepseek,
    "minimax": check_minimax,
    "mupapi": check_mupapi,
    "browser": check_browser,
    "runner": check_runner,
    "anysearch": check_anysearch,
}

VERDICT_HINTS = {
    "ok": "可用",
    "auth": "凭据被拒或缺失 —— 换 key / 配 key",
    "quota": "余额或配额不足 —— 充值",
    "cfg": "配置或端点错误 —— 改 base URL / 换端点",
    "net": "网络不可达 —— 检查出网策略",
    "skip": "不适用 —— 该能力不在本次交付范围",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether the local configuration can run each capability path.")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--only", default="", help="comma-separated check names")
    args = parser.parse_args()

    selected = [name.strip() for name in args.only.split(",") if name.strip()] or list(CHECKS)
    unknown = [name for name in selected if name not in CHECKS]
    if unknown:
        sys.stderr.write(f"check-runtime: unknown check(s): {', '.join(unknown)}\n")
        return 2

    results: List[Dict[str, object]] = []
    for name in selected:
        results.append(CHECKS[name]())

    if args.json:
        print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    else:
        print("运行时依赖体检")
        print("=" * 60)
        for entry in results:
            verdict = str(entry["verdict"])
            print(f"\n[{verdict.upper():5s}] {entry['name']}")
            print(f"    {entry['detail']}")
            print(f"    → {VERDICT_HINTS.get(verdict, '')}")
            for check in entry.get("checks", []):  # type: ignore[union-attr]
                print(f"      - {check['endpoint']}: {check['verdict']} ({check['detail'][:120]})")
        print()
        print("=" * 60)
        blocked = [entry for entry in results if entry["verdict"] not in ("ok", "skip")]
        if blocked:
            print(f"受阻路径 {len(blocked)} 条：" + ", ".join(str(entry["name"]) for entry in blocked))
        else:
            print("全部路径可用")

    return 1 if any(entry["verdict"] not in ("ok", "skip") for entry in results) else 0


if __name__ == "__main__":
    sys.exit(main())
