#!/usr/bin/env python3
"""
AI Pattern Detector - AI痕迹检测器
检测GEO内容中的AI生成特征和禁止模式
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# ============== AI禁止模式定义 ==============

@dataclass
class AIProhibitedPattern:
    pattern: str
    name: str
    severity: str  # 'high', 'medium', 'low'
    description: str


PROHIBITED_PATTERNS = [
    AIProhibitedPattern(
        pattern=r'值得注意的是',
        name='值得注意的是开头',
        severity='high',
        description='典型的AI总结性过渡语'
    ),
    AIProhibitedPattern(
        pattern=r'从上述分析可以看出',
        name='从上述分析可以看出',
        severity='high',
        description='典型的AI分析总结语'
    ),
    AIProhibitedPattern(
        pattern=r'综上所述',
        name='综上所述',
        severity='high',
        description='典型的AI结论过渡语'
    ),
    AIProhibitedPattern(
        pattern=r'综上所述，',
        name='综上所述开头',
        severity='high',
        description='典型的AI结论过渡语'
    ),
    AIProhibitedPattern(
        pattern=r'毫无疑问',
        name='毫无疑问',
        severity='medium',
        description='过于绝对的AI表达'
    ),
    AIProhibitedPattern(
        pattern=r'毫无疑问地',
        name='毫无疑问地',
        severity='medium',
        description='典型的AI强调表达'
    ),
    AIProhibitedPattern(
        pattern=r'首先.*?其次.*?最后',
        name='首先其次最后',
        severity='medium',
        description='典型的AI三段式结构'
    ),
    AIProhibitedPattern(
        pattern=r'第一.*?第二.*?第三',
        name='第一第二第三',
        severity='medium',
        description='典型的AI列表结构'
    ),
    AIProhibitedPattern(
        pattern=r'一方面.*?另一方面',
        name='一方面另一方面',
        severity='medium',
        description='典型的AI对比结构'
    ),
    AIProhibitedPattern(
        pattern=r'换句话说',
        name='换句话说',
        severity='medium',
        description='典型的AI解释过渡语'
    ),
    AIProhibitedPattern(
        pattern=r'换言之',
        name='换言之',
        severity='medium',
        description='典型的AI解释过渡语'
    ),
    AIProhibitedPattern(
        pattern=r'也就是说',
        name='也就是说',
        severity='low',
        description='可能的AI解释语'
    ),
    AIProhibitedPattern(
        pattern=r'具体来说',
        name='具体来说',
        severity='low',
        description='可能的AI解释语'
    ),
    AIProhibitedPattern(
        pattern=r'值得注意的是，',
        name='值得注意的是逗号',
        severity='high',
        description='典型的AI总结性过渡语'
    ),
    AIProhibitedPattern(
        pattern=r'从这个角度来看',
        name='从这个角度来看',
        severity='low',
        description='可能的AI分析语'
    ),
    AIProhibitedPattern(
        pattern=r'在.*?方面',
        name='在X方面',
        severity='low',
        description='可能的AI格式化表达'
    ),
    AIProhibitedPattern(
        pattern=r'就.*?而言',
        name='就X而言',
        severity='low',
        description='可能的AI分析语'
    ),
]

# AI风格特征
AI_STYLE_FEATURES = {
    'excessive_paragraphing': {
        'pattern': r'\n\n\n+',
        'name': '过多空行',
        'threshold': 3,
        'description': '连续3个以上空行可能是AI分段特征'
    },
    'bullet_list_heavy': {
        'pattern': r'^\s*[-*•]\s+',
        'name': '过多列表项',
        'threshold': 10,
        'description': '列表项过多可能表示AI格式化倾向'
    },
    'numbering_pattern': {
        'pattern': r'^\d+\.',
        'name': '规范化编号',
        'threshold': 8,
        'description': '过多编号列表可能表示AI格式化倾向'
    },
    'quote_cluster': {
        'pattern': r'[""]',
        'name': '引号聚集',
        'threshold': 5,
        'description': '引号过多可能是AI引用特征'
    },
    'caps_sentence_start': {
        'pattern': r'[.!?]\s+[A-Z][a-z]+\s+(?:首先|其次|最后|第一|第二|第三)',
        'name': '大写+AI结构',
        'threshold': 1,
        'description': '大写字母后紧跟AI结构词'
    },
}


# ============== 检测函数 ==============

def detect_prohibited_patterns(content: str) -> list:
    """检测禁止模式"""
    findings = []

    for p in PROHIBITED_PATTERNS:
        matches = re.findall(p.pattern, content)
        if matches:
            findings.append({
                'pattern': p.pattern,
                'name': p.name,
                'severity': p.severity,
                'count': len(matches),
                'positions': [m.start() for m in re.finditer(p.pattern, content)],
                'examples': matches[:3],  # 最多3个示例
                'description': p.description,
            })

    return findings


def detect_style_features(content: str) -> list:
    """检测AI风格特征"""
    findings = []

    for feature_name, feature_data in AI_STYLE_FEATURES.items():
        matches = re.findall(feature_data['pattern'], content)
        count = len(matches)

        if count >= feature_data['threshold']:
            findings.append({
                'feature': feature_name,
                'name': feature_data['name'],
                'count': count,
                'threshold': feature_data['threshold'],
                'severity': 'medium' if count > feature_data['threshold'] * 2 else 'low',
                'description': feature_data['description'],
            })

    return findings


def detect_repetitive_sentences(content: str) -> list:
    """检测重复句式"""
    findings = []

    # 分割句子
    sentences = re.split(r'[.!?。！？]', content)
    sentences = [s.strip() for s in sentences if s.strip() and len(s) > 15]

    # 检查句首重复
    sentence_starts = []
    for s in sentences[:30]:  # 只检查前30句
        words = s.split()[:5]  # 取前5个词
        if words:
            sentence_starts.append(' '.join(words))

    # 找出重复的句首
    from collections import Counter
    start_counts = Counter(sentence_starts)

    for start, count in start_counts.items():
        if count >= 3:
            findings.append({
                'type': 'sentence_start_repetition',
                'text': start,
                'count': count,
                'severity': 'medium',
                'description': f'句首"{start[:20]}..."重复{count}次',
            })

    # 检查段落开头重复
    paragraphs = re.split(r'\n\n+', content)
    paragraph_starts = []

    for p in paragraphs[:10]:
        first_line = p.strip().split('\n')[0][:30] if p.strip() else ''
        if first_line:
            paragraph_starts.append(first_line)

    start_counts = Counter(paragraph_starts)

    for start, count in start_counts.items():
        if count >= 2:
            findings.append({
                'type': 'paragraph_start_repetition',
                'text': start,
                'count': count,
                'severity': 'low',
                'description': f'段落开头"{start}"重复{count}次',
            })

    return findings


def calculate_ai_score(prohibited: list, style_features: list, repetitive: list) -> dict:
    """计算AI痕迹分数"""
    # 基础分数
    score = 0.0

    # 禁止模式贡献
    for p in prohibited:
        if p['severity'] == 'high':
            score += p['count'] * 0.15
        elif p['severity'] == 'medium':
            score += p['count'] * 0.08
        else:
            score += p['count'] * 0.03

    # 风格特征贡献
    for f in style_features:
        if f['severity'] == 'medium':
            score += 0.05
        else:
            score += 0.02

    # 重复句式贡献
    for r in repetitive:
        if r['severity'] == 'medium':
            score += 0.1
        else:
            score += 0.05

    # 限制在0-1范围
    ai_score = min(max(score, 0.0), 1.0)

    # 评级
    if ai_score < 0.3:
        grade = '🟢 通过'
        grade_desc = '自然人类写作风格'
    elif ai_score < 0.5:
        grade = '🟡 警告'
        grade_desc = '轻微模板化'
    elif ai_score < 0.7:
        grade = '🟠 需改进'
        grade_desc = '中度模板化'
    else:
        grade = '🔴 不通过'
        grade_desc = '明显AI生成痕迹'

    return {
        'score': ai_score,
        'grade': grade,
        'grade_desc': grade_desc,
        'passed': ai_score < 0.3,
    }


def full_ai_scan(content: str) -> dict:
    """执行完整的AI痕迹扫描"""
    results = {
        'success': True,
        'prohibited_patterns': [],
        'style_features': [],
        'repetitive_sentences': [],
        'ai_score': {},
        'summary': {},
    }

    # 检测禁止模式
    results['prohibited_patterns'] = detect_prohibited_patterns(content)

    # 检测风格特征
    results['style_features'] = detect_style_features(content)

    # 检测重复句式
    results['repetitive_sentences'] = detect_repetitive_sentences(content)

    # 计算AI分数
    results['ai_score'] = calculate_ai_score(
        results['prohibited_patterns'],
        results['style_features'],
        results['repetitive_sentences']
    )

    # 汇总
    total_issues = (
        len(results['prohibited_patterns']) +
        len(results['style_features']) +
        len(results['repetitive_sentences'])
    )

    high_severity_count = sum(
        1 for p in results['prohibited_patterns'] if p['severity'] == 'high'
    )

    results['summary'] = {
        'total_issues': total_issues,
        'high_severity_count': high_severity_count,
        'total_prohibited_count': sum(p['count'] for p in results['prohibited_patterns']),
    }

    return results


def print_scan_report(results: dict) -> None:
    """打印扫描报告"""
    print("\n" + "=" * 60)
    print("🔍 AI痕迹检测报告")
    print("=" * 60)

    # AI分数
    ai_score = results['ai_score']
    print(f"\n{ai_score['grade']} AI分数: {ai_score['score']:.2f}")
    print(f"   {ai_score['grade_desc']}")

    # 问题汇总
    summary = results['summary']
    print(f"\n📊 问题汇总:")
    print(f"   总问题数: {summary['total_issues']}")
    print(f"   禁止模式: {summary['total_prohibited_count']}处")
    print(f"   高严重性: {summary['high_severity_count']}处")

    # 禁止模式详情
    if results['prohibited_patterns']:
        print(f"\n❌ 禁止模式 ({len(results['prohibited_patterns'])}种):")
        for p in results['prohibited_patterns']:
            severity_icon = '🔴' if p['severity'] == 'high' else '🟡'
            print(f"   {severity_icon} [{p['name']}] ×{p['count']}")
            if p['examples']:
                example = p['examples'][0][:40]
                print(f"      例: \"{example}...\"")

    # 风格特征
    if results['style_features']:
        print(f"\n⚠️ 风格特征 ({len(results['style_features'])}种):")
        for f in results['style_features']:
            print(f"   🟡 {f['name']}: {f['count']}处 (阈值≥{f['threshold']})")

    # 重复句式
    if results['repetitive_sentences']:
        print(f"\n⚠️ 重复句式 ({len(results['repetitive_sentences'])}处):")
        for r in results['repetitive_sentences'][:5]:
            print(f"   🟡 {r['description']}")

    # 建议
    if results['prohibited_patterns']:
        print(f"\n💡 修改建议:")
        for p in results['prohibited_patterns'][:3]:
            print(f"   - 替换\"{p['name']}\"为更自然的表达")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="AI Pattern Detector - AI痕迹检测")
    parser.add_argument("--text", required=True, help="要扫描的文本内容")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")

    args = parser.parse_args()

    results = full_ai_scan(args.text)

    if args.format == "json":
        import json
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_scan_report(results)

    sys.exit(0 if results['ai_score']['passed'] else 1)


if __name__ == "__main__":
    main()
