#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
minimax_image.py · MiniMax 出图调用器
========================================================

async-task-pattern 的 minimax-image adapter 用它做真实调用与产物下载。

单独成文件的原因：bash 里从 JSON 抽 URL 需要处理 \\u0026 之类的转义，
用 Python 的 json 解析更稳。

用法：
    python minimax_image.py --payload '{"model":"image-01","prompt":"..."}' --output out.jpg
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Optional

DEFAULT_BASE = "https://api.minimax.chat/v1"
EXIT_OK = 0
EXIT_FAILED = 4


def request_image(base: str, key: str, payload: dict, timeout: int) -> str:
    """Call the MiniMax image generation endpoint and return the image URL."""
    request = urllib.request.Request(
        f"{base}/image_generation",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"HTTP {error.code}: {detail}") from error
    except Exception as error:  # noqa: BLE001 - adapter boundary
        raise RuntimeError(f"{type(error).__name__}: {error}") from error

    base_resp = body.get("base_resp") or {}
    status = base_resp.get("status_code")
    if status not in (None, 0):
        raise RuntimeError(f"status_code={status}: {base_resp.get('status_msg', '')}")

    data = body.get("data") or {}
    urls = data.get("image_urls") or []
    if not urls:
        raise RuntimeError(f"response carries no image_urls: {json.dumps(body, ensure_ascii=False)[:300]}")
    return str(urls[0])


def download(url: str, output: str, timeout: int) -> int:
    """Download the generated image and return its byte count."""
    request = urllib.request.Request(url, headers={"User-Agent": "dragon-assets/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read()
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"download failed: HTTP {error.code}") from error
    except Exception as error:  # noqa: BLE001 - adapter boundary
        raise RuntimeError(f"download failed: {type(error).__name__}: {error}") from error

    os.makedirs(os.path.dirname(os.path.abspath(output)) or ".", exist_ok=True)
    with open(output, "wb") as handle:
        handle.write(data)
    return len(data)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an image with the MiniMax image API.")
    parser.add_argument("--payload", required=True, help="request body as JSON")
    parser.add_argument("--output", default="", help="where to write the generated image")
    parser.add_argument("--base", default=DEFAULT_BASE, help="API base URL")
    parser.add_argument("--timeout", type=int, default=180, help="seconds")
    args = parser.parse_args()

    key = os.environ.get("MINIMAX_API_KEY", "")
    if not key:
        sys.stderr.write("❌ MINIMAX_API_KEY 未设置\n")
        return EXIT_FAILED

    try:
        payload = json.loads(args.payload)
    except json.JSONDecodeError as error:
        sys.stderr.write(f"❌ --payload 不是合法 JSON: {error}\n")
        return EXIT_FAILED

    try:
        url = request_image(args.base.rstrip("/"), key, payload, args.timeout)
        if args.output:
            size = download(url, args.output, args.timeout)
            print(json.dumps({
                "status": "completed",
                "provider": "minimax-image",
                "path": args.output,
                "size": size,
                "image_url": url,
            }, ensure_ascii=False))
        else:
            print(json.dumps({
                "status": "completed",
                "provider": "minimax-image",
                "image_url": url,
            }, ensure_ascii=False))
    except RuntimeError as error:
        sys.stderr.write(f"❌ minimax-image 失败: {error}\n")
        return EXIT_FAILED

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
