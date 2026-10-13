#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情感分析模块
Sentiment Analyzer Module

对评论进行情感倾向分析，支持四分类体系（正面/建议/中性/负面）。
"""

import re
from pathlib import Path
from typing import Dict, List
from collections import Counter


class SentimentAnalyzer:
    """情感分析类"""

    def __init__(self):
        self.sentiment_dict = self._load_sentiment_dict()
        self.negation_words = set(["不", "没", "非", "无", "别", "未", "莫", "勿"])
        self.degree_words = {
            "high": ["非常", "特别", "极其", "太", "超级", "十分"],
            "medium": ["很", "挺", "相当"],
            "low": ["有点", "稍微", "略微", "有些"]
        }

    def _load_sentiment_dict(self) -> Dict:
        """加载情感词典"""
        dict_path = Path(__file__).parent.parent / "data" / "sentiment_dict.txt"
        sentiment_dict = {}

        if dict_path.exists():
            with open(dict_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split()
                        if len(parts) >= 2:
                            word = parts[0]
                            weight = float(parts[1])
                            sentiment_dict[word] = weight

        return sentiment_dict

    def analyze(self, comments: List[Dict]) -> Dict:
        """
        分析评论情感

        Args:
            comments: 评论列表

        Returns:
            情感分析结果
        """
        if not comments:
            return {
                "overall": "中性",
                "distribution": {"positive": 0, "suggestion": 0, "neutral": 0, "negative": 0},
                "timeline": [],
                "sentiment_keywords": {"positive": [], "negative": []},
                "comment_scores": []
            }

        # 分析每条评论的情感
        comment_scores = []
        for comment in comments:
            content = comment.get("content", "")
            result = self._analyze_comment(content)
            result.update({
                "comment_id": comment.get("id"),
                "content": content,
                "likes": comment.get("likes", 0)
            })
            comment_scores.append(result)

        # 计算整体情感倾向
        overall = self._calculate_overall_sentiment(comment_scores)

        # 计算情感分布
        distribution = self._calculate_distribution(comment_scores)

        # 生成情感时间线
        timeline = self._generate_timeline(comment_scores)

        # 提取情感关键词
        sentiment_keywords = self._extract_sentiment_keywords(comment_scores)

        return {
            "overall": overall,
            "distribution": distribution,
            "timeline": timeline,
            "sentiment_keywords": sentiment_keywords,
            "comment_scores": comment_scores[:50]  # 只返回前50条用于展示
        }

    def _analyze_comment(self, content: str) -> Dict:
        """分析单条评论的情感"""
        # 分词（简单按空格和标点分割）
        words = re.findall(r'[\w]+', content)

        # 计算基础情感得分
        base_score = 0
        sentiment_words = []
        for word in words:
            if word in self.sentiment_dict:
                base_score += self.sentiment_dict[word]
                sentiment_words.append(word)

        # 检查否定词
        has_negation = any(word in self.negation_words for word in words)

        # 应用否定词反转
        if has_negation:
            base_score = -base_score

        # 检查程度词
        degree_modifier = 1.0
        for word in words:
            if word in self.degree_words["high"]:
                degree_modifier = 1.5
                break
            elif word in self.degree_words["medium"]:
                degree_modifier = 1.2
                break
            elif word in self.degree_words["low"]:
                degree_modifier = 0.8
                break

        # 应用程度词加权
        final_score = base_score * degree_modifier

        # 分类
        category = self._classify_sentiment(final_score)

        # 计算置信度
        confidence = min(1.0, len(sentiment_words) / 3 + 0.3)

        return {
            "score": final_score,
            "category": category,
            "confidence": confidence,
            "sentiment_words": sentiment_words,
            "reason": f"{len(sentiment_words)}个情感词"
        }

    def _classify_sentiment(self, score: float) -> str:
        """根据得分分类情感"""
        if score >= 0.3:
            return "positive"
        elif score > 0:
            return "suggestion"
        elif score > -0.3:
            return "neutral"
        else:
            return "negative"

    def _calculate_overall_sentiment(self, comment_scores: List[Dict]) -> str:
        """计算整体情感倾向"""
        if not comment_scores:
            return "neutral"

        # 计算平均得分
        total_score = sum(cs["score"] for cs in comment_scores)
        avg_score = total_score / len(comment_scores)

        return self._classify_sentiment(avg_score)

    def _calculate_distribution(self, comment_scores: List[Dict]) -> Dict:
        """计算情感分布"""
        total = len(comment_scores)
        if total == 0:
            return {"positive": 0, "suggestion": 0, "neutral": 0, "negative": 0}

        counter = Counter(cs["category"] for cs in comment_scores)

        return {
            "positive": counter.get("positive", 0),
            "suggestion": counter.get("suggestion", 0),
            "neutral": counter.get("neutral", 0),
            "negative": counter.get("negative", 0)
        }

    def _generate_timeline(self, comment_scores: List[Dict]) -> List[Dict]:
        """生成情感时间线"""
        # 简化版：按评论顺序生成
        timeline = []
        for i, cs in enumerate(comment_scores[:20]):  # 只取前20条
            timeline.append({
                "index": i,
                "score": cs["score"],
                "category": cs["category"]
            })

        return timeline

    def _extract_sentiment_keywords(self, comment_scores: List[Dict]) -> Dict:
        """提取情感关键词"""
        positive_words = []
        negative_words = []

        for cs in comment_scores:
            if cs["category"] == "positive":
                positive_words.extend(cs["sentiment_words"])
            elif cs["category"] == "negative":
                negative_words.extend(cs["sentiment_words"])

        # 统计词频
        positive_counter = Counter(positive_words)
        negative_counter = Counter(negative_words)

        return {
            "positive": [{"word": w, "count": c} for w, c in positive_counter.most_common(20)],
            "negative": [{"word": w, "count": c} for w, c in negative_counter.most_common(20)]
        }
