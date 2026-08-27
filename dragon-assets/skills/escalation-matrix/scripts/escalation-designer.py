#!/usr/bin/env python3
"""
升级路径设计器 (Escalation Path Designer)
基于 escalation-matrix 组织镜像4标准

功能: 根据用户场景自动生成定制化的升级矩阵配置
输入: 场景类型、团队规模、SLA要求等
输出: YAML格式的完整升级矩阵配置

使用方法:
    python escalation-designer.py --scene 产品开发 --team 5-10 --sla 30min
    python escalation-designer.py --interactive
"""

import argparse
import sys
import os
import yaml
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime


# ============================================================================
# 数据模型
# ============================================================================

@dataclass
class SceneConfig:
    """场景配置"""
    scene_type: str = ""           # 产品开发/数据分析/运维监控/客服
    team_size: str = ""            # 单Agent/2-5/5-10/10+
    org_structure: str = ""         # 扁平/2层/3层/4层
    collaboration_mode: str = ""    # 串行/并行/混合
    sla_requirement: str = ""      # SLA要求
    security_level: str = ""        # 普通/机密/高危
    special_constraints: list = field(default_factory=list)

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v}


@dataclass
class LevelConfig:
    """层级配置"""
    level: int
    name: str
    triggers: list
    response_time: str
    fallback_actions: list
    retry_count: int = 3
    timeout_multiplier: float = 1.5


@dataclass
class EscalationPath:
    """升级路径"""
    from_level: int
    to_level: int
    trigger_types: list
    conditions: list


@dataclass
class NotificationRule:
    """通知规则"""
    level: int
    on_escalation: list
    template: str
    channels: list = field(default_factory=list)
    sla: str = ""


# ============================================================================
# 场景配置生成器
# ============================================================================

class SceneConfigGenerator:
    """根据场景类型生成推荐配置"""

    SCENE_CONFIGS = {
        "产品开发": {
            "thresholds": {
                "l1_l2": {"retry_count": 3, "timeout_multiplier": 1.5},
                "l2_l3": {"coordination_attempts": 3, "resource_threshold": 0.8},
                "l3_l4": {"governance_attempts": 3, "core_function_impact": True},
            },
            "error_blacklist": ["SyntaxError", "ImportError", "TypeError"],
            "urgent_triggers": ["security_incident", "core_function_impact"],
            "sla_defaults": {"l1": "30秒", "l2": "5分钟", "l3": "30分钟", "l4": "按情况"}
        },
        "数据分析": {
            "thresholds": {
                "l1_l2": {"retry_count": 2, "timeout_multiplier": 1.5},
                "l2_l3": {"coordination_attempts": 2, "resource_threshold": 0.85},
                "l3_l4": {"governance_attempts": 2},
            },
            "error_blacklist": ["QueryTimeout", "DataCorruption", "SchemaMismatch"],
            "urgent_triggers": ["data_loss_risk", "core_function_impact"],
            "sla_defaults": {"l1": "10秒", "l2": "3分钟", "l3": "15分钟", "l4": "按情况"}
        },
        "运维监控": {
            "thresholds": {
                "l1_l2": {"retry_count": 2, "timeout_multiplier": 1.2},
                "l2_l3": {"coordination_attempts": 2, "resource_threshold": 0.9, "dependency_timeout": 60},
                "l3_l4": {"governance_attempts": 2, "core_function_impact": True, "security_incident": True},
            },
            "error_blacklist": ["ConnectionError", "TimeoutError", "503 Service Unavailable"],
            "urgent_triggers": ["security_incident", "data_loss_risk", "core_function_failure"],
            "sla_defaults": {"l1": "10秒", "l2": "2分钟", "l3": "10分钟", "l4": "即时"}
        },
        "客服": {
            "thresholds": {
                "l1_l2": {"retry_count": 2, "timeout_multiplier": 1.5},
                "l2_l3": {"coordination_attempts": 2, "resource_threshold": 0.8},
                "l3_l4": {"governance_attempts": 2},
            },
            "error_blacklist": ["IntentRecognitionFailed", "EmotionAnomaly", "ContextLost"],
            "urgent_triggers": ["security_incident", "emotion_crisis"],
            "sla_defaults": {"l1": "15秒", "l2": "2分钟", "l3": "5分钟", "l4": "即时"}
        }
    }

    @classmethod
    def generate(cls, scene_type: str, team_size: str = "2-5", custom_sla: str = "") -> dict:
        """生成场景配置"""
        config = cls.SCENE_CONFIGS.get(scene_type, cls.SCENE_CONFIGS["产品开发"])
        return {
            "scene_type": scene_type,
            "team_size": team_size,
            "thresholds": config["thresholds"],
            "error_blacklist": config["error_blacklist"],
            "urgent_triggers": config["urgent_triggers"],
            "sla_defaults": config.get("sla_defaults", cls.SCENE_CONFIGS["产品开发"]["sla_defaults"])
        }


# ============================================================================
# 升级路径生成器
# ============================================================================

class EscalationPathGenerator:
    """生成升级路径配置"""

    @staticmethod
    def generate_normal_path(config: dict) -> list:
        """生成正常升级路径"""
        thresholds = config.get("thresholds", {})
        scene = config.get("scene_type", "产品开发")

        paths = []

        # L1 → L2
        l1_l2 = thresholds.get("l1_l2", {})
        paths.append({
            "from": "L1",
            "to": "L2",
            "name": "执行层到编排层",
            "triggers": [
                {"type": "retry_exceeded", "threshold": l1_l2.get("retry_count", 3)},
                {"type": "time_exceeded", "multiplier": l1_l2.get("timeout_multiplier", 1.5)},
                {"type": "error_blacklist", "errors": config.get("error_blacklist", [])},
                {"type": "unknown_error"}
            ],
            "timeout": "5分钟",
            "sla": "30秒"
        })

        # L2 → L3
        l2_l3 = thresholds.get("l2_l3", {})
        paths.append({
            "from": "L2",
            "to": "L3",
            "name": "编排层到治理层",
            "triggers": [
                {"type": "coordination_failed", "threshold": l2_l3.get("coordination_attempts", 3)},
                {"type": "dependency_unavailable", "timeout": l2_l3.get("dependency_timeout", 180)},
                {"type": "resource_bottleneck", "threshold": l2_l3.get("resource_threshold", 0.8)},
                {"type": "cross_system_impact"}
            ],
            "timeout": "10分钟",
            "sla": "5分钟"
        })

        # L3 → L4
        l3_l4 = thresholds.get("l3_l4", {})
        paths.append({
            "from": "L3",
            "to": "L4",
            "name": "治理层到决策层",
            "triggers": [
                {"type": "governance_ineffective", "threshold": l3_l4.get("governance_attempts", 3)},
                {"type": "core_function_impact", "enabled": l3_l4.get("core_function_impact", True)},
                {"type": "security_incident", "enabled": l3_l4.get("security_incident", True)},
                {"type": "business_decision_required"}
            ],
            "timeout": "30分钟",
            "sla": "按情况"
        })

        # L4 → 人工
        paths.append({
            "from": "L4",
            "to": "人工",
            "name": "决策层到人工介入",
            "triggers": [
                {"type": "max_level_reached"},
                {"type": "circular_escalation"},
                {"type": "unrecoverable_state"},
                {"type": "l4_handling_failed"}
            ],
            "timeout": "根据紧急程度",
            "sla": "30分钟"
        })

        return paths

    @staticmethod
    def generate_urgent_paths(config: dict) -> list:
        """生成紧急升级路径（跳过中间层）"""
        urgent_triggers = config.get("urgent_triggers", [])

        urgent_paths = []

        # 安全事件: L1 → L4
        if "security_incident" in urgent_triggers:
            urgent_paths.append({
                "trigger": "security_incident",
                "path": "L1 → L4",
                "bypass": ["L2", "L3"],
                "reason": "安全事件需要最高决策层快速响应",
                "notification": "并行通知安全团队+管理层",
                "sla": "5分钟内响应"
            })

        # 核心功能影响: L2 → L4
        if "core_function_impact" in urgent_triggers or "core_function_failure" in urgent_triggers:
            urgent_paths.append({
                "trigger": "core_function_impact",
                "path": "L2 → L4",
                "bypass": ["L3"],
                "reason": "核心功能影响业务连续性",
                "notification": "并行通知技术负责人+产品负责人",
                "sla": "15分钟内响应"
            })

        # 数据丢失风险: L1 → L4
        if "data_loss_risk" in urgent_triggers:
            urgent_paths.append({
                "trigger": "data_loss_risk",
                "path": "L1 → L4",
                "bypass": ["L2", "L3"],
                "reason": "数据丢失风险不可逆",
                "notification": "并行通知所有相关方",
                "sla": "即时"
            })

        # 业务决策: L3 → L4
        urgent_paths.append({
            "trigger": "business_decision_required",
            "path": "L3 → L4",
            "bypass": [],
            "reason": "业务决策必须由决策层做出",
            "notification": "通知决策层+业务负责人",
            "sla": "根据紧急程度"
        })

        return urgent_paths


# ============================================================================
# 角色配置生成器
# ============================================================================

class RoleConfigGenerator:
    """生成角色配置"""

    @staticmethod
    def generate_role_config(team_size: str) -> dict:
        """根据团队规模生成角色配置"""
        configs = {
            "单Agent": {
                "max_level": 2,
                "roles": ["executor", "orchestrator"],
                "simplified": True,
                "notes": "单Agent简化为L1执行+L2编排，侧重自我治理"
            },
            "2-5": {
                "max_level": 3,
                "roles": ["executor", "orchestrator", "governor"],
                "simplified": True,
                "notes": "简化L1执行+L2编排+L3治理，可选L4决策"
            },
            "5-10": {
                "max_level": 4,
                "roles": ["executor", "orchestrator", "governor", "decision_maker"],
                "simplified": False,
                "notes": "完整L1-L2-L3层级，专职人工操作员"
            },
            "10+": {
                "max_level": 4,
                "roles": ["executor", "orchestrator", "governor", "decision_maker", "human_operator"],
                "simplified": False,
                "notes": "完整4层架构，多个执行者并行，治理委员会"
            }
        }
        return configs.get(team_size, configs["2-5"])


# ============================================================================
# 协作协议生成器
# ============================================================================

class CollaborationProtocolGenerator:
    """生成协作协议配置"""

    @staticmethod
    def generate_protocols() -> dict:
        """生成层级间协作协议"""
        return {
            "l1_l2_protocol": {
                "name": "执行层-编排层协作",
                "communication": {
                    "upgrade_request": {
                        "format": "escalation_event",
                        "fields": ["event_id", "source_level", "target_level", "trigger_type", "context", "retry_count", "timestamp", "suggested_action"]
                    },
                    "upgrade_ack": {
                        "format": "escalation_ack",
                        "fields": ["event_id", "accepted", "assigned_handler", "expected_response_time", "alternative_actions"]
                    },
                    "resolution_report": {
                        "format": "resolution_report",
                        "fields": ["event_id", "resolution", "duration", "lessons_learned"]
                    }
                },
                "timing": {
                    "upgrade_request_timeout": "5分钟",
                    "upgrade_ack_timeout": "30秒",
                    "resolution_report_delay": "完成后1分钟"
                }
            },
            "l2_l3_protocol": {
                "name": "编排层-治理层协作",
                "communication": {
                    "escalation_with_context": {
                        "format": "governance_escalation",
                        "fields": ["event_id", "root_cause_analysis", "coordination_attempts", "affected_systems", "risk_assessment", "recommended_actions"]
                    },
                    "governance_response": {
                        "format": "governance_decision",
                        "fields": ["event_id", "decision", "affected_config_changes", "risk_mitigation", "rollback_plan"]
                    }
                },
                "timing": {
                    "escalation_timeout": "10分钟",
                    "root_cause_analysis_deadline": "5分钟",
                    "governance_response_deadline": "5分钟"
                }
            },
            "l3_l4_protocol": {
                "name": "治理层-决策层协作",
                "communication": {
                    "critical_escalation": {
                        "format": "critical_escalation",
                        "fields": ["event_id", "business_impact", "governance_ineffective_reason", "multiple_system_failure", "security_incident_flag", "recommended_decision"]
                    },
                    "decision_directive": {
                        "format": "decision_directive",
                        "fields": ["event_id", "decision", "authority_granted", "external_coordination_required", "timeline"]
                    }
                },
                "timing": {
                    "escalation_timeout": "即时",
                    "decision_deadline": "根据紧急程度",
                    "notification_requirement": "所有相关方"
                }
            },
            "l4_human_protocol": {
                "name": "决策层-人工协作",
                "communication": {
                    "human_intervention_request": {
                        "format": "human_intervention_request",
                        "fields": ["event_id", "situation_summary", "available_context", "recommended_actions", "authority_needed"]
                    },
                    "human_response": {
                        "format": "human_response",
                        "fields": ["event_id", "action_taken", "outcome", "follow_up_required"]
                    }
                },
                "timing": {
                    "response_timeout": "30分钟",
                    "urgent_timeout": "5分钟",
                    "escalation_if_no_response": "超时后升级到备用人"
                }
            }
        }


# ============================================================================
# 通知规则生成器
# ============================================================================

class NotificationRuleGenerator:
    """生成通知规则"""

    @staticmethod
    def generate_rules() -> list:
        """生成层级通知规则"""
        return [
            {
                "level": "L1",
                "on_escalation": ["L2", "L1_parent"],
                "template": "L1执行失败，需要L2协调介入",
                "channels": ["内部消息"],
                "sla": "30秒内"
            },
            {
                "level": "L2",
                "on_escalation": ["L3", "L2_parent"],
                "template": "L2协调无效，需要L3治理介入",
                "channels": ["内部消息", "邮件"],
                "sla": "5分钟内"
            },
            {
                "level": "L3",
                "on_escalation": ["L4", "stakeholders"],
                "template": "L3治理无效，需要L4决策介入",
                "channels": ["内部消息", "邮件", "短信"],
                "sla": "15分钟内"
            },
            {
                "level": "L4",
                "on_escalation": ["all_stakeholders"],
                "template": "问题已解决，危机响应结束",
                "channels": ["所有渠道"],
                "sla": "完成后通知"
            }
        ]

    @staticmethod
    def generate_urgent_notifications() -> list:
        """生成紧急通知规则"""
        return [
            {
                "condition": "security_incident",
                "channels": ["电话", "短信", "邮件"],
                "recipients": ["安全团队", "管理层"],
                "sla": "5分钟内响应"
            },
            {
                "condition": "core_function_impact",
                "channels": ["短信", "邮件"],
                "recipients": ["技术负责人", "产品负责人"],
                "sla": "15分钟内响应"
            },
            {
                "condition": "data_loss_risk",
                "channels": ["电话", "短信", "邮件"],
                "recipients": ["数据团队", "管理层"],
                "sla": "即时响应"
            }
        ]


# ============================================================================
# 升级矩阵生成器
# ============================================================================

class EscalationMatrixGenerator:
    """完整的升级矩阵生成器"""

    def __init__(self, scene_type: str, team_size: str = "2-5", custom_sla: str = ""):
        self.scene_type = scene_type
        self.team_size = team_size
        self.custom_sla = custom_sla
        self.config = SceneConfigGenerator.generate(scene_type, team_size, custom_sla)

    def generate(self) -> dict:
        """生成完整的升级矩阵"""
        role_config = RoleConfigGenerator.generate_role_config(self.team_size)
        max_level = role_config["max_level"]

        matrix = {
            "escalation_matrix": {
                "metadata": {
                    "name": f"{self.scene_type}升级矩阵",
                    "version": "1.0.0",
                    "created_date": datetime.now().strftime("%Y-%m-%d"),
                    "author": "天龙引擎",
                    "description": f"基于{self.scene_type}场景的自动生成升级矩阵"
                },
                "levels": {},
                "paths": {
                    "normal": EscalationPathGenerator.generate_normal_path(self.config),
                    "urgent": EscalationPathGenerator.generate_urgent_paths(self.config)
                },
                "notifications": {
                    "level_notifications": NotificationRuleGenerator.generate_rules(),
                    "urgent_notifications": NotificationRuleGenerator.generate_urgent_notifications()
                },
                "collaboration_protocols": CollaborationProtocolGenerator.generate_protocols(),
                "governance": self._generate_governance(),
                "metrics": self._generate_metrics()
            }
        }

        # 根据团队规模生成层级配置
        matrix["escalation_matrix"]["levels"] = self._generate_levels(max_level)
        matrix["escalation_matrix"]["roles"] = role_config

        return matrix

    def _generate_levels(self, max_level: int) -> dict:
        """生成层级配置"""
        sla_defaults = self.config.get("sla_defaults", SceneConfigGenerator.SCENE_CONFIGS["产品开发"]["sla_defaults"])
        thresholds = self.config.get("thresholds", {})

        levels = {}

        # L1 执行层
        l1_th = thresholds.get("l1_l2", {})
        levels["level_1"] = {
            "name": "执行层",
            "description": "按标准流程执行任务",
            "triggers": [
                {"id": "retry_exceeded", "name": "重试超限", "threshold": l1_th.get("retry_count", 3), "priority": "P3"},
                {"id": "time_exceeded", "name": "时间超限", "multiplier": l1_th.get("timeout_multiplier", 1.5), "priority": "P3"},
                {"id": "error_blacklist", "name": "黑名单错误", "errors": self.config.get("error_blacklist", []), "priority": "P2"},
                {"id": "unknown_error", "name": "未知错误", "priority": "P4"}
            ],
            "response_time": sla_defaults.get("l1", "30秒"),
            "fallback_actions": ["重试", "使用备用方案", "触发L1→L2升级"]
        }

        # L2 编排层
        l2_th = thresholds.get("l2_l3", {})
        levels["level_2"] = {
            "name": "编排层",
            "description": "协调多个执行者，调度资源和任务",
            "triggers": [
                {"id": "coordination_failed", "name": "协调失败", "threshold": l2_th.get("coordination_attempts", 3), "priority": "P2"},
                {"id": "dependency_unavailable", "name": "依赖不可用", "timeout": l2_th.get("dependency_timeout", 180), "priority": "P2"},
                {"id": "resource_bottleneck", "name": "资源瓶颈", "threshold": l2_th.get("resource_threshold", 0.8), "priority": "P2"},
                {"id": "cross_system_impact", "name": "跨系统影响", "priority": "P1"}
            ],
            "response_time": sla_defaults.get("l2", "5分钟"),
            "fallback_actions": ["重新分配资源", "调整执行顺序", "触发并行执行", "触发L2→L3升级"]
        }

        # L3 治理层
        if max_level >= 3:
            l3_th = thresholds.get("l3_l4", {})
            levels["level_3"] = {
                "name": "治理层",
                "description": "制定和调整治理策略，处理跨系统问题",
                "triggers": [
                    {"id": "governance_ineffective", "name": "治理无效", "threshold": l3_th.get("governance_attempts", 3), "priority": "P2"},
                    {"id": "core_function_impact", "name": "核心功能影响", "enabled": l3_th.get("core_function_impact", True), "priority": "P0"},
                    {"id": "security_incident", "name": "安全事件", "enabled": l3_th.get("security_incident", True), "priority": "P0"},
                    {"id": "business_decision_required", "name": "需要业务决策", "priority": "P2"}
                ],
                "response_time": sla_defaults.get("l3", "30分钟"),
                "fallback_actions": ["调整治理策略", "触发容灾机制", "触发L3→L4升级"]
            }

        # L4 决策层
        if max_level >= 4:
            levels["level_4"] = {
                "name": "决策层",
                "description": "做出最终业务决策，处理危机和紧急情况",
                "triggers": [
                    {"id": "max_level_reached", "name": "最高层级", "priority": "P0"},
                    {"id": "circular_escalation", "name": "循环升级", "priority": "P0"},
                    {"id": "unrecoverable_state", "name": "不可恢复状态", "priority": "P0"}
                ],
                "response_time": sla_defaults.get("l4", "按情况"),
                "fallback_actions": ["做出最终决策", "调配外部资源", "触发人工介入"]
            }

        return levels

    def _generate_governance(self) -> dict:
        """生成治理配置"""
        return {
            "escalation_necessity_review": {
                "required_for": [
                    "超过重试阈值的错误",
                    "影响核心功能的故障",
                    "跨系统问题",
                    "安全事件",
                    "需要业务决策的情况"
                ],
                "not_required_for": [
                    "可自动恢复的小错误",
                    "在SLA内完成的操作",
                    "不影响用户的内部问题"
                ]
            },
            "escalation_efficiency": {
                "escalation_rate_target": "< 10%",
                "escalation_latency_target": "< 5分钟",
                "resolution_time_target": "< 30分钟",
                "false_escalation_rate_target": "< 5%"
            }
        }

    def _generate_metrics(self) -> dict:
        """生成度量配置"""
        return {
            "efficiency_metrics": {
                "escalation_rate": {"target": "< 10%", "alert_threshold": "> 15%"},
                "escalation_resolution_time": {"target": "< 30分钟", "alert_threshold": "> 60分钟"},
                "escalation_latency": {"target": "< 1分钟", "alert_threshold": "> 5分钟"},
                "self_resolution_rate": {"target": "> 85%", "alert_threshold": "< 70%"}
            },
            "quality_metrics": {
                "escalation_accuracy": {"target": "> 95%", "alert_threshold": "< 90%"},
                "circular_escalation_rate": {"target": "< 1%", "alert_threshold": "> 3%"},
                "human_intervention_rate": {"target": "< 5%", "alert_threshold": "> 10%"}
            }
        }


# ============================================================================
# 主程序
# ============================================================================

def interactive_mode():
    """交互式配置"""
    print("\n=== 升级矩阵设计器 - 交互式配置 ===\n")

    # 场景类型
    print("请选择场景类型:")
    scenes = ["产品开发", "数据分析", "运维监控", "客服"]
    for i, s in enumerate(scenes, 1):
        print(f"  {i}. {s}")
    scene_idx = input("选择 (1-4) [默认=1]: ").strip() or "1"
    scene_type = scenes[int(scene_idx) - 1]

    # 团队规模
    print("\n请选择团队规模:")
    sizes = ["单Agent", "2-5", "5-10", "10+"]
    for i, s in enumerate(sizes, 1):
        print(f"  {i}. {s}")
    size_idx = input("选择 (1-4) [默认=2]: ").strip() or "2"
    team_size = sizes[int(size_idx) - 1]

    # SLA要求
    custom_sla = input("\n自定义SLA要求 (可选，直接回车跳过): ").strip()

    return scene_type, team_size, custom_sla


def main():
    parser = argparse.ArgumentParser(
        description="升级路径设计器 - 基于组织镜像4标准生成定制化升级矩阵",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python escalation-designer.py --scene 产品开发 --team 5-10
  python escalation-designer.py --scene 运维监控 --team 10+ --sla 10min
  python escalation-designer.py --interactive
        """
    )

    parser.add_argument("--scene", "-s", choices=["产品开发", "数据分析", "运维监控", "客服"],
                        help="场景类型")
    parser.add_argument("--team", "-t", choices=["单Agent", "2-5", "5-10", "10+"],
                        default="2-5", help="团队规模 (默认: 2-5)")
    parser.add_argument("--sla", help="自定义SLA要求")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互式配置")
    parser.add_argument("--output", "-o", help="输出文件路径 (默认: stdout)")
    parser.add_argument("--format", "-f", choices=["yaml", "json"], default="yaml", help="输出格式")

    args = parser.parse_args()

    # 交互式或命令行获取配置
    if args.interactive or not args.scene:
        scene_type, team_size, custom_sla = interactive_mode()
    else:
        scene_type = args.scene
        team_size = args.team
        custom_sla = args.sla or ""

    # 生成升级矩阵
    generator = EscalationMatrixGenerator(scene_type, team_size, custom_sla)
    matrix = generator.generate()

    # 输出
    output = yaml.dump(matrix, allow_unicode=True, sort_keys=False, default_flow_style=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"\n升级矩阵已保存到: {args.output}")
    else:
        print("\n" + "=" * 60)
        print(f"生成的升级矩阵: {scene_type} - {team_size}团队")
        print("=" * 60)
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
