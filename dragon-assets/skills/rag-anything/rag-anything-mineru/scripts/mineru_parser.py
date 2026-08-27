"""MinerU高精度PDF解析器"""

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class FormulaData:
    """公式数据"""

    formula_id: str
    latex: str
    mathml: Optional[str] = None
    image_path: Optional[str] = None
    page_num: int = 0
    bbox: tuple = field(default_factory=lambda: (0, 0, 0, 0))
    formula_type: str = "inline"  # inline/display
    text_context: str = ""  # 周围文本上下文

    def to_dict(self) -> Dict[str, Any]:
        return {
            "formula_id": self.formula_id,
            "latex": self.latex,
            "mathml": self.mathml,
            "image_path": self.image_path,
            "page_num": self.page_num,
            "bbox": self.bbox,
            "formula_type": self.formula_type,
            "text_context": self.text_context,
        }


@dataclass
class TableData:
    """表格数据"""

    table_id: str
    html: str
    markdown: str
    csv: Optional[str] = None
    page_num: int = 0
    bbox: tuple = field(default_factory=lambda: (0, 0, 0, 0))
    rows: int = 0
    cols: int = 0
    header: List[str] = field(default_factory=list)
    caption: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table_id": self.table_id,
            "html": self.html,
            "markdown": self.markdown,
            "csv": self.csv,
            "page_num": self.page_num,
            "bbox": self.bbox,
            "rows": self.rows,
            "cols": self.cols,
            "header": self.header,
            "caption": self.caption,
        }


@dataclass
class ImageData:
    """图像数据"""

    image_id: str
    image_path: str
    page_num: int = 0
    bbox: tuple = field(default_factory=lambda: (0, 0, 0, 0))
    description: str = ""
    alt_text: str = ""
    figure_caption: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_id": self.image_id,
            "image_path": self.image_path,
            "page_num": self.page_num,
            "bbox": self.bbox,
            "description": self.description,
            "alt_text": self.alt_text,
            "figure_caption": self.figure_caption,
        }


@dataclass
class PageData:
    """页面数据"""

    page_num: int
    width: float
    height: float
    text: str
    text_blocks: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[TableData] = field(default_factory=list)
    formulas: List[FormulaData] = field(default_factory=list)
    images: List[ImageData] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_num": self.page_num,
            "width": self.width,
            "height": self.height,
            "text": self.text,
            "text_blocks": self.text_blocks,
            "tables": [t.to_dict() for t in self.tables],
            "formulas": [f.to_dict() for f in self.formulas],
            "images": [i.to_dict() for i in self.images],
            "metadata": self.metadata,
        }


@dataclass
class ParsedDocument:
    """解析后的文档"""

    doc_id: str
    file_path: str
    title: str = ""
    authors: List[str] = field(default_factory=list)
    page_count: int = 0
    pages: List[PageData] = field(default_factory=list)
    tables: List[TableData] = field(default_factory=list)
    formulas: List[FormulaData] = field(default_factory=list)
    images: List[ImageData] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def full_text(self) -> str:
        """获取完整文本"""
        return "\n\n".join(p.text for p in self.pages)

    @property
    def chunk_count(self) -> int:
        """获取块数量"""
        return len(self.tables) + len(self.formulas) + len(self.images) + len(
            self.pages
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "file_path": self.file_path,
            "title": self.title,
            "authors": self.authors,
            "page_count": self.page_count,
            "pages": [p.to_dict() for p in self.pages],
            "tables": [t.to_dict() for t in self.tables],
            "formulas": [f.to_dict() for f in self.formulas],
            "images": [i.to_dict() for i in self.images],
            "metadata": self.metadata,
        }


class MinerUParser:
    """MinerU高精度PDF解析器

    支持表格、公式、图像的多模态内容提取
    """

    def __init__(self, config: Optional[Any] = None):
        """初始化解析器

        Args:
            config: 配置对象
        """
        self.config = config
        self._initialized = False
        self._table_extractor = None
        self._formula_extractor = None
        self._image_processor = None

    async def initialize(self) -> None:
        """初始化子模块"""
        if self._initialized:
            return

        try:
            from .table_extractor import TableExtractor

            self._table_extractor = TableExtractor(self.config)
        except ImportError:
            logger.warning("TableExtractor导入失败，使用简化版本")

        try:
            from .formula_extractor import FormulaExtractor

            self._formula_extractor = FormulaExtractor(self.config)
        except ImportError:
            logger.warning("FormulaExtractor导入失败，使用简化版本")

        try:
            from .image_understanding import ImageUnderstandingProcessor

            self._image_processor = ImageUnderstandingProcessor(self.config)
        except ImportError:
            logger.warning("ImageUnderstandingProcessor导入失败，使用简化版本")

        self._initialized = True

    async def parse(
        self, doc_path: Union[str, Path], **kwargs
    ) -> ParsedDocument:
        """解析PDF文档

        Args:
            doc_path: 文档路径
            **kwargs: 额外参数

        Returns:
            ParsedDocument: 解析结果
        """
        await self.initialize()

        doc_path = Path(doc_path)
        logger.info(f"开始解析文档: {doc_path}")

        try:
            # 尝试使用MagicPDF（MinerU核心）
            return await self._parse_with_magicpdf(doc_path, **kwargs)
        except ImportError:
            logger.warning("MagicPDF未安装，使用备选解析器")
            return await self._parse_with_fallback(doc_path, **kwargs)

    async def _parse_with_magicpdf(
        self, doc_path: Path, **kwargs
    ) -> ParsedDocument:
        """使用MagicPDF解析"""
        try:
            from magic_pdf.data_utils import img2pdf
            from magic_pdf.model.doc_extract import doc_analyze
            from magic_pdf.pdf_parse import parse_pdf

            # 解析PDF
            parsed_result = parse_pdf(str(doc_path))

            # 构建ParsedDocument
            doc = ParsedDocument(
                doc_id=kwargs.get("doc_id", doc_path.stem),
                file_path=str(doc_path),
                page_count=len(parsed_result.get("pages", [])),
            )

            # 异步处理各页面
            for page_num, page_data in enumerate(parsed_result.get("pages", [])):
                page = PageData(
                    page_num=page_num,
                    width=page_data.get("width", 0),
                    height=page_data.get("height", 0),
                    text=page_data.get("text", ""),
                    text_blocks=page_data.get("text_blocks", []),
                )

                # 提取表格
                if self._table_extractor and page_data.get("tables"):
                    for table_data in page_data.get("tables", []):
                        table = await self._table_extractor.extract(table_data)
                        table.page_num = page_num
                        page.tables.append(table)
                        doc.tables.append(table)

                # 提取公式
                if self._formula_extractor and page_data.get("formulas"):
                    for formula_data in page_data.get("formulas", []):
                        formula = await self._formula_extractor.extract(formula_data)
                        formula.page_num = page_num
                        page.formulas.append(formula)
                        doc.formulas.append(formula)

                # 提取图像
                if self._image_processor and page_data.get("images"):
                    for img_data in page_data.get("images", []):
                        image = ImageData(
                            image_id=img_data.get("image_id", f"img_{page_num}"),
                            image_path=img_data.get("path", ""),
                            page_num=page_num,
                            bbox=img_data.get("bbox", (0, 0, 0, 0)),
                        )
                        # 生成图像描述
                        if self._image_processor:
                            image.description = (
                                await self._image_processor.understand(image.image_path)
                            )
                        page.images.append(image)
                        doc.images.append(image)

                doc.pages.append(page)

            return doc

        except Exception as e:
            logger.error(f"MagicPDF解析失败: {str(e)}")
            raise

    async def _parse_with_fallback(
        self, doc_path: Path, **kwargs
    ) -> ParsedDocument:
        """使用备选解析器（pdfplumber）"""
        try:
            import pdfplumber

            doc = ParsedDocument(
                doc_id=kwargs.get("doc_id", doc_path.stem),
                file_path=str(doc_path),
            )

            with pdfplumber.open(doc_path) as pdf:
                doc.page_count = len(pdf.pages)

                for page_num, page in enumerate(pdf.pages):
                    page_data = PageData(
                        page_num=page_num,
                        width=page.width,
                        height=page.height,
                        text=page.extract_text() or "",
                    )

                    # 提取表格
                    tables = page.extract_tables()
                    if tables and self._table_extractor:
                        for table in tables:
                            table_data = TableData(
                                table_id=f"table_{page_num}_{len(page_data.tables)}",
                                html=self._tables_to_html(table),
                                markdown=self._tables_to_markdown(table),
                                page_num=page_num,
                                rows=len(table),
                                cols=len(table[0]) if table else 0,
                            )
                            page_data.tables.append(table_data)
                            doc.tables.append(table_data)

                    doc.pages.append(page_data)

            return doc

        except Exception as e:
            logger.error(f"备选解析器失败: {str(e)}")
            raise

    async def extract_tables(self, page: PageData) -> List[TableData]:
        """提取页面中的表格

        Args:
            page: 页面数据

        Returns:
            List[TableData]: 表格列表
        """
        if self._table_extractor:
            return await self._table_extractor.extract_from_page(page)
        return page.tables

    async def extract_formulas(self, page: PageData) -> List[FormulaData]:
        """提取页面中的公式

        Args:
            page: 页面数据

        Returns:
            List[FormulaData]: 公式列表
        """
        if self._formula_extractor:
            return await self._formula_extractor.extract_from_page(page)
        return page.formulas

    async def understand_image(self, image_path: str) -> str:
        """理解图像内容

        Args:
            image_path: 图像路径

        Returns:
            str: 图像描述
        """
        if self._image_processor:
            return await self._image_processor.understand(image_path)
        return "图像内容（VLM未配置）"

    def _tables_to_html(self, table: List[List[str]]) -> str:
        """将表格转换为HTML"""
        if not table:
            return ""

        html = ['<table border="1">']

        # 表头
        html.append("<thead><tr>")
        for cell in table[0]:
            html.append(f"<th>{self._escape_html(cell or '')}</th>")
        html.append("</tr></thead>")

        # 数据行
        html.append("<tbody>")
        for row in table[1:]:
            html.append("<tr>")
            for cell in row:
                html.append(f"<td>{self._escape_html(cell or '')}</td>")
            html.append("</tr>")
        html.append("</tbody></table>")

        return "".join(html)

    def _tables_to_markdown(self, table: List[List[str]]) -> str:
        """将表格转换为Markdown"""
        if not table:
            return ""

        lines = []

        # 表头
        header = table[0]
        lines.append("| " + " | ".join(self._escape_md(c or "") for c in header) + " |")
        lines.append("|" + "|".join("---" for _ in header) + "|")

        # 数据行
        for row in table[1:]:
            lines.append("| " + " | ".join(self._escape_md(c or "") for c in row) + " |")

        return "\n".join(lines)

    def _escape_html(self, text: str) -> str:
        """HTML转义"""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def _escape_md(self, text: str) -> str:
        """Markdown转义"""
        return text.replace("|", "\\|").replace("\n", " ")
