"""
Fincept China Market - 中国市场数据客户端
天龙引擎独家 Skill，封装 AkShare 中国市场数据能力
"""

__version__ = "1.0.0"
__author__ = "天龙引擎"

from fincept_china_market.scripts.client import ChinaMarketClient, FinceptError

__all__ = ["ChinaMarketClient", "FinceptError"]
