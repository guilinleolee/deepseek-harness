#!/usr/bin/env python3
"""
discord_adapter.py - Discord平台适配器
将Discord消息转换为Dragon Gateway协议并路由到Claude Code会话
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
        logging.FileHandler(LOG_DIR / "discord.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("discord_adapter")


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


class DiscordBotHandler:
    """Discord Bot消息处理器"""

    def __init__(self, token: str, allowed_guilds: list[str], allowed_channels: list[str],
                 admin_roles: list[str], gateway_host: str = "localhost",
                 gateway_port: int = 37778, gateway_token: str = "", session_timeout: int = 3600):
        import discord
        from discord import app_commands

        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        intents.guilds = True

        self.token = token
        self.allowed_guilds = set(allowed_guilds)
        self.allowed_channels = set(allowed_channels)
        self.admin_roles = set(admin_roles)
        self.gateway = DragonGatewayClient(gateway_host, gateway_port, gateway_token)
        self.session_timeout = session_timeout
        self.processor = StreamProcessor("discord")
        self.permission_checker = PermissionChecker()
        self.bot: Optional[discord.Client] = None

        self.active_sessions: dict[str, str] = {}
        for uid in admin_roles:
            self.permission_checker.set_user_role(f"role:{uid}", "admin")

    def _check_access(self, guild_id: int, channel_id: int, user_id: int, roles: list[str]) -> bool:
        """检查用户是否有访问权限"""
        if self.allowed_guilds and str(guild_id) not in self.allowed_guilds:
            return False
        if self.allowed_channels and str(channel_id) not in self.allowed_channels:
            return False
        return True

    def _check_admin(self, roles: list[str]) -> bool:
        """检查用户是否有管理员权限"""
        return any(role in self.admin_roles for role in roles)

    async def setup_tree(self, tree: "app_commands.CommandTree"):
        """设置slash命令"""

        @tree.command(name="start", description="启动Claude Code Bot")
        async def start_command(interaction: "discord.Interaction"):
            guild_id = interaction.guild_id
            channel_id = interaction.channel_id
            user_id = interaction.user.id
            roles = [r.name for r in interaction.user.roles] if interaction.user.roles else []

            if not self._check_access(guild_id, channel_id, user_id, roles):
                await interaction.response.send_message("❌ 访问被拒绝。请联系管理员授权。", ephemeral=True)
                return

            welcome = "🤖 **Claude Code Discord Bot**\n\n你好！我是你的Claude Code远程助手。\n\n**可用命令：**\n`/new` - 创建新会话\n`/sessions` - 查看当前会话\n`/cancel` - 取消当前会话\n`/status` - 查看状态\n\n直接发送消息即可开始对话！"
            await interaction.response.send_message(welcome, ephemeral=True)

        @tree.command(name="new", description="创建新Claude Code会话")
        async def new_command(interaction: "discord.Interaction"):
            guild_id = interaction.guild_id
            channel_id = interaction.channel_id
            user_id = interaction.user.id
            roles = [r.name for r in interaction.user.roles] if interaction.user.roles else []
            key = f"{guild_id}:{channel_id}"

            if not self._check_access(guild_id, channel_id, user_id, roles):
                await interaction.response.send_message("❌ 访问被拒绝。", ephemeral=True)
                return

            if not check_permission(str(user_id), Permission.SESSION_CREATE):
                await interaction.response.send_message("❌ 权限不足，无法创建会话。", ephemeral=True)
                return

            if key in self.active_sessions:
                sid = self.active_sessions[key]
                await interaction.response.send_message(f"⚠️ 当前已有活跃会话 `{sid[:20]}...`，请先 /cancel 后再创建。", ephemeral=True)
                return

            await interaction.response.send_message("🆕 正在创建新会话...", ephemeral=True)
            try:
                result = await self.gateway.create_session(str(user_id), "discord", f"{guild_id}:{channel_id}", "")
                if result.get("success"):
                    session_id = result["session_id"]
                    self.active_sessions[key] = session_id
                    await interaction.edit_original_response(content=f"✅ 会话已创建：\n`{session_id}`")
                    logger.info(f"Session created: {session_id} for user {user_id}")
                else:
                    await interaction.edit_original_response(content=f"❌ 创建失败：{result.get('error', '未知错误')}")
            except Exception as e:
                logger.error(f"Failed to create session: {e}")
                await interaction.edit_original_response(content=f"❌ 连接Dragon Gateway失败：{str(e)[:100]}")

        @tree.command(name="sessions", description="查看当前会话状态")
        async def sessions_command(interaction: "discord.Interaction"):
            guild_id = interaction.guild_id
            channel_id = interaction.channel_id
            user_id = interaction.user.id
            key = f"{guild_id}:{channel_id}"

            if not self._check_access(guild_id, channel_id, user_id, []):
                await interaction.response.send_message("❌ 访问被拒绝。", ephemeral=True)
                return

            if key not in self.active_sessions:
                await interaction.response.send_message("⚠️ 当前没有活跃会话。", ephemeral=True)
                return

            sid = self.active_sessions[key]
            await interaction.response.send_message(f"📋 会话状态：\nID: `{sid[:20]}...`\n状态: 运行中", ephemeral=True)

        @tree.command(name="cancel", description="取消当前会话")
        async def cancel_command(interaction: "discord.Interaction"):
            guild_id = interaction.guild_id
            channel_id = interaction.channel_id
            user_id = interaction.user.id
            key = f"{guild_id}:{channel_id}"

            if not self._check_access(guild_id, channel_id, user_id, []):
                await interaction.response.send_message("❌ 访问被拒绝。", ephemeral=True)
                return

            if not check_permission(str(user_id), Permission.SESSION_CANCEL):
                await interaction.response.send_message("❌ 权限不足，无法取消会话。", ephemeral=True)
                return

            if key not in self.active_sessions:
                await interaction.response.send_message("⚠️ 当前没有活跃会话。", ephemeral=True)
                return

            session_id = self.active_sessions.pop(key)
            await interaction.response.send_message(f"🚫 会话已取消：`{session_id[:20]}...`", ephemeral=True)
            logger.info(f"Session cancelled: {session_id}")

        @tree.command(name="status", description="查看平台状态")
        async def status_command(interaction: "discord.Interaction"):
            await interaction.response.send_message(
                f"✅ **Dragon Gateway连接状态**\n"
                f"Gateway: {self.gateway.base_url}\n"
                f"活跃会话数: {len(self.active_sessions)}",
                ephemeral=True
            )


def main():
    """主入口"""
    import argparse
    import discord
    from discord import app_commands

    parser = argparse.ArgumentParser(description="Discord Platform Adapter")
    parser.add_argument("--token", default=os.getenv("DISCORD_BOT_TOKEN"), help="Discord Bot Token")
    parser.add_argument("--allowed-guilds", default=os.getenv("DISCORD_ALLOWED_GUILDS", ""),
                        help="Comma-separated allowed guild IDs")
    parser.add_argument("--allowed-channels", default=os.getenv("DISCORD_ALLOWED_CHANNELS", ""),
                        help="Comma-separated allowed channel IDs")
    parser.add_argument("--admin-roles", default=os.getenv("DISCORD_ADMIN_ROLES", ""),
                        help="Comma-separated admin role names")
    parser.add_argument("--gateway-host", default=os.getenv("DRAGON_GATEWAY_HOST", "localhost"))
    parser.add_argument("--gateway-port", type=int, default=int(os.getenv("DRAGON_GATEWAY_PORT", "37778")))
    parser.add_argument("--gateway-token", default=os.getenv("DRAGON_GATEWAY_TOKEN", ""))
    args = parser.parse_args()

    if not args.token:
        logger.error("DISCORD_BOT_TOKEN is required")
        sys.exit(1)

    guilds = [g.strip() for g in args.allowed_guilds.split(",") if g.strip()]
    channels = [c.strip() for c in args.allowed_channels.split(",") if c.strip()]
    admin_roles = [r.strip() for r in args.admin_roles.split(",") if r.strip()]

    handler = DiscordBotHandler(
        token=args.token,
        allowed_guilds=guilds,
        allowed_channels=channels,
        admin_roles=admin_roles,
        gateway_host=args.gateway_host,
        gateway_port=args.gateway_port,
        gateway_token=args.gateway_token,
    )

    intents = discord.Intents.default()
    intents.message_content = True
    intents.messages = True
    intents.guilds = True

    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)

    async def setup():
        await client.login(args.token)
        await handler.setup_tree(tree)
        await tree.sync()
        logger.info("Discord adapter starting...")

    async def on_message(message: discord.Message):
        if message.author.bot:
            return
        guild_id = message.guild.id if message.guild else 0
        channel_id = message.channel.id
        user_id = message.author.id
        key = f"{guild_id}:{channel_id}"

        if not handler._check_access(guild_id, channel_id, user_id, []):
            return

        if not check_permission(str(user_id), Permission.SESSION_CREATE):
            await message.channel.send("❌ 权限不足。")
            return

        if key not in handler.active_sessions:
            await message.channel.send("⚠️ 没有活跃会话，请先发送 `/new` 创建新会话。")
            return

        session_id = handler.active_sessions[key]
        await message.channel.send("⏳ 正在处理...")

        try:
            await handler.gateway.send_message(session_id, message.content)

            response_parts = []
            async for event_line in handler.gateway.stream_events(session_id):
                if event_line.startswith("data:"):
                    data = json.loads(event_line[5:])
                    chunk = StreamChunk(
                        content=data.get("content", ""),
                        chunk_type=data.get("type", "text"),
                        language=data.get("language"),
                    )
                    formatted = handler.processor.process_chunk(chunk)
                    response_parts.append(formatted)

                    if len(response_parts) % 5 == 0:
                        partial = "\n".join(response_parts[-5:])
                        try:
                            await message.channel.send(partial[:2000])
                        except Exception:
                            pass

            final_response = "\n".join(response_parts)
            if final_response:
                final_response = handler.processor.formatter.truncate(final_response)
                await message.channel.send(final_response[:2000])
            else:
                await message.channel.send("✅ 处理完成，无输出。")

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await message.channel.send(f"❌ 处理失败：{str(e)[:200]}")

    @client.event
    async def on_ready():
        await setup()
        print(f"Discord adapter started. Logged in as {client.user}")

    @client.event
    async def on_message_event(message):
        await on_message(message)

    client.run(args.token)


if __name__ == "__main__":
    main()
