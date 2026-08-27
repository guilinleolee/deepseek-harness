"""MinerU模块测试"""

import tempfile
from pathlib import Path

import pytest


class TestMinerUParser:
    """MinerU解析器测试"""

    @pytest.fixture
    def parser(self):
        """创建解析器实例"""
        from rag_anything_mineru.scripts.mineru_parser import MinerUParser

        return MinerUParser()

    @pytest.mark.asyncio
    async def test_parser_initialization(self, parser):
        """测试解析器初始化"""
        assert parser is not None
        assert not parser._initialized

        await parser.initialize()

        assert parser._initialized

    @pytest.mark.asyncio
    async def test_parse_nonexistent_file(self, parser):
        """测试解析不存在的文件"""
        with pytest.raises(Exception):
            await parser.parse("nonexistent.pdf")


class TestTableExtractor:
    """表格提取器测试"""

    @pytest.fixture
    def extractor(self):
        """创建提取器实例"""
        from rag_anything_mineru.scripts.table_extractor import TableExtractor

        return TableExtractor()

    @pytest.mark.asyncio
    async def test_extract_simple_table(self, extractor):
        """测试简单表格提取"""
        table_data = {
            "cells": [["Name", "Age"], ["Alice", "25"], ["Bob", "30"]],
            "bbox": (0, 0, 100, 50),
        }

        result = await extractor.extract(table_data, "test_table")

        assert result.table_id == "test_table"
        assert result.rows == 3
        assert result.cols == 2
        assert result.header == ["Name", "Age"]
        assert "html" in result.format.value

    @pytest.mark.asyncio
    async def test_to_html(self, extractor):
        """测试HTML转换"""
        cells = [["A", "B"], ["1", "2"]]
        html = extractor._to_html(cells)

        assert "<table" in html
        assert "<th>A</th>" in html
        assert "<td>1</td>" in html

    @pytest.mark.asyncio
    async def test_to_markdown(self, extractor):
        """测试Markdown转换"""
        cells = [["Name", "Age"], ["Alice", "25"]]
        md = extractor._to_markdown(cells, ["Name", "Age"])

        assert "| Name | Age |" in md
        assert "|---|---|" in md
        assert "| Alice | 25 |" in md


class TestFormulaExtractor:
    """公式提取器测试"""

    @pytest.fixture
    def extractor(self):
        """创建提取器实例"""
        from rag_anything_mineru.scripts.formula_extractor import FormulaExtractor

        return FormulaExtractor()

    @pytest.mark.asyncio
    async def test_extract_latex(self, extractor):
        """测试LaTeX公式提取"""
        formula_data = {
            "latex": r"\frac{a}{b}",
            "type": "inline",
        }

        result = await extractor.extract(formula_data, "formula_1")

        assert result.formula_id == "formula_1"
        assert result.latex == r"\frac{a}{b}"
        assert result.formula_type == "inline"

    @pytest.mark.asyncio
    async def test_latex_to_text(self, extractor):
        """测试LaTeX转文本"""
        latex = r"\frac{x}{y} + \sqrt{2}"
        text = extractor._latex_to_text(latex)

        assert "x" in text
        assert "/" in text or "(" in text

    @pytest.mark.asyncio
    async def test_normalize_latex(self, extractor):
        """测试LaTeX规范化"""
        latex = r"  \frac { a } { b }  "
        normalized = extractor.normalize_latex(latex)

        assert "  " not in normalized


class TestImageUnderstanding:
    """图像理解测试"""

    @pytest.fixture
    def processor(self):
        """创建处理器实例"""
        from rag_anything_mineru.scripts.image_understanding import (
            ImageUnderstandingProcessor,
        )

        return ImageUnderstandingProcessor()

    @pytest.mark.asyncio
    async def test_initialization(self, processor):
        """测试处理器初始化"""
        assert processor is not None
        assert not processor._initialized

        await processor.initialize()

        assert processor._initialized

    @pytest.mark.asyncio
    async def test_detect_layout(self, processor):
        """测试布局检测"""
        # 图表
        desc = "A bar chart showing sales data with X and Y axes"
        layout = processor._detect_layout(desc)
        assert layout == "chart"

        # 表格
        desc = "A table with rows and columns showing data"
        layout = processor._detect_layout(desc)
        assert layout == "table"

        # 照片
        desc = "A photo of a beautiful landscape with mountains"
        layout = processor._detect_layout(desc)
        assert layout == "photo"

    @pytest.mark.asyncio
    async def test_generate_alt_text(self, processor):
        """测试alt文本生成"""
        desc = "A graph showing the trend of stock prices"
        ocr = "Stock Price Trend 2024"
        alt = processor._generate_alt_text(desc, ocr)

        assert len(alt) > 0
        assert len(alt) <= 150


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
