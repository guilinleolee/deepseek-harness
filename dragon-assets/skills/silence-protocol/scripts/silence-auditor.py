#!/usr/bin/env python3
"""
沉默效果审计器
Silence Effect Auditor
周期性评估沉默协议效果并生成报告
"""

import json
import sys
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class SilenceMetrics:
    """沉默指标"""
    total_silence_events: int = 0
    total_card_attempts: int = 0
    correct_silences: int = 0
    incorrect_silences: int = 0
    timeout_triggers: int = 0
    wake_bypasses: int = 0
    cancelled_silences: int = 0

    # 用户反馈
    positive_feedback: int = 0
    negative_feedback: int = 0
    neutral_feedback: int = 0

    # 业务指标变化
    user_satisfaction_change: float = 0.0
    task_completion_change: float = 0.0
    deep_work_duration_change: float = 0.0

    # 时间范围
    start_date: str = ""
    end_date: str = ""


@dataclass
class HealthAssessment:
    """健康度评估"""
    health_score: float
    health_level: str  # 优秀/良好/警告/危险
    trend: str  # 改善中/稳定/退化中
    correctness_score: float
    timeout_rate: float
    natural_wake_rate: float
    silence_rate: float


@dataclass
class IdentifiedIssue:
    """识别的健康问题"""
    issue_id: str
    severity: str  # high/medium/low
    description: str
    affected_scenarios: list
    root_cause: str
    recommendation: str


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    priority: str  # high/medium/low
    suggestion: str
    expected_impact: str
    risk: str
    implementation_effort: str


@dataclass
class AuditReport:
    """审计报告"""
    report_id: str
    report_type: str  # daily/weekly/monthly
    evaluation_period: dict
    metrics: SilenceMetrics
    health: HealthAssessment
    issues: list[IdentifiedIssue]
    suggestions: list[OptimizationSuggestion]
    summary: str
    generated_at: str


class SilenceAuditor:
    """沉默效果审计器"""

    def __init__(self, history: list = None, statistics: dict = None):
        self.history = history or []
        self.statistics = statistics or {}
        self.metrics = SilenceMetrics()
        self.health_thresholds = {
            "silence_rate": {"min": 0.20, "max": 0.40},
            "correctness": {"min": 0.85},
            "timeout_rate": {"max": 0.10},
            "bypass_rate": {"max": 0.05}
        }

    def load_data(self, history: list, statistics: dict):
        """加载数据"""
        self.history = history
        self.statistics = statistics
        self._calculate_metrics()

    def _calculate_metrics(self):
        """计算指标"""
        m = self.metrics

        # 从历史记录计算
        m.total_silence_events = len([e for e in self.history if e.get("decision") == "silence"])
        m.correct_silences = len([e for e in self.history if e.get("was_correct") == True])
        m.incorrect_silences = len([e for e in self.history if e.get("was_correct") == False])
        m.timeout_triggers = len([e for e in self.history if e.get("outcome") == "timeout"])
        m.wake_bypasses = len([e for e in self.history if e.get("outcome") == "wake_bypass"])
        m.cancelled_silences = len([e for e in self.history if "cancelled" in str(e.get("outcome", ""))])

        # 从统计数据获取
        m.total_card_attempts = self.statistics.get("total_cards_processed", 0)
        m.positive_feedback = self.statistics.get("positive_feedback", 0)
        m.negative_feedback = self.statistics.get("negative_feedback", 0)
        m.neutral_feedback = self.statistics.get("neutral_feedback", 0)
        m.user_satisfaction_change = self.statistics.get("user_satisfaction_change", 0.0)
        m.task_completion_change = self.statistics.get("task_completion_change", 0.0)
        m.deep_work_duration_change = self.statistics.get("deep_work_duration_change", 0.0)

    def assess_health(self) -> HealthAssessment:
        """评估沉默健康度"""
        m = self.metrics

        # 计算各项得分
        silence_rate = m.total_silence_events / max(m.total_card_attempts, 1)
        correctness_rate = m.correct_silences / max(m.total_silence_events, 1)
        timeout_rate = m.timeout_triggers / max(m.total_silence_events, 1)
        bypass_rate = m.wake_bypasses / max(m.total_silence_events, 1)

        # 自然唤醒率
        other_deliveries = m.total_silence_events - m.timeout_triggers - m.wake_bypasses - m.cancelled_silences
        natural_wake_rate = other_deliveries / max(m.total_silence_events, 1)

        # 用户满意度得分
        total_feedback = m.positive_feedback + m.negative_feedback + m.neutral_feedback
        if total_feedback > 0:
            satisfaction_score = (m.positive_feedback * 1.0 + m.neutral_feedback * 0.5) / total_feedback
        else:
            satisfaction_score = 0.5

        # 综合健康度评分
        # 正确率(40%) + 唤醒效率(30%) + 沉默覆盖率(20%) + 用户满意度(10%)
        coverage_score = 100 if self.health_thresholds["silence_rate"]["min"] <= silence_rate <= self.health_thresholds["silence_rate"]["max"] \
            else max(0, 100 - abs(silence_rate - 0.30) * 200)

        health_score = (
            correctness_rate * 100 * 0.40 +
            (1 - timeout_rate) * 100 * 0.30 +
            coverage_score * 0.20 +
            satisfaction_score * 100 * 0.10
        )

        # 确定健康等级
        if health_score >= 90:
            health_level = "优秀"
        elif health_score >= 80:
            health_level = "良好"
        elif health_score >= 70:
            health_level = "警告"
        else:
            health_level = "危险"

        # 计算趋势（需要历史数据对比）
        trend = self._calculate_trend()

        return HealthAssessment(
            health_score=round(health_score, 1),
            health_level=health_level,
            trend=trend,
            correctness_score=round(correctness_rate * 100, 1),
            timeout_rate=round(timeout_rate * 100, 1),
            natural_wake_rate=round(natural_wake_rate * 100, 1),
            silence_rate=round(silence_rate * 100, 1)
        )

    def _calculate_trend(self) -> str:
        """计算趋势（需要历史数据）"""
        # 简化实现：基于用户满意度变化判断
        satisfaction_change = self.metrics.user_satisfaction_change
        if satisfaction_change > 0.05:
            return "改善中"
        elif satisfaction_change < -0.05:
            return "退化中"
        return "稳定"

    def identify_issues(self) -> list[IdentifiedIssue]:
        """识别问题"""
        issues = []
        m = self.metrics
        threshold = self.health_thresholds

        silence_rate = m.total_silence_events / max(m.total_card_attempts, 1)
        correctness_rate = m.correct_silences / max(m.total_silence_events, 1)
        timeout_rate = m.timeout_triggers / max(m.total_silence_events, 1)

        # 问题1：沉默过度
        if correctness_rate < 0.80:
            issues.append(IdentifiedIssue(
                issue_id="issue_001",
                severity="high" if correctness_rate < 0.75 else "medium",
                description=f"沉默正确率仅{correctness_rate*100:.1f}%，低于85%目标",
                affected_scenarios=self._get_affected_scenarios("incorrect"),
                root_cause="沉默阈值设置过低或唤醒条件过于严格",
                recommendation="降低沉默触发阈值，放宽唤醒条件"
            ))

        # 问题2：沉默不足
        if silence_rate < threshold["silence_rate"]["min"] - 0.10:
            issues.append(IdentifiedIssue(
                issue_id="issue_002",
                severity="medium",
                description=f"沉默率仅{silence_rate*100:.1f}%，低于20%目标",
                affected_scenarios=[],
                root_cause="沉默阈值设置过高",
                recommendation="提高沉默触发阈值"
            ))

        # 问题3：唤醒延迟
        if timeout_rate > threshold["timeout_rate"]["max"] * 1.5:
            issues.append(IdentifiedIssue(
                issue_id="issue_003",
                severity="high" if timeout_rate > 0.15 else "medium",
                description=f"超时触发率{timeout_rate*100:.1f}%，超过15%阈值",
                affected_scenarios=self._get_affected_scenarios("timeout"),
                root_cause="沉默时长设置过长或唤醒时机判断不准确",
                recommendation="缩短沉默时长，优化唤醒时机预测"
            ))

        # 问题4：用户满意度下降
        if m.user_satisfaction_change < -0.10:
            issues.append(IdentifiedIssue(
                issue_id="issue_004",
                severity="high",
                description=f"用户满意度下降{m.user_satisfaction_change*100:.1f}%",
                affected_scenarios=[],
                root_cause="沉默策略不符合用户预期",
                recommendation="收集用户反馈，调整沉默策略"
            ))

        return issues

    def _get_affected_scenarios(self, outcome_type: str) -> list:
        """获取受影响的场景"""
        scenarios = defaultdict(int)
        for event in self.history:
            if event.get("outcome") == outcome_type:
                reason = event.get("reason", "unknown")
                scenarios[reason] += 1
        return [f"{k}({v}次)" for k, v in sorted(scenarios.items(), key=lambda x: -x[1])[:3]]

    def generate_suggestions(self, issues: list[IdentifiedIssue]) -> list[OptimizationSuggestion]:
        """生成优化建议"""
        suggestions = []

        for issue in issues:
            if issue.severity == "high":
                suggestions.append(OptimizationSuggestion(
                    priority="high",
                    suggestion=f"优先解决：{issue.description}",
                    expected_impact="沉默正确率预计提升5-10%",
                    risk="低",
                    implementation_effort="1-2天"
                ))
            elif issue.severity == "medium":
                suggestions.append(OptimizationSuggestion(
                    priority="medium",
                    suggestion=f"次优先解决：{issue.description}",
                    expected_impact="沉默效果预计改善3-5%",
                    risk="低",
                    implementation_effort="2-3天"
                ))

        # 添加通用建议
        suggestions.append(OptimizationSuggestion(
            priority="low",
            suggestion="持续监控沉默指标，优化沉默策略",
            expected_impact="长期沉默效果稳定",
            risk="无",
            implementation_effort="持续"
        ))

        return suggestions

    def generate_report(self, report_type: str = "daily") -> AuditReport:
        """生成审计报告"""
        health = self.assess_health()
        issues = self.identify_issues()
        suggestions = self.generate_suggestions(issues)

        # 生成摘要
        summary_parts = []
        if health.health_level in ["优秀", "良好"]:
            summary_parts.append(f"沉默协议执行效果{health.health_level}。")
        else:
            summary_parts.append(f"沉默协议存在{len(issues)}个问题，需要优化。")

        summary_parts.append(f"沉默正确率{health.correctness_score}%，")
        summary_parts.append(f"超时触发率{health.timeout_rate}%。")
        if health.trend != "稳定":
            summary_parts.append(f"趋势{health.trend}。")

        summary = "".join(summary_parts)

        return AuditReport(
            report_id=f"ser_{report_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            report_type=report_type,
            evaluation_period={
                "start_date": self.metrics.start_date,
                "end_date": self.metrics.end_date
            },
            metrics=self.metrics,
            health=health,
            issues=issues,
            suggestions=suggestions,
            summary=summary,
            generated_at=datetime.now().isoformat()
        )

    def export_report(self, report: AuditReport, output_path: str = None) -> str:
        """导出报告为JSON"""
        report_dict = {
            "report_id": report.report_id,
            "report_type": report.report_type,
            "evaluation_period": report.evaluation_period,
            "metrics": {
                "total_silence_events": report.metrics.total_silence_events,
                "total_card_attempts": report.metrics.total_card_attempts,
                "silence_rate": f"{report.health.silence_rate}%",
                "correct_silences": report.metrics.correct_silences,
                "incorrect_silences": report.metrics.incorrect_silences,
                "timeout_triggers": report.metrics.timeout_triggers,
                "wake_bypasses": report.metrics.wake_bypasses,
                "cancelled_silences": report.metrics.cancelled_silences,
                "positive_feedback": report.metrics.positive_feedback,
                "negative_feedback": report.metrics.negative_feedback,
                "user_satisfaction_change": f"{report.metrics.user_satisfaction_change*100}%",
                "task_completion_change": f"{report.metrics.task_completion_change*100}%",
                "deep_work_duration_change": f"{report.metrics.deep_work_duration_change*100}%"
            },
            "health_assessment": {
                "health_score": report.health.health_score,
                "health_level": report.health.health_level,
                "trend": report.health.trend,
                "correctness_score": f"{report.health.correctness_score}%",
                "timeout_rate": f"{report.health.timeout_rate}%",
                "natural_wake_rate": f"{report.health.natural_wake_rate}%"
            },
            "issues": [
                {
                    "issue_id": i.issue_id,
                    "severity": i.severity,
                    "description": i.description,
                    "affected_scenarios": i.affected_scenarios,
                    "root_cause": i.root_cause,
                    "recommendation": i.recommendation
                }
                for i in report.issues
            ],
            "suggestions": [
                {
                    "priority": s.priority,
                    "suggestion": s.suggestion,
                    "expected_impact": s.expected_impact,
                    "risk": s.risk,
                    "implementation_effort": s.implementation_effort
                }
                for s in report.suggestions
            ],
            "summary": report.summary,
            "generated_at": report.generated_at
        }

        json_str = json.dumps(report_dict, ensure_ascii=False, indent=2)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(json_str)

        return json_str


def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print("用法: python silence-auditor.py <history.json> <statistics.json> [output.json]")
        sys.exit(1)

    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            history = json.load(f)
        with open(sys.argv[2], 'r', encoding='utf-8') as f:
            statistics = json.load(f)

        auditor = SilenceAuditor()
        auditor.load_data(history, statistics)

        output_path = sys.argv[3] if len(sys.argv) >= 4 else None
        report_json = auditor.export_report(
            auditor.generate_report("daily"),
            output_path
        )

        print(report_json)
    except Exception as e:
        print(f"审计失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
