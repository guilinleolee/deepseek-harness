#!/usr/bin/env python3
"""
n8n AI-BOM 安全扫描器
检测 n8n workflow JSON 中的15类安全漏洞
用法:
    python scanner.py scan <workflow.json>
    python scanner.py scan <workflow.json> --verbose
    python scanner.py scan <workflow.json> --min-severity high
    python scanner.py batch <dir/*.json>
    python scanner.py scan --stdin
"""
import json
import sys
import re
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

# 路径配置
SKILL_DIR = Path(__file__).parent.parent
RULES_PATH = SKILL_DIR / "detection_rules.json"


def load_rules() -> list[dict[str, Any]]:
    """加载检测规则"""
    with open(RULES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("rules", [])


def load_workflow(path: str | None = None) -> dict[str, Any]:
    """加载 workflow JSON"""
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def resolve_field(obj: Any, field: str) -> Any:
    """解析字段路径，返回值"""
    # 支持: *.parameters, nodes[].parameters.field, connections
    parts = re.split(r'\.|\[.*?\]', field)
    current = obj
    for part in parts:
        part = part.strip('.')
        if not part:
            continue
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            try:
                idx = int(part)
                current = current[idx] if 0 <= idx < len(current) else None
            except ValueError:
                current = None
        else:
            return None
        if current is None:
            return None
    return current


def match_pattern(workflow: dict[str, Any], pattern: dict[str, Any]) -> list[dict[str, Any]]:
    """在workflow中匹配单个pattern，返回匹配详情列表"""
    field = pattern.get("field", "")
    regex = pattern.get("regex", ".*")
    nested = pattern.get("nested")
    special = pattern.get("special")
    match_type = pattern.get("match_type", "pattern")

    results = []

    # 特殊检测：循环引用
    if special == "detect_cycles":
        if detect_cycles(workflow):
            results.append({
                "matched_field": field,
                "matched_value": "(cycle detected)",
                "match_type": match_type
            })
        return results

    # 特殊检测：检查废弃参数
    if special == "check_deprecated_params":
        if check_deprecated_params(workflow):
            results.append({
                "matched_field": field,
                "matched_value": "(deprecated params)",
                "match_type": match_type
            })
        return results

    # 解析字段路径，支持通配符
    if "[]" in field:
        # 数组通配符模式，如 nodes[].parameters
        base_pattern, rest = re.split(r'\[\]', field, maxsplit=1)
        rest = rest.lstrip('.')
        base_parts = base_pattern.split('.')
        nodes_obj = workflow
        for bp in base_parts:
            if isinstance(nodes_obj, dict):
                nodes_obj = nodes_obj.get(bp, [])
            else:
                break
        if isinstance(nodes_obj, list):
            for node in nodes_obj:
                rest_obj = node
                if rest:
                    for r in rest.split('.'):
                        r = r.strip()
                        if not r:
                            continue
                        rest_obj = rest_obj.get(r) if isinstance(rest_obj, dict) else None
                        if rest_obj is None:
                            break
                if rest_obj is not None:
                    val = rest_obj if isinstance(rest_obj, str) else json.dumps(rest_obj, ensure_ascii=False)
                    if re.search(regex, val, re.IGNORECASE):
                        results.append({
                            "matched_field": field,
                            "matched_value": val[:200] + "..." if len(val) > 200 else val,
                            "match_type": match_type,
                            "node": node.get("name", node.get("id", "unknown"))
                        })
    else:
        # 普通字段模式
        value = resolve_field(workflow, field)
        if value is None:
            return results

        if isinstance(value, str):
            if re.search(regex, value, re.IGNORECASE):
                results.append({
                    "matched_field": field,
                    "matched_value": value[:200] + "..." if len(value) > 200 else value,
                    "match_type": match_type
                })
        elif isinstance(value, list):
            for v in value:
                if isinstance(v, str) and re.search(regex, v, re.IGNORECASE):
                    results.append({
                        "matched_field": field,
                        "matched_value": v[:200] + "..." if len(v) > 200 else v,
                        "match_type": match_type
                    })
        elif isinstance(value, dict):
            val_str = json.dumps(value, ensure_ascii=False)
            if re.search(regex, val_str, re.IGNORECASE):
                results.append({
                    "matched_field": field,
                    "matched_value": val_str[:200] + "..." if len(val_str) > 200 else val_str,
                    "match_type": match_type
                })

    return results


def detect_cycles(workflow: dict[str, Any]) -> bool:
    """检测 workflow 中的循环引用"""
    nodes = workflow.get("nodes", [])
    connections = workflow.get("connections", {})

    # 构建邻接表
    adj = {}
    for node in nodes:
        nid = node.get("id", "")
        adj[nid] = []
    for src, conns in connections.items():
        if isinstance(conns, dict) and "main" in conns:
            for outputs in conns["main"]:
                for output in outputs:
                    tgt = output.get("node") if isinstance(output, dict) else None
                    if tgt:
                        adj[src].append(tgt)

    # DFS 检测环
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {nid: WHITE for nid in adj}

    def dfs(u: str) -> bool:
        color[u] = GRAY
        for v in adj.get(u, []):
            if color.get(v, WHITE) == GRAY:
                return True
            if color.get(v, WHITE) == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    for nid in adj:
        if color.get(nid, WHITE) == WHITE and dfs(nid):
            return True
    return False


def check_deprecated_params(workflow: dict[str, Any]) -> bool:
    """检查废弃参数"""
    nodes = workflow.get("nodes", [])
    for node in nodes:
        params = node.get("parameters", {})
        # 检查已废弃的参数名
        deprecated = ["raw", "jsonOutput", "binaryData", "includeOtherFields"]
        for key in deprecated:
            if key in params:
                return True
    return False


def scan_workflow(
    workflow: dict[str, Any],
    rules: list[dict[str, Any]],
    min_severity: str = "low"
) -> list[dict[str, Any]]:
    """扫描 workflow，返回漏洞列表"""
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    min_level = severity_order.get(min_severity, 3)

    findings = []
    for rule in rules:
        rule_id = rule["id"]
        severity = rule.get("severity", "low")
        if severity_order.get(severity, 3) < min_level:
            continue

        for pattern in rule.get("patterns", []):
            matches = match_pattern(workflow, pattern)
            for m in matches:
                findings.append({
                    "rule_id": rule_id,
                    "severity": severity,
                    "title": rule.get("title", ""),
                    "description": rule.get("description", ""),
                    "recommendation": rule.get("recommendation", ""),
                    "match_type": m.get("match_type", ""),
                    "matched_field": m.get("matched_field", ""),
                    "matched_value": m.get("matched_value", ""),
                    "node": m.get("node", ""),
                })

    # 按严重度排序
    return sorted(findings, key=lambda x: severity_order.get(x["severity"], 3))


def generate_report(
    workflow_name: str,
    findings: list[dict[str, Any]],
    total_rules: int,
    verbose: bool = False
) -> dict[str, Any]:
    """生成扫描报告"""
    summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        sev = f.get("severity", "low")
        if sev in summary:
            summary[sev] += 1

    # 构建 findings 输出
    findings_out = []
    for f in findings:
        entry = {
            "rule_id": f["rule_id"],
            "severity": f["severity"],
            "title": f["title"],
            "recommendation": f["recommendation"],
        }
        if verbose:
            entry["description"] = f["description"]
            entry["matched_field"] = f.get("matched_field", "")
            entry["matched_value"] = f.get("matched_value", "")
            entry["node"] = f.get("node", "")
            entry["match_type"] = f.get("match_type", "")
        findings_out.append(entry)

    has_critical = summary["critical"] > 0
    block_message = None
    if has_critical:
        block_message = f"发现{summary['critical']}个critical漏洞，请修复后重试"

    return {
        "workflow_name": workflow_name,
        "scan_time": datetime.now(timezone.utc).isoformat(),
        "total_rules": total_rules,
        "rules_checked": total_rules,
        "findings": findings_out,
        "summary": summary,
        "pass": not has_critical,
        "block_message": block_message
    }


def print_report(report: dict[str, Any], verbose: bool = False) -> None:
    """打印扫描报告到控制台"""
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"🔍 AI-BOM 安全扫描报告: {report['workflow_name']}")
    print(f"⏰ 扫描时间: {report['scan_time']}")
    print(f"📊 规则总数: {report['total_rules']}  |  已检测: {report['rules_checked']}")
    print(sep)

    summary = report["summary"]
    sev_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}

    print(f"\n📈 漏洞统计:")
    for sev in ["critical", "high", "medium", "low"]:
        count = summary.get(sev, 0)
        emoji = sev_emoji.get(sev, "⚪")
        print(f"   {emoji} {sev.upper():8s}: {count:3d} 个")

    findings = report["findings"]
    if findings:
        print(f"\n🚨 发现 {len(findings)} 个漏洞:")
        current_sev = None
        for f in findings:
            sev = f["severity"]
            if sev != current_sev:
                print(f"\n   {'─' * 60}")
                current_sev = sev
            print(f"   {sev_emoji.get(sev, '⚪')} [{f['rule_id']}] {f['title']}")
            if verbose:
                if f.get("node"):
                    print(f"      节点: {f['node']}")
                if f.get("matched_field"):
                    print(f"      字段: {f['matched_field']}")
                if f.get("matched_value"):
                    val = f["matched_value"].replace('\n', ' ')[:100]
                    print(f"      匹配: {val}...")
                print(f"      建议: {f['recommendation']}")
    else:
        print(f"\n✅ 未发现漏洞，workflow 安全通过!")

    print(f"\n{'=' * 70}")
    if report["pass"]:
        print(f"✅ 扫描通过 (PASS)")
    else:
        print(f"🔴 扫描阻断 (BLOCK) - {report['block_message']}")
    print(f"{'=' * 70}\n")


def scan_file(
    path: str,
    rules: list[dict[str, Any]],
    min_severity: str,
    verbose: bool
) -> dict[str, Any]:
    """扫描单个文件"""
    try:
        with open(path, encoding="utf-8") as f:
            workflow = json.load(f)
        name = workflow.get("name", Path(path).stem)
    except Exception as e:
        return {
            "file": path,
            "error": str(e),
            "pass": False
        }

    findings = scan_workflow(workflow, rules, min_severity)
    return generate_report(name, findings, len(rules), verbose)


def batch_scan(
    pattern: str,
    rules: list[dict[str, Any]],
    min_severity: str,
    verbose: bool
) -> list[dict[str, Any]]:
    """批量扫描"""
    results = []
    for p in Path().glob(pattern):
        if p.is_file() and p.suffix == ".json":
            r = scan_file(str(p), rules, min_severity, verbose)
            results.append(r)
            print_report(r, verbose) if verbose else print(
                f"  {'🔴' if not r.get('pass', True) else '✅'} {p.name}: "
                f"{sum(r.get('findings', []), [])} findings" if 'findings' in r else r.get('error', '')
            )
    return results


def main():
    parser = argparse.ArgumentParser(description="n8n AI-BOM 安全扫描器")
    sub = parser.add_subparsers(dest="cmd")

    # scan 子命令
    scan_p = sub.add_parser("scan", help="扫描单个 workflow 文件")
    scan_p.add_argument("file", nargs="?", help="workflow JSON 文件路径")
    scan_p.add_argument("--stdin", action="store_true", help="从 stdin 读取")
    scan_p.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    scan_p.add_argument("--min-severity", default="low",
                       choices=["critical", "high", "medium", "low"],
                       help="最小严重度阈值")
    scan_p.add_argument("--format", default="text",
                       choices=["text", "json"],
                       help="输出格式")

    # batch 子命令
    batch_p = sub.add_parser("batch", help="批量扫描")
    batch_p.add_argument("pattern", help="文件匹配模式，如 workflows/*.json")
    batch_p.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    batch_p.add_argument("--min-severity", default="low",
                        choices=["critical", "high", "medium", "low"],
                        help="最小严重度阈值")

    args = parser.parse_args()
    rules = load_rules()

    if args.cmd == "scan":
        workflow = load_workflow(args.file if not args.stdin else None) if not args.stdin or not args.file else load_workflow(args.file)
        if args.stdin and not args.file:
            workflow = json.load(sys.stdin)
        elif args.file:
            workflow = load_workflow(args.file)

        findings = scan_workflow(workflow, rules, args.min_severity)
        name = workflow.get("name", args.file or "stdin")
        report = generate_report(name, findings, len(rules), args.verbose)

        if args.format == "json":
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print_report(report, args.verbose)

        # 退出码：critical 漏洞 -> 2, 其他漏洞 -> 1, 无漏洞 -> 0
        if report["summary"]["critical"] > 0:
            sys.exit(2)
        elif sum(report["summary"].values()) > 0:
            sys.exit(1)
        sys.exit(0)

    elif args.cmd == "batch":
        print(f"\n📦 批量扫描: {args.pattern}")
        results = batch_scan(args.pattern, rules, args.min_severity, args.verbose)
        total = len(results)
        passed = sum(1 for r in results if r.get("pass", False))
        failed = sum(1 for r in results if not r.get("pass", True) and "error" not in r)
        errors = sum(1 for r in results if "error" in r)
        print(f"\n📊 批量扫描汇总: {passed}/{total} 通过, {failed} 失败, {errors} 错误")
        sys.exit(2 if failed > 0 else 0)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
