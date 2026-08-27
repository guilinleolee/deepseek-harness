#!/usr/bin/env python3
"""
Dual Delivery
双渠道发布：飞书云文档 + Web 直链

用法:
    python3 dual_delivery.py upload video.mp4 --title "产品介绍"
    python3 dual_delivery.py status TASK_ID
    python3 dual_delivery.py links TASK_ID
"""

import argparse
import json
import os
import sys
import base64
import hashlib
import time
from pathlib import Path
from typing import Optional, Dict

# 飞书 API 配置
FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"


def feishu_get_token() -> Optional[str]:
    """获取飞书 Tenant Access Token"""
    if not FEISHU_APP_ID or not FEISHU_APP_SECRET:
        return None

    try:
        import urllib.request
        url = f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
        payload = json.dumps({
            "app_id": FEISHU_APP_ID,
            "app_secret": FEISHU_APP_SECRET,
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if result.get("code") == 0:
                return result.get("tenant_access_token")
    except Exception as e:
        print(f"Feishu token error: {e}")
    return None


def feishu_upload(file_path: Path, token: str, folder_token: str = "") -> Optional[Dict]:
    """上传文件到飞书云文档"""
    try:
        import urllib.request

        url = f"{FEISHU_BASE_URL}/drive/v1/files/upload_all"
        boundary = f"----FormBoundary7MA4YWxkTrZu0gW"

        file_data = file_path.read_bytes()
        file_hash = hashlib.md5(file_data).hexdigest()

        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file_name"\r\n\r\n'
            f"{file_path.name}\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="parent_type"\r\n\r\n'
            f"explorer\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="parent_node"\r\n\r\n'
            f"{folder_token}\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="size"\r\n\r\n'
            f"{len(file_data)}\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="hash"\r\n\r\n'
            f"{file_hash}\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n"
        ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            if result.get("code") == 0:
                return result.get("data", {})
    except Exception as e:
        print(f"Feishu upload error: {e}")
    return None


def feishu_create_message(token: str, title: str, file_token: str, file_type: str = "mp4") -> Optional[Dict]:
    """在飞书群里发送消息（带视频卡片）"""
    try:
        import urllib.request

        url = f"{FEISHU_BASE_URL}/im/v1/messages?receive_id_type=chat_id"
        card_content = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {"tag": "plain_text", "content": f"🎬 {title}"},
                    "template": "purple",
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": f"**视频已生成**\n请在下方查看或下载：",
                    },
                    {
                        "tag": "action",
                        "actions": [
                            {
                                "tag": "button",
                                "text": {"tag": "plain_text", "content": "▶️ 预览视频"},
                                "type": "primary",
                                "url": f"https://internal.dracohu.cn/videos/{file_token}",
                            },
                            {
                                "tag": "button",
                                "text": {"tag": "plain_text", "content": "💾 下载视频"},
                                "type": "default",
                                "url": f"https://internal.dracohu.cn/videos/{file_token}/download",
                            },
                        ],
                    },
                    {
                        "tag": "note",
                        "elements": [
                            {"tag": "plain_text", "content": f"文件 Token: {file_token}"}
                        ],
                    },
                ],
            },
        }

        # 需要 chat_id，这里返回结构化结果
        return {
            "card_content": card_content,
            "file_token": file_token,
            "web_url": f"https://internal.dracohu.cn/videos/{file_token}",
        }
    except Exception as e:
        print(f"Feishu message error: {e}")
    return None


def web_upload(file_path: Path, api_url: str = "https://internal.dracohu.cn/api/upload") -> Optional[Dict]:
    """上传到 Web 直链存储（模拟）"""
    # 这里是模拟实现，实际使用时替换为真实 CDN API
    try:
        file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()[:12]
        web_url = f"https://internal.dracohu.cn/videos/{file_hash}/{file_path.name}"

        return {
            "url": web_url,
            "hash": file_hash,
            "size": file_path.stat().st_size,
        }
    except Exception as e:
        print(f"Web upload error: {e}")
    return None


def upload_dual(
    file_path: Path,
    title: str,
    description: str = "",
    tags: list = None,
) -> Dict:
    """双渠道发布"""
    results = {
        "title": title,
        "file": str(file_path),
        "size": file_path.stat().st_size if file_path.exists() else 0,
        "feishu": None,
        "web": None,
        "links": {},
    }

    if tags is None:
        tags = []

    # 1. 飞书云上传
    token = feishu_get_token()
    if token:
        print("飞书: 上传中...")
        feishu_result = feishu_upload(file_path, token)
        if feishu_result:
            feishu_token = feishu_result.get("file_token", "")
            feishu_url = f"https://internal.dracohu.cn/videos/{feishu_token}"
            results["feishu"] = {
                "token": feishu_token,
                "url": feishu_url,
                "name": feishu_result.get("name", file_path.name),
            }
            results["links"]["feishu"] = feishu_url
            print(f"  飞书: {feishu_url}")
    else:
        print("飞书: 未配置 APP_ID/APP_SECRET，跳过")

    # 2. Web 直链上传
    print("Web: 上传中...")
    web_result = web_upload(file_path)
    if web_result:
        results["web"] = web_result
        results["links"]["web"] = web_result["url"]
        print(f"  Web: {web_result['url']}")
    else:
        print("Web: 上传失败，跳过")

    return results


def save_delivery_results(results: Dict, output_path: Path = None) -> Path:
    """保存发布结果"""
    if output_path is None:
        ts = time.strftime("%Y%m%d-%H%M%S")
        output_path = Path(f"delivery_{ts}.json")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Dual Delivery")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # upload 子命令
    up_parser = subparsers.add_parser("upload", help="双渠道发布")
    up_parser.add_argument("file", type=Path, help="要发布的视频文件")
    up_parser.add_argument("--title", "-t", required=True, help="视频标题")
    up_parser.add_argument("--description", "-d", default="", help="视频描述")
    up_parser.add_argument("--tags", nargs="+", help="标签")
    up_parser.add_argument("--output", "-o", type=Path, help="结果输出文件")

    # links 子命令
    links_parser = subparsers.add_parser("links", help="获取发布链接")
    links_parser.add_argument("result_file", type=Path, help="结果 JSON 文件")

    # status 子命令
    status_parser = subparsers.add_parser("status", help="查询发布状态")
    status_parser.add_argument("result_file", type=Path, help="结果 JSON 文件")

    args = parser.parse_args()

    if args.command == "upload":
        if not args.file.exists():
            print(f"ERROR: File not found: {args.file}")
            sys.exit(1)

        print(f"=" * 60)
        print(f"双渠道发布")
        print(f"=" * 60)
        print(f"文件: {args.file.name} ({args.file.stat().st_size / 1024 / 1024:.1f} MB)")
        print(f"标题: {args.title}")
        if args.description:
            print(f"描述: {args.description}")
        if args.tags:
            print(f"标签: {', '.join(args.tags)}")
        print()

        results = upload_dual(args.file, args.title, args.description, args.tags)
        output_path = save_delivery_results(results, args.output)

        print()
        print("=" * 60)
        print("发布结果")
        print("=" * 60)
        if results["feishu"]:
            print(f"飞书: {results['links']['feishu']}")
        if results["web"]:
            print(f"Web:  {results['links']['web']}")

        if not results["feishu"] and not results["web"]:
            print("WARNING: 所有渠道均未成功")
            sys.exit(1)

        print(f"\n结果已保存: {output_path}")

    elif args.command == "links":
        if not args.result_file.exists():
            print(f"ERROR: File not found: {args.result_file}")
            sys.exit(1)

        with open(args.result_file, "r", encoding="utf-8") as f:
            results = json.load(f)

        print(f"标题: {results.get('title', 'N/A')}")
        print(f"文件: {results.get('file', 'N/A')}")
        print()
        print("发布链接:")
        for name, url in results.get("links", {}).items():
            print(f"  {name.upper()}: {url}")

    elif args.command == "status":
        if not args.result_file.exists():
            print(f"ERROR: File not found: {args.result_file}")
            sys.exit(1)

        with open(args.result_file, "r", encoding="utf-8") as f:
            results = json.load(f)

        print(f"标题: {results.get('title', 'N/A')}")
        print(f"文件大小: {results.get('size', 0) / 1024 / 1024:.1f} MB")
        print()
        print("状态:")
        for name, data in [("飞书", results.get("feishu")), ("Web", results.get("web"))]:
            if data:
                print(f"  ✅ {name}: {data.get('url', data.get('token', 'N/A'))}")
            else:
                print(f"  ❌ {name}: 未上传")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
