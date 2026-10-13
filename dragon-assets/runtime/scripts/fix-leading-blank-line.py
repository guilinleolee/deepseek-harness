#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix-leading-blank-line.py · 去除 hook .js 第 1 行空行（让 shebang 落 line 1）

strip-yaml-frontmatter.py 去除 frontmatter 后，部分文件第 1 行变成空行，
让原本在 line 2 的 shebang `#!/usr/bin/env node` 仍留在 line 2。
Node 不接受 line 1 是空 + line 2 是 shebang（SyntaxError）。

本脚本：扫描 hooks/**/*.js，如果文件以 \r\n 开头（CRLF 空行），去掉前 2 字节。
同理 \n 开头（LF 空行）去掉前 1 字节。

用法：
  python scripts/fix-leading-blank-line.py                  # dry-run
  python scripts/fix-leading-blank-line.py --apply          # 真改
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def main() -> int:
    ap = argparse.ArgumentParser(description="fix leading blank line in hook .js files")
    ap.add_argument("--apply", action="store_true", help="actually modify files")
    ap.add_argument("roots", nargs="*", default=("hooks",))
    args = ap.parse_args()

    repo = Path(__file__).resolve().parent.parent
    fixed = 0
    scanned = 0
    would_change = 0

    for root_name in args.roots:
        root = repo / root_name
        if not root.is_dir():
            continue
        for f in sorted(root.rglob("*.js")):
            scanned += 1
            raw = f.read_bytes()
            if raw.startswith(b"\r\n#"):
                would_change += 1
                rel = f.relative_to(repo)
                if args.apply:
                    f.write_bytes(raw[2:])
                    fixed += 1
                    print(f"  [FIX] {rel}")
                else:
                    print(f"  [DRY] {rel}  (strip leading CRLF before shebang)")
            elif raw.startswith(b"\n#"):
                would_change += 1
                rel = f.relative_to(repo)
                if args.apply:
                    f.write_bytes(raw[1:])
                    fixed += 1
                    print(f"  [FIX] {rel}")
                else:
                    print(f"  [DRY] {rel}  (strip leading LF before shebang)")

    print("")
    print(f"scanned    = {scanned}")
    print(f"would/chng = {would_change}")
    if args.apply:
        print(f"fixed      = {fixed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())