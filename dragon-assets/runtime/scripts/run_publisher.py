#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_publisher.py · 天龙引擎 内容发布包生成 命令
================================================

把一篇内容生成多平台适配的发布包（标题/正文/标签/封面建议），
供复制到 PostBot 浏览器扩展一键同步发布。

调用：
    python scripts/run_publisher.py "AI训练师如何入门"
    python scripts/run_publisher.py --file ~/viral-content-reports/AI训练师入门.md
    python scripts/run_publisher.py "内容" --platforms xiaohongshu,douyin

输出：
    ~/viral-content-reports/publish-pack/{标题}.md

仅用 Python 标准库（argparse / pathlib / re / datetime）。
要求 Python ≥ 3.8。
"""
from __future__ import annotations

import argparse
import sys
import os
import re
from pathlib import Path
from datetime import datetime

# Windows GBK 兼容：强制 UTF-8 输出
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


SCRIPT_DIR = Path(__file__).resolve().parent
DRAGON_ROOT = SCRIPT_DIR.parent

# Windows 兼容：home directory fallback
def _get_home_dir() -> Path:
    """获取用户主目录，多重 fallback"""
    try:
        home = Path.home()
        if home and home.exists():
            return home
    except (RuntimeError, ValueError):
        pass
    userprofile = os.environ.get("USERPROFILE")
    if userprofile and Path(userprofile).exists():
        return Path(userprofile)
    home_env = os.environ.get("HOME")
    if home_env and Path(home_env).exists():
        return Path(home_env)
    drive = os.environ.get("HOMEDRIVE")
    path = os.environ.get("HOMEPATH")
    if drive and path:
        combined = Path(drive + path)
        if combined.exists():
            return combined
    fallback = Path("C:/Users/li")
    if fallback.exists():
        return fallback
    return Path(os.environ.get("TEMP", "C:/Windows/Temp"))


HOME_DIR = _get_home_dir()
PUBLISH_DIR = HOME_DIR / "viral-content-reports" / "publish-pack"

# 平台适配模板
PLATFORM_TEMPLATES = {
    "xiaohongshu": {
        "name": "小红书",
        "title_max": 20,
        "title_suffix": "口语化钩子，≤20字",
        "tags": "#AI训练师 #副业 #干货",
    },
    "douyin": {
        "name": "抖音",
        "title_max": 15,
        "title_suffix": "口播前3秒钩子",
        "tags": "#AI #副业 #干货",
    },
    "wechat": {
        "name": "公众号",
        "title_max": 25,
        "title_suffix": "信息明确，≤25字",
        "tags": "（文末可选）",
    },
    "zhihu": {
        "name": "知乎",
        "title_max": 20,
        "title_suffix": "问题式标题",
        "tags": "#AI训练 #干货",
    },
    "bilibili": {
        "name": "B站",
        "title_max": 25,
        "title_suffix": "标题党适度，≤25字",
        "tags": "#AI #副业 #干货",
    },
}


def extract_title(content: str) -> str:
    """从内容中提取标题：
    1. 优先 frontmatter 的 title 字段
    2. 否则取第一个 # 标题
    3. 否则取第一行非空文本"""
    lines = [l.strip() for l in content.splitlines() if l.strip()]

    # 1. frontmatter title
    if content.startswith("---"):
        for l in lines[1:]:
            if l == "---":
                break
            if l.startswith("title:"):
                t = l.split(":", 1)[1].strip().strip('"\'')
                if t:
                    return t

    # 2. 第一个 markdown 标题
    for l in lines:
        m = re.match(r"^#{1,6}\s+(.+)$", l)
        if m:
            return m.group(1).strip()

    # 3. 第一行非空（去掉标题符号）
    for l in lines:
        t = re.sub(r"^#{1,6}\s*", "", l)
        if len(t) > 3:
            return t
    return content.strip()[:20]


def clean_content(content: str, title: str) -> str:
    """清洗正文（去掉 frontmatter、标题行、markdown 符号）"""
    body = content

    # 去掉 frontmatter
    if body.startswith("---"):
        end = body.find("\n---", 3)
        if end != -1:
            body = body[end + 4:]

    # 去掉标题行
    for line in body.splitlines():
        stripped = re.sub(r"^#{1,6}\s*", "", line).strip()
        if stripped == title:
            body = body.replace(line, "", 1)
            break

    # 压缩空白
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    return body[:500]  # 发布包正文限长


def generate_publish_pack(content: str, platforms: list[str]) -> str:
    """生成多平台发布包 Markdown"""
    title = extract_title(content)
    body = clean_content(content, title)
    today = datetime.now().strftime("%Y-%m-%d")

    md = f"""# 发布包 · {title}

> 生成时间：{today} | 源内容：{title}
> 配合 PostBot 浏览器扩展一键同步发布

"""
    for plat in platforms:
        tpl = PLATFORM_TEMPLATES[plat]
        t_title = title[: tpl["title_max"]]
        md += f"""## 📱 {tpl['name']}

**标题**：{t_title}（{tpl['title_suffix']}）
**正文**：{body}
**标签**：{tpl['tags']}

"""
    md += """## ✅ 发布前检查
- [ ] 各平台标题未超字数
- [ ] 标签平台差异已适配
- [ ] 无敏感词/违禁内容

## 🔗 相关
- 安装 PostBot：third-party/PostBot安装指南.md
- 发布后记录：python scripts/run_dashboard.py add ...
"""
    return md


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="天龙引擎 内容发布包生成（多平台适配）"
    )
    parser.add_argument("content", nargs="?", help="内容文本（或用 --file）")
    parser.add_argument("--file", help="从文件读取内容")
    parser.add_argument("--platforms", default="xiaohongshu,douyin,wechat",
                        help="目标平台，逗号分隔（xiaohongshu/douyin/wechat/zhihu/bilibili）")
    parser.add_argument("--no-save", action="store_true", help="不保存发布包文件")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ 文件不存在：{args.file}")
            return 1
        content = Path(args.file).read_text(encoding="utf-8")
    elif args.content:
        content = args.content
    else:
        print("❌ 缺少内容（传文本或 --file）")
        print("用法: python scripts/run_publisher.py \"内容\" 或 --file 内容.md")
        return 1

    platforms = [p.strip() for p in args.platforms.split(",") if p.strip() in PLATFORM_TEMPLATES]
    if not platforms:
        print("❌ 无有效平台，可选：xiaohongshu/douyin/wechat/zhihu/bilibili")
        return 1

    pack = generate_publish_pack(content, platforms)
    print(pack)

    # 保存
    if not args.no_save:
        PUBLISH_DIR.mkdir(parents=True, exist_ok=True)
        safe = re.sub(r'[\\/:*?"<>|]', "_", extract_title(content))
        pack_path = PUBLISH_DIR / f"{safe}.md"
        pack_path.write_text(pack, encoding="utf-8")
        print(f"\n📄 发布包已保存：{pack_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
