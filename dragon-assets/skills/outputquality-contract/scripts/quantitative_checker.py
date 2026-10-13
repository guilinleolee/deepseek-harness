#!/usr/bin/env python3
"""
Quantitative Checker - 量化标准检查器
检查引用数、字数、段落长度、章节数等量化指标
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# ============== 量化标准定义 ==============

@dataclass
class QuantitativeStandard:
    metric: str
    name: str
    minimum: int
    excellent: int
    unit: str
    description: str


STANDARDS = {
    'total_citations': QuantitativeStandard(
        metric='total_citations',
        name='总引用数',
        minimum=5,
        excellent=10,
        unit='个',
        description='Markdown链接和数字引用总数'
    ),
    'authority_citations': QuantitativeStandard(
        metric='authority_citations',
        name='权威来源数',
        minimum=2,
        excellent=4,
        unit='个',
        description='来自权威域名的引用'
    ),
    'official_citations': QuantitativeStandard(
        metric='official_citations',
        name='Official来源数',
        minimum=1,
        excellent=3,
        unit='个',
        description='来自.gov/.int等官方域名的引用'
    ),
    'research_citations': QuantitativeStandard(
        metric='research_citations',
        name='Research来源数',
        minimum=2,
        excellent=5,
        unit='个',
        description='来自学术域名的引用'
    ),
    'total_words': QuantitativeStandard(
        metric='total_words',
        name='总词数',
        minimum=1200,
        excellent=2000,
        unit='词',
        description='中文字符+英文单词总数'
    ),
    'paragraph_count': QuantitativeStandard(
        metric='paragraph_count',
        name='段落数',
        minimum=5,
        excellent=8,
        unit='个',
        description='有效段落数量（>50字）'
    ),
    'section_count': QuantitativeStandard(
        metric='section_count',
        name='章节数',
        minimum=5,
        excellent=7,
        unit='个',
        description='H2标题数量'
    ),
}

# 段落长度标准
PARAGRAPH_STANDARDS = {
    'minimum_length': 100,
    'ideal_min': 134,
    'ideal_max': 167,
    'excellent_min': 140,
    'excellent_max': 160,
}


# ============== 工具函数 ==============

def count_words(text: str) -> int:
    """统计中英文混合文本字数"""
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    return chinese_chars + english_words


# ============== 提取函数 ==============

def extract_citations(content: str) -> dict:
    """提取并分类所有引用"""
    citations = {
        'total': 0,
        'markdown_links': [],
        'number_refs': [],
        'authority': [],
        'official': [],
        'research': [],
        'editorial': [],
    }

    # 权威域名列表
    authority_domains = [
        'nature.com', 'science.org', 'arxiv.org', 'ieee.org', 'acm.org',
        'mckinsey.com', 'bain.com', 'bcg.com', 'deloitte.com', 'pwc.com',
        'forbes.com', 'hbr.org', 'economist.com',
    ]

    official_domains = [
        'gov.cn', 'who.int', 'cdc.gov', 'nih.gov', 'gov.uk',
        'europa.eu', 'gov.jp', 'gov.sg',
    ]

    research_domains = [
        'nature.com', 'science.org', 'arxiv.org', 'pubmed.ncbi.nlm.nih.gov',
        'ieee.org', 'acm.org', 'springer.com', 'wiley.com',
    ]

    editorial_domains = [
        'forbes.com', 'hbr.org', 'economist.com', 'bloomberg.com',
        'wsj.com', 'nytimes.com', 'techcrunch.com', 'wired.com',
        '36kr.com', 'huxiu.com', 'ifanr.com', 'pingwest.com',
    ]

    # Markdown链接格式 [text](url)
    md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    for text, url in md_links:
        if url.startswith('http'):
            citations['markdown_links'].append({'text': text, 'url': url})

            # 提取域名
            domain_match = re.search(r'://([^/]+)', url)
            domain = domain_match.group(1) if domain_match else ''

            citations['total'] += 1

            if any(d in domain for d in authority_domains):
                citations['authority'].append(domain)
            if any(d in domain for d in official_domains):
                citations['official'].append(domain)
            if any(d in domain for d in research_domains):
                citations['research'].append(domain)
            if any(d in domain for d in editorial_domains):
                citations['editorial'].append(domain)

    # 数字引用格式 [1]
    citations['number_refs'] = re.findall(r'\[\d+\]', content)
    citations['total'] += len(citations['number_refs'])

    return citations


def analyze_paragraphs(content: str) -> dict:
    """分析段落"""
    # 分割段落
    paragraphs = re.split(r'\n\n+', content)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    results = {
        'total': 0,
        'valid': [],  # >50字的段落
        'in_range': [],  # 134-167词
        'excellent': [],  # 140-160词
        'too_short': [],  # <100词
        'too_long': [],  # >200词
    }

    for i, p in enumerate(paragraphs):
        word_count = count_words(p)

        if word_count <= 50:
            continue  # 跳过太短的段落

        results['total'] += 1
        para_data = {
            'index': i,
            'word_count': word_count,
            'preview': p[:50] + '...' if len(p) > 50 else p,
        }

        results['valid'].append(para_data)

        if PARAGRAPH_STANDARDS['ideal_min'] <= word_count <= PARAGRAPH_STANDARDS['ideal_max']:
            results['in_range'].append(para_data)

        if (PARAGRAPH_STANDARDS['excellent_min'] <= word_count <=
            PARAGRAPH_STANDARDS['excellent_max']):
            results['excellent'].append(para_data)

        if word_count < PARAGRAPH_STANDARDS['minimum_length']:
            results['too_short'].append(para_data)

        if word_count > 200:
            results['too_long'].append(para_data)

    return results


def extract_sections(content: str) -> dict:
    """提取章节结构"""
    results = {
        'h2_count': 0,
        'h3_count': 0,
        'sections': [],
    }

    # H2标题
    h2_pattern = r'^#{2}\s+(.+)$'
    h2_matches = re.findall(h2_pattern, content, re.MULTILINE)
    results['h2_count'] = len(h2_matches)
    results['sections'].extend([{'level': 'h2', 'title': t} for t in h2_matches])

    # H3标题
    h3_pattern = r'^#{3}\s+(.+)$'
    h3_matches = re.findall(h3_pattern, content, re.MULTILINE)
    results['h3_count'] = len(h3_matches)
    results['sections'].extend([{'level': 'h3', 'title': t} for t in h3_matches])

    return results


# ============== 检查函数 ==============

def check_quantitative_standards(content: str) -> dict:
    """执行完整的量化标准检查"""
    results = {
        'success': True,
        'metrics': {},
        'standards': {},
        'overall_passed': True,
        'score': 0.0,
    }

    # 提取指标
    citations = extract_citations(content)
    paragraphs = analyze_paragraphs(content)
    sections = extract_sections(content)
    total_words = count_words(content)

    # 计算指标
    results['metrics'] = {
        'total_citations': citations['total'],
        'authority_citations': len(citations['authority']),
        'official_citations': len(citations['official']),
        'research_citations': len(citations['research']),
        'editorial_citations': len(citations['editorial']),
        'total_words': total_words,
        'paragraph_count': paragraphs['total'],
        'paragraph_in_range': len(paragraphs['in_range']),
        'paragraph_excellent': len(paragraphs['excellent']),
        'section_count': sections['h2_count'],
        'citation_breakdown': {
            'markdown_links': len(citations['markdown_links']),
            'number_refs': len(citations['number_refs']),
            'authority_domains': list(set(citations['authority'])),
            'official_domains': list(set(citations['official'])),
            'research_domains': list(set(citations['research'])),
        }
    }

    # 检查每项标准
    results['standards'] = {}

    for metric_name, standard in STANDARDS.items():
        value = results['metrics'].get(metric_name, 0)

        passed = value >= standard.minimum
        excellent = value >= standard.excellent

        score = 0.0
        if value >= standard.excellent:
            score = 1.0
        elif value >= standard.minimum:
            score = 0.7
        elif value >= standard.minimum * 0.5:
            score = 0.4
        else:
            score = 0.2

        results['standards'][metric_name] = {
            'name': standard.name,
            'value': value,
            'minimum': standard.minimum,
            'excellent': standard.excellent,
            'unit': standard.unit,
            'passed': passed,
            'excellent_passed': excellent,
            'score': score,
        }

        if not passed:
            results['overall_passed'] = False

    # 段落长度特殊检查
    para_ratio = len(paragraphs['in_range']) / max(paragraphs['total'], 1)
    results['standards']['paragraph_length_ratio'] = {
        'name': '段落长度达标率',
        'value': f"{para_ratio:.0%}",
        'minimum': '50%',
        'passed': para_ratio >= 0.5,
        'score': para_ratio,
    }

    if para_ratio < 0.5:
        results['overall_passed'] = False

    # 计算总分
    scores = [s['score'] for s in results['standards'].values() if 'score' in s]
    scores.append(para_ratio)
    results['score'] = sum(scores) / len(scores)

    # 汇总问题和建议
    results['issues'] = []
    results['suggestions'] = []

    for metric_name, std_result in results['standards'].items():
        if not std_result['passed']:
            results['issues'].append(
                f"{std_result['name']}: {std_result['value']}{std_result['unit']} "
                f"(要求≥{std_result['minimum']}{std_result['unit']})"
            )
            results['suggestions'].append(
                f"增加{std_result['name']}至{std_result['minimum']}{std_result['unit']}以上"
            )
        elif std_result.get('excellent_passed', False):
            results['suggestions'].append(f"✅ {std_result['name']}达到优秀标准")

    # 段落长度建议
    if paragraphs['too_short']:
        results['suggestions'].append(
            f"有{len(paragraphs['too_short'])}个段落过短(<{PARAGRAPH_STANDARDS['minimum_length']}词)"
        )

    return results


def print_quantitative_report(results: dict) -> None:
    """打印量化检查报告"""
    print("\n" + "=" * 60)
    print("📊 GEO内容量化标准检查报告")
    print("=" * 60)

    passed_count = sum(1 for s in results['standards'].values() if s['passed'])
    total_count = len(results['standards'])

    overall_icon = "✅" if results['overall_passed'] else "❌"
    print(f"\n{overall_icon} 整体状态: {'通过' if results['overall_passed'] else '未通过'}")
    print(f"评分: {results['score']:.0%}")
    print(f"通过项: {passed_count}/{total_count}")
    print("-" * 60)

    # 指标详情
    print("\n📈 指标详情:")

    for metric_name, std_result in results['standards'].items():
        icon = "✅" if std_result['passed'] else "❌"
        excellent_icon = " ⭐" if std_result.get('excellent_passed', False) else ""

        value_str = f"{std_result['value']}{std_result['unit']}"
        target_str = f"(要求≥{std_result['minimum']}{std_result['unit']}"

        print(f"\n{icon} {std_result['name']}: {value_str} {target_str}){excellent_icon}")

        if not std_result['passed']:
            suggest = std_result['minimum'] - std_result['value']
            print(f"   → 需增加{abs(suggest) if suggest < 0 else suggest}{std_result['unit']}")

    # 段落分析
    metrics = results['metrics']
    print(f"\n📝 段落分析:")
    print(f"   总段落数: {metrics['paragraph_count']}")
    print(f"   达标段落(134-167词): {metrics['paragraph_in_range']}")
    print(f"   优秀段落(140-160词): {metrics['paragraph_excellent']}")

    para_ratio = results['standards'].get('paragraph_length_ratio', {})
    if para_ratio:
        print(f"   达标率: {para_ratio.get('value', 'N/A')}")

    # 引用来源分析
    breakdown = metrics.get('citation_breakdown', {})
    if breakdown:
        print(f"\n📚 引用来源:")
        print(f"   Markdown链接: {breakdown.get('markdown_links', 0)}")
        print(f"   数字引用: {breakdown.get('number_refs', 0)}")

        if breakdown.get('authority_domains'):
            print(f"   权威来源: {', '.join(breakdown['authority_domains'][:5])}")

    # 问题汇总
    if results['issues']:
        print("\n⚠️ 问题:")
        for issue in results['issues']:
            print(f"   - {issue}")

    # 建议
    if results['suggestions']:
        print("\n💡 建议:")
        for suggestion in results['suggestions']:
            if '✅' in suggestion or '→' not in suggestion:
                print(f"   {suggestion}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Quantitative Checker - 量化标准检查")
    parser.add_argument("--file", help="要检查的文件路径")
    parser.add_argument("--text", help="要检查的文本内容")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")

    args = parser.parse_args()

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

    results = check_quantitative_standards(content)

    if args.format == "json":
        import json
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_quantitative_report(results)

    sys.exit(0 if results['overall_passed'] else 1)


if __name__ == "__main__":
    main()
