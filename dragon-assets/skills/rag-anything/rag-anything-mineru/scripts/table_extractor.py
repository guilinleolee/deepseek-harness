"""表格提取模块"""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TableFormat(Enum):
    """表格格式"""

    HTML = "html"
    MARKDOWN = "markdown"
    CSV = "csv"
    JSON = "json"


@dataclass
class ExtractedTable:
    """提取的表格"""

    table_id: str
    format: TableFormat
    content: str
    rows: int
    cols: int
    header: List[str]
    bbox: tuple = (0, 0, 0, 0)
    confidence: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table_id": self.table_id,
            "format": self.format.value,
            "content": self.content,
            "rows": self.rows,
            "cols": self.cols,
            "header": self.header,
            "bbox": self.bbox,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


class TableExtractor:
    """表格提取器"""

    def __init__(self, config: Optional[Any] = None):
        """初始化表格提取器

        Args:
            config: 配置对象
        """
        self.config = config
        self._mineru_available = False
        self._pdfplumber_available = False

        self._check_dependencies()

    def _check_dependencies(self) -> None:
        """检查依赖"""
        try:
            import pdfplumber

            self._pdfplumber_available = True
        except ImportError:
            logger.warning("pdfplumber未安装")

        try:
            from tablepyxl import Table

            self._mineru_available = True
        except ImportError:
            logger.warning("tablepyxl未安装")

    async def extract(
        self, table_data: Dict[str, Any], table_id: Optional[str] = None
    ) -> ExtractedTable:
        """从表格数据提取结构化表格

        Args:
            table_data: 原始表格数据
            table_id: 表格ID

        Returns:
            ExtractedTable: 提取的表格
        """
        table_id = table_id or f"table_{id(table_data)}"

        # 获取表格内容
        cells = table_data.get("cells", [])
        rows = len(cells)
        cols = len(cells[0]) if cells else 0

        # 提取表头
        header = cells[0] if cells else []

        # 转换为各种格式
        html = self._to_html(cells)
        markdown = self._to_markdown(cells, header)
        csv = self._to_csv(cells)

        return ExtractedTable(
            table_id=table_id,
            format=TableFormat.HTML,
            content=html,
            rows=rows,
            cols=cols,
            header=header,
            bbox=table_data.get("bbox", (0, 0, 0, 0)),
            confidence=table_data.get("confidence", 0.9),
            metadata={
                "original_format": table_data.get("format", "unknown"),
                "extraction_method": "mineru" if self._mineru_available else "pdfplumber",
            },
        )

    async def extract_from_page(self, page_data: Any) -> List[ExtractedTable]:
        """从页面提取所有表格

        Args:
            page_data: 页面数据

        Returns:
            List[ExtractedTable]: 提取的表格列表
        """
        tables = []

        for i, table in enumerate(page_data.tables if hasattr(page_data, "tables") else []):
            extracted = await self.extract(
                {"cells": table, "bbox": getattr(table, "bbox", (0, 0, 0, 0))},
                table_id=f"table_page{getattr(page_data, 'page_num', 0)}_{i}",
            )
            tables.append(extracted)

        return tables

    def _to_html(self, cells: List[List[str]]) -> str:
        """转换为HTML格式"""
        if not cells:
            return ""

        html = ['<table class="extracted-table">']

        # 表头
        html.append("<thead><tr>")
        for cell in cells[0]:
            html.append(f"<th>{self._escape_html(cell)}</th>")
        html.append("</tr></thead>")

        # 数据行
        html.append("<tbody>")
        for row in cells[1:]:
            html.append("<tr>")
            for cell in row:
                html.append(f"<td>{self._escape_html(cell)}</td>")
            html.append("</tr>")
        html.append("</tbody></table>")

        return "".join(html)

    def _to_markdown(self, cells: List[List[str]], header: List[str]) -> str:
        """转换为Markdown格式"""
        if not cells:
            return ""

        lines = []

        # 表头
        lines.append("| " + " | ".join(self._escape_md(h) for h in header) + " |")
        lines.append("|" + "|".join("---" for _ in header) + "|")

        # 数据行
        for row in cells[1:]:
            lines.append("| " + " | ".join(self._escape_md(c) for c in row) + " |")

        return "\n".join(lines)

    def _to_csv(self, cells: List[List[str]]) -> str:
        """转换为CSV格式"""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        for row in cells:
            writer.writerow(row)

        return output.getvalue()

    def _escape_html(self, text: str) -> str:
        """HTML转义"""
        if not text:
            return ""
        return (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def _escape_md(self, text: str) -> str:
        """Markdown转义"""
        if not text:
            return ""
        return str(text).replace("|", "\\|").replace("\n", " ")
