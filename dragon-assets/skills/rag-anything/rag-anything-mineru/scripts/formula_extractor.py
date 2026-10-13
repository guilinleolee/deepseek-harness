"""公式提取模块"""

import asyncio
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FormulaFormat(Enum):
    """公式格式"""

    LATEX = "latex"
    MATHML = "mathml"
    TEXT = "text"
    IMAGE = "image"


@dataclass
class ExtractedFormula:
    """提取的公式"""

    formula_id: str
    latex: str
    mathml: Optional[str] = None
    text_representation: Optional[str] = None
    image_path: Optional[str] = None
    formula_type: str = "inline"  # inline/display
    bbox: tuple = (0, 0, 0, 0)
    confidence: float = 0.0
    page_num: int = 0
    context: str = ""  # 周围文本上下文
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "formula_id": self.formula_id,
            "latex": self.latex,
            "mathml": self.mathml,
            "text_representation": self.text_representation,
            "image_path": self.image_path,
            "formula_type": self.formula_type,
            "bbox": self.bbox,
            "confidence": self.confidence,
            "page_num": self.page_num,
            "context": self.context,
            "metadata": self.metadata,
        }


class FormulaExtractor:
    """公式提取器

    支持LaTeX和MathML格式的公式提取
    """

    # LaTeX公式的正则表达式
    DISPLAY_PATTERN = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
    INLINE_PATTERN = re.compile(r"\$(.+?)\$", re.DOTALL)
    LATEX_ENV_PATTERN = re.compile(
        r"\\begin\{(equation|align|gather|multline)\}(.+?)\\end\{\1\}",
        re.DOTALL,
    )

    def __init__(self, config: Optional[Any] = None):
        """初始化公式提取器

        Args:
            config: 配置对象
        """
        self.config = config
        self._mathjax_available = False
        self._latexml_available = False

        self._check_dependencies()

    def _check_dependencies(self) -> None:
        """检查依赖"""
        try:
            import mathpixc_markdown

            self._mathjax_available = True
        except ImportError:
            pass

        try:
            from latexcross import cross

            self._latexml_available = True
        except ImportError:
            pass

    async def extract(
        self, formula_data: Dict[str, Any], formula_id: Optional[str] = None
    ) -> ExtractedFormula:
        """从公式数据提取结构化公式

        Args:
            formula_data: 原始公式数据
            formula_id: 公式ID

        Returns:
            ExtractedFormula: 提取的公式
        """
        formula_id = formula_id or f"formula_{id(formula_data)}"

        latex = formula_data.get("latex", "")
        mathml = formula_data.get("mathml")
        formula_type = formula_data.get("type", "inline")

        # 确定公式类型
        if "$$" in latex or formula_data.get("display", False):
            formula_type = "display"
        else:
            formula_type = "inline"

        # 生成MathML（如果需要且可能）
        if not mathml and latex:
            mathml = self._latex_to_mathml(latex)

        return ExtractedFormula(
            formula_id=formula_id,
            latex=latex,
            mathml=mathml,
            text_representation=self._latex_to_text(latex),
            image_path=formula_data.get("image_path"),
            formula_type=formula_type,
            bbox=formula_data.get("bbox", (0, 0, 0, 0)),
            confidence=formula_data.get("confidence", 0.9),
            page_num=formula_data.get("page_num", 0),
            context=formula_data.get("context", ""),
            metadata={
                "extraction_method": formula_data.get("method", "rule-based"),
            },
        )

    async def extract_from_page(self, page_data: Any) -> List[ExtractedFormula]:
        """从页面提取所有公式

        Args:
            page_data: 页面数据

        Returns:
            List[ExtractedFormula]: 提取的公式列表
        """
        formulas = []

        # 从页面文本中提取LaTeX公式
        text = page_data.text if hasattr(page_data, "text") else ""

        # 提取行间公式
        for i, match in enumerate(self.DISPLAY_PATTERN.finditer(text)):
            formula = await self.extract(
                {
                    "latex": match.group(1),
                    "type": "display",
                    "method": "regex",
                },
                formula_id=f"formula_page{getattr(page_data, 'page_num', 0)}_display_{i}",
            )
            formulas.append(formula)

        # 提取行内公式
        for i, match in enumerate(self.INLINE_PATTERN.finditer(text)):
            formula = await self.extract(
                {
                    "latex": match.group(1),
                    "type": "inline",
                    "method": "regex",
                },
                formula_id=f"formula_page{getattr(page_data, 'page_num', 0)}_inline_{i}",
            )
            formulas.append(formula)

        return formulas

    def _latex_to_mathml(self, latex: str) -> Optional[str]:
        """将LaTeX转换为MathML

        Args:
            latex: LaTeX公式

        Returns:
            str: MathML格式（如果转换失败则返回None）
        """
        if self._mathjax_available:
            try:
                import mathpixc_markdown

                mathml = mathpixc_markdown.latex_to_mathml(latex)
                return mathml
            except Exception as e:
                logger.warning(f"LaTeX到MathML转换失败: {str(e)}")

        # 简单的占位转换
        return f'<math><mi>{latex}</mi></math>'

    def _latex_to_text(self, latex: str) -> str:
        """将LaTeX转换为文本表示

        Args:
            latex: LaTeX公式

        Returns:
            str: 文本表示
        """
        # 移除常用LaTeX命令前缀
        text = latex
        text = re.sub(r"\\frac\{([^}]+)\}\{([^}]+)\}", r"(\1)/(\2)", text)
        text = re.sub(r"\\sqrt\{([^}]+)\}", r"sqrt(\1)", text)
        text = re.sub(r"\^(\d)", r"^\1", text)
        text = re.sub(r"\{([^}]+)\}", r"\1", text)
        text = re.sub(r"\\([a-zA-Z]+)", r"\1", text)

        # 移除多余空白
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def normalize_latex(self, latex: str) -> str:
        """规范化LaTeX公式

        Args:
            latex: 原始LaTeX

        Returns:
            str: 规范化后的LaTeX
        """
        # 移除多余空白
        latex = re.sub(r"\s+", " ", latex).strip()

        # 规范化分数
        latex = re.sub(r"\\frac\s*\{([^}]+)\}\s*\{([^}]+)\}", r"\\frac{\1}{\2}", latex)

        # 规范化上下标
        latex = re.sub(r"\^(\{[^}]+\})", r"^\1", latex)
        latex = re.sub(r"_\{([^}]+)\}", r"_\1", latex)

        return latex
