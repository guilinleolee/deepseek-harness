#!/usr/bin/env python3
"""
gh_fetch.py — 比对 GitHub 上游仓库的 HEAD / license / archived / release 状态。
纯标准库实现（urllib + re + json + subprocess[git ls-remote]）。

Usage:
    python gh_fetch.py --input parse_output.json [--no-readme] [--no-network]
        > fetch_output.json

设计：逐 skill 调用，输入 parse_skill.py 的 JSON 输出，输出每 skill 的 remote 状态。
网络层失败统一归到 fetch_status 字段，不抛异常。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


USER_AGENT = "skill-updater/1.0 (https://github.com/tianlong)"
GITHUB_API = "https://api.github.com"


def gh_api(path: str, token: str | None = None, timeout: int = 10) -> tuple[int, dict[str, Any] | None, dict[str, str] | None]:
    """调 GitHub REST API。返回 (status_code, json_or_None, headers_or_None)。
    status_code: 200/403/404/..., -1 表示 urllib 网络层异常(URL 错 / 超时 / 拒接)。
    """
    url = f"{GITHUB_API}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8")), dict(resp.headers)
    except urllib.error.HTTPError as e:
        # HTTPError 自带 headers,可以拿 X-RateLimit-Remaining 判断是否真的限流
        return e.code, None, dict(e.headers) if e.headers else None
    except (urllib.error.URLError, TimeoutError, OSError):
        return -1, None, None


def _fetch_latest_release(owner: str, repo: str, token: str | None) -> dict[str, Any] | None:
    """拉取最新 release 元数据,失败返回 None。"""
    rel_status, rel_data, _ = gh_api(f"/repos/{owner}/{repo}/releases/latest", token=token)
    if rel_status == 200 and rel_data:
        return {
            "tag": rel_data.get("tag_name"),
            "published_at": rel_data.get("published_at"),
            "notes_excerpt": (rel_data.get("body") or "")[:200],
        }
    return None


def _fetch_readme(owner: str, repo: str, token: str | None) -> str | None:
    """拉取 README base64 content,解码前 500 字,失败返回 None。"""
    import base64
    status, data, _ = gh_api(f"/repos/{owner}/{repo}/readme", token=token)
    if status == 200 and data and "content" in data:
        try:
            decoded = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
            return decoded[:500]
        except Exception:
            return None
    return None


def git_ls_remote(owner: str, repo: str, timeout: int = 10) -> dict[str, str]:
    """调 git ls-remote 拿 HEAD + 各 ref 的 SHA。"""
    try:
        result = subprocess.run(
            ["git", "ls-remote", f"https://github.com/{owner}/{repo}.git"],
            capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode != 0:
            return {"error": result.stderr.strip() or "ls-remote failed"}
    except FileNotFoundError:
        return {"error": "git not installed"}
    except subprocess.TimeoutExpired:
        return {"error": "ls-remote timeout"}

    refs: dict[str, str] = {}
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        sha, ref = line.split("\t", 1)
        refs[ref.strip()] = sha.strip()
    return refs


def fetch_remote(owner: str, repo: str, *, with_readme: bool = True, token: str | None = None) -> dict[str, Any]:
    """对单个 GitHub 仓库抓 HEAD + license + archived + 最新 release + README 摘要。

    返回 schema 见 design.md §2.2。
    """
    out: dict[str, Any] = {
        "owner": owner, "repo": repo,
        "fetch_status": "ok",
        "remote": {},
        "fetch_warnings": [],
    }

    # 1. HEAD SHA 优先从 GitHub API 拿（urllib 通常比 git ls-remote 在 Git Bash 上更稳）
    api_status, api_data, api_headers = gh_api(f"/repos/{owner}/{repo}", token=token)
    if api_status == 404:
        out["fetch_status"] = "not_found"
        out["fetch_warnings"].append("GitHub API returned 404")
        return out
    if api_status == 403:
        out["fetch_status"] = "rate_limited"
        remaining = (api_headers or {}).get("X-RateLimit-Remaining", "?") if api_headers else "?"
        out["fetch_warnings"].append(f"GitHub API rate limited (剩余 {remaining});建议 export GITHUB_TOKEN=... 提高限额")
        return out
    if api_status != 200 or not api_data:
        out["fetch_status"] = "network_error"
        out["fetch_warnings"].append(f"GitHub API returned {api_status}")
        return out

    head_sha = (api_data.get("sha") or "")[:7]
    default_branch = api_data.get("default_branch", "main")
    archived = api_data.get("archived", False)
    stars = api_data.get("stargazers_count")
    license_obj = api_data.get("license") or {}
    license_spdx = license_obj.get("spdx_id")

    # 2. 尝试 git ls-remote 拿更精确的 HEAD（失败不阻塞）
    refs = git_ls_remote(owner, repo)
    if "error" not in refs:
        ls_sha = refs.get("HEAD", "")[:7]
        if ls_sha:
            head_sha = ls_sha
        # main/master override
        if "refs/heads/main" in refs:
            default_branch = "main"
        elif "refs/heads/master" in refs:
            default_branch = "master"
    else:
        out["fetch_warnings"].append(f"ls-remote {refs['error']}（已 fallback 到 API HEAD）")

    # 3. 最新 release
    latest_release = _fetch_latest_release(owner, repo, token)

    # 4. README 抓取（仅取前 500 字）
    readme_excerpt = _fetch_readme(owner, repo, token) if with_readme else None

    out["remote"] = {
        "head_sha": head_sha[:7] if head_sha else None,
        "default_branch": default_branch,
        "archived": archived,
        "license_spdx": license_spdx,
        "stars": stars,
        "latest_release": latest_release,
        "commits_behind": None,  # V1.0 暂不算精确 commit diff（见 design.md §6.3）
        "readme_excerpt": readme_excerpt,
    }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="GitHub 上游比对")
    parser.add_argument("--input", required=True, help="parse_skill.py 输出的 JSON 文件路径")
    parser.add_argument("--no-readme", action="store_true", help="跳过 README 抓取")
    parser.add_argument("--no-network", action="store_true", help="跳过所有网络请求")
    parser.add_argument("--timeout", type=int, default=10, help="单请求超时秒")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or None

    try:
        with open(args.input, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: failed to read input: {e}", file=sys.stderr)
        return 2

    results: list[dict[str, Any]] = []
    for skill in data.get("skills", []):
        src = skill.get("source", {})
        if src.get("type") != "github":
            # 本地 / 缺失 / unparseable：跳过网络
            results.append({
                "name": skill["name"],
                "fetch_status": "skipped",
                "remote": {},
                "fetch_warnings": [f"source type is {src.get('type')}, not github"],
            })
            continue
        if args.no_network:
            results.append({
                "name": skill["name"],
                "fetch_status": "skipped",
                "remote": {},
                "fetch_warnings": ["--no-network specified"],
            })
            continue
        owner, repo = src["owner"], src["repo"]
        remote = fetch_remote(owner, repo, with_readme=not args.no_readme, token=token)
        remote["name"] = skill["name"]
        results.append(remote)

    print(json.dumps({"fetched_at": _now_iso(), "results": results}, ensure_ascii=False, indent=2))
    return 0


def _now_iso() -> str:
    import datetime as _dt
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    sys.exit(main())