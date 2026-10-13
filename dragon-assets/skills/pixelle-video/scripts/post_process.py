#!/usr/bin/env python3
"""
Pixelle-Video Post-Processing Tools
FFmpeg-based video editing and enhancement
"""

import os
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class VideoProcessor:
    """Video post-processing using FFmpeg"""

    def __init__(self, output_dir: str = None, ffmpeg_path: str = "ffmpeg"):
        self.output_dir = Path(output_dir) if output_dir else Path("./output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg = ffmpeg_path

    def _run_ffmpeg(self, args: List[str], input_file: str, output_file: str) -> bool:
        """Run FFmpeg command"""
        cmd = [self.ffmpeg, "-y", "-i", input_file] + args + [output_file]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e.stderr}")
            return False
        except FileNotFoundError:
            print("FFmpeg not found. Please install FFmpeg.")
            return False

    def trim(self, input_file: str, output_file: str,
             start: str = None, duration: str = None, end: str = None) -> bool:
        """Trim video to specified segment"""
        args = []
        if start:
            args.extend(["-ss", start])
        if duration:
            args.extend(["-t", duration])
        elif end:
            args.extend(["-to", end])
        args.extend(["-c", "copy"])
        return self._run_ffmpeg(args, input_file, output_file)

    def resize(self, input_file: str, output_file: str,
              width: int, height: int) -> bool:
        """Resize video to specified dimensions"""
        args = [
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease",
            "-c:a", "copy"
        ]
        return self._run_ffmpeg(args, input_file, output_file)

    def change_resolution(self, input_file: str, output_file: str,
                         resolution: str) -> bool:
        """Change video resolution (480p, 720p, 1080p)"""
        resolutions = {
            "480p": (854, 480),
            "720p": (1280, 720),
            "1080p": (1920, 1080)
        }
        if resolution not in resolutions:
            print(f"Unknown resolution: {resolution}")
            return False
        width, height = resolutions[resolution]
        return self.resize(input_file, output_file, width, height)

    def change_fps(self, input_file: str, output_file: str, fps: int) -> bool:
        """Change video frame rate"""
        args = ["-vf", f"fps={fps}", "-c:a", "copy"]
        return self._run_ffmpeg(args, input_file, output_file)

    def add_watermark(self, input_file: str, output_file: str,
                      watermark: str, position: str = "bottom-right") -> bool:
        """Add text watermark to video"""
        positions = {
            "top-left": "10:10",
            "top-right": "W-tw-10:10",
            "bottom-left": "10:H-th-10",
            "bottom-right": "W-tw-10:H-th-10",
            "center": "(W-tw)/2:(H-th)/2"
        }
        if position not in positions:
            position = "bottom-right"

        args = [
            "-vf", f"drawtext=text='{watermark}':fontsize=24:"
                   f"fontcolor=white:x={positions[position]}:shadowcolor=black:"
                   f"shadowx=2:shadowy=2"
        ]
        return self._run_ffmpeg(args, input_file, output_file)

    def change_aspect_ratio(self, input_file: str, output_file: str,
                           ratio: str) -> bool:
        """Change aspect ratio (9:16, 16:9, 1:1)"""
        args = []
        if ratio == "9:16":
            # Portrait (TikTok/Story format)
            args = ["-vf", "scale=1080:1920:force_original_aspect_ratio=increase"]
        elif ratio == "16:9":
            # Landscape (YouTube format)
            args = ["-vf", "scale=1920:1080:force_original_aspect_ratio=increase"]
        elif ratio == "1:1":
            # Square (Instagram format)
            args = ["-vf", "scale=1080:1080:force_original_aspect_ratio=increase"]
        else:
            print(f"Unknown ratio: {ratio}")
            return False

        args.extend(["-c:a", "copy"])
        return self._run_ffmpeg(args, input_file, output_file)

    def add_subtitles(self, input_file: str, output_file: str,
                      subtitle_file: str) -> bool:
        """Burn subtitles into video"""
        args = [
            "-vf", f"subtitles='{subtitle_file}'",
            "-c:a", "copy"
        ]
        return self._run_ffmpeg(args, input_file, output_file)

    def concat(self, input_files: List[str], output_file: str) -> bool:
        """Concatenate multiple videos"""
        # Create concat file
        concat_file = self.output_dir / "concat_list.txt"
        with open(concat_file, "w") as f:
            for file in input_files:
                f.write(f"file '{file}'\n")

        args = ["-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy"]
        success = self._run_ffmpeg(args, str(concat_file), output_file)

        # Cleanup
        concat_file.unlink(missing_ok=True)
        return success

    def speed_up(self, input_file: str, output_file: str, factor: float) -> bool:
        """Change video speed (1.5 = 1.5x faster, 0.5 = 2x slower)"""
        args = [
            "-filter:v", f"setpts={1/factor}*PTS",
            "-filter:a", f"atempo={factor}"
        ]
        return self._run_ffmpeg(args, input_file, output_file)

    def add_audio(self, input_file: str, audio_file: str,
                  output_file: str, audio_volume: float = 1.0) -> bool:
        """Replace or mix audio track"""
        args = [
            "-i", audio_file,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-filter:a", f"volume={audio_volume}"
        ]
        return self._run_ffmpeg(args, input_file, output_file)

    def get_info(self, input_file: str) -> Optional[Dict]:
        """Get video information using ffprobe"""
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", input_file
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except Exception as e:
            print(f"FFprobe error: {e}")
            return None

    def create_gif(self, input_file: str, output_file: str,
                   fps: int = 10, scale: int = 480) -> bool:
        """Create GIF from video"""
        # First create palette
        palette_file = self.output_dir / "palette.png"
        cmd1 = [
            self.ffmpeg, "-y", "-i", input_file,
            "-vf", f"fps={fps},scale={scale}:-1:flags=lanczos,palettegen",
            str(palette_file)
        ]
        try:
            subprocess.run(cmd1, capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Palette generation error: {e}")
            return False

        # Then create GIF
        cmd2 = [
            self.ffmpeg, "-y", "-i", input_file,
            "-i", str(palette_file),
            "-lavfi", f"fps={fps},scale={scale}:-1:flags=lanczos[x];[x][1:v]paletteuse",
            output_file
        ]
        try:
            subprocess.run(cmd2, capture_output=True, check=True)
            palette_file.unlink(missing_ok=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"GIF creation error: {e}")
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Pixelle-Video Post-Processing")
    parser.add_argument("--input", "-i", required=True, help="Input video file")
    parser.add_argument("--output", "-o", help="Output video file")
    parser.add_argument("--output-dir", "-d", help="Output directory")

    subparsers = parser.add_subparsers(dest="command", help="Processing command")

    # Trim command
    trim_parser = subparsers.add_parser("trim", help="Trim video")
    trim_parser.add_argument("--start", "-s", help="Start time (HH:MM:SS)")
    trim_parser.add_argument("--duration", "-t", help="Duration")
    trim_parser.add_argument("--end", "-e", help="End time")

    # Resize command
    resize_parser = subparsers.add_parser("resize", help="Resize video")
    resize_parser.add_argument("--width", "-w", type=int, help="Width")
    resize_parser.add_argument("--height", "-ht", type=int, help="Height")

    # Resolution command
    res_parser = subparsers.add_parser("resolution", help="Change resolution")
    res_parser.add_argument("--preset", "-p", choices=["480p", "720p", "1080p"])

    # FPS command
    fps_parser = subparsers.add_parser("fps", help="Change frame rate")
    fps_parser.add_argument("--rate", "-r", type=int, help="FPS")

    # Aspect ratio command
    ratio_parser = subparsers.add_parser("ratio", help="Change aspect ratio")
    ratio_parser.add_argument("--preset", "-p", choices=["9:16", "16:9", "1:1"])

    # Watermark command
    wm_parser = subparsers.add_parser("watermark", help="Add watermark")
    wm_parser.add_argument("--text", "-t", required=True, help="Watermark text")
    wm_parser.add_argument("--position", "-p",
                            choices=["top-left", "top-right", "bottom-left", "bottom-right"])

    # Concat command
    concat_parser = subparsers.add_parser("concat", help="Concatenate videos")
    concat_parser.add_argument("--files", "-f", nargs="+", required=True,
                               help="Input files to concatenate")

    # Speed command
    speed_parser = subparsers.add_parser("speed", help="Change speed")
    speed_parser.add_argument("--factor", "-f", type=float, required=True,
                              help="Speed factor (1.5 = faster)")

    # GIF command
    gif_parser = subparsers.add_parser("gif", help="Create GIF")
    gif_parser.add_argument("--fps", type=int, default=10, help="GIF FPS")
    gif_parser.add_argument("--scale", type=int, default=480, help="GIF scale")

    # Info command
    subparsers.add_parser("info", help="Get video info")

    args = parser.parse_args()

    if not args.output:
        input_name = Path(args.input).stem
        args.output = str(Path(args.output_dir or "./output") / f"{input_name}_processed.mp4")

    processor = VideoProcessor(args.output_dir)

    if args.command == "trim":
        processor.trim(args.input, args.output, args.start, args.duration, args.end)

    elif args.command == "resize":
        processor.resize(args.input, args.output, args.width, args.height)

    elif args.command == "resolution":
        processor.change_resolution(args.input, args.output, args.preset)

    elif args.command == "fps":
        processor.change_fps(args.input, args.output, args.rate)

    elif args.command == "ratio":
        processor.change_aspect_ratio(args.input, args.output, args.preset)

    elif args.command == "watermark":
        processor.add_watermark(args.input, args.output, args.text, args.position)

    elif args.command == "concat":
        processor.concat(args.files, args.output)

    elif args.command == "speed":
        processor.speed_up(args.input, args.output, args.factor)

    elif args.command == "gif":
        gif_output = args.output.replace(".mp4", ".gif")
        processor.create_gif(args.input, gif_output, args.fps, args.scale)

    elif args.command == "info":
        info = processor.get_info(args.input)
        if info:
            print(json.dumps(info, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
