"""
安全功能测试
测试日志脱敏、路径验证、速率限制
"""

import pytest
import time
from utils.security import sanitize_url, sanitize_exception, sanitize_log_message
from utils.path_security import validate_cache_path, safe_mkdir
from core.ratelimit import TokenBucket, SlidingWindowLogger, RateLimiter


class TestSanitizeURL:
    """测试URL脱敏"""

    def test_remove_token(self):
        """测试移除token参数"""
        url = "https://mp.weixin.qq.com/s/abc?token=secret123&id=456"
        sanitized = sanitize_url(url)
        assert "token=***" in sanitized
        assert "secret123" not in sanitized
        assert "id=456" in sanitized or "id=***" in sanitized

    def test_remove_multiple_params(self):
        """测试移除多个敏感参数"""
        url = "https://example.com/?token=abc&session=xyz&id=123"
        sanitized = sanitize_url(url)
        assert "token=***" in sanitized
        assert "session=***" in sanitized

    def test_keep_safe_params(self):
        """测试保留安全参数"""
        url = "https://example.com/?page=1&limit=10"
        sanitized = sanitize_url(url)
        assert "page=1" in sanitized
        assert "limit=10" in sanitized

    def test_invalid_url(self):
        """测试无效URL"""
        assert sanitize_url("") == "***"
        assert sanitize_url(None) == "***"

    def test_remove_api_key(self):
        """测试移除API密钥"""
        url = "https://api.example.com/?api_key=secret123&data=test"
        sanitized = sanitize_url(url)
        assert "api_key=***" in sanitized
        assert "secret123" not in sanitized


class TestSanitizeException:
    """测试异常脱敏"""

    def test_remove_file_path(self):
        """测试移除文件路径"""
        error = FileNotFoundError("/home/user/secret/key.txt")
        sanitized = sanitize_exception(error)
        assert "/home/user/" not in sanitized
        assert "key.txt" in sanitized

    def test_remove_env_vars(self):
        """测试移除环境变量"""
        error = ValueError("API_KEY_ABC123XYZ not found")
        sanitized = sanitize_exception(error)
        assert "ABC123XYZ" not in sanitized
        assert "[REDACTED]" in sanitized

    def test_limit_length(self):
        """测试长度限制"""
        long_msg = "x" * 300
        error = Exception(long_msg)
        sanitized = sanitize_exception(error)
        assert len(sanitized) < 250  # type + ":" + 200 + "..."

    def test_preserve_error_type(self):
        """测试保留错误类型"""
        error = ValueError("test error")
        sanitized = sanitize_exception(error)
        assert "ValueError" in sanitized


class TestSanitizeLogMessage:
    """测试日志消息脱敏"""

    def test_remove_email(self):
        """测试移除邮箱"""
        msg = "Contact user@example.com for support"
        sanitized = sanitize_log_message(msg)
        assert "user@example.com" not in sanitized
        assert "***@***.***" in sanitized

    def test_remove_phone(self):
        """测试移除手机号"""
        msg = "Call 13812345678 for help"
        sanitized = sanitize_log_message(msg)
        assert "13812345678" not in sanitized
        assert "***********" in sanitized

    def test_remove_id_card(self):
        """测试移除身份证"""
        msg = "ID: 110101199001011234"
        sanitized = sanitize_log_message(msg)
        assert "110101199001011234" not in sanitized
        assert "******************" in sanitized


class TestValidateCachePath:
    """测试路径验证"""

    def test_valid_path(self):
        """测试合法路径"""
        path = "./cache/articles.db"
        validated = validate_cache_path(path)
        assert validated.is_absolute()
        assert "articles.db" in str(validated)

    def test_path_traversal(self):
        """测试路径遍历攻击"""
        with pytest.raises(ValueError, match="非法缓存文件扩展名"):
            validate_cache_path("../../../etc/passwd")

    def test_absolute_path_outside(self):
        """测试外部绝对路径"""
        with pytest.raises(ValueError, match="非法缓存文件扩展名"):
            validate_cache_path("/etc/passwd")

    def test_invalid_extension(self):
        """测试非法扩展名"""
        with pytest.raises(ValueError, match="非法缓存文件扩展名"):
            validate_cache_path("./cache/config.ini")

    def test_subdirectory(self):
        """测试子目录"""
        path = "./cache/subdir/articles.db"
        validated = validate_cache_path(path)
        assert "subdir" in str(validated)


class TestTokenBucket:
    """测试令牌桶"""

    def test_consume_token(self):
        """测试消耗令牌"""
        bucket = TokenBucket(capacity=10, rate=1.0)
        assert bucket.consume(1) == True
        assert bucket.tokens < 10

    def test_refill_tokens(self):
        """测试令牌补充"""
        bucket = TokenBucket(capacity=10, rate=10.0)
        bucket.consume(10)
        assert bucket.tokens == 0

        time.sleep(0.2)  # 等待补充约2个令牌
        assert bucket.available_tokens >= 1.5

    def test_over_capacity(self):
        """测试不超过容量"""
        bucket = TokenBucket(capacity=10, rate=1.0)
        bucket.consume(5)
        time.sleep(10)  # 补充到容量
        assert bucket.available_tokens <= 10

    def test_wait_for_token(self):
        """测试等待令牌"""
        bucket = TokenBucket(capacity=5, rate=10.0)
        bucket.consume(5)  # 耗尽令牌
        assert bucket.wait_for_token(1, timeout=1) == True
        assert bucket.tokens < 5


class TestSlidingWindowLogger:
    """测试滑动窗口"""

    def test_allow_requests(self):
        """测试允许请求"""
        window = SlidingWindowLogger(window_size=10, max_requests=5)

        for _ in range(5):
            assert window.is_allowed() == True

        # 第6个请求应该被拒绝
        assert window.is_allowed() == False

    def test_window_sliding(self):
        """测试窗口滑动"""
        window = SlidingWindowLogger(window_size=1, max_requests=2)

        assert window.is_allowed() == True
        assert window.is_allowed() == True
        assert window.is_allowed() == False

        # 等待窗口滑动
        time.sleep(1.1)
        assert window.is_allowed() == True


class TestRateLimiter:
    """测试综合限流器"""

    def test_rate_limiting(self):
        """测试速率限制"""
        limiter = RateLimiter(
            bucket_capacity=10,
            bucket_rate=1.0,
            window_size=10,
            window_max_requests=5,
            max_concurrent=2
        )

        # 应该允许前5个请求
        for _ in range(5):
            assert limiter.acquire() == True
            limiter.release()

        # 第6个请求应该被拒绝（滑动窗口限制）
        assert limiter.acquire() == False

    def test_concurrent_limit(self):
        """测试并发限制"""
        limiter = RateLimiter(max_concurrent=2)

        assert limiter.acquire() == True
        assert limiter.acquire() == True
        assert limiter.acquire() == False  # 超过并发限制

        limiter.release()
        assert limiter.acquire() == True  # 释放后可以获取

    def test_get_stats(self):
        """测试获取统计信息"""
        limiter = RateLimiter(
            bucket_capacity=100,
            bucket_rate=10.0,
            max_concurrent=3
        )

        stats = limiter.get_stats()
        assert 'available_tokens' in stats
        assert 'window_requests' in stats
        assert 'current_concurrent' in stats
        assert stats['max_concurrent'] == 3
