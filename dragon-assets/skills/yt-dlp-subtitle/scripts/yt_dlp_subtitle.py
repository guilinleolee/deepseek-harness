#!/usr/bin/env python3
"""
yt-dlp-subtitle - 视频字幕下载封装
支持: YouTube, B站, Coursera 等 1000+ 平台
格式: srt, ass, vtt, lrc
"""

import yt_dlp
import argparse
import json
import sys
from pathlib import Path


def list_subs(url: str) -> dict:
    """列出可用字幕"""
    ydl_opts = {'quiet': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        subs = info.get('subtitles', {})
        auto_subs = info.get('automatic_captions', {})
        return {
            'title': info.get('title', 'Unknown'),
            'duration': info.get('duration', 0),
            'manual_subs': {k: list(v.keys()) if v else [] for k, v in subs.items()},
            'auto_subs': {k: list(v.keys()) if v else [] for k, v in auto_subs.items()},
        }


def download_subs(url: str, langs: str = 'en,zh', format: str = 'srt',
                   output_dir: str = '.', embed: bool = False) -> list:
    """下载字幕文件"""
    output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        'write_subs': True,
        'write_auto_subs': True,
        'sub_langs': langs,
        'skip_download': embed is False,  # embed时下载视频
        'outtmpl': str(output_path / '%(title)s.%(ext)s'),
    }

    if format != 'srt':  # 默认就是srt
        ydl_opts['convert_subs'] = format

    if embed:
        ydl_opts['embed_subs'] = True
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'

    downloaded_files = []

    def progress_hook(d):
        if d['status'] == 'finished':
            fname = d['filename']
            if fname.endswith(f'.{format}'):
                downloaded_files.append(fname)
            print(f"完成: {fname}")

    ydl_opts['progress_hooks'] = [progress_hook]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return downloaded_files


def get_subtitle_text(url: str, lang: str = 'en') -> str:
    """获取字幕文本内容（下载后读取）"""
    import tempfile
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        files = download_subs(url, lang, 'srt', tmpdir)
        if files:
            with open(files[0], 'r', encoding='utf-8') as f:
                return f.read()
    return ""


def main():
    parser = argparse.ArgumentParser(description='yt-dlp-subtitle 字幕下载工具')
    parser.add_argument('url', help='视频URL')
    parser.add_argument('--list', '-l', action='store_true',
                        help='列出可用字幕')
    parser.add_argument('--langs', '-L', default='en,zh',
                        help='字幕语言 (逗号分隔, 默认: en,zh)')
    parser.add_argument('--format', '-f', default='srt',
                        choices=['srt', 'vtt', 'ass', 'lrc'],
                        help='输出格式 (默认: srt)')
    parser.add_argument('--output', '-o', default='.',
                        help='输出目录 (默认: 当前目录)')
    parser.add_argument('--embed', '-e', action='store_true',
                        help='嵌入字幕到视频')
    parser.add_argument('--get-text', '-t', action='store_true',
                        help='输出字幕文本内容')

    args = parser.parse_args()

    if args.list:
        result = list_subs(args.url)
        print(f"视频: {result['title']}")
        print(f"时长: {result['duration']}秒")
        print("\n手动字幕:")
        for lang, formats in result['manual_subs'].items():
            print(f"  {lang}: {formats}")
        print("\n自动字幕:")
        for lang, formats in result['auto_subs'].items():
            print(f"  {lang}: {formats}")
    elif args.get_text:
        text = get_subtitle_text(args.url, args.langs.split(',')[0])
        print(text)
    else:
        print(f"下载字幕: {args.url}")
        print(f"语言: {args.langs}, 格式: {args.format}")
        files = download_subs(args.url, args.langs, args.format, args.output, args.embed)
        print(f"\n已下载 {len(files)} 个字幕文件:")
        for f in files:
            print(f"  {f}")


if __name__ == '__main__':
    main()
