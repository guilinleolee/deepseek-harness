"""图像理解模块"""

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class ImageUnderstanding:
    """图像理解结果"""

    image_id: str
    description: str
    detailed_description: str = ""
    alt_text: str = ""
    ocr_text: str = ""
    objects: List[Dict[str, Any]] = None
    layout: str = ""  # e.g., "figure", "table", "chart"
    figure_caption: str = ""
    page_num: int = 0
    bbox: tuple = (0, 0, 0, 0)
    confidence: float = 0.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.objects is None:
            self.objects = []
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_id": self.image_id,
            "description": self.description,
            "detailed_description": self.detailed_description,
            "alt_text": self.alt_text,
            "ocr_text": self.ocr_text,
            "objects": self.objects,
            "layout": self.layout,
            "figure_caption": self.figure_caption,
            "page_num": self.page_num,
            "bbox": self.bbox,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


class ImageUnderstandingProcessor:
    """图像理解处理器

    使用VLM（视觉语言模型）理解图像内容
    """

    def __init__(self, config: Optional[Any] = None):
        """初始化图像理解处理器

        Args:
            config: 配置对象
        """
        self.config = config
        self._client = None
        self._initialized = False

    async def initialize(self) -> None:
        """初始化VLM客户端"""
        if self._initialized:
            return

        try:
            from openai import AsyncOpenAI

            api_key = getattr(self.config, "api_key", None) or self._get_env_var(
                "OPENAI_API_KEY"
            )
            api_base = getattr(self.config, "api_base", None) or self._get_env_var(
                "OPENAI_API_BASE"
            )

            self._client = AsyncOpenAI(api_key=api_key, base_url=api_base)
            self._initialized = True
            logger.info("VLM客户端初始化完成")

        except Exception as e:
            logger.warning(f"VLM客户端初始化失败: {str(e)}")
            self._client = None

    def _get_env_var(self, key: str) -> Optional[str]:
        """获取环境变量"""
        import os

        return os.getenv(key)

    async def understand(
        self,
        image_path: Union[str, Path],
        prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """理解图像内容

        Args:
            image_path: 图像路径
            prompt: 可选的提示词
            **kwargs: 额外参数

        Returns:
            str: 图像描述
        """
        await self.initialize()

        if not self._client:
            return self._fallback_description(image_path)

        image_path = Path(image_path)
        if not image_path.exists():
            return "图像文件不存在"

        try:
            # 使用GPT-4o进行图像理解
            response = await self._client.chat.completions.create(
                model=getattr(self.config, "vision_model", "gpt-4o"),
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                                or "请详细描述这张图像的内容，包括其中的文字、图表、布局等所有重要信息。",
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{image_path.suffix[1:]};base64,{self._encode_image(image_path)}"
                                },
                            },
                        ],
                    }
                ],
                max_tokens=kwargs.get("max_tokens", 1024),
                temperature=kwargs.get("temperature", 0.7),
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"图像理解失败: {str(e)}")
            return self._fallback_description(image_path)

    async def understand_with_ocr(
        self, image_path: Union[str, Path], **kwargs
    ) -> ImageUnderstanding:
        """理解图像并提取OCR文本

        Args:
            image_path: 图像路径
            **kwargs: 额外参数

        Returns:
            ImageUnderstanding: 完整的图像理解结果
        """
        await self.initialize()

        image_path = Path(image_path)
        image_id = image_path.stem

        understanding = ImageUnderstanding(
            image_id=image_id,
            description="",
            page_num=kwargs.get("page_num", 0),
            bbox=kwargs.get("bbox", (0, 0, 0, 0)),
        )

        if not self._client:
            understanding.description = self._fallback_description(image_path)
            return understanding

        try:
            # 并行执行OCR和理解
            ocr_task = self._extract_ocr(image_path)
            desc_task = self.understand(
                image_path,
                prompt="请详细描述这张图像的内容，包括其中的文字、图表、布局等所有重要信息。",
            )

            ocr_text, description = await asyncio.gather(ocr_task, desc_task)

            understanding.ocr_text = ocr_text
            understanding.description = description

            # 尝试检测图像类型
            understanding.layout = self._detect_layout(description)

            # 生成alt文本
            understanding.alt_text = self._generate_alt_text(description, ocr_text)

        except Exception as e:
            logger.error(f"图像理解失败: {str(e)}")
            understanding.description = self._fallback_description(image_path)

        return understanding

    async def _extract_ocr(self, image_path: Path) -> str:
        """提取图像中的文字（OCR）

        Args:
            image_path: 图像路径

        Returns:
            str: OCR识别的文本
        """
        try:
            import pytesseract
            from PIL import Image

            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang="chi_sim+eng")
            return text.strip()

        except ImportError:
            logger.warning("pytesseract未安装，跳过OCR")
            return ""
        except Exception as e:
            logger.warning(f"OCR提取失败: {str(e)}")
            return ""

    def _encode_image(self, image_path: Path) -> str:
        """将图像编码为base64

        Args:
            image_path: 图像路径

        Returns:
            str: base64编码的图像
        """
        import base64

        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _detect_layout(self, description: str) -> str:
        """根据描述检测图像布局类型

        Args:
            description: 图像描述

        Returns:
            str: 布局类型
        """
        description_lower = description.lower()

        if any(
            keyword in description_lower
            for keyword in ["chart", "graph", "plot", "axis", "数据", "图表"]
        ):
            return "chart"
        elif any(
            keyword in description_lower
            for keyword in ["table", "表格", "row", "column", "单元格"]
        ):
            return "table"
        elif any(
            keyword in description_lower
            for keyword in ["equation", "formula", "公式", "数学"]
        ):
            return "equation"
        elif any(
            keyword in keyword in description_lower
            for keyword in ["photo", "image", "picture", "照片", "图片", "人物", "风景"]
        ):
            return "photo"
        elif any(
            keyword in description_lower
            for keyword in ["diagram", "流程图", "结构", "示意"]
        ):
            return "diagram"
        else:
            return "figure"

    def _generate_alt_text(self, description: str, ocr_text: str) -> str:
        """生成alt文本

        Args:
            description: 图像描述
            ocr_text: OCR文本

        Returns:
            str: 简短的alt文本
        """
        # 取描述的前100个字符
        alt = description[:100].strip()

        # 如果有OCR文本，添加部分
        if ocr_text and len(ocr_text) > 10:
            # 取OCR文本的前50个字符
            alt += f" - {ocr_text[:50].strip()}"

        return alt

    def _fallback_description(self, image_path: Path) -> str:
        """降级描述（当VLM不可用时）

        Args:
            image_path: 图像路径

        Returns:
            str: 基本描述
        """
        return f"[图像内容，需要VLM支持才能理解: {image_path.name}]"
