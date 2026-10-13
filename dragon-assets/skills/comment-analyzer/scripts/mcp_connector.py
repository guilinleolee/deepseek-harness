#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP连接器模块
MCP Connector Module

封装MCP Chrome DevTools的调用。
"""

import asyncio
import json
from typing import Dict, Any, List


class MCPConnector:
    """MCP连接器类"""

    def __init__(self):
        """初始化MCP连接器"""
        # MCP工具通过全局上下文自动注入
        # 这里提供统一的调用接口
        pass

    async def open_page(self, url: str) -> Any:
        """
        打开新页面

        Args:
            url: 目标URL

        Returns:
            页面对象
        """
        # 使用MCP Chrome DevTools打开页面
        from mcp__chrome_devtools import new_page

        page_info = await new_page(url=url)

        return page_info

    async def scroll_page(self, page):
        """滚动页面"""
        await self.evaluate_script(
            page,
            "window.scrollTo(0, document.body.scrollHeight)"
        )

    async def evaluate_script(
        self,
        page,
        script: str,
        args: List[Any] = None
    ) -> Any:
        """
        在页面中执行JavaScript

        Args:
            page: 页面对象
            script: JavaScript代码
            args: 参数列表

        Returns:
            执行结果
        """
        from mcp__chrome_devtools import evaluate_script

        if args:
            # 构建函数调用
            func_script = f"({script})({json.dumps(args)})"
        else:
            func_script = f"({script})()"

        result = await evaluate_script(
            uid=page.get("uid"),
            function=func_script
        )

        return result

    async def wait_for_selector(
        self,
        page,
        selector: str,
        timeout: int = 30000
    ):
        """等待选择器出现"""
        # 简化实现：直接等待
        await asyncio.sleep(2)

    async def extract_comments(
        self,
        page,
        selector: str
    ) -> List[Dict]:
        """提取评论数据"""
        script = f"""
        (selector) => {{
            return Array.from(document.querySelectorAll(selector))
                .map((item, index) => ({{
                    id: index,
                    content: item.textContent
                }}));
        }}
        """

        return await self.evaluate_script(page, script, args=[selector])

    async def take_screenshot(
        self,
        page,
        file_path: str
    ):
        """截图（调试用）"""
        from mcp__chrome_devtools import take_screenshot

        await take_screenshot(
            uid=page.get("uid"),
            file_path=file_path
        )
