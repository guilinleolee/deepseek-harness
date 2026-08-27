#!/usr/bin/env python3
"""
电子书下载脚本 - 从搜索结果下载书籍
支持：Z-Library下载、Libgen直链下载、NotebookLM上传
"""

import argparse
import json
import sys
import os
import subprocess
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# 默认下载目录
DEFAULT_DOWNLOAD_DIR = Path.home() / "Downloads" / "ebooks"

# zlibrary-to-notebooklm 路径
ZLIB_SKILL_PATH = Path.home() / ".claude" / "skills" / "zlibrary-to-notebooklm"


def download_from_libgen(url: str, output_dir: Path) -> Optional[Path]:
    """从 Libgen 直链下载"""
    import requests

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        # 从 URL 或 headers 获取文件名
        filename = None
        if "Content-Disposition" in response.headers:
            import re
            match = re.search(r'filename="?([^"]+)"?', response.headers["Content-Disposition"])
            if match:
                filename = match.group(1)

        if not filename:
            filename = urlparse(url).path.split("/")[-1] or "download.pdf"

        output_path = output_dir / filename

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        progress = (downloaded / total_size) * 100
                        print(f"\r📥 下载中: {progress:.1f}%", end="", flush=True)

        print(f"\n✅ 下载完成: {output_path}")
        return output_path

    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        return None


def download_from_zlibrary(url: str) -> Optional[Path]:
    """使用 zlibrary-to-notebooklm 下载"""
    upload_script = ZLIB_SKILL_PATH / "scripts" / "upload.py"

    if not upload_script.exists():
        print(f"❌ 未找到 zlibrary-to-notebooklm 技能")
        return None

    try:
        result = subprocess.run(
            [sys.executable, str(upload_script), url],
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            print("✅ Z-Library 下载成功")
            # 尝试从输出中提取文件路径
            for line in result.stdout.split("\n"):
                if "下载到" in line or "Downloaded to" in line:
                    # 提取路径
                    parts = line.split(":")
                    if len(parts) > 1:
                        return Path(parts[1].strip())
            return True
        else:
            print(f"❌ Z-Library 下载失败: {result.stderr}")
            return None

    except Exception as e:
        print(f"❌ 下载错误: {e}")
        return None


def upload_to_notebooklm(file_path: Path, title: str) -> Optional[str]:
    """上传到 NotebookLM"""
    try:
        # 检查 notebooklm CLI 是否可用
        result = subprocess.run(
            ["notebooklm", "create", title],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print("⚠️ NotebookLM CLI 不可用，跳过上传")
            return None

        # 提取 notebook ID
        notebook_id = None
        for line in result.stdout.split("\n"):
            if "ID:" in line or "notebook" in line.lower():
                parts = line.split()
                for part in parts:
                    if "-" in part and len(part) > 20:
                        notebook_id = part
                        break

        if not notebook_id:
            return None

        # 上传文件
        subprocess.run(
            ["notebooklm", "source", "add", str(file_path)],
            capture_output=True,
            text=True,
            timeout=120
        )

        print(f"📤 已上传到 NotebookLM: {notebook_id}")
        return notebook_id

    except FileNotFoundError:
        print("⚠️ NotebookLM CLI 未安装，跳过上传")
        return None
    except Exception as e:
        print(f"⚠️ 上传 NotebookLM 失败: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="电子书下载工具"
    )
    parser.add_argument("--url", "-u", help="下载链接")
    parser.add_argument("--index", "-i", type=int, help="从搜索结果JSON中选择（索引从1开始）")
    parser.add_argument("--input", "-f", help="搜索结果JSON文件")
    parser.add_argument("--output", "-o", default=str(DEFAULT_DOWNLOAD_DIR),
                       help="下载目录")
    parser.add_argument("--notebooklm", "-n", action="store_true",
                       help="下载后上传到 NotebookLM")
    parser.add_argument("--title", "-t", help="书籍标题（用于NotebookLM）")

    args = parser.parse_args()

    output_dir = Path(args.output)

    # 从 JSON 文件读取搜索结果
    if args.input and args.index:
        with open(args.input, 'r', encoding='utf-8') as f:
            results = json.load(f)

        if args.index < 1 or args.index > len(results):
            print(f"❌ 索引超出范围 (1-{len(results)})")
            return 1

        selected = results[args.index - 1]
        url = selected.get('download_url')
        title = selected.get('title', args.title or 'Unknown')
        source = selected.get('source', '')

        if not url:
            print("❌ 该结果没有可用的下载链接")
            return 1

        print(f"📥 准备下载: {title}")
        print(f"   来源: {source}")

    elif args.url:
        url = args.url
        title = args.title or 'Unknown'
        source = 'Z-Library' if 'zlib' in url else 'Libgen'
    else:
        print("❌ 请提供 --url 或 --input/--index")
        return 1

    # 下载
    file_path = None
    if 'libgen' in source.lower() or source == 'Libgen(.bz)':
        file_path = download_from_libgen(url, output_dir)
    else:
        file_path = download_from_zlibrary(url)

    # 上传到 NotebookLM
    if file_path and args.notebooklm:
        if isinstance(file_path, Path):
            upload_to_notebooklm(file_path, title)
        elif file_path is True:
            # zlibrary-to-notebooklm 可能已经上传了
            print("✅ 下载完成（可能已自动上传到 NotebookLM）")

    return 0


if __name__ == "__main__":
    sys.exit(main())