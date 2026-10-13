"""
代理池管理模块
"""

import random
import time
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ProxyInfo:
    """代理信息类"""

    def __init__(
        self,
        proxy: str,
        protocol: str = 'http',
        score: int = 100,
        last_used: Optional[datetime] = None,
        fail_count: int = 0
    ):
        self.proxy = proxy
        self.protocol = protocol
        self.score = score
        self.last_used = last_used
        self.fail_count = fail_count
        self.created_at = datetime.now()

    def is_available(self) -> bool:
        """检查代理是否可用"""
        # 失败次数过多则不可用
        if self.fail_count >= 3:
            return False

        # 分数太低则不可用
        if self.score < 20:
            return False

        return True

    def record_success(self):
        """记录成功使用"""
        self.fail_count = 0
        self.score = min(100, self.score + 5)
        self.last_used = datetime.now()

    def record_failure(self):
        """记录失败使用"""
        self.fail_count += 1
        self.score = max(0, self.score - 10)
        self.last_used = datetime.now()


class ProxyPool:
    """代理池管理类"""

    def __init__(
        self,
        proxies: Optional[List[str]] = None,
        strategy: str = 'round_robin',
        refresh_interval: int = 300  # 5分钟
    ):
        """
        初始化代理池

        Args:
            proxies: 代理列表
            strategy: 选择策略 (round_robin, random, least_used, score_based)
            refresh_interval: 刷新间隔（秒）
        """
        self.strategy = strategy
        self.refresh_interval = refresh_interval
        self.last_refresh = datetime.now()

        self.proxy_list: List[ProxyInfo] = []
        self.current_index = 0

        if proxies:
            self.add_proxies(proxies)

    def add_proxies(self, proxies: List[str]):
        """添加代理到池中"""
        for proxy in proxies:
            proxy_info = ProxyInfo(proxy)
            self.proxy_list.append(proxy_info)
            logger.info(f"Added proxy: {proxy}")

    def remove_proxy(self, proxy: str):
        """从池中移除代理"""
        self.proxy_list = [p for p in self.proxy_list if p.proxy != proxy]
        logger.info(f"Removed proxy: {proxy}")

    def get_next_proxy(self) -> Optional[str]:
        """获取下一个可用代理"""
        # 定期刷新代理池
        if (datetime.now() - self.last_refresh).seconds > self.refresh_interval:
            self.refresh_pool()

        # 获取可用代理
        available = [p for p in self.proxy_list if p.is_available()]

        if not available:
            logger.warning("No available proxies")
            return None

        # 根据策略选择代理
        if self.strategy == 'round_robin':
            proxy_info = available[self.current_index % len(available)]
            self.current_index += 1

        elif self.strategy == 'random':
            proxy_info = random.choice(available)

        elif self.strategy == 'least_used':
            proxy_info = min(
                available,
                key=lambda p: p.last_used or datetime.min
            )

        elif self.strategy == 'score_based':
            # 按分数加权随机选择
            scores = [p.score for p in available]
            total = sum(scores)
            if total == 0:
                proxy_info = random.choice(available)
            else:
                rand = random.uniform(0, total)
                cumsum = 0
                for i, score in enumerate(scores):
                    cumsum += score
                    if rand <= cumsum:
                        proxy_info = available[i]
                        break

        return proxy_info.proxy if proxy_info else None

    def record_success(self, proxy: str):
        """记录代理使用成功"""
        for proxy_info in self.proxy_list:
            if proxy_info.proxy == proxy:
                proxy_info.record_success()
                break

    def record_failure(self, proxy: str):
        """记录代理使用失败"""
        for proxy_info in self.proxy_list:
            if proxy_info.proxy == proxy:
                proxy_info.record_failure()
                logger.warning(f"Proxy failed: {proxy}, score: {proxy_info.score}")
                break

    def refresh_pool(self):
        """刷新代理池（移除不可用代理）"""
        before = len(self.proxy_list)
        self.proxy_list = [p for p in self.proxy_list if p.is_available()]
        after = len(self.proxy_list)
        self.last_refresh = datetime.now()

        if before != after:
            logger.info(f"Pool refreshed: {before} -> {after} proxies")

    def get_stats(self) -> Dict[str, Any]:
        """获取代理池统计信息"""
        available = [p for p in self.proxy_list if p.is_available()]

        return {
            'total_proxies': len(self.proxy_list),
            'available_proxies': len(available),
            'failed_proxies': len(self.proxy_list) - len(available),
            'avg_score': sum(p.score for p in available) / len(available) if available else 0,
            'strategy': self.strategy,
        }

    def print_stats(self):
        """打印统计信息"""
        stats = self.get_stats()
        print("\n" + "="*50)
        print("Proxy Pool Statistics")
        print("="*50)
        print(f"Total proxies: {stats['total_proxies']}")
        print(f"Available: {stats['available_proxies']}")
        print(f"Failed: {stats['failed_proxies']}")
        print(f"Avg score: {stats['avg_score']:.2f}")
        print(f"Strategy: {stats['strategy']}")
        print("="*50 + "\n")
