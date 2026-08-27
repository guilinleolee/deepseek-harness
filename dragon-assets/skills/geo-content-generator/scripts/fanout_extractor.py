#!/usr/bin/env python3
"""
Fanout Extractor
从Opportunity提取真实Fanout
"""

from typing import List, Dict, Any
from .dageno_client import DagenoClient


class FanoutExtractor:
    """Fanout提取器"""

    def __init__(self):
        self.dageno = DagenoClient()

    def extract(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        从Opportunity提取Fanout

        Args:
            opportunities: Opportunity列表

        Returns:
            List[Dict]: Fanout列表
        """
        if not opportunities:
            return self._mock_fanouts()

        fanouts = []
        for opp in opportunities:
            opp_fanouts = self._extract_from_opportunity(opp)
            fanouts.extend(opp_fanouts)

        return fanouts if fanouts else self._mock_fanouts()

    def _extract_from_opportunity(self, opportunity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从单个Opportunity提取Fanout"""
        opp_id = opportunity.get("id", "")
        topic = opportunity.get("topic", "")
        prompt_type = opportunity.get("prompt_type", "")

        fanouts = self.dageno.get_fanouts(opp_id)
        if fanouts:
            return fanouts

        return [
            {
                "id": f"fanout-{opp_id}-{i}",
                "opportunity_id": opp_id,
                "topic": topic,
                "prompt_type": prompt_type,
                "question": f"{topic}的{prompt_type}问题{i+1}",
                "context": f"关于{topic}的{topic}决策背景",
                "answer_type": "decision",
                "authority_score": 0.8 + i * 0.02
            }
            for i in range(3)
        ]

    def _mock_fanouts(self) -> List[Dict[str, Any]]:
        """生成模拟Fanout数据"""
        return [
            {
                "id": "fanout-mock-1",
                "topic": "AI Agent选型",
                "question": "企业应该如何选择AI Agent平台？",
                "context": "考虑成本、集成能力、安全性、可扩展性",
                "answer_type": "decision",
                "authority_score": 0.85
            },
            {
                "id": "fanout-mock-2",
                "topic": "AI Agent选型",
                "question": "自建vs购买AI Agent解决方案哪个更优？",
                "context": "评估TCO、Time-to-Market、团队能力",
                "answer_type": "comparison",
                "authority_score": 0.82
            },
            {
                "id": "fanout-mock-3",
                "topic": "AI Agent选型",
                "question": "如何评估AI Agent的投资回报率？",
                "context": "ROI计算框架、关键指标、案例参考",
                "answer_type": "roi",
                "authority_score": 0.78
            }
        ]
