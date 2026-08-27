#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提词师实战验证脚本

在真实场景中测试提词师的效果
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# 添加scripts目录到路径
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

# 修复Windows编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from render import TemplateManager


class ScenarioValidator:
    """场景验证器"""

    def __init__(self):
        self.manager = TemplateManager()
        self.results = []

    def validate_scenario(self, scenario_name: str, template_name: str,
                         variables: dict, expected_quality: int) -> dict:
        """验证单个场景"""
        print(f"\n{'='*70}")
        print(f"场景验证: {scenario_name}")
        print(f"{'='*70}\n")

        result = {
            'scenario': scenario_name,
            'template': template_name,
            'variables': variables,
            'timestamp': datetime.now().isoformat(),
            'metrics': {}
        }

        # 获取模板
        template = self.manager.get_template(template_name)

        if not template:
            result['status'] = '❌ 失败'
            result['error'] = f'模板 {template_name} 不存在'
            print(f"❌ 模板不存在: {template_name}\n")
            return result

        print(f"✅ 模板: {template.name}")
        print(f"   框架: {template.framework}")
        print(f"   评分: {template.rating}/100\n")

        # 渲染提示词
        try:
            start_time = datetime.now()
            output = template.render(**variables)
            render_time = (datetime.now() - start_time).total_seconds()

            print(f"✅ 渲染成功")
            print(f"   输出长度: {len(output)} 字符")
            print(f"   渲染时间: {render_time:.3f} 秒\n")

            result['metrics']['render_time'] = render_time
            result['metrics']['output_length'] = len(output)
            result['metrics']['output'] = output

            # 评估质量
            quality_score = self._evaluate_quality(output, template)
            result['metrics']['quality_score'] = quality_score

            print(f"📊 质量评估: {quality_score}/100")

            # 与预期对比
            gap = abs(quality_score - expected_quality)
            if gap <= 5:
                result['status'] = '✅ 优秀'
                print(f"✅ 符合预期 (预期: {expected_quality})\n")
            elif gap <= 10:
                result['status'] = '🟡 良好'
                print(f"🟡 基本符合预期 (预期: {expected_quality})\n")
            else:
                result['status'] = '⚠️ 需改进'
                print(f"⚠️  与预期有差距 (预期: {expected_quality})\n")

            # 保存输出
            output_dir = Path(__file__).parent.parent / "outputs"
            output_dir.mkdir(exist_ok=True)

            output_file = output_dir / f"{scenario_name}_{template_name}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)

            print(f"💾 输出已保存到: {output_file}\n")

        except Exception as e:
            result['status'] = '❌ 失败'
            result['error'] = str(e)
            print(f"❌ 渲染失败: {e}\n")

        self.results.append(result)
        return result

    def _evaluate_quality(self, output: str, template) -> int:
        """评估输出质量"""
        score = 0

        # 1. 结构完整性 (30分)
        if '# ' in output:  # 有标题
            score += 10
        if '## ' in output:  # 有二级标题
            score += 10
        if '### ' in output:  # 有三级标题
            score += 5
        if '```' in output:  # 有代码块
            score += 5

        # 2. 内容丰富度 (30分)
        word_count = len(output.split())
        if word_count > 1000:
            score += 15
        elif word_count > 500:
            score += 10
        elif word_count > 200:
            score += 5

        # 3. 指导性 (20分)
        guidance_keywords = ['步骤', '要求', '标准', '示例', '注意', '建议']
        found = sum(1 for kw in guidance_keywords if kw in output)
        score += min(found * 4, 20)

        # 4. 专业性 (20分)
        professional_keywords = ['分析', '评估', '验证', '优化', '设计', '实现']
        found = sum(1 for kw in professional_keywords if kw in output)
        score += min(found * 4, 20)

        return min(score, 100)

    def generate_validation_report(self):
        """生成验证报告"""
        print("\n" + "="*70)
        print("📊 实战验证报告")
        print("="*70 + "\n")

        total = len(self.results)
        success = sum(1 for r in self.results if '✅' in r['status'])
        warning = sum(1 for r in self.results if '🟡' in r['status'] or '⚠️' in r['status'])
        failed = sum(1 for r in self.results if '❌' in r['status'])

        print(f"总场景数: {total}")
        print(f"✅ 优秀: {success}")
        print(f"🟡 良好/警告: {warning}")
        print(f"❌ 失败: {failed}\n")

        # 详细结果
        for i, result in enumerate(self.results, 1):
            print(f"{i}. {result['scenario']}")
            print(f"   状态: {result['status']}")
            if 'metrics' in result and 'quality_score' in result['metrics']:
                print(f"   质量分: {result['metrics']['quality_score']}/100")
            if 'error' in result:
                print(f"   错误: {result['error']}")
            print()

        # 保存报告
        report_path = Path(__file__).parent.parent / "VALIDATION_REPORT.md"
        self._save_markdown_report(report_path)
        print(f"📝 详细报告已保存到: {report_path}\n")

    def _save_markdown_report(self, report_path: Path):
        """保存Markdown报告"""
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 提词师实战验证报告\n\n")
            f.write(f"**验证时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**验证场景数**: {len(self.results)}\n\n")

            f.write("## 📊 验证概览\n\n")

            total = len(self.results)
            success = sum(1 for r in self.results if '✅' in r['status'])
            avg_quality = sum(r.get('metrics', {}).get('quality_score', 0) for r in self.results) / total if total > 0 else 0

            f.write(f"- **总场景数**: {total}\n")
            f.write(f"- **优秀率**: {success/total*100:.1f}%\n")
            f.write(f"- **平均质量分**: {avg_quality:.1f}/100\n\n")

            f.write("## 🎯 场景详情\n\n")

            for i, result in enumerate(self.results, 1):
                f.write(f"### {i}. {result['scenario']}\n\n")
                f.write(f"**模板**: {result['template']}\n")
                f.write(f"**状态**: {result['status']}\n")

                if 'metrics' in result:
                    metrics = result['metrics']

                    if 'quality_score' in metrics:
                        f.write(f"**质量分**: {metrics['quality_score']}/100\n")

                    if 'render_time' in metrics:
                        f.write(f"**渲染时间**: {metrics['render_time']:.3f}秒\n")

                    if 'output_length' in metrics:
                        f.write(f"**输出长度**: {metrics['output_length']} 字符\n")

                if 'error' in result:
                    f.write(f"**错误**: {result['error']}\n")

                f.write("\n")

                if 'variables' in result:
                    f.write("**输入变量**:\n```json\n")
                    f.write(json.dumps(result['variables'], ensure_ascii=False, indent=2))
                    f.write("\n```\n\n")

                if 'metrics' in result and 'output' in result['metrics']:
                    output = result['metrics']['output']
                    # 只显示前500字符
                    preview = output[:500] + "..." if len(output) > 500 else output
                    f.write("**输出预览**:\n```\n")
                    f.write(preview)
                    f.write("\n```\n\n")

                f.write("---\n\n")


def main():
    validator = ScenarioValidator()

    # 场景1: 00分析师 - 问题解构
    validator.validate_scenario(
        scenario_name="场景1_00分析师_需求分析",
        template_name="problem-decomposition",
        variables={
            "task_description": "设计一个电商推荐系统，需要支持千万级商品和百万级用户",
            "context": "某大型电商平台，当前使用协同过滤算法，准确率70%，需要提升到85%以上"
        },
        expected_quality=90
    )

    # 场景2: 02架构师 - 系统设计
    validator.validate_scenario(
        scenario_name="场景2_02架构师_系统设计",
        template_name="system-design",
        variables={
            "task_description": "设计一个微服务架构的电商平台后端系统",
            "qps": "10000",
            "user_scale": "百万级",
            "data_scale": "TB级",
            "availability_requirement": "99.9%",
            "performance_requirement": "响应时间<100ms"
        },
        expected_quality=90
    )

    # 场景3: 06审查师 - 代码审查
    validator.validate_scenario(
        scenario_name="场景3_06审查师_代码审查",
        template_name="code-review",
        variables={
            "context_description": "用户认证模块的核心代码，负责JWT token生成和验证",
            "language": "python",
            "framework": "FastAPI",
            "review_focus": "安全性、性能、可维护性"
        },
        expected_quality=85
    )

    # 生成报告
    validator.generate_validation_report()


if __name__ == '__main__':
    main()
