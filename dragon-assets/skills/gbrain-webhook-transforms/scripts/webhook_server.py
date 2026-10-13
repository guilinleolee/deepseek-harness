#!/usr/bin/env python3
"""
GBrain Webhook Server — HTTP 服务器封装

提供独立的 Webhook 接收服务，支持多源 Webhook 处理。
可作为独立进程运行或集成到现有 Flask/FastAPI 应用。

Usage:
    python webhook_server.py --port 8080 --config ../config.yaml
    python webhook_server.py --daemon --pid /tmp/webhook.pid
    python webhook_server.py --status --pid /tmp/webhook.pid
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Callable

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from webhook_transforms import (
    load_config,
    get_brain_path,
    BrainWriter,
    dispatch_transform,
    verify_github_signature,
    verify_slack_signature,
    TransformResult,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stdout)
log = logging.getLogger("webhook_server")


class WebhookRouter:
    """Webhook 路由器"""

    def __init__(self, config: dict):
        self.config = config
        self.brain_path = get_brain_path(config)
        self.dry_run = config.get("webhook_transforms", {}).get("general", {}).get("dry_run", False)
        self.writer = BrainWriter(self.brain_path, dry_run=self.dry_run)
        self.stats = {"received": 0, "processed": 0, "errors": 0}

    def route(self, source: str, event_type: str, payload: dict) -> TransformResult:
        """路由并处理 Webhook"""
        start = time.time()
        self.stats["received"] += 1
        try:
            updates = dispatch_transform(source, event_type, payload, self.config)
            for update in updates:
                self.writer.write_update(update)
            duration = (time.time() - start) * 1000
            self.stats["processed"] += 1
            return TransformResult(success=True, updates=updates, duration_ms=duration)
        except Exception as e:
            self.stats["errors"] += 1
            log.error(f"处理失败: {e}")
            return TransformResult(success=False, errors=[str(e)], duration_ms=(time.time() - start) * 1000)


class WebhookHandler(BaseHTTPRequestHandler):
    """HTTP 请求处理器"""

    router: WebhookRouter = None

    def do_POST(self):
        if not self.router:
            self.send_error(500, "Router not initialized")
            return

        # 安全检查
        max_size = self.router.config.get("webhook_transforms", {}).get("security", {}).get("max_payload_size", 10485760)
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > max_size:
            self.send_error(413, "Payload too large")
            return

        # 路径解析
        path = self.path.lstrip("/")
        if path.startswith("webhook/"):
            source = path.split("/")[1] if len(path.split("/")) > 1 else "custom"
        else:
            source = "custom"

        # 读取 body
        body = self.rfile.read(content_length)

        # 签名验证
        if not self._verify_signature(source, body):
            self.send_error(403, "Invalid signature")
            return

        # 事件类型
        if source == "github":
            event_type = self.headers.get("X-GitHub-Event", "push")
        elif source == "slack":
            event_type = "message"
        else:
            event_type = self.headers.get("X-Event-Type", "unknown")

        # 处理
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as e:
            self.send_error(400, f"Invalid JSON: {e}")
            return

        result = self.router.route(source, event_type, payload)

        self.send_response(200 if result.success else 500)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Webhook-Stats", json.dumps(self.router.stats))
        self.end_headers()
        response = {
            "success": result.success,
            "updates": len(result.updates),
            "duration_ms": result.duration_ms,
            "errors": result.errors,
        }
        self.wfile.write(json.dumps(response).encode())

    def do_GET(self):
        """健康检查和状态端点"""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            stats = self.router.stats if self.router else {}
            self.wfile.write(json.dumps({"status": "ok", "stats": stats}).encode())
        elif self.path == "/stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(self.router.stats if self.router else {}).encode())
        else:
            self.send_response(404)

    def _verify_signature(self, source: str, body: bytes) -> bool:
        """验证 Webhook 签名"""
        security = self.router.config.get("webhook_transforms", {}).get("security", {})
        if not security.get("verify_signatures", True):
            return True

        if source == "github":
            sig = self.headers.get("X-Hub-Signature-256", "")
            secret = self.router.config.get("webhook_transforms", {}).get("github", {}).get("secret", "")
            secret = os.path.expandvars(secret) if secret.startswith("${") else secret
            if secret:
                return verify_github_signature(body, sig, secret)

        elif source == "slack":
            sig = self.headers.get("X-Slack-Signature", "")
            ts = self.headers.get("X-Slack-Request-Timestamp", "")
            secret = self.router.config.get("webhook_transforms", {}).get("slack", {}).get("signing_secret", "")
            secret = os.path.expandvars(secret) if secret.startswith("${") else secret
            if secret and ts:
                return verify_slack_signature(body, ts, sig, secret)

        return True

    def log_message(self, format, *args):
        log.info(format % args)


def start_server(port: int, config: dict, daemon: bool = False, pid_file: str = ""):
    """启动服务器"""
    router = WebhookRouter(config)
    WebhookHandler.router = router

    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    log.info(f"Webhook Server 启动: http://0.0.0.0:{port}")
    log.info(f"端点: POST /webhook/<source>, GET /health, GET /stats")
    log.info(f"Dry run: {router.dry_run}")

    if daemon and pid_file:
        pid = os.fork()
        if pid > 0:
            Path(pid_file).write_text(str(pid))
            log.info(f"PID: {pid}")
            return
        os.setsid()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("服务器停止")
        server.shutdown()


def stop_server(pid_file: str):
    """停止守护进程"""
    if not Path(pid_file).exists():
        log.error(f"PID 文件不存在: {pid_file}")
        return 1
    pid = int(Path(pid_file).read_text().strip())
    try:
        os.kill(pid, signal.SIGTERM)
        log.info(f"已发送 SIGTERM 到 PID {pid}")
        Path(pid_file).unlink()
        return 0
    except ProcessLookupError:
        log.error(f"进程不存在: {pid}")
        Path(pid_file).unlink()
        return 1


def status_server(pid_file: str):
    """查看服务器状态"""
    if not Path(pid_file).exists():
        print("服务器未运行")
        return 1
    pid = int(Path(pid_file).read_text().strip())
    try:
        os.kill(pid, 0)
        print(f"服务器运行中, PID: {pid}")
        return 0
    except ProcessLookupError:
        print("服务器未运行 (stale PID file)")
        Path(pid_file).unlink()
        return 1


def main():
    parser = argparse.ArgumentParser(description="GBrain Webhook Server")
    parser.add_argument("--port", type=int, default=8080, help="监听端口")
    parser.add_argument("--config", type=Path, help="配置文件路径")
    parser.add_argument("--daemon", action="store_true", help="守护进程模式")
    parser.add_argument("--pid", default="/tmp/webhook_server.pid", help="PID 文件路径")
    parser.add_argument("--stop", action="store_true", help="停止服务器")
    parser.add_argument("--status", action="store_true", help="查看服务器状态")
    args = parser.parse_args()

    if args.stop:
        return stop_server(args.pid)
    if args.status:
        return status_server(args.pid)

    config_path = args.config or Path(__file__).parent.parent / "config.yaml"
    config = load_config(config_path)
    if not config.get("webhook_transforms", {}).get("enabled", True):
        log.error("webhook_transforms 已禁用")
        return 1

    port = args.port or config.get("webhook_transforms", {}).get("server", {}).get("port", 8080)
    start_server(port, config, daemon=args.daemon, pid_file=args.pid)


if __name__ == "__main__":
    sys.exit(main())
