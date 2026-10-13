#!/usr/bin/env python3
"""
agents_scan.py — 扫 ~agents/**/*.md 的 sub-agents,识别并报告。
agent md 的 frontmatter 不含 upstream URL,所以全部标 🟣 本地定制。

Usage:
    python agents_scan.py <root_path> [--only PATTERN] [--format json]

Output: JSON to stdout,schema 与 parse_skill.py 一致:
{
  "scan_root": "...",
  "total_agent_md_found": <int>,
  "agents": [
    {
      "name": "...",
      "path": "...",
      "description": "...",
      "tools": "Read, Write, ...",
      "model": "sonnet",
      "source": {"type": "missing"},   # 永远 missing
      "license_local": null,
      "upstream_local": [],
      "parse_warnings": []
    },
    ...
  ]
}
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")


SKIP_DIRS = {"node_modules", ".venv", "venv", "__pycache__",
             ".git", ".pytest_cache", "dist", "build", ".tox"}


def _safe_str(v: Any) -> str:
    """把所有值转成单行字符串(JSON 安全)。"""
    if v is None:
        return ""
    s = str(v)
    # 替换换行/制表符/控制字符为空格,避免 JSON 转义问题
    return re.sub(r"[\x00-\x1f\x7f]+", " ", s).strip()


def parse_frontmatter(text: str) -> dict[str, Any]:
    """极简 frontmatter 解析:支持 key: value 与 key: list 一行。"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}
    fm = m.group(1)
    result: dict[str, Any] = {}
    current_list_key: str | None = None
    for raw_line in fm.split("\n"):
        if not raw_line.strip():
            continue
        list_match = re.match(r"^\s+-\s+(.*)$", raw_line)
        if list_match and current_list_key:
            result.setdefault(current_list_key, []).append(list_match.group(1).strip())
            continue
        kv_match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)$", raw_line)
        if kv_match:
            key = kv_match.group(1).strip()
            value = kv_match.group(2).strip()
            current_list_key = None
            if value == "":
                current_list_key = key
                result.setdefault(key, [])
            elif value.startswith("[") and value.endswith("]"):
                inner = value[1:-1]
                result[key] = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
            else:
                result[key] = value.strip('"').strip("'")
    return result


def scan_agents(root: Path, only: str | None = None) -> list[dict[str, Any]]:
    """扫 root 下所有 */agents/**/*.md,过滤黑名单。"""
    results: list[dict[str, Any]] = []
    for path in root.rglob("*.md"):
        # 只在 */agents/ 目录下的 md 才算 agent
        if "agents" not in path.relative_to(root).parts:
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if only and only.lower() not in path.parent.name.lower() and only.lower() not in path.stem.lower():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="gbk", errors="replace")
        except Exception as e:
            results.append({
                "name": path.stem,
                "path": str(path),
                "description": None,
                "tools": None,
                "model": None,
                "source": {"type": "missing"},
                "license_local": None,
                "upstream_local": [],
                "parse_warnings": [f"read_error: {e!s}"],
            })
            continue
        fm = parse_frontmatter(text)
        # agent md 不要求有 frontmatter,无 frontmatter 也不算错误
        warnings: list[str] = []
        if not fm:
            warnings.append("no_frontmatter")
        results.append({
            "name": _safe_str(fm.get("name", path.stem)) or path.stem,
            "path": str(path),
            "description": _safe_str(fm.get("description"))[:500] or None,
            "tools": _safe_str(fm.get("tools")) or None,
            "model": _safe_str(fm.get("model")) or None,
            "source": {"type": "missing"},  # agents 永远没 source
            "license_local": _safe_str(fm.get("license")) or None,
            "upstream_local": [],
            "parse_warnings": warnings,
        })
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="扫 sub-agent md")
    parser.add_argument("root", help="扫描根目录")
    parser.add_argument("--only", help="只扫描名字包含此子串的 agent")
    parser.add_argument("--format", default="json", choices=["json"])
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        return 2

    agents = scan_agents(root, only=args.only)
    output = {
        "scan_root": str(root),
        "scanned_at": _now_iso(),
        "total_agent_md_found": len(agents),
        "agents": agents,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


def _now_iso() -> str:
    import datetime as _dt
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    sys.exit(main())