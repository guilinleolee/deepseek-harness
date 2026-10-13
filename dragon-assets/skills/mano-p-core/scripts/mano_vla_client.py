"""
Mano-P GUI-VLA Client for 天龙引擎
支持本地GUI-VLA推理和无API跨系统集成
"""

import httpx
import asyncio
from typing import Optional, Dict, Any
import base64
import json

class ManoPVLAClient:
    """Mano-P GUI-VLA客户端"""

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=120.0)

    async def execute_task(self, task: str, screenshot: Optional[bytes] = None) -> Dict[str, Any]:
        """执行GUI任务"""
        payload = {
            "task": task,
            "think_act_verify": True,  # 启用三阶段循环
            "max_steps": 100,  # 长任务支持数百步
        }

        if screenshot:
            payload["screenshot"] = base64.b64encode(screenshot).decode()

        response = await self.client.post(f"{self.base_url}/api/v1/execute", json=payload)
        return response.json()

    async def cross_system_extract(self, source_app: str, target_format: str) -> Dict[str, Any]:
        """无API跨系统数据提取"""
        payload = {
            "mode": "cross_system_extract",
            "source": source_app,
            "target": target_format,
            "no_api_mode": True,  # 纯GUI操作
        }

        response = await self.client.post(f"{self.base_url}/api/v1/cross_system", json=payload)
        return response.json()

    async def close(self):
        await self.client.aclose()


# 天龙引擎集成接口
async def mano_vla_execute(task: str, **kwargs) -> Dict[str, Any]:
    """天龙引擎统一调用接口"""
    client = ManoPVLAClient()
    try:
        result = await client.execute_task(task, **kwargs)
        return result
    finally:
        await client.close()