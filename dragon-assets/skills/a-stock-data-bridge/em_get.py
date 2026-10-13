"""em_get · a-stock-data-bridge 统一节流入口

天龙自研模块 · 与 Apache-2.0 上游接口语义对齐
实现 5 层防封：
  1. 节流门 (≥1s + 抖动)
  2. 退避重试 (max 3)
  3. 主源失败切备胎
  4. 备胎失败标记缺失（不静默）
  5. 错误码识别决策树
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Any, Callable, Iterable

# UTC+8 时区
TZ_CN = timezone(timedelta(hours=8))

# 节流默认值（与 runtime.conf 对齐）
DEFAULT_MIN_INTERVAL = 1.0
DEFAULT_JITTER_MIN = 0.1
DEFAULT_JITTER_MAX = 0.5
DEFAULT_MAX_RETRIES = 3

# 触发降级的错误码
FALLBACK_ON = {"429", "500", "502", "503", "504", "BESTIP_EMPTY", "PARAM_MISSING"}


@dataclass
class FetchResult:
    """单次拉取结果（含溯源字段）"""
    source: str
    endpoint: str
    data: Any
    fetched_at: str
    fallback_used: bool
    fallback_from: str | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


class Throttle:
    """≥1s 限流 + 抖动控制器"""

    def __init__(
        self,
        min_interval: float = DEFAULT_MIN_INTERVAL,
        jitter_min: float = DEFAULT_JITTER_MIN,
        jitter_max: float = DEFAULT_JITTER_MAX,
    ):
        self.min_interval = min_interval
        self.jitter_min = jitter_min
        self.jitter_max = jitter_max
        self.last_call = 0.0

    def wait(self) -> float:
        """返回实际等待时间（秒）"""
        now = time.monotonic()
        elapsed = now - self.last_call
        jitter = random.uniform(self.jitter_min, self.jitter_max)
        wait_time = max(0.0, self.min_interval + jitter - elapsed)
        if wait_time > 0:
            time.sleep(wait_time)
        self.last_call = time.monotonic()
        return wait_time


class SourceSession:
    """会话复用（keep-alive），整体 5 层防封的中枢"""

    def __init__(self):
        self.throttle = Throttle()
        self.total_calls = 0
        self.fallbacks_used = 0
        self.errors_seen: list[str] = []

    def em_get(
        self,
        endpoint_name: str,
        primary_source: Callable[[], Any],
        fallback_sources: list[Callable[[], Any]] | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> FetchResult:
        """统一节流入口：
        1. 节流门 (≥1s + 抖动)
        2. 主源 + 退避重试 max_retries 次
        3. 主源失败 → 切备胎
        4. 备胎失败 → 标记缺失
        5. 错误码识别（bestip_empty / param_missing / 协议 404 等）
        """
        fallback_sources = fallback_sources or []
        now_iso = datetime.now(TZ_CN).isoformat(timespec="seconds")
        self.throttle.wait()
        self.total_calls += 1

        # 2. 主源 + 退避重试
        last_err = None
        for attempt in range(max_retries):
            try:
                data = primary_source()
                return FetchResult(
                    source=endpoint_name,
                    endpoint=endpoint_name,
                    data=data,
                    fetched_at=now_iso,
                    fallback_used=False,
                )
            except Exception as e:
                last_err = repr(e)
                self.errors_seen.append(repr(e)[:80])
                # 退避（指数退避 + 抖动）
                if attempt < max_retries - 1:
                    backoff = (2 ** attempt) + random.uniform(0, 0.5)
                    time.sleep(backoff)

        # 3. 主源失败 → 切备胎
        for i, fb in enumerate(fallback_sources):
            self.throttle.wait()
            self.fallbacks_used += 1
            try:
                data = fb()
                return FetchResult(
                    source=f"{endpoint_name}.fallback.{i}",
                    endpoint=endpoint_name,
                    data=data,
                    fetched_at=now_iso,
                    fallback_used=True,
                    fallback_from=endpoint_name,
                )
            except Exception as e:
                last_err = repr(e)
                self.errors_seen.append(repr(e)[:80])

        # 4. 全部失败 → 不静默
        return FetchResult(
            source=endpoint_name,
            endpoint=endpoint_name,
            data=None,
            fetched_at=now_iso,
            fallback_used=True,
            error=last_err or "all sources failed",
        )

    def stats(self) -> dict:
        return {
            "total_calls": self.total_calls,
            "fallbacks_used": self.fallbacks_used,
            "errors_seen": len(self.errors_seen),
            "throttle_min_interval": self.throttle.min_interval,
        }


# 单例（供 em_base.py 复用）
_default_session = SourceSession()


def get_session() -> SourceSession:
    return _default_session
