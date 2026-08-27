#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""strip-yaml-frontmatter.py · 批量去除 hook 文件首行 YAML frontmatter

历史问题：data-quality-fixes.py --apply A 在 SKILL.md 上加 license frontmatter 时，
误把同样的 frontmatter 加到了 hooks/ 下 67 个 .js 文件 + hooks.json 上。
Node 加载 .js 时会把第一行 `---` 当作表达式，导致 SyntaxError。
JSON 解析 hooks.json 时也会因第一行 `---` 而报错。

本脚本：
- 扫描指定目录下所有 .js / .json 文件
- 如果首行是 `---` 且文件包含标准的 `--- / license: ... / ---` frontmatter，则去掉
- 默认 dry-run，加 --apply 真改
- 文件必须以 CRLF 或 LF + `\n---/license: UNKNOWN/---/...` 开头

用法：
  python scripts/strip-yaml-frontmatter.py                  # dry-run
  python scripts/strip-yaml-frontmatter.py --apply          # 真改
  python scripts/strip-yaml-frontmatter.py --apply hooks/   # 指定目录
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Windows UTF-8
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# YAML frontmatter pattern: `---\r?\nlicense: ...\r?\n---\r?\n`
FRONTMATTER_RE = re.compile(
    rb"^---\r?\nlicense:[^\n]*\r?\n---\r?\n",
    re.MULTILINE,
)

# 仅处理 hooks/ 下的文件，避免误改 SKILL.md / CLAUDE.md / agent .md 等需要 frontmatter 的文件
DEFAULT_ROOTS = ("hooks",)


def has_frontmatter(content: bytes) -> bool:
    return bool(FRONTMATTER_RE.match(content))


def strip_frontmatter(content: bytes) -> bytes:
    return FRONTMATTER_RE.sub(b"", content, count=1)


def collect_files(root: Path) -> list[Path]:
    """递归收集所有 .js / .json 文件"""
    files = []
    for ext in ("*.js", "*.json"):
        files.extend(root.rglob(ext))
    return sorted(set(files))


def main() -> int:
    ap = argparse.ArgumentParser(description="strip YAML frontmatter from hook files")
    ap.add_argument("--apply", action="store_true", help="actually modify files (default dry-run)")
    ap.add_argument("roots", nargs="*", default=DEFAULT_ROOTS, help="directories to scan")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parent.parent
    scanned = 0
    would_change = 0
    changed = 0
    errors = []

    for root_name in args.roots:
        root = repo / root_name
        if not root.is_dir():
            errors.append(f"directory not found: {root}")
            continue
        for f in collect_files(root):
            scanned += 1
            try:
                raw = f.read_bytes()
            except OSError as e:
                errors.append(f"read failed: {f} ({e})")
                continue
            if not has_frontmatter(raw):
                continue
            would_change += 1
            stripped = strip_frontmatter(raw)
            if args.apply:
                try:
                    f.write_bytes(stripped)
                    changed += 1
                except OSError as e:
                    errors.append(f"write failed: {f} ({e})")
            else:
                rel = f.relative_to(repo)
                # show first line of original vs stripped
                orig_first = raw.split(b"\n", 1)[0].decode("utf-8", errors="replace")
                new_first = stripped.split(b"\n", 1)[0].decode("utf-8", errors="replace")[:60]
                print(f"  [DRY] {rel}  ({orig_first!r} -> {new_first!r}...)")

    print("")
    print(f"scanned    = {scanned}")
    print(f"would/chng = {would_change}{' (applied)' if args.apply else ' (dry-run)'}")
    if args.apply:
        print(f"changed    = {changed}")
    if errors:
        print(f"errors     = {len(errors)}")
        for e in errors:
            print(f"  {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())