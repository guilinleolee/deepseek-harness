#!/usr/bin/env python3
"""
MetaGPT 天龙引擎集成管理脚本
多Agent元编程框架 - SOP驱动软件开发
"""

import argparse
import json
import subprocess
import os
import sys
from pathlib import Path
from typing import List, Optional

class MetaGPTManager:
    """MetaGPT 管理器"""

    def __init__(self):
        self.home = Path.home() / ".claude" / "skills" / "metagpt"
        self.config_file = self.home / "config.yaml"
        self.history_file = self.home / "history.json"
        self.workspace = self.home / "workspace"
        self.load_config()

    def load_config(self):
        """加载配置"""
        self.config = {
            "model": {
                "provider": "anthropic",
                "name": "claude-3-5-sonnet-20240620",
                "api_key": os.getenv("ANTHROPIC_API_KEY", "")
            },
            "sop": {
                "enabled": True,
                "strict": True
            },
            "roles": {
                "product_manager": {"enabled": True},
                "architect": {"enabled": True},
                "project_manager": {"enabled": True},
                "engineer": {"enabled": True},
                "qa_engineer": {"enabled": True}
            },
            "output": {
                "directory": str(self.workspace),
                "save_actions": True
            }
        }

    def save_config(self):
        """保存配置"""
        self.home.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            f.write("# MetaGPT Configuration\n")
            f.write(f"model: {self.config['model']['name']}\n")
            f.write(f"provider: {self.config['model']['provider']}\n")
            f.write(f"output_dir: {self.config['output']['directory']}\n")

    def install(self):
        """安装MetaGPT"""
        print("📦 安装MetaGPT...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "meta-gpt"],
                          check=True, capture_output=True)
            print("✅ MetaGPT 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ 安装失败: {e.stderr.decode()}")
            return False
        return True

    def run(self, requirement: str, directory: str = None,
            model: str = None, roles: List[str] = None,
            verbose: bool = False):
        """运行MetaGPT"""

        if not requirement:
            print("❌ 请提供需求描述")
            return False

        print(f"🚀 开始处理需求: {requirement[:50]}...")

        # 构建命令
        cmd = ["metagpt"]

        if directory:
            cmd.extend(["--directory", directory])
        else:
            cmd.extend(["--directory", str(self.workspace / "projects")])

        if model:
            cmd.extend(["--model", model])
        else:
            cmd.extend(["--model", self.config["model"]["name"]])

        if verbose:
            cmd.append("--verbose")

        # 传递需求
        cmd.extend(["--requirement", requirement])

        print(f"📋 执行命令: {' '.join(cmd[:5])}...")

        try:
            result = subprocess.run(
                cmd,
                input=requirement,
                text=True,
                check=True,
                timeout=600  # 10分钟超时
            )
            self.log_history(requirement, "success")
            print("✅ MetaGPT 执行完成")
            return True
        except subprocess.CalledProcessError as e:
            self.log_history(requirement, "failed")
            print(f"❌ MetaGPT 执行失败")
            return False
        except subprocess.TimeoutExpired:
            self.log_history(requirement, "timeout")
            print("❌ MetaGPT 执行超时 (10分钟)")
            return False

    def init_project(self, name: str, template: str = "default"):
        """初始化项目"""
        print(f"📁 初始化项目: {name}")

        project_dir = self.workspace / "projects" / name
        project_dir.mkdir(parents=True, exist_ok=True)

        # 创建项目结构
        (project_dir / "docs").mkdir(exist_ok=True)
        (project_dir / "src").mkdir(exist_ok=True)
        (project_dir / "tests").mkdir(exist_ok=True)

        # 创建README
        readme = project_dir / "README.md"
        readme.write_text(f"""# {name}

## 项目说明

基于 MetaGPT SOP 驱动的多Agent协作开发项目。

## 架构

- **PM**: {name}/docs/requirements.md
- **Architect**: {name}/docs/architecture.md
- **Engineer**: {name}/src/
- **QA**: {name}/tests/

## 开发指南

```bash
metagpt --directory {project_dir} --requirement "开发{name}"
```
""")

        print(f"✅ 项目已初始化: {project_dir}")
        return project_dir

    def list_projects(self):
        """列出项目"""
        projects_dir = self.workspace / "projects"
        if not projects_dir.exists():
            print("📭 暂无项目")
            return

        projects = [p for p in projects_dir.iterdir() if p.is_dir()]
        if not projects:
            print("📭 暂无项目")
            return

        print(f"📁 项目列表 ({len(projects)} 个):")
        for p in sorted(projects):
            readme = p / "README.md"
            desc = ""
            if readme.exists():
                lines = readme.read_text().split('\n')
                if len(lines) > 2:
                    desc = lines[2].replace("## ", "").strip()
            print(f"  📂 {p.name}: {desc}")

    def generate_sop(self, project: str = None):
        """生成SOP流程文档"""
        print("📋 生成SOP流程文档...")

        sop_content = """# SOP (Standard Operating Procedure)

## 角色定义

### 1. Product Manager (PM)
**职责**: 需求解析与用户故事生成
**产出**: REQUIREMENTS.md

### 2. Architect
**职责**: 系统架构设计
**产出**: ARCHITECTURE.md

### 3. Project Manager
**职责**: 任务分解与进度管理
**产出**: TASKS.md

### 4. Engineer
**职责**: 代码实现
**产出**: src/

### 5. QA Engineer
**职责**: 测试设计与验证
**产出**: tests/

## 工作流程

```
需求输入
    ↓
PM: 需求解析 → 生成用户故事
    ↓
Architect: 架构设计 → 生成系统架构
    ↓
PM: 任务分解 → 生成任务列表
    ↓
Engineer: 并行开发 → 生成代码
    ↓
QA: 测试设计 → 生成测试报告
    ↓
输出: 完整软件产品
```

## 天龙引擎对标

| MetaGPT 角色 | 天龙岗位 | 核心能力 |
|-------------|---------|---------|
| PM | 00分析师 | 需求解析 |
| Architect | 02架构师 | 架构设计 |
| Engineer | 03构建师 | 代码实现 |
| QA | 04验证师 | 测试验证 |
| PM | 09-02编排 | 任务编排 |
"""

        sop_file = self.workspace / "SOP.md"
        sop_file.write_text(sop_content)
        print(f"✅ SOP文档已生成: {sop_file}")
        return sop_file

    def log_history(self, requirement: str, status: str):
        """记录历史"""
        history = []
        if self.history_file.exists():
            with open(self.history_file) as f:
                history = json.load(f)

        history.append({
            "requirement": requirement[:100],
            "status": status,
            "timestamp": subprocess.run(
                ["date", "+%Y-%m-%d %H:%M:%S"],
                capture_output=True, text=True
            ).stdout.strip()
        })

        with open(self.history_file, 'w') as f:
            json.dump(history[-100:], f, indent=2)

    def history(self, limit: int = 10):
        """查看历史"""
        if not self.history_file.exists():
            print("📭 暂无历史记录")
            return

        with open(self.history_file) as f:
            history = json.load(f)

        print(f"📜 最近 {min(limit, len(history))} 条历史记录:")
        for i, record in enumerate(history[-limit:], 1):
            status_icon = "✅" if record["status"] == "success" else "❌"
            print(f"  {status_icon} {record['requirement'][:40]}... - {record['timestamp']}")

    def status(self):
        """检查状态"""
        print("🔍 MetaGPT 状态检查")
        print("")

        # Python检查
        print("Python环境:")
        python_version = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True, text=True
        ).stdout.strip()
        print(f"  {python_version}")

        # MetaGPT检查
        print("MetaGPT:")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "meta-gpt"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("  ✅ 已安装")
            for line in result.stdout.split('\n')[:3]:
                if line:
                    print(f"  {line}")
        else:
            print("  ⚠️ 未安装 (运行 'metagpt-manager install' 安装)")

        # API Key检查
        print("API Key:")
        if os.getenv("ANTHROPIC_API_KEY"):
            print("  ✅ ANTHROPIC_API_KEY 已设置")
        else:
            print("  ⚠️ ANTHROPIC_API_KEY 未设置")

        # 工作区检查
        print("工作区:")
        if self.workspace.exists():
            print(f"  ✅ {self.workspace}")
        else:
            print(f"  📁 {self.workspace} (将创建)")


def main():
    parser = argparse.ArgumentParser(description="MetaGPT 天龙引擎集成管理")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # install
    subparsers.add_parser("install", help="安装MetaGPT")

    # run
    run_parser = subparsers.add_parser("run", help="运行MetaGPT")
    run_parser.add_argument("--requirement", "-r", required=True, help="需求描述")
    run_parser.add_argument("--directory", "-d", help="项目目录")
    run_parser.add_argument("--model", "-m", help="模型名称")
    run_parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    # init
    init_parser = subparsers.add_parser("init", help="初始化项目")
    init_parser.add_argument("name", help="项目名称")
    init_parser.add_argument("--template", "-t", default="default", help="模板")

    # list
    subparsers.add_parser("list", help="列出项目")

    # sop
    subparsers.add_parser("sop", help="生成SOP文档")

    # history
    history_parser = subparsers.add_parser("history", help="查看历史")
    history_parser.add_argument("--limit", "-n", type=int, default=10, help="显示条数")

    # status
    subparsers.add_parser("status", help="检查状态")

    args = parser.parse_args()
    manager = MetaGPTManager()

    if args.command == "install":
        manager.install()
    elif args.command == "run":
        manager.run(
            args.requirement,
            args.directory,
            args.model,
            verbose=args.verbose
        )
    elif args.command == "init":
        manager.init_project(args.name, args.template)
    elif args.command == "list":
        manager.list_projects()
    elif args.command == "sop":
        manager.generate_sop()
    elif args.command == "history":
        manager.history(args.limit)
    elif args.command == "status":
        manager.status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
