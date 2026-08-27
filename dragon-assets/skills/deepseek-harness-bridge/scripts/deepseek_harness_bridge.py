"""
deepseek-harness-bridge V1.0 · Stage 50.1 借鉴档 · deepseek-ai/deepseek-harness MIT 借鉴

================================================================================
  Stage 50.1 · 2026-08-26

设计：
  - 借鉴档模式（与 stage 41 mneme / 45 dsh-eval / 46 dsh-peak-gate / 48 dsh-TUI / 49.1-49.4 同）
  - 5 类借鉴：DSH 官方主仓架构 / "Everything is a Plugin" 哲学 / cordis patch 协议 /
    @deepseek-ai/* peer dependencies / pnpm monorepo workspace 模板
  - 3 重 blocker：108.9 MB 巨型 + native/landlock-run + vendor + 自定义 scripts
  - 自研 15+ unittest PASS
  - 退出码契约：0=OK / 1=PARSE_ERR / 2=CONFIG_ERR / 3=PEER_ERR
================================================================================
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

EXIT_OK = 0
EXIT_PARSE = 1
EXIT_CONFIG = 2
EXIT_PEER = 3


# ==============================================================================
# 1. DSH 官方主仓架构（5 子仓模板 · 借鉴 workspace 配置）
# ==============================================================================

DSH_OFFICIAL_WORKSPACES = [
    "vendor/*",                    # @deepseek-ai/* 主仓包（peer 依赖）
    "packages/*/*",                # 官方子包（host / client / mcp 等）
    "native/landlock-run",         # Linux 内核 sandbox（Windows 不可用）
    "native/landlock-run/packages/*",
    "apps/*",                      # 终端应用（CLI / TUI / IDE 等）
    "website",                     # 官方文档站
]


@dataclass
class DSHWorkspace:
    """DSH workspace 模板（借鉴上游 monorepo）"""
    pattern: str          # glob pattern
    purpose: str          # workspace 用途
    is_native: bool = False   # 是否 native code（Linux only）


# ==============================================================================
# 2. "Everything is a Plugin" 哲学（5 原则 · 借鉴 README 核心）
# ==============================================================================

EVERYTHING_IS_A_PLUGIN_PRINCIPLES = [
    "每个工具都是 Plugin（cordis + DSH bundle 标准）",
    "Plugin 通过 manifest 声明 metadata（id/name/version/entry）",
    "Plugin 与 host 解耦（通过 cordis Service interface）",
    "Plugin 失败不影响 host（graceful degradation）",
    "Plugin 可热插拔（runtime load/unload）",
]


# ==============================================================================
# 3. cordis.patch.yml 协议（借鉴 stage 47 dsh-univer-office 与 stage 44 trajectory-debug）
# ==============================================================================

REQUIRED_PATCH_KEYS = ["patch"]


@dataclass
class CordisPatch:
    """cordis patch 单元（借鉴官方 cordis plugin 协议）"""
    insert: List[Dict[str, Any]]  # 待插入的 plugin 行


def parse_cordis_patch(yaml_text: str) -> CordisPatch:
    """解析 cordis.patch.yml（mock YAML 解析）"""
    # 简化版：检查 'patch:' 存在
    if "patch:" not in yaml_text:
        raise ValueError("missing 'patch:' key in cordis.patch.yml")
    inserts = []
    # 提取 - insert: 块（简化）
    in_insert = False
    for line in yaml_text.split("\n"):
        if "- insert:" in line:
            in_insert = True
            continue
        if in_insert and line.strip().startswith("- id:"):
            plugin_id = line.split(":", 1)[1].strip()
            inserts.append({"id": plugin_id})
    return CordisPatch(insert=inserts)


def validate_cordis_patch(patch: CordisPatch) -> List[str]:
    """校验 cordis patch 完整性"""
    issues = []
    if not patch.insert:
        issues.append("no insert entries in cordis.patch.yml")
    for entry in patch.insert:
        if "id" not in entry:
            issues.append(f"missing 'id' in patch entry: {entry}")
    return issues


# ==============================================================================
# 4. @deepseek-ai/* peer dependencies 校验（7 包）
# ==============================================================================

DEEPSEEK_AI_PEERS = [
    "@deepseek-ai/cordis",
    "@deepseek-ai/dsh-cmdline",
    "@deepseek-ai/dsh-invariants",
    "@deepseek-ai/dsh-llm",
    "@deepseek-ai/dsh-llm-retry",
    "@deepseek-ai/dsh-session",
    "@deepseek-ai/dsh-web-frontend",
]


@dataclass
class PeerCheck:
    """peer dependency 检查结果"""
    package: str
    in_package_json: bool
    in_node_modules: bool
    note: str = ""


def check_peers(package_json: Dict[str, Any]) -> List[PeerCheck]:
    """检查 7 个 @deepseek-ai/* peer 是否在 package.json 中"""
    deps = {**package_json.get("dependencies", {}),
            **package_json.get("devDependencies", {}),
            **package_json.get("peerDependencies", {})}
    results = []
    for peer in DEEPSEEK_AI_PEERS:
        # 简化版：用 startswith 检查（@deepseek-ai/cordis vs ^4.0.1）
        matched = any(p.startswith(peer) for p in deps.keys())
        results.append(PeerCheck(
            package=peer,
            in_package_json=matched,
            in_node_modules=False,  # mock：不实跑 npm ls
            note="OK" if matched else "MISSING",
        ))
    return results


# ==============================================================================
# 5. pnpm monorepo workspace 模板生成
# ==============================================================================

@dataclass
class WorkspaceTemplate:
    """pnpm workspace 模板"""
    packages: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"packages": self.packages}


def generate_workspace_template() -> WorkspaceTemplate:
    """借鉴上游 monorepo 配置生成天龙自研模板"""
    return WorkspaceTemplate(packages=DSH_OFFICIAL_WORKSPACES)


# ==============================================================================
# CLI
# ==============================================================================

def cmd_parse_patch(args: argparse.Namespace) -> int:
    """解析 cordis patch + 校验"""
    try:
        patch = parse_cordis_patch(args.yaml)
    except ValueError as e:
        print(f"[parse error] {e}", file=sys.stderr)
        return EXIT_PARSE
    issues = validate_cordis_patch(patch)
    result = {
        "insert_count": len(patch.insert),
        "inserts": patch.insert,
        "validation_issues": issues,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return EXIT_OK if not issues else EXIT_CONFIG


def cmd_check_peers(args: argparse.Namespace) -> int:
    """检查 @deepseek-ai/* peer 依赖"""
    try:
        pj = json.loads(args.package_json) if args.package_json else {}
    except json.JSONDecodeError as e:
        print(f"[parse error] {e}", file=sys.stderr)
        return EXIT_PARSE
    results = check_peers(pj)
    missing = [r for r in results if not r.in_package_json]
    print(json.dumps({
        "total_peers": len(results),
        "matched": len(results) - len(missing),
        "missing": [{"package": r.package, "note": r.note} for r in missing],
    }, indent=2, ensure_ascii=False))
    return EXIT_PEER if missing else EXIT_OK


def cmd_list_workspaces(args: argparse.Namespace) -> int:
    """列出 DSH 官方 monorepo workspaces"""
    tmpl = generate_workspace_template()
    print(json.dumps(tmpl.to_dict(), indent=2, ensure_ascii=False))
    return EXIT_OK


def cmd_check_principles(args: argparse.Namespace) -> int:
    """列出 Everything is a Plugin 5 原则"""
    print("Everything is a Plugin 5 principles:")
    for i, p in enumerate(EVERYTHING_IS_A_PLUGIN_PRINCIPLES, 1):
        print(f"  {i}. {p}")
    return EXIT_OK


def cmd_example_plugins(args: argparse.Namespace) -> int:
    """列出 6 个 example plugin 借鉴模板"""
    examples = [
        {"id": "tui-bridge",       "category": "frontend", "borrowed_from": "ccch1mneyyy/dsh-TUI"},
        {"id": "peak-gate",        "category": "traffic",  "borrowed_from": "f20880479-lab/dsh-peak-gate"},
        {"id": "balance-meter",    "category": "finance",  "borrowed_from": "Ghost011118/dsh-balance-meter"},
        {"id": "univer-office",    "category": "office",   "borrowed_from": "dream-num/dsh-univer-office"},
        {"id": "agent-teams",       "category": "multi-agent", "borrowed_from": "NanmiCoder/dsh-agent-teams"},
        {"id": "eval-bridge",      "category": "eval",     "borrowed_from": "hccccc01333/dsh-eval"},
    ]
    print(json.dumps(examples, indent=2, ensure_ascii=False))
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="deepseek_harness_bridge",
        description="Stage 50.1 deepseek-harness-bridge V1.0 · deepseek-ai/deepseek-harness MIT 借鉴档",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("parse-patch", help="解析 cordis patch YAML + 校验")
    sp.add_argument("--yaml", required=True, help="cordis.patch.yml 文本")
    sp.set_defaults(func=cmd_parse_patch)

    sp = sub.add_parser("check-peers", help="检查 7 个 @deepseek-ai/* peer")
    sp.add_argument("--package-json", required=True, help="package.json 内容")
    sp.set_defaults(func=cmd_check_peers)

    sp = sub.add_parser("list-workspaces", help="列出 DSH 官方 monorepo workspaces")
    sp.set_defaults(func=cmd_list_workspaces)

    sp = sub.add_parser("check-principles", help="列出 Everything is a Plugin 5 原则")
    sp.set_defaults(func=cmd_check_principles)

    sp = sub.add_parser("example-plugins", help="列出 6 个 example plugin 借鉴模板")
    sp.set_defaults(func=cmd_example_plugins)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
