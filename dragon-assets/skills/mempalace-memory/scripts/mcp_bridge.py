#!/usr/bin/env python3
"""
MemPalace MCP Bridge - 天龙引擎MCP集成桥接
提供19个MCP工具供Claude Code使用
"""

import json
import subprocess
from typing import Any, Dict, List, Optional
from datetime import datetime


class MemPalaceMCPBridge:
    """MemPalace MCP工具桥接器"""

    def __init__(self, wing: str = "tianlong"):
        self.wing = wing

    def run(self, args: List[str]) -> str:
        """执行mempalace命令"""
        try:
            result = subprocess.run(
                ["mempalace"] + args,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return json.dumps({"error": e.stderr})
        except FileNotFoundError:
            return json.dumps({"error": "mempalace not installed. Run: pip install mempalace"})

    # ==================== 搜索工具 ====================

    def mempalace_search(
        self,
        query: str,
        wing: Optional[str] = None,
        room: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        语义记忆搜索
        用于跨会话知识复用
        """
        wing = wing or self.wing
        args = ["search", query, "--wing", wing, "--limit", str(limit), "--json"]
        if room:
            args.extend(["--room", room])

        result = self.run(args)
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"results": [{"raw": result}], "count": 1}

    # ==================== 日记工具 ====================

    def mempalace_diary_write(
        self,
        content: str,
        agent: str = "tianlong"
    ) -> Dict[str, str]:
        """
        写入代理日记
        记录执行过程和决策
        """
        self.run(["diary", "write", "--agent", agent, "--content", content])
        return {
            "status": "success",
            "agent": agent,
            "timestamp": datetime.now().isoformat()
        }

    def mempalace_diary_read(
        self,
        agent: str = "tianlong",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        读取代理日记
        恢复执行上下文
        """
        result = self.run(["diary", "read", "--agent", agent, "--limit", str(limit), "--json"])
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return [{"raw": result}]

    # ==================== 知识图谱工具 ====================

    def mempalace_kg_add(
        self,
        entity: str,
        relation: str,
        target: str,
        valid_from: Optional[str] = None
    ) -> Dict[str, str]:
        """
        添加知识三元组
        格式: (entity, relation, target)
        """
        args = ["kg", "add", entity, relation, target]
        if valid_from:
            args.extend(["--valid-from", valid_from])

        self.run(args)
        return {
            "status": "added",
            "triple": {"entity": entity, "relation": relation, "target": target},
            "valid_from": valid_from or datetime.now().date().isoformat()
        }

    def mempalace_kg_query(
        self,
        entity: str
    ) -> List[Dict[str, Any]]:
        """
        查询实体知识
        获取实体的所有关系
        """
        result = self.run(["kg", "query", entity, "--json"])
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return [{"entity": entity, "relations": []}]

    def mempalace_kg_timeline(
        self,
        entity: str
    ) -> List[Dict[str, Any]]:
        """
        获取实体时间线
        追踪事实变化历史
        """
        result = self.run(["kg", "timeline", entity, "--json"])
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return [{"entity": entity, "timeline": []}]

    def mempalace_kg_invalidate(
        self,
        entity: str,
        relation: str,
        target: str,
        valid_until: Optional[str] = None
    ) -> Dict[str, str]:
        """
        使三元组失效
        用于更新过时知识
        """
        args = ["kg", "invalidate", entity, relation, target]
        if valid_until:
            args.extend(["--valid-until", valid_until])

        self.run(args)
        return {
            "status": "invalidated",
            "triple": {"entity": entity, "relation": relation, "target": target}
        }

    # ==================== 摄入工具 ====================

    def mempalace_ingest(
        self,
        path: str,
        wing: Optional[str] = None,
        mode: str = "auto"
    ) -> Dict[str, str]:
        """
        摄入文档/对话到记忆
        """
        wing = wing or self.wing
        self.run(["ingest", path, "--wing", wing, "--mode", mode])
        return {
            "status": "ingested",
            "path": path,
            "wing": wing
        }

    # ==================== 结构工具 ====================

    def mempalace_wing_create(
        self,
        name: str,
        description: str = ""
    ) -> Dict[str, str]:
        """
        创建翅膀
        用于新项目或用户
        """
        args = ["wing", "create", name]
        if description:
            args.extend(["--description", description])

        self.run(args)
        return {"status": "created", "wing": name}

    def mempalace_room_create(
        self,
        name: str,
        wing: Optional[str] = None,
        topic: str = ""
    ) -> Dict[str, str]:
        """
        创建房间
        用于新话题
        """
        wing = wing or self.wing
        args = ["room", "create", name, "--wing", wing]
        if topic:
            args.extend(["--topic", topic])

        self.run(args)
        return {"status": "created", "room": name, "wing": wing}

    # ==================== 矛盾检测 ====================

    def mempalace_contradiction_check(
        self,
        entity: str,
        relation: str,
        target: str,
        confidence: float = 0.9
    ) -> Dict[str, Any]:
        """
        矛盾检测
        验证新断言与现有知识的一致性
        """
        claim = {
            "entity": entity,
            "relation": relation,
            "target": target,
            "confidence": confidence
        }

        result = self.run([
            "contradiction-check",
            "--fact", json.dumps(claim),
            "--wing", self.wing,
            "--json"
        ])

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            # 如果命令不存在，模拟矛盾检测
            existing = self.mempalace_kg_query(entity)
            contradictions = []

            for item in existing:
                if item.get("relation") == relation and item.get("target") != target:
                    contradictions.append({
                        "existing": item,
                        "claim": claim
                    })

            return {
                "claim": claim,
                "contradictions": contradictions,
                "is_consistent": len(contradictions) == 0
            }

    # ==================== 上下文工具 ====================

    def mempalace_context_get(
        self,
        level: str = "l3"
    ) -> Dict[str, Any]:
        """
        获取分层上下文
        L0: Identity (~50 tokens)
        L1: Critical Facts (~120 tokens)
        L2: Room Recall (recent sessions)
        L3: Deep Search (semantic query)
        """
        result = self.run(["context", "get", "--level", level, "--wing", self.wing])

        context_map = {
            "l0": "Identity - AI身份",
            "l1": "Critical Facts - 关键事实",
            "l2": "Room Recall - 最近会话",
            "l3": "Deep Search - 全局检索"
        }

        return {
            "level": level,
            "description": context_map.get(level, "Unknown"),
            "content": result.strip()
        }

    # ==================== 遗忘工具 ====================

    def mempalace_forget(
        self,
        memory_id: str
    ) -> Dict[str, str]:
        """
        选择性遗忘
        清理过期记忆
        """
        self.run(["forget", memory_id])
        return {"status": "forgotten", "memory_id": memory_id}

    # ==================== 统计工具 ====================

    def mempalace_stats(
        self,
        wing: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        记忆统计
        查看记忆状态
        """
        wing = wing or self.wing
        result = self.run(["stats", "--wing", wing, "--json"])

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"raw": result, "wing": wing}


# MCP工具注册表
MCP_TOOLS = {
    "mempalace_search": {
        "description": "语义记忆搜索",
        "parameters": {
            "query": "搜索查询字符串",
            "wing": "翅膀名称（可选）",
            "room": "房间名称（可选）",
            "limit": "结果数量（默认5）"
        }
    },
    "mempalace_diary_write": {
        "description": "写入代理日记",
        "parameters": {
            "content": "日记内容",
            "agent": "代理名称"
        }
    },
    "mempalace_diary_read": {
        "description": "读取代理日记",
        "parameters": {
            "agent": "代理名称",
            "limit": "读取数量"
        }
    },
    "mempalace_kg_add": {
        "description": "添加知识三元组",
        "parameters": {
            "entity": "实体",
            "relation": "关系",
            "target": "目标",
            "valid_from": "生效时间（可选）"
        }
    },
    "mempalace_kg_query": {
        "description": "查询实体知识",
        "parameters": {
            "entity": "实体名称"
        }
    },
    "mempalace_kg_timeline": {
        "description": "获取实体时间线",
        "parameters": {
            "entity": "实体名称"
        }
    },
    "mempalace_kg_invalidate": {
        "description": "使三元组失效",
        "parameters": {
            "entity": "实体",
            "relation": "关系",
            "target": "目标"
        }
    },
    "mempalace_ingest": {
        "description": "摄入文档/对话",
        "parameters": {
            "path": "文件路径",
            "wing": "翅膀名称（可选）",
            "mode": "摄入模式"
        }
    },
    "mempalace_wing_create": {
        "description": "创建翅膀",
        "parameters": {
            "name": "翅膀名称",
            "description": "描述（可选）"
        }
    },
    "mempalace_room_create": {
        "description": "创建房间",
        "parameters": {
            "name": "房间名称",
            "wing": "翅膀名称（可选）",
            "topic": "话题（可选）"
        }
    },
    "mempalace_contradiction_check": {
        "description": "矛盾检测",
        "parameters": {
            "entity": "实体",
            "relation": "关系",
            "target": "目标",
            "confidence": "置信度"
        }
    },
    "mempalace_context_get": {
        "description": "获取分层上下文",
        "parameters": {
            "level": "层级 (l0/l1/l2/l3)"
        }
    },
    "mempalace_forget": {
        "description": "选择性遗忘",
        "parameters": {
            "memory_id": "记忆ID"
        }
    },
    "mempalace_stats": {
        "description": "记忆统计",
        "parameters": {
            "wing": "翅膀名称（可选）"
        }
    }
}


def main():
    """MCP服务器入口"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--tools":
        print(json.dumps(MCP_TOOLS, ensure_ascii=False, indent=2))
        return

    bridge = MemPalaceMCPBridge()

    # 交互模式
    print("MemPalace MCP Bridge Ready")
    print(f"Wing: {bridge.wing}")
    print(f"Available tools: {len(MCP_TOOLS)}")
    print()
    print("Usage: python mcp_bridge.py --tools")


if __name__ == "__main__":
    main()
