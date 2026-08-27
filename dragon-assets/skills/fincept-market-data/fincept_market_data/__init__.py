"""
Fincept Market Data Skill
金融市场数据一站式连接器

支持30+数据源: Yahoo Finance, Polygon.io, Kraken, Binance, Coinbase等
"""

__version__ = "1.0.0"

from .client import MarketDataClient, RateLimitError, DataNotFoundError, ProviderError
from . import exceptions

__all__ = [
    "MarketDataClient",
    "RateLimitError",
    "DataNotFoundError",
    "ProviderError",
    "exceptions"
]
