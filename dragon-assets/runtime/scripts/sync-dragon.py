#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync-dragon.py · 天龙引擎升级同步系统 V1.0

功能：
1. 检测 GitHub 最新 VERSION（如有新版 → 提示升级）
2. 下载最新 BIBLE.md + cross-ai-replication-prompt.md
3. 同步到本地 AI 工具配置：
   - Cursor: ~/.cursor/rules/dragon-engine.mdc
   - Claude desktop: ~/.claude/projects/.../CLAUDE.md 注入
   - Codex: ~/.codex/prompts/dragon-engine.md (可选)
4. 生成 sync 报告 + 输出下次升级 prompt

用法：
  python scripts/sync-dragon.py             # 完整 sync（检测升级 + 下载 + 同步 + 报告）
  python scripts/sync-dragon.py --check    # 仅检查 GitHub 最新版本，不下载
  python scripts/sync-dragon.py --dry-run  # 不实际写文件
  python scripts/sync-dragon.py --target cursor|claude|codex|all  # 只同步到指定工具

退出码：0=PASS / 1=FAIL / 2=配置错
"""
import sys, os, io, json, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone

# Force UTF-8 stdout on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

REPO_OWNER = "guilinleolee"
REPO_NAME = "dragon-engine"
REPO_BRANCH = "master"
GITHUB_RAW = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{REPO_BRANCH}"
GITHUB_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

# Token (optional, 从 GH_TOKEN 环境变量读)
GITHUB_TOKEN = os.environ.get("GH_TOKEN", "") or os.environ.get("GITHUB_TOKEN", "")

def http_get(url, timeout=15):
    """HTTP GET with token auth if available"""
    req = urllib.request.Request(url)
    if GITHUB_TOKEN:
        req.add_header("Authorization", f"token {GITHUB_TOKEN}")
    req.add_header("User-Agent", "dragon-engine-sync")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def get_remote_version():
    """从 GitHub 读最新 VERSION（试 raw.githubusercontent.com，失败 fallback API）"""
    # 尝试 1: raw.githubusercontent.com
    try:
        data = http_get(f"{GITHUB_RAW}/VERSION").decode("utf-8").strip()
        for line in data.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                return line
    except Exception:
        pass
    # 尝试 2: api.github.com (JSON API)
    try:
        import json
        url = f"{GITHUB_API}/contents/VERSION"
        data = json.loads(http_get(url).decode("utf-8"))
        import base64
        content = base64.b64decode(data.get("content", "")).decode("utf-8")
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                return line
    except Exception as e:
        print(f"⚠️  无法读 GitHub VERSION (raw + api 都失败): {e}", file=sys.stderr)
    return None

def get_remote_file(filename):
    """下载远端文件（raw → api fallback）"""
    # 尝试 1: raw
    try:
        return http_get(f"{GITHUB_RAW}/{filename}").decode("utf-8")
    except Exception:
        pass
    # 尝试 2: API
    try:
        import json, base64
        url = f"{GITHUB_API}/contents/{filename}"
        data = json.loads(http_get(url).decode("utf-8"))
        return base64.b64decode(data["content"]).decode("utf-8")
    except Exception as e:
        print(f"⚠️  无法下载 {filename}: {e}", file=sys.stderr)
        return None

def get_local_version():
    """从本地 VERSION 文件读当前版本"""
    local_v = Path("VERSION")
    if not local_v.exists():
        return None
    for line in local_v.read_text(encoding="utf-8").split("\n"):
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    return None

def parse_version(v):
    """V2.0 → (2, 0)"""
    if not v:
        return (0, 0)
    try:
        return tuple(int(x) for x in v.lstrip("V").split(".")[:2])
    except (ValueError, AttributeError):
        return (0, 0)

def download_files(targets):
    """下载 BIBLE.md + cross-ai-replication-prompt.md 到本地"""
    out = {}
    for filename, local_path in targets.items():
        content = get_remote_file(filename)
        if content:
            out[local_path] = content
            print(f"  ✅ 下载 {filename} ({len(content)} bytes)")
        else:
            out[local_path] = None
    return out

def sync_to_cursor(content, dry_run=False):
    """同步到 Cursor rules"""
    cursor_dir = Path.home() / ".cursor" / "rules"
    target = cursor_dir / "dragon-engine.mdc"
    if dry_run:
        print(f"  🔍 [DRY] Cursor → {target} ({len(content)} bytes)")
        return True
    cursor_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"  ✅ Cursor → {target}")
    return True

def sync_to_claude(content, dry_run=False):
    """同步到 Claude desktop 项目 CLAUDE.md 注入块"""
    # 找到 ~/.claude/projects/c--Users-li--claude/dragon-engine/CLAUDE.md
    claude_md = Path("CLAUDE.md")
    if not claude_md.exists():
        if dry_run:
            print(f"  🔍 [DRY] Claude → CLAUDE.md 不存在，跳过")
            return False
        print(f"  ⚠️  CLAUDE.md 不存在（不在天龙主树根）", file=sys.stderr)
        return False
    # 标记块：天龙同步段（带 sentinel 防止重复）
    sentinel_start = "<!-- DRAGON-ENGINE-SYNC-START v"
    sentinel_end = "<!-- DRAGON-ENGINE-SYNC-END -->"
    version = get_remote_version() or "?"
    block = (
        f"{sentinel_start}{version} -->\n"
        + content
        + f"\n{sentinel_end}\n"
    )
    existing = claude_md.read_text(encoding="utf-8")
    if sentinel_start in existing:
        # 替换旧块
        import re
        new = re.sub(
            rf"{sentinel_start}.*?{sentinel_end}\n?",
            block,
            existing,
            flags=re.DOTALL,
        )
    else:
        # 追加新块
        new = existing + "\n\n" + block
    if dry_run:
        print(f"  🔍 [DRY] Claude → CLAUDE.md 更新（{len(content)} bytes 注入块）")
    else:
        claude_md.write_text(new, encoding="utf-8")
        print(f"  ✅ Claude → CLAUDE.md 注入天龙 sync 块")
    return True

def sync_to_codex(content, dry_run=False):
    """同步到 Codex prompts (若 Codex 安装)"""
    codex_dir = Path.home() / ".codex" / "prompts"
    if not codex_dir.exists():
        if dry_run:
            print(f"  🔍 [DRY] Codex → ~/.codex/prompts/ 不存在，跳过")
        else:
            print(f"  ⚠️  Codex 未安装（~/.codex/prompts/ 不存在），跳过")
        return False
    target = codex_dir / "dragon-engine.md"
    if dry_run:
        print(f"  🔍 [DRY] Codex → {target} ({len(content)} bytes)")
        return True
    codex_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"  ✅ Codex → {target}")
    return True

def main():
    import argparse
    parser = argparse.ArgumentParser(description="天龙引擎升级同步")
    parser.add_argument("--check", action="store_true", help="仅检查版本")
    parser.add_argument("--dry-run", action="store_true", help="不实际写文件")
    parser.add_argument("--target", default="all",
                        choices=["all", "cursor", "claude", "codex"],
                        help="同步目标（默认 all）")
    args = parser.parse_args()

    print("═══ 天龙引擎 sync V1.0 ═══")
    print(f"时间：{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print(f"仓库：{REPO_OWNER}/{REPO_NAME}@{REPO_BRANCH}")
    print(f"模式：{'check-only' if args.check else 'dry-run' if args.dry_run else 'real'}")
    print()

    # 1. 检测版本
    print("── 1. 版本检测 ──")
    local_v = get_local_version()
    remote_v = get_remote_version()
    print(f"  本地 VERSION: {local_v or '(无)'}")
    print(f"  GitHub 最新 : {remote_v or '(无法访问)'}")

    if not remote_v:
        print("❌ 无法访问 GitHub VERSION，退出")
        sys.exit(1)

    local_tuple = parse_version(local_v)
    remote_tuple = parse_version(remote_v)

    if local_tuple >= remote_tuple:
        print(f"  ✅ 本地已是最新（{local_v} >= {remote_v}）")
        if args.check:
            sys.exit(0)
        # 仍然继续下载 + 同步，让其他 AI 应用拿到最新
    else:
        print(f"  ⬆️  本地 {local_v or '无'} < 远程 {remote_v} → 升级")
        if not args.check:
            # 更新本地 VERSION
            if not args.dry_run:
                Path("VERSION").write_text(f"V{remote_tuple[0]}.{remote_tuple[1]}\n", encoding="utf-8")
                print(f"  ✅ VERSION 更新为 {remote_v}")

    if args.check:
        sys.exit(0)

    # 2. 下载文件
    print()
    print("── 2. 下载最新文件 ──")
    files = download_files({
        "BIBLE.md": "BIBLE.md",
        "memory/cross-ai-replication-prompt.md": "cross-ai-replication-prompt.md",
    })
    if not files.get("BIBLE.md"):
        print("❌ BIBLE.md 下载失败")
        sys.exit(1)

    # 写到临时位置（不覆盖现有 BIBLE.md 让 git diff）
    # 实际策略：放到 output/sync-{version}/ 让用户自己手动 merge

    sync_dir = Path(f"output/sync-{remote_v.replace('.', '_')}")
    if not args.dry_run:
        sync_dir.mkdir(parents=True, exist_ok=True)
        (sync_dir / "BIBLE.md").write_text(files["BIBLE.md"], encoding="utf-8")
        if files.get("cross-ai-replication-prompt.md"):
            (sync_dir / "cross-ai-replication-prompt.md").write_text(
                files["cross-ai-replication-prompt.md"], encoding="utf-8"
            )
        print(f"  ✅ 新版文件已存到 {sync_dir}/")

    # 3. 同步到 AI 应用
    print()
    print("── 3. 同步到 AI 应用 ──")
    cross_ai = files.get("cross-ai-replication-prompt.md")
    if not cross_ai:
        cross_ai = files["BIBLE.md"]  # fallback
        print(f"  ⚠️  cross-ai-replication-prompt.md 缺失，用 BIBLE.md fallback")

    targets = args.target
    if targets in ("all", "cursor"):
        sync_to_cursor(cross_ai, args.dry_run)
    if targets in ("all", "claude"):
        sync_to_claude(cross_ai, args.dry_run)
    if targets in ("all", "codex"):
        sync_to_codex(cross_ai, args.dry_run)

    # 4. 报告
    print()
    print("── 4. 同步报告 ──")
    print(f"  版本：{local_v or '无'} → {remote_v}")
    print(f"  BIBLE.md: {len(files['BIBLE.md'])} bytes")
    print(f"  cross-ai prompt: {len(cross_ai)} bytes")
    if not args.dry_run:
        print(f"  存到：{sync_dir}/")
        print(f"  下一步：git diff {sync_dir}/ 后手动 commit")
    print()
    print("✅ 同步完成")
    sys.exit(0)

if __name__ == "__main__":
    main()