"""
速率限制模块
化学视角：速率限制是酶反应动力学，控制反应速率防止系统过载

功能：
- 令牌桶算法：平滑请求速率
- 滑动窗口：精确限制请求数
- 并发控制：限制同时进行的请求数
"""

import time
import logging
from threading import Lock
from typing import Optional
from collections import deque

logger = logging.getLogger(__name__)


class TokenBucket:
    """令牌桶限流器

    机制：
    - 桶容量：最大令牌数
    - 令牌速率：每秒生成的令牌数
    - 每个请求消耗1个令牌
    - 令牌不足时阻塞等待
    """

    def __init__(self, capacity: int, rate: float):
        """初始化令牌桶

        Args:
            capacity: 桶容量（最大令牌数）
            rate: 令牌生成速率（令牌/秒）
        """
        self.capacity = capacity
        self.rate = rate
        self.tokens = float(capacity)
        self.last_time = time.time()
        self._lock = Lock()

    def consume(self, tokens: int = 1) -> bool:
        """消耗令牌

        Args:
            tokens: 需要消耗的令牌数

        Returns:
            是否成功消耗
        """
        with self._lock:
            # 计算新增令牌
            now = time.time()
            elapsed = now - self.last_time
            new_tokens = elapsed * self.rate

            # 更新令牌数（不超过容量）
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_time = now

            # 检查令牌是否足够
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            return False

    def wait_for_token(self, tokens: int = 1, timeout: float = 60) -> bool:
        """等待令牌可用

        Args:
            tokens: 需要的令牌数
            timeout: 最大等待时间（秒）

        Returns:
            是否成功获取令牌
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.consume(tokens):
                return True

            # 计算等待时间
            wait_time = (tokens - self.tokens) / self.rate if self.rate > 0 else 1.0
            time.sleep(min(wait_time, 1.0))  # 最多等待1秒

        return False

    @property
    def available_tokens(self) -> float:
        """获取可用令牌数"""
        with self._lock:
            now = time.time()
            elapsed = now - self.last_time
            new_tokens = elapsed * self.rate
            return min(self.capacity, self.tokens + new_tokens)


class SlidingWindowLogger:
    """滑动窗口日志记录器

    用于更精确的速率限制
    """

    def __init__(self, window_size: int, max_requests: int):
        """初始化滑动窗口

        Args:
            window_size: 窗口大小（秒）
            max_requests: 窗口内最大请求数
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests = deque()
        self._lock = Lock()

    def is_allowed(self) -> bool:
        """检查是否允许请求

        Returns:
            是否允许
        """
        with self._lock:
            now = time.time()

            # 移除窗口外的请求
            while self.requests and now - self.requests[0] > self.window_size:
                self.requests.popleft()

            # 检查是否超过限制
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True

            return False

    def reset(self) -> None:
        """重置计数器"""
        with self._lock:
            self.requests.clear()


class RateLimiter:
    """综合限流器

    结合令牌桶和滑动窗口
    """

    def __init__(
        self,
        # 令牌桶配置
        bucket_capacity: int = 100,
        bucket_rate: float = 10.0,  # 每秒10个令牌

        # 滑动窗口配置
        window_size: int = 60,  # 60秒窗口
        window_max_requests: int = 100,  # 每分钟最多100个请求

        # 并发限制
        max_concurrent: int = 3
    ):
        """初始化限流器

        Args:
            bucket_capacity: 令牌桶容量
            bucket_rate: 令牌生成速率
            window_size: 滑动窗口大小
            window_max_requests: 窗口内最大请求数
            max_concurrent: 最大并发数
        """
        self.token_bucket = TokenBucket(bucket_capacity, bucket_rate)
        self.sliding_window = SlidingWindowLogger(window_size, window_max_requests)
        self.max_concurrent = max_concurrent
        self.current_concurrent = 0
        self._concurrent_lock = Lock()

    def acquire(self, tokens: int = 1, timeout: float = 60) -> bool:
        """获取访问权限

        Args:
            tokens: 需要的令牌数
            timeout: 最大等待时间

        Returns:
            是否成功获取
        """
        # 检查滑动窗口
        if not self.sliding_window.is_allowed():
            logger.warning(f"速率限制：超过滑动窗口限制")
            return False

        # 检查令牌桶
        if not self.token_bucket.wait_for_token(tokens, timeout):
            logger.warning(f"速率限制：令牌不足")
            return False

        # 检查并发限制
        with self._concurrent_lock:
            if self.current_concurrent >= self.max_concurrent:
                logger.warning(f"速率限制：超过并发限制")
                return False
            self.current_concurrent += 1

        return True

    def release(self) -> None:
        """释放并发槽位"""
        with self._concurrent_lock:
            if self.current_concurrent > 0:
                self.current_concurrent -= 1

    def get_stats(self) -> dict:
        """获取限流统计

        Returns:
            统计信息
        """
        return {
            'available_tokens': self.token_bucket.available_tokens,
            'window_requests': len(self.sliding_window.requests),
            'current_concurrent': self.current_concurrent,
            'max_concurrent': self.max_concurrent
        }


# 全局限流器实例
_global_limiter: Optional[RateLimiter] = None


def get_global_limiter() -> RateLimiter:
    """获取全局限流器（单例）

    Returns:
        RateLimiter实例
    """
    global _global_limiter
    if _global_limiter is None:
        # 默认配置：
        # - 每秒10个请求（令牌桶）
        # - 每分钟100个请求（滑动窗口）
        # - 最多3个并发
        _global_limiter = RateLimiter(
            bucket_capacity=100,
            bucket_rate=10.0,
            window_size=60,
            window_max_requests=100,
            max_concurrent=3
        )
    return _global_limiter


class RateLimitedError(Exception):
    """速率限制错误"""
    pass
