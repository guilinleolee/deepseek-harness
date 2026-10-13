"""
主题聚类模块

使用 TF-IDF + HDBSCAN/K-Means 对新闻进行主题聚类。
"""

from typing import List, Dict, Any, Optional
from collections import Counter
import re

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    np = None

try:
    import hdbscan
    HDBSCAN_AVAILABLE = True
except ImportError:
    HDBSCAN_AVAILABLE = False


class NewsClustering:
    """
    新闻主题聚类器

    使用 TF-IDF 特征提取和 HDBSCAN/K-Means 聚类。
    """

    def __init__(self):
        """初始化聚类器"""
        self._sklearn_available = SKLEARN_AVAILABLE
        self._hdbscan_available = HDBSCAN_AVAILABLE

    def cluster(
        self,
        news: List[Dict[str, Any]],
        n_clusters: int = 5,
        method: str = "hdbscan"
    ) -> List[Dict[str, Any]]:
        """
        对新闻进行主题聚类。

        Args:
            news: 新闻列表
            n_clusters: 目标聚类数量
            method: 聚类方法 (hdbscan/kmeans)

        Returns:
            聚类结果列表 [{
                "topic": str,           # 主题描述
                "size": int,            # 文章数量
                "keywords": List[str], # 核心关键词
                "articles": List[Dict]  # 文章列表
            }]
        """
        if not news:
            return []

        # 提取文本
        texts = [self._extract_text(item) for item in news]

        if not any(texts):
            return self._fallback_cluster(news, n_clusters)

        if method == "hdbscan" and self._hdbscan_available and self._sklearn_available:
            return self._hdbscan_cluster(news, texts, n_clusters)
        else:
            return self._kmeans_cluster(news, texts, n_clusters)

    def _extract_text(self, item: Dict[str, Any]) -> str:
        """提取新闻文本"""
        parts = [
            item.get("title", ""),
            item.get("summary", ""),
            item.get("content", "")
        ]
        return " ".join(p for p in parts if p)

    def _hdbscan_cluster(
        self,
        news: List[Dict[str, Any]],
        texts: List[str],
        n_clusters: int
    ) -> List[Dict[str, Any]]:
        """使用 HDBSCAN 聚类"""
        if not HDBSCAN_AVAILABLE or not self._sklearn_available:
            return self._kmeans_cluster(news, texts, n_clusters)

        # TF-IDF 特征提取
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words="english",
            ngram_range=(1, 2)
        )
        tfidf_matrix = vectorizer.fit_transform(texts)

        # HDBSCAN 聚类
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=2,
            min_samples=1,
            metric="cosine"
        )
        labels = clusterer.fit_predict(tfidf_matrix.toarray())

        # 构建结果
        return self._build_clusters(news, texts, labels, vectorizer.get_feature_names_out())

    def _kmeans_cluster(
        self,
        news: List[Dict[str, Any]],
        texts: List[str],
        n_clusters: int
    ) -> List[Dict[str, Any]]:
        """使用 K-Means 聚类"""
        if not self._sklearn_available:
            return self._fallback_cluster(news, n_clusters)

        # TF-IDF 特征提取
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words="english",
            ngram_range=(1, 2)
        )
        tfidf_matrix = vectorizer.fit_transform(texts)

        # K-Means 聚类
        n_clusters = min(n_clusters, len(news))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(tfidf_matrix)

        # 构建结果
        return self._build_clusters(news, texts, labels, vectorizer.get_feature_names_out())

    def _build_clusters(
        self,
        news: List[Dict[str, Any]],
        texts: List[str],
        labels: Any,
        feature_names: Any
    ) -> List[Dict[str, Any]]:
        """从聚类标签构建结果"""
        # 按标签分组
        clusters_dict: Dict[int, List[int]] = {}
        for idx, label in enumerate(labels):
            if label not in clusters_dict:
                clusters_dict[label] = []
            clusters_dict[label].append(idx)

        results = []
        for label, indices in clusters_dict.items():
            cluster_texts = [texts[i] for i in indices]
            cluster_news = [news[i] for i in indices]

            # 提取关键词
            keywords = self._extract_keywords(cluster_texts, feature_names)

            # 生成主题描述
            topic = self._generate_topic(keywords)

            results.append({
                "topic": topic,
                "size": len(indices),
                "keywords": keywords,
                "articles": cluster_news
            })

        # 按大小排序
        results.sort(key=lambda x: x["size"], reverse=True)

        return results

    def _extract_keywords(
        self,
        texts: List[str],
        feature_names: Any,
        top_n: int = 5
    ) -> List[str]:
        """提取关键词"""
        if not texts or not feature_names.size:
            return []

        try:
            # 简单词频统计
            words = " ".join(texts).lower()
            words = re.findall(r'\b[a-z]{3,}\b', words)

            # 停用词
            stopwords = {
                "the", "and", "for", "are", "but", "not", "you", "all",
                "can", "had", "her", "was", "one", "our", "out", "has",
                "have", "been", "were", "they", "this", "that", "with"
            }
            words = [w for w in words if w not in stopwords]

            counter = Counter(words)
            return [word for word, _ in counter.most_common(top_n)]

        except Exception:
            return []

    def _generate_topic(self, keywords: List[str]) -> str:
        """生成主题描述"""
        if not keywords:
            return "General News"

        if len(keywords) >= 3:
            return f"{keywords[0].title()}, {keywords[1].title()} & {keywords[2].title()}"
        elif len(keywords) == 2:
            return f"{keywords[0].title()} & {keywords[1].title()}"
        else:
            return keywords[0].title()

    def _fallback_cluster(
        self,
        news: List[Dict[str, Any]],
        n_clusters: int
    ) -> List[Dict[str, Any]]:
        """简单回退聚类（无依赖时）"""
        if not news:
            return []

        # 简单按来源分组
        by_source: Dict[str, List[Dict]] = {}
        for item in news:
            source = item.get("source", "Unknown")
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(item)

        results = []
        for source, articles in by_source.items():
            keywords = self._extract_keywords(
                [self._extract_text(a) for a in articles]
            )
            results.append({
                "topic": source,
                "size": len(articles),
                "keywords": keywords[:5],
                "articles": articles
            })

        results.sort(key=lambda x: x["size"], reverse=True)
        return results[:n_clusters]
