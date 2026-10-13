#!/usr/bin/env python3
"""
YouTube Clipper Environment Check
检查所有依赖是否正确安装
"""

import sys
import shutil
import subprocess
from pathlib import Path


def check_python():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"[FAIL] Python {version.major}.{version.minor} < 3.8")
        return False
    print(f"[PASS] Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_command(cmd: str) -> tuple[bool, str]:
    """检查命令是否存在"""
    path = shutil.which(cmd)
    if path:
        return True, path
    return False, ""


def check_ffmpeg_libass():
    """检查FFmpeg是否支持libass(字幕烧录)"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-filters"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if "subtitles" in result.stdout.lower():
            return True, "FFmpeg supports subtitles filter (libass)"
        return False, "FFmpeg missing libass support"
    except Exception as e:
        return False, f"FFmpeg check failed: {e}"


def check_python_packages():
    """检查Python包"""
    packages = ["yt_dlp", "pysrt", "openai"]
    results = {}
    for pkg in packages:
        try:
            if pkg == "yt_dlp":
                import yt_dlp
                results[pkg] = True, yt_dlp.version.__version__
            elif pkg == "pysrt":
                import pysrt
                results[pkg] = True, pysrt.__version__
            elif pkg == "openai":
                import openai
                results[pkg] = True, openai.__version__
        except ImportError:
            results[pkg] = False, "not installed"
        except AttributeError:
            results[pkg] = True, "installed"

    return results


def main():
    print("=" * 50)
    print("YouTube Clipper Environment Check")
    print("=" * 50)

    all_pass = True

    # Python版本
    print("\n[1/4] Python Version:")
    if not check_python():
        all_pass = False

    # FFmpeg
    print("\n[2/4] FFmpeg:")
    ffmpeg_ok, ffmpeg_path = check_command("ffmpeg")
    if ffmpeg_ok:
        print(f"[PASS] FFmpeg found: {ffmpeg_path}")
        # 检查libass
        libass_ok, libass_msg = check_ffmpeg_libass()
        if libass_ok:
            print(f"[PASS] {libass_msg}")
        else:
            print(f"[FAIL] {libass_msg}")
            print("  → Install ffmpeg-full: brew install ffmpeg-full (macOS)")
            all_pass = False
    else:
        print("[FAIL] FFmpeg not found")
        print("  → Install: brew install ffmpeg (or ffmpeg-full for subtitles)")
        all_pass = False

    # yt-dlp
    print("\n[3/4] yt-dlp:")
    ytdlp_ok, ytdlp_path = check_command("yt-dlp")
    if ytdlp_ok:
        print(f"[PASS] yt-dlp found: {ytdlp_path}")
    else:
        print("[FAIL] yt-dlp not found")
        print("  → Install: pip install yt-dlp")
        all_pass = False

    # Python packages
    print("\n[4/4] Python Packages:")
    pkg_results = check_python_packages()
    for pkg, (ok, version) in pkg_results.items():
        if ok:
            print(f"[PASS] {pkg}: {version}")
        else:
            print(f"[FAIL] {pkg}: {version}")
            print(f"  → Install: pip install {pkg.replace('_', '-')}")
            all_pass = False

    # Summary
    print("\n" + "=" * 50)
    if all_pass:
        print("✓ All checks passed! YouTube Clipper is ready.")
        return 0
    else:
        print("✗ Some checks failed. Please install missing dependencies.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
