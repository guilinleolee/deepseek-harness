#!/usr/bin/env python3
"""
元质量评估器 (Meta Quality Evaluator)

基于元5特征评估体系，对元进行系统性质量评估。
评估维度：独立、足够小、边界清晰、可替换、可复用

用法:
    python meta-evaluator.py <meta_id> [--input input.json] [--output report.md]
"""

import json
import sys
import argparse
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime


@dataclass
class MetaIdentity:
    """元身份定义"""
    meta_id: str
    meta_name: str
    core_responsibility: str
    problem_solved: str


@dataclass
class CharacteristicScore:
    """特征评分"""
    name: str
    score: int  # 1-5
    questions: dict  # 问题回答
    evidence: str  # 评分依据
    suggestions: list  # 改进建议


@dataclass
class EvaluationResult:
    """评估结果"""
    meta_id: str
    meta_name: str
    evaluation_date: str

    # 五特征评分
    independence: CharacteristicScore
    granularity: CharacteristicScore
    boundary_clarity: CharacteristicScore
    replaceability: CharacteristicScore
    reusability: CharacteristicScore

    # 综合评分
    total_score: int  # /25
    percentage: float  # 百分比

    # 等级判定
    qualification: str  # 优秀/良好/及格/不及格
    improvement_items: list

    def to_dict(self) -> dict:
        return {
            'meta_id': self.meta_id,
            'meta_name': self.meta_name,
            'evaluation_date': self.evaluation_date,
            'independence': asdict(self.independence),
            'granularity': asdict(self.granularity),
            'boundary_clarity': asdict(self.boundary_clarity),
            'replaceability': asdict(self.replaceability),
            'reusability': asdict(self.reusability),
            'total_score': self.total_score,
            'percentage': self.percentage,
            'qualification': self.qualification,
            'improvement_items': self.improvement_items
        }


class MetaEvaluator:
    """元质量评估器"""

    # 五特征定义
    CHARACTERISTICS = {
        'independence': {
            'name': '独立',
            'question': '这个元能单独拿出来说清楚吗？没有上下文也能理解它的职责吗？',
            'scoring': {
                1: '无法独立，必须依赖多个其他元，缺少任何一个都无法工作',
                2: '高度依赖，依赖2-3个其他元，少一个就有问题',
                3: '中度依赖，依赖1-2个其他元，但有降级方案',
                4: '基本独立，核心功能可独立，辅助功能需要少量依赖',
                5: '完全独立，自身功能完整，依赖仅用于增强而非必需'
            }
        },
        'granularity': {
            'name': '足够小',
            'question': '这个元再往下拆，收益开始变低吗？',
            'scoring': {
                1: '过于臃肿，职责数量>10个，难以理解和维护',
                2: '偏大，职责数量7-10个，建议拆分',
                3: '合理偏大，职责数量5-7个，可接受',
                4: '理想大小，职责数量3-5个，粒度合适',
                5: '过于细小，职责数量≤2个，可能粒度过细'
            }
        },
        'boundary_clarity': {
            'name': '边界清晰',
            'question': '这个元的边界在哪里？负责什么/不负责什么明确吗？',
            'scoring': {
                1: '边界模糊，无法清晰描述负责和不负责的边界',
                2: '部分清晰，知道大概边界，但无法清晰描述',
                3: '基本清晰，有明确的内外边界，但灰色地带较多',
                4: '清晰，边界清晰，灰色地带少',
                5: '非常清晰，边界非常清晰，NAC文档完整，协作者一目了然'
            }
        },
        'replaceability': {
            'name': '可替换',
            'question': '升级或替换这个元会塌掉整个系统吗？',
            'scoring': {
                1: '不可替换，替换=系统崩溃，必须完整重建',
                2: '难替换，替换需要协调>5个团队，接口强耦合',
                3: '中等可替换，替换需要通知调用方，但有标准接口',
                4: '较易替换，替换只需通知少量调用方，接口兼容',
                5: '随时可替换，替换无影响，接口完全解耦'
            }
        },
        'reusability': {
            'name': '可复用',
            'question': '下次遇到相近任务，这个元能复用吗？',
            'scoring': {
                1: '不可复用，强耦合特定项目，无法提取',
                2: '难复用，接口不标准，文档缺失',
                3: '基本可复用，接口基本标准，但需要适配',
                4: '较易复用，接口标准，文档完整，稍作适配即可',
                5: '完全可复用，接口标准化，文档完整，开箱即用'
            }
        }
    }

    def __init__(self, meta_id: str):
        self.meta_id = meta_id
        self.scores = {}

    def evaluate_interactive(self, meta_name: str) -> EvaluationResult:
        """交互式评估"""
        print(f"\n{'='*60}")
        print(f"🔍 元质量评估 - {meta_name} ({self.meta_id})")
        print(f"{'='*60}\n")

        results = {}

        for char_id, char_info in self.CHARACTERISTICS.items():
            print(f"\n📊 特征 {char_id}: {char_info['name']}")
            print(f"   核心问题: {char_info['question']}")
            print(f"\n   评分标准:")
            for score, desc in char_info['scoring'].items():
                print(f"   {score}分: {desc}")

            while True:
                try:
                    score = int(input(f"\n   请输入评分 (1-5): "))
                    if 1 <= score <= 5:
                        break
                    print("   ⚠️  请输入1-5之间的整数")
                except ValueError:
                    print("   ⚠️  请输入有效整数")

            evidence = input("   评分依据（简述）: ")
            suggestions = input("   改进建议（多选逗号分隔，空跳过）: ")

            results[char_id] = CharacteristicScore(
                name=char_info['name'],
                score=score,
                questions={char_info['question']: 'answered'},
                evidence=evidence,
                suggestions=[s.strip() for s in suggestions.split(',') if s.strip()]
            )

        return self._compute_result(meta_name, results)

    def evaluate_from_data(self, meta_name: str, data: dict) -> EvaluationResult:
        """从数据评估"""
        results = {}

        for char_id, char_info in self.CHARACTERISTICS.items():
            score_data = data.get(char_id, {})
            results[char_id] = CharacteristicScore(
                name=char_info['name'],
                score=score_data.get('score', 3),
                questions=score_data.get('questions', {}),
                evidence=score_data.get('evidence', ''),
                suggestions=score_data.get('suggestions', [])
            )

        return self._compute_result(meta_name, results)

    def _compute_result(self, meta_name: str, results: dict) -> EvaluationResult:
        """计算评估结果"""
        total = sum(s.score for s in results.values())
        percentage = (total / 25) * 100

        if total >= 20:
            qualification = '优秀'
        elif total >= 15:
            qualification = '良好'
        elif total >= 12:
            qualification = '及格'
        else:
            qualification = '不及格'

        # 收集改进项
        improvement_items = []
        for char_id, score in results.items():
            if score.score < 4:
                improvement_items.append({
                    'characteristic': score.name,
                    'current_score': score.score,
                    'suggestions': score.suggestions
                })

        return EvaluationResult(
            meta_id=self.meta_id,
            meta_name=meta_name,
            evaluation_date=datetime.now().isoformat(),
            independence=results['independence'],
            granularity=results['granularity'],
            boundary_clarity=results['boundary_clarity'],
            replaceability=results['replaceability'],
            reusability=results['reusability'],
            total_score=total,
            percentage=percentage,
            qualification=qualification,
            improvement_items=improvement_items
        )

    def generate_report(self, result: EvaluationResult) -> str:
        """生成评估报告"""
        report = f"""# 元质量评估报告

## 基本信息

| 项目 | 内容 |
|------|------|
| 元ID | {result.meta_id} |
| 元名称 | {result.meta_name} |
| 评估日期 | {result.evaluation_date} |

## 五特征评分

| 特征 | 得分 | 等级 | 评分依据 |
|------|------|------|---------|
| 独立 | {result.independence.score}/5 | {self._score_label(result.independence.score)} | {result.independence.evidence} |
| 足够小 | {result.granularity.score}/5 | {self._score_label(result.granularity.score)} | {result.granularity.evidence} |
| 边界清晰 | {result.boundary_clarity.score}/5 | {self._score_label(result.boundary_clarity.score)} | {result.boundary_clarity.evidence} |
| 可替换 | {result.replaceability.score}/5 | {self._score_label(result.replaceability.score)} | {result.replaceability.evidence} |
| 可复用 | {result.reusability.score}/5 | {self._score_label(result.reusability.score)} | {result.reusability.evidence} |

## 综合评分

| 指标 | 数值 |
|------|------|
| 总分 | {result.total_score}/25 |
| 百分比 | {result.percentage:.1f}% |
| 等级 | **{result.qualification}** |

## 改进项

"""

        if result.improvement_items:
            for item in result.improvement_items:
                report += f"""### {item['characteristic']} (当前: {item['current_score']}分)

"""
                if item['suggestions']:
                    for sug in item['suggestions']:
                        report += f"- {sug}\n"
                else:
                    report += "- 暂无具体建议\n"
                report += "\n"
        else:
            report += "✅ 所有特征均达到4分以上，无需强制改进。\n\n"

        report += f"""## 评估结论

{'✅ **通过** - 该元设计质量优秀，可进入下一阶段。' if result.total_score >= 20 else '⚠️ **有条件通过** - 该元存在改进空间，建议按优先级改进。' if result.total_score >= 12 else '❌ **不通过** - 该元存在重大缺陷，需要重新设计。'}

---
*本报告由 Meta Evaluator 自动生成*
"""
        return report

    def _score_label(self, score: int) -> str:
        labels = {1: '不合格', 2: '较差', 3: '及格', 4: '良好', 5: '优秀'}
        return labels.get(score, '未知')


def main():
    parser = argparse.ArgumentParser(description='元质量评估器')
    parser.add_argument('meta_id', help='元ID')
    parser.add_argument('--input', '-i', help='输入JSON文件')
    parser.add_argument('--output', '-o', help='输出报告文件')
    parser.add_argument('--meta-name', '-n', default='未命名元', help='元名称')

    args = parser.parse_args()

    evaluator = MetaEvaluator(args.meta_id)

    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        result = evaluator.evaluate_from_data(args.meta_name, data)
    else:
        result = evaluator.evaluate_interactive(args.meta_name)

    report = evaluator.generate_report(result)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✅ 报告已保存到: {args.output}")

        # 同时保存JSON结果
        json_output = args.output.replace('.md', '.json')
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"✅ JSON结果已保存到: {json_output}")
    else:
        print(report)

    return 0 if result.total_score >= 15 else 1


if __name__ == '__main__':
    sys.exit(main())
