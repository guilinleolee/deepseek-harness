"""多模态模块测试"""

import pytest


class TestMultimodalProcessor:
    """多模态处理器测试"""

    @pytest.fixture
    def processor(self):
        """创建处理器实例"""
        from rag_anything_multimodal.scripts.multimodal_processor import (
            MultimodalProcessor,
        )

        return MultimodalProcessor()

    @pytest.fixture
    def sample_parsed_doc(self):
        """样本解析文档"""
        return {
            "doc_id": "test_doc",
            "file_path": "test.pdf",
            "pages": [
                {
                    "page_num": 0,
                    "text": "This is a sample text about machine learning.",
                    "text_blocks": [
                        {"text": "This is a sample text about machine learning.", "type": "paragraph"}
                    ],
                    "tables": [],
                    "formulas": [],
                    "images": [],
                }
            ],
            "tables": [
                {
                    "table_id": "table_0",
                    "html": "<table><tr><th>Name</th></tr><tr><td>Alice</td></tr></table>",
                    "markdown": "| Name |\n| --- |\n| Alice |",
                    "page_num": 0,
                    "rows": 2,
                    "cols": 1,
                    "header": ["Name"],
                }
            ],
            "formulas": [
                {
                    "formula_id": "formula_0",
                    "latex": "E = mc^2",
                    "page_num": 0,
                    "formula_type": "display",
                }
            ],
            "images": [
                {
                    "image_id": "image_0",
                    "image_path": "test.png",
                    "page_num": 0,
                    "description": "A neural network diagram",
                }
            ],
        }

    @pytest.mark.asyncio
    async def test_process_text_chunks(self, processor, sample_parsed_doc):
        """测试文本块处理"""
        await processor.initialize()

        chunks = await processor._process_text_chunks(
            sample_parsed_doc, "test_doc"
        )

        assert len(chunks) > 0
        assert any(c.modality_type == "text" for c in chunks)

    @pytest.mark.asyncio
    async def test_process_table_chunks(self, processor, sample_parsed_doc):
        """测试表格块处理"""
        await processor.initialize()

        chunks = await processor._process_table_chunks(
            sample_parsed_doc, "test_doc"
        )

        assert len(chunks) == 1
        assert chunks[0].modality_type == "table"
        assert chunks[0].table_content is not None

    @pytest.mark.asyncio
    async def test_process_formula_chunks(self, processor, sample_parsed_doc):
        """测试公式块处理"""
        await processor.initialize()

        chunks = await processor._process_formula_chunks(
            sample_parsed_doc, "test_doc"
        )

        assert len(chunks) >= 1
        assert chunks[0].modality_type == "formula"

    @pytest.mark.asyncio
    async def test_process_image_chunks(self, processor, sample_parsed_doc):
        """测试图像块处理"""
        await processor.initialize()

        chunks = await processor._process_image_chunks(
            sample_parsed_doc, "test_doc"
        )

        assert len(chunks) == 1
        assert chunks[0].modality_type == "image"

    @pytest.mark.asyncio
    async def test_chunk_to_text(self, processor):
        """测试块转文本"""
        from rag_anything_multimodal.scripts.multimodal_processor import (
            MultimodalChunk,
        )

        chunk = MultimodalChunk(
            chunk_id="test",
            text_content="Hello World",
            table_content="| A | B |\n| --- | --- |\n| 1 | 2 |",
            formula_content="E = mc^2",
            image_descriptions=["A diagram"],
        )

        text = processor._chunk_to_text(chunk)

        assert "Hello World" in text
        assert "[TABLE]" in text
        assert "[FORMULA]" in text
        assert "[IMAGE]" in text


class TestModalRetriever:
    """模态检索器测试"""

    @pytest.fixture
    def retriever(self):
        """创建检索器实例"""
        from rag_anything_multimodal.scripts.modal_retriever import ModalRetriever

        return ModalRetriever()

    @pytest.mark.asyncio
    async def test_retriever_initialization(self, retriever):
        """测试检索器初始化"""
        assert retriever is not None
        assert not retriever._initialized

        await retriever.initialize()

        assert retriever._initialized

    @pytest.mark.asyncio
    async def test_search(self, retriever):
        """测试搜索"""
        await retriever.initialize()

        results = await retriever.search("test query", mode="hybrid", top_k=5)

        assert "results" in results
        assert "modality_distribution" in results
        assert isinstance(results["results"], list)

    @pytest.mark.asyncio
    async def test_modality_aware_rerank(self, retriever):
        """测试模态自适应重排序"""
        from rag_anything_multimodal.scripts.modal_retriever import RetrievalResult

        results = [
            RetrievalResult(chunk_id="1", content="text", modality="text", score=0.5),
            RetrievalResult(chunk_id="2", content="table", modality="table", score=0.5),
            RetrievalResult(chunk_id="3", content="image", modality="image", score=0.5),
        ]

        reranked = await retriever._modality_aware_rerank(results, "表格数据")

        # 表格应该排在前面
        assert reranked[0].modality == "table"

    @pytest.mark.asyncio
    async def test_generate_summary(self, retriever):
        """测试摘要生成"""
        results = [
            {"content": "Sample result 1 about AI", "modality": "text"},
            {"content": "Sample result 2 about ML", "modality": "text"},
        ]

        summary = await retriever._generate_summary(results, "What is AI?")

        assert isinstance(summary, str)
        assert len(summary) > 0


class TestCrossModalEmbedder:
    """跨模态嵌入器测试"""

    @pytest.fixture
    def embedder(self):
        """创建嵌入器实例"""
        from rag_anything_multimodal.scripts.cross_modal_embedding import (
            CrossModalEmbedder,
        )

        return CrossModalEmbedder()

    @pytest.mark.asyncio
    async def test_embed_initialization(self, embedder):
        """测试嵌入器初始化"""
        assert embedder is not None
        assert not embedder._initialized

        await embedder.initialize()

        assert embedder._initialized

    @pytest.mark.asyncio
    async def test_simple_embed(self, embedder):
        """测试简单嵌入"""
        await embedder.initialize()

        embedding = await embedder.embed("test text")

        assert isinstance(embedding, list)
        assert len(embedding) > 0

    @pytest.mark.asyncio
    async def test_embed_batch(self, embedder):
        """测试批量嵌入"""
        await embedder.initialize()

        texts = ["text 1", "text 2", "text 3"]
        embeddings = await embedder.embed_batch(texts)

        assert len(embeddings) == 3
        assert all(isinstance(e, list) for e in embeddings)

    @pytest.mark.asyncio
    async def test_compute_similarity(self, embedder):
        """测试相似度计算"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        vec3 = [0.0, 1.0, 0.0]

        sim_same = await embedder.compute_similarity(vec1, vec2)
        sim_diff = await embedder.compute_similarity(vec1, vec3)

        assert sim_same == 1.0
        assert sim_diff == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
