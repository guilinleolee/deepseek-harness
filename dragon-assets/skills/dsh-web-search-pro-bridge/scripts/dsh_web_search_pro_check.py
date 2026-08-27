#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
dsh-web-search-pro 健康检查器（天龙侧桥 V1.0）

退出码契约（与 aihot / anysearch V3 对齐）：
  0  [OK]    健康（DSH profile 已装 dsh-web-search-pro）
  1  [FAIL]  dsh-web-search-pro 未装
  2  [WARN]  部分后端 missing（platforms 部分不可用）
  3  [FAIL]  当前环境不是 DSH / 无 $DSH_HOME

输出：ASCII-only（Windows GBK 兼容），emoji 通过 --json 走 JSON 编码。

用法：
  python dsh_web_search_pro_check.py                 # 默认探测 $DSH_HOME/profiles/web
  python dsh_web_search_pro_check.py --profile web   # 指定 profile 名
  python dsh_web_search_pro_check.py --json          # JSON 输出（CI 友好）
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


def detect_dsh_home() -> Path | None:
    """Locate $DSH_HOME; fall back to %USERPROFILE%/.dsh on Windows."""
    home = os.environ.get("DSH_HOME")
    if home:
        return Path(home)
    userprofile = os.environ.get("USERPROFILE") or os.environ.get("HOME")
    if userprofile:
        candidate = Path(userprofile) / ".dsh"
        if candidate.is_dir():
            return candidate
    return None


def resolve_profile_dir(dsh_home: Path, profile: str) -> Path:
    return dsh_home / "profiles" / profile


def check_bundle_installed(profile_dir: Path) -> dict[str, Any]:
    """Check if dsh-web-search-pro + @anweat/dsh-browser are installed."""
    nm = profile_dir / "node_modules"
    pro_dir = nm / "dsh-web-search-pro"
    browser_dir = nm / "@anweat" / "dsh-browser"

    result: dict[str, Any] = {
        "pro_installed": pro_dir.is_dir(),
        "browser_installed": browser_dir.is_dir(),
        "pro_version": None,
        "browser_version": None,
    }
    for label, path in (("pro_version", pro_dir), ("browser_version", browser_dir)):
        pkg = path / "package.json"
        if pkg.is_file():
            try:
                data = json.loads(pkg.read_text(encoding="utf-8"))
                result[label] = data.get("version")
            except (json.JSONDecodeError, OSError):
                pass
    return result


def check_profile_bundles(profile_dir: Path) -> dict[str, Any]:
    """Check if dsh.profile.bundles declares dsh-web-search-pro as a bundle layer."""
    pkg_json = profile_dir / "package.json"
    if not pkg_json.is_file():
        return {"manifest_exists": False, "declared_in_bundles": False}
    try:
        data = json.loads(pkg_json.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"manifest_exists": True, "manifest_parseable": False, "declared_in_bundles": False}
    bundles = ((data.get("dsh") or {}).get("profile") or {}).get("bundles") or []
    return {
        "manifest_exists": True,
        "manifest_parseable": True,
        "declared_in_bundles": "dsh-web-search-pro" in bundles,
        "bundle_count": len(bundles),
    }


def check_engines_in_settings(dsh_home: Path) -> dict[str, Any]:
    """Check if ~/.dsh/settings.yaml declares web-search-pro section."""
    settings = dsh_home / "settings.yaml"
    if not settings.is_file():
        return {"settings_exists": False, "section_declared": False}
    try:
        text = settings.read_text(encoding="utf-8")
    except OSError:
        return {"settings_exists": True, "readable": False, "section_declared": False}
    # very simple grep; YAML structure is whitespace-sensitive but the section
    # header itself is unambiguous
    return {
        "settings_exists": True,
        "readable": True,
        "section_declared": "web-search-pro:" in text,
    }


def check_workspace_dirty(repo_dir: Path) -> dict[str, Any]:
    """If repo_dir is a git repo, report uncommitted changes (warning only)."""
    if not (repo_dir / ".git").exists():
        return {"is_git_repo": False}
    import subprocess

    try:
        proc = subprocess.run(
            ["git", "-C", str(repo_dir), "status", "--short"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {"is_git_repo": True, "git_available": False}
    return {
        "is_git_repo": True,
        "git_available": True,
        "dirty_lines": proc.stdout.splitlines(),
        "is_dirty": bool(proc.stdout.strip()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="dsh-web-search-pro 健康检查器")
    parser.add_argument("--profile", default="web", help="DSH profile 名（默认 web）")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument(
        "--repo",
        default=r"D:\deepseek-harness",
        help="DSH 主仓根（用于 git dirty 检查）",
    )
    args = parser.parse_args()

    dsh_home = detect_dsh_home()
    if dsh_home is None:
        result = {"status": 3, "reason": "DSH_HOME not found (env or ~/.dsh)"}
        emit(result, args.json)
        return 3

    profile_dir = resolve_profile_dir(dsh_home, args.profile)
    if not profile_dir.is_dir():
        result = {
            "status": 1,
            "reason": f"profile {args.profile!r} not found at {profile_dir}",
        }
        emit(result, args.json)
        return 1

    installed = check_bundle_installed(profile_dir)
    bundles = check_profile_bundles(profile_dir)
    settings = check_engines_in_settings(dsh_home)
    dirty = check_workspace_dirty(Path(args.repo))

    if not installed["pro_installed"] or not installed["browser_installed"]:
        status = 1
        reason = (
            "dsh-web-search-pro 或 @anweat/dsh-browser 未安装到 "
            f"{profile_dir / 'node_modules'}"
        )
    elif not bundles.get("declared_in_bundles", False):
        status = 2
        reason = "package.json 已装但 dsh.profile.bundles 未声明（需重跑 `pnpm dsh plugin add`）"
    else:
        status = 0
        reason = "ok"

    payload = {
        "status": status,
        "reason": reason,
        "dsh_home": str(dsh_home),
        "profile_dir": str(profile_dir),
        "installed": installed,
        "bundles": bundles,
        "settings": settings,
        "repo_dirty": dirty,
    }
    emit(payload, args.json)
    return status


def emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    status = payload["status"]
    # ASCII-only output for Windows GBK compatibility (same convention as
    # aihot_check.py / anysearch V3 check scripts).
    icon = {0: "[OK]", 1: "[FAIL]", 2: "[WARN]", 3: "[FAIL]"}.get(status, "[?]")
    print(f"{icon} status={status}  reason={payload['reason']}")
    print(f"   DSH_HOME={payload['dsh_home']}")
    print(f"   profile_dir={payload['profile_dir']}")
    inst = payload["installed"]
    print(
        f"   installed: dsh-web-search-pro={inst['pro_version'] or 'MISSING'} "
        f"@anweat/dsh-browser={inst['browser_version'] or 'MISSING'}"
    )
    b = payload["bundles"]
    print(
        f"   bundles: declared={b.get('declared_in_bundles')}, count={b.get('bundle_count', '?')}"
    )
    s = payload["settings"]
    print(f"   settings.yaml: section_declared={s.get('section_declared')}")
    d = payload["repo_dirty"]
    if d.get("is_git_repo"):
        marker = "YES" if d.get("is_dirty") else "no"
        print(f"   repo_dirty={marker} ({len(d.get('dirty_lines', []))} lines)")


if __name__ == "__main__":
    sys.exit(main())
