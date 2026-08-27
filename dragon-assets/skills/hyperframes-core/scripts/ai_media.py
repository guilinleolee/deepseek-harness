#!/usr/bin/env python3
"""
AI Media Generator
调用 AI 生成配图/素材，与场景时间线对齐

用法:
    python3 ai_media.py generate --prompt "科技感粒子动画背景" --output background.png
    python3 ai_media.py batch prompts.json --output-dir ./media
    python3 ai_media.py find-free  # 查找免费方案
"""

import argparse
import json
import os
import sys
import base64
import hashlib
from pathlib import Path
from typing import Optional, List, Dict

# 可用的 AI 图像生成 API
FREE_PROVIDERS = [
    {
        "name": "Pollinations",
        "endpoint": "https://image.pollinations.ai/prompt/{prompt}?width={w}&height={h}&seed={seed}",
        "free": True,
        "rate_limit": "无限制",
        "quality": "中等",
    },
    {
        "name": "HuggingFace Free",
        "endpoint": "https://api-inference.huggingface.co/models/{model}",
        "free": True,
        "models": ["stabilityai/stable-diffusion-xl-base-1.0", "prompthero/openjourney"],
        "rate_limit": "100次/小时",
        "quality": "中上",
    },
]

PAID_PROVIDERS = [
    {
        "name": "OpenAI DALL-E",
        "env": "OPENAI_API_KEY",
        "quality": "高",
        "cost": "$0.04-$0.12/图",
    },
    {
        "name": "Midjourney",
        "env": "MJ_API_TOKEN",
        "quality": "高",
        "cost": "$0.02-$0.11/图",
    },
    {
        "name": "Flux (Replicate)",
        "env": "REPLICATE_API_TOKEN",
        "quality": "高",
        "cost": "$0.003-$0.055/图",
    },
]


def generate_pollinations(prompt: str, width: int = 1024, height: int = 1024,
                          seed: Optional[int] = None, output_path: Path = None) -> Optional[bytes]:
    """Pollinations AI 免费生成（无需 API Key）"""
    import urllib.parse
    import urllib.request

    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}"
    if seed:
        url += f"&seed={seed}"

    try:
        print(f"Generating with Pollinations AI...")
        print(f"  Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as response:
            data = response.read()

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(data)
            print(f"  Saved: {output_path}")
        return data
    except Exception as e:
        print(f"  Error: {e}")
        return None


def generate_huggingface(prompt: str, model: str = "stabilityai/stable-diffusion-xl-base-1.0",
                          width: int = 1024, height: int = 1024,
                          output_path: Path = None) -> Optional[bytes]:
    """HuggingFace Inference API（需 API Key，免费额度）"""
    api_key = os.environ.get("HF_API_KEY")
    if not api_key:
        print("WARNING: HF_API_KEY not set, skipping HuggingFace")
        return None

    import urllib.request

    url = f"https://api-inference.huggingface.co/models/{model}"
    payload = {
        "inputs": prompt,
        "parameters": {"width": width, "height": height},
    }

    try:
        print(f"Generating with HuggingFace ({model})...")
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as response:
            result = response.read()

        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(result)
            print(f"  Saved: {output_path}")
        return result
    except Exception as e:
        print(f"  Error: {e}")
        return None


def generate_flux_replicate(prompt: str, width: int = 1024, height: int = 1024,
                            output_path: Path = None) -> Optional[str]:
    """Flux via Replicate（需 API Key）"""
    api_key = os.environ.get("REPLICATE_API_TOKEN")
    if not api_key:
        print("WARNING: REPLICATE_API_TOKEN not set, skipping Flux")
        return None

    try:
        import urllib.request

        url = "https://api.replicate.com/v1/predictions"
        payload = {
            "version": "schnell",
            "input": {
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_inference_steps": 4,
                "seed": 0,
            },
        }

        # 创建预测
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Token {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            pred = json.loads(response.read())

        pred_id = pred.get("id")
        if not pred_id:
            print("  Error: No prediction ID returned")
            return None

        print(f"  Prediction: {pred_id}")
        print(f"  Polling for completion...")

        # 轮询结果
        import time
        for _ in range(60):
            time.sleep(5)
            req = urllib.request.Request(
                f"{url}/{pred_id}",
                headers={"Authorization": f"Token {api_key}"},
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read())

            if result.get("status") == "succeeded":
                output_url = result["output"][0]
                # 下载图片
                req = urllib.request.Request(output_url)
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = resp.read()

                if output_path:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_bytes(data)
                    print(f"  Saved: {output_path}")
                return str(output_path)
            elif result.get("status") == "failed":
                print(f"  Failed: {result.get('error')}")
                return None

        print("  Timeout waiting for prediction")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def find_free_provider() -> str:
    """查找免费方案"""
    if os.environ.get("HF_API_KEY"):
        return "huggingface"
    return "pollinations"


def generate_batch(prompts_file: Path, output_dir: Path, provider: str = "auto") -> List[Dict]:
    """批量生成配图"""
    with open(prompts_file, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    if isinstance(prompts, dict) and "media" in prompts:
        prompts = prompts["media"]

    if not isinstance(prompts, list):
        prompts = [prompts]

    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for i, item in enumerate(prompts):
        prompt = item.get("prompt", item.get("text", ""))
        name = item.get("name", f"media_{i+1}")
        width = item.get("width", 1024)
        height = item.get("height", 768)

        print(f"\n[{i+1}/{len(prompts)}] {name}")
        output_path = output_dir / f"{name}.png"

        # 选择 provider
        if provider == "auto":
            provider = find_free_provider()

        if provider == "pollinations":
            data = generate_pollinations(prompt, width, height, output_path=output_path)
        elif provider == "huggingface":
            data = generate_huggingface(prompt, width=width, height=height, output_path=output_path)
        else:
            print(f"  Unknown provider: {provider}")
            continue

        results.append({
            "name": name,
            "prompt": prompt,
            "output": str(output_path),
            "success": data is not None,
        })

    # 保存结果
    result_file = output_dir / "generation_results.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存: {result_file}")

    success_count = sum(1 for r in results if r["success"])
    print(f"成功: {success_count}/{len(results)}")

    return results


def main():
    parser = argparse.ArgumentParser(description="AI Media Generator")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # generate 子命令
    gen_parser = subparsers.add_parser("generate", help="生成单张图片")
    gen_parser.add_argument("--prompt", "-p", required=True, help="图像描述")
    gen_parser.add_argument("--output", "-o", type=Path, required=True, help="输出文件")
    gen_parser.add_argument("--width", "-w", type=int, default=1024)
    gen_parser.add_argument("--height", "-H", type=int, default=1024)
    gen_parser.add_argument("--provider", default="auto", choices=["pollinations", "huggingface", "flux", "auto"])
    gen_parser.add_argument("--seed", type=int, help="随机种子（Pollinations）")

    # batch 子命令
    batch_parser = subparsers.add_parser("batch", help="批量生成")
    batch_parser.add_argument("prompts_file", type=Path, help="提示词 JSON 文件")
    batch_parser.add_argument("--output-dir", "-o", type=Path, required=True)
    batch_parser.add_argument("--provider", default="auto")

    # find-free 子命令
    free_parser = subparsers.add_parser("find-free", help="查找免费方案")
    free_parser.add_argument("--list-providers", action="store_true", help="列出所有 provider")

    args = parser.parse_args()

    if args.command == "generate":
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if args.provider == "pollinations" or args.provider == "auto":
            data = generate_pollinations(
                args.prompt, args.width, args.height,
                args.seed, output_path
            )
            if data:
                print(f"生成成功: {output_path}")
            else:
                sys.exit(1)
        elif args.provider == "huggingface":
            data = generate_huggingface(
                args.prompt, width=args.width, height=args.height,
                output_path=output_path
            )
            if data:
                print(f"生成成功: {output_path}")
            else:
                print("HuggingFace 生成失败，尝试 Pollinations...")
                generate_pollinations(
                    args.prompt, args.width, args.height,
                    args.seed, output_path
                )
        elif args.provider == "flux":
            result = generate_flux_replicate(
                args.prompt, args.width, args.height, output_path
            )
            if result:
                print(f"生成成功: {output_path}")
            else:
                sys.exit(1)

    elif args.command == "batch":
        generate_batch(args.prompts_file, args.output_dir, args.provider)

    elif args.command == "find-free":
        print("=" * 60)
        print("免费 AI 图像生成方案")
        print("=" * 60)
        print("\n[免费] Pollinations AI")
        print(f"  URL: {FREE_PROVIDERS[0]['endpoint'][:70]}...")
        print(f"  限制: {FREE_PROVIDERS[0]['rate_limit']}")
        print(f"  质量: {FREE_PROVIDERS[0]['quality']}")

        hf_key = "已设置" if os.environ.get("HF_API_KEY") else "未设置"
        print(f"\n[HuggingFace - {hf_key}]")
        for m in FREE_PROVIDERS[1]["models"]:
            print(f"  Model: {m}")
        print(f"  限制: {FREE_PROVIDERS[1]['rate_limit']}")

        print("\n[付费方案]")
        for p in PAID_PROVIDERS:
            key = "已设置" if os.environ.get(p["env"]) else "未设置"
            print(f"  {p['name']} ({key}): {p['cost']}, 质量: {p['quality']}")
        print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
