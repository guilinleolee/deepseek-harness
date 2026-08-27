#!/usr/bin/env python3
"""
Fanout Executor - 多平台内容分发执行器
GEO内容Fanout工作流执行引擎
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 配置路径
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
BACKLOG_FILE = DATA_DIR / "backlog.json"
ARCHIVE_DIR = DATA_DIR / "archive"

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


def load_backlog() -> dict:
    """加载backlog数据"""
    if BACKLOG_FILE.exists():
        with open(BACKLOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tasks": [], "version": "1.0", "updated_at": datetime.now().isoformat()}


def get_task(task_id: str) -> Optional[dict]:
    """获取任务"""
    backlog = load_backlog()
    for task in backlog["tasks"]:
        if task["task_id"] == task_id:
            return task
    return None


def execute_wordpress(task_id: str, content: str, title: str) -> dict:
    """
    执行WordPress发布

    环境变量:
    - WP_SITE_URL: WordPress站点URL
    - WP_USERNAME: WordPress用户名
    - WP_APP_PASSWORD: WordPress应用密码
    """
    wp_url = os.environ.get("WP_SITE_URL")
    wp_username = os.environ.get("WP_USERNAME")
    wp_password = os.environ.get("WP_APP_PASSWORD")

    if not all([wp_url, wp_username, wp_password]):
        return {
            "success": False,
            "error": "WordPress credentials not configured. Set WP_SITE_URL, WP_USERNAME, WP_APP_PASSWORD"
        }

    try:
        import requests
        from requests.auth import HTTPBasicAuth

        # WordPress REST API创建文章
        api_url = f"{wp_url}/wp-json/wp/v2/posts"

        post_data = {
            "title": title,
            "content": content,
            "status": "draft"  # 默认草稿，可改为"publish"
        }

        response = requests.post(
            api_url,
            auth=HTTPBasicAuth(wp_username, wp_password),
            json=post_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code in [200, 201]:
            result = response.json()
            return {
                "success": True,
                "url": result.get("link"),
                "post_id": result.get("id")
            }
        else:
            return {
                "success": False,
                "error": f"WordPress API error: {response.status_code} - {response.text}"
            }

    except ImportError:
        return {
            "success": False,
            "error": "requests library not installed. Run: pip install requests"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def execute_wechat(task_id: str, content: str, title: str) -> dict:
    """
    执行微信公众号发布

    环境变量:
    - WECHAT_APP_ID: 微信公众号AppID
    - WECHAT_APP_SECRET: 微信公众号AppSecret
    """
    app_id = os.environ.get("WECHAT_APP_ID")
    app_secret = os.environ.get("WECHAT_APP_SECRET")

    if not all([app_id, app_secret]):
        return {
            "success": False,
            "error": "WeChat credentials not configured. Set WECHAT_APP_ID, WECHAT_APP_SECRET"
        }

    # 微信公众号发布需要access_token，这里提供基础实现
    try:
        import requests

        # 获取access_token
        token_url = f"https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": app_id,
            "secret": app_secret
        }
        token_response = requests.get(token_url, params=params)
        token_data = token_response.json()

        if "access_token" not in token_data:
            return {
                "success": False,
                "error": f"Failed to get access_token: {token_data}"
            }

        access_token = token_data["access_token"]

        # 上传草稿
        draft_url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"

        # 微信公众号需要特殊格式
        articles = [{
            "title": title,
            "author": "GEO Content Team",
            "digest": content[:54],  # 摘要
            "content": content,
            "content_source_url": "",
            "thumb_media_id": "",
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }]

        draft_data = {
            "articles": articles
        }

        draft_response = requests.post(draft_url, json=draft_data)
        draft_result = draft_response.json()

        if draft_result.get("errcode") == 0:
            return {
                "success": True,
                "media_id": draft_result.get("media_id"),
                "note": "Draft created. Manually publish from WeChat backend."
            }
        else:
            return {
                "success": False,
                "error": f"WeChat API error: {draft_result}"
            }

    except ImportError:
        return {
            "success": False,
            "error": "requests library not installed. Run: pip install requests"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def execute_fanout(task_id: str, targets: list = None, dry_run: bool = False) -> dict:
    """
    执行Fanout分发

    Args:
        task_id: 任务ID
        targets: 分发目标列表，默认所有目标
        dry_run: 是否仅模拟执行
    """
    task = get_task(task_id)
    if not task:
        return {"success": False, "error": f"Task not found: {task_id}"}

    # 检查质量门控是否全部通过
    gates = task.get("gates", {})
    all_gates_passed = all(g.get("passed", False) for g in gates.values())

    if not all_gates_passed:
        return {
            "success": False,
            "error": "Not all quality gates passed. Cannot publish.",
            "failed_gates": [k for k, v in gates.items() if not v.get("passed", False)]
        }

    # 获取内容（实际应从文件系统读取）
    content = task.get("content", "# Placeholder content")
    title = task.get("title", task.get("brief_id", "Untitled"))

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "task_id": task_id,
            "targets": targets or task.get("fanout_targets", ["wordpress"]),
            "title": title
        }

    # 执行分发
    results = {}
    fanout_targets = targets or task.get("fanout_targets", ["wordpress"])

    for target in fanout_targets:
        if target == "wordpress":
            results["wordpress"] = execute_wordpress(task_id, content, title)
        elif target == "wechat":
            results["wechat"] = execute_wechat(task_id, content, title)
        else:
            results[target] = {
                "success": False,
                "error": f"Unknown target: {target}"
            }

    # 更新任务状态
    update_backlog(task_id, results)

    return {
        "success": all(r.get("success", False) for r in results.values()),
        "task_id": task_id,
        "results": results
    }


def update_backlog(task_id: str, fanout_results: dict) -> None:
    """更新backlog中的任务状态和分发结果"""
    backlog = load_backlog()

    for task in backlog["tasks"]:
        if task["task_id"] == task_id:
            task["fanout_results"] = fanout_results
            task["fanout_executed_at"] = datetime.now().isoformat()

            # 如果所有分发都成功，更新状态为published
            all_success = all(r.get("success", False) for r in fanout_results.values())
            if all_success:
                task["status"] = "published"

            task["updated_at"] = datetime.now().isoformat()
            break

    with open(BACKLOG_FILE, "w", encoding="utf-8") as f:
        json.dump(backlog, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Fanout Executor - 多平台内容分发")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # execute命令
    exec_parser = subparsers.add_parser("execute", help="执行Fanout分发")
    exec_parser.add_argument("task_id", help="任务ID")
    exec_parser.add_argument("--targets", nargs="+", help="分发目标")
    exec_parser.add_argument("--dry-run", action="store_true", help="模拟执行")

    # status命令
    status_parser = subparsers.add_parser("status", help="查看分发状态")
    status_parser.add_argument("task_id", help="任务ID")

    args = parser.parse_args()

    if args.command == "execute":
        result = execute_fanout(args.task_id, args.targets, args.dry_run)

        if result.get("dry_run"):
            print(f"🧪 模拟执行: {args.task_id}")
            print(f"   目标: {', '.join(result.get('targets', []))}")
            print(f"   标题: {result.get('title')}")
            print("   (dry-run模式，未实际发布)")

        elif result.get("success"):
            print(f"✅ Fanout完成: {args.task_id}")
            for target, res in result.get("results", {}).items():
                if res.get("success"):
                    print(f"   [{target}] ✅ {res.get('url', res.get('media_id', 'OK'))}")
                else:
                    print(f"   [{target}] ❌ {res.get('error')}")
        else:
            print(f"❌ Fanout失败: {result.get('error')}")
            if result.get("failed_gates"):
                print(f"   未通过门控: {', '.join(result['failed_gates'])}")
            sys.exit(1)

    elif args.command == "status":
        task = get_task(args.task_id)
        if task:
            print(f"\n📊 分发状态: {args.task_id}")
            print(f"   状态: {task.get('status')}")
            print(f"   分发目标: {', '.join(task.get('fanout_targets', []))}")

            if task.get("fanout_results"):
                print("   分发结果:")
                for target, res in task["fanout_results"].items():
                    icon = "✅" if res.get("success") else "❌"
                    print(f"      {icon} {target}: {res.get('url', res.get('error', 'OK'))}")
            else:
                print("   (尚未执行)")

            # 显示门控状态
            print("   质量门控:")
            for gate, info in task.get("gates", {}).items():
                icon = "✅" if info.get("passed") else "⬜"
                print(f"      {icon} {gate}: {info.get('status')}")
        else:
            print(f"❌ 未找到任务: {args.task_id}")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
