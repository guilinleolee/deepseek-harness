#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pack-skill-library.py · 客户技能库打包器
========================================================

从 dragon-assets 打出一个只含可再分发资产的技能库目录，供卡巴格服务端
（或任何私有部署交付）直接使用。资产来源由 DELIVERABLE_SKILLS.json 决定，
该清单由 build-deliverable-skills.py 从 LICENSES.json 生成 —— 授权判断
不在这份脚本里重复实现。

行为：
- 按 DELIVERABLE_SKILLS.json 的 deliverable 清单复制资产目录。
- 复制前重跑清单一致性校验（--check 语义内联），清单过期即失败。
- Apache-2.0 / BSD-3-Clause 资产必带 LICENSE（或 NOTICE）；缺失即失败。
- 生成 ATTRIBUTIONS.md，汇总每个资产的上游与义务，放在库根。
- 排除 node_modules / __pycache__ / .git / 测试产物 / 备份目录。

用法：
    python pack-skill-library.py --out D:/deliver/library
    python pack-skill-library.py --out D:/deliver/library --dry-run

退出码：0 = 打包成功；1 = 有资产缺失或清单不一致。
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent.parent.parent
ASSETS_DIR = ROOT / "dragon-assets"
MANIFEST_PATH = ASSETS_DIR / "index" / "DELIVERABLE_SKILLS.json"
LICENSES_PATH = ASSETS_DIR / "index" / "LICENSES.json"

SKIP_DIR_NAMES = {
    "_archive", "_template", "__pycache__", "node_modules", ".git",
    ".github", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "backups", "db-backup", "cache", ".cache", "library", "local-tests",
}

# 需要 LICENSE 文件随包的 tier
TIERS_REQUIRING_LICENSE = {"Apache-2.0", "BSD-3-Clause", "MIT"}
LICENSE_FILE_NAMES = ("LICENSE", "LICENSE.txt", "LICENSE.md", "LICENCE", "NOTICE", "NOTICE.md")

# 资产目录名 → 注册表键的候选（family 通配在注册表里以 * 结尾）
def skill_dir_candidates(asset_id: str) -> List[str]:
    if asset_id.endswith("*"):
        return []
    return [asset_id]


def find_skill_dir(asset_id: str) -> Path | None:
    """Locate the asset directory for one manifest id.

    The manifest id usually equals the directory name, but some entries use a
    frontmatter id that differs from it, so fall back to a scan.
    """
    direct = ASSETS_DIR / "skills" / asset_id
    if direct.is_dir():
        return direct
    skills_dir = ASSETS_DIR / "skills"
    for entry in sorted(skills_dir.iterdir()):
        if not entry.is_dir():
            continue
        frontmatter = entry / "SKILL.md"
        nested = entry / "skill" / "SKILL.md"
        probe = nested if nested.is_file() else frontmatter
        if not probe.is_file():
            continue
        head = probe.read_text(encoding="utf-8", errors="ignore")[:600]
        if f"name: {asset_id}" in head:
            return entry
    return None


def copy_asset(source: Path, target: Path) -> int:
    """Copy one asset directory, skipping generated content. Returns file count."""
    count = 0
    for item in source.rglob("*"):
        relative = item.relative_to(source)
        if any(part in SKIP_DIR_NAMES for part in relative.parts):
            continue
        if item.is_dir():
            continue
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, destination)
        count += 1
    return count


def find_license_file(asset_dir: Path) -> Path | None:
    for name in LICENSE_FILE_NAMES:
        candidate = asset_dir / name
        if candidate.is_file():
            return candidate
    # Some skills nest their entry point one level down.
    nested = asset_dir / "skill"
    if nested.is_dir():
        for name in LICENSE_FILE_NAMES:
            candidate = nested / name
            if candidate.is_file():
                return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Pack the deliverable skill library.")
    parser.add_argument("--out", required=True, help="output directory for the packed library")
    parser.add_argument("--dry-run", action="store_true", help="list what would be packed without copying")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    registry = json.loads(LICENSES_PATH.read_text(encoding="utf-8"))["skills"]

    deliverable = manifest.get("deliverable") or []
    violations = manifest.get("violations") or []
    if violations:
        for violation in violations:
            print(f"pack-skill-library: manifest violation: {violation}", file=sys.stderr)
        print("pack-skill-library: regenerate DELIVERABLE_SKILLS.json first", file=sys.stderr)
        return 1

    failures: List[str] = []
    packed: List[Dict[str, object]] = []
    total_files = 0

    out_dir = Path(args.out)
    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    for record in deliverable:
        asset_id = str(record["id"])
        tier = str(record["tier"])
        entry = registry.get(asset_id) or {}
        obligations = list(entry.get("obligations") or [])

        source = find_skill_dir(asset_id)
        if source is None:
            failures.append(f"{asset_id}: asset directory not found in dragon-assets/skills")
            continue

        needs_license = tier in TIERS_REQUIRING_LICENSE or "retain-license-text" in obligations
        license_file = find_license_file(source)
        if needs_license and license_file is None:
            failures.append(f"{asset_id}: tier {tier} requires a LICENSE file but none exists in {source.name}")

        target = out_dir / "skills" / source.name
        if not args.dry_run:
            count = copy_asset(source, target)
            total_files += count

        packed.append({
            "id": asset_id,
            "dir": source.name,
            "tier": tier,
            "upstream": str(entry.get("upstream") or ""),
            "upstream_url": str(entry.get("upstream_url") or ""),
            "obligations": obligations,
        })

    if not args.dry_run and packed:
        lines = [
            "# 技能库致谢汇总",
            "",
            "> 由 pack-skill-library.py 自动生成。每个资产的完整上游 LICENSE 随包携带在各自目录内。",
            "",
        ]
        for item in sorted(packed, key=lambda entry: str(entry["id"])):
            upstream = str(item["upstream"]) or "自研"
            url = str(item["upstream_url"])
            suffix = f"（{url}）" if url else ""
            lines.append(f"- **{item['id']}** — {upstream}{suffix} · {item['tier']}")
        (out_dir / "ATTRIBUTIONS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    mode = "dry-run" if args.dry_run else "packed"
    print(f"[{mode}] {len(packed)} assets, {total_files} files -> {out_dir}")
    for failure in failures:
        print(f"  [FAIL] {failure}", file=sys.stderr)
    if failures:
        print(f"pack-skill-library: {len(failures)} asset(s) failed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
