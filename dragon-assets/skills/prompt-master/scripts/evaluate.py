#!/usr/bin/env python3
"""
提示词质量评估脚本

功能:
1. 评估提示词的5维度质量
2. 提供改进建议
3. 生成评分报告

使用方法:
    python evaluate.py --prompt my_prompt.txt
    python evaluate.py --template problem-decomposition
"""

import argparse
import io
import re
import sys
from pathlib import Path
from typing import Dict, List

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class PromptEvaluator:
    """提示词质量评估器"""

    def __init__(self):
        self.weights = {
            'clarity': 0.20,
            'completeness': 0.25,
            'actionability': 0.25,
            'consistency': 0.15,
            'efficiency': 0.15
        }

    def evaluate(self, prompt: str) -> Dict:
        """评估提示词质量"""
        results = {
            'clarity': self._evaluate_clarity(prompt),
            'completeness': self._evaluate_completeness(prompt),
            'actionability': self._evaluate_actionability(prompt),
            'consistency': self._evaluate_consistency(prompt),
            'efficiency': self._evaluate_efficiency(prompt)
        }

        # 计算加权总分
        total = sum(score * self.weights[key] for key, score in results.items())
        results['total'] = total * 20  # 转换为100分制

        return results

    def _evaluate_clarity(self, prompt: str) -> float:
        """评估清晰度 (0-5)"""
        score = 3.0  # 基础分

        # 加分项
        if self._has_clear_structure(prompt):
            score += 0.5
        if self._has_examples(prompt):
            score += 0.5
        if not self._has_ambiguous_terms(prompt):
            score += 0.5

        # 减分项
        if self._has_vague_language(prompt):
            score -= 0.5

        return max(0, min(5, score))

    def _evaluate_completeness(self, prompt: str) -> float:
        """评估完整性 (0-5)"""
        score = 3.0  # 基础分

        # 关键要素
        elements = [
            ('context', self._has_section(prompt, ['context', 'background', '背景'])),
            ('objective', self._has_section(prompt, ['objective', 'goal', '目标'])),
            ('requirements', self._has_section(prompt, ['requirement', '要求', 'output'])),
        ]

        for name, present in elements:
            if present:
                score += 0.5

        return max(0, min(5, score))

    def _evaluate_actionability(self, prompt: str) -> float:
        """评估可操作性 (0-5)"""
        score = 3.0  # 基础分

        # 加分项
        if self._has_clear_steps(prompt):
            score += 0.5
        if self._has_output_format(prompt):
            score += 0.5
        if self._has_examples(prompt):
            score += 0.3

        return max(0, min(5, score))

    def _evaluate_consistency(self, prompt: str) -> float:
        """评估一致性 (0-5)"""
        score = 4.0  # 基础分
        return score

    def _evaluate_efficiency(self, prompt: str) -> float:
        """评估效率 (0-5)"""
        # 基于Token长度评估
        token_count = len(prompt.split())

        if token_count < 500:
            return 5.0
        elif token_count < 1000:
            return 4.0
        elif token_count < 2000:
            return 3.0
        elif token_count < 4000:
            return 2.0
        else:
            return 1.0

    # 辅助方法

    def _has_clear_structure(self, prompt: str) -> bool:
        """是否有清晰的结构"""
        return bool(re.search(r'^#{1,3}\s+', prompt, re.MULTILINE))

    def _has_examples(self, prompt: str) -> bool:
        """是否包含示例"""
        return bool(re.search(r'示例|example', prompt, re.IGNORECASE))

    def _has_ambiguous_terms(self, prompt: str) -> bool:
        """是否有模糊术语"""
        ambiguous = ['一些', '某些', '可能', '也许']
        return any(term in prompt.lower() for term in ambiguous)

    def _has_vague_language(self, prompt: str) -> bool:
        """是否有模糊语言"""
        vague = ['尽量', '尽可能', '最好']
        return any(term in prompt for term in vague)

    def _has_section(self, prompt: str, keywords: List[str]) -> bool:
        """是否包含特定章节"""
        pattern = '|'.join(keywords)
        return bool(re.search(pattern, prompt, re.IGNORECASE))

    def _has_clear_steps(self, prompt: str) -> bool:
        """是否有清晰的步骤"""
        return bool(re.search(r'步骤|step|\d+\.', prompt, re.IGNORECASE))

    def _has_output_format(self, prompt: str) -> bool:
        """是否有输出格式说明"""
        return bool(re.search(r'输出格式|output', prompt, re.IGNORECASE))


def print_report(results: Dict, prompt_length: int):
    """打印评估报告"""

    print("\n" + "="*60)
    print("提示词质量评估报告")
    print("="*60 + "\n")

    # 5维度评分
    print("5维度评分:")
    dimensions = {
        'clarity': ('清晰度', '表达是否清晰无歧义'),
        'completeness': ('完整性', '是否包含所有必要要素'),
        'actionability': ('可操作性', '是否可直接执行'),
        'consistency': ('一致性', '术语和风格是否统一'),
        'efficiency': ('效率', 'Token使用是否精简')
    }

    for key, (name, desc) in dimensions.items():
        score = results[key]
        bar = '*' * int(score)
        print(f"  {name:12} [{bar:<5}] {score:.1f}/5 - {desc}")

    print()

    # 总分
    total = results['total']
    if total >= 90:
        grade = "优秀 ✅"
    elif total >= 75:
        grade = "良好 🟡"
    elif total >= 60:
        grade = "及格 🟠"
    else:
        grade = "不及格 🔴"

    print(f"{'='*60}")
    print(f"总评分: {total:.1f}/100")
    print(f"质量等级: {grade}")
    print(f"{'='*60}\n")

    # Token统计
    token_count = len(str(prompt_length).split())
    print(f"Token统计: 约{token_count * 4} tokens (估算)")

    print()

    # 改进建议
    suggestions = []
    if results['clarity'] < 4.0:
        suggestions.append("提升清晰度: 添加更多示例，减少模糊表达")
    if results['completeness'] < 4.0:
        suggestions.append("增强完整性: 补充context、objective等关键章节")
    if results['actionability'] < 4.0:
        suggestions.append("提高可操作性: 明确输出格式，提供具体步骤")
    if results['efficiency'] < 3.0:
        suggestions.append("优化效率: 精简内容，删除冗余信息")

    if suggestions:
        print("改进建议:")
        for suggestion in suggestions:
            print(f"  - {suggestion}")
    else:
        print("质量优秀，无需改进")

    print()


def main():
    parser = argparse.ArgumentParser(
        description='提示词质量评估工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--prompt', metavar='FILE', help='提示词文件路径')
    parser.add_argument('--text', metavar='TEXT', help='直接输入提示词文本')

    args = parser.parse_args()

    # 获取提示词
    prompt_text = None

    if args.prompt:
        path = Path(args.prompt)
        if not path.exists():
            print(f"错误: 文件不存在: {args.prompt}")
            return

        with open(path, 'r', encoding='utf-8') as f:
            prompt_text = f.read()

    elif args.text:
        prompt_text = args.text

    else:
        parser.print_help()
        return

    # 评估
    evaluator = PromptEvaluator()
    results = evaluator.evaluate(prompt_text)

    # 打印报告
    print_report(results, len(prompt_text))


if __name__ == '__main__':
    main()
