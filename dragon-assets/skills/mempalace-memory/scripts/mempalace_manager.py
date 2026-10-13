#!/usr/bin/env python3
"""
MemPalace Manager - 天龙引擎宫殿记忆系统管理脚本
基于 mempalace 18.1k Stars 项目
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any


class MemPalaceManager:
    """MemPalace宫殿记忆系统管理器"""

    def __init__(self, base_path: str = "~/.claude/mempalace-memory"):
        self.base_path = os.path.expanduser(base_path)
        self.tianlong_wing = "tianlong"

    def run_command(self, args: List[str], capture: bool = True) -> str:
        """执行mempalace命令"""
        cmd = ["mempalace"] + args
        try:
            if capture:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, check=True
                )
                return result.stdout
            else:
                subprocess.run(cmd, check=True)
                return ""
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr}"
        except FileNotFoundError:
            return "Error: mempalace not found. Run: pip install mempalace"

    def init(self, wing: Optional[str] = None) -> str:
        """初始化记忆宫殿"""
        wing = wing or self.tianlong_wing
        return self.run_command(["init", self.base_path, "--wing", wing])

    def search(
        self,
        query: str,
        wing: Optional[str] = None,
        room: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """语义搜索记忆"""
        wing = wing or self.tianlong_wing
        args = ["search", query, "--wing", wing, "--limit", str(limit), "--json"]
        if room:
            args.extend(["--room", room])

        result = self.run_command(args)
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return [{"raw": result}]

    def mine(
        self,
        path: str,
        mode: str = "projects"
    ) -> str:
        """挖掘数据到记忆宫殿"""
        return self.run_command([
            "mine",
            os.path.expanduser(path),
            "--mode", mode,
            "--wing", self.tianlong_wing
        ])

    def create_wing(self, name: str, description: str = "") -> str:
        """创建翅膀（项目/用户）"""
        return self.run_command([
            "wing", "create", name,
            "--description", description
        ])

    def create_room(self, wing: str, name: str, topic: str = "") -> str:
        """创建房间（话题）"""
        return self.run_command([
            "room", "create", name,
            "--wing", wing,
            "--topic", topic
        ])

    def diary_write(self, content: str, agent: str = "tianlong") -> str:
        """写入代理日记"""
        return self.run_command([
            "diary", "write",
            "--agent", agent,
            "--content", content
        ])

    def diary_read(self, agent: str = "tianlong", limit: int = 10) -> List[Dict]:
        """读取代理日记"""
        result = self.run_command([
            "diary", "read",
            "--agent", agent,
            "--limit", str(limit),
            "--json"
        ])
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return [{"raw": result}]

    def kg_add(
        self,
        entity: str,
        relation: str,
        target: str,
        valid_from: Optional[str] = None
    ) -> str:
        """添加知识三元组"""
        args = ["kg", "add", entity, relation, target]
        if valid_from:
            args.extend(["--valid-from", valid_from])
        return self.run_command(args)

    def kg_query(self, entity: str) -> List[Dict]:
        """查询实体知识"""
        result = self.run_command([
            "kg", "query", entity, "--json"
        ])
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return [{"raw": result}]

    def kg_timeline(self, entity: str) -> List[Dict]:
        """获取实体时间线"""
        result = self.run_command([
            "kg", "timeline", entity, "--json"
        ])
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return [{"raw": result}]

    def kg_invalidate(self, entity: str, relation: str, target: str) -> str:
        """使知识失效"""
        return self.run_command([
            "kg", "invalidate", entity, relation, target
        ])

    def contradiction_check(
        self,
        claim: Dict[str, Any]
    ) -> Dict[str, Any]:
        """矛盾检测"""
        result = self.run_command([
            "contradiction-check",
            "--fact", json.dumps(claim),
            "--wing", self.tianlong_wing,
            "--json"
        ])
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"raw": result, "contradictions": []}

    def stats(self, wing: Optional[str] = None) -> Dict:
        """记忆统计"""
        wing = wing or self.tianlong_wing
        result = self.run_command(["stats", "--wing", wing, "--json"])
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"raw": result}

    def context_get(self, level: str = "l3") -> str:
        """获取分层上下文"""
        return self.run_command([
            "context", "get",
            "--level", level,
            "--wing", self.tianlong_wing
        ])

    def forget(self, memory_id: str) -> str:
        """选择性遗忘"""
        return self.run_command(["forget", memory_id])

    def agent_create(
        self,
        name: str,
        rooms: List[str],
        specialization: str = ""
    ) -> str:
        """创建专家代理配置"""
        return self.run_command([
            "agent", "create", name,
            "--rooms", ",".join(rooms),
            "--specialization", specialization
        ])

    def agent_list(self) -> List[Dict]:
        """列出专家代理"""
        result = self.run_command(["agent", "list", "--json"])
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return []

    def ingest_file(self, file_path: str, wing: Optional[str] = None) -> str:
        """摄入文件到记忆"""
        wing = wing or self.tianlong_wing
        return self.run_command([
            "ingest",
            os.path.expanduser(file_path),
            "--wing", wing
        ])


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="MemPalace Manager for 天龙引擎")
    parser.add_argument("action", choices=[
        "init", "search", "mine", "diary-write", "diary-read",
        "kg-add", "kg-query", "kg-timeline", "kg-invalidate",
        "contradiction-check", "stats", "context", "forget",
        "agent-create", "agent-list", "ingest"
    ], help="操作类型")

    parser.add_argument("--query", help="搜索查询")
    parser.add_argument("--path", help="文件路径")
    parser.add_argument("--mode", default="projects", help="挖掘模式")
    parser.add_argument("--content", help="日记内容")
    parser.add_argument("--agent", default="tianlong", help="代理名称")
    parser.add_argument("--limit", type=int, default=5, help="结果数量")
    parser.add_argument("--entity", help="实体名称")
    parser.add_argument("--relation", help="关系")
    parser.add_argument("--target", help="目标")
    parser.add_argument("--wing", default="tianlong", help="翅膀名称")
    parser.add_argument("--rooms", help="房间列表（逗号分隔）")
    parser.add_argument("--specialization", help="专家代理专长")
    parser.add_argument("--level", default="l3", help="上下文层级")
    parser.add_argument("--memory-id", help="记忆ID")
    parser.add_argument("--json", action="store_true", help="JSON输出")
    parser.add_argument("--valid-from", help="有效起始时间")

    args = parser.parse_args()
    manager = MemPalaceManager()

    result = ""

    if args.action == "init":
        result = manager.init(args.wing)
    elif args.action == "search":
        result = manager.search(args.query, args.wing, limit=args.limit)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
    elif args.action == "mine":
        result = manager.mine(args.path, args.mode)
    elif args.action == "diary-write":
        result = manager.diary_write(args.content, args.agent)
    elif args.action == "diary-read":
        result = manager.diary_read(args.agent, args.limit)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
    elif args.action == "kg-add":
        result = manager.kg_add(args.entity, args.relation, args.target, args.valid_from)
    elif args.action == "kg-query":
        result = manager.kg_query(args.entity)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
    elif args.action == "kg-timeline":
        result = manager.kg_timeline(args.entity)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
    elif args.action == "kg-invalidate":
        result = manager.kg_invalidate(args.entity, args.relation, args.target)
    elif args.action == "contradiction-check":
        claim = json.loads(args.entity) if args.entity else {}
        result = manager.contradiction_check(claim)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
    elif args.action == "stats":
        result = manager.stats(args.wing)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
    elif args.action == "context":
        result = manager.context_get(args.level)
    elif args.action == "forget":
        result = manager.forget(args.memory_id)
    elif args.action == "agent-create":
        rooms = args.rooms.split(",") if args.rooms else []
        result = manager.agent_create(args.agent, rooms, args.specialization or "")
    elif args.action == "agent-list":
        result = manager.agent_list()
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return
    elif args.action == "ingest":
        result = manager.ingest_file(args.path, args.wing)

    print(result)


if __name__ == "__main__":
    main()
