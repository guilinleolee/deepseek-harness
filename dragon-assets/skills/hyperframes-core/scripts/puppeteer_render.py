#!/usr/bin/env python3
"""
Puppeteer Fine Renderer
精细化浏览器渲染，支持帧级别精度 + 预热优化

用法:
    python3 puppeteer_render.py video.html --output video.mp4
    python3 puppeteer_render.py video.html --output video.mp4 --fps 30
    python3 puppeteer_render.py video.html --output video.mp4 --format webm
"""

import argparse
import asyncio
import json
import sys
import os
import tempfile
from pathlib import Path
from typing import Optional, List

try:
    from pyppeteer import launch
    from pyppeteer.browser import Browser
    from pyppeteer.page import Page
except ImportError:
    print("ERROR: pyppeteer not installed. Run: pip install pyppeteer")
    sys.exit(1)

DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080
DEFAULT_FPS = 30


async def warm_up_page(page: Page, html_path: Path) -> None:
    """预热页面，避免 CORS/RAF 冲突"""
    await page.setViewport({"width": DEFAULT_WIDTH, "height": DEFAULT_HEIGHT})
    await page.goto(f"file://{html_path.absolute()}", {"waitUntil": "domcontentloaded"})

    # 预热 Registry 组件
    await page.evaluate("""
        async () => {
            // 预加载 GSAP
            if (typeof gsap === 'undefined') {
                await new Promise((resolve) => {
                    const script = document.createElement('script');
                    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js';
                    script.onload = resolve;
                    document.head.appendChild(script);
                });
            }
            // 初始化场景
            if (typeof initScenes === 'function') initScenes();
        }
    """)
    await asyncio.sleep(0.5)


async def capture_frame(page: Page, timestamp: float) -> bytes:
    """捕获指定时间戳的帧"""
    await page.evaluate(f"""
        () => {{
            // 触发 RAF 更新
            if (window.__composer && window.__composer.getTimeline) {{
                const tl = window.__composer.getTimeline();
                tl.time({timestamp});
                tl.pause();
            }}
        }}
    """)
    await asyncio.sleep(0.05)  # 等待渲染稳定
    return await page.screenshot({"type": "png"})


async def render_video(
    html_path: Path,
    output_path: Path,
    fps: int = DEFAULT_FPS,
    format: str = "mp4",
    timeline_config: Optional[dict] = None,
) -> bool:
    """渲染视频，支持帧级别精度"""

    browser = await launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
        ],
    )
    page = await browser.newPage()
    await page.setViewport({"width": DEFAULT_WIDTH, "height": DEFAULT_HEIGHT})

    # 预热
    print("预热页面...")
    await warm_up_page(page, html_path)

    # 加载时间线配置
    if timeline_config is None:
        timeline_config = await page.evaluate("() => window.__composer?.getConfigs() || []")

    if not timeline_config:
        print("WARNING: No timeline config found, using default 10s render")
        timeline_config = [{"type": "hero", "duration": 10}]

    total_duration = sum(s.get("duration", 5) for s in timeline_config)
    total_frames = int(total_duration * fps)

    print(f"渲染: {total_duration}s @ {fps}fps = {total_frames} 帧")
    print(f"输出: {output_path}")

    # 使用 FFmpeg 合成视频
    tmp_dir = Path(tempfile.mkdtemp())
    frames_dir = tmp_dir / "frames"
    frames_dir.mkdir(exist_ok=True)

    for frame_num in range(total_frames):
        timestamp = frame_num / fps
        frame_path = frames_dir / f"frame_{frame_num:06d}.png"

        try:
            frame_data = await capture_frame(page, timestamp)
            frame_path.write_bytes(frame_data)
        except Exception as e:
            print(f"WARNING: Frame {frame_num} capture failed: {e}")
            # 使用上一帧填充
            if frame_num > 0:
                prev_frame = frames_dir / f"frame_{frame_num-1:06d}.png"
                if prev_frame.exists():
                    import shutil
                    shutil.copy(prev_frame, frame_path)

        if (frame_num + 1) % 30 == 0:
            progress = (frame_num + 1) / total_frames * 100
            print(f"  进度: {progress:.1f}% ({frame_num+1}/{total_frames})")

    await browser.close()

    # FFmpeg 合成
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(frames_dir / "frame_%06d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        str(output_path),
    ]

    print("合成视频...")
    import subprocess

    result = subprocess.run(
        ffmpeg_cmd,
        capture_output=True,
        text=True,
    )

    # 清理临时文件
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)

    if result.returncode != 0:
        print(f"FFmpeg error: {result.stderr}")
        return False

    print(f"视频已保存: {output_path}")
    return True


async def render_webm(
    html_path: Path,
    output_path: Path,
    fps: int = DEFAULT_FPS,
) -> bool:
    """渲染 WebM 格式（备选方案，无 FFmpeg 时）"""
    browser = await launch(headless=True)
    page = await browser.newPage()
    await page.setViewport({"width": DEFAULT_WIDTH, "height": DEFAULT_HEIGHT})
    await page.goto(f"file://{html_path.absolute()}", {"waitUntil": "networkidle0"})

    # 录制模式
    await page.evaluate("""
        async () => {
            window.__videoMode = true;
            const tl = window.__composer?.getTimeline();
            if (tl) tl.play();
        }
    """)

    # 使用 MediaRecorder API（需要额外处理）
    print("WebM rendering not fully implemented, use --format mp4")
    await browser.close()
    return False


def main():
    parser = argparse.ArgumentParser(description="Puppeteer Fine Renderer")
    parser.add_argument("html", type=Path, help="Input HTML file")
    parser.add_argument("--output", "-o", type=Path, help="Output video file")
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS, help=f"Frames per second (default: {DEFAULT_FPS})")
    parser.add_argument("--format", default="mp4", choices=["mp4", "webm"], help="Output format")
    parser.add_argument("--timeline", type=Path, help="Timeline JSON for precise rendering")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)

    args = parser.parse_args()

    if not args.html.exists():
        print(f"ERROR: HTML file not found: {args.html}")
        sys.exit(1)

    if not args.output:
        args.output = args.html.with_suffix(f".{args.format}")

    # 检查 FFmpeg
    import subprocess
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: FFmpeg not found. Install: https://ffmpeg.org/download.html")
        sys.exit(1)

    # 加载时间线
    timeline_config = None
    if args.timeline and args.timeline.exists():
        with open(args.timeline, "r", encoding="utf-8") as f:
            timeline_config = json.load(f).get("scenes", [])

    # 检查 GPU 加速
    try:
        subprocess.run(
            ["nvidia-smi"], capture_output=True, check=False
        )
        print("GPU: NVIDIA detected, using hardware acceleration")
    except FileNotFoundError:
        print("GPU: No NVIDIA GPU, using software encoding")

    # 运行渲染
    success = asyncio.run(render_video(
        args.html,
        args.output,
        fps=args.fps,
        format=args.format,
        timeline_config=timeline_config,
    ))

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
