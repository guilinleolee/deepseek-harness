"""模态感知检索器"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """检索结果"""

    chunk_id: str
    content: str
    modality: str = "text"  # text/table/formula/image
    score: float = 0.0
    rank: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "modality": self.modality,
            "score": self.score,
            "rank": self.rank,
            "metadata": self.metadata,
        }


@dataclass
class QueryResult:
    """查询结果"""

    answer: str
    results: List[RetrievalResult]
    confidence: float = 0.0
    total_results: int = 0
    modality_distribution: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer": self.answer,
            "results": [r.to_dict() for r in self.results],
            "confidence": self.confidence,
            "total_results": self.total_results,
            "modality_distribution": self.modality_distribution,
            "metadata": self.metadata,
        }


class ModalRetriever:
    """模态感知检索器

    支持Vector-Graph Fusion、Modality-Aware Ranking和Relational Coherence
    """

    def __init__(self, config: Optional[Any] = None):
        """初始化检索器

        Args:
            config: 配置对象
        """
        self.config = config
        self._vector_store = None
        self._graph_store = None
        self._initialized = False

    async def initialize(self) -> None:
        """初始化存储"""
        if self._initialized:
            return

        # 初始化向量存储
        try:
            import chromadb

            vector_store_path = getattr(self.config, "vector_store_path", "./data/vector_store")
            collection_name = getattr(self.config, "collection_name", "rag_anything")

            self._vector_store = chromadb.PersistentClient(path=vector_store_path)
            self._vector_collection = self._vector_store.get_or_create_collection(
                name=collection_name
            )
            logger.info(f"向量存储初始化完成: {collection_name}")

        except ImportError:
            logger.warning("ChromaDB未安装，使用简化向量存储")
            self._vector_store = None

        self._initialized = True

    async def index(self, parsed_doc: Dict[str, Any], **kwargs) -> bool:
        """索引文档

        Args:
            parsed_doc: 解析后的文档
            **kwargs: 额外参数

        Returns:
            bool: 是否成功
        """
        await self.initialize()

        try:
            from .multimodal_processor import MultimodalProcessor

            processor = MultimodalProcessor(self.config)
            chunks = await processor.process(parsed_doc)

            # 提取嵌入
            for i, chunk in enumerate(chunks):
                if chunk.embedding is None:
                    # 使用文本内容作为降级
                    text = chunk.text_content or chunk.table_content or chunk.formula_content or ""
                    chunk.embedding = await self._simple_embed(text)

                # 添加到向量存储
                self._vector_collection.add(
                    ids=[chunk.chunk_id],
                    embeddings=[chunk.embedding],
                    documents=[chunk.text_content or chunk.table_content or ""],
                    metadatas=[
                        {
                            "modality": chunk.modality_type,
                            "page_num": chunk.page_num,
                            **chunk.metadata,
                        }
                    ],
                )

            logger.info(f"文档索引完成: {len(chunks)} 个块")
            return True

        except Exception as e:
            logger.error(f"文档索引失败: {str(e)}")
            return False

    async def remove(self, doc_id: str) -> bool:
        """移除文档

        Args:
            doc_id: 文档ID

        Returns:
            bool: 是否成功
        """
        if not self._vector_collection:
            return False

        try:
            # 删除以doc_id开头的所有块
            results = self._vector_collection.get()
            ids_to_delete = [
                r["id"] for r in results["metadatas"] if r.get("doc_id", "").startswith(doc_id)
            ]

            if ids_to_delete:
                self._vector_collection.delete(ids=ids_to_delete)

            logger.info(f"文档移除完成: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"文档移除失败: {str(e)}")
            return False

    async def search(
        self,
        query: str,
        mode: str = "hybrid",
        top_k: int = 10,
        modality_filter: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """检索

        Args:
            query: 查询文本
            mode: 检索模式 (local/global/hybrid/mix)
            top_k: 返回结果数量
            modality_filter: 模态过滤器
            **kwargs: 额外参数

        Returns:
            Dict: 检索结果
        """
        await self.initialize()

        try:
            # 生成查询嵌入
            query_embedding = await self._simple_embed(query)

            # 向量检索
            vector_results = self._vector_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k * 2,  # 多取一些以便重排序
            )

            # 解析结果
            results = []
            seen_ids = set()

            for i, (ids, dists, docs, metas) in enumerate(
                zip(
                    vector_results["ids"],
                    vector_results["distances"],
                    vector_results["documents"],
                    vector_results["metadatas"],
                )
            ):
                for j, (doc_id, dist, doc, meta) in enumerate(zip(ids, dists, docs, metas)):
                    if doc_id in seen_ids:
                        continue

                    # 模态过滤
                    if modality_filter and meta.get("modality") not in modality_filter:
                        continue

                    seen_ids.add(doc_id)

                    # 计算分数（距离转分数）
                    score = 1.0 / (1.0 + dist)

                    result = RetrievalResult(
                        chunk_id=doc_id,
                        content=doc,
                        modality=meta.get("modality", "text"),
                        score=score,
                        rank=len(results) + 1,
                        metadata=meta,
                    )
                    results.append(result)

            # 应用模态自适应排序
            if mode == "hybrid":
                results = await self._modality_aware_rerank(results, query)

            # 截取top_k
            results = results[:top_k]

            # 更新排名
            for i, r in enumerate(results):
                r.rank = i + 1

            # 计算模态分布
            modality_dist = {}
            for r in results:
                modality_dist[r.modality] = modality_dist.get(r.modality, 0) + 1

            return {
                "results": [r.to_dict() for r in results],
                "modality_distribution": modality_dist,
                "total_results": len(results),
                "confidence": sum(r.score for r in results) / len(results) if results else 0.0,
            }

        except Exception as e:
            logger.error(f"检索失败: {str(e)}")
            return {
                "results": [],
                "modality_distribution": {},
                "total_results": 0,
                "confidence": 0.0,
                "error": str(e),
            }

    async def rerank_and_summarize(
        self, results: Dict[str, Any], query: str, **kwargs
    ) -> Dict[str, Any]:
        """重排序和摘要

        Args:
            results: 检索结果
            query: 查询
            **kwargs: 额外参数

        Returns:
            Dict: 处理后的结果
        """
        rerank_top_k = getattr(self.config, "rerank_top_k", 5)

        # 获取top_k结果进行摘要
        top_results = results.get("results", [])[:rerank_top_k]

        # 生成摘要（使用LLM）
        answer = await self._generate_summary(top_results, query)

        return {
            "answer": answer,
            "results": top_results,
            "confidence": results.get("confidence", 0.0),
            "modality_distribution": results.get("modality_distribution", {}),
        }

    async def _modality_aware_rerank(
        self, results: List[RetrievalResult], query: str
    ) -> List[RetrievalResult]:
        """模态自适应重排序

        根据查询类型调整各模态的权重

        Args:
            results: 原始结果
            query: 查询

        Returns:
            List[RetrievalResult]: 重排序后的结果
        """
        query_lower = query.lower()

        # 确定查询类型
        modality_weights = {
            "text": 1.0,
            "table": 1.0,
            "formula": 1.0,
            "image": 1.0,
        }

        # 根据查询关键词调整权重
        if any(kw in query_lower for kw in ["表格", "数据", "统计", "table", "data"]):
            modality_weights["table"] = 1.5
            modality_weights["text"] = 0.8

        if any(kw in query_lower for kw in ["公式", "方程", "计算", "formula", "equation"]):
            modality_weights["formula"] = 1.5
            modality_weights["text"] = 0.8

        if any(kw in query_lower for kw in ["图片", "图像", "图表", "image", "picture", "chart"]):
            modality_weights["image"] = 1.5
            modality_weights["text"] = 0.8

        # 应用权重
        for r in results:
            r.score *= modality_weights.get(r.modality, 1.0)

        # 按分数排序
        results.sort(key=lambda x: x.score, reverse=True)

        return results

    async def _generate_summary(
        self, results: List[Dict[str, Any]], query: str
    ) -> str:
        """生成摘要

        Args:
            results: 检索结果
            query: 查询

        Returns:
            str: 摘要
        """
        if not results:
            return "没有找到相关结果"

        # 简单的拼接摘要（实际应该用LLM）
        contexts = []
        for r in results[:3]:
            modality = r.get("modality", "text")
            content = r.get("content", "")[:200]
            contexts.append(f"[{modality}] {content}")

        return f"根据检索结果，{query}相关的内容如下:\n\n" + "\n\n".join(contexts)

    async def _simple_embed(self, text: str) -> List[float]:
        """简单文本嵌入（降级实现）

        Args:
            text: 文本

        Returns:
            List[float]: 嵌入向量
        """
        import hashlib

        # 简单的基于hash的降级实现
        # 实际应该使用真正的embedding模型
        h = hashlib.sha256(text.encode()).digest()
        return list(h[:64]) + [0.0] * (1536 - 64)  # 填充到标准维度
