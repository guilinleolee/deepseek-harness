#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_cec_ticket.py · 天龙引擎 /cec-ticket 命令包装脚本
=========================================================

把天龙 commands/cec-ticket.md 的 9 个子命令包装为命令行：
- pool-init <客户>    初始化客户工单池
- list <客户>         列出工单
- status <ticket_id>  查看工单详情
- update <ticket_id> --status {backlog|in_progress|review|completed|cancelled}
- assign <ticket_id> <agent>
- history <ticket_id>  查看历史
- dashboard <客户>    健康度仪表盘
- flow <客户>         完整工单流
- create <客户> <title> 手动创建工单

调用：
    python scripts/run_cec_ticket.py pool-init dragon-engine-v1
    python scripts/run_cec_ticket.py list dragon-engine-v1
    python scripts/run_cec_ticket.py status T-2026-08-10-001
    python scripts/run_cec_ticket.py update T-2026-08-10-001 --status completed
    python scripts/run_cec_ticket.py dashboard dragon-engine-v1

输出：
    ~/customers/{customer}/tickets/ 目录操作
    ~/customers/{customer}/health/dashboard.md 联动更新

仅用 Python 标准库（argparse / pathlib / re / json）。
要求 Python ≥ 3.8（已与项目兼容）。
"""
from __future__ import annotations

import argparse
import sys
import re
from pathlib import Path
from datetime import datetime

# Windows GBK 兼容：强制 UTF-8 输出
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


SCRIPT_DIR = Path(__file__).resolve().parent
DRAGON_ROOT = SCRIPT_DIR.parent

# Windows 兼容：处理 home directory 找不到的情况
def _get_home_dir() -> Path:
    """获取用户主目录，多重 fallback"""
    try:
        home = Path.home()
        if home and home.exists():
            return home
    except (RuntimeError, ValueError):
        pass

    userprofile = os.environ.get("USERPROFILE")
    if userprofile and Path(userprofile).exists():
        return Path(userprofile)

    home_env = os.environ.get("HOME")
    if home_env and Path(home_env).exists():
        return Path(home_env)

    drive = os.environ.get("HOMEDRIVE")
    path = os.environ.get("HOMEPATH")
    if drive and path:
        combined = Path(drive + path)
        if combined.exists():
            return combined

    fallback = Path("C:/Users/li")
    if fallback.exists():
        return fallback

    return Path(os.environ.get("TEMP", "C:/Windows/Temp"))


HOME_DIR = _get_home_dir()
CUSTOMERS_DIR = HOME_DIR / "customers"

# 工单状态枚举（天龙 v1.5 数据模型）
VALID_STATUSES = ["backlog", "in_progress", "review", "completed", "cancelled"]
VALID_PRIORITIES = ["low", "medium", "high", "urgent"]

# FDE 阶段 → 默认 assignee agent 映射
STAGE_AGENT_MAP = {
    "land": "39-forward-deployed-engineer",
    "discover": "39-forward-deployed-engineer",
    "plan": "02-architect",
    "build": "03-builder",
    "ship": "16-devops",
    "close": "41-customer-success-architect",
}

NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="天龙引擎 /cec-ticket 命令包装脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
子命令：
  pool-init <客户>            初始化客户工单池
  list <客户> [--status X]    列出工单
  status <ticket_id>          查看工单详情
  update <ticket_id> --status X
  assign <ticket_id> <agent>
  history <ticket_id>         查看历史
  dashboard <客户>            健康度仪表盘
  flow <客户>                 完整工单流
  create <客户> <title> [--stage X] [--priority X] [--assignee X]
        """,
    )

    subparsers = parser.add_subparsers(dest="action", help="子命令")

    # pool-init
    p_pool = subparsers.add_parser("pool-init", help="初始化客户工单池")
    p_pool.add_argument("customer", help="客户名")

    # list
    p_list = subparsers.add_parser("list", help="列出工单")
    p_list.add_argument("customer", help="客户名")
    p_list.add_argument("--status", choices=VALID_STATUSES, help="按状态过滤")

    # status
    p_status = subparsers.add_parser("status", help="查看工单详情")
    p_status.add_argument("ticket_id", help="工单 ID")

    # update
    p_update = subparsers.add_parser("update", help="更新工单状态")
    p_update.add_argument("ticket_id", help="工单 ID")
    p_update.add_argument("--status", required=True, choices=VALID_STATUSES, help="新状态")
    p_update.add_argument("--reason", help="取消原因（仅 cancelled）")

    # assign
    p_assign = subparsers.add_parser("assign", help="分配工单")
    p_assign.add_argument("ticket_id", help="工单 ID")
    p_assign.add_argument("agent", help="天龙 agent 名")

    # history
    p_history = subparsers.add_parser("history", help="查看工单历史")
    p_history.add_argument("ticket_id", help="工单 ID")

    # dashboard
    p_dash = subparsers.add_parser("dashboard", help="健康度仪表盘")
    p_dash.add_argument("customer", help="客户名")

    # flow
    p_flow = subparsers.add_parser("flow", help="完整工单流")
    p_flow.add_argument("customer", help="客户名")

    # create
    p_create = subparsers.add_parser("create", help="手动创建工单")
    p_create.add_argument("customer", help="客户名")
    p_create.add_argument("title", help="工单标题")
    p_create.add_argument("--stage", help="FDE 阶段", choices=list(STAGE_AGENT_MAP.keys()))
    p_create.add_argument("--priority", default="medium", choices=VALID_PRIORITIES, help="优先级")
    p_create.add_argument("--assignee", help="天龙 agent 名")

    return parser.parse_args()


def cmd_pool_init(customer: str) -> int:
    """初始化客户工单池"""
    base = CUSTOMERS_DIR / customer
    if not base.exists():
        print(f"❌ 客户目录不存在：{base}")
        print(f"   请先运行: python scripts/run_onboard.py {customer}")
        return 1

    ticket_dirs = [
        base / "tickets",
        base / "tickets" / "backlog",
        base / "tickets" / "in-progress",
        base / "tickets" / "review",
        base / "tickets" / "completed",
        base / "tickets" / "cancelled",
    ]
    for d in ticket_dirs:
        d.mkdir(parents=True, exist_ok=True)

    # 创建 tickets/index.md
    index_path = base / "tickets" / "index.md"
    if not index_path.exists():
        index_path.write_text(
            f"""# {customer} - 工单池索引

> 创建时间：{datetime.now().strftime("%Y-%m-%d")}

## 工单池结构

```
~/customers/{customer}/tickets/
├── backlog/      # 待办
├── in-progress/  # 进行中
├── review/       # 复核
├── completed/    # 已完成
└── cancelled/    # 已取消
```

## 工单统计

| 状态 | 数量 |
|---|---|
| backlog | 0 |
| in-progress | 0 |
| review | 0 |
| completed | 0 |
| cancelled | 0 |

## 工单索引

（运行后自动追加）
""",
            encoding="utf-8",
        )

    print(f"✅ 工单池已初始化：{base / 'tickets'}")
    return 0


def scan_tickets(customer: str, status_filter: str = None) -> list[Path]:
    """扫描客户目录下所有工单文件"""
    base = CUSTOMERS_DIR / customer / "tickets"
    if not base.exists():
        return []

    tickets = []
    for status in VALID_STATUSES:
        if status_filter and status != status_filter:
            continue
        status_dir = base / status
        if status_dir.exists():
            for f in sorted(status_dir.glob("*.md")):
                tickets.append(f)
    return tickets


def cmd_list(customer: str, status: str = None) -> int:
    """列出工单"""
    tickets = scan_tickets(customer, status_filter=status)
    if not tickets:
        print(f"📭 {customer} 暂无工单")
        return 0

    print(f"📋 {customer} 工单池（{len(tickets)} 个）")
    if status:
        print(f"   过滤: {status}")
    print()
    for t in tickets:
        # 提取状态 + ID + 标题
        rel = t.relative_to(t.parent.parent)
        print(f"  [{rel.parent.name}] {t.stem}")
    return 0


def parse_frontmatter(content: str) -> dict[str, str]:
    """解析 markdown frontmatter"""
    if not content.startswith("---"):
        return {}
    end = content.find("\n---", 3)
    if end == -1:
        return {}
    fm = {}
    for line in content[3:end].strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            fm[key.strip()] = value.strip()
    return fm


def find_ticket_path(ticket_id: str) -> Path | None:
    """在天龙所有客户目录中查找工单"""
    for status in VALID_STATUSES:
        for customer_dir in CUSTOMERS_DIR.iterdir():
            if not customer_dir.is_dir():
                continue
            tickets_dir = customer_dir / "tickets" / status
            if not tickets_dir.exists():
                continue
            for f in tickets_dir.glob(f"{ticket_id}.md"):
                return f
    return None


def cmd_status(ticket_id: str) -> int:
    """查看工单详情"""
    ticket_path = find_ticket_path(ticket_id)
    if not ticket_path:
        print(f"❌ 工单未找到：{ticket_id}")
        return 1

    content = ticket_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)
    print(f"📋 工单详情")
    print(f"=" * 50)
    for key in ["ticket_id", "title", "status", "priority", "assignee_agent",
                "fde_stage", "customer", "created_at", "updated_at"]:
        if key in fm:
            print(f"  {key}: {fm[key]}")
    print(f"=" * 50)
    print(f"  路径: {ticket_path}")
    return 0


def cmd_update(ticket_id: str, status: str, reason: str = None) -> int:
    """更新工单状态（触发 ticket-health-bridge hook 逻辑）"""
    ticket_path = find_ticket_path(ticket_id)
    if not ticket_path:
        print(f"❌ 工单未找到：{ticket_id}")
        return 1

    content = ticket_path.read_text(encoding="utf-8")
    # 解析 frontmatter
    if not content.startswith("---"):
        print(f"❌ 工单格式错误（无 frontmatter）")
        return 1

    end = content.find("\n---", 3)
    fm_text = content[3:end]
    body = content[end + 4:]

    # 构造新 frontmatter
    new_lines = []
    for line in fm_text.strip().split("\n"):
        if line.startswith("status:"):
            new_lines.append(f"status: {status}")
        elif line.startswith("updated_at:"):
            new_lines.append(f"updated_at: {datetime.now().isoformat()}")
        else:
            new_lines.append(line)

    # 取消原因
    if status == "cancelled" and reason:
        if "cancel_reason:" not in "\n".join(new_lines):
            new_lines.append(f"cancel_reason: \"{reason}\"")

    # 历史记录
    timestamp = datetime.now().isoformat()
    history_entry = f"\n- {timestamp} - 状态变更 → {status}"
    if status == "cancelled" and reason:
        history_entry += f"（{reason}）"
    new_body = body.rstrip() + history_entry + "\n"

    new_content = "---\n" + "\n".join(new_lines) + "\n---\n" + new_body

    # 移动到对应状态目录
    customer_dir = ticket_path.parent.parent.parent
    new_status_dir = customer_dir / "tickets" / status
    new_status_dir.mkdir(parents=True, exist_ok=True)
    new_path = new_status_dir / ticket_path.name

    ticket_path.unlink()
    new_path.write_text(new_content, encoding="utf-8")

    print(f"✅ 工单已更新：{ticket_id} → {status}")
    print(f"   新路径：{new_path}")
    print(f"\n💡 提示：天龙 v1.5 ticket-health-bridge hook 会自动联动健康度仪表盘")
    return 0


def cmd_dashboard(customer: str) -> int:
    """查看健康度仪表盘"""
    dashboard_path = CUSTOMERS_DIR / customer / "health" / "dashboard.md"
    if not dashboard_path.exists():
        print(f"❌ 健康度仪表盘不存在：{dashboard_path}")
        return 1

    print(f"📊 {customer} 健康度仪表盘")
    print("=" * 60)
    print(dashboard_path.read_text(encoding="utf-8"))
    return 0


def cmd_create(customer: str, title: str, stage: str = None,
               priority: str = "medium", assignee: str = None) -> int:
    """手动创建工单"""
    base = CUSTOMERS_DIR / customer / "tickets"
    if not base.exists():
        print(f"❌ 工单池未初始化：{base}")
        print(f"   请先运行: python scripts/run_cec_ticket.py pool-init {customer}")
        return 1

    # 生成工单 ID
    today = datetime.now().strftime("%Y-%m-%d")
    seq = len(list((base / "backlog").glob("*.md"))) + 1
    ticket_id = f"T-{today}-{seq:05d}"

    # 默认 assignee
    if not assignee and stage:
        assignee = STAGE_AGENT_MAP.get(stage, "39-forward-deployed-engineer")
    elif not assignee:
        assignee = "39-forward-deployed-engineer"

    if not stage:
        stage = "land"

    # 创建工单
    ticket_content = f"""---
ticket_id: {ticket_id}
title: "{customer} - {title}"
status: backlog
priority: {priority}
assignee_agent: {assignee}
created_at: {datetime.now().isoformat()}
updated_at: {datetime.now().isoformat()}
fde_stage: {stage}
customer: {customer}
source_type: manual
source_file: （手动创建）
---

# {ticket_id} - {title}

## 描述
天龙引擎 /cec-ticket 手工创建工单。

## 验收标准
- [ ] {stage} 阶段完成
- [ ] assignee agent 确认

## 历史
- {datetime.now().isoformat()} - 工单创建（run_cec_ticket.py）
"""

    ticket_path = base / "backlog" / f"{ticket_id}.md"
    ticket_path.write_text(ticket_content, encoding="utf-8")

    print(f"✅ 工单已创建：{ticket_id}")
    print(f"   标题: {title}")
    print(f"   阶段: {stage}")
    print(f"   Assignee: {assignee}")
    print(f"   路径: {ticket_path}")
    return 0


def main() -> int:
    args = parse_args()

    if not args.action:
        print("❌ 缺少子命令")
        print("用法: python scripts/run_cec_ticket.py <子命令> [参数]")
        return 1

    # 路由子命令
    if args.action == "pool-init":
        return cmd_pool_init(args.customer)
    elif args.action == "list":
        return cmd_list(args.customer, args.status)
    elif args.action == "status":
        return cmd_status(args.ticket_id)
    elif args.action == "update":
        return cmd_update(args.ticket_id, args.status, args.reason)
    elif args.action == "assign":
        # 触发天龙 paperclip-heartbeat 流程
        print(f"⚠️  分配工单 {args.ticket_id} → {args.agent}（暂未实现完整版）")
        print(f"   建议：手动编辑工单 frontmatter 的 assignee_agent 字段")
        return 0
    elif args.action == "history":
        print(f"⚠️  history 查看工单历史（建议直接 Read 工单文件）")
        return cmd_status(args.ticket_id)
    elif args.action == "dashboard":
        return cmd_dashboard(args.customer)
    elif args.action == "flow":
        print(f"📊 {args.customer} 完整工单流（按状态分组）")
        return cmd_list(args.customer)
    elif args.action == "create":
        return cmd_create(args.customer, args.title, args.stage,
                          args.priority, args.assignee)
    else:
        print(f"❌ 未知子命令：{args.action}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
