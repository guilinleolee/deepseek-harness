#!/usr/bin/env python3
"""
plugins_scan.py — 扫 plugin/marketplace 元数据,从 owner 推断可能上游。

marketplace.json 顶层无 repository 字段,只能从 owner.name + 目录名推断。
plugin.json 同理,且有些 plugin 是 ./ 子目录(本地),不是 GitHub 上的源。

策略:
- 扫 marketplace.json → 提取 owner.name + 目录名 → 推断可能 GitHub URL
- 扫 plugin.json → 只能拿到 source (本地 path),无法反推 GitHub
- 全部标 🟡 "可能的本地 marketplace,owner=X",不做 license 比对

Usage:
    python plugins_scan.py <root_path> [--only PATTERN] [--format json]
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


def _safe_str(v: Any) -> str:
    """把所有值转成单行字符串(JSON 安全)。"""
    if v is None:
        return ""
    s = str(v)
    return re.sub(r"[\x00-\x1f\x7f]+", " ", s).strip()


SKIP_DIRS = {"node_modules", ".venv", "venv", "__pycache__",
             ".git", ".pytest_cache", "dist", "build", ".tox"}


def infer_github_from_marketplace(mp_path: Path, owner_name: str | None) -> dict[str, Any]:
    """从 marketplace 路径 + owner 推断可能的 GitHub URL (heuristic,可能不准)。

    启发式规则:
    - 路径形如 .../<...>/<slug>/.claude-plugin/marketplace.json
    - owner.name 是 GitHub 用户名(常见规范: PascalCase 或小写字母)
    - slug 可能是 "<owner>-<repo>" 或 直接 "<repo>"
    - 优先尝试 owner/slug,如果 slug 已含 owner 前缀则剥掉

    Note: marketplace.json 可能在 .../marketplaces/<slug>/ 或 .../skills/<slug>/
    等位置。我们从 .claude-plugin 倒推上两级目录作为 slug。
    """
    parts = mp_path.parts
    # 找 ".claude-plugin" 在 path 里的位置
    try:
        idx = parts.index(".claude-plugin")
    except ValueError:
        # fallback: 找 "marketplaces"
        try:
            idx = parts.index("marketplaces") + 1
        except ValueError:
            return {"type": "unparseable", "url": None, "owner": None, "repo": None,
                    "inferred": False}

    if idx <= 0 or idx >= len(parts):
        return {"type": "unparseable", "url": None, "owner": None, "repo": None,
                "inferred": False}

    slug = parts[idx - 1]  # .claude-plugin 的上一级
    owner_slug = (owner_name or "").lower().replace(" ", "")

    # 启发 1: slug 是 "<owner>-<repo>" 格式
    if owner_slug and slug.lower().startswith(owner_slug + "-"):
        repo = slug[len(owner_slug) + 1:].lower()
        owner = owner_slug
        url = f"https://github.com/{owner}/{repo}"
        return {"type": "github_inferred", "url": url, "owner": owner, "repo": repo,
                "inferred": True, "note": "从 owner.name + slug 推断"}

    # 启发 2: 有 owner.name 但 slug 无关
    if owner_slug:
        url = f"https://github.com/{owner_slug}/{slug.lower()}"
        return {"type": "github_inferred", "url": url, "owner": owner_slug, "repo": slug.lower(),
                "inferred": True, "note": "从 owner.name + 目录名 slug 推断"}

    # 启发 3: 没 owner
    return {"type": "github_inferred", "url": None, "owner": None, "repo": slug.lower(),
            "inferred": False, "note": "无 owner 信息,无法可靠推断 URL"}


def scan_marketplaces(root: Path, only: str | None = None) -> list[dict[str, Any]]:
    """扫所有 .claude-plugin/marketplace.json。"""
    results: list[dict[str, Any]] = []
    for path in root.rglob(".claude-plugin/marketplace.json"):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if only and only.lower() not in str(rel).lower():
            continue
        try:
            text = path.read_text(encoding="utf-8")
            data = json.loads(text)
        except Exception as e:
            results.append({
                "name": path.parent.parent.name,
                "path": str(path),
                "version": None,
                "description": None,
                "owner_name": None,
                "plugin_count": 0,
                "source": {"type": "read_error"},
                "license_local": None,
                "parse_warnings": [f"parse_error: {e!s}"],
            })
            continue
        owner_obj = data.get("owner") or {}
        owner_name = owner_obj.get("name") if isinstance(owner_obj, dict) else None
        source = infer_github_from_marketplace(path, owner_name)
        results.append({
            "name": _safe_str(data.get("name", path.parent.parent.name)) or path.parent.parent.name,
            "path": str(path),
            "version": _safe_str(data.get("version")) or None,
            "description": _safe_str(data.get("description") or (data.get("metadata") or {}).get("description"))[:500] or None,
            "owner_name": _safe_str(owner_name) or None,
            "plugin_count": len(data.get("plugins", []) or []),
            "source": source,
            "license_local": _safe_str(data.get("license")) or None,
            "parse_warnings": [],
        })
    return results


def scan_plugin_jsons(root: Path, only: str | None = None) -> list[dict[str, Any]]:
    """扫所有 plugin.json (per-plugin metadata,不含 marketplace)。"""
    results: list[dict[str, Any]] = []
    for path in root.rglob(".claude-plugin/plugin.json"):
        rel = path.relative_to(root)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if only and only.lower() not in str(rel).lower():
            continue
        try:
            text = path.read_text(encoding="utf-8")
            data = json.loads(text)
        except Exception as e:
            continue  # 不报告,因为 marketplace 已经覆盖
        # plugin.json 是 marketplace 数组中元素之一,不单独作为可更新资产
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="扫 plugin marketplace 元数据")
    parser.add_argument("root", help="扫描根目录")
    parser.add_argument("--only", help="只扫描名字包含此子串的 marketplace")
    parser.add_argument("--format", default="json", choices=["json"])
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"ERROR: root not found: {root}", file=sys.stderr)
        return 2

    marketplaces = scan_marketplaces(root, only=args.only)
    output = {
        "scan_root": str(root),
        "scanned_at": _now_iso(),
        "total_marketplace_found": len(marketplaces),
        "marketplaces": marketplaces,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


def _now_iso() -> str:
    import datetime as _dt
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    sys.exit(main())