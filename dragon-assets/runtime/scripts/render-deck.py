#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render-deck.py · 零 AGPL 图文卡片渲染器
========================================================

把 xhs-visual-director（MIT）产出的页面方案渲染成可发布 PNG。

用系统 headless Chrome 截图，不依赖 Playwright npm 包：
    python render-deck.py --input deck.html --out out/ --sizes 1080x1440
    python render-deck.py --input deck.html --out out/ --preset xhs

多尺寸一次渲染，同一份 HTML 出 3:4 / 21:9 / 1:1 三种比例。

设计约束：
- 只用 Python 标准库 + 系统 Chrome。
- Chrome 路径可由 --chrome 覆盖，也读 CHROME_PATH 环境变量。
- 找不到 Chrome 时退出码 4，与 async-task-pattern 的"未实现"语义一致。

授权：自研，随仓库分发。
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

EXIT_OK = 0
EXIT_BAD_INPUT = 2
EXIT_NO_CHROME = 4

# 常见 Chrome / Chromium 安装位置（Windows 优先，其次 macOS / Linux）
CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Chromium\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]

# 常用版式比例：宽 x 高
SIZE_PRESETS = {
    "xhs": [(1080, 1440)],              # 小红书 3:4
    "xhs-wide": [(1080, 1440), (1080, 1440)],
    "wechat": [(900, 383), (900, 900)],  # 公众号 21:9 + 1:1
    "square": [(1080, 1080)],
    "story": [(1080, 1920)],             # 视频号 / 抖音 9:16
    "all": [(1080, 1440), (900, 383), (900, 900), (1080, 1080)],
}


def find_chrome(explicit: str | None = None) -> str | None:
    """Locate a Chrome/Chromium binary."""
    if explicit:
        return explicit if Path(explicit).exists() else None
    env_path = os.environ.get("CHROME_PATH")
    if env_path and Path(env_path).exists():
        return env_path
    for candidate in CHROME_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    for name in ("google-chrome", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    return None


def parse_sizes(spec: str) -> List[Tuple[int, int]]:
    """Parse "1080x1440,900x900" into size pairs."""
    sizes: List[Tuple[int, int]] = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "x" not in chunk:
            raise ValueError(f"bad size {chunk!r}; expected WIDTHxHEIGHT")
        width_text, _, height_text = chunk.partition("x")
        try:
            width, height = int(width_text), int(height_text)
        except ValueError as error:
            raise ValueError(f"bad size {chunk!r}: {error}") from error
        if width <= 0 or height <= 0:
            raise ValueError(f"bad size {chunk!r}: dimensions must be positive")
        sizes.append((width, height))
    if not sizes:
        raise ValueError("no sizes given")
    return sizes


def render_one(chrome: str, html: Path, out_png: Path, width: int, height: int) -> None:
    """Render the HTML to one PNG at the given viewport size."""
    out_png.parent.mkdir(parents=True, exist_ok=True)
    command = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        f"--screenshot={out_png}",
        f"--window-size={width},{height}",
        html.resolve().as_uri(),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=180)
    if result.returncode != 0 or not out_png.exists():
        message = (result.stderr or result.stdout or "").strip().splitlines()
        detail = message[-1] if message else "unknown error"
        raise RuntimeError(f"chrome failed for {width}x{height}: {detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render an HTML deck to PNG at several ratios.")
    parser.add_argument("--input", required=True, help="source HTML file")
    parser.add_argument("--out", required=True, help="output directory")
    parser.add_argument("--sizes", default="xhs", help="size preset or WIDTHxHEIGHT list")
    parser.add_argument("--name", default="", help="output file stem; defaults to the input stem")
    parser.add_argument("--chrome", default="", help="explicit Chrome/Chromium binary path")
    args = parser.parse_args()

    source = Path(args.input)
    if not source.is_file():
        sys.stderr.write(f"render-deck: input not found: {source}\n")
        return EXIT_BAD_INPUT

    try:
        if "x" in args.sizes and "," in args.sizes:
            sizes = parse_sizes(args.sizes)
        elif args.sizes in SIZE_PRESETS:
            sizes = SIZE_PRESETS[args.sizes]
        elif "x" in args.sizes:
            sizes = parse_sizes(args.sizes)
        else:
            sizes = SIZE_PRESETS["xhs"]
    except ValueError as error:
        sys.stderr.write(f"render-deck: {error}\n")
        return EXIT_BAD_INPUT

    chrome = find_chrome(args.chrome or None)
    if chrome is None:
        sys.stderr.write(
            "render-deck: no Chrome/Chromium binary found. "
            "Pass --chrome or set CHROME_PATH.\n"
        )
        return EXIT_NO_CHROME

    out_dir = Path(args.out)
    stem = args.name or source.stem
    written: List[Path] = []
    for width, height in sizes:
        target = out_dir / f"{stem}-{width}x{height}.png"
        try:
            render_one(chrome, source, target, width, height)
        except (RuntimeError, subprocess.TimeoutExpired) as error:
            sys.stderr.write(f"render-deck: {error}\n")
            return EXIT_BAD_INPUT
        written.append(target)
        sys.stderr.write(f"[OK] {target} ({width}x{height})\n")

    sys.stderr.write(f"[DONE] {len(written)} PNG written to {out_dir}\n")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
