#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成器
Report Generator

负责生成用户画像分析报告，支持 Markdown、HTML 和 CSV 格式。
"""

import csv
import os
import webbrowser
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class ReportGenerator:
    """用户画像报告生成器"""

    def __init__(self, template_dir: str = None):
        """
        初始化报告生成器

        Args:
            template_dir: 模板目录路径
        """
        if template_dir is None:
            # 默认模板目录
            current_dir = Path(__file__).parent.parent.parent
            template_dir = current_dir / 'assets' / 'templates'

        self.template_dir = Path(template_dir)

    def generate_all(self, persona_data: Dict[str, Any], output_dir: str = None, auto_open_html: bool = True):
        """
        生成所有格式的报告

        Args:
            persona_data: 用户画像数据
            output_dir: 输出目录
            auto_open_html: 是否自动在浏览器中打开 HTML 报告

        Returns:
            生成的文件路径
        """
        if output_dir is None:
            output_dir = "~/persona-reports"

        output_path = Path(output_dir).expanduser()
        output_path.mkdir(parents=True, exist_ok=True)

        keyword = persona_data.get('keyword', 'unknown')
        base_name = f"{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 生成 Markdown 报告
        md_file = output_path / f"{base_name}.md"
        self.generate_markdown(persona_data, str(md_file))

        # 生成 HTML 报告（自动在浏览器中打开）
        html_file = output_path / f"{base_name}.html"
        self.generate_html(persona_data, str(html_file), auto_open=auto_open_html)

        # 生成 CSV 数据
        csv_file = output_path / f"{base_name}.csv"
        self.generate_csv(persona_data, str(csv_file))

        return {
            'markdown': str(md_file),
            'html': str(html_file),
            'csv': str(csv_file)
        }

    def generate_markdown(self, persona_data: Dict[str, Any], output_path: str) -> str:
        """
        生成 Markdown 报告

        Args:
            persona_data: 用户画像数据
            output_path: 输出文件路径

        Returns:
            生成的文件路径
        """
        # 构建报告内容
        report = self._build_markdown_report(persona_data)

        # 保存文件
        output_path = Path(output_path).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        return str(output_path)

    def generate_html(self, persona_data: Dict[str, Any], output_path: str, auto_open: bool = True) -> str:
        """
        生成 HTML 可视化报告

        Args:
            persona_data: 用户画像数据
            output_path: 输出文件路径
            auto_open: 是否自动在浏览器中打开

        Returns:
            生成的文件路径
        """
        # 构建 HTML 报告
        html = self._build_html_report(persona_data)

        # 保存文件
        output_path = Path(output_path).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        # 自动在浏览器中打开
        if auto_open:
            try:
                webbrowser.open(f'file:///{output_path.as_posix()}')
            except Exception as e:
                print(f'无法自动打开浏览器: {e}')

        return str(output_path)

    def generate_csv(self, persona_data: Dict[str, Any], output_path: str) -> str:
        """
        生成 CSV 数据文件

        Args:
            persona_data: 用户画像数据
            output_path: 输出文件路径

        Returns:
            生成的文件路径
        """
        output_path = Path(output_path).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)

            # 写入基本信息
            writer.writerow(['字段', '值'])
            writer.writerow(['关键词', persona_data.get('keyword', '')])
            writer.writerow(['数据源', ', '.join(persona_data.get('sources', []))])
            writer.writerow(['数据源数量', persona_data.get('source_count', 0)])
            writer.writerow(['聚合时间', persona_data.get('metadata', {}).get('aggregation_time', '')])
            writer.writerow([])

            # 写入核心用户画像
            core_persona = persona_data.get('core_persona', {})
            writer.writerow(['核心用户画像', ''])
            writer.writerow(['主要年龄段', core_persona.get('primary_age', '')])
            writer.writerow(['年龄段占比', f"{core_persona.get('primary_age_pct', 0)}%"])
            writer.writerow(['性别特征', core_persona.get('gender_dominant', '')])
            writer.writerow(['TOP 地域', ', '.join(core_persona.get('top_regions', []))])
            writer.writerow([])

            # 写入年龄分布
            writer.writerow(['年龄段', '占比'])
            age_dist = persona_data.get('demographics', {}).get('age', {})
            for age, percentage in age_dist.items():
                writer.writerow([age, f"{percentage*100:.2f}%"])
            writer.writerow([])

            # 写入性别分布
            writer.writerow(['性别', '占比'])
            gender_dist = persona_data.get('demographics', {}).get('gender', {})
            for gender, percentage in gender_dist.items():
                gender_name = '男性' if gender == 'male' else '女性'
                writer.writerow([gender_name, f"{percentage*100:.2f}%"])
            writer.writerow([])

            # 写入地域分布
            writer.writerow(['排名', '地域', '占比'])
            region_dist = persona_data.get('demographics', {}).get('region', [])
            for region_data in region_dist:
                writer.writerow([
                    region_data.get('rank', ''),
                    region_data.get('region', ''),
                    f"{region_data.get('percentage', 0)*100:.2f}%"
                ])
            writer.writerow([])

            # 写入洞察
            writer.writerow(['洞察', ''])
            insights = persona_data.get('insights', [])
            for idx, insight in enumerate(insights, 1):
                writer.writerow([idx, insight])

        return str(output_path)

    def _build_markdown_report(self, persona_data: Dict[str, Any]) -> str:
        """构建 Markdown 报告"""
        keyword = persona_data.get('keyword', '')
        sources = persona_data.get('sources', [])
        source_count = persona_data.get('source_count', 0)
        demographics = persona_data.get('demographics', {})
        core_persona = persona_data.get('core_persona', {})
        insights = persona_data.get('insights', [])
        aggregation_time = persona_data.get('metadata', {}).get('aggregation_time', '')

        # 格式化时间
        try:
            dt = datetime.fromisoformat(aggregation_time.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            formatted_time = aggregation_time

        # 构建报告
        report = f"""# 用户画像分析报告 - {keyword}

> 生成时间：{formatted_time}
> 数据源：{', '.join(sources)}（共 {source_count} 个）

---

## 📊 执行摘要

### 核心用户画像
{core_persona.get('user_profile', '')}

### 关键指标
- **主要年龄段**：{core_persona.get('primary_age', '')}（{core_persona.get('primary_age_pct', 0)}%）
- **性别比例**：{core_persona.get('gender_desc', '')}
- **核心地域**：{'、'.join(core_persona.get('top_regions', [])[:3])}
- **数据来源**：{source_count} 个数据源

### 核心发现
"""

        # 添加洞察
        for insight in insights:
            report += f"- {insight}\n"

        report += "\n---\n\n"

        # 添加年龄分布
        report += "## 👶 年龄分布\n\n"
        report += "| 年龄段 | 占比 | 特征描述 |\n"
        report += "|--------|------|----------|\n"

        age_descriptions = {
            '18-24': 'Z世代，学生/职场新人',
            '25-30': '职场青年，消费主力',
            '31-35': '职场中坚，家庭阶段',
            '36-40': '职场资深，稳定阶段',
            '40+': '资深用户，决策层'
        }

        age_dist = demographics.get('age', {})
        for age in ['18-24', '25-30', '31-35', '36-40', '40+']:
            percentage = age_dist.get(age, 0) * 100
            desc = age_descriptions.get(age, '')
            report += f"| {age}岁 | {percentage:.1f}% | {desc} |\n"

        # 添加性别分布
        report += "\n## ⚧ 性别分布\n\n"
        gender_dist = demographics.get('gender', {})
        male_pct = gender_dist.get('male', 0) * 100
        female_pct = gender_dist.get('female', 0) * 100
        report += f"- **男性**：{male_pct:.1f}%\n"
        report += f"- **女性**：{female_pct:.1f}%\n"
        report += f"- **性别特征**：{core_persona.get('gender_dominant', '')}\n"

        # 添加地域分布
        report += "\n## 🌍 地域分布\n\n"
        report += "### TOP 10 省份/城市\n\n"
        report += "| 排名 | 地域 | 占比 |\n"
        report += "|------|------|------|\n"

        region_dist = demographics.get('region', [])
        for region_data in region_dist[:10]:
            report += f"| {region_data.get('rank', '')} | {region_data.get('region', '')} | {region_data.get('percentage', 0)*100:.1f}% |\n"

        # 添加策略建议
        report += "\n## 💡 策略建议\n\n"

        # 内容策略
        primary_age = core_persona.get('primary_age', '25-30')
        content_strategy_map = {
            '18-24': {
                'tone': '轻松、幽默、互动性强',
                'format': '短视频、图文、表情包',
                'topics': '娱乐、二次元、游戏、潮流',
                'length': '短视频<30秒，图文<500字'
            },
            '25-30': {
                'tone': '共鸣、实用、有态度',
                'format': '中长视频、深度图文',
                'topics': '职场、情感、生活方式、个人成长',
                'length': '视频3-5分钟，图文800-1500字'
            },
            '31-35': {
                'tone': '专业、理性、有价值',
                'format': '深度图文、课程、直播',
                'topics': '育儿、理财、健康、职业发展',
                'length': '视频5-10分钟，图文1500-3000字'
            },
            '36-40': {
                'tone': '权威、深度、有洞见',
                'format': '深度文章、案例分析',
                'topics': '管理、投资、教育、行业洞察',
                'length': '视频10-20分钟，图文3000字以上'
            },
            '40+': {
                'tone': '稳重、可信、有温度',
                'format': '长文、音频、视频',
                'topics': '养生、旅游、时事、家庭',
                'length': '灵活，注重质量'
            }
        }

        strategy = content_strategy_map.get(primary_age, content_strategy_map['25-30'])

        report += "### 内容策略\n\n"
        report += f"- **内容调性**：{strategy['tone']}\n"
        report += f"- **内容形式**：{strategy['format']}\n"
        report += f"- **话题建议**：{strategy['topics']}\n"
        report += f"- **内容长度**：{strategy['length']}\n"

        # 平台策略
        report += "\n### 平台投放建议\n\n"

        top_regions = core_persona.get('top_regions', [])
        tier_1_pct = 0
        tier_1_regions = ['北京', '上海', '广州', '深圳']
        for region_data in region_dist:
            if region_data.get('region', '') in tier_1_regions:
                tier_1_pct += region_data.get('percentage', 0)

        if tier_1_pct > 0.5:
            report += f"- **一线城市用户占比高**（{tier_1_pct*100:.1f}%），用户消费能力强\n"
            report += "- **推荐平台**：知乎、B站、小红书\n"
        else:
            report += "- **推荐平台**：抖音、快手、今日头条\n"

        report += "\n---\n\n"
        report += "*本报告由 用户画像提取器 自动生成*\n"
        report += f"*数据来源：{', '.join(sources)}*\n"

        return report

    def _build_html_report(self, persona_data: Dict[str, Any]) -> str:
        """构建 HTML 可视化报告"""
        keyword = persona_data.get('keyword', '')
        sources = persona_data.get('sources', [])
        source_count = persona_data.get('source_count', 0)
        demographics = persona_data.get('demographics', {})
        core_persona = persona_data.get('core_persona', {})
        insights = persona_data.get('insights', [])

        # 准备图表数据
        age_data = demographics.get('age', {})
        age_labels = list(age_data.keys())
        age_values = [age_data[k] * 100 for k in age_labels]

        gender_data = demographics.get('gender', {})
        gender_labels = ['男性', '女性']
        gender_values = [
            gender_data.get('male', 0) * 100,
            gender_data.get('female', 0) * 100
        ]

        region_data = demographics.get('region', [])
        region_labels = [r['region'] for r in region_data[:10]]
        region_values = [r['percentage'] * 100 for r in region_data[:10]]

        # 构建 HTML
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>用户画像分析报告 - {keyword}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; }}
        .chart-container {{ position: relative; height: 300px; width: 100%; }}
    </style>
</head>
<body class="bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 py-8">
        <!-- 头部 -->
        <header class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">
                用户画像分析报告
            </h1>
            <p class="text-gray-600">关键词：{keyword}</p>
            <p class="text-sm text-gray-500">数据源：{', '.join(sources)}（共 {source_count} 个）</p>
        </header>

        <!-- 核心用户画像卡片 -->
        <section class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 class="text-2xl font-bold mb-4">👥 核心用户画像</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div class="bg-blue-50 rounded-lg p-4">
                    <p class="text-sm text-gray-600 mb-1">主要年龄段</p>
                    <p class="text-2xl font-bold text-blue-600">{core_persona.get('primary_age', '')}</p>
                    <p class="text-sm text-gray-500 mt-1">{core_persona.get('primary_age_pct', 0)}%</p>
                </div>
                <div class="bg-green-50 rounded-lg p-4">
                    <p class="text-sm text-gray-600 mb-1">性别比例</p>
                    <p class="text-xl font-bold text-green-600">
                        {core_persona.get('gender_desc', '')}
                    </p>
                </div>
                <div class="bg-purple-50 rounded-lg p-4">
                    <p class="text-sm text-gray-600 mb-1">核心地域</p>
                    <p class="text-lg font-bold text-purple-600">
                        {'、'.join(core_persona.get('top_regions', [])[:2])}
                    </p>
                </div>
                <div class="bg-orange-50 rounded-lg p-4">
                    <p class="text-sm text-gray-600 mb-1">数据源</p>
                    <p class="text-2xl font-bold text-orange-600">{source_count} 个</p>
                </div>
            </div>
        </section>

        <!-- 年龄分布图表 -->
        <section class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 class="text-2xl font-bold mb-4">👶 年龄分布</h2>
            <div class="chart-container">
                <canvas id="ageChart"></canvas>
            </div>
        </section>

        <!-- 性别和地域分布 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <!-- 性别分布 -->
            <section class="bg-white rounded-lg shadow-lg p-6">
                <h2 class="text-2xl font-bold mb-4">⚧ 性别分布</h2>
                <div class="chart-container">
                    <canvas id="genderChart"></canvas>
                </div>
            </section>

            <!-- 地域分布 TOP 10 -->
            <section class="bg-white rounded-lg shadow-lg p-6">
                <h2 class="text-2xl font-bold mb-4">🌍 地域分布 TOP 10</h2>
                <div class="chart-container">
                    <canvas id="regionChart"></canvas>
                </div>
            </section>
        </div>

        <!-- 洞察与建议 -->
        <section class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 class="text-2xl font-bold mb-4">💡 洞察与建议</h2>
            <div class="space-y-4">
"""

        # 添加洞察
        for insight in insights:
            html += f"""
                <div class="border-l-4 border-blue-500 pl-4 py-2">
                    <p class="text-gray-800">{insight}</p>
                </div>
"""

        html += """
            </div>
        </section>

        <!-- 页脚 -->
        <footer class="text-center text-sm text-gray-500 mt-8">
            <p>报告由 用户画像提取器 自动生成</p>
        </footer>
    </div>

    <!-- 图表脚本 -->
    <script>
        // 年龄分布饼图
        const ageCtx = document.getElementById('ageChart').getContext('2d');
        new Chart(ageCtx, {
            type: 'pie',
            data: {
                labels: """ + str(age_labels) + """,
                datasets: [{
                    data: """ + str(age_values) + """,
                    backgroundColor: [
                        '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right' },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed.toFixed(1) + '%';
                            }
                        }
                    }
                }
            }
        });

        // 性别分布饼图
        const genderCtx = document.getElementById('genderChart').getContext('2d');
        new Chart(genderCtx, {
            type: 'doughnut',
            data: {
                labels: """ + str(gender_labels) + """,
                datasets: [{
                    data: """ + str(gender_values) + """,
                    backgroundColor: ['#3B82F6', '#EC4899']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed.toFixed(1) + '%';
                            }
                        }
                    }
                }
            }
        });

        // 地域分布柱状图
        const regionCtx = document.getElementById('regionChart').getContext('2d');
        new Chart(regionCtx, {
            type: 'bar',
            data: {
                labels: """ + str(region_labels) + """,
                datasets: [{
                    label: '占比 (%)',
                    data: """ + str(region_values) + """,
                    backgroundColor: '#3B82F6'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return '占比: ' + context.parsed.y.toFixed(1) + '%';
                            }
                        }
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

        return html
