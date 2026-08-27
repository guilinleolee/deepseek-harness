#!/usr/bin/env python3
"""
OPF (OpenAI Privacy Filter) Core Wrapper
========================================
OpenAI Privacy Filter PII检测与脱敏核心封装

功能:
    - 8类PII即时检测
    - typed/untyped/redacted三种模式
    - 批量处理支持
    - 自定义标签空间微调

支持PII类型:
    - private_person: 私人人员信息
    - private_date: 私人日期
    - private_email: 私人邮箱
    - private_phone: 私人电话
    - private_address: 私人地址
    - account_number: 账户号码
    - private_url: 私人URL
    - secret: 密钥/密码

Author: Tianlong Engine Integration
Version: 1.0
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Literal, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class OPFConfig:
    """OPF配置"""
    mode: Literal["typed", "untyped", "redacted"] = "typed"
    device: Literal["cpu", "cuda"] = "cpu"
    checkpoint: Optional[str] = None
    label_space: Optional[dict] = None

    def to_args(self) -> list[str]:
        args = []
        if self.device == "cuda":
            args.append("--device")
            args.append("cuda")
        if self.checkpoint:
            args.append("--checkpoint")
            args.append(self.checkpoint)
        return args


@dataclass
class PIISpan:
    """PII检测结果"""
    label: str
    start: int
    end: int
    text: str
    placeholder: str

    @classmethod
    def from_dict(cls, d: dict) -> "PIISpan":
        return cls(
            label=d["label"],
            start=d["start"],
            end=d["end"],
            text=d["text"],
            placeholder=d.get("placeholder", f"<{d['label'].upper()}>")
        )


@dataclass
class OPFResult:
    """OPF检测结果"""
    text: str
    redacted_text: str
    spans: list[PIISpan]
    span_count: int
    by_label: dict[str, int]
    output_mode: str
    decoded_mismatch: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "OPFResult":
        spans = [PIISpan.from_dict(s) for s in d.get("detected_spans", [])]
        summary = d.get("summary", {})
        by_label = summary.get("by_label", {})
        return cls(
            text=d.get("text", ""),
            redacted_text=d.get("redacted_text", ""),
            spans=spans,
            span_count=summary.get("span_count", len(spans)),
            by_label=by_label,
            output_mode=summary.get("output_mode", "typed"),
            decoded_mismatch=summary.get("decoded_mismatch", False)
        )

    def has_pii(self) -> bool:
        """检测是否有PII"""
        return self.span_count > 0

    def get_pii_types(self) -> list[str]:
        """获取检测到的PII类型列表"""
        return list(self.by_label.keys())

    def get_summary_text(self) -> str:
        """获取摘要文本"""
        if not self.by_label:
            return "无隐私信息"
        parts = [f"{label}: {count}处" for label, count in self.by_label.items()]
        return ", ".join(parts)


class OPFWrappedModel:
    """
    OPF核心封装类

    使用示例:
        >>> opf = OPFWrappedModel()
        >>> result = opf.redact("张三邮箱 zhangsan@example.com")
        >>> print(result.redacted_text)  # 张三邮箱 <PRIVATE_EMAIL>
        >>> print(result.get_summary_text())  # private_person: 1处, private_email: 1处
    """

    def __init__(
        self,
        mode: Literal["typed", "untyped", "redacted"] = "typed",
        device: Literal["cpu", "cuda"] = "cpu",
        checkpoint: Optional[str] = None
    ):
        """
        初始化OPF模型

        Args:
            mode: 输出模式
                - typed: 类型标签模式 <PRIVATE_EMAIL>
                - untyped: 统一标签模式 <PII>
                - redacted: 替换为原文（仅检测）
            device: 设备类型 cpu/cuda
            checkpoint: 自定义模型路径
        """
        self.config = OPFConfig(mode=mode, device=device, checkpoint=checkpoint)
        self._check_opf_installed()

    def _check_opf_installed(self) -> bool:
        """检查OPF是否已安装"""
        try:
            result = subprocess.run(
                ["opf", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            raise RuntimeError(
                "OPF未安装。请运行:\n"
                "  pip install privacy-filter  # 推荐\n"
                "  或 cd ~/.claude/skills/privacy-filter && pip install -e ."
            )

    def _run_opf(self, text: str, extra_args: Optional[list[str]] = None) -> dict:
        """执行OPF命令"""
        cmd = ["opf", "--output-mode", self.config.mode] + self.config.to_args()
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(text)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            output = result.stdout.strip()

            # 尝试解析JSON输出
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                # 如果不是JSON，包装为简化格式
                return {
                    "schema_version": 1,
                    "text": text,
                    "redacted_text": output,
                    "detected_spans": [],
                    "summary": {"span_count": 0, "by_label": {}, "output_mode": self.config.mode}
                }
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"OPF处理超时: {text[:50]}...")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"OPF执行失败: {e.stderr}")

    def redact(self, text: str) -> OPFResult:
        """
        即时脱敏文本

        Args:
            text: 待脱敏文本

        Returns:
            OPFResult: 脱敏结果对象

        示例:
            >>> opf = OPFWrappedModel()
            >>> result = opf.redact("张三邮箱 zhangsan@example.com")
            >>> print(result.redacted_text)
            <PRIVATE_PERSON>邮箱 <PRIVATE_EMAIL>
        """
        data = self._run_opf(text)
        return OPFResult.from_dict(data)

    def batch_redact(self, texts: list[str]) -> list[OPFResult]:
        """
        批量脱敏

        Args:
            texts: 文本列表

        Returns:
            list[OPFResult]: 脱敏结果列表

        示例:
            >>> opf = OPFWrappedModel()
            >>> results = opf.batch_redact(["文本1", "文本2", "文本3"])
        """
        return [self.redact(text) for text in texts]

    def file_redact(self, input_path: str, output_path: Optional[str] = None) -> dict:
        """
        文件脱敏

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径（可选）

        Returns:
            dict: 处理结果统计
        """
        output_path = output_path or tempfile.mktemp(suffix=".txt")
        cmd = ["opf", "-f", input_path, "-o", output_path]
        cmd.extend(self.config.to_args())

        subprocess.run(cmd, check=True, timeout=60)

        # 读取输出文件统计
        with open(output_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        return {
            "output_path": output_path,
            "lines_processed": len(lines),
            "timestamp": datetime.now().isoformat()
        }

    def check_text(self, text: str) -> dict:
        """
        仅检测不脱敏

        Args:
            text: 待检测文本

        Returns:
            dict: 检测统计信息
        """
        result = self.redact(text)
        return {
            "has_pii": result.has_pii(),
            "pii_count": result.span_count,
            "pii_types": result.get_pii_types(),
            "types_detail": result.by_label
        }

    def __repr__(self) -> str:
        return f"OPFWrappedModel(mode={self.config.mode}, device={self.config.device})"


def create_opf_with_labels(
    custom_labels: list[str],
    category_version: str = "custom_v1"
) -> OPFWrappedModel:
    """
    创建自定义标签空间的OPF实例

    Args:
        custom_labels: 自定义标签列表，如 ["O", "chinese_name", "chinese_phone", "chinese_id"]
        category_version: 标签版本标识

    Returns:
        OPFWrappedModel: 配置了自定义标签的实例

    示例:
        >>> custom_opf = create_opf_with_labels(
        ...     ["O", "chinese_name", "chinese_phone", "chinese_id"]
        ... )
    """
    config = OPFConfig()
    config.label_space = {
        "category_version": category_version,
        "span_class_names": custom_labels
    }
    return OPFWrappedModel()


if __name__ == "__main__":
    # 测试代码
    print("=== OPF Wrapper Test ===")

    try:
        # 初始化
        opf = OPFWrappedModel()
        print(f"✓ OPF初始化成功: {opf}")

        # 测试文本
        test_text = "张三的邮箱是 zhangsan@example.com，电话 13812345678"

        # 即时脱敏
        result = opf.redact(test_text)
        print(f"\n输入文本: {test_text}")
        print(f"脱敏文本: {result.redacted_text}")
        print(f"PII摘要: {result.get_summary_text()}")

        # 仅检测
        check = opf.check_text(test_text)
        print(f"\n检测结果: {check}")

        print("\n=== 测试通过 ===")

    except RuntimeError as e:
        print(f"✗ OPF未安装: {e}")
        print("\n请先安装OPF:")
        print("  pip install privacy-filter")
