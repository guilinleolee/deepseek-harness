#!/usr/bin/env python3
"""
节奏设计器 (Rhythm Designer)

基于任务复杂度和Agent能力，生成最佳节奏配置。
支持三种模式：设计、分析、优化

用法:
    python rhythm-designer.py design --task-complexity high --agent-count 5
    python rhythm-designer.py analyze --log tasks.log
    python rhythm-designer.py optimize --current-config config.yaml
"""

import json
import sys
import argparse
import yaml
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class ComplexityLevel(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    SUPER_COMPLEX = "super_complex"


class RhythmIntensity(Enum):
    LIGHTWEIGHT = "lightweight"
    STANDARD = "standard"
    HEAVY = "heavy"
    CUSTOM = "custom"


class CoordinationMode(Enum):
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    HYBRID = "hybrid"


@dataclass
class AgentAllocation:
    """Agent分配配置"""
    agent_id: str
    agent_name: str
    allocation_ratio: float  # 0.0-1.0
    max_parallel: int
    priority: str  # high/medium/low


@dataclass
class TimingConfig:
    """时序配置"""
    trigger_interval: int  # 秒
    poll_interval: int     # 秒
    timeout_threshold: int  # 分钟
    heartbeat_interval: int  # 秒


@dataclass
class RhythmBlueprint:
    """节奏蓝图"""
    blueprint_id: str
    name: str
    description: str

    # 任务分析
    complexity_score: float
    complexity_level: str
    compute_ratio: float
    communication_ratio: float

    # Agent分配
    agent_allocations: List[AgentAllocation]
    total_agents: int

    # 依赖结构
    is_parallel: bool
    critical_path: List[str]
    critical_path_duration: str

    # 节奏配置
    intensity: str
    timing: TimingConfig
    max_parallel_tasks: int
    coordination_mode: str

    # 预期效果
    expected_throughput: str
    expected_latency_p50: str
    expected_success_rate: str

    def to_dict(self) -> dict:
        return {
            'blueprint_id': self.blueprint_id,
            'name': self.name,
            'description': self.description,
            'complexity_score': self.complexity_score,
            'complexity_level': self.complexity_level,
            'compute_ratio': self.compute_ratio,
            'communication_ratio': self.communication_ratio,
            'agent_allocations': [
                {
                    'agent_id': a.agent_id,
                    'agent_name': a.agent_name,
                    'allocation_ratio': a.allocation_ratio,
                    'max_parallel': a.max_parallel,
                    'priority': a.priority
                }
                for a in self.agent_allocations
            ],
            'total_agents': self.total_agents,
            'is_parallel': self.is_parallel,
            'critical_path': self.critical_path,
            'critical_path_duration': self.critical_path_duration,
            'intensity': self.intensity,
            'timing': asdict(self.timing),
            'max_parallel_tasks': self.max_parallel_tasks,
            'coordination_mode': self.coordination_mode,
            'expected_throughput': self.expected_throughput,
            'expected_latency_p50': self.expected_latency_p50,
            'expected_success_rate': self.expected_success_rate
        }


class RhythmDesigner:
    """节奏设计器"""

    # Agent能力矩阵
    AGENT_CAPABILITIES = {
        '01': {'name': '调研师', 'compute': 0.8, 'comm': 0.5, 'parallel': 2},
        '02': {'name': '架构师', 'compute': 0.5, 'comm': 0.9, 'parallel': 3},
        '03': {'name': '构建师', 'compute': 0.95, 'comm': 0.3, 'parallel': 5},
        '04': {'name': '验证师', 'compute': 0.8, 'comm': 0.5, 'parallel': 3},
        '05': {'name': '安全师', 'compute': 0.8, 'comm': 0.5, 'parallel': 2},
        '06': {'name': '审查师', 'compute': 0.6, 'comm': 0.8, 'parallel': 3},
    }

    # 节奏强度预设
    RHYTHM_PRESETS = {
        'lightweight': {
            'trigger_interval': 1,
            'poll_interval': 5,
            'timeout_threshold': 1,  # 分钟
            'heartbeat_interval': 10,
            'max_parallel': 3
        },
        'standard': {
            'trigger_interval': 5,
            'poll_interval': 30,
            'timeout_threshold': 5,
            'heartbeat_interval': 30,
            'max_parallel': 5
        },
        'heavy': {
            'trigger_interval': 30,
            'poll_interval': 120,
            'timeout_threshold': 30,
            'heartbeat_interval': 60,
            'max_parallel': 10
        }
    }

    def __init__(self):
        self.blueprint_id = f"RB-{datetime.now().strftime('%Y%m%d')}-{id(self) % 1000:03d}"

    def calculate_complexity(
        self,
        compute_ratio: float,
        communication_ratio: float,
        waiting_tolerance: float,
        deadline_critical: bool
    ) -> tuple[float, ComplexityLevel]:
        """计算任务复杂度"""
        # 加权计算
        complexity = (
            compute_ratio * 0.3 +
            communication_ratio * 0.3 +
            (1 - waiting_tolerance) * 0.2 +
            (0.2 if deadline_critical else 0)
        )

        # 分级
        if complexity < 0.3:
            level = ComplexityLevel.SIMPLE
        elif complexity < 0.5:
            level = ComplexityLevel.MEDIUM
        elif complexity < 0.7:
            level = ComplexityLevel.COMPLEX
        else:
            level = ComplexityLevel.SUPER_COMPLEX

        return complexity, level

    def match_agents(
        self,
        complexity: ComplexityLevel,
        agent_count: int,
        compute_intensive: bool,
        comm_intensive: bool
    ) -> List[AgentAllocation]:
        """匹配Agent分配"""
        allocations = []

        if compute_intensive:
            # 计算密集型：优先构建师
            primary = '03'
            secondary = ['01', '04']
        elif comm_intensive:
            # 沟通密集型：优先架构师
            primary = '02'
            secondary = ['06', '01']
        else:
            # 平衡型：均匀分配
            primary = '01'
            secondary = ['02', '03', '04']

        # 主Agent分配
        primary_cap = self.AGENT_CAPABILITIES.get(primary, {})
        allocations.append(AgentAllocation(
            agent_id=primary,
            agent_name=primary_cap.get('name', primary),
            allocation_ratio=0.4,
            max_parallel=primary_cap.get('parallel', 3),
            priority='high'
        ))

        # 辅助Agent分配
        remaining = 0.6
        per_agent = remaining / len(secondary)
        for agent_id in secondary[:agent_count - 1]:
            cap = self.AGENT_CAPABILITIES.get(agent_id, {})
            allocations.append(AgentAllocation(
                agent_id=agent_id,
                agent_name=cap.get('name', agent_id),
                allocation_ratio=per_agent,
                max_parallel=cap.get('parallel', 2),
                priority='medium'
            ))

        return allocations

    def select_rhythm_intensity(
        self,
        complexity: ComplexityLevel,
        agent_count: int
    ) -> tuple[RhythmIntensity, Dict]:
        """选择节奏强度"""
        if complexity == ComplexityLevel.SIMPLE and agent_count <= 2:
            intensity = RhythmIntensity.LIGHTWEIGHT
        elif complexity == ComplexityLevel.SIMPLE:
            intensity = RhythmIntensity.LIGHTWEIGHT
        elif complexity == ComplexityLevel.MEDIUM and agent_count <= 5:
            intensity = RhythmIntensity.STANDARD
        elif complexity == ComplexityLevel.COMPLEX and agent_count <= 4:
            intensity = RhythmIntensity.STANDARD
        elif complexity == ComplexityLevel.COMPLEX:
            intensity = RhythmIntensity.HEAVY
        else:
            intensity = RhythmIntensity.CUSTOM

        preset = self.RHYTHM_PRESETS.get(intensity.value, self.RHYTHM_PRESETS['standard'])
        return intensity, preset

    def design_rhythm(
        self,
        name: str,
        description: str,
        compute_ratio: float,
        communication_ratio: float,
        waiting_tolerance: float,
        deadline_critical: bool,
        agent_count: int,
        is_parallel: bool,
        critical_path: List[str],
        critical_path_duration: str
    ) -> RhythmBlueprint:
        """设计节奏蓝图"""
        # 计算复杂度
        complexity, level = self.calculate_complexity(
            compute_ratio, communication_ratio, waiting_tolerance, deadline_critical
        )

        # 判断任务类型
        compute_intensive = compute_ratio > 0.5
        comm_intensive = communication_ratio > 0.5

        # 匹配Agent
        allocations = self.match_agents(
            complexity, agent_count, compute_intensive, comm_intensive
        )

        # 选择节奏强度
        intensity, preset = self.select_rhythm_intensity(complexity, agent_count)

        # 计算预期指标
        base_throughput = 10 * agent_count * (1 - complexity * 0.3)
        expected_throughput = f"{int(base_throughput)} tasks/min"
        expected_latency = f"{int(preset['timeout_threshold'] * 0.5)}s"

        return RhythmBlueprint(
            blueprint_id=self.blueprint_id,
            name=name,
            description=description,
            complexity_score=round(complexity, 2),
            complexity_level=level.value,
            compute_ratio=compute_ratio,
            communication_ratio=communication_ratio,
            agent_allocations=allocations,
            total_agents=agent_count,
            is_parallel=is_parallel,
            critical_path=critical_path,
            critical_path_duration=critical_path_duration,
            intensity=intensity.value,
            timing=TimingConfig(
                trigger_interval=preset['trigger_interval'],
                poll_interval=preset['poll_interval'],
                timeout_threshold=preset['timeout_threshold'],
                heartbeat_interval=preset['heartbeat_interval']
            ),
            max_parallel_tasks=preset['max_parallel'],
            coordination_mode='hybrid',
            expected_throughput=expected_throughput,
            expected_latency_p50=expected_latency,
            expected_success_rate='> 99%'
        )

    def generate_report(self, blueprint: RhythmBlueprint) -> str:
        """生成节奏设计报告"""
        report = f"""# 节奏设计报告

## 基本信息

| 项目 | 内容 |
|------|------|
| 蓝图ID | {blueprint.blueprint_id} |
| 名称 | {blueprint.name} |
| 描述 | {blueprint.description} |

## 任务分析

| 指标 | 数值 |
|------|------|
| 复杂度评分 | {blueprint.complexity_score}/1.0 |
| 复杂度级别 | {blueprint.complexity_level} |
| 计算密集度 | {blueprint.compute_ratio * 100:.0f}% |
| 沟通密集度 | {blueprint.communication_ratio * 100:.0f}% |

## Agent分配

| Agent | 名称 | 分配比例 | 最大并行 | 优先级 |
|------|------|---------|---------|--------|
"""
        for alloc in blueprint.agent_allocations:
            report += f"| {alloc.agent_id} | {alloc.agent_name} | {alloc.allocation_ratio * 100:.0f}% | {alloc.max_parallel} | {alloc.priority} |\n"

        report += f"""
## 依赖结构

| 属性 | 值 |
|------|---|
| 并行模式 | {'是' if blueprint.is_parallel else '否'} |
| 关键路径 | {' → '.join(blueprint.critical_path)} |
| 关键路径时长 | {blueprint.critical_path_duration} |

## 节奏配置

| 配置项 | 值 |
|--------|---|
| 节奏强度 | {blueprint.intensity} |
| 触发间隔 | {blueprint.timing.trigger_interval}秒 |
| 轮询间隔 | {blueprint.timing.poll_interval}秒 |
| 超时阈值 | {blueprint.timing.timeout_threshold}分钟 |
| 心跳间隔 | {blueprint.timing.heartbeat_interval}秒 |
| 最大并行任务 | {blueprint.max_parallel_tasks} |
| 协调模式 | {blueprint.coordination_mode} |

## 预期效果

| 指标 | 目标值 |
|------|--------|
| 吞吐量 | {blueprint.expected_throughput} |
| P50延迟 | {blueprint.expected_latency_p50} |
| 成功率 | {blueprint.expected_success_rate} |

---

*本报告由 Rhythm Designer 自动生成*
"""
        return report


def main():
    parser = argparse.ArgumentParser(description='节奏设计器')
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # design子命令
    design_parser = subparsers.add_parser('design', help='设计节奏蓝图')
    design_parser.add_argument('--name', default='未命名节奏', help='节奏名称')
    design_parser.add_argument('--description', default='', help='描述')
    design_parser.add_argument('--compute-ratio', type=float, default=0.5, help='计算密集度 0-1')
    design_parser.add_argument('--comm-ratio', type=float, default=0.5, help='沟通密集度 0-1')
    design_parser.add_argument('--waiting', type=float, default=0.5, help='等待容忍度 0-1')
    design_parser.add_argument('--deadline-critical', action='store_true', help='截止时间关键')
    design_parser.add_argument('--agent-count', type=int, default=3, help='Agent数量')
    design_parser.add_argument('--parallel', action='store_true', help='支持并行')
    design_parser.add_argument('--critical-path', nargs='+', default=['task_1', 'task_2'], help='关键路径')
    design_parser.add_argument('--critical-duration', default='10m', help='关键路径时长')
    design_parser.add_argument('--output', '-o', help='输出文件')

    # analyze子命令
    analyze_parser = subparsers.add_parser('analyze', help='分析任务日志')
    analyze_parser.add_argument('--log', required=True, help='任务日志文件')
    analyze_parser.add_argument('--output', '-o', help='输出文件')

    args = parser.parse_args()

    designer = RhythmDesigner()

    if args.command == 'design':
        blueprint = designer.design_rhythm(
            name=args.name,
            description=args.description,
            compute_ratio=args.compute_ratio,
            communication_ratio=args.comm_ratio,
            waiting_tolerance=args.waiting,
            deadline_critical=args.deadline_critical,
            agent_count=args.agent_count,
            is_parallel=args.parallel,
            critical_path=args.critical_path,
            critical_path_duration=args.critical_duration
        )

        report = designer.generate_report(blueprint)

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ 报告已保存到: {args.output}")

            json_output = args.output.replace('.md', '.json')
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(blueprint.to_dict(), f, ensure_ascii=False, indent=2)
            print(f"✅ JSON已保存到: {json_output}")
        else:
            print(report)

    elif args.command == 'analyze':
        print(f"📊 分析任务日志: {args.log}")
        print("功能开发中...")

    else:
        parser.print_help()

    return 0


if __name__ == '__main__':
    sys.exit(main())
