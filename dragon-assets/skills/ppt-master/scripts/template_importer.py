#!/usr/bin/env python3
"""
PPT Template Importer

从外部PPT/PDF提取品牌元素并导入到天龙引擎模板库
"""

import argparse
import json
import re
import sys
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class ExtractedColors:
    """提取的颜色"""
    primary: str = "#000000"
    secondary: str = "#666666"
    accent: str = "#007BFF"
    background: str = "#FFFFFF"
    text: list = None

    def __post_init__(self):
        if self.text is None:
            self.text = []


@dataclass
class ExtractedFonts:
    """提取的字体"""
    fonts: list = None

    def __post_init__(self):
        if self.fonts is None:
            self.fonts = []


@dataclass
class ExtractedLogo:
    """提取的Logo"""
    filename: str
    path: Path
    usage: str = "primary"


@dataclass
class ImportResult:
    """导入结果"""
    success: bool
    template_name: str
    output_path: Path
    colors: Optional[ExtractedColors] = None
    fonts: Optional[ExtractedFonts] = None
    logos: list = None
    errors: list = None
    warnings: list = None

    def __post_init__(self):
        if self.logos is None:
            self.logos = []
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class ColorExtractor:
    """颜色提取器"""

    def __init__(self):
        self.colors = ExtractedColors()

    def extract_from_pptx(self, pptx_path: Path) -> ExtractedColors:
        """从PPTX提取颜色"""
        try:
            with zipfile.ZipFile(pptx_path, 'r') as z:
                # 读取主题颜色
                theme_path = 'ppt/theme/theme1.xml'
                if theme_path in z.namelist():
                    theme_content = z.read(theme_path).decode('utf-8')
                    self._parse_theme_colors(theme_content)

                # 读取幻灯片母版
                slide_master_paths = [n for n in z.namelist()
                                    if 'slideMasters/slideMaster' in n]
                for master_path in slide_master_paths[:1]:
                    master_content = z.read(master_path).decode('utf-8')
                    self._parse_master_colors(master_content)

        except Exception as e:
            print(f"警告: 颜色提取失败 - {e}")

        return self.colors

    def _parse_theme_colors(self, content: str):
        """解析主题颜色"""
        # 提取主要颜色
        color_patterns = [
            (r'clrScheme>.*?<a:dk1.*?srgbClr val="([^"]+)"', 'text'),
            (r'clrScheme>.*?<a:lt1.*?srgbClr val="([^"]+)"', 'background'),
            (r'clrScheme>.*?<a:accent1.*?srgbClr val="([^"]+)"', 'primary'),
        ]

        for pattern, target in color_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                color = "#" + match.group(1)
                setattr(self.colors, target, color)

    def _parse_master_colors(self, content: str):
        """解析母版颜色"""
        # 提取背景色
        bg_match = re.search(r'bg>.*?solidFill.*?srgbClr val="([^"]+)"', content)
        if bg_match:
            self.colors.background = "#" + bg_match.group(1)

        # 提取文本色
        text_matches = re.findall(r'solidFill.*?srgbClr val="([^"]+)"', content)
        if text_matches:
            self.colors.text = ["#" + c for c in text_matches[:3]]


class FontExtractor:
    """字体提取器"""

    def __init__(self):
        self.fonts = ExtractedFonts()

    def extract_from_pptx(self, pptx_path: Path) -> ExtractedFonts:
        """从PPTX提取字体"""
        try:
            with zipfile.ZipFile(pptx_path, 'r') as z:
                # 读取主题字体
                theme_path = 'ppt/theme/theme1.xml'
                if theme_path in z.namelist():
                    theme_content = z.read(theme_path).decode('utf-8')
                    self._parse_theme_fonts(theme_content)

                # 读取幻灯片
                slide_paths = [n for n in z.namelist()
                              if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
                for slide_path in slide_paths[:3]:
                    slide_content = z.read(slide_path).decode('utf-8')
                    self._parse_slide_fonts(slide_content)

        except Exception as e:
            print(f"警告: 字体提取失败 - {e}")

        return self.fonts

    def _parse_theme_fonts(self, content: str):
        """解析主题字体"""
        # 提取字体方案
        font_patterns = [
            (r'<a:majorFont.*?typeface="([^"]+)"', '标题字体'),
            (r'<a:minorFont.*?typeface="([^"]+)"', '正文字体'),
        ]

        for pattern, usage in font_patterns:
            match = re.search(pattern, content)
            if match:
                self.fonts.fonts.append({
                    "name": match.group(1),
                    "usage": usage,
                    "confidence": 0.95
                })

    def _parse_slide_fonts(self, content: str):
        """解析幻灯片字体"""
        font_matches = re.findall(r'typeface="([^"]+)"', content)
        seen = {f.get('name') for f in self.fonts.fonts}

        for font_name in font_matches[:5]:
            if font_name not in seen:
                self.fonts.fonts.append({
                    "name": font_name,
                    "usage": "幻灯片",
                    "confidence": 0.7
                })
                seen.add(font_name)


class LogoExtractor:
    """Logo提取器"""

    def extract_from_pptx(self, pptx_path: Path, output_dir: Path) -> list[ExtractedLogo]:
        """从PPTX提取Logo"""
        logos = []
        assets_dir = output_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(pptx_path, 'r') as z:
                # 查找媒体文件
                media_files = [n for n in z.namelist()
                              if n.startswith('ppt/media/')]

                for i, media_path in enumerate(media_files[:3]):
                    filename = Path(media_path).name
                    output_file = assets_dir / filename

                    # 复制文件
                    with z.open(media_path) as src:
                        output_file.write_bytes(src.read())

                    logos.append(ExtractedLogo(
                        filename=filename,
                        path=output_file,
                        usage="主要Logo" if i == 0 else f"Logo {i+1}"
                    ))

        except Exception as e:
            print(f"警告: Logo提取失败 - {e}")

        return logos


class TemplateImporter:
    """模板导入器"""

    def __init__(self, source_path: Path, template_name: str,
                 template_type: str = "brand"):
        self.source_path = source_path
        self.template_name = template_name
        self.template_type = template_type
        self.result = ImportResult(
            success=False,
            template_name=template_name,
            output_path=None
        )

    def import_template(self, output_base: Path) -> ImportResult:
        """执行模板导入"""
        # 确定输出目录
        type_dir = f"{self.template_type}s"  # brands/layouts/decks
        output_dir = output_base / type_dir / self.template_name
        self.result.output_path = output_dir

        try:
            # 创建目录
            output_dir.mkdir(parents=True, exist_ok=True)
            (output_dir / "assets").mkdir(exist_ok=True)

            # 提取元素
            if self.source_path.suffix.lower() == '.pptx':
                self._extract_from_pptx(output_dir)
            elif self.source_path.suffix.lower() == '.pdf':
                self._extract_from_pdf(output_dir)
            else:
                self._extract_from_image(output_dir)

            # 生成设计规范
            self._generate_design_spec(output_dir)

            # 生成颜色配置
            self._generate_colors_json(output_dir)

            # 生成字体配置
            self._generate_fonts_json(output_dir)

            self.result.success = True

        except Exception as e:
            self.result.errors.append(str(e))

        return self.result

    def _extract_from_pptx(self, output_dir: Path):
        """从PPTX提取"""
        color_extractor = ColorExtractor()
        self.result.colors = color_extractor.extract_from_pptx(self.source_path)

        font_extractor = FontExtractor()
        self.result.fonts = font_extractor.extract_from_pptx(self.source_path)

        logo_extractor = LogoExtractor()
        self.result.logos = logo_extractor.extract_from_pptx(
            self.source_path, output_dir)

    def _extract_from_pdf(self, output_dir: Path):
        """从PDF提取（基础实现）"""
        self.result.warnings.append("PDF提取功能需要额外依赖（如PyMuPDF）")
        self.result.colors = ExtractedColors()

    def _extract_from_image(self, output_dir: Path):
        """从图片提取（基础实现）"""
        self.result.warnings.append("图片提取功能需要额外依赖（如Pillow）")
        self.result.colors = ExtractedColors()

    def _generate_design_spec(self, output_dir: Path):
        """生成设计规范文档"""
        colors = self.result.colors or ExtractedColors()
        fonts = self.result.fonts or ExtractedFonts()

        spec_content = f'''---
{self.template_type}_id: {self.template_name}
kind: {self.template_type}
summary: Imported from {self.source_path.name}
primary_color: {colors.primary}
---

# Brand Overview

| Property | Value |
|---|---|
| Brand Name | {self.template_name} |
| Source | {self.source_path.name} |
| Import Date | Auto-generated |

## Color Scheme

| Role | HEX | Usage |
|---|---|---|
| Primary | {colors.primary} | Main brand color |
| Secondary | {colors.secondary} | Secondary elements |
| Accent | {colors.accent} | Highlights and CTAs |
| Background | {colors.background} | Page backgrounds |
'''

        # 添加文本颜色
        if colors.text:
            for i, text_color in enumerate(colors.text, 1):
                spec_content += f"| Text {i} | {text_color} | Body text |\n"

        spec_content += "\n## Typography\n\n"
        for font in fonts.fonts[:5]:
            spec_content += f"| {font['usage']} | {font['name']} | {font.get('confidence', 0)*100:.0f}% |\n"

        if self.result.logos:
            spec_content += "\n## Logo\n\n"
            for logo in self.result.logos:
                spec_content += f"| {logo.filename} | {logo.usage} | {logo.path.name} |\n"

        spec_file = output_dir / "design_spec.md"
        spec_file.write_text(spec_content, encoding='utf-8')

    def _generate_colors_json(self, output_dir: Path):
        """生成颜色配置JSON"""
        colors = self.result.colors or ExtractedColors()

        colors_data = {
            "brand_id": self.template_name,
            "primary": colors.primary,
            "secondary": colors.secondary,
            "accent": colors.accent,
            "background": colors.background,
            "text": colors.text
        }

        colors_file = output_dir / "colors.json"
        colors_file.write_text(
            json.dumps(colors_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    def _generate_fonts_json(self, output_dir: Path):
        """生成字体配置JSON"""
        fonts = self.result.fonts or ExtractedFonts()

        fonts_data = {
            "brand_id": self.template_name,
            "fonts": fonts.fonts
        }

        fonts_file = output_dir / "fonts.json"
        fonts_file.write_text(
            json.dumps(fonts_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )


def validate_template(template_path: Path) -> dict:
    """验证模板完整性"""
    issues = []
    warnings = []

    # 检查必需文件
    required = ["design_spec.md"]
    for req in required:
        if not (template_path / req).exists():
            issues.append(f"缺少必需文件: {req}")

    # 检查design_spec.md格式
    spec_file = template_path / "design_spec.md"
    if spec_file.exists():
        content = spec_file.read_text(encoding='utf-8')
        if not content.startswith('---'):
            issues.append("design_spec.md缺少YAML frontmatter")
        if 'kind:' not in content:
            issues.append("design_spec.md缺少kind字段")

    # 检查颜色配置
    colors_file = template_path / "colors.json"
    if colors_file.exists():
        try:
            json.loads(colors_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            issues.append("colors.json格式错误")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings
    }


def main():
    parser = argparse.ArgumentParser(
        description='从外部PPT/PDF提取品牌元素并导入到模板库',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('source', help='源文件路径（PPTX/PDF/图片）')
    parser.add_argument('--name', '-n', required=True, help='模板名称')
    parser.add_argument('--type', '-t', choices=['brand', 'layout', 'deck'],
                       default='brand', help='模板类型')
    parser.add_argument('--output', '-o', default='templates',
                       help='输出目录')
    parser.add_argument('--validate', action='store_true',
                       help='验证模板完整性')
    parser.add_argument('--force', action='store_true',
                       help='覆盖已存在模板')

    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"错误: 文件不存在 - {source_path}")
        sys.exit(1)

    # 确定输出目录
    script_dir = Path(__file__).parent
    output_base = script_dir.parent.parent / args.output

    # 检查已存在
    type_dir = f"{args.type}s"
    template_dir = output_base / type_dir / args.name
    if template_dir.exists() and not args.force:
        print(f"错误: 模板已存在 - {template_dir}")
        print("使用 --force 覆盖或 --name 指定新名称")
        sys.exit(1)

    # 执行导入
    importer = TemplateImporter(source_path, args.name, args.type)
    result = importer.import_template(output_base)

    # 输出结果
    if result.success:
        print(f"✅ 模板导入成功!")
        print(f"📁 输出目录: {result.output_path}")
        print()
        print("提取结果:")

        if result.colors:
            c = result.colors
            print(f"├── 🎨 主色: {c.primary}")
            print(f"├── 🎨 辅色: {c.secondary}")
            print(f"├── 🎨 强调色: {c.accent}")
            print(f"└── 🎨 背景色: {c.background}")

        if result.fonts and result.fonts.fonts:
            print(f"└── 🔤 字体: {len(result.fonts.fonts)}种")
            for font in result.fonts.fonts[:3]:
                print(f"    └── {font['usage']}: {font['name']}")

        if result.logos:
            print(f"└── 🖼️ Logo: {len(result.logos)}个")

        # 验证
        if args.validate:
            validation = validate_template(result.output_path)
            print()
            if validation["valid"]:
                print("✅ 模板验证通过")
            else:
                print("⚠️ 模板验证发现问题:")
                for issue in validation["issues"]:
                    print(f"   - {issue}")

        if result.warnings:
            print()
            for warning in result.warnings:
                print(f"⚠️ {warning}")

    else:
        print("❌ 模板导入失败:")
        for error in result.errors:
            print(f"   - {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
