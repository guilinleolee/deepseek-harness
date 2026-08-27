#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
观点提炼模块
Viewpoint Summarizer Module

从评论中提炼核心观点和代表性意见。
"""

import re
from typing import Dict, List
from collections import defaultdict


class ViewpointSummarizer:
    """观点提炼类"""

    def __init__(self):
        pass

    def summarize(self, comments: List[Dict]) -> Dict:
        """
        提炼核心观点

        Args:
            comments: 评论列表

        Returns:
            观点提炼结果
        """
        if not comments:
            return {
                "viewpoints": [],
                "distribution": {"support": 0, "oppose": 0, "neutral": 0}
            }

        # 分析每条评论的观点极性
        comment_viewpoints = []
        for comment in comments:
            content = comment.get("content", "")
            polarity = self._detect_polarity(content)

            comment_viewpoints.append({
                "content": content,
                "polarity": polarity,
                "likes": comment.get("likes", 0),
                "comment_id": comment.get("id")
            })

        # 聚类相似观点
        viewpoint_groups = self._cluster_viewpoints(comment_viewpoints)

        # 按支持度排序
        viewpoint_groups.sort(key=lambda x: x["support_count"], reverse=True)

        # 计算观点分布
        distribution = self._calculate_distribution(comment_viewpoints)

        # 提取代表性评论
        for group in viewpoint_groups:
            group["sample_comments"] = group["comments"][:3]

        return {
            "viewpoints": [
                {
                    "viewpoint": vg["viewpoint"],
                    "polarity": vg["polarity"],
                    "support_count": vg["support_count"],
                    "sample_comments": vg["sample_comments"]
                }
                for vg in viewpoint_groups[:10]
            ],
            "distribution": distribution
        }

    def _detect_polarity(self, content: str) -> str:
        """检测评论的观点极性"""
        # 支持类关键词
        support_keywords = ["支持", "赞同", "同意", "认可", "肯定", "喜欢", "推荐", "好", "棒", "赞"]
        # 反对类关键词
        oppose_keywords = ["反对", "不赞成", "不同意", "质疑", "批评", "差", "不好", "失望"]

        support_count = sum(1 for kw in support_keywords if kw in content)
        oppose_count = sum(1 for kw in oppose_keywords if kw in content)

        if support_count > oppose_count:
            return "support"
        elif oppose_count > support_count:
            return "oppose"
        else:
            return "neutral"

    def _cluster_viewpoints(self, comment_viewpoints: List[Dict]) -> List[Dict]:
        """聚类相似观点"""
        # 简化版：按极性分组，提取代表句子
        groups = defaultdict(list)

        for cv in comment_viewpoints:
            # 提取关键句子（第一句话）
            sentences = re.split(r'[。！？\n]', cv["content"])
            key_sentence = sentences[0].strip() if sentences else cv["content"]

            # 基于极性和关键词分组
            polarity = cv["polarity"]
            groups[polarity].append({
                "content": cv["content"],
                "key_sentence": key_sentence,
                "likes": cv["likes"]
            })

        # 为每个极性选择代表观点
        viewpoint_groups = []

        for polarity, comments in groups.items():
            if not comments:
                continue

            # 按点赞数排序，选择最热门的作为代表观点
            comments.sort(key=lambda x: x["likes"], reverse=True)

            # 选择多个代表性观点（避免重复）
            seen_sentences = set()
            for comment in comments:
                key_sentence = comment["key_sentence"]
                if key_sentence and key_sentence not in seen_sentences and len(key_sentence) > 5:
                    seen_sentences.add(key_sentence)

                    # 计算支持度（点赞数 + 相似评论数）
                    similar_count = sum(
                        1 for c in comments
                        if self._similarity(c["content"], comment["content"]) > 0.5
                    )

                    viewpoint_groups.append({
                        "viewpoint": key_sentence,
                        "polarity": polarity,
                        "support_count": comment["likes"] + similar_count,
                        "comments": [c["content"] for c in comments if self._similarity(c["content"], comment["content"]) > 0.5]
                    })

                    if len(viewpoint_groups) >= 10:
                        break

        return viewpoint_groups

    def _similarity(self, text1: str, text2: str) -> float:
        """计算两段文本的相似度（简化版）"""
        # 使用关键词重叠度
        words1 = set(re.findall(r'[\w]+', text1))
        words2 = set(re.findall(r'[\w]+', text2))

        if not words1 or not words2:
            return 0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _calculate_distribution(self, comment_viewpoints: List[Dict]) -> Dict:
        """计算观点分布"""
        total = len(comment_viewpoints)
        if total == 0:
            return {"support": 0, "oppose": 0, "neutral": 0}

        counter = defaultdict(int)
        for cv in comment_viewpoints:
            counter[cv["polarity"]] += 1

        return {
            "support": counter.get("support", 0),
            "oppose": counter.get("oppose", 0),
            "neutral": counter.get("neutral", 0)
        }
