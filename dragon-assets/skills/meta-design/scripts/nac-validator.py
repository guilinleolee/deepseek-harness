#!/usr/bin/env python3
"""
NAC边界验证器 (NAC Boundary Validator)

基于NAC边界协议，验证元是否超出其职责范围。
检测五大边界类型：领域、能力、规模、质量、安全

用法:
    python nac-validator.py <meta_id> [--input input.json] [--output report.md]
"""

import json
import sys
import argparse
from dataclasses import dataclass, asdict, field
from typing import Optional, List
from datetime import datetime


@dataclass
class BoundaryViolation:
    """边界违规记录"""
    boundary_type: str
    violation_type: str  # overstep/incomplete/unclear
    description: str
    evidence: str
    severity: str  # critical/high/medium/low
    handler: str  # 应该由谁处理
    suggestion: str


@dataclass
class NACValidationResult:
    """NAC验证结果"""
    meta_id: str
    meta_name: str
    validation_date: str

    # 五类边界验证结果
    domain_boundary: dict
    capability_boundary: dict
    scale_boundary: dict
    quality_boundary: dict
    security_boundary: dict

    # 违规汇总
    violations: List[BoundaryViolation]
    total_violations: int
    critical_count: int
    high_count: int

    # 综合评估
    boundary_clarity_score: int  # 1-5
    overall_status: str  # compliant/minor_issues/issues_found/critical_violations

    def to_dict(self) -> dict:
        return {
            'meta_id': self.meta_id,
            'meta_name': self.meta_name,
            'validation_date': self.validation_date,
            'domain_boundary': self.domain_boundary,
            'capability_boundary': self.capability_boundary,
            'scale_boundary': self.scale_boundary,
            'quality_boundary': self.quality_boundary,
            'security_boundary': self.security_boundary,
            'violations': [asdict(v) for v in self.violations],
            'total_violations': self.total_violations,
            'critical_count': self.critical_count,
            'high_count': self.high_count,
            'boundary_clarity_score': self.boundary_clarity_score,
            'overall_status': self.overall_status
        }


class NACValidator:
    """NAC边界验证器"""

    BOUNDARY_TYPES = {
        'domain': {
            'name': '领域边界',
            'question': '这个任务在元的专业领域内吗？',
            'criteria': [
                '任务属于核心专业领域',
                '不属于排除领域的任务',
                '有明确的领域归属'
            ]
        },
        'capability': {
            'name': '能力边界',
            'question': '元有足够的知识/能力处理这个任务吗？',
            'criteria': [
                '在已知能力范围内',
                '不需要升级到更高层级',
                '可以独立处理或委托'
            ]
        },
        'scale': {
            'name': '规模边界',
            'question': '任务规模在元的处理能力范围内吗？',
            'criteria': [
                '数据量在限制内',
                '并发数在限制内',
                '耗时在限制内'
            ]
        },
        'quality': {
            'name': '质量边界',
            'question': '元能达到任务要求的最低质量标准吗？',
            'criteria': [
                '准确率要求可达',
                '可用性要求可达',
                '有时间保证'
            ]
        },
        'security': {
            'name': '安全边界',
            'question': '元有权限访问任务所需的数据/系统吗？',
            'criteria': [
                '在授权范围内',
                '不涉及敏感数据越界访问',
                '符合安全策略'
            ]
        }
    }

    def __init__(self, meta_id: str):
        self.meta_id = meta_id

    def validate_interactive(self, meta_name: str) -> NACValidationResult:
        """交互式验证"""
        print(f"\n{'='*60}")
        print(f"🔍 NAC边界验证 - {meta_name} ({self.meta_id})")
        print(f"{'='*60}\n")

        boundaries = {}
        violations = []

        for boundary_id, boundary_info in self.BOUNDARY_TYPES.items():
            print(f"\n📋 边界类型: {boundary_info['name']}")
            print(f"   核心问题: {boundary_info['question']}")
            print(f"\n   验证标准:")
            for i, criterion in enumerate(boundary_info['criteria'], 1):
                print(f"   {i}. {criterion}")

            # 检查边界状态
            print(f"\n   边界状态评估:")
            print(f"   1. 完全合规 - 任务完全在边界内")
            print(f"   2. 轻微逾越 - 小幅超出，可调整")
            print(f"   3. 明显违规 - 明显超出边界")
            print(f"   4. 严重违规 - 完全超出，无法处理")

            while True:
                try:
                    status = int(input(f"\n   请选择状态 (1-4): "))
                    if 1 <= status <= 4:
                        break
                    print("   ⚠️  请输入1-4之间的整数")
                except ValueError:
                    print("   ⚠️  请输入有效整数")

            # 违规描述
            if status > 1:
                violation_desc = input("   违规描述（简述超出边界的任务）: ")
                evidence = input("   违规证据（具体数据/日志）: ")
                handler = input("   应该由谁处理: ")

                severity_map = {2: 'medium', 3: 'high', 4: 'critical'}
                severity = severity_map[status]

                violations.append(BoundaryViolation(
                    boundary_type=boundary_info['name'],
                    violation_type='overstep',
                    description=violation_desc,
                    evidence=evidence,
                    severity=severity,
                    handler=handler,
                    suggestion=self._generate_suggestion(boundary_info['name'], severity)
                ))

            boundaries[boundary_id] = {
                'name': boundary_info['name'],
                'status': ['compliant', 'minor', 'overstep', 'critical'][status - 1],
                'score': 5 - (status - 1) * 1
            }

        return self._compute_result(meta_name, boundaries, violations)

    def validate_from_data(self, meta_name: str, data: dict) -> NACValidationResult:
        """从数据验证"""
        boundaries = {}
        violations = []

        for boundary_id, boundary_info in self.BOUNDARY_TYPES.items():
            boundary_data = data.get(boundary_id, {})
            status = boundary_data.get('status', 'compliant')
            status_map = {'compliant': 1, 'minor': 2, 'overstep': 3, 'critical': 4}

            boundaries[boundary_id] = {
                'name': boundary_info['name'],
                'status': status,
                'score': 5 - (status_map.get(status, 1) - 1) * 1
            }

            if status in ['overstep', 'critical']:
                violations.append(BoundaryViolation(
                    boundary_type=boundary_info['name'],
                    violation_type='overstep',
                    description=boundary_data.get('description', ''),
                    evidence=boundary_data.get('evidence', ''),
                    severity=boundary_data.get('severity', 'high'),
                    handler=boundary_data.get('handler', ''),
                    suggestion=self._generate_suggestion(boundary_info['name'], boundary_data.get('severity', 'high'))
                ))

        return self._compute_result(meta_name, boundaries, violations)

    def _compute_result(self, meta_name: str, boundaries: dict, violations: List[BoundaryViolation]) -> NACValidationResult:
        """计算验证结果"""
        critical_count = sum(1 for v in violations if v.severity == 'critical')
        high_count = sum(1 for v in violations if v.severity in ['critical', 'high'])

        # 计算边界清晰度评分
        total_score = sum(b['score'] for b in boundaries.values())
        boundary_clarity_score = max(1, min(5, total_score // len(boundaries)))

        # 综合状态
        if critical_count > 0:
            overall_status = 'critical_violations'
        elif high_count > 0:
            overall_status = 'issues_found'
        elif any(b['status'] != 'compliant' for b in boundaries.values()):
            overall_status = 'minor_issues'
        else:
            overall_status = 'compliant'

        return NACValidationResult(
            meta_id=self.meta_id,
            meta_name=meta_name,
            validation_date=datetime.now().isoformat(),
            domain_boundary=boundaries.get('domain', {}),
            capability_boundary=boundaries.get('capability', {}),
            scale_boundary=boundaries.get('scale', {}),
            quality_boundary=boundaries.get('quality', {}),
            security_boundary=boundaries.get('security', {}),
            violations=violations,
            total_violations=len(violations),
            critical_count=critical_count,
            high_count=high_count,
            boundary_clarity_score=boundary_clarity_score,
            overall_status=overall_status
        )

    def _generate_suggestion(self, boundary_type: str, severity: str) -> str:
        """生成处理建议"""
        suggestions = {
            '领域边界': {
                'medium': '考虑委托给相关领域的元处理',
                'high': '升级到编排元进行跨领域协调',
                'critical': '需要明确领域分工，重构元边界'
            },
            '能力边界': {
                'medium': '评估是否需要升级元能力',
                'high': '升级到更高能力的元或人工处理',
                'critical': '需要扩充元能力或重新设计'
            },
            '规模边界': {
                'medium': '考虑分批处理',
                'high': '升级到有更大处理能力的元',
                'critical': '拆分任务或升级基础设施'
            },
            '质量边界': {
                'medium': '调整质量预期或增加复核',
                'high': '启用降级方案或人工复核',
                'critical': '需要升级质量保障机制'
            },
            '安全边界': {
                'medium': '申请临时权限或脱敏处理',
                'high': '通过网关元或申请正式权限',
                'critical': '必须升级到有权限的元或人工处理'
            }
        }
        return suggestions.get(boundary_type, {}).get(severity, '评估并采取适当行动')

    def generate_report(self, result: NACValidationResult) -> str:
        """生成验证报告"""
        status_emoji = {
            'compliant': '✅',
            'minor_issues': '⚠️',
            'issues_found': '🔴',
            'critical_violations': '🚨'
        }

        status_text = {
            'compliant': '完全合规',
            'minor_issues': '轻微问题',
            'issues_found': '存在违规',
            'critical_violations': '严重违规'
        }

        report = f"""# NAC边界验证报告

## 基本信息

| 项目 | 内容 |
|------|------|
| 元ID | {result.meta_id} |
| 元名称 | {result.meta_name} |
| 验证日期 | {result.validation_date} |

## 边界验证状态

| 边界类型 | 状态 | 评分 |
|----------|------|------|
| 领域边界 | {result.domain_boundary.get('status', 'unknown')} | {result.domain_boundary.get('score', 0)}/5 |
| 能力边界 | {result.capability_boundary.get('status', 'unknown')} | {result.capability_boundary.get('score', 0)}/5 |
| 规模边界 | {result.scale_boundary.get('status', 'unknown')} | {result.scale_boundary.get('score', 0)}/5 |
| 质量边界 | {result.quality_boundary.get('status', 'unknown')} | {result.quality_boundary.get('score', 0)}/5 |
| 安全边界 | {result.security_boundary.get('status', 'unknown')} | {result.security_boundary.get('score', 0)}/5 |

## 违规汇总

| 指标 | 数值 |
|------|------|
| 总违规数 | {result.total_violations} |
| 严重违规 | {result.critical_count} |
| 高风险违规 | {result.high_count} |
| 边界清晰度评分 | {result.boundary_clarity_score}/5 |

## 整体状态

{status_emoji.get(result.overall_status, '❓')} **{status_text.get(result.overall_status, '未知')}**

"""

        if result.violations:
            report += "\n## 违规详情\n\n"
            for i, v in enumerate(result.violations, 1):
                severity_emoji = {'critical': '🚨', 'high': '🔴', 'medium': '⚠️', 'low': '💡'}
                report += f"""### {severity_emoji.get(v.severity, '📋')} {i}. {v.boundary_type} - {v.violation_type.upper()}

- **严重程度**: {v.severity}
- **违规描述**: {v.description}
- **违规证据**: {v.evidence}
- **处理建议**: {v.handler}
- **改进建议**: {v.suggestion}

"""

        report += f"""## NAC合规结论

"""

        if result.overall_status == 'compliant':
            report += "✅ **通过** - 该元完全符合NAC边界协议，无需调整。\n\n"
        elif result.overall_status == 'minor_issues':
            report += "⚠️ **有条件通过** - 存在轻微边界问题，建议监控。\n\n"
        elif result.overall_status == 'issues_found':
            report += "🔴 **不通过** - 存在明显边界违规，需要调整。\n\n"
        else:
            report += "🚨 **严重不通过** - 存在严重边界违规，必须重构。\n\n"

        report += f"""---

*本报告由 NAC Validator 自动生成*
"""
        return report


def main():
    parser = argparse.ArgumentParser(description='NAC边界验证器')
    parser.add_argument('meta_id', help='元ID')
    parser.add_argument('--input', '-i', help='输入JSON文件')
    parser.add_argument('--output', '-o', help='输出报告文件')
    parser.add_argument('--meta-name', '-n', default='未命名元', help='元名称')

    args = parser.parse_args()

    validator = NACValidator(args.meta_id)

    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        result = validator.validate_from_data(args.meta_name, data)
    else:
        result = validator.validate_interactive(args.meta_name)

    report = validator.generate_report(result)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✅ 报告已保存到: {args.output}")

        json_output = args.output.replace('.md', '.json')
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"✅ JSON结果已保存到: {json_output}")
    else:
        print(report)

    return 0 if result.overall_status in ['compliant', 'minor_issues'] else 1


if __name__ == '__main__':
    sys.exit(main())
