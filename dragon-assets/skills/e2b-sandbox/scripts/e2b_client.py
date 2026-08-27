#!/usr/bin/env python3
"""
E2B Sandbox Client - 天龙引擎云沙箱执行集成
用于安全隔离的远程代码执行和测试
"""

import os
import json
import httpx
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

@dataclass
class E2BConfig:
    """E2B配置"""
    api_key: str = ""
    base_url: str = "https://api.e2b.dev/v1"

    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv("E2B_API_KEY", ""),
            base_url=os.getenv("E2B_BASE_URL", "https://api.e2b.dev/v1")
        )

class E2BClient:
    """E2B沙箱客户端"""

    def __init__(self, config: Optional[E2BConfig] = None):
        self.config = config or E2BConfig.from_env()
        self.client = httpx.Client(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            },
            timeout=120.0
        )

    def list_sandboxes(self) -> List[Dict[str, Any]]:
        """列出所有沙箱"""
        response = self.client.get("/sandboxes")
        response.raise_for_status()
        return response.json().get("sandboxes", [])

    def create_sandbox(self, template: str = "base", timeout: int = 60) -> Dict[str, Any]:
        """创建沙箱"""
        response = self.client.post("/sandboxes", json={
            "template": template,
            "timeout": timeout
        })
        response.raise_for_status()
        return response.json()

    def run_code(self, sandbox_id: str, code: str, language: str = "python") -> Dict[str, Any]:
        """在沙箱中运行代码"""
        response = self.client.post(
            f"/sandboxes/{sandbox_id}/run",
            json={"code": code, "language": language}
        )
        response.raise_for_status()
        return response.json()

    def run_command(self, sandbox_id: str, command: str) -> Dict[str, Any]:
        """在沙箱中运行命令"""
        response = self.client.post(
            f"/sandboxes/{sandbox_id}/commands",
            json={"command": command}
        )
        response.raise_for_status()
        return response.json()

    def write_file(self, sandbox_id: str, path: str, content: str) -> Dict[str, Any]:
        """写入文件"""
        response = self.client.post(
            f"/sandboxes/{sandbox_id}/files",
            json={"path": path, "content": content}
        )
        response.raise_for_status()
        return response.json()

    def read_file(self, sandbox_id: str, path: str) -> str:
        """读取文件"""
        response = self.client.get(f"/sandboxes/{sandbox_id}/files/{path}")
        response.raise_for_status()
        return response.json().get("content", "")

    def delete_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        """删除沙箱"""
        response = self.client.delete(f"/sandboxes/{sandbox_id}")
        response.raise_for_status()
        return response.json()

    def list_templates(self) -> List[str]:
        """列出可用模板"""
        return [
            "base",           # 通用基础模板
            "data-science",  # Python数据分析
            "web-dev",       # Web开发
            "nodejs",        # Node.js开发
            "python",        # Python环境
        ]


class DragonSandbox:
    """天龙引擎集成 - 简化使用接口"""

    def __init__(self, template: str = "base", timeout: int = 60):
        self.client = E2BClient()
        self.template = template
        self.timeout = timeout
        self.sandbox_id = None

    def __enter__(self):
        result = self.client.create_sandbox(self.template, self.timeout)
        self.sandbox_id = result.get("id")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.sandbox_id:
            try:
                self.client.delete_sandbox(self.sandbox_id)
            except:
                pass

    def run_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """运行代码"""
        if not self.sandbox_id:
            raise RuntimeError("Sandbox not initialized. Use 'with' statement.")
        return self.client.run_code(self.sandbox_id, code, language)

    def run_command(self, command: str) -> Dict[str, Any]:
        """运行命令"""
        if not self.sandbox_id:
            raise RuntimeError("Sandbox not initialized. Use 'with' statement.")
        return self.client.run_command(self.sandbox_id, command)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="E2B Sandbox Client")
    parser.add_argument("action", choices=["run", "templates"], help="操作")
    parser.add_argument("--code", help="要执行的代码")
    parser.add_argument("--language", default="python", choices=["python", "nodejs", "bash"], help="语言")
    parser.add_argument("--template", default="base", help="沙箱模板")
    parser.add_argument("--timeout", type=int, default=60, help="超时时间(秒)")

    args = parser.parse_args()
    client = E2BClient()

    try:
        if args.action == "templates":
            print("Available templates:")
            for t in client.list_templates():
                print(f"  - {t}")
        elif args.action == "run":
            if not args.code:
                print("Error: --code required for run")
                exit(1)

            with DragonSandbox(template=args.template, timeout=args.timeout) as sandbox:
                result = sandbox.run_code(args.code, args.language)
                print(json.dumps(result, indent=2, ensure_ascii=False))
    except httpx.HTTPError as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
