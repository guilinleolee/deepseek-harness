"""
fincept-news-intel - 新闻智能分析模块

提供新闻抓取、情感分析、主题聚类、实体关联和 SEC 公告追踪能力。
"""

from .client import NewsIntelligence, NewsIntelError

__all__ = ["NewsIntelligence", "NewsIntelError"]
