#!/usr/bin/env python3
"""
Pixelle-Video ComfyUI API Client
天龙引擎视频生成五引擎架构 - Pixelle-Video封装
"""

import requests
import json
import time
import os
from typing import Optional, Dict, Any, List


class PixelleClient:
    """Pixelle-Video ComfyUI API客户端"""

    def __init__(
        self,
        base_url: str = "http://localhost:8188",
        timeout: int = 300
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统状态"""
        try:
            resp = self.session.get(f"{self.base_url}/api/system_stats", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e), "status": "offline"}

    def get_models(self) -> List[str]:
        """获取可用模型列表"""
        try:
            resp = self.session.get(f"{self.base_url}/api/models", timeout=10)
            resp.raise_for_status()
            return resp.json().get("models", [])
        except Exception as e:
            return []

    def queue_prompt(self, prompt: Dict[str, Any]) -> Optional[str]:
        """提交任务到队列，返回prompt_id"""
        try:
            resp = self.session.post(
                f"{self.base_url}/prompt",
                json={"prompt": prompt},
                timeout=self.timeout
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("prompt_id")
        except Exception as e:
            print(f"[PixelleClient] 提交任务失败: {e}")
            return None

    def get_history(self, prompt_id: str) -> Dict[str, Any]:
        """获取任务执行历史"""
        try:
            resp = self.session.get(
                f"{self.base_url}/history/{prompt_id}",
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {}

    def get_output_images(self, prompt_id: str) -> List[str]:
        """获取输出图片URL列表"""
        history = self.get_history(prompt_id)
        images = []
        for node_id, node_data in history.items():
            if "images" in node_data:
                for img in node_data["images"]:
                    images.append(
                        f"{self.base_url}/view?filename={img['filename']}&type={img['type']}"
                    )
        return images

    def get_output_audio(self, prompt_id: str) -> Optional[str]:
        """获取输出音频URL"""
        history = self.get_history(prompt_id)
        for node_id, node_data in history.items():
            if "audio" in node_data:
                audio = node_data["audio"]
                return f"{self.base_url}/view?filename={audio['filename']}&type={audio['type']}"
        return None

    def wait_for_completion(
        self,
        prompt_id: str,
        poll_interval: int = 2,
        max_wait: int = 600
    ) -> Dict[str, Any]:
        """等待任务完成"""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            history = self.get_history(prompt_id)
            if prompt_id in history:
                status = history[prompt_id].get("status", "running")
                if status == "success":
                    return {"status": "success", "history": history}
                elif status == "failed":
                    return {"status": "failed", "history": history}
            time.sleep(poll_interval)
        return {"status": "timeout", "history": {}}

    def interrupt(self) -> bool:
        """中断当前任务"""
        try:
            resp = self.session.post(f"{self.base_url}/interrupt", timeout=10)
            resp.raise_for_status()
            return True
        except Exception:
            return False

    def generate_video(
        self,
        workflow: str = "full-auto",
        topic: str = "",
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """快捷生成视频"""
        params = params or {}

        # 加载工作流模板
        workflow_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "workflows",
            f"{workflow}.json"
        )

        if not os.path.exists(workflow_path):
            print(f"[PixelleClient] 工作流文件不存在: {workflow_path}")
            return None

        with open(workflow_path, "r", encoding="utf-8") as f:
            workflow_data = json.load(f)

        # 替换主题参数
        prompt = workflow_data.get("prompt", {})

        # 提交任务
        prompt_id = self.queue_prompt(prompt)
        if prompt_id:
            print(f"[PixelleClient] 任务已提交: {prompt_id}")
        return prompt_id


def main():
    """CLI入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Pixelle-Video ComfyUI API Client")
    parser.add_argument("--url", default="http://localhost:8188", help="ComfyUI服务器地址")
    parser.add_argument("--action", choices=["status", "models", "generate", "interrupt"], default="status")

    args = parser.parse_args()
    client = PixelleClient(base_url=args.url)

    if args.action == "status":
        stats = client.get_system_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))

    elif args.action == "models":
        models = client.get_models()
        print("可用模型:")
        for m in models:
            print(f"  - {m}")

    elif args.action == "interrupt":
        if client.interrupt():
            print("已发送中断信号")
        else:
            print("中断失败")


if __name__ == "__main__":
    main()
