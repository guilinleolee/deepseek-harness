#!/usr/bin/env python3
"""
Quality Gate
5层质量门控系统
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class GateResult:
    """门控结果"""
    layer: str
    passed: bool
    score: float
    issues: List[str]
    suggestions: List[str]


class QualityGate:
    """5层质量门控"""

    def __init__(self):
        self.thresholds = {
            "factual_accuracy": 1.0,
            "citation_count": 5,
            "citation_authority": 0.75,
            "paragraph_length_min": 134,
            "paragraph_length_max": 167,
            "entity_clarity": 0.8,
            "ai_score_max": 0.3,
            "word_count_min": 1200
        }

    def check(self, brief: Dict[str, Any], citations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        执行5层质量门控

        Args:
            brief: Editorial Brief
            citations: 引用列表

        Returns:
            Dict: 门控结果
        """
        results = []

        l1_result = self._check_l1_factual(brief, citations)
        results.append(l1_result)

        l2_result = self._check_l2_citation(brief, citations)
        results.append(l2_result)

        l3_result = self._check_l3_structure(brief)
        results.append(l3_result)

        l4_result = self._check_l4_entity_clarity(brief)
        results.append(l4_result)

        l5_result = self._check_l5_human_readability(brief)
        results.append(l5_result)

        overall_pass = all(r.passed for r in results)
        overall_score = sum(r.score for r in results) / len(results) if results else 0

        all_issues = []
        all_suggestions = []
        for r in results:
            all_issues.extend(r.issues)
            all_suggestions.extend(r.suggestions)

        return {
            "passed": overall_pass,
            "score": round(overall_score, 2),
            "layers": {
                r.layer: {
                    "passed": r.passed,
                    "score": r.score,
                    "issues": r.issues,
                    "suggestions": r.suggestions
                }
                for r in results
            },
            "all_issues": all_issues,
            "all_suggestions": all_suggestions,
            "reason": "通过" if overall_pass else f"未通过: {', '.join(all_issues[:3])}"
        }

    def _check_l1_factual(self, brief: Dict[str, Any], citations: List[Dict[str, Any]]) -> GateResult:
        """L1层: 事实核查"""
        issues = []
        suggestions = []
        score = 1.0

        if not citations:
            issues.append("缺少引用来源")
            suggestions.append("添加至少5个权威来源")
            score -= 0.4
        else:
            authoritative = [c for c in citations if c.get("authority") in ["editorial", "official", "research"]]
            if len(authoritative) < 3:
                issues.append(f"权威来源不足 (当前{len(authoritative)}个)")
                suggestions.append("增加学术论文、行业报告等权威来源")
                score -= 0.2

        for must_prove in brief.get("must_prove", []):
            if not must_prove or len(must_prove) < 10:
                issues.append(f"核心观点不够具体: {must_prove}")
                suggestions.append("确保每个核心观点都有具体的数据和证据支撑")
                score -= 0.15
                break

        return GateResult(
            layer="L1_事实核查",
            passed=score >= 0.7,
            score=score,
            issues=issues,
            suggestions=suggestions
        )

    def _check_l2_citation(self, brief: Dict[str, Any], citations: List[Dict[str, Any]]) -> GateResult:
        """L2层: 引用质量"""
        issues = []
        suggestions = []
        score = 1.0

        citation_count = len(citations)
        threshold = self.thresholds["citation_count"]

        if citation_count < threshold:
            issues.append(f"引用数量不足 ({citation_count}/{threshold})")
            suggestions.append(f"至少添加{threshold - citation_count}个额外引用")
            score -= 0.3 * (threshold - citation_count) / threshold
        else:
            score += 0.1 * min((citation_count - threshold) / threshold, 0.2)

        high_authority = [c for c in citations if c.get("authority") in ["editorial", "official"]]
        authority_ratio = len(high_authority) / citation_count if citation_count > 0 else 0

        if authority_ratio < 0.3:
            issues.append(f"编辑来源比例过低 ({authority_ratio:.0%})")
            suggestions.append("增加编辑来源和官方来源的比例")
            score -= 0.2

        for citation in citations[:3]:
            snippet = citation.get("content_snippet", "")
            if len(snippet) < 50:
                issues.append(f"引用摘要过短: {citation.get('title', '')[:30]}...")
                suggestions.append("为每个引用添加更详细的摘要")
                score -= 0.05
                break

        return GateResult(
            layer="L2_引用质量",
            passed=score >= 0.7,
            score=min(score, 1.0),
            issues=issues,
            suggestions=suggestions
        )

    def _check_l3_structure(self, brief: Dict[str, Any]) -> GateResult:
        """L3层: 结构化检查"""
        issues = []
        suggestions = []
        score = 1.0

        outline = brief.get("recommended_outline", [])
        if len(outline) < 3:
            issues.append(f"章节数量不足 ({len(outline)}个)")
            suggestions.append("至少包含5个主要章节")
            score -= 0.2

        for section in outline:
            length_str = section.get("target_length", "0词")
            try:
                length = int(length_str.replace("词", ""))
                if section.get("purpose") == "目的" and length > 100:
                    pass
            except:
                pass

        if "must_include" not in brief or len(brief["must_include"]) < 5:
            issues.append("缺少必须包含要素清单")
            suggestions.append("添加完整的must_include清单")
            score -= 0.15

        must_avoid = brief.get("must_avoid", [])
        if len(must_avoid) < 3:
            issues.append("必须避免要素不足")
            suggestions.append("至少列出3个需要避免的陷阱")
            score -= 0.1

        return GateResult(
            layer="L3_结构化",
            passed=score >= 0.7,
            score=min(score, 1.0),
            issues=issues,
            suggestions=suggestions
        )

    def _check_l4_entity_clarity(self, brief: Dict[str, Any]) -> GateResult:
        """L4层: 实体清晰度"""
        issues = []
        suggestions = []
        score = 1.0

        persona = brief.get("reader_persona", {})
        if not persona.get("role") or not persona.get("challenge"):
            issues.append("读者画像不完整")
            suggestions.append("完善reader_persona的role、level、challenge字段")
            score -= 0.25

        article_angle = brief.get("article_angle", {})
        if not article_angle.get("hook"):
            issues.append("缺少Hook")
            suggestions.append("添加一个能吸引读者的Hook")
            score -= 0.2

        if not article_angle.get("promise"):
            issues.append("缺少承诺")
            suggestions.append("明确告诉读者读完后能获得什么")
            score -= 0.15

        decision_frame = brief.get("decision_frame", {})
        if not decision_frame.get("structure"):
            issues.append("缺少决策框架")
            suggestions.append("添加If X -> Choose Y的决策框架")
            score -= 0.2

        return GateResult(
            layer="L4_实体清晰度",
            passed=score >= 0.7,
            score=min(score, 1.0),
            issues=issues,
            suggestions=suggestions
        )

    def _check_l5_human_readability(self, brief: Dict[str, Any]) -> GateResult:
        """L5层: 人类可读性"""
        issues = []
        suggestions = []
        score = 1.0

        differentiation = brief.get("differentiation_targets", [])
        if len(differentiation) < 3:
            issues.append("差异化目标不足")
            suggestions.append("至少列出3个差异化目标")
            score -= 0.2

        if "must_avoid" not in brief or not brief["must_avoid"]:
            issues.append("缺少必须避免清单")
            suggestions.append("添加明确的must_avoid清单")
            score -= 0.15

        outline = brief.get("recommended_outline", [])
        has_convergence = any(
            "收敛" in s.get("purpose", "") or "one thing" in s.get("heading", "").lower()
            for s in outline
        )

        if not has_convergence:
            issues.append("缺少收敛性总结")
            suggestions.append('添加"If You Only Remember One Thing"章节')
            score -= 0.15

        decision_frame = brief.get("decision_frame", {})
        has_default = any(
            "默认" in s or "推荐" in s
            for s in decision_frame.get("structure", [])
        )

        if not has_default:
            issues.append("缺少默认推荐")
            suggestions.append("添加明确的默认推荐和例外情况")
            score -= 0.1

        return GateResult(
            layer="L5_人类可读性",
            passed=score >= 0.7,
            score=min(score, 1.0),
            issues=issues,
            suggestions=suggestions
        )

    def check_by_id(self, content_id: str) -> Dict[str, Any]:
        """根据ID检查内容（模拟）"""
        return {
            "passed": True,
            "score": 0.85,
            "layers": {
                f"L{i}": {
                    "passed": True,
                    "score": 0.85
                }
                for i in range(1, 6)
            },
            "issues": [],
            "suggestions": ["内容质量良好"],
            "reason": "通过"
        }

    def generate_report(self, result: Dict[str, Any]) -> str:
        """生成质量报告"""
        report = "# GEO内容质量报告\n\n"
        report += f"## 总体评估\n\n"
        report += f"- **通过状态**: {'✅ 通过' if result['passed'] else '❌ 未通过'}\n"
        report += f"- **综合得分**: {result['score']:.2f}/1.00\n"
        report += f"- **原因**: {result.get('reason', '')}\n\n"

        report += "## 各层检查结果\n\n"
        for layer, data in result.get("layers", {}).items():
            status = "✅" if data["passed"] else "❌"
            report += f"### {layer} {status} ({data['score']:.2f})\n"
            if data.get("issues"):
                report += "**问题**:\n"
                for issue in data["issues"]:
                    report += f"- {issue}\n"
            if data.get("suggestions"):
                report += "**建议**:\n"
                for suggestion in data["suggestions"]:
                    report += f"- {suggestion}\n"
            report += "\n"

        return report
