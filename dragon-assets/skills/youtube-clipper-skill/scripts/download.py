#!/usr/bin/env python3
"""
YouTube Video Downloader
下载YouTube视频和字幕
"""

import sys
import os
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass
import yt_dlp


@dataclass
class DownloadResult:
    video_path: Optional[str]
    subtitle_path: Optional[str]
    video_title: str
    video_id: str
    duration: int


class VideoDownloader:
    def __init__(self, output_dir: str = "./youtube-clips"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download(self, url: str, max_height: int = 1080) -> DownloadResult:
        """
        下载视频和字幕

        Args:
            url: YouTube视频URL
            max_height: 最大视频高度(默认1080p)

        Returns:
            DownloadResult包含视频路径、字幕路径、标题等信息
        """
        video_path = None
        subtitle_path = None
        video_title = ""
        video_id = ""
        duration = 0

        ydl_opts = {
            'format': f'bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]',
            'outtmpl': str(self.output_dir / '%(id)s.%(ext)s'),
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'quiet': False,
            'no_warnings': False,
        }

        def progress_hook(d):
            if d['status'] == 'downloading':
                pct = d.get('_percent_str', 'N/A')
                print(f"\r  Downloading: {pct}", end='', flush=True)
            elif d['status'] == 'finished':
                print(f"\r  Download complete: {d['filename']}")

        ydl_opts['progress_hooks'] = [progress_hook]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    video_id = info.get('id', '')
                    video_title = info.get('title', '')
                    duration = info.get('duration', 0)

                    # 查找下载的文件
                    for ext in ['mp4', 'mkv', 'webm']:
                        potential_video = self.output_dir / f"{video_id}.{ext}"
                        if potential_video.exists():
                            video_path = str(potential_video)
                            break

                    # 查找字幕文件
                    potential_subtitle = self.output_dir / f"{video_id}.en.vtt"
                    if potential_subtitle.exists():
                        subtitle_path = str(potential_subtitle)

            print(f"\n✓ Download complete: {video_title}")

        except Exception as e:
            print(f"\n✗ Download failed: {e}")
            raise

        return DownloadResult(
            video_path=video_path,
            subtitle_path=subtitle_path,
            video_title=video_title,
            video_id=video_id,
            duration=duration
        )


def main():
    if len(sys.argv) < 2:
        print("Usage: python download.py <YouTube_URL> [output_dir]")
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./youtube-clips"

    print(f"Downloading: {url}")
    print(f"Output dir: {output_dir}")

    downloader = VideoDownloader(output_dir)
    result = downloader.download(url)

    print("\n" + "=" * 50)
    print("Download Result:")
    print(f"  Video ID: {result.video_id}")
    print(f"  Title: {result.video_title}")
    print(f"  Duration: {result.duration}s ({result.duration // 60}:{result.duration % 60:02d})")
    print(f"  Video: {result.video_path}")
    print(f"  Subtitle: {result.subtitle_path}")


if __name__ == "__main__":
    main()
