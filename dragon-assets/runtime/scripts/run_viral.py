#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_viral.py · 天龙引擎 /viral 命令完整执行脚本 V2.0
==========================================================

把天龙 commands/viral.md + skills/china-viral-content-analyzer 的
6 步流程封装为命令行调用。

支持 3 种执行模式：
1. **天龙 CLI 模式**（推荐，需要在天龙 CLI 真实环境运行）
   - 生成完整 Prompt + 6 步执行清单
   - 用户复制到 Claude Code / 天龙 CLI 会话
2. **WebSearch 模式**（自动）
   - 直接用 Python 调用 web search（受限于环境）
3. **模板模式**（兜底）
   - 生成完整报告模板 + 占位符
   - 用户手动填充数据

调用：
    python scripts/run_viral.py AI训练师
    python scripts/run_viral.py "抖店 AI 客服" --mode cli
    python scripts/run_viral.py "AI 训练师" --mode web
    python scripts/run_viral.py "AI 训练师" --mode template
    python scripts/run_viral.py --help

输出：
    ~/viral-content-reports/{关键词}.md

仅用 Python 标准库（argparse / pathlib / subprocess / re）。
要求 Python ≥ 3.8（已与项目兼容）。
"""
from __future__ import annotations

import argparse
import sys
import os
import json
import subprocess
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

# Windows 兼容：处理 home directory 找不到的情况
def _get_home_dir() -> Path:
    """获取用户主目录，多重 fallback"""
    # 1. 优先用 Path.home()
    try:
        home = Path.home()
        if home and home.exists():
            return home
    except (RuntimeError, ValueError):
        pass

    # 2. 尝试 USERPROFILE（Windows）
    userprofile = os.environ.get("USERPROFILE")
    if userprofile and Path(userprofile).exists():
        return Path(userprofile)

    # 3. 尝试 HOME（Unix）
    home_env = os.environ.get("HOME")
    if home_env and Path(home_env).exists():
        return Path(home_env)

    # 4. 尝试 HOMEDRIVE + HOMEPATH（Windows 备选）
    drive = os.environ.get("HOMEDRIVE")
    path = os.environ.get("HOMEPATH")
    if drive and path:
        combined = Path(drive + path)
        if combined.exists():
            return combined

    # 5. 最后的兜底（Windows 常见路径）
    fallback = Path("C:/Users/li")
    if fallback.exists():
        return fallback

    # 6. 实在找不到就用临时目录
    return Path(os.environ.get("TEMP", "C:/Windows/Temp"))


HOME_DIR = _get_home_dir()
REPORTS_DIR = HOME_DIR / "viral-content-reports"
IMAGES_DIR = REPORTS_DIR / "images"

# 6 大平台搜索模板（天龙 china-viral-content-analyzer SKILL 协议）
PLATFORM_SEARCHES = [
    {"name": "小红书", "code": "xhs", "site": "xiaohongshu.com",
     "query_template": 'site:xiaohongshu.com "{keyword}" 爆款',
     "user_profile": "18-35岁女性为主", "preference": "种草、教程、生活方式"},
    {"name": "抖音", "code": "dy", "site": "douyin.com",
     "query_template": 'site:douyin.com "{keyword}" 热门',
     "user_profile": "全年龄段", "preference": "娱乐、情感、实用技巧"},
    {"name": "B站", "code": "bili", "site": "bilibili.com",
     "query_template": 'site:bilibili.com "{keyword}" 播放量高',
     "user_profile": "Z世代", "preference": "知识、娱乐、二次元"},
    {"name": "知乎", "code": "zh", "site": "zhihu.com",
     "query_template": 'site:zhihu.com "{keyword}" 高赞',
     "user_profile": "高学历群体", "preference": "专业观点、深度分析"},
    {"name": "视频号", "code": "wxv", "site": None,
     "query_template": '"{keyword}" 视频号 爆款',
     "user_profile": "30+岁，微信生态", "preference": "情感、职场、健康"},
    {"name": "公众号", "code": "wx", "site": "mp.weixin.qq.com",
     "query_template": 'site:mp.weixin.qq.com "{keyword}"',
     "user_profile": "微信用户", "preference": "深度文章、观点"},
]

# 6 维度分析框架（天龙 china-viral-content-analyzer SKILL 协议）
ANALYSIS_DIMENSIONS = [
    {"key": "title", "name": "标题分析",
     "points": ["字数统计", "关键词分类（数字/身份/反常识/承诺/对比）",
                "情绪词识别", "结构模式提炼"]},
    {"key": "cover", "name": "封面/视觉分析",
     "points": ["视觉风格（实拍/排版/插图）", "文字信息量（大字/小字/无字）",
                "色彩情绪（红/黄/绿/蓝）", "主体元素（人/工具/数据）"]},
    {"key": "structure", "name": "内容结构分析",
     "points": ["开头钩子（前 3 秒 / 前 200 字）", "段落结构（5 段式 / 7 段式 / 故事化）",
                "结尾引导（关注/评论/加微信）"]},
    {"key": "tags", "name": "话题标签分析",
     "points": ["高频标签 TOP 20", "标签组合策略（品类 + 工具 + 场景 + 类型）",
                "平台差异化标签"]},
    {"key": "pain", "name": "用户痛点/情绪价值分析",
     "points": ["5 大痛点（按出现频率）", "情绪价值层次（生存/效率/成长/身份）",
                "痛点-解决方案映射"]},
    {"key": "data", "name": "数据表现分析",
     "points": ["关键数据中位数（点赞/评论/收藏/转发）", "互动深度（收藏 > 点赞 > 转发 > 评论）",
                "爆款比例（爆款数 / 总内容）", "平台爆款率对比"]},
]

# 爆款公式（天龙 SKILL 提取自大量案例）
VIRAL_FORMULAS = [
    {"name": "数字冲击型",
     "template": "[数字] 天 + [身份] + [AI 训练] + [结果]",
     "example": "30 天训练 AI 客服 | 准确率 78%，省 1000 倍成本",
     "platform": "抖音/视频号"},
    {"name": "身份代入型",
     "template": "[人物] + [场景] + [AI 训练] + [结果]",
     "example": "我让老张老婆下班了：抖店 AI 客服这样训练",
     "platform": "小红书/视频号"},
    {"name": "反常识型",
     "template": "[反常识结论] + [理由] + [正确做法]",
     "example": "AI 训练师不是教 AI，'训练' 是个被误解的词",
     "platform": "知乎/公众号"},
    {"name": "承诺型",
     "template": "[时间] + [训练成果] + [0 限制]",
     "example": "30 天 AI 训练营，0 基础也能训练你的 AI",
     "platform": "抖音/小红书"},
    {"name": "对比型",
     "template": "[A] vs [B] + [差异化结论] + [你能得到什么]",
     "example": "AI 训练师 vs AI 工程师：差的不只是 1 个字",
     "platform": "B站/公众号"},
]


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="天龙引擎 /viral 命令完整执行脚本 V2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/run_viral.py AI训练师                 # 默认 CLI 模式
  python scripts/run_viral.py "AI 训练师" --mode web        # WebSearch 模式
  python scripts/run_viral.py "AI 训练师" --mode template   # 模板模式
  python scripts/run_viral.py AI训练师 --force               # 覆盖已有报告

模式说明：
  cli      生成天龙 CLI 完整调用 Prompt（推荐）
  web      用 curl 直接 WebSearch（受限于环境）
  template 生成报告模板 + 占位符（兜底）
        """,
    )
    parser.add_argument(
        "keyword",
        nargs="?",
        help="要分析的关键词（必填）",
    )
    parser.add_argument(
        "--mode",
        choices=["cli", "web", "template"],
        default="cli",
        help="执行模式（默认 cli）",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制覆盖已存在的报告",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只显示流程，不实际生成报告",
    )
    parser.add_argument(
        "--platforms",
        default="xhs,dy,bili,zh,wxv,wx",
        help="要分析的平台（逗号分隔，默认 6 个全选）",
    )
    return parser.parse_args()


def check_dedup(keyword: str, force: bool = False) -> bool:
    """检查是否已存在报告"""
    report_path = REPORTS_DIR / f"{keyword}.md"
    if report_path.exists() and not force:
        print(f"[!] 报告已存在：{report_path}")
        print(f"    使用 --force 覆盖，或先删除旧文件")
        return False
    return True


def ensure_output_dirs(keyword: str) -> None:
    """确保输出目录存在"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    (IMAGES_DIR / keyword).mkdir(parents=True, exist_ok=True)


def filter_platforms(platforms_str: str) -> list[dict]:
    """根据用户输入过滤平台"""
    wanted = set(platforms_str.split(","))
    return [p for p in PLATFORM_SEARCHES if p["code"] in wanted]


def generate_cli_prompt(keyword: str, platforms: list[dict]) -> str:
    """生成天龙 CLI 调用的完整 Prompt（让 Claude Code / 天龙 CLI 执行）"""
    platform_lines = "\n".join(
        f"   - {p['name']}: {p['query_template'].format(keyword=keyword)}"
        for p in platforms
    )

    return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 天龙 /viral 命令 · 完整调用 Prompt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

请执行天龙 /viral 命令，关键词：「{keyword}」

【天龙命令调用】
1. 读取 commands/viral.md 完整流程
2. 调用 china-viral-content-analyzer SKILL（路径：skills/china-viral-content-analyzer/）
3. 多平台搜索（{len(platforms)} 个 site: 搜索）：
{platform_lines}
4. 使用 playwright-skill 提取每个爆款的内容（标题/封面/数据）
5. 六维度分析（标题/封面/结构/标签/痛点/数据）
6. 生成报告到 ~/viral-content-reports/{keyword}.md
7. 输出 3-5 条核心洞察 + 爆款公式

【报告模板】
- 标题：# 「{keyword}」爆款内容分析报告
- 9 大模块：执行摘要 / 平台概览 / 标题 / 封面 / 结构 / 标签 / 痛点 / 数据 / 公式 + 建议 + 附录
- 长度：约 300-500 行

【返回要求】
报告生成完成后：
1. 显示报告路径
2. 列出 5 个核心发现
3. 列出 4 个爆款公式
4. 给出 5 个可立即执行的选题

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 提示：把以上 prompt 复制到 Claude Code 输入框，回车即可触发天龙引擎完整执行。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""


def generate_template_report(keyword: str, platforms: list[dict]) -> str:
    """生成完整报告模板（含占位符）"""
    today = datetime.now().strftime("%Y-%m-%d")
    platform_rows = "\n".join(
        f"| **{p['name']}** | （待填） | （待填） | {p['user_profile']} | {p['preference']} |"
        for p in platforms
    )

    formulas_section = "\n".join(
        f"### 公式 {i+1}：{f['name']}\n\n"
        f"```\n{f['template']}\n```\n\n"
        f"**示例**：{f['example']}\n\n"
        f"**适用平台**：{f['platform']}\n"
        for i, f in enumerate(VIRAL_FORMULAS)
    )

    dimensions_section = "\n".join(
        f"### 维度 {i+1}：{d['name']}\n\n"
        f"```\n" + "\n".join(f"- {p}" for p in d['points']) + "\n```"
        for i, d in enumerate(ANALYSIS_DIMENSIONS)
    )

    return f"""# 「{keyword}」爆款内容分析报告（模板）

> **生成时间**：{today}
> **分析方法**：天龙引擎 /viral 命令 + china-viral-content-analyzer SKILL
> **模式**：template（占位符填充模式）
> **状态**：⏳ 模板已生成，待填充数据

---

## ⚠️ 模板说明

本报告由天龙引擎 `/viral` 命令的模板模式生成。**所有「待填」字段需要你手动填充**。

**填充方式**：
1. 在天龙 CLI 真实环境运行 /viral {keyword}（推荐）→ 自动填充
2. 手动访问 6 大平台 + 搜索 + 复制数据填入下方

---

## 执行摘要（待填）

【请用 3-5 条核心发现总结】

## 一、平台概览

| 平台 | 爆款数 | 平均互动 | 用户特征 | 内容偏好 |
|------|--------|----------|---------|---------|
{platform_rows}

## 二、6 大维度分析框架

{dimensions_section}

## 三、爆款公式总结（5 大公式）

{formulas_section}

## 四、5 个可立即执行的选题

```
选题 1：（待填 - 用公式 1「数字冲击型」）
选题 2：（待填 - 用公式 2「身份代入型」）
选题 3：（待填 - 用公式 3「反常识型」）
选题 4：（待填 - 用公式 4「承诺型」）
选题 5：（待填 - 用公式 5「对比型」）
```

## 五、报告元数据

- 生成时间：{today}
- 使用工具：天龙引擎 /viral 命令（template 模式）
- 数据来源：（待填：手动搜索 / 第三方工具 / 平台 API）
- 填充时间：（待填）
- 置信度：⭐⭐⭐（模板级，待数据填充后升级为 ⭐⭐⭐⭐⭐）

---

## 填充指南（建议 30 分钟完成）

### Step 1：小红书（5 分钟）
打开小红书 App → 搜索「{keyword} 爆款」 → 浏览前 10 条 → 填写数据到平台概览表

### Step 2：抖音（5 分钟）
抖音搜索「{keyword}」 → 切到"综合"→ 找前 10 个高赞视频 → 提取数据

### Step 3：B站（5 分钟）
B站搜索「{keyword} 播放量高」→ 找前 5 个视频 → 提取数据

### Step 4：知乎 + 视频号 + 公众号（10 分钟）
- 知乎搜索「{keyword} 高赞」→ 前 5 个
- 视频号搜一搜「{keyword} 爆款」→ 前 5 个
- 公众号搜狗微信「{keyword}」→ 前 5 篇

### Step 5：6 维度分析（5 分钟）
按维度逐个分析，填写发现

### Step 6：5 个选题（5 分钟）
从发现的爆款公式中，套出 5 个垂类选题

---

## 报告引用

- [[FDE]]
- [[天龙-viral-工作流-SOP]]
- [[天龙-viral-工作流-SOP-V2]]
- [[用户真实需求采集方案]]

## 元数据

- SKILL: china-viral-content-analyzer
- VERSION: 1.0.0
- AUTHOR: 天龙引擎团队
"""


def run_websearch_mode(keyword: str, platforms: list[dict]) -> dict[str, str]:
    """WebSearch 模式：用 curl 调用搜索引擎（仅作为框架占位）"""
    print(f"⚠️  WebSearch 模式：直接调用 web search 在 Windows 环境受网络限制")
    print(f"    仅生成 search 模板，不实际执行（避免 anti-bot）")
    print()

    searches = {}
    for p in platforms:
        searches[p["name"]] = p["query_template"].format(keyword=keyword)

    return searches


def save_report(report_content: str, keyword: str) -> Path:
    """保存报告到 ~/viral-content-reports/{keyword}.md"""
    report_path = REPORTS_DIR / f"{keyword}.md"
    report_path.write_text(report_content, encoding="utf-8")
    return report_path


def main() -> int:
    args = parse_args()

    if not args.keyword:
        print("❌ 缺少关键词")
        print("用法: python scripts/run_viral.py <关键词>")
        return 1

    keyword = args.keyword.strip()
    platforms = filter_platforms(args.platforms)

    # 1. 去重检查
    if not check_dedup(keyword, force=args.force):
        return 1

    # 2. dry-run
    if args.dry_run:
        print(f"🔍 DRY-RUN 模式：{keyword}")
        print(f"   将使用 {len(platforms)} 个平台：{', '.join(p['name'] for p in platforms)}")
        print(f"   模式：{args.mode}")
        return 0

    # 3. 执行
    print(f"\n🚀 天龙 /viral「{keyword}」| 模式：{args.mode}")
    print(f"   平台：{len(platforms)} 个（{', '.join(p['name'] for p in platforms)}）")
    print()

    ensure_output_dirs(keyword)

    # 根据模式执行
    if args.mode == "cli":
        # CLI 模式：生成完整 Prompt（让用户在天龙 CLI 真实环境执行）
        cli_prompt = generate_cli_prompt(keyword, platforms)
        print(cli_prompt)

        # 写一个"任务清单"文件
        task_file = REPORTS_DIR / f".{keyword}.task.md"
        task_file.write_text(
            f"""# /viral {keyword} 任务清单（CLI 模式）

生成时间：{datetime.now().isoformat()}
模式：CLI（推荐）
状态：⏳ 待执行

## 执行步骤

1. 复制上方 Prompt 到 Claude Code / 天龙 CLI 输入框
2. 等待天龙执行完成（预计 5-10 分钟）
3. 检查 ~/viral-content-reports/{keyword}.md 是否生成
4. 用 --force 覆盖或删除本任务文件后重跑

## 关联笔记

- [[天龙-viral-工作流-SOP]]
- [[天龙-viral-工作流-SOP-V2]]
- [[用户真实需求采集方案]]
""",
            encoding="utf-8",
        )
        print(f"\n📝 任务清单已写入 {task_file}")

    elif args.mode == "web":
        # WebSearch 模式：生成查询模板
        searches = run_websearch_mode(keyword, platforms)

        print("🌐 WebSearch 查询模板（手动复制到浏览器执行）:\n")
        for platform, query in searches.items():
            print(f"  [{platform}] https://www.google.com/search?q={query}")
            print()
            print(f"    复制：{query}")
            print()

        # 写一个"查询清单"
        query_file = REPORTS_DIR / f".{keyword}.queries.md"
        with query_file.open("w", encoding="utf-8") as f:
            f.write(f"# /viral {keyword} WebSearch 查询清单\n\n")
            f.write(f"生成时间：{datetime.now().isoformat()}\n\n")
            f.write("## 6 平台查询\n\n")
            for platform, query in searches.items():
                f.write(f"### {platform}\n\n")
                f.write(f"```\n{query}\n```\n\n")
        print(f"📝 查询清单已写入 {query_file}")

    elif args.mode == "template":
        # Template 模式：生成完整报告模板
        report_content = generate_template_report(keyword, platforms)
        report_path = save_report(report_content, keyword)
        print(f"✅ 报告模板已生成：{report_path}")
        print()
        print("📝 模板使用指南：")
        print("   1. 打开报告文件")
        print("   2. 按「填充指南」章节手动搜索 6 大平台数据")
        print("   3. 替换所有「待填」字段")
        print("   4. 30 分钟可完成")

    print()
    print("=" * 60)
    print("✅ 天龙 /viral 执行完成")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())