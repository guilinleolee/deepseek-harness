#!/usr/bin/env python3
"""
Supermemory Python Client - 天龙引擎集成脚本

功能：
1. 存储内容到 Supermemory
2. 查询用户画像和记忆
3. 同步飞书/微信消息
"""

import os
import json
import argparse
from typing import Optional, Dict, Any, List

# 尝试导入 supermemory，如果未安装则使用 requests
try:
    from supermemory import Supermemory
    HAS_SUPERMEMORY = True
except ImportError:
    HAS_SUPERMEMORY = False
    import requests

class SupermemoryClient:
    """Supermemory 客户端封装"""

    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.api_key = api_key or os.environ.get("SUPERMEMORY_API_KEY", "")
        self.endpoint = endpoint or "https://mcp.supermemory.ai"
        self.client = None

        if HAS_SUPERMEMORY:
            self.client = Supermemory(api_key=self.api_key) if self.api_key else Supermemory()

    def add(self, content: str, container_tag: str, source: str = "manual",
            metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """存储内容到 Supermemory"""

        if self.client:
            result = self.client.add({
                "content": content,
                "containerTag": container_tag,
                "source": source,
                "metadata": metadata or {}
            })
            return {"status": "success", "result": result}

        # 备用：直接调用 MCP API
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        response = requests.post(
            f"{self.endpoint}/add",
            headers=headers,
            json={"content": content, "containerTag": container_tag, "source": source}
        )
        return response.json()

    def profile(self, container_tag: str, query: str) -> Dict[str, Any]:
        """获取用户画像 + 搜索结果"""

        if self.client:
            result = self.client.profile({
                "containerTag": container_tag,
                "q": query
            })
            return result

        # 备用：直接调用 MCP API
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        response = requests.post(
            f"{self.endpoint}/profile",
            headers=headers,
            json={"containerTag": container_tag, "q": query}
        )
        return response.json()

    def search(self, container_tag: str, query: str,
                mode: str = "hybrid") -> List[Dict[str, Any]]:
        """搜索记忆"""

        if self.client:
            result = self.client.search.memories({
                "containerTag": container_tag,
                "q": query,
                "mode": mode
            })
            return result

        # 备用：直接调用 MCP API
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        response = requests.post(
            f"{self.endpoint}/search",
            headers=headers,
            json={"containerTag": container_tag, "q": query, "mode": mode}
        )
        return response.json().get("results", [])

    def sync_feishu(self, chat_id: str, limit: int = 100) -> Dict[str, Any]:
        """同步飞书消息到 Supermemory"""

        # 这里需要集成飞书 SDK
        # 暂时返回示例
        return {
            "status": "success",
            "source": "feishu",
            "chat_id": chat_id,
            "synced_count": 0,
            "message": "需要配置飞书 API Key"
        }

    def sync_wechat(self, chat_id: str, limit: int = 100) -> Dict[str, Any]:
        """同步微信消息到 Supermemory"""

        # 这里需要集成微信 SDK
        # 暂时返回示例
        return {
            "status": "success",
            "source": "wechat",
            "chat_id": chat_id,
            "synced_count": 0,
            "message": "需要配置微信 API Key"
        }


def main():
    parser = argparse.ArgumentParser(description="Supermemory 客户端")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # add 子命令
    add_parser = subparsers.add_parser("add", help="添加记忆")
    add_parser.add_argument("--content", "-c", required=True, help="记忆内容")
    add_parser.add_argument("--tag", "-t", required=True, help="容器标签")
    add_parser.add_argument("--source", "-s", default="manual", help="来源")
    add_parser.add_argument("--api-key", "-k", help="API Key")

    # profile 子命令
    profile_parser = subparsers.add_parser("profile", help="查询用户画像")
    profile_parser.add_argument("--tag", "-t", required=True, help="容器标签")
    profile_parser.add_argument("--query", "-q", required=True, help="查询内容")
    profile_parser.add_argument("--api-key", "-k", help="API Key")

    # search 子命令
    search_parser = subparsers.add_parser("search", help="搜索记忆")
    search_parser.add_argument("--tag", "-t", required=True, help="容器标签")
    search_parser.add_argument("--query", "-q", required=True, help="查询内容")
    search_parser.add_argument("--mode", "-m", default="hybrid", help="搜索模式")
    search_parser.add_argument("--api-key", "-k", help="API Key")

    # sync 子命令
    sync_parser = subparsers.add_parser("sync", help="同步消息")
    sync_parser.add_argument("--source", required=True, choices=["feishu", "wechat"],
                           help="同步来源")
    sync_parser.add_argument("--chat-id", required=True, help="会话 ID")
    sync_parser.add_argument("--limit", "-l", type=int, default=100, help="同步数量")
    sync_parser.add_argument("--api-key", "-k", help="API Key")

    args = parser.parse_args()
    client = SupermemoryClient(api_key=args.api_key if hasattr(args, 'api_key') else None)

    if args.command == "add":
        result = client.add(args.content, args.tag, args.source)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "profile":
        result = client.profile(args.tag, args.query)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "search":
        results = client.search(args.tag, args.query, args.mode)
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.command == "sync":
        if args.source == "feishu":
            result = client.sync_feishu(args.chat_id, args.limit)
        else:
            result = client.sync_wechat(args.chat_id, args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
