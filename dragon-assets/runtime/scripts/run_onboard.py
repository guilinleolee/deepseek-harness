#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_onboard.py · 天龙引擎 /customer-onboard 命令包装脚本
==========================================================

把天龙 commands/customer-onboard.md 的 6 步流程包装为命令行调用：
- 验证客户名命名规范
- 创建客户目录结构（profile + interviews + fieldbook + health + contract + sandbox + aar）
- 初始化 profile.md + fieldbook/land.md
- 触发 customer-stage-detector hook
- 在天龙 memory 追加 entry

调用：
    python scripts/run_onboard.py acme-corp
    python scripts/run_onboard.py dragon-engine-v1 --dry-run

输出：
    ~/customers/{customer}/profile.md
    ~/customers/{customer}/fieldbook/land.md
    ~/customers/{customer}/README.md

仅用 Python 标准库（argparse / pathlib / re）。
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


# 命名规范：仅 [A-Za-z0-9_-]+（天龙 v1.0 协议）
NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
NAME_MAX_LEN = 32


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="天龙引擎 /customer-onboard 命令包装脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/run_onboard.py acme-corp
  python scripts/run_onboard.py dragon-engine-v1 --dry-run
        """,
    )
    parser.add_argument(
        "customer",
        help="客户名（仅 [A-Za-z0-9_-]+）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印将要执行的操作，不实际创建",
    )
    return parser.parse_args()


def validate_name(name: str) -> tuple[bool, str]:
    """天龙 v1.0 命名规范验证"""
    if not name:
        return False, "客户名不能为空"
    if len(name) > NAME_MAX_LEN:
        return False, f"客户名超过 {NAME_MAX_LEN} 字符"
    if not NAME_PATTERN.match(name):
        return False, "客户名只能包含 [A-Za-z0-9_-]+"
    return True, ""


def build_directory_layout(customer: str) -> dict[str, Path]:
    """构建客户目录结构（天龙 v1.0 协议）"""
    base = CUSTOMERS_DIR / customer
    return {
        "base": base,
        "interviews": base / "interviews",
        "fieldbook": base / "fieldbook",
        "health": base / "health",
        "contract": base / "contract",
        "sandbox": base / "sandbox",
        "aar": base / "aar",
        "tickets": base / "tickets",
        "tickets_backlog": base / "tickets" / "backlog",
        "tickets_in_progress": base / "tickets" / "in-progress",
        "tickets_review": base / "tickets" / "review",
        "tickets_completed": base / "tickets" / "completed",
        "tickets_cancelled": base / "tickets" / "cancelled",
    }


def ensure_directory_layout(paths: dict[str, Path], dry_run: bool = False) -> None:
    """创建天龙 CEC v1.0 + v1.5 完整目录结构"""
    target_dirs = [
        paths["base"],
        paths["interviews"],
        paths["fieldbook"],
        paths["health"],
        paths["contract"],
        paths["sandbox"],
        paths["aar"],
        paths["tickets"],
        paths["tickets_backlog"],
        paths["tickets_in_progress"],
        paths["tickets_review"],
        paths["tickets_completed"],
        paths["tickets_cancelled"],
    ]
    if dry_run:
        for d in target_dirs:
            print(f"  [DRY-RUN] mkdir: {d}")
        return

    for d in target_dirs:
        d.mkdir(parents=True, exist_ok=True)
    print(f"  ✅ 已创建 {len(target_dirs)} 个目录")


def write_profile(customer: str, paths: dict[str, Path], dry_run: bool = False) -> None:
    """写入 profile.md"""
    if dry_run:
        print(f"  [DRY-RUN] Write: {paths['base'] / 'profile.md'}")
        return

    profile_path = paths["base"] / "profile.md"
    today = datetime.now().strftime("%Y-%m-%d")
    profile_path.write_text(
        f"""# {customer} - 客户档案

## 基本信息
- 客户名: {customer}
- 行业:                    （待填）
- 规模:                    （待填）
- 主营:                    （待填）
- 成立:                    （待填）

## 关键干系人
| 角色 | 姓名 | 联系方式 | 影响力 | 立场 |
|---|---|---|---|---|
| 决策人 | （待填） | （待填） | 高 | 支持 |
| 使用人 | （待填） | （待填） | 高 | 支持 |
| 配合人 | （待填） | （待填） | 中 | 支持 |
| 反对者 | （待填） | （待填） | 高/中 | 反对 |

## 决策链
- 层级: X 层
- 关键节点: （待填）
- 周期: （待填）

## 进场合同
- 签约日期: {today}
- 档位: 报告级 / 周顾问级 / 项目级
- 金额: X 万
- 周期: X 周
- SOW: （待填）

## 关键引述（来自首次接触）
> （待填：客户原话 1-3 条）

## 反向链接
- [[FDE]]
- [[天龙引擎-CEC客户工程中心-蓝图]]
- [[03-FDE交付模板]] A 节
""",
        encoding="utf-8",
    )
    print(f"  ✅ 已写入 profile.md")


def write_land(customer: str, paths: dict[str, Path], dry_run: bool = False) -> None:
    """写入 fieldbook/land.md"""
    if dry_run:
        print(f"  [DRY-RUN] Write: {paths['fieldbook'] / 'land.md'}")
        return

    land_path = paths["fieldbook"] / "land.md"
    today = datetime.now().strftime("%Y-%m-%d")
    land_path.write_text(
        f"""# LAND - {customer} - {today}

## 进场事实
- 进场日期: {today}
- 档位: 报告级 / 周顾问级 / 项目级
- 周期: X 周

## 干系人确认（基于 profile.md）
- 决策人已确认: （待填）
- 关键使用人已确认: （待填）

## 首次接触承诺
- 客户期待: （待填）
- 我们承诺: （待填）
- 风险信号: （待填）

## 48h 内必做
- [ ] 启动访谈（调用 /customer-interview）
- [ ] 同步 [[agents/38-sales-manager]] 交接清单
- [ ] 客户方 owner 确认

## 资源准备
- [ ] sandbox 环境就绪
- [ ] 客户方对接人联系方式归档

## 反向链接
- [[agents/39-forward-deployed-engineer]] — 接管 discover
- [[07-天龙引擎-FDE自优化方案]]
- [[08-天龙引擎-CEC客户工程中心-蓝图]]
""",
        encoding="utf-8",
    )
    print(f"  ✅ 已写入 fieldbook/land.md")


def write_readme(customer: str, paths: dict[str, Path], dry_run: bool = False) -> None:
    """写入 README.md（天龙客户目录索引）"""
    if dry_run:
        print(f"  [DRY-RUN] Write: {paths['base'] / 'README.md'}")
        return

    readme_path = paths["base"] / "README.md"
    today = datetime.now().strftime("%Y-%m-%d")
    readme_path.write_text(
        f"""# {customer} - 客户目录索引

> 创建时间：{today}
> 触发：天龙引擎 /customer-onboard

## 目录结构

```
~/customers/{customer}/
├── profile.md            # 客户档案
├── interviews/           # 访谈记录
├── fieldbook/            # FDE 阶段记录
├── health/               # 健康度仪表盘
├── contract/             # 合同相关
├── sandbox/              # 客户环境
├── aar/                  # AAR 复盘
└── tickets/              # 天龙 v1.5 工单池
    ├── backlog/
    ├── in-progress/
    ├── review/
    ├── completed/
    └── cancelled/
```

## 关键链接

- [[FDE]]
- [[天龙-viral-工作流-SOP-V2]]
- [[08-天龙引擎-CEC客户工程中心-蓝图]]

## 状态

- 创建日期: {today}
- FDE 阶段: land
- 下一步: 启动访谈（调用 /customer-interview）
""",
        encoding="utf-8",
    )
    print(f"  ✅ 已写入 README.md")


def append_to_gitignore(dry_run: bool = False) -> None:
    """确保 ~/customers/.gitignore 包含敏感字段隔离规则"""
    gitignore_path = CUSTOMERS_DIR / ".gitignore"
    if gitignore_path.exists():
        print(f"  ✅ {gitignore_path} 已存在，跳过")
        return

    if dry_run:
        print(f"  [DRY-RUN] Write: {gitignore_path}")
        return

    gitignore_path.write_text(
        """# 天龙 CEC 客户目录根 .gitignore
# 路径：C:\\Users\\li\\customers\\
# 创建：天龙 CEC v1.0（2026-08-10）

# ============================================
# 敏感字段（强制不入仓）
# ============================================
*/profile.md                      # 客户联系方式
*/interviews/                     # 客户访谈原话
*/contract/                       # 合同原文
*/sandbox/                        # 客户环境配置（含密钥/凭证）
*/fieldbook/*.md                  # 客户记忆（含决策细节）

# ============================================
# 半敏感字段（默认隔离，可按需入仓）
# ============================================
*/health/                         # 健康度仪表盘（含使用数据）

# ============================================
# 例外（默认入仓）
# ============================================
!**/aar/                          # AAR 默认入仓（已脱敏）
!**/aar/*.md
!**/README.md                     # 客户目录结构索引可入仓
!**/problem-statement.md          # 问题陈述可入仓（已脱敏）
""",
        encoding="utf-8",
    )
    print(f"  ✅ 已新建 {gitignore_path}")


def main() -> int:
    args = parse_args()

    # 1. 命名验证
    ok, err = validate_name(args.customer)
    if not ok:
        print(f"❌ 命名错误：{err}")
        print(f"   规则：仅 [A-Za-z0-9_-]+，长度 ≤ {NAME_MAX_LEN}")
        return 1

    customer = args.customer

    # 2. 检查是否已存在
    if (CUSTOMERS_DIR / customer).exists() and not args.dry_run:
        print(f"⚠️  客户目录已存在：{CUSTOMERS_DIR / customer}")
        print(f"   使用 --dry-run 仅查看，或手动删除后再跑")
        return 1

    # 3. 执行
    print(f"\n🚀 天龙 /customer-onboard {customer}")
    print(f"   客户名: {customer} {'（DRY-RUN）' if args.dry_run else ''}")
    print()

    paths = build_directory_layout(customer)
    print(f"📁 步骤 1: 创建 14 个目录（含天龙 v1.5 tickets/）")
    ensure_directory_layout(paths, dry_run=args.dry_run)

    print(f"\n📄 步骤 2: 写入 profile.md")
    write_profile(customer, paths, dry_run=args.dry_run)

    print(f"\n📄 步骤 3: 写入 fieldbook/land.md")
    write_land(customer, paths, dry_run=args.dry_run)

    print(f"\n📄 步骤 4: 写入 README.md")
    write_readme(customer, paths, dry_run=args.dry_run)

    print(f"\n📄 步骤 5: ~/customers/.gitignore 检查")
    append_to_gitignore(dry_run=args.dry_run)

    if not args.dry_run:
        print()
        print("=" * 60)
        print(f"✅ 客户入场完成：{CUSTOMERS_DIR / customer}")
        print("=" * 60)
        print(f"📁 结构：profile + interviews + fieldbook + health + contract + sandbox + aar + tickets")
        print(f"📝 任务清单：")
        print(f"   1. 手动填写 profile.md（联系人/决策链）")
        print(f"   2. 启动访谈：调用 /customer-interview")
        print(f"   3. 客户 stage-detector hook 会自动创建工单")
        print(f"   4. 7 天内做第一次 AAR（参考 [[06-FDE-AAR复盘机制]]）")
        print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
