#!/usr/bin/env python3
"""
RedBox Wander Engine - 漫步选题引擎
Inspired by RedBox's Wander Ideation feature

核心能力:
1. 知识漫步 - 从种子关键词随机游走知识图谱
2. 主题发散 - 围绕核心主题生成N个创意方向
3. 组合创新 - 将主体库元素随机组合生成新选题
4. 关键词联想 - 基于语义网络的近邻词汇推荐
5. 灵感记录 - 漫步过程中的灵感自动存入灵感库
"""

import random
import json
import re
import os
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Set
from datetime import datetime
from pathlib import Path

# 配置路径
CONFIG_DIR = Path.home() / ".claude" / "skills" / "redbox-wander"
DATA_DIR = CONFIG_DIR / "data"
INSPIRATION_LOG = CONFIG_DIR / "inspiration_log.md"
SUBJECT_LIB = DATA_DIR / "subjects.json"
KNOWLEDGE_GRAPH = DATA_DIR / "knowledge_graph.json"

@dataclass
class WanderNode:
    """漫步节点"""
    topic: str
    score: float = 0.5
    tags: List[str] = None
    source: str = "knowledge_base"
    connections: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.connections is None:
            self.connections = []

@dataclass
class Idea:
    """生成的想法"""
    seed: str
    path: List[str]
    content: str
    trigger: str
    creativity_score: float
    timestamp: str
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def to_markdown(self) -> str:
        """转换为Markdown格式"""
        path_str = " → ".join(self.path)
        tags_str = " ".join([f"#{t}" for t in self.tags])
        return f"""## 灵感 {self.timestamp}

- **种子**: {self.seed}
- **路径**: {path_str}
- **触发**: {self.trigger}
- **内容**: {self.content}
- **创意评分**: {self.creativity_score:.1%}
- **标签**: {tags_str}
"""

class WanderEngine:
    """漫步选题引擎"""

    def __init__(self, config: Dict = None):
        self.config = config or self._default_config()
        self.max_steps = self.config.get("max_steps", 20)
        self.diversity = self.config.get("diversity", 0.7)
        self.creativity = self.config.get("creativity", 0.8)

        # 加载数据
        self.knowledge_graph = self._load_knowledge_graph()
        self.subjects = self._load_subjects()

    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            "max_steps": 20,
            "diversity": 0.7,
            "creativity": 0.8,
            "topic_seed": None,
            "sources": {
                "subject_library": 0.3,
                "knowledge_base": 0.3,
                "trending": 0.2,
                "personal": 0.2
            }
        }

    def _load_knowledge_graph(self) -> Dict:
        """加载知识图谱"""
        if KNOWLEDGE_GRAPH.exists():
            with open(KNOWLEDGE_GRAPH, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._create_sample_graph()

    def _load_subjects(self) -> List[Dict]:
        """加载主体库"""
        if SUBJECT_LIB.exists():
            with open(SUBJECT_LIB, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _create_sample_graph(self) -> Dict:
        """创建示例知识图谱"""
        return {
            "nodes": {
                "AI": {"tags": ["技术", "趋势"], "connections": ["AI编程", "AI助手", "AI Agent"]},
                "AI编程": {"tags": ["技术", "效率"], "connections": ["Claude Code", "Copilot", "Cursor"]},
                "Claude Code": {"tags": ["工具", "开发"], "connections": ["编程民主化", "AI编程", "开发效率"]},
                "编程民主化": {"tags": ["趋势", "社会"], "connections": ["内容创作", "创作者经济", "自媒体"]},
                "内容创作": {"tags": ["创作", "媒体"], "connections": ["小红书", "短视频", "写作"]},
                "创作者经济": {"tags": ["经济", "趋势"], "connections": ["内容创作", "副业", "自由职业"]},
                "小红书": {"tags": ["平台", "社交"], "connections": ["种草", "博主", "内容营销"]},
                "自媒体": {"tags": ["媒体", "趋势"], "connections": ["内容创作", "变现", "个人IP"]},
                "个人IP": {"tags": ["品牌", "商业"], "connections": ["个人品牌", "影响力", "变现"]},
                "变现": {"tags": ["商业", "目标"], "connections": ["商业模式", "副业收入", "个人品牌"]}
            },
            "edges": []
        }

    def _get_candidates(self, current: WanderNode) -> List[WanderNode]:
        """获取候选节点"""
        candidates = []

        # 从知识图谱获取连接
        if current.topic in self.knowledge_graph["nodes"]:
            node_data = self.knowledge_graph["nodes"][current.topic]
            for conn in node_data.get("connections", []):
                if conn not in self._visited:
                    candidates.append(WanderNode(
                        topic=conn,
                        score=random.uniform(0.5, 0.9),
                        tags=node_data.get("tags", []),
                        source="knowledge_base"
                    ))

        # 从主体库获取相关主题
        for subject in self.subjects:
            if any(tag in current.topic for tag in subject.get("tags", [])):
                if subject.get("name") not in self._visited:
                    candidates.append(WanderNode(
                        topic=subject.get("name"),
                        score=random.uniform(0.6, 0.85),
                        tags=subject.get("tags", []),
                        source="subject_library"
                    ))

        # 随机补充一些创意节点
        creative_nodes = ["创新", "颠覆", "意外", "反转", "跨界", "融合", "回归", "进化"]
        random.shuffle(creative_nodes)
        for node in creative_nodes[:3]:
            if node not in self._visited:
                candidates.append(WanderNode(
                    topic=node,
                    score=random.uniform(0.4, 0.7) * self.creativity,
                    tags=["创意"],
                    source="creative"
                ))

        return candidates

    def _random_select(self, candidates: List[WanderNode]) -> WanderNode:
        """随机选择"""
        return random.choice(candidates)

    def _score_select(self, candidates: List[WanderNode]) -> WanderNode:
        """基于分数选择"""
        if not candidates:
            return WanderNode(topic="灵感")
        return max(candidates, key=lambda x: x.score)

    def _generate_idea(self, from_node: WanderNode, to_node: WanderNode, visited: Set[str]) -> Idea:
        """生成创意想法"""
        # 组合路径
        path = list(visited) + [to_node.topic]

        # 生成触发描述
        triggers = [
            f"从{from_node.topic}联想到{to_node.topic}",
            f"{to_node.topic}与{from_node.topic}的意外碰撞",
            f"当{from_node.topic}遇到{to_node.topic}时...",
            f"绕道{to_node.topic}发现新视角"
        ]

        # 生成创意内容
        ideas = [
            f"探索{to_node.topic}如何改变{from_node.topic}的格局",
            f"{to_node.topic}: {from_node.topic}的新解法",
            f"当{from_node.topic}遇上{to_node.topic}，会产生什么火花？",
            f"从{to_node.topic}的角度重新审视{from_node.topic}"
        ]

        return Idea(
            seed=list(visited)[0] if visited else "",
            path=path,
            content=random.choice(ideas),
            trigger=random.choice(triggers),
            creativity_score=to_node.score * self.creativity,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
            tags=to_node.tags + from_node.tags
        )

    def wander(self, seed: str) -> List[Idea]:
        """
        漫步主方法

        Args:
            seed: 种子关键词

        Returns:
            生成的创意列表
        """
        self._visited = {seed}
        results = []
        current = WanderNode(topic=seed)

        print(f"\n🌀 开始漫步: {seed}")
        print("=" * 60)

        for step in range(self.max_steps):
            candidates = self._get_candidates(current)

            if not candidates:
                print(f"  [Step {step+1}] 探索结束，无更多节点")
                break

            # 多样性选择
            if random.random() < self.diversity:
                next_node = self._random_select(candidates)
                selector = "🎲 随机"
            else:
                next_node = self._score_select(candidates)
                selector = "📊 评分"

            # 生成创意
            idea = self._generate_idea(current, next_node, self._visited)
            results.append(idea)

            # 打印进度
            print(f"\n  [Step {step+1}] {selector} 选择: {next_node.topic}")
            print(f"  💡 {idea.trigger}")
            print(f"  📝 {idea.content}")

            self._visited.add(next_node.topic)
            current = next_node

        print("\n" + "=" * 60)
        print(f"✨ 漫步完成，共生成 {len(results)} 个灵感")

        return results

    def combine(self, theme: str, subject_names: List[str] = None) -> List[Dict]:
        """
        组合创新模式

        Args:
            theme: 主题
            subject_names: 主体名称列表

        Returns:
            组合结果列表
        """
        if not subject_names:
            # 随机选择主体
            subject_names = random.sample(
                [s.get("name") for s in self.subjects] or ["博主", "产品", "场景"],
                min(3, len(self.subjects) or 3)
            )

        combinations = []
        print(f"\n🔗 组合创新: {theme}")
        print("=" * 60)

        for i, subject_name in enumerate(subject_names, 1):
            # 查找主体信息
            subject = next(
                (s for s in self.subjects if s.get("name") == subject_name),
                {"name": subject_name, "type": "generic", "tags": ["创作"]}
            )

            subject_type = subject.get("type", "generic")
            tags = subject.get("tags", [])

            # 根据主体类型生成不同角度的prompt
            if subject_type == "character":
                prompt = f"以{subject_name}的视角，探讨{theme}"
                angle = f"从{subject_name}的角度看问题"
            elif subject_type == "product":
                prompt = f"围绕{subject_name}，从产品角度分析{theme}"
                angle = "产品视角"
            elif subject_type == "scene":
                prompt = f"在{subject_name}场景下，演绎{theme}"
                angle = "场景化叙事"
            else:
                prompt = f"结合{subject_name}，深入探讨{theme}"
                angle = "综合视角"

            result = {
                "subject": subject_name,
                "prompt": prompt,
                "angle": angle,
                "tags": tags
            }
            combinations.append(result)

            print(f"\n  [{i}] {subject_name} ({subject_type})")
            print(f"      角度: {angle}")
            print(f"      选题: {prompt}")

        print("\n" + "=" * 60)
        return combinations

    def diverge(self, topic: str, num_ideas: int = 5) -> List[str]:
        """
        主题发散 - 围绕主题生成多个创意方向

        Args:
            topic: 核心主题
            num_ideas: 生成数量

        Returns:
            创意方向列表
        """
        print(f"\n📡 主题发散: {topic}")
        print("=" * 60)

        # 发散方向库
        directions = [
            f"深入分析{topic}的背后逻辑",
            f"用{topic}解决一个具体问题",
            f"从{topic}反推它的前提假设",
            f"对比{topic}与相关概念的差异",
            f"用{topic}讲一个有共鸣的故事",
            f"挑战{topic}的常见误区",
            f"用{topic}预测未来趋势",
            f"把{topic}用通俗语言解释给外行",
        ]

        results = random.sample(directions, min(num_ideas, len(directions)))

        for i, direction in enumerate(results, 1):
            print(f"  [{i}] {direction}")

        print("\n" + "=" * 60)
        return results

    def capture(self, inspiration: str, context: Dict = None) -> None:
        """
        捕获灵感到灵感库

        Args:
            inspiration: 灵感内容
            context: 上下文信息
        """
        context = context or {}

        # 更新灵感日志
        with open(INSPIRATION_LOG, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

            f.write(f"\n## 灵感记录 {timestamp}\n")
            if "seed" in context:
                f.write(f"- 种子: {context.get('seed')}\n")
            if "path" in context:
                f.write(f"- 路径: {' → '.join(context.get('path', []))}\n")
            if "trigger" in context:
                f.write(f"- 触发: {context.get('trigger')}\n")
            f.write(f"\n{inspiration}\n")

        print(f"\n💾 灵感已保存到: {INSPIRATION_LOG}")

    def init(self) -> None:
        """初始化数据目录"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # 创建示例主体库
        if not SUBJECT_LIB.exists():
            sample_subjects = [
                {"name": "职场博主", "type": "character", "tags": ["职场", "成长"]},
                {"name": "00后", "type": "character", "tags": ["年轻", "反差"]},
                {"name": "程序员", "type": "character", "tags": ["技术", "逻辑"]},
                {"name": "精致生活", "type": "scene", "tags": ["生活", "品质"]},
                {"name": "办公室", "type": "scene", "tags": ["工作", "日常"]},
                {"name": "AI助手", "type": "product", "tags": ["科技", "效率"]},
            ]
            with open(SUBJECT_LIB, "w", encoding="utf-8") as f:
                json.dump(sample_subjects, f, ensure_ascii=False, indent=2)

        # 创建灵感日志
        if not INSPIRATION_LOG.exists():
            with open(INSPIRATION_LOG, "w", encoding="utf-8") as f:
                f.write("# 灵感库\n\n记录所有创作灵感\n")

        # 创建知识图谱
        if not KNOWLEDGE_GRAPH.exists():
            with open(KNOWLEDGE_GRAPH, "w", encoding="utf-8") as f:
                json.dump(self._create_sample_graph(), f, ensure_ascii=False, indent=2)

        print("✅ 初始化完成")
        print(f"   主体库: {SUBJECT_LIB}")
        print(f"   知识图谱: {KNOWLEDGE_GRAPH}")
        print(f"   灵感日志: {INSPIRATION_LOG}")


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="RedBox Wander Engine - 漫步选题引擎")
    parser.add_argument("command", choices=["wander", "combine", "diverge", "capture", "init"],
                        help="命令")
    parser.add_argument("topic", nargs="?", help="主题")
    parser.add_argument("--subjects", "-s", nargs="+", help="主体列表")
    parser.add_argument("--diversity", "-d", type=float, default=0.7, help="多样性参数 (0-1)")
    parser.add_argument("--creativity", "-c", type=float, default=0.8, help="创意性参数 (0-1)")
    parser.add_argument("--max-steps", "-m", type=int, default=20, help="最大步数")
    parser.add_argument("--num", "-n", type=int, default=5, help="生成数量")

    args = parser.parse_args()

    config = {
        "diversity": args.diversity,
        "creativity": args.creativity,
        "max_steps": args.max_steps
    }
    engine = WanderEngine(config)

    if args.command == "init":
        engine.init()

    elif args.command == "wander":
        if not args.topic:
            print("❌ 需要提供主题")
            return
        ideas = engine.wander(args.topic)
        for idea in ideas:
            print(idea.to_markdown())

    elif args.command == "combine":
        theme = args.topic or "通用话题"
        results = engine.combine(theme, args.subjects)

    elif args.command == "diverge":
        topic = args.topic or "未定义主题"
        engine.diverge(topic, args.num)

    elif args.command == "capture":
        print("📝 请输入灵感内容 (输入空行结束):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        inspiration = "\n".join(lines)
        engine.capture(inspiration)


if __name__ == "__main__":
    main()