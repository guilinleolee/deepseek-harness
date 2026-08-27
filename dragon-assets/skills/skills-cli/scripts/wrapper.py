#!/usr/bin/env python3
"""
Vercel Skills CLI 包装器
用于管理 AI Agent 技能生态系统的命令行工具
"""

import subprocess
import sys
import json
import os
from pathlib import Path


class SkillsCLI:
    """Vercel Skills CLI 接口"""

    def __init__(self):
        self.cmd = "npx"
        self.base_args = ["skills"]

    def _run(self, args: list, capture: bool = True) -> str:
        """执行命令并返回结果"""
        full_cmd = [self.cmd] + self.base_args + args

        if capture:
            try:
                result = subprocess.run(
                    full_cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=120
                )
                return result.stdout
            except subprocess.CalledProcessError as e:
                return f"错误: {e.stderr}"
            except subprocess.TimeoutExpired:
                return "错误: 命令执行超时"
        else:
            subprocess.run(full_cmd, check=True)
            return ""

    def add(self, source: str, **kwargs) -> str:
        """
        安装技能

        Args:
            source: 技能来源（GitHub URL、GitLab URL、本地路径等）
            **kwargs:
                global: bool - 安装到全局目录
                agent: list - 目标 Agent 列表
                skill: list - 特定技能名称列表
                list: bool - 仅列出可用技能
                yes: bool - 跳过确认
                all: bool - 安装所有技能到所有 Agent
        """
        args = ["add", source]

        if kwargs.get("global"):
            args.append("-g")

        if kwargs.get("agent"):
            for agent in kwargs["agent"]:
                args.extend(["-a", agent])

        if kwargs.get("skill"):
            for skill in kwargs["skill"]:
                args.extend(["-s", skill])

        if kwargs.get("list"):
            args.append("-l")

        if kwargs.get("yes"):
            args.append("-y")

        if kwargs.get("all"):
            args.append("--all")

        return self._run(args)

    def list(self, global_scope: bool = False, agents: list = None) -> str:
        """
        列出已安装技能

        Args:
            global_scope: 是否仅列出全局技能
            agents: 过滤特定 Agent
        """
        args = ["list"]

        if global_scope:
            args.append("-g")

        if agents:
            for agent in agents:
                args.extend(["-a", agent])

        return self._run(args)

    def find(self, query: str = None) -> str:
        """
        搜索技能

        Args:
            query: 搜索关键词（可选，无参数时交互式搜索）
        """
        args = ["find"]
        if query:
            args.append(query)

        # 交互式命令，不捕获输出
        return self._run(args, capture=False)

    def remove(self,
               skills: list = None,
               global_scope: bool = False,
               agents: list = None,
               yes: bool = False,
               all: bool = False) -> str:
        """
        移除已安装技能

        Args:
            skills: 要移除的技能列表
            global_scope: 从全局范围移除
            agents: 从特定 Agent 移除
            yes: 跳过确认
            all: 移除所有技能
        """
        args = ["remove"]

        if global_scope:
            args.append("-g")

        if agents:
            for agent in agents:
                args.extend(["-a", agent])

        if skills:
            for skill in skills:
                args.extend(["-s", skill])

        if yes:
            args.append("-y")

        if all:
            args.append("--all")

        return self._run(args)

    def check(self) -> str:
        """检查技能更新"""
        return self._run(["check"])

    def update(self) -> str:
        """更新所有已安装技能"""
        return self._run(["update"])

    def init(self, name: str = None) -> str:
        """
        创建新技能模板

        Args:
            name: 技能名称（可选）
        """
        args = ["init"]
        if name:
            args.append(name)

        return self._run(args, capture=False)


def main():
    """命令行入口"""
    cli = SkillsCLI()

    if len(sys.argv) < 2:
        print("Vercel Skills CLI 包装器")
        print("\n可用命令:")
        print("  add <source>     - 安装技能")
        print("  list             - 列出已安装技能")
        print("  find [query]     - 搜索技能")
        print("  remove [skills]  - 移除技能")
        print("  check            - 检查更新")
        print("  update           - 更新技能")
        print("  init [name]      - 创建新技能模板")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "add":
        if not args:
            print("错误: 请指定技能来源")
            sys.exit(1)
        result = cli.add(args[0])
        print(result)

    elif command == "list":
        result = cli.list()
        print(result)

    elif command == "find":
        query = args[0] if args else None
        cli.find(query)

    elif command == "remove":
        # 简化处理，直接传给 CLI
        result = cli.remove(skills=args if args else None)
        print(result)

    elif command == "check":
        result = cli.check()
        print(result)

    elif command == "update":
        result = cli.update()
        print(result)

    elif command == "init":
        name = args[0] if args else None
        cli.init(name)

    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
