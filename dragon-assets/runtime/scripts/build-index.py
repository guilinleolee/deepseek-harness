#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build-index.py · 天龙引擎五资产三层索引构建器
========================================================

扫描仓库内 5 类资产（skill / agent / hook / command / plugin），
按统一 JSONL schema 写出 5 个 jsonl + 1 个 INDEX_MASTER.json。

调用：
    python scripts/build-index.py                # 全量扫 + 输出
    python scripts/build-index.py --stats       # 只统计不写盘
    python scripts/build-index.py --kind skill  # 仅扫一类
    python scripts/build-index.py --root .      # 指定根

输出：
    index/SKILLS.jsonl
    index/AGENTS.jsonl
    index/HOOKS.jsonl
    index/COMMANDS.jsonl
    index/PLUGINS.jsonl
    index/INDEX_MASTER.json
    index/INDEX_README.md

仅用 Python 标准库（json / re / configparser / pathlib）。
要求 Python ≥ 3.8（已与项目兼容）。

Schema 版本： dragon-index/1.0
"""
from __future__ import annotations

import argparse
import collections
import configparser
import json
import os
import re
import subprocess
import sys
import hashlib
import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

# ============================================================
# 常量
# ============================================================
SCHEMA_VERSION = "dragon-index/1.0"
REPO_ROOT_DEFAULT = Path(__file__).resolve().parent.parent
INDEX_DIR = REPO_ROOT_DEFAULT / "index"

STATUSES = ("blessed", "active", "experimental", "dormant", "deprecated")
KIND_TO_DIR = {
    "skill":   ("skills",   "SKILL.md"),
    "agent":   ("agents",   None),       # any *.md at depth 1
    "hook":    ("hooks",    None),       # .sh|.js|.py|.json
    "command": ("commands", None),       # *.md (含子目录)
    "plugin":  ("plugins",  None),       # 子目录
}

SKIP_DIR_NAMES = {"_archive", "_template", "__pycache__", "node_modules", ".git",
                  ".github", ".pytest_cache", ".mypy_cache", ".ruff_cache",
                  "backups", "db-backup", "cache", ".cache", "library"}

# ============================================================
# 元数据解析
# ============================================================
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL | re.MULTILINE)
SIMPLE_KV_RE = re.compile(r"^([A-Za-z0-9_\-\.]+)\s*:\s*(.*)$")
TRIGGERS_RE = re.compile(r'^\s*-\s*"?([^"\n]+?)"?\s*$', re.MULTILINE)
LIST_KEY_RE = re.compile(r"^([A-Za-z0-9_\-\.]+)\s*:\s*$")
NESTED_RE = re.compile(r"^(\s{2,})([A-Za-z0-9_\-\.]+)\s*:\s*(.*)$")

def _strip_inline_yaml(v: str) -> str:
    """剥离包裹引号 / | 块标记"""
    v = v.strip()
    if v.startswith('"') and v.endswith('"'):
        v = v[1:-1]
    if v.startswith("'") and v.endswith("'"):
        v = v[1:-1]
    if v.startswith("|") or v.startswith(">"):
        # 块标，前端只取一句概要
        v = ""
    return v.strip()

def parse_frontmatter(text: str) -> Tuple[Dict, str]:
    """极简 YAML frontmatter 解析 —— 不依赖 PyYAML。

    支持：
      - name: x
      - license: MIT
      - upstream: { 嵌套字段（缩进 2-4 空格） }
      - triggers: [ a, b ]   或   - a
                                        - b
    异常 → 返 ({}, 原文)
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    body = text[m.end():]
    fm: Dict = {}
    list_key: Optional[str] = None
    list_lines: List[str] = []
    nested_path: List[Tuple[str, int]] = []  # stack of (key, indent)

    def commit_list():
        nonlocal list_key, list_lines
        if list_key and list_lines:
            # 去引号 + 去空
            fm[list_key] = [s.strip().strip('"').strip("'") for s in list_lines if s.strip()]
        list_key = None
        list_lines = []

    for raw_line in m.group(1).splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        # list item?
        list_item = re.match(r"^\s*-\s+(.*)$", raw_line)
        if list_item and (list_key or nested_path):
            item = _strip_inline_yaml(list_item.group(1))
            if item:
                if not list_key:
                    # nested list under last parent
                    if nested_path:
                        parent_key = nested_path[-1][0]
                        parent = fm
                        for k, _ in nested_path[:-1]:
                            parent = parent.setdefault(k, {})
                        parent.setdefault(parent_key, []).append(item)
                    else:
                        fm.setdefault("_loose_list", []).append(item)
                else:
                    list_lines.append(item)
            continue

        # 顶层 k:v
        top = re.match(r"^([A-Za-z0-9_\-\.]+)\s*:\s*(.*)$", raw_line)
        if top and not raw_line.startswith(" "):
            commit_list()
            nested_path = []
            key = top.group(1).strip()
            val = top.group(2).strip()
            if val == "" or val in ("|", ">"):
                # list-block start
                list_key = key
                list_lines = []
                continue
            if val.startswith("[") and val.endswith("]"):
                # inline list
                inner = val[1:-1].strip()
                fm[key] = [s.strip().strip('"').strip("'") for s in inner.split(",") if s.strip()]
            else:
                fm[key] = _strip_inline_yaml(val)

            # check if next non-empty is nested (handled in next iter)
            continue

        # nested (indent 2-)
        nest = NESTED_RE.match(raw_line)
        if nest:
            indent = len(nest.group(1))
            key = nest.group(2)
            val = nest.group(3).strip()
            # pop deeper
            while nested_path and nested_path[-1][1] >= indent:
                nested_path.pop()
            nested_path.append((key, indent))

            parent = fm
            for k, _ in nested_path[:-1]:
                if k not in parent or not isinstance(parent.get(k), dict):
                    parent[k] = {}
                parent = parent[k]
            if val == "" or val in ("|", ">"):
                # nested list-start — handle inline  ▼
                pass
            else:
                parent[key] = _strip_inline_yaml(val)
            continue

    commit_list()
    return fm, body


def parse_runtime_conf(path: Path) -> Dict:
    if not path.exists():
        return {}
    cp = configparser.ConfigParser()
    try:
        cp.read(path, encoding="utf-8")
    except Exception:
        return {}
    out: Dict = {}
    for sec in cp.sections():
        sec_d = {}
        for k in cp[sec]:
            sec_d[k] = cp[sec][k]
        out[sec] = sec_d
    return out


# ============================================================
# 辅助
# ============================================================

def safe_read(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "gbk", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
        except OSError:
            return ""
    return ""


def file_size_kb(path: Path) -> float:
    try:
        return round(path.stat().st_size / 1024.0, 1)
    except OSError:
        return 0.0


def file_mtime_iso(path: Path) -> str:
    try:
        ts = path.stat().st_mtime
        return datetime.datetime.utcfromtimestamp(ts).isoformat(timespec="seconds") + "Z"
    except OSError:
        return ""


# 仓库根的 .git（前置 wrapper：subprocess 调用 git log 时使用）
def _repo_root(start: Path) -> Optional[Path]:
    cur = start.resolve()
    for p in [cur, *cur.parents]:
        if (p / ".git").exists():
            return p
    return None

def git_last_commit_iso(repo: Optional[Path], path: Path) -> str:
    """返回 path 相对 repo 的最后一次 commit ISO 时间。无 git → """""
    if not repo:
        return ""
    try:
        rel = str(path.resolve().relative_to(repo)).replace("\\", "/")
        out = subprocess.run(
            ["git", "-C", str(repo), "log", "-1", "--format=%cI", "--", rel],
            capture_output=True, text=True, timeout=8,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    return ""


def sniff_license_text(path: Path) -> str:
    """嗅 LICENSE / NOTICE 文件首段关键字。返回归一化 license 名或 ''。"""
    candidates = []
    for nm in ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "NOTICE", "NOTICE.md"):
        p = path / nm
        if p.exists() and p.is_file():
            candidates.append(p)
    if not candidates:
        return ""
    text = safe_read(candidates[0]).lower()
    head = text[:4000]
    if "apache license" in head and "version 2" in head:
        return "Apache-2.0"
    if "apache license" in head and "version 1" in head:
        return "Apache-1.0"
    if "gnu general public license" in head and "version 3" in head and "affero" in head:
        return "AGPL-3.0"
    if "gnu general public license" in head and "version 3" in head:
        return "GPL-3.0"
    if "gnu general public license" in head and "version 2" in head:
        return "GPL-2.0"
    if "gnu lesser general public" in head:
        return "LGPL"
    if "mit license" in head or "permission is hereby granted, free of charge" in head:
        return "MIT"
    if "bsd 2-clause" in head or "redistribution and use in source and binary forms" in head and "neither the name of" in head:
        return "BSD-2-Clause"
    if "bsd 3-clause" in head or ("redistribution and use in source and binary forms" in head and "neither the name of" in head):
        return "BSD-3-Clause"
    if "mozilla public license" in head and "version 2" in head:
        return "MPL-2.0"
    if "isc license" in head or "permission to use, copy, modify" in head and "without restriction" in head:
        return "ISC"
    if "creative commons" in head and "attribution" in head:
        return "CC-BY"
    if "creative commons" in head and "attribution-sharealike" in head:
        return "CC-BY-SA"
    if "the unlicense" in head or "this is free and unencumbered software" in head:
        return "Unlicense"
    return "unknown"


def short_hash(path: Path) -> str:
    try:
        with path.open("rb") as f:
            data = f.read(4096)
        return hashlib.sha1(data).hexdigest()[:8]
    except OSError:
        return ""


def first_doc_line(text: str) -> str:
    """提取首段一级标题 / 描述首句作为 one_liner。"""
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            s = s.lstrip("#").strip()
        if s:
            # 截断到 80 字符
            return s[:80].rstrip() + ("…" if len(s) > 80 else "")
    return ""


def looks_cjk_corrupted(name: str) -> bool:
    """简单检测中文是否被当成 GBK 误解码（典型：连续 璋冪爺 这种乱码特征）。"""
    if not name:
        return False
    for bad in ("璋", "鏋", "鐢", "浣"):
        if bad in name:
            return True
    return False


def normalize_license(s: str) -> str:
    if not s:
        return "unknown"
    s = s.strip().lower()
    if "agpl" in s:
        return "AGPL-3.0"
    if "apache" in s:
        return "Apache-2.0"
    if "mit" in s:
        return "MIT"
    if "self" in s or "self-research" in s:
        return "self"
    if "proprietary" in s or "commercial" in s:
        return "proprietary"
    return s.split()[0]


def derive_status(fm: Dict, rel: Path) -> str:
    """启发式：frontmatter 显式 status > 路径里有 archive/deprecated > 默认 active。"""
    s = (fm.get("status") or "").strip().lower()
    if s in STATUSES:
        return s
    if "deprecated" in str(fm).lower() or "_archive" in rel.parts or "DEPRECATED" in str(fm):
        return "deprecated"
    if "experimental" in str(fm.get("description", "")).lower():
        return "experimental"
    return "active"


def detect_kind_from_id(id_: str, rel: Path) -> str:
    """极少需要：本函数保留以备 hand-rolled 元数据。"""
    return ""


# ============================================================
# 扫描器
# ============================================================

def scan_skills(root: Path, include_library: bool = False, repo: Optional[Path] = None) -> Iterable[Dict]:
    """skills/<name>/SKILL.md。include_library=True 时递归扫 library/ 子目录。"""
    skills_dir = root / "skills"
    if not skills_dir.exists():
        return
    for entry in sorted(skills_dir.iterdir()):
        if not entry.is_dir() or entry.name in SKIP_DIR_NAMES or entry.name.startswith("."):
            continue
        skill_md = entry / "SKILL.md"
        if skill_md.exists():
            text = safe_read(skill_md)
            fm, body = parse_frontmatter(text)
            rc = parse_runtime_conf(entry / "runtime.conf")
            yield _emit(
                kind="skill",
                path=skill_md,
                id_=fm.get("name") or entry.name,
                fm=fm,
                body=body,
                rc=rc,
                rel=skill_md.relative_to(root),
                sibling=entry,
                repo=repo,
            )
        # 递归：library/<group>/<name>/SKILL.md —— muapi 镜像
        if include_library:
            lib_dir = entry / "library"
            if lib_dir.exists() and lib_dir.is_dir():
                for sub in sorted(lib_dir.rglob("SKILL.md")):
                    if not sub.is_file():
                        continue
                    text = safe_read(sub)
                    fm, body = parse_frontmatter(text)
                    # 旧 muapi 格式只有 slug:/name: 无 --- 包裹
                    if not fm:
                        # 退化：从正文首行扫 slug:
                        head = text[:512]
                        m = re.search(r"^slug:\s*(\S+)", head, re.MULTILINE)
                        if m:
                            fm = {"name": m.group(1), "license": "MIT"}
                    yield _emit(
                        kind="skill",
                        path=sub,
                        id_=fm.get("name") or fm.get("slug") or sub.parent.name,
                        fm=fm,
                        body=body,
                        rc={},
                        rel=sub.relative_to(root),
                        sibling=sub.parent,
                        repo=repo,
                    )


def scan_agents(root: Path, repo: Optional[Path] = None) -> Iterable[Dict]:
    agents_dir = root / "agents"
    if not agents_dir.exists():
        return
    for entry in sorted(agents_dir.iterdir()):
        if entry.is_dir():
            # 嵌套 .md，名字带一层
            for sub in sorted(entry.rglob("*.md")):
                if sub.is_file() and sub.parent.name not in SKIP_DIR_NAMES:
                    yield from _scan_agent_file(root, sub, repo)
            continue
        if entry.suffix == ".md" and entry.name not in SKIP_DIR_NAMES and not entry.name.startswith("."):
            yield from _scan_agent_file(root, entry, repo)


def _scan_agent_file(root: Path, path: Path, repo: Optional[Path] = None) -> Iterable[Dict]:
    text = safe_read(path)
    fm, body = parse_frontmatter(text)
    yield _emit(
        kind="agent",
        path=path,
        id_=fm.get("name") or path.stem,
        fm=fm,
        body=body,
        rc={},
        rel=path.relative_to(root),
        sibling=path,
        repo=repo,
    )


def scan_hooks(root: Path, repo: Optional[Path] = None) -> Iterable[Dict]:
    hooks_dir = root / "hooks"
    if not hooks_dir.exists():
        return
    for path in sorted(hooks_dir.rglob("*")):
        if not path.is_file():
            continue
        if any(p in SKIP_DIR_NAMES for p in path.relative_to(hooks_dir).parts[:-1]):
            continue
        if path.suffix not in {".sh", ".js", ".py", ".json"}:
            continue
        if path.name.startswith("."):
            continue
        # 取 hooks 内的相对路径作为 id（去后缀 + 去 hooks/ 前缀）
        rel = path.relative_to(root)
        rel_no_ext = str(rel.with_suffix("")).replace("\\", "/")
        if rel_no_ext.startswith("hooks/"):
            rel_no_ext = rel_no_ext[len("hooks/"):]
        text = safe_read(path) if path.suffix != ".json" else ""
        fm = {}
        # .js/.py/.sh 通常无 frontmatter，不强求
        if text:
            fm, _ = parse_frontmatter(text)
        yield _emit(
            kind="hook",
            path=path,
            id_=rel_no_ext,
            fm=fm,
            body=text,
            rc={},
            rel=rel,
            sibling=path,
            repo=repo,
        )


def scan_commands(root: Path, repo: Optional[Path] = None) -> Iterable[Dict]:
    commands_dir = root / "commands"
    if not commands_dir.exists():
        return
    for path in sorted(commands_dir.rglob("*.md")):
        if not path.is_file():
            continue
        if any(p in SKIP_DIR_NAMES for p in path.relative_to(commands_dir).parts[:-1]):
            continue
        rel = path.relative_to(root)
        rel_str = str(rel).replace("\\", "/")
        if looks_cjk_corrupted(path.name):
            # 不抛错，仅标注乱码
            pass
        text = safe_read(path)
        fm, body = parse_frontmatter(text)
        yield _emit(
            kind="command",
            path=path,
            id_=fm.get("name") or rel_str.replace("/", "-").replace(".md", ""),
            fm=fm,
            body=body,
            rc={},
            rel=rel,
            sibling=path,
            repo=repo,
        )


def scan_plugins(root: Path, repo: Optional[Path] = None) -> Iterable[Dict]:
    plugins_dir = root / "plugins"
    if not plugins_dir.exists():
        return
    # 1) 以子目录为单位
    for entry in sorted(plugins_dir.iterdir()):
        if not entry.is_dir() or entry.name in SKIP_DIR_NAMES or entry.name.startswith("."):
            continue
        # 嗅插件 README / package.json / settings.json
        marker = None
        for cand in ("README.md", "package.json", "settings.json"):
            p = entry / cand
            if p.exists():
                marker = p
                break
        meta_text = safe_read(marker) if marker and marker.suffix != ".json" else ""
        fm = {}
        if meta_text and meta_text.lstrip().startswith("---"):
            fm, _ = parse_frontmatter(meta_text)
        # 也尝试读 installed_plugins.json 摘要
        yield _emit(
            kind="plugin",
            path=marker or (entry / "__dir__"),
            id_=entry.name,
            fm=fm,
            body=meta_text,
            rc={},
            rel=(marker or entry).relative_to(root),
            sibling=entry,
            repo=repo,
        )


# ============================================================
# 发射器
# ============================================================

def _emit(kind: str, path: Path, id_: str, fm: Dict, body: str, rc: Dict,
          rel: Path, sibling: Path, repo: Optional[Path] = None) -> Dict:
    """统一 schema 输出。"""
    upstream = fm.get("upstream") if isinstance(fm.get("upstream"), dict) else {}
    triggers = fm.get("triggers")
    if isinstance(triggers, str):
        triggers = [triggers]
    if not isinstance(triggers, list):
        triggers = []
    phrases = fm.get("phrases")
    if not isinstance(phrases, list):
        phrases = []
    tags = fm.get("tags")
    if not isinstance(tags, list):
        tags = []
    pitfalls = fm.get("pitfalls")
    if not isinstance(pitfalls, list):
        pitfalls = []

    # license 解析流水线：frontmatter → runtime.conf → upstream → LICENSE/NOTICE sniff
    raw_license = (
        fm.get("license")
        or rc.get("skill", {}).get("license")
        or (upstream.get("license") if upstream else "")
        or ""
    )
    license_norm = normalize_license(raw_license) if raw_license else ""
    license_source = "frontmatter" if raw_license else ""
    if not license_norm:
        sniffed = sniff_license_text(sibling.parent if sibling.is_file() else sibling)
        if sniffed and sniffed != "unknown":
            license_norm = sniffed
            license_source = "LICENSE_FILE"
            raw_license = sniffed

    version = (
        fm.get("version")
        or rc.get("skill", {}).get("version")
        or (upstream.get("version") if upstream else "")
        or ""
    )

    one_liner = (
        fm.get("description")
        or first_doc_line(body)
        or ""
    )
    if isinstance(one_liner, list):
        one_liner = " / ".join(str(x) for x in one_liner)
    one_liner = str(one_liner).replace("\n", " ").strip()
    if len(one_liner) > 120:
        one_liner = one_liner[:117] + "…"

    mtime = file_mtime_iso(path)
    last_used = git_last_commit_iso(repo, path)
    return {
        "schema": SCHEMA_VERSION,
        "id": id_,
        "kind": kind,
        "version": str(version) if version else "",
        "status": derive_status(fm, rel),
        "license": license_norm or "unknown",
        "license_raw": str(raw_license) if raw_license else "",
        "license_source": license_source,
        "upstream": {
            "name": upstream.get("name", ""),
            "version": upstream.get("version", ""),
            "url": upstream.get("url", ""),
            "stars": upstream.get("stars", ""),
        } if upstream else {},
        "path": str(rel).replace("\\", "/"),
        "size_kb": file_size_kb(path),
        "mtime": mtime,
        "last_used": last_used,
        "hash": short_hash(path),
        "triggers": [str(t).strip() for t in triggers if str(t).strip()],
        "phrases": [str(t).strip() for t in phrases if str(t).strip()],
        "tags": [str(t).strip() for t in tags if str(t).strip()],
        "pitfalls": [str(t).strip() for t in pitfalls if str(t).strip()][:3],
        "department": str(fm.get("department", "")),
        "category": str(fm.get("category", "")),
        "modified": str(fm.get("modified", "")),
        "modified_by": str(fm.get("modified_by", "")),
        "doc_one_liner": one_liner,
    }


# ============================================================
# 写入
# ============================================================

def write_jsonl(rows: List[Dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_master(master: Dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(master, f, ensure_ascii=False, indent=2)


def write_readme(master: Dict, rows_by_kind: Dict[str, List[Dict]], path: Path) -> None:
    lines: List[str] = []
    lines.append("# index/ · 天龙引擎五资产索引 · 自动生成\n")
    lines.append(f"> **schema**: `{SCHEMA_VERSION}`  ·  生成时间：{datetime.datetime.utcnow().isoformat(timespec='seconds')}Z\n")
    lines.append("> **用法**：每次大模型启动时只读 `CLAUDE.md`（hot 层）；命中触发词后查对应 `*.jsonl`（warm 层）；按 `id` 再读 `cold` 资产原文。\n")
    lines.append("\n## 📊 全量统计\n")
    lines.append("| kind | files | total_kb | active | deprecated | license breakdown |")
    lines.append("|---|---|---|---|---|---|")
    for kind, rows in rows_by_kind.items():
        total_kb = round(sum(r.get("size_kb", 0) for r in rows), 1)
        active = sum(1 for r in rows if r.get("status") == "active")
        deprecated = sum(1 for r in rows if r.get("status") == "deprecated")
        lic = {}
        for r in rows:
            l = r.get("license", "unknown")
            lic[l] = lic.get(l, 0) + 1
        breakdown = " · ".join(f"{k}:{v}" for k, v in sorted(lic.items(), key=lambda x: -x[1])[:4])
        lines.append(f"| {kind} | {len(rows)} | {total_kb:.1f} | {active} | {deprecated} | {breakdown} |")

    lines.append("\n## 📁 文件清单\n")
    lines.append("| 文件 | 行数 | 用途 |")
    lines.append("|---|---|---|")
    lines.append(f"| `SKILLS.jsonl` | {master['counts']['skill']} | skill 一级目录（含 library/ 套件剔除） |")
    lines.append(f"| `AGENTS.jsonl` | {master['counts']['agent']} | agent 角色定义 |")
    lines.append(f"| `HOOKS.jsonl` | {master['counts']['hook']} | 钩子脚本（sh/js/py/json） |")
    lines.append(f"| `COMMANDS.jsonl` | {master['counts']['command']} | 命令文件（含中文乱码警告） |")
    lines.append(f"| `PLUGINS.jsonl` | {master['counts']['plugin']} | plugin 插件 |")
    lines.append(f"| `INDEX_MASTER.json` | - | 总入口 + 元数据 + schema 版本 |")
    lines.append(f"| `INDEX_README.md` | - | 本文件 |")

    lines.append("\n## 🔥 Hot / Warm / Cold 三层模型\n")
    lines.append("- **Hot**（每次必读 · ≤ 6 KB）→ `CLAUDE.md` §3 触发词路由表")
    lines.append("- **Warm**（按需 lazy · 命中后整类加载）→ 5 个 `*.jsonl`")
    lines.append("- **Cold**（按 ID 精确加载）→ 各资产原文件 SKILL.md / *.md\n")

    lines.append("## 💡 检索样例\n")
    lines.append("```bash")
    lines.append("# 按 ID 查 skill")
    lines.append("grep '\"id\": \"nuwa-skill\"' index/SKILLS.jsonl")
    lines.append("")
    lines.append("# 按触发词查 agents")
    lines.append("grep '\"博主' index/AGENTS.jsonl | head -5")
    lines.append("")
    lines.append("# 找所有 MIT license 的 skill")
    lines.append("grep '\"license\": \"MIT\"' index/SKILLS.jsonl | wc -l")
    lines.append("```\n")

    lines.append("## 🔁 同步\n")
    lines.append("```bash")
    lines.append("# 全量重建")
    lines.append("python scripts/build-index.py")
    lines.append("")
    lines.append("# 仅统计")
    lines.append("python scripts/build-index.py --stats")
    lines.append("```\n")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ============================================================
# 主流程
# ============================================================

SCANNERS = {
    "skill":   scan_skills,
    "agent":   scan_agents,
    "hook":    scan_hooks,
    "command": scan_commands,
    "plugin":  scan_plugins,
}

def main():
    ap = argparse.ArgumentParser(description="build 5-asset dragon-engine index")
    ap.add_argument("--root", default=str(REPO_ROOT_DEFAULT), help="项目根")
    ap.add_argument("--kind", choices=list(SCANNERS) + ["all"], default="all")
    ap.add_argument("--stats", action="store_true", help="只统计，不写盘")
    ap.add_argument("--index-dir", default=str(INDEX_DIR), help="索引输出目录")
    ap.add_argument("--include-library", action="store_true",
                    help="递归扫 skills/*/library/ 下的镜像 SKILL.md（默认关闭）")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    index_dir = Path(args.index_dir).resolve()
    repo = _repo_root(root)

    if not (root / "skills").exists():
        print(f"[ERR] root 不像天龙引擎主树：{root}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] root = {root}", file=sys.stderr)
    print(f"[INFO] index_dir = {index_dir}", file=sys.stderr)
    print(f"[INFO] git_repo = {repo or '(no .git found)'}", file=sys.stderr)
    print(f"[INFO] include_library = {args.include_library}", file=sys.stderr)

    kinds = list(SCANNERS) if args.kind == "all" else [args.kind]
    rows_by_kind: Dict[str, List[Dict]] = {}
    total = 0

    for kind in kinds:
        fn = SCANNERS[kind]
        if kind == "skill":
            rows = list(fn(root, include_library=args.include_library, repo=repo))
        else:
            rows = list(fn(root, repo=repo))
        # 去重：按 id，路径更短的优先（去嵌套过深）
        rows.sort(key=lambda r: (r["id"], len(r["path"])))
        dedup = {}
        for r in rows:
            dedup[r["id"]] = r
        rows = sorted(dedup.values(), key=lambda r: r["id"])
        rows_by_kind[kind] = rows
        total += len(rows)

    print("[INFO] counts:", {k: len(v) for k, v in rows_by_kind.items()}, file=sys.stderr)

    # license 来源统计
    src_counter = collections.Counter()
    for rows in rows_by_kind.values():
        for r in rows:
            src_counter[r.get("license_source") or "(empty/none)"] += 1
    print("[INFO] license_source:", dict(src_counter), file=sys.stderr)

    if args.stats:
        for kind, rows in rows_by_kind.items():
            print(f"\n=== {kind.upper()}  (n={len(rows)}) ===")
            for r in rows[:6]:
                print(f"  {r['id']:50s} {r.get('license', '?'):14s} {r.get('status', '?'):12s} {r['path']}")
            if len(rows) > 6:
                print(f"  ... (+{len(rows)-6} more)")
        return

    # 写盘
    jsonl_targets = {
        "skill":   index_dir / "SKILLS.jsonl",
        "agent":   index_dir / "AGENTS.jsonl",
        "hook":    index_dir / "HOOKS.jsonl",
        "command": index_dir / "COMMANDS.jsonl",
        "plugin":  index_dir / "PLUGINS.jsonl",
    }

    for kind, path in jsonl_targets.items():
        if kind in rows_by_kind:
            write_jsonl(rows_by_kind[kind], path)
            print(f"[OK] wrote {path}  (n={len(rows_by_kind[kind])})", file=sys.stderr)

    master = {
        "schema": SCHEMA_VERSION,
        "generated_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "root": str(root),
        "counts": {k: len(v) for k, v in rows_by_kind.items()},
        "total": total,
        "files": {k: str(p.relative_to(index_dir)).replace("\\", "/") for k, p in jsonl_targets.items() if k in rows_by_kind},
        "layers": {
            "hot": "CLAUDE.md §3 触发词路由表",
            "warm": [str(p.relative_to(index_dir)).replace("\\", "/") for p in jsonl_targets.values()],
            "cold": "skills/<id>/SKILL.md · agents/<id>.md · hooks/<id>.{sh,js,py} · commands/<id>.md · plugins/<id>/README.md",
        },
        "schema_definition": {
            "required": ["schema", "id", "kind", "status", "path"],
            "optional": [
                "version", "license", "license_raw", "license_source",
                "upstream.{name,version,url,stars}",
                "size_kb", "mtime", "last_used", "hash",
                "triggers", "phrases", "tags", "pitfalls",
                "department", "category", "modified", "modified_by",
                "doc_one_liner",
            ],
        },
    }
    write_master(master, index_dir / "INDEX_MASTER.json")
    print(f"[OK] wrote {index_dir / 'INDEX_MASTER.json'}", file=sys.stderr)

    write_readme(master, rows_by_kind, index_dir / "INDEX_README.md")
    print(f"[OK] wrote {index_dir / 'INDEX_README.md'}", file=sys.stderr)

    print(f"\n[DONE] {total} 个资产已索引。", file=sys.stderr)


if __name__ == "__main__":
    main()
