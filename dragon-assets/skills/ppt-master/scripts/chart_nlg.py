#!/usr/bin/env python3
"""
Chart Natural Language Generator

通过自然语言描述生成图表SVG
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class ChartType(Enum):
    """图表类型"""
    BAR = "bar"
    COLUMN = "column"
    LINE = "line"
    AREA = "area"
    PIE = "pie"
    DONUT = "donut"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    FUNNEL = "funnel"
    GANTT = "gantt"
    TIMELINE = "timeline"
    FLOW = "flow"
    PYRAMID = "pyramid"
    MINDMAP = "mind_map"
    SWOT = "swot"
    BCG = "bcg"
    COMPARISON = "comparison"
    OTHER = "other"


@dataclass
class DataSeries:
    """数据系列"""
    name: str
    values: list = field(default_factory=list)


@dataclass
class ChartSpec:
    """图表规格"""
    type: ChartType = ChartType.BAR
    title: str = ""
    categories: list = field(default_factory=list)
    series: list[DataSeries] = field(default_factory=list)
    style: str = "corporate"
    colors: list = field(default_factory=list)
    width: int = 800
    height: int = 600

    # 样式配置
    primary_color: str = "#1E3A5F"
    secondary_color: str = "#3182CE"
    accent_color: str = "#10B981"
    background_color: str = "#FFFFFF"
    text_color: str = "#1A202C"

    def __post_init__(self):
        if not self.colors:
            self.colors = [
                self.primary_color,
                self.secondary_color,
                self.accent_color,
                "#F59E0B",  # Amber
                "#8B5CF6",  # Purple
                "#EC4899",  # Pink
            ]


class NLUParser:
    """自然语言理解解析器"""

    def __init__(self):
        self.type_keywords = {
            'bar': ['对比', '对比图', '条形', '柱状', '柱形', '横向'],
            'column': ['柱状', '柱形', '竖向'],
            'line': ['趋势', '趋势图', '折线', '变化', '增长', '下降'],
            'area': ['累积', '面积', '堆积'],
            'pie': ['占比', '份额', '比例', '饼图', '圆形'],
            'donut': ['环形', '甜甜圈'],
            'scatter': ['分布', '散点', '相关'],
            'funnel': ['漏斗', '转化', '流程'],
            'gantt': ['甘特', '进度', '项目'],
            'timeline': ['时间线', '时间轴', '历史'],
            'flow': ['流程', '步骤', '工序'],
            'pyramid': ['金字塔', '层级', '层次'],
            'mind_map': ['思维导图', '脑图', '发散'],
            'swot': ['swot', 'swot分析'],
            'bcg': ['bcg', '矩阵', '投资组合'],
            'comparison': ['对比', '比较', '对照'],
        }

        self.style_keywords = {
            'corporate': ['企业', '商务', '正式', '专业'],
            'modern': ['现代', '时尚', '新颖'],
            'minimal': ['极简', '简约', '简单'],
            'dark': ['暗', '深色', '黑色'],
            'gradient': ['渐变', '彩色', '鲜艳'],
        }

    def parse(self, description: str, args: dict) -> ChartSpec:
        """解析自然语言描述"""
        spec = ChartSpec()

        # 解析类型
        desc_lower = description.lower()
        for chart_type, keywords in self.type_keywords.items():
            if any(kw in description for kw in keywords):
                spec.type = ChartType(chart_type)
                break

        # 从参数获取类型（优先级更高）
        if args.get('type'):
            try:
                spec.type = ChartType(args['type'])
            except ValueError:
                pass

        # 解析标题
        spec.title = args.get('title', '')
        if not spec.title:
            # 从描述中提取标题
            title_match = re.search(r'[一-龥a-zA-Z0-9\s]+', description)
            if title_match:
                spec.title = title_match.group().strip()

        # 解析数据
        data_str = args.get('data', '')
        if data_str:
            spec.series, spec.categories = self._parse_data(data_str)
        else:
            # 生成示例数据
            spec.categories = ['A', 'B', 'C', 'D']
            spec.series = [DataSeries(name='数据', values=[100, 150, 200, 120])]

        # 解析样式
        for style, keywords in self.style_keywords.items():
            if any(kw in description for kw in keywords):
                spec.style = style
                break

        if args.get('style'):
            spec.style = args['style']

        # 解析自定义颜色
        colors_str = args.get('colors', '')
        if colors_str:
            spec.colors = colors_str.split(',')

        # 应用样式配置
        self._apply_style(spec)

        return spec

    def _parse_data(self, data_str: str) -> tuple[list[DataSeries], list]:
        """解析数据字符串"""
        series = []
        categories = []

        # 尝试不同格式
        if '|' in data_str:
            # 键值对格式
            parts = data_str.split('|')
            for part in parts:
                if ':' in part:
                    key, value = part.split(':', 1)
                    categories.append(key.strip())
                    if series:
                        series[0].values.append(self._parse_number(value))
                    else:
                        series = [DataSeries(name='数据', values=[self._parse_number(value)])]
        elif ';' in data_str:
            # 列表格式
            parts = data_str.split(';')
            series_data = []
            for part in parts:
                series_data.append(self._parse_number(part))
            series = [DataSeries(name='数据', values=series_data)]
            categories = [str(i+1) for i in range(len(series_data))]
        elif ',' in data_str:
            # CSV格式
            parts = data_str.split(',')
            if ':' in data_str:
                # 多系列
                for part in parts:
                    if ':' in part:
                        name, values = part.split(':', 1)
                        values_list = [self._parse_number(v) for v in values.split(',')]
                        series.append(DataSeries(name=name.strip(), values=values_list))
            else:
                # 单系列
                values = [self._parse_number(v) for v in parts]
                series = [DataSeries(name='数据', values=values)]
                categories = [str(i+1) for i in range(len(values))]

        return series, categories

    def _parse_number(self, s: str) -> float:
        """解析数字"""
        s = s.strip()
        # 处理百分比
        if '%' in s:
            s = s.replace('%', '')
            return float(s)
        # 处理中文数字（简化）
        cn_map = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
                   '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'}
        for k, v in cn_map.items():
            s = s.replace(k, v)
        # 提取数字
        match = re.search(r'[\d.]+', s)
        if match:
            return float(match.group())
        return 0.0

    def _apply_style(self, spec: ChartSpec):
        """应用样式配置"""
        style_configs = {
            'corporate': {
                'primary': '#1E3A5F',
                'secondary': '#3182CE',
                'accent': '#10B981',
                'background': '#FFFFFF',
                'text': '#1A202C',
            },
            'modern': {
                'primary': '#667EEA',
                'secondary': '#764BA2',
                'accent': '#F59E0B',
                'background': '#FFFFFF',
                'text': '#1A202C',
            },
            'minimal': {
                'primary': '#1A202C',
                'secondary': '#4A5568',
                'accent': '#718096',
                'background': '#FFFFFF',
                'text': '#1A202C',
            },
            'dark': {
                'primary': '#60A5FA',
                'secondary': '#34D399',
                'accent': '#F59E0B',
                'background': '#1A202C',
                'text': '#F7FAFC',
            },
            'gradient': {
                'primary': '#FF6B6B',
                'secondary': '#4ECDC4',
                'accent': '#45B7D1',
                'background': '#FFFFFF',
                'text': '#1A202C',
            },
        }

        config = style_configs.get(spec.style, style_configs['corporate'])
        spec.primary_color = config['primary']
        spec.secondary_color = config['secondary']
        spec.accent_color = config['accent']
        spec.background_color = config['background']
        spec.text_color = config['text']


class ChartGenerator:
    """图表生成器"""

    def __init__(self):
        self.parser = NLUParser()

    def generate(self, description: str, args: dict) -> str:
        """生成SVG图表"""
        spec = self.parser.parse(description, args)

        generators = {
            ChartType.BAR: self._generate_bar,
            ChartType.COLUMN: self._generate_column,
            ChartType.LINE: self._generate_line,
            ChartType.AREA: self._generate_area,
            ChartType.PIE: self._generate_pie,
            ChartType.DONUT: self._generate_donut,
        }

        generator = generators.get(spec.type, self._generate_bar)
        return generator(spec)

    def _generate_column(self, spec: ChartSpec) -> str:
        """生成柱状图"""
        view_box = f"0 0 {spec.width} {spec.height}"
        padding = {'top': 60, 'right': 40, 'bottom': 60, 'left': 60}
        chart_width = spec.width - padding['left'] - padding['right']
        chart_height = spec.height - padding['top'] - padding['bottom']

        # 计算柱子
        num_categories = len(spec.categories)
        num_series = len(spec.series)
        total_groups = num_categories
        group_width = chart_width / total_groups if total_groups > 0 else chart_width
        bar_width = group_width * 0.6 / num_series if num_series > 0 else group_width * 0.6
        bar_gap = group_width * 0.4 / (num_series + 1) if num_series > 0 else group_width * 0.4

        # 计算比例
        all_values = [v for s in spec.series for v in s.values]
        max_value = max(all_values) if all_values else 100
        min_value = min(0, min(all_values))

        # 生成柱子
        rects = []
        for si, series in enumerate(spec.series):
            for ci, value in enumerate(series.values):
                x = padding['left'] + ci * group_width + bar_gap * (si + 1) + si * bar_width
                height = (value - min_value) / (max_value - min_value) * chart_height if max_value != min_value else chart_height / 2
                y = padding['top'] + chart_height - height
                color = spec.colors[si % len(spec.colors)]
                rects.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{height:.1f}" fill="{color}" rx="4"/>')

        # 生成标签
        labels = []
        for ci, cat in enumerate(spec.categories):
            x = padding['left'] + ci * group_width + group_width / 2
            y = spec.height - padding['bottom'] + 20
            labels.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" fill="{spec.text_color}" font-size="12">{cat}</text>')

        # 生成Y轴刻度
        y_ticks = []
        num_ticks = 5
        tick_step = max_value / num_ticks
        for i in range(num_ticks + 1):
            value = i * tick_step
            y = padding['top'] + chart_height - (i / num_ticks) * chart_height
            y_ticks.append(f'<text x="{padding["left"] - 10}" y="{y:.1f}" text-anchor="end" fill="{spec.text_color}" font-size="11">{value:.0f}</text>')
            y_ticks.append(f'<line x1="{padding["left"]}" y1="{y:.1f}" x2="{spec.width - padding["right"]}" y2="{y:.1f}" stroke="{spec.text_color}" stroke-opacity="0.2" stroke-dasharray="4"/>')

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}">
  <rect width="{spec.width}" height="{spec.height}" fill="{spec.background_color}"/>
  <text x="{spec.width/2}" y="35" text-anchor="middle" fill="{spec.text_color}" font-size="18" font-weight="bold">{spec.title}</text>
  <line x1="{padding['left']}" y1="{padding['top']}" x2="{padding['left']}" y2="{spec.height - padding['bottom']}" stroke="{spec.text_color}" stroke-opacity="0.3"/>
  <line x1="{padding['left']}" y1="{spec.height - padding['bottom']}" x2="{spec.width - padding['right']}" y2="{spec.height - padding['bottom']}" stroke="{spec.text_color}" stroke-opacity="0.3"/>
  {chr(10).join(y_ticks)}
  {chr(10).join(rects)}
  {chr(10).join(labels)}
</svg>'''

    def _generate_bar(self, spec: ChartSpec) -> str:
        """生成条形图（横向柱状图）"""
        # 复用柱状图，但交换宽高逻辑
        spec.width, spec.height = spec.height, spec.width
        return self._generate_column(spec).replace(
            f'viewBox="0 0 {spec.height} {spec.width}"',
            f'viewBox="0 0 {spec.width} {spec.height}"'
        ).replace(
            f'width="{spec.height}" height="{spec.width}"',
            f'width="{spec.width}" height="{spec.height}"'
        )

    def _generate_line(self, spec: ChartSpec) -> str:
        """生成折线图"""
        view_box = f"0 0 {spec.width} {spec.height}"
        padding = {'top': 60, 'right': 40, 'bottom': 60, 'left': 60}
        chart_width = spec.width - padding['left'] - padding['right']
        chart_height = spec.height - padding['top'] - padding['bottom']

        # 计算点
        num_points = len(spec.categories)
        point_gap = chart_width / (num_points - 1) if num_points > 1 else chart_width

        all_values = [v for s in spec.series for v in s.values]
        max_value = max(all_values) if all_values else 100
        min_value = min(0, min(all_values))

        points_list = []
        for si, series in enumerate(spec.series):
            points = []
            for ci, value in enumerate(series.values):
                x = padding['left'] + ci * point_gap
                y = padding['top'] + chart_height - (value - min_value) / (max_value - min_value) * chart_height if max_value != min_value else padding['top'] + chart_height / 2
                points.append(f"{x:.1f},{y:.1f}")
            points_list.append((series.name, points, spec.colors[si % len(spec.colors)]))

        # 生成线
        lines = []
        for name, points, color in points_list:
            polyline_points = ' '.join(points)
            lines.append(f'<polyline points="{polyline_points}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
            # 生成点
            for point in points:
                x, y = point.split(',')
                lines.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{color}"/>')

        # 生成X轴标签
        labels = []
        for ci, cat in enumerate(spec.categories):
            x = padding['left'] + ci * point_gap
            y = spec.height - padding['bottom'] + 20
            labels.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" fill="{spec.text_color}" font-size="12">{cat}</text>')

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}">
  <rect width="{spec.width}" height="{spec.height}" fill="{spec.background_color}"/>
  <text x="{spec.width/2}" y="35" text-anchor="middle" fill="{spec.text_color}" font-size="18" font-weight="bold">{spec.title}</text>
  <line x1="{padding['left']}" y1="{padding['top']}" x2="{padding['left']}" y2="{spec.height - padding['bottom']}" stroke="{spec.text_color}" stroke-opacity="0.3"/>
  <line x1="{padding['left']}" y1="{spec.height - padding['bottom']}" x2="{spec.width - padding['right']}" y2="{spec.height - padding['bottom']}" stroke="{spec.text_color}" stroke-opacity="0.3"/>
  {chr(10).join(lines)}
  {chr(10).join(labels)}
</svg>'''

    def _generate_pie(self, spec: ChartSpec) -> str:
        """生成饼图"""
        view_box = f"0 0 {spec.width} {spec.height}"
        cx, cy = spec.width / 2, spec.height / 2
        radius = min(spec.width, spec.height) / 2 - 60

        all_values = [v for s in spec.series for v in s.values]
        total = sum(all_values) if all_values else 1

        # 计算扇形
        paths = []
        current_angle = -90  # 从顶部开始
        for si, series in enumerate(spec.series):
            for ci, value in enumerate(series.values):
                if total > 0:
                    angle = (value / total) * 360
                else:
                    angle = 0

                start_angle = current_angle
                end_angle = current_angle + angle

                start_rad = start_angle * 3.14159 / 180
                end_rad = end_angle * 3.14159 / 180

                x1 = cx + radius * (1 + 0.1 * (si % 2 - 0.5)) * _cos(start_rad)
                y1 = cy + radius * (1 + 0.1 * (si % 2 - 0.5)) * _sin(start_rad)
                x2 = cx + radius * (1 + 0.1 * (si % 2 - 0.5)) * _cos(end_rad)
                y2 = cy + radius * (1 + 0.1 * (si % 2 - 0.5)) * _sin(end_rad)

                large_arc = 1 if angle > 180 else 0

                path = f'M {cx} {cy} L {x1:.1f} {y1:.1f} A {radius} {radius} 0 {large_arc} 1 {x2:.1f} {y2:.1f} Z'
                color = spec.colors[(si + ci) % len(spec.colors)]
                paths.append(f'<path d="{path}" fill="{color}"/>')

                # 标签
                label_angle = (start_angle + angle / 2) * 3.14159 / 180
                label_radius = radius * 0.7
                lx = cx + label_radius * _cos(label_angle)
                ly = cy + label_radius * _sin(label_angle)
                percentage = value / total * 100 if total > 0 else 0
                paths.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="bold">{percentage:.0f}%</text>')

                current_angle = end_angle

        return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}">
  <rect width="{spec.width}" height="{spec.height}" fill="{spec.background_color}"/>
  <text x="{spec.width/2}" y="35" text-anchor="middle" fill="{spec.text_color}" font-size="18" font-weight="bold">{spec.title}</text>
  {chr(10).join(paths)}
</svg>'''

    def _generate_donut(self, spec: ChartSpec) -> str:
        """生成环形图"""
        svg = self._generate_pie(spec)
        # 在中心添加一个白色圆形
        svg = svg.replace('</svg>', '<circle cx="400" cy="300" r="150" fill="{bg}"/></svg>'.format(bg=spec.background_color))
        return svg

    def _generate_area(self, spec: ChartSpec) -> str:
        """生成面积图（复用折线图）"""
        svg = self._generate_line(spec)
        # TODO: 添加面积填充
        return svg


def _cos(angle: float) -> float:
    import math
    return math.cos(angle)


def _sin(angle: float) -> float:
    import math
    return math.sin(angle)


def main():
    parser = argparse.ArgumentParser(
        description='通过自然语言生成图表SVG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python chart_nlg.py "显示季度销售对比柱状图"
  python chart_nlg.py "展示用户增长趋势" --type line --output chart.svg
  python chart_nlg.py "市场份额占比" --type pie --title "市场份额" --data "A:30|B:25|C:20|D:25"
        '''
    )

    parser.add_argument('description', help='图表的自然语言描述')
    parser.add_argument('--type', '-t', help='图表类型 (bar/column/line/pie/donut)')
    parser.add_argument('--title', help='图表标题')
    parser.add_argument('--data', '-d', help='数据内容')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--style', '-s', default='corporate',
                       choices=['corporate', 'modern', 'minimal', 'dark', 'gradient'],
                       help='图表风格')
    parser.add_argument('--colors', '-c', help='自定义颜色（逗号分隔HEX值）')
    parser.add_argument('--width', type=int, default=800, help='SVG宽度')
    parser.add_argument('--height', type=int, default=600, help='SVG高度')
    parser.add_argument('--format', '-f', choices=['svg', 'json'], default='svg',
                       help='输出格式')

    args = parser.parse_args()

    # 解析参数
    parsed_args = {
        'type': args.type,
        'title': args.title,
        'data': args.data,
        'style': args.style,
        'colors': args.colors,
    }

    # 生成图表
    generator = ChartGenerator()
    svg_content = generator.generate(args.description, parsed_args)

    # 输出
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(svg_content, encoding='utf-8')
        print(f"✅ 图表已保存: {output_path}")
    else:
        print(svg_content)


if __name__ == '__main__':
    main()
