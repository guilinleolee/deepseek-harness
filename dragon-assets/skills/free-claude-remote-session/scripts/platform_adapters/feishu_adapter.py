#!/usr/bin/env python3
"""
feishu_adapter.py - 飞书/Lark平台适配器
将飞书消息转换为Dragon Gateway协议并路由到Claude Code会话
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from permission_checker import PermissionChecker, Permission, check_permission, require_permission
from stream_output import get_formatter, StreamProcessor, StreamChunk

LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "feishu.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("feishu_adapter")


class DragonGatewayClient:
    """Dragon Gateway HTTP客户端"""

    def __init__(self, host: str = "localhost", port: int = 37778, token: str = ""):
        self.base_url = f"http://{host}:{port}"
        self.token = token
        self.timeout = 30

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def create_session(self, user_id: str, platform: str, chat_id: str, message: str) -> dict:
        """创建新会话"""
        import aiohttp
        payload = {
            "action": "session_create",
            "user_id": user_id,
            "platform": platform,
            "chat_id": chat_id,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/session",
                json=payload,
                headers=self._headers(),
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as resp:
                return await resp.json()

    async def send_message(self, session_id: str, content: str, chunk_type: str = "text") -> dict:
        """发送消息到会话"""
        import aiohttp
        payload = {
            "action": "message_send",
            "session_id": session_id,
            "content": content,
            "chunk_type": chunk_type,
            "timestamp": datetime.now().isoformat(),
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/message",
                json=payload,
                headers=self._headers(),
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            ) as resp:
                return await resp.json()

    async def stream_events(self, session_id: str):
        """获取会话流式事件（SSE）"""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/session/{session_id}/stream",
                headers=self._headers(),
                timeout=aiohttp.ClientTimeout(total=self.timeout * 10),
            ) as resp:
                async for line in resp.content:
                    if line:
                        yield line.decode("utf-8").strip()


class FeishuBotHandler:
    """飞书 Bot消息处理器"""

    def __init__(self, app_id: str, app_secret: str, allowed_chats: list[str],
                 admin_users: list[str], gateway_host: str = "localhost",
                 gateway_port: int = 37778, gateway_token: str = "", session_timeout: int = 3600):
        from lark_oapi.adapter.standard import DefaultSigner
        from lark_oapi.api.im.v1 import CreateMessageClient
        from lark_oapi.event import EventDispatcher
        from lark_oapi.event.annotation import Event
        from lark_oapi.event.callback import MessageReceiveV1

        self.app_id = app_id
        self.app_secret = app_secret
        self.allowed_chats = set(allowed_chats)
        self.admin_users = set(admin_users)
        self.gateway = DragonGatewayClient(gateway_host, gateway_port, gateway_token)
        self.session_timeout = session_timeout
        self.processor = StreamProcessor("feishu")
        self.permission_checker = PermissionChecker()
        self.client = None
        self.message_client = None
        self.dispatcher = None

        self.active_sessions: dict[str, str] = {}
        for uid in self.admin_users:
            self.permission_checker.set_user_role(uid, "admin")

    def _check_access(self, chat_id: str, user_id: str) -> bool:
        """检查用户是否有访问权限"""
        if self.allowed_chats and chat_id not in self.allowed_chats:
            return False
        return True

    def _make_card(self, content: str) -> dict:
        """生成飞书消息卡片"""
        return {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "elements": [{"tag": "markdown", "content": content}]
            }
        }

    def _make_text_card(self, text: str) -> dict:
        """生成飞书文本卡片"""
        return {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "elements": [{"tag": "div", "text": {"tag": "lark_md", "content": text}}]
            }
        }

    async def send_card(self, chat_id: str, content: str):
        """发送卡片消息"""
        from lark_oapi.api.im.v1 import CreateMessageClient
        from lark_oapi.api.im.v1.model import CreateMessageRequestBody

        card = self._make_card(content)
        body = CreateMessageRequestBody(
            receive_id=chat_id,
            msg_type="interactive",
            content=json.dumps(card),
        )
        self.message_client.create(
            CreateMessageClient.CreateMessageRequestBuilder().body(body).build()
        )

    async def send_text(self, chat_id: str, text: str):
        """发送文本消息"""
        from lark_oapi.api.im.v1 import CreateMessageClient
        from lark_oapi.api.im.v1.model import CreateMessageRequestBody

        body = CreateMessageRequestBody(
            receive_id=chat_id,
            msg_type="text",
            content=json.dumps({"text": text}),
        )
        self.message_client.create(
            CreateMessageClient.CreateMessageRequestBuilder().body(body).build()
        )

    async def handle_command(self, chat_id: str, user_id: str, text: str):
        """处理命令消息"""
        from lark_oapi.api.im.v1 import CreateMessageClient
        from lark_oapi.api.im.v1.model import CreateMessageRequestBody

        if text.startswith("/start"):
            if not self._check_access(chat_id, user_id):
                await self.send_text(chat_id, "❌ 访问被拒绝。请联系管理员授权。")
                return
            welcome = "🤖 **Claude Code 飞书 Bot**\n\n你好！我是你的Claude Code远程助手。\n\n**可用命令：**\n`/new` - 创建新会话\n`/sessions` - 查看当前会话\n`/cancel` - 取消当前会话\n`/help` - 显示帮助\n\n直接发送消息即可开始对话！"
            await self.send_text(chat_id, welcome)

        elif text.startswith("/new"):
            if not self._check_access(chat_id, user_id):
                await self.send_text(chat_id, "❌ 访问被拒绝。")
                return
            if not check_permission(user_id, Permission.SESSION_CREATE):
                await self.send_text(chat_id, "❌ 权限不足，无法创建会话。")
                return
            if chat_id in self.active_sessions:
                sid = self.active_sessions[chat_id]
                await self.send_text(chat_id, f"⚠️ 当前已有活跃会话 `{sid[:20]}...`，请先 /cancel 后再创建。")
                return
            await self.send_text(chat_id, "🆕 正在创建新会话...")
            try:
                result = await self.gateway.create_session(user_id, "feishu", chat_id, "")
                if result.get("success"):
                    session_id = result["session_id"]
                    self.active_sessions[chat_id] = session_id
                    await self.send_text(chat_id, f"✅ 会话已创建：\n`{session_id}`")
                    logger.info(f"Session created: {session_id} for user {user_id}")
                else:
                    await self.send_text(chat_id, f"❌ 创建失败：{result.get('error', '未知错误')}")
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                await self.send_text(chat_id, f"❌ 连接Dragon Gateway失败：{str(e)[:100]}")

        elif text.startswith("/sessions"):
            if chat_id not in self.active_sessions:
                await self.send_text(chat_id, "⚠️ 当前没有活跃会话。")
                return
            sid = self.active_sessions[chat_id]
            await self.send_text(chat_id, f"📋 会话状态：\nID: `{sid[:20]}...`\n状态: 运行中")

        elif text.startswith("/cancel"):
            if not check_permission(user_id, Permission.SESSION_CANCEL):
                await self.send_text(chat_id, "❌ 权限不足，无法取消会话。")
                return
            if chat_id not in self.active_sessions:
                await self.send_text(chat_id, "⚠️ 当前没有活跃会话。")
                return
            session_id = self.active_sessions.pop(chat_id)
            await self.send_text(chat_id, f"🚫 会话已取消：`{session_id[:20]}...`")
            logger.info(f"Session cancelled: {session_id}")

        elif text.startswith("/help"):
            help_text = "📖 **帮助**\n\n**基本命令：**\n`/new` - 创建新会话\n`/sessions` - 查看当前会话\n`/cancel` - 取消当前会话\n`/status` - 查看状态"
            await self.send_text(chat_id, help_text)

        elif text.startswith("/status"):
            await self.send_text(chat_id,
                f"✅ **Dragon Gateway连接状态**\n"
                f"Gateway: {self.gateway.base_url}\n"
                f"活跃会话数: {len(self.active_sessions)}")

        else:
            if chat_id not in self.active_sessions:
                await self.send_text(chat_id, "⚠️ 没有活跃会话，请先发送 `/new` 创建新会话。")
                return
            if not check_permission(user_id, Permission.SESSION_CREATE):
                await self.send_text(chat_id, "❌ 权限不足。")
                return
            session_id = self.active_sessions[chat_id]
            await self.send_text(chat_id, "⏳ 正在处理...")
            try:
                await self.gateway.send_message(session_id, text)
                response_parts = []
                async for event_line in self.gateway.stream_events(session_id):
                    if event_line.startswith("data:"):
                        data = json.loads(event_line[5:])
                        chunk = StreamChunk(
                            content=data.get("content", ""),
                            chunk_type=data.get("type", "text"),
                            language=data.get("language"),
                        )
                        formatted = self.processor.process_chunk(chunk)
                        response_parts.append(formatted)

                final_response = "\n".join(response_parts)
                if final_response:
                    final_response = self.processor.formatter.truncate(final_response)
                    card = self._make_card(final_response)
                    await self.send_card(chat_id, final_response)
                else:
                    await self.send_text(chat_id, "✅ 处理完成，无输出。")
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                await self.send_text(chat_id, f"❌ 处理失败：{str(e)[:200]}")


def main():
    """主入口"""
    import argparse
    from lark_oapi.adapter.standard import DefaultSigner
    from lark_oapi.api.im.v1 import CreateMessageClient
    from lark_oapi.event import EventDispatcher
    from lark_oapi.event.annotation import Event
    from lark_oapi.event.callback import MessageReceiveV1

    parser = argparse.ArgumentParser(description="Feishu Platform Adapter")
    parser.add_argument("--app-id", default=os.getenv("FEISHU_APP_ID"), help="飞书 App ID")
    parser.add_argument("--app-secret", default=os.getenv("FEISHU_APP_SECRET"), help="飞书 App Secret")
    parser.add_argument("--allowed-chats", default=os.getenv("FEISHU_ALLOWED_CHATS", ""),
                        help="Comma-separated allowed chat IDs")
    parser.add_argument("--admin-users", default=os.getenv("FEISHU_ADMIN_USERS", ""),
                        help="Comma-separated admin user IDs")
    parser.add_argument("--gateway-host", default=os.getenv("DRAGON_GATEWAY_HOST", "localhost"))
    parser.add_argument("--gateway-port", type=int, default=int(os.getenv("DRAGON_GATEWAY_PORT", "37778")))
    parser.add_argument("--gateway-token", default=os.getenv("DRAGON_GATEWAY_TOKEN", ""))
    parser.add_argument("--port", type=int, default=int(os.getenv("FEISHU_PORT", "37777")))
    args = parser.parse_args()

    if not args.app_id or not args.app_secret:
        logger.error("FEISHU_APP_ID and FEISHU_APP_SECRET are required")
        sys.exit(1)

    chats = [c.strip() for c in args.allowed_chats.split(",") if c.strip()]
    admins = [u.strip() for u in args.admin_users.split(",") if u.strip()]

    handler = FeishuBotHandler(
        app_id=args.app_id,
        app_secret=args.app_secret,
        allowed_chats=chats,
        admin_users=admins,
        gateway_host=args.gateway_host,
        gateway_port=args.gateway_port,
        gateway_token=args.gateway_token,
    )

    from lark_oapi.api.im.v1 import CreateMessageClient
    from lark_oapi.api.im.v1.model import CreateMessageRequestBody

    handler.message_client = CreateMessageClient(
        args.app_id, args.app_secret, DefaultSigner(args.app_id, args.app_secret)
    )

    event_handler = handler

    @Event(event_type="im.message.receive_v1")
    def handle_message(data: MessageReceiveV1) -> None:
        message = data.message
        if not message:
            return

        sender = message.sender
        if not sender or not sender.sender_id:
            return

        chat_id = message.chat_id
        user_id = sender.sender_id.open_id or sender.sender_id.user_id or ""

        if message.message_type != "text":
            return

        try:
            content = json.loads(message.content)
            text = content.get("text", "")
        except Exception:
            return

        if not text.startswith("/"):
            asyncio.create_task(event_handler.handle_command(chat_id, user_id, text))
        else:
            asyncio.create_task(event_handler.handle_command(chat_id, user_id, text))

    from lark_oapi.adapter.fastapi import build_routing_fastapi
    from fastapi import FastAPI
    import uvicorn

    app: FastAPI = build_routing_fastapi(handler.dispatcher)

    logger.info("Feishu adapter starting...")
    print(f"Feishu adapter started. Listening on port {args.port}")
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == "__main__":
    main()
