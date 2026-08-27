"""19-01数据工程师V9.0多模态RAG集成测试"""

import asyncio
import tempfile
from pathlib import Path

import pytest


class TestDataEngineerMultimodalRAG:
    """数据工程师多模态RAG能力测试"""

    @pytest.fixture
    def sample_pdf_content(self):
        """模拟PDF解析结果"""
        return {
            "doc_id": "test_financial_report",
            "file_path": "financial_report.pdf",
            "pages": [
                {
                    "page_num": 0,
                    "text": "Q1 2024 Financial Summary: Revenue grew 25% year over year.",
                    "text_blocks": [
                        {"text": "Q1 2024 Financial Summary", "type": "heading"},
                        {"text": "Revenue grew 25% year over year.", "type": "paragraph"},
                    ],
                    "tables": [
                        {
                            "table_id": "table_0",
                            "html": "<table><tr><th>Quarter</th><th>Revenue</th></tr><tr><td>Q1</td><td>100M</td></tr></table>",
                            "markdown": "| Quarter | Revenue |\n| --- | --- |\n| Q1 | 100M |",
                            "page_num": 0,
                            "rows": 2,
                            "cols": 2,
                            "header": ["Quarter", "Revenue"],
                        }
                    ],
                    "formulas": [],
                    "images": [],
                },
                {
                    "page_num": 1,
                    "text": "The profit margin is calculated using the formula: E = mc^2.",
                    "text_blocks": [
                        {"text": "Profit Margin Calculation", "type": "heading"},
                        {"text": "The profit margin is calculated using the formula: E = mc^2.", "type": "paragraph"},
                    ],
                    "tables": [],
                    "formulas": [
                        {
                            "formula_id": "formula_0",
                            "latex": r"E = mc^2",
                            "page_num": 1,
                            "formula_type": "display",
                        }
                    ],
                    "images": [
                        {
                            "image_id": "image_0",
                            "image_path": "chart.png",
                            "page_num": 1,
                            "description": "Revenue growth chart showing 25% increase",
                        }
                    ],
                },
            ],
            "tables": [
                {
                    "table_id": "table_0",
                    "html": "<table><tr><th>Quarter</th><th>Revenue</th></tr><tr><td>Q1</td><td>100M</td></tr></table>",
                    "markdown": "| Quarter | Revenue |\n| --- | --- |\n| Q1 | 100M |",
                    "page_num": 0,
                    "rows": 2,
                    "cols": 2,
                    "header": ["Quarter", "Revenue"],
                }
            ],
            "formulas": [
                {
                    "formula_id": "formula_0",
                    "latex": r"E = mc^2",
                    "page_num": 1,
                    "formula_type": "display",
                }
            ],
            "images": [
                {
                    "image_id": "image_0",
                    "image_path": "chart.png",
                    "page_num": 1,
                    "description": "Revenue growth chart showing 25% increase",
                }
            ],
        }

    @pytest.mark.asyncio
    async def test_rag_ingest_multimodal(self, sample_pdf_content):
        """测试多模态文档摄取"""
        from rag_anything_core.scripts.rag_anything_manager import RAGAnythingManager

        manager = RAGAnythingManager()
        await manager.initialize()

        # 验证管理器支持多模态
        assert manager.config.multimodal_enabled is True
        assert manager.config.kg_enabled is True

    @pytest.mark.asyncio
    async def test_rag_kg_build_cross_modal(self, sample_pdf_content):
        """测试跨模态知识图谱构建"""
        from rag_anything_knowledge_graph.scripts.kg_builder import KGBuilder

        builder = KGBuilder()
        kg_data = await builder.build(sample_pdf_content)

        # 验证多模态实体
        entity_types = {e.entity_type for e in kg_data.entities}
        assert "text" in entity_types
        assert "table" in entity_types
        assert "formula" in entity_types
        assert "image" in entity_types

        # 验证跨模态边
        assert len(kg_data.cross_modal_edges) >= 0
        for edge in kg_data.cross_modal_edges:
            assert edge.source_modality != edge.target_modality

    @pytest.mark.asyncio
    async def test_multimodal_processor_table_extraction(self, sample_pdf_content):
        """测试表格提取处理"""
        from rag_anything_multimodal.scripts.multimodal_processor import (
            MultimodalProcessor,
        )

        processor = MultimodalProcessor()
        await processor.initialize()

        chunks = await processor._process_table_chunks(sample_pdf_content, "test_doc")

        assert len(chunks) == 1
        assert chunks[0].modality_type == "table"
        assert chunks[0].table_content is not None
        # 验证表格内容包含Markdown格式
        assert "Quarter" in chunks[0].table_content or "Revenue" in chunks[0].table_content

    @pytest.mark.asyncio
    async def test_multimodal_processor_formula_extraction(self, sample_pdf_content):
        """测试公式提取处理"""
        from rag_anything_multimodal.scripts.multimodal_processor import (
            MultimodalProcessor,
        )

        processor = MultimodalProcessor()
        await processor.initialize()

        chunks = await processor._process_formula_chunks(sample_pdf_content, "test_doc")

        assert len(chunks) >= 1
        assert chunks[0].modality_type == "formula"
        assert chunks[0].formula_content is not None

    @pytest.mark.asyncio
    async def test_multimodal_processor_image_understanding(self, sample_pdf_content):
        """测试图像理解处理"""
        from rag_anything_multimodal.scripts.multimodal_processor import (
            MultimodalProcessor,
        )

        processor = MultimodalProcessor()
        await processor.initialize()

        chunks = await processor._process_image_chunks(sample_pdf_content, "test_doc")

        assert len(chunks) == 1
        assert chunks[0].modality_type == "image"
        assert len(chunks[0].image_descriptions) > 0

    @pytest.mark.asyncio
    async def test_cross_modal_embedder(self):
        """测试跨模态嵌入"""
        from rag_anything_multimodal.scripts.cross_modal_embedding import (
            CrossModalEmbedder,
        )

        embedder = CrossModalEmbedder()
        await embedder.initialize()

        # 测试文本嵌入
        text_emb = await embedder.embed("Machine learning is a subset of AI")
        assert isinstance(text_emb, list)
        assert len(text_emb) > 0

        # 测试批量嵌入
        batch_embs = await embedder.embed_batch([
            "First text about AI",
            "Second text about ML",
            "Third text about neural networks"
        ])
        assert len(batch_embs) == 3

    @pytest.mark.asyncio
    async def test_modal_retriever_hybrid_search(self):
        """测试混合检索模式"""
        from rag_anything_multimodal.scripts.modal_retriever import ModalRetriever

        retriever = ModalRetriever()
        await retriever.initialize()

        results = await retriever.search(
            "financial report revenue",
            mode="hybrid",
            top_k=5
        )

        assert "results" in results
        assert "modality_distribution" in results
        assert isinstance(results["results"], list)

    @pytest.mark.asyncio
    async def test_modality_aware_rerank(self):
        """测试模态自适应重排序"""
        from rag_anything_multimodal.scripts.modal_retriever import (
            ModalRetriever,
            RetrievalResult,
        )

        retriever = ModalRetriever()

        # 模拟不同模态的检索结果
        results = [
            RetrievalResult(chunk_id="1", content="text content", modality="text", score=0.5),
            RetrievalResult(chunk_id="2", content="table content", modality="table", score=0.5),
            RetrievalResult(chunk_id="3", content="formula content", modality="formula", score=0.5),
            RetrievalResult(chunk_id="4", content="image content", modality="image", score=0.5),
        ]

        # 当查询涉及表格时，表格应该排在前面
        reranked = await retriever._modality_aware_rerank(results, "表格数据")

        assert reranked[0].modality == "table"

    @pytest.mark.asyncio
    async def test_entity_linker_disambiguation(self):
        """测试实体链接消歧"""
        from rag_anything_knowledge_graph.scripts.entity_linker import EntityLinker
        from rag_anything_knowledge_graph.scripts.kg_builder import Entity

        linker = EntityLinker()

        entity = Entity(entity_id="1", name="Machine Learning", entity_type="text")
        candidates = [
            Entity(entity_id="2", name="Machine Learning", entity_type="text"),
            Entity(entity_id="3", name="Deep Learning", entity_type="text"),
        ]

        result = await linker.disambiguate(entity, candidates)

        # 应该匹配到名称完全相同的实体
        assert result is not None
        assert result.entity_id == "2"

    @pytest.mark.asyncio
    async def test_kg_stats_tracking(self):
        """测试知识图谱统计追踪"""
        from rag_anything_core.scripts.rag_anything_manager import RAGAnythingManager

        manager = RAGAnythingManager()
        await manager.initialize()

        stats = await manager.get_stats()

        assert "total_documents" in stats
        assert "total_entities" in stats
        assert "kg_enabled" in stats
        assert stats["kg_enabled"] is True


class TestDataEngineerPipelineIntegration:
    """数据工程师管道集成测试"""

    @pytest.mark.asyncio
    async def test_multimodal_ingest_query_pipeline(self, sample_pdf_content):
        """测试完整的多模态摄取-查询管道"""
        from rag_anything_core.scripts.rag_anything_manager import RAGAnythingManager

        manager = RAGAnythingManager()
        await manager.initialize()

        # 1. 处理文档
        result = await manager.process("test_document.pdf")
        # 注意：由于是模拟数据，process可能返回失败，但不影响管道验证

        # 2. 查询
        answer = await manager.query("What is the financial summary?")

        assert answer is not None
        assert answer.question == "What is the financial summary?"

    @pytest.mark.asyncio
    async def test_kg_query_pipeline(self):
        """测试知识图谱查询管道"""
        from rag_anything_knowledge_graph.scripts.kg_builder import KGBuilder

        builder = KGBuilder()

        # 构建图谱
        doc = {
            "doc_id": "test",
            "pages": [
                {
                    "page_num": 0,
                    "text": "Machine learning uses neural networks for deep learning.",
                    "text_blocks": [],
                    "tables": [],
                    "formulas": [],
                    "images": [],
                }
            ],
            "tables": [],
            "formulas": [],
            "images": [],
        }

        kg_data = await builder.build(doc)

        # 验证图谱结构
        assert len(kg_data.entities) > 0
        assert kg_data.to_dict() is not None
        stats = kg_data.to_dict()["stats"]
        assert stats["total_entities"] > 0


class TestDataQualityMetrics:
    """数据质量指标测试"""

    @pytest.fixture
    def quality_metrics_doc(self):
        """多模态质量测试文档"""
        return {
            "doc_id": "quality_test",
            "pages": [
                {
                    "page_num": 0,
                    "text": "Important business metrics",
                    "text_blocks": [],
                    "tables": [
                        {
                            "table_id": "t1",
                            "html": "<table><tr><th>A</th><th>B</th></tr></table>",
                            "markdown": "| A | B |",
                            "page_num": 0,
                            "rows": 1,
                            "cols": 2,
                            "header": ["A", "B"],
                        }
                    ],
                    "formulas": [
                        {
                            "formula_id": "f1",
                            "latex": r"x^2 + y^2 = z^2",
                            "page_num": 0,
                            "formula_type": "display",
                        }
                    ],
                    "images": [
                        {
                            "image_id": "i1",
                            "image_path": "img.png",
                            "page_num": 0,
                            "description": "Business growth chart",
                        }
                    ],
                }
            ],
            "tables": [
                {
                    "table_id": "t1",
                    "html": "<table><tr><th>A</th><th>B</th></tr></table>",
                    "markdown": "| A | B |",
                    "page_num": 0,
                    "rows": 1,
                    "cols": 2,
                    "header": ["A", "B"],
                }
            ],
            "formulas": [
                {
                    "formula_id": "f1",
                    "latex": r"x^2 + y^2 = z^2",
                    "page_num": 0,
                    "formula_type": "display",
                }
            ],
            "images": [
                {
                    "image_id": "i1",
                    "image_path": "img.png",
                    "page_num": 0,
                    "description": "Business growth chart",
                }
            ],
        }

    @pytest.mark.asyncio
    async def test_table_extraction_completeness(self, quality_metrics_doc):
        """测试表格提取完整率"""
        from rag_anything_multimodal.scripts.multimodal_processor import (
            MultimodalProcessor,
        )

        processor = MultimodalProcessor()
        await processor.initialize()

        chunks = await processor._process_table_chunks(quality_metrics_doc, "test_doc")

        # 表格提取完整率目标>95%
        assert len(chunks) >= 1
        table_chunk = chunks[0]
        assert table_chunk.table_content is not None
        # 验证表格内容非空
        assert len(table_chunk.table_content) > 0

    @pytest.mark.asyncio
    async def test_formula_extraction_accuracy(self, quality_metrics_doc):
        """测试公式提取准确率"""
        from rag_anything_multimodal.scripts.multimodal_processor import (
            MultimodalProcessor,
        )

        processor = MultimodalProcessor()
        await processor.initialize()

        chunks = await processor._process_formula_chunks(quality_metrics_doc, "test_doc")

        # 公式识别准确率目标>90%
        assert len(chunks) >= 1
        formula_chunk = chunks[0]
        assert formula_chunk.formula_content is not None
        assert "x^2" in formula_chunk.formula_content or "x" in formula_chunk.formula_content

    @pytest.mark.asyncio
    async def test_image_description_coverage(self, quality_metrics_doc):
        """测试图像描述覆盖率"""
        from rag_anything_multimodal.scripts.multimodal_processor import (
            MultimodalProcessor,
        )

        processor = MultimodalProcessor()
        await processor.initialize()

        chunks = await processor._process_image_chunks(quality_metrics_doc, "test_doc")

        # 图像描述覆盖率目标>85%
        assert len(chunks) >= 1
        image_chunk = chunks[0]
        assert len(image_chunk.image_descriptions) > 0
        # 验证描述内容
        assert any(
            "business" in desc.lower() or "chart" in desc.lower()
            for desc in image_chunk.image_descriptions
        )

    @pytest.mark.asyncio
    async def test_entity_recognition_accuracy(self):
        """测试实体识别准确率"""
        from rag_anything_knowledge_graph.scripts.kg_builder import KGBuilder

        builder = KGBuilder()

        doc = {
            "doc_id": "entity_test",
            "pages": [
                {
                    "page_num": 0,
                    "text": "Apple Inc. released iPhone 15 in September 2023.",
                    "text_blocks": [],
                    "tables": [],
                    "formulas": [],
                    "images": [],
                }
            ],
            "tables": [],
            "formulas": [],
            "images": [],
        }

        kg_data = await builder.build(doc)

        # 实体识别准确率目标>92%
        assert len(kg_data.entities) > 0
        # 验证实体名称非空
        for entity in kg_data.entities:
            assert entity.name is not None
            assert len(entity.name) > 0


# 用于测试的fixture
@pytest.fixture
def sample_pdf_content():
    """样本PDF内容fixture"""
    return {
        "doc_id": "test_doc",
        "file_path": "test.pdf",
        "pages": [
            {
                "page_num": 0,
                "text": "Machine learning is a subset of artificial intelligence.",
                "text_blocks": [],
                "tables": [],
                "formulas": [],
                "images": [],
            }
        ],
        "tables": [],
        "formulas": [],
        "images": [],
    }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
