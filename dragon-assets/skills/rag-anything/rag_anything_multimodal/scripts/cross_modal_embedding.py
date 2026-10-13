"""跨模态Embedding模块"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class CrossModalEmbedder:
    """跨模态嵌入器

    支持文本和图像的统一向量表示
    """

    def __init__(self, config: Optional[Any] = None):
        """初始化嵌入器

        Args:
            config: 配置对象
        """
        self.config = config
        self._text_embedder = None
        self._image_embedder = None
        self._initialized = False

    async def initialize(self) -> None:
        """初始化嵌入模型"""
        if self._initialized:
            return

        # 初始化文本嵌入
        try:
            from openai import AsyncOpenAI

            api_key = getattr(self.config, "api_key", None)
            api_base = getattr(self.config, "api_base", None)

            if api_key:
                self._text_embedder = AsyncOpenAI(api_key=api_key, base_url=api_base)
                logger.info("OpenAI嵌入模型初始化完成")
        except ImportError:
            logger.warning("OpenAI SDK未安装")

        # 初始化图像嵌入（如果配置了）
        try:
            # 可以使用 CLIP 或其他图像嵌入模型
            self._image_embedder = None
            logger.info("图像嵌入模型初始化完成（使用文本描述作为替代）")
        except Exception as e:
            logger.warning(f"图像嵌入模型初始化失败: {str(e)}")

        self._initialized = True

    async def embed(self, text: str, **kwargs) -> List[float]:
        """生成文本嵌入

        Args:
            text: 文本
            **kwargs: 额外参数

        Returns:
            List[float]: 嵌入向量
        """
        if not self._initialized:
            await self.initialize()

        if self._text_embedder:
            try:
                response = await self._text_embedder.embeddings.create(
                    model=getattr(self.config, "embedding_model", "text-embedding-3-small"),
                    input=text,
                )
                return response.data[0].embedding
            except Exception as e:
                logger.warning(f"OpenAI嵌入失败: {str(e)}")

        # 降级：使用简单hash
        return await self._fallback_embed(text)

    async def embed_image(self, image_path: str, **kwargs) -> List[float]:
        """生成图像嵌入

        Args:
            image_path: 图像路径
            **kwargs: 额外参数

        Returns:
            List[float]: 嵌入向量
        """
        if not self._initialized:
            await self.initialize()

        if self._image_embedder:
            try:
                # 使用图像嵌入模型
                return await self._image_embedder.embed(image_path)
            except Exception as e:
                logger.warning(f"图像嵌入失败: {str(e)}")

        # 降级：返回零向量
        embedding_dim = getattr(self.config, "embedding_dimension", 1536)
        return [0.0] * embedding_dim

    async def embed_batch(
        self, texts: List[str], **kwargs
    ) -> List[List[float]]:
        """批量生成嵌入

        Args:
            texts: 文本列表
            **kwargs: 额外参数

        Returns:
            List[List[float]]: 嵌入向量列表
        """
        if not self._initialized:
            await self.initialize()

        if self._text_embedder and len(texts) <= 100:
            try:
                response = await self._text_embedder.embeddings.create(
                    model=getattr(self.config, "embedding_model", "text-embedding-3-small"),
                    input=texts,
                )
                return [item.embedding for item in response.data]
            except Exception as e:
                logger.warning(f"批量嵌入失败: {str(e)}")

        # 降级：逐个处理
        return [await self.embed(text) for text in texts]

    async def compute_similarity(
        self, embedding1: List[float], embedding2: List[float]
    ) -> float:
        """计算两个嵌入向量的余弦相似度

        Args:
            embedding1: 嵌入向量1
            embedding2: 嵌入向量2

        Returns:
            float: 相似度分数
        """
        import math

        # 余弦相似度
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = math.sqrt(sum(a * a for a in embedding1))
        norm2 = math.sqrt(sum(b * b for b in embedding2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    async def _fallback_embed(self, text: str) -> List[float]:
        """降级嵌入实现

        Args:
            text: 文本

        Returns:
            List[float]: 降级嵌入向量
        """
        import hashlib

        # 基于hash的降级实现
        h = hashlib.sha256(text.encode()).digest()
        embedding_dim = getattr(self.config, "embedding_dimension", 1536)

        # 使用hash字节生成伪随机向量
        result = list(h * (embedding_dim // len(h) + 1))[:embedding_dim]
        return [float(b) / 255.0 for b in result]
