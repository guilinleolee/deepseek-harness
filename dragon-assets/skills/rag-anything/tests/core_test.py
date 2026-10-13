"""RAG-Anything核心模块测试"""

import asyncio
import tempfile
from pathlib import Path

import pytest


class TestRAGAnythingCore:
    """核心模块测试"""

    @pytest.fixture
    def sample_config(self):
        """样本配置"""
        from rag_anything_core.scripts.config import RAGAnythingConfig

        return RAGAnythingConfig(
            data_dir=tempfile.mkdtemp(),
            cache_dir=tempfile.mkdtemp(),
            vector_store="chroma",
            chunk_size=512,
            chunk_overlap=50,
        )

    @pytest.fixture
    def manager(self, sample_config):
        """创建管理器实例"""
        from rag_anything_core.scripts.rag_anything_manager import RAGAnythingManager

        return RAGAnythingManager(config=sample_config)

    @pytest.mark.asyncio
    async def test_manager_initialization(self, manager):
        """测试管理器初始化"""
        assert manager is not None
        assert manager.config is not None
        assert not manager._initialized

        await manager.initialize()

        assert manager._initialized

    @pytest.mark.asyncio
    async def test_process_nonexistent_file(self, manager):
        """测试处理不存在的文件"""
        result = await manager.process("nonexistent_file.pdf")

        assert not result.success
        assert "文件不存在" in result.error

    @pytest.mark.asyncio
    async def test_query(self, manager):
        """测试查询"""
        result = await manager.query("测试问题")

        assert result is not None
        assert result.question == "测试问题"
        assert isinstance(result.sources, list)

    @pytest.mark.asyncio
    async def test_get_stats(self, manager):
        """测试统计信息"""
        stats = await manager.get_stats()

        assert "total_documents" in stats
        assert "total_entities" in stats
        assert "kg_enabled" in stats
        assert stats["kg_enabled"] is True

    @pytest.mark.asyncio
    async def test_list_documents(self, manager):
        """测试文档列表"""
        docs = await manager.list_documents()

        assert isinstance(docs, list)


class TestConfig:
    """配置测试"""

    def test_default_config(self):
        """测试默认配置"""
        from rag_anything_core.scripts.config import get_default_config

        config = get_default_config()

        assert config.data_dir == "./data"
        assert config.chunk_size == 512
        assert config.chunk_overlap == 50
        assert config.kg_enabled is True
        assert config.multimodal_enabled is True

    def test_config_to_dict(self):
        """测试配置转字典"""
        from rag_anything_core.scripts.config import RAGAnythingConfig

        config = RAGAnythingConfig(data_dir="/test", chunk_size=1024)
        config_dict = config.to_dict()

        assert config_dict["data_dir"] == "/test"
        assert config_dict["chunk_size"] == 1024

    def test_config_from_dict(self):
        """测试从字典创建配置"""
        from rag_anything_core.scripts.config import RAGAnythingConfig

        config_dict = {
            "data_dir": "/custom",
            "chunk_size": 2048,
            "unknown_field": "ignored",
        }

        config = RAGAnythingConfig.from_dict(config_dict)

        assert config.data_dir == "/custom"
        assert config.chunk_size == 2048

    def test_config_update(self):
        """测试配置更新"""
        from rag_anything_core.scripts.config import RAGAnythingConfig

        config = RAGAnythingConfig()
        config.update(chunk_size=1024, top_k=20)

        assert config.chunk_size == 1024
        assert config.top_k == 20


class TestUtils:
    """工具函数测试"""

    def test_async_retry(self):
        """测试异步重试装饰器"""
        from rag_anything_core.scripts.utils import async_retry

        attempt_count = 0

        @async_retry(max_attempts=3, delay=0.1)
        async def flaky_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ValueError("Temporary error")
            return "success"

        result = asyncio.run(flaky_function())

        assert result == "success"
        assert attempt_count == 2

    def test_async_retry_max_attempts(self):
        """测试异步重试达到最大次数"""
        from rag_anything_core.scripts.utils import async_retry

        @async_retry(max_attempts=2, delay=0.1)
        async def always_fail():
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            asyncio.run(always_fail())

    def test_get_file_type(self):
        """测试文件类型判断"""
        from rag_anything_core.scripts.utils import get_file_type

        assert get_file_type("test.pdf") == "pdf"
        assert get_file_type("test.docx") == "docx"
        assert get_file_type("test.xlsx") == "xlsx"
        assert get_file_type("test.txt") == "text"
        assert get_file_type("test.png") == "image"
        assert get_file_type("test.unknown") == "unknown"

    def test_calculate_file_hash(self):
        """测试文件哈希计算"""
        from rag_anything_core.scripts.utils import calculate_file_hash

        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            temp_path = f.name

        hash1 = calculate_file_hash(temp_path)
        hash2 = calculate_file_hash(temp_path)
        assert hash1 == hash2

        # 不同内容不同哈希
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"different content")
            temp_path2 = f.name

        hash3 = calculate_file_hash(temp_path2)
        assert hash1 != hash3

    def test_batch_items(self):
        """测试列表分批"""
        from rag_anything_core.scripts.utils import batch_items

        items = list(range(10))
        batches = batch_items(items, batch_size=3)

        assert len(batches) == 4
        assert batches[0] == [0, 1, 2]
        assert batches[3] == [9]

    def test_clean_text(self):
        """测试文本清理"""
        from rag_anything_core.scripts.utils import clean_text

        assert clean_text("  hello   world  ") == "hello world"
        assert clean_text("\n\ttest\n") == "test"

    def test_truncate_text(self):
        """测试文本截断"""
        from rag_anything_core.scripts.utils import truncate_text

        text = "a" * 100
        truncated = truncate_text(text, max_length=20)

        assert len(truncated) == 20
        assert truncated.endswith("...")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
