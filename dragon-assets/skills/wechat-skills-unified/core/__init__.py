"""
微信公众号SKILL - 核心模块

这是系统的主入口，提供统一的文章获取API。

使用示例:
    >>> from wechat_skills_unified import fetch_article, fetch_batch, clear_cache
    >>>
    >>> # 获取单篇文章
    >>> article = fetch_article("https://mp.weixin.qq.com/s/xxxxx")
    >>> print(article.title)
    >>>
    >>> # 批量获取
    >>> urls = ["url1", "url2", "url3"]
    >>> articles = fetch_batch(urls)
    >>>
    >>> # 清理缓存
    >>> clear_cache()
"""

# 版本信息
__version__ = "1.0.0"
__author__ = "03构建师"

# 延迟导入以避免循环依赖
def __getattr__(name: str):
    if name == 'fetch_article':
        from .fetcher import fetch_article
        return fetch_article
    elif name == 'fetch_batch':
        from .fetcher import fetch_batch
        return fetch_batch
    elif name == 'clear_cache':
        from .fetcher import clear_cache
        return clear_cache
    elif name == 'UnifiedFetcher':
        from .fetcher import UnifiedFetcher
        return UnifiedFetcher
    elif name == 'Config':
        from .config import Config
        return Config
    elif name == 'get_default_config':
        from .config import get_default_config
        return get_default_config
    elif name == 'get_default_fetcher':
        from .fetcher import get_default_fetcher
        return get_default_fetcher
    elif name == 'Article':
        from models.article import Article
        return Article
    elif name == 'ArticleList':
        from models.article import ArticleList
        return ArticleList
    elif name == 'OptionalArticle':
        from models.article import OptionalArticle
        return OptionalArticle
    elif name == 'FetchError':
        from .fallback import FetchError
        return FetchError
    elif name == 'URLValidationError':
        from .fallback import URLValidationError
        return URLValidationError
    elif name == 'CaptchaDetectedError':
        from .fallback import CaptchaDetectedError
        return CaptchaDetectedError
    elif name == 'AllStrategiesFailedError':
        from .fallback import AllStrategiesFailedError
        return AllStrategiesFailedError
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# 公开API
__all__ = [
    # 版本
    '__version__',
    '__author__',

    # 顶层函数
    'fetch_article',
    'fetch_batch',
    'clear_cache',

    # 类
    'UnifiedFetcher',
    'Config',
    'Article',

    # 异常
    'FetchError',
    'URLValidationError',
    'CaptchaDetectedError',
    'AllStrategiesFailedError',

    # 工具函数
    'get_default_config',
    'get_default_fetcher',
]
