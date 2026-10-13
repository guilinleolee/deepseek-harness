#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix-commands-frontmatter.py · 修复 commands/*.md 让 Continue 1.x 能识别

历史问题：
- data-quality-fixes.py --apply A 把 `license: UNKNOWN` 加到 109 个 .md frontmatter
- 当时只有 skills/*.md 才需要 license frontmatter，commands/*.md 不该有
- Continue 1.x 需要 `name` + `description` + `invokable: true` 三件套

处理三类文件：
  A. license_only (42)     frontmatter 只有 license    → 整段删除，从正文 H1 提取 description
  B. license_plus_desc (67) frontmatter 有 license+其它 → 去掉 license 行，保留其它
  C. desc_only (8)          frontmatter 只有 description → 保持，补 invokable + name

name 字段从文件名 stem 生成（如 `00调研师.md` → name=`00调研师`，`architect.md` → name=`architect`）
INDEX.md 跳过（它是索引文档，不当 slash command）

用法：
  python scripts/fix-commands-frontmatter.py              # dry-run
  python scripts/fix-commands-frontmatter.py --apply      # 真改
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 跳过的文件（索引/只读文档）
SKIP_NAMES = {"INDEX.md", "README.md"}

# frontmatter 区域正则
FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# license 单行
LICENSE_LINE_RE = re.compile(r"^license:\s*UNKNOWN\s*\n", re.MULTILINE)

# H1 标题正则（# 开头）
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str, str]:
    """解析 frontmatter，返回 (kv dict, frontmatter 原文, frontmatter 后的 body)

    frontmatter 不存在时返回 ({}, '', text)
    """
    m = FM_RE.match(text)
    if not m:
        return {}, "", text
    fm_text = m.group(1)
    body = text[m.end():]
    kv = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            kv[k.strip()] = v.strip()
    return kv, fm_text, body


def extract_description_from_body(body: str, max_len: int = 120) -> str:
    """从正文中提取 description 候选：
    1) H1 标题去掉前缀编号（`/01架构师` → `01架构师 (Architect)`）
    2) 第一段非空文本
    """
    # 先找 H1
    m = H1_RE.search(body)
    if m:
        title = m.group(1).strip()
        # 去掉开头的 `/`（一些文件用 `/00调研师` 风格）
        title = title.lstrip("/").strip()
        # 去掉尾部的 (Xxx)
        return title[:max_len]

    # fallback：第一段非空文字
    for para in body.split("\n\n"):
        para = para.strip()
        if para and not para.startswith("#"):
            # 截断
            return para[:max_len].replace("\n", " ")
    return ""


def build_frontmatter(kv: dict[str, str], name: str) -> str:
    """构造新的 frontmatter：
    - 保留 description / allowed-tools 等
    - 加 invokable: true
    - 加 name
    - 移除 license
    字段顺序：name → description → invokable → allowed-tools → 其它
    """
    # 删除 license
    if "license" in kv:
        kv.pop("license")

    # 强制设置 / 更新
    kv["name"] = name
    if "invokable" not in kv:
        kv["invokable"] = "true"

    # 字段顺序
    order = ["name", "description", "invokable", "allowed-tools"]
    ordered_kv = {}
    for k in order:
        if k in kv:
            ordered_kv[k] = kv[k]
    for k in kv:
        if k not in ordered_kv:
            ordered_kv[k] = kv[k]

    lines = ["---"]
    for k, v in ordered_kv.items():
        lines.append(f"{k}: {v}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def transform(path: Path, dry: bool = True) -> str:
    """处理单个文件，返回动作描述（DRY/FIX/SKIP）。dry=False 时写文件。"""
    name = path.stem

    if path.name in SKIP_NAMES:
        return "SKIP"

    raw = path.read_text(encoding="utf-8", errors="replace")
    kv, fm_text, body = parse_frontmatter(raw)

    has_license = "license" in kv
    has_desc = "description" in kv

    if not fm_text and not has_license and not has_desc:
        # 完全没 frontmatter（INDEX.md 之类） → SKIP（已经在 SKIP_NAMES 里处理）
        return "SKIP"

    if has_license and has_desc:
        # B. license_plus_desc：删除 license 行，保留其它
        new_kv = {k: v for k, v in kv.items() if k != "license"}
        # description 已在
        action = "FIX-B"
    elif has_license:
        # A. license_only：删除整个 frontmatter，从 body 提取 description
        new_kv = {}
        extracted = extract_description_from_body(body)
        if extracted:
            new_kv["description"] = extracted
        action = "FIX-A"
    elif has_desc:
        # C. desc_only：保留 description，补其它
        new_kv = {k: v for k, v in kv.items()}
        action = "FIX-C"
    else:
        return "SKIP"

    # 构造新 frontmatter
    new_fm = build_frontmatter(new_kv, name)
    new_text = new_fm + body.lstrip("\n")

    if not dry:
        path.write_text(new_text, encoding="utf-8")

    return action


def main() -> int:
    ap = argparse.ArgumentParser(description="fix Continue 1.x slash command frontmatter")
    ap.add_argument("--apply", action="store_true", help="actually modify files")
    ap.add_argument("root", nargs="?", default="commands")
    args = ap.parse_args()
    dry = not args.apply

    repo = Path(__file__).resolve().parent.parent
    root = repo / args.root
    if not root.is_dir():
        print(f"ERROR: {root} not a directory")
        return 1

    counts = {"FIX-A": 0, "FIX-B": 0, "FIX-C": 0, "SKIP": 0}
    for f in sorted(root.glob("*.md")):
        action = transform(f, dry=dry)
        counts[action] += 1
        marker = "[DRY]" if dry else "[FIX]"
        if action != "SKIP":
            print(f"  {marker} {action}  {f.relative_to(repo)}")

    print("")
    print(f"mode       = {'dry-run' if dry else 'apply'}")
    print(f"FIX-A (license_only)       = {counts['FIX-A']}")
    print(f"FIX-B (license+desc)       = {counts['FIX-B']}")
    print(f"FIX-C (desc_only)          = {counts['FIX-C']}")
    print(f"SKIP (no fm / INDEX.md)    = {counts['SKIP']}")
    print(f"total fixed (excl SKIP)    = {counts['FIX-A'] + counts['FIX-B'] + counts['FIX-C']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())