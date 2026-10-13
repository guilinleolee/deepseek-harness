#!/usr/bin/env python3
"""
PPT Templates Index Generator

列出所有可用的PPT模板，品牌预设和图表
"""

import argparse
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class TemplateType(Enum):
    """模板类型"""
    BRAND = "brand"
    LAYOUT = "layout"
    CHART = "chart"
    ALL = "all"


@dataclass
class BrandTemplate:
    """品牌预设"""
    id: str
    name: str
    summary: str
    primary_color: str
    path: Path
    use_cases: list = field(default_factory=list)
    tone: str = ""
    typography: str = ""
    logo: str = ""


@dataclass
class LayoutTemplate:
    """布局模板"""
    id: str
    name: str
    summary: str
    page_count: int
    page_types: list
    canvas_format: str
    path: Path


@dataclass
class ChartTemplate:
    """图表模板"""
    id: str
    name: str
    summary: str
    category: str
    path: Path


@dataclass
class TemplateIndex:
    """模板索引"""
    brands: list[BrandTemplate] = field(default_factory=list)
    layouts: list[LayoutTemplate] = field(default_factory=list)
    charts: list[ChartTemplate] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.brands) + len(self.layouts) + len(self.charts)


class TemplateLister:
    """模板列表生成器"""

    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.index = TemplateIndex()

    def load_all(self):
        """加载所有模板"""
        self._load_brands()
        self._load_layouts()
        self._load_charts()

    def _load_brands(self):
        """加载品牌预设"""
        brands_dir = self.templates_dir / "brands"
        if not brands_dir.exists():
            return

        # 读取品牌索引
        index_file = brands_dir / "brands_index.json"
        if index_file.exists():
            with open(index_file, encoding='utf-8') as f:
                data = json.load(f)
                for brand_id, info in data.items():
                    self.index.brands.append(BrandTemplate(
                        id=brand_id,
                        name=info.get("name", brand_id),
                        summary=info.get("summary", ""),
                        primary_color=info.get("primary_color", "#000000"),
                        path=brands_dir / brand_id
                    ))

        # 如果没有索引文件，扫描目录
        if not self.index.brands:
            for brand_dir in brands_dir.iterdir():
                if brand_dir.is_dir():
                    self.index.brands.append(BrandTemplate(
                        id=brand_dir.name,
                        name=brand_dir.name,
                        summary="",
                        primary_color="#000000",
                        path=brand_dir
                    ))

    def _load_layouts(self):
        """加载布局模板"""
        layouts_dir = self.templates_dir / "layouts"
        if not layouts_dir.exists():
            return

        # 读取布局索引
        index_file = layouts_dir / "layouts_index.json"
        if index_file.exists():
            with open(index_file, encoding='utf-8') as f:
                data = json.load(f)
                for layout_id, info in data.items():
                    self.index.layouts.append(LayoutTemplate(
                        id=layout_id,
                        name=info.get("name", layout_id),
                        summary=info.get("summary", ""),
                        page_count=info.get("page_count", 0),
                        page_types=info.get("page_types", []),
                        canvas_format=info.get("canvas_format", "ppt169"),
                        path=layouts_dir / layout_id
                    ))

        # 如果没有索引文件，扫描目录
        if not self.index.layouts:
            for layout_dir in layouts_dir.iterdir():
                if layout_dir.is_dir():
                    self.index.layouts.append(LayoutTemplate(
                        id=layout_dir.name,
                        name=layout_dir.name,
                        summary="",
                        page_count=0,
                        page_types=[],
                        canvas_format="ppt169",
                        path=layout_dir
                    ))

    def _load_charts(self):
        """加载图表模板"""
        charts_dir = self.templates_dir / "charts"
        if not charts_dir.exists():
            return

        # 读取图表索引
        index_file = charts_dir / "charts_index.json"
        if index_file.exists():
            with open(index_file, encoding='utf-8') as f:
                data = json.load(f)
                charts_data = data.get("charts", {})
                for chart_id, info in charts_data.items():
                    self.index.charts.append(ChartTemplate(
                        id=chart_id,
                        name=info.get("name", chart_id),
                        summary=info.get("summary", ""),
                        category=info.get("category", "其他"),
                        path=charts_dir / f"{chart_id}.svg"
                    ))

        # 如果没有索引文件，扫描SVG文件
        if not self.index.charts:
            for chart_file in charts_dir.glob("*.svg"):
                chart_id = chart_file.stem
                # 根据文件名推断分类
                category = self._infer_chart_category(chart_id)
                self.index.charts.append(ChartTemplate(
                    id=chart_id,
                    name=chart_id.replace("_", " ").title(),
                    summary="",
                    category=category,
                    path=chart_file
                ))

    def _infer_chart_category(self, chart_id: str) -> str:
        """根据ID推断图表分类"""
        chart_id_lower = chart_id.lower()

        if any(k in chart_id_lower for k in ["area", "line", "bar", "column", "pie", "donut", "scatter", "bubble", "funnel", "gantt", "timeline"]):
            if "area" in chart_id_lower:
                return "时间序列"
            elif "line" in chart_id_lower:
                return "时间序列"
            elif "bar" in chart_id_lower or "column" in chart_id_lower:
                return "比较类"
            elif "pie" in chart_id_lower or "donut" in chart_id_lower:
                return "占比类"
            elif "scatter" in chart_id_lower or "bubble" in chart_id_lower:
                return "分布类"
            elif "funnel" in chart_id_lower or "gantt" in chart_id_lower:
                return "流程类"
            else:
                return "图表类"

        elif any(k in chart_id_lower for k in ["flow", "step", "process", "cycle", "hub", "wheel", "pyramid", "tree", "matrix", "quadrant"]):
            if "flow" in chart_id_lower or "step" in chart_id_lower or "process" in chart_id_lower:
                return "流程图"
            elif "cycle" in chart_id_lower or "wheel" in chart_id_lower:
                return "循环图"
            elif "pyramid" in chart_id_lower or "tree" in chart_id_lower:
                return "层级图"
            elif "matrix" in chart_id_lower or "quadrant" in chart_id_lower:
                return "矩阵图"
            else:
                return "信息图"

        elif any(k in chart_id_lower for k in ["swot", "bcg", "pest", "okr", "comparison", "pros_cons"]):
            return "框架类"

        elif any(k in chart_id_lower for k in ["icon", "table", "mind_map", "journey", "fishbone"]):
            return "图示类"

        return "其他"

    def search(self, keyword: str, template_type: TemplateType = TemplateType.ALL) -> TemplateIndex:
        """搜索模板"""
        result = TemplateIndex()
        keyword_lower = keyword.lower()

        def match(text: str) -> bool:
            return keyword_lower in text.lower()

        if template_type in (TemplateType.ALL, TemplateType.BRAND):
            result.brands = [
                b for b in self.index.brands
                if match(b.id) or match(b.name) or match(b.summary)
            ]

        if template_type in (TemplateType.ALL, TemplateType.LAYOUT):
            result.layouts = [
                l for l in self.index.layouts
                if match(l.id) or match(l.name) or match(l.summary)
            ]

        if template_type in (TemplateType.ALL, TemplateType.CHART):
            result.charts = [
                c for c in self.index.charts
                if match(c.id) or match(c.name) or match(c.summary)
            ]

        return result


def format_ascii(index: TemplateIndex, template_type: TemplateType = TemplateType.ALL,
                 verbose: bool = False) -> str:
    """格式化为ASCII表格"""
    lines = []

    lines.append("═" * 70)
    lines.append("  PPT 模板索引")
    lines.append("═" * 70)

    # 品牌预设
    if template_type in (TemplateType.ALL, TemplateType.BRAND) and index.brands:
        lines.append("")
        lines.append(f"📁 品牌预设 ({len(index.brands)})")
        lines.append("─" * 70)
        for brand in index.brands:
            if verbose:
                lines.append(f"  {brand.id}")
                lines.append(f"    名称: {brand.name}")
                lines.append(f"    描述: {brand.summary}")
                lines.append(f"    主色: {brand.primary_color}")
                lines.append(f"    路径: {brand.path}")
            else:
                summary = brand.summary[:30] + "..." if len(brand.summary) > 30 else brand.summary
                lines.append(f"  ├── {brand.id}")
                lines.append(f"  │   └── {summary} | {brand.primary_color}")
        lines.append("")

    # 布局模板
    if template_type in (TemplateType.ALL, TemplateType.LAYOUT) and index.layouts:
        lines.append(f"📁 布局模板 ({len(index.layouts)})")
        lines.append("─" * 70)
        for layout in index.layouts:
            if verbose:
                lines.append(f"  {layout.id}")
                lines.append(f"    名称: {layout.name}")
                lines.append(f"    描述: {layout.summary}")
                lines.append(f"    页数: {layout.page_count}")
                lines.append(f"    页面类型: {', '.join(layout.page_types)}")
                lines.append(f"    路径: {layout.path}")
            else:
                summary = layout.summary[:25] + "..." if len(layout.summary) > 25 else layout.summary
                lines.append(f"  ├── {layout.id}")
                lines.append(f"  │   └── {layout.page_count}页 | {summary}")
        lines.append("")

    # 图表模板
    if template_type in (TemplateType.ALL, TemplateType.CHART) and index.charts:
        # 按分类分组
        categories = {}
        for chart in index.charts:
            if chart.category not in categories:
                categories[chart.category] = []
            categories[chart.category].append(chart)

        lines.append(f"📊 图表模板 ({len(index.charts)})")
        lines.append("─" * 70)

        for category, charts in categories.items():
            lines.append(f"  📂 {category} ({len(charts)})")
            for chart in charts[:10]:  # 只显示前10个
                lines.append(f"      ├── {chart.id}")
            if len(charts) > 10:
                lines.append(f"      └── ... 还有 {len(charts) - 10} 个")

        lines.append("")

    # 统计
    lines.append("─" * 70)
    lines.append(f"  总计: {index.total} 个模板")
    lines.append("═" * 70)

    return "\n".join(lines)


def format_json(index: TemplateIndex) -> str:
    """格式化为JSON"""
    data = {
        "total": index.total,
        "brands": [
            {
                "id": b.id,
                "name": b.name,
                "summary": b.summary,
                "primary_color": b.primary_color,
                "path": str(b.path)
            }
            for b in index.brands
        ],
        "layouts": [
            {
                "id": l.id,
                "name": l.name,
                "summary": l.summary,
                "page_count": l.page_count,
                "page_types": l.page_types,
                "canvas_format": l.canvas_format,
                "path": str(l.path)
            }
            for l in index.layouts
        ],
        "charts": [
            {
                "id": c.id,
                "name": c.name,
                "summary": c.summary,
                "category": c.category,
                "path": str(c.path)
            }
            for c in index.charts
        ]
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_markdown(index: TemplateIndex) -> str:
    """格式化为Markdown"""
    lines = []

    lines.append("# PPT 模板索引\n")

    # 品牌预设
    if index.brands:
        lines.append("## 📁 品牌预设\n")
        lines.append(f"| ID | 名称 | 描述 | 主色 |")
        lines.append("|---|---|---|---|")
        for brand in index.brands:
            lines.append(f"| `{brand.id}` | {brand.name} | {brand.summary[:40]}... | {brand.primary_color} |")
        lines.append("")

    # 布局模板
    if index.layouts:
        lines.append("## 📁 布局模板\n")
        lines.append(f"| ID | 名称 | 描述 | 页数 | 页面类型 |")
        lines.append("|---|---|---|---|---|")
        for layout in index.layouts:
            page_types = ", ".join(layout.page_types[:3])
            lines.append(f"| `{layout.id}` | {layout.name} | {layout.summary[:30]}... | {layout.page_count} | {page_types}... |")
        lines.append("")

    # 图表模板
    if index.charts:
        # 按分类分组
        categories = {}
        for chart in index.charts:
            if chart.category not in categories:
                categories[chart.category] = []
            categories[chart.category].append(chart)

        lines.append("## 📊 图表模板\n")
        for category, charts in categories.items():
            lines.append(f"### {category} ({len(charts)})\n")
            chart_list = ", ".join([f"`{c.id}`" for c in charts[:20]])
            if len(charts) > 20:
                chart_list += f", ... 还有 {len(charts) - 20} 个"
            lines.append(chart_list)
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='列出所有可用的PPT模板',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--type', '-t', choices=['brand', 'layout', 'chart', 'all'],
                       default='all', help='模板类型')
    parser.add_argument('--search', '-s', help='关键词搜索')
    parser.add_argument('--format', '-f', choices=['ascii', 'json', 'markdown'],
                       default='ascii', help='输出格式')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--path', '-p', help='模板目录路径',
                        default='templates')

    args = parser.parse_args()

    # 确定模板目录
    script_dir = Path(__file__).parent
    templates_dir = script_dir.parent / args.path

    if not templates_dir.exists():
        # 尝试从skill目录查找
        skill_dir = script_dir.parent
        templates_dir = skill_dir / "templates"
        if not templates_dir.exists():
            print(f"错误: 找不到模板目录 {templates_dir}", file=sys.stderr)
            sys.exit(1)

    # 加载模板
    lister = TemplateLister(templates_dir)
    lister.load_all()

    # 搜索
    if args.search:
        index = lister.search(args.search, TemplateType(args.type))
    else:
        index = TemplateIndex()
        template_type = TemplateType(args.type)

        if template_type in (TemplateType.ALL, TemplateType.BRAND):
            index.brands = lister.index.brands
        if template_type in (TemplateType.ALL, TemplateType.LAYOUT):
            index.layouts = lister.index.layouts
        if template_type in (TemplateType.ALL, TemplateType.CHART):
            index.charts = lister.index.charts

    # 输出
    if index.total == 0:
        print("未找到匹配的模板")
        sys.exit(0)

    if args.format == 'json':
        print(format_json(index))
    elif args.format == 'markdown':
        print(format_markdown(index))
    else:
        print(format_ascii(index, TemplateType(args.type), args.verbose))


if __name__ == '__main__':
    main()
