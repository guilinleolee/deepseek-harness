#!/usr/bin/env python3
"""
GPT-Image-2 Prompt Library 数据同步脚本
从GitHub同步最新数据
"""

import os
import json
import requests
import argparse
from pathlib import Path


RAW_JSON_URL = "https://raw.githubusercontent.com/EvoLinkAI/awesome-gpt-image-2-prompts/main/gpt_image2_prompts.json"
GITHUB_API_URL = "https://api.github.com/repos/EvoLinkAI/awesome-gpt-image-2-prompts/contents"


def sync_data(output_dir: str, incremental: bool = False):
    """同步数据"""
    print("🔄 正在同步GPT-Image-2提示词库...")

    try:
        # 获取最新数据
        response = requests.get(RAW_JSON_URL, timeout=30)
        response.raise_for_status()
        remote_data = response.json()

        # 创建输出目录
        data_dir = os.path.join(output_dir, "data")
        os.makedirs(data_dir, exist_ok=True)

        output_path = os.path.join(data_dir, "gpt_image2_prompts.json")

        if incremental and os.path.exists(output_path):
            # 增量更新
            with open(output_path, "r", encoding="utf-8") as f:
                local_data = json.load(f)

            # 合并数据（去重）
            local_ids = {p["id"] for p in local_data.get("prompts", [])}
            new_prompts = [p for p in remote_data.get("prompts", [])
                          if p["id"] not in local_ids]

            if new_prompts:
                local_data["prompts"].extend(new_prompts)
                local_data["updated"] = "incremental"
                print(f"📈 增量更新: 新增 {len(new_prompts)} 条提示词")
            else:
                print("✅ 无需更新，数据已是最新")

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(local_data, f, ensure_ascii=False, indent=2)
        else:
            # 全量更新
            remote_data["updated"] = "full"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(remote_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 全量同步: 共 {len(remote_data.get('prompts', []))} 条提示词")

        print(f"📁 数据保存至: {output_path}")

    except requests.RequestException as e:
        print(f"❌ 同步失败: {e}")
        print("💡 将使用内置示例数据")


def check_update(output_dir: str):
    """检查更新"""
    try:
        response = requests.get(GITHUB_API_URL, timeout=10)
        data = response.json()

        for item in data:
            if item["name"] == "gpt_image2_prompts.json":
                print(f"📅 GitHub最新更新: {item['updated']}")
                print(f"📊 文件大小: {item['size']} bytes")
                return

        print("⚠️ 未找到数据文件")
    except Exception as e:
        print(f"❌ 检查失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="GPT-Image-2 数据同步")
    parser.add_argument("--dir", default=os.path.dirname(__file__), help="输出目录")
    parser.add_argument("--incremental", action="store_true", help="增量更新")
    parser.add_argument("--check", action="store_true", help="检查更新")

    args = parser.parse_args()

    if args.check:
        check_update(args.dir)
    else:
        sync_data(args.dir, args.incremental)


if __name__ == "__main__":
    main()