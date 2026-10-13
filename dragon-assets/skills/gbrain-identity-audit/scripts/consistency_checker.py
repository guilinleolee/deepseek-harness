#!/usr/bin/env python3
"""
一致性检查器 - Consistency Checker
验证Agent身份配置的一致性：文档vs配置、配置vs行为、自我认知vs实际能力
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))
from identity_auditor import load_config


def load_identity_config(agent_id: str) -> dict[str, Any] | None:
    """加载Agent身份配置"""
    config_dir = Path(__file__).parent.parent / "identity-configs"
    config_file = config_dir / f"{agent_id}.yaml"

    if not config_file.exists():
        return None

    try:
        import yaml
        with open(config_file, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def load_agent_definition(agent_id: str) -> str | None:
    """加载Agent定义文档"""
    agents_dir = Path.home() / ".claude" / "agents"

    patterns = [
        agent_id,
        agent_id.replace("-", "_"),
        agent_id.replace("_", "-"),
    ]

    for pattern in patterns:
        md_file = agents_dir / f"{pattern}.md"
        if md_file.exists():
            return md_file.read_text(encoding="utf-8")

    return None


def check_doc_vs_config(agent_id: str, doc: str, config: dict[str, Any]) -> list[dict[str, Any]]:
    """检查文档与配置一致性"""
    issues = []

    # 提取文档中的角色信息
    doc_role = re.search(r"role[:\s]+([^\n]+)", doc, re.IGNORECASE)
    doc_keywords = re.findall(r"keyword[s]?[:\s]+([^\n]+)", doc, re.IGNORECASE)

    # 与配置对比
    config_role = config.get("identity", {}).get("role", {}).get("primary", "")
    config_keywords = config.get("identity", {}).get("role", {}).get("keywords", [])

    if doc_role and config_role:
        if doc_role.group(1).strip() != config_role:
            issues.append({
                "type": "doc_vs_config",
                "category": "role_mismatch",
                "severity": "error",
                "description": f"角色定义不一致: 文档='{doc_role.group(1).strip()}' vs 配置='{config_role}'",
                "recommendation": "统一角色定义，确保文档与配置同步",
            })

    if doc_keywords and config_keywords:
        doc_kw_set = set(k.strip().lower() for k in doc_keywords)
        config_kw_set = set(k.lower() for k in config_keywords)
        missing = config_kw_set - doc_kw_set

        if missing:
            issues.append({
                "type": "doc_vs_config",
                "category": "keywords_missing",
                "severity": "warn",
                "description": f"文档中缺少配置中的关键词: {', '.join(missing)}",
                "recommendation": "在Agent文档中添加缺失的触发关键词",
            })

    return issues


def check_config_structure(config: dict[str, Any]) -> list[dict[str, Any]]:
    """检查配置结构完整性"""
    issues = []
    identity = config.get("identity", {})

    required_sections = ["agent_id", "name", "role", "capabilities", "collaboration"]
    for section in required_sections:
        if section not in identity:
            issues.append({
                "type": "config_structure",
                "category": "missing_section",
                "severity": "error",
                "description": f"配置缺少必需字段: {section}",
                "recommendation": f"在identity配置中添加 {section} 字段",
            })

    # 检查能力边界
    capabilities = identity.get("capabilities", {})
    if "can_do" not in capabilities:
        issues.append({
            "type": "config_structure",
            "category": "missing_boundary",
            "severity": "error",
            "description": "配置缺少 can_do 字段",
            "recommendation": "定义Agent能够执行的能力范围",
        })

    if "cannot_do" not in capabilities:
        issues.append({
            "type": "config_structure",
            "category": "missing_boundary",
            "severity": "warn",
            "description": "配置缺少 cannot_do 字段",
            "recommendation": "明确Agent不能执行的能力边界",
        })

    # 检查协作接口
    collaboration = identity.get("collaboration", {})
    if "upstream" not in collaboration:
        issues.append({
            "type": "config_structure",
            "category": "missing_interface",
            "severity": "warn",
            "description": "配置缺少 upstream 字段（上游接口）",
            "recommendation": "定义哪些Agent会调用此Agent",
        })

    if "downstream" not in collaboration:
        issues.append({
            "type": "config_structure",
            "category": "missing_interface",
            "severity": "warn",
            "description": "配置缺少 downstream 字段（下游接口）",
            "recommendation": "定义此Agent会调用哪些Agent",
        })

    return issues


def check_boundary_consistency(capabilities: dict[str, Any]) -> list[dict[str, Any]]:
    """检查能力边界一致性"""
    issues = []

    can_do = capabilities.get("can_do", [])
    cannot_do = capabilities.get("cannot_do", [])

    # 检查是否有重叠
    can_do_set = set(c.lower() for c in can_do)
    cannot_do_set = set(c.lower() for c in cannot_do)
    overlap = can_do_set & cannot_do_set

    if overlap:
        issues.append({
            "type": "boundary_consistency",
            "category": "can_cannot_overlap",
            "severity": "error",
            "description": f"can_do 和 cannot_do 存在重叠: {', '.join(overlap)}",
            "recommendation": "确保 can_do 和 cannot_do 是互斥的",
        })

    # 检查禁止事项
    prohibitions = capabilities.get("prohibitions", [])
    if not prohibitions:
        issues.append({
            "type": "boundary_consistency",
            "category": "missing_prohibitions",
            "severity": "warn",
            "description": "配置缺少 prohibitions 字段",
            "recommendation": "定义Agent的安全禁止事项",
        })

    return issues


def check_self_vs_ability(doc: str, config: dict[str, Any]) -> list[dict[str, Any]]:
    """检查自我认知与实际能力一致性"""
    issues = []

    # 从文档中提取自我描述
    doc_lines = doc.split("\n")
    doc_claims = []

    for line in doc_lines:
        if any(word in line.lower() for word in ["i can", "i am", "i will", "able to", "capable"]):
            doc_claims.append(line.strip())

    capabilities = config.get("identity", {}).get("capabilities", {})
    can_do = [c.lower() for c in capabilities.get("can_do", [])]

    # 检查声称但未配置的能力
    for claim in doc_claims[:5]:  # 只检查前5个声称
        claim_lower = claim.lower()
        matched = any(ability in claim_lower for ability in can_do)

        if not matched and len(can_do) > 0:
            issues.append({
                "type": "self_vs_ability",
                "category": "unclaimed_capability",
                "severity": "warn",
                "description": f"文档声称但未在配置中声明: {claim[:80]}...",
                "recommendation": "在can_do中添加此能力或修正文档描述",
            })

    return issues


def run_consistency_check(agent_id: str) -> dict[str, Any]:
    """对单个Agent执行一致性检查"""
    result = {
        "agent_id": agent_id,
        "status": "unknown",
        "issues": [],
        "warnings": 0,
        "errors": 0,
    }

    config = load_identity_config(agent_id)
    doc = load_agent_definition(agent_id)

    if not config:
        result["status"] = "no_config"
        result["issues"].append({
            "type": "missing",
            "category": "no_identity_config",
            "severity": "error",
            "description": f"未找到 {agent_id} 的身份配置文件",
            "recommendation": "运行 'identity_auditor.py generate --agent {agent_id}' 生成配置",
        })
        result["errors"] += 1
        return result

    if doc:
        # 文档vs配置
        result["issues"].extend(check_doc_vs_config(agent_id, doc, config))

    # 配置结构
    result["issues"].extend(check_config_structure(config))

    # 边界一致性
    capabilities = config.get("identity", {}).get("capabilities", {})
    result["issues"].extend(check_boundary_consistency(capabilities))

    # 自我认知vs能力
    if doc:
        result["issues"].extend(check_self_vs_ability(doc, config))

    # 统计
    result["warnings"] = sum(1 for i in result["issues"] if i["severity"] == "warn")
    result["errors"] = sum(1 for i in result["issues"] if i["severity"] == "error")
    result["status"] = "passed" if result["errors"] == 0 else "failed"

    return result


def generate_check_report(results: list[dict[str, Any]], format: str = "markdown") -> str:
    """生成一致性检查报告"""
    total_agents = len(results)
    total_errors = sum(r["errors"] for r in results)
    total_warnings = sum(r["warnings"] for r in results)
    passed = sum(1 for r in results if r["status"] == "passed")

    if format == "json":
        return json.dumps({
            "summary": {
                "total_agents": total_agents,
                "passed": passed,
                "failed": total_agents - passed,
                "total_errors": total_errors,
                "total_warnings": total_warnings,
            },
            "results": results,
        }, ensure_ascii=False, indent=2)

    lines = []
    lines.append("# 天龙引擎一致性检查报告\n")
    lines.append("## 总体统计\n")
    lines.append(f"- **Agent总数**: {total_agents}")
    lines.append(f"- **通过**: {passed} ({passed / total_agents * 100:.1f}%)")
    lines.append(f"- **失败**: {total_agents - passed}")
    lines.append(f"- **错误数**: {total_errors}")
    lines.append(f"- **警告数**: {total_warnings}")
    lines.append("")

    for result in results:
        lines.append(f"## {result['agent_id']}\n")
        status_icon = "✅" if result["status"] == "passed" else "❌"
        lines.append(f"{status_icon} 状态: **{result['status']}**\n")

        if result["issues"]:
            lines.append("### 发现的问题\n")
            for issue in result["issues"]:
                severity = "🔴" if issue["severity"] == "error" else "🟡"
                lines.append(f"{severity} **[{issue['type']}]** {issue['description']}")
                lines.append(f"   建议: {issue['recommendation']}\n")
        else:
            lines.append("✅ 未发现问题\n")

        lines.append("---\n")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="天龙引擎一致性检查器")
    parser.add_argument("--agent", "-a", help="指定Agent ID")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown", help="输出格式")
    parser.add_argument("--output", "-o", help="输出文件路径")

    args = parser.parse_args()

    if args.agent:
        print(f"🔍 检查 {args.agent} 的一致性...")
        results = [run_consistency_check(args.agent)]
    else:
        print("🔍 检查所有Agent的一致性...")
        config = load_config()
        scope = config.get("identity_audit", {}).get("scope", {})
        departments = scope.get("departments", [])

        all_agents = []
        for dept in departments:
            all_agents.extend(dept.get("agents", []))

        results = []
        for agent_id in all_agents[:10]:  # 限制检查数量
            results.append(run_consistency_check(agent_id))

    report = generate_check_report(results, args.format)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"✅ 一致性检查报告已保存到 {args.output}")
    else:
        print(report)

    total_errors = sum(r["errors"] for r in results)
    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
