#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_keywords_index.py · 天龙引擎 行业关键词数据 命令 V1.2
========================================================

输入一个关键词，查询各平台指数/热度数据：
- 百度热榜（免费）：该关键词是否上榜 + 排名 + 热度档位
- 头条热榜（免费）：是否上榜 + 排名 + 热度值
- 百度联想词（免费）：相关搜索词
- 必应联想词（免费）：相关搜索词
- 抖音指数（原巨量算数）：直达链接 + 关联词抓取（需企业账号）
- 百度指数：直达链接
- 谷歌趋势：直达链接

V1.2 新增：
- 巨量算数已升级为「抖音指数」，更新直达链接
- 新增头条搜索联想词
- 新增抖音搜索联想词（需登录）

调用：
    python scripts/run_keywords_index.py "AI训练师"
    python scripts/run_keywords_index.py "智能客服" --json
    python scripts/run_keywords_index.py "Coze" --no-save

输出：
    ~/viral-content-reports/keywords-index/{keyword}.md
    ~/viral-content-reports/keywords-index/{keyword}.json

仅用 Python 标准库（argparse / urllib / json / re）。
要求 Python ≥ 3.8。
"""
from __future__ import annotations

import argparse
import sys
import os
import json
import re
import urllib.request
import urllib.error
import urllib.parse
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
REPORTS_DIR = HOME_DIR / "viral-content-reports"
INDEX_DIR = REPORTS_DIR / "keywords-index"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


# ============================================
# 官方指数直达链接（V1.2 更新：巨量算数→抖音指数）
# ============================================
def official_links(keyword: str) -> list[dict]:
    """生成官方指数查询链接（用户点开自行查看）"""
    kw = urllib.parse.quote(keyword)
    kw_zh = urllib.parse.quote(keyword.encode('utf-8'))  # 中文 URL 编码
    return [
        {
            "name": "抖音指数",
            "name_cn": "抖音指数（原巨量算数）",
            "url": f"https://trendinsight.oceanengine.com/arithmetic-index/analysis?keyword={kw}",
            "need": "需抖音创作者账号授权",
            "desc": "抖音搜索指数 + 关联词分析 + 人群画像",
            "icon": "🎵",
        },
        {
            "name": "百度指数",
            "name_cn": "百度指数",
            "url": f"https://index.baidu.com/v2/index.html#/?words={kw}",
            "need": "需登录百度账号",
            "desc": "百度搜索指数 + 资讯指数 + 人群画像",
            "icon": "🔍",
        },
        {
            "name": "微信指数",
            "name_cn": "微信指数",
            "url": "https://weixin.qq.com/cgi-bin/readtemplate?t=weixin_search_index",
            "need": "需微信公众号授权",
            "desc": "微信搜索指数（需公众号权限）",
            "icon": "💬",
        },
        {
            "name": "谷歌趋势",
            "name_cn": "Google Trends",
            "url": f"https://trends.google.com/trends/explore?q={kw}&geo=CN",
            "need": "需访问 Google（网络限制）",
            "desc": "全球搜索趋势对比",
            "icon": "🌐",
        },
    ]


# ============================================
# 数据源 1：百度热榜
# ============================================
def fetch_baidu_hot() -> list[dict]:
    """抓取百度实时热榜，返回 [{word, rank, hot_tag, url}]"""
    url = "https://top.baidu.com/api/board?platform=wise&tab=realtime"
    items = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        cards = data.get("data", {}).get("cards", [])
        for card in cards:
            for block in card.get("content", []):
                inner = block.get("content", [])
                if isinstance(inner, list):
                    for rank, it in enumerate(inner, 1):
                        items.append({
                            "word": it.get("word", ""),
                            "rank": rank,
                            "hot_tag": it.get("hotTag", ""),
                            "url": it.get("url", ""),
                        })
        return items
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError) as e:
        print(f"[!] 百度热榜抓取失败: {e}")
        return []


# ============================================
# 数据源 2：头条热榜
# ============================================
def fetch_toutiao_hot() -> list[dict]:
    """抓取头条热榜，返回 [{word, rank, hot_value, url}]"""
    url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
    items = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        for rank, it in enumerate(data.get("data", []), 1):
            items.append({
                "word": it.get("Title", ""),
                "rank": rank,
                "hot_value": it.get("HotValue", 0),
                "url": it.get("Url", ""),
            })
        return items
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError) as e:
        print(f"[!] 头条热榜抓取失败: {e}")
        return []


# ============================================
# 数据源 3/4：搜索联想词
# ============================================
def fetch_baidu_suggest(keyword: str) -> list[str]:
    """百度搜索联想词"""
    kw = urllib.parse.quote(keyword)
    url = f"https://suggestion.baidu.com/su?wd={kw}&json=1"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read()
        # 百度 suggest 返回 GBK 编码（偶尔 UTF-8），做编码容错
        text = None
        for enc in ("utf-8", "gbk"):
            try:
                text = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        if text is None:
            return []
        # 返回 window.baidu.sug({...})，用正则提取 g 数组
        m = re.search(r'window\.baidu\.sug\((.*)\)', text, re.DOTALL)
        if m:
            data = json.loads(m.group(1))
            return [g.get("q", "") for g in data.get("g", []) if g.get("q")]
        return []
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError) as e:
        print(f"[!] 百度联想词抓取失败: {e}")
        return []


def fetch_bing_suggest(keyword: str) -> list[str]:
    """必应搜索联想词"""
    kw = urllib.parse.quote(keyword)
    url = f"https://api.bing.com/osjson.aspx?query={kw}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return list(data[1]) if len(data) > 1 else []
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError) as e:
        print(f"[!] 必应联想词抓取失败: {e}")
        return []


# ============================================
# V1.2 新增数据源
# ============================================

def fetch_toutiao_suggest(keyword: str) -> list[str]:
    """头条搜索联想词（巨量算数替代数据源）"""
    kw = urllib.parse.quote(keyword)
    # 头条搜索建议接口
    url = f"https://www.toutiao.com/api/pc/feed/?keyword={kw}&pd=synthesis&source=input&callback=json"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Referer": "https://www.toutiao.com/",
            "Accept": "*/*",
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        # 提取 JSON 数据
        m = re.search(r'json\((.*?)\)$', raw, re.DOTALL)
        if m:
            data = json.loads(m.group(1))
            suggestions = []
            for item in data.get("data", []):
                if isinstance(item, dict):
                    suggestions.append(item.get("keyword", ""))
                elif isinstance(item, str):
                    suggestions.append(item)
            return [s for s in suggestions if s][:10]
        return []
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError) as e:
        print(f"[!] 头条联想词抓取失败: {e}")
        return []


def fetch_douyin_index(keyword: str) -> dict:
    """
    获取抖音指数/巨量算数数据

    注意：巨量算数已升级为「抖音指数」，需要登录抖音创作者中心才能查看详细数据。
    此函数尝试抓取公开可用的关联词数据，如果失败则返回直达链接提示。

    返回：
        {
            "status": "success" | "login_required" | "error",
            "related_words": [],  # 关联词
            "hot_trends": [],     # 热门话题
            "direct_url": str,    # 直达链接
            "message": str,       # 状态消息
        }
    """
    kw = urllib.parse.quote(keyword)
    result = {
        "status": "unknown",
        "related_words": [],
        "hot_trends": [],
        "direct_url": f"https://trendinsight.oceanengine.com/arithmetic-index/analysis?keyword={kw}",
        "message": "",
    }

    # 尝试抖音搜索建议接口（部分公开）
    douyin_suggest_url = f"https://www.douyin.com/aweme/v1/web/search/sug/?keyword={kw}&count=10"
    try:
        req = urllib.request.Request(douyin_suggest_url, headers={
            "User-Agent": UA,
            "Referer": "https://www.douyin.com/",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("status_code") == 0:
            sug_list = data.get("sug_list", [])
            if sug_list:
                result["status"] = "success"
                result["related_words"] = [s.get("sug_word", "") for s in sug_list if isinstance(s, dict)]
                result["message"] = f"获取到 {len(result['related_words'])} 条抖音搜索建议"
            else:
                result["status"] = "login_required"
                result["message"] = "抖音搜索建议需要登录账号"
        else:
            result["status"] = "login_required"
            result["message"] = f"抖音接口状态码: {data.get('status_code')}，需要登录"

    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, OSError) as e:
        result["status"] = "error"
        result["message"] = f"抓取失败: {str(e)[:50]}"

    return result


def fetch_baidu_index_data(keyword: str) -> dict:
    """
    获取百度指数数据

    注意：百度指数需要登录才能查看详细数据。
    此函数尝试抓取公开可用的数据，如果失败则返回直达链接提示。

    返回：
        {
            "status": "success" | "login_required" | "error",
            "index_value": int,       # 搜索指数
            "related_words": [],       # 相关词
            "trend_direction": str,    # 趋势方向
            "direct_url": str,        # 直达链接
            "message": str,           # 状态消息
        }
    """
    kw = urllib.parse.quote(keyword)
    result = {
        "status": "unknown",
        "index_value": None,
        "related_words": [],
        "trend_direction": "",
        "direct_url": f"https://index.baidu.com/v2/index.html#/?words={kw}",
        "message": "",
    }

    # 百度搜索下拉词（可作为相关词参考）
    baidu_sug = fetch_baidu_suggest(keyword)
    if baidu_sug:
        result["status"] = "success"
        result["related_words"] = baidu_sug[:5]
        result["message"] = "百度搜索建议（完整指数需登录）"
    else:
        result["status"] = "login_required"
        result["message"] = "获取百度指数需要登录百度账号"

    return result


# ============================================
# 匹配：关键词是否在热榜上
# ============================================
def match_hotlist(keyword: str, hotlist: list[dict]) -> dict | None:
    """在热榜中精确/模糊匹配关键词"""
    kw_low = keyword.lower()
    for it in hotlist:
        word = it.get("word", "")
        if not word:
            continue
        # 精确匹配优先，其次包含匹配
        if word.lower() == kw_low or (kw_low in word.lower() and len(kw_low) >= 2):
            return it
    return None


# ============================================
# 报告生成
# ============================================
def generate_report(keyword: str, result: dict) -> str:
    """生成 Markdown 报告"""
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    kw = keyword

    # 热榜命中情况
    bd = result["baidu_hot"]
    tt = result["toutiao_hot"]
    bd_line = f"🏅 百度热榜 **第 {bd['rank']} 名**（热度档 {bd['hot_tag']}）" if bd else "❌ 未上榜"
    tt_line = f"🏅 头条热榜 **第 {tt['rank']} 名**（热度 {tt['hot_value']:,}）" if tt else "❌ 未上榜"

    # 联想词
    bd_sugg = result["baidu_suggest"]
    tt_sugg = result["bing_suggest"]
    toutiao_sugg = result.get("toutiao_suggest", [])
    douyin_data = result.get("douyin_index", {})
    baidu_index = result.get("baidu_index", {})

    bd_sugg_md = "\n".join(f"- {s}" for s in bd_sugg) if bd_sugg else "- （无）"
    bing_sugg_md = "\n".join(f"- {s}" for s in tt_sugg) if tt_sugg else "- （无）"
    toutiao_sugg_md = "\n".join(f"- {s}" for s in toutiao_sugg) if toutiao_sugg else "- （无）"

    # 抖音指数数据
    douyin_words = douyin_data.get("related_words", [])
    douyin_status = douyin_data.get("status", "unknown")
    douyin_msg = douyin_data.get("message", "")
    douyin_sugg_md = "\n".join(f"- {s}" for s in douyin_words) if douyin_words else f"- ⚠️ {douyin_msg}"
    if douyin_status == "login_required":
        douyin_sugg_md += "\n\n> 💡 点击下方「抖音指数」直达链接，登录后可查看完整数据"

    # 官方链接
    links_md = "\n".join(
        f"- {l['icon']} [{l['name_cn']}]({l['url']}) — {l['need']}\n  - {l['desc']}"
        for l in result["official_links"]
    )

    return f"""# 行业关键词数据 · 「{kw}」

> 生成时间：{today}
> 数据来源：百度/头条热榜（免费实时）+ 搜索联想词 + 官方指数直达链接

---

## 📊 热榜命中

| 平台 | 结果 |
|---|---|
| 百度热榜 | {bd_line} |
| 头条热榜 | {tt_line} |

## 🔗 搜索联想词（反映用户真实搜索习惯）

### 百度联想
{bd_sugg_md}

### 必应联想
{bing_sugg_md}

### 头条联想
{toutiao_sugg_md}

## 🎵 抖音搜索建议（巨量算数/抖音指数）

{douyin_sugg_md}

> 💡 抖音指数已升级为「抖音指数（原巨量算数）」，提供抖音平台搜索指数、关联词分析、人群画像等数据。

## 🏢 官方指数直达链接

{links_md}

> 💡 **提示**：点击上方链接在新窗口打开，登录对应平台账号后即可查看完整指数曲线和详细数据

---

## 📈 数据源说明

| 数据源 | 类型 | 说明 |
|---|---|---|
| 百度热榜 / 头条热榜 | ✅ 免费 | 实时抓取，实时榜单 |
| 百度联想 / 必应联想 / 头条联想 | ✅ 免费 | 搜索下拉词，反映真实搜索需求 |
| 抖音搜索建议 | ⚠️ 部分免费 | 需登录抖音账号才能获取完整关联词 |
| 抖音指数 / 百度指数 / 微信指数 / 谷歌趋势 | 🔌 需登录 | 点击直达链接，登录后查看完整数据 |

## 🔗 反向链接

- [[FDE]]
- [[天龙-viral-工作流-SOP-V2]]
- [[用户真实需求采集方案]]
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="天龙引擎 行业关键词数据（热榜命中 + 联想词 + 官方指数直达）"
    )
    parser.add_argument("keyword", nargs="?", help="要查询的关键词（必填）")
    parser.add_argument("--json", action="store_true", help="仅输出 JSON")
    parser.add_argument("--no-save", action="store_true", help="不保存报告文件")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.keyword:
        print("❌ 缺少关键词")
        print("用法: python scripts/run_keywords_index.py <关键词>")
        return 1

    keyword = args.keyword.strip()
    print(f"\n🔍 天龙 行业关键词数据：{keyword}")
    print()

    # 1. 抓取热榜
    print("📡 抓取百度热榜...")
    bd_hot = fetch_baidu_hot()
    print(f"   ✅ 百度热榜 {len(bd_hot)} 条")

    print("📡 抓取头条热榜...")
    tt_hot = fetch_toutiao_hot()
    print(f"   ✅ 头条热榜 {len(tt_hot)} 条")

    # 2. 抓取联想词
    print("📡 抓取百度联想词...")
    bd_sugg = fetch_baidu_suggest(keyword)
    print(f"   ✅ 百度联想 {len(bd_sugg)} 条")

    print("📡 抓取必应联想词...")
    bing_sugg = fetch_bing_suggest(keyword)
    print(f"   ✅ 必应联想 {len(bing_sugg)} 条")

    print("📡 抓取头条联想词...")
    toutiao_sugg = fetch_toutiao_suggest(keyword)
    print(f"   ✅ 头条联想 {len(toutiao_sugg)} 条")

    # 3. 抓取抖音指数/巨量算数数据
    print("📡 抓取抖音指数数据（巨量算数）...")
    douyin_index = fetch_douyin_index(keyword)
    print(f"   ✅ 抖音指数: {douyin_index['message']}")

    # 4. 抓取百度指数数据
    print("📡 抓取百度指数数据...")
    baidu_index = fetch_baidu_index_data(keyword)
    print(f"   ✅ 百度指数: {baidu_index['message']}")

    # 5. 匹配热榜
    bd_match = match_hotlist(keyword, bd_hot)
    tt_match = match_hotlist(keyword, tt_hot)

    result = {
        "keyword": keyword,
        "queried_at": datetime.now().isoformat(),
        "baidu_hot": bd_match,
        "toutiao_hot": tt_match,
        "baidu_suggest": bd_sugg,
        "bing_suggest": bing_sugg,
        "toutiao_suggest": toutiao_sugg,
        "douyin_index": douyin_index,
        "baidu_index": baidu_index,
        "official_links": official_links(keyword),
        "note": "百度/头条热榜为免费实时数据；官方指数需登录授权",
    }

    # 6. 输出
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print()
        print("=" * 60)
        print(f"🔍 「{keyword}」行业关键词数据")
        print("=" * 60)

        print(f"\n📊 热榜命中")
        if bd_match:
            print(f"   🏅 百度热榜 第 {bd_match['rank']} 名（热度档 {bd_match['hot_tag']}）")
        else:
            print(f"   ❌ 百度热榜 未上榜")
        if tt_match:
            print(f"   🏅 头条热榜 第 {tt_match['rank']} 名（热度 {tt_match['hot_value']:,}）")
        else:
            print(f"   ❌ 头条热榜 未上榜")

        print(f"\n🔗 搜索联想词")
        print(f"   百度: {bd_sugg[:8] if bd_sugg else '（无）'}")
        print(f"   必应: {bing_sugg[:8] if bing_sugg else '（无）'}")
        print(f"   头条: {toutiao_sugg[:8] if toutiao_sugg else '（无）'}")

        print(f"\n🎵 抖音搜索建议（巨量算数）")
        douyin_words = douyin_index.get("related_words", [])
        if douyin_words:
            print(f"   ✅ {douyin_words[:8]}")
        else:
            print(f"   ⚠️ {douyin_index.get('message', '需要登录')}")
        print(f"   📎 直达: {douyin_index.get('direct_url', '')[:60]}...")

        print(f"\n🏢 官方指数直达链接（需登录/授权）")
        for l in result["official_links"]:
            print(f"   {l['icon']} {l['name_cn']}: {l['url'][:50]}...")

        # 7. 保存
        if not args.no_save:
            INDEX_DIR.mkdir(parents=True, exist_ok=True)
            safe_name = re.sub(r'[\\/:*?"<>|]', "_", keyword)
            md_path = INDEX_DIR / f"{safe_name}.md"
            md_path.write_text(generate_report(keyword, result), encoding="utf-8")
            print(f"\n📄 Markdown 报告：{md_path}")

            json_path = INDEX_DIR / f"{safe_name}.json"
            json_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"📄 JSON 数据：{json_path}")

    print()
    print("=" * 60)
    print("✅ 天龙 行业关键词数据 查询完成")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
