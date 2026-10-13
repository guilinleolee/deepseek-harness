#!/usr/bin/env python3
"""
parse_skill.py — 扫描根目录下所有 SKILL.md，抽取 frontmatter 关键字段。
纯标准库实现（urllib / re / json / pathlib），不依赖 PyYAML。

Usage:
    python parse_skill.py <root_path> [--only PATTERN] [--format json]

Output: JSON to stdout, schema 详见 design.md §2.1.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Windows Git Bash 默认 GBK，stdout 打不出 ⭐ / 中文 → 强制 utf-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")


# 默认黑名单：node_modules / .venv / __pycache__ / .git / .pytest_cache
DEFAULT_BLACKLIST = [
    "**/node_modules/**",
    "**/.venv/**",
    "**/venv/**",
    "**/__pycache__/**",
    "**/.git/**",
    "**/.pytest_cache/**",
    "**/dist/**",
    "**/build/**",
]


def parse_frontmatter(text: str) -> dict[str, Any]:
    """解析 YAML frontmatter 的最常见子集。

    不依赖 PyYAML。仅支持天龙 SKILL.md 真实出现的字段写法：
    - key: value
    - key: "value with spaces"
    - key:
        - item1
        - item2
    - key: ["a", "b"]  (inline list)
    """
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}
    fm = m.group(1)
    result: dict[str, Any] = {}
    current_list_key: str | None = None
    for raw_line in fm.split("\n"):
        # 跳过空行
        if not raw_line.strip():
            continue
        # 列表项（"  - item"）
        list_match = re.match(r"^\s+-\s+(.*)$", raw_line)
        if list_match and current_list_key:
            val = _strip_quotes(list_match.group(1).strip())
            result.setdefault(current_list_key, []).append(val)
            continue
        # "key: value" 或 "key:"（后接列表）
        kv_match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)$", raw_line)
        if kv_match:
            key = kv_match.group(1).strip()
            value = kv_match.group(2).strip()
            current_list_key = None
            if value == "":
                # 列表起点，下一行开始读 - item
                current_list_key = key
                result.setdefault(key, [])
            elif value.startswith("[") and value.endswith("]"):
                # 内联列表 ["a", "b"] / ['a', 'b']
                inner = value[1:-1]
                items = [_strip_quotes(x.strip()) for x in inner.split(",") if x.strip()]
                result[key] = items
            elif value.startswith('"') and value.endswith('"'):
                result[key] = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                result[key] = value[1:-1]
            else:
                result[key] = value
    return result


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")):
        return s[1:-1]
    return s


def parse_source(source_raw: str | None) -> dict[str, Any]:
    """从 source: 字段抽取 GitHub URL / 本地路径。

    支持的形式：
    - "https://github.com/owner/repo (3.2k ⭐ · 借调 xxx)"
    - "https://github.com/owner/repo"
    - "./local/path" 或 "C:/local/path"
    - null / 空
    """
    if not source_raw:
        return {"raw": None, "url": None, "owner": None, "repo": None, "type": "missing"}
    # GitHub URL (允许 .git 后缀、可选括号注释)
    gh_match = re.match(r"(https?://github\.com/([^/\s]+)/([^/\s)\]]+))", source_raw)
    if gh_match:
        url = gh_match.group(1)
        owner = gh_match.group(2)
        repo = gh_match.group(3)
        # 去掉结尾的 .git
        if url.endswith(".git"):
            url = url[:-4]
            repo = repo[:-4] if repo.endswith(".git") else repo
        return {"raw": source_raw, "url": url, "owner": owner, "repo": repo, "type": "github"}
    # 本地路径
    if source_raw.startswith("./") or source_raw.startswith("/") or re.match(r"^[a-zA-Z]:", source_raw):
        return {"raw": source_raw, "url": None, "owner": None, "repo": None, "type": "local_only"}
    # 其它（描述性文本，无法解析）
    return {"raw": source_raw, "url": None, "owner": None, "repo": None, "type": "unparseable"}


def scan_skill_md(root: Path, only: str | None = None) -> list[dict[str, Any]]:
    """递归扫 root 下所有 SKILL.md，按 blacklist 过滤。"""
    skills: list[dict[str, Any]] = []
    skip_dirs = {"node_modules", ".venv", "venv", "__pycache__",
                 ".git", ".pytest_cache", "dist", "build", ".tox"}
    for path in root.rglob("SKILL.md"):
        rel = path.relative_to(root)
        # 任一路径段命中黑名单就跳过
        if any(part in skip_dirs for part in rel.parts):
            continue
        # only 过滤
        if only and only.lower() not in path.parent.name.lower():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="gbk", errors="replace")
        except Exception as e:
            skills.append({
                "name": path.parent.name,
                "path": str(path),
                "version": None,
                "last_updated": None,
                "source": {"raw": None, "url": None, "owner": None, "repo": None, "type": "read_error"},
                "license_local": None,
                "upstream_local": [],
                "parse_warnings": [f"read_error: {e!s}"],
            })
            continue
        fm = parse_frontmatter(text)
        warnings: list[str] = []
        if not fm:
            warnings.append("no_frontmatter")
        source = parse_source(fm.get("source"))
        upstream = fm.get("upstream", [])
        if isinstance(upstream, str):
            upstream = [upstream]
        skill = {
            "name": fm.get("name", path.parent.name),
            "path": str(path),
            "version": fm.get("version"),
            "last_updated": fm.get("last_updated"),
            "source": source,
            "license_local": fm.get("license"),
            "upstream_local": upstream,
            "parse_warnings": warnings,
        }
        skills.append(skill)
    return skills


def main() -> int:
    parser = argparse.ArgumentParser(description="扫描 SKILL.md 并抽取 frontmatter")
    parser.add_argument("root", help="扫描根目录")
    parser.add_argument("--only", help="只扫描名字包含此子串的 skill")
    parser.add_argument("--format", default="json", choices=["json"], help="输出格式")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        return 2

    skills = scan_skill_md(root, only=args.only)
    output = {
        "scan_root": str(root),
        "scanned_at": _now_iso(),
        "total_skill_md_found": len(skills),
        "skills": skills,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


def _now_iso() -> str:
    """返回 ISO-8601 时间戳（避开 datetime.now() 在某些环境的性能问题）"""
    import datetime as _dt
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    sys.exit(main())