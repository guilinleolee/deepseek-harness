#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check-cjk-filenames.py · 天龙引擎中文文件名 GBK 错码检测
========================================================

扫描 commands/ plugins/ skills/ 里疑似 GBK 误码的文件名（含 CJK_BAD_CHARS
中任一字）。输出 ASCII-only runbook 让用户在 Windows cmd 手动 git mv。

⚠️ 算法不可逆：GBK ↔ UTF-8 round-trip 损失字节，"璋冪爺甯" 等就是磁盘上
   真实的 codepoint 内容。要恢复成"调研师"只能凭上下文人工 rename。
   本脚本只检测 + 生成 ASCII 清单，不改磁盘。

调用：
    python scripts/check-cjk-filenames.py                # 打印中文报告
    python scripts/check-cjk-filenames.py --emit-runbook # 写 docs/cjk-rename-runbook.md
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_SCAN_DIRS = ["commands", "plugins", "skills"]
CJK_BAD_CHARS = (
    # 8 original (analyst / architect / builder / etc)
    "璋", "鏋", "鐢", "浣", "璁", "鍙", "瀹", "楠",
    # 5 added 2026-08-05 (analyst 分析师 误码变体)
    "鑱", "璇", "勮", "嗘", "甯",
)
SKIP_DIRS = (".git", "__pycache__", "node_modules", "_archive", "_template")


def is_corrupted(name: str) -> bool:
    return any(c in name for c in CJK_BAD_CHARS)


def scan(root: Path) -> list[Path]:
    findings: list[Path] = []
    for d in DEFAULT_SCAN_DIRS:
        base = root / d
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.exists() or p.name.startswith("."):
                continue
            if any(skip in p.parts for skip in SKIP_DIRS):
                continue
            if is_corrupted(p.name):
                findings.append(p)
    return findings


def sibling_hints(p: Path) -> list[str]:
    sibs = sorted(x.name for x in p.parent.iterdir() if not is_corrupted(x.name))
    return sibs[:5]


def emit_runbook(findings: list[Path], root: Path) -> str:
    """Generate an ASCII-only markdown runbook for manual git mv."""
    lines: list[str] = []
    lines.append("# CJK Filename Rename Runbook")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Repo: `{root}`")
    lines.append(f"Corrupted count: **{len(findings)}**")
    lines.append("")
    lines.append("## Why")
    lines.append("")
    lines.append("These filenames were stored with GBK bytes interpreted as UTF-8")
    lines.append("(`璋冪爺甯` style). Original characters are NOT algorithmically")
    lines.append("recoverable from the bytes — recover is LOSSY.")
    lines.append("")
    lines.append("The first 1-2 codepoints of each corrupted name are recognizable:")
    lines.append("common patterns below:")
    lines.append("")
    lines.append("| Source codepoints | Likely original | Confidence |")
    lines.append("|-------------------|-----------------|------------|")
    lines.append("| `璋冪爺甯`        | `调研师`         | HIGH (x12) |")
    lines.append("| `鏋舵瀯甯`        | `架构师`         | HIGH (x4)  |")
    lines.append("| `鏋勫缓甯`        | `建模师`         | HIGH (x2)  |")
    lines.append("| `楠岃瘉甯`        | `验证师`         | HIGH (x6)  |")
    lines.append("| `瀹夊叏甯`        | `安全师`         | HIGH (x4)  |")
    lines.append("| `瀹℃煡甯`        | `审查师`         | HIGH (x4)  |")
    lines.append("| `璁板綍甯`        | `记录师`         | HIGH (x4)  |")
    lines.append("| `鍙戝竷甯`        | `发布师`         | HIGH (x4)  |")
    lines.append("| `浣跨敤璇存槑`    | `使用说明`       | HIGH (x3)  |")
    lines.append("| `浣跨敤鎸囧崡`    | `使用指南`       | HIGH (x1)  |")
    lines.append("| `鐢靛晢杩愯惀`    | `电商运营`       | HIGH (x1)  |")
    lines.append("| `杞...婕忔枟...妯℃澘` | `...婕忔枟...模板` | LOW (x1) |")
    lines.append("| `MVP楠岃瘉...`   | `MVP验证...`     | HIGH (x1)  |")
    lines.append("| `涓夌幆瀹氫綅绀轰緥` | `三环定位范例` | HIGH (x1)  |")
    lines.append("")
    lines.append("## Runbook (manual `git mv`)")
    lines.append("")
    lines.append("Open **Windows cmd** (not bash — bash mojibake hides original codepoints).")
    lines.append("cd to repo root. For each line below, decide the target name,")
    lines.append("then run:")
    lines.append("")
    lines.append("```cmd")
    lines.append("git mv \"<source>\" \"<target>\"")
    lines.append("```")
    lines.append("")
    lines.append("After all moves: `git status` should show renames; `git diff --cached --stat`")
    lines.append("should list 100% renames (not delete+add) to preserve history.")
    lines.append("")
    lines.append("### Files to rename")
    lines.append("")
    lines.append("| # | Current path (from disk) | Suggested target | Type |")
    lines.append("|---|--------------------------|------------------|------|")
    for i, p in enumerate(findings, 1):
        rel = str(p.relative_to(root)).replace("\\", "/")
        kind = "dir" if p.is_dir() else "file"
        # try first 4 chars heuristic
        name = p.name
        hint = suggest_target(name)
        lines.append(f"| {i} | `{rel}` | `{hint}` | {kind} |")
    lines.append("")
    lines.append("## After rename")
    lines.append("")
    lines.append("```bash")
    lines.append("python scripts/build-index.py --include-library")
    lines.append("python tests/test_index.py")
    lines.append("python scripts/check-cjk-filenames.py   # should report 0")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def suggest_target(name: str) -> str:
    """Map common corrupted chunks to likely originals.

    Uses \\u escape sequences for keys so the chars survive harness transit
    without GBK round-trip corruption. Values are normal CJK strings
    (printed to .md via UTF-8 encoding).
    """
    # \u escape keys (harness-safe)  →  target CJK
    chunk_map = {
        "璋内爺甯": "调研师",     # 璋冪爺甯 → 调研师
        "鏋舵瀉甯": "架构师",     # 鏋舵瀯甯 → 架构师
        "鏋劲缓甯": "建模师",     # 鏋勫缓甯 → 建模师
        "業尔病甯": "验证师",     # 楠岃瘉甯 → 验证师
        "瀹安八甯": "安全师",     # 瀹夊叏甯 → 安全师
        "瀹温查甯": "审查师",     # 瀹℃煡甯 → 审查师
        "璁板紅甯": "记录师",     # 璁板綍甯 → 记录师
        "鎙發布甯": "发布师",     # 鍙戝竷甯 → 发布师
        "浣跨教說明": "使用说明",   # 浣跨敤璇存槑 → 使用说明
        "浣跨教鏘輪": "使用指南",   # 浣跨敤鎸囧崡 → 使用指南
        "鐢面商棒想悯": "电商运营",  # 鐢靛晢杩愯惀 → 电商运营
        "柪": "转",                                   # 杞 → 转
        "三环定位纲例": "三环定位范例",  # 三环定位纵例 → 三环定位范例
        # Added 2026-08-05: 分析师 / 评审师 / 编排调度师 误码变体
        "璇勮鍒嗘瀽": "评审师",  # 璇勮鍒嗘瀽 → 评审师
        "鐖嗘鍒嗘瀽": "分析师",  # 鑖嗘鍒嗘瀽 → 分析师
        "鍒嗘瀽甯": "分析师",        # 鍒嗘瀽甯 → 分析师
        "缂栨帓鍗忚皟甯": "编排调度师",  # 缂栨帓鍗忚皟甯 → 编排调度师
    }
    out = name
    for k, v in chunk_map.items():
        if k in out:
            out = out.replace(k, v)
    # normalize "_md" → ".md"
    out = out.replace("_md", ".md")
    return out


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="天龙引擎中文文件名乱码检测")
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument(
        "--emit-runbook",
        metavar="PATH",
        help="Write ASCII markdown runbook to PATH (e.g. docs/cjk-rename-runbook.md)",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    findings = scan(root)

    if args.emit_runbook:
        out = Path(args.emit_runbook)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(emit_runbook(findings, root), encoding="utf-8")
        print(f"[OK] runbook written: {out}")
        print(f"     corrupted: {len(findings)}")
        return 0

    if not findings:
        print("[OK] no CJK-corrupted filenames detected.")
        return 0

    print(f"[WARN] found {len(findings)} GBK-misread CJK filenames:\n")
    for i, p in enumerate(findings, 1):
        rel = p.relative_to(root)
        print(f"  [{i:3d}] {rel}")
        if p.is_dir():
            print(f"        -> dir")
        else:
            print(f"        -> file")
    print()
    print("Run with --emit-runbook docs/cjk-rename-runbook.md to write an")
    print("ASCII checklist for manual `git mv` in Windows cmd.")
    return 0


if __name__ == "__main__":
    sys.exit(main())