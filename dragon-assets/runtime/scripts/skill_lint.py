"""skill_lint V1.0 — Stage 46 nomifun-methodology.

扫 dragon-engine/skills/**/SKILL.md 与 _templates/* 文件，对 frontmatter 做 12 项断言。

借鉴档模式（与 stage 41 mneme / stage 45 dsh-eval 一致）：不克隆真源，自研 lint。
参考：https://github.com/nomifun/nomifun-desktop/blob/main/docs/skills/drive-nomifun/SKILL.md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

# SKILL.md 11 字段标准 frontmatter（自上而下）
STANDARD_FIELDS = [
    "name", "version", "base_version", "description",
    "triggers", "upstream", "downstream", "inputs", "outputs", "errors",
    "DO", "DONTS", "example",
]
# 最小模式兼容字段（天龙现有 SKILL.md 大多为此模式）
MINIMAL_FIELDS = ["license", "triggers"]
SEMVER_RE = re.compile(r"^V?\d+(\.\d+){0,2}$")
KEBAB_RE = re.compile(r"^[a-z][a-z0-9-]*[a-z0-9]$")
TRIGGER_MAX_LEN = 15


def _parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    """Extract YAML frontmatter (between --- fences) as a dict.

    自研 YAML 微解析（不接 PyYAML）：
      - key: value
      - key:
          - "item"   (YAML list)
      - key: |
          block     (block scalar)
      - key: >-
          folded
      - example:
          cli: |
            ...
          output: |
            ...      (YAML mapping 之 nested scalar)
    """
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    raw = parts[1]
    body = parts[2].lstrip("\n")
    fm: dict[str, object] = {}
    cur_key: str | None = None
    cur_block_kind: str | None = None  # None | "scalar" | "list" | "map_scalar"
    cur_lines: list[str] = []

    def _commit() -> None:
        nonlocal cur_block_kind, cur_lines
        if cur_key is None:
            return
        if cur_block_kind == "list":
            items: list[str] = []
            for ln in cur_lines:
                if ln.startswith("  - "):
                    rest = ln[4:].strip()
                    if rest:
                        items.append(rest.strip('"').strip("'"))
                elif ln.startswith("    ") and items:
                    # 后续子项对齐
                    items.append(ln.strip().strip('"').strip("'"))
            fm[cur_key] = [x for x in items if x]
        elif cur_block_kind == "scalar":
            fm[cur_key] = "\n".join(cur_lines).strip()
        elif cur_block_kind == "map_scalar":
            # for `example: { cli: '|', output: '|' }` —— 把 mapping 收集为 nested dict 字符串
            sub: dict[str, object] = {}
            last_key: str | None = None
            buf: list[str] = []
            for ln in cur_lines:
                # 形如 `  cli: |`
                if ln.startswith("  ") and ":" in ln and not ln.startswith("    "):
                    if last_key is not None:
                        sub[last_key] = "\n".join(buf).strip()
                    last_k, _, last_v = ln.strip().partition(":")
                    last_key = last_k.strip()
                    lv = last_v.strip()
                    if lv.startswith("|") or lv.startswith(">"):
                        buf = []
                    else:
                        buf = [lv]
                elif last_key is not None:
                    buf.append(ln.lstrip())
            if last_key is not None:
                sub[last_key] = "\n".join(buf).strip()
            fm[cur_key] = sub
        else:
            fm[cur_key] = ""
        cur_block_kind = None
        cur_lines = []

    for line in raw.splitlines():
        is_top_key = (
            line
            and not line.startswith((" ", "\t"))
            and ":" in line
            and not line.startswith("-")
        )
        if is_top_key:
            _commit()
            key, _, value = line.partition(":")
            cur_key = key.strip()
            value = value.strip()
            if value == "":
                # 默认 list —— 下一行再视情形升级为 scalar / map_scalar
                cur_block_kind = "list"
                cur_lines = []
            elif value.startswith("|") or value.startswith(">"):
                cur_block_kind = "scalar"
                cur_lines = []
            elif value.startswith("["):
                inner = value[1:-1] if value.endswith("]") else value[1:]
                items = [x.strip().strip('"').strip("'") for x in inner.split(",") if x.strip()]
                fm[cur_key] = items
                cur_key = None
                cur_block_kind = None
                cur_lines = []
            else:
                fm[cur_key] = value
                cur_key = None
                cur_block_kind = None
                cur_lines = []
            continue

        if cur_key is None:
            continue

        stripped = line.lstrip()

        if not stripped:
            cur_lines.append(line)
            continue

        # 升级路径：list → map_scalar 若第一行是 `  cli: |`
        if cur_block_kind == "list" and line.startswith("  ") and ":" in stripped and not stripped.startswith("-"):
            cur_block_kind = "map_scalar"
            cur_lines.append(line)
            continue

        if cur_block_kind == "list" and stripped.startswith("-"):
            cur_lines.append(line)
            continue

        if cur_block_kind == "scalar":
            cur_lines.append(stripped)
            continue

        if cur_block_kind == "map_scalar":
            cur_lines.append(line)
            continue

    _commit()
    return fm, body


def _is_standard(fm: dict[str, object]) -> bool:
    return "name" in fm and "DO" in fm


def lint_file(path: Path) -> list[tuple[str, str]]:
    """Return list of (severity, message) for each issue found.

    severity: "PASS" (informational) or "FAIL" (assertion violation).
    """
    issues: list[tuple[str, str]] = []
    text = path.read_text(encoding="utf-8")

    # 模板文件默认跳过严格断言（占位符 / 注释非真值）
    if path.name.endswith(".template"):
        issues.append(("PASS", f"{path.name}: TEMPLATE mode (skipped strict assertions)"))
        return issues

    fm, _ = _parse_frontmatter(text)
    if not fm:
        issues.append(("FAIL", f"{path.name}: frontmatter missing (no leading '---')"))
        return issues

    standard = _is_standard(fm)

    # === 12 断言 ===
    # 1. name kebab-case + ≤ 64
    name = str(fm.get("name", "")).strip()
    if standard:
        if not name:
            issues.append(("FAIL", f"{path.name}: standard mode: name missing"))
        elif not KEBAB_RE.match(name):
            issues.append(("FAIL", f"{path.name}: name '{name}' not kebab-case"))
        elif len(name) > 64:
            issues.append(("FAIL", f"{path.name}: name too long ({len(name)} > 64)"))

    # 2. version semver
    version = str(fm.get("version", "")).strip()
    if standard and version:
        if not SEMVER_RE.match(version):
            issues.append(("FAIL", f"{path.name}: version '{version}' not semver X.Y(.Z)"))

    # 3. frontmatter 字段顺序（standard 模式严格）
    if standard:
        seen: list[str] = []
        for line in (text.split("---", 2)[1] if text.startswith("---") else "").splitlines():
            if line and not line.startswith((" ", "\t", "-", "|", "#")) and ":" in line:
                key = line.partition(":")[0].strip()
                if key in STANDARD_FIELDS:
                    seen.append(key)
        # 检查 seen 是否是 STANDARD_FIELDS 的 prefix
        canonical = [f for f in STANDARD_FIELDS if f in seen] + [f for f in seen if f not in STANDARD_FIELDS]
        if canonical != seen:
            issues.append(("FAIL", f"{path.name}: standard fields out-of-order; got {seen}"))

    # 4. triggers 非空 + ≥ 2 条 + 去重 + 长度
    triggers = fm.get("triggers", [])
    if not isinstance(triggers, list):
        triggers = []
    if not triggers:
        issues.append(("FAIL", f"{path.name}: triggers missing"))
    else:
        if len(set(triggers)) != len(triggers):
            dup = sorted({t for t in triggers if triggers.count(t) > 1})
            issues.append(("FAIL", f"{path.name}: triggers duplicated: {dup}"))
        for t in triggers:
            if not isinstance(t, str):
                continue
            t = t.strip()
            if len(t) > TRIGGER_MAX_LEN:
                issues.append(("FAIL", f"{path.name}: trigger '{t}' too long ({len(t)}>{TRIGGER_MAX_LEN})"))

    # 5. triggers 不与 description 字符串完全相同
    desc = str(fm.get("description", "")).strip()
    if isinstance(triggers, list) and desc:
        desc_compact = re.sub(r"\s+", " ", desc).strip()
        for t in triggers:
            if isinstance(t, str) and re.sub(r"\s+", " ", t).strip() == desc_compact:
                issues.append(("FAIL", f"{path.name}: trigger '{t}' duplicates description verbatim"))

    # 6. description 长度（≤ 200 字符——"一句" + 触发词锚定）
    if standard and desc and len(desc) > 200:
        issues.append(("FAIL", f"{path.name}: description too long ({len(desc)}>200)"))

    # 7. upstream 是列表且每条格式 owner/repo Vx.y.z (Protocol · Stars)
    if standard and "upstream" in fm:
        upstream = fm["upstream"]
        if isinstance(upstream, list):
            for u in upstream:
                if not isinstance(u, str) or "/" not in u:
                    issues.append(("FAIL", f"{path.name}: upstream entry '{u}' missing 'owner/repo'"))

    # 8. downstream ≥ 2 条
    if standard:
        downstream = fm.get("downstream", [])
        if isinstance(downstream, list) and len(downstream) < 2:
            issues.append(("FAIL", f"{path.name}: downstream < 2 agents"))

    # 9. inputs / outputs 是列表
    if standard:
        for key in ("inputs", "outputs", "errors"):
            val = fm.get(key, [])
            if isinstance(val, list) and len(val) == 0:
                issues.append(("FAIL", f"{path.name}: {key} empty"))

    # 10. DO 恰好 6 条（天龙约定）
    if standard:
        do = fm.get("DO", [])
        if isinstance(do, list) and len(do) != 6:
            issues.append(("FAIL", f"{path.name}: DO must be exactly 6 items, got {len(do)}"))

    # 11. DONTS 恰好 10 条（天龙约定 + mneme 借鉴）
    if standard:
        donts = fm.get("DONTS", [])
        if isinstance(donts, list) and len(donts) != 10:
            issues.append(("FAIL", f"{path.name}: DONTS must be exactly 10 items, got {len(donts)}"))

    # 12. example 必须含 cli + output
    if standard:
        ex = fm.get("example", "")
        if not ex:
            issues.append(("FAIL", f"{path.name}: example missing"))
        elif "..." == str(ex).strip():
            issues.append(("FAIL", f"{path.name}: example is placeholder '...'; provide real output"))

    if not issues:
        mode = "STANDARD" if standard else "MINIMAL"
        issues.append(("PASS", f"{path.name}: {mode} mode OK"))
    return issues


def _iter_skill_files(root: Path) -> Iterable[Path]:
    for path in (root / "skills").rglob("SKILL.md"):
        yield path
    for path in (root / "skills" / "_templates").glob("SKILL*.template"):
        # 模板文件默认跳过严格 lint（占位符 / 注释）
        yield path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="skill_lint V1.0 — Stage 46 nomifun-methodology")
    parser.add_argument("paths", nargs="*", default=None,
                        help="Specific SKILL.md paths; omit to scan whole skills/ tree")
    parser.add_argument("--root", default=".",
                        help="Project root (default: current dir)")
    parser.add_argument("--strict", action="store_true",
                        help="Exit non-zero on FAIL")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if args.paths:
        targets = [Path(p).resolve() for p in args.paths]
    else:
        targets = list(_iter_skill_files(root))

    overall_fail = False
    print(f"skill_lint V1.0 · Stage 46 nomifun-methodology · scanning {len(targets)} files")
    for path in targets:
        if not path.exists():
            print(f"  [SKIP]  {path}: not found")
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
