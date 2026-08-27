#!/usr/bin/env python3
"""
notify.py — skill-updater 告警推送器
读 reports/*.json (skill-updater 生成),把 yellow/red 的 skill 转成
飞书 / Slack / 企业微信 webhook 消息。

Usage:
    # 推送最新一份报告
    python scripts/notify.py feishu    # 或 slack / wechat
    python scripts/notify.py slack --report reports/report-20260721-091846.json

    # dry-run（只打不推）
    python scripts/notify.py feishu --dry-run

Environment:
    FEISHU_WEBHOOK_URL    飞书机器人 webhook
    SLACK_WEBHOOK_URL     Slack incoming webhook
    WECHAT_WEBHOOK_URL    企业微信机器人 webhook
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def load_latest_report(reports_dir: Path, specific: str | None = None) -> Path:
    """加载最新的 .json 报告(或用户指定的)。"""
    if specific:
        p = Path(specific)
        if not p.exists():
            sys.exit(f"ERROR: report not found: {p}")
        return p
    json_files = sorted(reports_dir.glob("report-*.json"), reverse=True)
    if not json_files:
        sys.exit(f"ERROR: no report-*.json found in {reports_dir}")
    return json_files[0]


def extract_alerts(report_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """从 report 抽出 yellow + red 的 skill。"""
    with open(report_path, encoding="utf-8") as f:
        data = json.load(f)
    yellows, reds = [], []
    for item in data.get("items", []):
        level = item.get("verdict", {}).get("level")
        if level == "yellow":
            yellows.append(item)
        elif level == "red":
            reds.append(item)
    return yellows, reds


# ---------- 飞书 ----------

def format_feishu(yellows: list, reds: list, scan_root: str) -> dict[str, Any]:
    """构造飞书消息 (interactive card)。"""
    blocks = [
        {"tag": "div", "text": {"tag": "lark_md",
                                  "content": f"**天龙 skill-updater 告警** · 扫描根 `{scan_root}`"}},
    ]
    if reds:
        rows = []
        for r in reds:
            s = r["skill"]; v = r["verdict"]
            rows.append(f"🔴 **{s['name']}** · {v['reason']}")
        blocks.append({"tag": "div", "text": {"tag": "lark_md",
                  "content": "**🔴 必读告警（{} 条）**\n{}".format(len(reds), "\n".join(rows))}})
    if yellows:
        rows = []
        for y in yellows:
            s = y["skill"]; v = y["verdict"]
            r = y.get("remote", {})
            head = r.get("remote", {}).get("head_sha") if r else "-"
            lic = r.get("remote", {}).get("license_spdx") if r else "-"
            rows.append(f"🟡 **{s['name']}** · head=`{head}` · license=`{lic}` · {v['reason']}")
        blocks.append({"tag": "div", "text": {"tag": "lark_md",
                  "content": "**🟡 推荐 review（{} 条）**\n{}".format(len(yellows), "\n".join(rows))}})
    if not yellows and not reds:
        blocks.append({"tag": "div", "text": {"tag": "lark_md",
                      "content": "✅ **全绿,无需告警**"}})
    return {
        "msg_type": "interactive",
        "card": {
            "header": {"title": {"tag": "plain_text",
                                "content": "天龙 skill-updater"}, "template": "red"},
            "elements": blocks,
        },
    }


# ---------- Slack ----------

def format_slack(yellows: list, reds: list, scan_root: str) -> dict[str, Any]:
    """构造 Slack incoming webhook payload (Block Kit 简化版)。"""
    blocks = [
        {"type": "section", "text": {"type": "mrkdwn",
            "text": f"*天龙 skill-updater 告警* · 扫描根 `{scan_root}`"}},
    ]
    if reds:
        lines = [f"🔴 *{r['skill']['name']}* — {r['verdict']['reason']}" for r in reds]
        blocks.append({"type": "section", "text": {"type": "mrkdwn",
            "text": "*🔴 必读告警 ({} 条)*\n{}".format(len(reds), "\n".join(lines))}})
    if yellows:
        lines = [f"🟡 *{y['skill']['name']}* — {y['verdict']['reason']}" for y in yellows]
        blocks.append({"type": "section", "text": {"type": "mrkdwn",
            "text": "*🟡 推荐 review ({} 条)*\n{}".format(len(yellows), "\n".join(lines))}})
    if not yellows and not reds:
        blocks.append({"type": "section", "text": {"type": "mrkdwn",
            "text": "✅ *全绿,无需告警*"}})
    return {"text": "天龙 skill-updater 告警", "blocks": blocks}


# ---------- 企业微信 ----------

def format_wechat(yellows: list, reds: list, scan_root: str) -> dict[str, Any]:
    """构造企业微信机器人 markdown 消息。"""
    lines = [f"## 天龙 skill-updater 告警", f"> 扫描根: `{scan_root}`", ""]
    if reds:
        lines.append(f"### 🔴 必读告警 ({len(reds)} 条)")
        for r in reds:
            lines.append(f"- **{r['skill']['name']}** — {r['verdict']['reason']}")
        lines.append("")
    if yellows:
        lines.append(f"### 🟡 推荐 review ({len(yellows)} 条)")
        for y in yellows:
            lines.append(f"- **{y['skill']['name']}** — {y['verdict']['reason']}")
        lines.append("")
    if not yellows and not reds:
        lines.append("✅ **全绿,无需告警**")
    return {"msgtype": "markdown", "markdown": {"content": "\n".join(lines)}}


# ---------- 推送 ----------

def post_webhook(url: str, payload: dict[str, Any], dry_run: bool) -> tuple[int, str]:
    """POST webhook。返回 (http_status, body)。"""
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if dry_run:
        return 0, f"[dry-run] payload:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json",
        "User-Agent": "skill-updater/1.0 notify",
    }, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace") if e.fp else str(e)
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return -1, str(e)


def main() -> int:
    parser = argparse.ArgumentParser(description="skill-updater 告警推送器")
    parser.add_argument("channel", choices=["feishu", "slack", "wechat"],
                        help="推送渠道:feishu / slack / wechat")
    parser.add_argument("--report", help="指定 report JSON 路径(默认最新一份)")
    parser.add_argument("--reports-dir", default="reports", help="reports 目录")
    parser.add_argument("--dry-run", action="store_true", help="只打 payload 不真推")
    parser.add_argument("--webhook-url", help="覆盖环境变量,直接给 webhook URL")
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parent.parent
    reports_dir = (skill_dir / args.reports_dir).resolve()
    report_path = load_latest_report(reports_dir, args.report)
    print(f"[notify] 读报告: {report_path}", file=sys.stderr)

    with open(report_path, encoding="utf-8") as f:
        full = json.load(f)
    scan_root = full.get("scan_roots", [{}])[0].get("root", "?") if full.get("scan_roots") else "?"
    yellows, reds = extract_alerts(report_path)
    print(f"[notify] 检出: {len(reds)} 🔴 + {len(yellows)} 🟡", file=sys.stderr)

    if args.channel == "feishu":
        url = args.webhook_url or os.environ.get("FEISHU_WEBHOOK_URL")
        if not url and not args.dry_run:
            sys.exit("ERROR: 需设 FEISHU_WEBHOOK_URL 环境变量,或加 --webhook-url,或 --dry-run")
        payload = format_feishu(yellows, reds, scan_root)
    elif args.channel == "slack":
        url = args.webhook_url or os.environ.get("SLACK_WEBHOOK_URL")
        if not url and not args.dry_run:
            sys.exit("ERROR: 需设 SLACK_WEBHOOK_URL 环境变量,或加 --webhook-url,或 --dry-run")
        payload = format_slack(yellows, reds, scan_root)
    else:  # wechat
        url = args.webhook_url or os.environ.get("WECHAT_WEBHOOK_URL")
        if not url and not args.dry_run:
            sys.exit("ERROR: 需设 WECHAT_WEBHOOK_URL 环境变量,或加 --webhook-url,或 --dry-run")
        payload = format_wechat(yellows, reds, scan_root)

    status, body = post_webhook(url, payload, args.dry_run)
    if args.dry_run:
        print(body)
        return 0
    print(f"[notify] POST → {args.channel} → HTTP {status}", file=sys.stderr)
    if status < 200 or status >= 300:
        print(f"[notify] 推送失败: {body}", file=sys.stderr)
        return 1
    print(f"[notify] 推送成功: {body[:200]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())