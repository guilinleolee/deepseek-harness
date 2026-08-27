"""RAG-Anything核心管理器"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .config import RAGAnythingConfig, get_default_config
from .utils import (
    async_retry,
    calculate_file_hash,
    clean_text,
    get_file_type,
    is_document_file,
    truncate_text,
)

logger = logging.getLogger(__name__)


@dataclass
class ProcessResult:
    """文档处理结果"""

    doc_id: str
    file_path: str
    success: bool
    error: Optional[str] = None
    entities_count: int = 0
    relations_count: int = 0
    chunks_count: int = 0
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "file_path": self.file_path,
            "success": self.success,
            "error": self.error,
            "entities_count": self.entities_count,
            "relations_count": self.relations_count,
            "chunks_count": self.chunks_count,
            "processing_time": self.processing_time,
            "metadata": self.metadata,
        }


@dataclass
class QueryResult:
    """查询结果"""

    question: str
    answer: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    modality_distribution: Dict[str, int] = field(default_factory=dict)
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "answer": self.answer,
            "sources": self.sources,
            "confidence": self.confidence,
            "modality_distribution": self.modality_distribution,
            "processing_time": self.processing_time,
            "metadata": self.metadata,
        }


@dataclass
class DocumentMetadata:
    """文档元数据"""

    doc_id: str
    file_path: str
    file_name: str
    file_type: str
    file_size: int
    file_hash: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    page_count: int = 0
    entity_count: int = 0
    relation_count: int = 0
    chunk_count: int = 0
    processing_status: str = "pending"  # pending/processing/completed/failed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "file_hash": self.file_hash,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "page_count": self.page_count,
            "entity_count": self.entity_count,
            "relation_count": self.relation_count,
            "chunk_count": self.chunk_count,
            "processing_status": self.processing_status,
        }


class RAGAnythingManager:
    """RAG-Anything核心管理器

    协调各子模块完成文档处理和查询任务
    """

    def __init__(self, config: Optional[RAGAnythingConfig] = None, **kwargs):
        """初始化管理器

        Args:
            config: 配置对象，如果为None则使用默认配置
            **kwargs: 配置参数，会覆盖config中的值
        """
        self.config = config or get_default_config()

        # 更新配置
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        # 状态管理
        self._documents: Dict[str, DocumentMetadata] = {}
        self._initialized = False

        # 子模块（延迟加载）
        self._parser = None
        self._kg_builder = None
        self._retriever = None
        self._multimodal_processor = None

        logger.info(f"RAGAnythingManager初始化完成，配置: {self.config.data_dir}")

    async def initialize(self) -> None:
        """初始化子模块"""
        if self._initialized:
            return

        logger.info("开始初始化RAG-Anything子模块...")

        # 初始化MinerU解析器
        if self.config.multimodal_enabled:
            try:
                from rag_anything_mineru import MinerUParser

                self._parser = MinerUParser(self.config)
                logger.info("MinerU解析器初始化完成")
            except ImportError:
                logger.warning("MinerU未安装，使用简化解析器")
                self._parser = None

        # 初始化知识图谱构建器
        if self.config.kg_enabled:
            try:
                from rag_anything_knowledge_graph import KGBuilder

                self._kg_builder = KGBuilder(self.config)
                logger.info("知识图谱构建器初始化完成")
            except ImportError:
                logger.warning("知识图谱模块未安装")
                self._kg_builder = None

        # 初始化检索器
        try:
            from rag_anything_multimodal import ModalRetriever

            self._retriever = ModalRetriever(self.config)
            logger.info("模态检索器初始化完成")
        except ImportError:
            logger.warning("多模态模块未安装，使用LightRAG替代")
            self._retriever = None

        self._initialized = True
        logger.info("RAG-Anything子模块初始化完成")

    @async_retry(max_attempts=3, delay=1.0)
    async def process(
        self,
        doc_path: Union[str, Path],
        force_reprocess: bool = False,
        **kwargs,
    ) -> ProcessResult:
        """处理文档并构建知识图谱

        Args:
            doc_path: 文档路径
            force_reprocess: 是否强制重新处理
            **kwargs: 额外参数

        Returns:
            ProcessResult: 处理结果
        """
        await self.initialize()

        doc_path = Path(doc_path)
        if not doc_path.exists():
            return ProcessResult(
                doc_id="",
                file_path=str(doc_path),
                success=False,
                error=f"文件不存在: {doc_path}",
            )

        start_time = datetime.now()
        file_hash = calculate_file_hash(doc_path)
        doc_id = file_hash[:16]

        # 检查是否已处理
        if doc_id in self._documents and not force_reprocess:
            existing = self._documents[doc_id]
            if existing.processing_status == "completed":
                logger.info(f"文档已处理，跳过: {doc_path}")
                return ProcessResult(
                    doc_id=doc_id,
                    file_path=str(doc_path),
                    success=True,
                    entities_count=existing.entity_count,
                    relations_count=existing.relation_count,
                    chunks_count=existing.chunk_count,
                    processing_time=0.0,
                    metadata={"skipped": True},
                )

        logger.info(f"开始处理文档: {doc_path}")

        try:
            # 更新状态
            metadata = DocumentMetadata(
                doc_id=doc_id,
                file_path=str(doc_path),
                file_name=doc_path.name,
                file_type=get_file_type(doc_path),
                file_size=doc_path.stat().st_size,
                file_hash=file_hash,
                processing_status="processing",
            )
            self._documents[doc_id] = metadata

            # 使用MinerU解析文档
            if self._parser:
                parsed_doc = await self._parser.parse(doc_path, **kwargs)
            else:
                parsed_doc = await self._simple_parse(doc_path)

            # 构建知识图谱
            entities_count = 0
            relations_count = 0

            if self._kg_builder and parsed_doc:
                kg_data = await self._kg_builder.build(parsed_doc)
                entities_count = len(kg_data.entities)
                relations_count = len(kg_data.relations)

            # 索引到检索器
            if self._retriever and parsed_doc:
                await self._retriever.index(parsed_doc)

            # 更新元数据
            processing_time = (datetime.now() - start_time).total_seconds()
            metadata.page_count = parsed_doc.get("page_count", 0) if parsed_doc else 0
            metadata.entity_count = entities_count
            metadata.relation_count = relations_count
            metadata.chunk_count = parsed_doc.get("chunk_count", 0) if parsed_doc else 0
            metadata.processing_status = "completed"
            metadata.updated_at = datetime.now()

            # 保存元数据
            await self._save_metadata(metadata)

            logger.info(
                f"文档处理完成: {doc_path}, "
                f"实体: {entities_count}, 关系: {relations_count}, "
                f"耗时: {processing_time:.2f}s"
            )

            return ProcessResult(
                doc_id=doc_id,
                file_path=str(doc_path),
                success=True,
                entities_count=entities_count,
                relations_count=relations_count,
                chunks_count=metadata.chunk_count,
                processing_time=processing_time,
                metadata={
                    "page_count": metadata.page_count,
                    "file_type": metadata.file_type,
                },
            )

        except Exception as e:
            logger.error(f"文档处理失败: {doc_path}, 错误: {str(e)}")

            if doc_id in self._documents:
                self._documents[doc_id].processing_status = "failed"

            return ProcessResult(
                doc_id=doc_id,
                file_path=str(doc_path),
                success=False,
                error=str(e),
                processing_time=(datetime.now() - start_time).total_seconds(),
            )

    async def query(
        self,
        question: str,
        mode: str = "hybrid",
        top_k: Optional[int] = None,
        **kwargs,
    ) -> QueryResult:
        """多模态问答查询

        Args:
            question: 问题
            mode: 检索模式 (local/global/hybrid/mix)
            top_k: 返回结果数量
            **kwargs: 额外参数

        Returns:
            QueryResult: 查询结果
        """
        await self.initialize()

        start_time = datetime.now()
        top_k = top_k or self.config.top_k

        logger.info(f"开始查询: {truncate_text(question, 50)}")

        try:
            # 执行检索
            if self._retriever:
                results = await self._retriever.search(
                    query=question,
                    mode=mode,
                    top_k=top_k,
                    **kwargs,
                )
            else:
                # 降级到LightRAG
                results = await self._fallback_query(question, mode, top_k)

            # 重排序和摘要
            if self._retriever and self.config.rerank_enabled:
                final_result = await self._retriever.rerank_and_summarize(
                    results, question
                )
            else:
                final_result = results

            processing_time = (datetime.now() - start_time).total_seconds()

            # 计算模态分布
            modality_dist = {}
            for r in final_result.get("results", []):
                modality = r.get("modality", "text")
                modality_dist[modality] = modality_dist.get(modality, 0) + 1

            return QueryResult(
                question=question,
                answer=final_result.get("answer", ""),
                sources=final_result.get("results", []),
                confidence=final_result.get("confidence", 0.0),
                modality_distribution=modality_dist,
                processing_time=processing_time,
                metadata={
                    "retrieval_mode": mode,
                    "total_results": len(final_result.get("results", [])),
                },
            )

        except Exception as e:
            logger.error(f"查询失败: {question}, 错误: {str(e)}")
            return QueryResult(
                question=question,
                answer=f"查询失败: {str(e)}",
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={"error": str(e)},
            )

    async def add_document(self, doc_path: Union[str, Path]) -> bool:
        """添加文档到知识库

        Args:
            doc_path: 文档路径

        Returns:
            bool: 是否成功
        """
        result = await self.process(doc_path)
        return result.success

    async def remove_document(self, doc_id: str) -> bool:
        """从知识库移除文档

        Args:
            doc_id: 文档ID

        Returns:
            bool: 是否成功
        """
        if doc_id not in self._documents:
            logger.warning(f"文档不存在: {doc_id}")
            return False

        try:
            # 从检索器移除
            if self._retriever:
                await self._retriever.remove(doc_id)

            # 从元数据中移除
            del self._documents[doc_id]

            # 删除元数据文件
            metadata_path = Path(self.config.data_dir) / "metadata" / f"{doc_id}.json"
            if metadata_path.exists():
                metadata_path.unlink()

            logger.info(f"文档已移除: {doc_id}")
            return True

        except Exception as e:
            logger.error(f"移除文档失败: {doc_id}, 错误: {str(e)}")
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息

        Returns:
            dict: 统计信息
        """
        total_docs = len(self._documents)
        completed_docs = sum(
            1 for d in self._documents.values() if d.processing_status == "completed"
        )
        total_entities = sum(d.entity_count for d in self._documents.values())
        total_relations = sum(d.relation_count for d in self._documents.values())
        total_chunks = sum(d.chunk_count for d in self._documents.values())

        return {
            "total_documents": total_docs,
            "completed_documents": completed_docs,
            "failed_documents": total_docs - completed_docs,
            "total_entities": total_entities,
            "total_relations": total_relations,
            "total_chunks": total_chunks,
            "kg_enabled": self.config.kg_enabled,
            "multimodal_enabled": self.config.multimodal_enabled,
            "retrieval_mode": self.config.retrieval_mode,
        }

    async def list_documents(self) -> List[Dict[str, Any]]:
        """列出所有文档

        Returns:
            list: 文档列表
        """
        return [doc.to_dict() for doc in self._documents.values()]

    async def _save_metadata(self, metadata: DocumentMetadata) -> None:
        """保存文档元数据"""
        metadata_dir = Path(self.config.data_dir) / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)

        metadata_path = metadata_dir / f"{metadata.doc_id}.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata.to_dict(), f, indent=2, ensure_ascii=False)

    async def _load_metadata(self) -> None:
        """加载已保存的元数据"""
        metadata_dir = Path(self.config.data_dir) / "metadata"
        if not metadata_dir.exists():
            return

        for metadata_file in metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    metadata = DocumentMetadata(
                        doc_id=data["doc_id"],
                        file_path=data["file_path"],
                        file_name=data["file_name"],
                        file_type=data["file_type"],
                        file_size=data["file_size"],
                        file_hash=data["file_hash"],
                        created_at=datetime.fromisoformat(data["created_at"]),
                        updated_at=datetime.fromisoformat(data["updated_at"]),
                        page_count=data.get("page_count", 0),
                        entity_count=data.get("entity_count", 0),
                        relation_count=data.get("relation_count", 0),
                        chunk_count=data.get("chunk_count", 0),
                        processing_status=data.get("processing_status", "pending"),
                    )
                    self._documents[metadata.doc_id] = metadata
            except Exception as e:
                logger.warning(f"加载元数据失败: {metadata_file}, 错误: {str(e)}")

    async def _simple_parse(self, doc_path: Path) -> Dict[str, Any]:
        """简化文档解析（当MinerU不可用时）"""
        file_type = get_file_type(doc_path)

        return {
            "doc_id": calculate_file_hash(doc_path)[:16],
            "file_path": str(doc_path),
            "file_type": file_type,
            "page_count": 1,
            "chunks": [{"text": f"Document: {doc_path.name}", "page": 1}],
            "chunk_count": 1,
        }

    async def _fallback_query(
        self, question: str, mode: str, top_k: int
    ) -> Dict[str, Any]:
        """降级查询（当RAG-Anything不可用时）"""
        logger.warning("使用降级查询模式")

        return {
            "answer": "RAG-Anything多模态模块未正确配置，请检查安装",
            "results": [],
            "confidence": 0.0,
        }
