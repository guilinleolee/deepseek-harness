#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""backup-web-access.py · web-access skill 增量备份到 V8 归档

功能：
- 每 5 分钟增量同步 web-access/ 到 D:\\知识库\\天龙引擎\\dragon-engine-backup-20260722\\skills\\web-access\\
- 用 robocopy 的 /MIR 等价实现（cp + 删除目标侧多余文件）
- 保留：config.env 不复制（V8 归档中 config.env 是从 templates 自动生成的副本，可重新生成）
- 保留：site-experience.yaml（本地累积的站点经验）
- 输出：单行同步报告（PASS / FAIL + 同步文件数）

用法：
  python scripts/backup-web-access.py             # 执行一次同步
  python scripts/backup-web-access.py --dry-run   # 只打印将要做的，不实际复制
"""
import sys, os, io, shutil, time
from pathlib import Path

# Force UTF-8 stdout on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# --- 路径配置 ---
SRC = Path(os.environ.get(
    "WEB_ACCESS_SRC",
    r"C:\Users\li\.claude\projects\dragon-engine\skills\web-access"
))
DST = Path(os.environ.get(
    "WEB_ACCESS_DST",
    r"D:\知识库\天龙引擎\dragon-engine-backup-20260722\skills\web-access"
))

# 不复制的文件（避免泄露本地浏览器偏好 + 自动生成物）
EXCLUDE_NAMES = {"config.env", "node_modules", ".DS_Store"}
EXCLUDE_SUFFIXES = (".log", ".tmp", ".bak")


def should_exclude(name: str) -> bool:
    """判断单个文件/目录是否要排除"""
    if name in EXCLUDE_NAMES:
        return True
    if any(name.endswith(suf) for suf in EXCLUDE_SUFFIXES):
        return True
    return False


def sync_once(dry_run: bool = False) -> tuple[int, int, list[str]]:
    """执行一次同步。返回 (copied, skipped, errors)"""
    if not SRC.exists():
        return (0, 0, [f"SRC 不存在: {SRC}"])
    DST.mkdir(parents=True, exist_ok=True)

    copied = 0
    skipped = 0
    errors: list[str] = []

    # 1. 遍历 SRC 每个文件 → 复制到 DST
    src_files: dict[Path, Path] = {}  # rel_path → abs_path
    for p in SRC.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(SRC)
        if should_exclude(p.name):
            skipped += 1
            continue
        # 二级 .git 目录里的 metadata 不复制
        if ".git" in rel.parts:
            skipped += 1
            continue
        src_files[rel] = p

    # 2. 复制
    for rel, src_p in src_files.items():
        dst_p = DST / rel
        try:
            if not dry_run:
                dst_p.parent.mkdir(parents=True, exist_ok=True)
                # 比 mtime 后才复制（增量）
                if dst_p.exists():
                    src_mtime = src_p.stat().st_mtime
                    dst_mtime = dst_p.stat().st_mtime
                    if dst_mtime >= src_mtime:
                        skipped += 1
                        continue
                shutil.copy2(src_p, dst_p)
            copied += 1
        except Exception as e:
            errors.append(f"{rel}: {e}")

    # 3. 删除 DST 中 SRC 已不存在的文件（mirror 行为）
    if DST.exists() and not dry_run:
        for dst_p in DST.rglob("*"):
            if not dst_p.is_file():
                continue
            rel = dst_p.relative_to(DST)
            if rel not in src_files and not should_exclude(dst_p.name):
                try:
                    dst_p.unlink()
                except Exception as e:
                    errors.append(f"delete {rel}: {e}")

    return (copied, skipped, errors)


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    start = time.time()
    copied, skipped, errors = sync_once(dry_run=dry_run)
    elapsed = (time.time() - start) * 1000

    if errors:
        print(f"❌ backup-web-access FAIL · copied={copied} skipped={skipped} errors={len(errors)} ms={elapsed:.0f}", flush=True)
        for e in errors[:5]:
            print(f"   - {e}", flush=True)
        return 1

    tag = "[DRY-RUN] " if dry_run else ""
    print(f"✅ {tag}backup-web-access PASS · copied={copied} skipped={skipped} ms={elapsed:.0f} src={SRC.name}→dst={DST.parent.parent.name}\\{DST.name}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())