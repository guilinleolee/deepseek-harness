#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build-continue-config.py · 生成 ~/.continue/config.json

从 dragon-engine/commands/*.md 读 frontmatter，生成 customCommands 数组。
这是 Continue 1.x 显式注册 slash commands 的方式（fallback 优先于自动发现）。

schema（Continue 1.x）：
{
  "customCommands": [
    {"name": "00调研师", "description": "考古摸底...", "prompt": "<full body>"}
  ]
}

用法：
  python scripts/build-continue-config.py
  python scripts/build-continue-config.py --out ~/.continue/config.json
  python scripts/build-continue-config.py --prompt       # 含完整 prompt body
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# frontmatter 解析（与 fix-commands-frontmatter.py 一致）
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# 跳过的文件（不是 slash command）
SKIP_NAMES = {"INDEX.md", "README.md"}

DEFAULT_OUT = Path.home() / ".continue" / "config.json"


def parse_fm(text: str) -> tuple[dict[str, str], str]:
    m = FM_RE.match(text)
    if not m:
        return {}, text
    kv = {}
    for line in m.group(1).split("\n"):
        if ":" in line:
            k, _, v = line.partition(":")
            kv[k.strip()] = v.strip()
    return kv, text[m.end():]


def main() -> int:
    ap = argparse.ArgumentParser(description="build Continue config.json")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help=f"output path (default: {DEFAULT_OUT})")
    ap.add_argument("--root", type=Path, default=None,
                    help="commands dir (default: <repo>/commands)")
    ap.add_argument("--prompt", action="store_true",
                    help="include full prompt body (large file)")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parent.parent
    cmds = args.root or (repo / "commands")

    if not cmds.is_dir():
        print(f"ERROR: {cmds} not a directory")
        return 1

    custom_commands = []
    for f in sorted(cmds.glob("*.md")):
        if f.name in SKIP_NAMES:
            continue
        raw = f.read_text(encoding="utf-8", errors="replace")
        kv, body = parse_fm(raw)
        if "name" not in kv or "description" not in kv:
            print(f"  WARN: {f.name} missing name/description, skipped")
            continue

        cmd = {
            "name": kv["name"],
            "description": kv["description"],
        }
        if args.prompt:
            cmd["prompt"] = body.strip()
        custom_commands.append(cmd)

    config = {
        "$schema": "https://continue.dev/config-schema/latest.json",
        "customCommands": custom_commands,
    }

    # 输出到目标
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"wrote {args.out}")
    print(f"customCommands count = {len(custom_commands)}")
    print(f"size = {args.out.stat().st_size} bytes")
    if args.prompt:
        print(f"mode = with full prompt body")
    else:
        print(f"mode = name+description only (compact)")
    return 0


if __name__ == "__main__":
    sys.exit(main())