#!/usr/bin/env python3
"""
ViMax Agent Communicator - Agent通信管理器
支持12个专业Agent的状态查询、消息传递、并行协调
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class AgentStatus(Enum):
    """Agent状态枚举"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"


@dataclass
class AgentMessage:
    """Agent消息"""
    sender: str
    receiver: str
    content: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    type: str = "request"  # request, response, notification


@dataclass
class AgentState:
    """Agent状态"""
    name: str
    status: AgentStatus
    current_task: Optional[str] = None
    last_update: str = field(default_factory=lambda: datetime.now().isoformat())
    result: Optional[Dict[str, Any]] = None
    dependencies: List[str] = field(default_factory=list)


class ViMaxAgentCommunicator:
    """ViMax Agent通信管理器"""

    # 12个专业Agent定义
    AGENTS = {
        # 核心规划Agent
        "screenwriter": {"description": "剧本编写", "type": "planner"},
        "script_planner": {"description": "脚本规划", "type": "planner"},
        "global_info_planner": {"description": "全局信息规划", "type": "planner"},

        # 角色Agent
        "character_extractor": {"description": "角色提取", "type": "character"},
        "character_portraits_generator": {"description": "角色肖像生成", "type": "character"},

        # 参考图Agent
        "reference_image_selector": {"description": "参考图筛选", "type": "reference"},
        "best_image_selector": {"description": "最优图像选择", "type": "reference"},

        # 机位Agent
        "camera_image_generator": {"description": "机位图像生成", "type": "camera"},
        "scene_extractor": {"description": "场景提取", "type": "camera"},

        # 压缩Agent
        "event_extractor": {"description": "事件提取", "type": "compressor"},
        "novel_compressor": {"description": "小说压缩", "type": "compressor"},

        # 编排Agent
        "orchestrator": {"description": "流水线编排", "type": "coordinator"},
    }

    def __init__(self, log_dir: str = "./vimax_agent_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.agent_states: Dict[str, AgentState] = {}
        self.message_queue: List[AgentMessage] = []

        # 初始化所有Agent状态
        for agent_name in self.AGENTS:
            self.agent_states[agent_name] = AgentState(
                name=agent_name,
                status=AgentStatus.IDLE
            )

    def send_message(self, sender: str, receiver: str, content: Dict[str, Any]) -> bool:
        """发送消息"""
        if sender not in self.AGENTS:
            print(f"[Agent] 未知发送者: {sender}")
            return False
        if receiver not in self.AGENTS:
            print(f"[Agent] 未知接收者: {receiver}")
            return False

        message = AgentMessage(sender=sender, receiver=receiver, content=content)
        self.message_queue.append(message)

        self._log_message(message)
        return True

    def get_status(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """获取Agent状态"""
        if agent_name:
            if agent_name not in self.agent_states:
                return {"error": f"未知Agent: {agent_name}"}
            state = self.agent_states[agent_name]
            return {
                "name": state.name,
                "status": state.status.value,
                "current_task": state.current_task,
                "last_update": state.last_update,
                "result": state.result
            }
        else:
            return {
                "agents": {
                    name: {
                        "status": state.status.value,
                        "task": state.current_task,
                        "updated": state.last_update
                    }
                    for name, state in self.agent_states.items()
                },
                "total_agents": len(self.agent_states),
                "running_count": sum(1 for s in self.agent_states.values() if s.status == AgentStatus.RUNNING)
            }

    def update_status(self, agent_name: str, status: AgentStatus,
                     task: Optional[str] = None, result: Optional[Dict] = None):
        """更新Agent状态"""
        if agent_name not in self.agent_states:
            print(f"[Agent] 未知Agent: {agent_name}")
            return

        state = self.agent_states[agent_name]
        state.status = status
        state.last_update = datetime.now().isoformat()

        if task:
            state.current_task = task
        if result is not None:
            state.result = result

    def wait_for_dependencies(self, agent_name: str, timeout: int = 300) -> bool:
        """等待依赖Agent完成"""
        if agent_name not in self.agent_states:
            return False

        state = self.agent_states[agent_name]
        for dep in state.dependencies:
            if dep in self.agent_states:
                dep_state = self.agent_states[dep]
                if dep_state.status != AgentStatus.COMPLETED:
                    return False
        return True

    def get_pending_messages(self, agent_name: str) -> List[AgentMessage]:
        """获取待处理消息"""
        return [m for m in self.message_queue if m.receiver == agent_name and m.type == "request"]

    def _log_message(self, message: AgentMessage):
        """记录消息到日志"""
        log_file = self.log_dir / f"{message.timestamp[:10]}.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "sender": message.sender,
                "receiver": message.receiver,
                "content": message.content,
                "timestamp": message.timestamp,
                "type": message.type
            }, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="ViMax Agent Communicator")
    parser.add_argument("--status", nargs="?", const="all", help="查看Agent状态")
    parser.add_argument("--send", nargs=3, metavar=("FROM", "TO", "CONTENT"),
                       help="发送消息 (FROM TO CONTENT)")
    parser.add_argument("--update", nargs=2, metavar=("AGENT", "STATUS"),
                       help="更新状态 (AGENT STATUS)")
    parser.add_argument("--list-agents", action="store_true", help="列出所有Agent")
    parser.add_argument("--log-dir", default="./vimax_agent_logs", help="日志目录")

    args = parser.parse_args()
    communicator = ViMaxAgentCommunicator(args.log_dir)

    if args.list_agents:
        print(f"[Agent] ViMax 12个专业Agent:")
        for name, info in communicator.AGENTS.items():
            print(f"  - {name}: {info['description']} ({info['type']})")

    elif args.status:
        status = communicator.get_status(args.status if args.status != "all" else None)
        print(json.dumps(status, ensure_ascii=False, indent=2))

    elif args.send:
        sender, receiver, content = args.send
        content_json = json.loads(content) if content.startswith('{') else {"message": content}
        communicator.send_message(sender, receiver, content_json)
        print(f"[Agent] 消息已发送: {sender} -> {receiver}")

    elif args.update:
        agent, status = args.update
        status_enum = AgentStatus(status)
        communicator.update_status(agent, status_enum)
        print(f"[Agent] 状态已更新: {agent} -> {status}")


if __name__ == "__main__":
    main()
