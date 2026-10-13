#!/usr/bin/env python3
"""
OPF CLI Wrapper - 命令行管道封装
===================================
提供与天龙引擎岗位协同的CLI接口

功能:
    - 即时扫描管道 (stdin/stdout)
    - 文件批量处理
    - JSONL批量处理
    - 统计报告生成
    - ETL节点集成

Author: Tianlong Engine Integration
Version: 1.0
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional, TextIO, List
from .opf_wrapper import OPFWrappedModel, OPFResult


class OPFCLI:
    """OPF CLI封装类"""

    def __init__(
        self,
        mode: str = "typed",
        device: str = "cpu",
        checkpoint: Optional[str] = None,
        verbose: bool = False
    ):
        self.opf = OPFWrappedModel(mode=mode, device=device, checkpoint=checkpoint)
        self.verbose = verbose

    def scan_stdin(self, input_stream: TextIO = sys.stdin) -> None:
        """扫描标准输入"""
        text = input_stream.read()
        result = self.opf.redact(text)
        print(result.redacted_text)

    def scan_file(self, input_path: str, output_path: Optional[str] = None) -> dict:
        """扫描单个文件"""
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        result = self.opf.redact(text)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result.redacted_text)
            return {"input": input_path, "output": output_path, "status": "success"}

        return {
            "input": input_path,
            "text": result.redacted_text,
            "pii_count": result.span_count,
            "pii_types": result.by_label
        }

    def scan_jsonl(self, input_path: str, output_path: Optional[str] = None) -> dict:
        """扫描JSONL批量文件"""
        results = []
        stats = {"total": 0, "with_pii": 0, "total_pii": 0, "by_label": {}}

        with open(input_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    record = json.loads(line)
                    text = record.get("text", record.get("content", ""))
                    result = self.opf.redact(text)

                    stats["total"] += 1
                    if result.has_pii():
                        stats["with_pii"] += 1
                    stats["total_pii"] += result.span_count

                    for label, count in result.by_label.items():
                        stats["by_label"][label] = stats["by_label"].get(label, 0) + count

                    results.append({
                        "line": line_num,
                        "redacted": result.redacted_text,
                        "pii_count": result.span_count,
                        "pii_types": result.by_label
                    })
                except json.JSONDecodeError:
                    if self.verbose:
                        print(f"警告: 第{line_num}行JSON解析失败", file=sys.stderr)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                for r in results:
                    output_record = {"line": r["line"], "redacted": r["redacted"]}
                    f.write(json.dumps(output_record, ensure_ascii=False) + "\n")

        stats["results"] = results
        return stats

    def scan_batch(self, input_paths: List[str], output_dir: Optional[str] = None) -> dict:
        """批量扫描多个文件"""
        results = []
        output_dir = Path(output_dir) if output_dir else None

        for input_path in input_paths:
            p = Path(input_path)
            output_path = None
            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(output_dir / p.name)

            result = self.scan_file(str(p), output_path)
            results.append(result)

        return {"files": results, "total": len(results)}

    def generate_report(self, input_path: str) -> str:
        """生成隐私合规审计报告"""
        result = self.opf.check_text(Path(input_path).read_text(encoding="utf-8"))

        report = []
        report.append("=" * 50)
        report.append("OPF 隐私合规审计报告")
        report.append("=" * 50)
        report.append(f"文件: {input_path}")
        report.append(f"检测结果: {'发现隐私信息' if result['has_pii'] else '无隐私信息'}")
        report.append(f"PII总数: {result['pii_count']}")

        if result["pii_types"]:
            report.append("\n按类型分布:")
            for pii_type, count in result["types_detail"].items():
                report.append(f"  - {pii_type}: {count}处")

        report.append("=" * 50)
        return "\n".join(report)


def main():
    """CLI入口点"""
    parser = argparse.ArgumentParser(
        description="OPF (OpenAI Privacy Filter) CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 即时扫描
  opf-cli "张三邮箱 zhangsan@example.com"

  # 管道输入
  cat logs/app.log | opf-cli --stdin

  # 文件扫描
  opf-cli --file ./input.txt --output ./output.txt

  # JSONL批量
  opf-cli --jsonl ./data.jsonl --output ./clean.jsonl

  # 统计报告
  opf-cli --report ./document.txt
        """
    )

    parser.add_argument("text", nargs="?", help="待扫描文本")
    parser.add_argument("--stdin", action="store_true", help="从标准输入读取")
    parser.add_argument("--file", "-f", help="输入文件路径")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--jsonl", help="JSONL批量文件")
    parser.add_argument("--report", action="store_true", help="生成报告")
    parser.add_argument("--mode", "-m", default="typed",
                        choices=["typed", "untyped", "redacted"],
                        help="输出模式")
    parser.add_argument("--device", "-d", default="cpu",
                        choices=["cpu", "cuda"],
                        help="设备类型")
    parser.add_argument("--checkpoint", help="自定义模型路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--batch-dir", help="批量处理目录")
    parser.add_argument("--version", action="version", version="OPF CLI v1.0")

    args = parser.parse_args()
    cli = OPFCLI(mode=args.mode, device=args.device,
                 checkpoint=args.checkpoint, verbose=args.verbose)

    # 管道输入模式
    if args.stdin:
        cli.scan_stdin()
        return

    # 即时文本模式
    if args.text:
        result = cli.opf.redact(args.text)
        print(result.redacted_text)
        if args.verbose:
            print(f"\n[摘要] {result.get_summary_text()}", file=sys.stderr)
        return

    # 报告模式
    if args.report and args.file:
        print(cli.generate_report(args.file))
        return

    # JSONL批量模式
    if args.jsonl:
        stats = cli.scan_jsonl(args.jsonl, args.output)
        if args.verbose:
            print(f"处理: {stats['total']}条", file=sys.stderr)
            print(f"发现PII: {stats['with_pii']}条", file=sys.stderr)
            print(f"PII总数: {stats['total_pii']}", file=sys.stderr)
        return

    # 批量目录模式
    if args.batch_dir:
        from pathlib import Path
        files = list(Path(args.batch_dir).glob("*.txt"))
        stats = cli.scan_batch([str(f) for f in files], args.output)
        print(f"批量处理完成: {stats['total']}个文件", file=sys.stderr)
        return

    # 单文件模式
    if args.file:
        result = cli.scan_file(args.file, args.output)
        if args.output:
            print(f"已保存到: {args.output}", file=sys.stderr)
        else:
            print(result["text"])
        return

    # 无参数
    parser.print_help()


if __name__ == "__main__":
    main()
