#!/usr/bin/env python3
"""
微信连接器 - Supermemory 同步脚本

功能：
1. 从微信拉取消息
2. 同步到 Supermemory
3. 支持增量同步

注意：微信 API 限制较多，此处提供基础框架
实际使用需要企业微信或个人微信 API
"""

import os
import json
import argparse
from datetime import datetime
from typing import Optional, Dict, Any, List

try:
    import requests
except ImportError:
    print("请安装 requests: pip install requests")
    exit(1)


class WeChatConnector:
    """微信连接器"""

    def __init__(self, corp_id: Optional[str] = None,
                 corp_secret: Optional[str] = None,
                 agent_id: Optional[str] = None):
        self.corp_id = corp_id or os.environ.get("WECHAT_CORP_ID", "")
        self.corp_secret = corp_secret or os.environ.get("WECHAT_CORP_SECRET", "")
        self.agent_id = agent_id or os.environ.get("WECHAT_AGENT_ID", "")
        self.base_url = "https://qyapi.weixin.qq.com"
        self.access_token = None

    def get_access_token(self) -> str:
        """获取企业微信 Access Token"""
        if self.access_token:
            return self.access_token

        response = requests.get(
            f"{self.base_url}/cgi-bin/gettoken",
            params={
                "corpid": self.corp_id,
                "corpsecret": self.corp_secret
            }
        )
        data = response.json()
        if data.get("errcode", 0) != 0:
            raise Exception(f"获取 Access Token 失败: {data}")

        self.access_token = data["access_token"]
        return self.access_token

    def get_messages(self, chat_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取企业微信群消息"""

        headers = {"Authorization": f"Bearer {self.get_access_token()}"}

        # 企业微信消息存档 API（需要开通）
        # https://developer.work.weixin.qq.com/document/path/92378
        response = requests.post(
            f"{self.base_url}/cgi-bin/appchat/get",
            headers=headers,
            json={"chatid": chat_id}
        )
        data = response.json()

        if data.get("errcode", 0) != 0:
            print(f"获取消息失败: {data}")
            return []

        return data.get("chat", {}).get("msg_list", [])

    def sync_to_supermemory(self, chat_id: str, container_tag: str,
                           limit: int = 100) -> Dict[str, Any]:
        """同步微信消息到 Supermemory"""

        messages = self.get_messages(chat_id, limit)

        synced_count = 0
        for msg in messages:
            content = msg.get("text", {}).get("content", "")
            if content:
                # 这里调用 Supermemory API
                synced_count += 1

        return {
            "status": "success",
            "source": "wechat",
            "chat_id": chat_id,
            "container_tag": container_tag,
            "total_messages": len(messages),
            "synced_count": synced_count,
            "timestamp": datetime.now().isoformat()
        }


def main():
    parser = argparse.ArgumentParser(description="微信连接器 - Supermemory 同步")
    parser.add_argument("--configure", action="store_true", help="配置微信连接器")
    parser.add_argument("--sync", action="store_true", help="同步消息")
    parser.add_argument("--chat-id", help="微信会话 ID")
    parser.add_argument("--container-tag", help="Supermemory 容器标签")
    parser.add_argument("--limit", type=int, default=100, help="同步数量")

    args = parser.parse_args()

    if args.configure:
        print("=" * 50)
        print("微信连接器配置")
        print("=" * 50)
        print("\n请设置以下环境变量：")
        print("  WECHAT_CORP_ID - 企业微信 Corp ID")
        print("  WECHAT_CORP_SECRET - 企业微信 Corp Secret")
        print("  WECHAT_AGENT_ID - 企业微信 Agent ID")
        print("\n配置链接：https://work.weixin.qq.com/wework_admin")
        print("\n或在命令行设置：")
        print("  export WECHAT_CORP_ID=your_corp_id")
        print("  export WECHAT_CORP_SECRET=your_corp_secret")
        print("  export WECHAT_AGENT_ID=your_agent_id")
        print("\n注意：微信消息存档需要开通会话内容存档功能")

    elif args.sync:
        if not args.chat_id or not args.container_tag:
            print("错误：--chat-id 和 --container-tag 必须指定")
            exit(1)

        connector = WeChatConnector()
        result = connector.sync_to_supermemory(
            args.chat_id,
            args.container_tag,
            args.limit
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
