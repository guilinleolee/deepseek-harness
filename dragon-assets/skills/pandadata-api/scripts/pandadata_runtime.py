#!/usr/bin/env python3
"""
Pandadata Runtime - 统一的 pandadata-api 调用封装

支持：
- 方法调用封装
- 自动重试
- 限流处理
- 错误处理
- 数据缓存

Usage:
    from pandadata_runtime import PandadataRuntime
    runtime = PandadataRuntime()
    result = runtime.call("get_stock_daily", code="600519", date="2026-08-18")
"""

import os
import time
import json
import hashlib
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import requests

try:
    from functools import lru_cache
except ImportError:
    def lru_cache(maxsize=128):
        """简单的 LRU 缓存装饰器（Python 3.10 以下兼容）"""
        def decorator(func):
            cache = {}
            def wrapper(*args, **kwargs):
                key = str(args) + str(sorted(kwargs.items()))
                if key not in cache:
                    cache[key] = func(*args, **kwargs)
                    if len(cache) > maxsize:
                        # 简单的 FIFO
                        oldest = next(iter(cache))
                        del cache[oldest]
                return cache[key]
            return wrapper
        return decorator


class PandadataError(Exception):
    """Pandadata API 错误"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class RateLimitError(PandadataError):
    """限流错误"""
    pass


class NetworkError(PandadataError):
    """网络错误"""
    pass


class ResponseCode(Enum):
    """响应码"""
    SUCCESS = 0
    PARAM_ERROR = 400
    AUTH_ERROR = 401
    RATE_LIMIT = 429
    SERVER_ERROR = 500
    UNKNOWN = -1


@dataclass
class APIResponse:
    """API 响应"""
    code: int
    message: str
    data: Any = None
    request_id: str = ""
    cost_time: float = 0.0

    @property
    def is_success(self) -> bool:
        return self.code == 0

    @property
    def is_rate_limit(self) -> bool:
        return self.code in (429, -429)


@dataclass
class CacheEntry:
    """缓存条目"""
    data: Any
    timestamp: float
    ttl: float = 300.0  # 默认5分钟

    @property
    def is_expired(self) -> bool:
        return time.time() - self.timestamp > self.ttl


class PandadataRuntime:
    """Pandadata API 运行时"""

    BASE_URL = "https://api.pandadata.wiki/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        cache_ttl: int = 300,
        rate_limit_delay: float = 1.0,
    ):
        """
        初始化运行时

        Args:
            api_key: API 密钥，默认从环境变量 PANDADATA_API_KEY 读取
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            cache_ttl: 缓存过期时间（秒）
            rate_limit_delay: 限流时的延迟时间（秒）
        """
        self.api_key = api_key or os.environ.get("PANDADATA_API_KEY", "")
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache_ttl = cache_ttl
        self.rate_limit_delay = rate_limit_delay
        self._cache: Dict[str, CacheEntry] = {}

    def _get_cache_key(self, method: str, **kwargs) -> str:
        """生成缓存键"""
        key_str = f"{method}:{json.dumps(kwargs, sort_keys=True, ensure_ascii=False)}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_from_cache(self, method: str, **kwargs) -> Optional[Any]:
        """从缓存获取"""
        key = self._get_cache_key(method, **kwargs)
        if key in self._cache:
            entry = self._cache[key]
            if not entry.is_expired:
                return entry.data
            else:
                del self._cache[key]
        return None

    def _set_cache(self, method: str, data: Any, **kwargs):
        """设置缓存"""
        key = self._get_cache_key(method, **kwargs)
        self._cache[key] = CacheEntry(
            data=data,
            timestamp=time.time(),
            ttl=self.cache_ttl
        )

    def _request(
        self,
        method: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求

        Args:
            method: API 方法名
            **kwargs: 方法参数

        Returns:
            API 响应数据
        """
        url = f"{self.BASE_URL}/{method}"

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "pandadata-runtime/1.0",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "params": kwargs,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            raise NetworkError(-1, "Request timeout")

        except requests.exceptions.ConnectionError:
            raise NetworkError(-1, "Connection error")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                raise RateLimitError(429, "Rate limit exceeded")
            raise NetworkError(e.response.status_code, str(e))

        except requests.exceptions.RequestException as e:
            raise NetworkError(-1, str(e))

    def call(
        self,
        method: str,
        use_cache: bool = True,
        **kwargs
    ) -> Union[Dict[str, Any], List, Any]:
        """
        调用 API 方法

        Args:
            method: API 方法名
            use_cache: 是否使用缓存
            **kwargs: 方法参数

        Returns:
            API 响应数据

        Raises:
            PandadataError: API 调用错误
            RateLimitError: 限流错误
            NetworkError: 网络错误
        """
        # 缓存检查
        if use_cache:
            cached = self._get_from_cache(method, **kwargs)
            if cached is not None:
                return cached

        # 重试循环
        last_error = None
        for attempt in range(self.max_retries):
            try:
                result = self._request(method, **kwargs)

                # 解析响应
                code = result.get("code", 0)
                message = result.get("message", "")
                data = result.get("data")

                if code == 0:
                    # 成功，缓存数据
                    if use_cache:
                        self._set_cache(method, data, **kwargs)
                    return data

                elif code == 429 or "rate limit" in message.lower():
                    # 限流，等待后重试
                    wait_time = self.rate_limit_delay * (2 ** attempt)
                    time.sleep(wait_time)
                    last_error = RateLimitError(code, message)
                    continue

                else:
                    # 其他错误
                    raise PandadataError(code, message)

            except (NetworkError, RateLimitError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = self.rate_limit_delay * (2 ** attempt)
                    time.sleep(wait_time)
                    continue
                raise

        # 超出重试次数
        if last_error:
            raise last_error
        raise PandadataError(-1, "Unknown error")

    def call_batch(
        self,
        calls: List[Dict[str, Any]],
        use_cache: bool = True,
    ) -> List[Any]:
        """
        批量调用 API

        Args:
            calls: 调用列表，格式：[{"method": "xxx", "params": {...}}, ...]
            use_cache: 是否使用缓存

        Returns:
            结果列表
        """
        results = []
        for call in calls:
            method = call.get("method")
            params = call.get("params", {})
            result = self.call(method, use_cache=use_cache, **params)
            results.append(result)
        return results

    def get_stock_daily(
        self,
        code: str,
        date: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """获取股票日线数据"""
        return self.call(
            "get_stock_daily",
            code=code,
            date=date or "",
            use_cache=use_cache
        )

    def get_stock_detail(
        self,
        code: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """获取股票基本信息"""
        return self.call(
            "get_stock_detail",
            code=code,
            use_cache=use_cache
        )

    def get_money_flow(
        self,
        code: str,
        date: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """获取资金流向"""
        return self.call(
            "get_money_flow",
            code=code,
            date=date or "",
            use_cache=use_cache
        )

    def get_fina_indicator(
        self,
        code: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """获取财务指标"""
        return self.call(
            "get_fina_indicator",
            code=code,
            use_cache=use_cache
        )

    def get_margin(
        self,
        code: str,
        date: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """获取融资融券数据"""
        return self.call(
            "get_margin",
            code=code,
            date=date or "",
            use_cache=use_cache
        )

    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """获取缓存统计"""
        total = len(self._cache)
        expired = sum(1 for e in self._cache.values() if e.is_expired)
        return {
            "total": total,
            "active": total - expired,
            "expired": expired
        }


# 全局默认运行时实例
_default_runtime: Optional[PandadataRuntime] = None


def get_runtime() -> PandadataRuntime:
    """获取默认运行时实例"""
    global _default_runtime
    if _default_runtime is None:
        _default_runtime = PandadataRuntime()
    return _default_runtime


def call(method: str, **kwargs) -> Any:
    """便捷调用函数"""
    return get_runtime().call(method, **kwargs)


# CLI 入口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Pandadata Runtime CLI")
    parser.add_argument("method", help="API method name")
    parser.add_argument("--code", help="Stock code")
    parser.add_argument("--date", help="Date (YYYY-MM-DD)")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON")

    args = parser.parse_args()

    runtime = PandadataRuntime()

    kwargs = {}
    if args.code:
        kwargs["code"] = args.code
    if args.date:
        kwargs["date"] = args.date

    try:
        result = runtime.call(args.method, **kwargs)
        if args.pretty:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(result, ensure_ascii=False))
    except PandadataError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
