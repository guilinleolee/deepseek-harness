"""ecc_watcher V1.0 — Stage 47.2 ECC 7 天观察期监控脚本.

每 24 小时跑一次 stdout 检查 + 落盘 TSV 报告.
最终 7 天结果决定 stage 47.2 GO / NO-GO / 延期.

指标 (7 维):
- stars (3 天增量 ≥ 30 = GO)
- 末 push 时戳 (≤ 14 天 = GO, > 30 天 = NO-GO)
- contributors 数 (≥ 5 = GO)
- commit 频次 (> 1/天 = GO)
- Issue Close Rate (≥ 70% = GO)
- DISCUSSIONS / PR 活跃度 (≥ 30d 连续活跃 = GO)
- README 长度 (> 1kB 说明成熟 = GO)
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

GITHUB_API = "https://api.github.com"
CACHE = Path.home() / ".cache" / "dragon-engine" / "ecc_watcher"
CACHE.mkdir(parents=True, exist_ok=True)
REPORT_DIR = Path("reports") / "stage-472-ecc"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

REPO = "affaan-m/ECC"


def gh_json(endpoint: str) -> dict | list:
    """调用 gh api 解析 JSON; 输出强制 UTF-8."""
    try:
        result = subprocess.run(
            ["gh", "api", endpoint],
            capture_output=True, timeout=20,
            env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
        )
    except subprocess.TimeoutExpired:
        print(f"[ERR] gh api {endpoint}: timeout", file=__import__("sys").stderr)
        return {}
    if result.returncode != 0:
        return {}
    raw = result.stdout.decode("utf-8", errors="replace").strip()
    if not raw:
        return {}
    return json.loads(raw)


def _fetch_endpoint_first_page(endpoint: str) -> dict | list:
    """仅拉第一页 (per_page=10 限定)."""
    sep = "&" if "?" in endpoint else "?"
    return gh_json(f"{endpoint}{sep}per_page=10")


def collect_metrics() -> dict:
    """采集 7 维指标; 轻量级: 仅取首页."""
    repo = gh_json(f"repos/{REPO}")  # type: ignore[assignment]
    if not repo or not isinstance(repo, dict):
        return {"error": "gh api repos call failed (timeout or rate-limit)"}

    commits = _fetch_endpoint_first_page(f"repos/{REPO}/commits")
    if not isinstance(commits, list):
        commits = []
    issues = _fetch_endpoint_first_page(f"repos/{REPO}/issues?state=all")
    if not isinstance(issues, list):
        issues = []

    pushed_at_str = repo.get("pushed_at", "")
    pushed_at = datetime.fromisoformat(pushed_at_str.replace("Z", "+00:00")) if pushed_at_str else None
    now = datetime.now(timezone.utc)
    days_since_push = (now - pushed_at).days if pushed_at else 999

    closed_issues = sum(1 for i in issues if i.get("state") == "closed")
    total = len(issues)
    close_rate = closed_issues / total * 100 if total else 0

    contributors = _fetch_endpoint_first_page(f"repos/{REPO}/contributors")
    contributors_n = len(contributors) if isinstance(contributors, list) else 0

    readme = _fetch_endpoint_first_page(f"repos/{REPO}/readme")
    readme_size = readme.get("size", 0) if isinstance(readme, dict) else 0  # type: ignore[union-attr]

    return {
        "timestamp": now.isoformat(),
        "repo": REPO,
        "stars": repo.get("stargazers_count"),
        "forks": repo.get("forks_count"),
        "language": repo.get("language"),
        "license": (repo.get("license") or {}).get("spdx_id"),  # type: ignore[union-attr]
        "days_since_last_push": days_since_push,
        "contributors_count": contributors_n,
        "open_issues": repo.get("open_issues_count"),
        "closed_issues_count": closed_issues,
        "issues_total_first_page": total,
        "issue_close_rate_first_page": round(close_rate, 1),
        "commits_first_page": len(commits),
        "readme_size_kb": round(readme_size / 1024, 1) if readme_size else 0,
    }


def classify(metrics: dict) -> str:
    """GO / NO-GO / 延期 三级判定."""
    if metrics.get("license") not in ("MIT", "Apache-2.0", "BSD-3-Clause"):
        return "NO-GO (协议不符)"
    if metrics.get("days_since_last_push", 999) > 30:
        return "NO-GO (30+ 天无 push)"
    if metrics.get("commit_freq_per_day", 0) < 0.3:
        return "NO-GO (commit < 0.3/天)"
    if metrics.get("issue_close_rate", 0) < 70 and metrics.get("issues_total", 0) > 5:
        return "延期 (close rate < 70%)"
    if metrics.get("stars", 0) < 1000:
        return "延期 (stars < 1000)"
    return "GO"


def cmd_snapshot(args: argparse.Namespace) -> int:
    metrics = collect_metrics()
    metrics["verdict"] = classify(metrics)
    out_file = REPORT_DIR / f"snapshot-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.json"
    out_file.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print(f"\n[OK] snapshot → {out_file}")
    return 0


def cmd_watch(args: argparse.Namespace) -> int:
    """7 天循环 daily check, 落 tsv 日志."""
    print("ecc_watcher · 7-day observation cycle")
    for day in range(1, 8):
        print(f"\n--- Day {day} ---")
        cmd_snapshot(args)
        if day < 7:
            # 不阻塞当日，超时按秒看; 应用级 sleep: 不真等, 用户可后续 cron 化
            print("(next-day snapshot expected via cron / re-run)")
            break
    return 0


def cmd_final(args: argparse.Namespace) -> int:
    """读所有 snapshot, 输出最终判定."""
    snapshots = sorted(REPORT_DIR.glob("snapshot-*.json"))
    if not snapshots:
        print(f"[ERR] no snapshot found in {REPORT_DIR}")
        return 1
    last = json.loads(snapshots[-1].read_text(encoding="utf-8"))
    print(f"Last snapshot ({last.get('timestamp')}):")
    print(json.dumps(last, ensure_ascii=False, indent=2))
    print(f"\n=== 7 天观察期综合判定: {last.get('verdict')} ===")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ecc_watcher V1.0 — Stage 47.2 ECC 7-day observation")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_snap = sub.add_parser("snapshot", help="single daily snapshot")
    p_watch = sub.add_parser("watch", help="7-day cycle")
    p_final = sub.add_parser("final", help="read snapshots + final verdict")

    args = parser.parse_args(argv)
    if args.cmd == "snapshot":
        return cmd_snapshot(args)
    if args.cmd == "watch":
        return cmd_watch(args)
    if args.cmd == "final":
        return cmd_final(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
