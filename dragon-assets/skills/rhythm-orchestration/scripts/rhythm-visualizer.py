#!/usr/bin/env python3
"""
节奏可视化器 (Rhythm Visualizer)

将节奏编排蓝图渲染为Mermaid图表，支持多种可视化格式。
支持ASCII、Timeline、State Diagram、Sequence Diagram四种模式。

用法:
    python rhythm-visualizer.py <blueprint.yaml> [--format mermaid|timeline|state|sequence]
    python rhythm-visualizer.py --input-json <blueprint.json>
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@dataclass
class AgentState:
    """Agent状态节点"""
    id: str
    name: str
    status: str  # waiting, active, paused, completed
    duration_ms: int
    start_time: int
    end_time: int


@dataclass
class Transition:
    """状态转换"""
    from_id: str
    to_id: str
    condition: str  # on_success, on_failure, on_timeout
    label: str = ""


@dataclass
class Phase:
    """执行阶段"""
    id: str
    name: str
    agents: list[str]
    start_time: int
    end_time: int
    parallel: bool = False


@dataclass
class RhythmVisualization:
    """可视化数据"""
    phases: list[Phase]
    agent_states: list[AgentState]
    transitions: list[Transition]
    total_duration_ms: int
    critical_path: list[str] = field(default_factory=list)


class RhythmVisualizer:
    """节奏可视化器核心类"""

    def __init__(self):
        self.visualization: Optional[RhythmVisualization] = None

    def load_blueprint(self, path: str) -> RhythmVisualization:
        """加载蓝图文件"""
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"Blueprint file not found: {path}")

        suffix = file_path.suffix.lower()

        if suffix in ['.yaml', '.yml']:
            if not YAML_AVAILABLE:
                raise ImportError("PyYAML required for YAML files. Install: pip install pyyaml")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        elif suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")

        return self._parse_blueprint(data)

    def _parse_blueprint(self, data: dict) -> RhythmVisualization:
        """解析蓝图数据"""
        # 解析阶段
        phases = []
        for p_data in data.get('phases', []):
            phase = Phase(
                id=p_data['id'],
                name=p_data['name'],
                agents=p_data.get('agents', []),
                start_time=p_data.get('start_time', 0),
                end_time=p_data.get('end_time', 0),
                parallel=p_data.get('parallel', False)
            )
            phases.append(phase)

        # 解析Agent状态
        agent_states = []
        for s_data in data.get('agent_states', []):
            state = AgentState(
                id=s_data['id'],
                name=s_data['name'],
                status=s_data.get('status', 'waiting'),
                duration_ms=s_data.get('duration_ms', 0),
                start_time=s_data.get('start_time', 0),
                end_time=s_data.get('end_time', 0)
            )
            agent_states.append(state)

        # 解析转换
        transitions = []
        for t_data in data.get('transitions', []):
            trans = Transition(
                from_id=t_data['from'],
                to_id=t_data['to'],
                condition=t_data.get('condition', 'on_success'),
                label=t_data.get('label', '')
            )
            transitions.append(trans)

        total_duration = data.get('total_duration_ms', 0)
        critical_path = data.get('critical_path', [])

        return RhythmVisualization(
            phases=phases,
            agent_states=agent_states,
            transitions=transitions,
            total_duration_ms=total_duration,
            critical_path=critical_path
        )

    def generate_mermaid_flowchart(self) -> str:
        """生成Mermaid流程图"""
        if not self.visualization:
            raise ValueError("No visualization loaded")

        lines = ["```mermaid", "flowchart TD"]
        lines.append('    subgraph orchestration["节奏编排"]')

        # 添加阶段节点
        for phase in self.visualization.phases:
            status_icon = self._get_status_icon(phase)
            label = f'{status_icon} {phase.name}'
            lines.append(f'        {phase.id}["{label}"]')

        # 添加转换
        for trans in self.visualization.transitions:
            if trans.condition == 'on_success':
                arrow = "-->"
            elif trans.condition == 'on_failure':
                arrow = "-.->|失败|"
            elif trans.condition == 'on_timeout':
                arrow = "-.->|超时|"
            else:
                arrow = "-->"

            if trans.label:
                lines.append(f'        {trans.from_id} {arrow} {trans.to_id} : {trans.label}')
            else:
                lines.append(f'        {trans.from_id} {arrow} {trans.to_id}')

        lines.append('    end')

        # 添加图例
        lines.append('')
        lines.append('    subgraph legend["图例"]')
        lines.append('        L1["🟢 就绪"]')
        lines.append('        L2["🔵 执行中"]')
        lines.append('        L3["🟡 等待"]')
        lines.append('        L4["🟠 暂停"]')
        lines.append('        L5["🔴 失败"]')
        lines.append('        L6["🟣 完成"]')
        lines.append('    end')

        lines.append('```')
        return '\n'.join(lines)

    def generate_mermaid_timeline(self) -> str:
        """生成Mermaid时间线图"""
        if not self.visualization:
            raise ValueError("No visualization loaded")

        lines = ["```mermaid", "gantt"]

        # 标题
        title = self.visualization.phases[0].name if self.visualization.phases else "Agent Timeline"
        lines.append(f'    title {title}')
        lines.append('    dateFormat X')
        lines.append('    axisFormat %s')

        # 添加任务条
        for state in self.visualization.agent_states:
            status_color = self._get_status_color(state.status)
            duration = state.end_time - state.start_time
            lines.append(f'    {state.name} :{state.start_time}, {duration}')

        lines.append('```')
        return '\n'.join(lines)

    def generate_state_diagram(self) -> str:
        """生成Mermaid状态图"""
        if not self.visualization:
            raise ValueError("No visualization loaded")

        lines = ["```mermaid", "stateDiagram-v2"]

        # 定义状态
        for state in self.visualization.agent_states:
            status_icon = self._get_status_icon(state)
            lines.append(f'    {state.id} : {status_icon} {state.name}')

        lines.append('')

        # 定义转换
        for trans in self.visualization.transitions:
            if trans.condition == 'on_success':
                lines.append(f'    {trans.from_id} --> {trans.to_id}')
            elif trans.condition == 'on_failure':
                lines.append(f'    {trans.from_id} --> [{trans.to_id} 失败]')
            elif trans.condition == 'on_timeout':
                lines.append(f'    {trans.from_id} --> [{trans.to_id} 超时]')

        lines.append('```')
        return '\n'.join(lines)

    def generate_sequence_diagram(self) -> str:
        """生成Mermaid序列图"""
        if not self.visualization:
            raise ValueError("No visualization loaded")

        lines = ["```mermaid", "sequenceDiagram"]

        # 参与者
        agent_names = [s.name for s in self.visualization.agent_states]
        for name in agent_names:
            lines.append(f'    participant {name}')

        lines.append('')

        # 时间线
        current_time = 0
        for state in self.visualization.agent_states:
            duration = state.end_time - state.start_time

            if duration > 0:
                # 进入激活
                lines.append(f'    {state.name}->>+{state.name} : 开始执行')
                lines.append(f'    Note over {state.name} : 持续 {duration}ms')
                lines.append(f'    {state.name}-->>-{state.name} : 完成')

        # 转换箭头
        for trans in self.visualization.transitions:
            from_state = next((s for s in self.visualization.agent_states if s.id == trans.from_id), None)
            to_state = next((s for s in self.visualization.agent_states if s.id == trans.to_id), None)

            if from_state and to_state:
                if trans.condition == 'on_success':
                    lines.append(f'    {from_state.name}-->>{to_state.name} : 成功')
                elif trans.condition == 'on_failure':
                    lines.append(f'    {from_state.name}-->>{to_state.name} : 失败')
                elif trans.condition == 'on_timeout':
                    lines.append(f'    {from_state.name}-->>{to_state.name} : 超时')

        lines.append('```')
        return '\n'.join(lines)

    def generate_ascii_timeline(self) -> str:
        """生成ASCII时间线图"""
        if not self.visualization:
            raise ValueError("No visualization loaded")

        lines = []
        total_time = self.visualization.total_duration_ms

        # 时间轴头部
        lines.append('=' * 80)
        lines.append('节奏编排时间线')
        lines.append('=' * 80)

        # 时间刻度
        scale = 50  # 字符宽度
        time_markers = [0, total_time // 4, total_time // 2, 3 * total_time // 4, total_time]
        time_labels = [f'{t}ms' for t in time_markers]

        lines.append('')
        lines.append('时间轴: ' + '─' * scale)

        # 时间标签
        for i, (marker, label) in enumerate(zip(time_markers, time_labels)):
            pos = int(marker / total_time * scale)
            lines.append(' ' * (7 + pos) + f'│{label}')

        lines.append('')

        # Agent行
        for state in self.visualization.agent_states:
            start_pos = int(state.start_time / total_time * scale)
            duration = int((state.end_time - state.start_time) / total_time * scale)

            status_icon = self._get_status_icon(state)
            bar = ' ' * start_pos + '█' * max(duration, 1) + status_icon

            lines.append(f'{state.name:12} │{bar}')
            lines.append(' ' * 12 + ' │' + ' ' * scale)

        lines.append('')
        lines.append('=' * 80)

        # 图例
        lines.append('')
        lines.append('图例:')
        lines.append('  🟢 就绪  🔵 执行中  🟡 等待  🟠 暂停  🔴 失败  🟣 完成')

        # 统计信息
        lines.append('')
        lines.append(f'总时长: {self.visualization.total_duration_ms}ms')
        lines.append(f'Agent数: {len(self.visualization.agent_states)}')
        lines.append(f'阶段数: {len(self.visualization.phases)}')

        if self.visualization.critical_path:
            lines.append(f'关键路径: {" -> ".join(self.visualization.critical_path)}')

        return '\n'.join(lines)

    def generate(self, format: str = 'mermaid') -> str:
        """生成可视化输出"""
        format_handlers = {
            'mermaid': self.generate_mermaid_flowchart,
            'flowchart': self.generate_mermaid_flowchart,
            'timeline': self.generate_mermaid_timeline,
            'state': self.generate_state_diagram,
            'sequence': self.generate_sequence_diagram,
            'ascii': self.generate_ascii_timeline,
        }

        handler = format_handlers.get(format.lower(), self.generate_mermaid_flowchart)
        return handler()

    def _get_status_icon(self, obj) -> str:
        """获取状态图标"""
        status = getattr(obj, 'status', 'waiting')
        icons = {
            'ready': '🟢',
            'waiting': '🟡',
            'active': '🔵',
            'running': '🔵',
            'paused': '🟠',
            'failed': '🔴',
            'completed': '🟣',
            'success': '🟣',
        }
        return icons.get(status, '⚪')

    def _get_status_color(self, status: str) -> str:
        """获取状态颜色（Mermaid）"""
        colors = {
            'ready': 'green',
            'waiting': 'yellow',
            'active': 'blue',
            'running': 'blue',
            'paused': 'orange',
            'failed': 'red',
            'completed': 'purple',
            'success': 'purple',
        }
        return colors.get(status, 'gray')


def main():
    parser = argparse.ArgumentParser(
        description='节奏可视化器 - 将节奏编排蓝图渲染为可视化图表',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python rhythm-visualizer.py blueprint.yaml --format mermaid
  python rhythm-visualizer.py blueprint.json --format ascii
  python rhythm-visualizer.py blueprint.yaml --format timeline --output timeline.md

支持格式:
  mermaid  - Mermaid流程图（默认）
  flowchart - Mermaid流程图（同mermaid）
  timeline  - Mermaid时间线图
  state    - Mermaid状态图
  sequence - Mermaid序列图
  ascii    - ASCII艺术时间线
'''
    )

    parser.add_argument('blueprint', nargs='?', help='蓝图文件路径（YAML或JSON）')
    parser.add_argument('--input-json', '--json', dest='input_json',
                        help='从JSON字符串加载蓝图（用于管道输入）')
    parser.add_argument('--format', '-f', choices=['mermaid', 'flowchart', 'timeline', 'state', 'sequence', 'ascii'],
                        default='mermaid', help='输出格式（默认: mermaid）')
    parser.add_argument('--output', '-o', help='输出文件路径（默认: 输出到stdout）')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')

    args = parser.parse_args()

    try:
        visualizer = RhythmVisualizer()

        # 加载数据
        if args.input_json:
            data = json.loads(args.input_json)
            visualizer.visualization = visualizer._parse_blueprint(data)
        elif args.blueprint:
            visualizer.visualization = visualizer.load_blueprint(args.blueprint)
        else:
            # 尝试从stdin读取
            if not sys.stdin.isatty():
                input_data = sys.stdin.read()
                data = json.loads(input_data)
                visualizer.visualization = visualizer._parse_blueprint(data)
            else:
                parser.print_help()
                sys.exit(1)

        # 生成可视化
        output = visualizer.generate(args.format)

        # 输出
        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f'可视化已保存到: {args.output}', file=sys.stderr)
        else:
            print(output)

    except FileNotFoundError as e:
        print(f'错误: {e}', file=sys.stderr)
        sys.exit(1)
    except ImportError as e:
        print(f'错误: {e}', file=sys.stderr)
        print('提示: 安装依赖: pip install pyyaml', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'错误: {e}', file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
