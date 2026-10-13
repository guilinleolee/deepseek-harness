#!/usr/bin/env python3
"""
GBrain Identity Auditor
身份审计脚本 - 实现天龙引擎Agent身份6阶段审计流程

Usage:
    python identity_auditor.py audit --agent "07-scribe"
    python identity_auditor.py audit --all
    python identity_auditor.py generate --agent "09-02"
    python identity_auditor.py detect-conflicts
    python identity_auditor.py verify --agent "07-scribe"
    python identity_auditor.py track --agent "07-scribe"
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any

# 脚本所在目录
SCRIPT_DIR = Path(__file__).parent.parent
CONFIG_PATH = SCRIPT_DIR / "config.yaml"
AGENTS_DIR = Path("c:/Users/li/.claude/agents")
SKILLS_DIR = Path("c:/Users/li/.claude/skills")
AUDIT_REPORTS_DIR = SCRIPT_DIR / "reports"
IDENTITY_CONFIGS_DIR = SCRIPT_DIR / "identity-configs"
EVOLUTION_HISTORY_DIR = SCRIPT_DIR / "evolution-history"


def load_config() -> dict[str, Any]:
    """加载审计配置"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def load_agent_definition(agent_id: str) -> dict[str, Any]:
    """加载Agent定义"""
    # 尝试多种命名格式
    possible_names = [
        f"{agent_id}.md",
        f"{agent_id.replace('-', '-')}.md",
        f"0{agent_id}.md" if agent_id.startswith("-") else None,
    ]

    for name in possible_names:
        if name:
            path = AGENTS_DIR / name
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    return {
                        "agent_id": agent_id,
                        "name": name.replace(".md", ""),
                        "content": content,
                    }

    # 尝试从SKILL.md推断
    skill_path = SKILLS_DIR / agent_id / "SKILL.md"
    if skill_path.exists():
        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
            return {
                "agent_id": agent_id,
                "name": agent_id,
                "content": content,
            }

    return {
        "agent_id": agent_id,
        "name": agent_id,
        "content": "",
        "error": "Agent definition not found",
    }


def stage1_role_definition(agent_def: dict) -> dict[str, Any]:
    """
    Stage 1: 角色定义审查
    - 核心职责定义
    - 能力范围界定
    - 汇报关系确认
    """
    content = agent_def.get("content", "")
    issues = []
    warnings = []

    # 检查主要职责
    primary_keywords = ["职责", "角色", "核心能力", "主要任务"]
    has_primary = any(kw in content for kw in primary_keywords)
    if not has_primary:
        issues.append("缺少主要职责定义")

    # 检查触发关键词
    keyword_indicators = ["关键词", "trigger", "适用场景"]
    has_keywords = any(kw in content for kw in keyword_indicators)
    if not has_keywords:
        warnings.append("缺少触发关键词定义")

    # 检查次要职责数量（应该不超过3项）
    secondary_indicators = ["次要", "辅助", "附加"]
    secondary_count = sum(1 for kw in secondary_indicators if kw in content)
    if secondary_count > 3:
        warnings.append(f"次要职责数量({secondary_count})超过3项")

    return {
        "stage": "1-role-definition",
        "status": "error" if issues else ("warn" if warnings else "pass"),
        "issues": issues,
        "warnings": warnings,
        "summary": f"角色定义{'有问题' if issues else ('有警告' if warnings else '通过')}",
    }


def stage2_capability_inventory(agent_def: dict) -> dict[str, Any]:
    """
    Stage 2: 能力盘点审查
    - 技能列表审计
    - 工具权限审计
    - 知识领域审计
    """
    content = agent_def.get("content", "")
    issues = []
    warnings = []

    # 检查SKILL引用
    skill_indicators = ["SKILL", "skill", "技能", "能力"]
    has_skills = any(kw in content for kw in skill_indicators)
    if not has_skills:
        warnings.append("缺少SKILL列表引用")

    # 检查工具权限
    tool_indicators = ["工具", "tool", "MCP", "能力"]
    has_tools = any(kw in content for kw in tool_indicators)
    if not has_tools:
        warnings.append("缺少工具权限定义")

    # 检查can_do/cannot_do边界
    can_do_indicators = ["can_do", "能做", "能力范围"]
    cannot_do_indicators = ["cannot_do", "不能做", "禁止"]
    has_can_do = any(kw in content.lower() for kw in ["can_do", "can do", "能做"])
    has_cannot_do = any(kw in content.lower() for kw in ["cannot_do", "cannot do", "不能做"])

    if not has_can_do:
        warnings.append("缺少can_do能力边界定义")
    if not has_cannot_do:
        warnings.append("缺少cannot_do禁止边界定义")

    return {
        "stage": "2-capability-inventory",
        "status": "warn" if warnings else "pass",
        "issues": issues,
        "warnings": warnings,
        "summary": f"能力盘点{'有问题' if issues else ('有警告' if warnings else '通过')}",
    }


def stage3_collaboration_interface(agent_def: dict) -> dict[str, Any]:
    """
    Stage 3: 协作接口审查
    - 上游接口（谁调用我）
    - 下游接口（我调用谁）
    - 通信协议定义
    """
    content = agent_def.get("content", "")
    issues = []
    warnings = []

    # 检查上下游接口
    upstream_indicators = ["上游", "upstream", "调用者"]
    downstream_indicators = ["下游", "downstream", "被调用"]
    has_upstream = any(kw in content for kw in upstream_indicators)
    has_downstream = any(kw in content for kw in downstream_indicators)

    if not has_upstream:
        warnings.append("缺少上游接口定义")
    if not has_downstream:
        warnings.append("缺少下游接口定义")

    # 检查天龙九部协同
    dragon_team_indicators = ["天龙", "dragon", "协同", "九部"]
    has_dragon = any(kw in content for kw in dragon_team_indicators)
    if not has_dragon:
        warnings.append("缺少天龙九部协同定义")

    return {
        "stage": "3-collaboration-interface",
        "status": "warn" if warnings else "pass",
        "issues": issues,
        "warnings": warnings,
        "summary": f"协作接口{'有问题' if issues else ('有警告' if warnings else '通过')}",
    }


def stage4_boundary_definition(agent_def: dict) -> dict[str, Any]:
    """
    Stage 4: 边界界定审查
    - 能力上限
    - 禁止事项
    - 升级路径
    """
    content = agent_def.get("content", "")
    issues = []
    warnings = []

    # 检查禁止事项
    prohibition_indicators = ["禁止", "禁止事项", "cannot", "must_not"]
    has_prohibition = any(kw in content for kw in prohibition_indicators)
    if not has_prohibition:
        warnings.append("缺少禁止事项定义")

    # 检查升级路径
    escalation_indicators = ["升级", "escalation", "升级路径", "转发"]
    has_escalation = any(kw in content for kw in escalation_indicators)
    if not has_escalation:
        warnings.append("缺少升级路径定义")

    return {
        "stage": "4-boundary-definition",
        "status": "warn" if warnings else "pass",
        "issues": issues,
        "warnings": warnings,
        "summary": f"边界界定{'有问题' if issues else ('有警告' if warnings else '通过')}",
    }


def stage5_consistency_verification(agent_def: dict) -> dict[str, Any]:
    """
    Stage 5: 一致性验证审查
    - 文档vs配置一致性
    - 配置vs行为一致性
    - 自我认知vs实际能力
    """
    content = agent_def.get("content", "")
    issues = []
    warnings = []

    # 检查版本一致性
    version_indicators = ["版本", "version", "V"]
    has_version = any(kw in content for kw in version_indicators)
    if not has_version:
        warnings.append("缺少版本定义")

    # 检查变更历史
    history_indicators = ["变更", "历史", "changelog", "版本历史"]
    has_history = any(kw in content for kw in history_indicators)
    if not has_history:
        warnings.append("缺少变更历史记录")

    return {
        "stage": "5-consistency-verification",
        "status": "warn" if warnings else "pass",
        "issues": issues,
        "warnings": warnings,
        "summary": f"一致性验证{'有问题' if issues else ('有警告' if warnings else '通过')}",
    }


def stage6_evolution_tracking(agent_def: dict) -> dict[str, Any]:
    """
    Stage 6: 演进追踪审查
    - 变更历史记录
    - 能力成长轨迹
    - 风险预警
    """
    content = agent_def.get("content", "")
    issues = []
    warnings = []

    # 检查成长指标
    growth_indicators = ["成长", "growth", "演进", "优化"]
    has_growth = any(kw in content for kw in growth_indicators)
    if not has_growth:
        warnings.append("缺少能力成长指标")

    # 检查风险预警
    risk_indicators = ["风险", "risk", "预警", "警告"]
    has_risk = any(kw in content for kw in risk_indicators)
    if not has_risk:
        warnings.append("缺少风险预警机制")

    return {
        "stage": "6-evolution-tracking",
        "status": "warn" if warnings else "pass",
        "issues": issues,
        "warnings": warnings,
        "summary": f"演进追踪{'有问题' if issues else ('有警告' if warnings else '通过')}",
    }


def run_full_audit(agent_id: str) -> dict[str, Any]:
    """
    对单个Agent执行完整的6阶段审计
    """
    agent_def = load_agent_definition(agent_id)

    stages = [
        stage1_role_definition(agent_def),
        stage2_capability_inventory(agent_def),
        stage3_collaboration_interface(agent_def),
        stage4_boundary_definition(agent_def),
        stage5_consistency_verification(agent_def),
        stage6_evolution_tracking(agent_def),
    ]

    # 汇总结果
    total_issues = sum(len(s["issues"]) for s in stages)
    total_warnings = sum(len(s["warnings"]) for s in stages)
    has_errors = any(s["status"] == "error" for s in stages)
    has_warns = any(s["status"] == "warn" for s in stages)

    return {
        "agent_id": agent_id,
        "audit_time": datetime.now().isoformat(),
        "stages": stages,
        "summary": {
            "overall_status": "error" if has_errors else ("warn" if has_warns else "pass"),
            "total_issues": total_issues,
            "total_warnings": total_warnings,
            "pass_rate": f"{(6 - sum(1 for s in stages if s['status'] != 'pass') * 100 / 6):.1f}%",
        },
    }


def generate_audit_report(audit_result: dict) -> str:
    """生成Markdown审计报告"""
    agent_id = audit_result["agent_id"]
    summary = audit_result["summary"]

    report_lines = [
        f"# {agent_id} 身份审计报告",
        "",
        f"**审计时间**: {audit_result['audit_time']}",
        f"**总体状态**: {'❌ 错误' if summary['overall_status'] == 'error' else ('⚠️ 警告' if summary['overall_status'] == 'warn' else '✅ 通过')}",
        f"**通过率**: {summary['pass_rate']}",
        f"**问题数**: {summary['total_issues']}",
        f"**警告数**: {summary['total_warnings']}",
        "",
        "---",
        "",
        "## 6阶段审计结果",
        "",
    ]

    stage_names = {
        "1-role-definition": "Stage 1: 角色定义",
        "2-capability-inventory": "Stage 2: 能力盘点",
        "3-collaboration-interface": "Stage 3: 协作接口",
        "4-boundary-definition": "Stage 4: 边界界定",
        "5-consistency-verification": "Stage 5: 一致性验证",
        "6-evolution-tracking": "Stage 6: 演进追踪",
    }

    for stage in audit_result["stages"]:
        stage_name = stage_names.get(stage["stage"], stage["stage"])
        status_icon = "❌" if stage["status"] == "error" else ("⚠️" if stage["status"] == "warn" else "✅")

        report_lines.append(f"### {status_icon} {stage_name}")
        report_lines.append(f"- **状态**: {stage['status'].upper()}")
        report_lines.append(f"- **结果**: {stage['summary']}")
        report_lines.append("")

        if stage["issues"]:
            report_lines.append("**问题列表**:")
            for issue in stage["issues"]:
                report_lines.append(f"  - 🔴 {issue}")
            report_lines.append("")

        if stage["warnings"]:
            report_lines.append("**警告列表**:")
            for warning in stage["warnings"]:
                report_lines.append(f"  - 🟡 {warning}")
            report_lines.append("")

    report_lines.append("---")
    report_lines.append("")
    report_lines.append("*由 GBrain Identity Auditor 自动生成*")

    return "\n".join(report_lines)


def save_audit_report(audit_result: dict, output_format: str = "markdown"):
    """保存审计报告"""
    AUDIT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    agent_id = audit_result["agent_id"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if output_format == "markdown":
        content = generate_audit_report(audit_result)
        report_path = AUDIT_REPORTS_DIR / f"{agent_id}_{timestamp}.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ 审计报告已保存: {report_path}")

    elif output_format == "json":
        content = json.dumps(audit_result, ensure_ascii=False, indent=2)
        report_path = AUDIT_REPORTS_DIR / f"{agent_id}_{timestamp}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ 审计报告已保存: {report_path}")

    elif output_format == "yaml":
        content = yaml.dump(audit_result, allow_unicode=True, default_flow_style=False)
        report_path = AUDIT_REPORTS_DIR / f"{agent_id}_{timestamp}.yaml"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ 审计报告已保存: {report_path}")

    return report_path


def generate_identity_config(agent_id: str) -> dict[str, Any]:
    """生成标准身份配置"""
    agent_def = load_agent_definition(agent_id)
    content = agent_def.get("content", "")

    # 提取版本信息
    version = "V1.0"
    for line in content.split("\n"):
        if "version" in line.lower() or "版本" in line:
            import re
            v_match = re.search(r"V?\d+\.\d+", line)
            if v_match:
                version = v_match.group()
                break

    config = {
        "identity": {
            "agent_id": agent_id,
            "name": agent_def.get("name", agent_id),
            "version": version,
            "audit_date": datetime.now().isoformat(),
            "role": {
                "primary": "待定义",
                "secondary": [],
                "keywords": [],
            },
            "capabilities": {
                "can_do": [],
                "cannot_do": [],
                "learning_path": [],
            },
            "collaboration": {
                "upstream": [],
                "downstream": [],
            },
            "prohibitions": [],
            "escalation": [],
        }
    }

    return config


def save_identity_config(agent_id: str):
    """保存身份配置"""
    IDENTITY_CONFIGS_DIR.mkdir(parents=True, exist_ok=True)

    config = generate_identity_config(agent_id)
    config_path = IDENTITY_CONFIGS_DIR / f"{agent_id}_identity.yaml"

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

    print(f"✅ 身份配置已生成: {config_path}")
    return config_path


def main():
    parser = argparse.ArgumentParser(description="GBrain Identity Auditor - 天龙引擎Agent身份审计")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # audit命令
    audit_parser = subparsers.add_parser("audit", help="审计Agent身份")
    audit_parser.add_argument("--agent", type=str, help="Agent编号 (如: 07-scribe)")
    audit_parser.add_argument("--all", action="store_true", help="审计全部Agent")
    audit_parser.add_argument("--format", choices=["markdown", "json", "yaml"], default="markdown", help="报告格式")

    # generate命令
    gen_parser = subparsers.add_parser("generate", help="生成身份配置")
    gen_parser.add_argument("--agent", type=str, required=True, help="Agent编号")

    # detect-conflicts命令
    subparsers.add_parser("detect-conflicts", help="检测角色冲突")

    # verify命令
    verify_parser = subparsers.add_parser("verify", help="验证一致性")
    verify_parser.add_argument("--agent", type=str, required=True, help="Agent编号")

    # track命令
    track_parser = subparsers.add_parser("track", help="追踪演进历史")
    track_parser.add_argument("--agent", type=str, required=True, help="Agent编号")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    config = load_config()
    scope = config.get("identity_audit", {}).get("scope", {})

    if args.command == "audit":
        if args.all:
            # 审计所有Agent
            all_agents = []
            for dept in scope.get("departments", []):
                all_agents.extend(dept.get("agents", []))

            print(f"📊 开始审计全部 {len(all_agents)} 个Agent...")
            print()

            results = []
            for agent_id in all_agents:
                try:
                    result = run_full_audit(agent_id)
                    results.append(result)

                    status = result["summary"]["overall_status"]
                    icon = "❌" if status == "error" else ("⚠️" if status == "warn" else "✅")
                    print(f"  {icon} {agent_id}: {result['summary']['pass_rate']}")
                except Exception as e:
                    print(f"  ❌ {agent_id}: 审计失败 - {e}")

            print()
            print(f"✅ 审计完成，共 {len(results)} 个Agent")
            print(f"📁 报告保存目录: {AUDIT_REPORTS_DIR}")

        elif args.agent:
            # 审计单个Agent
            print(f"🔍 审计Agent: {args.agent}")
            result = run_full_audit(args.agent)
            save_audit_report(result, args.format)
            print()
            print("=" * 50)
            print(result["summary"])
        else:
            print("❌ 请指定 --agent 或使用 --all")

    elif args.command == "generate":
        print(f"📝 生成身份配置: {args.agent}")
        save_identity_config(args.agent)

    elif args.command == "detect-conflicts":
        print("🔍 检测角色冲突...")
        # 导入冲突检测模块
        try:
            from conflict_detector import ConflictDetector
            detector = ConflictDetector(config)
            conflicts = detector.detect_all()
            print(f"✅ 检测完成，发现 {len(conflicts)} 个冲突")
            for conflict in conflicts:
                print(f"  - {conflict['agent_a']} vs {conflict['agent_b']}: {conflict['type']}")
        except ImportError:
            print("⚠️ 冲突检测模块未找到，使用配置文件中的已知冲突")
            known_conflicts = config.get("identity_audit", {}).get("conflict_detection", {}).get("known_conflicts", [])
            print(f"✅ 发现 {len(known_conflicts)} 个已知冲突:")
            for conflict in known_conflicts:
                print(f"  - {conflict.get('agent_a')} vs {conflict.get('agent_b')}: {conflict.get('type')}")

    elif args.command == "verify":
        print(f"✅ 验证一致性: {args.agent}")
        result = run_full_audit(args.agent)
        stage5 = next((s for s in result["stages"] if s["stage"] == "5-consistency-verification"), None)
        if stage5:
            print(f"  一致性验证: {stage5['summary']}")

    elif args.command == "track":
        print(f"📈 追踪演进历史: {args.agent}")
        EVOLUTION_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        history_file = EVOLUTION_HISTORY_DIR / f"{args.agent}_evolution.json"
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
            print(f"✅ 找到演进历史，共 {len(history.get('versions', []))} 个版本")
        else:
            print(f"⚠️ 未找到演进历史，将创建新记录")
            new_history = {
                "agent_id": args.agent,
                "created": datetime.now().isoformat(),
                "versions": [],
            }
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(new_history, f, ensure_ascii=False, indent=2)
            print(f"✅ 已创建演进历史文件: {history_file}")


if __name__ == "__main__":
    main()
