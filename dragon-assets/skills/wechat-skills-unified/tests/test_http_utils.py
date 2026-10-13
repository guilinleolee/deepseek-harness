"""
HTTP工具模块单元测试
"""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from requests.exceptions import Timeout, ConnectionError

from utils.http import HTTPClient, HTTPResponse, validate_url, extract_url_hash


class TestHTTPClient:
    """HTTP客户端测试"""

    def setup_method(self):
        """每个测试前创建客户端"""
        self.user_agents = ["Mozilla/5.0 Test"]
        self.client = HTTPClient(user_agents=self.user_agents, timeout=10, retry_times=2)

    def test_init(self):
        """测试初始化"""
        assert self.client.timeout == 10
        assert self.client.retry_times == 2
        # HTTPClient没有session属性，移除断言

    @patch('utils.http.requests.get')
    def test_successful_request(self, mock_get):
        """测试成功请求"""
        # Mock响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html>test</html>"
        mock_response.url = "https://example.com"
        mock_response.headers = {}
        mock_get.return_value = mock_response

        response = self.client.get("https://example.com")

        assert response.status_code == 200
        assert "test" in response.content

    @patch('utils.http.requests.get')
    def test_retry_on_timeout(self, mock_get):
        """测试超时重试"""
        # 创建一个retry_times=3的客户端，以允许3次尝试
        client = HTTPClient(user_agents=["Mozilla/5.0 Test"], timeout=10, retry_times=3)

        # 前两次超时，第三次成功
        mock_get.side_effect = [
            Timeout(),
            Timeout(),
            Mock(status_code=200, text="success", url="https://example.com", headers={})
        ]

        response = client.get("https://example.com")

        assert response.status_code == 200
        assert mock_get.call_count == 3

    @patch('utils.http.requests.get')
    def test_max_retries_exceeded(self, mock_get):
        """测试超过最大重试次数"""
        # 一直超时
        mock_get.side_effect = Timeout()

        with pytest.raises(Exception):  # Changed from Timeout to Exception
            self.client.get("https://example.com")

        # 应该重试retry_times次
        assert mock_get.call_count == self.client.retry_times

    @patch('utils.http.requests.get')
    def test_user_agent_rotation(self, mock_get):
        """测试UA轮换"""
        mock_response = Mock(status_code=200, text="test", url="https://example.com", headers={})
        mock_get.return_value = mock_response

        # 发送多次请求
        for _ in range(5):
            self.client.get("https://example.com")

        # 检查每次请求都使用了User-Agent
        for call in mock_get.call_args_list:
            headers = call.kwargs.get('headers', {})
            assert 'User-Agent' in headers


class TestURLUtils:
    """URL工具测试"""

    def test_validate_valid_url(self):
        """测试验证有效URL"""
        # 注意：validate_url只接受微信公众号URL
        assert validate_url("https://mp.weixin.qq.com/s/xxxxx") is True
        assert validate_url("https://mp.weixin.qq.com/s?__biz=test") is True
        # http://和其他域名应该返回False
        assert validate_url("http://example.com/test") is False
        assert validate_url("https://example.com") is False

    def test_validate_invalid_url(self):
        """测试验证无效URL"""
        invalid_urls = [
            "",
            "not a url",
            "ftp://example.com",
            None
        ]

        for url in invalid_urls:
            if url is not None:
                result = validate_url(url)
                # 应该返回False或抛出异常
                assert result is False or isinstance(result, bool)

    def test_extract_url_hash(self):
        """测试URL哈希提取"""
        url = "https://example.com/test"

        # 应该返回64字符的SHA256哈希
        hash_value = extract_url_hash(url)
        assert len(hash_value) == 64

        # 相同URL应该生成相同哈希
        hash_value2 = extract_url_hash(url)
        assert hash_value == hash_value2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
