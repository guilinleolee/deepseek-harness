#!/usr/bin/env python3
"""
Quality Contract Checker - GEO内容质量契约5层门控检查器
基于outputquality-contract SKILL规范实现
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ============== 配置 ==============

# AI禁止模式
AI_PROHIBITED_PATTERNS = [
    (r'值得注意的是', '模板化表达'),
    (r'从上述分析可以看出', '模板化表达'),
    (r'综上所述', '模板化表达'),
    (r'毫无疑问', '模板化表达'),
    (r'首先.*?其次.*?最后', '模板化结构'),
    (r'换句话说', '模板化表达'),
    (r'换言之', '模板化表达'),
    (r'一方面.*?另一方面', '模板化对比'),
]

# 权威域名白名单
AUTHORITY_DOMAINS = [
    # 学术
    'nature.com', 'science.org', 'arxiv.org', 'pubmed.ncbi.nlm.nih.gov',
    'ieee.org', 'acm.org', 'springer.com', 'wiley.com',
    # 咨询
    'mckinsey.com', 'bain.com', 'bcg.com', 'deloitte.com', 'pwc.com', 'ey.com', 'kpmg.com',
    # 商业媒体
    'forbes.com', 'hbr.org', 'economist.com', 'ft.com', 'bloomberg.com',
    'wsj.com', 'nytimes.com', 'techcrunch.com', 'wired.com',
    # 官方
    'who.int', 'cdc.gov', 'nih.gov', 'gov.cn', 'europa.eu',
    # 技术
    'github.com', 'stackoverflow.com', 'dev.to', 'medium.com',
    # 中文权威
    '36kr.com', 'huxiu.com', 'ifanr.com', 'pingwest.com',
    'caixin.com', 'yicai.com', 'eqingdan.com',
]

# ============== 工具函数 ==============

def count_words(text: str) -> int:
    """统计中英文混合文本字数"""
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    return chinese_chars + english_words


def count_chinese_chars(text: str) -> int:
    """统计中文字符数"""
    return len(re.findall(r'[\u4e00-\u9fff]', text))


def extract_citations(content: str) -> list:
    """提取所有引用"""
    citations = []

    # Markdown链接格式 [text](url)
    md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    for text, url in md_links:
        if url.startswith('http'):
            domain = re.search(r'://([^/]+)', url)
            citations.append({
                'type': 'markdown_link',
                'text': text,
                'url': url,
                'domain': domain.group(1) if domain else '',
                'is_authority': any(a in (domain.group(1) if domain else '') for a in AUTHORITY_DOMAINS)
            })

    # 数字引用格式 [1]
    number_refs = re.findall(r'\[\d+\]', content)
    citations.extend([{'type': 'number_ref', 'text': r} for r in number_refs])

    return citations


def is_authority_source(domain: str) -> bool:
    """检查是否为权威来源"""
    return any(a in domain for a in AUTHORITY_DOMAINS)


# ============== L1: 事实核查 ==============

def check_l1_fact_check(content: str) -> dict:
    """
    L1: 事实核查
    检查数据准确性、来源可靠性
    """
    issues = []
    suggestions = []

    # 检查引用数量
    citations = extract_citations(content)
    citation_count = len(citations)

    if citation_count < 5:
        issues.append(f"引用数量不足: {citation_count}/5")
        suggestions.append("添加至少5个引用")
    elif citation_count < 10:
        suggestions.append("优秀标准: 引用数≥10")

    # 检查数据准确性
    numbers = re.findall(r'\d+(?:\.\d+)?%|\d+(?:\.\d+)?倍|\$\d+(?:\.\d+)?', content)
    if numbers and citation_count == 0:
        issues.append("存在数据但缺少引用标注")

    # 检查是否有具体数据支撑
    has_statistics = bool(re.search(r'\d+%|\d+倍|\$\d+', content))
    has_citation_context = citation_count > 0

    if has_statistics and not has_citation_context:
        issues.append("数据缺少引用来源支撑")

    score = 1.0 if citation_count >= 10 else 0.7 if citation_count >= 5 else 0.3

    return {
        'layer': 'L1',
        'name': '事实核查',
        'passed': len(issues) == 0 and score >= 0.7,
        'score': score,
        'issues': issues,
        'suggestions': suggestions,
        'metrics': {
            'citation_count': citation_count,
            'has_statistics': has_statistics,
        }
    }


# ============== L2: 引用质量 ==============

def check_l2_citation_quality(content: str) -> dict:
    """
    L2: 引用质量
    检查来源权威性、引用格式
    """
    issues = []
    suggestions = []

    citations = extract_citations(content)
    url_citations = [c for c in citations if c['type'] == 'markdown_link']

    total_urls = len(url_citations)
    authority_count = sum(1 for c in url_citations if c.get('is_authority', False))

    if total_urls == 0:
        issues.append("缺少Markdown链接格式引用")
        suggestions.append("使用[文本](URL)格式添加引用")

    authority_ratio = authority_count / max(total_urls, 1)

    if total_urls < 5:
        issues.append(f"引用数量不足: {total_urls}/5")
    if authority_ratio < 0.3:
        issues.append(f"权威来源比例过低: {authority_ratio:.0%}/30%")
        suggestions.append("优先使用学术、官方、权威媒体来源")

    # 检查Editorial/Official/Research来源
    editorial_count = sum(1 for c in url_citations if any(
        domain in c.get('domain', '') for domain in [
            'forbes.com', 'hbr.org', 'economist.com', '36kr.com', 'huxiu.com'
        ]
    ))
    official_count = sum(1 for c in url_citations if any(
        domain in c.get('domain', '') for domain in [
            'gov.cn', 'who.int', 'cdc.gov', 'nih.gov'
        ]
    ))
    research_count = sum(1 for c in url_citations if any(
        domain in c.get('domain', '') for domain in [
            'nature.com', 'science.org', 'arxiv.org', 'ieee.org'
        ]
    ))

    suggestions.extend([
        f"Editorial来源: {editorial_count} (推荐≥2)",
        f"Official来源: {official_count} (推荐≥1)",
        f"Research来源: {research_count} (推荐≥2)",
    ])

    score = 1.0 if authority_ratio >= 0.3 and total_urls >= 10 else 0.7 if authority_ratio >= 0.3 else 0.4

    return {
        'layer': 'L2',
        'name': '引用质量',
        'passed': len(issues) == 0 and score >= 0.7,
        'score': score,
        'issues': issues,
        'suggestions': suggestions,
        'metrics': {
            'total_urls': total_urls,
            'authority_count': authority_count,
            'authority_ratio': authority_ratio,
            'editorial_count': editorial_count,
            'official_count': official_count,
            'research_count': research_count,
        }
    }


# ============== L3: 结构化 ==============

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

    # 检查段落长度分布
    in_range = sum(1 for l in paragraph_lengths if 134 <= l <= 167)
    ideal_count = sum(1 for l in paragraph_lengths if 140 <= l <= 160)

    if len(paragraph_lengths) > 0:
        range_ratio = in_range / len(paragraph_lengths)
        if range_ratio < 0.5:
            issues.append(f"段落长度达标率过低: {range_ratio:.0%} (推荐≥50%)")
            suggestions.append("保持段落长度在134-167词范围内")
    else:
        issues.append("缺少有效段落")
        suggestions.append("确保每段≥50字")

    # 检查标题层级
    h2_count = len(re.findall(r'^#{2}\s', content, re.MULTILINE))
    h3_count = len(re.findall(r'^#{3}\s', content, re.MULTILINE))

    if h2_count < 5:
        issues.append(f"H2标题不足: {h2_count}/5")
        suggestions.append("使用##划分主要章节")
    if h2_count < 7:
        suggestions.append("优秀标准: H2标题≥7")

    # 检查必须元素
    has_decision_tree = bool(re.search(r'[Ii]f\s+.+?\s*[→→]\s*.+?', content))
    has_decision_frame = bool(re.search(r'[Ii]f\s+.+?\s+[Tt]hen\s+.+?', content))

    if not (has_decision_tree or has_decision_frame):
        issues.append("缺少决策树/决策框架")
        suggestions.append("添加 If X -> Choose Y 格式的决策树")
    else:
        suggestions.append("✅ 包含决策框架")

    # 检查收敛总结
    has_convergence = bool(re.search(r'[Ii]f\s+[Yy]ou\s+[Oo]nly\s+[Rr]emember', content))
    has_summary_section = bool(re.search(r'总结|结论|关键takeaway', content[-1000:]))

    if not has_convergence:
        issues.append("缺少收敛性总结")
        suggestions.append("添加 'If You Only Remember One Thing' 总结块")
    else:
        suggestions.append("✅ 包含收敛总结")

    # 检查对比表格
    has_table = bool(re.findall(r'\|.+\|.*\|', content))
    if has_table:
        suggestions.append("✅ 包含对比表格")
    else:
        suggestions.append("建议添加对比表格增强可读性")

    score = 0.0
    if h2_count >= 5: score += 0.2
    if h2_count >= 7: score += 0.05
    if has_decision_tree or has_decision_frame: score += 0.25
    if has_convergence: score += 0.25
    if has_table: score += 0.15
    if in_range >= len(paragraph_lengths) * 0.5: score += 0.1

    return {
        'layer': 'L3',
        'name': '结构化',
        'passed': len(issues) == 0 and score >= 0.7,
        'score': score,
        'issues': issues,
        'suggestions': suggestions,
        'metrics': {
            'h2_count': h2_count,
            'h3_count': h3_count,
            'paragraph_count': len(paragraph_lengths),
            'paragraph_in_range': in_range,
            'has_decision_tree': has_decision_tree or has_decision_frame,
            'has_convergence': has_convergence,
            'has_table': has_table,
        }
    }


# ============== L4: 实体清晰 ==============

def check_l4_entity_clarity(content: str) -> dict:
    """
    L4: 实体清晰度
    检查读者画像、Hook、承诺、决策框架
    """
    issues = []
    suggestions = []

    # 检查Hook（反直觉观点）
    hook_patterns = [
        r'事实上',
        r'反直觉',
        r'并非如此',
        r'但大多数人',
        r'然而真相',
        r'出乎意料',
        r'一个常见的误区',
        r'你可能认为.*但',
    ]
    has_hook = any(re.search(p, content[:2000]) for p in hook_patterns)

    if not has_hook:
        issues.append("缺少Hook（反直觉观点）")
        suggestions.append("在开头添加反直觉的Hook吸引读者")
    else:
        suggestions.append("✅ 包含Hook")

    # 检查承诺
    promise_patterns = [
        r'读完.*你将',
        r'本文.*帮你',
        r'你将.*了解',
        r'通过本文.*你',
        r'读完这篇',
    ]
    has_promise = any(re.search(p, content[:2000]) for p in promise_patterns)

    if not has_promise:
        issues.append("缺少明确承诺")
        suggestions.append("在开头说明读者读完本文的收获")
    else:
        suggestions.append("✅ 包含承诺")

    # 检查读者画像
    reader_patterns = [
        r'如果你.*应该',
        r'适合.*人群',
        r'面向.*用户',
        r'针对.*人',
        r'这篇指南.*适用',
    ]
    has_reader = any(re.search(p, content[:2000]) for p in reader_patterns)

    if not has_reader:
        issues.append("缺少读者画像")
        suggestions.append("明确说明本文目标读者")
    else:
        suggestions.append("✅ 包含读者画像")

    # 检查术语定义
    defined_terms = re.findall(r'[\u4e00-\u9fff]*\w+[\u4e00-\u9fff]*(?:叫做|称为|即|是|：|:)\s*[^。]+。', content)
    if len(defined_terms) < 3:
        suggestions.append(f"术语定义较少({len(defined_terms)}个)，建议增加专业术语解释")

    score = 0.0
    if has_hook: score += 0.25
    if has_promise: score += 0.25
    if has_reader: score += 0.25
    if len(defined_terms) >= 3: score += 0.25

    return {
        'layer': 'L4',
        'name': '实体清晰',
        'passed': len(issues) == 0 and score >= 0.75,
        'score': score,
        'issues': issues,
        'suggestions': suggestions,
        'metrics': {
            'has_hook': has_hook,
            'has_promise': has_promise,
            'has_reader': has_reader,
            'defined_terms_count': len(defined_terms),
        }
    }


# ============== L5: 人类可读 ==============

def check_l5_human_readability(content: str) -> dict:
    """
    L5: 人类可读性
    检查AI痕迹、重复句式、模板表达
    """
    issues = []
    suggestions = []

    # AI痕迹检测
    ai_matches = []
    for pattern, name in AI_PROHIBITED_PATTERNS:
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            ai_matches.append((name, len(matches)))

    if ai_matches:
        for name, count in ai_matches:
            issues.append(f"AI痕迹: {name}出现{count}次")
        suggestions.append("使用更自然的人类表达方式")
    else:
        suggestions.append("✅ 无AI模板化表达")

    # 检查句式重复
    sentences = re.split(r'[.!?。！？]', content)
    sentences = [s.strip() for s in sentences if s.strip() and len(s) > 10]

    sentence_starts = [s[:15] for s in sentences[:20]]
    duplicates = len(sentence_starts) - len(set(sentence_starts))

    if duplicates > 5:
        issues.append(f"句式重复: {duplicates}处")
        suggestions.append("交替使用不同句式开头")

    # 检查段落开头模式
    paragraphs = re.split(r'\n\n+', content)
    paragraph_starts = []
    for p in paragraphs:
        first_line = p.strip().split('\n')[0][:30] if p.strip() else ''
        if first_line:
            paragraph_starts.append(first_line)

    if len(paragraph_starts) > 3:
        unique_starts = len(set(paragraph_starts))
        if unique_starts < len(paragraph_starts) * 0.5:
            issues.append("段落开头模式重复")
            suggestions.append("使用不同方式开篇各段落")

    # AI分数计算
    ai_score = min(len(ai_matches) * 0.15, 0.9)

    return {
        'layer': 'L5',
        'name': '人类可读',
        'passed': len(ai_matches) == 0 and ai_score < 0.3,
        'score': 1.0 - ai_score,
        'issues': issues,
        'suggestions': suggestions,
        'metrics': {
            'ai_pattern_count': len(ai_matches),
            'ai_score': ai_score,
            'sentence_duplicates': duplicates,
        }
    }


# ============== 必须元素检查 ==============

def check_must_have_elements(content: str) -> dict:
    """
    检查必须包含元素
    [not ideal when], [default recommendation], [comparison],
    [decision engine], [convergence]
    """
    issues = []
    suggestions = []

    elements = {}

    # [not ideal when]
    not_ideal_count = len(re.findall(r'\[not ideal when\]', content, re.IGNORECASE))
    elements['not_ideal_when'] = {
        'count': not_ideal_count,
        'required': 1,
        'excellent': 2,
        'passed': not_ideal_count >= 1,
        'excellent_passed': not_ideal_count >= 2,
    }
    if not_ideal_count < 1:
        issues.append("缺少[not ideal when]元素")
        suggestions.append("每个方案需包含[not ideal when]场景")
    elif not_ideal_count < 2:
        suggestions.append("优秀标准: 每个方案≥2个[not ideal when]")

    # [default recommendation]
    default_rec = bool(re.search(r'\[default recommendation\]', content, re.IGNORECASE))
    elements['default_recommendation'] = {
        'present': default_rec,
        'passed': default_rec,
    }
    if not default_rec:
        issues.append("缺少[default recommendation]元素")
        suggestions.append("必须包含1个默认推荐")

    # [comparison]
    comparison_count = len(re.findall(r'\[comparison\]', content, re.IGNORECASE))
    elements['comparison'] = {
        'count': comparison_count,
        'required': 1,
        'excellent': 2,
        'passed': comparison_count >= 1,
        'excellent_passed': comparison_count >= 2,
    }
    if comparison_count < 1:
        issues.append("缺少[comparison]元素")
        suggestions.append("必须包含正面对比")

    # [decision engine]
    decision_count = len(re.findall(r'\[decision engine\]', content, re.IGNORECASE))
    elements['decision_engine'] = {
        'count': decision_count,
        'required': 1,
        'excellent': 3,
        'passed': decision_count >= 1,
        'excellent_passed': decision_count >= 3,
    }
    if decision_count < 1:
        issues.append("缺少[decision engine]元素")
        suggestions.append("必须包含1个决策树")
    elif decision_count < 3:
        suggestions.append("优秀标准: ≥3个决策树")

    # [convergence]
    convergence_count = len(re.findall(r'\[convergence\]', content, re.IGNORECASE))
    elements['convergence'] = {
        'count': convergence_count,
        'required': 1,
        'passed': convergence_count >= 1,
    }

    # 检查收敛总结字数
    convergence_text = re.search(r'\[convergence\](.*?)(?:\n\n|$)', content, re.DOTALL)
    if convergence_text:
        conv_words = count_words(convergence_text.group(1))
        elements['convergence']['word_count'] = conv_words
        elements['convergence']['word_count_passed'] = conv_words <= 25
        if conv_words > 25:
            issues.append(f"收敛总结超过25词: {conv_words}词")
            suggestions.append("收敛总结应≤25词")
    else:
        issues.append("缺少[convergence]元素")

    all_passed = all(e.get('passed', True) for e in elements.values())

    return {
        'passed': all_passed and len(issues) == 0,
        'score': sum(1 for e in elements.values() if e.get('passed', True)) / len(elements),
        'issues': issues,
        'suggestions': suggestions,
        'elements': elements,
    }


# ============== 完整检查 ==============

def check_quality_contract(content: str, file_path: str = None) -> dict:
    """
    执行完整的质量契约检查
    """
    results = {
        'success': True,
        'file_path': file_path,
        'overall_score': 0.0,
        'all_passed': False,
        'grade': '',
        'layers': {},
        'must_have': {},
        'summary': {},
        'timestamp': datetime.now().isoformat(),
    }

    # 执行5层门控检查
    results['layers']['L1'] = check_l1_fact_check(content)
    results['layers']['L2'] = check_l2_citation_quality(content)
    results['layers']['L3'] = check_l3_structure(content)
    results['layers']['L4'] = check_l4_entity_clarity(content)
    results['layers']['L5'] = check_l5_human_readability(content)

    # 执行必须元素检查
    results['must_have'] = check_must_have_elements(content)

    # 计算总体分数
    layer_scores = [r['score'] for r in results['layers'].values()]
    results['overall_score'] = sum(layer_scores) / len(layer_scores)

    # 计算必须元素分数
    must_have_score = results['must_have']['score']

    # 综合评分
    combined_score = results['overall_score'] * 0.7 + must_have_score * 0.3

    # 评级
    all_layers_passed = all(r['passed'] for r in results['layers'].values())
    must_have_passed = results['must_have']['passed']

    results['all_passed'] = all_layers_passed and must_have_passed

    if combined_score >= 0.9 and results['all_passed']:
        results['grade'] = '🟢 A级 - 优秀'
    elif combined_score >= 0.8 and results['all_passed']:
        results['grade'] = '🟢 B级 - 良好'
    elif combined_score >= 0.7:
        results['grade'] = '🟡 C级 - 及格'
    elif combined_score >= 0.5:
        results['grade'] = '🟠 D级 - 需改进'
    else:
        results['grade'] = '🔴 F级 - 不通过'

    # 汇总摘要
    results['summary'] = {
        'total_words': count_words(content),
        'total_citations': results['layers']['L1']['metrics']['citation_count'],
        'authority_ratio': results['layers']['L2']['metrics']['authority_ratio'],
        'paragraph_count': results['layers']['L3']['metrics']['paragraph_count'],
        'ai_score': results['layers']['L5']['metrics']['ai_score'],
        'combined_score': combined_score,
        'layers_passed': sum(1 for r in results['layers'].values() if r['passed']),
        'must_have_passed': must_have_passed,
    }

    return results


def print_report(results: dict) -> None:
    """打印检查报告"""
    print("\n" + "=" * 60)
    print(f"📋 GEO内容质量契约检查报告")
    print("=" * 60)

    print(f"\n{results['grade']}")
    print(f"综合评分: {results['summary']['combined_score']:.0%}")
    print("-" * 60)

    print("\n📊 5层质量门控:")
    for layer_id, layer_result in results['layers'].items():
        icon = "✅" if layer_result['passed'] else "❌"
        score = layer_result['score']
        name = layer_result['name']

        print(f"\n{icon} {layer_id} {name} ({score:.0%})")

        if layer_result.get('issues'):
            print("   问题:")
            for issue in layer_result['issues']:
                print(f"   - {issue}")

    print("\n📌 必须元素:")
    must_have = results['must_have']
    icon = "✅" if must_have['passed'] else "❌"
    print(f"{icon} 必须元素检查 ({must_have['score']:.0%})")

    for elem_name, elem_data in must_have['elements'].items():
        elem_icon = "✅" if elem_data.get('passed', True) else "❌"
        if 'count' in elem_data:
            print(f"   {elem_icon} {elem_name}: {elem_data['count']} (要求≥{elem_data['required']})")
        else:
            print(f"   {elem_icon} {elem_name}: {'存在' if elem_data.get('present', False) else '缺失'}")

    print("\n📈 关键指标:")
    summary = results['summary']
    print(f"   总字数: {summary['total_words']}")
    print(f"   引用数: {summary['total_citations']}")
    print(f"   权威来源比例: {summary['authority_ratio']:.0%}")
    print(f"   AI痕迹分数: {summary['ai_score']:.2f} (越低越好)")

    if must_have.get('suggestions'):
        print("\n💡 建议:")
        for suggestion in must_have['suggestions']:
            if '✅' not in suggestion:
                print(f"   - {suggestion}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Quality Contract Checker - GEO内容质量契约检查")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # check命令
    check_parser = subparsers.add_parser("check", help="执行质量契约检查")
    check_parser.add_argument("--file", help="要检查的文件路径")
    check_parser.add_argument("--text", help="要检查的文本内容")
    check_parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")

    # ai-scan命令
    scan_parser = subparsers.add_parser("ai-scan", help="快速AI痕迹扫描")
    scan_parser.add_argument("--text", required=True, help="要扫描的文本内容")

    # must-have命令
    must_parser = subparsers.add_parser("must-have", help="检查必须元素")
    must_parser.add_argument("--file", help="要检查的文件路径")
    must_parser.add_argument("--text", help="要检查的文本内容")

    # report命令
    report_parser = subparsers.add_parser("report", help="生成质量报告")
    report_parser.add_argument("--file", required=True, help="要检查的文件路径")
    report_parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")

    args = parser.parse_args()

    if args.command == "check":
        content = None

        if args.file:
            file_path = Path(args.file)
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
            else:
                print(f"❌ 文件不存在: {args.file}")
                sys.exit(1)
        elif args.text:
            content = args.text
        else:
            print("❌ 请提供 --file 或 --text 参数")
            sys.exit(1)

        results = check_quality_contract(content, args.file)

        if args.format == "json":
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print_report(results)

        sys.exit(0 if results['all_passed'] else 1)

    elif args.command == "ai-scan":
        result = check_l5_human_readability(args.text)

        print(f"\n🔍 AI痕迹扫描结果")
        print("-" * 40)
        print(f"AI分数: {result['metrics']['ai_score']:.2f}")

        if result['metrics']['ai_pattern_count'] > 0:
            print("\n发现AI模式:")
            for name, count in zip([p[1] for p in AI_PROHIBITED_PATTERNS],
                                   [result['metrics']['ai_pattern_count']],
                                   strict=False):
                if count > 0:
                    print(f"  - {name}: {count}次")
        else:
            print("✅ 未发现AI模板化表达")

        sys.exit(0 if result['passed'] else 1)

    elif args.command == "must-have":
        content = None

        if args.file:
            file_path = Path(args.file)
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
            else:
                print(f"❌ 文件不存在: {args.file}")
                sys.exit(1)
        elif args.text:
            content = args.text
        else:
            print("❌ 请提供 --file 或 --text 参数")
            sys.exit(1)

        result = check_must_have_elements(content)

        print(f"\n📌 必须元素检查")
        print("-" * 40)

        for elem_name, elem_data in result['elements'].items():
            icon = "✅" if elem_data.get('passed', True) else "❌"
            if 'count' in elem_data:
                status = f"{elem_data['count']}/{elem_data['required']}"
                if elem_data.get('excellent_passed', False):
                    status += " ⭐"
            elif 'present' in elem_data:
                status = "存在" if elem_data['present'] else "缺失"
            print(f"{icon} {elem_name}: {status}")

        if result.get('issues'):
            print("\n问题:")
            for issue in result['issues']:
                print(f"  - {issue}")

        sys.exit(0 if result['passed'] else 1)

    elif args.command == "report":
        file_path = Path(args.report_file if hasattr(args, 'report_file') else args.file)

        if not file_path.exists():
            print(f"❌ 文件不存在: {args.file}")
            sys.exit(1)

        content = file_path.read_text(encoding="utf-8")
        results = check_quality_contract(content, str(file_path))

        if args.format == "json":
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print_report(results)

        sys.exit(0 if results['all_passed'] else 1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
