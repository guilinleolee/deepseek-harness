"""
微信公众号SKILL - 统一重构版

一个高性能、可靠的微信公众号文章获取工具。

核心特性:
    - 三层缓存（L1内存 + L2SQLite + L3网络）
    - 智能降级（直接访问 > API降级）
    - 防御性编程（依赖缺失优雅降级）
    - 向后兼容（兼容旧版API）

使用示例:
    >>> import wechat_skills_unified
    >>>
    >>> # 获取单篇文章
    >>> article = wechat_skills_unified.fetch_article("https://mp.weixin.qq.com/s/xxxxx")
    >>> print(article.title)
    >>>
    >>> # 批量获取
    >>> urls = ["url1", "url2", "url3"]
    >>> articles = wechat_skills_unified.fetch_batch(urls)
"""

__version__ = "1.0.0"

# 尝试相对导入（安装后），失败则使用绝对导入（测试/开发环境）
try:
    # 尝试相对导入（当作为包安装时）
    from .core import (
        fetch_article,
        fetch_batch,
        clear_cache,
        Config,
        Article,
        FetchError,
        URLValidationError,
        CaptchaDetectedError,
        AllStrategiesFailedError,
    )
except ImportError:
    # 回退到绝对导入（测试/开发环境）
    from core import (
        fetch_article,
        fetch_batch,
        clear_cache,
        Config,
        Article,
        FetchError,
        URLValidationError,
        CaptchaDetectedError,
        AllStrategiesFailedError,
    )

__all__ = [
    '__version__',
    'fetch_article',
    'fetch_batch',
    'clear_cache',
    'Config',
    'Article',
    'FetchError',
    'URLValidationError',
    'CaptchaDetectedError',
    'AllStrategiesFailedError',
]
