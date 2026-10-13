#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_video.py · 天龙引擎 短视频生成 命令（MINIMAX Hailuo）
============================================================

用 MINIMAX CODE PLAN 视频权益生成短视频成片（非脚本）。

调用：
    python scripts/run_video.py --prompt "一只橘猫在阳光下散步"
    python scripts/run_video.py --prompt "..." --duration 6 --resolution 1080P
    python scripts/run_video.py --query <task_id>        # 查询任务
    python scripts/run_video.py --list                   # 查看历史

输出：
    ~/viral-content-reports/videos/YYYYMMDD_HHMMSS.mp4

API key 读取：
1. 环境变量 MINIMAX_API_KEY
2. 配置文件 ~/.minimax/config.json

仅用 Python 标准库（argparse / urllib / json / time / pathlib）。
"""
from __future__ import annotations

import argparse
import sys
import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# Windows GBK 兼容
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


SCRIPT_DIR = Path(__file__).resolve().parent
DRAGON_ROOT = SCRIPT_DIR.parent

# 默认配置
BASE_URL = "https://api.minimaxi.com"
CONFIG_FILE = Path.home() / ".minimax" / "config.json"
MODEL = "MiniMax-Hailuo-2.3"  # CODE PLAN 支持（v1 端点）

# 输出路径约定（秉凌自媒体工作台）：短视频 → 输出内容/短视频/日期/
OUTPUT_ROOT = Path("E:/秉凌自媒体工作台/输出内容")
VIDEO_DIR = OUTPUT_ROOT / "短视频"


def get_api_key() -> str:
    """获取 API key（环境变量 > 配置文件）"""
    env_key = os.environ.get("MINIMAX_API_KEY", "")
    if env_key:
        return env_key
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return data.get("api_key", "")
        except (json.JSONDecodeError, OSError):
            return ""
    return ""


def api_request(key: str, path: str, method: str = "GET", data: dict = None) -> dict:
    """发起 API 请求"""
    url = BASE_URL + path
    headers = {
        "Authorization": f"Bearer {key}",
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json",
    }
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


def cmd_generate(key: str, prompt: str, duration: int, resolution: str) -> int:
    """提交文生视频任务"""
    print(f"🎬 提交文生视频任务...")
    print(f"   模型: {MODEL} | 时长: {duration}s | 分辨率: {resolution}")
    print(f"   提示词: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
    print()

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "aspect_ratio": "16:9",
    }
    r = api_request(key, "/v1/video_generation", "POST", payload)
    if r["status"] != 200 or r["body"].get("base_resp", {}).get("status_code") != 0:
        print(f"❌ 提交失败: {json.dumps(r['body'], ensure_ascii=False)[:300]}")
        return 1

    task_id = r["body"].get("task_id", "")
    print(f"✅ 任务已提交: task_id={task_id}")
    print(f"   预计 1-3 分钟生成完成（异步）")
    print(f"   可用 --query {task_id} 查询状态")
    return 0


def cmd_query(key: str, task_id: str, wait: bool = False, max_wait: int = 180) -> int:
    """查询视频任务状态，wait=True 时轮询直到完成"""
    if wait:
        print(f"⏳ 等待视频生成（最长 {max_wait}s）...")
        for i in range(max_wait // 10):
            r = api_request(key, f"/v1/query/video_generation?task_id={task_id}")
            status = r["body"].get("status", "")
            print(f"   [{i*10}s] {status}", flush=True)
            if status in ("Success", "Failed", "Cancelled"):
                return _handle_result(key, task_id, r["body"])
            time.sleep(10)
        print("❌ 等待超时，请稍后查询")
        return 1

    r = api_request(key, f"/v1/query/video_generation?task_id={task_id}")
    if r["status"] != 200:
        print(f"❌ 查询失败: {json.dumps(r['body'], ensure_ascii=False)[:300]}")
        return 1
    return _handle_result(key, task_id, r["body"])


def _handle_result(key: str, task_id: str, body: dict) -> int:
    """处理查询结果"""
    status = body.get("status", "")
    print(f"📊 状态: {status}")
    if status == "Success":
        file_id = body.get("file_id", "")
        print(f"   file_id: {file_id}")
        print(f"   分辨率: {body.get('video_width')}x{body.get('video_height')}")
        return _download(key, file_id)
    elif status in ("Failed", "Cancelled"):
        print(f"❌ 任务{status}")
        return 1
    else:
        print(f"   任务进行中，稍后再查")
        return 0


def _download(key: str, file_id: str) -> int:
    """获取并下载视频"""
    print(f"\n📥 获取视频下载地址...")
    r = api_request(key, f"/v1/files/retrieve?file_id={file_id}")
    if r["status"] != 200:
        print(f"❌ 获取下载地址失败: {json.dumps(r['body'], ensure_ascii=False)[:300]}")
        return 1
    download_url = r["body"].get("file", {}).get("download_url", "")
    filename = r["body"].get("file", {}).get("filename", "output.mp4")
    if not download_url:
        print("❌ 未获取到下载地址")
        return 1

    # 下载（按日期建子文件夹）
    today_dir = VIDEO_DIR / datetime.now().strftime("%Y-%m-%d")
    today_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%H%M%S")
    out_path = today_dir / f"{ts}.mp4"
    print(f"⏬ 下载视频...")
    try:
        req = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
        out_path.write_bytes(data)
        size_mb = len(data) / 1024 / 1024
        print(f"✅ 视频已保存: {out_path} ({size_mb:.1f} MB)")
        print(f"   原名: {filename}")
        return 0
    except Exception as e:
        print(f"❌ 下载失败: {type(e).__name__}: {str(e)[:200]}")
        return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="天龙引擎 短视频生成（MINIMAX Hailuo 文生视频）"
    )
    parser.add_argument("--prompt", help="视频内容描述（文生视频）")
    parser.add_argument("--duration", type=int, default=6, help="时长（秒，4-15）")
    parser.add_argument("--resolution", default="768P", choices=["768P", "1080P", "2K"],
                        help="分辨率")
    parser.add_argument("--query", help="查询任务状态（task_id）")
    parser.add_argument("--wait", action="store_true", help="等待直到视频生成完成")
    parser.add_argument("--max-wait", type=int, default=180, help="最大等待秒数")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    key = get_api_key()
    if not key:
        print("❌ 未找到 API key（环境变量 MINIMAX_API_KEY 或 ~/.minimax/config.json）")
        print("   获取：platform.minimaxi.com 创建 API key")
        return 1
    print(f"🔑 API: {key[:6]}****{key[-4:]}")

    if args.query:
        return cmd_query(key, args.query, wait=args.wait, max_wait=args.max_wait)
    elif args.prompt:
        return cmd_generate(key, args.prompt, args.duration, args.resolution)
    else:
        print("❌ 请提供 --prompt（生成）或 --query（查询）")
        print("用法: python scripts/run_video.py --prompt \"橘猫散步\"")
        return 1


if __name__ == "__main__":
    sys.exit(main())
