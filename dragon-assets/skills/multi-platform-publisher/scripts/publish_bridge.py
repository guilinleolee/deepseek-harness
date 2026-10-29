#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish_bridge.py · 真实发布桥
========================================================

把 multi-platform-publisher 的发布动作接到真实的浏览器发布器上。

背景：publisher.py 的 publish_to_platform() 是 mock 实现——它不联系任何平台，
只造一个假 post_id 就返回 success。对外报价说"9 平台自动发布"会直接翻车。

本桥的行为：
- 有真实发布器的平台（weibo / wechat / x）→ 调 baoyu-post-to-* 的 CDP 脚本，真发。
- 没有真实发布器的平台（douyin / xiaohongshu / shipinhao / bilibili /
  kuaishou / tiktok / youtube）→ 明确返回 "no_publisher" 失败，绝不假装成功。

安全默认值：--submit 才会真的发出去。不加 --submit 时走预览模式，
只做渲染与内容检查，不点击发布。x-browser.ts 本身就是这个语义（默认预览）。

用法：
    python publish_bridge.py --platform weibo --content ./post.md --image ./a.png
    python publish_bridge.py --platform x --content ./post.md --submit
    python publish_bridge.py --platform douyin --content ./post.md   # 失败并说明原因
    python publish_bridge.py --list

退出码：
    0  发布或预览成功
    2  参数错误 / 输入文件缺失
    3  平台没有真实发布器（明确失败，不假装成功）
    4  发布器依赖缺失（bun / npx / chrome）
    5  发布器执行失败

授权：自研，随仓库分发。
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

EXIT_OK = 0
EXIT_BAD_INPUT = 2
EXIT_NO_PUBLISHER = 3
EXIT_MISSING_DEPENDENCY = 4
EXIT_PUBLISH_FAILED = 5

SKILL_ROOT = Path(__file__).resolve().parent.parent
BAOYU_ROOT = SKILL_ROOT.parent

# 平台 -> (真实发布器脚本, 该脚本要求的额外参数)
#
# 只收录仓库内确有 CDP 发布器的平台。收录标准：脚本文件存在，且
# 内部确实有对外请求（fetch / CDP 连接），而不是写一个占位文件。
PUBLISHERS: Dict[str, Dict[str, object]] = {
    "weibo": {
        "name": "微博",
        "script": BAOYU_ROOT / "baoyu-post-to-weibo" / "scripts" / "weibo-post.ts",
        "runner": "bun",
        "submit_flag": "",
        "content_arg": "text",
    },
    "x": {
        "name": "X (Twitter)",
        "script": BAOYU_ROOT / "baoyu-post-to-x" / "scripts" / "x-browser.ts",
        "runner": "bun",
        "submit_flag": "--submit",
        "content_arg": "text",
    },
    "wechat": {
        "name": "微信公众号",
        "script": BAOYU_ROOT / "baoyu-post-to-wechat" / "scripts" / "md-to-wechat.ts",
        "runner": "bun",
        "submit_flag": "",
        "content_arg": "file",
    },
}

# publisher.py 里声明的平台。列在这里是为了给出明确原因，而不是让调用方
# 收到一个 KeyError。
UNSUPPORTED_PLATFORMS: Dict[str, str] = {
    "douyin": "仓库内没有抖音的 CDP 发布器；抖音的自动化登录与风控成本另计。",
    "xiaohongshu": "仓库内没有小红书的 CDP 发布器。",
    "shipinhao": "仓库内没有视频号的 CDP 发布器。",
    "bilibili": "仓库内没有 B 站的 CDP 发布器。",
    "kuaishou": "仓库内没有快手的 CDP 发布器。",
    "tiktok": "仓库内没有 TikTok 的 CDP 发布器。",
    "youtube": "仓库内没有 YouTube 的 CDP 发布器。",
}

# 需要 bun 或 npx 之一
RUNNER_CANDIDATES = ("bun", "npx")


def find_runner() -> Optional[str]:
    """Locate bun or npx, preferring bun."""
    for name in RUNNER_CANDIDATES:
        found = shutil.which(name)
        if found:
            return name
    return None


def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    """Split a leading YAML-ish frontmatter block from the body."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta: Dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip().strip("'\"")
    return meta, parts[2]


def build_command(
    platform: str,
    content_path: Path,
    images: List[str],
    submit: bool,
    runner: str,
) -> List[str]:
    """Build the argv for one platform's publisher."""
    spec = PUBLISHERS[platform]
    script = Path(str(spec["script"]))
    text = content_path.read_text(encoding="utf-8", errors="replace")
    meta, body = parse_frontmatter(text)
    title = meta.get("title", "").strip()
    summary = meta.get("description", "").strip() or body.strip()

    command: List[str] = []
    if runner == "npx":
        command += ["npx", "-y", "bun"]
    else:
        command += ["bun"]
    command.append(str(script))

    if spec["content_arg"] == "file":
        command.append(str(content_path))
    else:
        command.append(summary)

    for image in images:
        command += ["--image", image]

    submit_flag = str(spec.get("submit_flag") or "")
    if submit and submit_flag:
        command.append(submit_flag)

    if title and platform == "wechat":
        command += ["--title", title]

    return command


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish content through a real browser publisher.")
    parser.add_argument("--platform", default="", help="platform id; see --list")
    parser.add_argument("--content", default="", help="markdown or text file to publish")
    parser.add_argument("--image", action="append", default=[], help="image path; repeatable")
    parser.add_argument("--submit", action="store_true", help="actually post (default: preview only)")
    parser.add_argument("--timeout", type=int, default=300, help="seconds")
    parser.add_argument("--list", action="store_true", help="list supported platforms")
    args = parser.parse_args()

    if args.list:
        print("platforms with a real publisher:")
        for platform, spec in PUBLISHERS.items():
            print(f"  {platform:10s} {spec['name']}")
        print()
        print("platforms without a publisher (this bridge fails loudly for them):")
        for platform, reason in UNSUPPORTED_PLATFORMS.items():
            print(f"  {platform:14s} {reason}")
        return EXIT_OK

    if not args.platform:
        sys.stderr.write("publish_bridge: --platform is required (see --list)\n")
        return EXIT_BAD_INPUT
    if not args.content:
        sys.stderr.write("publish_bridge: --content is required\n")
        return EXIT_BAD_INPUT

    if args.platform in UNSUPPORTED_PLATFORMS:
        sys.stderr.write(
            f"publish_bridge: platform {args.platform!r} has no real publisher. "
            f"{UNSUPPORTED_PLATFORMS[args.platform]} This bridge does not fabricate success.\n"
        )
        return EXIT_NO_PUBLISHER

    spec = PUBLISHERS.get(args.platform)
    if spec is None:
        sys.stderr.write(f"publish_bridge: unknown platform {args.platform!r}\n")
        return EXIT_BAD_INPUT

    script = Path(str(spec["script"]))
    if not script.is_file():
        sys.stderr.write(f"publish_bridge: publisher script missing: {script}\n")
        return EXIT_MISSING_DEPENDENCY

    content_path = Path(args.content)
    if not content_path.is_file():
        sys.stderr.write(f"publish_bridge: content file not found: {content_path}\n")
        return EXIT_BAD_INPUT

    for image in args.image:
        if not Path(image).is_file():
            sys.stderr.write(f"publish_bridge: image not found: {image}\n")
            return EXIT_BAD_INPUT

    runner = find_runner()
    if runner is None:
        sys.stderr.write(
            "publish_bridge: neither bun nor npx is on PATH; the publisher scripts need one of them.\n"
        )
        return EXIT_MISSING_DEPENDENCY

    command = build_command(args.platform, content_path, args.image, args.submit, runner)
    mode = "publish" if args.submit else "preview"
    sys.stderr.write(f"[publish_bridge] {args.platform} ({mode}) via {runner}\n")
    sys.stderr.write(f"[publish_bridge] {' '.join(command)}\n")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=max(30, args.timeout),
        )
    except subprocess.TimeoutExpired:
        sys.stderr.write(f"publish_bridge: {args.platform} publisher timed out\n")
        return EXIT_PUBLISH_FAILED
    except OSError as error:
        sys.stderr.write(f"publish_bridge: cannot run publisher: {error}\n")
        return EXIT_MISSING_DEPENDENCY

    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)

    if result.returncode != 0:
        sys.stderr.write(f"publish_bridge: {args.platform} publisher exited {result.returncode}\n")
        return EXIT_PUBLISH_FAILED

    print(json.dumps({
        "platform": args.platform,
        "mode": mode,
        "status": "submitted" if args.submit else "previewed",
        "publisher": str(spec["script"]),
    }, ensure_ascii=False))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
