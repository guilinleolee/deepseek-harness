#!/usr/bin/env python3
"""
GBrain Webhook Transforms
将外部 Webhook 事件转换为 GBrain 知识库条目

Usage:
    python webhook_transforms.py serve [--port 8080]
    python webhook_transforms.py test --source github --event push
    python webhook_transforms.py list
    python webhook_transforms.py sync --source rss --feed "https://example.com/rss"
    python webhook_transforms.py transform --source github --payload @event.json --dry-run
    python webhook_transforms.py add --source github --events push,pr,issue
    python webhook_transforms.py remove --source github
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import logging
import os
import re
import sys
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from typing import Any

import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("webhook_transforms")


# ═══════════════════════════════════════════════════════════════
# 数据模型
# ═══════════════════════════════════════════════════════════════

@dataclass
class EntityUpdate:
    """实体更新条目"""
    entity_type: str
    slug: str
    frontmatter: dict
    body: str = ""
    event: dict = field(default_factory=dict)
    confidence: float = 0.9
    raw: dict = field(default_factory=dict)


@dataclass
class TransformResult:
    """转换结果"""
    success: bool
    updates: list[EntityUpdate] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    duration_ms: float = 0.0


# ═══════════════════════════════════════════════════════════════
# 配置加载
# ═══════════════════════════════════════════════════════════════

def load_config(config_path: Path | None = None) -> dict:
    """加载 YAML 配置"""
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.yaml"
    if not config_path.exists():
        log.warning(f"配置文件不存在: {config_path}，使用默认配置")
        return {"webhook_transforms": {"enabled": True, "general": {"dry_run": False}}}
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_brain_path(config: dict) -> Path:
    """获取 GBrain 根路径"""
    raw = config.get("webhook_transforms", {}).get("brain", {}).get("base_path", "~/.claude/gbrain")
    return Path(os.path.expanduser(raw))


# ═══════════════════════════════════════════════════════════════
# GBrain 写入接口
# ═══════════════════════════════════════════════════════════════

class BrainWriter:
    """写入 GBrain 知识库"""

    def __init__(self, brain_path: Path, dry_run: bool = False):
        self.brain_path = brain_path
        self.dry_run = dry_run
        self.entities_dir = brain_path / config.get("webhook_transforms", {}).get("brain", {}).get("entities_dir", "entities")
        self.pages_dir = brain_path / config.get("webhook_transforms", {}).get("brain", {}).get("pages_dir", "pages")

    def write_update(self, update: EntityUpdate) -> bool:
        """写入单个实体更新"""
        if self.dry_run:
            log.info(f"[DRY RUN] 写入实体: {update.entity_type}/{update.slug}")
            return True
        try:
            entity_dir = self.entities_dir / update.entity_type
            entity_dir.mkdir(parents=True, exist_ok=True)
            file_path = entity_dir / f"{update.slug}.md"
            content = self._render_entity(update)
            file_path.write_text(content, encoding="utf-8")
            log.info(f"已写入: {file_path}")
            self._update_index(update)
            return True
        except Exception as e:
            log.error(f"写入失败 {update.slug}: {e}")
            return False

    def _render_entity(self, update: EntityUpdate) -> str:
        """渲染 Markdown 实体文件"""
        lines = ["---"]
        for key, value in update.frontmatter.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            elif isinstance(value, dict):
                lines.append(f"{key}:")
                for k, v in value.items():
                    lines.append(f"  {k}: {v}")
            else:
                lines.append(f"{key}: {value}")
        lines.append("---\n")
        if update.body:
            lines.append(update.body)
        return "\n".join(lines)

    def _update_index(self, update: EntityUpdate) -> None:
        """更新索引文件"""
        # 简化实现：追加到索引日志
        index_log = self.brain_path / ".cache" / "webhook_index_log.jsonl"
        index_log.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entity_type": update.entity_type,
            "slug": update.slug,
            "event": update.event.get("type", "unknown"),
        }
        with open(index_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ═══════════════════════════════════════════════════════════════
# Transform 函数
# ═══════════════════════════════════════════════════════════════

def transform_github_push(payload: dict, config: dict) -> list[EntityUpdate]:
    """GitHub push 事件转换"""
    repo = payload.get("repository", {}).get("full_name", "unknown")
    commits = payload.get("commits", [])
    slug = repo.replace("/", "-").lower()

    updates = []
    for commit in commits[:5]:
        timestamp = commit.get("timestamp", datetime.now(timezone.utc).isoformat())
        author = commit.get("author", {}).get("name", "unknown")
        message = commit.get("message", "")[:100]
        url = commit.get("url", "")

        frontmatter = {
            "title": f"Push to {repo}",
            "type": "timeline-event",
            "source": "github",
            "timestamp": timestamp,
            "author": author,
            "url": url,
            "tags": ["github", "push", repo],
        }
        body = f"## Commit\n\n**{author}** pushed to `{repo}`\n\n> {message}\n\n[{url}]({url})"
        updates.append(EntityUpdate(
            entity_type="github",
            slug=f"{slug}-timeline",
            frontmatter=frontmatter,
            body=body,
            event={"type": "push", "repo": repo, "author": author},
            raw=payload,
        ))

    return updates


def transform_github_pr(payload: dict, config: dict) -> list[EntityUpdate]:
    """GitHub PR 事件转换"""
    repo = payload.get("repository", {}).get("full_name", "unknown")
    action = payload.get("action", "unknown")
    pr_data = payload.get("pull_request", {})
    slug = repo.replace("/", "-").lower()

    frontmatter = {
        "title": f"PR: {pr_data.get('title', 'No title')}",
        "type": "timeline-event",
        "source": "github",
        "action": action,
        "state": pr_data.get("state", "unknown"),
        "author": pr_data.get("user", {}).get("login", "unknown"),
        "url": pr_data.get("html_url", ""),
        "tags": ["github", "pull_request", repo],
    }
    body = f"## Pull Request\n\n**{action}** — [{pr_data.get('title', 'No title')}]({pr_data.get('html_url', '')})\n\nState: {pr_data.get('state', 'unknown')}"
    return [EntityUpdate(
        entity_type="github",
        slug=f"{slug}-pr-{pr_data.get('id', 'unknown')}",
        frontmatter=frontmatter,
        body=body,
        event={"type": "pull_request", "action": action, "repo": repo},
        raw=payload,
    )]


def transform_github_issue(payload: dict, config: dict) -> list[EntityUpdate]:
    """GitHub issue 事件转换"""
    repo = payload.get("repository", {}).get("full_name", "unknown")
    action = payload.get("action", "unknown")
    issue_data = payload.get("issue", {})
    slug = repo.replace("/", "-").lower()

    frontmatter = {
        "title": issue_data.get("title", "No title"),
        "type": "discussion",
        "source": "github",
        "action": action,
        "state": issue_data.get("state", "unknown"),
        "author": issue_data.get("user", {}).get("login", "unknown"),
        "labels": [l.get("name") for l in issue_data.get("labels", [])],
        "url": issue_data.get("html_url", ""),
        "tags": ["github", "issue", repo],
    }
    body = f"## Issue\n\n**{action}** — [{issue_data.get('title', 'No title')}]({issue_data.get('html_url', '')})\n\nState: {issue_data.get('state', 'unknown')}\n\n{issue_data.get('body', '')}"
    return [EntityUpdate(
        entity_type="github",
        slug=f"{slug}-issue-{issue_data.get('id', 'unknown')}",
        frontmatter=frontmatter,
        body=body,
        event={"type": "issues", "action": action, "repo": repo},
        raw=payload,
    )]


def transform_slack_message(payload: dict, config: dict) -> list[EntityUpdate]:
    """Slack 消息事件转换"""
    channel = payload.get("channel", {}).get("name", "unknown")
    user = payload.get("user", {}).get("name", payload.get("user_name", "unknown"))
    text = payload.get("text", "")
    ts = payload.get("ts", str(time.time()))

    frontmatter = {
        "title": f"Slack: {channel}",
        "type": "discussion",
        "source": "slack",
        "channel": channel,
        "author": user,
        "timestamp": datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat(),
        "tags": ["slack", "discussion"],
    }
    body = f"## Message\n\n**{user}** in #{channel}\n\n{text}"
    return [EntityUpdate(
        entity_type="slack",
        slug=f"slack-{channel}-{ts.replace('.', '-')}",
        frontmatter=frontmatter,
        body=body,
        event={"type": "message", "channel": channel, "user": user},
        raw=payload,
    )]


def transform_rss_entry(entry: dict, config: dict, feed_slug: str) -> list[EntityUpdate]:
    """RSS 条目转换"""
    title = entry.get("title", "No title")
    link = entry.get("link", "")
    published = entry.get("published", datetime.now(timezone.utc).isoformat())
    summary = entry.get("summary", entry.get("content", ""))[:500]
    slug = re.sub(r"[^\w\-]", "-", title.lower())[:60]

    frontmatter = {
        "title": title,
        "type": "external-info",
        "source": "rss",
        "feed": feed_slug,
        "url": link,
        "published": published,
        "tags": ["rss", "external", feed_slug],
    }
    body = f"## {title}\n\n[Source]({link})\n\n{summary}"
    return [EntityUpdate(
        entity_type="rss",
        slug=f"{feed_slug}-{slug}",
        frontmatter=frontmatter,
        body=body,
        event={"type": "rss_entry", "feed": feed_slug, "title": title},
        raw=entry,
    )]


def transform_calendar_event(event: dict, config: dict) -> list[EntityUpdate]:
    """日历事件转换"""
    title = event.get("summary", "No title")
    start = event.get("start", {}).get("dateTime", datetime.now(timezone.utc).isoformat())
    attendees = [a.get("email", "") for a in event.get("attendees", []) if a.get("responseStatus") == "accepted"]

    frontmatter = {
        "title": title,
        "type": "timeline-event",
        "source": "calendar",
        "start": start,
        "attendees": attendees,
        "tags": ["calendar", "event"],
    }
    body = f"## Calendar Event\n\n**{title}**\n\nStart: {start}\n\nAttendees: {', '.join(attendees) or 'None'}"
    return [EntityUpdate(
        entity_type="calendar",
        slug=f"cal-{start[:10]}-{re.sub(r'[^\w]', '-', title.lower())[:30]}",
        frontmatter=frontmatter,
        body=body,
        event={"type": "calendar_event", "title": title},
        raw=event,
    )]


# ═══════════════════════════════════════════════════════════════
# Transform 路由器
# ═══════════════════════════════════════════════════════════════

def dispatch_transform(source: str, event_type: str, payload: dict, config: dict) -> list[EntityUpdate]:
    """根据 source 和 event_type 分发到对应 Transform 函数"""
    handlers = {
        ("github", "push"): transform_github_push,
        ("github", "pull_request"): transform_github_pr,
        ("github", "pull_request_target"): transform_github_pr,
        ("github", "issues"): transform_github_issue,
        ("github", "issue_comment"): transform_github_issue,
        ("github", "release"): lambda p, c: transform_github_pr(p, c),
        ("slack", "message"): transform_slack_message,
    }
    key = (source.lower(), event_type.lower())
    handler = handlers.get(key)
    if handler:
        return handler(payload, config)

    # 自定义 Webhook
    if source == "custom":
        entity_type = payload.get("entity_type", "custom")
        slug = payload.get("slug", f"custom-{uuid.uuid4().hex[:8]}")
        frontmatter = payload.get("frontmatter", {"title": payload.get("event", {}).get("type", "Custom Event")})
        body = payload.get("body", "")
        return [EntityUpdate(
            entity_type=entity_type,
            slug=slug,
            frontmatter=frontmatter,
            body=body,
            event=payload.get("event", {}),
            confidence=payload.get("confidence", 0.8),
            raw=payload,
        )]

    log.warning(f"未找到处理器: source={source}, event_type={event_type}")
    return []


# ═══════════════════════════════════════════════════════════════
# 签名验证
# ═══════════════════════════════════════════════════════════════

def verify_github_signature(payload_bytes: bytes, signature: str, secret: str) -> bool:
    """验证 GitHub HMAC-SHA256 签名"""
    if not signature or not secret:
        return True
    expected = "sha256=" + hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def verify_slack_signature(body: bytes, timestamp: str, signature: str, secret: str) -> bool:
    """验证 Slack 签名"""
    if not signature or not secret:
        return True
    base = f"v0:{timestamp}:".encode() + body
    expected = "v0=" + hmac.new(secret.encode(), base, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


# ═══════════════════════════════════════════════════════════════
# CLI 命令
# ═══════════════════════════════════════════════════════════════

def cmd_serve(args, config: dict) -> int:
    """启动 Webhook HTTP 服务器"""
    try:
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import threading
    except ImportError:
        log.error("需要 http.server: python3 -m http.server 8080")
        return 1

    port = args.port or config.get("webhook_transforms", {}).get("server", {}).get("port", 8080)
    dry_run = config.get("webhook_transforms", {}).get("general", {}).get("dry_run", False)
    brain_path = get_brain_path(config)
    writer = BrainWriter(brain_path, dry_run=dry_run)

    class WebhookHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                if content_length > config.get("webhook_transforms", {}).get("security", {}).get("max_payload_size", 10485760):
                    self.send_error(413, "Payload too large")
                    return
                body = self.rfile.read(content_length)
                source = self.path.lstrip("/").split("/")[0] or "github"

                # GitHub 签名验证
                if source == "github":
                    sig = self.headers.get("X-Hub-Signature-256", "")
                    secret = config.get("webhook_transforms", {}).get("github", {}).get("secret", "")
                    secret = os.path.expandvars(secret) if secret.startswith("${") else secret
                    if config.get("webhook_transforms", {}).get("security", {}).get("verify_signatures", True):
                        if secret and not verify_github_signature(body, sig, secret):
                            log.warning("GitHub 签名验证失败")
                            self.send_error(403, "Invalid signature")
                            return

                event_type = self.headers.get("X-GitHub-Event", "push")
                if source == "slack":
                    event_type = self.headers.get("X-Slack-Signature", "")

                payload = json.loads(body)
                updates = dispatch_transform(source, event_type, payload, config)

                for update in updates:
                    writer.write_update(update)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "updates": len(updates)}).encode())
                log.info(f"处理 {len(updates)} 条更新")
            except Exception as e:
                log.error(f"处理请求失败: {e}")
                self.send_error(500, str(e))

        def log_message(self, format, *args):
            log.info(format % args)

    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    log.info(f"Webhook 服务器启动: http://0.0.0.0:{port}")
    log.info(f"端点: POST /webhook/<source>")
    server.serve_forever()


def cmd_test(args, config: dict) -> int:
    """发送测试 Webhook 事件"""
    source = args.source
    event = args.event

    if source == "github":
        payload = {
            "repository": {"full_name": "test/repo"},
            "commits": [{
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "author": {"name": "Test Author"},
                "message": "Test commit message",
                "url": "https://github.com/test/repo/commit/abc123",
            }],
        }
        event_type = event or "push"
    elif source == "slack":
        payload = {
            "channel": {"name": "general"},
            "user": {"name": "test-user"},
            "text": "Test message",
            "ts": str(time.time()),
        }
        event_type = "message"
    elif source == "rss":
        payload = {
            "title": "Test RSS Entry",
            "link": "https://example.com/test",
            "published": datetime.now(timezone.utc).isoformat(),
            "summary": "This is a test RSS entry for webhook transforms.",
        }
        event_type = "new_entry"
    else:
        log.error(f"未知 source: {source}")
        return 1

    dry_run = True
    brain_path = get_brain_path(config)
    writer = BrainWriter(brain_path, dry_run=dry_run)
    updates = dispatch_transform(source, event_type, payload, config)

    for update in updates:
        writer.write_update(update)

    log.info(f"测试完成，生成 {len(updates)} 条更新")
    return 0


def cmd_list(args, config: dict) -> int:
    """列出已注册的 Webhook 源"""
    wt = config.get("webhook_transforms", {})
    github = wt.get("github", {})
    slack = wt.get("slack", {})
    rss = wt.get("rss", {})

    print("已注册的 Webhook 源:")
    print(f"  GitHub: {len(github.get('allowed_repos', []))} repos, events: {', '.join(github.get('event_transforms', {}).keys())}")
    print(f"  Slack: {len(slack.get('allowed_channels', []))} channels")
    print(f"  RSS: {len(rss.get('feeds', []))} feeds")
    print(f"  通用: dry_run={wt.get('general', {}).get('dry_run', False)}")
    return 0


def cmd_sync(args, config: dict) -> int:
    """手动触发 RSS 同步"""
    import urllib.request
    import xml.etree.ElementTree as ET

    feed_url = args.feed
    if not feed_url:
        log.error("--feed 必须指定 RSS URL")
        return 1

    try:
        with urllib.request.urlopen(feed_url, timeout=10) as resp:
            data = resp.read()
        root = ET.fromstring(data)
        feed_slug = re.sub(r"[^\w]", "-", feed_url.split("//")[1].split("/")[0]).lower()

        entries = []
        for item in root.iter("item")[:20]:
            entries.append({
                "title": (item.findtext("title") or "").strip(),
                "link": (item.findtext("link") or "").strip(),
                "published": (item.findtext("pubDate") or datetime.now(timezone.utc).isoformat()),
                "summary": (item.findtext("description") or "")[:500],
            })

        brain_path = get_brain_path(config)
        writer = BrainWriter(brain_path, dry_run=config.get("webhook_transforms", {}).get("general", {}).get("dry_run", False))

        count = 0
        for entry in entries:
            updates = transform_rss_entry(entry, config, feed_slug)
            for update in updates:
                if writer.write_update(update):
                    count += 1

        log.info(f"RSS 同步完成: {count} 条更新 (来自 {feed_url})")
        return 0
    except Exception as e:
        log.error(f"RSS 同步失败: {e}")
        return 1


def cmd_transform(args, config: dict) -> int:
    """Transform 测试（不写入）"""
    if args.payload and args.payload.startswith("@"):
        file_path = Path(args.payload[1:])
        if not file_path.is_absolute():
            file_path = Path.cwd() / file_path
        with open(file_path, encoding="utf-8") as f:
            payload = json.load(f)
    else:
        payload = json.loads(args.payload or "{}")

    source = args.source
    event_type = args.event or "push"

    dry_run = True
    brain_path = get_brain_path(config)
    writer = BrainWriter(brain_path, dry_run=dry_run)
    updates = dispatch_transform(source, event_type, payload, config)

    for update in updates:
        if not args.dry_run:
            writer.write_update(update)
        print(f"  {update.entity_type}/{update.slug}")
        print(f"    title: {update.frontmatter.get('title', 'N/A')}")
        print(f"    tags: {update.frontmatter.get('tags', [])}")

    log.info(f"Transform 完成: {len(updates)} 条更新")
    return 0


def cmd_add(args, config: dict) -> int:
    """添加新的 Webhook 源"""
    log.info(f"添加 Webhook 源: {args.source}, events: {args.events}")
    # 简化实现：写入配置
    log.info("请手动更新 config.yaml 添加 Webhook 配置")
    return 0


def cmd_remove(args, config: dict) -> int:
    """移除 Webhook 源"""
    log.info(f"移除 Webhook 源: {args.source}")
    log.info("请手动从 config.yaml 中删除 Webhook 配置")
    return 0


# ═══════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="GBrain Webhook Transforms")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # serve
    p_serve = sub.add_parser("serve", help="启动 Webhook 服务器")
    p_serve.add_argument("--port", type=int, help="监听端口")
    p_serve.set_defaults(func=cmd_serve)

    # test
    p_test = sub.add_parser("test", help="发送测试 Webhook 事件")
    p_test.add_argument("--source", choices=["github", "slack", "rss"], required=True)
    p_test.add_argument("--event", help="事件类型")
    p_test.set_defaults(func=cmd_test)

    # list
    p_list = sub.add_parser("list", help="列出已注册的 Webhook")
    p_list.set_defaults(func=cmd_list)

    # sync
    p_sync = sub.add_parser("sync", help="手动触发 RSS 同步")
    p_sync.add_argument("--source", default="rss")
    p_sync.add_argument("--feed", help="RSS feed URL")
    p_sync.set_defaults(func=cmd_sync)

    # transform
    p_t = sub.add_parser("transform", help="Transform 测试")
    p_t.add_argument("--source", required=True)
    p_t.add_argument("--event", help="事件类型")
    p_t.add_argument("--payload", help="JSON payload 或 @file.json")
    p_t.add_argument("--dry-run", action="store_true", default=True)
    p_t.set_defaults(func=cmd_transform)

    # add
    p_add = sub.add_parser("add", help="添加 Webhook 源")
    p_add.add_argument("--source", required=True)
    p_add.add_argument("--events", required=True)
    p_add.add_argument("--transform", default="standard")
    p_add.set_defaults(func=cmd_add)

    # remove
    p_rm = sub.add_parser("remove", help="移除 Webhook 源")
    p_rm.add_argument("--source", required=True)
    p_rm.set_defaults(func=cmd_remove)

    args = parser.parse_args()
    config = load_config()
    if not config.get("webhook_transforms", {}).get("enabled", True):
        log.error("webhook_transforms 在配置中已禁用")
        return 1
    return args.func(args, config)


if __name__ == "__main__":
    sys.exit(main())
