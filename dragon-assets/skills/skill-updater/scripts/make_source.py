#!/usr/bin/env python3
"""
make_source.py — 交互式给缺 source 的 SKILL.md 补 source / license 字段。
默认 dry-run,只显示建议,不改文件;加 --apply 才真改。

Usage:
    # 默认 dry-run,逐个资产询问
    python scripts/make_source.py

    # 限制根目录
    python scripts/make_source.py --root "c:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine"

    # 自动猜测(基于 name 关键词)
    python scripts/make_source.py --auto

    # 真改文件(谨慎!)
    python scripts/make_source.py --apply

    # 只补某个 skill
    python scripts/make_source.py --only guizang --apply
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# 基于 name 关键词的自动猜测表(name 关键字 -> GitHub URL + license)
AUTO_HINTS: dict[str, tuple[str, str, str]] = {
    # name 关键字小写              (url,                                                  license,  note)
    "guizang":            ("https://github.com/op7418/guizang-social-card-skill",
                           "AGPL-3.0", "5.1k ⭐ · 借调 28 版式"),
    "voxcpm":             ("https://github.com/OpenBMB/VoxCPM",
                           "Apache-2.0", "31.7k ⭐ · 借调 VoxCPM2 推理"),
    "generative-media":   ("https://github.com/SamurAIGPT/Generative-Media-Skills",
                           "MIT", "78 SKILL · 借调 agent-native 范式"),
    "gpt-image":          ("https://github.com/freestylefly/awesome-gpt-image-2",
                           "MIT", "7.7k ⭐ · 借调 reasoning brief 范式"),
    "nano-banana-brief":  ("https://github.com/freestylefly/awesome-gpt-image-2",
                           "MIT", "7.7k ⭐ · 借调 reasoning brief 范式"),
    "huashu":             ("https://github.com/alchaincyf/huashu-design",
                           "MIT", "21.5k ⭐ · 借调 cinematic-patterns"),
    "cinema-director":    ("https://github.com/alchaincyf/huashu-design",
                           "MIT", "21.5k ⭐ · 借调 cinematic-patterns"),
    "async-task-pattern": ("https://github.com/SamurAIGPT/Generative-Media-Skills",
                           "MIT", "反向抽取 agent-native 范式"),
}


def auto_hint(name: str) -> tuple[str, str, str] | None:
    """基于 skill name 推断 source URL + license + note。"""
    n = name.lower()
    for key, (url, lic, note) in AUTO_HINTS.items():
        if key in n:
            return (url, lic, note)
    return None


def parse_frontmatter(text: str) -> dict[str, Any]:
    """跟 parse_skill.py 同款。"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}
    fm = m.group(1)
    result: dict[str, Any] = {}
    current_list_key: str | None = None
    for line in fm.split("\n"):
        if not line.strip():
            continue
        list_match = re.match(r"^\s+-\s+(.*)$", line)
        if list_match and current_list_key:
            result.setdefault(current_list_key, []).append(list_match.group(1).strip())
            continue
        kv_match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)$", line)
        if kv_match:
            key = kv_match.group(1).strip()
            value = kv_match.group(2).strip()
            current_list_key = None
            if value == "":
                current_list_key = key
                result.setdefault(key, [])
            else:
                result[key] = value.strip('"').strip("'")
    return result


def detect_source_type(skill: dict[str, Any]) -> str:
    return skill.get("source", {}).get("type", "missing")


def is_tianlong_native(description: str | None) -> bool:
    if not description:
        return False
    return any(kw in description for kw in ["天龙自研", "天龙引擎", "天龍"])


def inject_fields(skill_md_path: Path, source_line: str, license_line: str) -> bool:
    """在 frontmatter 末尾插入 source + license。返回 True 表示真改了文件。"""
    text = skill_md_path.read_text(encoding="utf-8")
    m = re.match(r"^(---\s*\n)(.*?)(\n---\s*\n)", text, re.DOTALL)
    if not m:
        return False
    fm_body = m.group(2)
    # 跳过已存在的 source / license 行
    new_lines = []
    for line in fm_body.split("\n"):
        if re.match(r"^\s*source\s*:", line) or re.match(r"^\s*license\s*:", line):
            continue
        new_lines.append(line)
    new_fm = "\n".join(new_lines).rstrip("\n") + f"\n{source_line}\n{license_line}\n"
    new_text = text[:m.start()] + m.group(1) + new_fm + m.group(3) + text[m.end():]
    skill_md_path.write_text(new_text, encoding="utf-8")
    return True


def interactive_ask(skill: dict[str, Any]) -> tuple[str, str] | None:
    """交互式询问用户,返回 (source_line, license_line);None = 跳过。"""
    name = skill["name"]
    hint = auto_hint(name)
    path = skill["path"]

    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📦 {name}")
    print(f"   path: {path}")
    if hint:
        url, lic, note = hint
        print(f"   自动猜测: url={url}, license={lic}")
        print(f"   说明: {note}")
    print()
    print("选项:")
    print("  1) 天龙自研 (跳过,在 description 里建议加 '天龙自研')")
    print("  2) 外部借调 - 使用自动猜测 (如果有)")
    if not hint:
        print("  3) 外部借调 - 手动填 URL")
        print("  s) 跳过本次")

    choice = input(f"\n选 [1/2/3/s, 默认 2]: ").strip() or "2"
    if choice == "1":
        print("  → 跳过(标记为天龙自研)")
        return None
    if choice == "s":
        print("  → 跳过")
        return None
    if choice == "2":
        if not hint:
            print("  没有自动猜测,改用手动输入")
            choice = "3"
        else:
            url, lic, note = hint
            source_line = f"source: {url} ({note})"
            license_line = f"license: {lic}"
            print(f"  → 将写入:\n     {source_line}\n     {license_line}")
            return (source_line, license_line)
    if choice == "3":
        url = input("  GitHub URL (e.g. https://github.com/owner/repo): ").strip()
        if not url:
            return None
        lic = input("  SPDX License (e.g. MIT, Apache-2.0, AGPL-3.0) [默认 MIT]: ").strip() or "MIT"
        note = input("  说明 (可选, e.g. 5k ⭐ · 借调 X): ").strip()
        source_line = f"source: {url}" + (f" ({note})" if note else "")
        license_line = f"license: {lic}"
        return (source_line, license_line)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="天龙 SKILL.md source 字段补全")
    parser.add_argument("--root", default=os.path.expanduser("~/.claude"),
                        help="扫描根目录")
    parser.add_argument("--only", help="只处理名字含此子串的 skill")
    parser.add_argument("--apply", action="store_true",
                        help="真改文件(默认 dry-run,只显示)")
    parser.add_argument("--auto", action="store_true",
                        help="自动用猜测表填,不询问")
    args = parser.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import parse_skill  # type: ignore
    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        sys.exit(f"ERROR: root not found: {root}")

    skills_data = parse_skill.scan_skill_md(root)
    # 过滤:只有 missing source 且非天龙自研
    targets = [
        s for s in skills_data
        if detect_source_type(s) in ("missing", "unparseable")
        and not is_tianlong_native(s.get("description"))
        and (not args.only or args.only.lower() in s["name"].lower())
    ]

    print(f"找到 {len(targets)} 个缺 source 的 SKILL.md(天龙自研已过滤)")
    if not targets:
        print("✅ 无需补 source")
        return 0

    if args.apply:
        print("⚠️  --apply 模式:真改文件!")
    else:
        print("ℹ️  默认 dry-run,只显示建议;加 --apply 才真改文件\n")

    applied = 0
    skipped = 0
    for s in targets:
        if args.auto:
            hint = auto_hint(s["name"])
            if hint:
                url, lic, note = hint
                source_line = f"source: {url} ({note})"
                license_line = f"license: {lic}"
            else:
                print(f"⏭️  {s['name']:<30} | 没自动猜测,跳过")
                skipped += 1
                continue
        else:
            result = interactive_ask(s)
            if result is None:
                skipped += 1
                continue
            source_line, license_line = result

        if args.apply:
            ok = inject_fields(Path(s["path"]), source_line, license_line)
            if ok:
                print(f"✅ 已写入: {s['name']}")
                applied += 1
            else:
                print(f"❌ 写入失败: {s['name']}")
        else:
            print(f"📝 计划写入 {s['name']}:")
            print(f"     {source_line}")
            print(f"     {license_line}")
            applied += 1
        print()

    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"完成: {applied} 处理, {skipped} 跳过")
    if not args.apply and applied > 0:
        print(f"💡 加 --apply 才会真改文件")
    return 0


if __name__ == "__main__":
    sys.exit(main())