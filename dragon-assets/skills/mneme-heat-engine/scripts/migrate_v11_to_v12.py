"""mneme-heat-engine · migrate_v11_to_v12 V2.0.0 (老节点 heat 字段迁移)

一次性脚本：把主仓 memory/ 下的所有 Markdown 节点加上 heat + last_ref_date 字段。
schema 兼容性：保留原有 frontmatter 全部字段，仅追加 V12.0 新字段。

兼容性策略：
  - heat 不存在 → init=0.7
  - last_ref_date 不存在 → init=today
  - archive/ 子目录跳过（已归档节点不需要再次迁移）
  - 已有 heat 字段的节点保持不变（幂等性）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

# V12.0 默认值（与 heat_engine.py 对齐）
INIT_HEAT = 0.7
SCHEMA_VERSION = "v12.0"


def parse_frontmatter(content: str) -> tuple[dict, str, str]:
    """简单 YAML frontmatter 解析（key: value 格式）.

    返回 (metadata_dict, frontmatter_text, body_text).
    """
    if not content.startswith("---"):
        return {}, "", content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, "", content

    _, fm_text, body = parts
    metadata = {}
    for line in fm_text.strip().splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip()
    return metadata, fm_text, body


def build_frontmatter(metadata: dict, fm_template: str) -> str:
    """根据现有 frontmatter 模板重建，加 heat + last_ref_date + schema_version."""
    new_lines = []
    for line in fm_template.strip().splitlines():
        key_match = re.match(r"^(\w+):", line)
        if key_match:
            new_lines.append(line)
        else:
            new_lines.append(line)

    # 追加 V12.0 字段（如缺失）
    if "heat" not in metadata:
        new_lines.append(f"heat: {INIT_HEAT}")
    if "last_ref_date" not in metadata:
        new_lines.append(f"last_ref_date: {date.today().isoformat()}")
    if "mneme_schema" not in metadata:
        new_lines.append(f"mneme_schema: {SCHEMA_VERSION}")

    return "---\n" + "\n".join(new_lines) + "\n---\n"


def migrate_file(
    path: Path,
    today: str,
    dry_run: bool = True,
) -> dict:
    """迁移单个文件（幂等）."""
    if "archive" in path.parts:
        return {"path": str(path), "skipped": "in archive", "migrated": False}

    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return {"path": str(path), "skipped": "read error", "migrated": False}

    metadata, fm_text, body = parse_frontmatter(content)

    # 幂等检查：已有 heat 字段跳过
    if "heat" in metadata:
        return {"path": str(path), "skipped": "already has heat", "migrated": False}

    # 重构 frontmatter
    new_fm = build_frontmatter(metadata, fm_text)
    new_content = new_fm + body

    # 写回（dry_run 模式只统计不写）
    if not dry_run:
        try:
            path.write_text(new_content, encoding="utf-8")
        except OSError as e:
            return {"path": str(path), "skipped": f"write error: {e}", "migrated": False}

    return {
        "path": str(path),
        "migrated": True,
        "added_fields": [
            k for k in ("heat", "last_ref_date", "mneme_schema")
            if k not in metadata
        ],
    }


def migrate_directory(
    root: Path,
    dry_run: bool = True,
) -> dict:
    """递归扫描目录并迁移所有 .md 文件."""
    today = date.today().isoformat()
    results = {
        "dry_run": dry_run,
        "today": today,
        "total_scanned": 0,
        "migrated": 0,
        "skipped": 0,
        "files": [],
    }

    for path in root.rglob("*.md"):
        results["total_scanned"] += 1
        result = migrate_file(path, today, dry_run=dry_run)
        results["files"].append(result)
        if result.get("migrated"):
            results["migrated"] += 1
        else:
            results["skipped"] += 1

    return results


def cmd_dry_run(args: argparse.Namespace) -> int:
    """dry-run 模式：仅统计，不修改文件."""
    root = Path(args.root)
    if not root.exists():
        print(f"[ERROR] root path not found: {root}")
        return 1

    results = migrate_directory(root, dry_run=True)
    print(json.dumps({
        "mode": "dry_run",
        "root": str(root),
        "total_scanned": results["total_scanned"],
        "would_migrate": results["migrated"],
        "would_skip": results["skipped"],
        "sample_migrated": [f for f in results["files"] if f.get("migrated")][:5],
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    """apply 模式：实际修改文件."""
    root = Path(args.root)
    if not root.exists():
        print(f"[ERROR] root path not found: {root}")
        return 1

    results = migrate_directory(root, dry_run=False)
    print(json.dumps({
        "mode": "apply",
        "root": str(root),
        "total_scanned": results["total_scanned"],
        "migrated": results["migrated"],
        "skipped": results["skipped"],
    }, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="mneme-heat-engine · migrate_v11_to_v12 · 老节点 heat 字段迁移",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_dry = sub.add_parser("dry-run", help="dry-run: 只统计不修改")
    p_dry.add_argument("--root", required=True, help="扫描根目录（e.g. dragon-engine/memory）")
    p_dry.set_defaults(func=cmd_dry_run)

    p_app = sub.add_parser("apply", help="apply: 实际写回 frontmatter")
    p_app.add_argument("--root", required=True, help="扫描根目录")
    p_app.set_defaults(func=cmd_apply)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())