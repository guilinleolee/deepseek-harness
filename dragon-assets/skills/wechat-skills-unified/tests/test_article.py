"""
Article模型单元测试
"""

import pytest
import json
from datetime import datetime

from models.article import Article


class TestArticle:
    """Article模型测试"""

    def test_create_minimal(self):
        """测试创建最小Article"""
        article = Article(
            url="https://example.com/test",
            url_hash="",
            title="Test",
            author="Author",
            account_name="Account"
        )

        assert article.url == "https://example.com/test"
        assert article.title == "Test"
        assert article.url_hash  # 应该自动生成
        assert len(article.url_hash) == 64  # SHA256长度

    def test_hash_url(self):
        """测试URL哈希"""
        url = "https://example.com/test"
        hash1 = Article._hash_url(url)
        hash2 = Article._hash_url(url)

        assert hash1 == hash2  # 相同URL应该生成相同哈希
        assert len(hash1) == 64  # SHA256十六进制长度

    def test_to_dict(self):
        """测试序列化"""
        article = Article(
            url="https://example.com/test",
            url_hash="",
            title="Test",
            author="Author",
            account_name="Account",
            content_text="Some content"
        )

        data = article.to_dict()

        assert isinstance(data, dict)
        assert data["title"] == "Test"
        assert data["url"] == "https://example.com/test"
        assert data["word_count"] == len("Some content")

    def test_to_json(self):
        """测试JSON序列化"""
        article = Article(
            url="https://example.com/test",
            url_hash="",
            title="测试标题",
            author="作者",
            account_name="公众号"
        )

        json_str = article.to_json()
        data = json.loads(json_str)

        assert data["title"] == "测试标题"
        assert data["author"] == "作者"

    def test_word_count_calculation(self):
        """测试字数计算"""
        article = Article(
            url="https://example.com/test",
            url_hash="",
            title="Test",
            author="Author",
            account_name="Account",
            content_text="This is a test content with some words."
        )

        # __post_init__应该自动计算字数
        assert article.word_count == len("This is a test content with some words.")

    def test_save_and_load(self):
        """测试保存和加载"""
        import tempfile
        import os

        article = Article(
            url="https://example.com/test",
            url_hash="",
            title="测试文章",
            author="作者",
            account_name="公众号",
            content_markdown="# 测试\n\n内容"
        )

        # 保存到临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".md")
        temp_file.close()

        try:
            article.save_markdown(temp_file.name)

            # 检查文件存在
            assert os.path.exists(temp_file.name)

            # 读取文件内容
            with open(temp_file.name, 'r', encoding='utf-8') as f:
                content = f.read()

            assert "测试文章" in content
            assert "内容" in content

        finally:
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
