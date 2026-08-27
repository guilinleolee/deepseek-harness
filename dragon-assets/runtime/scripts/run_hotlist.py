#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_hotlist.py · 天龙引擎 /hotlist 命令包装脚本 V2.0
====================================================

把天龙 skills/aihot + skills/news-free-api + Hacker News 的能力封装为命令行：
- 国内热榜：aihot 今日 AI 热点 + news-free-api 通用新闻（关键词过滤）
- 国外热榜：Hacker News（Algolia API，免费无需 KEY）
- 5 维度评分（相关性/热度/新鲜度/可落地/可读性）
- 关键词管理（按栏目持久化到 keywords.json，参与相关性评分）
- 输出 JSON + Markdown 报告（按栏目归档）
- 集成天龙 hooks（hotlist-archiver 自动归档）

调用：
    python scripts/run_hotlist.py
    python scripts/run_hotlist.py --category international
    python scripts/run_hotlist.py --days 7
    python scripts/run_hotlist.py --limit 20
    python scripts/run_hotlist.py --keyword "AI 训练师"
    python scripts/run_hotlist.py --json
    python scripts/run_hotlist.py --list-keywords
    python scripts/run_hotlist.py --add-keyword "抖店 AI 客服" --category domestic
    python scripts/run_hotlist.py --remove-keyword "抖店 AI 客服" --category domestic

输出：
    ~/viral-content-reports/hotlist/{domestic|international}/YYYY-MM-DD.md
    ~/viral-content-reports/hotlist/{domestic|international}/index.md
    ~/viral-content-reports/hotlist/keywords.json

仅用 Python 标准库（argparse / urllib / json / re）。
要求 Python ≥ 3.8。
"""
from __future__ import annotations

import argparse
import sys
import os
import json
import urllib.request
import urllib.error
import re
from pathlib import Path
from datetime import datetime, timezone

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
    try:
        home = Path.home()
        if home and home.exists():
            return home
    except (RuntimeError, ValueError):
        pass
    for env_var in ["USERPROFILE", "HOME", "TEMP"]:
        val = os.environ.get(env_var)
        if val and Path(val).exists():
            return Path(val)
    fallback = Path("C:/Users/li")
    if fallback.exists():
        return fallback
    return Path("C:/Windows/Temp")


HOME_DIR = _get_home_dir()
REPORTS_DIR = HOME_DIR / "viral-content-reports"
HOTLIST_DIR = REPORTS_DIR / "hotlist"
KEYWORDS_FILE = HOTLIST_DIR / "keywords.json"

# ============================================
# 栏目定义（V2.0 双栏目）
# ============================================
CATEGORIES = {
    "domestic": {
        "label": "🇨🇳 国内",
        "desc": "DailyHotApi 多平台热榜聚合（微博/知乎/百度/抖音等）",
        "platforms": [
            {"name": "dailyhot", "desc": "本地 DailyHotApi 聚合：微博/知乎/百度/抖音/头条/B站/36氪/虎嗅/掘金/澎湃", "enabled": True},
            {"name": "aihot", "desc": "AI 领域聚合（今日 AI 热点，免费 600 req/min）", "enabled": True},
            {"name": "news-free-api", "desc": "通用新闻（需 NEWS_API_KEY 环境变量）", "enabled": False},
        ],
    },
    "international": {
        "label": "🌍 国外",
        "desc": "Hacker News 英文科技热点（Algolia API，免费无需 KEY）",
        "platforms": [
            {"name": "hacker-news", "desc": "Hacker News 头条+Ask HN+Show HN（Algolia，免费无需 KEY）", "enabled": True},
            {"name": "news-free-api", "desc": "通用新闻（需 NEWS_API_KEY 环境变量）", "enabled": False},
        ],
    },
}

# ============================================
# DailyHotApi 本地服务（V2.2 接入）
# ============================================
DAILYHOT_BASE = "http://localhost:6688"
# 国内栏目聚合的平台（DailyHotApi 调用名）
DAILYHOT_PLATFORMS = [
    ("weibo", "微博热搜"),
    ("zhihu", "知乎热榜"),
    ("baidu", "百度热搜"),
    ("douyin", "抖音热点"),
    ("toutiao", "今日头条"),
    ("bilibili", "B站热门"),
    ("36kr", "36氪"),
    ("huxiu", "虎嗅"),
    ("juejin", "掘金"),
    ("thepaper", "澎湃新闻"),
]

# AI 训练师相关业务关键词（用于相关性评分）
BUSINESS_KEYWORDS = [
    "AI 训练师", "AI 客服", "Coze", "Dify", "豆包", "DeepSeek", "Claude",
    "智能体", "Agent", "工作R", "知识库", "RAG", "LLM",
    "中小企业", "超级个体", "陪跑", "训练营", "数字人",
    "抖音", "小红书", "公众号", "视频号", "知乎",
    "GEO", "SEO", "小程序", "电商", "直播",
    "创业", "副业", "一人公司", "自由职业",
    "降本增效", "自动化", "效率", "AI 提效",
]

# ============================================
# 用户自定义关键词管理（V2.0 新增）
# ============================================
def _load_keywords() -> dict[str, list[str]]:
    """读取关键词配置（{category: [keyword, ...]}）"""
    if KEYWORDS_FILE.exists():
        try:
            data = json.loads(KEYWORDS_FILE.read_text(encoding="utf-8"))
            return {cat: list(data.get(cat, [])) for cat in CATEGORIES}
        except (json.JSONDecodeError, OSError):
            pass
    return {cat: [] for cat in CATEGORIES}


def _save_keywords(data: dict[str, list[str]]) -> None:
    """保存关键词配置"""
    HOTLIST_DIR.mkdir(parents=True, exist_ok=True)
    KEYWORDS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_user_keywords(category: str) -> list[str]:
    """获取某栏目的用户关键词（去重，保留顺序）"""
    data = _load_keywords()
    return data.get(category, [])


def effective_keywords(category: str) -> list[str]:
    """合并业务关键词 + 用户关键词（评分用）"""
    return BUSINESS_KEYWORDS + get_user_keywords(category)


def cmd_add_keyword(keyword: str, category: str) -> int:
    """添加用户关键词"""
    kw = keyword.strip()
    if not kw:
        print(f"❌ 关键词不能为空")
        return 1
    data = _load_keywords()
    if kw not in data[category]:
        data[category].append(kw)
        _save_keywords(data)
        print(f"✅ 已添加关键词「{kw}」到「{CATEGORIES[category]['label']}」")
    else:
        print(f"ℹ️ 关键词「{kw}」已存在，无需重复添加")
    print(f"   当前「{CATEGORIES[category]['label']}」关键词：{get_user_keywords(category)}")
    return 0


def cmd_remove_keyword(keyword: str, category: str) -> int:
    """删除用户关键词"""
    data = _load_keywords()
    kw = keyword.strip()
    if kw in data[category]:
        data[category].remove(kw)
        _save_keywords(data)
        print(f"✅ 已删除关键词「{kw}」")
    else:
        print(f"ℹ️ 关键词「{kw}」不存在（当前：{get_user_keywords(category)}）")
    return 0


def cmd_list_keywords() -> int:
    """列出所有栏目的用户关键词"""
    data = _load_keywords()
    print(f"🔑 用户自定义关键词（{KEYWORDS_FILE}）")
    for cat in CATEGORIES:
        kws = data.get(cat, [])
        print(f"  {CATEGORIES[cat]['label']}（{len(kws)} 个）：{kws if kws else '（空）'}")
    return 0


# ============================================
# 数据源 0：DailyHotApi（本地多平台热榜聚合）
# ============================================
def dailyhot_alive() -> bool:
    """检查本地 DailyHotApi 服务是否在运行"""
    try:
        req = urllib.request.Request(DAILYHOT_BASE + "/weibo", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("code") == 200
    except Exception:
        return False


def fetch_dailyhot(limit: int = 20) -> list[dict]:
    """从本地 DailyHotApi 拉取多平台热榜（微博/知乎/百度/抖音等）"""
    items = []
    for call, name in DAILYHOT_PLATFORMS:
        try:
            req = urllib.request.Request(
                f"{DAILYHOT_BASE}/{call}",
                headers={"User-Agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            for it in data.get("data", [])[:limit]:
                hot = it.get("hot", 0)
                items.append({
                    "title": it.get("title", ""),
                    "desc": it.get("desc", "") or (f"{name}热度 {hot}" if hot else ""),
                    "url": it.get("url", ""),
                    "source": name,
                    # timestamp 是毫秒，转成秒
                    "ct": (it.get("timestamp", 0) or 0) // 1000,
                    "category": "domestic",
                    "source_type": "dailyhot",
                    "hot": hot,
                })
        except Exception as e:
            print(f"      ⚠️ {name} 抓取失败: {str(e)[:60]}")
    return items


# ============================================
# 数据源 1：aihot API（中文 AI 领域）
# ============================================
def fetch_aihot(days: int = 1, category: str = None) -> list[dict]:
    """从 aihot.virxact.com 抓取今日 AI 热点"""
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    url = "https://aihot.virxact.com/api/public/daily"
    if days > 1:
        url = f"https://aihot.virxact.com/api/public/dailies?days={days}"

    items = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        # aihot 实际返回结构：
        # {"date": "...", "sections": [{"label": "...", "items": [...]}, ...]}
        if isinstance(data, dict) and "sections" in data:
            for section in data["sections"]:
                section_label = section.get("label", "general")
                for it in section.get("items", []):
                    items.append({
                        "title": it.get("title", ""),
                        "desc": it.get("summary", "") or it.get("desc", ""),
                        "url": it.get("sourceUrl", "") or it.get("url", ""),
                        "source": it.get("sourceName", "") or it.get("source", "aihot"),
                        # 时间戳：尝试从 generatedAt / date / ct 中提取
                        "ct": _parse_aihot_timestamp(it, data),
                        "category": section_label,
                        "source_type": "aihot",
                    })
        elif isinstance(data, list):
            # 兼容老格式
            for it in data:
                items.append({
                    "title": it.get("title", ""),
                    "desc": it.get("desc", "") or it.get("summary", ""),
                    "url": it.get("url", "") or it.get("sourceUrl", ""),
                    "source": it.get("source", "aihot"),
                    "ct": it.get("ct", 0),
                    "category": it.get("category", "ai-general"),
                    "source_type": "aihot",
                })

        return items
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError) as e:
        print(f"[!] aihot API 调用失败: {e}")
        return []


def _parse_aihot_timestamp(item: dict, data: dict) -> int:
    """从 aihot 返回提取时间戳（fallback 链）"""
    # 1. 优先用 item.ct
    if item.get("ct"):
        return int(item["ct"])

    # 2. 尝试从 generatedAt 推断（数据生成时间）
    gen = data.get("generatedAt", "")
    if gen:
        try:
            dt = datetime.fromisoformat(gen.replace("Z", "+00:00"))
            return int(dt.timestamp())
        except (ValueError, TypeError):
            pass

    # 3. 尝试从 data.date 推断（数据日期）
    date = data.get("date", "")
    if date:
        try:
            dt = datetime.fromisoformat(date + "T00:00:00+00:00")
            return int(dt.timestamp())
        except (ValueError, TypeError):
            pass

    return 0


# ============================================
# 数据源 2：news-free-api（通用新闻）
# ============================================
def fetch_news_free(keyword: str = "AI") -> list[dict]:
    """从 news-free-api 抓取新闻（注意：需要 Key 才能跑）"""
    # news-free-api 通常需要 NEWS_API_KEY（SKILL.md 说明）
    # 没有 Key 时返回空 list，让 aihot 成为主数据源
    api_key = os.environ.get("NEWS_API_KEY")
    if not api_key:
        return []  # 静默跳过

    url = f"https://newsapi.org/v2/everything?q={keyword}&pageSize=20&apiKey={api_key}"
    items = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for it in data.get("articles", []):
                items.append({
                    "title": it.get("title", ""),
                    "desc": it.get("description", ""),
                    "url": it.get("url", ""),
                    "source": it.get("source", {}).get("name", "news-api"),
                    "ct": int(datetime.fromisoformat(
                        it.get("publishedAt", "").replace("Z", "+00:00")
                    ).timestamp()) if it.get("publishedAt") else 0,
                    "category": "general",
                    "source_type": "news-free-api",
                })
        return items
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
        print(f"[!] news-free-api 调用失败: {e}")
        return []


# ============================================
# 数据源 3：Hacker News（Algolia API，免费无需 KEY）
# ============================================
def fetch_hackernews() -> list[dict]:
    """从 Algolia HN API 抓取 Hacker News 英文科技热点"""
    # Algolia HN Search API：search_by_date 按发布时间排序（最近热门）
    # 加 numericFilters=points>100 过滤掉低热度条目
    url = (
        "https://hn.algolia.com/api/v1/search_by_date"
        "?tags=story"
        "&numericFilters=points>100"
        "&hitsPerPage=60"
    )
    items = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        for it in data.get("hits", []):
            # objectID 即 HN 条目 ID，可直接拼出新闻页 URL
            object_id = it.get("objectID", "")
            items.append({
                "title": it.get("title", ""),
                "desc": it.get("story_text", "") or it.get("comment_text", "") or "",
                # 有外部链接用外链，否则用 HN 讨论页
                "url": it.get("url", "") or f"https://news.ycombinator.com/item?id={object_id}",
                "source": it.get("author", "HN") or "HN",
                "ct": int(it.get("created_at_i", 0)),
                "category": it.get("_tags", ["hn"])[0] if it.get("_tags") else "hn",
                "source_type": "hacker-news",
                "points": it.get("points", 0),
                "comments": it.get("num_comments", 0),
            })
        return items
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
        print(f"[!] Hacker News 调用失败: {e}")
        return []


# ============================================
# 5 维度评分算法
# ============================================
def score_relevance(item: dict, business_keywords: list[str]) -> float:
    """相关性（0-100）：标题+描述中业务关键词的命中数"""
    text = (item.get("title", "") + " " + item.get("desc", "")).lower()
    hits = sum(1 for kw in business_keywords if kw.lower() in text)
    # 1-3 个命中：30-60 分；4+ 个命中：70-100 分
    if hits == 0:
        return 20
    elif hits == 1:
        return 40
    elif hits == 2:
        return 60
    elif hits == 3:
        return 75
    else:
        return min(95, 70 + hits * 5)


def score_hotness(item: dict) -> float:
    """热度（0-100）：基于来源权威性 + HN points + DailyHotApi hot"""
    source_score = {
        "OpenAI官方": 100, "Google AI": 95, "Microsoft": 90, "Anthropic": 90,
        "aihot": 70, "机器之心": 85, "量子位": 85, "36氪": 80,
        "infoq": 75, "虎嗅": 75,
    }
    src = item.get("source", "")
    base = source_score.get(src, 60)
    # Hacker News：按 points 加成（100+ 分 => +20 封顶）
    if item.get("source_type") == "hacker-news":
        points = item.get("points", 0)
        base = 55 + min(35, points // 10)
    # DailyHotApi：按各平台热度值归一化加成（热度值越大越高）
    elif item.get("source_type") == "dailyhot":
        hot = item.get("hot", 0)
        if hot:
            # 热度值差异大（微博热度可达 1000万+），用对数压缩到 0-25
            import math
            base = min(90, base + int(math.log10(max(hot, 1)) * 5))
    # 标题越长通常信息量越大
    title_len = len(item.get("title", ""))
    title_bonus = min(15, title_len // 4)
    return min(100, base + title_bonus)


def score_freshness(item: dict) -> float:
    """新鲜度（0-100）：基于发布时间"""
    ct = item.get("ct", 0)
    if ct == 0:
        return 50
    now = datetime.now(timezone.utc).timestamp()
    age_hours = (now - ct) / 3600
    if age_hours < 6:
        return 100
    elif age_hours < 24:
        return 90
    elif age_hours < 72:
        return 75
    elif age_hours < 168:  # 7 天
        return 60
    else:
        return 40


def score_actionable(item: dict) -> float:
    """可落地（0-100）：能否转化为 AI 训练师相关选题"""
    title = item.get("title", "").lower()
    desc = item.get("desc", "").lower()
    text = title + " " + desc
    # 高分关键词：发布/更新/融资/工具/教程/开源
    high = ["发布", "更新", "开源", "融资", "工具", "教程", "推出", "功能"]
    # 中分关键词：评测/对比/趋势/分析
    mid = ["评测", "对比", "趋势", "分析", "增长", "应用"]
    score = 50  # 基础分
    score += sum(10 for kw in high if kw in text)
    score += sum(5 for kw in mid if kw in text)
    return min(100, score)


def score_readability(item: dict) -> float:
    """可读性（0-100）：基于标题字数+描述完整度"""
    title = item.get("title", "")
    desc = item.get("desc", "")
    # 标题 15-25 字最佳
    title_len = len(title)
    if 15 <= title_len <= 25:
        title_score = 90
    elif 10 <= title_len <= 30:
        title_score = 75
    else:
        title_score = 50
    # 描述 30-150 字最佳
    desc_len = len(desc)
    if 30 <= desc_len <= 150:
        desc_score = 90
    elif desc_len > 0:
        desc_score = 70
    else:
        desc_score = 50
    return (title_score + desc_score) // 2


def score_item(item: dict, business_keywords: list[str]) -> dict:
    """综合评分（5 维度加权）"""
    s_rel = score_relevance(item, business_keywords)
    s_hot = score_hotness(item)
    s_new = score_freshness(item)
    s_act = score_actionable(item)
    s_read = score_readability(item)

    # 权重：相关性 30 + 热度 25 + 新鲜度 20 + 可落地 15 + 可读性 10 = 100
    total = (
        s_rel * 0.30
        + s_hot * 0.25
        + s_new * 0.20
        + s_act * 0.15
        + s_read * 0.10
    )

    return {
        "title": item.get("title", ""),
        "desc": item.get("desc", ""),
        "url": item.get("url", ""),
        "source": item.get("source", ""),
        "ct": item.get("ct", 0),
        "category": item.get("category", "general"),
        "source_type": item.get("source_type", ""),
        "points": item.get("points", 0),
        "comments": item.get("comments", 0),
        "scores": {
            "relevance": round(s_rel, 1),
            "hotness": round(s_hot, 1),
            "freshness": round(s_new, 1),
            "actionable": round(s_act, 1),
            "readability": round(s_read, 1),
        },
        "total_score": round(total, 1),
    }


# ============================================
# 报告生成
# ============================================
def generate_markdown_report(items: list[dict], date_str: str, category: str = "domestic",
                             user_keywords: list[str] = None) -> str:
    """生成 Markdown 报告"""
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cat_label = CATEGORIES[category]["label"]
    platforms_desc = " + ".join(p["name"] for p in CATEGORIES[category]["platforms"] if p["enabled"])
    kw_line = f"\n> 用户关键词：{user_keywords}" if user_keywords else ""

    md = f"""# 今日热榜 · {cat_label}（{date_str}）

> 自动抓取 · 抓取时间：{today}
> 栏目：{cat_label} | 数据源：{platforms_desc}
> 评分模型：5 维度加权（相关性 30% + 热度 25% + 新鲜度 20% + 可落地 15% + 可读性 10%）
> 共 {len(items)} 条，按综合评分降序
{kw_line}

---

## 🏆 TOP 10 必看

| 排名 | 标题 | 总分 | 相关 | 热新 | 可落 | 来源 |
|---|---|---|---|---|---|---|
"""

    # 按总分排序
    sorted_items = sorted(items, key=lambda x: x["total_score"], reverse=True)
    top10 = sorted_items[:10]

    for i, item in enumerate(top10, 1):
        title = item["title"][:30] + ("..." if len(item["title"]) > 30 else "")
        sc = item["scores"]
        md += f"| {i} | [{title}]({item['url']}) | **{item['total_score']}** | {sc['relevance']} | {sc['hotness']}/{sc['freshness']} | {sc['actionable']} | {item['source']} |\n"

    md += "\n---\n\n## 📊 全部热榜（按分组）\n\n"

    # 按分数段分组
    high_score = [x for x in sorted_items if x["total_score"] >= 70]
    mid_score = [x for x in sorted_items if 50 <= x["total_score"] < 70]
    low_score = [x for x in sorted_items if x["total_score"] < 50]

    md += f"### ⭐ 高分（≥70）— {len(high_score)} 条\n\n"
    for item in high_score:
        md += format_item_md(item)
    md += f"\n### 📝 中分（50-69）— {len(mid_score)} 条\n\n"
    for item in mid_score[:20]:  # 限 20 条
        md += format_item_md(item)
    if low_score:
        md += f"\n### 📋 低分（<50）— {len(low_score)} 条\n\n"
        md += "_略，详见 JSON 文件_\n"

    md += "\n---\n\n## 📈 统计\n\n"
    md += f"- 数据源分布：\n"
    sources = {}
    for it in items:
        s = it.get("source_type", "unknown")
        sources[s] = sources.get(s, 0) + 1
    for s, n in sources.items():
        md += f"  - {s}: {n} 条\n"
    md += f"\n- 平均分：{sum(x['total_score'] for x in items) / max(len(items), 1):.1f}\n"
    md += f"- 最高分：{max((x['total_score'] for x in items), default=0):.1f}\n"
    md += f"- 最低分：{min((x['total_score'] for x in items), default=0):.1f}\n"

    md += "\n---\n\n## 🔗 反向链接\n\n- [[FDE]]\n- [[天龙-viral-工作流-SOP-V2]]\n- [[天龙UI-Streamlit方案]]\n"
    return md


def format_item_md(item: dict) -> str:
    """格式化单条热榜"""
    sc = item["scores"]
    ct_str = (
        datetime.fromtimestamp(item["ct"], tz=timezone.utc).strftime("%m-%d %H:%M")
        if item["ct"] else "未知"
    )
    # Hacker News 附加信息：points / comments
    hn_extra = ""
    if item.get("source_type") == "hacker-news":
        hn_extra = f" | 🔺{item.get('points', 0)}pts | 💬{item.get('comments', 0)}"
    md = f"""### [{item['title']}]({item['url']})

> **总分：{item['total_score']}** | 相关 {sc['relevance']} | 热 {sc['hotness']} | 新 {sc['freshness']} | 可落 {sc['actionable']} | 可读 {sc['readability']} | {item['source']} | {ct_str}{hn_extra}

{item['desc']}

"""
    return md


def update_index(items: list[dict], date_str: str, category: str = "domestic") -> None:
    """更新栏目 index.md 索引（按栏目归档）"""
    cat_dir = HOTLIST_DIR / category
    cat_dir.mkdir(parents=True, exist_ok=True)
    index_path = cat_dir / "index.md"

    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
    else:
        content = f"""# 天龙今日热榜索引 · {CATEGORIES[category]['label']}

> 按日期归档{category}栏目热榜报告

## 历史报告

"""

    new_entry = f"- [{date_str}](./{date_str}.md) — {len(items)} 条\n"
    if new_entry not in content:
        content += new_entry
        index_path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="天龙引擎 /hotlist 命令（国内/国外 AI 热榜 + 5 维度评分 + 关键词管理）"
    )
    parser.add_argument("--category", choices=list(CATEGORIES.keys()), default="domestic",
                        help="栏目：domestic 国内 / international 国外（默认 domestic）")
    parser.add_argument("--days", type=int, default=1, help="抓取最近 N 天")
    parser.add_argument("--limit", type=int, default=30, help="返回条数限制")
    parser.add_argument("--keyword", default="AI", help="新闻关键词过滤（news-free-api 用）")
    parser.add_argument("--json", action="store_true", help="仅输出 JSON")
    # 关键词管理子命令
    parser.add_argument("--list-keywords", action="store_true", help="列出所有用户关键词")
    parser.add_argument("--add-keyword", help="添加用户关键词（配合 --category）")
    parser.add_argument("--remove-keyword", help="删除用户关键词（配合 --category）")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # 关键词管理子命令：独立处理
    if args.list_keywords:
        return cmd_list_keywords()
    if args.add_keyword:
        return cmd_add_keyword(args.add_keyword, args.category)
    if args.remove_keyword:
        return cmd_remove_keyword(args.remove_keyword, args.category)

    category = args.category
    cat_label = CATEGORIES[category]["label"]
    user_kws = get_user_keywords(category)

    print(f"\n🔥 天龙 /hotlist：今日热榜 · {cat_label}")
    print(f"   days: {args.days} | limit: {args.limit} | 用户关键词: {user_kws or '（无）'}\n")

    # 1. 抓取数据（按栏目选数据源）
    all_items = []
    if category == "domestic":
        # 优先用本地 DailyHotApi（多平台聚合），服务未启动则回退 aihot
        if dailyhot_alive():
            print(f"📡 抓取 DailyHotApi 多平台热榜（{DAILYHOT_BASE}）...")
            dh_items = fetch_dailyhot(limit=args.limit)
            print(f"   ✅ DailyHotApi: {len(dh_items)} 条（{len(DAILYHOT_PLATFORMS)} 个平台）")
            all_items.extend(dh_items)
        else:
            print("⚠️  本地 DailyHotApi 未启动，回退到 aihot（提示：双击 third-party/start-dailyhot.bat 可启动）")
            print("📡 抓取 aihot 数据...")
            aihot_items = fetch_aihot(days=args.days)
            print(f"   ✅ aihot: {len(aihot_items)} 条")
            all_items.extend(aihot_items)

        print("📡 抓取 news-free-api 数据...")
        nf_items = fetch_news_free(keyword=args.keyword)
        print(f"   ✅ news-free-api: {len(nf_items)} 条")
        all_items.extend(nf_items)
    else:  # international
        print("📡 抓取 Hacker News 数据...")
        hn_items = fetch_hackernews()
        print(f"   ✅ hacker-news: {len(hn_items)} 条")
        all_items.extend(hn_items)

        print("📡 抓取 news-free-api 数据...")
        nf_items = fetch_news_free(keyword=args.keyword)
        print(f"   ✅ news-free-api: {len(nf_items)} 条")
        all_items.extend(nf_items)

    print(f"\n📊 原始数据：{len(all_items)} 条")

    # 2. 评分（使用业务关键词 + 用户关键词）
    print("🎯 5 维度评分中...")
    keywords = effective_keywords(category)
    scored = [score_item(it, keywords) for it in all_items]
    scored.sort(key=lambda x: x["total_score"], reverse=True)
    scored = scored[:args.limit]
    print(f"   ✅ 评分完成，返回 TOP {len(scored)} 条\n")

    # 3. 输出
    if args.json:
        print(json.dumps(scored, ensure_ascii=False, indent=2))
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
        # 输出表格
        for item in scored[:20]:
            sc = item["scores"]
            title_short = item["title"][:35] + ("..." if len(item["title"]) > 35 else "")
            print(f"  [{item['total_score']:5.1f}] {title_short}")
            print(f"         相关 {sc['relevance']} | 热 {sc['hotness']} | 新 {sc['freshness']} | 可落 {sc['actionable']} | {item['source']}")
            print()

        # 保存报告（按栏目归档）
        cat_dir = HOTLIST_DIR / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        report_path = cat_dir / f"{date_str}.md"
        report_content = generate_markdown_report(scored, date_str, category, user_kws)
        report_path.write_text(report_content, encoding="utf-8")
        print(f"📄 Markdown 报告：{report_path}")

        # 保存 JSON
        json_path = cat_dir / f"{date_str}.json"
        json_path.write_text(
            json.dumps(scored, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"📄 JSON 数据：{json_path}")

        # 更新索引
        update_index(scored, date_str, category)
        print(f"📄 索引更新：{cat_dir / 'index.md'}")

    print()
    print("=" * 60)
    print(f"✅ 天龙 /hotlist（{cat_label}）执行完成")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())