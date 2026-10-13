#!/usr/bin/env python3
"""
telegram_adapter.py - Telegram平台适配器
将Telegram消息转换为Dragon Gateway协议并路由到Claude Code会话
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 添加父目录到路径以便导入共享模块
sys.path.insert(0, str(Path(__file__).parent.parent))
from permission_checker import PermissionChecker, Permission, check_permission, require_permission
from stream_output import get_formatter, StreamProcessor, StreamChunk

# 配置日志
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "telegram.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("telegram_adapter")


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

    async def get_session_status(self, session_id: str) -> dict:
        """获取会话状态"""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/api/session/{session_id}",
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


# ============ Telegram Bot Handler ============
class TelegramBotHandler:
    """Telegram Bot消息处理器"""

    def __init__(self, token: str, allowed_users: list[str], admin_users: list[str],
                 gateway_host: str = "localhost", gateway_port: int = 37778,
                 gateway_token: str = "", session_timeout: int = 3600):
        from telegram import Update, Bot
        from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

        self.token = token
        self.allowed_users = set(allowed_users)
        self.admin_users = set(admin_users)
        self.gateway = DragonGatewayClient(gateway_host, gateway_port, gateway_token)
        self.session_timeout = session_timeout
        self.processor = StreamProcessor("telegram")
        self.permission_checker = PermissionChecker()
        self.bot: Optional[Bot] = None

        # 用户会话映射: telegram_chat_id -> session_id
        self.active_sessions: dict[str, str] = {}
        # 用户角色初始化
        for uid in self.admin_users:
            self.permission_checker.set_user_role(uid, "admin")
        for uid in self.allowed_users:
            if uid not in self.admin_users:
                self.permission_checker.set_user_role(uid, "user")

    def _check_access(self, user_id: str) -> bool:
        """检查用户是否有访问权限"""
        return user_id in self.allowed_users

    async def start_command(self, update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        """处理 /start 命令"""
        user_id = str(update.effective_user.id)
        if not self._check_access(user_id):
            await update.message.reply_text("❌ 访问被拒绝。请联系管理员授权。")
            return

        welcome = """🤖 *Claude Code Telegram Bot*

你好！我是你的Claude Code远程助手。

*可用命令：*
/new - 创建新会话
/list - 查看所有会话
/session - 查看当前会话状态
/cancel - 取消当前会话
/help - 显示帮助

直接发送消息即可开始对话！"""
        await update.message.reply_text(welcome, parse_mode="MarkdownV2")

    async def help_command(self, update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        """处理 /help 命令"""
        user_id = str(update.effective_user.id)
        if not self._check_access(user_id):
            await update.message.reply_text("❌ 访问被拒绝。")
            return

        help_text = """📖 *帮助*

*基本命令：*
/new \- 创建新会话
/list \- 查看所有会话
/session \- 查看当前会话
/cancel \- 取消当前会话
/logs [n] \- 查看最近n行日志
/status \- 查看平台状态

*权限说明：*
普通用户：可创建会话、执行代码、写入文件
只读用户：仅可查看会话和日志
管理员：全部权限，包括危险操作"""
        await update.message.reply_text(help_text, parse_mode="MarkdownV2")

    async def new_session(self, update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        """处理 /new 命令"""
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)

        if not self._check_access(user_id):
            await update.message.reply_text("❌ 访问被拒绝。")
            return

        if not check_permission(user_id, Permission.SESSION_CREATE):
            reason = self.permission_checker.check(user_id, Permission.SESSION_CREATE).reason
            await update.message.reply_text(f"❌ {reason}")
            return

        # 检查是否已有活跃会话
        if chat_id in self.active_sessions:
            sid = self.active_sessions[chat_id]
            await update.message.reply_text(f"⚠️ 当前已有活跃会话 `{sid[:20]}...`，请先 /cancel 后再创建新会话。")
            return

        await update.message.reply_text("🆕 正在创建新会话...")
        try:
            result = await self.gateway.create_session(user_id, "telegram", chat_id, "")
            if result.get("success"):
                session_id = result["session_id"]
                self.active_sessions[chat_id] = session_id
                await update.message.reply_text(f"✅ 会话已创建：\n`{session_id}`")
                logger.info(f"Session created: {session_id} for user {user_id}")
            else:
                await update.message.reply_text(f"❌ 创建失败：{result.get('error', '未知错误')}")
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            await update.message.reply_text(f"❌ 连接Dragon Gateway失败：{str(e)[:100]}")

    async def list_sessions(self, update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        """处理 /list 命令"""
        user_id = str(update.effective_user.id)
        if not self._check_access(user_id):
            await update.message.reply_text("❌ 访问被拒绝。")
            return

        if not check_permission(user_id, Permission.SESSION_READ):
            await update.message.reply_text("❌ 权限不足，无法查看会话。")
            return

        await update.message.reply_text("📋 加载会话列表...")
        # TODO: 调用Dragon Gateway获取会话列表
        await update.message.reply_text("⚠️ 会话列表功能开发中")

    async def cancel_session(self, update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        """处理 /cancel 命令"""
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)

        if not self._check_access(user_id):
            await update.message.reply_text("❌ 访问被拒绝。")
            return

        if not check_permission(user_id, Permission.SESSION_CANCEL):
            await update.message.reply_text("❌ 权限不足，无法取消会话。")
            return

        if chat_id not in self.active_sessions:
            await update.message.reply_text("⚠️ 当前没有活跃会话。")
            return

        session_id = self.active_sessions[chat_id]
        del self.active_sessions[chat_id]
        await update.message.reply_text(f"🚫 会话已取消：`{session_id[:20]}...`")
        logger.info(f"Session cancelled: {session_id}")

    async def handle_message(self, update: "Update", context: "ContextTypes.DEFAULT_TYPE"):
        """处理普通文本消息"""
        user_id = str(update.effective_user.id)
        chat_id = str(update.effective_chat.id)
        text = update.message.text

        if not self._check_access(user_id):
            await update.message.reply_text("❌ 访问被拒绝。")
            return

        # 忽略命令消息
        if text.startswith("/"):
            return

        # 检查是否有活跃会话
        if chat_id not in self.active_sessions:
            await update.message.reply_text("⚠️ 没有活跃会话，请先发送 /new 创建新会话。")
            return

        session_id = self.active_sessions[chat_id]

        # 权限检查
        require_permission(user_id, Permission.SESSION_CREATE)

        # 发送等待消息
        status_msg = await update.message.reply_text("⏳ 正在处理...")

        try:
            # 发送到Dragon Gateway
            await self.gateway.send_message(session_id, text)

            # 收集流式响应
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

                    # 分段发送（避免消息过长）
                    if len(response_parts) % 5 == 0:
                        partial = "\n".join(response_parts[-5:])
                        try:
                            await status_msg.edit_text(partial[:4000])
                        except Exception:
                            pass

            # 发送最终响应
            final_response = "\n".join(response_parts)
            if final_response:
                final_response = self.processor.formatter.truncate(final_response)
                await status_msg.edit_text(final_response)
            else:
                await status_msg.edit_text("✅ 处理完成，无输出。")

        except PermissionDeniedError as e:
            await status_msg.edit_text(f"❌ {str(e)}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await status_msg.edit_text(f"❌ 处理失败：{str(e)[:200]}")


# ============ 主入口 ============
def main():
    """主入口"""
    import argparse
    from telegram import Bot
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

    parser = argparse.ArgumentParser(description="Telegram Platform Adapter")
    parser.add_argument("--token", default=os.getenv("TELEGRAM_BOT_TOKEN"), help="Telegram Bot Token")
    parser.add_argument("--allowed-users", default=os.getenv("TELEGRAM_ALLOWED_USERS", ""),
                        help="Comma-separated allowed user IDs")
    parser.add_argument("--admin-users", default=os.getenv("TELEGRAM_ADMIN_USERS", ""),
                        help="Comma-separated admin user IDs")
    parser.add_argument("--gateway-host", default=os.getenv("DRAGON_GATEWAY_HOST", "localhost"))
    parser.add_argument("--gateway-port", type=int, default=int(os.getenv("DRAGON_GATEWAY_PORT", "37778")))
    parser.add_argument("--gateway-token", default=os.getenv("DRAGON_GATEWAY_TOKEN", ""))
    args = parser.parse_args()

    if not args.token:
        logger.error("TELEGRAM_BOT_TOKEN is required")
        sys.exit(1)

    allowed = [u.strip() for u in args.allowed_users.split(",") if u.strip()]
    admins = [u.strip() for u in args.admin_users.split(",") if u.strip()]

    handler = TelegramBotHandler(
        token=args.token,
        allowed_users=allowed,
        admin_users=admins,
        gateway_host=args.gateway_host,
        gateway_port=args.gateway_port,
        gateway_token=args.gateway_token,
    )

    app = Application.builder().token(args.token).build()

    # 注册命令处理器
    app.add_handler(CommandHandler("start", handler.start_command))
    app.add_handler(CommandHandler("help", handler.help_command))
    app.add_handler(CommandHandler("new", handler.new_session))
    app.add_handler(CommandHandler("list", handler.list_sessions))
    app.add_handler(CommandHandler("cancel", handler.cancel_session))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler.handle_message))

    logger.info("Telegram adapter starting...")
    print("Telegram adapter started. Bot is polling for messages.")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
