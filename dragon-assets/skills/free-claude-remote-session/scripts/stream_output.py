#!/usr/bin/env python3
"""
stream_output.py - 流式输出处理器
将 Claude Code 的流式输出转换为各 IM 平台的消息格式
"""

import re
import textwrap
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class StreamChunk:
    """流式输出块"""
    content: str
    chunk_type: str  # text, code, error, tool_use, tool_result, thinking
    language: Optional[str] = None  # for code blocks


class BaseFormatter(ABC):
    """各平台格式化器的基类"""

    MAX_LENGTH = 4000  # 默认最大消息长度
    TRUNCATE_MARKER = "\n\n...**[截断，请使用 /logs 查看完整输出]**"

    @abstractmethod
    def format_text(self, text: str, bold: bool = False, italic: bool = False) -> str:
        """格式化纯文本"""
        pass

    @abstractmethod
    def format_code(self, code: str, language: str = "") -> str:
        """格式化代码块"""
        pass

    @abstractmethod
    def format_error(self, error: str) -> str:
        """格式化错误信息"""
        pass

    @abstractmethod
    def format_tool(self, tool_name: str, description: str) -> str:
        """格式化工具调用"""
        pass

    def truncate(self, text: str) -> str:
        """截断超长文本"""
        if len(text) <= self.MAX_LENGTH:
            return text
        return text[:self.MAX_LENGTH - len(self.TRUNCATE_MARKER)] + self.TRUNCATE_MARKER

    def wrap_text(self, text: str, width: int = 80) -> str:
        """自动换行"""
        lines = []
        for line in text.split("\n"):
            if len(line) <= width:
                lines.append(line)
            else:
                wrapped = textwrap.wrap(line, width=width)
                lines.extend(wrapped if wrapped else [line])
        return "\n".join(lines)


class TelegramFormatter(BaseFormatter):
    """Telegram MarkdownV2 格式化器"""

    # Telegram MarkdownV2 转义
    ESCAPE_CHARS = re.compile(r'([_*\[\]`~>#+\-|{}.!\\])')

    def escape(self, text: str) -> str:
        """转义特殊字符"""
        return self.ESCAPE_CHARS.sub(r'\\\1', text)

    def format_text(self, text: str, bold: bool = False, italic: bool = False) -> str:
        text = self.escape(text)
        text = self.wrap_text(text)
        if bold:
            text = f"*{text}*"
        if italic:
            text = f"_{text}_"
        return text

    def format_code(self, code: str, language: str = "") -> str:
        lang = language or "plaintext"
        # Telegram 使用 ```language\ncode```
        escaped = self.escape(code)
        return f"```{lang}\n{escaped}\n```"

    def format_error(self, error: str) -> str:
        escaped = self.escape(error)
        return f"🔴 *ERROR:* _{escaped}_"

    def format_tool(self, tool_name: str, description: str) -> str:
        name = self.escape(tool_name)
        desc = self.escape(description)
        return f"🔧 *Tool:* `{name}`\n_{desc}_"


class DiscordFormatter(BaseFormatter):
    """Discord Markdown 格式化器"""

    MAX_LENGTH = 2000  # Discord 限制

    def escape(self, text: str) -> str:
        """转义特殊字符"""
        for char in ["*", "_", "~", "`", "||"]:
            text = text.replace(char, "\\" + char)
        return text

    def format_text(self, text: str, bold: bool = False, italic: bool = False) -> str:
        text = self.escape(text)
        text = self.wrap_text(text)
        if bold:
            text = f"**{text}**"
        if italic:
            text = f"*{text}*"
        return text

    def format_code(self, code: str, language: str = "") -> str:
        lang = language or "plaintext"
        escaped = self.escape(code)
        return f"```{lang}\n{escaped}\n```"

    def format_error(self, error: str) -> str:
        escaped = self.escape(error)
        return f"🔴 **ERROR:** {escaped}"

    def format_tool(self, tool_name: str, description: str) -> str:
        name = self.escape(tool_name)
        desc = self.escape(description)
        return f"🔧 **Tool:** `{name}`\n{desc}"


class FeishuFormatter(BaseFormatter):
    """飞书消息卡片格式化器"""

    MAX_LENGTH = 4000

    def format_text(self, text: str, bold: bool = False, italic: bool = False) -> str:
        text = self.wrap_text(text)
        if bold:
            text = f"*{text}*"
        if italic:
            text = f"_{text}_"
        return text

    def format_code(self, code: str, language: str = "") -> str:
        # 飞书支持 markdown 代码块
        lang = language or "plaintext"
        return f"```{lang}\n{code}\n```"

    def format_error(self, error: str) -> str:
        return f"🔴 *ERROR:* {error}"

    def format_tool(self, tool_name: str, description: str) -> str:
        return f"🔧 *Tool:* `{tool_name}`\n_{description}_"

    def make_card(self, content: str, msg_type: str = "interactive") -> dict:
        """生成飞书消息卡片"""
        return {
            "msg_type": msg_type,
            "card": {
                "config": {"wide_screen_mode": True},
                "elements": [
                    {"tag": "markdown", "content": content}
                ]
            }
        }


class QQFormatter(BaseFormatter):
    """QQ CQ码格式化器"""

    MAX_LENGTH = 500  # CQ码消息较短

    def escape(self, text: str) -> str:
        """转义 CQ 码特殊字符"""
        text = text.replace("&", "&amp;")
        text = text.replace("[", "&#91;")
        text = text.replace("]", "&#93;")
        return text

    def format_text(self, text: str, bold: bool = False, italic: bool = False) -> str:
        text = self.wrap_text(text, width=60)
        if bold:
            text = f"[bold]{text}[/bold]"
        if italic:
            text = f"[italic]{text}[/italic]"
        return self.escape(text)

    def format_code(self, code: str, language: str = "") -> str:
        escaped = self.escape(code)
        return f"[CQ:code,text={escaped}]"

    def format_error(self, error: str) -> str:
        return f"[CQ:at,qq=all] 🔴 ERROR: {self.escape(error)}"

    def format_tool(self, tool_name: str, description: str) -> str:
        return f"🔧 {tool_name}: {self.escape(description)}"


# ============ 工厂函数 ============
def get_formatter(platform: str) -> BaseFormatter:
    """根据平台获取格式化器"""
    formatters = {
        "telegram": TelegramFormatter,
        "discord": DiscordFormatter,
        "feishu": FeishuFormatter,
        "qq": QQFormatter,
    }
    formatter_class = formatters.get(platform, TelegramFormatter)
    return formatter_class()


# ============ 流式处理器 ============
class StreamProcessor:
    """流式输出处理器"""

    def __init__(self, platform: str):
        self.formatter = get_formatter(platform)
        self.platform = platform

    def process_chunk(self, chunk: StreamChunk) -> str:
        """处理单个流式块"""
        if chunk.chunk_type == "text":
            return self.formatter.format_text(chunk.content)
        elif chunk.chunk_type == "code":
            return self.formatter.format_code(chunk.content, chunk.language or "")
        elif chunk.chunk_type == "error":
            return self.formatter.format_error(chunk.content)
        elif chunk.chunk_type == "tool_use":
            return self.formatter.format_tool(chunk.content, "")
        elif chunk.chunk_type == "tool_result":
            return self.formatter.format_text(chunk.content)
        elif chunk.chunk_type == "thinking":
            # 思考过程默认不输出，或用斜体
            return self.formatter.format_text(f"[思考] {chunk.content}", italic=True)
        return chunk.content

    def process_stream(self, chunks: list[StreamChunk]) -> list[str]:
        """处理流式输出列表，返回消息片段列表"""
        messages = []
        current = ""

        for chunk in chunks:
            formatted = self.process_chunk(chunk)

            # 如果加上这个块会超长，先发送当前的
            if len(current) + len(formatted) > self.formatter.MAX_LENGTH:
                if current:
                    messages.append(self.formatter.truncate(current))
                current = formatted
            else:
                current += "\n" + formatted

        if current:
            messages.append(self.formatter.truncate(current))

        return messages

    def format_progress(self, current: int, total: int, description: str = "") -> str:
        """格式化进度消息"""
        percent = int(current / total * 100) if total > 0 else 0
        bar = "█" * (percent // 5) + "░" * (20 - percent // 5)

        if description:
            text = f"⏳ [{bar}] {percent}% - {description}"
        else:
            text = f"⏳ [{bar}] {percent}%"

        if self.platform == "feishu":
            return self.formatter.make_card(self.formatter.format_text(text))
        return text
