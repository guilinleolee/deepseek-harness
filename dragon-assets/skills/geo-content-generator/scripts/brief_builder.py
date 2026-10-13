#!/usr/bin/env python3
"""
Brief Builder
Editorial Brief构建器
"""

from typing import List, Dict, Any
from datetime import datetime


class BriefBuilder:
    """Editorial Brief构建器"""

    def __init__(self):
        self.templates = {}

    def build(
        self,
        topic: str,
        fanouts: List[Dict[str, Any]],
        citations: List[Dict[str, Any]],
        depth: str = "full"
    ) -> Dict[str, Any]:
        """
        构建Editorial Brief

        Args:
            topic: 内容主题
            fanouts: Fanout列表
            citations: 引用列表
            depth: 生成深度 (brief/full/decision)

        Returns:
            Dict: Editorial Brief
        """
        brief = self._create_base_brief(topic, depth)
        brief = self._add_reader_persona(brief, topic)
        brief = self._add_article_angle(brief, topic, fanouts)
        brief = self._add_decision_frame(brief, fanouts)
        brief = self._add_differentiation(brief, citations)
        brief = self._add_must_elements(brief, topic, fanouts)
        brief = self._add_outline(brief, topic, depth)
        brief = self._add_citations(brief, citations)

        return brief

    def _create_base_brief(self, topic: str, depth: str) -> Dict[str, Any]:
        """创建基础Brief"""
        depth_descriptions = {
            "brief": "简明扼要的Brief",
            "full": "完整的Editorial Brief",
            "decision": "决策驱动的深度Brief"
        }

        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "working_title": self._generate_title(topic),
            "depth": depth,
            "description": depth_descriptions.get(depth, "完整的Editorial Brief")
        }

    def _generate_title(self, topic: str) -> str:
        """生成工作标题"""
        templates = [
            f"{topic}完整指南：决策者的必读手册",
            f"如何做出明智的{topic}决策",
            f"{topic}：权威专家指南",
            f"{topic}的全面解析与最佳实践"
        ]
        import random
        return random.choice(templates)

    def _add_reader_persona(self, brief: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """添加读者画像"""
        brief["reader_persona"] = {
            "role": "决策者/CTO/技术VP",
            "level": "Senior",
            "challenge": f"需要在{topic}领域做出明智决策",
            "biases": [
                "倾向于相信知名品牌的解决方案",
                "重视ROI和可量化的收益",
                "担心技术风险和团队学习曲线"
            ],
            "desired_outcome": f"获得清晰的{topic}决策框架和可操作的建议"
        }
        return brief

    def _add_article_angle(self, brief: Dict[str, Any], topic: str, fanouts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """添加文章独特角度"""
        brief["article_angle"] = {
            "hook": f"大多数{topic}指南都是推销文章，这篇不一样",
            "differentiator": "基于真实数据和专家访谈的决策框架",
            "promise": "读完本文后，你将能够自信地做出{topic}决策"
        }

        if fanouts:
            top_fanout = fanouts[0]
            brief["article_angle"]["primary_question"] = top_fanout.get("question", "")

        return brief

    def _add_decision_frame(self, brief: Dict[str, Any], fanouts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """添加决策框架"""
        brief["decision_frame"] = {
            "type": "comparison_and_recommendation",
            "structure": [
                "现状分析：为什么{topic}很重要",
                "方案对比：各方案优缺点",
                "决策树：If X -> Choose Y",
                "默认推荐：适合大多数情况的选择",
                "例外情况：何时不选择默认推荐"
            ],
            "questions_to_answer": [
                {
                    "question": f.get("question", ""),
                    "answer_type": f.get("answer_type", "decision")
                }
                for f in fanouts[:5]
            ]
        }
        return brief

    def _add_differentiation(self, brief: Dict[str, Any], citations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """添加差异化目标"""
        brief["differentiation_targets"] = [
            "对比文章：只罗列方案不做推荐",
            "厂商软文：只说好处不说风险",
            "技术文档：过于深入不够实用",
            "社交帖子：过于简短缺乏深度"
        ]

        brief["citation_requirements"] = {
            "min_count": 5,
            "min_authority_score": 0.75,
            "preferred_types": ["editorial", "official", "research"]
        }

        if citations:
            high_quality = [c for c in citations if c.get("authority") in ["editorial", "official"]]
            brief["citation_plan"] = {
                "planned": len(citations),
                "high_authority": len(high_quality),
                "status": "sufficient" if len(high_quality) >= 3 else "needs_more"
            }

        return brief

    def _add_must_elements(self, brief: Dict[str, Any], topic: str, fanouts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """添加必须要素"""
        brief["must_prove"] = [
            f"{topic}能为企业带来可量化的价值",
            "不同方案之间存在真实的权衡取舍",
            "存在一个适合大多数情况的默认选择"
        ]

        brief["must_include"] = [
            "清晰的决策框架（If X -> Choose Y）",
            "每个方案的真实优缺点",
            "成本和风险的具体数字",
            "实际案例和数据支撑",
            "收敛性总结（If You Only Remember One Thing）"
        ]

        brief["must_avoid"] = [
            "只推荐单一方案而不说例外",
            "使用模糊的描述性语言",
            "忽略潜在的负面影响",
            "过于技术化让决策者无法理解"
        ]

        return brief

    def _add_outline(self, brief: Dict[str, Any], topic: str, depth: str) -> Dict[str, Any]:
        """添加推荐大纲"""
        if depth == "brief":
            outline = [
                {
                    "heading": "为什么你需要了解{topic}",
                    "purpose": "建立紧迫感",
                    "target_length": "100词"
                },
                {
                    "heading": "{topic}的核心决策点",
                    "purpose": "明确关键选择",
                    "target_length": "200词"
                },
                {
                    "heading": "默认推荐方案",
                    "purpose": "给出清晰建议",
                    "target_length": "300词"
                }
            ]
        elif depth == "decision":
            outline = [
                {
                    "heading": "引言：{topic}决策的 stakes",
                    "purpose": "建立重要性",
                    "target_length": "150词"
                },
                {
                    "heading": "现状分析：当前{topic}的挑战",
                    "purpose": "问题定义",
                    "target_length": "300词"
                },
                {
                    "heading": "方案一：方案A的完整评估",
                    "purpose": "深入分析",
                    "target_length": "400词"
                },
                {
                    "heading": "方案二：方案B的完整评估",
                    "purpose": "深入分析",
                    "target_length": "400词"
                },
                {
                    "heading": "方案三：方案C的完整评估",
                    "purpose": "深入分析",
                    "target_length": "400词"
                },
                {
                    "heading": "对比矩阵：综合评估",
                    "purpose": "并列对比",
                    "target_length": "300词"
                },
                {
                    "heading": "决策树：如何选择",
                    "purpose": "If X -> Choose Y",
                    "target_length": "250词"
                },
                {
                    "heading": "默认推荐及例外情况",
                    "purpose": "收敛建议",
                    "target_length": "200词"
                },
                {
                    "heading": "If You Only Remember One Thing",
                    "purpose": "单句收敛",
                    "target_length": "50词"
                }
            ]
        else:
            outline = [
                {
                    "heading": "引言：为什么{topic}值得你花时间",
                    "purpose": "吸引读者",
                    "target_length": "200词"
                },
                {
                    "heading": "{topic}全景图",
                    "purpose": "概览全貌",
                    "target_length": "300词"
                },
                {
                    "heading": "核心方案对比",
                    "purpose": "深入分析",
                    "target_length": "500词"
                },
                {
                    "heading": "决策框架",
                    "purpose": "指导选择",
                    "target_length": "300词"
                },
                {
                    "heading": "实施建议",
                    "purpose": "可操作指南",
                    "target_length": "250词"
                },
                {
                    "heading": "总结与下一步",
                    "purpose": "收敛行动",
                    "target_length": "150词"
                }
            ]

        brief["recommended_outline"] = outline
        return brief

    def _add_citations(self, brief: Dict[str, Any], citations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """添加引用计划"""
        brief["citation_plan"] = {
            "citations": citations[:10] if citations else [],
            "sources_needed": [
                "行业报告",
                "学术论文",
                "专家观点",
                "实际案例"
            ]
        }
        return brief

    def export_to_yaml(self, brief: Dict[str, Any]) -> str:
        """导出为YAML格式"""
        import yaml
        return yaml.dump(brief, allow_unicode=True, default_flow_style=False)

    def export_to_markdown(self, brief: Dict[str, Any]) -> str:
        """导出为Markdown格式"""
        md = f"# {brief.get('working_title', 'Editorial Brief')}\n\n"
        md += f"**版本**: {brief.get('version', '1.0')} | "
        md += f"**深度**: {brief.get('depth', 'full')} | "
        md += f"**创建时间**: {brief.get('created_at', '')}\n\n"

        md += "## 读者画像\n\n"
        persona = brief.get("reader_persona", {})
        md += f"- **角色**: {persona.get('role', '')}\n"
        md += f"- **级别**: {persona.get('level', '')}\n"
        md += f"- **挑战**: {persona.get('challenge', '')}\n"
        md += f"- **期望**: {persona.get('desired_outcome', '')}\n\n"

        md += "## 文章角度\n\n"
        angle = brief.get("article_angle", {})
        md += f"- **Hook**: {angle.get('hook', '')}\n"
        md += f"- **差异化**: {angle.get('differentiator', '')}\n"
        md += f"- **承诺**: {angle.get('promise', '')}\n\n"

        md += "## 必须包含\n\n"
        for item in brief.get("must_include", []):
            md += f"- {item}\n"

        md += "\n## 推荐大纲\n\n"
        for i, section in enumerate(brief.get("recommended_outline", []), 1):
            md += f"{i}. **{section['heading']}** ({section['target_length']})\n"
            md += f"   - 目的: {section['purpose']}\n"

        return md
