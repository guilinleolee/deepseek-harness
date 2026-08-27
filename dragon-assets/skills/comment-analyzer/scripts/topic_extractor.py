#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
话题提取模块
Topic Extractor Module

从评论中提取高频话题和关键词。
"""

import re
import jieba
from pathlib import Path
from typing import Dict, List
from collections import Counter


class TopicExtractor:
    """话题提取类"""

    def __init__(self):
        self.stop_words = self._load_stop_words()

    def _load_stop_words(self) -> set:
        """加载停用词表"""
        stop_words_path = Path(__file__).parent.parent / "data" / "stop_words.txt"
        stop_words = set()

        if stop_words_path.exists():
            with open(stop_words_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        stop_words.add(line)

        # 添加常见停用词
        stop_words.update(['的', '了', '是', '在', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'])

        return stop_words

    def extract(self, comments: List[Dict]) -> Dict:
        """
        提取高频话题

        Args:
            comments: 评论列表

        Returns:
            话题分析结果
        """
        if not comments:
            return {
                "keywords": [],
                "topics": [],
                "topic_clusters": []
            }

        # 预处理文本
        texts = [self._preprocess_text(c.get("content", "")) for c in comments]
        texts = [t for t in texts if t]  # 过滤空文本

        if not texts:
            return {
                "keywords": [],
                "topics": [],
                "topic_clusters": []
            }

        # 提取关键词
        keywords = self._extract_keywords(texts)

        # 聚类话题
        topic_clusters = self._cluster_topics(keywords)

        return {
            "keywords": keywords[:50],  # TOP50关键词
            "topics": topic_clusters[:10],  # TOP10话题
            "topic_clusters": topic_clusters
        }

    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)

        # 去除@用户
        text = re.sub(r'@\w+', '', text)

        # 去除#话题#
        text = re.sub(r'#\w+#', '', text)

        # 去除URL
        text = re.sub(r'http\S+', '', text)

        # 去除表情符号
        text = re.sub(r'[\U00010000-\U0010ffff]', '', text)

        # 去除特殊符号
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)

        return text.strip()

    def _extract_keywords(self, texts: List[str]) -> List[Dict]:
        """提取高频关键词"""
        all_words = []

        for text in texts:
            # 使用jieba分词
            words = jieba.cut(text)

            # 过滤停用词和短词
            filtered_words = [
                w for w in words
                if len(w) >= 2 and w not in self.stop_words
            ]

            all_words.extend(filtered_words)

        # 统计词频
        word_counter = Counter(all_words)

        # 转换为列表格式
        keywords = [
            {"word": word, "count": count}
            for word, count in word_counter.most_common(100)
        ]

        return keywords

    def _cluster_topics(self, keywords: List[Dict]) -> List[Dict]:
        """聚类相似话题"""
        # 简化版：基于关键词的相似性聚类
        clusters = []

        for kw in keywords[:20]:  # 只对前20个关键词进行聚类
            word = kw["word"]
            count = kw["count"]

            # 查找相似关键词（包含关系）
            similar_words = [
                k for k in keywords
                if word in k["word"] or k["word"] in word
            ]

            if similar_words:
                cluster = {
                    "topic": word,
                    "total_count": sum(w["count"] for w in similar_words),
                    "keywords": similar_words[:5]  # 每个聚类最多5个关键词
                }
                clusters.append(cluster)

        # 按总数排序并去重
        unique_clusters = []
        seen_topics = set()

        for cluster in sorted(clusters, key=lambda x: x["total_count"], reverse=True):
            if cluster["topic"] not in seen_topics:
                unique_clusters.append(cluster)
                seen_topics.add(cluster["topic"])
                if len(unique_clusters) >= 10:
                    break

        return unique_clusters
