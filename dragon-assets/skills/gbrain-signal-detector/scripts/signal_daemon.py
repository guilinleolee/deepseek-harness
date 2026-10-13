#!/usr/bin/env python3
"""
gbrain-signal-detector: Always-on Signal Detection Daemon
整合自 garrytan/gbrain signal-detector

功能:
- 并行实时信息挖掘
- 后台持续监控
- 多源信号聚合
- 智能触发机制
"""

from __future__ import annotations
import asyncio
import logging
import signal
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import yaml
import json
import hashlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SignalPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Signal:
    """信号数据模型"""
    id: str
    source: str
    source_type: str
    content: str
    url: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    priority: SignalPriority = SignalPriority.MEDIUM
    keywords: list = field(default_factory=list)
    relevance_score: float = 0.0
    entities: dict = field(default_factory=dict)
    processed: bool = False


@dataclass
class SignalConfig:
    """信号检测配置"""
    enabled: bool = False
    check_interval: int = 3600  # 默认1小时
    sources: list = field(default_factory=list)
    keywords: list = field(default_factory=list)
    relevance_threshold: float = 0.7
    max_signals_per_day: int = 100

    @classmethod
    def from_yaml(cls, path: str) -> "SignalConfig":
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return cls(**data.get('signal_detector', {}))


class SignalProcessor:
    """信号处理器"""

    def __init__(self, config: SignalConfig):
        self.config = config
        self.signals: list[Signal] = []
        self.seen_hashes: set[str] = set()

    def generate_signal_id(self, content: str) -> str:
        """生成唯一信号ID"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def check_relevance(self, content: str) -> float:
        """检查内容相关性"""
        if not self.config.keywords:
            return 0.5

        content_lower = content.lower()
        matches = sum(1 for kw in self.config.keywords if kw.lower() in content_lower)
        return min(1.0, matches / len(self.config.keywords))

    def extract_keywords(self, content: str) -> list[str]:
        """提取关键词"""
        keywords = []
        content_lower = content.lower()
        for kw in self.config.keywords:
            if kw.lower() in content_lower:
                keywords.append(kw)
        return keywords

    async def process_signal(self, signal: Signal) -> bool:
        """处理单个信号"""
        # 去重检查
        signal_hash = self.generate_signal_id(signal.content)
        if signal_hash in self.seen_hashes:
            logger.debug(f"Duplicate signal skipped: {signal.id}")
            return False

        self.seen_hashes.add(signal_hash)

        # 相关性评分
        signal.relevance_score = self.check_relevance(signal.content)
        if signal.relevance_score < self.config.relevance_threshold:
            logger.debug(f"Low relevance signal skipped: {signal.id}")
            return False

        # 关键词提取
        signal.keywords = self.extract_keywords(signal.content)

        # 优先级判定
        if signal.relevance_score >= 0.9:
            signal.priority = SignalPriority.HIGH
        elif signal.relevance_score >= 0.7:
            signal.priority = SignalPriority.MEDIUM
        else:
            signal.priority = SignalPriority.LOW

        self.signals.append(signal)
        logger.info(f"Signal processed: {signal.id} (priority={signal.priority.value}, score={signal.relevance_score:.2f})")
        return True

    async def process_batch(self, signals: list[Signal]) -> int:
        """批量处理信号"""
        processed_count = 0
        for signal in signals:
            if await self.process_signal(signal):
                processed_count += 1
        return processed_count


class SignalAggregator:
    """信号聚合器"""

    def __init__(self, max_signals: int = 100):
        self.max_signals = max_signals
        self.signal_queue: list[Signal] = []

    async def add_signal(self, signal: Signal):
        """添加信号到队列"""
        self.signal_queue.append(signal)

        # 按相关性排序
        self.signal_queue.sort(key=lambda s: s.relevance_score, reverse=True)

        # 限制队列大小
        if len(self.signal_queue) > self.max_signals:
            self.signal_queue = self.signal_queue[:self.max_signals]

    async def get_top_signals(self, n: int = 10) -> list[Signal]:
        """获取top N信号"""
        return self.signal_queue[:n]

    async def get_signals_by_priority(self, priority: SignalPriority) -> list[Signal]:
        """按优先级筛选"""
        return [s for s in self.signal_queue if s.priority == priority]


class SignalMonitor:
    """信号监控器"""

    def __init__(self, config: SignalConfig):
        self.config = config
        self.processor = SignalProcessor(config)
        self.aggregator = SignalAggregator(config.max_signals_per_day)
        self.running = False
        self.stats = {
            "total_signals": 0,
            "processed_signals": 0,
            "high_priority": 0,
            "errors": 0,
            "last_run": None
        }

    async def check_sources(self) -> list[Signal]:
        """检查所有信号源"""
        signals = []

        for source in self.config.sources:
            try:
                if source.get('type') == 'rss':
                    signals.extend(await self._check_rss(source))
                elif source.get('type') == 'api':
                    signals.extend(await self._check_api(source))
            except Exception as e:
                logger.error(f"Error checking source {source.get('name')}: {e}")
                self.stats["errors"] += 1

        self.stats["total_signals"] += len(signals)
        return signals

    async def _check_rss(self, source: dict) -> list[Signal]:
        """检查RSS源"""
        # TODO: 实现RSS解析
        logger.debug(f"Checking RSS: {source.get('name')}")
        return []

    async def _check_api(self, source: dict) -> list[Signal]:
        """检查API源"""
        # TODO: 实现API轮询
        logger.debug(f"Checking API: {source.get('name')}")
        return []

    async def run_cycle(self):
        """运行一个检测周期"""
        logger.info("Starting signal detection cycle...")

        # 1. 检查所有信号源
        signals = await self.check_sources()
        logger.info(f"Found {len(signals)} signals from sources")

        # 2. 处理信号
        processed = await self.processor.process_batch(signals)
        self.stats["processed_signals"] += processed
        logger.info(f"Processed {processed} signals")

        # 3. 聚合信号
        for signal in self.processor.signals[-processed:]:
            await self.aggregator.add_signal(signal)

        # 4. 更新统计
        self.stats["high_priority"] = len([
            s for s in self.aggregator.signal_queue
            if s.priority == SignalPriority.HIGH
        ])
        self.stats["last_run"] = datetime.now().isoformat()

    async def start(self):
        """启动守护进程"""
        if not self.config.enabled:
            logger.warning("Signal detector is disabled in config")
            return

        self.running = True
        logger.info("Signal detector daemon started")

        while self.running:
            try:
                await self.run_cycle()
                await asyncio.sleep(self.config.check_interval)
            except asyncio.CancelledError:
                logger.info("Signal detector cancelled")
                break
            except Exception as e:
                logger.error(f"Error in detection cycle: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(60)  # 出错后等待1分钟

    def stop(self):
        """停止守护进程"""
        self.running = False
        logger.info("Signal detector daemon stopped")

    def get_stats(self) -> dict:
        """获取统计信息"""
        result = dict(self.stats)
        result.update({
            "queue_size": len(self.aggregator.signal_queue),
            "high_priority_signals": len([
                s for s in self.aggregator.signal_queue
                if s.priority == SignalPriority.HIGH
            ]),
            "medium_priority_signals": len([
                s for s in self.aggregator.signal_queue
                if s.priority == SignalPriority.MEDIUM
            ]),
            "low_priority_signals": len([
                s for s in self.aggregator.signal_queue
                if s.priority == SignalPriority.LOW
            ])
        })
        return result


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='gbrain-signal-detector')
    parser.add_argument('--config', default='config.yaml', help='Config file path')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--once', action='store_true', help='Run single cycle')
    parser.add_argument('--stats', action='store_true', help='Show stats')
    args = parser.parse_args()

    # 加载配置
    config_path = args.config
    if not config_path.startswith('/'):
        config_path = f"{__file__}/../config.yaml"

    try:
        config = SignalConfig.from_yaml(config_path)
    except FileNotFoundError:
        logger.warning(f"Config not found: {config_path}, using defaults")
        config = SignalConfig()

    monitor = SignalMonitor(config)

    # 设置信号处理
    def signal_handler(sig, frame):
        logger.info("Received signal, shutting down...")
        monitor.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if args.stats:
        print(json.dumps(monitor.get_stats(), indent=2, default=str))
        return

    if args.daemon or args.once:
        if args.once:
            await monitor.run_cycle()
            print(json.dumps(monitor.get_stats(), indent=2, default=str))
        else:
            await monitor.start()
    else:
        # 交互模式
        print("gbrain-signal-detector Interactive Mode")
        print("Commands: run, stats, quit")
        while True:
            cmd = input("> ").strip()
            if cmd == 'quit':
                break
            elif cmd == 'run':
                await monitor.run_cycle()
                print(json.dumps(monitor.get_stats(), indent=2, default=str))
            elif cmd == 'stats':
                print(json.dumps(monitor.get_stats(), indent=2, default=str))
            elif cmd == 'top':
                signals = await monitor.aggregator.get_top_signals(5)
                for s in signals:
                    print(f"[{s.priority.value}] {s.content[:100]}...")


if __name__ == "__main__":
    asyncio.run(main())
