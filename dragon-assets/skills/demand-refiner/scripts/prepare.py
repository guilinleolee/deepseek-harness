#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prepare.py · 需求提炼 · 数据预处理脚本
============================================

把采集到的原始用户评论/笔记清洗、去重、统计，输出给 LLM 做痛点聚类。

输入：JSON 数组 [{"text": "...", "source": "..."}, ...]
输出：clean.json（清洗去重后）+ 控制台 Top 高频词

用法：
    python prepare.py --input raw.json --output clean.json
    python prepare.py --input raw.json --output clean.json --min-len 8
    python prepare.py --input raw.json --stats-only

仅用 Python 标准库（argparse / json / re / collections）。
要求 Python ≥ 3.8。
"""
from __future__ import annotations

import argparse
import sys
import os
import json
import re
from collections import Counter

# Windows GBK 兼容：强制 UTF-8 输出
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


# 无意义内容特征（广告/水军/灌水）
SPAM_PATTERNS = [
    r"加.{0,4}微信", r"vx[:：]?\s*\w", r"wx[:：]?\s*\w",
    r"私信我", r"戳我", r"直播间.{0,6}抢", r"限时.{0,4}优惠",
    r"点击链接", r"http\S+", r"www\.\S+",
]
# 高噪声词（清洗后统计时忽略）
STOPWORDS = {
    "一个", "这个", "那个", "什么", "怎么", "可以", "就是", "感觉",
    "觉得", "真的", "其实", "但是", "还是", "然后", "所以", "因为",
    "如果", "一下", "有点", "很", "太", "好", "我", "你", "他", "她",
    "我们", "你们", "他们", "没有", "不是", "不会", "不能", "了", "吗",
    "吧", "啊", "呢", "呀", "嗯", "哦", "的", "地", "得", "也", "都",
    "在", "就", "说", "看", "想", "用", "做", "能", "会", "要", "让",
}


def strip_emoji(text: str) -> str:
    """去除 emoji 和特殊符号"""
    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001FAFF"  # 表情符号
        "\U00002600-\U000027BF"  # 杂项符号
        "\U0001F1E6-\U0001F1FF"  # 国旗
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub("", text)


def clean_text(text: str) -> str:
    """单条文本清洗"""
    if not text:
        return ""
    t = str(text)
    t = strip_emoji(t)
    t = re.sub(r"@\w+", "", t)          # @提及
    t = re.sub(r"#\S+", "", t)          # #话题
    t = re.sub(r"http\S+|www\.\S+", "", t)  # 链接
    t = re.sub(r"\s+", " ", t)          # 合并空白
    return t.strip()


def is_spam(text: str) -> bool:
    """判断是否广告/水军"""
    t = text.lower()
    for pat in SPAM_PATTERNS:
        if re.search(pat, t):
            return True
    return False


def tokenize_chinese(text: str) -> list[str]:
    """中文分词：n-gram 候选词提取（供词频统计）"""
    cjk = re.findall(r"[一-鿿A-Za-z]+", text)
    words = []
    for seg in cjk:
        if re.fullmatch(r"[一-鿿]+", seg) and len(seg) >= 2:
            # 对 2-4 字中文片段做 n-gram 候选（1-gram 太碎，用 2-4）
            for n in (4, 3, 2):
                if len(seg) >= n:
                    words.extend(seg[i:i + n] for i in range(0, len(seg) - n + 1, 1))
        else:
            words.append(seg)  # 英文/数字整段
    return words


def freq_words(clean_items: list[dict], top_n: int = 30,
               min_df: int = 2) -> list[tuple[str, int]]:
    """统计跨文档共现词：只在 ≥min_df 条不同文本中出现的高频词"""
    # 1. 每条文本 → 去重后的候选词集合
    doc_words = []
    for item in clean_items:
        tokens = set(tokenize_chinese(item["text"]))
        tokens = {w for w in tokens if len(w) >= 2 and w not in STOPWORDS}
        doc_words.append(tokens)

    # 2. 文档频率（DF）：词出现在几条不同文本
    df: Counter = Counter()
    for tokens in doc_words:
        df.update(tokens)

    # 3. 过滤：只保留跨文档共现的词（df >= min_df），按频率排序
    #    再按"词长优先"（长词信息量更大，如"被割韭菜" > "韭菜"）
    candidates = [(w, c) for w, c in df.items() if c >= min_df]
    candidates.sort(key=lambda x: (-x[1], -len(x[0])))
    # 若长词包含短词（如"陪跑服务"含"陪跑"），保留长词
    top = []
    for w, c in candidates:
        if any(w in tw for tw, _ in top):
            continue  # 已被更长词覆盖
        top.append((w, c))
        if len(top) >= top_n:
            break
    return top


def load_data(input_path: str) -> list[dict]:
    """读取 JSON 数据（兼容数组或 {items: [...]} 结构）"""
    if not os.path.exists(input_path):
        print(f"❌ 文件不存在: {input_path}")
        return []
    try:
        with open(input_path, encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"❌ 文件读取失败: {e}")
        return []
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ("items", "data", "comments", "notes"):
            if key in raw and isinstance(raw[key], list):
                return raw[key]
    return []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="需求提炼数据预处理：清洗/去重/词频统计"
    )
    parser.add_argument("--input", required=True, help="原始数据 JSON 路径")
    parser.add_argument("--output", help="清洗后输出路径（缺省则只打印统计）")
    parser.add_argument("--min-len", type=int, default=6, help="最短有效文本长度（默认 6）")
    parser.add_argument("--stats-only", action="store_true", help="仅统计不输出文件")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw_items = load_data(args.input)
    if not raw_items:
        print(f"❌ 未读取到数据（{args.input}）")
        return 1
    print(f"📥 原始数据: {len(raw_items)} 条")

    # 1. 清洗 + 去重 + 过滤
    seen = set()
    clean_items: list[dict] = []
    for it in raw_items:
        text = clean_text(it.get("text", "") or it.get("content", "") or "")
        if len(text) < args.min_len:
            continue
        if is_spam(text):
            continue
        key = text[:50]  # 近似去重（取前 50 字）
        if key in seen:
            continue
        seen.add(key)
        clean_items.append({
            "text": text,
            "source": it.get("source", ""),
            "platform": it.get("platform", ""),
        })
    print(f"✨ 清洗后: {len(clean_items)} 条（去重/去广告后）")

    # 2. 词频统计（跨文档共现词）
    top_words = freq_words(clean_items, top_n=30, min_df=2)

    print(f"\n🔝 Top 高频词（出现在 ≥2 条评论中）：")
    if top_words:
        for word, cnt in top_words:
            print(f"  {word}: {cnt}")
    else:
        print("  （样本太少或无共现词，请直接让 LLM 阅读全文分析）")

    # 3. 输出
    if args.output and not args.stats_only:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(clean_items, f, ensure_ascii=False, indent=2)
        print(f"\n📄 清洗后数据已保存: {args.output}")
    else:
        print(f"\n📄 清洗后数据（前 10 条预览）：")
        for item in clean_items[:10]:
            print(f"  - {item['text'][:50]}")

    print(f"\n✅ 预处理完成：{len(clean_items)} 条有效文本可供 LLM 分析")
    return 0


if __name__ == "__main__":
    sys.exit(main())
