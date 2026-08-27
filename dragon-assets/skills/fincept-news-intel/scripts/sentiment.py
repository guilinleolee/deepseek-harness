"""
情感分析模块

使用 TextBlob 进行新闻情感分析，支持批量处理。
"""

from typing import List, Dict, Any
import time

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False


class SentimentAnalyzer:
    """
    新闻情感分析器

    使用 TextBlob 的极性分析量化文本情感。
    """

    def __init__(self):
        """初始化情感分析器"""
        self._initialized = TEXTBLOB_AVAILABLE

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        分析单条文本情感。

        Args:
            text: 待分析文本

        Returns:
            情感分析结果 {
                "label": str,       # positive/negative/neutral
                "score": float,    # -1 to 1
                "confidence": float  # 0 to 1
            }
        """
        if not text:
            return self._default_result()

        if not self._initialized:
            return self._rule_based_sentiment(text)

        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1

            # 标签判断
            if polarity > 0.1:
                label = "positive"
            elif polarity < -0.1:
                label = "negative"
            else:
                label = "neutral"

            # 置信度基于主观性（越客观置信度越高）
            confidence = 1.0 - subjectivity

            return {
                "label": label,
                "score": round(polarity, 4),
                "confidence": round(confidence, 4)
            }

        except Exception:
            return self._rule_based_sentiment(text)

    def batch_analyze(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[Dict[str, Any]]:
        """
        批量分析文本情感。

        Args:
            texts: 文本列表
            batch_size: 批大小

        Returns:
            情感分析结果列表
        """
        results = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            for text in batch:
                results.append(self.analyze(text))
                # 避免频率限制
                time.sleep(0.01)

        return results

    def _rule_based_sentiment(self, text: str) -> Dict[str, Any]:
        """
        基于规则的情感分析（TextBlob 不可用时备用）

        使用情感词典匹配计算极性。
        """
        # 简单情感词典
        positive_words = {
            "beat", "beats", "exceeded", "record", "growth", "grow", "rising",
            "rise", "profit", "surge", "surpassed", "bullish", "upgrade",
            "outperform", "strong", "stronger", "gain", "gains", "positive",
            "increase", "increased", "success", "successful", "breakthrough"
        }

        negative_words = {
            "miss", "missed", "loss", "decline", "declined", "drop", "dropped",
            "fall", "fell", "weak", "weaker", "cut", "downgrade", "underperform",
            "bearish", "negative", "decrease", "decreased", "concern", "concerns",
            "risk", "risks", "warning", "uncertainty", "lawsuit", "investigation"
        }

        text_lower = text.lower()
        words = set(text_lower.replace(",", " ").replace(".", " ").split())

        pos_count = len(words & positive_words)
        neg_count = len(words & negative_words)

        total = pos_count + neg_count
        if total == 0:
            return self._default_result()

        score = (pos_count - neg_count) / total

        if score > 0.1:
            label = "positive"
        elif score < -0.1:
            label = "negative"
        else:
            label = "neutral"

        confidence = min(total / 5.0, 1.0)  # 最多5个词命中

        return {
            "label": label,
            "score": round(score, 4),
            "confidence": round(confidence, 4)
        }

    def _default_result(self) -> Dict[str, Any]:
        """返回默认结果"""
        return {
            "label": "neutral",
            "score": 0.0,
            "confidence": 0.0
        }
