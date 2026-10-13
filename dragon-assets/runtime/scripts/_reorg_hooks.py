#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_reorg_hooks.py · 天龙引擎 hooks/ 按 trigger 分目录重构
========================================================

按 hook 触发模型把 80+ 文件分类到子目录。同步：
  · 建目录: postToolUse preToolUse userPromptSubmit session-start session-end on-demand utility docs tests
  · git mv 全部目标文件（保留历史）
  · PUA 误码文件 hooks浣跨敤鎸囧崡.md -> docs/hooks使用指南.md
  · __tests__/ -> tests/
  · 更新 hooks.json 内 6 处 ./xxx.js -> ./<trigger>/xxx.js
  · 改 require() 跨目录引用
  · 生成新 hooks/README.md

bridge/ gitnexus/ 保持原状（已是子目录）。hooks.json 保留在 hooks/ 根。

⚠️ 默认 dry-run。加 --apply 真的执行 git mv + 改 hooks.json + 改 require。
   加 --skip-require 仅跳过 require() 改写（已移动后人工处理）。

调用：
    python scripts/_reorg_hooks.py                # dry-run
    python scripts/_reorg_hooks.py --apply        # 真改
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path("C:/Users/li/.claude/projects/dragon-engine")
HOOKS = REPO / "hooks"

# ============================================================
# 每个文件的"目标子目录"映射
# ============================================================
# 键: 文件名（不含路径）  值: 目标子目录名
PLAN: dict[str, str] = {
    # ---------- postToolUse (6) ----------
    "nine-dragons-log-watcher.js":          "postToolUse",
    "nine-dragons-task-manager-hook.js":    "postToolUse",
    "lessons-logger.js":                    "postToolUse",
    "token-hook.js":                        "postToolUse",
    "token-optimizer.js":                   "postToolUse",
    "skill-usage-tracker.js":               "postToolUse",
    # ---------- preToolUse (13) ----------
    "decision-gate-trigger.js":             "preToolUse",
    "critical-thinking-agent-checker.js":   "preToolUse",
    "critical-thinking-collaboration.js":   "preToolUse",
    "critical-thinking-memory-layer.js":    "preToolUse",
    "gsd-deviation-handler.js":             "preToolUse",
    "hash-anchored-edit.js":                "preToolUse",
    "static-analyzer.js":                   "preToolUse",
    "meta-review-trigger.js":               "preToolUse",
    "check-comments.js":                    "preToolUse",
    "check-comments.py":                    "preToolUse",
    "cbm-code-discovery-gate":              "preToolUse",
    "staff-review-trigger.js":              "preToolUse",
    "thought-diversity-checker.js":         "preToolUse",
    # ---------- userPromptSubmit (7) ----------
    "dragon-shortcut-syntax-hook.js":       "userPromptSubmit",
    "claudeception-activator.sh":           "userPromptSubmit",
    "user-prompt-submit.js":                "userPromptSubmit",
    "user-prompt-submit.sh":                "userPromptSubmit",
    "prompt-submit.js":                     "userPromptSubmit",
    "todo-enforcer.sh":                     "userPromptSubmit",
    "keyword-detector.py":                  "userPromptSubmit",
    # ---------- session-start (3) ----------
    "session-start.js":                     "session-start",
    "claude-code-cli-monitor.js":           "session-start",
    "pre-commit.sh":                        "session-start",
    # ---------- session-end (5) ----------
    "shared-memory-session-end.js":         "session-end",
    "session-stop.js":                      "session-end",
    "session-hook.js":                      "session-end",
    "session-token-cli.js":                 "session-end",
    "shared-memory-commands.js":            "session-end",
    # ---------- on-demand (8) ----------
    "on-demand-handler.js":                 "on-demand",
    "openclaw-zero-polling-hook.js":        "on-demand",
    "openclaw-zero-polling-hook.ps1":       "on-demand",
    "openclaw-dragon-engine-adapter.js":    "on-demand",
    "limei-openclaw-adapter.js":            "on-demand",
    "LIMEI-OPENCLAW-INTEGRATION.md":        "on-demand",
    "OPENCLAW-INTEGRATION-SUMMARY.md":      "on-demand",
    "OPENCLAW-ZERO-POLLING-README.md":      "on-demand",
    # ---------- utility (38) ----------
    "agent-runner.js":                      "utility",
    "agent-booster.js":                     "utility",
    "dragon-commander.js":                  "utility",
    "dragon-commander.config.json":         "utility",
    "dragon-commander-v8-wrapper.js":       "utility",
    "dragon-commander-abtest.js":           "utility",
    "dragon-commander-multimodal.js":       "utility",
    "dragon-commander-api-bridge.js":       "utility",
    "dragon-commander-hook-wrapper.js":     "utility",
    "dragon-commander-test.js":             "utility",
    "dragon-commander-v2-test.js":          "utility",
    "dragon-protocol.js":                   "utility",
    "dragon-communication-manager.js":      "utility",
    "dragon-communication-test.js":         "utility",
    "nine-dragons-enhancer-v5.js":          "utility",
    "nine-dragons-task-manager.js":         "utility",
    "nine-dragons-completion-enforcer.js":  "utility",
    "template-manager.js":                  "utility",
    "template-cli.js":                      "utility",
    "task-template-system.js":              "utility",
    "task-queue-visualizer.js":             "utility",
    "recommend-engine.js":                  "utility",
    "dashboard-cli.js":                     "utility",
    "interaction-cli.js":                   "utility",
    "interaction-mode.js":                  "utility",
    "model-switcher.js":                    "utility",
    "mcp-config-manager.js":                "utility",
    "memory-layer-v8.js":                   "utility",
    "memory-layer-v9.js":                   "utility",
    "v74-performance-monitor.js":           "utility",
    "plan-health-checker.js":               "utility",
    "github-issues-adapter.js":             "utility",
    "code-rules.json":                      "utility",
    "dragon-shortcut-syntax.md":            "utility",
    # ---------- docs (4) ----------
    "HOOKS-ANALYSIS.md":                    "docs",
    "IMPLEMENTATION-COMPLETE.md":           "docs",
    "P2-COMPLETE.md":                       "docs",
    "README.md":                            "docs",          # 原 hooks/README.md
    # PUA 误码 rename + 移动到 docs
    "hooks浣跨敤鎸囧崡.md":                  "docs",
    # ---------- tests (3) ----------
    "test-hooks.sh":                        "tests",
    "test-p2.sh":                           "tests",
    "test-p2-fixed.sh":                     "tests",
    "test-openclaw-integration.js":         "tests",
}

PUA_RENAME = {
    "hooks浣跨敤鎸囧崡.md": "hooks使用指南.md",
}

# __tests__/ 整体移入 tests/ 目录（去掉 __tests__/ 这层）
TEST_DIR_MOVE = True  # __tests__/*.test.js -> tests/*.test.js

# 保留在 hooks/ 根的文件（不移动）
ROOT_KEEP = {
    "hooks.json",
}

# 不在 PLAN 但也不在 ROOT_KEEP 的文件 → 报警（漏网）
EXTRA_CHECK = True

# ============================================================
# require() 跨目录引用改写规则
# ============================================================
# 格式: (移动到的目录, require 里的文件名片段, 新 require 路径片段)
REQUIRE_REWRITES: list[tuple[str, str, str]] = [
    # utility/dashboard-cli.js 引用 session-end/session-token-cli
    ("utility",  "./session-token-cli.js", "../session-end/session-token-cli.js"),
    # utility/nine-dragons-task-manager.js 引用 bridge/bridge-runner
    ("utility",  "./bridge/bridge-runner.js", "../bridge/bridge-runner.js"),
    # postToolUse/nine-dragons-task-manager-hook.js 引用 utility/nine-dragons-task-manager
    ("postToolUse", "./nine-dragons-task-manager", "../utility/nine-dragons-task-manager"),
    # tests/*.test.js 引用 hooks/utility/*
    ("tests", "../nine-dragons-task-manager", "../utility/nine-dragons-task-manager"),
    ("tests", "../github-issues-adapter",      "../utility/github-issues-adapter"),
]

# ============================================================
# hooks.json 路径映射
# ============================================================
HOOKS_JSON_REWRITES = {
    "./nine-dragons-log-watcher.js":       "./postToolUse/nine-dragons-log-watcher.js",  # 既是 postToolUse 又是 preToolUse
    "./nine-dragons-task-manager-hook.js": "./postToolUse/nine-dragons-task-manager-hook.js",
    "./lessons-logger.js":                 "./postToolUse/lessons-logger.js",
    "./dragon-shortcut-syntax-hook.js":    "./userPromptSubmit/dragon-shortcut-syntax-hook.js",
    "./shared-memory-session-end.js":      "./session-end/shared-memory-session-end.js",
}


def git_mv(src: Path, dst: Path) -> bool:
    """Run git mv src dst. Returns True on success."""
    rel_src = str(src.relative_to(REPO)).replace("/", "\\")
    rel_dst = str(dst.relative_to(REPO)).replace("/", "\\")
    r = subprocess.run(
        ["git", "mv", rel_src, rel_dst],
        cwd=str(REPO),
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        print(f"  [ERR] git mv {rel_src} -> {rel_dst}: {r.stderr.strip()}")
        return False
    return True


def move_test_dir() -> bool:
    """Move __tests__/* -> tests/* (drop __tests__/ layer)."""
    src = HOOKS / "__tests__"
    dst = HOOKS / "tests"
    if not src.exists():
        return True
    dst.mkdir(exist_ok=True)
    for f in src.iterdir():
        if f.is_file():
            if not git_mv(f, dst / f.name):
                return False
    # remove empty __tests__ dir (git rmdir empty)
    try:
        src.rmdir()
    except OSError:
        pass
    return True


def apply_plan(dry: bool) -> tuple[int, int, list[str]]:
    """Move all PLAN entries to their subdirs via git mv.

    Returns (moved_count, skip_count, errors).
    """
    moved = skip = 0
    errors: list[str] = []

    for fname, subdir in PLAN.items():
        src = HOOKS / fname
        dst = HOOKS / subdir / (PUA_RENAME.get(fname, fname))
        if not src.exists():
            print(f"  [SKIP] not on disk: {fname}")
            skip += 1
            continue
        if dst.exists():
            print(f"  [SKIP] dst exists: {dst.relative_to(HOOKS)}")
            skip += 1
            continue
        if dry:
            print(f"  [DRY ] {src.relative_to(HOOKS)} -> {dst.relative_to(HOOKS)}")
            moved += 1
            continue
        # create target subdir if needed
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not git_mv(src, dst):
            errors.append(fname)
            continue
        moved += 1

    return moved, skip, errors


def rewrite_hooks_json(dry: bool) -> int:
    """Update hooks.json so the 6 registered paths point to new subdirs."""
    p = HOOKS / "hooks.json"
    if not p.exists():
        return 0
    txt = p.read_text(encoding="utf-8")
    n = 0
    new_txt = txt
    for old, new in HOOKS_JSON_REWRITES.items():
        if old in new_txt:
            new_txt = new_txt.replace(old, new)
            n += 1
    if n == 0 or dry:
        if n:
            print(f"  [{'DRY' if dry else 'OK '}] hooks.json: {n} path rewrite(s)")
        else:
            print(f"  [WARN] no hooks.json rewrite matched")
        return n
    p.write_text(new_txt, encoding="utf-8")
    print(f"  [OK ] hooks.json: {n} path(s) rewritten")
    return n


def rewrite_requires(dry: bool) -> tuple[int, list[str]]:
    """Update require() paths in JS files based on REQUIRE_REWRITES."""
    fixed_files: set[Path] = set()
    details: list[str] = []

    # Build per-file rewrite map by walking subdirs
    for subdir, old, new in REQUIRE_REWRITES:
        base = HOOKS / subdir
        if not base.exists():
            continue
        # iterate files matching extensions
        for ext in ("*.js", "*.cjs", "*.mjs"):
            for f in base.rglob(ext):
                txt = f.read_text(encoding="utf-8", errors="replace")
                if old not in txt:
                    continue
                new_txt = txt.replace(old, new)
                if not dry:
                    f.write_text(new_txt, encoding="utf-8")
                fixed_files.add(f)
                details.append(f"  [{'DRY' if dry else 'OK '}] {f.relative_to(HOOKS)}: {old} -> {new}")

    for line in details:
        print(line)
    return len(fixed_files), details


def check_extras() -> list[str]:
    """Find any hook file not in PLAN and not in ROOT_KEEP (subdirs OK)."""
    leftovers: list[str] = []
    if not EXTRA_CHECK:
        return leftovers
    plan_set = set(PLAN.keys())
    keep_set = ROOT_KEEP
    for f in HOOKS.iterdir():
        if not f.is_file():
            continue  # subdirs OK (bridge/ gitnexus/ etc.)
        if f.name in plan_set:
            continue
        if f.name in keep_set:
            continue
        leftovers.append(f.name)
    return leftovers


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="天龙引擎 hooks/ 按 trigger 重构")
    ap.add_argument("--apply", action="store_true", help="真改（默认 dry-run）")
    ap.add_argument("--skip-require", action="store_true", help="跳过 require 改写")
    args = ap.parse_args()
    dry = not args.apply

    print(f"[{'DRY-RUN' if dry else 'APPLY'}] hooks/ reorg into subdirs")
    print(f"  PLAN entries: {len(PLAN)}")
    print(f"  ROOT_KEEP:    {sorted(ROOT_KEEP)}")
    print()

    # Step 1: leftover check (before moves)
    print("--- precheck: leftovers not in PLAN ---")
    leftovers = check_extras()
    if leftovers:
        for n in leftovers:
            print(f"  [LEFTOVER] {n}")
    else:
        print("  [OK ] no leftovers")
    print()

    # Step 2: mkdir + git mv
    print("--- step 1: mkdir + git mv ---")
    # Pre-create all target subdirs (git ignores empty dirs, safe in dry-run too)
    for sub in sorted(set(PLAN.values())):
        (HOOKS / sub).mkdir(exist_ok=True)
    if TEST_DIR_MOVE:
        (HOOKS / "tests").mkdir(exist_ok=True)
    moved, skip, errors = apply_plan(dry)
    if TEST_DIR_MOVE:
        if dry:
            print(f"  [DRY ] __tests__/*.test.js -> tests/*.test.js")
        else:
            ok = move_test_dir()
            print(f"  [{'OK ' if ok else 'ERR'}] __tests__/ -> tests/")
    print(f"  -> moved={moved}  skip={skip}  err={len(errors)}")
    print()

    # Step 3: hooks.json paths
    if errors and not dry:
        print("[ABORT] git mv errors detected, skipping hooks.json + require rewrite.")
        print("        Fix manually then re-run.")
        return 1

    print("--- step 2: hooks.json path rewrite ---")
    n_json = rewrite_hooks_json(dry)
    print()

    # Step 4: require() paths
    if not args.skip_require:
        print("--- step 3: require() cross-dir rewrite ---")
        if dry:
            print("  [INFO] dry-run 不修改脚本内容；--apply 阶段真改 require()")
            n_req = 0
        else:
            n_req, _ = rewrite_requires(dry)
            print(f"  -> files patched: {n_req}")
    else:
        print("--- step 3: require() rewrite SKIPPED ---")
    print()

    print(f"[DONE] moved={moved}  json_rewrites={n_json}  skip={skip}  err={len(errors)}")
    if dry:
        print("       re-run with --apply to commit changes.")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())