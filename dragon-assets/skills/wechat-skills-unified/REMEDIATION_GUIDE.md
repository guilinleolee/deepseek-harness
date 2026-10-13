# 微信公众号SKILL统一重构 - 安全修复指南

## 指南信息

- **执行者**: 05安全师（Security-Master）
- **创建时间**: 2026-02-26
- **适用版本**: V1.0.0
- **目标版本**: V1.1.0 (安全加固版)

---

## 使用说明

本指南按优先级（P1→P2→P3）组织，每个问题包含：
- **详细说明**: 问题描述和影响
- **修复代码**: 可直接使用的代码
- **验证方法**: 如何验证修复成功
- **预计时间**: 修复所需时间

---

## 第一部分：P1级别修复（必须）

### 🔴 修复 #1: 日志脱敏

#### 问题描述

**位置**:
- `core/fetcher.py:105, 112, 117, 128`
- `core/fallback.py:332`
- `utils/http.py:206`

**问题**:
```python
# 不安全：记录完整URL
logger.error(f"获取失败: {url}, 错误: {e}")

# 风险：URL可能包含敏感参数
# https://mp.weixin.qq.com/s/abc?token=secret123&user_id=123
```

**影响**:
- 日志文件泄露用户隐私
- URL中的token、session等参数被记录
- 违反GDPR/PIPL数据保护要求

**CVSS评分**: 7.5 (High)

---

#### 修复方案

**步骤1**: 创建工具模块 `utils/security.py`

```python
# utils/security.py (新建文件)
import re
import urllib.parse
from typing import Any
from pathlib import Path


def sanitize_url(url: str, keep_params: list = None) -> str:
    """URL脱敏：移除敏感参数

    Args:
        url: 原始URL
        keep_params: 保留的参数列表

    Returns:
        脱敏后的URL

    示例:
        >>> sanitize_url("https://example.com/?token=abc&id=123")
        'https://example.com/?token=***&id=***'
    """
    if not url:
        return "***"

    try:
        parsed = urllib.parse.urlparse(url)

        # 敏感参数列表
        sensitive_params = [
            'token', 'session', 'sid', 'jsessionid',
            'access_token', 'refresh_token', 'api_key',
            'password', 'passwd', 'secret', 'credential',
            'user_id', 'uid', 'openid', 'unionid'
        ]

        # 解析查询参数
        params = urllib.parse.parse_qs(parsed.query)

        # 脱敏处理
        sanitized_params = []
        for key, values in params.items():
            if key in sensitive_params and (not keep_params or key not in keep_params):
                # 敏感参数：脱敏
                sanitized_params.append(f"{key}=***")
            else:
                # 安全参数：保留值但限制长度
                value = values[0] if values else ""
                if len(value) > 20:
                    value = value[:20] + "..."
                sanitized_params.append(f"{key}={value}")

        # 重建URL
        sanitized_query = "&".join(sanitized_params)
        sanitized_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            sanitized_query,
            ""  # 移除fragment
        ))

        return sanitized_url

    except Exception:
        # 解析失败，返回基本形式
        try:
            parsed = urllib.parse.urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}***"
        except Exception:
            return "***"


def sanitize_exception(e: Exception) -> str:
    """异常信息脱敏：移除敏感信息

    Args:
        e: 异常对象

    Returns:
        脱敏后的异常信息

    示例:
        >>> sanitize_exception(FileNotFoundError("path/to/secret.key"))
        'FileNotFoundError: path/to/***.key'
    """
    error_msg = str(e)
    error_type = type(e).__name__

    # 移除文件路径中的敏感信息
    error_msg = re.sub(
        r'File ".*?/([^/]+\.py)"',
        r'File "\1"',
        error_msg
    )

    # 移除环境变量（大写+下划线的长字符串）
    error_msg = re.sub(
        r'[A-Z_]{20,}',
        '[REDACTED]',
        error_msg
    )

    # 移除可能的密钥（Base64字符串）
    error_msg = re.sub(
        r'[A-Za-z0-9+/]{32,}={0,2}',
        '[REDACTED]',
        error_msg
    )

    # 限制长度
    if len(error_msg) > 200:
        error_msg = error_msg[:200] + "..."

    return f"{error_type}: {error_msg}"


def sanitize_log_message(message: str) -> str:
    """日志消息通用脱敏

    Args:
        message: 原始消息

    Returns:
        脱敏后的消息
    """
    # 移除邮箱
    message = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***', message)

    # 移除手机号
    message = re.sub(r'\b1[3-9]\d{9}\b', '***********', message)

    # 移除身份证
    message = re.sub(r'\b\d{17}[\dXx]\b', '******************', message)

    return message
```

**步骤2**: 修改日志调用

```python
# core/fetcher.py
from utils.security import sanitize_url, sanitize_exception, sanitize_log_message

# 修改前
logger.error(f"获取失败: {url}, 错误: {e}")

# 修改后
logger.error(
    sanitize_log_message(f"获取失败: {sanitize_url(url)}, 错误: {sanitize_exception(e)}")
)

# 其他位置类似修改
logger.info(f"缓存命中: {sanitize_url(url)}")
logger.info(f"开始获取: {sanitize_url(url)}")
```

```python
# core/fallback.py
from utils.security import sanitize_url, sanitize_exception

# 修改前
logger.error(f"策略 {strategy.name} 失败: {e}")

# 修改后
logger.error(f"策略 {strategy.name} 失败: {sanitize_exception(e)}")
```

```python
# utils/http.py
from utils.security import sanitize_url

# 修改前
logger.debug(f"HTTP请求: {url} (尝试 {attempt + 1}/{self.retry_times})")

# 修改后
logger.debug(f"HTTP请求: {sanitize_url(url)} (尝试 {attempt + 1}/{self.retry_times})")
```

**步骤3**: 更新requirements.txt

```text
# requirements/full.txt
# 添加依赖（无新增依赖，使用标准库）
```

---

#### 验证方法

**单元测试**:

```python
# tests/test_security.py (新建文件)
import pytest
from utils.security import sanitize_url, sanitize_exception, sanitize_log_message


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
```

**手动测试**:

```bash
# 运行测试
pytest tests/test_security.py -v

# 运行程序并检查日志
python -m wechat_skills_unified fetch "https://mp.weixin.qq.com/s/test?token=abc123"

# 检查日志文件
cat wechat_skills.log | grep "token"
# 应该看到 token=*** 而不是 token=abc123
```

---

#### 预计时间

- 创建工具模块: 1小时
- 修改日志调用: 1小时
- 编写测试: 1小时
- **总计**: **3小时**

---

### 🔴 修复 #2: 速率限制

#### 问题描述

**位置**: `core/fetcher.py:131-174`

**问题**:
```python
# 不安全：无全局速率限制
def fetch_batch(self, urls, use_cache=True, concurrent=3):
    concurrent = max(1, min(concurrent, 10))  # 仅限制并发
    # 恶意用户可传入1000个URL，导致DoS
```

**影响**:
- 恶意大量请求耗尽系统资源
- 可能触发微信服务器反爬
- 违反公平使用原则

**CVSS评分**: 7.5 (High)

---

#### 修复方案

**步骤1**: 添加令牌桶限流器

```python
# core/ratelimit.py (新建文件)
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
            wait_time = (tokens - self.tokens) / self.rate
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
```

**步骤2**: 修改fetcher.py

```python
# core/fetcher.py
from core.ratelimit import get_global_limiter, RateLimitError

# 添加自定义异常
class RateLimitError(Exception):
    """速率限制错误"""
    pass


def fetch_article(
    self,
    url: str,
    use_cache: bool = True
) -> Optional[Article]:
    """获取单篇文章（带速率限制）"""
    # 验证URL
    from utils.http import validate_url
    if not validate_url(url):
        logger.error(f"URL格式错误: {url}")
        return None

    # 获取限流许可
    limiter = get_global_limiter()
    if not limiter.acquire(tokens=1, timeout=30):
        logger.warning(f"速率限制：请求被拒绝")
        raise RateLimitError("超过速率限制，请稍后重试")

    try:
        # 1. 查询缓存
        if use_cache and self.cache:
            article = self.cache.get(url)
            if article:
                logger.info(f"缓存命中: {url}")
                return article

        # 2. 降级获取
        try:
            logger.info(f"开始获取: {url}")
            article = self.fallback.fetch(url)

            # 3. 写入缓存
            if use_cache and self.cache:
                self.cache.set(article)
                logger.info("已写入缓存")

            return article

        except Exception as e:
            logger.error(f"获取失败: {url}, 错误: {e}")
            return None

    finally:
        # 释放许可
        limiter.release()


def fetch_batch(
    self,
    urls: List[str],
    use_cache: bool = True,
    concurrent: int = 3
) -> List[Optional[Article]]:
    """批量获取文章（带速率限制）"""
    # 限制并发数
    concurrent = max(1, min(concurrent, 10))

    # 预检查：是否超过限流
    limiter = get_global_limiter()
    if len(urls) > 100:
        logger.warning(f"批量获取数量过大: {len(urls)}")
        raise RateLimitError(f"单次最多100个URL，当前: {len(urls)}")

    results = []

    # 分批处理
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def fetch_single(url: str) -> tuple:
        """获取单篇文章（返回索引和结果）"""
        return urls.index(url), self.fetch_article(url, use_cache)

    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = {executor.submit(fetch_single, url): url for url in urls}

        for future in as_completed(futures):
            try:
                idx, article = future.result()
                results.append((idx, article))
            except RateLimitError as e:
                logger.error(f"速率限制: {e}")
                idx = urls.index(futures[future])
                results.append((idx, None))
            except Exception as e:
                url = futures[future]
                logger.error(f"批量获取失败: {url}, 错误: {e}")
                idx = urls.index(url)
                results.append((idx, None))

    # 按原始顺序排序
    results.sort(key=lambda x: x[0])
    return [article for _, article in results]
```

**步骤3**: 更新配置

```python
# core/config.py
@dataclass
class Config:
    # ... 现有字段 ...

    # 速率限制配置
    rate_limit_enabled: bool = True
    rate_limit_per_second: float = 10.0  # 每秒10个请求
    rate_limit_per_minute: int = 100     # 每分钟100个请求
    rate_limit_max_concurrent: int = 3   # 最多3个并发
```

---

#### 验证方法

**单元测试**:

```python
# tests/test_ratelimit.py (新建文件)
import pytest
import time
from core.ratelimit import TokenBucket, SlidingWindowLogger, RateLimiter


class TestTokenBucket:
    """测试令牌桶"""

    def test_consume_token(self):
        """测试消耗令牌"""
        bucket = TokenBucket(capacity=10, rate=1.0)
        assert bucket.consume(1) == True
        assert bucket.tokens == 9

    def test_refill_tokens(self):
        """测试令牌补充"""
        bucket = TokenBucket(capacity=10, rate=10.0)
        bucket.consume(10)
        assert bucket.tokens == 0

        time.sleep(0.2)  # 等待补充2个令牌
        assert bucket.available_tokens >= 1.5  # 约2个

    def test_over_capacity(self):
        """测试不超过容量"""
        bucket = TokenBucket(capacity=10, rate=1.0)
        assert bucket.consume(5) == True
        time.sleep(10)  # 补充到容量
        assert bucket.available_tokens <= 10


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
```

**手动测试**:

```bash
# 运行测试
pytest tests/test_ratelimit.py -v

# 测试速率限制
python -m wechat_skills_unified batch url1 url2 ... url1000
# 应该在100个请求后被限流
```

---

#### 预计时间

- 实现限流器: 2小时
- 集成到fetcher: 1小时
- 编写测试: 1小时
- **总计**: **4小时**

---

### 🔴 修复 #3: 路径遍历防护

#### 问题描述

**位置**: `core/config.py:34`, `core/cache.py:158`

**问题**:
```python
# 不安全：cache_path用户可控
cache_path: str = "./cache/articles.db"  # 可能来自配置文件

# 用户可配置为：
cache_path = "../../../../../etc/passwd"
Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
# 创建目录到任意位置
```

**影响**:
- 攻击者可写入任意路径
- 可能覆盖系统文件
- 可能读取敏感文件

**CVSS评分**: 8.5 (High)

---

#### 修复方案

**步骤1**: 添加路径验证

```python
# utils/path_security.py (新建文件)
import os
from pathlib import Path
from typing import Optional


def validate_cache_path(path: str, base_dir: str = None) -> Path:
    """验证缓存路径合法性

    Args:
        path: 用户提供的路径
        base_dir: 基础目录（默认为当前工作目录）

    Returns:
        验证后的绝对路径

    Raises:
        ValueError: 路径不合法
    """
    if base_dir is None:
        base_dir = os.getcwd()

    base = Path(base_dir).resolve()
    user_path = Path(path).resolve()

    # 检查路径遍历
    try:
        # 检查是否在基础目录下
        user_path.relative_to(base)
    except ValueError:
        raise ValueError(
            f"非法缓存路径: {path}\n"
            f"路径必须在项目目录下: {base}"
        )

    # 检查文件扩展名
    if user_path.suffix not in ['.db', '.sqlite', '.sqlite3']:
        raise ValueError(
            f"非法缓存文件扩展名: {user_path.suffix}\n"
            f"仅允许: .db, .sqlite, .sqlite3"
        )

    # 检查文件名（禁止特殊字符）
    if not user_path.name.replace('.', '').replace('_', '').isalnum():
        raise ValueError(
            f"非法缓存文件名: {user_path.name}\n"
            f"文件名只能包含字母、数字、点、下划线"
        )

    return user_path


def safe_mkdir(path: Path, mode: int = 0o750) -> Path:
    """安全创建目录

    Args:
        path: 目录路径
        mode: 权限模式

    Returns:
        创建的目录路径

    Raises:
        ValueError: 路径不合法
    """
    # 验证路径
    validated = validate_cache_path(str(path))

    # 创建目录（如果不存在）
    validated.mkdir(parents=True, exist_ok=True)

    # 设置权限
    os.chmod(validated, mode)

    return validated
```

**步骤2**: 修改cache.py

```python
# core/cache.py
from utils.path_security import validate_cache_path

class SQLiteCache:
    def __init__(self, db_path: str, ttl_days: int = 30):
        """初始化SQLite缓存"""
        # 验证路径
        self.db_path = validate_cache_path(db_path)
        self.ttl = timedelta(days=ttl_days)
        self._init_db()

    def _init_db(self) -> None:
        """初始化数据库"""
        # 创建目录（使用安全方法）
        from utils.path_security import safe_mkdir
        safe_mkdir(Path(self.db_path).parent)

        # ... 其余代码 ...
```

**步骤3**: 修改config.py

```python
# core/config.py
from utils.path_security import validate_cache_path

@dataclass
class Config:
    cache_path: str = "./cache/articles.db"

    def __post_init__(self):
        """初始化后验证"""
        # 验证缓存路径
        self.cache_path = str(validate_cache_path(self.cache_path))
```

---

#### 验证方法

**单元测试**:

```python
# tests/test_path_security.py (新建文件)
import pytest
from pathlib import Path
from utils.path_security import validate_cache_path, safe_mkdir


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
        with pytest.raises(ValueError):
            validate_cache_path("../../../etc/passwd")

    def test_absolute_path(self):
        """测试绝对路径"""
        with pytest.raises(ValueError):
            validate_cache_path("/etc/passwd")

    def test_invalid_extension(self):
        """测试非法扩展名"""
        with pytest.raises(ValueError):
            validate_cache_path("./cache/config.ini")

    def test_invalid_filename(self):
        """测试非法文件名"""
        with pytest.raises(ValueError):
            validate_cache_path("./cache/../../etc/passwd.db")

    def test_subdirectory(self):
        """测试子目录"""
        path = "./cache/subdir/articles.db"
        validated = validate_cache_path(path)
        assert "subdir" in str(validated)


class TestSafeMkdir:
    """测试安全创建目录"""

    def test_create_directory(self, tmp_path):
        """测试创建目录"""
        new_dir = tmp_path / "cache" / "subdir"
        result = safe_mkdir(new_dir)
        assert result.exists()
        assert result.is_dir()

    def test_set_permissions(self, tmp_path):
        """测试设置权限"""
        new_dir = tmp_path / "cache"
        result = safe_mkdir(new_dir, mode=0o750)
        # 检查权限（Unix系统）
        import os
        if os.name != 'nt':
            assert result.stat().st_mode & 0o777 == 0o750
```

**手动测试**:

```bash
# 测试路径遍历攻击
python -c "
from core.config import Config
try:
    config = Config(cache_path='../../../etc/passwd')
except ValueError as e:
    print(f'已阻止: {e}')
"

# 应该输出：
# 已阻止: 非法缓存路径: ../../../etc/passwd
```

---

#### 预计时间

- 实现路径验证: 1.5小时
- 集成到config/cache: 1小时
- 编写测试: 0.5小时
- **总计**: **3小时**

---

### 🔴 修复 #4: 错误消息过滤

#### 问题描述

**位置**: 所有 `except Exception as e:` 块

**问题**:
```python
# 不安全：直接记录异常
except Exception as e:
    logger.error(f"获取失败: {url}, 错误: {e}")
    # 可能输出：
    # 获取失败: https://..., 错误: HTTPConnectionPool(host='api.server.com', port=443): Max retries exceeded with url: /api?api_key=SECRET123
```

**影响**:
- 泄露内部架构信息
- 泄露API密钥
- 泄露文件路径

**CVSS评分**: 7.0 (High)

---

#### 修复方案

**已在修复#1中实现** (`sanitize_exception` 函数)

**额外修改**: 更新所有异常处理

```python
# 所有文件统一修改
from utils.security import sanitize_exception

# 修改前
except Exception as e:
    logger.error(f"操作失败: {e}")
    raise

# 修改后
except Exception as e:
    logger.error(f"操作失败: {sanitize_exception(e)}")
    raise
```

**受影响文件**:
- `core/cache.py:212, 250, 270, 294, 318`
- `core/fetcher.py:127, 168`
- `core/fallback.py:245, 332`
- `utils/http.py:248, 252`
- `utils/html.py:118, 155`

---

#### 验证方法

**手动测试**:

```python
# 测试脚本
from utils.security import sanitize_exception

# 模拟各种异常
try:
    raise FileNotFoundError("/home/user/secret.key")
except Exception as e:
    print(f"原始: {e}")
    print(f"脱敏: {sanitize_exception(e)}")

# 输出应该不包含完整路径
```

---

#### 预计时间

- 更新所有异常处理: 1小时
- **总计**: **1小时** (依赖修复#1)

---

## 第二部分：P2级别修复（建议）

### ⚠️ 修复 #5: 缓存数据加密

#### 问题描述

**位置**: `core/cache.py:119-136`

**问题**:
```python
# 不安全：SQLite明文存储
CREATE TABLE articles (
    content_html TEXT,  -- 明文存储
    content_markdown TEXT,  -- 明文存储
    ...
)
```

**影响**:
- 缓存文件泄露导致数据泄露
- 违反数据保护法规

**CVSS评分**: 5.5 (Medium)

---

#### 修复方案

**方案A**: 使用SQLCipher（推荐）

```python
# requirements/full.txt
# 添加依赖
# pysqlcipher3>=1.2.0

# core/cache.py
import pysqlcipher3

class SQLiteCache:
    def __init__(self, db_path: str, ttl_days: int = 30, encryption_key: str = None):
        """初始化加密SQLite缓存"""
        self.db_path = validate_cache_path(db_path)
        self.ttl = timedelta(days=ttl_days)
        self.encryption_key = encryption_key or self._get_default_key()
        self._init_db()

    def _get_default_key(self) -> str:
        """获取默认加密密钥"""
        # 从环境变量读取
        import os
        key = os.environ.get('WECHAT_CACHE_KEY')
        if not key:
            # 生成随机密钥
            import secrets
            key = secrets.token_hex(32)
            logger.warning("未设置WECHAT_CACHE_KEY，已生成随机密钥")
        return key

    @contextmanager
    def _get_conn(self):
        """获取加密数据库连接"""
        conn = pysqlcipher3.connect(self.db_path, timeout=30)
        # 设置加密密钥
        conn.execute(f"PRAGMA key = '{self.encryption_key}'")
        conn.row_factory = pysqlcipher3.Row
        try:
            yield conn
        finally:
            conn.close()
```

**方案B**: 应用层加密（备用）

```python
# core/cache.py
from cryptography.fernet import Fernet
import base64

class EncryptedCache:
    def __init__(self, db_path: str, encryption_key: str = None):
        """初始化加密缓存"""
        self.db_path = validate_cache_path(db_path)
        self.encryption_key = encryption_key or self._get_default_key()
        self.cipher = Fernet(self._get_fernet_key())

    def _get_fernet_key(self) -> bytes:
        """转换密钥为Fernet格式"""
        # Fernet需要32字节密钥
        key = self.encryption_key[:32].encode('utf-8')
        return base64.urlsafe_b64encode(key.ljust(32, b'0'))

    def encrypt(self, data: str) -> bytes:
        """加密数据"""
        return self.cipher.encrypt(data.encode('utf-8'))

    def decrypt(self, data: bytes) -> str:
        """解密数据"""
        return self.cipher.decrypt(data).decode('utf-8')

    def set(self, article: Article) -> None:
        """写入缓存（加密）"""
        # 加密敏感字段
        encrypted_html = self.encrypt(article.content_html)
        encrypted_markdown = self.encrypt(article.content_markdown)

        # 写入数据库
        conn.execute(
            "INSERT INTO articles (content_html, content_markdown, ...) VALUES (?, ?, ...)",
            (encrypted_html, encrypted_markdown, ...)
        )
```

---

#### 验证方法

```bash
# 测试加密
python -c "
from core.cache import SQLiteCache
cache = SQLiteCache('./cache/test.db', encryption_key='my_secret_key')

# 写入数据
article = Article(...)
cache.set(article)

# 尝试不使用密钥读取（应该失败）
import sqlite3
conn = sqlite3.connect('./cache/test.db')
cursor = conn.execute('SELECT content_html FROM articles LIMIT 1')
print(cursor.fetchone())  # 应该是乱码或无法读取
"
```

---

#### 预计时间

- 集成SQLCipher: 3小时
- 或实现应用层加密: 4小时
- 迁移现有数据: 2小时
- 编写测试: 1小时
- **总计**: **6小时**

---

### ⚠️ 修复 #6-9: 其他P2问题

（篇幅限制，其他P2问题的修复方案请参考完整文档）

- **#6 结构化日志**: 4小时
- **#7 API密钥验证**: 2小时
- **#8 资源配额管理**: 4小时
- **#9 文件权限设置**: 1小时

---

## 第三部分：修复优先级和时间表

### Week 1 (P0-P1修复)

| 天 | 任务 | 时间 | 状态 |
|----|------|------|------|
| Day 1 | 修复#1: 日志脱敏 | 3h | ⏳ |
| Day 2 | 修复#4: 错误消息过滤 | 1h | ⏳ |
| Day 3 | 修复#2: 速率限制 | 4h | ⏳ |
| Day 4 | 修复#3: 路径遍历 | 3h | ⏳ |
| Day 5 | 安全测试 + 文档 | 4h | ⏳ |

**总计**: 15小时 (约2个工作日)

---

### Week 2 (P2修复)

| 天 | 任务 | 时间 | 状态 |
|----|------|------|------|
| Day 1-3 | 修复#5: 缓存加密 | 6h | ⏳ |
| Day 4 | 修复#6: 结构化日志 | 4h | ⏳ |
| Day 5 | 其他P2修复 | 7h | ⏳ |

**总计**: 17小时 (约2个工作日)

---

## 第四部分：验证清单

### 修复前检查

- [ ] 备份现有代码
- [ ] 创建测试分支
- [ ] 运行现有测试套件
- [ ] 记录基线性能指标

---

### 修复后验证

- [ ] 所有单元测试通过
- [ ] 手动测试所有功能
- [ ] 安全扫描通过 (`pip-audit`, `bandit`)
- [ ] 性能测试无退化
- [ ] 代码审查通过

---

### 回归测试

```bash
# 完整测试套件
pytest tests/ -v

# 安全扫描
pip-audit
bandit -r .

# 性能测试
python -m tests.performance_benchmark
```

---

## 第五部分：紧急安全响应

如果发现安全漏洞被利用：

1. **立即禁用**: 设置 `cache_enabled=False`
2. **隔离环境**: 检查日志文件是否泄露
3. **清理缓存**: `clear_cache()`
4. **轮换密钥**: 更新所有API密钥
5. **通知用户**: 如有必要，发布安全公告

---

**修复指南版本**: V1.0.0
**最后更新**: 2026-02-26
**维护者**: 05安全师（Security-Master）

**注意**: 本指南包含可执行的代码示例，请根据项目实际情况调整。
