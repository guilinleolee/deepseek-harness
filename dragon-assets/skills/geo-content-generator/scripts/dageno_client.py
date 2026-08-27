#!/usr/bin/env python3
"""
Dageno API Client
GEO机会发现API客户端
"""

import os
import json
import requests
from typing import List, Dict, Any


class DagenoClient:
    """Dageno API客户端"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("DAGEN0_API_KEY")
        self.base_url = "https://api.dageno.dev/v1"
        self.session = requests.Session()

        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def discover_opportunities(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        发现GEO机会

        Args:
            topic: 主题
            limit: 最多返回数量

        Returns:
            List[Dict]: GEO机会列表
        """
        if not self.api_key:
            print("⚠️  DAGENO_API_KEY未设置，使用模拟数据")
            return self._mock_opportunities(topic, limit)

        try:
            response = self.session.get(
                f"{self.base_url}/opportunities",
                params={"topic": topic, "limit": limit}
            )
            response.raise_for_status()
            return response.json().get("opportunities", [])
        except Exception as e:
            print(f"❌ API调用失败: {e}，使用模拟数据")
            return self._mock_opportunities(topic, limit)

    def get_fanouts(self, opportunity_id: str) -> List[Dict[str, Any]]:
        """
        获取Fanout列表

        Args:
            opportunity_id: 机会ID

        Returns:
            List[Dict]: Fanout列表
        """
        if not self.api_key:
            return self._mock_fanouts()

        try:
            response = self.session.get(
                f"{self.base_url}/opportunities/{opportunity_id}/fanouts"
            )
            response.raise_for_status()
            return response.json().get("fanouts", [])
        except Exception as e:
            print(f"❌ API调用失败: {e}，使用模拟数据")
            return self._mock_fanouts()

    def get_citations(self, fanout_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取引用列表

        Args:
            fanout_id: Fanout ID
            limit: 最多返回数量

        Returns:
            List[Dict]: 引用列表
        """
        if not self.api_key:
            return self._mock_citations(limit)

        try:
            response = self.session.get(
                f"{self.base_url}/fanouts/{fanout_id}/citations",
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json().get("citations", [])
        except Exception as e:
            print(f"❌ API调用失败: {e}，使用模拟数据")
            return self._mock_citations(limit)

    def _mock_opportunities(self, topic: str, limit: int) -> List[Dict[str, Any]]:
        """生成模拟GEO机会数据"""
        return [
            {
                "id": f"opp-{i}",
                "topic": topic,
                "prompt": f"{topic}的{prompt_type}决策问题",
                "prompt_type": prompt_type,
                "volume": 1000 + i * 100,
                "difficulty": ["easy", "medium", "hard"][i % 3],
                "potential": 0.7 + i * 0.03
            }
            for i, prompt_type in enumerate([
                "最佳实践", "对比分析", "选型建议", "实施指南", "成本效益",
                "风险评估", "技术对比", "供应商评估", "ROI计算", "迁移策略"
            ][:limit])
        ]

    def _mock_fanouts(self) -> List[Dict[str, Any]]:
        """生成模拟Fanout数据"""
        return [
            {
                "id": f"fanout-{i}",
                "question": f"关于{i+1}的决策问题",
                "context": "相关背景和上下文信息",
                "answer_type": "decision",
                "authority_score": 0.8 + i * 0.02
            }
            for i in range(5)
        ]

    def _mock_citations(self, limit: int) -> List[Dict[str, Any]]:
        """生成模拟引用数据"""
        return [
            {
                "id": f"citation-{i}",
                "url": f"https://example.com/article-{i}",
                "title": f"权威来源 {i+1}",
                "authority": ["editorial", "official", "research", "expert"][i % 4],
                "relevance": 0.8 + i * 0.02,
                "content_snippet": "这是引用内容片段..."
            }
            for i in range(limit)
        ]
