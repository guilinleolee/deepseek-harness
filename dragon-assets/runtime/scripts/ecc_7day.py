"""ecc_7day V1.0 — Stage 47.2 ECC 7 天一次性监控循环.

每日 1 snapshot, 落 JSON + tsv 双产物.
Day 7 auto-judge (GO/延期/NO-GO).

用法:
    # 一次性 Day 1-7
    python scripts/ecc_7day.py
    # 仅运行 1 天 (snapshot)
    python scripts/ecc_7day.py single
    # 7 天总结 + verdict
    python scripts/ecc_7day.py final

7 维判定阈值 (与 ecc_watcher.py 一致):
    1. stars 增量          (3 天 ≥ 30 → GO)
    2. last push           (≤ 14 天 → GO, > 30 → NO-GO)
    3. contributors        (≥ 5 → GO)
    4. commit_freq_per_day (> 1/天 → GO, < 0.3 → NO-GO)
    5. issue_close_rate    (≥ 70% (issues > 5) → GO)
    6. 持续活跃度         (30d 连续有 commit → GO)
    7. README 长度         (≥ 1 KB → GO)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = "affaan-m/ECC"
DEFAULT_REPORT_DIR = Path("reports") / "stage-472-ecc"
TSV_FILE = DEFAULT_REPORT_DIR / "ecc_daily_log.tsv"
LOCK = DEFAULT_REPORT_DIR / ".ecc_7day.lock"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _day_key(d: datetime | None = None) -> str:
    """Day-key YYYY-MM-DD UTC."""
    d = d or datetime.now(timezone.utc)
    return d.strftime("%Y-%m-%d")


def _already_today_snapshot() -> bool:
    """同一天禁止重复 snapshot."""
    if not TSV_FILE.exists():
        return False
    today = _day_key()
    with TSV_FILE.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("day_key\t"):
                continue
            parts = line.rstrip("\n").split("\t")
            if parts and parts[0] == today:
                return True
    return False


def _save_snapshot(metrics: dict[str, object], verdict: str) -> None:
    """落 JSON 文件 + TSV 行."""
    DEFAULT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    day = _day_key()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    json_path = DEFAULT_REPORT_DIR / f"snapshot-{stamp}.json"
    json_path.write_text(
        json.dumps(
            {"timestamp": metrics.get("timestamp"), "day_key": day, "verdict": verdict, **metrics},
            ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )

    # TSV: append single line (idempotent per day)
    tsv_header = (
        "day_key\ttimestamp\tstars\tforks\tcontributors\tdays_since_push\t"
        "issues_total\tissues_closed\tclose_rate\tcommits_first_page\t"
        "readme_size_kb\tverdict\n"
    )
    write_header = not TSV_FILE.exists()
    with TSV_FILE.open("a", encoding="utf-8", newline="") as fh:
        if write_header:
            fh.write(tsv_header)
        row = "\t".join(
            [
                day,
                str(metrics.get("timestamp", "")),
                str(metrics.get("stars", "")),
                str(metrics.get("forks", "")),
                str(metrics.get("contributors_count", "")),
                str(metrics.get("days_since_last_push", "")),
                str(metrics.get("issues_total_first_page", "")),
                str(metrics.get("closed_issues_count", "")),
                str(metrics.get("issue_close_rate_first_page", "")),
                str(metrics.get("commits_first_page", "")),
                str(metrics.get("readme_size_kb", "")),
                verdict,
            ]
        )
        fh.write(row + "\n")

    print(f"[OK] snapshot saved → {json_path}")


def _run_watcher_snapshot() -> dict[str, object]:
    """委托 ecc_watcher.py snapshot 子命令, 解析 stdout JSON."""
    result = subprocess.run(
        [sys.executable, str(Path("scripts/ecc_watcher.py").resolve()), "snapshot"],
        capture_output=True, timeout=60,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if result.returncode != 0:
        err = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"ecc_watcher.py failed: {err[:300]}")
    out = result.stdout.decode("utf-8", errors="replace")
    # ecc_watcher 输出含 "[OK] snapshot → ..." 等附加行, 取首段 JSON
    start = out.find("{")
    end = out.rfind("}")
    if start < 0 or end < 0:
        raise RuntimeError(f"ecc_watcher 没有 JSON 输出: {out[:300]}")
    parsed: dict[str, object] = json.loads(out[start:end + 1])
    return parsed


def cmd_single(args: argparse.Namespace) -> int:
    """当日 snapshot, 落 JSON + TSV."""
    if _already_today_snapshot():
        print(f"[OK] Day {_day_key()} 已 snapshot 过, 跳过 (idempotent)")
        return 0
    metrics = _run_watcher_snapshot()
    verdict = str(metrics.get("verdict", "UNKNOWN"))
    _save_snapshot(metrics, verdict)
    return 0


def cmd_final(args: argparse.Namespace) -> int:
    """总结 7 天数据, 输出 GO/NO-GO 决策."""
    if not TSV_FILE.exists():
        print(f"[ERR] TSV 不存在: {TSV_FILE}")
        return 1
    rows = []
    with TSV_FILE.open("r", encoding="utf-8") as fh:
        header = None
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if not parts or not parts[0]:
                continue
            if header is None:
                header = parts
                continue
            if parts[0] == "day_key":
                continue
            rows.append(dict(zip(header, parts)))
    rows.sort(key=lambda r: r.get("day_key", ""))
    print(f"=== 观察期汇总 ({len(rows)} 天)===")
    print(f"  start: {rows[0].get('day_key') if rows else 'N/A'}")
    print(f"  end:   {rows[-1].get('day_key') if rows else 'N/A'}")
    if len(rows) < 2:
        print("[INFO] 数据 < 2 天, 不计算 star 增量")
    else:
        try:
            star_start = int(rows[0].get("stars", 0))
            star_end = int(rows[-1].get("stars", 0))
            star_delta = star_end - star_start
            print(f"  stars delta: {star_delta:+d} ({star_start} → {star_end})")
        except ValueError:
            print("  [WARN] stars 解析失败")
    # 7 维判定 (基于最后一天)
    last = rows[-1] if rows else {}
    by_votes = {"GO": 0, "延期": 0, "NO-GO": 0, "UNKNOWN": 0}
    for r in rows:
        v = r.get("verdict", "")
        if "GO" in v and "NO-GO" not in v:
            by_votes["GO"] += 1
        elif "NO-GO" in v:
            by_votes["NO-GO"] += 1
        elif "延期" in v:
            by_votes["延期"] += 1
        else:
            by_votes["UNKNOWN"] += 1
    print(f"\n=== 7 维判定投票 ===")
    for k, v in by_votes.items():
        print(f"  {k}: {v} / {len(rows)}")

    # 最终 verdict
    if by_votes["NO-GO"] >= 2:
        final = "🔴 NO-GO (观察期有 ≥ 2 天 NO-GO)"
    elif by_votes["GO"] >= 5 and by_votes["NO-GO"] == 0:
        final = "🟢 GO (≥ 5 天 GO + 0 NO-GO)"
    elif by_votes["延期"] >= 3:
        final = "🟡 延期 (≥ 3 天延期, 待真实 commit_freq)"
    else:
        final = "🟡 待续 (7 天数据不足, 30 天后再评)"
    print(f"\n=== 最终判定 ===\n  {final}")
    return 0


def cmd_loop(args: argparse.Namespace) -> int:
    """Day 1-7 一次性循环 (主要用于离线测试)."""
    days = max(1, args.days)
    for i in range(days):
        print(f"\n--- Day {i + 1}/{days} ---")
        rc = cmd_single(args)
        if rc != 0:
            print(f"[WARN] Day {i + 1} snapshot 退出码 {rc}")
        if i < days - 1:
            print("(不阻塞当日, 用户可后续 cron 化)")
            break
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """查看 TSV 当前进度."""
    if not TSV_FILE.exists():
        print(f"[INFO] TSV 不存在 ({TSV_FILE}), 尚无 snapshot")
        return 0
    print(f"=== {TSV_FILE} ===")
    with TSV_FILE.open("r", encoding="utf-8") as fh:
        for line in fh:
            sys.stdout.write(line)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ecc_7day V1.0 — Stage 47.2 ECC 7-day loop")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_single = sub.add_parser("single", help="当日 snapshot (idempotent per day)")
    p_loop = sub.add_parser("loop", help="Day 1-N 一次性循环 (默认 7)")
    p_loop.add_argument("--days", type=int, default=7)
    p_final = sub.add_parser("final", help="总结 + verdict")
    p_status = sub.add_parser("status", help="查 TSV 当前进度")

    args = parser.parse_args(argv)
    if args.cmd == "single":
        return cmd_single(args)
    if args.cmd == "loop":
        return cmd_loop(args)
    if args.cmd == "final":
        return cmd_final(args)
    if args.cmd == "status":
        return cmd_status(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
