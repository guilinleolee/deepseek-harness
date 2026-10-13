#!/usr/bin/env python3
"""
Must-Have Element Checker - GEO内容必须元素检查器
检查[not ideal when], [default recommendation], [comparison],
[decision engine], [convergence]五类必须元素
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


# ============== 元素定义 ==============

MUST_HAVE_ELEMENTS = {
    'not_ideal_when': {
        'tag': '[not ideal when]',
        'description': '非理想场景说明',
        'required': 1,
        'excellent': 2,
        'unit': 'per_option',
    },
    'default_recommendation': {
        'tag': '[default recommendation]',
        'description': '默认推荐',
        'required': 1,
        'excellent': 1,
        'unit': 'total',
    },
    'comparison': {
        'tag': '[comparison]',
        'description': '正面对比',
        'required': 1,
        'excellent': 2,
        'unit': 'total',
    },
    'decision_engine': {
        'tag': '[decision engine]',
        'description': '决策树',
        'required': 1,
        'excellent': 3,
        'unit': 'total',
    },
    'convergence': {
        'tag': '[convergence]',
        'description': '收敛总结',
        'required': 1,
        'excellent': 1,
        'unit': 'total',
        'max_words': 25,
    },
}


# ============== 工具函数 ==============

def count_words(text: str) -> int:
    """统计中英文混合文本字数"""
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))
    return chinese_chars + english_words


def extract_element_content(content: str, tag: str) -> list:
    """提取元素内容和上下文"""
    results = []

    # 匹配元素标记
    pattern = rf'{re.escape(tag)}(.*?)(?=\n\n|\n\[|$)'
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

    for match in matches:
        text = match.strip()
        results.append({
            'tag': tag,
            'content': text,
            'word_count': count_words(text),
            'has_content': len(text) > 0,
        })

    return results


def check_element_quality(element_data: dict, content: str) -> dict:
    """检查单个元素的质量"""
    tag = element_data['tag']
    required = element_data['required']
    excellent = element_data.get('excellent', required)
    max_words = element_data.get('max_words', None)

    elements = extract_element_content(content, tag)

    result = {
        'tag': tag,
        'description': element_data['description'],
        'count': len(elements),
        'required': required,
        'excellent': excellent,
        'passed': len(elements) >= required,
        'excellent_passed': len(elements) >= excellent,
        'elements': elements,
        'issues': [],
        'suggestions': [],
    }

    # 数量检查
    if len(elements) < required:
        result['issues'].append(f"数量不足: {len(elements)}/{required}")

    if len(elements) >= excellent:
        result['suggestions'].append("⭐ 达到优秀标准")
    elif len(elements) >= required:
        result['suggestions'].append("满足最低要求")

    # 内容质量检查
    empty_elements = [e for e in elements if not e['has_content']]
    if empty_elements:
        result['issues'].append(f"{len(empty_elements)}个元素内容为空")

    # 字数检查
    if max_words:
        over_limit = [e for e in elements if e['word_count'] > max_words]
        if over_limit:
            for e in over_limit:
                result['issues'].append(
                    f"字数超限: {e['word_count']}词/{max_words}词"
                )

    return result


def check_decision_tree_format(content: str) -> dict:
    """检查决策树格式"""
    # If X -> Choose Y 格式
    decision_patterns = [
        r'[Ii]f\s+.+?\s*[→→]\s*.+?',  # If X -> Choose Y
        r'[Ii]f\s+.+?\s+[Tt]hen\s+.+?',  # If X then Y
        r'[Ww]hen\s+.+?,\s*[Ss]elect\s+.+?',  # When X, Select Y
        r'[Cc]hoose\s+.+?\s+when\s+.+?',  # Choose X when Y
    ]

    found_decisions = []
    for pattern in decision_patterns:
        matches = re.findall(pattern, content)
        found_decisions.extend(matches)

    # 提取[decision engine]标记的决策树
    decision_sections = extract_element_content(content, '[decision engine]')

    # 检查是否有决策分支
    has_branches = bool(re.search(r'[Oo]ption\s+[1-9]|[Cc]ase\s+[1-9]', content))

    return {
        'decision_count': len(found_decisions),
        'marked_count': len(decision_sections),
        'has_branches': has_branches,
        'format_valid': len(found_decisions) > 0 or len(decision_sections) > 0,
    }


def check_all_must_have(content: str) -> dict:
    """执行完整的必须元素检查"""
    results = {
        'success': True,
        'overall_passed': True,
        'score': 0.0,
        'elements': {},
        'summary': {
            'total_found': 0,
            'total_required': 0,
        },
    }

    # 检查每个必须元素
    for elem_name, elem_data in MUST_HAVE_ELEMENTS.items():
        result = check_element_quality(elem_data, content)
        results['elements'][elem_name] = result

        results['summary']['total_found'] += result['count']
        results['summary']['total_required'] += result['required']

        if not result['passed']:
            results['overall_passed'] = False

    # 检查决策树格式
    decision_check = check_decision_tree_format(content)
    results['decision_check'] = decision_check

    # 计算分数
    passed_count = sum(
        1 for e in results['elements'].values()
        if e['passed']
    )
    results['score'] = passed_count / len(results['elements'])

    # 汇总问题和建议
    results['all_issues'] = []
    results['all_suggestions'] = []

    for elem_result in results['elements'].values():
        results['all_issues'].extend(elem_result['issues'])
        results['all_suggestions'].extend(elem_result['suggestions'])

    return results


def print_must_have_report(results: dict) -> None:
    """打印必须元素检查报告"""
    print("\n" + "=" * 50)
    print("📌 GEO内容必须元素检查报告")
    print("=" * 50)

    overall_icon = "✅" if results['overall_passed'] else "❌"
    print(f"\n{overall_icon} 整体状态: {'通过' if results['overall_passed'] else '未通过'}")
    print(f"评分: {results['score']:.0%}")
    print("-" * 50)

    print("\n📊 元素检查详情:")

    for elem_name, elem_result in results['elements'].items():
        icon = "✅" if elem_result['passed'] else "❌"
        excellent_icon = " ⭐" if elem_result['excellent_passed'] else ""

        count_str = f"{elem_result['count']}/{elem_result['required']}"
        if elem_result['excellent'] != elem_result['required']:
            count_str += f" (优秀≥{elem_result['excellent']})"

        print(f"\n{icon} {elem_result['description']} ({count_str}){excellent_icon}")

        if elem_result['issues']:
            for issue in elem_result['issues']:
                print(f"   ❗ {issue}")

    # 决策树特殊检查
    if 'decision_check' in results:
        dc = results['decision_check']
        print(f"\n🌲 决策树格式检查:")
        print(f"   发现决策逻辑: {dc['decision_count']}个")
        print(f"   标记决策树: {dc['marked_count']}个")
        print(f"   包含分支选项: {'是' if dc['has_branches'] else '否'}")

    # 汇总
    if results['all_issues']:
        print("\n⚠️ 问题汇总:")
        for issue in results['all_issues']:
            print(f"   - {issue}")

    if results['all_suggestions']:
        print("\n💡 建议:")
        for suggestion in results['all_suggestions']:
            if '⭐' in suggestion:
                print(f"   {suggestion}")

    print("\n" + "=" * 50)

    # 快速对照表
    print("\n📋 快速对照表:")
    print("-" * 40)
    for elem_name, elem_result in results['elements'].items():
        icon = "✅" if elem_result['passed'] else "❌"
        status = "PASS" if elem_result['passed'] else "FAIL"
        print(f"   [{status}] {elem_result['description']}: {elem_result['count']}")


def main():
    parser = argparse.ArgumentParser(description="Must-Have Element Checker - 必须元素检查")
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

    results = check_all_must_have(content)

    if args.format == "json":
        import json
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_must_have_report(results)

    sys.exit(0 if results['overall_passed'] else 1)


if __name__ == "__main__":
    main()
