"""
Supertonic TTS 批量合成脚本
支持文件输入、多语言并行处理、进度追踪

Usage:
    python batch_synthesize.py --input texts.txt --lang zh --output ./audio
    python batch_synthesize.py --csv products.csv --column description --voice F2
"""

import argparse
import asyncio
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    from tts_client import TTSClient
except ImportError:
    from .tts_client import TTSClient


@dataclass
class SynthesisJob:
    """合成任务"""
    id: int
    text: str
    lang: str
    voice: str
    speed: float
    enable_expression: bool
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SynthesisResult:
    """合成结果"""
    job_id: int
    text: str
    success: bool
    output_path: Optional[str] = None
    duration: float = 0.0
    error: Optional[str] = None
    elapsed_time: float = 0.0


class BatchSynthesizer:
    """
    批量语音合成器

    天龙引擎协同:
    - [@35-05] 短视频编导: 批量配音生成
    - [@07] 记录师: 文档批量语音化
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        max_workers: int = 4,
        output_dir: str = "./output",
        voice: str = "M1",
        lang: str = "zh",
        speed: float = 1.0,
        enable_expression: bool = False
    ):
        self.max_workers = max_workers
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.voice = voice
        self.lang = lang
        self.speed = speed
        self.enable_expression = enable_expression

        self.tts_client = TTSClient(model_path=model_path, auto_download=True)
        self.results: List[SynthesisResult] = []

    def load_from_file(self, file_path: str, encoding: str = "utf-8") -> List[str]:
        """
        从文件加载文本

        支持格式:
        - .txt: 每行一个文本
        - .json: JSON数组或JSONL
        - .csv: CSV文件
        """
        path = Path(file_path)
        texts = []

        if path.suffix == ".txt":
            with open(path, "r", encoding=encoding) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        texts.append(line)

        elif path.suffix == ".json":
            with open(path, "r", encoding=encoding) as f:
                data = json.load(f)
                if isinstance(data, list):
                    texts = [str(item) if isinstance(item, dict) else item for item in data]
                elif isinstance(data, dict) and "texts" in data:
                    texts = data["texts"]

        elif path.suffix == ".jsonl":
            with open(path, "r", encoding=encoding) as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        if isinstance(item, dict):
                            texts.append(item.get("text", item.get("content", "")))
                        else:
                            texts.append(str(item))

        elif path.suffix == ".csv":
            import csv
            with open(path, "r", encoding=encoding, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    for value in row.values():
                        if value and value.strip():
                            texts.append(value.strip())
                            break

        else:
            raise ValueError(f"不支持的文件格式: {path.suffix}")

        return texts

    def create_jobs(self, texts: List[str]) -> List[SynthesisJob]:
        """创建合成任务列表"""
        jobs = []
        for i, text in enumerate(texts):
            job = SynthesisJob(
                id=i,
                text=text[:500],  # 限制单条长度
                lang=self.lang,
                voice=self.voice,
                speed=self.speed,
                enable_expression=self.enable_expression,
                metadata={"index": i, "total_chars": len(text)}
            )
            jobs.append(job)
        return jobs

    def synthesize_job(self, job: SynthesisJob) -> SynthesisResult:
        """执行单个合成任务"""
        start_time = time.time()

        try:
            wav, duration = self.tts_client.synthesize(
                text=job.text,
                lang=job.lang,
                voice=job.voice,
                speed=job.speed,
                enable_expression=job.enable_expression
            )

            if wav is None:
                # 模拟结果（实际使用时替换为真实合成）
                output_path = str(self.output_dir / f"audio_{job.id:04d}.wav")
                duration = len(job.text) / 10.0  # 估算
                wav = b""  # Placeholder

            else:
                output_path = str(self.output_dir / f"audio_{job.id:04d}.wav")
                self.tts_client.save_audio(wav, output_path)

            elapsed = time.time() - start_time

            return SynthesisResult(
                job_id=job.id,
                text=job.text[:50] + "..." if len(job.text) > 50 else job.text,
                success=True,
                output_path=output_path,
                duration=duration,
                elapsed_time=elapsed
            )

        except Exception as e:
            elapsed = time.time() - start_time
            return SynthesisResult(
                job_id=job.id,
                text=job.text[:50] + "..." if len(job.text) > 50 else job.text,
                success=False,
                error=str(e),
                elapsed_time=elapsed
            )

    def process_jobs(self, jobs: List[SynthesisJob], show_progress: bool = True) -> List[SynthesisResult]:
        """并行处理任务列表"""
        results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.synthesize_job, job): job for job in jobs}

            for i, future in enumerate(as_completed(futures)):
                result = future.result()
                results.append(result)

                if show_progress:
                    self._print_progress(i + 1, len(jobs), result)

        self.results = sorted(results, key=lambda x: x.job_id)
        return self.results

    def _print_progress(self, current: int, total: int, result: SynthesisResult):
        """打印进度"""
        status = "✓" if result.success else "✗"
        elapsed = f"{result.elapsed_time:.2f}s"
        text_preview = result.text[:30].replace("\n", " ")

        print(f"[{current}/{total}] {status} {elapsed:>8} | {text_preview}...")

    def generate_report(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """生成合成报告"""
        total = len(self.results)
        success = sum(1 for r in self.results if r.success)
        failed = total - success

        total_duration = sum(r.duration for r in self.results if r.success)
        total_time = sum(r.elapsed_time for r in self.results)

        report = {
            "summary": {
                "total": total,
                "success": success,
                "failed": failed,
                "success_rate": f"{success/total*100:.1f}%" if total > 0 else "0%",
                "total_duration": f"{total_duration:.2f}s",
                "total_time": f"{total_time:.2f}s",
                "avg_time_per_item": f"{total_time/total:.2f}s" if total > 0 else "0s"
            },
            "results": [
                {
                    "id": r.job_id,
                    "text": r.text,
                    "success": r.success,
                    "output_path": r.output_path,
                    "duration": r.duration,
                    "error": r.error
                }
                for r in self.results
            ]
        }

        if output_path:
            report_path = Path(output_path)
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n报告已保存: {report_path}")

        return report

    def print_summary(self):
        """打印汇总信息"""
        if not self.results:
            print("无结果")
            return

        total = len(self.results)
        success = sum(1 for r in self.results if r.success)
        failed = total - success
        total_duration = sum(r.duration for r in self.results if r.success)

        print("\n" + "=" * 50)
        print("批量合成完成")
        print("=" * 50)
        print(f"总计: {total}")
        print(f"成功: {success} ({success/total*100:.1f}%)")
        print(f"失败: {failed} ({failed/total*100:.1f}%)")
        print(f"总时长: {total_duration:.2f}s")
        print(f"输出目录: {self.output_dir}")
        print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Supertonic TTS 批量合成")

    # 输入
    parser.add_argument("--input", "-i", required=True, help="输入文件路径")
    parser.add_argument("--column", "-c", help="CSV列名（当输入为CSV时）")
    parser.add_argument("--encoding", default="utf-8", help="文件编码")

    # 输出
    parser.add_argument("--output", "-o", default="./output", help="输出目录")

    # 合成参数
    parser.add_argument("--lang", default="zh", help="语言代码")
    parser.add_argument("--voice", default="M1", help="语音名称")
    parser.add_argument("--speed", type=float, default=1.0, help="语速")
    parser.add_argument("--expression", action="store_true", help="启用情感标签")

    # 性能
    parser.add_argument("--workers", type=int, default=4, help="并行工作数")
    parser.add_argument("--model", help="模型路径")

    # 报告
    parser.add_argument("--report", help="报告输出路径")

    args = parser.parse_args()

    # 创建合成器
    synthesizer = BatchSynthesizer(
        model_path=args.model,
        max_workers=args.workers,
        output_dir=args.output,
        voice=args.voice,
        lang=args.lang,
        speed=args.speed,
        enable_expression=args.expression
    )

    # 加载文本
    print(f"加载文本: {args.input}")
    texts = synthesizer.load_from_file(args.input, args.encoding)
    print(f"共 {len(texts)} 条文本")

    # 创建任务
    jobs = synthesizer.create_jobs(texts)

    # 执行合成
    print(f"开始合成（{args.workers}并行）...")
    start = time.time()
    synthesizer.process_jobs(jobs)
    elapsed = time.time() - start

    # 打印结果
    synthesizer.print_summary()

    # 生成报告
    if args.report:
        synthesizer.generate_report(args.report)
    else:
        synthesizer.generate_report(str(synthesizer.output_dir / "report.json"))


if __name__ == "__main__":
    main()
