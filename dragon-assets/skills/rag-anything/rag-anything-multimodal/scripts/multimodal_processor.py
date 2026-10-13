"""多模态处理器"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class ChunkData:
    """数据块"""

    chunk_id: str
    content: str
    modality: str = "text"  # text/table/formula/image
    chunk_type: str = "text"
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "modality": self.modality,
            "chunk_type": self.chunk_type,
            "metadata": self.metadata,
        }


@dataclass
class MultimodalChunk:
    """多模态块"""

    chunk_id: str
    text_content: str = ""
    table_content: Optional[str] = None
    formula_content: Optional[str] = None
    image_content: Optional[str] = None
    image_descriptions: List[str] = field(default_factory=list)
    modality_type: str = "text"  # text/table/formula/image/mixed
    page_num: int = 0
    bbox: tuple = (0, 0, 0, 0)
    relations: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text_content": self.text_content,
            "table_content": self.table_content,
            "formula_content": self.formula_content,
            "image_content": self.image_content,
            "image_descriptions": self.image_descriptions,
            "modality_type": self.modality_type,
            "page_num": self.page_num,
            "bbox": self.bbox,
            "relations": self.relations,
            "metadata": self.metadata,
        }


class MultimodalProcessor:
    """多模态处理器

    负责将解析的文档内容转换为统一的多模态块格式
    """

    def __init__(self, config: Optional[Any] = None):
        """初始化多模态处理器

        Args:
            config: 配置对象
        """
        self.config = config
        self._embedder = None

    async def initialize(self) -> None:
        """初始化嵌入模型"""
        if self._embedder is not None:
            return

        try:
            from .cross_modal_embedding import CrossModalEmbedder

            self._embedder = CrossModalEmbedder(self.config)
            await self._embedder.initialize()
        except ImportError:
            logger.warning("CrossModalEmbedder导入失败，使用简化版本")

    async def process(
        self, parsed_doc: Dict[str, Any], **kwargs
    ) -> List[MultimodalChunk]:
        """处理解析的文档，生成多模态块

        Args:
            parsed_doc: 解析后的文档
            **kwargs: 额外参数

        Returns:
            List[MultimodalChunk]: 多模态块列表
        """
        await self.initialize()

        chunks = []
        doc_id = parsed_doc.get("doc_id", "unknown")

        # 处理文本块
        text_chunks = await self._process_text_chunks(parsed_doc, doc_id)
        chunks.extend(text_chunks)

        # 处理表格块
        table_chunks = await self._process_table_chunks(parsed_doc, doc_id)
        chunks.extend(table_chunks)

        # 处理公式块
        formula_chunks = await self._process_formula_chunks(parsed_doc, doc_id)
        chunks.extend(formula_chunks)

        # 处理图像块
        image_chunks = await self._process_image_chunks(parsed_doc, doc_id)
        chunks.extend(image_chunks)

        # 生成嵌入
        if self._embedder:
            await self._generate_embeddings(chunks)

        logger.info(f"文档 {doc_id} 处理完成，生成 {len(chunks)} 个多模态块")

        return chunks

    async def _process_text_chunks(
        self, parsed_doc: Dict[str, Any], doc_id: str
    ) -> List[MultimodalChunk]:
        """处理文本块"""
        chunks = []
        chunk_size = getattr(self.config, "chunk_size", 512)

        for page in parsed_doc.get("pages", []):
            page_num = page.get("page_num", 0)
            text = page.get("text", "")

            # 简单的固定大小分块
            text_blocks = page.get("text_blocks", [])
            if not text_blocks:
                text_blocks = [{"text": text}]

            for i, block in enumerate(text_blocks):
                text_content = block.get("text", "")
                if not text_content.strip():
                    continue

                chunk = MultimodalChunk(
                    chunk_id=f"{doc_id}_text_{page_num}_{i}",
                    text_content=text_content,
                    modality_type="text",
                    page_num=page_num,
                    bbox=block.get("bbox", (0, 0, 0, 0)),
                    metadata={
                        "source": "text",
                        "block_type": block.get("type", "paragraph"),
                    },
                )
                chunks.append(chunk)

        return chunks

    async def _process_table_chunks(
        self, parsed_doc: Dict[str, Any], doc_id: str
    ) -> List[MultimodalChunk]:
        """处理表格块"""
        chunks = []

        for i, table in enumerate(parsed_doc.get("tables", [])):
            chunk = MultimodalChunk(
                chunk_id=f"{doc_id}_table_{table.get('page_num', 0)}_{i}",
                table_content=table.get("markdown", table.get("html", "")),
                modality_type="table",
                page_num=table.get("page_num", 0),
                bbox=table.get("bbox", (0, 0, 0, 0)),
                metadata={
                    "source": "table",
                    "rows": table.get("rows", 0),
                    "cols": table.get("cols", 0),
                    "header": table.get("header", []),
                },
            )
            chunks.append(chunk)

        return chunks

    async def _process_formula_chunks(
        self, parsed_doc: Dict[str, Any], doc_id: str
    ) -> List[MultimodalChunk]:
        """处理公式块"""
        chunks = []

        for i, formula in enumerate(parsed_doc.get("formulas", [])):
            chunk = MultimodalChunk(
                chunk_id=f"{doc_id}_formula_{formula.get('page_num', 0)}_{i}",
                formula_content=formula.get("latex", ""),
                modality_type="formula",
                page_num=formula.get("page_num", 0),
                bbox=formula.get("bbox", (0, 0, 0, 0)),
                metadata={
                    "source": "formula",
                    "latex": formula.get("latex", ""),
                    "mathml": formula.get("mathml"),
                    "formula_type": formula.get("formula_type", "inline"),
                },
            )
            chunks.append(chunk)

        return chunks

    async def _process_image_chunks(
        self, parsed_doc: Dict[str, Any], doc_id: str
    ) -> List[MultimodalChunk]:
        """处理图像块"""
        chunks = []

        for i, image in enumerate(parsed_doc.get("images", [])):
            chunk = MultimodalChunk(
                chunk_id=f"{doc_id}_image_{image.get('page_num', 0)}_{i}",
                image_content=image.get("image_path", ""),
                image_descriptions=[image.get("description", "")],
                modality_type="image",
                page_num=image.get("page_num", 0),
                bbox=image.get("bbox", (0, 0, 0, 0)),
                metadata={
                    "source": "image",
                    "description": image.get("description", ""),
                    "alt_text": image.get("alt_text", ""),
                    "figure_caption": image.get("figure_caption", ""),
                },
            )
            chunks.append(chunk)

        return chunks

    async def _generate_embeddings(
        self, chunks: List[MultimodalChunk]
    ) -> None:
        """为块生成嵌入向量

        Args:
            chunks: 多模态块列表
        """
        if not self._embedder:
            return

        for chunk in chunks:
            try:
                # 优先使用图像描述，其次是表格/公式，最后是文本
                text_to_embed = (
                    chunk.image_descriptions[0]
                    if chunk.image_descriptions
                    else chunk.table_content
                    or chunk.formula_content
                    or chunk.text_content
                )

                if text_to_embed:
                    embedding = await self._embedder.embed(text_to_embed)
                    chunk.embedding = embedding

            except Exception as e:
                logger.warning(f"生成嵌入失败 {chunk.chunk_id}: {str(e)}")

    async def fuse_chunks(
        self, chunks: List[MultimodalChunk], fusion_strategy: str = "concat"
    ) -> List[str]:
        """融合多模态块为文本

        Args:
            chunks: 多模态块列表
            fusion_strategy: 融合策略 (concat/summary)

        Returns:
            List[str]: 融合后的文本列表
        """
        if fusion_strategy == "concat":
            return [self._chunk_to_text(c) for c in chunks]
        else:
            # summary策略：简单拼接
            texts = [self._chunk_to_text(c) for c in chunks]
            return ["\n\n".join(texts)]

    def _chunk_to_text(self, chunk: MultimodalChunk) -> str:
        """将多模态块转换为文本"""
        parts = []

        if chunk.text_content:
            parts.append(chunk.text_content)

        if chunk.table_content:
            parts.append(f"[TABLE]\n{chunk.table_content}\n[/TABLE]")

        if chunk.formula_content:
            parts.append(f"[FORMULA] {chunk.formula_content} [/FORMULA]")

        if chunk.image_descriptions:
            parts.append(f"[IMAGE] {'; '.join(chunk.image_descriptions)} [/IMAGE]")

        return "\n".join(parts)
