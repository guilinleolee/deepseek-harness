"""
HTTP工具模块
化学视角：HTTP工具是细胞膜，控制物质进出（请求/响应）

设计原则：
- 重试机制：自动重试可恢复错误
- UA池：模拟真实浏览器
- 超时控制：防止长时间阻塞
- 反爬检测：识别验证码和频率限制
"""

import time
import random
import logging
from typing import Optional, List, Dict, Callable
from enum import Enum

try:
    import requests
    from requests.exceptions import RequestException, Timeout, ConnectionError
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    RequestException = Exception

from utils.security import sanitize_url, sanitize_exception


logger = logging.getLogger(__name__)


class AntiCrawlError(Enum):
    """反爬错误类型"""
    CAPTCHA = "验证码"
    RATE_LIMIT = "频率限制"
    BLOCKED = "IP被封"
    UNKNOWN = "未知"


class HTTPResponse:
    """HTTP响应封装"""

    def __init__(
        self,
        status_code: int,
        content: str,
        headers: Dict[str, str],
        url: str
    ):
        self.status_code = status_code
        self.content = content
        self.headers = headers
        self.url = url

    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.status_code == 200

    @property
    def is_captcha(self) -> bool:
        """是否验证码"""
        # 检查特征
        captcha_keywords = ['验证码', 'captcha', 'verify']
        content_lower = self.content.lower()

        for keyword in captcha_keywords:
            if keyword in content_lower:
                return True

        return False

    def detect_anti_crawl(self) -> Optional[AntiCrawlError]:
        """检测反爬机制

        Returns:
            AntiCrawlError或None
        """
        if self.is_captcha:
            return AntiCrawlError.CAPTCHA

        if self.status_code == 429:
            return AntiCrawlError.RATE_LIMIT

        if self.status_code == 403:
            return AntiCrawlError.BLOCKED

        return None


class HTTPClient:
    """HTTP客户端

    功能：
    - 自动重试
    - UA池
    - 超时控制
    - 反爬检测
    - Cookie支持
    """

    # 验证码检测关键词
    CAPTCHA_KEYWORDS = [
        '验证码', 'captcha', '人机验证',
        'verify', '请在微信中', '请访问'
    ]

    def __init__(
        self,
        user_agents: List[str],
        timeout: int = 30,
        retry_times: int = 3,
        retry_delay: float = 2.0,
        request_interval: float = 3.0,
        cookies: Optional[Dict[str, str]] = None
    ):
        """初始化HTTP客户端

        Args:
            user_agents: User-Agent池
            timeout: 请求超时（秒）
            retry_times: 重试次数
            retry_delay: 重试延迟（秒）
            request_interval: 请求间隔（秒）
            cookies: Cookie字典
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests库未安装，请运行: pip install requests")

        self.user_agents = user_agents
        self.timeout = timeout
        self.retry_times = retry_times
        self.retry_delay = retry_delay
        self.request_interval = request_interval
        self.cookies = cookies or {}

        self._last_request_time = 0

    def _get_user_agent(self) -> str:
        """随机获取User-Agent"""
        return random.choice(self.user_agents)

    def _wait_interval(self) -> None:
        """等待请求间隔"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_interval:
            wait_time = self.request_interval - elapsed
            time.sleep(wait_time)

    def _should_retry(self, error: Exception, attempt: int) -> bool:
        """判断是否应该重试

        Args:
            error: 异常对象
            attempt: 当前尝试次数

        Returns:
            是否重试
        """
        if attempt >= self.retry_times:
            return False

        # 可重试的错误
        if isinstance(error, Timeout):
            return True
        if isinstance(error, ConnectionError):
            return True

        return False

    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None
    ) -> HTTPResponse:
        """GET请求（带重试）

        Args:
            url: 请求URL
            headers: 额外请求头

        Returns:
            HTTPResponse对象

        Raises:
            RequestException: 所有重试失败后抛出
        """
        # 等待间隔
        self._wait_interval()

        # 默认请求头
        default_headers = {
            'User-Agent': self._get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

        # 合并请求头
        if headers:
            default_headers.update(headers)

        # 重试循环
        last_error = None
        for attempt in range(self.retry_times):
            try:
                logger.debug(f"HTTP请求: {sanitize_url(url)} (尝试 {attempt + 1}/{self.retry_times})")

                response = requests.get(
                    url,
                    headers=default_headers,
                    cookies=self.cookies,
                    timeout=self.timeout,
                    verify=True  # 验证SSL
                )

                # 更新最后请求时间
                self._last_request_time = time.time()

                # 检查反爬
                http_response = HTTPResponse(
                    status_code=response.status_code,
                    content=response.text,
                    headers=dict(response.headers),
                    url=response.url
                )

                anti_crawl = http_response.detect_anti_crawl()
                if anti_crawl:
                    logger.warning(f"检测到反爬: {anti_crawl.value}")
                    # 反爬不重试，直接返回
                    return http_response

                # 检查状态码
                if response.status_code == 200:
                    return http_response

                # 非200状态码，可能需要重试
                if response.status_code in [429, 503, 504]:
                    # 可重试的状态码
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"状态码 {response.status_code}, 等待 {wait_time}秒后重试")
                    time.sleep(wait_time)
                    continue
                else:
                    # 不可重试的状态码
                    return http_response

            except Exception as e:
                last_error = e
                if self._should_retry(e, attempt):
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"请求失败: {sanitize_exception(e)}, 等待 {wait_time}秒后重试")
                    time.sleep(wait_time)
                    continue
                else:
                    break

        # 所有重试失败
        if last_error:
            raise RequestException(f"请求失败: {last_error}") from last_error

        raise RequestException("请求失败：未知错误")


def validate_url(url: str) -> bool:
    """验证微信公众号URL格式

    Args:
        url: 待验证URL

    Returns:
        是否合法
    """
    # 基本检查
    if not url or not isinstance(url, str):
        return False

    # 域名检查
    if not url.startswith("https://mp.weixin.qq.com/"):
        return False

    # 路径格式检查
    # /s/<xxxxx> 或 /s?__biz=...
    if "/s/" in url:
        return True
    if "/s?" in url:
        return True

    return False


def extract_url_hash(url: str) -> str:
    """提取URL中的哈希部分

    Args:
        url: 微信文章URL

    Returns:
        URL哈希部分
    """
    import hashlib
    return hashlib.sha256(url.encode('utf-8')).hexdigest()
