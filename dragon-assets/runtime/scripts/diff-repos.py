"""diff-repos.py · 主仓 vs D 盘备份 · 全量对比脚本

主仓：C:\\Users\\li\\.claude\\projects\\c--Users-li--claude\\dragon-engine\\
备份：D:\\知识库\\天龙引擎\\dragon-engine-backup-20260722\

对比维度：
- 5 个顶层目录：agents/ skills/ memory/ scripts/ prompts/
- 文件大小 + mtime + 内容 hash
- 输出：3 列表（仅主仓 / 仅备份 / 双向都有但内容不同）
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path


MAIN_REPO = Path(r"C:\Users\li\.claude\projects\c--Users-li--claude\dragon-engine")
BACKUP = Path(r"D:\知识库\天龙引擎\dragon-engine-backup-20260722")

# 排除：node_modules / .git / __pycache__ / .pytest_cache
EXCLUDE_PATTERNS = ("node_modules", ".git", "__pycache__", ".pytest_cache")

# 限制对比顶层目录（避免太慢）
COMPARE_DIRS = ["agents", "skills", "memory", "scripts", "prompts"]


def hash_file(p: Path) -> str:
    h = hashlib.sha256()
    try:
        h.update(p.read_bytes())
    except Exception:
        return "ERR"
    return h.hexdigest()[:16]


def should_skip(p: Path) -> bool:
    parts = p.parts
    return any(pat in parts for pat in EXCLUDE_PATTERNS)


def walk_files(root: Path, max_depth: int = 6) -> dict[str, tuple[int, str, float]]:
    """返回 rel_path → (size, sha256, mtime)"""
    files = {}
    if not root.exists():
        return files
    for dirpath, dirnames, filenames in os.walk(root):
        # 深度控制
        rel = os.path.relpath(dirpath, root)
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        if depth > max_depth:
            dirnames.clear()
            continue
        # 排除
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_PATTERNS]
        for fname in filenames:
            if fname in EXCLUDE_PATTERNS:
                continue
            full = Path(dirpath) / fname
            rel_path = (Path(rel) / fname).as_posix() if rel != "." else fname
            try:
                stat = full.stat()
                if should_skip(full):
                    continue
                files[rel_path] = (stat.st_size, hash_file(full), stat.st_mtime)
            except Exception:
                pass
    return files


def diff_repos(main: Path, backup: Path, compare_dirs: list[str]) -> tuple[list, list, list]:
    only_main = []
    only_backup = []
    different = []

    for subdir in compare_dirs:
        m_root = main / subdir
        b_root = backup / subdir
        if not m_root.exists() and not b_root.exists():
            continue

        m_files = walk_files(m_root) if m_root.exists() else {}
        b_files = walk_files(b_root) if b_root.exists() else {}

        m_keys = set(m_files.keys())
        b_keys = set(b_files.keys())

        for k in sorted(m_keys - b_keys):
            sz, h, mt = m_files[k]
            only_main.append((f"{subdir}/{k}", sz, mt))
        for k in sorted(b_keys - m_keys):
            sz, h, mt = b_files[k]
            only_backup.append((f"{subdir}/{k}", sz, mt))
        for k in sorted(m_keys & b_keys):
            m_sz, m_h, m_mt = m_files[k]
            b_sz, b_h, b_mt = b_files[k]
            if m_h != b_h:
                different.append((f"{subdir}/{k}", m_sz, b_sz, m_h, b_h))

    return only_main, only_backup, different


def main():
    print("=" * 60)
    print(f"主仓: {MAIN_REPO}")
    print(f"备份: {BACKUP}")
    print(f"对比顶层目录: {COMPARE_DIRS}")
    print("=" * 60)

    if not MAIN_REPO.exists():
        print(f"[ERROR] 主仓不存在: {MAIN_REPO}")
        return 1
    if not BACKUP.exists():
        print(f"[ERROR] 备份不存在: {BACKUP}")
        return 1

    only_main, only_backup, different = diff_repos(MAIN_REPO, BACKUP, COMPARE_DIRS)

    print(f"\n[仅主仓有] {len(only_main)} 个文件")
    for path, sz, mt in only_main[:30]:
        print(f"  + {path:60s} {sz:>9,} B")
    if len(only_main) > 30:
        print(f"  ... ({len(only_main) - 30} more)")

    print(f"\n[仅备份有] {len(only_backup)} 个文件")
    for path, sz, mt in only_backup[:30]:
        print(f"  - {path:60s} {sz:>9,} B")
    if len(only_backup) > 30:
        print(f"  ... ({len(only_backup) - 30} more)")

    print(f"\n[内容不同] {len(different)} 个文件")
    for path, m_sz, b_sz, m_h, b_h in different[:20]:
        print(f"  ≠ {path:60s} {m_sz:>9,} B → {b_sz:>9,} B ({m_h[:6]} vs {b_h[:6]})")
    if len(different) > 20:
        print(f"  ... ({len(different) - 20} more)")

    print()
    print("=" * 60)
    print(f"汇总: 仅主仓 {len(only_main)} + 仅备份 {len(only_backup)} + 内容不同 {len(different)}")
    print("=" * 60)

    # 建议
    print()
    if only_main and not only_backup:
        print("✅ 主仓 ≥ 备份（新增文件是阶段 26.1 的合理产物）")
    elif only_backup:
        print(f"⚠️ 备份有 {len(only_backup)} 个文件主仓缺 → 评估是否需要补 sync")
    if different:
        print(f"ℹ️ 内容不同 {len(different)} 个 → 主仓修改后未反向 sync")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())