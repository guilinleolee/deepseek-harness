#!/usr/bin/env python3
"""
Card Auditor - 卡片效果审计器
Card Dealing Protocol - 发牌协议脚本

周期性评估卡片发送效果，生成改进建议，支持日/周/月报告。

Usage:
    python card-auditor.py --period daily
    python card-auditor.py --period weekly --output report.json
    python card-auditor.py --period monthly --history history.json
    python card-auditor.py --interactive
"""

import json
import argparse
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from enum import Enum
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class HealthLevel(Enum):
    """健康度等级"""
    EXCELLENT = "excellent"    # 优秀: 90-100
    GOOD = "good"               # 良好: 75-89
    WARNING = "warning"          # 警告: 60-74
    DANGER = "danger"           # 危险: <60


@dataclass
class CardMetrics:
    """卡片指标"""
    # 效率指标
    total_cards: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    avg_frequency_per_hour: float = 0.0
    quality_gate_pass_rate: float = 0.0

    # 响应指标
    confirmation_rate: float = 0.0
    avg_response_time_minutes: float = 0.0
    action_completion_rate: float = 0.0
    ignore_rate: float = 0.0

    # 沉默协议协同
    silence_protection_rate: float = 0.0
    flow_interruptions: int = 0
    queue_backlog_rate: float = 0.0
    delayed_accuracy_rate: float = 0.0

    # 用户满意度
    satisfaction_score: float = 0.0
    helpfulness_score: float = 0.0
    disturbance_score: float = 0.0


@dataclass
class HealthAssessment:
    """健康度评估"""
    health_score: float
    health_level: str
    trend: str  # improving/stable/declining
    efficiency_score: float
    response_score: float
    silence_score: float
    satisfaction_score: float


@dataclass
class IdentifiedIssue:
    """识别的问题"""
    issue_id: str
    severity: str  # high/medium/low
    description: str
    affected_metrics: List[str]
    root_cause: str
    recommendation: str


@dataclass
class AuditReport:
    """审计报告"""
    report_id: str
    period: str
    period_start: str
    period_end: str
    health: HealthAssessment
    metrics: CardMetrics
    issues: List[IdentifiedIssue]
    recommendations: Dict[str, any]
    generated_at: str


class CardAuditor:
    """卡片效果审计器"""

    # 健康度权重
    WEIGHTS = {
        'efficiency': 0.25,
        'response': 0.25,
        'silence': 0.25,
        'satisfaction': 0.25
    }

    # 目标值
    TARGETS = {
        'confirmation_rate': 0.80,
        'action_completion_rate': 0.70,
        'interruption_rate': 0.05,
        'satisfaction_score': 4.0,
        'quality_gate_pass_rate': 0.85,
        'silence_protection_rate': 0.95,
        'ignore_rate': 0.20
    }

    # 告警阈值
    ALERT_THRESHOLDS = {
        'confirmation_rate': 0.60,
        'action_completion_rate': 0.50,
        'interruption_rate': 0.10,
        'satisfaction_score': 3.0,
        'ignore_rate': 0.40
    }

    def __init__(self, config: Optional[dict] = None):
        """初始化审计器"""
        self.config = config or {}
        self._load_targets()

    def _load_targets(self):
        """从配置加载目标值"""
        self.TARGETS.update(self.config.get('targets', {}))
        self.ALERT_THRESHOLDS.update(
            self.config.get('alert_thresholds', {}))

    def calculate_health_score(self, metrics: CardMetrics) -> HealthAssessment:
        """计算健康度得分"""
        # 效率分
        efficiency_factors = [
            min(1.0, metrics.quality_gate_pass_rate /
                self.TARGETS['quality_gate_pass_rate']),
            max(0.0, 1.0 - metrics.avg_frequency_per_hour / 5.0)
        ]
        efficiency_score = sum(efficiency_factors) / len(efficiency_factors)

        # 响应分
        response_factors = [
            metrics.confirmation_rate / self.TARGETS['confirmation_rate'],
            metrics.action_completion_rate / self.TARGETS['action_completion_rate'],
            max(0.0, 1.0 - metrics.ignore_rate / self.TARGETS['ignore_rate']),
            max(0.0, 1.0 - metrics.avg_response_time_minutes / 15.0)
        ]
        response_score = sum(response_factors) / len(response_factors)

        # 沉默分
        silence_factors = [
            metrics.silence_protection_rate / self.TARGETS['silence_protection_rate'],
            max(0.0, 1.0 - metrics.flow_interruptions / 3.0),
            max(0.0, 1.0 - metrics.queue_backlog_rate / 0.30)
        ]
        silence_score = sum(silence_factors) / len(silence_factors)

        # 满意分
        satisfaction_factors = [
            metrics.satisfaction_score / 5.0,
            metrics.helpfulness_score / 5.0,
            max(0.0, 1.0 - metrics.disturbance_score / 3.5)
        ]
        satisfaction_score_raw = sum(
            satisfaction_factors) / len(satisfaction_factors)

        # 综合健康度
        health_score = (
            efficiency_score * self.WEIGHTS['efficiency'] +
            response_score * self.WEIGHTS['response'] +
            silence_score * self.WEIGHTS['silence'] +
            satisfaction_score_raw * self.WEIGHTS['satisfaction']
        ) * 100

        # 确定等级
        if health_score >= 90:
            level = HealthLevel.EXCELLENT
        elif health_score >= 75:
            level = HealthLevel.GOOD
        elif health_score >= 60:
            level = HealthLevel.WARNING
        else:
            level = HealthLevel.DANGER

        # 趋势判断（简化版，需要历史数据对比）
        trend = "stable"

        return HealthAssessment(
            health_score=round(health_score, 1),
            health_level=level.value,
            trend=trend,
            efficiency_score=round(efficiency_score * 100, 1),
            response_score=round(response_score * 100, 1),
            silence_score=round(silence_score * 100, 1),
            satisfaction_score=round(satisfaction_score_raw * 100, 1)
        )

    def identify_issues(self, metrics: CardMetrics,
                        previous_metrics: Optional[CardMetrics] = None
                        ) -> List[IdentifiedIssue]:
        """识别问题"""
        issues = []
        issue_id_counter = 1

        # 误发问题
        if metrics.confirmation_rate < self.ALERT_THRESHOLDS['confirmation_rate']:
            severity = "high" if metrics.confirmation_rate < 0.4 else "medium"
            issues.append(IdentifiedIssue(
                issue_id=f"issue_{issue_id_counter:03d}",
                severity=severity,
                description=f"确认率仅{metrics.confirmation_rate*100:.1f}%，"
                            f"低于{self.ALERT_THRESHOLDS['confirmation_rate']*100:.0f}%告警阈值",
                affected_metrics=["confirmation_rate", "ignore_rate"],
                root_cause="发牌阈值设置过低或用户意图误判",
                recommendation="提高发牌质量门控阈值，增加用户价值验证"
            ))
            issue_id_counter += 1

        # 漏发问题
        if (previous_metrics and
                metrics.confirmation_rate > previous_metrics.confirmation_rate and
                metrics.ignore_rate < 0.1):
            issues.append(IdentifiedIssue(
                issue_id=f"issue_{issue_id_counter:03d}",
                severity="medium",
                description="确认率提升但忽略率很低，可能存在漏发",
                affected_metrics=["confirmation_rate"],
                root_cause="发牌时机判断过于保守",
                recommendation="降低发牌阈值，增加试探性发牌"
            ))
            issue_id_counter += 1

        # 打断问题
        if metrics.flow_interruptions > 3:
            severity = "high" if metrics.flow_interruptions > 5 else "medium"
            issues.append(IdentifiedIssue(
                issue_id=f"issue_{issue_id_counter:03d}",
                severity=severity,
                description=f"心流打断{metrics.flow_interruptions}次，超过3次阈值",
                affected_metrics=["silence_protection_rate", "satisfaction_score"],
                root_cause="心流检测不准确或沉默协议协同不完善",
                recommendation="加强心流状态检测，优化沉默协议协同逻辑"
            ))
            issue_id_counter += 1

        # 行动完成率低
        if (metrics.action_completion_rate <
                self.ALERT_THRESHOLDS['action_completion_rate']):
            severity = "high" if metrics.action_completion_rate < 0.4 else "medium"
            issues.append(IdentifiedIssue(
                issue_id=f"issue_{issue_id_counter:03d}",
                severity=severity,
                description=f"行动完成率仅{metrics.action_completion_rate*100:.1f}%，"
                            f"低于{self.ALERT_THRESHOLDS['action_completion_rate']*100:.0f}%目标",
                affected_metrics=["action_completion_rate"],
                root_cause="行动描述不够清晰或可行性不足",
                recommendation="优化行动卡模板，增加具体示例和步骤分解"
            ))
            issue_id_counter += 1

        # 满意度低
        if (metrics.satisfaction_score <
                self.ALERT_THRESHOLDS['satisfaction_score']):
            severity = "high" if metrics.satisfaction_score < 2.5 else "medium"
            issues.append(IdentifiedIssue(
                issue_id=f"issue_{issue_id_counter:03d}",
                severity=severity,
                description=f"用户满意度仅{metrics.satisfaction_score:.1f}/5.0，"
                            f"低于{self.ALERT_THRESHOLDS['satisfaction_score']:.0f}/5.0告警阈值",
                affected_metrics=["satisfaction_score", "helpfulness_score",
                                 "disturbance_score"],
                root_cause="多维度综合问题，需逐项分析",
                recommendation="分析各维度满意度分布，识别主要短板"
            ))
            issue_id_counter += 1

        # 打断率高
        interruption_rate = (metrics.flow_interruptions /
                            max(1, metrics.total_cards))
        if interruption_rate > self.ALERT_THRESHOLDS['interruption_rate']:
            issues.append(IdentifiedIssue(
                issue_id=f"issue_{issue_id_counter:03d}",
                severity="high",
                description=f"打断率{interruption_rate*100:.1f}%，超过5%阈值",
                affected_metrics=["silence_protection_rate"],
                root_cause="发牌时机判断不准确",
                recommendation="加强发牌前延迟检查，优化自然断点检测"
            ))

        return issues

    def generate_recommendations(self, issues: List[IdentifiedIssue],
                                 health: HealthAssessment) -> Dict:
        """生成改进建议"""
        immediate = []
        short_term = []
        long_term = []

        high_severity_issues = [i for i in issues if i.severity == "high"]

        # 紧急建议
        for issue in high_severity_issues:
            if "确认率" in issue.description:
                immediate.append({
                    "action": "提高发牌质量门控阈值",
                    "priority": "high",
                    "expected_impact": "+10% 确认率"
                })
            if "打断" in issue.description:
                immediate.append({
                    "action": "加强心流检测算法",
                    "priority": "high",
                    "expected_impact": "-50% 打断率"
                })
            if "满意度" in issue.description:
                immediate.append({
                    "action": "分析满意度各维度短板",
                    "priority": "high",
                    "expected_impact": "+0.5 满意度"
                })

        # 短期建议
        for issue in issues:
            if issue.severity == "medium":
                if "行动完成率" in issue.description:
                    short_term.append({
                        "action": "优化行动卡模板",
                        "priority": "medium",
                        "expected_impact": "+8% 行动完成率"
                    })
                if "队列" in issue.description:
                    short_term.append({
                        "action": "优化队列管理策略",
                        "priority": "medium",
                        "expected_impact": "-20% 队列积压"
                    })

        # 长期建议
        if health.health_level in ["warning", "danger"]:
            long_term.append({
                "action": "建立发牌质量A/B测试机制",
                "priority": "low",
                "expected_impact": "持续优化基础"
            })
            long_term.append({
                "action": "引入机器学习优化发牌决策",
                "priority": "low",
                "expected_impact": "+15% 综合质量"
            })

        return {
            "immediate": immediate,
            "short_term": short_term,
            "long_term": long_term
        }

    def audit(self, period: str,
              history_data: Optional[dict] = None,
              previous_period: Optional[dict] = None) -> AuditReport:
        """主审计方法"""
        # 计算指标
        metrics = self._calculate_metrics(history_data or {})

        # 计算健康度
        prev_metrics = None
        if previous_period:
            prev_metrics = self._calculate_metrics(previous_period)
        health = self.calculate_health_score(metrics)

        # 识别问题
        issues = self.identify_issues(metrics, prev_metrics)

        # 生成建议
        recommendations = self.generate_recommendations(issues, health)

        # 确定时间范围
        now = datetime.now()
        if period == "daily":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "weekly":
            start = now - timedelta(days=7)
        elif period == "monthly":
            start = now - timedelta(days=30)
        else:
            start = now - timedelta(days=1)

        return AuditReport(
            report_id=f"card_audit_{period}_{int(now.timestamp())}",
            period=period,
            period_start=start.isoformat(),
            period_end=now.isoformat(),
            health=health,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            generated_at=now.isoformat()
        )

    def _calculate_metrics(self, data: dict) -> CardMetrics:
        """计算指标"""
        cards = data.get('cards', [])

        metrics = CardMetrics()

        # 基本统计
        metrics.total_cards = len(cards)
        by_type = {}
        for card in cards:
            t = card.get('card_type', 'unknown')
            by_type[t] = by_type.get(t, 0) + 1
        metrics.by_type = by_type

        # 响应指标
        confirmed = len([c for c in cards if c.get('status') == 'confirmed'])
        ignored = len([c for c in cards if c.get('status') == 'ignored'])
        sent = len([c for c in cards if c.get('status') == 'sent'])

        if sent > 0:
            metrics.confirmation_rate = confirmed / sent
            metrics.ignore_rate = ignored / sent

        # 行动完成率
        action_cards = [c for c in cards if c.get('card_type') == 'action']
        completed = len([c for c in action_cards if c.get('completed')])
        if action_cards:
            metrics.action_completion_rate = completed / len(action_cards)

        # 沉默协议协同
        metrics.flow_interruptions = data.get('flow_interruptions', 0)
        metrics.silence_protection_rate = data.get('silence_protection_rate', 0.95)

        # 满意度
        metrics.satisfaction_score = data.get('satisfaction_score', 4.0)
        metrics.helpfulness_score = data.get('helpfulness_score', 4.0)
        metrics.disturbance_score = data.get('disturbance_score', 2.0)

        # 质量门控
        passed = len([c for c in cards if c.get('evaluation_score', 0) >= 0.5])
        if cards:
            metrics.quality_gate_pass_rate = passed / len(cards)

        return metrics


def load_history(filepath: str) -> dict:
    """从文件加载历史数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_report(report: AuditReport, filepath: str):
    """保存报告到文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(asdict(report), f, ensure_ascii=False, indent=2)


def interactive_audit():
    """交互式审计"""
    print("=== Card Auditor 交互模式 ===")
    print("选择审计周期: daily / weekly / monthly / quit\n")

    auditor = CardAuditor()

    while True:
        period = input("审计周期 (daily/weekly/monthly/quit): ").strip().lower()
        if period in ['quit', 'exit', 'q']:
            break

        if period not in ['daily', 'weekly', 'monthly']:
            print("无效周期，请输入 daily/weekly/monthly")
            continue

        # 尝试加载历史数据
        history_file = input("历史数据文件 (回车跳过): ").strip()
        history = {}
        if history_file:
            try:
                history = load_history(history_file)
            except Exception as e:
                print(f"加载历史数据失败: {e}")

        # 尝试加载上一周期数据（用于趋势分析）
        prev_file = input("上一周期数据文件 (回车跳过): ").strip()
        previous = {}
        if prev_file:
            try:
                previous = load_history(prev_file)
            except Exception as e:
                print(f"加载数据失败: {e}")

        report = auditor.audit(period, history, previous)

        print(f"\n{'='*60}")
        print(f"卡片效果审计报告 - {report.period}")
        print(f"{'='*60}")
        print(f"\n综合健康度: {report.health.health_score:.1f}/100 ({report.health.health_level})")
        print(f"趋势: {report.health.trend}")
        print(f"\n分项得分:")
        print(f"  效率分: {report.health.efficiency_score:.1f}")
        print(f"  响应分: {report.health.response_score:.1f}")
        print(f"  沉默分: {report.health.silence_score:.1f}")
        print(f"  满意分: {report.health.satisfaction_score:.1f}")

        print(f"\n关键指标:")
        m = report.metrics
        print(f"  总发牌数: {m.total_cards}")
        print(f"  确认率: {m.confirmation_rate*100:.1f}%")
        print(f"  行动完成率: {m.action_completion_rate*100:.1f}%")
        print(f"  打断次数: {m.flow_interruptions}")
        print(f"  满意度: {m.satisfaction_score:.1f}/5.0")

        if report.issues:
            print(f"\n识别的问题 ({len(report.issues)}个):")
            for issue in report.issues:
                severity_icon = {"high": "🔴", "medium": "🟡",
                                 "low": "🟢"}.get(issue.severity, "⚪")
                print(f"  {severity_icon} [{issue.severity.upper()}] {issue.description}")
                print(f"     根因: {issue.root_cause}")
                print(f"     建议: {issue.recommendation}")

        if report.recommendations.get('immediate'):
            print(f"\n紧急建议:")
            for rec in report.recommendations['immediate']:
                print(f"  • {rec['action']} (预期: {rec['expected_impact']})")


def main():
    parser = argparse.ArgumentParser(description="Card Auditor - 卡片效果审计器")
    parser.add_argument('--period', type=str, required=True,
                        choices=['daily', 'weekly', 'monthly'],
                        help='审计周期')
    parser.add_argument('--history', type=str, help='历史数据文件')
    parser.add_argument('--previous', type=str,
                        help='上一周期数据文件 (用于趋势分析)')
    parser.add_argument('--output', type=str, help='报告输出文件')
    parser.add_argument('--interactive', action='store_true', help='交互模式')
    parser.add_argument('--config', type=str, help='配置文件')

    args = parser.parse_args()

    if args.interactive:
        interactive_audit()
        return

    # 加载配置
    config = {}
    if args.config:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)

    auditor = CardAuditor(config)

    # 加载数据
    history = {}
    if args.history:
        history = load_history(args.history)

    previous = {}
    if args.previous:
        previous = load_history(args.previous)

    # 生成报告
    report = auditor.audit(args.period, history, previous)

    # 输出
    if args.output:
        save_report(report, args.output)
        print(f"报告已保存到: {args.output}")
    else:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
