#!/usr/bin/env python3
"""
autofill_source.py — V1.1.2 · 自动给缺 source 的 SKILL.md 填 source/license 字段。
3 层 fallback:
  1. git remote get-url origin (从 .git/ 反推)
  2. AUTO_HINTS 关键词表 (make_source.py 复用)
  3. 跳过 (天龙自研 / 无 git / 无 hint)

默认 dry-run,只显示建议;加 --apply 才真改。

Usage:
    # 默认 dry-run
    python scripts/autofill_source.py

    # 限制根目录
    python scripts/autofill_source.py --root "c:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine"

    # 真改文件
    python scripts/autofill_source.py --apply

    # 只针对某个 skill
    python scripts/autofill_source.py --only guizang --apply

    # 关闭 git remote 探测 (只用 AUTO_HINTS)
    python scripts/autofill_source.py --no-git --apply
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# 复用 make_source 的 AUTO_HINTS
sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_source  # type: ignore  # noqa: E402
from make_source import (  # type: ignore  # noqa: E402
    inject_fields,
    is_tianlong_native,
    auto_hint,
)


# 天龙自身的仓库 URL 黑名单。
# 这些 repo 不该被填进集成版 skill 的 source 字段(因为集成版 skill 是天龙内子目录,
# 不是真正 git clone 下来的)。检测到 → 返回 None,触发 fallback 到 AUTO_HINTS。
TIANLONG_REPOS = {
    "guilinleolee/dragon-engine",
    "guilinleolee/tianlong",
    "guilinleolee/.claude",
}

# 已知天龙集成版 skill 名字关键字(name 含这些关键字 → 直接走 AUTO_HINTS, 不查 git)。
# 这些 skill 是天龙从外部借调/集成到本地的,不是真的 git clone 下来的。
# 添加新条目: 在 A 场景出现过且已知的 skill,加进来避免误判。
INTEGRATED_SKILLS = {
    "guizang",              # op7418/guizang-social-card-skill
    "voxcpm",               # OpenBMB/VoxCPM
    "generative-media",     # SamurAIGPT/Generative-Media-Skills
    "gpt-image",            # freestylefly/awesome-gpt-image-2
    "huashu",               # alchaincyf/huashu-design
    "cinema-director",      # alchaincyf/huashu-design
    "async-task-pattern",   # SamurAIGPT/Generative-Media-Skills
    "nano-banana-brief",    # freestylefly/awesome-gpt-image-2
    "skill-updater",        # 天龙自研
    "dsh-computer-use",     # Anionex/dsh-computer-use(阶段 42 · macOS native action layer · MIT)
}


def _is_tianlong_repo(url: str) -> bool:
    """判断 URL 是否指向天龙自身仓库。"""
    # 转 https 后判断 owner/repo
    if url.startswith("git@github.com:"):
        url = f"https://github.com/{url[len('git@github.com:'):]}"
    # owner/repo 提取
    m = re.match(r"https?://github\.com/([^/]+)/([^/\s]+?)(?:\.git)?$", url)
    if not m:
        return False
    owner, repo = m.group(1), m.group(2)
    return f"{owner}/{repo}" in TIANLONG_REPOS


def _is_integrated_skill(skill_name: str) -> bool:
    """判断是否是已知天龙集成版(应走 AUTO_HINTS, 不查 git remote)。"""
    n = skill_name.lower()
    return any(kw in n for kw in INTEGRATED_SKILLS)


def _has_own_git(skill_md_path: Path, target_root: Path | None = None) -> bool:
    """检查 skill 是否真有自己的 .git/ (在 skill 父目录 或 skill 自身目录)。

    天龙下的 skill 是父仓库的子目录, 没有自己的 .git/ → 返回 False。
    用户从 GitHub clone 到独立的 /tmp/xxx/ 的资产 → 返回 True。
    """
    cur = skill_md_path.parent.resolve()
    # 只看 skill 自身 + skill 父目录
    for _ in range(2):
        git_dir = cur / ".git"
        if git_dir.exists() and git_dir.is_dir():
            return True
        # 如果 target_root 给定, 爬到 target_root 就停
        if target_root is not None and cur == Path(target_root).resolve():
            return False
        if cur == cur.parent:
            break
        cur = cur.parent
    return False


def git_remote_get_url(skill_md_path: Path, target_root: Path | None = None) -> str | None:
    """从 SKILL.md 同级目录往上找 .git/,跑 git config --get remote.origin.url。

    ⚠️ 安全: 如果 URL 里嵌入了 credential (e.g. https://x-access-token:XXX@github.com/...),
    返回 None 并打印警告 (不能把 token 写进 SKILL.md frontmatter)。

    ⚠️ 黑名单: 如果 URL 是天龙自身仓库 (dragon-engine / tianlong 等),
    返回 None 让 caller fallback 到 AUTO_HINTS — 因为集成版 skill 是天龙子目录,
    不是真的从那个仓库 git clone 下来。

    V1.1.3: target_root 限定深度, 避免误用父仓库 .git/。
    """
    if not _has_own_git(skill_md_path, target_root):
        return None
    cur = skill_md_path.parent.resolve()
    while cur != cur.parent:
        git_dir = cur / ".git"
        if git_dir.exists() and git_dir.is_dir():
            try:
                result = subprocess.run(
                    ["git", "config", "--get", "remote.origin.url"],
                    cwd=str(cur), capture_output=True, text=True, timeout=5,
                )
                if result.returncode == 0 and result.stdout.strip():
                    url = result.stdout.strip()
                    if url.endswith(".git"):
                        url = url[:-4]
                    # SSH 转 HTTPS: git@github.com:owner/repo → https://github.com/owner/repo
                    if url.startswith("git@github.com:"):
                        path = url[len("git@github.com:"):]
                        url = f"https://github.com/{path}"
                    # 安全检查: 只对 https:// URL 检测 credential (SSH git@... 格式不带密码)
                    if url.startswith("https://") or url.startswith("http://"):
                        # 找 userinfo (URL 中 @ 之前的部分)
                        try:
                            from urllib.parse import urlparse
                            parsed = urlparse(url)
                            if parsed.username or parsed.password:
                                print(f"   ⚠️  WARNING: git remote URL 含 credential (user={parsed.username!r}), 跳过", file=sys.stderr)
                                print(f"       请用 `git remote set-url origin https://github.com/owner/repo` 清理后重试", file=sys.stderr)
                                return None
                        except Exception:
                            pass
                    # 黑名单: 天龙自身仓库 → 跳过,触发 fallback 到 AUTO_HINTS
                    if _is_tianlong_repo(url):
                        print(f"   ⚠️  WARNING: git remote URL 是天龙自身仓库 ({url})", file=sys.stderr)
                        print(f"       集成版 skill 是天龙子目录,不应填天龙自身 URL,跳过", file=sys.stderr)
                        print(f"       fallback 到 AUTO_HINTS 关键词猜测", file=sys.stderr)
                        return None
                    return url
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                return None
            return None
        cur = cur.parent
    return None


def parse_github_url(url: str) -> tuple[str, str] | None:
    """从 GitHub URL 抽 owner / repo。"""
    m = re.match(r"https?://github\.com/([^/]+)/([^/\s]+?)(?:\.git)?$", url)
    if m:
        return (m.group(1), m.group(2))
    return None


def detect_license_via_local_files(skill_md_path: Path) -> str | None:
    """从 .git 同级目录找 LICENSE/COPYING 文件,简单正则 SPDX。"""
    cur = skill_md_path.parent.resolve()
    for _ in range(5):
        for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "COPYING.md"):
            lic_file = cur / name
            if lic_file.exists():
                try:
                    text = lic_file.read_text(encoding="utf-8", errors="replace")[:2000]
                    if re.search(r"Apache License.*?Version 2\.0", text, re.DOTALL):
                        return "Apache-2.0"
                    if "MIT License" in text:
                        return "MIT"
                    if "GNU GENERAL PUBLIC LICENSE" in text and "version 3" in text.lower():
                        return "GPL-3.0"
                    if "GNU AFFERO GENERAL PUBLIC LICENSE" in text:
                        return "AGPL-3.0"
                    if "BSD" in text and "3-Clause" in text:
                        return "BSD-3-Clause"
                    if "BSD" in text and "2-Clause" in text:
                        return "BSD-2-Clause"
                    if "Mozilla Public License" in text:
                        return "MPL-2.0"
                    return "License-Unknown"
                except OSError:
                    pass
        cur = cur.parent
    return None


def resolve_source_license(skill: dict[str, Any], use_git: bool = True,
                            target_root: Path | None = None) -> tuple[str, str, str, str] | None:
    """混合模式解析 source/license。

    V1.1.3: 集成版 skill 直接走 AUTO_HINTS, 不查 git remote;
            target_root 限定 git remote 查找的深度。

    返回 (source_line, license_line, source_method, license_method) 或 None。
    source_method ∈ {git_remote, auto_hint, none}
    license_method ∈ {github_api, local_license_file, auto_hint_default, none}
    """
    name = skill["name"]
    skill_md_path = Path(skill["path"])

    # V1.1.3: 已知天龙集成版 → 直接 AUTO_HINTS, 不查 git (天龙子目录, 不应填天龙仓库 URL)
    if _is_integrated_skill(name):
        # Layer 2: AUTO_HINTS (强制)
        hint = auto_hint(name)
        if hint:
            url, lic, note = hint
            source_line = f"source: {url} ({note})"
            license_line = f"license: {lic}"
            return (source_line, license_line, "auto_hint", "auto_hint")
        return None

    # Layer 1: git remote (优先级最高)
    if use_git:
        git_url = git_remote_get_url(skill_md_path, target_root=target_root)
        if git_url:
            lic = detect_license_via_local_files(skill_md_path)
            lic_method = "local_license_file" if lic else "none"
            if not lic:
                lic = "MIT"
                lic_method = "auto_hint_default"
            source_line = f"source: {git_url} (auto-filled from git remote)"
            license_line = f"license: {lic}"
            return (source_line, license_line, "git_remote", lic_method)

    # Layer 2: AUTO_HINTS 关键词表
    hint = auto_hint(name)
    if hint:
        url, lic, note = hint
        source_line = f"source: {url} ({note})"
        license_line = f"license: {lic}"
        return (source_line, license_line, "auto_hint", "auto_hint")

    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="V1.1.2 自动补 source/license (git remote + AUTO_HINTS)")
    parser.add_argument("--root", default=os.path.expanduser("~/.claude"),
                        help="扫描根目录")
    parser.add_argument("--target-root",
                        help="(V1.1.3) 单项目根(限定 git remote 查找深度)。例如 dragon-engine/skills/")
    parser.add_argument("--only", help="只处理名字含此子串的 skill")
    parser.add_argument("--apply", action="store_true",
                        help="真改文件(默认 dry-run,只显示)")
    parser.add_argument("--no-git", action="store_true",
                        help="(默认)关闭 git remote 探测,只用 AUTO_HINTS(天龙集成版推荐)")
    parser.add_argument("--use-git", action="store_true",
                        help="开启 git remote 探测,真 git clone 下来的资产用(天龙仓库会被黑名单拦截)")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import parse_skill  # type: ignore  # noqa: E402
    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        sys.exit(f"ERROR: root not found: {root}")

    skills_data = parse_skill.scan_skill_md(root)
    targets = [
        s for s in skills_data
        if s.get("source", {}).get("type") in ("missing", "unparseable")
        and not is_tianlong_native(s.get("description"))
        and (not args.only or args.only.lower() in s["name"].lower())
    ]

    print(f"找到 {len(targets)} 个缺 source 的 SKILL.md (天龙自研已过滤)")
    if not targets:
        print("✅ 无需补 source")
        return 0

    if args.apply:
        print("⚠️  --apply 模式:真改文件!\n")
    else:
        print("ℹ️  默认 dry-run,只显示建议;加 --apply 才真改文件\n")

    by_method = {"git_remote": [], "auto_hint": [], "none": []}
    target_root = Path(args.target_root).expanduser().resolve() if args.target_root else None
    for s in targets:
        # 默认关闭 git remote (天龙集成版会被黑名单拦截;真 git clone 下来的再加 --use-git)
        result = resolve_source_license(s, use_git=args.use_git, target_root=target_root)
        if result is None:
            by_method["none"].append(s)
            print(f"⏭️  {s['name']:<35} | 无 git remote + 无 AUTO_HINTS,跳过")
            continue
        source_line, license_line, src_method, lic_method = result

        if args.verbose or not args.apply:
            print(f"📦 {s['name']:<35} | 来源={src_method:<11} license={lic_method}")
            print(f"   {source_line}")
            print(f"   {license_line}")

        if args.apply:
            ok = inject_fields(Path(s["path"]), source_line, license_line)
            if ok:
                print(f"   ✅ 已写入\n")
                by_method[src_method].append(s["name"])
            else:
                print(f"   ❌ 写入失败\n")
        else:
            by_method[src_method].append(s["name"])

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"git_remote: {len(by_method['git_remote'])} 个")
    print(f"auto_hint:  {len(by_method['auto_hint'])} 个")
    print(f"skipped:    {len(by_method['none'])} 个")
    if not args.apply and sum(len(v) for v in by_method.values()) > 0:
        print(f"💡 加 --apply 才会真改文件")
    return 0


if __name__ == "__main__":
    sys.exit(main())