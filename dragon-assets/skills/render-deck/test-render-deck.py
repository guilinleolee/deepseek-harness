#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smoke test for render-deck.py.

Renders the bundled example deck at one ratio and checks that a non-trivial PNG
comes out. Skips with exit code 0 when no Chrome/Chromium is installed, so the
test stays usable on machines without a browser.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "render-deck.py"
EXAMPLE = HERE / "example-deck.html"

# A blank or near-blank PNG renders smaller than this.
MIN_PNG_BYTES = 5000


def main() -> int:
    if not SCRIPT.is_file():
        sys.stderr.write("render-deck: script not found\n")
        return 1
    if not EXAMPLE.is_file():
        sys.stderr.write("render-deck: example deck not found\n")
        return 1

    with tempfile.TemporaryDirectory() as temp_dir:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--input",
                str(EXAMPLE),
                "--out",
                temp_dir,
                "--sizes",
                "1080x1440",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 4:
            sys.stderr.write("SKIP: no Chrome/Chromium on this machine\n")
            return 0
        if result.returncode != 0:
            sys.stderr.write(result.stderr)
            return 1

        rendered = list(Path(temp_dir).glob("*.png"))
        if not rendered:
            sys.stderr.write("render-deck: no PNG produced\n")
            return 1
        for png in rendered:
            size = png.stat().st_size
            if size < MIN_PNG_BYTES:
                sys.stderr.write(f"render-deck: {png.name} is only {size} bytes\n")
                return 1
            sys.stderr.write(f"[OK] {png.name} ({size} bytes)\n")

    sys.stderr.write("PASS: render-deck produced a non-trivial PNG\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
