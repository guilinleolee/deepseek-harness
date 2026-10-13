#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""notify_email.py · skill-updater V1.1 增量 · SMTP 邮件通知

环境变量配置（SMTP）：
  SMTP_HOST        SMTP 服务器（如 smtp.gmail.com）
  SMTP_PORT        SMTP 端口（默认 587）
  SMTP_USER        SMTP 用户名（发件邮箱）
  SMTP_PASS        SMTP 密码 / 应用专用密码
  SMTP_TLS         1=STARTTLS（默认）/ 0=不加密
  NOTIFY_FROM      发件人（默认 SMTP_USER）
  NOTIFY_TO        收件人（多个用 , 分隔，必填）

用法：
  python scripts/notify_email.py --subject "test" --body "hello"
  python scripts/notify_email.py --subject "..." --body "..." --html  # HTML 格式

退出码：0=发送成功 / 1=发送失败 / 2=配置缺失
"""
import sys, os, io, argparse, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 stdout on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def send_email(subject: str, body: str, html: bool = False) -> int:
    """发邮件，返回 0=成功 1=失败 2=配置缺失"""
    # 1. 读环境变量
    host = os.environ.get("SMTP_HOST", "").strip()
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER", "").strip()
    pwd = os.environ.get("SMTP_PASS", "").strip()
    use_tls = os.environ.get("SMTP_TLS", "1").strip() == "1"
    sender = os.environ.get("NOTIFY_FROM", user).strip()
    recipients = [r.strip() for r in os.environ.get("NOTIFY_TO", "").split(",") if r.strip()]

    # 2. 校验
    if not all([host, user, pwd, sender, recipients]):
        print(
            f"⚠️  邮件配置缺失（需 SMTP_HOST/PORT/USER/PASS/NOTIFY_TO）",
            file=sys.stderr
        )
        return 2

    # 3. 组装邮件
    msg = MIMEMultipart("alternative") if html else MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg["Date"] = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    if html:
        part1 = MIMEText(body, "plain", "utf-8")
        html_body = body.replace("\n", "<br>")
        part2 = MIMEText(f"<html><body><pre>{html_body}</pre></body></html>", "html", "utf-8")
        msg.attach(part1)
        msg.attach(part2)

    # 4. 发邮件
    try:
        print(f"📧 发邮件到 {recipients}（{host}:{port}）", file=sys.stderr)
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.ehlo()
            if use_tls:
                smtp.starttls()
                smtp.ehlo()
            smtp.login(user, pwd)
            smtp.sendmail(sender, recipients, msg.as_string())
        print(f"✅ 邮件已发送", file=sys.stderr)
        return 0
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP 认证失败: {e}（检查 SMTP_USER / SMTP_PASS）", file=sys.stderr)
        return 1
    except smtplib.SMTPException as e:
        print(f"❌ SMTP 错误: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(description="天龙引擎 skill-updater 邮件通知")
    parser.add_argument("--subject", required=True, help="邮件主题")
    parser.add_argument("--body", required=True, help="邮件正文")
    parser.add_argument("--html", action="store_true", help="HTML 格式（默认纯文本）")
    args = parser.parse_args()

    rc = send_email(args.subject, args.body, args.html)
    sys.exit(rc)


if __name__ == "__main__":
    main()
