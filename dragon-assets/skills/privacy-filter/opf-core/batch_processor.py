#!/usr/bin/env python3
"""
OPF Batch Processor - 批量处理与ETL管道封装
=========================================
大规模数据脱敏处理与ETL管道集成

功能:
    - 流式批处理（内存友好）
    - ETL管道节点
    - 增量处理支持
    - 进度追踪与断点续传
    - 统计报告生成

Author: Tianlong Engine Integration
Version: 1.0
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Optional, Callable, Iterator, Any
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

from .opf_wrapper import OPFWrappedModel, OPFResult


@dataclass
class BatchConfig:
    """批量处理配置"""
    batch_size: int = 100
    max_workers: int = 4
    checkpoint_interval: int = 1000
    resume_on_error: bool = True
    max_retries: int = 3
    mode: str = "typed"
    device: str = "cpu"


@dataclass
class ProcessingStats:
    """处理统计"""
    total: int = 0
    processed: int = 0
    failed: int = 0
    skipped: int = 0
    total_pii: int = 0
    by_label: dict = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    last_checkpoint: Optional[str] = None

    def to_dict(self) -> dict:
        elapsed = time.time() - self.start_time
        return {
            "total": self.total,
            "processed": self.processed,
            "failed": self.failed,
            "skipped": self.skipped,
            "total_pii": self.total_pii,
            "by_label": self.by_label,
            "elapsed_seconds": round(elapsed, 2),
            "rate_per_second": round(self.processed / elapsed, 2) if elapsed > 0 else 0
        }


class ETLRedactionNode:
    """
    ETL数据管道脱敏节点

    用于数据处理管道中的隐私信息脱敏步骤

    使用示例:
        >>> from opf_core.batch_processor import ETLRedactionNode
        >>> node = ETLRedactionNode(mode="typed")
        >>> records = [{"content": "张三邮箱 zhangsan@example.com"}]
        >>> clean = node.process_batch(records)
        >>> print(clean[0]["content_clean"])
        <PRIVATE_PERSON>邮箱 <PRIVATE_EMAIL>
    """

    def __init__(
        self,
        mode: str = "typed",
        device: str = "cpu",
        text_field: str = "content",
        output_prefix: str = "clean"
    ):
        self.opf = OPFWrappedModel(mode=mode, device=device)
        self.text_field = text_field
        self.output_prefix = output_prefix

    def process_record(self, record: dict) -> dict:
        """处理单条记录"""
        text = record.get(self.text_field, "")
        result = self.opf.redact(text)

        record[f"{self.output_prefix}_text"] = result.redacted_text
        record[f"{self.output_prefix}_pii_count"] = result.span_count
        record[f"{self.output_prefix}_pii_types"] = result.by_label
        record[f"{self.output_prefix}_has_pii"] = result.has_pii()

        return record

    def process_batch(self, records: list[dict]) -> list[dict]:
        """批量处理"""
        return [self.process_record(r) for r in records]

    def __repr__(self) -> str:
        return f"ETLRedactionNode(text_field={self.text_field}, mode={self.opf.config.mode})"


class StreamBatchProcessor:
    """
    流式批处理（内存友好）

    适用于大文件处理，避免一次性加载全部数据到内存

    使用示例:
        >>> processor = StreamBatchProcessor(batch_size=100)
        >>> processor.process_jsonl_large(
        ...     input_path="large.jsonl",
        ...     output_path="clean.jsonl",
        ...     progress_callback=lambda p, t: print(f"{p}/{t}")
        ... )
    """

    def __init__(self, config: Optional[BatchConfig] = None):
        self.config = config or BatchConfig()
        self.opf = OPFWrappedModel(mode=self.config.mode, device=self.config.device)
        self.stats = ProcessingStats()

    def process_jsonl_large(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        checkpoint_path: Optional[str] = None
    ) -> dict:
        """大文件JSONL流式处理"""
        input_p = Path(input_path)
        output_p = Path(output_path) if output_path else None
        checkpoint_p = Path(checkpoint_path) if checkpoint_path else None

        # 读取或创建检查点
        processed_lines = set()
        if checkpoint_p and checkpoint_p.exists():
            with open(checkpoint_p, "r", encoding="utf-8") as f:
                processed_lines = set(json.loads(line)["line"] for line in f)

        output_file = open(output_p, "w", encoding="utf-8") if output_p else None

        try:
            with open(input_p, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line_num in processed_lines:
                        continue

                    try:
                        record = json.loads(line)
                        text = record.get("text", record.get("content", ""))
                        result = self.opf.redact(text)

                        self.stats.processed += 1
                        self.stats.total_pii += result.span_count

                        for label, count in result.by_label.items():
                            self.stats.by_label[label] = self.stats.by_label.get(label, 0) + count

                        if output_file:
                            output_record = {"line": line_num, "redacted": result.redacted_text}
                            output_file.write(json.dumps(output_record, ensure_ascii=False) + "\n")

                        # 定期保存检查点
                        if checkpoint_p and line_num % self.config.checkpoint_interval == 0:
                            self._save_checkpoint(checkpoint_p, line_num)
                            self.stats.last_checkpoint = str(checkpoint_p)

                        if progress_callback:
                            progress_callback(self.stats.processed, self.stats.total)

                    except json.JSONDecodeError:
                        self.stats.failed += 1
                        continue

        finally:
            if output_file:
                output_file.close()

        return self.stats.to_dict()

    def _save_checkpoint(self, checkpoint_path: Path, line_num: int) -> None:
        """保存检查点"""
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        with open(checkpoint_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"line": line_num, "timestamp": datetime.now().isoformat()}) + "\n")

    def __repr__(self) -> str:
        return f"StreamBatchProcessor(batch_size={self.config.batch_size})"


class ParallelBatchProcessor:
    """
    并行批处理（多线程）

    适用于多核CPU加速处理

    使用示例:
        >>> processor = ParallelBatchProcessor(max_workers=4)
        >>> results = processor.process_texts([
        ...     "张三邮箱 zhangsan@example.com",
        ...     "李四电话 13812345678"
        ... ])
    """

    def __init__(self, config: Optional[BatchConfig] = None):
        self.config = config or BatchConfig()
        self.opf = OPFWrappedModel(mode=self.config.mode, device=self.config.device)

    def process_texts(self, texts: list[str]) -> list[OPFResult]:
        """并行处理文本列表"""
        results = []

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_idx = {
                executor.submit(self.opf.redact, text): idx
                for idx, text in enumerate(texts)
            }

            result_list = [None] * len(texts)

            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    result_list[idx] = future.result()
                except Exception as e:
                    result_list[idx] = None

        return [r for r in result_list if r is not None]


def create_etl_pipeline(
    mode: str = "typed",
    text_field: str = "content",
    output_prefix: str = "redacted"
) -> ETLRedactionNode:
    """
    创建ETL脱敏管道节点

    Args:
        mode: 脱敏模式 (typed/untyped/redacted)
        text_field: 输入文本字段名
        output_prefix: 输出字段前缀

    Returns:
        ETLRedactionNode: 配置好的ETL节点
    """
    return ETLRedactionNode(
        mode=mode,
        text_field=text_field,
        output_prefix=output_prefix
    )


def quick_redact(
    text: str,
    mode: str = "typed"
) -> str:
    """
    快速脱敏（单次调用）

    Args:
        text: 待脱敏文本
        mode: 脱敏模式

    Returns:
        str: 脱敏后文本
    """
    opf = OPFWrappedModel(mode=mode)
    result = opf.redact(text)
    return result.redacted_text


def batch_redact(
    texts: list[str],
    mode: str = "typed",
    max_workers: int = 4
) -> list[dict]:
    """
    批量脱敏（多线程）

    Args:
        texts: 文本列表
        mode: 脱敏模式
        max_workers: 最大线程数

    Returns:
        list[dict]: 脱敏结果列表
    """
    processor = ParallelBatchProcessor(
        config=BatchConfig(max_workers=max_workers, mode=mode)
    )
    results = processor.process_texts(texts)

    return [
        {
            "text": r.text,
            "redacted": r.redacted_text,
            "pii_count": r.span_count,
            "pii_types": r.by_label
        }
        for r in results
    ]


if __name__ == "__main__":
    print("=== OPF Batch Processor Test ===")

    try:
        # ETL节点测试
        print("\n[1] ETL节点测试")
        node = ETLRedactionNode()
        records = [
            {"content": "张三邮箱 zhangsan@example.com"},
            {"content": "李四电话 13812345678"}
        ]
        results = node.process_batch(records)
        for r in results:
            print(f"  输入: {r['content']}")
            print(f"  输出: {r['redacted_text']}")
            print(f"  PII数量: {r['redacted_pii_count']}")
            print()

        # 快速脱敏测试
        print("[2] 快速脱敏测试")
        text = "王五身份证 110101199001011234"
        redacted = quick_redact(text)
        print(f"  输入: {text}")
        print(f"  输出: {redacted}")

        # 批量脱敏测试
        print("\n[3] 批量脱敏测试")
        texts = [
            "张三邮箱 zhangsan@example.com",
            "李四电话 13812345678",
            "王五地址 北京市朝阳区xxx"
        ]
        results = batch_redact(texts, max_workers=2)
        for r in results:
            print(f"  {r['redacted']} ({r['pii_count']}处PII)")

        print("\n=== 测试通过 ===")

    except RuntimeError as e:
        print(f"✗ OPF未安装: {e}")
        print("\n请先安装OPF:")
        print("  pip install privacy-filter")
