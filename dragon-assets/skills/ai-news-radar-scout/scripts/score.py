#!/usr/bin/env python3
"""
AI News Radar - AI相关性评分脚本 (v0.4.0可解释评分)
"""

import argparse
import json
import sys
from pathlib import Path


# AI领域关键词分类
AI_KEYWORD_CATEGORIES = {
    "model_release": [
        "release", "launch", "announce", "debut", "introducing",
        "gpt", "claude", "gemini", "llama", "mistral", "grok",
        "model", "version", "update"
    ],
    "research": [
        "paper", "research", "study", "arxiv", " preprint",
        "benchmark", "performance", "accuracy", "result"
    ],
    "api_product": [
        "api", "sdk", "pricing", "token", "rate limit",
        "endpoint", "model", "completion", "embedding"
    ],
    "safety": [
        "safety", "alignment", "ethics", "responsible", "trust",
        "privacy", "security", "bias", "fairness"
    ],
    "industry": [
        "industry", "market", "trend", "growth", "adoption",
        "enterprise", "startup", "funding", "investment"
    ]
}


def calculate_relevance_score(article: dict) -> dict:
    """
    计算AI相关性评分 (0-1)
    采用多维度加权评分
    """
    title = article.get("title", "").lower()
    summary = article.get("summary", "")[:1000].lower()
    source = article.get("source", "").lower()
    combined = f"{title} {summary} {source}"

    scores = {}
    matched_keywords = {}

    for category, keywords in AI_KEYWORD_CATEGORIES.items():
        hits = sum(1 for kw in keywords if kw in combined)
        scores[category] = min(hits / 3, 1.0)  # 最多3个关键词满分

        # 记录命中的关键词
        matched = [kw for kw in keywords if kw in combined]
        if matched:
            matched_keywords[category] = matched

    # 加权总分
    weights = {
        "model_release": 0.35,  # 模型发布权重最高
        "research": 0.20,
        "api_product": 0.20,
        "safety": 0.10,
        "industry": 0.15
    }

    total_score = sum(scores[k] * weights[k] for k in weights)

    # 生成可解释理由
    reasons = []
    top_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    for cat, score in top_categories:
        if score > 0.3:
            reasons.append(f"{cat}: {matched_keywords.get(cat, [])[:3]}")

    return {
        "score": round(total_score, 3),
        "breakdown": {k: round(v, 3) for k, v in scores.items()},
        "matched_keywords": matched_keywords,
        "reason": f"AI强相关 ({total_score:.0%})" if total_score > 0.2 else "AI弱相关",
        "explanation": " | ".join(reasons) if reasons else "未命中AI核心关键词"
    }


def score_batch(input_path: str, output_path: str):
    """批量评分"""
    input_file = Path(input_path)
    data = json.loads(input_file.read_text(encoding="utf-8"))

    articles = data.get("articles", [])
    scored_articles = []

    for article in articles:
        score_result = calculate_relevance_score(article)
        article.update(score_result)
        scored_articles.append(article)

    # 按评分排序
    scored_articles.sort(key=lambda x: x.get("score", 0), reverse=True)

    # 更新输出
    data["articles"] = scored_articles
    data["scoring_timestamp"] = str(Path().cwd())

    output_file = Path(output_path)
    output_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✅ 评分完成: {len(scored_articles)} 篇")
    print(f"📊 平均AI相关性: {sum(a.get('score', 0) for a in scored_articles) / len(scored_articles):.1%}")
    print(f"📁 输出文件: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="AI News Radar - AI相关性评分")
    parser.add_argument("--input", "-i", required=True, help="输入JSON文件")
    parser.add_argument("--output", "-o", required=True, help="输出JSON文件")
    parser.add_argument("--threshold", type=float, default=0.3, help="相关性阈值")

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"错误: 输入文件不存在 {args.input}")
        sys.exit(1)

    score_batch(args.input, args.output)


if __name__ == "__main__":
    main()
