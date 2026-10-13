#!/usr/bin/env python3
"""
DeerFlow API Client for天龙引擎
用于与DeerFlow进行交互
"""

import os
import json
import requests
from typing import Optional, Dict, Any, Generator

class DeerFlowClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.environ.get("DEERFLOW_URL", "http://localhost:2026")
        self.gateway_url = os.environ.get("DEERFLOW_GATEWAY_URL", self.base_url)
        self.langgraph_url = os.environ.get("DEERFLOW_LANGGRAPH_URL", f"{self.base_url}/api/langgraph")

    def health_check(self) -> Dict[str, Any]:
        """检查DeerFlow服务状态"""
        try:
            response = requests.get(f"{self.gateway_url}/health", timeout=5)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_models(self) -> list:
        """列出可用模型"""
        response = requests.get(f"{self.gateway_url}/api/models")
        return response.json().get("models", [])

    def list_skills(self) -> list:
        """列出可用技能"""
        response = requests.get(f"{self.gateway_url}/api/skills")
        return response.json().get("skills", [])

    def list_agents(self) -> list:
        """列出可用Agent"""
        response = requests.get(f"{self.gateway_url}/api/agents")
        return response.json().get("agents", [])

    def get_memory(self) -> Dict[str, Any]:
        """获取记忆内容"""
        response = requests.get(f"{self.gateway_url}/api/memory")
        return response.json()

    def create_thread(self) -> str:
        """创建新线程"""
        response = requests.post(f"{self.langgraph_url}/threads", json={})
        data = response.json()
        return data.get("thread_id", "")

    def send_message(self, thread_id: str, message: str, mode: str = "standard") -> Generator[str, None, None]:
        """发送消息并流式返回响应"""
        context_modes = {
            "flash": {"thinking_enabled": False, "is_plan_mode": False, "subagent_enabled": False},
            "standard": {"thinking_enabled": True, "is_plan_mode": False, "subagent_enabled": False},
            "pro": {"thinking_enabled": True, "is_plan_mode": True, "subagent_enabled": False},
            "ultra": {"thinking_enabled": True, "is_plan_mode": True, "subagent_enabled": True}
        }

        context = context_modes.get(mode, context_modes["standard"])

        payload = {
            "assistant_id": "lead_agent",
            "input": {
                "messages": [
                    {"type": "human", "content": [{"type": "text", "text": message}]}
                ]
            },
            "stream_mode": ["values", "messages-tuple"],
            "stream_subgraphs": True,
            "config": {"recursion_limit": 1000},
            "context": {**context, "thread_id": thread_id}
        }

        response = requests.post(
            f"{self.langgraph_url}/threads/{thread_id}/runs/stream",
            json=payload,
            stream=True
        )

        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    yield data

    def upload_file(self, thread_id: str, file_path: str) -> Dict[str, Any]:
        """上传文件到线程"""
        with open(file_path, "rb") as f:
            files = {"files": f}
            response = requests.post(
                f"{self.gateway_url}/api/threads/{thread_id}/uploads",
                files=files
            )
        return response.json()

    def get_thread_history(self, thread_id: str) -> list:
        """获取线程历史"""
        response = requests.get(f"{self.langgraph_url}/threads/{thread_id}/history")
        return response.json()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="DeerFlow Client")
    parser.add_argument("--health", action="store_true", help="Check service health")
    parser.add_argument("--models", action="store_true", help="List available models")
    parser.add_argument("--skills", action="store_true", help="List available skills")
    parser.add_argument("--message", type=str, help="Send a message")
    parser.add_argument("--mode", type=str, default="standard",
                        choices=["flash", "standard", "pro", "ultra"],
                        help="Execution mode")
    args = parser.parse_args()

    client = DeerFlowClient()

    if args.health:
        print(json.dumps(client.health_check(), indent=2))
    elif args.models:
        print(json.dumps(client.list_models(), indent=2))
    elif args.skills:
        print(json.dumps(client.list_skills(), indent=2))
    elif args.message:
        thread_id = client.create_thread()
        print(f"Thread ID: {thread_id}")
        print("Response:")
        for data in client.send_message(thread_id, args.message, args.mode):
            if "messages-tuple" in str(data):
                print(data)

if __name__ == "__main__":
    main()
