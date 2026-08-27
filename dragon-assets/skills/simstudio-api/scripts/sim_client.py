#!/usr/bin/env python3
"""
SimStudio API Client - 天龙引擎Sim工作流编排集成
用于与Sim平台交互，执行和管理AI Agent工作流
"""

import os
import json
import httpx
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

@dataclass
class SimConfig:
    """Sim配置"""
    api_key: str = ""
    workspace_id: str = ""
    base_url: str = "https://api.sim.ai/v1"

    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv("SIM_API_KEY", ""),
            workspace_id=os.getenv("SIM_WORKSPACE_ID", ""),
            base_url=os.getenv("SIM_BASE_URL", "https://api.sim.ai/v1")
        )

class SimClient:
    """Sim工作流客户端"""

    def __init__(self, config: Optional[SimConfig] = None):
        self.config = config or SimConfig.from_env()
        self.client = httpx.Client(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )

    def list_workflows(self) -> List[Dict[str, Any]]:
        """列出所有工作流"""
        response = self.client.get("/workflows")
        response.raise_for_status()
        return response.json().get("workflows", [])

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流详情"""
        response = self.client.get(f"/workflows/{workflow_id}")
        response.raise_for_status()
        return response.json()

    def create_workflow(self, name: str, description: str = "", nodes: List[Dict] = None, edges: List[Dict] = None) -> Dict[str, Any]:
        """创建工作流"""
        workflow = {
            "name": name,
            "description": description,
            "nodes": nodes or [],
            "edges": edges or []
        }
        response = self.client.post("/workflows", json=workflow)
        response.raise_for_status()
        return response.json()

    def run_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行工作流"""
        response = self.client.post(
            f"/workflows/{workflow_id}/run",
            json={"input": input_data}
        )
        response.raise_for_status()
        return response.json()

    def get_run_status(self, workflow_id: str, run_id: str) -> Dict[str, Any]:
        """获取运行状态"""
        response = self.client.get(f"/workflows/{workflow_id}/runs/{run_id}")
        response.raise_for_status()
        return response.json()

    def list_integrations(self) -> List[Dict[str, Any]]:
        """列出所有可用集成"""
        response = self.client.get("/integrations")
        response.raise_for_status()
        return response.json().get("integrations", [])

    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        response = self.client.post(
            "/tools/execute",
            json={"tool": tool_name, "params": params}
        )
        response.raise_for_status()
        return response.json()

def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="SimStudio API Client")
    parser.add_argument("action", choices=["list", "get", "create", "run", "status", "integrations"], help="操作")
    parser.add_argument("--workflow-id", help="工作流ID")
    parser.add_argument("--run-id", help="运行ID")
    parser.add_argument("--name", help="工作流名称")
    parser.add_argument("--description", help="工作流描述")
    parser.add_argument("--input", help="输入数据(JSON)")
    parser.add_argument("--tool", help="工具名称")
    parser.add_argument("--params", help="工具参数(JSON)")

    args = parser.parse_args()
    client = SimClient()

    try:
        if args.action == "list":
            workflows = client.list_workflows()
            print(json.dumps(workflows, indent=2, ensure_ascii=False))
        elif args.action == "get":
            if not args.workflow_id:
                parser.error("--workflow-id required for get")
            result = client.get_workflow(args.workflow_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.action == "create":
            if not args.name:
                parser.error("--name required for create")
            result = client.create_workflow(args.name, args.description or "")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.action == "run":
            if not args.workflow_id:
                parser.error("--workflow-id required for run")
            input_data = json.loads(args.input) if args.input else {}
            result = client.run_workflow(args.workflow_id, input_data)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.action == "status":
            if not args.workflow_id or not args.run_id:
                parser.error("--workflow-id and --run-id required for status")
            result = client.get_run_status(args.workflow_id, args.run_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.action == "integrations":
            integrations = client.list_integrations()
            print(json.dumps(integrations, indent=2, ensure_ascii=False))
    except httpx.HTTPError as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
