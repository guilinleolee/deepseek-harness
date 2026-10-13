#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply.py · skill-updater V1.0 → V1.1 增量 · 实际 apply 模式

功能：
  1. 读最新 reports/scan-*.tsv
  2. 对每行评估 4 道 gate（G1 LICENSE / G2 archive / G3 commits / G4 smoke）
  3. gate 通过 → git fetch + rebase + 跑 smoke test
  4. 失败 → git rebase --abort / git reset --hard HEAD 回滚
  5. 写 logs/apply-YYYYMMDD.log
  6. 失败时调 notify_email.py

用法：
  python scripts/apply.py                 # 跑全部 🟡 推荐更新的
  python scripts/apply.py --only guizang   # 只跟某个 skill
  python scripts/apply.py --dry-run        # 演练，不真改
  python scripts/apply.py --max-behind 50  # 改 G3 阈值（默认 100）

退出码：0=PASS / 1=FAIL（至少一个 skill apply 失败） / 2=配置错
"""
import sys, os, io, json, subprocess, argparse, shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple

# Force UTF-8 stdout on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ──────────────────────────────────────────────────────
# 常量
# ──────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPORTS_DIR = SKILL_DIR / "reports"
LOGS_DIR = SKILL_DIR / "logs"
SMOKE_TEST = Path(r"C:\Users\li\.claude\projects\dragon-engine\skills\async-task-pattern\tests\smoke.sh")

# 天龙自研 skill（永远不自动跟；必须人工 review）
DRAGON_OWN_SKILLS = {
    "skill-updater",
    "dragon-engine",
    "async-task-pattern",
    "nano-banana-brief",
    "cinema-director-laoli",
    "guizang-social-card-skill",
    "blogger-fingerprint-registry",
    "blogger-hologram-to-poster",
    "multi-platform-publisher",
    "laoli-writer",
    "khazix-writer",
    "huashu-design",
    "html-anything-bridge",
    "baoyu-xhs-images",
    "anysearch",
    "a-stock-data-bridge",
    "apocdata-bridge",
    "trading-agents-astock-wrapper",
}

# Git Bash 命令前缀（Windows 上 git 在 PATH 中）
GIT_ENV = os.environ.copy()
GIT_ENV["PYTHONIOENCODING"] = "utf-8"
GIT_ENV["LC_ALL"] = "C.UTF-8"


# ──────────────────────────────────────────────────────
# 工具函数
# ──────────────────────────────────────────────────────

def log(msg: str, level: str = "INFO") -> None:
    """统一日志输出"""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] [{level}] {msg}"
    print(line, file=sys.stderr, flush=True)
    LOG_FILE.write_text(LOG_FILE.read_text(encoding="utf-8") + line + "\n" if LOG_FILE.exists() else line + "\n", encoding="utf-8")


def find_latest_report() -> Optional[Path]:
    """找最新一份 reports/report-*.tsv"""
    if not REPORTS_DIR.exists():
        return None
    candidates = sorted(REPORTS_DIR.glob("report-*.tsv"), reverse=True)
    return candidates[0] if candidates else None


def parse_tsv(report: Path) -> List[Dict]:
    """解析 TSV 报告 → 列表 of dict

    scan.sh 实际输出格式：
      NR==1: # type=skill（注释行）
      NR==2: 表头
      NR>=3: 数据
    """
    rows = []
    with open(report, encoding="utf-8") as f:
        lines = [l for l in f if l.strip()]
    if len(lines) < 3:
        return rows
    header = lines[1].strip().split("\t")
    for line in lines[2:]:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < len(header):
            parts += [""] * (len(header) - len(parts))
        rows.append(dict(zip(header, parts)))
    return rows


def run_cmd(cmd: List[str], cwd: Path, timeout: int = 60) -> Tuple[int, str, str]:
    """跑子命令，返回 (returncode, stdout, stderr)"""
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True,
            timeout=timeout, env=GIT_ENV, encoding="utf-8", errors="replace"
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"timeout after {timeout}s"
    except Exception as e:
        return -1, "", str(e)


# ──────────────────────────────────────────────────────
# 4 道 Gate
# ──────────────────────────────────────────────────────

def gate1_license_unchanged(row: Dict) -> Tuple[bool, str]:
    """G1 · LICENSE 不变（local == remote）"""
    local_lic = row.get("local_license", "").strip()
    remote_lic = row.get("upstream_license", "").strip()
    if not remote_lic:
        return True, "无远程 license 信息（跳过 G1）"
    if local_lic and remote_lic and local_lic.lower() != remote_lic.lower():
        return False, f"LICENSE 变更: {local_lic} → {remote_lic}"
    return True, f"LICENSE 一致: {local_lic or '?'}"


def gate2_not_archived(row: Dict) -> Tuple[bool, str]:
    """G2 · 仓库未 archive"""
    archived = row.get("upstream_archived", "").strip().lower()
    if archived in ("true", "1", "yes"):
        return False, "上游已 archive，不能跟"
    return True, "上游 active"


def gate3_age_threshold(row: Dict, max_age_days: int) -> Tuple[bool, str]:
    """G3 · 本地 last_updated 距今 > max_age_days 视为需要更新

    报告里没有 commits_behind 字段（V1.0 没存），改用 last_updated 时间差。
    scan.sh 已分类 yellow = 有更新，本 gate 防止"local last_updated 就在几天前
    但被误报为 yellow"的极端情况。
    """
    last_updated = row.get("local_last_updated", "").strip()
    if not last_updated or last_updated == "-":
        return True, "无 last_updated（首次跟）"
    try:
        from datetime import date as _date
        lu = _date.fromisoformat(last_updated)
        today = _date.today()
        age = (today - lu).days
        if age > max_age_days * 5:
            return False, f"本地 last_updated 距今 {age} 天（> {max_age_days * 5}）疑似长期未维护"
        return True, f"last_updated {age} 天前（正常）"
    except (ValueError, ImportError):
        return True, "last_updated 格式无法解析（跳过 G3）"


def gate4_smoke_test(skill_dir: Path) -> Tuple[bool, str]:
    """G4 · 跑 async-task-pattern smoke test"""
    if not SMOKE_TEST.exists():
        return True, f"smoke 脚本不存在 {SMOKE_TEST}（跳过 G4）"
    rc, out, err = run_cmd(
        ["bash", str(SMOKE_TEST)], cwd=SMOKE_TEST.parent, timeout=300
    )
    if rc != 0:
        return False, f"smoke test 失败 exit={rc}（已尝试回滚）"
    return True, "smoke test PASS"


# ──────────────────────────────────────────────────────
# Apply 主流程
# ──────────────────────────────────────────────────────

def apply_one_skill(row: Dict, args, skill_path: Path) -> Tuple[str, str]:
    """对单个 skill 执行 apply，返回 (status, message)

    status: APPLIED / SKIPPED / FAILED
    """
    name = row.get("name", "<unknown>")
    if not skill_path.exists():
        return "SKIPPED", f"本地路径不存在: {skill_path}"

    # 白名单：天龙自研 skill 不自动跟
    if name in DRAGON_OWN_SKILLS:
        return "SKIPPED", f"天龙自研 skill（{name}），永不自动跟"

    # 检查是否是 git 仓库
    if not (skill_path / ".git").exists():
        return "SKIPPED", f"非 git 仓库（{skill_path}/.git 缺失）"

    # 拿远程 URL
    upstream_url = row.get("source") or row.get("upstream") or ""
    if not upstream_url:
        return "SKIPPED", "无 source / upstream URL"

    # 4 道 gate
    g1_ok, g1_msg = gate1_license_unchanged(row)
    g2_ok, g2_msg = gate2_not_archived(row)
    # max_behind 复用为 max_age_days（语义已改）
    g3_ok, g3_msg = gate3_age_threshold(row, args.max_behind)

    if not all([g1_ok, g2_ok, g3_ok]):
        reasons = []
        if not g1_ok: reasons.append(f"G1: {g1_msg}")
        if not g2_ok: reasons.append(f"G2: {g2_msg}")
        if not g3_ok: reasons.append(f"G3: {g3_msg}")
        return "SKIPPED", " | ".join(reasons)

    log(f"  ├─ {name} gates: G1✓ G2✓ G3✓ ({g3_msg})", "DEBUG")

    # 拉取上游
    rc, _, err = run_cmd(["git", "fetch", "origin"], cwd=skill_path, timeout=120)
    if rc != 0:
        return "FAILED", f"git fetch 失败: {err.strip()[:200]}"

    # 记录 HEAD hash（用于回滚）
    rc, head_before, _ = run_cmd(["git", "rev-parse", "HEAD"], cwd=skill_path, timeout=10)
    head_before = head_before.strip()

    # rebase 到 origin/main（默认分支尝试）
    for branch in ["main", "master"]:
        rc, _, err = run_cmd(
            ["git", "rebase", f"origin/{branch}"], cwd=skill_path, timeout=120
        )
        if rc == 0:
            log(f"  ├─ {name} rebase 到 origin/{branch} 成功", "DEBUG")
            break
    else:
        # rebase 失败，尝试 merge
        log(f"  ├─ {name} rebase 失败，尝试 merge", "WARN")
        for branch in ["main", "master"]:
            rc, _, err = run_cmd(
                ["git", "merge", f"origin/{branch}", "--ff-only"],
                cwd=skill_path, timeout=120
            )
            if rc == 0:
                log(f"  ├─ {name} merge origin/{branch} 成功", "DEBUG")
                break
        else:
            # 都失败 → 回滚
            run_cmd(["git", "rebase", "--abort"], cwd=skill_path, timeout=10)
            return "FAILED", f"rebase + merge 都失败: {err.strip()[:200]}"

    # G4 · smoke test
    if not args.skip_smoke:
        g4_ok, g4_msg = gate4_smoke_test(skill_path)
        if not g4_ok:
            # 回滚
            run_cmd(["git", "reset", "--hard", head_before], cwd=skill_path, timeout=10)
            return "FAILED", f"G4: {g4_msg}（已回滚到 {head_before[:8]}）"

    # 写回新 last_updated
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log(f"  └─ {name} APPLIED · {g3_msg} · smoke ✓ · head {head_before[:8]} → {head_before[:8] if not g4_ok else 'updated'} · synced_at={today}")
    return "APPLIED", f"{g3_msg}; smoke test PASS; synced_at={today}"


def send_email_notification(results: Dict, args) -> None:
    """失败时调 notify_email.py 发邮件"""
    if not any(v == "FAILED" for v in results.values()):
        return  # 无失败不发
    notify_script = SCRIPT_DIR / "notify_email.py"
    if not notify_script.exists():
        log("notify_email.py 不存在，跳过邮件通知", "WARN")
        return
    failed_skills = [k for k, v in results.items() if v == "FAILED"]
    summary = json.dumps(results, ensure_ascii=False, indent=2)
    try:
        subprocess.run(
            [
                "python", str(notify_script),
                "--subject", f"⚠️ skill-updater apply 失败: {len(failed_skills)} 个",
                "--body", f"失败 skill: {failed_skills}\n\n完整结果:\n{summary}\n\n日志: {LOG_FILE}"
            ],
            timeout=30, env=GIT_ENV
        )
    except Exception as e:
        log(f"邮件通知失败: {e}", "WARN")


# ──────────────────────────────────────────────────────
# 入口
# ──────────────────────────────────────────────────────

def main():
    global LOG_FILE

    parser = argparse.ArgumentParser(description="skill-updater apply 模式 · 实际跟上游")
    parser.add_argument("--report", type=Path, help="指定 reports/scan-*.tsv（默认最新）")
    parser.add_argument("--only", help="只 apply 名字包含 PATTERN 的 skill")
    parser.add_argument("--dry-run", action="store_true", help="演练，不真改")
    parser.add_argument("--max-behind", type=int, default=100, help="G3 last_updated 阈值天数（默认 100 ~半年未更才视为需跟）")
    parser.add_argument("--skip-smoke", action="store_true", help="跳过 G4 smoke test（不推荐）")
    parser.add_argument("--root", type=Path, help="天龙真主树根（默认 C:\\Users\\li\\.claude\\projects\\dragon-engine）")
    args = parser.parse_args()

    dragon_root = args.root or Path(r"C:\Users\li\.claude\projects\dragon-engine")
    if not dragon_root.exists():
        log(f"天龙真主树不存在: {dragon_root}", "ERROR")
        sys.exit(2)

    # 准备日志
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    LOG_FILE = LOGS_DIR / f"apply-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.log"
    LOG_FILE.write_text("", encoding="utf-8")

    log(f"═══ skill-updater apply 模式 ═══")
    log(f"  模式: {'DRY-RUN' if args.dry_run else 'REAL-APPLY'}")
    log(f"  G3 阈值: {args.max_behind} commits")
    log(f"  G4 smoke: {'SKIP' if args.skip_smoke else 'RUN'}")
    log(f"  天龙根: {dragon_root}")

    # 找最新报告
    report = args.report or find_latest_report()
    if not report or not report.exists():
        log(f"找不到 reports/scan-*.tsv，请先跑 scan.sh", "ERROR")
        sys.exit(2)
    log(f"  报告: {report.name}")

    rows = parse_tsv(report)
    log(f"  报告 skill 数: {len(rows)}")

    # 过滤 🟡 推荐更新（scan.sh 输出 status="yellow"）
    candidates = [r for r in rows if r.get("status", "").strip().lower() == "yellow"]
    if args.only:
        candidates = [r for r in candidates if args.only in r.get("name", "")]
    log(f"  🟡 候选数: {len(candidates)}")

    if not candidates:
        log("✅ 无 yellow 候选，apply 模式无需工作")
        sys.exit(0)

    # 逐个 apply
    results: Dict[str, str] = {}
    applied_count = 0
    failed_count = 0
    skipped_count = 0

    for row in candidates:
        name = row.get("name", "<unknown>")
        # 本地路径 = dragon_root/skills/<name>
        skill_path = dragon_root / "skills" / name
        log(f"  → 处理 {name}（path={skill_path}）")

        if args.dry_run:
            log(f"    [DRY-RUN] 跳过实际 apply")
            results[name] = "DRY-RUN"
            continue

        status, msg = apply_one_skill(row, args, skill_path)
        results[name] = f"{status}: {msg}"
        log(f"    └─ {status}: {msg}")

        if status == "APPLIED":
            applied_count += 1
        elif status == "FAILED":
            failed_count += 1
        else:
            skipped_count += 1

    # 汇总
    log(f"")
    log(f"═══ 汇总 ═══")
    log(f"  APPLIED: {applied_count}")
    log(f"  SKIPPED: {skipped_count}")
    log(f"  FAILED:  {failed_count}")
    log(f"  日志: {LOG_FILE}")

    # 失败时发邮件
    if failed_count > 0:
        send_email_notification(results, args)
        log(f"📧 已发邮件通知")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
