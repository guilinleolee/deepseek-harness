#!/usr/bin/env python3
"""
提词师模板测试脚本

功能:
1. 测试所有模板的加载
2. 测试变量插值
3. 测试边界情况
4. 生成测试报告

使用方法:
    python test_templates.py
    python test_templates.py --verbose
"""

import io
import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import json

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from render import PromptTemplate, TemplateManager


class TemplateTester:
    """模板测试器"""

    def __init__(self):
        self.manager = TemplateManager()
        self.test_results = []

    def test_template_loading(self, template_name: str) -> Dict[str, Any]:
        """测试模板加载"""
        result = {
            'name': template_name,
            'tests': []
        }

        try:
            template = self.manager.get_template(template_name)

            if not template:
                result['tests'].append({
                    'name': '加载模板',
                    'status': '❌ 失败',
                    'error': '模板不存在'
                })
                return result

            # 测试1: 检查元数据
            result['tests'].append({
                'name': '元数据解析',
                'status': '✅ 通过',
                'details': {
                    'name': template.name,
                    'framework': template.framework,
                    'priority': template.priority,
                    'rating': template.rating
                }
            })

            # 测试2: 检查内容
            if not template.content:
                result['tests'].append({
                    'name': '内容检查',
                    'status': '❌ 失败',
                    'error': '模板内容为空'
                })
            else:
                result['tests'].append({
                    'name': '内容检查',
                    'status': '✅ 通过',
                    'details': {
                        'length': len(template.content)
                    }
                })

            # 测试3: 检查YAML frontmatter
            if template.metadata:
                result['tests'].append({
                    'name': 'YAML解析',
                    'status': '✅ 通过',
                    'details': {
                        'metadata_keys': list(template.metadata.keys())
                    }
                })
            else:
                result['tests'].append({
                    'name': 'YAML解析',
                    'status': '⚠️  警告',
                    'error': '缺少YAML frontmatter'
                })

        except Exception as e:
            result['tests'].append({
                'name': '加载模板',
                'status': '❌ 失败',
                'error': str(e)
            })

        return result

    def test_template_rendering(self, template_name: str) -> Dict[str, Any]:
        """测试模板渲染"""
        result = {
            'name': template_name,
            'tests': []
        }

        try:
            template = self.manager.get_template(template_name)

            if not template:
                result['tests'].append({
                    'name': '渲染测试',
                    'status': '❌ 失败',
                    'error': '模板不存在'
                })
                return result

            # 测试基础渲染
            test_vars = {
                'task_description': '测试任务：设计一个用户认证系统',
                'context': '这是一个Web应用，需要支持多种认证方式',
                'language': 'python',
                'framework': 'Django',
            }

            try:
                output = template.render(**test_vars)

                result['tests'].append({
                    'name': '基础渲染',
                    'status': '✅ 通过',
                    'details': {
                        'output_length': len(output)
                    }
                })

                # 检查变量插值
                if '{{' in output or '}}' in output:
                    result['tests'].append({
                        'name': '变量插值',
                        'status': '⚠️  警告',
                        'error': '输出中仍有未替换的变量'
                    })
                else:
                    result['tests'].append({
                        'name': '变量插值',
                        'status': '✅ 通过'
                    })

            except Exception as e:
                result['tests'].append({
                    'name': '基础渲染',
                    'status': '❌ 失败',
                    'error': str(e)
                })

        except Exception as e:
            result['tests'].append({
                'name': '渲染测试',
                'status': '❌ 失败',
                'error': str(e)
            })

        return result

    def test_edge_cases(self, template_name: str) -> Dict[str, Any]:
        """测试边界情况"""
        result = {
            'name': template_name,
            'tests': []
        }

        try:
            template = self.manager.get_template(template_name)

            if not template:
                return result

            # 测试1: 空变量
            try:
                output = template.render()
                result['tests'].append({
                    'name': '空变量处理',
                    'status': '✅ 通过'
                })
            except Exception as e:
                result['tests'].append({
                    'name': '空变量处理',
                    'status': '⚠️  警告',
                    'error': f'空变量时报错: {str(e)[:50]}'
                })

            # 测试2: 特殊字符
            try:
                special_vars = {
                    'task_description': '测试 <script>alert("XSS")</script> & 特殊字符: @#$%^&*()',
                }
                output = template.render(**special_vars)
                result['tests'].append({
                    'name': '特殊字符处理',
                    'status': '✅ 通过'
                })
            except Exception as e:
                result['tests'].append({
                    'name': '特殊字符处理',
                    'status': '❌ 失败',
                    'error': str(e)
                })

        except Exception as e:
            result['tests'].append({
                'name': '边界测试',
                'status': '❌ 失败',
                'error': str(e)
            })

        return result

    def run_all_tests(self, verbose: bool = False) -> List[Dict]:
        """运行所有测试"""
        templates = self.manager.list_templates()

        if not templates:
            print("❌ 未找到任何模板")
            return []

        print(f"\n🧪 开始测试 {len(templates)} 个模板\n")

        all_results = []

        for template in templates:
            template_name = template.path.stem

            if verbose:
                print(f"\n{'='*60}")
                print(f"测试模板: {template.name}")
                print(f"{'='*60}")

            # 运行测试套件
            loading_result = self.test_template_loading(template_name)
            rendering_result = self.test_template_rendering(template_name)
            edge_result = self.test_edge_cases(template_name)

            # 合并结果
            combined_result = {
                'name': template.name,
                'loading': loading_result,
                'rendering': rendering_result,
                'edge_cases': edge_result
            }

            all_results.append(combined_result)

            # 快速输出
            if verbose:
                for test_type in ['loading', 'rendering', 'edge_cases']:
                    for test in combined_result[test_type]['tests']:
                        status = test['status']
                        name = test['name']
                        print(f"  {status} {name}")
                        if 'error' in test:
                            print(f"     错误: {test['error']}")

        return all_results

    def generate_report(self, results: List[Dict]):
        """生成测试报告"""
        print("\n" + "="*70)
        print("📊 测试报告")
        print("="*70 + "\n")

        total_templates = len(results)
        total_tests = 0
        passed_tests = 0
        warning_tests = 0
        failed_tests = 0

        for result in results:
            print(f"\n📄 {result['name']}")

            for test_type in ['loading', 'rendering', 'edge_cases']:
                for test in result[test_type]['tests']:
                    total_tests += 1

                    status = test['status']
                    if '✅' in status:
                        passed_tests += 1
                        print(f"  ✅ {test['name']}")
                    elif '⚠️' in status:
                        warning_tests += 1
                        print(f"  ⚠️  {test['name']}")
                        if 'error' in test:
                            print(f"     警告: {test['error']}")
                    else:
                        failed_tests += 1
                        print(f"  ❌ {test['name']}")
                        if 'error' in test:
                            print(f"     错误: {test['error']}")

        # 汇总统计
        print("\n" + "="*70)
        print("📈 测试统计")
        print("="*70)
        print(f"总模板数: {total_templates}")
        print(f"总测试数: {total_tests}")
        print(f"✅ 通过: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"⚠️  警告: {warning_tests} ({warning_tests/total_tests*100:.1f}%)")
        print(f"❌ 失败: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")

        # 整体评估
        pass_rate = passed_tests / total_tests if total_tests > 0 else 0

        print("\n" + "="*70)
        if pass_rate >= 0.95:
            print("整体评估: 优秀 ✅")
        elif pass_rate >= 0.85:
            print("整体评估: 良好 🟢")
        elif pass_rate >= 0.70:
            print("整体评估: 及格 🟡")
        else:
            print("整体评估: 需要改进 🔴")
        print("="*70 + "\n")

        # 保存报告
        report_path = Path(__file__).parent.parent / "TEST_REPORT.md"
        self.save_markdown_report(results, report_path)
        print(f"📝 详细报告已保存到: {report_path}\n")

    def save_markdown_report(self, results: List[Dict], report_path: Path):
        """保存Markdown格式的报告"""
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 提词师模板测试报告\n\n")
            f.write(f"**生成时间**: {os.popen('date /T && time /T').read().strip()}\n\n")

            # 汇总统计
            total_tests = 0
            passed_tests = 0

            for result in results:
                for test_type in ['loading', 'rendering', 'edge_cases']:
                    for test in result[test_type]['tests']:
                        total_tests += 1
                        if '✅' in test['status']:
                            passed_tests += 1

            f.write("## 📊 测试统计\n\n")
            f.write(f"- **总模板数**: {len(results)}\n")
            f.write(f"- **总测试数**: {total_tests}\n")
            f.write(f"- **通过率**: {passed_tests/total_tests*100:.1f}%\n\n")

            # 详细结果
            f.write("## 📄 详细测试结果\n\n")

            for result in results:
                f.write(f"### {result['name']}\n\n")

                for test_type in ['loading', 'rendering', 'edge_cases']:
                    f.write(f"#### {test_type.replace('_', ' ').title()}\n\n")

                    for test in result[test_type]['tests']:
                        status_icon = '✅' if '✅' in test['status'] else '⚠️' if '⚠️' in test['status'] else '❌'
                        f.write(f"- {status_icon} **{test['name']}**: {test['status']}\n")

                        if 'error' in test:
                            f.write(f"  - 错误: `{test['error']}`\n")

                        if 'details' in test:
                            f.write(f"  - 详情: `{test['details']}`\n")

                    f.write("\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='提词师模板测试脚本')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='显示详细输出')

    args = parser.parse_args()

    tester = TemplateTester()
    results = tester.run_all_tests(verbose=args.verbose)
    tester.generate_report(results)


if __name__ == '__main__':
    main()
