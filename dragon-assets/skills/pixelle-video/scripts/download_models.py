#!/usr/bin/env python3
"""
Pixelle-Video Model Downloader
Automatically downloads required models for workflows
"""

import os
import urllib.request
import hashlib
from pathlib import Path
from typing import Dict, List, Optional


MODELS = {
    "checkpoints": [
        {
            "name": "wan2.1_text2img_1.3B_bf16.safetensors",
            "url": "https://huggingface.co/ByteDance/HunyuanVideo/resolve/main/hunyuan_video_720_personal_gate_权重名称.safetensors",
            "size": "2.5GB",
            "required": True,
            "description": "WAN 2.1 Text-to-Image model (1.3B parameters)"
        },
        {
            "name": "wan2.1_i2v_480p_diffusion.safetensors",
            "url": "https://huggingface.co/ByteDance/HunyuanVideo/resolve/main/hunyuan_video_i2v_权重名称.safetensors",
            "size": "2.5GB",
            "required": True,
            "description": "WAN 2.1 Image-to-Video model (480p)"
        },
    ],
    "vae": [
        {
            "name": "wan_vae_bf16.safetensors",
            "url": "https://huggingface.co/ByteDance/HunyuanVideo/resolve/main/vae_bf16_fix.safetensors",
            "size": "334MB",
            "required": True,
            "description": "WAN VAE (bf16)"
        }
    ],
    "audio": [
        {
            "name": "ChatTTS",
            "url": "https://huggingface.co/2Noise/ChatTTS/resolve/main/model.pt",
            "size": "250MB",
            "required": True,
            "description": "ChatTTS voice synthesis model"
        }
    ]
}


class ModelDownloader:
    def __init__(self, models_dir: str = None):
        if models_dir is None:
            # Default ComfyUI models directory
            models_dir = os.path.join(
                os.path.dirname(__file__), "..", "..", "ComfyUI", "models"
            )
        self.models_dir = Path(models_dir)

    def ensure_dirs(self):
        """Create model directories"""
        for category in MODELS.keys():
            (self.models_dir / category).mkdir(parents=True, exist_ok=True)

    def get_model_path(self, category: str, model_name: str) -> Path:
        """Get full path for a model"""
        return self.models_dir / category / model_name

    def model_exists(self, category: str, model_name: str) -> bool:
        """Check if model already exists"""
        path = self.get_model_path(category, model_name)
        return path.exists() and path.stat().st_size > 0

    def download_file(self, url: str, dest: Path, chunk_size: int = 8192) -> bool:
        """Download a file with progress"""
        try:
            print(f"  Downloading: {dest.name}")

            def reporthook(block_num, block_size, total_size):
                downloaded = block_num * block_size
                percent = min(100, downloaded * 100 // total_size) if total_size > 0 else 0
                bar_len = 40
                filled = bar_len * percent // 100
                bar = "=" * filled + "-" * (bar_len - filled)
                print(f"\r  [{bar}] {percent}%", end="", flush=True)

            urllib.request.urlretrieve(url, dest, reporthook)
            print()  # New line after progress
            return True

        except Exception as e:
            print(f"\n  Error: {e}")
            if dest.exists():
                dest.unlink()
            return False

    def download_model(self, category: str, model: Dict) -> bool:
        """Download a single model"""
        if self.model_exists(category, model["name"]):
            print(f"  [SKIP] {model['name']} (already exists)")
            return True

        path = self.get_model_path(category, model["name"])
        print(f"\n  Category: {category}")
        print(f"  Description: {model['description']}")
        print(f"  Size: ~{model['size']}")

        # For HuggingFace, use huggingface-cli or direct download
        # This is a simplified version - in production use hf_hub_download
        return self.download_file(model["url"], path)

    def download_all(self, categories: List[str] = None) -> Dict[str, bool]:
        """Download all models"""
        self.ensure_dirs()

        if categories is None:
            categories = list(MODELS.keys())

        results = {}
        for category in categories:
            if category not in MODELS:
                continue

            print(f"\n{'='*60}")
            print(f"Category: {category.upper()}")
            print(f"{'='*60}")

            results[category] = []
            for model in MODELS[category]:
                success = self.download_model(category, model)
                results[category].append({
                    "name": model["name"],
                    "success": success,
                    "required": model.get("required", False)
                })

        return results

    def verify_installations(self) -> Dict[str, bool]:
        """Verify all required models are installed"""
        print("\nVerifying installations:")
        print("-" * 50)

        all_ok = True
        for category, models in MODELS.items():
            print(f"\n{category}:")
            for model in models:
                exists = self.model_exists(category, model["name"])
                status = "OK" if exists else "MISSING"
                required = "(required)" if model.get("required") else ""
                print(f"  [{status}] {model['name']} {required}")
                if not exists and model.get("required"):
                    all_ok = False

        return {"all_ok": all_ok}

    def get_status(self) -> Dict:
        """Get installation status"""
        status = {}
        for category, models in MODELS.items():
            status[category] = {
                "total": len(models),
                "installed": sum(
                    1 for m in models
                    if self.model_exists(category, m["name"])
                ),
                "required": sum(1 for m in models if m.get("required"))
            }
        return status


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Pixelle-Video Model Downloader")
    parser.add_argument("--dir", help="Models directory")
    parser.add_argument("--verify", action="store_true", help="Verify installations")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument(
        "--categories",
        nargs="+",
        choices=list(MODELS.keys()),
        help="Download specific categories"
    )

    args = parser.parse_args()
    downloader = ModelDownloader(args.dir)

    if args.verify:
        result = downloader.verify_installations()
        if result["all_ok"]:
            print("\nAll required models installed!")
        else:
            print("\nSome required models are missing.")
        return

    if args.status:
        status = downloader.get_status()
        print("\nModel Status:")
        for category, info in status.items():
            print(f"  {category}: {info['installed']}/{info['total']} installed")
            if info['required'] > 0:
                required_ok = info['installed'] >= info['required']
                print(f"    Required: {'OK' if required_ok else 'MISSING'}")
        return

    # Download all (default)
    print("Pixelle-Video Model Downloader")
    print("=" * 60)
    print("\nNote: Due to large model sizes, download may take hours.")
    print("Models will be saved to:")
    print(f"  {downloader.models_dir}")

    results = downloader.download_all(args.categories)

    # Summary
    print("\n" + "=" * 60)
    print("Download Summary:")
    print("-" * 60)
    for category, items in results.items():
        success = sum(1 for i in items if i["success"])
        total = len(items)
        print(f"  {category}: {success}/{total} succeeded")

    # Verify
    print("\n" + "=" * 60)
    downloader.verify_installations()


if __name__ == "__main__":
    main()
