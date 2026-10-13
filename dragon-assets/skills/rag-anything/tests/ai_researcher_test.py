"""AI研究员RAG-Anything集成测试"""

import pytest
import asyncio
import tempfile
from pathlib import Path


class TestRAGAnythingIntegration:
    """RAG-Anything与AI研究员能力集成测试"""

    @pytest.fixture
    def sample_paper_path(self):
        """创建样本论文路径"""
        temp_dir = tempfile.mkdtemp()
        return temp_dir

    @pytest.mark.asyncio
    async def test_rag_anything_core_initialization(self):
        """测试RAG-Anything核心初始化"""
        from rag_anything_core import RAGAnythingManager

        manager = RAGAnythingManager()
        await manager.initialize()

        assert manager._initialized
        stats = await manager.get_stats()
        assert "total_documents" in stats
        assert stats["kg_enabled"] is True

    @pytest.mark.asyncio
    async def test_multimodal_rag_workflow(self):
        """测试多模态RAG完整工作流"""
        from rag_anything_core import RAGAnythingManager

        manager = RAGAnythingManager()
        await manager.initialize()

        # 查询测试
        result = await manager.query("测试多模态RAG查询")

        assert result is not None
        assert result.question == "测试多模态RAG查询"
        assert isinstance(result.sources, list)

    @pytest.mark.asyncio
    async def test_mineru_parser_initialization(self):
        """测试MinerU解析器初始化"""
        from rag_anything_mineru import MinerUParser

        parser = MinerUParser()
        await parser.initialize()

        assert parser._initialized

    @pytest.mark.asyncio
    async def test_formula_extraction(self):
        """测试公式提取能力"""
        from rag_anything_mineru import MinerUParser
        from rag_anything_knowledge_graph import KGBuilder

        parser = MinerUParser()
        await parser.initialize()

        # 模拟公式数据
        formula_data = {
            "formula_id": "test_formula",
            "latex": r"\frac{a}{b} + \sqrt{c}",
            "page_num": 0,
            "formula_type": "display"
        }

        # 提取公式变量
        kg_builder = KGBuilder()
        variables = kg_builder._extract_formula_variables(formula_data["latex"])

        assert isinstance(variables, list)

    @pytest.mark.asyncio
    async def test_table_extraction(self):
        """测试表格提取能力"""
        from rag_anything_mineru import MinerUParser

        parser = MinerUParser()
        await parser.initialize()

        # 模拟表格数据
        table_data = {
            "table_id": "test_table",
            "cells": [["Name", "Score"], ["Alice", "95"], ["Bob", "88"]],
            "bbox": (0, 0, 100, 50)
        }

        result = await parser.extract_tables({"pages": [], "tables": [table_data], "page_num": 0})

        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_image_understanding(self):
        """测试图像理解能力"""
        from rag_anything_mineru import MinerUParser

        parser = MinerUParser()
        await parser.initialize()

        # 模拟图像数据
        image_data = {
            "image_id": "test_image",
            "image_path": "test.png",
            "page_num": 0,
            "description": "A neural network architecture diagram"
        }

        result = await parser.understand_image(image_data)

        assert result is not None

    @pytest.mark.asyncio
    async def test_knowledge_graph_construction(self):
        """测试知识图谱构建"""
        from rag_anything_knowledge_graph import KGBuilder

        kg_builder = KGBuilder()

        # 模拟解析文档
        sample_doc = {
            "doc_id": "test_doc",
            "pages": [
                {
                    "page_num": 0,
                    "text": "Machine learning is a subset of artificial intelligence.",
                    "text_blocks": []
                }
            ],
            "tables": [],
            "formulas": [
                {
                    "formula_id": "formula_0",
                    "latex": r"E = mc^2",
                    "page_num": 0,
                    "formula_type": "display"
                }
            ],
            "images": []
        }

        kg_data = await kg_builder.build(sample_doc)

        assert kg_data is not None
        assert len(kg_data.entities) > 0
        assert len(kg_data.relations) >= 0

    @pytest.mark.asyncio
    async def test_multimodal_retriever_initialization(self):
        """测试多模态检索器初始化"""
        from rag_anything_multimodal import ModalRetriever

        retriever = ModalRetriever()
        await retriever.initialize()

        assert retriever._initialized

    @pytest.mark.asyncio
    async def test_hybrid_search(self):
        """测试混合检索模式"""
        from rag_anything_multimodal import ModalRetriever

        retriever = ModalRetriever()
        await retriever.initialize()

        results = await retriever.search("test query", mode="hybrid", top_k=5)

        assert "results" in results
        assert "modality_distribution" in results
        assert isinstance(results["results"], list)

    @pytest.mark.asyncio
    async def test_modality_aware_rerank(self):
        """测试模态自适应重排序"""
        from rag_anything_multimodal import ModalRetriever, RetrievalResult

        retriever = ModalRetriever()

        # 模拟不同模态的检索结果
        results = [
            RetrievalResult(chunk_id="1", content="text result", modality="text", score=0.5),
            RetrievalResult(chunk_id="2", content="table result", modality="table", score=0.5),
            RetrievalResult(chunk_id="3", content="formula result", modality="formula", score=0.5),
            RetrievalResult(chunk_id="4", content="image result", modality="image", score=0.5),
        ]

        # 查询表格相关内容
        reranked = await retriever._modality_aware_rerank(results, "表格数据")

        # 表格应该排在前面
        assert reranked[0].modality == "table"

    @pytest.mark.asyncio
    async def test_cross_modal_embedding(self):
        """测试跨模态Embedding"""
        from rag_anything_multimodal import CrossModalEmbedder

        embedder = CrossModalEmbedder()
        await embedder.initialize()

        # 文本嵌入
        text_embedding = await embedder.embed("Machine learning")

        assert isinstance(text_embedding, list)
        assert len(text_embedding) > 0

    @pytest.mark.asyncio
    async def test_entity_linking(self):
        """测试实体链接"""
        from rag_anything_knowledge_graph import KGBuilder, Entity

        kg_builder = KGBuilder()

        # 创建实体
        entity = Entity(
            entity_id="test_1",
            name="Machine Learning",
            entity_type="text"
        )

        # 模拟无知识库的链接
        result = await kg_builder.link_entity(entity)

        assert result is None

    @pytest.mark.asyncio
    async def test_relation_extraction(self):
        """测试关系抽取"""
        from rag_anything_knowledge_graph import KGBuilder, Entity, RelationExtractor

        kg_builder = KGBuilder()
        extractor = RelationExtractor()

        # 创建实体
        entities = [
            Entity(entity_id="1", name="ML", entity_type="text"),
            Entity(entity_id="2", name="AI", entity_type="text"),
        ]

        text = "Machine Learning is a subset of Artificial Intelligence."
        relations = await extractor.extract_relations(text, entities)

        assert isinstance(relations, list)

    @pytest.mark.asyncio
    async def test_dspy_multimodal_signature(self):
        """测试DSPy多模态Signature（如果有DSPy可用）"""
        try:
            import dspy

            # 定义多模态RAG Signature
            class MultimodalRAG(dspy.Signature):
                """多模态RAG，支持文本、表格、公式、图像的联合检索"""
                query: str = dspy.InputField(desc="用户查询")
                text_context: str = dspy.InputField(desc="文本检索结果")
                table_context: str = dspy.InputField(desc="表格检索结果")
                formula_context: str = dspy.InputField(desc="公式检索结果")
                answer: str = dspy.OutputField(desc="综合多模态信息的回答")

            assert MultimodalRAG is not None

        except ImportError:
            pytest.skip("DSPy not installed")


class TestRAGResearchWorkflow:
    """RAG研究工作流测试"""

    @pytest.mark.asyncio
    async def test_research_workflow(self):
        """测试完整研究工作流"""
        from rag_anything_core import RAGAnythingManager

        # 1. 初始化管理器
        manager = RAGAnythingManager()
        await manager.initialize()

        # 2. 查询
        result = await manager.query("什么是多模态RAG?")

        # 3. 获取统计
        stats = await manager.get_stats()

        assert stats["kg_enabled"] is True
        assert stats["multimodal_enabled"] is True

    @pytest.mark.asyncio
    async def test_paper_analysis_workflow(self):
        """测试论文分析工作流"""
        from rag_anything_mineru import MinerUParser
        from rag_anything_knowledge_graph import KGBuilder

        # 1. 解析论文
        parser = MinerUParser()
        await parser.initialize()

        # 2. 构建知识图谱
        kg_builder = KGBuilder()

        sample_doc = {
            "doc_id": "paper_1",
            "pages": [
                {
                    "page_num": 0,
                    "text": "Deep learning has revolutionized computer vision.",
                    "text_blocks": []
                }
            ],
            "tables": [
                {
                    "table_id": "table_0",
                    "html": "<table><tr><th>Method</th><th>Accuracy</th></tr><tr><td>CNN</td><td>95%</td></tr></table>",
                    "markdown": "| Method | Accuracy |\n| --- | --- |\n| CNN | 95% |",
                    "page_num": 0,
                    "rows": 2,
                    "cols": 2,
                    "header": ["Method", "Accuracy"]
                }
            ],
            "formulas": [
                {
                    "formula_id": "formula_0",
                    "latex": r"y = f(x) + \epsilon",
                    "page_num": 0,
                    "formula_type": "display"
                }
            ],
            "images": [
                {
                    "image_id": "image_0",
                    "image_path": "architecture.png",
                    "page_num": 0,
                    "description": "Neural network architecture diagram"
                }
            ]
        }

        kg_data = await kg_builder.build(sample_doc)

        # 验证各类型实体
        entity_types = {e.entity_type for e in kg_data.entities}
        assert "text" in entity_types
        assert "table" in entity_types
        assert "formula" in entity_types
        assert "image" in entity_types

    @pytest.mark.asyncio
    async def test_multimodal_retrieval_workflow(self):
        """测试多模态检索工作流"""
        from rag_anything_multimodal import ModalRetriever

        retriever = ModalRetriever()
        await retriever.initialize()

        # 1. 混合检索
        results = await retriever.search(
            "深度学习的准确率对比",
            mode="hybrid",
            top_k=10
        )

        assert "results" in results
        assert "modality_distribution" in results

        # 2. 重排序
        if results["results"]:
            reranked = await retriever._modality_aware_rerank(
                results["results"],
                "表格对比"
            )
            assert isinstance(reranked, list)

        # 3. 生成摘要
        summary = await retriever._generate_summary(
            results["results"],
            "深度学习的准确率对比"
        )
        assert isinstance(summary, str)
        assert len(summary) > 0


class TestQualityMetrics:
    """质量指标测试"""

    @pytest.mark.asyncio
    async def test_retrieval_quality_metrics(self):
        """测试检索质量指标"""
        from rag_anything_multimodal import ModalRetriever

        retriever = ModalRetriever()
        await retriever.initialize()

        # 模拟检索结果
        results = await retriever.search("test query", mode="hybrid")

        # 验证模态分布
        modality_dist = results["modality_distribution"]
        assert "text" in modality_dist
        assert "table" in modality_dist
        assert "formula" in modality_dist
        assert "image" in modality_dist

    @pytest.mark.asyncio
    async def test_knowledge_graph_metrics(self):
        """测试知识图谱质量指标"""
        from rag_anything_knowledge_graph import KGBuilder

        kg_builder = KGBuilder()

        sample_doc = {
            "doc_id": "metrics_test",
            "pages": [
                {
                    "page_num": 0,
                    "text": "This paper presents a novel method for image classification.",
                    "text_blocks": []
                }
            ],
            "tables": [
                {
                    "table_id": "t1",
                    "html": "<table><tr><th>Model</th></tr><tr><td>ResNet</td></tr></table>",
                    "markdown": "| Model |\n| --- |\n| ResNet |",
                    "page_num": 0,
                    "rows": 2,
                    "cols": 1,
                    "header": ["Model"]
                }
            ],
            "formulas": [
                {
                    "formula_id": "f1",
                    "latex": r"accuracy = \frac{TP + TN}{TP + TN + FP + FN}",
                    "page_num": 0,
                    "formula_type": "display"
                }
            ],
            "images": []
        }

        kg_data = await kg_builder.build(sample_doc)

        # 验证实体类型覆盖
        entity_type_counts = {}
        for entity in kg_data.entities:
            entity_type_counts[entity.entity_type] = entity_type_counts.get(entity.entity_type, 0) + 1

        assert entity_type_counts.get("text", 0) > 0
        assert entity_type_counts.get("table", 0) > 0
        assert entity_type_counts.get("formula", 0) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
