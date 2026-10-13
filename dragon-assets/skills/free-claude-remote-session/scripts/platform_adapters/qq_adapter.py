#!/usr/bin/env python3
"""
qq_adapter.py - QQ平台适配器
将QQ消息转换为Dragon Gateway协议并路由到Claude Code会话
支持go-cqhttp / Lagrange.Core /NapCat 等CQHTTP协议兼容端点
"""

import asyncio
import json
import logging
import os
import re
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
        logging.FileHandler(LOG_DIR / "qq.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("qq_adapter")


# ============ CQ码解析工具 ============

CQ_PATTERN = re.compile(r'\[CQ:([^,\]]+)(?:,([^\]]*))?\]')

def escape_cq(text: str) -> str:
    """转义CQ码特殊字符"""
    mapping = {
        "&amp;": "&",
        "&quot;": "\"",
        "&#91;": "[",
        "&#93;": "]",
        "&comma;": ",",
    }
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text

def unescape_cq(text: str) -> str:
    """反转义CQ码特殊字符"""
    mapping = {
        "&": "&amp;",
        "\"": "&quot;",
        "[": "&#91;",
        "]": "&#93;",
        ",": "&comma;",
    }
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text

def parse_cq_codes(text: str) -> list[dict]:
    """解析CQ码，返回元素列表"""
    elements = []
    last_end = 0
    for match in CQ_PATTERN.finditer(text):
        if match.start() > last_end:
            plain = text[last_end:match.start()]
            if plain:
                elements.append({"type": "text", "data": {"text": escape_cq(plain)}})
        cq_type = match.group(1)
        params_str = match.group(2) or ""
        params = {}
        if params_str:
            for pair in params_str.split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    params[k] = v
        elements.append({"type": cq_type, "data": params})
        last_end = match.end()
    if last_end < len(text):
        plain = text[last_end:]
        if plain:
            elements.append({"type": "text", "data": {"text": escape_cq(plain)}})
    return elements


# ============ Dragon Gateway 通信 ============

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


# ============ QQ WebSocket 适配器 ============

class QQBotHandler:
    """QQ Bot消息处理器 (CQHTTP WebSocket反向WebSocket模式)"""

    def __init__(self, ws_url: str, access_token: str, allowed_groups: list[str],
                 allowed_users: list[str], admin_users: list[str],
                 gateway_host: str = "localhost", gateway_port: int = 37778,
                 gateway_token: str = "", session_timeout: int = 3600):
        self.ws_url = ws_url
        self.access_token = access_token
        self.allowed_groups = set(allowed_groups)
        self.allowed_users = set(allowed_users)
        self.admin_users = set(admin_users)
        self.gateway = DragonGatewayClient(gateway_host, gateway_port, gateway_token)
        self.session_timeout = session_timeout
        self.processor = StreamProcessor("qq")
        self.permission_checker = PermissionChecker()
        self.ws = None
        self.running = False

        # group_id -> session_id
        self.active_sessions: dict[str, str] = {}
        # user_id -> session_id (私聊)
        self.private_sessions: dict[str, str] = {}

        for uid in self.admin_users:
            self.permission_checker.set_user_role(uid, "admin")

    def _check_access(self, group_id: Optional[str], user_id: str) -> bool:
        """检查用户是否有访问权限"""
        if group_id and self.allowed_groups and group_id not in self.allowed_groups:
            return False
        if self.allowed_users and user_id not in self.allowed_users:
            return False
        return True

    def _get_text_content(self, message: list) -> str:
        """从CQ消息列表中提取纯文本"""
        parts = []
        for seg in message:
            if seg.get("type") == "text":
                parts.append(seg.get("data", {}).get("text", ""))
            elif seg.get("type") == "image":
                parts.append("[图片]")
            elif seg.get("type") == "at":
                parts.append(f"@{seg.get('data', {}).get('qq', '')} ")
            elif seg.get("type") == "reply":
                parts.append(f"[回复:{seg.get('data', {}).get('id', '')}] ")
        return "".join(parts).strip()

    def _build_cq_message(self, text: str) -> str:
        """将文本转换为CQ码格式消息"""
        safe = unescape_cq(text)
        safe = safe.replace("\n", "\n")
        return safe

    async def send_group_msg(self, group_id: str, text: str):
        """发送群消息"""
        if not self.ws:
            return
        cq = self._build_cq_message(text)
        payload = {
            "action": "send_group_msg",
            "params": {"group_id": int(group_id), "message": cq},
            "echo": f"reply_{datetime.now().timestamp()}",
        }
        await self.ws.send_json(payload)

    async def send_private_msg(self, user_id: str, text: str):
        """发送私聊消息"""
        if not self.ws:
            return
        cq = self._build_cq_message(text)
        payload = {
            "action": "send_private_msg",
            "params": {"user_id": int(user_id), "message": cq},
            "echo": f"reply_{datetime.now().timestamp()}",
        }
        await self.ws.send_json(payload)

    async def handle_private_msg(self, user_id: str, message: list):
        """处理私聊消息"""
        if not self._check_access(None, user_id):
            return

        text = self._get_text_content(message)
        if not text:
            return

        if text.startswith("/start"):
            await self.send_private_msg(user_id,
                "🤖 Claude Code QQ Bot\n\n你好！我是你的Claude Code远程助手。\n\n命令：\n/new - 创建新会话\n/sessions - 查看会话\n/cancel - 取消会话")
            return

        if text.startswith("/new"):
            if not check_permission(user_id, Permission.SESSION_CREATE):
                await self.send_private_msg(user_id, "❌ 权限不足，无法创建会话。")
                return
            if user_id in self.private_sessions:
                sid = self.private_sessions[user_id]
                await self.send_private_msg(user_id, f"⚠️ 当前已有活跃会话 `{sid[:20]}...`，请先 /cancel 后再创建。")
                return
            await self.send_private_msg(user_id, "🆕 正在创建新会话...")
            try:
                result = await self.gateway.create_session(user_id, "qq", f"private:{user_id}", "")
                if result.get("success"):
                    session_id = result["session_id"]
                    self.private_sessions[user_id] = session_id
                    await self.send_private_msg(user_id, f"✅ 会话已创建：\n`{session_id}`")
                    logger.info(f"Session created: {session_id} for user {user_id}")
                else:
                    await self.send_private_msg(user_id, f"❌ 创建失败：{result.get('error', '未知错误')}")
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                await self.send_private_msg(user_id, f"❌ 连接Dragon Gateway失败：{str(e)[:100]}")
            return

        if text.startswith("/sessions"):
            if user_id not in self.private_sessions:
                await self.send_private_msg(user_id, "⚠️ 当前没有活跃会话。")
                return
            sid = self.private_sessions[user_id]
            await self.send_private_msg(user_id, f"📋 会话状态：\nID: `{sid[:20]}...`")
            return

        if text.startswith("/cancel"):
            if not check_permission(user_id, Permission.SESSION_CANCEL):
                await self.send_private_msg(user_id, "❌ 权限不足，无法取消会话。")
                return
            if user_id not in self.private_sessions:
                await self.send_private_msg(user_id, "⚠️ 当前没有活跃会话。")
                return
            session_id = self.private_sessions.pop(user_id)
            await self.send_private_msg(user_id, f"🚫 会话已取消：`{session_id[:20]}...`")
            logger.info(f"Session cancelled: {session_id}")
            return

        if not text.startswith("/"):
            if user_id not in self.private_sessions:
                await self.send_private_msg(user_id, "⚠️ 没有活跃会话，请先发送 /new 创建新会话。")
                return
            if not check_permission(user_id, Permission.SESSION_CREATE):
                await self.send_private_msg(user_id, "❌ 权限不足。")
                return
            session_id = self.private_sessions[user_id]
            await self.send_private_msg(user_id, "⏳ 正在处理...")
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
                    # QQ消息限制500字符，分段发送
                    for i in range(0, min(len(final_response), 500), 500):
                        await self.send_private_msg(user_id, final_response[i:i+500])
                else:
                    await self.send_private_msg(user_id, "✅ 处理完成，无输出。")
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                await self.send_private_msg(user_id, f"❌ 处理失败：{str(e)[:200]}")

    async def handle_group_msg(self, group_id: str, user_id: str, message: list):
        """处理群消息"""
        if not self._check_access(group_id, user_id):
            return

        text = self._get_text_content(message)
        if not text:
            return

        # 群消息需要 @Bot 才处理，或以命令前缀触发
        if not text.startswith("/") and not text.startswith("."):
            return

        if text.startswith("/start"):
            await self.send_group_msg(group_id,
                "🤖 Claude Code QQ Bot\n\n你好！我是你的Claude Code远程助手。\n\n命令：\n/new - 创建新会话\n/sessions - 查看会话\n/cancel - 取消会话")
            return

        if text.startswith("/new"):
            if not check_permission(user_id, Permission.SESSION_CREATE):
                await self.send_group_msg(group_id, "❌ 权限不足，无法创建会话。")
                return
            if group_id in self.active_sessions:
                sid = self.active_sessions[group_id]
                await self.send_group_msg(group_id, f"⚠️ 当前已有活跃会话 `{sid[:20]}...`，请先 /cancel 后再创建。")
                return
            await self.send_group_msg(group_id, "🆕 正在创建新会话...")
            try:
                result = await self.gateway.create_session(user_id, "qq", f"group:{group_id}", "")
                if result.get("success"):
                    session_id = result["session_id"]
                    self.active_sessions[group_id] = session_id
                    await self.send_group_msg(group_id, f"✅ 会话已创建：\n`{session_id}`")
                    logger.info(f"Session created: {session_id} for user {user_id} in group {group_id}")
                else:
                    await self.send_group_msg(group_id, f"❌ 创建失败：{result.get('error', '未知错误')}")
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                await self.send_group_msg(group_id, f"❌ 连接Dragon Gateway失败：{str(e)[:100]}")
            return

        if text.startswith("/sessions"):
            if group_id not in self.active_sessions:
                await self.send_group_msg(group_id, "⚠️ 当前没有活跃会话。")
                return
            sid = self.active_sessions[group_id]
            await self.send_group_msg(group_id, f"📋 会话状态：\nID: `{sid[:20]}...`")
            return

        if text.startswith("/cancel"):
            if not check_permission(user_id, Permission.SESSION_CANCEL):
                await self.send_group_msg(group_id, "❌ 权限不足，无法取消会话。")
                return
            if group_id not in self.active_sessions:
                await self.send_group_msg(group_id, "⚠️ 当前没有活跃会话。")
                return
            session_id = self.active_sessions.pop(group_id)
            await self.send_group_msg(group_id, f"🚫 会话已取消：`{session_id[:20]}...`")
            logger.info(f"Session cancelled: {session_id}")
            return

    async def connect(self):
        """启动WebSocket连接"""
        import websockets

        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        self.running = True
        while self.running:
            try:
                async with websockets.connect(self.ws_url, extra_headers=headers) as ws:
                    self.ws = ws
                    logger.info("Connected to CQHTTP WebSocket")
                    async for raw in ws:
                        try:
                            data = json.loads(raw)
                            await self._handle_cq_event(data)
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await asyncio.sleep(5)

    async def _handle_cq_event(self, data: dict):
        """处理CQHTTP事件"""
        post_type = data.get("post_type", "")
        if post_type == "message":
            sub_type = data.get("sub_type", "")
            message_type = data.get("message_type", "")
            user_id = str(data.get("user_id", ""))
            raw_msg = data.get("raw_message", "")

            # 解析CQ消息
            message = data.get("message", [])
            if isinstance(message, str):
                message = [{"type": "text", "data": {"text": message}}]

            if message_type == "group":
                group_id = str(data.get("group_id", ""))
                await self.handle_group_msg(group_id, user_id, message)
            elif message_type == "private":
                await self.handle_private_msg(user_id, message)


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(description="QQ Platform Adapter (CQHTTP)")
    parser.add_argument("--ws-url", default=os.getenv("CQHTTP_WS_URL", "ws://localhost:8080/cqhttp/ws"),
                        help="CQHTTP WebSocket URL")
    parser.add_argument("--access-token", default=os.getenv("CQHTTP_ACCESS_TOKEN", ""),
                        help="CQHTTP Access Token")
    parser.add_argument("--allowed-groups", default=os.getenv("QQ_ALLOWED_GROUPS", ""),
                        help="Comma-separated allowed group IDs")
    parser.add_argument("--allowed-users", default=os.getenv("QQ_ALLOWED_USERS", ""),
                        help="Comma-separated allowed user IDs")
    parser.add_argument("--admin-users", default=os.getenv("QQ_ADMIN_USERS", ""),
                        help="Comma-separated admin user IDs")
    parser.add_argument("--gateway-host", default=os.getenv("DRAGON_GATEWAY_HOST", "localhost"))
    parser.add_argument("--gateway-port", type=int, default=int(os.getenv("DRAGON_GATEWAY_PORT", "37778")))
    parser.add_argument("--gateway-token", default=os.getenv("DRAGON_GATEWAY_TOKEN", ""))
    args = parser.parse_args()

    groups = [g.strip() for g in args.allowed_groups.split(",") if g.strip()]
    users = [u.strip() for u in args.allowed_users.split(",") if u.strip()]
    admins = [u.strip() for u in args.admin_users.split(",") if u.strip()]

    handler = QQBotHandler(
        ws_url=args.ws_url,
        access_token=args.access_token,
        allowed_groups=groups,
        allowed_users=users,
        admin_users=admins,
        gateway_host=args.gateway_host,
        gateway_port=args.gateway_port,
        gateway_token=args.gateway_token,
    )

    logger.info("QQ adapter starting...")
    print("QQ adapter started. Connecting to CQHTTP WebSocket...")
    asyncio.run(handler.connect())


if __name__ == "__main__":
    main()
