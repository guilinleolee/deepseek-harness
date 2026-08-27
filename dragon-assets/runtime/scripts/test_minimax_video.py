#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_minimax_video.py · 验证 MINIMAX CODE PLAN 视频生成权益
=============================================================
根据 MiniMax 官方 MCP 源码，CODE PLAN 的视频生成走 v1 端点 + Hailuo 系列模型
（不是 v2 端点 + H3）。本脚本验证正确调用方式。

用法：
    python test_minimax_video.py            # 测试认证 + 列出可用模型
    python test_minimax_video.py --t2v      # 测试文生视频（Hailuo-2.3）
    python test_minimax_video.py --key XXX  # 指定 key（默认读配置文件）

API key 读取优先级：
1. 环境变量 MINIMAX_API_KEY
2. 命令行 --key
3. 配置文件 ~/.minimax/config.json
"""
import argparse
import json
import sys
import os
import urllib.request
import urllib.error
from pathlib import Path

# Windows GBK 兼容
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

CONFIG_FILE = Path.home() / ".minimax" / "config.json"
BASE_URL = "https://api.minimaxi.com"


def get_api_key(args_key: str) -> str:
    """按优先级获取 API key"""
    env_key = os.environ.get("MINIMAX_API_KEY", "")
    if env_key:
        return env_key
    if args_key:
        return args_key
    if CONFIG_FILE.exists():
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return data.get("api_key", "")
    return ""


def api_request(key: str, path: str, method: str = "GET", data: dict = None) -> dict:
    """发起 API 请求"""
    url = BASE_URL + path
    headers = {"Authorization": f"Bearer {key}", "User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
    req = urllib.request.Request(url, method=method, headers=headers,
                                 data=json.dumps(data).encode() if data else None)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {"status": resp.status, "body": json.loads(resp.read().decode("utf-8"))}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        try:
            return {"status": e.code, "body": json.loads(body)}
        except json.JSONDecodeError:
            return {"status": e.code, "body": {"raw": body}}


def cmd_models(key: str):
    """列出可用模型"""
    print("=== 你的账号可用模型 ===")
    r = api_request(key, "/v1/models")
    if r["status"] == 200:
        for m in r["body"].get("data", []):
            print(f"  - {m['id']}")
    else:
        print(f"  请求失败: {r['body']}")


def cmd_t2v(key: str):
    """测试文生视频（v1 端点 + Hailuo-2.3）"""
    print("=== 测试文生视频（v1 + Hailuo-2.3） ===")
    payload = {
        "model": "MiniMax-Hailuo-2.3",
        "prompt": "一只橘猫在阳光下慵懒地散步，高清写实风格",
        "duration": 6,
        "resolution": "768P",
        "aspect_ratio": "16:9",
    }
    r = api_request(key, "/v1/video_generation", "POST", payload)
    print(f"HTTP {r['status']}")
    print(json.dumps(r["body"], ensure_ascii=False, indent=1)[:500])


def cmd_t2v_hailuo02(key: str):
    """测试 Hailuo-02 模型"""
    print("=== 测试文生视频（v1 + Hailuo-02） ===")
    payload = {
        "model": "MiniMax-Hailuo-02",
        "prompt": "一只橘猫在阳光下慵懒地散步",
        "duration": 6,
        "resolution": "768P",
        "aspect_ratio": "16:9",
    }
    r = api_request(key, "/v1/video_generation", "POST", payload)
    print(f"HTTP {r['status']}")
    print(json.dumps(r["body"], ensure_ascii=False, indent=1)[:500])


def main() -> int:
    parser = argparse.ArgumentParser(description="验证 MINIMAX 视频生成权益")
    parser.add_argument("--key", default="", help="API key（默认读配置）")
    parser.add_argument("--models", action="store_true", help="列出可用模型")
    parser.add_argument("--t2v", action="store_true", help="测试文生视频 Hailuo-2.3")
    parser.add_argument("--t2v-hailuo02", action="store_true", help="测试文生视频 Hailuo-02")
    args = parser.parse_args()

    key = get_api_key(args.key)
    if not key:
        print("❌ 未找到 API key（环境变量 MINIMAX_API_KEY / --key / ~/.minimax/config.json）")
        return 1
    print(f"API key: {key[:6]}****{key[-4:]} ({len(key)}字符)")
    print()

    if args.models:
        cmd_models(key)
    elif args.t2v:
        cmd_t2v(key)
    elif args.t2v_hailuo02:
        cmd_t2v_hailuo02(key)
    else:
        cmd_models(key)

    return 0


if __name__ == "__main__":
    sys.exit(main())
