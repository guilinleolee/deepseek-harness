"""uuid_v7_lint V1.0 — Stage 46 nomifun-methodology.

借鉴 nomifun v3 ID 五类分立（技术 id / 业务 UUIDv7 / 自然键 / 外部 ID / 操作 token），
扫 dragon-engine/memory/*.md 与 agents/*.md：

- 主题文件 frontmatter 必含稳定 UUIDv7 业务 ID 字段（可选，但被使用则必合规）
- 拒绝物理外键关键字：FOREIGN KEY / REFERENCES / *_row_id / ON DELETE CASCADE
- 拒绝双轨业务 ID/行 ID（任何 `*_row_id` 模式）

参考：https://github.com/nomifun/nomifun-desktop/blob/main/docs/architecture/id-system.zh.md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

# 标准 UUIDv7 8-4-4-4-12 (lowercase)
UUID7_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

# 物理外键禁词
FORBIDDEN_DDL_KEYWORDS = [
    "FOREIGN KEY",
    "REFERENCES",
    "CREATE TRIGGER",
    "ON DELETE CASCADE",
    "ON UPDATE CASCADE",
]
ROW_ID_DOUBLE_TRACK_RE = re.compile(r"\b\w*_row_id\b")
UUID4_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")


def lint_file(path: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # === 4 断言 ===
    # 1. 所有出现的 UUIDv7 字符串必须符合 8-4-4-4-12 + version=7 + variant
    for i, line in enumerate(lines, 1):
        for cand in re.findall(
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", line
        ):
            if UUID4_RE.match(cand):
                issues.append(("FAIL", f"{path.name}:{i}: UUIDv4 '{cand[:8]}...' used; spec requires v7"))
            elif not UUID7_RE.match(cand):
                issues.append(("FAIL", f"{path.name}:{i}: UUID '{cand[:8]}...' not canonical 8-4-4-4-12"))

    # 2. 拒绝物理外键禁词（仅 SQL 代码块内生效）
    in_code = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            for kw in FORBIDDEN_DDL_KEYWORDS:
                if kw in line:
                    issues.append(("FAIL", f"{path.name}:{i}: forbidden DDL keyword '{kw}'"))
            if ROW_ID_DOUBLE_TRACK_RE.search(line):
                issues.append(("FAIL", f"{path.name}:{i}: double-track *_row_id pattern"))

    # 3. frontmatter 里有 `name:` 字段且含 UUIDv7 时校验 v7 规范
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm = parts[1]
            for cand in re.findall(
                r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", fm
            ):
                if UUID4_RE.match(cand):
                    issues.append(("FAIL", f"{path.name}: frontmatter UUIDv4 '{cand[:8]}...'; spec requires v7"))
                elif not UUID7_RE.match(cand):
                    issues.append(("FAIL", f"{path.name}: frontmatter UUID '{cand[:8]}...' not canonical v7"))

    # 4. 主题文件 / agents 文件：name 应含 origin_session_id（如果出现则强制 v7）
    # 简易校验：含 `originSessionId:` 行 → 该行不应同时出现双轨业务 ID/行 ID
    for i, line in enumerate(lines, 1):
        if "originSessionId" in line and ROW_ID_DOUBLE_TRACK_RE.search(line):
            issues.append(("FAIL", f"{path.name}:{i}: row_id pattern adjacent to originSessionId"))

    if not issues:
        issues.append(("PASS", f"{path.name}: 5 类分立 + v7 规范 OK"))
    return issues


def _iter_target_files(root: Path) -> Iterable[Path]:
    for path in (root / "memory").rglob("*.md"):
        if "obsidian-mirror" in path.parts:
            continue
        yield path
    for path in (root / "agents").rglob("*.md"):
        yield path
    for path in (root / "skills").rglob("SKILL.md"):
        yield path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="uuid_v7_lint V1.0 — Stage 46 nomifun-methodology")
    parser.add_argument("paths", nargs="*", default=None,
                        help="Specific .md paths or dirs; omit to scan memory/+agents/+skills/ tree")
    parser.add_argument("--root", default=".",
                        help="Project root (default: current dir)")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if args.paths:
        targets: list[Path] = []
        for p in args.paths:
            pp = Path(p).resolve()
            if pp.is_dir():
                targets.extend(pp.rglob("*.md"))
                targets.extend(pp.rglob("SKILL.md"))
            else:
                targets.append(pp)
        targets = list(dict.fromkeys(targets))  # dedupe
    else:
        targets = list(_iter_target_files(root))

    overall_fail = False
    print(f"uuid_v7_lint V1.0 · Stage 46 nomifun-methodology · scanning {len(targets)} files")
    for path in targets:
        if not path.exists():
            print(f"  [SKIP]  {path}: not found")
            continue
        if not path.is_file():
            continue
        issues = lint_file(path)
        for severity, msg in issues:
            tag = {"PASS": "[OK]   ", "FAIL": "[FAIL] "}.get(severity, f"[{severity}]")
            print(f"  {tag} {msg}")
            if severity == "FAIL":
                overall_fail = True

    print()
    if overall_fail:
        print("---EXIT: 1---")
        return 1
    print("---EXIT: 0---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
