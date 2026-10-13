#!/usr/bin/env python3
"""
Quality Gate Checker - 5层质量门控检查器
GEO内容质量门控验证系统
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 配置路径
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
BACKLOG_FILE = DATA_DIR / "backlog.json"

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_backlog() -> dict:
    """加载backlog数据"""
    if BACKLOG_FILE.exists():
        with open(BACKLOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tasks": [], "version": "1.0", "updated_at": datetime.now().isoformat()}


def get_task(task_id: str) -> Optional[dict]:
    """获取任务"""
    backlog = load_backlog()
    for task in backlog["tasks"]:
        if task["task_id"] == task_id:
            return task
    return None


def count_words(text: str) -> int:
    """统计中英文混合文本字数"""
    # 中文字符
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    # 英文单词
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    # 其他字符（标点等）不计入
    return chinese_chars + english_words


def check_l1_fact_check(content: str) -> dict:
    """
    L1: 事实核查
    检查数据准确性、来源可靠性
    """
    issues = []
    suggestions = []

    # 检查是否有来源标注
    has_citations = bool(re.search(r'\[.*?\]\(.*?\)', content))  # Markdown链接格式
    has_number_markers = bool(re.search(r'\[\d+\]', content))  # 数字引用

    if not (has_citations or has_number_markers):
        issues.append("缺少引用标注")

    # 检查是否有具体数据
    has_numbers = bool(re.search(r'\d+%|\d+倍|\$\d+', content))
    if has_numbers:
        # 检查数字后是否有说明
        numbers = re.findall(r'\d+%|\d+倍|\$\d+', content)
        for num in numbers:
            # 简单检查：如果数字单独出现，可能缺少上下文
            if num in content:
                idx = content.index(num)
                # 检查前后是否有文字说明
                before = content[max(0, idx-20):idx]
                after = content[idx+len(num):idx+len(num)+20]
                if not (before.strip() or after.strip()):
                    issues.append(f"数据'{num}'缺少上下文说明")

    # 统计引用数量
    citation_count = len(re.findall(r'\[.*?\]\(.*?\)', content))
    citation_count += len(re.findall(r'\[\d+\]', content))

    score = 1.0 if citation_count >= 5 and not issues else 0.5 if citation_count >= 2 else 0.0

    return {
        "passed": len(issues) == 0 and score >= 0.8,
        "score": score,
        "issues": issues,
        "suggestions": suggestions if not issues else ["添加至少5个引用", "确保每个数据点有来源支撑"],
        "citation_count": citation_count
    }


def check_l2_citation_quality(content: str) -> dict:
    """
    L2: 引用质量
    检查来源权威性、引用格式
    """
    issues = []
    suggestions = []

    # 检查引用格式
    markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    number_refs = re.findall(r'\[\d+\]', content)

    # 分析域名来源
    domains = []
    for text, url in markdown_links:
        if url.startswith('http'):
            domain_match = re.search(r'://([^/]+)', url)
            if domain_match:
                domains.append(domain_match.group(1))

    # 权威域名检查
    authority_domains = [
        'nature.com', 'science.org', 'arxiv.org',  # 学术
        'mckinsey.com', 'bain.com', 'bcg.com',  # 咨询
        'forbes.com', 'hbr.org', 'economist.com',  # 商业媒体
        'who.int', 'cdc.gov', 'nature.com',  # 官方
        'github.com', 'stackoverflow.com'  # 技术
    ]

    high_authority_count = sum(1 for d in domains if any(a in d for a in authority_domains))

    # 引用数量检查
    total_citations = len(markdown_links) + len(number_refs)

    if total_citations < 5:
        issues.append(f"引用数量不足: {total_citations}/5")
        suggestions.append("确保至少5个引用")

    authority_ratio = high_authority_count / max(total_citations, 1)
    if authority_ratio < 0.3:
        issues.append(f"权威来源比例过低: {authority_ratio:.0%}/30%")
        suggestions.append("优先使用学术、官方、权威媒体来源")

    score = 1.0 if authority_ratio >= 0.3 and total_citations >= 5 else 0.5 if total_citations >= 2 else 0.0

    return {
        "passed": len(issues) == 0 and score >= 0.7,
        "score": score,
        "issues": issues,
        "suggestions": suggestions,
        "total_citations": total_citations,
        "authority_ratio": authority_ratio
    }


def check_l3_structure(content: str) -> dict:
    """
    L3: 结构化
    检查段落长度、标题层级、决策树、收敛总结
    """
    issues = []
    suggestions = []

    # 段落分析
    paragraphs = re.split(r'\n\n+', content)
    paragraphs = [p.strip() for p in paragraphs if p.strip() and len(p) > 50]

    paragraph_lengths = [count_words(p) for p in paragraphs]

    # 检查段落长度是否在134-167词范围内
    out_of_range = [l for l in paragraph_lengths if l < 100 or l > 200]
    if len(out_of_range) > len(paragraph_lengths) * 0.3:
        issues.append(f"段落长度偏差较大: {len(out_of_range)}/{len(paragraph_lengths)}个段落超出推荐范围")
        suggestions.append("保持段落长度在134-167词范围内")

    # 检查标题层级
    h2_count = len(re.findall(r'^#{2}\s', content, re.MULTILINE))
    h3_count = len(re.findall(r'^#{3}\s', content, re.MULTILINE))

    if h2_count < 3:
        issues.append(f"H2标题不足: {h2_count}/3")
        suggestions.append("使用H2划分主要章节")

    # 检查是否包含决策树
    has_decision_tree = bool(re.search(r'If\s+.+?\s+→\s+.+?', content, re.IGNORECASE))
    has_decision_frame = bool(re.search(r'If\s+.+?\s+then\s+.+?', content, re.IGNORECASE))

    if not (has_decision_tree or has_decision_frame):
        issues.append("缺少决策框架")
        suggestions.append("添加 If X -> Choose Y 格式的决策树")

    # 检查是否包含收敛总结
    has_convergence = bool(re.search(r'If You Only Remember One Thing', content, re.IGNORECASE))
    has_summary = bool(re.search(r'总结|结论|一句话', content[-500:]))  # 在最后500字内查找

    if not has_convergence:
        issues.append("缺少收敛性总结")
        suggestions.append("添加 'If You Only Remember One Thing' 总结块")

    # 检查是否包含对比表格
    has_table = bool(re.findall(r'\|.+\|.+\|', content))

    score = 0.0
    if h2_count >= 3:
        score += 0.25
    if has_decision_tree or has_decision_frame:
        score += 0.25
    if has_convergence:
        score += 0.25
    if has_table:
        score += 0.25

    return {
        "passed": len(issues) == 0 and score >= 0.75,
        "score": score,
        "issues": issues,
        "suggestions": suggestions,
        "h2_count": h2_count,
        "has_decision_tree": has_decision_tree or has_decision_frame,
        "has_convergence": has_convergence,
        "has_table": has_table
    }


def check_l4_entity_clarity(content: str) -> dict:
    """
    L4: 实体清晰度
    检查读者画像、Hook、承诺、决策框架
    """
    issues = []
    suggestions = []

    # 检查是否有Hook（反直觉观点）
    hook_patterns = [
        r'事实上',
        r'反直觉',
        r'并非',
        r'大多数人认为.*但',
        r'然而',
        r'出乎意料'
    ]
    has_hook = any(re.search(p, content[:1000]) for p in hook_patterns)

    if not has_hook:
        issues.append("缺少Hook（反直觉观点）")
        suggestions.append("在开头添加反直觉的Hook吸引读者")

    # 检查是否有明确承诺
    promise_patterns = [
        r'读完.*你将',
        r'本文.*帮你',
        r'你将.*了解',
        r'通过本文'
    ]
    has_promise = any(re.search(p, content[:2000]) for p in promise_patterns)

    if not has_promise:
        issues.append("缺少明确承诺")
        suggestions.append("在开头说明读者读完本文的收获")

    # 检查是否针对特定读者
    reader_patterns = [
        r'如果你.*应该',
        r'适合.*人群',
        r'面向',
        r'针对.*用户'
    ]
    has_reader_target = any(re.search(p, content[:1500]) for p in reader_patterns)

    # 检查实体清晰度（专业术语是否有解释）
    technical_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)  # 驼峰命名的术语
    defined_terms = re.findall(r'\b(?:叫做|称为|即|是).*?\.', content)  # 术语定义

    if len(technical_terms) > 5 and len(defined_terms) < len(technical_terms) * 0.5:
        issues.append("技术术语定义不足")

    score = 0.0
    if has_hook:
        score += 0.25
    if has_promise:
        score += 0.25
    if has_reader_target:
        score += 0.25
    if defined_terms:
        score += 0.25

    return {
        "passed": len(issues) == 0 and score >= 0.75,
        "score": score,
        "issues": issues,
        "suggestions": suggestions,
        "has_hook": has_hook,
        "has_promise": has_promise,
        "has_reader_target": has_reader_target
    }


def check_l5_human_readability(content: str) -> dict:
    """
    L5: 人类可读性
    检查AI痕迹、重复句式、模板表达
    """
    issues = []
    suggestions = []

    # AI痕迹检测 - 禁止模式
    ai_patterns = [
        (r'值得注意的是', '模板化表达'),
        (r'从上述分析可以看出', '模板化表达'),
        (r'综上所述', '模板化表达'),
        (r'毫无疑问', '模板化表达'),
        (r'首先.*其次.*最后', '模板化结构'),
        (r'换句话说', '模板化表达'),
        (r'换言之', '模板化表达'),
        (r'一方面.*另一方面', '模板化对比'),
    ]

    ai_matches = []
    for pattern, name in ai_patterns:
        matches = re.findall(pattern, content)
        if matches:
            ai_matches.append((name, len(matches)))

    if ai_matches:
        for name, count in ai_matches:
            issues.append(f"AI痕迹: {name}出现{count}次")
        suggestions.append("使用更自然的人类表达方式")

    # 检查重复句式
    sentences = re.split(r'[.!?。！？]', content)
    sentences = [s.strip() for s in sentences if s.strip()]

    # 简单检查句首重复
    sentence_starts = [s[:10] for s in sentences if len(s) > 10]
    duplicates = len(sentence_starts) - len(set(sentence_starts[:20]))  # 检查前20句

    if duplicates > 3:
        issues.append(f"句式重复: {duplicates}处")
        suggestions.append("交替使用不同句式开头")

    # 检查段落开头重复模式
    paragraph_starts = []
    paragraphs = re.split(r'\n\n+', content)
    for p in paragraphs:
        first_line = p.strip().split('\n')[0][:30] if p.strip() else ''
        if first_line:
            paragraph_starts.append(first_line)

    if len(paragraph_starts) > 3:
        unique_starts = len(set(paragraph_starts))
        if unique_starts < len(paragraph_starts) * 0.5:
            issues.append("段落开头模式重复")

    # AI分数计算
    ai_score = min(len(ai_matches) * 0.15, 0.9)
    ai_score = max(ai_score, 0.0)

    return {
        "passed": len(ai_matches) == 0 and ai_score < 0.3,
        "score": 1.0 - ai_score,
        "issues": issues,
        "suggestions": suggestions,
        "ai_pattern_count": len(ai_matches),
        "ai_score": ai_score
    }


def check_quality_gate(task_id: str, content: str = None) -> dict:
    """
    执行完整的5层质量门控检查
    """
    task = get_task(task_id)
    if not task:
        return {"success": False, "error": f"Task not found: {task_id}"}

    # 如果没有提供内容，尝试从任务中获取
    if content is None:
        content = task.get("content", "")

    if not content:
        return {"success": False, "error": "No content provided for checking"}

    results = {
        "success": True,
        "task_id": task_id,
        "overall_score": 0.0,
        "all_passed": False,
        "layers": {}
    }

    # L1: 事实核查
    l1_result = check_l1_fact_check(content)
    results["layers"]["L1_事实核查"] = l1_result

    # L2: 引用质量
    l2_result = check_l2_citation_quality(content)
    results["layers"]["L2_引用质量"] = l2_result

    # L3: 结构化
    l3_result = check_l3_structure(content)
    results["layers"]["L3_结构化"] = l3_result

    # L4: 实体清晰度
    l4_result = check_l4_entity_clarity(content)
    results["layers"]["L4_实体清晰度"] = l4_result

    # L5: 人类可读性
    l5_result = check_l5_human_readability(content)
    results["layers"]["L5_人类可读性"] = l5_result

    # 计算总体分数
    total_score = sum(r["score"] for r in results["layers"].values())
    results["overall_score"] = total_score / 5

    # 判断是否全部通过
    results["all_passed"] = all(r["passed"] for r in results["layers"].values())

    # 更新backlog中的门控状态
    update_gates(task_id, results)

    return results


def update_gates(task_id: str, results: dict) -> None:
    """更新backlog中的质量门控状态"""
    backlog = load_backlog()

    for task in backlog["tasks"]:
        if task["task_id"] == task_id:
            for gate_key, gate_result in results["layers"].items():
                gate_level = gate_key.split("_")[0]  # L1, L2, etc.
                if gate_level in task["gates"]:
                    task["gates"][gate_level]["status"] = "passed" if gate_result["passed"] else "failed"
                    task["gates"][gate_level]["passed"] = gate_result["passed"]
                    task["gates"][gate_level]["score"] = gate_result["score"]
                    task["gates"][gate_level]["notes"] = "; ".join(gate_result.get("issues", []))

            task["updated_at"] = datetime.now().isoformat()
            break

    with open(BACKLOG_FILE, "w", encoding="utf-8") as f:
        json.dump(backlog, f, ensure_ascii=False, indent=2)


def print_report(results: dict) -> None:
    """打印质量检查报告"""
    print(f"\n{'='*60}")
    print(f"📋 质量门控报告: {results['task_id']}")
    print(f"{'='*60}")

    overall = results["overall_score"]
    passed = results["all_passed"]

    print(f"\n{'✅ 全部通过' if passed else '❌ 未全部通过'} | 总体分数: {overall:.0%}")
    print("-" * 60)

    for gate_name, gate_result in results["layers"].items():
        icon = "✅" if gate_result["passed"] else "❌"
        score = gate_result["score"]

        print(f"\n{icon} {gate_name} ({score:.0%})")

        if gate_result.get("issues"):
            print("   问题:")
            for issue in gate_result["issues"]:
                print(f"   - {issue}")

        if gate_result.get("suggestions"):
            print("   建议:")
            for suggestion in gate_result["suggestions"]:
                print(f"   + {suggestion}")

    print(f"\n{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="Quality Gate Checker - GEO内容质量门控")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # check命令
    check_parser = subparsers.add_parser("check", help="执行质量门控检查")
    check_parser.add_argument("task_id", help="任务ID")
    check_parser.add_argument("--content", help="直接提供内容进行检查")

    # report命令
    report_parser = subparsers.add_parser("report", help="查看任务门控状态")
    report_parser.add_argument("task_id", help="任务ID")

    args = parser.parse_args()

    if args.command == "check":
        content = args.content
        if content is None:
            # 从文件读取
            print("请提供要检查的内容（--content），或通过以下方式：")
            print("python qc_checker.py check <task_id> --content '内容...'")
            print("或使用任务中的content字段内容")

            # 尝试从任务获取
            task = get_task(args.task_id)
            if task and task.get("content"):
                content = task.get("content")
            else:
                sys.exit(1)

        results = check_quality_gate(args.task_id, content)
        if results.get("success"):
            print_report(results)

            # 返回码：0=通过，1=未通过
            sys.exit(0 if results["all_passed"] else 1)
        else:
            print(f"❌ 检查失败: {results.get('error')}")
            sys.exit(1)

    elif args.command == "report":
        task = get_task(args.task_id)
        if task:
            print(f"\n📊 门控状态: {args.task_id}")
            print("-" * 60)

            all_passed = True
            for gate, info in task.get("gates", {}).items():
                icon = "✅" if info.get("passed") else "⬜"
                status = info.get("status", "pending")
                score = info.get("score", 0)
                notes = info.get("notes", "")

                print(f"{icon} {gate}: {status} ({score:.0%})")
                if notes:
                    print(f"   {notes}")

                if not info.get("passed"):
                    all_passed = False

            print("-" * 60)
            print(f"结论: {'✅ 全部通过' if all_passed else '❌ 存在未通过项'}")
        else:
            print(f"❌ 未找到任务: {args.task_id}")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
