#!/usr/bin/env python3
"""
冲突检测器 - Role Conflict Detector
检测天龙引擎内部的角色职责重叠或冲突
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))
from identity_auditor import load_config, load_agent_definitions


def load_known_conflicts() -> list[dict[str, Any]]:
    """加载已知冲突矩阵"""
    config = load_config()
    return config.get("conflict_detection", {}).get("known_conflicts", [])


def load_all_agent_definitions() -> dict[str, Any]:
    """加载所有Agent定义"""
    agents_dir = Path.home() / ".claude" / "agents"
    agents = {}
    if agents_dir.exists():
        for agent_file in agents_dir.glob("*.md"):
            agent_id = agent_file.stem
            content = agent_file.read_text(encoding="utf-8")
            agents[agent_id] = content
    return agents


def extract_keywords(content: str) -> set[str]:
    """从Agent定义中提取关键词"""
    keywords = set()
    lines = content.split("\n")
    in_keywords = False

    for line in lines:
        line = line.strip().lower()
        if "keyword" in line or "触发" in line or "trigger" in line:
            in_keywords = True
            continue
        if in_keywords:
            if line.startswith("-") or line.startswith("*"):
                keyword = line.lstrip("-* ").strip()
                if keyword:
                    keywords.add(keyword)
            elif line and not line.startswith("-"):
                in_keywords = False

    return keywords


def extract_role_info(content: str) -> dict[str, str]:
    """提取角色信息"""
    info = {
        "primary": "",
        "department": "",
        "can_do": [],
        "cannot_do": [],
    }

    lines = content.split("\n")
    section = None

    for line in lines:
        line_lower = line.lower().strip()

        if "##" in line and not line_lower.startswith("## #"):
            section = line_lower.strip("# ").strip()
            continue

        if section in ["role", "角色", "职责"]:
            if line.strip().startswith("-"):
                text = line.strip().lstrip("- ")
                if "primary" in line_lower or info["primary"]:
                    if not info["primary"]:
                        info["primary"] = text
            elif "primary:" in line_lower:
                info["primary"] = line.split(":", 1)[1].strip()

        if section in ["capabilities", "能力", "can_do"]:
            if line.strip().startswith("-"):
                info["can_do"].append(line.strip().lstrip("- ").strip())

        if section in ["boundary", "边界", "cannot_do"]:
            if line.strip().startswith("-"):
                info["cannot_do"].append(line.strip().lstrip("- ").strip())

    return info


def detect_keyword_overlap(agents: dict[str, str]) -> list[dict[str, Any]]:
    """检测关键词重叠"""
    overlaps = []
    agent_keywords = {}

    for agent_id, content in agents.items():
        agent_keywords[agent_id] = extract_keywords(content)

    agent_ids = list(agent_keywords.keys())
    for i, agent_a in enumerate(agent_ids):
        for agent_b in agent_ids[i + 1:]:
            common = agent_keywords[agent_a] & agent_keywords[agent_b]
            if len(common) >= 3:
                overlaps.append({
                    "type": "keyword_overlap",
                    "agent_a": agent_a,
                    "agent_b": agent_b,
                    "common_keywords": list(common),
                    "count": len(common),
                    "severity": "high" if len(common) >= 5 else "medium",
                })

    return overlaps


def detect_capability_overlap(agents: dict[str, str]) -> list[dict[str, Any]]:
    """检测能力重叠"""
    overlaps = []
    agent_capabilities = {}

    for agent_id, content in agents.items():
        info = extract_role_info(content)
        agent_capabilities[agent_id] = set(info.get("can_do", []))

    agent_ids = list(agent_capabilities.keys())
    for i, agent_a in enumerate(agent_ids):
        for agent_b in agent_ids[i + 1:]:
            common = agent_capabilities[agent_a] & agent_capabilities[agent_b]
            if len(common) >= 2:
                overlaps.append({
                    "type": "capability_overlap",
                    "agent_a": agent_a,
                    "agent_b": agent_b,
                    "common_capabilities": list(common),
                    "count": len(common),
                    "severity": "high" if len(common) >= 4 else "medium",
                })

    return overlaps


def detect_circular_dependencies(agents: dict[str, str]) -> list[dict[str, Any]]:
    """检测循环依赖"""
    # 简化实现：检测 A->B->C->A 模式
    circular = []

    for agent_id, content in agents.items():
        if "upstream" in content.lower() or "下游" in content:
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "upstream" in line.lower() or "下游" in line:
                    for j in range(i, min(i + 20, len(lines))):
                        if j > i and ("downstream" in lines[j].lower() or "上游" in lines[j]):
                            circular.append({
                                "type": "potential_circular",
                                "agent": agent_id,
                                "line_start": i,
                                "line_end": j,
                                "description": "可能存在循环依赖",
                            })

    return circular


def check_known_conflicts(agents: dict[str, str]) -> list[dict[str, Any]]:
    """检查已知冲突矩阵中的冲突"""
    conflicts_found = []
    known_conflicts = load_known_conflicts()

    for conflict in known_conflicts:
        agent_a = conflict.get("agent_a", "").replace("-", "_")
        agent_b = conflict.get("agent_b", "").replace("-", "_")

        has_a = any(agent_a in id or id in agent_a for id in agents.keys())
        has_b = any(agent_b in id or id in agent_b for id in agents.keys())

        if has_a and has_b:
            conflicts_found.append({
                **conflict,
                "detected": True,
            })

    return conflicts_found


def generate_conflict_report(
    known: list[dict[str, Any]],
    keyword_overlaps: list[dict[str, Any]],
    capability_overlaps: list[dict[str, Any]],
    circular: list[dict[str, Any]],
    output_format: str = "markdown",
) -> str:
    """生成冲突报告"""
    if output_format == "json":
        return json.dumps({
            "known_conflicts": known,
            "keyword_overlaps": keyword_overlaps,
            "capability_overlaps": capability_overlaps,
            "circular_dependencies": circular,
        }, ensure_ascii=False, indent=2)

    lines = []
    lines.append("# 天龙引擎角色冲突检测报告\n")
    lines.append("## 已知冲突矩阵\n")

    if known:
        for c in known:
            lines.append(f"### {c.get('agent_a')} ↔ {c.get('agent_b')}")
            lines.append(f"- **类型**: {c.get('type', 'unknown')}")
            lines.append(f"- **描述**: {c.get('description', 'N/A')}")
            lines.append(f"- **解决方案**: {c.get('resolution', 'N/A')}")
            lines.append("")
    else:
        lines.append("✅ 未检测到已知冲突\n\n")

    if keyword_overlaps:
        lines.append("## 关键词重叠检测\n")
        lines.append("> 警告：多个Agent使用相同的触发关键词\n\n")
        for o in keyword_overlaps:
            severity = "🔴" if o["severity"] == "high" else "🟡"
            lines.append(f"{severity} **{o['agent_a']}** ↔ **{o['agent_b']}**")
            lines.append(f"   共同关键词: {', '.join(o['common_keywords'][:5])}")
            lines.append("")
    else:
        lines.append("## 关键词重叠检测\n")
        lines.append("✅ 未检测到显著的关键词重叠\n\n")

    if capability_overlaps:
        lines.append("## 能力重叠检测\n")
        lines.append("> 警告：多个Agent具有相同的能力范围\n\n")
        for o in capability_overlaps:
            severity = "🔴" if o["severity"] == "high" else "🟡"
            lines.append(f"{severity} **{o['agent_a']}** ↔ **{o['agent_b']}**")
            lines.append(f"   共同能力: {', '.join(o['common_capabilities'][:3])}")
            lines.append("")
    else:
        lines.append("## 能力重叠检测\n")
        lines.append("✅ 未检测到显著的能力重叠\n\n")

    if circular:
        lines.append("## 循环依赖检测\n")
        lines.append("> ⚠️ 可能存在循环依赖风险\n\n")
        for c in circular:
            lines.append(f"⚠️ **{c['agent']}** (行 {c['line_start']}-{c['line_end']})")
            lines.append(f"   {c['description']}")
            lines.append("")
    else:
        lines.append("## 循环依赖检测\n")
        lines.append("✅ 未检测到循环依赖\n\n")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="天龙引擎角色冲突检测器")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown", help="输出格式")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--check-known", action="store_true", help="仅检查已知冲突")
    parser.add_argument("--auto-detect", action="store_true", help="自动检测所有冲突类型")

    args = parser.parse_args()

    print("🔍 正在加载天龙引擎Agent定义...")

    agents = load_all_agent_definitions()
    if not agents:
        print("⚠️ 未找到Agent定义文件，跳过自动检测")
        auto_detect = []
    else:
        print(f"📋 已加载 {len(agents)} 个Agent定义")

        if args.check_known:
            auto_detect = []
        else:
            auto_detect = args.auto_detect

    known = check_known_conflicts(agents) if agents else []

    keyword_overlaps = []
    capability_overlaps = []
    circular = []

    if auto_detect and agents:
        print("🔍 正在进行关键词重叠检测...")
        keyword_overlaps = detect_keyword_overlap(agents)

        print("🔍 正在进行能力重叠检测...")
        capability_overlaps = detect_capability_overlap(agents)

        print("🔍 正在进行循环依赖检测...")
        circular = detect_circular_dependencies(agents)

    report = generate_conflict_report(
        known,
        keyword_overlaps,
        capability_overlaps,
        circular,
        args.format,
    )

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"✅ 冲突报告已保存到 {args.output}")
    else:
        print(report)

    total = len(known) + len(keyword_overlaps) + len(capability_overlaps) + len(circular)
    if total > 0:
        print(f"\n📊 检测到 {total} 个潜在冲突/重叠")
        return 1
    else:
        print("\n✅ 未检测到冲突")
        return 0


if __name__ == "__main__":
    sys.exit(main())
