#!/usr/bin/env python3
"""
YouTube Video Clipper - Main Entry Script
YouTube视频剪辑主入口：下载 → 章节分析 → 字幕翻译 → 社媒生成

Usage:
    python clipper.py <command> [args...]

Commands:
    full     - 完整工作流: URL → 下载 → 章节 → 剪辑 → 发布
    download - 下载视频和字幕
    analyze  - 分析章节
    translate - 翻译字幕
    social   - 生成社媒内容
    clip     - 剪辑视频片段
    burn     - 烧录字幕到视频
"""

import sys
import os
import json
import argparse
from pathlib import Path
from dataclasses import asdict
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from download import VideoDownloader, DownloadResult
from chapter_analyzer import parse_vtt, generate_chapters, Chapter
from subtitle_translator import BatchTranslator
from social_media_generator import SocialMediaGenerator
from video_processor import VideoProcessor


class YouTubeClipper:
    """
    YouTube视频剪辑完整工作流

    流程:
    1. 下载视频和字幕
    2. AI语义章节分析
    3. 批量字幕翻译(95% API节省)
    4. 视频片段剪辑
    5. 字幕烧录
    6. 社媒内容生成
    """

    def __init__(
        self,
        output_dir: str = "./youtube-clips",
        api_key: Optional[str] = None
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")

        self.downloader = VideoDownloader(str(self.output_dir))
        self.translator = BatchTranslator(api_key=self.api_key)
        self.social_gen = SocialMediaGenerator()
        self.processor = VideoProcessor(output_dir=str(self.output_dir))

    def full_workflow(
        self,
        url: str,
        platforms: list[str] = None,
        max_height: int = 1080,
        min_chapter_duration: int = 180,
        max_chapter_duration: int = 300,
        translate_subtitles: bool = False,
        target_lang: str = "zh-CN"
    ) -> dict:
        """
        完整工作流: URL → 下载 → 章节 → 剪辑 → 发布

        Args:
            url: YouTube视频URL
            platforms: 社媒平台列表
            max_height: 最大视频高度
            min_chapter_duration: 最小章节时长(秒)
            max_chapter_duration: 最大章节时长(秒)
            translate_subtitles: 是否翻译字幕
            target_lang: 目标语言

        Returns:
            工作流结果字典
        """
        results = {
            "url": url,
            "steps": [],
            "chapters": [],
            "clips": [],
            "social_content": {},
            "errors": []
        }

        # Step 1: Download
        print("\n" + "=" * 60)
        print("Step 1: Downloading video and subtitles...")
        print("=" * 60)
        try:
            dl_result = self.downloader.download(url, max_height)
            results["steps"].append({
                "name": "download",
                "status": "success",
                "data": asdict(dl_result)
            })
            results["download"] = asdict(dl_result)
            print(f"  Video: {dl_result.video_path}")
            print(f"  Subtitle: {dl_result.subtitle_path}")
        except Exception as e:
            results["steps"].append({
                "name": "download",
                "status": "error",
                "error": str(e)
            })
            results["errors"].append(f"Download failed: {e}")
            print(f"  Error: {e}")
            return results

        # Step 2: Analyze chapters
        print("\n" + "=" * 60)
        print("Step 2: AI Semantic Chapter Analysis...")
        print("=" * 60)
        if dl_result.subtitle_path:
            try:
                subtitles = parse_vtt(dl_result.subtitle_path)
                chapters = generate_chapters(
                    subtitles,
                    min_chapter_duration,
                    max_chapter_duration,
                    self.api_key
                )
                chapters_data = []
                for ch in chapters:
                    chapters_data.append({
                        "title": ch.title,
                        "start": ch.start,
                        "end": ch.end,
                        "summary": ch.summary,
                        "keywords": ch.keywords
                    })
                results["chapters"] = chapters_data
                results["steps"].append({
                    "name": "analyze",
                    "status": "success",
                    "chapter_count": len(chapters)
                })
                print(f"  Generated {len(chapters)} chapters:")
                for i, ch in enumerate(chapters, 1):
                    duration = ch.end_seconds - ch.start_seconds
                    print(f"    [{i}] {ch.title} ({ch.start} - {ch.end}, {duration}s)")
            except Exception as e:
                results["steps"].append({
                    "name": "analyze",
                    "status": "error",
                    "error": str(e)
                })
                results["errors"].append(f"Chapter analysis failed: {e}")
                print(f"  Error: {e}")
                chapters = []
        else:
            results["steps"].append({
                "name": "analyze",
                "status": "skipped",
                "reason": "No subtitle file"
            })
            print("  Skipped: No subtitle file")
            chapters = []

        # Step 3: Translate subtitles
        if translate_subtitles and dl_result.subtitle_path:
            print("\n" + "=" * 60)
            print(f"Step 3: Translating subtitles to {target_lang}...")
            print("=" * 60)
            try:
                bilingual_path = self.translator.translate_file(
                    dl_result.subtitle_path,
                    target_lang
                )
                results["steps"].append({
                    "name": "translate",
                    "status": "success",
                    "output": bilingual_path
                })
                print(f"  Bilingual subtitle: {bilingual_path}")
            except Exception as e:
                results["steps"].append({
                    "name": "translate",
                    "status": "error",
                    "error": str(e)
                })
                results["errors"].append(f"Translation failed: {e}")
                print(f"  Error: {e}")

        # Step 4-5: Generate social content
        if platforms and chapters:
            print("\n" + "=" * 60)
            print(f"Step 4: Generating social media content for {platforms}...")
            print("=" * 60)
            try:
                social_contents = {}
                for chapter in chapters:
                    ch_obj = Chapter(
                        title=chapter.title,
                        start=chapter.start,
                        end=chapter.end,
                        summary=chapter.summary,
                        keywords=chapter.keywords
                    )
                    content = self.social_gen.generate(
                        ch_obj,
                        platforms,
                        self.api_key
                    )
                    social_contents[chapter.title] = {
                        "xiaohongshu": content["xiaohongshu"],
                        "douyin": content["douyin"],
                        "wechat": content["wechat"]
                    }
                results["social_content"] = social_contents
                results["steps"].append({
                    "name": "social",
                    "status": "success",
                    "platforms": platforms
                })
                print(f"  Generated content for {len(chapters)} chapters")
            except Exception as e:
                results["steps"].append({
                    "name": "social",
                    "status": "error",
                    "error": str(e)
                })
                results["errors"].append(f"Social content generation failed: {e}")
                print(f"  Error: {e}")

        # Step 6: Clip video with subtitles
        if chapters and dl_result.video_path:
            print("\n" + "=" * 60)
            print("Step 5: Clipping video with subtitles...")
            print("=" * 60)
            subtitle_file = results.get("download", {}).get("subtitle_path")
            if subtitle_file and os.path.exists(subtitle_file):
                try:
                    # Clip first chapter
                    first_chapter = chapters[0]
                    clip_name = f"clip_{first_chapter.start.replace(':', '')}.mp4"
                    clip_result = self.processor.clip_video(
                        dl_result.video_path,
                        first_chapter.start,
                        first_chapter.end,
                        clip_name
                    )
                    if clip_result.success:
                        # Burn subtitles
                        burned_name = clip_name.replace(".mp4", "_with_subs.mp4")
                        burn_result = self.processor.burn_subtitles(
                            clip_result.output_path,
                            subtitle_file,
                            burned_name
                        )
                        if burn_result.success:
                            results["clips"].append({
                                "chapter": first_chapter.title,
                                "path": burn_result.output_path
                            })
                            print(f"  Clip + Subtitles: {burn_result.output_path}")
                        else:
                            results["clips"].append({
                                "chapter": first_chapter.title,
                                "path": clip_result.output_path,
                                "burn_status": "failed"
                            })
                            print(f"  Clip only: {clip_result.output_path}")
                    else:
                        print(f"  Clip failed: {clip_result.message}")
                except Exception as e:
                    results["errors"].append(f"Video processing failed: {e}")
                    print(f"  Error: {e}")

        # Summary
        print("\n" + "=" * 60)
        print("Workflow Summary")
        print("=" * 60)
        print(f"Video: {results['download'].get('video_title', 'N/A')}")
        print(f"Duration: {results['download'].get('duration', 0)}s")
        print(f"Chapters: {len(results['chapters'])}")
        print(f"Clips: {len(results['clips'])}")
        print(f"Errors: {len(results['errors'])}")
        if results['errors']:
            for err in results['errors']:
                print(f"  - {err}")

        return results


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Video Clipper - AI-powered video clipping tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full workflow
  python clipper.py full "https://youtube.com/watch?v=xxx"

  # Download only
  python clipper.py download "https://youtube.com/watch?v=xxx"

  # Analyze chapters
  python clipper.py analyze ./subtitle.vtt

  # Translate subtitles
  python clipper.py translate ./subtitle.vtt zh-CN

  # Generate social content
  python clipper.py social "Chapter Title" "Chapter summary" "keyword1,keyword2"

  # Clip video
  python clipper.py clip video.mp4 00:01:00 00:05:00

  # Burn subtitles
  python clipper.py burn video.mp4 subtitle.srt
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Full workflow command
    full_parser = subparsers.add_parser("full", help="Run full workflow")
    full_parser.add_argument("url", help="YouTube video URL")
    full_parser.add_argument("--platforms", "-p", nargs="+",
                            choices=["xiaohongshu", "douyin", "wechat"],
                            default=["xiaohongshu", "douyin", "wechat"],
                            help="Social media platforms")
    full_parser.add_argument("--max-height", "-m", type=int, default=1080,
                            help="Max video height (default: 1080)")
    full_parser.add_argument("--min-duration", type=int, default=180,
                            help="Min chapter duration in seconds (default: 180)")
    full_parser.add_argument("--max-duration", type=int, default=300,
                            help="Max chapter duration in seconds (default: 300)")
    full_parser.add_argument("--translate", action="store_true",
                            help="Translate subtitles")
    full_parser.add_argument("--target-lang", default="zh-CN",
                            help="Target language for translation (default: zh-CN)")
    full_parser.add_argument("--output", "-o", default="./youtube-clips",
                            help="Output directory")
    full_parser.add_argument("--api-key", help="OpenAI API key (or set OPENAI_API_KEY)")

    # Download command
    dl_parser = subparsers.add_parser("download", help="Download video and subtitles")
    dl_parser.add_argument("url", help="YouTube video URL")
    dl_parser.add_argument("--output", "-o", default="./youtube-clips",
                          help="Output directory")
    dl_parser.add_argument("--max-height", "-m", type=int, default=1080,
                          help="Max video height")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze video chapters")
    analyze_parser.add_argument("subtitle", help="Subtitle file (.vtt or .srt)")
    analyze_parser.add_argument("--min-duration", type=int, default=180,
                              help="Min chapter duration (seconds)")
    analyze_parser.add_argument("--max-duration", type=int, default=300,
                              help="Max chapter duration (seconds)")
    analyze_parser.add_argument("--api-key", help="OpenAI API key")

    # Translate command
    trans_parser = subparsers.add_parser("translate", help="Translate subtitles")
    trans_parser.add_argument("subtitle", help="Subtitle file (.srt)")
    trans_parser.add_argument("target_lang", nargs="?", default="zh-CN",
                             help="Target language (default: zh-CN)")
    trans_parser.add_argument("--api-key", help="OpenAI API key")

    # Social content command
    social_parser = subparsers.add_parser("social", help="Generate social media content")
    social_parser.add_argument("title", help="Chapter title")
    social_parser.add_argument("summary", help="Chapter summary")
    social_parser.add_argument("keywords", help="Keywords (comma-separated)")
    social_parser.add_argument("--platforms", "-p", nargs="+",
                             choices=["xiaohongshu", "douyin", "wechat"],
                             default=["xiaohongshu", "douyin", "wechat"],
                             help="Platforms to generate for")
    social_parser.add_argument("--api-key", help="OpenAI API key")

    # Clip command
    clip_parser = subparsers.add_parser("clip", help="Clip video segment")
    clip_parser.add_argument("video", help="Video file path")
    clip_parser.add_argument("start", help="Start time (HH:MM:SS)")
    clip_parser.add_argument("end", help="End time (HH:MM:SS)")
    clip_parser.add_argument("--output", "-o", help="Output filename")

    # Burn command
    burn_parser = subparsers.add_parser("burn", help="Burn subtitles into video")
    burn_parser.add_argument("video", help="Video file path")
    burn_parser.add_argument("subtitle", help="Subtitle file (.srt)")
    burn_parser.add_argument("--output", "-o", help="Output filename")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    if args.command == "full":
        clipper = YouTubeClipper(
            output_dir=args.output,
            api_key=args.api_key
        )
        results = clipper.full_workflow(
            url=args.url,
            platforms=args.platforms,
            max_height=args.max_height,
            min_chapter_duration=args.min_duration,
            max_chapter_duration=args.max_duration,
            translate_subtitles=args.translate,
            target_lang=args.target_lang
        )
        # Save results
        output_file = Path(args.output) / "workflow_results.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nResults saved to: {output_file}")

    elif args.command == "download":
        downloader = VideoDownloader(args.output)
        result = downloader.download(args.url, args.max_height)
        print("\n" + "=" * 50)
        print("Download Result:")
        print(f"  Video ID: {result.video_id}")
        print(f"  Title: {result.video_title}")
        print(f"  Duration: {result.duration}s")
        print(f"  Video: {result.video_path}")
        print(f"  Subtitle: {result.subtitle_path}")

    elif args.command == "analyze":
        api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
        subtitles = parse_vtt(args.subtitle)
        chapters = generate_chapters(
            subtitles,
            args.min_duration,
            args.max_duration,
            api_key
        )
        print("\n" + "=" * 50)
        print(f"Generated {len(chapters)} chapters:\n")
        for i, ch in enumerate(chapters, 1):
            duration = ch.end_seconds - ch.start_seconds
            print(f"[{i}] {ch.title}")
            print(f"    {ch.start} - {ch.end} ({duration}s)")
            print(f"    Summary: {ch.summary}")
            print(f"    Keywords: {', '.join(ch.keywords)}")
            print()

    elif args.command == "translate":
        api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
        translator = BatchTranslator(api_key=api_key)
        output_path = translator.translate_file(args.subtitle, args.target_lang)
        print(f"\nBilingual subtitle saved to: {output_path}")

    elif args.command == "social":
        api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
        keywords = [k.strip() for k in args.keywords.split(",")]
        chapter = Chapter(
            title=args.title,
            start="00:00:00",
            end="00:05:00",
            summary=args.summary,
            keywords=keywords
        )
        generator = SocialMediaGenerator()
        content = generator.generate(chapter, args.platforms, api_key)

        print("\n" + "=" * 50)
        print("Social Media Content:")
        print("=" * 50)

        if "xiaohongshu" in args.platforms:
            print("\n小红书:")
            print("-" * 50)
            print(content["xiaohongshu"])

        if "douyin" in args.platforms:
            print("\n抖音:")
            print("-" * 50)
            print(content["douyin"])

        if "wechat" in args.platforms:
            print("\n公众号:")
            print("-" * 50)
            print(content["wechat"])

    elif args.command == "clip":
        processor = VideoProcessor()
        output = args.output or "clip.mp4"
        result = processor.clip_video(args.video, args.start, args.end, output)
        print(f"\n{'✓' if result.success else '✗'} {result.message}")
        if result.success:
            print(f"Output: {result.output_path}")

    elif args.command == "burn":
        processor = VideoProcessor()
        output = args.output or "with_subtitles.mp4"
        result = processor.burn_subtitles(args.video, args.subtitle, output)
        print(f"\n{'✓' if result.success else '✗'} {result.message}")
        if result.success:
            print(f"Output: {result.output_path}")


if __name__ == "__main__":
    main()
