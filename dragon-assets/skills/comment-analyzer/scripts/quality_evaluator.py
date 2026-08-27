#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量评估模块
Quality Evaluator Module

评估评论的质量，筛选高质量评论。
"""

import re
from typing import Dict, List


class QualityEvaluator:
    """质量评估类"""

    def __init__(self):
        pass

    def evaluate(self, comments: List[Dict]) -> Dict:
        """
        评估评论质量

        Args:
            comments: 评论列表

        Returns:
            质量评估结果
        """
        if not comments:
            return {
                "high_quality_comments": [],
                "low_quality_comments": [],
                "high_quality_count": 0,
                "low_quality_count": 0,
                "high_quality_ratio": 0.0,
                "quality_distribution": {}
            }

        # 评估每条评论的质量
        scored_comments = []
        for comment in comments:
            content = comment.get("content", "")
            score = self._calculate_quality_score(content, comment)

            scored_comments.append({
                **comment,
                "quality_score": score,
                "quality_level": "high" if score >= 0.7 else "low"
            })

        # 分离高质量和低质量评论
        high_quality = [c for c in scored_comments if c["quality_level"] == "high"]
        low_quality = [c for c in scored_comments if c["quality_level"] == "low"]

        # 按质量得分排序
        high_quality.sort(key=lambda x: x["quality_score"], reverse=True)

        return {
            "high_quality_comments": high_quality[:20],  # Top20高质量评论
            "low_quality_comments": low_quality[:10],  # Top10低质量评论（示例）
            "high_quality_count": len(high_quality),
            "low_quality_count": len(low_quality),
            "high_quality_ratio": len(high_quality) / len(scored_comments),
            "quality_distribution": {
                "high": len(high_quality),
                "medium": len([c for c in scored_comments if 0.4 <= c["quality_score"] < 0.7]),
                "low": len(low_quality)
            }
        }

    def _calculate_quality_score(self, content: str, comment: Dict) -> float:
        """
        计算评论质量得分

        Args:
            content: 评论文本
            comment: 评论数据

        Returns:
            质量得分（0-1）
        """
        score = 0.0

        # 1. 评论长度（20%）
        length = len(content)
        if 20 <= length <= 200:
            score += 0.2
        elif length > 200:
            score += 0.15  # 太长可能冗余
        elif length >= 10:
            score += 0.1

        # 2. 信息密度（30%）
        info_density = self._calculate_info_density(content)
        score += info_density * 0.3

        # 3. 结构完整性（20%）
        if self._has_structure(content):
            score += 0.2

        # 4. 情感词丰富度（15%）
        if self._has_sentiment_words(content):
            score += 0.15

        # 5. 点赞数（15%）
        likes = comment.get("likes", 0)
        if likes > 0:
            # 使用对数避免极端值
            import math
            score += min(0.15, math.log10(likes + 1) / 10)

        # 6. 惩罚项
        # 检测垃圾内容
        if self._is_spam(content):
            score *= 0.5

        # 检测重复字符
        if self._has_repeated_chars(content):
            score *= 0.7

        return min(1.0, max(0.0, score))

    def _calculate_info_density(self, content: str) -> float:
        """计算信息密度"""
        # 检查是否有具体细节
        has_numbers = bool(re.search(r'\d+', content))
        has_examples = any(kw in content for kw in ["例如", "比如", "像", "诸如", "举例"])
        has_reasons = any(kw in content for kw in ["因为", "由于", "原因", "所以", "因此"])

        density_score = 0
        if has_numbers:
            density_score += 0.3
        if has_examples:
            density_score += 0.4
        if has_reasons:
            density_score += 0.3

        return density_score

    def _has_structure(self, content: str) -> bool:
        """检查是否有结构"""
        # 检查是否有标点符号
        has_punctuation = bool(re.search(r'[，。！？；：、]', content))

        # 检查是否分句
        sentence_count = len(re.split(r'[。！？\n]', content))

        return has_punctuation and sentence_count >= 2

    def _has_sentiment_words(self, content: str) -> bool:
        """检查是否有情感词"""
        sentiment_keywords = [
            "好", "棒", "优秀", "喜欢", "爱", "支持", "赞", "推荐",
            "差", "失望", "批评", "不满", "反对",
            "建议", "希望", "可以", "改进"
        ]

        return any(kw in content for kw in sentiment_keywords)

    def _is_spam(self, content: str) -> bool:
        """检测垃圾内容"""
        # 纯表情符号
        emoji_count = len(re.findall(r'[\U00010000-\U0010ffff]', content))
        if emoji_count > 5 and len(content) < 20:
            return True

        # 纯符号
        symbol_count = len(re.findall(r'[^\w\s\u4e00-\u9fff]', content))
        if symbol_count > len(content) * 0.5:
            return True

        # 重复短语
        words = re.findall(r'[\w]+', content)
        if len(words) > 0:
            most_common_word = max(set(words), key=words.count)
            if words.count(most_common_word) > len(words) * 0.5:
                return True

        return False

    def _has_repeated_chars(self, content: str) -> bool:
        """检测重复字符"""
        # 检查连续重复字符
        if re.search(r'(.)\1{4,}', content):
            return True

        return False
