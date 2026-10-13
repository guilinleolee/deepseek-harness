#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag-commands-frontmatter.py · 诊断 commands/*.md frontmatter 分类
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def main() -> int:
    repo = Path(__file__).resolve().parent.parent
    cmds = repo / "commands"
    files = sorted(cmds.glob("*.md"))

    stats = {
        "license_only": [],        # only license (no description)
        "license_plus_desc": [],   # both license and description
        "desc_only": [],           # only description
        "no_frontmatter": [],      # neither
    }

    for f in files:
        raw = f.read_text(encoding="utf-8", errors="replace")
        has_license = bool(re.search(r"^license:\s*UNKNOWN", raw, re.M))
        has_desc = bool(re.search(r"^description:", raw, re.M))
        if has_license and has_desc:
            stats["license_plus_desc"].append(f.name)
        elif has_license:
            stats["license_only"].append(f.name)
        elif has_desc:
            stats["desc_only"].append(f.name)
        else:
            stats["no_frontmatter"].append(f.name)

    total = sum(len(v) for v in stats.values())
    print(f"total = {total}")
    for k, v in stats.items():
        print(f"{k:20} = {len(v)}")
    print()

    for key in ["license_only", "license_plus_desc", "desc_only", "no_frontmatter"]:
        print(f"=== {key} 样本 (前 5) ===")
        for n in stats[key][:5]:
            print(f"  {n}")
        print()

    # 看 license_only 的实际 frontmatter 内容（前 3 个）
    print("=== license_only 文件 frontmatter 实际内容（前 3） ===")
    for n in stats["license_only"][:3]:
        path = cmds / n
        raw = path.read_text(encoding="utf-8", errors="replace")
        # 提取 frontmatter 区域
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n", raw, re.DOTALL)
        if m:
            print(f"--- {n} ---")
            print(m.group(1))
            print()

    # 看 license_plus_desc 的实际 frontmatter（前 3 个）
    print("=== license_plus_desc 文件 frontmatter 实际内容（前 3） ===")
    for n in stats["license_plus_desc"][:3]:
        path = cmds / n
        raw = path.read_text(encoding="utf-8", errors="replace")
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n", raw, re.DOTALL)
        if m:
            print(f"--- {n} ---")
            print(m.group(1))
            print()

    # 看 no_frontmatter 的第一行（前 3 个）
    print("=== no_frontmatter 文件第一行（前 3） ===")
    for n in stats["no_frontmatter"][:3]:
        path = cmds / n
        raw = path.read_text(encoding="utf-8", errors="replace")
        first_line = raw.split("\n", 1)[0][:80]
        print(f"  {n}: {first_line!r}")

    return 0


if __name__ == "__main__":
    sys.exit(main())