#!/usr/bin/env python3
"""
gbrain-multimodal-ingest: Main Processor
多模态摄入主处理器 - 协调视频/音频/会议摄入全流程
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional, Literal

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# 媒体类型检测
MEDIA_EXTENSIONS = {
    'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'],
    'audio': ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.wma'],
}


class MultimodalProcessor:
    """多模态摄入处理器"""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.language = self.config.get('language', 'auto')
        self.model = self.config.get('model', 'whisper-1')
        self.enable_speaker_diarization = self.config.get('enable_speaker_diarization', True)
        self.auto_summary = self.config.get('auto_summary', True)
        self.extract_keywords = self.config.get('extract_keywords', True)

    def detect_media_type(self, file_path: str) -> Literal['video', 'audio', 'unknown']:
        """检测媒体类型"""
        ext = Path(file_path).suffix.lower()
        if ext in MEDIA_EXTENSIONS['video']:
            return 'video'
        elif ext in MEDIA_EXTENSIONS['audio']:
            return 'audio'
        return 'unknown'

    def process(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        media_type: Optional[str] = None,
    ) -> dict:
        """
        处理多媒体文件

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径（可选）
            media_type: 媒体类型指定（可选，自动检测）

        Returns:
            处理结果字典
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")

        # 自动检测媒体类型
        if media_type is None:
            media_type = self.detect_media_type(str(input_path))

        logger.info(f"Processing {media_type}: {input_path}")

        # 根据类型选择处理器
        if media_type == 'video':
            result = self._process_video(input_path)
        elif media_type == 'audio':
            result = self._process_audio(input_path)
        else:
            raise ValueError(f"Unsupported media type or unknown file: {input_path}")

        # 后处理
        if self.auto_summary:
            result = self._add_summary(result)

        if self.extract_keywords:
            result = self._add_keywords(result)

        # 保存结果
        if output_path:
            self._save_result(result, output_path)

        return result

    def _process_video(self, video_path: Path) -> dict:
        """处理视频文件"""
        from video_transcriber import transcribe_video

        result = transcribe_video(
            video_path=str(video_path),
            language=self.language,
            model=self.model,
            enable_speaker_diarization=self.enable_speaker_diarization,
        )
        result['media_type'] = 'video'
        return result

    def _process_audio(self, audio_path: Path) -> dict:
        """处理音频文件"""
        from audio_transcriber import transcribe_audio

        result = transcribe_audio(
            audio_path=str(audio_path),
            language=self.language,
            model=self.model,
            enable_speaker_diarization=self.enable_speaker_diarization,
        )
        result['media_type'] = 'audio'
        return result

    def _add_summary(self, result: dict) -> dict:
        """添加摘要（TODO: 实现LLM摘要生成）"""
        # TODO: 调用LLM生成摘要
        # 可以使用 prompts/summarizer.md 中的提示词
        logger.debug("Summary generation not yet implemented")
        return result

    def _add_keywords(self, result: dict) -> dict:
        """添加关键词提取（TODO: 实现关键词提取）"""
        # TODO: 实现关键词提取
        logger.debug("Keyword extraction not yet implemented")
        return result

    def _save_result(self, result: dict, output_path: str):
        """保存结果到文件"""
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        with open(output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"Result saved to: {output_path}")

    def batch_process(
        self,
        input_dir: str,
        output_dir: str,
        media_type: Optional[str] = None,
    ) -> dict:
        """
        批量处理目录中的多媒体文件

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            media_type: 媒体类型过滤（可选）

        Returns:
            批量处理结果汇总
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if not input_path.is_dir():
            raise ValueError(f"Input path is not a directory: {input_dir}")

        results = []
        errors = []

        # 遍历目录中的文件
        for file_path in input_path.iterdir():
            if not file_path.is_file():
                continue

            detected_type = self.detect_media_type(str(file_path))
            if detected_type == 'unknown':
                continue

            if media_type and detected_type != media_type:
                continue

            try:
                result = self.process(
                    input_path=str(file_path),
                    output_path=str(output_path / f"{file_path.stem}.json"),
                )
                results.append({
                    'file': str(file_path),
                    'status': 'success',
                    'result': result,
                })
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                errors.append({
                    'file': str(file_path),
                    'error': str(e),
                })

        summary = {
            'total': len(results) + len(errors),
            'success': len(results),
            'errors': len(errors),
            'results': results,
            'errors_detail': errors,
        }

        logger.info(f"Batch processing completed: {len(results)} success, {len(errors)} errors")
        return summary


def main():
    parser = argparse.ArgumentParser(description='Multimodal Ingest Processor')
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('--output', '-o', help='Output file or directory')
    parser.add_argument('--type', '-t', choices=['video', 'audio'],
                        help='Media type (auto-detect if not specified)')
    parser.add_argument('--language', '-l', default='auto', help='Language code')
    parser.add_argument('--model', '-m', default='whisper-1', help='Whisper model')
    parser.add_argument('--no-speaker', action='store_true', help='Disable speaker diarization')
    parser.add_argument('--batch', action='store_true', help='Batch process directory')
    parser.add_argument('--no-summary', action='store_true', help='Disable auto summary')
    parser.add_argument('--no-keywords', action='store_true', help='Disable keyword extraction')

    args = parser.parse_args()

    # 构建配置
    config = {
        'language': args.language,
        'model': args.model,
        'enable_speaker_diarization': not args.no_speaker,
        'auto_summary': not args.no_summary,
        'extract_keywords': not args.no_keywords,
    }

    processor = MultimodalProcessor(config)

    try:
        if args.batch:
            # 批量处理
            if not args.output:
                raise ValueError("Output directory required for batch processing")
            result = processor.batch_process(
                input_dir=args.input,
                output_dir=args.output,
                media_type=args.type,
            )
        else:
            # 单文件处理
            result = processor.process(
                input_path=args.input,
                output_path=args.output,
                media_type=args.type,
            )

        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
