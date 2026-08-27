"""
天龙引擎 V1.0 · gpt-image-2-gallery-explorer sync.py
====================================================
同步上游 518 案例到本地 references/gallery/。
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

# UTF-8 stdout
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

SKILL_DIR = Path(__file__).parent.parent
STAGING_DIR = Path("/tmp/gpt-image2-staging/awesome-gpt-image-2")
TARBALL_URL = "https://codeload.github.com/freestylefly/awesome-gpt-image-2/tar.gz/refs/heads/main"
GALLERY_DST = SKILL_DIR / "references" / "gallery"


def sync_full():
    """完整同步：从 tarball 下载并更新 gallery 文件"""
    print("📥 同步 518 案例库...")
    GALLERY_DST.mkdir(parents=True, exist_ok=True)

    if not STAGING_DIR.exists():
        STAGING_DIR.parent.mkdir(parents=True, exist_ok=True)
        tarball = STAGING_DIR.parent / "awesome.tar.gz"
        print(f"  下载 tarball: {TARBALL_URL}")
        subprocess.run(
            ["curl", "-sL", "--max-time", "180", "-o", str(tarball), TARBALL_URL],
            check=True,
        )
        STAGING_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "tar", "-xzf", str(tarball),
                "--strip-components=1",
                "-C", str(STAGING_DIR),
                "awesome-gpt-image-2-main/docs/gallery.md",
                "awesome-gpt-image-2-main/docs/gallery-part-1.md",
                "awesome-gpt-image-2-main/docs/gallery-part-2.md",
            ],
            check=True,
        )

    for fname in ("gallery.md", "gallery-part-1.md", "gallery-part-2.md"):
        src = STAGING_DIR / "docs" / fname
        if src.exists():
            shutil.copy2(src, GALLERY_DST / fname)
            size_kb = src.stat().st_size / 1024
            print(f"  ✅ {fname} ({size_kb:.1f}KB)")

    print(f"\n✅ 同步完成: {GALLERY_DST}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="同步 518 案例")
    parser.add_argument("--incremental", action="store_true")
    args = parser.parse_args()
    sync_full()


if __name__ == "__main__":
    main()