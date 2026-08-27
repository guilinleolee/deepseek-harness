#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
data-quality-fixes.py · 天龙引擎数据质量批量修复（dry-run 默认）
================================================================

为 skill-admin 5 类检查发现的"超阈值"项提供 dry-run 预览：
  - C: AGPL NOTICE 缺失      -> 生成 NOTICE 文件
  - B: triggers 缺失          -> 自动推断 + 填 frontmatter
  - A: license 未知          -> 批量 stamp license: UNKNOWN

⚠️ 默认 dry-run。加 `--apply <C|B|A>` 才写盘。
   加 `--apply all` 一键全部（建议分步走）。

调用：
    python scripts/data-quality-fixes.py --preview C    # 预览 2 条 NOTICE
    python scripts/data-quality-fixes.py --preview B    # 预览 830 条 triggers
    python scripts/data-quality-fixes.py --preview A    # 预览 1089 条 license stamp
    python scripts/data-quality-fixes.py --apply C      # 写 2 个 NOTICE
    python scripts/data-quality-fixes.py --apply A      # 改 1089 个 SKILL.md
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def run_skill_admin() -> dict:
    """Reuse skill-admin --json output."""
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "skill-admin.py"), "--json"],
        capture_output=True, text=True, timeout=120, cwd=str(REPO),
        encoding="utf-8", errors="replace",
    )
    return json.loads(out.stdout) if out.stdout else {}


# ------------------------------------------------------------------
# C: AGPL NOTICE generator
# ------------------------------------------------------------------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter dict, body). Naive: only top `---` block."""
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm_raw, body = m.group(1), m.group(2)
    fm: dict = {}
    cur_key = None
    for line in fm_raw.splitlines():
        if line.startswith("  ") and cur_key:
            fm[cur_key] = (fm.get(cur_key, "") + "\n" + line.strip()).strip()
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
            cur_key = k.strip()
    return fm, body


def generate_notice(skill_path: Path, fm: dict) -> str:
    """Compose AGPL-style NOTICE file content."""
    license_id = fm.get("license", "AGPL-3.0")
    upstream = fm.get("upstream", "unknown")
    name = fm.get("name", skill_path.parent.name)
    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        f"NOTICE for {name}",
        "=" * 60,
        "",
        f"This skill is distributed under the {license_id} license.",
        f"License text: see LICENSE in this directory.",
        "",
        f"Upstream: {upstream}",
        "",
        f"Modifications by Tianlong Engine (dragon-engine) on {today}:",
        "  - Mirrored into dragon-engine asset index.",
        "  - Re-indexed under schema dragon-index/1.0.",
        "  - Triggers/last_used/audit fields added (informational only).",
        "",
        "Per AGPL-3.0 Section 5(d): this NOTICE accompanies the source",
        "when conveyed. Source modifications, if any, are listed above.",
        "",
        "Compliance:",
        "  - AGPL-3.0 requires source availability when network service",
        "    is offered. This skill is delivered as method summary /",
        "    PNG output, NOT as a running network service.",
        "  - See BIBLE.md for AGPL compliance policy.",
        "",
    ]
    return "\n".join(lines)


def preview_C(findings: dict) -> list[tuple[Path, str]]:
    plans = []
    for f in findings.get("C_AGPL_missing_NOTICE", []):
        p = REPO / f["path"]
        if not p.exists():
            continue
        skill_dir = p.parent
        text = p.read_text(encoding="utf-8", errors="replace")
        fm, _ = parse_frontmatter(text)
        notice_path = skill_dir / "NOTICE"
        plans.append((notice_path, generate_notice(skill_dir, fm)))
    return plans


def apply_C(plans: list[tuple[Path, str]]) -> int:
    n = 0
    for path, content in plans:
        if path.exists():
            print(f"  [SKIP] {path.relative_to(REPO)} exists")
            continue
        path.write_text(content, encoding="utf-8")
        print(f"  [OK]   {path.relative_to(REPO)}  ({len(content)} bytes)")
        n += 1
    return n


# ------------------------------------------------------------------
# B: triggers inference
# ------------------------------------------------------------------

def infer_triggers(skill_path: Path, fm: dict) -> list[str]:
    """Best-effort trigger inference from directory name + first H1."""
    triggers = []
    # dir name kebab → words
    dir_name = skill_path.parent.name
    if dir_name and dir_name not in (".", "skills", "agents", "hooks", "commands", "plugins"):
        # strip leading numbers like "10-02-"
        words = re.sub(r"^\d{2}-\d{2}-?", "", dir_name)
        words = words.replace("-", " ").replace("_", " ").strip()
        if words:
            triggers.append(words)
    # first H1 from body
    text = skill_path.read_text(encoding="utf-8", errors="replace")
    _, body = parse_frontmatter(text)
    h1 = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if h1:
        title = h1.group(1).strip()
        # only short titles
        if len(title) <= 60 and title not in triggers:
            triggers.append(title)
    return triggers[:5] or ["<needs human review>"]


def preview_B(findings: dict) -> list[tuple[Path, dict, list[str]]]:
    plans = []
    for f in findings.get("B_triggers_missing", []):
        p = REPO / f["path"]
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        fm, body = parse_frontmatter(text)
        triggers = infer_triggers(p, fm)
        plans.append((p, fm, triggers))
    return plans


def apply_B(plans: list[tuple[Path, dict, list[str]]]) -> int:
    """Stamp triggers: [...] into SKILL.md frontmatter."""
    n = 0
    for path, fm, triggers in plans:
        text = path.read_text(encoding="utf-8", errors="replace")
        if "---" in text:
            # Insert triggers: [...] just before the closing ---
            fm_block, body = parse_frontmatter(text)
            fm_block["triggers"] = json.dumps(triggers, ensure_ascii=False)
            # rebuild
            new_fm = "\n".join(f"{k}: {v}" for k, v in fm_block.items())
            new_text = f"---\n{new_fm}\n---\n{body}"
            path.write_text(new_text, encoding="utf-8")
            print(f"  [OK]   {path.relative_to(REPO)}  triggers={triggers}")
            n += 1
    return n


# ------------------------------------------------------------------
# A: license stamp
# ------------------------------------------------------------------

def preview_A(findings: dict) -> list[tuple[Path, str]]:
    plans = []
    for f in findings.get("A_license_unknown", []):
        p = REPO / f["path"]
        if not p.exists():
            continue
        # Only file findings — skip directories accidentally listed
        if p.is_dir():
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        plans.append((p, text[:80].replace("\n", " ")))
    return plans


def apply_A(plans: list[tuple[Path, str]]) -> int:
    """Stamp license: UNKNOWN into SKILL.md frontmatter."""
    n = 0
    for path, _head in plans:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if text.startswith("---"):
            # add license line right after ---
            new_text = "---\nlicense: UNKNOWN\n" + text[4:].lstrip("\n")
        else:
            # no frontmatter at all — create one
            new_text = f"---\nlicense: UNKNOWN\n---\n\n{text}"
        path.write_text(new_text, encoding="utf-8")
        n += 1
    return n


# ------------------------------------------------------------------
# main
# ------------------------------------------------------------------

def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="天龙引擎数据质量批量修复")
    ap.add_argument("--preview", choices=["C", "B", "A"],
                    help="预览某个 section 的修改计划")
    ap.add_argument("--apply", choices=["C", "B", "A", "all"],
                    help="应用某个 section 的修改（覆盖 --preview）")
    args = ap.parse_args()

    if not args.preview and not args.apply:
        ap.print_help()
        return 0

    print("[INFO] running skill-admin.py --json ...", file=sys.stderr)
    admin = run_skill_admin()
    findings = admin.get("findings", {})

    if args.preview == "C" or args.apply == "C":
        plans = preview_C(findings)
        print(f"\n=== [C] AGPL NOTICE preview · {len(plans)} plans ===")
        for path, content in plans:
            print(f"\n--- {path.relative_to(REPO)} ---")
            print(content)
        if not args.apply:
            return 0
        print("\n[APPLY] writing NOTICE files ...")
        n = apply_C(plans)
        print(f"[DONE] {n} NOTICE files written.")
        if args.apply == "C":
            return 0

    if args.preview == "B" or args.apply == "B":
        plans = preview_B(findings)
        print(f"\n=== [B] triggers preview · {len(plans)} plans (showing 30) ===")
        for path, fm, triggers in plans[:30]:
            print(f"  {path.relative_to(REPO)}")
            print(f"    triggers: {triggers}")
        if len(plans) > 30:
            print(f"  ... and {len(plans) - 30} more")
        if not args.apply:
            return 0
        print("\n[APPLY] stamping triggers ...")
        n = apply_B(plans)
        print(f"[DONE] {n} SKILL.md files updated.")

    if args.preview == "A" or args.apply == "A" or args.apply == "all":
        plans = preview_A(findings)
        print(f"\n=== [A] license: UNKNOWN preview · {len(plans)} plans (showing 30) ===")
        for path, head in plans[:30]:
            print(f"  {path.relative_to(REPO)}")
            print(f"    head: {head!r}")
        if len(plans) > 30:
            print(f"  ... and {len(plans) - 30} more")
        if args.apply in ("A", "all"):
            print("\n[APPLY] stamping license: UNKNOWN ...")
            n = apply_A(plans)
            print(f"[DONE] {n} SKILL.md files stamped.")

    print("\n[NEXT] python scripts/build-index.py --include-library")
    print("       python scripts/skill-admin.py        # re-check counts")
    return 0


if __name__ == "__main__":
    sys.exit(main())