"""
降级控制器
化学视角：降级是免疫反应，主策略失败时启动备用防御机制

设计原则：
- 多策略分层：直接访问 > API降级
- 健康检查：实时监控策略可用性
- 自动恢复：策略失败后自动恢复
- 熔断机制：连续失败后暂时熔断
"""

import time
import logging
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, timedelta

from models.article import Article
from utils.http import HTTPClient, validate_url
from utils.security import sanitize_exception


logger = logging.getLogger(__name__)


class StrategyStatus(Enum):
    """策略状态"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class FetchStrategy(ABC):
    """获取策略抽象基类

    所有策略必须实现此接口
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """策略名称"""
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """优先级（数字越小优先级越高）"""
        pass

    @abstractmethod
    def fetch(self, url: str) -> Article:
        """获取文章

        Args:
            url: 文章URL

        Returns:
            Article对象

        Raises:
            Exception: 获取失败
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查策略是否可用

        Returns:
            是否可用
        """
        pass


class DirectFetchStrategy(FetchStrategy):
    """直接访问微信服务器策略

    优先级：1（最高）
    可靠性：85%（无反爬情况下）
    成本：0
    """

    def __init__(
        self,
        http_client: HTTPClient,
        parser: 'HTMLParser'  # 延迟导入避免循环
    ):
        """初始化直接访问策略

        Args:
            http_client: HTTP客户端
            parser: HTML解析器
        """
        self.http_client = http_client
        self.parser = parser
        self._failure_count = 0
        self._last_failure_time = None

    @property
    def name(self) -> str:
        return "direct"

    @property
    def priority(self) -> int:
        return 1

    def fetch(self, url: str) -> Article:
        """直接访问微信服务器"""
        try:
            # 发送HTTP请求
            response = self.http_client.get(url)

            # 检查反爬
            if response.detect_anti_crawl():
                raise CaptchaDetectedError("检测到反爬机制")

            if not response.is_success:
                raise FetchError(f"HTTP {response.status_code}")

            # 解析HTML
            parsed = self.parser.parse(response.content)

            # 构建Article对象
            article = Article(
                url=url,
                url_hash="",  # 会自动生成
                title=parsed.get('title', ''),
                author=parsed.get('author', ''),
                account_name=parsed.get('account_name', ''),
                content_html=parsed.get('content_html', ''),
                images=parsed.get('images', []),
                cover_image=parsed.get('cover_image'),
                source='direct'
            )

            # 提取纯文本
            article.content_text = self.parser.extract_text(response.content)

            # 提取Markdown
            try:
                from utils.html import html_to_markdown
                article.content_markdown = html_to_markdown(article.content_html)
            except Exception:
                article.content_markdown = article.content_text

            # 重置失败计数
            self._failure_count = 0

            return article

        except Exception as e:
            self._failure_count += 1
            self._last_failure_time = datetime.now()
            raise FetchError(f"直接访问失败: {e}") from e

    def is_available(self) -> bool:
        """检查策略是否可用"""
        # 连续失败超过5次，暂时不可用
        if self._failure_count >= 5:
            # 10分钟后恢复
            if self._last_failure_time:
                elapsed = datetime.now() - self._last_failure_time
                if elapsed < timedelta(minutes=10):
                    return False
                else:
                    # 重置失败计数
                    self._failure_count = 0
        return True


class APIFetchStrategy(FetchStrategy):
    """API降级策略

    优先级：2（降级）
    可靠性：65%（依赖第三方服务）
    成本：低（可选API Key）
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_endpoint: str = "https://down.mptext.top"
    ):
        """初始化API策略

        Args:
            api_key: API密钥（可选）
            api_endpoint: API端点
        """
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self._failure_count = 0
        self._last_failure_time = None

    @property
    def name(self) -> str:
        return "api"

    @property
    def priority(self) -> int:
        return 2

    def fetch(self, url: str) -> Article:
        """通过API获取文章"""
        try:
            # 构建请求
            import requests

            params = {'url': url}
            if self.api_key:
                params['api_key'] = self.api_key

            response = requests.get(
                self.api_endpoint,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                # 构建Article对象
                article = Article(
                    url=url,
                    url_hash="",  # 会自动生成
                    title=data.get('title', ''),
                    author=data.get('author', ''),
                    account_name=data.get('account_name', ''),
                    content_html=data.get('content_html', ''),
                    content_markdown=data.get('content_markdown', ''),
                    content_text=data.get('content_text', ''),
                    images=data.get('images', []),
                    cover_image=data.get('cover_image'),
                    source='api'
                )

                # 重置失败计数
                self._failure_count = 0

                return article
            else:
                raise FetchError(f"API返回错误: {response.status_code}")

        except Exception as e:
            self._failure_count += 1
            self._last_failure_time = datetime.now()
            raise FetchError(f"API获取失败: {e}") from e

    def is_available(self) -> bool:
        """检查策略是否可用"""
        # 如果没有API Key，不使用API
        if not self.api_key:
            return False

        # 连续失败超过3次，暂时不可用
        if self._failure_count >= 3:
            if self._last_failure_time:
                elapsed = datetime.now() - self._last_failure_time
                if elapsed < timedelta(minutes=5):
                    return False
                else:
                    self._failure_count = 0
        return True


class FallbackController:
    """降级控制器

    功能：
    - 管理多个获取策略
    - 按优先级尝试策略
    - 健康检查
    - 自动恢复
    """

    def __init__(self, strategies: List[FetchStrategy]):
        """初始化降级控制器

        Args:
            strategies: 策略列表（会按优先级排序）
        """
        # 按优先级排序
        self.strategies = sorted(strategies, key=lambda s: s.priority)
        self.health_status: Dict[str, StrategyStatus] = {
            s.name: StrategyStatus.HEALTHY for s in self.strategies
        }

    def fetch(self, url: str) -> Article:
        """获取文章（自动降级）

        Args:
            url: 文章URL

        Returns:
            Article对象

        Raises:
            AllStrategiesFailedError: 所有策略失败
        """
        if not validate_url(url):
            raise URLValidationError(f"URL格式错误: {url}")

        failures = {}

        for strategy in self.strategies:
            # 检查健康状态
            if not strategy.is_available():
                logger.debug(f"策略 {strategy.name} 不可用，跳过")
                continue

            try:
                logger.info(f"尝试策略: {strategy.name}")

                article = strategy.fetch(url)

                # 标记为健康
                self.health_status[strategy.name] = StrategyStatus.HEALTHY

                logger.info(f"策略 {strategy.name} 成功")

                return article

            except CaptchaDetectedError as e:
                # 验证码错误，策略健康但暂时不可用
                logger.warning(f"策略 {strategy.name} 检测到验证码")
                failures[strategy.name] = str(e)
                continue

            except Exception as e:
                # 其他错误，标记为不健康
                logger.error(f"策略 {strategy.name} 失败: {sanitize_exception(e)}")
                failures[strategy.name] = str(e)
                self.health_status[strategy.name] = StrategyStatus.UNHEALTHY
                continue

        # 所有策略失败
        raise AllStrategiesFailedError(failures)

    def get_health_status(self) -> Dict[str, str]:
        """获取所有策略的健康状态

        Returns:
            健康状态字典
        """
        return {
            name: status.value
            for name, status in self.health_status.items()
        }


class FetchError(Exception):
    """获取错误基类"""
    pass


class URLValidationError(FetchError):
    """URL验证错误"""
    pass


class CaptchaDetectedError(FetchError):
    """验证码检测错误"""
    pass


class AllStrategiesFailedError(FetchError):
    """所有策略失败错误"""

    def __init__(self, failures: Dict[str, str]):
        self.failures = failures
        super().__init__(f"所有策略失败: {failures}")
