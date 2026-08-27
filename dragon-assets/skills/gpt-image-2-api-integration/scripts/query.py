#!/usr/bin/env python3
"""
GPT-Image-2 API Integration Query Script
EvoLink/Gateway多后端API调用封装
"""

import json
import os
import argparse
import subprocess
from pathlib import Path

# 默认API配置
DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "backends.json")


class ImageAPI:
    """GPT-Image-2 API集成管理器"""

    def __init__(self, data_path: str = None):
        self.data_path = data_path or DEFAULT_DATA_PATH
        self._load_data()
        self._check_env()

    def _load_data(self):
        """加载后端配置"""
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = self._get_builtin_config()

    def _get_builtin_config(self):
        """内置后端配置"""
        return {
            "backends": [
                {
                    "id": "evolink",
                    "name": "EvoLink API",
                    "endpoint": "https://api.evolink.ai/v1/images/generations",
                    "quota_note": "需申请额度",
                    "features": ["gpt-image-2", "flux-3", "dall-e-3"],
                    "cost": "中"
                },
                {
                    "id": "openai",
                    "name": "OpenAI 官方",
                    "endpoint": "https://api.openai.com/v1/images/generations",
                    "quota_note": "付费使用",
                    "features": ["dall-e-3"],
                    "cost": "高"
                },
                {
                    "id": "gateway",
                    "name": "Gateway 中转",
                    "endpoint": "https://gateway.evolink.ai/v1/images/generations",
                    "quota_note": "按量计费",
                    "features": ["gpt-image-2"],
                    "cost": "低"
                }
            ]
        }

    def _check_env(self):
        """检查环境变量配置"""
        self.evolink_key = os.getenv("EVOLINK_API_KEY", "")
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.gateway_key = os.getenv("GATEWAY_API_KEY", "")

    def status(self) -> dict:
        """检查各后端状态"""
        backends = self.data.get("backends", [])
        results = []

        for backend in backends:
            key_name = f"{backend['id'].upper()}_API_KEY"
            has_key = bool(getattr(self, f"{backend['id']}_key", ""))
            results.append({
                "id": backend["id"],
                "name": backend["name"],
                "configured": has_key,
                "features": backend["features"],
                "cost": backend["cost"]
            })

        return {"backends": results, "total": len(results)}

    def generate(self, prompt: str, model: str = "gpt-image-2",
                 backend: str = "evolink", **kwargs) -> dict:
        """生成图像"""
        backends = {b["id"]: b for b in self.data.get("backends", [])}
        if backend not in backends:
            return {"error": f"未知后端: {backend}"}

        config = backends[backend]
        key = getattr(self, f"{backend}_key", "")

        if not key:
            return {
                "error": f"未配置API Key",
                "hint": f"请设置 {backend.upper()}_API_KEY 环境变量",
                "backend": backend
            }

        # 构建请求参数
        params = {
            "model": model,
            "prompt": prompt,
            "n": kwargs.get("n", 1),
            "size": kwargs.get("size", "1024x1024"),
            "quality": kwargs.get("quality", "standard"),
            "response_format": kwargs.get("response_format", "url")
        }

        # 尝试CLI调用
        try:
            cmd = [
                "npx", "evolink-gpt-image",
                prompt,
                "--model", model,
                "--backend", backend
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                return {"success": True, "output": result.stdout, "backend": backend}
            else:
                return {"error": result.stderr, "backend": backend}
        except FileNotFoundError:
            return {
                "error": "npx不可用，请安装: npm install -g evolink-gpt-image",
                "fallback": "可使用curl直接调用API",
                "params": params,
                "endpoint": config["endpoint"]
            }
        except Exception as e:
            return {"error": str(e), "backend": backend}

    def list_models(self, backend: str = None) -> list:
        """列出可用模型"""
        backends = self.data.get("backends", [])
        if backend:
            backends = [b for b in backends if b["id"] == backend]
        return [{"id": b["id"], "name": b["name"], "models": b["features"]} for b in backends]


def main():
    parser = argparse.ArgumentParser(description="GPT-Image-2 API集成工具")
    parser.add_argument("--status", action="store_true", help="检查后端配置状态")
    parser.add_argument("--generate", "-y", help="生成图像提示词")
    parser.add_argument("--model", default="gpt-image-2",
                        choices=["gpt-image-2", "flux-3", "dall-e-3"])
    parser.add_argument("--backend", default="evolink",
                        choices=["evolink", "openai", "gateway"])
    parser.add_argument("--size", default="1024x1024",
                        choices=["1024x1024", "1536x1024", "1024x1536"])
    parser.add_argument("--n", type=int, default=1, help="生成数量")
    parser.add_argument("--list-models", action="store_true", help="列出可用模型")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")

    args = parser.parse_args()

    api = ImageAPI()

    if args.status:
        status = api.status()
        if args.json:
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            print("📡 GPT-Image-2 API 后端状态\n")
            for b in status["backends"]:
                icon = "✅" if b["configured"] else "❌"
                print(f"{icon} {b['name']}")
                print(f"   模型: {', '.join(b['features'])}")
                print(f"   成本: {b['cost']}")
                print(f"   状态: {'已配置' if b['configured'] else '未配置API Key'}")
                print()

    elif args.list_models:
        models = api.list_models()
        if args.json:
            print(json.dumps(models, ensure_ascii=False, indent=2))
        else:
            print("🤖 可用模型列表\n")
            for m in models:
                print(f"[{m['id']}] {m['name']}")
                print(f"   模型: {', '.join(m['models'])}")
                print()

    elif args.generate:
        result = api.generate(args.generate, model=args.model,
                              backend=args.backend, size=args.size, n=args.n)
        if result.get("error"):
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"❌ 错误: {result['error']}")
                if "hint" in result:
                    print(f"💡 {result['hint']}")
        else:
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"✅ 成功 (后端: {result.get('backend', 'unknown')})")
                print(result.get("output", result))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
