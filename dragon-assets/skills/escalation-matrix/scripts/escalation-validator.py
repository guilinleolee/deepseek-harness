#!/usr/bin/env python3
"""
escalation-validator.py — 升级路径验证器
Escalation Matrix V9.02 — 天龙引擎

功能:
  1. 完整性验证 — 每个失败模式是否有升级路径
  2. 有效性验证 — 升级路径逻辑是否正确，无循环升级风险
  3. 可行性验证 — 每层是否有足够处理能力
  4. 组织镜像4标准验证 — 明确分工/路径/复核点/兜底点
  5. 场景模拟 — 模拟各种失败场景验证升级响应

Usage:
    python escalation-validator.py --config escalation.yaml
    python escalation-validator.py --interactive
    python escalation-validator.py --simulate failure_mode --config escalation.yaml
    python escalation-validator.py --audit --config escalation.yaml
"""

from __future__ import annotations
import argparse
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


# ─────────────────────────────────────────────
# 数据模型
# ─────────────────────────────────────────────

class ValidationStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIP = "SKIP"


class ValidationType(Enum):
    COMPLETENESS = "completeness"      # 完整性
    VALIDITY = "validity"              # 有效性
    FEASIBILITY = "feasibility"        # 可行性
    ORG_STANDARDS = "org_standards"   # 组织镜像4标准
    SIMULATION = "simulation"          # 场景模拟


class OrgStandard(Enum):
    CLEAR_DIVISION = "明确分工"       # 谁产出/判断/复核/升级
    CLEAR_ESCALATION = "明确升级路径"  # 出了问题往哪里抬
    CLEAR_REVIEW = "明确复核点"        # 哪些节点必须复核
    CLEAR_FALLBACK = "明确兜底点"     # 兜不住时谁接管


@dataclass
class EscalationLevel:
    """升级层级"""
    level: int
    name: str
    description: str
    capabilities: list[str] = field(default_factory=list)
    limits: list[str] = field(default_factory=list)
    escalation_threshold: list[str] = field(default_factory=list)
    response_time_sla: str = ""


@dataclass
class FailureMode:
    """失败模式"""
    id: str
    name: str
    description: str
    severity: str = "medium"  # low/medium/high/critical
    escalation_level: int = 1
    retry_threshold: int = 3
    time_threshold_seconds: int = 300
    error_types: list[str] = field(default_factory=list)


@dataclass
class EscalationPath:
    """升级路径"""
    from_level: int
    to_level: int
    trigger_condition: str
    trigger_type: str  # retry_exceeded/time_exceeded/error_type/impact_level
    response_time_sla: str
    fallback_enabled: bool = True


@dataclass
class ValidationCheck:
    """单项验证结果"""
    check_id: str
    check_type: ValidationType
    title: str
    status: ValidationStatus
    details: str
    recommendation: str = ""
    affected_items: list[str] = field(default_factory=list)
    severity: str = "medium"  # low/medium/high/critical


@dataclass
class ValidationReport:
    """完整验证报告"""
    report_id: str
    config_name: str
    generated_at: str
    overall_status: ValidationStatus
    total_checks: int
    passed_checks: int
    failed_checks: int
    warning_checks: int
    checks: list[ValidationCheck]
    org_standards_score: dict[str, int] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    risk_summary: str = ""


# ─────────────────────────────────────────────
# 验证引擎
# ─────────────────────────────────────────────

class EscalationValidator:
    """升级路径验证器"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._build_internal_models()

    def _build_internal_models(self):
        """从配置字典构建内部数据模型"""
        # 解析升级层级
        self.levels: dict[int, EscalationLevel] = {}
        raw_levels = self.config.get("escalation_levels", {})
        for key, val in raw_levels.items():
            lvl = int(key.split("_")[-1])
            self.levels[lvl] = EscalationLevel(
                level=lvl,
                name=val.get("name", ""),
                description=val.get("description", ""),
                capabilities=val.get("capability", []),
                limits=val.get("limits", []),
                escalation_threshold=val.get("escalation_threshold", []),
                response_time_sla=val.get("response_time_sla", ""),
            )

        # 解析失败模式
        self.failure_modes: dict[str, FailureMode] = {}
        raw_failures = self.config.get("failure_modes", [])
        for fm in raw_failures:
            self.failure_modes[fm["id"]] = FailureMode(
                id=fm["id"],
                name=fm.get("name", ""),
                description=fm.get("description", ""),
                severity=fm.get("severity", "medium"),
                escalation_level=fm.get("escalation_level", 1),
                retry_threshold=fm.get("retry_threshold", 3),
                time_threshold_seconds=fm.get("time_threshold_seconds", 300),
                error_types=fm.get("error_types", []),
            )

        # 解析升级路径
        self.escalation_paths: list[EscalationPath] = []
        raw_paths = self.config.get("escalation_paths", [])
        for ep in raw_paths:
            self.escalation_paths.append(EscalationPath(
                from_level=ep.get("from_level", 1),
                to_level=ep.get("to_level", 2),
                trigger_condition=ep.get("trigger_condition", ""),
                trigger_type=ep.get("trigger_type", ""),
                response_time_sla=ep.get("response_time_sla", ""),
                fallback_enabled=ep.get("fallback_enabled", True),
            ))

        # 解析兜底配置
        self.fallback_config = self.config.get("fallback", {})
        self.org_standards = self.config.get("org_standards", {})

    # ─────────────────────────────────────────
    # 核心验证方法
    # ─────────────────────────────────────────

    def validate_all(self) -> ValidationReport:
        """执行全部验证"""
        checks: list[ValidationCheck] = []

        checks.extend(self._validate_completeness())
        checks.extend(self._validate_validity())
        checks.extend(self._validate_feasibility())
        checks.extend(self._validate_org_standards())
        checks.extend(self._validate_fallback())

        passed = sum(1 for c in checks if c.status == ValidationStatus.PASS)
        failed = sum(1 for c in checks if c.status == ValidationStatus.FAIL)
        warnings = sum(1 for c in checks if c.status == ValidationStatus.WARNING)

        # 整体状态
        if failed > 0:
            overall = ValidationStatus.FAIL
        elif warnings > passed // 3:
            overall = ValidationStatus.WARNING
        else:
            overall = ValidationStatus.PASS

        # 组织镜像4标准评分
        org_scores = {
            "明确分工": self._score_clear_division(),
            "明确升级路径": self._score_clear_escalation(),
            "明确复核点": self._score_clear_review(),
            "明确兜底点": self._score_clear_fallback(),
        }

        report = ValidationReport(
            report_id=f"eval-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            config_name=self.config.get("name", "unknown"),
            generated_at=datetime.now().isoformat(),
            overall_status=overall,
            total_checks=len(checks),
            passed_checks=passed,
            failed_checks=failed,
            warning_checks=warnings,
            checks=checks,
            org_standards_score=org_scores,
            recommendations=self._generate_recommendations(checks),
            risk_summary=self._summarize_risk(checks),
        )
        return report

    def _validate_completeness(self) -> list[ValidationCheck]:
        """完整性验证 — 每个失败模式都有升级路径"""
        checks: list[ValidationCheck] = []

        # 检查1: 每个失败模式是否有升级路径
        if not self.failure_modes:
            checks.append(ValidationCheck(
                check_id="C-001",
                check_type=ValidationType.COMPLETENESS,
                title="失败模式覆盖",
                status=ValidationStatus.WARNING,
                details="未定义任何失败模式",
                recommendation="定义至少3个主要失败模式及其升级路径",
                severity="high",
            ))
        else:
            covered = 0
            uncovered = []
            for fm_id, fm in self.failure_modes.items():
                if any(ep.from_level == fm.escalation_level for ep in self.escalation_paths):
                    covered += 1
                else:
                    uncovered.append(fm_id)

            if uncovered:
                checks.append(ValidationCheck(
                    check_id="C-001",
                    check_type=ValidationType.COMPLETENESS,
                    title="失败模式升级路径覆盖",
                    status=ValidationStatus.FAIL,
                    details=f"失败模式 {len(uncovered)} 个无升级路径: {uncovered}",
                    recommendation="为每个失败模式定义至少一条升级路径",
                    affected_items=uncovered,
                    severity="critical",
                ))
            else:
                checks.append(ValidationCheck(
                    check_id="C-001",
                    check_type=ValidationType.COMPLETENESS,
                    title="失败模式升级路径覆盖",
                    status=ValidationStatus.PASS,
                    details=f"所有 {covered} 个失败模式都有升级路径",
                ))

        # 检查2: 每个层级是否有明确定义
        if not self.levels:
            checks.append(ValidationCheck(
                check_id="C-002",
                check_type=ValidationType.COMPLETENESS,
                title="升级层级定义",
                status=ValidationStatus.FAIL,
                details="未定义任何升级层级",
                recommendation="定义至少L1-L2两级升级层级",
                severity="critical",
            ))
        else:
            missing_fields = []
            for lvl_num, lvl in sorted(self.levels.items()):
                if not lvl.name:
                    missing_fields.append(f"L{lvl_num}缺少name")
                if not lvl.description:
                    missing_fields.append(f"L{lvl_num}缺少description")
                if not lvl.capabilities:
                    missing_fields.append(f"L{lvl_num}缺少capabilities")

            if missing_fields:
                checks.append(ValidationCheck(
                    check_id="C-002",
                    check_type=ValidationType.COMPLETENESS,
                    title="升级层级定义完整性",
                    status=ValidationStatus.WARNING,
                    details=f"层级定义不完整: {', '.join(missing_fields)}",
                    recommendation="为每个层级填充name/description/capabilities",
                    severity="medium",
                ))
            else:
                checks.append(ValidationCheck(
                    check_id="C-002",
                    check_type=ValidationType.COMPLETENESS,
                    title="升级层级定义完整性",
                    status=ValidationStatus.PASS,
                    details=f"所有 {len(self.levels)} 个层级定义完整",
                ))

        # 检查3: 每个触发条件是否有处理时限
        no_sla = [ep for ep in self.escalation_paths if not ep.response_time_sla]
        if no_sla:
            checks.append(ValidationCheck(
                check_id="C-003",
                check_type=ValidationType.COMPLETENESS,
                title="升级触发SLA定义",
                status=ValidationStatus.WARNING,
                details=f"{len(no_sla)} 条升级路径无SLA定义",
                recommendation="为所有升级路径定义响应时限",
                severity="medium",
            ))
        else:
            checks.append(ValidationCheck(
                check_id="C-003",
                check_type=ValidationType.COMPLETENESS,
                title="升级触发SLA定义",
                status=ValidationStatus.PASS,
                details=f"所有 {len(self.escalation_paths)} 条路径都有SLA",
            ))

        return checks

    def _validate_validity(self) -> list[ValidationCheck]:
        """有效性验证 — 升级路径逻辑正确性"""
        checks: list[ValidationCheck] = []

        # 检查1: 循环升级风险
        circular = self._detect_circular_escalation()
        if circular:
            checks.append(ValidationCheck(
                check_id="V-001",
                check_type=ValidationType.VALIDITY,
                title="循环升级检测",
                status=ValidationStatus.FAIL,
                details=f"检测到循环升级: {' → '.join(str(x) for x in circular)}",
                recommendation="移除循环依赖，确保升级链是单向的",
                severity="critical",
            ))
        else:
            checks.append(ValidationCheck(
                check_id="V-001",
                check_type=ValidationType.VALIDITY,
                title="循环升级检测",
                status=ValidationStatus.PASS,
                details="无循环升级风险",
            ))

        # 检查2: 层级授权合理性 (不能越级太多)
        problematic_skips = []
        for ep in self.escalation_paths:
            diff = ep.to_level - ep.from_level
            if diff > 1:
                problematic_skips.append(
                    f"L{ep.from_level}→L{ep.to_level} (跳{diff}级)"
                )

        if problematic_skips:
            checks.append(ValidationCheck(
                check_id="V-002",
                check_type=ValidationType.VALIDITY,
                title="层级跳跃合理性",
                status=ValidationStatus.WARNING,
                details=f"发现越级升级: {', '.join(problematic_skips)}",
                recommendation="优先逐级升级，除非有明确业务理由",
                affected_items=problematic_skips,
                severity="medium",
            ))
        else:
            checks.append(ValidationCheck(
                check_id="V-002",
                check_type=ValidationType.VALIDITY,
                title="层级跳跃合理性",
                status=ValidationStatus.PASS,
                details="所有升级都是逐级或合理跳跃",
            ))

        # 检查3: 升级触发条件无冲突
        conflicts = self._detect_trigger_conflicts()
        if conflicts:
            checks.append(ValidationCheck(
                check_id="V-003",
                check_type=ValidationType.VALIDITY,
                title="触发条件冲突检测",
                status=ValidationStatus.FAIL,
                details=f"发现 {len(conflicts)} 个触发条件冲突",
                recommendation="确保相同失败模式的触发条件不重叠",
                affected_items=conflicts,
                severity="high",
            ))
        else:
            checks.append(ValidationCheck(
                check_id="V-003",
                check_type=ValidationType.VALIDITY,
                title="触发条件冲突检测",
                status=ValidationStatus.PASS,
                details="无触发条件冲突",
            ))

        # 检查4: 最高层级必须有兜底
        max_level = max((lvl.level for lvl in self.levels.values()), default=0)
        has_fallback_at_max = any(
            fb.get("handler") for fb in self.fallback_config.get("scenarios", [])
            if fb.get("level") == max_level or fb.get("type") == "max_level_reached"
        )
        if max_level > 0 and not has_fallback_at_max:
            checks.append(ValidationCheck(
                check_id="V-004",
                check_type=ValidationType.VALIDITY,
                title="最高层级兜底覆盖",
                status=ValidationStatus.FAIL,
                details=f"L{max_level} 无人工兜底配置",
                recommendation=f"L{max_level} 必须定义最终兜底处理人",
                severity="critical",
            ))
        elif max_level > 0:
            checks.append(ValidationCheck(
                check_id="V-004",
                check_type=ValidationType.VALIDITY,
                title="最高层级兜底覆盖",
                status=ValidationStatus.PASS,
                details=f"L{max_level} 有人工兜底配置",
            ))

        return checks

    def _validate_feasibility(self) -> list[ValidationCheck]:
        """可行性验证 — 每层有足够处理能力"""
        checks: list[ValidationCheck] = []

        for lvl_num, lvl in sorted(self.levels.items()):
            if not lvl.capabilities:
                checks.append(ValidationCheck(
                    check_id=f"F-{lvl_num:02d}-001",
                    check_type=ValidationType.FEASIBILITY,
                    title=f"L{lvl_num} ({lvl.name}) 处理能力定义",
                    status=ValidationStatus.FAIL,
                    details="L没有定义任何处理能力",
                    recommendation="明确L的处理能力范围",
                    severity="high",
                ))
            elif len(lvl.capabilities) < 2:
                checks.append(ValidationCheck(
                    check_id=f"F-{lvl_num:02d}-001",
                    check_type=ValidationType.FEASIBILITY,
                    title=f"L{lvl_num} ({lvl.name}) 处理能力定义",
                    status=ValidationStatus.WARNING,
                    details=f"L只有 {len(lvl.capabilities)} 项能力，建议至少2项",
                    recommendation="补充L的处理能力范围定义",
                    severity="medium",
                ))
            else:
                checks.append(ValidationCheck(
                    check_id=f"F-{lvl_num:02d}-001",
                    check_type=ValidationType.FEASIBILITY,
                    title=f"L{lvl_num} ({lvl.name}) 处理能力定义",
                    status=ValidationStatus.PASS,
                    details=f"L定义 {len(lvl.capabilities)} 项能力",
                ))

            # 检查层级限制是否明确
            if not lvl.limits:
                checks.append(ValidationCheck(
                    check_id=f"F-{lvl_num:02d}-002",
                    check_type=ValidationType.FEASIBILITY,
                    title=f"L{lvl_num} ({lvl.name}) 能力边界定义",
                    status=ValidationStatus.WARNING,
                    details="L没有定义能力边界",
                    recommendation="明确L的能力边界，哪些情况必须升级",
                    severity="medium",
                ))
            else:
                checks.append(ValidationCheck(
                    check_id=f"F-{lvl_num:02d}-002",
                    check_type=ValidationType.FEASIBILITY,
                    title=f"L{lvl_num} ({lvl.name}) 能力边界定义",
                    status=ValidationStatus.PASS,
                    details=f"L定义 {len(lvl.limits)} 条边界限制",
                ))

        return checks

    def _validate_org_standards(self) -> list[ValidationCheck]:
        """组织镜像4标准验证"""
        checks: list[ValidationCheck] = []

        # 标准1: 明确分工
        division = self.org_standards.get("division_of_labor", {})
        has_responsible = bool(division.get("responsible"))
        has_accountable = bool(division.get("accountable"))
        has_consulted = bool(division.get("consulted"))
        has_informed = bool(division.get("informed"))

        if all([has_responsible, has_accountable, has_consulted, has_informed]):
            status = ValidationStatus.PASS
            detail = "RACI四角色完整定义"
        elif sum([has_responsible, has_accountable, has_consulted, has_informed]) >= 2:
            status = ValidationStatus.WARNING
            missing = []
            if not has_responsible: missing.append("responsible")
            if not has_accountable: missing.append("accountable")
            if not has_consulted: missing.append("consulted")
            if not has_informed: missing.append("informed")
            detail = f"RACI定义不完整，缺少: {', '.join(missing)}"
        else:
            status = ValidationStatus.FAIL
            detail = "分工定义严重缺失"

        checks.append(ValidationCheck(
            check_id="OS-001",
            check_type=ValidationType.ORG_STANDARDS,
            title="标准1: 明确分工 (RACI)",
            status=status,
            details=detail,
            recommendation="定义responsible/accountable/consulted/informed四角色",
            severity="critical" if status == ValidationStatus.FAIL else "medium",
        ))

        # 标准2: 明确升级路径
        has_paths = len(self.escalation_paths) > 0
        has_levels = len(self.levels) > 0
        has_triggers = all(ep.trigger_condition for ep in self.escalation_paths)

        if has_paths and has_levels and has_triggers:
            status2 = ValidationStatus.PASS
            detail2 = "升级路径完整 (层级+路径+触发)"
        elif has_paths and has_levels:
            status2 = ValidationStatus.WARNING
            detail2 = "缺少部分触发条件定义"
        else:
            status2 = ValidationStatus.FAIL
            detail2 = "升级路径定义不完整"

        checks.append(ValidationCheck(
            check_id="OS-002",
            check_type=ValidationType.ORG_STANDARDS,
            title="标准2: 明确升级路径",
            status=status2,
            details=detail2,
            recommendation="确保每个失败模式有对应的升级路径和触发条件",
            severity="critical" if status2 == ValidationStatus.FAIL else "medium",
        ))

        # 标准3: 明确复核点
        review_checkpoints = self.config.get("review_checkpoints", [])
        if len(review_checkpoints) >= 2:
            status3 = ValidationStatus.PASS
            detail3 = f"定义了 {len(review_checkpoints)} 个复核点"
        elif len(review_checkpoints) == 1:
            status3 = ValidationStatus.WARNING
            detail3 = "只有1个复核点，建议至少2个 (执行前+执行后)"
        else:
            status3 = ValidationStatus.WARNING
            detail3 = "未定义复核点"

        checks.append(ValidationCheck(
            check_id="OS-003",
            check_type=ValidationType.ORG_STANDARDS,
            title="标准3: 明确复核点",
            status=status3,
            details=detail3,
            recommendation="定义关键复核点: 执行前复核、关键里程碑复核、执行后复核",
            severity="low",
        ))

        # 标准4: 明确兜底点
        fallback_scenarios = self.fallback_config.get("scenarios", [])
        critical_fallbacks = [s for s in fallback_scenarios if s.get("type") in [
            "max_level_reached", "all_attempts_failed", "unrecoverable_state"
        ]]

        if len(critical_fallbacks) >= 3:
            status4 = ValidationStatus.PASS
            detail4 = f"定义了 {len(critical_fallbacks)} 个关键兜底场景"
        elif len(fallback_scenarios) >= 3:
            status4 = ValidationStatus.WARNING
            detail4 = f"定义了 {len(fallback_scenarios)} 个兜底场景，建议覆盖关键场景"
        else:
            status4 = ValidationStatus.FAIL
            detail4 = f"只定义了 {len(fallback_scenarios)} 个兜底场景，必须覆盖关键兜底场景"

        checks.append(ValidationCheck(
            check_id="OS-004",
            check_type=ValidationType.ORG_STANDARDS,
            title="标准4: 明确兜底点",
            status=status4,
            details=detail4,
            recommendation="覆盖3个关键兜底: max_level_reached/all_attempts_failed/unrecoverable_state",
            severity="critical" if status4 == ValidationStatus.FAIL else "medium",
        ))

        return checks

    def _validate_fallback(self) -> list[ValidationCheck]:
        """兜底协议验证"""
        checks: list[ValidationCheck] = []

        scenarios = self.fallback_config.get("scenarios", [])
        if not scenarios:
            checks.append(ValidationCheck(
                check_id="FB-001",
                check_type=ValidationType.COMPLETENESS,
                title="兜底协议定义",
                status=ValidationStatus.FAIL,
                details="未定义任何兜底场景",
                recommendation="至少定义3个关键兜底场景",
                severity="critical",
            ))
            return checks

        missing_handlers = []
        missing_recovery = []

        for sc in scenarios:
            if not sc.get("handler"):
                missing_handlers.append(sc.get("type", "unknown"))
            if not sc.get("recovery"):
                missing_recovery.append(sc.get("type", "unknown"))

        if missing_handlers:
            checks.append(ValidationCheck(
                check_id="FB-002",
                check_type=ValidationType.COMPLETENESS,
                title="兜底处理人定义",
                status=ValidationStatus.FAIL,
                details=f"以下兜底场景缺少handler: {missing_handlers}",
                recommendation="每个兜底场景必须指定处理人",
                affected_items=missing_handlers,
                severity="critical",
            ))
        else:
            checks.append(ValidationCheck(
                check_id="FB-002",
                check_type=ValidationType.COMPLETENESS,
                title="兜底处理人定义",
                status=ValidationStatus.PASS,
                details=f"所有 {len(scenarios)} 个兜底场景都定义了处理人",
            ))

        if missing_recovery:
            checks.append(ValidationCheck(
                check_id="FB-003",
                check_type=ValidationType.COMPLETENESS,
                title="兜底恢复流程定义",
                status=ValidationStatus.WARNING,
                details=f"以下场景缺少恢复流程: {missing_recovery}",
                recommendation="为每个兜底场景定义恢复流程",
                affected_items=missing_recovery,
                severity="medium",
            ))
        else:
            checks.append(ValidationCheck(
                check_id="FB-003",
                check_type=ValidationType.COMPLETENESS,
                title="兜底恢复流程定义",
                status=ValidationStatus.PASS,
                details="所有兜底场景都有恢复流程",
            ))

        return checks

    # ─────────────────────────────────────────
    # 辅助方法
    # ─────────────────────────────────────────

    def _detect_circular_escalation(self) -> list[int] | None:
        """检测循环升级，返回循环路径或None"""
        if not self.levels:
            return None

        # 构建层级依赖图
        graph: dict[int, set[int]] = {lvl: set() for lvl in self.levels}
        for ep in self.escalation_paths:
            if ep.from_level in graph:
                graph[ep.from_level].add(ep.to_level)

        # DFS检测环
        visited: set[int] = set()
        rec_stack: set[int] = set()
        path: list[int] = []

        def dfs(node: int) -> list[int] | None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            for neighbor in sorted(graph[node]):
                if neighbor not in visited:
                    result = dfs(neighbor)
                    if result:
                        return result
                elif neighbor in rec_stack:
                    # 找到环
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
            path.pop()
            rec_stack.remove(node)
            return None

        for start in sorted(graph.keys()):
            if start not in visited:
                cycle = dfs(start)
                if cycle:
                    return cycle

        return None

    def _detect_trigger_conflicts(self) -> list[str]:
        """检测触发条件冲突"""
        conflicts: list[str] = []
        # 按 from_level 分组
        by_level: dict[int, list[EscalationPath]] = {}
        for ep in self.escalation_paths:
            by_level.setdefault(ep.from_level, []).append(ep)

        for lvl, paths in by_level.items():
            # 同一level多个to_level的相同trigger_condition算冲突
            conditions: dict[str, list[int]] = {}
            for ep in paths:
                key = ep.trigger_condition.strip().lower()
                conditions.setdefault(key, []).append(ep.to_level)

            for cond, targets in conditions.items():
                if len(targets) > 1 and len(set(targets)) > 1:
                    conflicts.append(f"L{lvl}: '{cond}' → L{'/L'.join(map(str, sorted(set(targets))))}")

        return conflicts

    def _score_clear_division(self) -> int:
        """评分: 明确分工 (0-100)"""
        division = self.org_standards.get("division_of_labor", {})
        score = 0
        if division.get("responsible"): score += 25
        if division.get("accountable"): score += 25
        if division.get("consulted"): score += 25
        if division.get("informed"): score += 25
        return score

    def _score_clear_escalation(self) -> int:
        """评分: 明确升级路径 (0-100)"""
        if not self.levels or not self.escalation_paths:
            return 0
        score = 40  # 基础分: 有层级和路径
        if all(ep.trigger_condition for ep in self.escalation_paths):
            score += 30
        if not self._detect_circular_escalation():
            score += 30
        return min(100, score)

    def _score_clear_review(self) -> int:
        """评分: 明确复核点 (0-100)"""
        checkpoints = self.config.get("review_checkpoints", [])
        if len(checkpoints) >= 3:
            return 100
        elif len(checkpoints) >= 2:
            return 70
        elif len(checkpoints) >= 1:
            return 40
        return 10

    def _score_clear_fallback(self) -> int:
        """评分: 明确兜底点 (0-100)"""
        scenarios = self.fallback_config.get("scenarios", [])
        if not scenarios:
            return 0
        score = min(100, len(scenarios) * 20)
        critical = ["max_level_reached", "all_attempts_failed", "unrecoverable_state"]
        has_critical = any(s.get("type") in critical for s in scenarios)
        if has_critical:
            score = min(100, score + 20)
        return score

    def _generate_recommendations(self, checks: list[ValidationCheck]) -> list[str]:
        """从失败检查生成建议"""
        recs: list[str] = []
        failed = [c for c in checks if c.status == ValidationStatus.FAIL]
        critical = [c for c in failed if c.severity == "critical"]
        high = [c for c in failed if c.severity == "high"]

        if critical:
            recs.append(f"【必须修复】修复 {len(critical)} 个严重问题:")
            for c in critical:
                recs.append(f"  - [{c.check_id}] {c.title}: {c.recommendation}")

        if high:
            recs.append(f"【建议修复】修复 {len(high)} 个高风险问题:")
            for c in high:
                recs.append(f"  - [{c.check_id}] {c.title}: {c.recommendation}")

        if not failed:
            recs.append("✅ 升级路径配置通过所有严重检查，建议进行场景模拟验证")

        return recs

    def _summarize_risk(self, checks: list[ValidationCheck]) -> str:
        """风险总结"""
        failed = [c for c in checks if c.status == ValidationStatus.FAIL]
        warnings = [c for c in checks if c.status == ValidationStatus.WARNING]

        if not failed:
            if not warnings:
                return "🟢 低风险 — 配置完整且无警告"
            return f"🟡 中风险 — {len(warnings)} 个警告需要关注"
        elif len(failed) <= 2:
            return f"🟠 高风险 — {len(failed)} 个问题必须修复"
        else:
            return f"🔴 极高风险 — {len(failed)} 个严重问题，系统不可用"


# ─────────────────────────────────────────────
# 场景模拟器
# ─────────────────────────────────────────────

class EscalationSimulator:
    """升级路径场景模拟器"""

    def __init__(self, validator: EscalationValidator):
        self.validator = validator
        self.sim_log: list[dict[str, Any]] = []

    def simulate(self, failure_mode_id: str, steps: int = 10) -> dict[str, Any]:
        """
        模拟失败场景升级路径

        Args:
            failure_mode_id: 失败模式ID
            steps: 最大模拟步数
        """
        fm = self.validator.failure_modes.get(failure_mode_id)
        if not fm:
            return {"error": f"未知失败模式: {failure_mode_id}"}

        self.sim_log = []
        current_level = fm.escalation_level
        step = 0
        outcome = "unknown"

        self.sim_log.append({
            "step": step,
            "event": "failure_occurred",
            "level": current_level,
            "message": f"失败模式 '{fm.name}' 发生于 L{current_level}",
        })

        while step < steps:
            step += 1
            # 查找匹配的升级路径
            matching_paths = [
                ep for ep in self.validator.escalation_paths
                if ep.from_level == current_level
            ]

            if not matching_paths:
                outcome = "handled"
                self.sim_log.append({
                    "step": step,
                    "event": "handled",
                    "level": current_level,
                    "message": f"L{current_level} 成功处理，无升级路径",
                })
                break

            # 选择第一个可用路径
            ep = matching_paths[0]
            self.sim_log.append({
                "step": step,
                "event": "escalate",
                "level": current_level,
                "to_level": ep.to_level,
                "trigger": ep.trigger_type,
                "sla": ep.response_time_sla,
                "message": f"触发升级: {ep.trigger_condition} → L{ep.to_level} (SLA: {ep.response_time_sla})",
            })

            current_level = ep.to_level

            # 检查是否达到最高层级
            max_lvl = max(self.validator.levels.keys(), default=0)
            if current_level >= max_lvl:
                # 检查是否有兜底
                fallback_scenarios = self.validator.fallback_config.get("scenarios", [])
                fb = next((s for s in fallback_scenarios if s.get("type") == "max_level_reached"), None)
                if fb:
                    outcome = "fallback"
                    self.sim_log.append({
                        "step": step + 1,
                        "event": "fallback",
                        "handler": fb.get("handler"),
                        "action": fb.get("action", ""),
                        "message": f"兜底启动: {fb.get('handler')} 接管处理",
                    })
                else:
                    outcome = "escalated_to_human"
                    self.sim_log.append({
                        "step": step + 1,
                        "event": "human_escalation",
                        "level": current_level,
                        "message": "已达最高层级，需要人工介入",
                    })
                break

        # 检查循环
        circular = self.validator._detect_circular_escalation()
        if circular and outcome == "unknown":
            outcome = "circular"
            self.sim_log.append({
                "step": -1,
                "event": "circular_detected",
                "message": f"检测到循环升级: {' → L'.join(map(str, circular))}",
            })

        return {
            "failure_mode": fm.name,
            "outcome": outcome,
            "final_level": current_level,
            "total_steps": step,
            "simulation_log": self.sim_log,
        }


# ─────────────────────────────────────────────
# 输出格式化
# ─────────────────────────────────────────────

def format_report(report: ValidationReport) -> str:
    """格式化验证报告为可读文本"""
    lines: list[str] = []
    divider = "=" * 70

    # 头部
    lines.append(divider)
    status_icon = {"PASS": "✅", "FAIL": "❌", "WARNING": "⚠️", "SKIP": "➖"}
    icon = status_icon.get(report.overall_status.value, "?")
    lines.append(f"{icon} 升级路径验证报告 #{report.report_id}")
    lines.append(f"配置: {report.config_name}")
    lines.append(f"时间: {report.generated_at}")
    lines.append(divider)

    # 统计摘要
    lines.append(f"\n📊 验证统计:")
    lines.append(f"   总检查项: {report.total_checks}")
    lines.append(f"   ✅ 通过: {report.passed_checks}")
    lines.append(f"   ❌ 失败: {report.failed_checks}")
    lines.append(f"   ⚠️ 警告: {report.warning_checks}")

    # 组织镜像4标准评分
    lines.append(f"\n📋 组织镜像4标准评分:")
    for name, score in report.org_standards_score.items():
        bar = "█" * (score // 10) + "░" * (10 - score // 10)
        color = "🟢" if score >= 80 else "🟡" if score >= 50 else "🔴"
        lines.append(f"   {color} {name}: {bar} {score}/100")

    # 风险总结
    lines.append(f"\n{report.risk_summary}")

    # 详细检查结果
    lines.append(f"\n📝 详细检查结果:")
    for check in report.checks:
        icon = status_icon.get(check.status.value, "?")
        sev_marker = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(check.severity, "")
        lines.append(f"\n   {icon} [{check.check_id}] {sev_marker}{check.title}")
        lines.append(f"      类型: {check.check_type.value}")
        lines.append(f"      结果: {check.details}")
        if check.recommendation:
            lines.append(f"      建议: {check.recommendation}")

    # 建议
    if report.recommendations:
        lines.append(f"\n📌 改进建议:")
        for rec in report.recommendations:
            lines.append(f"   {rec}")

    lines.append("\n" + divider)
    return "\n".join(lines)


# ─────────────────────────────────────────────
# CLI入口
# ─────────────────────────────────────────────

def interactive_mode():
    """交互式验证"""
    print("╔══════════════════════════════════════════════════════╗")
    print("║       升级路径验证器 — 交互式模式                     ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    import yaml
    config_path = input("配置文件路径 (escalation.yaml): ").strip() or "escalation.yaml"

    if not Path(config_path).exists():
        print(f"❌ 文件不存在: {config_path}")
        print("使用 --demo 参数运行演示模式")
        return

    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    validator = EscalationValidator(config)
    report = validator.validate_all()

    print(format_report(report))

    # 场景模拟
    if validator.failure_modes:
        print("\n可用失败模式:")
        for fm_id in list(validator.failure_modes.keys())[:5]:
            print(f"  - {fm_id}")

        simulate_id = input("\n输入失败模式ID进行模拟 (直接回车跳过): ").strip()
        if simulate_id:
            simulator = EscalationSimulator(validator)
            result = simulator.simulate(simulate_id)
            print("\n🔄 模拟结果:")
            print(f"   结局: {result.get('outcome', 'unknown')}")
            print(f"   最终层级: L{result.get('final_level', '?')}")
            print(f"   总步数: {result.get('total_steps', 0)}")
            for entry in result.get("simulation_log", []):
                print(f"   Step {entry['step']}: {entry['message']}")


def demo_mode():
    """演示模式 — 使用内置示例配置"""
    print("🧪 演示模式: 使用内置示例配置\n")

    demo_config: dict[str, Any] = {
        "name": "天龙引擎Agent升级矩阵",
        "escalation_levels": {
            "level_1": {
                "name": "执行层",
                "description": "元级别自主处理",
                "capability": ["执行标准任务", "处理已知错误", "调用预设修复"],
                "limits": ["超出预设的错误", "需要判断的情况"],
                "escalation_threshold": ["重试次数 > 3", "时间 > SLA"],
                "response_time_sla": "1min",
            },
            "level_2": {
                "name": "编排层",
                "description": "协调元和资源调度",
                "capability": ["协调多元协作", "调整执行顺序", "重新分配资源"],
                "limits": ["架构性变更", "策略性决策"],
                "escalation_threshold": ["协调无效", "资源耗尽"],
                "response_time_sla": "5min",
            },
            "level_3": {
                "name": "治理层",
                "description": "系统级问题处理",
                "capability": ["修改元配置", "调整流程", "触发容灾"],
                "limits": ["业务决策", "资源采购"],
                "escalation_threshold": ["治理无效", "需要业务决策"],
                "response_time_sla": "30min",
            },
        },
        "failure_modes": [
            {"id": "FM-001", "name": "执行失败", "description": "任务执行失败", "severity": "high", "escalation_level": 1},
            {"id": "FM-002", "name": "协调失败", "description": "多Agent协调失败", "severity": "critical", "escalation_level": 2},
            {"id": "FM-003", "name": "系统故障", "description": "核心系统不可用", "severity": "critical", "escalation_level": 3},
        ],
        "escalation_paths": [
            {"from_level": 1, "to_level": 2, "trigger_condition": "重试3次无效", "trigger_type": "retry_exceeded", "response_time_sla": "5min"},
            {"from_level": 1, "to_level": 2, "trigger_condition": "执行超时", "trigger_type": "time_exceeded", "response_time_sla": "5min"},
            {"from_level": 2, "to_level": 3, "trigger_condition": "协调无效", "trigger_type": "coordination_failed", "response_time_sla": "30min"},
        ],
        "fallback": {
            "scenarios": [
                {"type": "max_level_reached", "description": "达到最高层级仍无法解决", "handler": "人工运维团队", "action": "人工接管处理", "recovery": "记录问题 → 分析根因 → 预防措施"},
                {"type": "all_attempts_failed", "description": "所有自动修复尝试失败", "handler": "值班SRE", "action": "触发降级", "recovery": "降级 → 人工介入 → 复盘"},
            ]
        },
        "org_standards": {
            "division_of_labor": {
                "responsible": [{"role": "执行元", "accountable_for": "任务产出"}],
                "accountable": [{"role": "编排元", "accountable_for": "协调决策"}],
                "consulted": [{"role": "审查元", "accountable_for": "质量把关"}],
                "informed": [{"role": "记录元", "accountable_for": "状态同步"}],
            }
        },
        "review_checkpoints": [
            {"checkpoint": "执行前复核", "when": "执行前", "what": "任务可行性", "who": "编排元"},
            {"checkpoint": "执行后复核", "when": "执行后", "what": "结果质量", "who": "审查元"},
        ],
    }

    validator = EscalationValidator(demo_config)
    report = validator.validate_all()
    print(format_report(report))

    # 模拟
    print("\n" + "=" * 70)
    print("🔄 场景模拟演示: FM-001 (执行失败)")
    print("=" * 70)
    simulator = EscalationSimulator(validator)
    result = simulator.simulate("FM-001")
    print(f"\n结局: {result.get('outcome', 'unknown')}")
    print(f"最终层级: L{result.get('final_level', '?')}")
    print(f"总步数: {result.get('total_steps', 0)}")
    for entry in result.get("simulation_log", []):
        print(f"  Step {entry['step']}: {entry['message']}")


def main():
    parser = argparse.ArgumentParser(
        description="escalation-validator.py — 升级路径验证器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python escalation-validator.py --demo                    # 演示模式
    python escalation-validator.py --config escalation.yaml    # 验证配置文件
    python escalation-validator.py --interactive            # 交互式验证
    python escalation-validator.py --simulate FM-001 --config escalation.yaml  # 场景模拟
    python escalation-validator.py --audit escalation.yaml   # 生成审计报告
        """,
    )
    parser.add_argument("--config", "-c", help="升级矩阵配置文件 (YAML)")
    parser.add_argument("--demo", "-d", action="store_true", help="演示模式")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互式模式")
    parser.add_argument("--simulate", "-s", metavar="FM-ID", help="模拟指定失败模式")
    parser.add_argument("--audit", "-a", metavar="FILE", help="生成审计报告")
    parser.add_argument("--format", "-f", choices=["text", "json", "yaml"],
                        default="text", help="输出格式")
    args = parser.parse_args()

    if args.demo:
        demo_mode()
        return

    if args.interactive:
        interactive_mode()
        return

    if args.simulate:
        if not args.config:
            print("❌ --simulate 需要 --config 参数指定配置文件")
            sys.exit(1)
        import yaml
        with open(args.config, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        validator = EscalationValidator(config)
        simulator = EscalationSimulator(validator)
        result = simulator.simulate(args.simulate)
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.config:
        import yaml
        with open(args.config, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        validator = EscalationValidator(config)
        report = validator.validate_all()

        if args.format == "json":
            import json
            output = {
                "report_id": report.report_id,
                "overall_status": report.overall_status.value,
                "total_checks": report.total_checks,
                "passed_checks": report.passed_checks,
                "failed_checks": report.failed_checks,
                "warning_checks": report.warning_checks,
                "org_standards_score": report.org_standards_score,
                "risk_summary": report.risk_summary,
                "checks": [
                    {
                        "check_id": c.check_id,
                        "type": c.check_type.value,
                        "title": c.title,
                        "status": c.status.value,
                        "details": c.details,
                        "recommendation": c.recommendation,
                    }
                    for c in report.checks
                ],
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            print(format_report(report))

        if report.overall_status == ValidationStatus.FAIL:
            sys.exit(1)
        return

    if args.audit:
        import yaml
        with open(args.audit, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        validator = EscalationValidator(config)
        report = validator.validate_all()

        audit_lines = ["# 升级路径审计报告", "---", f"生成时间: {report.generated_at}", ""]
        audit_lines.append("## 审计摘要")
        audit_lines.append(f"- 配置: {report.config_name}")
        audit_lines.append(f"- 状态: {report.overall_status.value}")
        audit_lines.append(f"- 通过率: {report.passed_checks}/{report.total_checks}")
        audit_lines.append("")
        audit_lines.append("## 组织镜像4标准评分")
        for name, score in report.org_standards_score.items():
            audit_lines.append(f"- {name}: {score}/100")
        audit_lines.append("")
        audit_lines.append("## 失败项")
        for c in report.checks:
            if c.status == ValidationStatus.FAIL:
                audit_lines.append(f"### [{c.check_id}] {c.title}")
                audit_lines.append(f"- 问题: {c.details}")
                audit_lines.append(f"- 建议: {c.recommendation}")
                audit_lines.append("")

        Path(f"audit-{datetime.now().strftime('%Y%m%d')}.md").write_text(
            "\n".join(audit_lines), encoding="utf-8"
        )
        print(f"✅ 审计报告已保存: audit-{datetime.now().strftime('%Y%m%d')}.md")
        return

    # 默认: 显示帮助
    parser.print_help()
    print("\n💡 提示: 使用 --demo 查看演示验证")


if __name__ == "__main__":
    main()
