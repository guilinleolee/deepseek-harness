"""
Pandadata API - A股/港股/美股金融数据接口

Usage:
    from pandadata_runtime import PandadataRuntime
    runtime = PandadataRuntime()
    result = runtime.call("get_stock_daily", code="600519", date="2026-08-18")
"""

from .pandadata_runtime import PandadataRuntime, PandadataError, call, get_runtime

__version__ = "1.0.0"
__all__ = [
    "PandadataRuntime",
    "PandadataError",
    "call",
    "get_runtime",
]
