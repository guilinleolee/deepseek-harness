"""
天龙引擎 V2.0 · gpt-image-2-style-library sync.py
================================================
同步上游 freestylefly/awesome-gpt-image-2 仓库到本地 skill。
"""

from __future__ import annotations

import argparse
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
UPSTREAM_URL = "https://github.com/freestylefly/awesome-gpt-image-2.git"
TARBALL_URL = "https://codeload.github.com/freestylefly/awesome-gpt-image-2/tar.gz/refs/heads/main"


def sync_full():
    """完整同步：从 GitHub tarball 拉取并更新 references + scripts"""
    print("📥 同步上游仓库...")
    if STAGING_DIR.exists():
        shutil.rmtree(STAGING_DIR)
    STAGING_DIR.parent.mkdir(parents=True, exist_ok=True)

    # 用 tarball 下载（更稳定）
    tarball = STAGING_DIR.parent / "awesome.tar.gz"
    print(f"  下载 tarball: {TARBALL_URL}")
    subprocess.run(
        ["curl", "-sL", "--max-time", "180", "-o", str(tarball), TARBALL_URL],
        check=True,
    )

    print(f"  解压到 {STAGING_DIR}")
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "tar", "-xzf", str(tarball),
            "--strip-components=1",
            "-C", str(STAGING_DIR),
            "awesome-gpt-image-2-main/agents",
            "awesome-gpt-image-2-main/docs",
            "awesome-gpt-image-2-main/scripts",
        ],
        check=True,
    )

    # 拷贝关键文件
    src_ref = STAGING_DIR / "agents" / "skills" / "gpt-image-2-style-library" / "references" / "style-library.md"
    dst_ref = SKILL_DIR / "references" / "style-library.md"
    if src_ref.exists():
        shutil.copy2(src_ref, dst_ref)
        print(f"  ✅ 更新 references/style-library.md")

    src_tpl = STAGING_DIR / "docs" / "templates.md"
    dst_tpl = SKILL_DIR / "references" / "templates.md"
    if src_tpl.exists():
        shutil.copy2(src_tpl, dst_tpl)
        print(f"  ✅ 更新 references/templates.md")

    src_script = STAGING_DIR / "scripts" / "generate-style-skill.mjs"
    dst_script = SKILL_DIR / "scripts" / "generate-style-skill.mjs"
    if src_script.exists():
        shutil.copy2(src_script, dst_script)
        print(f"  ✅ 更新 scripts/generate-style-skill.mjs")

    print(f"\n✅ 同步完成: {SKILL_DIR}")


def sync_incremental():
    """增量同步：仅当 staging 目录已存在时"""
    if not STAGING_DIR.exists():
        print("⚠️  无 staging 目录，降级到完整同步")
        return sync_full()

    print("📥 增量同步（git pull）...")
    result = subprocess.run(
        ["git", "-C", str(STAGING_DIR), "pull", "--depth", "1"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"⚠️  git pull 失败，降级到 tarball 下载")
        return sync_full()

    # 拷贝更新文件
    src_ref = STAGING_DIR / "agents" / "skills" / "gpt-image-2-style-library" / "references" / "style-library.md"
    if src_ref.exists():
        shutil.copy2(src_ref, SKILL_DIR / "references" / "style-library.md")
        print(f"  ✅ 更新 references/style-library.md")

    src_tpl = STAGING_DIR / "docs" / "templates.md"
    if src_tpl.exists():
        shutil.copy2(src_tpl, SKILL_DIR / "references" / "templates.md")
        print(f"  ✅ 更新 references/templates.md")

    print(f"\n✅ 增量同步完成")


def main():
    parser = argparse.ArgumentParser(description="同步 awesome-gpt-image-2 上游数据")
    parser.add_argument("--incremental", action="store_true", help="增量同步")
    args = parser.parse_args()

    if args.incremental:
        sync_incremental()
    else:
        sync_full()


if __name__ == "__main__":
    main()